
<div align="center">

# 🩺 XRayAnalyzer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

> **An AI-powered tool using Deep Learning to detect and localize suspicious areas in chest radiographs.**

</div>

---

## 📖 About The Project

**XRayAnalyzer** è un assistente diagnostico intelligente progettato per supportare l'analisi di radiografie toraciche. A differenza dei classificatori standard, questo sistema combina due tecnologie avanzate:

1.  **Visione (Deep Learning):** Un modello **Faster R-CNN** (addestrato su HPC) localizza con precisione le opacità polmonari disegnando Bounding Box.
2.  **Ragionamento (Agente AI):** Un modulo logico (RAG) consulta una **Knowledge Base medica locale** per generare un referto testuale completo, suggerendo protocolli terapeutici basati sulle evidenze visive.

Questo progetto è stato sviluppato come parte del corso di *Applicazione industriali dell'intelligenza artificiale* (Laurea Magistrale in Informatica, Università di Parma).

---

## 🚀 Caratteristiche Principali

* **Object Detection:** Localizzazione precisa delle anomalie (non solo classificazione).
* **Knowledge Base Estendibile:** L'agente legge dinamicamente file `.txt` (protocolli, linee guida AIFA, sintomi) per costruire le risposte.
* **Architettura Ibrida:** Unisce l'accuratezza di una CNN classica con la flessibilità di un sistema a regole/agenti.
* **Dockerized:** Ambiente completamente isolato e riproducibile.

---

## 🛠️ Installazione e Configurazione (Docker)

Il progetto è interamente containerizzato tramite Docker per garantire la riproducibilità dell'ambiente di sviluppo, indipendentemente dal sistema operativo host.

### 1. Build dell'Immagine

Per costruire l'immagine Docker contenente tutte le dipendenze necessarie, eseguire lo script di build dalla cartella *docker/* del progetto:

```bash
./build.sh
```

> **⚠️ Nota per architetture non-NVIDIA (CPU-only / Apple Silicon)**
> Il Dockerfile è configurato di default per installare le versioni di PyTorch ottimizzate per CUDA 13.0 (GPU NVIDIA). Se si intende eseguire il container su una macchina priva di GPU NVIDIA compatibile è necessario modificare il Dockerfile prima di avviare il build:
> 1. Aprire il file `Dockerfile`.
> 2. Individuare il comando `RUN pip install ...` relativo all'installazione di torch.
> 3. Sostituirlo con il comando appropriato per la propria architettura (es. CPU-only), consultando la [documentazione ufficiale di PyTorch](https://pytorch.org/get-started/locally/).


### 2. Utilizzo del container

È necessario predisporre una cartella di lavoro (es. `src/` o `workspace/`) all'interno della directory del progetto. Questa cartella verrà passata come argomento allo script di avvio e verrà mappata direttamente nella directory `/app` all'interno del container.

L'avvio del container è gestito dallo script **run.sh**, che accetta due argomenti posizionali:

1. **Path della cartella sorgente (Obbligatorio)**: Il percorso relativo alla cartella di lavoro sull'host.
2. **Flag GPU (Opzionale)**: La stringa `gpu` per abilitare l'accelerazione hardware.

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

---

## 📦 Gestione del Modello AI (Git LFS)

Il file del modello (`web_app/modello_detection_polmonite.pth`) supera i 100MB, il limite standard di GitHub. Per questo motivo, il progetto utilizza **Git Large File Storage (LFS)**.

### Come caricare aggiornamenti del modello
Se riaddestri il modello e devi caricare una nuova versione su GitHub, segui questi passaggi tassativi per evitare errori di upload:

1. **Installa Git LFS**:
   ```bash
   git lfs install
    ```
1. **Assicurati che il file sia tracciato da LFS:** :
   ```bash
   git lfs track "web_app/modello_detection_polmonite.pth"
    ```

---

## 🌐 Web App (MediScan AI)

Il progetto include una Web App interattiva basata su Flask per testare il modello in tempo reale. Puoi avviarla in due modi:

### 🐳 Opzione 1: Esecuzione con Docker (Consigliata)
Questo metodo garantisce che l'ambiente sia identico a quello di sviluppo, evitando errori di dipendenze.

1.  **Avvia il container** mappando la porta 5000 e la cartella corrente:
    * **Windows (PowerShell):**
        ```powershell
        docker run --rm -it -p 5000:5000 -v "${PWD}:/app" app_ind_ai:latest
        ```
    * **Linux / Mac:**
        ```bash
        docker run --rm -it -p 5000:5000 -v "$(pwd):/app" app_ind_ai:latest
        ```

2.  **Lancia l'applicazione** (dentro il terminale del container):
    ```bash
    python3 web_app/app.py
    ```

3.  **Apri il browser** all'indirizzo: [http://localhost:5000](http://localhost:5000)

---

### 💻 Opzione 2: Esecuzione Locale
Se preferisci eseguire l'app direttamente sul tuo computer senza Docker:

1.  **Spostati nella cartella della web app**:
    ```bash
    cd web_app
    ```

2.  **Installa le dipendenze** (si consiglia di usare un virtual environment):
    ```bash
    pip install -r requirements.txt
    ```

3.  **Avvia il server**:
    ```bash
    python app.py
    ```

4.  **Apri il browser** all'indirizzo: [http://localhost:5000](http://localhost:5000)

