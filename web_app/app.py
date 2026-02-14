import os
from flask import Flask, render_template, request, jsonify
import torch
from model_utils import load_model, get_prediction
import io

app = Flask(__name__)

MODEL_PATH = 'modello_detection_polmonite.pth'
DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

try:
    print(f"Loading model from {MODEL_PATH}...")
    model = load_model(MODEL_PATH, DEVICE)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        image_bytes = io.BytesIO(file.read())
        
        boxes, scores = get_prediction(model, image_bytes, DEVICE, threshold=0.2)
        
        return jsonify({
            'boxes': boxes,
            'scores': scores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
