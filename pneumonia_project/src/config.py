import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Percorsi mappati dentro Docker
YOLO_PATH = os.getenv("YOLO_MODEL_PATH", "/app/models/yolo11/best.pt")
TEMP_DIR = os.getenv("TEMP_DIR", "/app/temp")

# Assicuriamoci che la temp dir esista
os.makedirs(TEMP_DIR, exist_ok=True)