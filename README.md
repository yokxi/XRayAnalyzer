# XRayAnalyzer 🩺

> An AI-powered tool using Deep Learning to **detect and localize suspicious areas** in chest radiographs.

This repository contains the code for **XRayAnalyzer**, a project designed to assist in medical diagnosis by **detecting and localizing potential anomalies** in chest X-rays.

The primary goal is to **identify suspicious areas (e.g., nodules, opacities, or other pathologies)** that may require further medical review. This project is part of my M.Sc. in Computer Science at the University of Parma.

---

## 🛠️ Installazione e Configurazione

Il progetto è interamente containerizzato tramite Docker per garantire la riproducibilità dell'ambiente di sviluppo, indipendentemente dal sistema operativo host.

### 1. Build dell'Immagine

Per costruire l'immagine Docker contenente tutte le dipendenze necessarie, eseguire lo script di build dalla cartella *docker/* del progetto:

```bash
./build.sh
```

#### ⚠️ Nota per architetture non-NVIDIA (CPU-only / Apple Silicon)
Il Dockerfile è configurato di default per installare le versioni di PyTorch ottimizzate per CUDA 13.0 (GPU NVIDIA). Se si intende eseguire il container su una macchina priva di GPU NVIDIA compatibile è necessario modificare il Dockerfile prima di avviare il build:
1) Aprire il file Dockerfile.
2) Individuare il comando RUN pip install ... relativo all'installazione di torch.
3) Sostituirlo con il comando appropriato per la propria architettura (es. CPU-only), consultando la [documentazione ufficiale di PyTorch](https://pytorch.org/get-started/locally/).


### 2. Utilizzo del container
È necessario predisporre una cartella di lavoro (es. src/ o workspace/) all'interno della directory del progetto. Questa cartella verrà passata come argomento allo script di avvio e verrà mappata direttamente nella directory /app all'interno del container. Qualsiasi file salvato in /app dal container sarà immediatamente disponibile nella cartella host specificata.

L'avvio del container è gestito dallo script **run.sh**, che accetta due argomenti posizionali:

1) **Path della cartella sorgente (Obbligatorio)**: Il percorso relativo alla cartella di lavoro sull'host.
2) **Flag GPU (Opzionale)**: La stringa gpu per abilitare l'accelerazione hardware.

#### Esecuzione Standard (CPU)
```bash
# Sintassi: ./run.sh <cartella_sorgente>
./run.sh /src
```

#### Esecuzione con Accelerazione GPU
```bash
# Sintassi: ./run.sh <cartella_sorgente> gpu
./run.sh ./src gpu
```