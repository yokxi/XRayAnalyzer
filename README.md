<div align="center">

# 🩺 XRayAnalyzer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

> **An AI-powered tool using Deep Learning to detect and localize suspicious areas in chest radiographs.**

</div>

---

## 📖 About The Project

This repository contains the code for **XRayAnalyzer**, a project designed to assist in medical diagnosis by **detecting and localizing potential anomalies** in chest X-rays.

The primary goal is to **identify suspicious areas (e.g., nodules, opacities, or other pathologies)** that may require further medical review. This project is part of my M.Sc. in Computer Science at the University of Parma.

---

## 🛠️ Installazione e Configurazione (Docker)

Il progetto è interamente containerizzato tramite Docker per garantire la riproducibilità dell'ambiente di sviluppo, indipendentemente dal sistema operativo host.

### 1. Build dell'Immagine

Per costruire l'immagine Docker è necessario utilizzare lo script `build.sh` presente nella cartella `docker/`. Lo script supporta due modalità: **CPU** (default) e **GPU**.

#### Esecuzione Standard (CPU / Mac Apple Silicon)

Se non si dispone di una scheda video NVIDIA, eseguire semplicemente lo script. Questo installerà la versione di PyTorch ottimizzata per CPU.

```bash
cd docker
./build.sh
```

#### Esecuzione con Supporto GPU (NVIDIA CUDA)

Se si intende utilizzare l'accelerazione hardware su scheda video NVIDIA, passare l'argomento `gpu`. Questo configurerà il container con i driver CUDA 13.0 e PyTorch compatibile.

```bash
cd docker
./build.sh gpu
```

### 2. Utilizzo del container

L'avvio del container avviene tramite lo script `run.sh`, che monta la cartella del codice sorgente all'interno del container. Il container mappa la cartella fornita su `/app`.

**Nota:** Gli esempi seguenti assumono di trovarsi all'interno della cartella `docker/` dove risiede lo script. Poiché il codice del progetto si trova nella cartella `pneumonia_project`, useremo il percorso relativo `../pneumonia_project`.

#### Esecuzione Standard (CPU)

```bash
# Sintassi: ./run.sh <percorso_cartella_progetto>
./run.sh ../pneumonia_project
```

#### Esecuzione con Accelerazione GPU

Richiede di aver eseguito il build con l'opzione `gpu`.

```bash
# Sintassi: ./run.sh <percorso_cartella_progetto> gpu
./run.sh ../pneumonia_project gpu
```

---

## 🚀 Lancio dell'Applicazione

Una volta avviato il container, vi troverete nella shell interna. Per lanciare l'interfaccia grafica Web (Streamlit), seguire questi passaggi:

1.  Spostarsi nella cartella dell'interfaccia utente:

    ```bash
    cd /app/src/ui
    ```

2.  Lanciare l'applicazione:
    ```bash
    streamlit run app.py
    ```

L'applicazione sarà accessibile dal browser all'indirizzo indicato nel terminale (solitamente `http://localhost:8501`).
