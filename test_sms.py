import smtplib
import socket
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json
import os
from datetime import datetime
import shortuuid

import sqlite3
from datetime import datetime

def get_ip_and_location():
    services = [
        'https://api.ipify.org?format=json',
        'https://ipinfo.io/json',
        'http://ip-api.com/json/',
        'https://ifconfig.me/all.json'
    ]
    
    ip, city, region, country, coords = None, "Inconnue", "Inconnue", "Inconnu", (0, 0)
    
    for service in services:
        try:
            response = requests.get(service, timeout=2)
            data = response.json()
            
            # Extraction des données selon le format de réponse
            ip = data.get('ip') or data.get('query') or ip
            city = data.get('city') or data.get('ville') or city
            region = data.get('region') or data.get('regionName') or region
            country = data.get('country') or data.get('pays') or country
            
            # Gestion des coordonnées selon différents formats
            if 'loc' in data:
                coords = tuple(map(float, data['loc'].split(',')))
            elif 'lat' in data and 'lon' in data:
                coords = (data['lat'], data['lon'])
            
            if ip and any([city != "Inconnue", region != "Inconnue"]):
                break
                
        except Exception as e:
            print(f"Erreur avec {service}: {str(e)}")
            continue
    
    # Fallback si aucune IP n'a été trouvée
    if not ip:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "Adresse IP non détectée"
    
    return ip, city, region, country, coords

def envoyer_alerte(path_video, label):
    # Configuration SMTP (à personnaliser)
    SMTP_SERVER = "smtp.gmail.com"  
    SMTP_PORT =587
    EMAIL_EXPEDITEUR = "mary85@gmail.com"
    EMAIL_PASSWORD = "*****"
    
    # Destinataires selon le type d'alerte
    ALERTE_RECIPIENTS = {
        "police": ["mary85@gmail.com"],
        "pompiers": ["tahiri.maryem@ensam-casa.ma"]
    }
    
   # Vérification du label
    label = label.lower()
    if label in ["feu"]:
        destinataires = ALERTE_RECIPIENTS["pompiers"]
        sujet = f"🔥 ALERTE POMPIERS: {label.capitalize()} détecté"
    else:
        if label not in ["arme","knife" , "pistol"]:
            label = "Criminel"
        destinataires = ALERTE_RECIPIENTS["police"]
        sujet = f"🚨 ALERTE POLICE: {label.capitalize()} détecté"
    
    # Récupération de la localisation 
    ip, ville, region, pays, (lat, lon) = get_ip_and_location()
    maps_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "#"
    

    # Préparation de l'email
    message = MIMEMultipart()
    message["From"] = EMAIL_EXPEDITEUR
    message["To"] = ", ".join(destinataires)
    message["Subject"] = sujet
    message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

    # Corps HTML du message
    
    corps_html = f"""
    <html>
    <head>
        <style type="text/css">
        body, html {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #2d3748;
            margin: 0;
            padding: 0;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .email-header {{
            background-color: {'#2c5282' if 'police' in label.lower() else '#9c4221'};
            color: white;
            padding: 25px;
            text-align: center;
        }}
        .email-content {{
            padding: 30px;
            background-color: #ffffff;
        }}
        .alert-section {{
            background-color: #f8fafc;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid {'#2c5282' if 'police' in label.lower() else '#9c4221'};
        }}
        .location-section {{
            background-color: #f0fff4;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid #38a169;
        }}
        .technical-section {{
            background-color: #ebf8ff;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid #3182ce;
        }}
        .footer {{
            font-size: 12px;
            color: #718096;
            text-align: center;
            padding: 20px;
            background-color: #f7fafc;
            border-top: 1px solid #e2e8f0;
        }}
        h2 {{
            margin-top: 0;
            font-weight: 600;
            font-size: 22px;
        }}
        h3 {{
            color: {'#2c5282' if 'police' in label.lower() else '#9c4221'};
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        .map-link {{
            display: inline-block;
            background-color: {'#2c5282' if 'police' in label.lower() else '#9c4221'};
            color: white !important;
            padding: 10px 18px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 12px;
            font-weight: 500;
            font-size: 14px;
        }}
        .info-item {{
            margin-bottom: 10px;
            font-size: 15px;
        }}
        .info-label {{
            font-weight: 600;
            color: #4a5568;
        }}
        .urgency-indicator {{
            display: inline-block;
            background-color: {'#e53e3e' if 'police' in label.lower() else '#dd6b20'};
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
            vertical-align: middle;
        }}
        </style>
    </head>
    <body>
        <div class="email-container">
        <div class="email-header">
            <h2>{'SÉCURITÉ PUBLIQUE' if 'police' in label.lower() else 'ALERTE INCENDIE'} <span class="urgency-indicator">URGENT</span></h2>
        </div>
        
        <div class="email-content">
            <div class="alert-section">
            <h3>Détection du système</h3>
            <div class="info-item">
                <span >Le système a détecté une situation nécessitant votre attention immédiate.</span>
            </div>
            <div class="info-item">
                <span class="info-label">Type d'alerte:</span> {label.capitalize()}
            </div>
            
            </div>
            
            <div class="location-section">
            <h3>Localisation</h3>
            <div class="info-item">
                <span class="info-label">Adresse:</span> {ville}, {region}, {pays}
            </div>
            <div class="info-item">
                <span class="info-label">Coordonnées:</span> {lat}, {lon}
            </div>
            <a href="{maps_link}" class="map-link" target="_blank">Ouvrir dans Google Maps</a>
            </div>
            
            <div class="technical-section">
            <h3>Détails techniques</h3>
            
            <div class="info-item">
                <span class="info-label">Horodatage:</span> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            </div>
            <div class="info-item">
                <span class="info-label">Source:</span> Système de surveillance #{ip.split('.')[-1]}
            </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© {datetime.now().year} Système de Surveillance Automatisé. Message généré automatiquement.</p>
            <p>Pour toute question, contacter le support technique.</p>
        </div>
        </div>
    </body>
    </html>
    """
    message.attach(MIMEText(corps_html, "html"))

    # Attachement de la vidéo
    try:
        with open(path_video, "rb") as video_file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(video_file.read())
        encoders.encode_base64(part)
        filename = os.path.basename(path_video)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}",
        )
        message.attach(part)
    except Exception as file_error:
        print(f"Erreur fichier vidéo: {file_error}")
        return False

    # Envoi de l'email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_EXPEDITEUR, EMAIL_PASSWORD)
            server.sendmail(EMAIL_EXPEDITEUR, destinataires, message.as_string())
        print(f"Alerte '{label}' envoyée avec succès à {len(destinataires)} destinataire(s)")
        
        return True
    except smtplib.SMTPException as smtp_error:
        print(f"Erreur SMTP: {smtp_error}")
    except Exception as general_error:
        print(f"Erreur inattendue: {general_error}")
    
    return False

def inserer_alerte_db(path_video, label, media_reference):
    # Récupération des informations de localisation
    ip, ville, region, pays, (lat, lon) = get_ip_and_location()
    location = f"{ville}, {region}, {pays} , {lat}, {lon}"
    
    # Connexion à la base de données
    conn = None
    try:
        conn = sqlite3.connect('C:\\Users\\Meryem\\surveillance-platform\\backend\\alerts.db')
        cursor = conn.cursor()
        
        # Génération d'un ID unique pour l'alerte
        alert_id = shortuuid.uuid()
        
        # Insertion des données dans la base
        cursor.execute('''
        INSERT INTO alerts (
            alert_id,
            detection_type,
            location,
            timestamp,
            media_reference,
            statut,
            video_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert_id,
            label.lower(),
            location,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            media_reference,
            "Non traité",
            path_video
        ))
        
        conn.commit()
        print(f"Alerte enregistrée dans la base de données (ID: {alert_id})")
        return True
        
    except sqlite3.Error as e:
        print(f"Erreur base de données: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def envoyer_alerte_avec_db(path_video, label, path_image):
    print(f"[DEBUG] Envoi alerte avec {label}, image: {path_image}, video: {path_video}")
    resultat_db = inserer_alerte_db(path_video, label,path_image)

    resultat_email = envoyer_alerte(path_video, label)
    
    return resultat_email and resultat_db

#envoyer_alerte_avec_db("C:\\Users\\DELL\\Videos\\WhatsApp Video 2022-05-11 at 12.16.28.mp4", "arme","images\\test3.jpg")
