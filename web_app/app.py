import os
from flask import Flask, render_template, request, jsonify
import torch
from model_utils import load_model, get_prediction
from agent import MedicalAgent  # <--- 1. IMPORTIAMO L'AGENTE
import io

app = Flask(__name__)

# Configurazione

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, 'modello_detection_polmonite.pth')

DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

# Caricamento Modello Visione (HPC)
try:
    model = load_model(MODEL_PATH, DEVICE)
    print("✅ Modello Visione Caricato.")
except Exception as e:
    print(f"❌ Errore Modello: {e}")
    model = None

# Caricamento Agente (Cervello)
try:
    agent = MedicalAgent() # <--- 2. INIZIALIZZIAMO L'AGENTE
    print("✅ Agente Medico Attivo.")
except Exception as e:
    print(f"❌ Errore Agente: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model: return jsonify({'error': 'Model not loaded'}), 500
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'}), 400
        
    try:
        image_bytes = io.BytesIO(file.read())
        
        # FASE 1: VISIONE (Il tuo Faster R-CNN)
        boxes, scores = get_prediction(model, image_bytes, DEVICE, threshold=0.5)
        
        # Calcoli per l'Agente
        num_boxes = len(boxes)
        max_score = max(scores) if scores else 0.0
        
        # FASE 2: RAGIONAMENTO (L'Agente scrive il report)
        report_data = agent.generate_report(num_boxes, max_score) # <--- 3. CHIAMIAMO L'AGENTE
        
        return jsonify({
            'boxes': boxes,
            'scores': scores,
            'report': report_data # <--- 4. MANDIAMO IL REPORT AL SITO
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)