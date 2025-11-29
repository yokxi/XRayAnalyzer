import os
import cv2
import numpy as np
from ultralytics import YOLO
from src.config import YOLO_PATH, TEMP_DIR

class YoloTool:
    def __init__(self):
        if os.path.exists(YOLO_PATH):
            self.model = YOLO(YOLO_PATH)
        else:
            self.model = None

    def _load_safe_image(self, image_path):
        """
        Funzione interna per caricare e pulire l'immagine.
        Gestisce:
        1. File corrotti o non leggibili.
        2. Conversione da RGBA (PNG trasparente) a RGB.
        3. Conversione da Grayscale a RGB (YOLO vuole 3 canali).
        """
        # Carica l'immagine con OpenCV
        img = cv2.imread(image_path)
        
        if img is None:
            return None, "Errore: Impossibile leggere il file (formato non valido o corrotto)."

        # Caso 1: Immagine PNG con trasparenza (4 canali) -> Converti a 3 canali
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Caso 2: Immagine Grayscale pura (1 canale) -> Converti a 3 canali (finto RGB)
        # YOLO è addestrato su RGB, quindi si aspetta 3 canali anche se la foto è in b/n
        if len(img.shape) == 2 or img.shape[2] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        return img, None

    def analyze(self, image_paths: list):
        if not self.model:
            return [{"diagnosis": "Errore critico: Modello YOLO non caricato.", "processed": image_paths[0]}]

        results_summary = []

        for img_path in image_paths:
            # 1. CARICAMENTO SICURO
            clean_img, error = self._load_safe_image(img_path)
            
            if error:
                results_summary.append({"diagnosis": error, "processed": img_path})
                continue # Salta alla prossima immagine

            # 2. PREDIZIONE
            # Qui passiamo 'clean_img' (array numpy) invece del path.
            # imgsz=1024 attiva il Letterboxing automatico di YOLO.
            results = self.model.predict(source=clean_img, imgsz=1024, conf=0.15, verbose=False)
            
            for r in results:
                # Disegna
                im_array = r.plot()
                
                # Salva risultato
                filename = os.path.basename(img_path)
                output_path = os.path.join(TEMP_DIR, f"pred_{filename}")
                cv2.imwrite(output_path, im_array)
                
                # Crea report
                boxes = r.boxes
                if len(boxes) > 0:
                    # Logica per report più dettagliato
                    detection_text = f"Rilevata Polmonite (Confidenza max: {boxes.conf.max():.2f})"
                else:
                    detection_text = "Nessuna anomalia rilevata (Polmoni puliti)."
                
                results_summary.append({
                    "original": img_path,
                    "processed": output_path,
                    "diagnosis": detection_text
                })
                
        return results_summary