import os
import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms, models
import torch.nn as nn
from src import config

class VisionTool:
    def __init__(self, yolo_model_path=config.YOLO_MODEL_PATH, classifier_weights_path=config.CLASSIFIER_MODEL_PATH):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 1. STAGE 1: Classificatore Swin-B (Filtro Globale)
        print(f"Inizializzazione Swin-B SOTA da: {classifier_weights_path}")

        self.classifier = models.swin_b()
        n_inputs = self.classifier.head.in_features
        self.classifier.head = nn.Sequential(
            nn.Linear(n_inputs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 2)
        )
        
        if os.path.exists(classifier_weights_path):
            self.classifier.load_state_dict(torch.load(classifier_weights_path, map_location=self.device))
        else:
            print(f"Errore: Pesi Swin-B non trovati in {classifier_weights_path}")
            
        self.classifier.to(self.device).eval()
        
        # 2. STAGE 2: Detector YOLO11 (Localizzazione)
        print(f"Inizializzazione YOLO11 Detector da: {yolo_model_path}")
        if os.path.exists(yolo_model_path):
            self.yolo_model = YOLO(yolo_model_path)
        else:
            print(f"Errore: Pesi YOLO non trovati in {yolo_model_path}")
            self.yolo_model = None
        
        # Trasformazioni Standard SOTA (224x224 per Swin)
        self.classifier_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def apply_clahe(self, pil_img):
        """Standardizza il contrasto (Essenziale per Stage 1, Stage 2 e validazione AP/PA)."""
        img_np = np.array(pil_img.convert('L'))
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        res = clahe.apply(img_np)
        return Image.fromarray(cv2.cvtColor(res, cv2.COLOR_GRAY2RGB))

    def get_location_description(self, coords):
        """Determina la posizione anatomica basata sulle coordinate del box (1024x1024)."""
        x1, y1, x2, y2 = coords
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Inversione radiologica: DX immagine = SX paziente
        side = "zona polmonare sinistra" if center_x > 512 else "zona polmonare destra"
        
        if center_y < 341:
            depth = "campo superiore"
        elif center_y < 682:
            depth = "campo medio"
        else:
            depth = "campo inferiore (base)"
            
        return f"{depth} della {side}"

    def analyze(self, image_path):
        """
        Analisi a due stadi.
        Ritorna: (classifier_data, lista_detections, immagine_clahe_originale)
        """
        # Caricamento e Pre-processing (Punto di applicazione CLAHE)
        raw_img = Image.open(image_path).convert('RGB')
        clahe_img = self.apply_clahe(raw_img)
        
        # --- STAGE 1: CLASSIFICAZIONE ---
        input_tensor = self.classifier_transform(clahe_img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.classifier(input_tensor)
            prob = torch.softmax(output, dim=1)
            is_positive = torch.argmax(prob).item() == 1
            confidence = prob[0][1].item()

        classifier_data = {"is_positive": is_positive, "confidence": confidence}
        
        # --- STAGE 2: DETECTION (YOLO lavora comunque, l'agente con le informazioni che ha deciderà la "diagnosi" finale) ---
        detections = []
        if self.yolo_model:
            results = self.yolo_model.predict(source=clahe_img, imgsz=1024, conf=0.25, verbose=False)
            for box in results[0].boxes:
                coords = box.xyxy[0].tolist()
                crop = clahe_img.crop((coords[0], coords[1], coords[2], coords[3]))
                detections.append({
                    "diagnosis": "Lung Opacity",
                    "confidence": box.conf[0].item(),
                    "location_text": self.get_location_description(coords),
                    "image_crop": crop,
                    "coords": coords
                })
        
        return classifier_data, detections, clahe_img