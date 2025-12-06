# Artefatti Anatomici e Falsi Positivi

## 1. Ombre dei Capezzoli (Nipple Shadows)
**Descrizione Visiva:** Opacità nodulari, rotondeggianti o ovali, spesso parzialmente sfumate.

**Posizione Tipica:** Campi polmonari inferiori, proiettati spesso sul 5° o 6° arco costale anteriore.

**Rischio:** YOLO le classifica erroneamente come noduli o polmonite focale.

### Istruzione Operativa per l'Agente
Se YOLO rileva un'opacità rotonda nel campo inferiore:
1.  **Check Bilateralità:** Controlla il polmone opposto alla stessa altezza. Esiste un'ombra simile?
2.  **Check Simmetria:** Sono simmetrici rispetto alla colonna vertebrale?
3.  **Decisione:**
    * SE Simmetrici/Bilaterali -> Classifica come **Artefatto (Nipple Shadow)**. Ignora l'alert di YOLO.
    * SE Unilaterale -> Mantieni il sospetto clinico ma segnala bassa confidenza.

---

## 2. Bordo Mediale della Scapola
**Descrizione Visiva:** Linea verticale o leggermente obliqua, molto netta su un lato (laterale) e sfumata sull'altro.

**Causa:** Rotazione insufficiente delle spalle del paziente durante l'acquisizione, che proietta la scapola dentro il campo polmonare.

**Rischio:** YOLO interpreta il bordo osseo come "Pneumotorace" (se vede la linea) o "Opacità" (se vede l'osso sovrapposto).

### Istruzione Operativa per l'Agente
Se YOLO rileva un'opacità lineare verticale nella periferia superiore/media:
1.  **Analisi Bordo:** Il bordo laterale è perfettamente netto e continuo?
2.  **Analisi Continuità:** Segui la linea verso l'alto. Si connette alla struttura ossea della spalla?
3.  **Decisione:**
    * SE Connessa alla spalla -> Classifica come **Scapola**. Diagnosi: Paziente mal posizionato, non malato.

---

## 3. Bottone Aortico (Aortic Knuckle)
**Descrizione Visiva:** Prominenza tondeggiante e ben definita del mediastino superiore sinistro.

**Posizione:** Immediatamente sopra l'ombra cardiaca, a sinistra della trachea.

**Rischio:** YOLO lo scambia per una massa mediastinica o un consolidamento.

### Istruzione Operativa per l'Agente
Se YOLO segna un box sopra il cuore a sinistra:
1.  **Check Anatomico:** L'area corrisponde all'arco aortico?
2.  **Check Densità:** È omogenea e con bordi lisci?
3.  **Decisione:** È una struttura anatomica normale (**Bottone Aortico**). Non è patologico.