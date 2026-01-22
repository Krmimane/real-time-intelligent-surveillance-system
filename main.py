import cv2
import csv
import numpy as np
import os
from datetime import datetime
from ultralytics import YOLO
from yolov5.utils.general import non_max_suppression
from yolov5.utils.torch_utils import select_device
from yolov5.models.experimental import attempt_load
import face_recognition
import torch
import pickle
from test_sms import envoyer_alerte_avec_db
import depthai as dai

# === Paramètres Reconnaissance Faciale ===
ENCODING_MODEL_PATH = r'models\face_encodings_model.pkl'
TOLERANCE = 0.45

# === Chargement modèles ===
yolo8_fire_model = YOLO('models/IncendieDetection.pt')
torch_device = select_device('')
yolo5_model = attempt_load('models/WeaponDetection.pt', device=torch_device)  # Fixed: Use torch_device
yolo5_model.model.float()
imgsz = 640

# === Chargement du modèle facial (pickle) ===
with open(ENCODING_MODEL_PATH, 'rb') as f:
    data = pickle.load(f)
    known_face_encodings = data['encodings']
    known_face_ids = data['ids']
print(f"✅ Modèle de visages chargé : {len(known_face_ids)} visages connus.")

# === Initialisation de la caméra OAK-D ===
pipeline = dai.Pipeline()
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setFps(30)

xout = pipeline.createXLinkOut()
xout.setStreamName("video")
cam_rgb.preview.link(xout.input)

device = dai.Device(pipeline)
video_queue = device.getOutputQueue(name="video", maxSize=4, blocking=False)

# === Initialisation des variables ===
os.makedirs('output', exist_ok=True)
recording = False
out_video = None
last_detection_time = None
non_detection_delay = 5  # seconds
saved_detections = set()
frame_number = 0
recording_start_time = None  # Initialize recording start time

def scale_coords(img1_shape, coords, img0_shape):
    gain = torch.tensor([
        img0_shape[1] / img1_shape[1],
        img0_shape[0] / img1_shape[0],
        img0_shape[1] / img1_shape[1],
        img0_shape[0] / img1_shape[0]
    ], device=coords.device)
    coords = coords * gain
    coords = coords.round()
    return coords

def start_new_recording(frame_shape):
    global out_video, recording
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = os.path.abspath(f"output/session_{timestamp}.mp4")
    
    # Dimensions de la frame
    height, width = frame_shape[:2]
    
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Use 'avc1' for better compatibility
    out_video = cv2.VideoWriter(
        video_filename,
        fourcc,
        20.0,
        (width, height)
    )
    
    if not out_video.isOpened():
        print(f"❌ Erreur: Impossible de créer le fichier vidéo {video_filename}")
        return None
    
    print(f"📹 Enregistrement démarré : {video_filename}")
    recording = True
    return video_filename

def stop_recording():
    global out_video, recording
    if out_video is not None:
        out_video.release()
        print("🛑 Enregistrement arrêté.")
    out_video = None
    recording = False

try:
    while True:
        frame_data = video_queue.get()
        frame = frame_data.getCvFrame()
        
        frame_number += 1
        detected_items = set()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # === Détection des armes ===
        resized = cv2.resize(frame, (imgsz, imgsz))
        img_tensor = torch.from_numpy(resized).to(torch_device).permute(2, 0, 1).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0)
        pred = yolo5_model(img_tensor)
        pred = non_max_suppression(pred, conf_thres=0.6, iou_thres=0.45)
        names = yolo5_model.names

        for det in pred:
            if det is not None and len(det):
                det[:, :4] = scale_coords(img_tensor.shape[2:], det[:, :4], frame.shape).round()
                for *xyxy, conf, cls in reversed(det):
                    label = names[int(cls)]
                    confidence = float(conf)
                    if confidence > 0.5:
                        detected_items.add(label)
                        x1, y1, x2, y2 = map(int, xyxy)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                        cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # === Détection incendie YOLOv8 ===
        results_yolo8 = yolo8_fire_model(frame, imgsz=640)
        names_yolo8 = yolo8_fire_model.names
        for r in results_yolo8:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    confidence = float(box.conf[0].item())
                    if confidence > 0.5:
                        label = names_yolo8[cls_id]
                        detected_items.add(label)
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # === Reconnaissance faciale (pickle) ===
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Inconnu"
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            if len(distances) > 0:
                min_distance = np.min(distances)
                best_match_index = np.argmin(distances)
                if min_distance < TOLERANCE:
                    name = known_face_ids[best_match_index]
                    detected_items.add(name)

            # Mise à l’échelle vers la taille d'origine
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # === Gestion de l'enregistrement ===
       
        MIN_RECORDING_TIME = 1.0  # secondes

        if len(detected_items) > 0:
            if not recording:
                video_filename = start_new_recording(frame.shape)
                if video_filename is None:
                    continue  # Skip if video writer failed to initialize
                last_detection_time = datetime.now()
                recording_start_time = datetime.now()
            
            last_detection_time = datetime.now()

            for item in detected_items:
                # Générer un timestamp unique pour chaque image
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")  # Inclut les microsecondes pour unicité
                img_filename = os.path.abspath(f"output/{timestamp}_{item}.jpg")
                if item not in [det[0] for det in saved_detections]:  # Vérifier si l'item n'est pas déjà sauvegardé
                    cv2.imwrite(img_filename, frame)
                    print(f"✅ Détection : {item} image sauvegardée : {img_filename}")
                    saved_detections.add((item, img_filename))  # Stocker l'item avec son img_filename

        # Stop recording if no detections for non_detection_delay seconds
        if recording and last_detection_time is not None:
            if (datetime.now() - last_detection_time).total_seconds() > non_detection_delay:
                stop_recording()
                if video_filename:  # Ensure video_filename is defined
                    for item, img_filename in saved_detections:  # Parcourir les tuples (item, img_filename)
                        envoyer_alerte_avec_db(video_filename, item, img_filename)  # Envoyer l'alerte avec le bon img_filename
                    saved_detections.clear()  # Clear detections after stopping 

        if recording and out_video is not None:
            out_video.write(frame)

            cv2.imshow('Webcam Real-time Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

except KeyboardInterrupt:
    print("🛑 Programme interrompu par l'utilisateur.")

finally:
    # Cleanup
    stop_recording()
    cv2.destroyAllWindows()
    device.close()

# Chemins absolus
output_dir = os.path.abspath("output")
print(f"📸 Images des détections dans : {output_dir}")