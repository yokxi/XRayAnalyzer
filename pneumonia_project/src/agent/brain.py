import streamlit as st
import base64
import io
from openai import OpenAI
from src import config
from src.tools.vision import VisionTool
from src.tools.rag import RagTool

class MedicalAgent:
    def __init__(self):
        self.client = OpenAI(base_url=config.HPC_ENDPOINT, api_key="EMPTY")
        self.model_name = config.HPC_MODEL_NAME
        self.vision = VisionTool()
        self.rag = RagTool()

    def encode_image(self, pil_img):
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def call_hpc(self, prompt, pil_img):
        """Helper for single multimodal call to HPC"""
        base64_img = self.encode_image(pil_img)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_img}"}
                        },
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content

    def _update_status(self, text, icon="fa-spinner fa-spin"):
        """Aggiorna lo stato visivo e invia una notifica toast."""
        st.toast(text, icon="🩺")
        st.markdown(f"""
            <div class="progress-step active">
                <div class="step-icon"><i class="fa-solid {icon}"></i></div>
                <div style="font-size: 0.9rem; font-weight: 600; color: #ffffff;">{text}</div>
            </div>
        """, unsafe_allow_html=True)

    def run_full_pipeline(self, image_path, user_query, user_metadata=None):
        # 1. Vision Analysis (Swin-B + YOLO)
        self._update_status("Esecuzione Vision Ensemble (Swin-B + YOLO11)...", "fa-eye")
        cls_data, detections, clahe_img = self.vision.analyze(image_path)

        full_reasoning = ""

        # --- STEP 1: TECHNICAL ANALYSIS ---
        self._update_status("Sintesi del Contesto Statico (Proiezione e Allineamento)...", "fa-gears")
        rag_tech = self.rag.search("protocollo riconoscimento proiezione AP PA", k=2)
        tech_prompt = f"""
        Analyze this full chest radiograph.
        1. Determine if the projection is AP or PA based on standard medical protocols: {rag_tech}.
        2. Note: User declared: {user_metadata if user_metadata else 'No specific metadata provided'}.
        3. Evaluate image quality, inspiration, and centering.
        IMPORTANT: Please provide the analysis in ITALIAN.
        """
        tech_analysis = self.call_hpc(tech_prompt, clahe_img)
        full_reasoning += f"### 1. Analisi Tecnica e Posizionamento\n{tech_analysis}\n\n"

        # --- STEP 2: ARBITRATED ANALYSIS ---
        if len(detections) > 0:
            self._update_status(f"Validazione di {len(detections)} aree focali sospette...", "fa-target-sharp")
            for i, det in enumerate(detections):
                rag_context = self.rag.search(f"validazione {det['location_text']} {det['diagnosis']}", k=3)

                arbitrator_note = ""
                if not cls_data['is_positive']:
                    arbitrator_note = "CRITICAL ALERT: Global classifier is NEGATIVE. Verify if this area is an ARTIFACT (e.g., bone structure, device)."

                det_prompt = f"""
                Analyze this CROP of the suspected area: {det['location_text']}.
                Follow this RAG validation protocol:
                {rag_context}

                {arbitrator_note}
                Describe the texture (reticular, nodular, etc.) and confirm if it is pathological opacity or an artifact.
                IMPORTANT: Please provide the analysis in ITALIAN.
                """

                det_analysis = self.call_hpc(det_prompt, det['image_crop'])
                full_reasoning += f"### 2.{i+1} Analisi Area Focale: {det['location_text']}\n{det_analysis}\n\n"
        else:
            # Case where Swin-B is positive but YOLO found no boxes
            if cls_data['is_positive']:
                self._update_status("Ricerca di opacità diffuse (Pattern a Vetro Smerigliato)...", "fa-magnifying-glass-plus")
                diffuse_prompt = "Global classifier predicts positive for pneumonia, but no focal boxes were found. Look for signs of diffuse veiling, interstitial patterns, or ground-glass opacities. IMPORTANT: Please provide the analysis in ITALIAN."
                diffuse_analysis = self.call_hpc(diffuse_prompt, clahe_img)
                full_reasoning += f"### 2. Analisi Opacità Diffusa\n{diffuse_analysis}\n"
            else:
                self._update_status("Finalizzazione del report dei reperti negativi...", "fa-file-shield")
                full_reasoning += "### 2. Analisi Patologica\nNessuna anomalia focale o globale rilevata dai modelli di visione. I risultati sono coerenti con un esame normale."

        return full_reasoning, clahe_img, detections, cls_data