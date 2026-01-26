#!/bin/bash

# Argomento passato (gpu o cpu).
# Default: cpu
DEVICE_ARG=${1:-cpu}

if [[ "$DEVICE_ARG" != "gpu" && "$DEVICE_ARG" != "cpu" ]]; then
    echo "ERRORE: Specifica 'gpu' o 'cpu' (es: ./build.sh gpu)"
    exit 1
fi

IMAGE_NAME="app_ind_ai:latest"

echo "--- INIZIO BUILD DOCKER ---"
echo "Immagine: ${IMAGE_NAME}"
echo "Modalità: ${DEVICE_ARG}"
echo "---------------------------"

docker build -t ${IMAGE_NAME} \
    --build-arg USER_ID=$(id -u) \
    --build-arg USERNAME=$(id -un) \
    --build-arg DEVICE=${DEVICE_ARG} \
    .

echo "Build completato con successo per ${DEVICE_ARG}."