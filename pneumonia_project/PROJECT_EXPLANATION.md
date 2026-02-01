# XRayAnalyzer: Documentazione Tecnica del Progetto

XRayAnalyzer è un sistema avanzato di supporto clinico basato su Intelligenza Artificiale progettato per l'analisi di radiografie del torace (CXR) e il rilevamento della polmonite. Il sistema combina visione artificiale (Deep Learning), recupero di informazioni (RAG) e ragionamento clinico (Multimodal LLM) per fornire report diagnostici spiegabili (XAI) in tempo reale.

## 1. Architettura del Sistema

Il progetto segue una pipeline multi-fase coordinata da un "Agente Medico". L'architettura è suddivisa in quattro componenti principali:

- **Interfaccia Utente (Streamlit)**: Frontend reattivo "Medical-Grade" con streaming dei passi di ragionamento e gestione dei tab analitici.
- **Agente di Ragionamento (`MedicalAgent`)**: L'orchestratore che gestisce il flusso di dati in streaming e la logica di arbitrato tra modelli.
- **Strumenti Specialistici (`VisionTool`, `RagTool`)**: Modelli di visione per l'analisi e localizzazione, e base di conoscenza vettoriale per il supporto clinico.
- **Sottosistema di Persistenza & Reportistica**: Modulo `Archive` per la memorizzazione storica delle analisi e `PDFGenerator` per la creazione di report clinici ufficiali.

---

## 2. Pipeline di Analisi Passo-Passo (Streaming Mode)

A differenza dei sistemi tradizionali, XRayAnalyzer utilizza una pipeline **streaming** che permette al clinico di osservare il processo decisionale dell'IA mentre avviene.

### Fase 1: Ottimizzazione e Classificazione (Vision Init)

- **CLAHE**: L'immagine viene normalizzata per migliorare il contrasto locale.
- **Ensemble Vision**: Il sistema utilizza una combinazione di due modelli allo stato dell'arte: **Swin-B Transformer** per la classificazione globale e un **Ensemble di YOLOv10 + YOLOv11** per la localizzazione precisa delle anomalie focali.
- **Risultato**: Viene calcolato un punteggio di confidenza iniziale e mappate le aree di interesse.

### Fase 2: Analisi Tecnica e Proiezione

- In questa fase l'LLM, supportato dal RAG, analizza la qualità dell'immagine e la proiezione (AP/PA).
- Il sistema incrocia i metadati dichiarati dall'utente (es. proiezione specificata nella sidebar) con l'evidenza visiva per validare la correttezza del posizionamento del paziente.

### Fase 3: Analisi Arbitrata per Aree Focali

Se l'Ensemble YOLO rileva anomalie (bounding boxes), l'Agente attiva un'analisi specifica per ogni area:

1. **Extraction & Fusion**: Le rilevazioni di YOLOv10 e YOLOv11 vengono fuse tramite **Weighted Box Fusion (WBF)** per ridurre i falsi positivi.
2. **Crop Extraction**: Viene estratto un ritaglio ad alta risoluzione dell'area sospetta.
3. **RAG Validation**: Si interrogano i manuali medici per ottenere criteri di validazione per quella specifica zona anatomica.
4. **Arbitrato**: L'LLM funge da arbitro. Se il classificatore globale è negativo ma l'Ensemble YOLO è positivo, l'LLM viene istruito con un "Critical Alert" per verificare se si tratti di una falsa rilevazione (es. artefatto osseo) o di una polmonite incipiente.

### Fase 4: Analisi delle Opacità Diffuse (Fallback)

Se il classificatore globale rileva polmonite ma non ci sono box YOLO focali, il sistema attiva un'analisi per cercare segni di **velatura diffusa** o pattern interstiziali che non occupano un'area geometrica definita.

### Fase 5: Sintesi Finale e Generazione Report

Tutti i passi di ragionamento vengono sintetizzati in un report XAI coerente. L'utente può quindi:

- Visualizzare il ragionamento completo nel modale dedicato.
- Generare un **Report PDF** con timbro temporale e metadati.
- **Salvare in Archivio** l'analisi (con gestione automatica dei duplicati tramite hash MD5).

---

## 3. Classi e Metodi Principali

### `MedicalAgent` (src/agent/brain.py)

- `run_full_pipeline_streaming(...)`: Metodo generatore (yield) che gestisce il flusso asincrono dei dati verso la UI.
- `call_hpc(...)`: Gestisce la comunicazione multimodale con il server di calcolo (Qwen-VL-72B).

### Utilities di Archiviazione (`src/utils/archive.py`)

- Gestisce il database locale delle analisi tramite un sistema di file strutturato.
- `compute_image_hash()`: Previene il salvataggio duplicato della stessa immagine.
- Serializzazione JSON per i metadati e PNG per i risultati visivi (originale, processata, YOLO crops).

### `PDFGenerator` (src/utils/pdf_generator.py)

- Utilizza `FPDF` per creare un documento clinico strutturato.
- Include sintesi diagnostica color-coded, passi di ragionamento e disclaimer medico.

---

## 4. Specifiche Tecniche per Esperti (Q&A Ready)

**Q: Come viene gestita la discordanza tra Swin-B (globale) e YOLO (locale)?**

- **Risposta**: Attraverso la **Logica di Arbitrato**. Se YOLO trova un'anomalia che il classificatore globale non ritiene patologica, l'Agente passa un prompt di "sfida" all'LLM multimodale, chiedendogli di validare specificamente il ritaglio (crop) dell'area per escludere artefatti comuni (es. scapole sovrapposte, calcificazioni costali).

**Q: Quali sono i vantaggi della pipeline di streaming?**

- **Risposta**: Trasparenza e fiducia clinica. Il radiologo non riceve solo un "Sì/No", ma può seguire il "filo del pensiero" dell'IA mentre analizza la qualità dell'immagine, consulta la base di conoscenza e valida ogni singola lesione individuata.

**Q: Come garantite l'integrità dei dati salvati?**

- **Risposta**: Ogni analisi salvata nell'archivio è legata a un hash MD5 dell'immagine originale. Se un utente prova a salvare nuovamente la stessa immagine, il sistema lo rileva e impedisce la duplicazione, mantenendo l'archivio pulito e coerente.

**Q: Quali sono i parametri di "stabilità" dell'LLM?**

- **Risposta**: Usiamo una **Temperature di 0.1** per massimizzare la precisione tecnica e ridurre le allucinazioni. Inoltre, il prompt include vincoli rigorosi di formattazione in markdown per garantire che tutte le fasi vengano visualizzate correttamente nella UI.

---

## 5. Tecnologie Utilizzate

- **Visione Profonda**: PyTorch, Ultralytics YOLOv11 + YOLOv10 (1024px input), Swin Transformer-B.
- **RAG & Knowledge Base**: ChromaDB (persistente), FastEmbed (E5-large), LangChain.
- **LLM Core**: Qwen-VL-72B gestito via protocollo OpenAI-compatible.
- **Backend & Logica**: Python 3.12, OpenCV (CLAHE).
- **Frontend**: Streamlit 1.41+ con CSS custom, Google Fonts (Outfit) e Font Awesome 6.
- **Reportistica**: FPDF library per la generazione dinamica di PDF.
- **Storage**: JSON + File System strutturato per l'archiviazione (Persistence Layer).
