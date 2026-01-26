# import streamlit as st
# import base64
# import io

# from openai import OpenAI
# # import config
# from src import config

# from src.tools.vision import VisionTool
# from src.tools.rag import RagTool

# class MedicalAgent:
#     def __init__(self):
#         # Client per l'HPC (standard OpenAI via vLLM)
#         self.client = OpenAI(base_url=config.HPC_ENDPOINT, api_key="EMPTY")
#         self.model_name = config.HPC_MODEL_NAME
        
#         # Carichiamo i tool una sola volta (grazie al caching di streamlit in app.py)
#         self.vision = VisionTool()
#         self.rag = RagTool()

#     def encode_image(self, pil_img):
#         buffered = io.BytesIO()
#         pil_img.save(buffered, format="PNG")
#         return base64.b64encode(buffered.getvalue()).decode('utf-8')

#     def run_full_pipeline(self, image_path, user_query, user_metadata=None):
#         """Esegue l'intera catena XAI"""
        
#         # 1. Vision Analysis
#         cls_data, detections, clahe_img = self.vision.analyze(image_path)
        
#         # 2. RAG Search (Algoritmico)
#         # Cerchiamo protocolli basati sulla query e sulle zone trovate da YOLO
#         search_terms = f"{user_query} " + " ".join([d['location_text'] for d in detections])
#         rag_context = self.rag.search(search_terms, k=4)
        
#         # 3. Logica Arbitro per il Prompt
#         arbitrator_note = ""
#         if not cls_data['is_positive'] and len(detections) > 0:
#             arbitrator_note = "ALERT ARBITRO: Il Classificatore Globale non vede polmonite, ma YOLO ha trovato dei box. Verifica con massimo rigore se sono ARTEFATTI (Capezzoli, Scapole, Dispositivi)."
#         elif cls_data['is_positive'] and len(detections) == 0:
#             arbitrator_note = "ALERT ARBITRO: Sospetta polmonite diffusa rilevata, ma nessun box isolato. Cerca segni di Ground-Glass Opacity (GGO) diffusa."

#         system_prompt = f"""
#         SEI UN RADIOLOGO ESPERTO (SOTA EXPLAINABLE AI). 
#         Il tuo compito è validare i rilevamenti dei modelli AI.
        
#         === DATI DI PARTENZA ===
#         - Stato Classificatore: {'POSITIVO' if cls_data['is_positive'] else 'NEGATIVO'} (Conf: {cls_data['confidence']:.2f})
#         - Info Utente: {user_metadata if user_metadata else 'Nessuna'}
        
#         === PROTOCOLLI ALGORITMICI (RAG) ===
#         {rag_context}
        
#         === ISTRUZIONI XAI ===
#         1. {arbitrator_note}
#         2. Per ogni area sospetta, applica i protocolli RAG passo dopo passo.
#         3. Se l'utente ha dichiarato AP/PA, quella è la verità assoluta.
#         4. PRODUCI UN RAGIONAMENTO LOGICO (Chain of Thought) prima della diagnosi finale.
#         """

#         # 4. Preparazione Input per HPC
#         contents = [{"type": "text", "text": f"Domanda Clinica: {user_query}"}]
        
#         # Aggiungiamo l'immagine intera per il contesto (AP/PA, ecc.)
#         contents.append({"type": "text", "text": "Immagine Intera (Contesto Tecnico):"})
#         contents.append({
#             "type": "image_url",
#             "image_url": {"url": f"data:image/png;base64,{self.encode_image(clahe_img)}"}
#         })

#         # Aggiungiamo i crop per il dettaglio
#         for i, det in enumerate(detections):
#             contents.append({"type": "text", "text": f"Dettaglio Area {det['location_text']}:"})
#             contents.append({
#                 "type": "image_url",
#                 "image_url": {"url": f"data:image/png;base64,{self.encode_image(det['image_crop'])}"}
#             })

#         # 5. Chiamata all'HPC
#         response = self.client.chat.completions.create(
#             model=self.model_name,
#             messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": contents}],
#             temperature=0.1,
#             max_tokens=2000
#         )
        
#         return response.choices[0].message.content, clahe_img, detections, cls_data
# ----------------------------------------------------------------------------------------------------------------------------------------
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
        """Helper per singola chiamata multimodale all'HPC"""
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

    def run_full_pipeline(self, image_path, user_query, user_metadata=None):
        # 1. Vision Analysis (Swin-B + YOLO)
        cls_data, detections, clahe_img = self.vision.analyze(image_path)
        
        full_reasoning = ""
        
        # --- STEP 1: ANALISI TECNICA (Immagine Intera) ---
        st.write("--- 🔍 Fase 1: Analisi Tecnica Globale ---")
        rag_tech = self.rag.search("protocollo riconoscimento proiezione AP PA", k=2)
        tech_prompt = f"""
        Analizza questa radiografia intera. 
        1. Determina se la proiezione è AP o PA basandoti sui protocolli: {rag_tech}.
        2. Nota: L'utente ha dichiarato: {user_metadata if user_metadata else 'Nessuna specifica'}.
        3. Valuta la qualità dell'immagine e l'ispirazione.
        """
        tech_analysis = self.call_hpc(tech_prompt, clahe_img)
        full_reasoning += f"### 1. Analisi Tecnica e Posizionamento\n{tech_analysis}\n\n"

        # --- STEP 2: ANALISI ARBITRATA (Per ogni box YOLO) ---
        if len(detections) > 0:
            st.write(f"--- 🎯 Fase 2: Validazione di {len(detections)} rilevamenti ---")
            for i, det in enumerate(detections):
                rag_context = self.rag.search(f"validazione {det['location_text']} {det['diagnosis']}", k=3)
                
                arbitrator_note = ""
                if not cls_data['is_positive']:
                    arbitrator_note = "ALERT: Il classificatore globale è negativo. Verifica con sospetto di ARTEFATTO."
                
                det_prompt = f"""
                Analizza questo dettaglio (CROP) dell'area: {det['location_text']}.
                Protocollo RAG da seguire:
                {rag_context}
                
                {arbitrator_note}
                Descrivi la texture e conferma se si tratta di opacità patologica o artefatto.
                """
                
                det_analysis = self.call_hpc(det_prompt, det['image_crop'])
                full_reasoning += f"### 2.{i+1} Analisi Area: {det['location_text']}\n{det_analysis}\n\n"
        else:
            # Caso in cui Swin-B è positivo ma YOLO non trova box
            if cls_data['is_positive']:
                st.write("--- 🧠 Fase 2: Ricerca opacità diffusa ---")
                diffuse_prompt = "Il classificatore globale segnala opacità, ma non ci sono box focali. Cerca segni di velatura diffusa o vetro smerigliato."
                diffuse_analysis = self.call_hpc(diffuse_prompt, clahe_img)
                full_reasoning += f"### 2. Analisi Opacità Diffusa\n{diffuse_analysis}\n"
            else:
                full_reasoning += "### 2. Analisi Patologica\nNessuna anomalia focale o globale rilevata dai modelli di visione."

        return full_reasoning, clahe_img, detections, cls_data