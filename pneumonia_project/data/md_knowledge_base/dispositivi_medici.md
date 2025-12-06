# Dispositivi Medici e Corpi Estranei

## 1. Pacemaker e ICD (Dispositivi Cardiaci)
**Descrizione Visiva:**
* **Generatore:** Oggetto ovale con densità metallica (bianco assoluto/uniforme) e bordi netti e geometrici. Solitamente sottoclavicolare (sinistra o destra).
* **Leads (Elettrocateteri):** Linee sottili, continue, ad alta densità (fili metallici) che partono dal generatore e vanno verso il cuore.

### Istruzione Operativa per l'Agente
Se YOLO rileva un'opacità ad altissima densità:
1.  **Check Geometria:** L'oggetto ha una forma artificiale (rettangolo smussato, ovale perfetto)?
2.  **Check Connessioni:** Ci sono fili metallici che escono dall'oggetto?
3.  **Decisione:**
    * SE Geometria artificiale + Fili -> Classifica come **Device Medico (Pacemaker)**.
    * **IMPORTANTE:** I pacemaker NON sono polmonite. Segnalare come "Presenza di device", non come patologia polmonare.

---

## 2. Elettrodi ECG e Clip Chirurgiche
**Descrizione Visiva:**
* **Elettrodi:** Cerchietti o bottoni metallici sparsi sulla superficie toracica esterna.
* **Clip:** Piccoli punti metallici (spesso a forma di V o doppi punti) nel mediastino o ascelle.

### Istruzione Operativa per l'Agente
Se YOLO rileva piccoli punti bianchi multipli:
1.  **Analisi Densità:** Sono "bianco metallico" (più bianchi dell'osso)?
2.  **Analisi Pattern:** Sono sparsi in modo casuale o seguono pattern chirurgici?
3.  **Decisione:** Sono artefatti esterni. Ignorare nella diagnosi di polmonite.