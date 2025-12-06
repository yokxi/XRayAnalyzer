# Protocollo di Annotazione RSNA Pneumonia Challenge

## Definizione della Classe Target "Lung Opacity"
**Nota Critica:** Nel dataset RSNA, la classe target (Class 1) è etichettata genericamente come **"Lung Opacity"**, non specificamente come "Bacterial Pneumonia".

**Cosa include la classe 1 (Target):**
1.  Polmonite batterica/virale (Consolidamenti).
2.  Infiltrati polmonari non specifici.
3.  Atelettasie (collasso parziale del polmone).
4.  Noduli polmonari sospetti.

**Cosa è Classe 0 (Normal / No Opacity):**
1.  Polmoni completamente sani.
2.  Altre patologie che NON sono opacità (es. Pneumotorace, Fratture costali, Cardiomegalia senza opacità).

### Istruzione Operativa per l'Agente
Quando YOLO rileva una classe positivo:
1.  Non saltare alla conclusione "È sicuramente Polmonite Batterica".
2.  Formula il referto così: **"Rilevata Opacità Polmonare (Lung Opacity) compatibile con quadro infiammatorio/infettivo..."**.
3.  Usa il RAG clinico (sintomi, se presenti) per raffinare la diagnosi tra Polmonite e altre opacità (es. atelettasia).