import os
import cv2
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from torchvision import transforms, models
import torch.nn as nn
from ensemble_boxes import weighted_boxes_fusion # Necessario: pip install ensemble-boxes
from src import config

# 1. INIEZIONE MODULO MLCA SOTA (Necessario per caricare YOLOv10)
class MLCA(nn.Module):
    def __init__(self, c1, c2=None):
        super().__init__()
        self.c2 = c2 if c2 is not None else c1
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv2d(c1, self.c2, 1, 1, 0, bias=False)
        self.sig = nn.Sigmoid()

    def forward(self, x):
        return x * self.sig(self.conv(self.gap(x)))

# Patch dinamica della libreria Ultralytics prima del caricamento
import ultralytics.nn.tasks as tasks
import ultralytics.nn.modules as modules
tasks.MLCA = MLCA
modules.MLCA = MLCA
# =================================================================

class VisionTool:
    def __init__(self, v10_model_path=config.YOLO10_MODEL_PATH, v11_model_path=config.YOLO11_MODEL_PATH, classifier_weights_path=config.CLASSIFIER_MODEL_PATH):
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
        print(f"Inizializzazione Ensemble YOLOv10 + YOLOv11 da: {v10_model_path} e {v11_model_path}")
        if os.path.exists(v10_model_path) and os.path.exists(v11_model_path):
            self.yolo_v10 = YOLO(v10_model_path) # Il tuo v10 con BiFPN/MLCA
            self.yolo_v11 = YOLO(v11_model_path) # Il v11 standard/SOTA
        else:
            print(f"Errore: Pesi YOLO non trovati in {v10_model_path} o {v11_model_path}")
            self.yolo_v10 = None
            self.yolo_v11 = None

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
        # Pre-processing
        raw_img = Image.open(image_path).convert('RGB')
        clahe_img = self.apply_clahe(raw_img)
        width, height = clahe_img.size

        # --- STAGE 1: CLASSIFICAZIONE (Swin-B) ---
        input_tensor = self.classifier_transform(clahe_img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.classifier(input_tensor)
            prob = torch.softmax(output, dim=1)
            swin_conf = prob[0][1].item()
            is_positive_global = swin_conf > 0.5

        print(f"\n--- DEBUG PIPELINE SOTA ---")
        print(f"1. [Swin-B] Confidence Globale: {swin_conf:.4f}")

        # --- STAGE 2: DETECTION ENSEMBLE CON TTA ---
        # Eseguiamo entrambi i modelli con TTA (augment=True)
        res_v10 = None
        res_v11 = None

        # YOLOv10
        if self.yolo_v10:
            try:
                res_v10 = self.yolo_v10.predict(
                    source=clahe_img,
                    imgsz=1024,
                    conf=0.15,
                    augment=True,
                    verbose=False
                )[0]
                print(f"2. [YOLOv10] Box trovati: {len(res_v10.boxes)} | Max Conf: {res_v10.boxes.conf.max().item() if len(res_v10.boxes)>0 else 0:.4f}")
            except Exception as e:
                print(f"Errore inferenza YOLOv10: {e}")
        else:
            print("2. [YOLOv10] Modello non caricato, skip.")

        # YOLOv11
        if self.yolo_v11:
            try:
                res_v11 = self.yolo_v11.predict(
                    source=clahe_img,
                    imgsz=1024,
                    conf=0.15,
                    augment=True,
                    verbose=False
                )[0]
                print(f"3. [YOLOv11] Box trovati: {len(res_v11.boxes)} | Max Conf: {res_v11.boxes.conf.max().item() if len(res_v11.boxes)>0 else 0:.4f}")
            except Exception as e:
                print(f"Errore inferenza YOLOv11: {e}")
        else:
            print("3. [YOLOv11] Modello non caricato, skip.")

        # Preparazione dati per WBF (Weighted Box Fusion)
        boxes_list = []
        scores_list = []
        labels_list = []

        # Process YOLOv10 results
        if res_v10 and len(res_v10.boxes) > 0:
            boxes_list.append(res_v10.boxes.xyxyn.cpu().numpy().tolist())
            scores_list.append(res_v10.boxes.conf.cpu().numpy().tolist())
            labels_list.append([0] * len(res_v10.boxes))
        else:
            boxes_list.append([])
            scores_list.append([])
            labels_list.append([])

        # Process YOLOv11 results
        if res_v11 and len(res_v11.boxes) > 0:
            boxes_list.append(res_v11.boxes.xyxyn.cpu().numpy().tolist())
            scores_list.append(res_v11.boxes.conf.cpu().numpy().tolist())
            labels_list.append([0] * len(res_v11.boxes))
        else:
            boxes_list.append([])
            scores_list.append([])
            labels_list.append([])

        # Fusione dei Box
        detections = []
        yolo_annotated_img = clahe_img.copy()
        draw = ImageDraw.Draw(yolo_annotated_img)

        if any(len(b) > 0 for b in boxes_list):
            f_boxes, f_scores, f_labels = weighted_boxes_fusion(
                boxes_list, scores_list, labels_list,
                weights=[1.2, 1.0], # Diamo più peso al tuo v10 custom
                iou_thr=0.5, skip_box_thr=0.1
            )

            for i, (box, score) in enumerate(zip(f_boxes, f_scores)):
                # CALCOLO DETTAGLIATO
                yolo_ensemble_contribution = score * 0.4
                swin_contribution = swin_conf * 0.6
                final_conf = yolo_ensemble_contribution + swin_contribution

                print(f"\n>> Analisi Box #{i+1}:")
                print(f"   - Score Consenso YOLO (WBF): {score:.4f} (Peso 40% -> {yolo_ensemble_contribution:.4f})")
                print(f"   - Score Garante Swin-B:      {swin_conf:.4f} (Peso 60% -> {swin_contribution:.4f})")
                print(f"   - CONFIDENZA FINALE COMPOSTA: {final_conf:.4f} ({(final_conf*100):.1f}%)")

                if final_conf > 0.35: # Soglia di sensibilità SOTA
                    # Riconvertiamo in pixel per crop e disegno
                    coords = [box[0]*width, box[1]*height, box[2]*width, box[3]*height]

                    # Disegno box sull'immagine finale
                    draw.rectangle(coords, outline="red", width=4)
                    draw.text((coords[0], coords[1]-20), f"Pneumonia {final_conf:.2f}", fill="red")

                    detections.append({
                        "diagnosis": "Lung Opacity",
                        "confidence": final_conf,
                        "location_text": self.get_location_description(coords),
                        "image_crop": clahe_img.crop(coords),
                        "coords": coords
                    })

        classifier_data = {
            "is_positive": len(detections) > 0 or swin_conf > 0.7,
            "confidence": swin_conf
        }

        return classifier_data, detections, clahe_img, yolo_annotated_img