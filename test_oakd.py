import depthai as dai
import cv2

# Créer un pipeline DepthAI
pipeline = dai.Pipeline()

# Ajouter une caméra couleur au pipeline
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setFps(30)

# Envoyer la sortie vers l'hôte
xout = pipeline.createXLinkOut()
xout.setStreamName("video")
cam_rgb.preview.link(xout.input)

# Démarrer le pipeline
with dai.Device(pipeline) as device:
    video = device.getOutputQueue(name="video", maxSize=4, blocking=False)

    while True:
        frame = video.get().getCvFrame()
        cv2.imshow("OAK-D Camera", frame)
        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()
