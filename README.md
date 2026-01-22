# Real-Time Intelligent Surveillance System

## 📌 Description
Ce projet consiste en la conception et le développement d’un **système de vidéosurveillance intelligent en temps réel**, capable de détecter automatiquement des menaces telles que :
- 🔫 Armes (pistolets, couteaux)
- 🔥 Départs de feu / incendies
- 👤 Visages suspects

Le système combine **vision par ordinateur**, **deep learning** et une **architecture web moderne** afin d’assurer une détection rapide, une gestion efficace des alertes et une visualisation intuitive via une interface web.

## 🎯 Objectifs
- Détecter automatiquement des menaces à partir de flux vidéo en temps réel
- Générer des alertes visuelles et stocker les événements détectés
- Envoyer automatiquement des alertes par e-mail aux autorités compétentes
- Fournir une interface web de supervision en temps réel


## 🧠 Technologies utilisées

### 🔍 Intelligence Artificielle
- **YOLOv5** : détection d’armes (rapide et léger)
- **YOLOv8** : détection de feu (meilleure précision)
- **face_recognition (Dlib + OpenCV)** : détection de visages suspects

### 🖥️ Backend
- **FastAPI** (Python 3.10)
- **SQLite** (stockage des alertes)
- **SMTP (smtplib)** pour l’envoi automatique d’e-mails

### 🌐 Frontend
- **Next.js (React)**
- **Tailwind CSS**

### 🛠️ Outils
- OpenCV
- PyTorch
- Git & GitHub
- CVAT (annotation des données)


## 🏗️ Architecture du système

1. Capture du flux vidéo (webcam ou caméra IP)
2. Analyse en temps réel via YOLOv5 / YOLOv8
3. Envoi des détections à l’API FastAPI
4. Enregistrement des alertes dans la base de données
5. Envoi automatique d’e-mails en cas de menace critique
6. Visualisation en temps réel via l’interface Next.js


## 📊 Résultats clés

### 🔫 Détection d’armes (YOLOv5)
- Accuracy : **85%**
- Recall : **82.5%**
- mAP@0.5 : **89.1%**

### 🔥 Détection de feu (YOLOv8n)
- mAP@0.5 : **74.5%**
- Bon compromis précision / rapidité

### 👤 Reconnaissance faciale
- Précision ≈ **99.38%** (réseau pré-entraîné)

### 🚨 Alertes automatiques
- Temps de réaction < **1 seconde**
- Envoi d’e-mails avec :
  - Type de menace
  - Localisation estimée
  - Horodatage
  - Image / vidéo associée


## 🖥️ Interfaces
- **Tableau de bord** : vue globale des incidents en temps réel
- **Page alertes** : liste détaillée avec filtres, statut et génération de rapports PDF


## ⚖️ Considérations éthiques
- Aucune donnée biométrique stockée de manière permanente
- Pas d’identification faciale (détection uniquement)
- Traitement local des flux vidéo
- Projet à but **pédagogique et de recherche**, conforme aux principes RGPD


## 🚀 Améliorations futures
- Classification fine des armes (rifle, shotgun, pistol, etc.)
- Amélioration des performances en faible luminosité
- Déploiement sur systèmes edge (Jetson, Raspberry Pi)
- Ajout de notifications SMS / mobile


## 👤 Auteur
**Imane Karam**  
Étudiante en ingénierie informatique & intelligence artificielle

---

## 📄 Licence
Projet académique – usage pédagogique et de recherche.
