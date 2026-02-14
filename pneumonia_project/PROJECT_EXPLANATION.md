# XRayAnalyzer: Documentazione Tecnica del Progetto

XRayAnalyzer è un sistema avanzato di supporto clinico basato su Intelligenza Artificiale progettato per l'analisi di radiografie del torace (CXR) e il rilevamento della polmonite. Il sistema combina visione artificiale (Deep Learning), recupero di informazioni (RAG) e ragionamento clinico (Multimodal LLM) per fornire report diagnostici spiegabili (XAI) in tempo reale.

## 1. Architettura del Sistema

Il progetto segue una pipeline multi-fase coordinata da un "Agente Medico". L'architettura è suddivisa in componenti modulari per massimizzare la manutenibilità:

- **Interfaccia Utente (Streamlit)**: Frontend reattivo "Medical-Grade" con streaming dei passi di ragionamento e gestione dei tab analitici. Utilizza stili centralizzati in `src/ui/styles.py`.
- **Agente di Ragionamento (`MedicalAgent`)**: L'orchestratore che gestisce il flusso di dati in streaming e la logica di arbitrato tra modelli.
- **Strumenti Specialistici (`VisionTool`, `RagTool`)**: Modelli di visione per l'analisi e localizzazione (Swin-B + YOLO Ensemble), e base di conoscenza vettoriale (ChromaDB).
- **Dashboard Performance**: Modulo per il calcolo in tempo reale di KPI e visualizzazione analitica.

---

## 2. Punti Chiave per l'Esposizione (Highlight)

Se dovessi presentare il progetto, questi sono i 3 pilastri fondamentali:

1.  **Trasparenza (XAI)**: Il sistema non è una "scatola nera". Grazie allo streaming dei passi di ragionamento, il medico vede _perché_ l'AI ha preso una decisione.
2.  **Affidabilità tramite Ensemble**: La fusione di 3 modelli diversi (Swin per il globale, 2 YOLO per il locale) riduce drasticamente i margini di errore rispetto a un modello singolo.
3.  **User Experience Clinica**: Dalla schermata di caricamento "respirante" al report PDF ufficiale, ogni dettaglio è pensato per integrarsi in un flusso di lavoro ospedaliero reale.

---

## 3. Pipeline di Analisi Passo-Passo (Streaming Mode)

Il sistema permette al clinico di osservare il processo decisionale dell'IA in tempo reale.

### Fase 0: Inizializzazione & Medical Loading

All'avvio o durante il caricamento dei modelli, viene visualizzata una schermata tematica con animazione respiratoria dei polmoni e scanner laser verticale per fornire feedback immediato sulla reattività del sistema.

### Fase 1: Ottimizzazione e Classificazione (Vision Init)

- **CLAHE**: L'immagine viene normalizzata per migliorare il contrasto locale.
- **Ensemble Vision**: Utilizzo di **Swin-B Transformer** (classificazione globale) ed Ensemble **YOLOv10 + YOLOv11** (localizzazione).
- **TTA (Test Time Augmentation)**: Opzionale per aumentare la precisione nella localizzazione delle opacità.

### Fase 2: Analisi Tecnica e Proiezione

- L'LLM analizza la qualità dell'immagine e la proiezione (AP/PA).
- Cross-check tra metadati utente ed evidenza visiva per validare il posizionamento.

### Fase 3: Analisi Arbitrata per Aree Focali

Se YOLO rileva anomalie:

1. **Extraction & Fusion**: Fusione delle rilevazioni tramite **Weighted Box Fusion (WBF)**.
2. **Crop Extraction**: Estrazione di ritagli ad alta risoluzione 1024px.
3. **RAG Validation**: Consultazione della base di conoscenza clinica per i criteri diagnostici.
4. **Arbitrato**: L'LLM valida l'area per confermare la polmonite o escludere artefatti (es. scapole, calcificazioni).

### Fase 4: Analisi delle Opacità Diffuse (Fallback)

Se il classificatore globale è positivo ma YOLO non trova box, l'Agente cerca segni di **velatura diffusa** o pattern interstiziali non focalizzati.

### Fase 5: Sintesi Finale e Diagnosi

Generazione del report XAI comprensivo di:

- **Punteggio di Confidenza** e Anomalie Focali.
- **Livello di Gravità**: Calcolato dinamicamente (Alta/Moderata/Bassa).
- **Qualità Scansione**: Indicatori sulla risoluzione del reperto.

---

## 4. Dashboard Performance AI

Monitoraggio delle prestazioni basato sull'archivio storico:

- **KPI Cards**: Totale analisi, Casi Positivi/Negativi, Confidenza Media.
- **Visual Analytics**: Grafici Altair color-coded (Red/Green) per la distribuzione dei casi diagnostici.

---

## 5. Classi e Metodi Principali

### `MedicalAgent` (src/agent/brain.py)

- `run_full_pipeline_streaming(...)`: Metodo generatore che gestisce il flusso asincrono verso la UI.
- `call_hpc(...)`: Gestisce la comunicazione multimodale (Qwen-VL-72B).

### `Archive` (src/utils/archive.py)

- Gestione database locale strutturato.
- `compute_image_hash()`: Previene duplicati tramite MD5 dell'immagine originale.
- Serializzazione completa dei metadati e delle immagini di ragionamento (crops).

### `PDFGenerator` (src/utils/pdf_generator.py)

- Generazione dinamica PDF con `FPDF`.
- Include sintesi diagnostica, passi di ragionamento e disclaimer medico.

---

## 6. Specifiche Tecniche per Esperti (Q&A)

**Q: Come viene gestita la discordanza tra Swin-B e YOLO?**

- **Risposta**: Tramite **Logica di Arbitrato**. L'Agente sfida l'LLM multimodale a validare i ritagli YOLO se il classificatore globale differisce, riducendo i falsi positivi da artefatti ossei.

**Q: Come garantite l'integrità dei dati salvati?**

- **Risposta**: Ogni analisi è legata all'hash MD5 dell'RX. Caricando la stessa immagine, il sistema recupera l'analisi esistente invece di duplicarla.

**Q: Come viene ottimizzata la latenza LLM?**

- **Risposta**: Le immagini vengono ridimensionate proporzionalmente a 1024px prima del caricamento, garantendo il miglior bilanciamento tra dettaglio diagnostico e velocità di risposta.

---

## 7. Tecnologie Utilizzate

- **Vision Core**: Swin Transformer-B, YOLOv11 (L), YOLOv10 (L).
- **Intelligence**: Qwen-VL-72B (Multimodal reasoning), ChromaDB (RAG).
- **Frontend**: Streamlit 1.41+ (Custom Theme #1d4ed8), Altair Charts.
- **Backend**: Python 3.12, PyTorch, OpenCV, FPDF.
