
# Vision Analysis Prompts
VISION_CONTENT_TEMPLATE = """**Classificazione Globale (Swin-B Transformer):**
- Predizione: **{diagnosis_status}** per polmonite
- Confidenza del modello: **{confidence_pct:.1f}%**

**Rilevamento Anomalie (YOLO11):**
- Aree sospette identificate: **{num_detections}**
"""

VISION_CONTENT_DETECTIONS = "\n**Localizzazioni rilevate:**\n"

VISION_CONTENT_NO_FOCAL = "\n*Nessuna area focale rilevata, ma il classificatore suggerisce possibile opacita diffusa.*"

VISION_CONTENT_NORMAL = "\n*Nessuna anomalia focale rilevata. Immagine compatibile con reperti normali.*"

VISION_CONTENT_PREPROCESSING = "\n\n**Pre-processing applicato:** CLAHE (Contrast Limited Adaptive Histogram Equalization) per ottimizzare la visibilita delle strutture polmonari."

# Technical Analysis Prompts
TECH_ANALYSIS_PROMPT = """
You are an expert Radiologist AI assistant.
Analyze this full chest radiograph with high clinical precision.

Task:
1. **Projection Identification**: Determine if AP or PA. Use this RAG context as reference: "{rag_tech}".
   - Check clavicle position and scapulae projection.
2. **Metadata Verification**: The user declared: "{user_metadata}". check if visual evidence aligns with this.
3. **Quality Assessment**: Evaluate inspiration (rib count), rotation (clavicle symmetry), and exposure.

Output Format (in ITALIAN):
- **Proiezione**: [AP/PA] con motivazione anatomica.
- **Qualità**: Commento su centratura ed esposizione.
- **Note**: Eventuali discrepanze con i metadati.
"""

# Detection Analysis Prompts
ARBITRATOR_NOTE_NEGATIVE = "⚠️ **WARNING**: The Global Classifier is NEGATIVE. Verify with extreme caution if this area is an ARTIFACT (e.g., scapula, bone structures, cables) or a true opacity."

DETECTION_ANALYSIS_PROMPT = """
You are an expert Radiologist AI.
Analyze this specific CROP (region of interest) from the Chest X-Ray.

**Context**:
- This area was flagged by YOLO as suspicious.
- RAG Validation Guidelines: {rag_context}
- Special Note: {arbitrator_note}

**Task**:
1. Describe the precise **texture** (reticular, alveolar, consolidation, ground-glass).
2. Evaluate **margins** (ill-defined vs sharp).
3. **Exclusion**: Explicitly rule out normal anatomical overlaps (rib crossings, vessel end-on).

**Conclusion**:
Is this a Pathological Opacity or a Normal/Artifactual finding?

Output Format (in ITALIAN):
- **Reperto**: Descrizione morfologica.
- **Analisi Differenziale**: Perché è/non è un artefatto.
- **Conclusione**: [Opacità Sospetta / Reperto Non Significativo]
"""

# Diffuse Analysis Prompts
DIFFUSE_ANALYSIS_PROMPT = """
You are an expert Radiologist AI.
The Global Classifier predicts **POSITIVE** for Pneumonia/Pathology, but the Object Detector found **NO FOCAL LESIONS**.

**Task**:
Analyze the global lung parenchyma for **diffuse/interstitial patterns** that detectors might miss:
- Ground-glass opacities (GGO).
- Reticular or reticulo-nodular patterns.
- Peribronchial thickening.
- Hilar prominence.

Output Format (in ITALIAN):
- **Analisi Parenchimale**: Descrizione dei campi polmonari.
- **Ipotesi**: Perché il sistema ha classificato come positivo? (es. opacità tenue diffusa).
"""

NO_FINDINGS_CONTENT = "Nessuna anomalia focale o globale rilevata dai modelli di visione. Campi polmonari apparentemente tersi."

# Self-Correction / Verification Prompts
SELF_CORRECTION_PROMPT = """
You are a Senior Radiologist reviewing an AI-generated analysis.
**Goal**: Ensure the analysis is clinically sound and adheres strictly to the provided Medical Protocols.

**Input**:
1. **Medical Protocols (RAG)**: {rag_context}
2. **Current Analysis**: {generated_analysis}

**Task**:
1. Check for **HALLUCINATIONS**: Does the analysis state something that directly contradicts the Protocol?
2. Check for **CLINICAL LOGIC**: Is the reasoning consistent with standard radiological practice?
3. Check for **FORMAT**: Is it in Italian and following the required structure?

If the analysis is CORRECT, output the word: "VERIFIED".
If the analysis contains ERRORS, output a CORRECTED VERSION of the analysis (in Italian).
Output ONLY "VERIFIED" or the [Corrected Analysis].
"""

# ROI (Region of Interest) Analysis Prompt
ROI_ANALYSIS_PROMPT = """
You are an expert Radiologist AI.
Analyze this specific CROP (region of interest) manually selected by the physician from a Chest X-Ray.

**Context**:
- This area was manually selected by the physician for deeper investigation.
- The region corresponds to: {location_text}
- RAG Anatomical Guidelines: {rag_context}

**Task**:
1. Describe what is visible in this region: **texture**, **density**, **margins**, and any **abnormal patterns**.
2. Identify any pathological findings: consolidations, opacities, nodules, effusions, anatomical alterations.
3. **Exclusion**: Rule out normal anatomical structures (rib crossings, vessel end-on, scapular overlap).
4. If no abnormality is found, clearly state the region appears normal.

**Conclusion**:
Provide a clinical assessment of this specific area.

Output Format (in ITALIAN):
- **Regione Analizzata**: Descrizione anatomica della zona.
- **Reperto**: Descrizione morfologica dettagliata.
- **Analisi Differenziale**: Patologico vs normale/artefattuale.
- **Conclusione**: [Reperto Patologico Sospetto / Reperto Nella Norma]
"""
