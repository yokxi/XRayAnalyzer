# <p align="center">🩺 XRayAnalyzer: AI-Powered Clinical Support</p>

<p align="center">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" />
</p>

---

## 📖 Panoramica del Progetto

**XRayAnalyzer** è un sistema avanzato di supporto clinico progettato per l'analisi di radiografie del torace (CXR). Utilizza una combinazione di **Computer Vision** e **Ragionamento Multimodale** per assistere i medici nell'identificazione e localizzazione di anomalie polmonari, con un focus specifico sulla polmonite.

Il sistema non si limita a fornire un esito positivo/negativo, ma genera un **report di ragionamento spiegabile (XAI)** che permette al clinico di comprendere il processo decisionale dell'intelligenza artificiale.

### ✨ Funzionalità Chiave

- 🔍 **Localizzazione Precisa**: Individuazione di aree sospette tramite un Ensemble di modelli YOLO.
- 🧠 **Ragionamento Clinico**: Analisi multimodale basata su Large Language Models (LLM) per convalidare i reperti.
- 📚 **Integrazione RAG**: Accesso a una base di conoscenza medica (linee guida Fleischner, anatomia) per standardizzare i referti.
- 📊 **Dashboard Analitica**: Monitoraggio delle prestazioni e statistiche storiche delle analisi effettuate.
- 📄 **Reportistica Professionale**: Generazione istantanea di report clinici in formato PDF.

---

## 🛠️ Architettura e Tecnologie

Oltre ai linguaggi core, il progetto sfrutta:

- **Visione**: Swin Transformer-B per la classificazione globale, YOLOv10/v11 per la localizzazione locale.
- **RAG**: ChromaDB e FastEmbed per il recupero di linee guida cliniche in tempo reale.
- **Containerizzazione**: Docker e Docker Compose per un deployment riproducibile.

---

## 🚀 Guida Rapida alla Configurazione

### 1. Preparazione dell'Ambiente

Il progetto è interamente containerizzato. Spostati nella cartella `docker/` per iniziare.

```bash
cd docker
./build.sh  # Per build standard (CPU/Mac)
# OPPURE
./build.sh gpu  # Per supporto accelerazione hardware NVIDIA
```

### 2. Avvio del Sistema

Lancia il container montando la cartella del progetto:

```bash
./run.sh ../pneumonia_project
```

### 3. Lancio dell'Interfaccia Clinica

Una volta dentro il container:

```bash
python3 -m streamlit run src/ui/app.py
```

L'applicazione sarà visibile su: **`http://localhost:8501`**

---

## 🎓 Progetto Universitario

Sviluppato come parte del corso di Laurea Magistrale in **Computer Science** presso l'**Università di Parma**. Il sistema è progettato per dimostrare l'integrazione di tecniche moderne di AI in contesti critici come quello medico.

---

<p align="center">
  <i>"L'AI non sostituisce il medico, ma lo potenzia."</i>
</p>
