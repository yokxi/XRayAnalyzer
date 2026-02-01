import streamlit as st
import base64
import io
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

    def run_full_pipeline_streaming(self, image_path, user_query, user_metadata=None):
        """
        Generator that yields each reasoning step as it completes.
        Yields: (step_data, is_final, final_data)
        - step_data: the current step dict
        - is_final: True if this is the last yield with complete results
        - final_data: (reasoning_data, clahe_img, yolo_img, detections, cls_data) only on final yield
        """
        # 1. Vision Analysis (Swin-B + YOLO)
        cls_data, detections, clahe_img, yolo_img = self.vision.analyze(image_path)

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

        # --- STEP 1: ANALISI TECNICA (Immagine Intera) ---
        rag_tech = self.rag.search("protocollo riconoscimento proiezione AP PA", k=2)
        tech_prompt = prompts.TECH_ANALYSIS_PROMPT.format(
            rag_tech=rag_tech,
            user_metadata=user_metadata if user_metadata else 'No specific metadata provided'
        )
        tech_analysis = self.call_hpc(tech_prompt, clahe_img)

        step = {
            "id": "tech_analysis",
            "title": "Analisi Tecnica e Posizionamento",
            "icon": "fa-microscope",
            "content": tech_analysis,
            "image": None
        }
        reasoning_steps.append(step)
        full_reasoning += f"### 1. Analisi Tecnica e Posizionamento\n{tech_analysis}\n\n"
        yield step, False, None

        # --- STEP 2: ANALISI ARBITRATA (Per ogni box YOLO) ---
        if len(detections) > 0:
            for i, det in enumerate(detections):
                rag_context = self.rag.search(f"validazione {det['location_text']} {det['diagnosis']}", k=3)

                arbitrator_note = ""
                if not cls_data['is_positive']:
                    arbitrator_note = prompts.ARBITRATOR_NOTE_NEGATIVE

                det_prompt = prompts.DETECTION_ANALYSIS_PROMPT.format(
                    location_text=det['location_text'],
                    rag_context=rag_context,
                    arbitrator_note=arbitrator_note
                )

                det_analysis = self.call_hpc(det_prompt, det['image_crop'])

                step = {
                    "id": f"detection_{i+1}",
                    "title": f"Analisi Area: {det['location_text']}",
                    "icon": "fa-bullseye",
                    "content": det_analysis,
                    "image": det['image_crop']
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