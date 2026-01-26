import os
from dotenv import load_dotenv

load_dotenv()

# --- HPC & MODELLO VISION-LANGUAGE ---
HPC_ENDPOINT = os.getenv("HPC_ENDPOINT", "http://host.docker.internal:8000/v1")
HPC_MODEL_NAME = os.getenv("HPC_MODEL_NAME", "qwen-vl")

# --- MODELLO DI VISIONE ---
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "/app/models/yolo11/best_clahe.pt")
# --- CLASSIFICATORE ---
CLASSIFIER_MODEL_PATH = os.getenv("CLASSIFIER_MODEL_PATH", "/app/models/swinB_classifier/swinB_classifier.pth")

# --- RAG KNOWLEDGE BASE ---
# Percorso alla cartella con i file MD di KNOWLEDGE BASE(anatomia, tecnica, fleischner, ecc.)
KB_PATH = os.getenv("KB_PATH", "/app/data/md_knowledge_base")
# Percorso al database vettoriale
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "/app/data/chromaDB_vector_db")

# --- UTILITY ---
TEMP_DIR = os.getenv("TEMP_DIR", "/app/temp")
os.makedirs(TEMP_DIR, exist_ok=True)