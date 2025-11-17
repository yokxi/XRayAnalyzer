#!/bin/bash

# Nome che vuoi dare alla tua immagine
IMAGE_NAME="app_ind_ai:latest"

echo "Building l'immagine ${IMAGE_NAME}..."

docker build -t ${IMAGE_NAME} \
    --build-arg USER_ID=$(id -u) \
    --build-arg USERNAME=$(id -un) \
    .

echo "Build completato."