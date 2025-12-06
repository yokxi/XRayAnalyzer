# Riconoscimento Proiezione: AP vs PA

## Gerarchia delle Fonti Informativa
Per determinare la proiezione corretta, segui rigorosamente questo ordine di priorità:
1.  **Dichiarazione Utente:** Se l'utente specifica nel messaggio "AP", "PA", "a letto", "portatile" o "in piedi", questa informazione ha la precedenza assoluta.
2.  **Analisi Visiva (Deduzione):** Se l'utente non specifica nulla, deduci la proiezione dai segni anatomici descritti sotto.

---

## 1. Proiezione PA (Standard / In Piedi)
È la proiezione ottimale, tipica di pazienti stabili.

**Segni Visivi Chiave:**
* **Scapole:** Sono proiettate **fuori** dai campi polmonari (laterali). I polmoni appaiono "puliti" da ossa nella parte alta.
* **Clavicole:** Hanno una forma a "V" (oblique verso il basso).
* **Bolla Gastrica:** Spesso visibile sotto il diaframma sinistro.

## 2. Proiezione AP (A Letto / Portatile)
Tipica di pazienti gravi, allettati o in terapia intensiva. È la più "ingannevole" per l'AI.

**Segni Visivi Chiave:**
* **Scapole:** I bordi mediali delle scapole sono visibili **dentro** i campi polmonari (appaiono come linee verticali nei lobi superiori).
* **Clavicole:** Appaiono più **orizzontali** e proiettate molto in alto (sopra la 1° costola).
* **Cuore:** Appare ingrandito artificialmente (magnificazione geometrica).

---

### Istruzione Operativa per l'Agente (Flow Decisionale)

**STEP 0: Analisi del Prompt Utente**

L'utente ha menzionato la posizione?
* *Keywords AP:* "letto", "sdraiato", "portatile", "AP", "antero-posteriore".
* *Keywords PA:* "in piedi", "standard", "PA", "postero-anteriore".
    * **SE SÌ:** Usa questa informazione e salta allo STEP 2.
    * **SE NO:** Procedi allo STEP 1 (Analisi Visiva).

**STEP 1: Analisi Visiva (Solo se Step 0 è vuoto)**

Osserva l'immagine:
* Vedi linee verticali (scapole) dentro i polmoni? -> Deduci **AP**.
* Vedi clavicole orizzontali e alte? -> Deduci **AP**.
* Altrimenti -> Deduci **PA**.

**STEP 2: Applicazione delle Regole Cliniche**

Ora che hai stabilito la proiezione (AP o PA):

* **CASO AP (Confermato o Dedotto):**
    1.  **Cuore:** Ignora totalmente la dimensione cardiaca. Non diagnosticare Cardiomegalia.
    2.  **Mediastino:** Accetta un allargamento superiore come artefatto di proiezione.
    3.  **Falsi Positivi:** Controlla che le linee delle scapole non siano state segnate da YOLO.

* **CASO PA (Confermato o Dedotto):**
    1.  L'anatomia è affidabile. Se il cuore è grande, segnala Cardiomegalia.