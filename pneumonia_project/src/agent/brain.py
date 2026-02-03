import streamlit as st
import base64
import io
import json
from PIL import Image
from openai import OpenAI
from src import config
from src.tools.vision import VisionTool
from src.tools.rag import RagTool
from src.agent import prompts

class MedicalAgent:
    def __init__(self):
        self.client = OpenAI(base_url=config.HPC_ENDPOINT, api_key="EMPTY")
        self.model_name = config.HPC_MODEL_NAME
        self.vision = VisionTool()
        self.rag = RagTool()

    def generate_queries(self, base_query: str) -> list:
        """Genera varianti cliniche della query per migliorare la recall del RAG."""
        prompt = f"""
        Generate 3 diverse clinical search queries for a medical RAG system based on this input: "{base_query}".
        Focus on technical synonyms, anatomical landmarks, and pathological terms.
        Output ONLY a JSON list of strings.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            queries = data.get("queries", list(data.values())[0]) if isinstance(data, dict) else data
            return queries[:3]
        except:
            return [base_query]

    def encode_image(self, pil_img):
        # Resize if too large to improve LLM latency
        max_size = 1024
        if max(pil_img.size) > max_size:
            pil_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

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

    def verify_and_correct(self, generated_analysis, rag_context):
        """Self-Correction loop: checks analysis against RAG context and corrects if needed."""
        verify_prompt = prompts.SELF_CORRECTION_PROMPT.format(
            rag_context=rag_context,
            generated_analysis=generated_analysis
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": verify_prompt}],
                temperature=0.0, # Zero temp for consistency
                max_tokens=1000
            )
            result = response.choices[0].message.content.strip()

            if "VERIFIED" in result and len(result) < 20:
                print("[Self-RAG] Analisi verificata con successo.")
                return generated_analysis, False
            else:
                print("[Self-RAG] Correzione applicata dall'Agente Senior.")
                return result, True
        except Exception as e:
            print(f"[Self-RAG] Errore verifica: {e}")
            return generated_analysis, False

    def run_full_pipeline_streaming(self, image_path, user_query, user_metadata=None):
        """
        Workflow ibrido: Visione Artificiale (Swin+YOLO) seguita da Ragionamento Clinico (GPT-4o).
        Lo streaming permette alla UI di mostrare i progressi intermedi man mano che i modelli rispondono.
        """
        # Analisi computerizzata iniziale per identificare anomalie focali e stato globale
        cls_data, detections, clahe_img, yolo_img = self.vision.run_vision_analysis(image_path)

        reasoning_steps = []
        full_reasoning = ""

        # Build detailed vision analysis content
        diagnosis_status = "POSITIVA" if cls_data['is_positive'] else "NEGATIVA"
        confidence_pct = cls_data['confidence'] * 100

        vision_content = prompts.VISION_CONTENT_TEMPLATE.format(
            diagnosis_status=diagnosis_status,
            confidence_pct=confidence_pct,
            num_detections=len(detections)
        )

        if len(detections) > 0:
            vision_content += prompts.VISION_CONTENT_DETECTIONS
            for i, det in enumerate(detections):
                vision_content += f"- Area {i+1}: {det['location_text']} (confidenza: {det['confidence']*100:.1f}%)\n"
        else:
            if cls_data['is_positive']:
                vision_content += prompts.VISION_CONTENT_NO_FOCAL
            else:
                vision_content += prompts.VISION_CONTENT_NORMAL

        vision_content += prompts.VISION_CONTENT_PREPROCESSING

        # Yield initial vision results
        yield {
            "id": "vision_init",
            "title": "Elaborazione Visiva",
            "icon": "fa-eye",
            "content": vision_content,
            "image": None,
            "status": "complete"
        }, False, (None, clahe_img, yolo_img, detections, cls_data)

        # 1. Analisi Tecnica: Verifica la qualità dell'immagine e la proiezione RX tramite HPC
        # Filtro RAG: 'tecnica' per focalizzarsi su protocolli di acquisizione
        tech_queries = self.generate_queries("protocollo recognition proiezione AP PA")
        rag_tech = self.rag.search(tech_queries, k=3, category="tecnica")

        # Yield intermediate status
        yield {
            "id": "tech_analysis",
            "title": "Analisi Tecnica e Posizionamento",
            "icon": "fa-microscope",
            "content": "Analisi strutturale e di posizionamento in corso...",
            "image": None
        }, False, None

        tech_prompt = prompts.TECH_ANALYSIS_PROMPT.format(
            rag_tech=rag_tech,
            user_metadata=user_metadata if user_metadata else 'No specific metadata provided'
        )
        tech_analysis = self.call_hpc(tech_prompt, clahe_img)

        # Yield verification status
        yield {
            "id": "tech_analysis",
            "title": "Analisi Tecnica (Verifica Clinica...)",
            "icon": "fa-shield-halved",
            "content": tech_analysis + "\n\n*Verifica coerenza con protocollo RAG in corso...*",
            "image": None
        }, False, None

        # Self-Correction Step
        tech_analysis, was_corrected = self.verify_and_correct(tech_analysis, rag_tech)
        correction_suffix = " (Verificato e Corretto)" if was_corrected else " (Verificato)"

        step = {
            "id": "tech_analysis",
            "title": "Analisi Tecnica e Posizionamento" + correction_suffix,
            "icon": "fa-microscope",
            "content": tech_analysis,
            "image": None
        }
        reasoning_steps.append(step)
        full_reasoning += f"### 1. Analisi Tecnica e Posizionamento\n{tech_analysis}\n\n"
        yield step, False, None

        # Analisi Arbitrata: GPT-4o valida ogni area sospetta segnalata da YOLO
        if len(detections) > 0:
            for i, det in enumerate(detections):
                # Filtro RAG: 'anatomia' per validare i reperti focalizzati
                det_queries = self.generate_queries(f"validazione {det['location_text']} {det['diagnosis']}")
                rag_context = self.rag.search(det_queries, k=4, category="anatomia")

                arbitrator_note = ""
                if not cls_data['is_positive']:
                    arbitrator_note = prompts.ARBITRATOR_NOTE_NEGATIVE

                # Yield intermediate status
                yield {
                    "id": f"detection_{i+1}",
                    "title": f"Analisi Area: {det['location_text']}",
                    "icon": "fa-bullseye",
                    "content": "Validazione area sospetta tramite protocollo anatomico...",
                    "image": det['image_crop']
                }, False, None

                det_prompt = prompts.DETECTION_ANALYSIS_PROMPT.format(
                    location_text=det['location_text'],
                    rag_context=rag_context,
                    arbitrator_note=arbitrator_note
                )

                det_analysis = self.call_hpc(det_prompt, det['image_crop'])

                # Yield verification status
                yield {
                    "id": f"detection_{i+1}",
                    "title": f"Analisi Area {i+1} (Verifica Clinica...)",
                    "icon": "fa-shield-halved",
                    "content": det_analysis + "\n\n*Validazione anatomica finale...*",
                    "image": det['image_crop']
                }, False, None

                # Self-Correction Step
                det_analysis, was_corrected = self.verify_and_correct(det_analysis, rag_context)
                correction_suffix = " (Verificato)" if not was_corrected else " (Verificato e Corretto)"

                # Visual RAG: Cerca immagine di riferimento nell'atlante
                ref_image = self.rag.get_visual_reference(det_analysis)

                step = {
                    "id": f"detection_{i+1}",
                    "title": f"Analisi Area: {det['location_text']}" + correction_suffix,
                    "icon": "fa-bullseye",
                    "content": det_analysis,
                    "image": det['image_crop'],
                    "ref_image": ref_image
                }
                reasoning_steps.append(step)
                full_reasoning += f"### 2.{i+1} Analisi Area: {det['location_text']}\n{det_analysis}\n\n"
                yield step, False, None
        else:
            if cls_data['is_positive']:
                diffuse_analysis = self.call_hpc(prompts.DIFFUSE_ANALYSIS_PROMPT, clahe_img)

                step = {
                    "id": "diffuse_analysis",
                    "title": "Analisi Opacita Diffusa",
                    "icon": "fa-cloud",
                    "content": diffuse_analysis,
                    "image": None
                }
                reasoning_steps.append(step)
                full_reasoning += f"### 2. Analisi Opacita Diffusa\n{diffuse_analysis}\n"
                yield step, False, None
            else:
                step = {
                    "id": "no_findings",
                    "title": "Analisi Patologica",
                    "icon": "fa-check-circle",
                    "content": prompts.NO_FINDINGS_CONTENT,
                    "image": None
                }
                reasoning_steps.append(step)
                full_reasoning += f"### 2. Analisi Patologica\n{prompts.NO_FINDINGS_CONTENT}"
                yield step, False, None

        # Final yield with complete data
        reasoning_data = {
            "steps": reasoning_steps,
            "full_markdown": full_reasoning
        }
        yield None, True, (reasoning_data, clahe_img, yolo_img, detections, cls_data)

    def run_full_pipeline(self, image_path, user_query, user_metadata=None):
        """Non-streaming version for backward compatibility."""
        result = None
        for step, is_final, final_data in self.run_full_pipeline_streaming(image_path, user_query, user_metadata):
            if is_final:
                result = final_data
        return result