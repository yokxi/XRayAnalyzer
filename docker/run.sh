#!/bin/bash

# Nome dell'immagine costruita con build.sh
IMAGE_NAME="app_ind_ai:latest"

# 1. Prende la cartella da montare come primo argomento
PROJECT_PATH=$1

# 2. Prende l'opzione GPU come secondo argomento (opzionale)
GPU_FLAG=$2

# 3. Se non fornisci un percorso, usa 'src' come default
if [ -z "$PROJECT_PATH" ]; then
  PROJECT_PATH="./src"
fi

# Risolve il percorso assoluto della cartella
PROJECT_DIR=$(realpath "$PROJECT_PATH")

# Crea la cartella se non esiste
if [ ! -d "$PROJECT_DIR" ]; then
  echo "Creando la cartella di progetto: $PROJECT_DIR"
  mkdir -p "$PROJECT_DIR"
fi

# 4. Configurazione GPU
DOCKER_GPU_ARGS=""
if [ "$GPU_FLAG" == "gpu" ]; then
    DOCKER_GPU_ARGS="--gpus all"
    echo "🟢 ATTENZIONE: Abilitato accesso a tutte le GPU host (--gpus all)."
fi

echo "------------------------------------------"
echo "Montando la cartella HOST: $PROJECT_DIR"
echo "Nella cartella CONTAINER: /app"
echo "Per uscire, digita 'exit'"
echo "------------------------------------------"
echo ""

# 5. Avvia il container (aggiungendo la variabile GPU se impostata)
docker run --rm -it \
    --platform linux/amd64 \
    $DOCKER_GPU_ARGS \
    -p 8501:8501 \
    -e STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    -e PYTHONPATH=/app \
    --env-file .env \
    -v "${PROJECT_DIR}:/app" \
    ${IMAGE_NAME} \
    bash