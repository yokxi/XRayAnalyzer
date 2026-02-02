import streamlit as st
import os
from datetime import datetime
from PIL import Image
from src.agent.brain import MedicalAgent
from src.utils.pdf_generator import generate_pdf_report
from src.utils.archive import save_analysis, list_analyses, load_analysis, delete_analysis, is_already_archived, compute_image_hash

# Page Configuration
st.set_page_config(
    page_title="XRayAnalyzer | Supporto Clinico AI",
    page_icon="https://img.icons8.com/ink/color/96/lungs.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.ui.styles import EXTERNAL_LINKS, MAIN_STYLES, SPINNER_CSS, SIDEBAR_HEADER, LOADING_HTML

# Load External Resources (Font Awesome & Google Fonts)
st.markdown(EXTERNAL_LINKS + MAIN_STYLES, unsafe_allow_html=True)

# Agent Caching
@st.cache_resource(show_spinner=False)
def load_medical_agent():
    return MedicalAgent()

if "agent" not in st.session_state:
    # Custom Loading Screen
    placeholder = st.empty()
    placeholder.markdown(LOADING_HTML, unsafe_allow_html=True)

    # Load Model
    st.session_state.agent = load_medical_agent()

    # Clear Loader
    placeholder.empty()

agent = st.session_state.agent

# --- REASONING MODAL (Static - for viewing completed results) ---
@st.dialog("Ragionamento Diagnostico AI", width="large")
def show_reasoning_modal(reasoning_data):
    """Modale con tabs per ogni step di ragionamento (risultati completati)."""
    steps = reasoning_data["steps"]

    tab_titles = [f"{step['title'][:28]}..." if len(step['title']) > 28 else step['title'] for step in steps]
    tabs = st.tabs(tab_titles)

    for tab, step in zip(tabs, steps):
        with tab:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                    <i class="fa-solid {step['icon']}" style="font-size: 1.5rem; color: #60a5fa;"></i>
                    <h3 style="margin: 0; color: #ffffff;">{step['title']}</h3>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2); color: #e2e8f0; line-height: 1.7;">
                    {step['content']}
                </div>
            """, unsafe_allow_html=True)

            if step.get('image') is not None:
                st.image(step['image'], caption="Area analizzata", width=300)


@st.dialog("Ragionamento Diagnostico AI", width="large")
def show_live_reasoning_modal(pipeline_generator, file_name):
    """Modale che mostra il ragionamento in tempo reale con tabs."""
    completed_steps = []
    processed_img = None
    detections = []
    cls_data = None

    # Spinner CSS
    st.markdown(SPINNER_CSS, unsafe_allow_html=True)

    tabs_placeholder = st.empty()
    status_placeholder = st.empty()

    # Track next step info for "Analizzando..." tab
    next_step_title = "Elaborazione Visiva"
    next_step_icon = "fa-eye"
    step_count = 0

    for step, is_final, final_data in pipeline_generator:
        if is_final:
            # Save final results to session state
            reasoning_data_final, processed_img, yolo_img, detections, cls_data = final_data
            reasoning_data = {
                "steps": completed_steps,
                "full_markdown": "\n\n".join([f"### {s['title']}\n{s['content']}" for s in completed_steps])
            }
            st.session_state.current_file = file_name
            st.session_state.analysis_results = {
                'reasoning_data': reasoning_data,
                'processed_img': processed_img,
                'yolo_img': yolo_img,
                'detections': detections,
                'cls_data': cls_data
            }
            break

        # Get intermediate data
        if final_data and final_data[1] is not None:
            processed_img = final_data[1]
            yolo_img = final_data[2]
            detections = final_data[3]
            cls_data = final_data[4]

        completed_steps.append(step)
        step_count += 1

        # Determine next step info based on what's coming
        if step['id'] == 'vision_init':
            next_step_title = "Analisi Tecnica"
            next_step_icon = "fa-microscope"
        elif step['id'] == 'tech_analysis':
            if len(detections) > 0:
                next_step_title = f"Analisi Area 1/{len(detections)}"
                next_step_icon = "fa-bullseye"
            elif cls_data and cls_data['is_positive']:
                next_step_title = "Analisi Opacita Diffusa"
                next_step_icon = "fa-cloud"
            else:
                next_step_title = None  # No more steps
        elif 'detection_' in step['id']:
            det_num = int(step['id'].split('_')[1])
            if det_num < len(detections):
                next_step_title = f"Analisi Area {det_num + 1}/{len(detections)}"
                next_step_icon = "fa-bullseye"
            else:
                next_step_title = None

        # Build tabs: completed steps + "Analizzando..." tab for next step
        with tabs_placeholder.container():
            tab_titles = [s['title'][:20] + "..." if len(s['title']) > 20 else s['title'] for s in completed_steps]
            if next_step_title:
                tab_titles.append(f"{next_step_title[:18]}...")

            tabs = st.tabs(tab_titles)

            # Render completed steps
            for i, (tab, s) in enumerate(zip(tabs[:len(completed_steps)], completed_steps)):
                with tab:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <i class="fa-solid {s['icon']}" style="font-size: 1.2rem; color: #60a5fa;"></i>
                            <strong style="color: #ffffff; font-size: 1.05rem;">{s['title']}</strong>
                            <span style="margin-left: auto; background: #dcfce7; color: #166534;
                                         padding: 3px 10px; border-radius: 10px; font-size: 0.75rem;">
                                <i class="fa-solid fa-check"></i> Completato
                            </span>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;
                                    border: 1px solid rgba(255,255,255,0.2); color: #e2e8f0; line-height: 1.7;">
                            {s['content']}
                        </div>
                    """, unsafe_allow_html=True)

                    if s.get('image') is not None:
                        st.image(s['image'], caption="Area analizzata", width=280)

            # Render "Analizzando..." tab for next step
            if next_step_title and len(tabs) > len(completed_steps):
                with tabs[len(completed_steps)]:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <i class="fa-solid {next_step_icon}" style="font-size: 1.2rem; color: #94a3b8;"></i>
                            <strong style="color: #cbd5e1; font-size: 1.05rem;">{next_step_title}</strong>
                            <span style="margin-left: auto; background: rgba(59,130,246,0.2); color: #60a5fa;
                                         padding: 3px 10px; border-radius: 10px; font-size: 0.75rem;">
                                <span class="analyzing-spinner"></span> In corso
                            </span>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 10px;
                                    border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; text-align: center;">
                            <div class="analyzing-spinner" style="width: 24px; height: 24px; margin: 0 auto 12px;"></div>
                            <p style="margin: 0;">Analizzando...</p>
                        </div>
                    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(SIDEBAR_HEADER, unsafe_allow_html=True)

    st.divider()

    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; color: #64748b; margin-bottom: 10px;">METADATI CLINICI</p>', unsafe_allow_html=True)
    user_pos = st.selectbox(
        "Proiezione RX",
        ["Non Specificata", "AP (Antero-Posteriore)", "PA (Postero-Anteriore)"],
        help="Specificare la proiezione migliora la precisione del ragionamento diagnostico."
    )

    st.divider()

    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; color: #64748b;">PIPELINE DI SISTEMA</p>', unsafe_allow_html=True)

    with st.expander("Fase 1: Miglioramento Digitale"):
        st.markdown("""
            <i class="fa-solid fa-wand-magic-sparkles" style="color: #2563eb;"></i>
            **Normalizzazione CLAHE**<br>
            Ottimizza il contrasto locale per rivelare infiltrati sottili e strutture polmonari.
        """, unsafe_allow_html=True)

    with st.expander("Fase 2: Classificazione Deep"):
        st.markdown("""
            <i class="fa-solid fa-brain" style="color: #2563eb;"></i>
            **Swin-B Transformer**<br>
            Analizza le caratteristiche semantiche globali per determinare la probabilità diagnostica.
        """, unsafe_allow_html=True)

    with st.expander("Fase 3: Rilevamento Oggetti"):
        st.markdown("""
            <i class="fa-solid fa-bullseye" style="color: #2563eb;"></i>
            **Rilevamento YOLO11**<br>
            Localizza aree sospette nello spazio con bounding box ad alta precisione.
        """, unsafe_allow_html=True)

    with st.expander("Fase 4: Ragionamento Clinico"):
        st.markdown("""
            <i class="fa-solid fa-comment-medical" style="color: #2563eb;"></i>
            **LLM + RAG**<br>
            Sintetizza i risultati della visione con basi di conoscenza medica per il report XAI.
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
        <div style="background-color: #fefce8; padding: 1rem; border-radius: 8px; border: 1px solid #fef08a;">
            <p style="color: #854d0e; font-size: 0.8rem; margin: 0;">
                <i class="fa-solid fa-triangle-exclamation"></i>
                <strong>Disclaimer Medico:</strong> Questo strumento AI è solo per supporto professionale. Consultare sempre un radiologo qualificato per la diagnosi finale.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
tab_analysis, tab_archive, tab_info = st.tabs([
    "Terminale di Analisi",
    "Archivio",
    "Performance del Sistema"
])

with tab_info:
    st.markdown("### Performance & Architettura")
    st.markdown("I seguenti valori rappresentano le performance del modello validate sul Dataset Clinico di Test.")

    cols = st.columns(4)
    metrics = [
        ("Leopoldo", "90%", "fa-check-circle", "#dcfce7", "#166534"),
        ("Aurora", "9%", "fa-heart-pulse", "#fee2e2", "#991b1b"),
        ("Martin", "1%", "fa-shield-halved", "#e0f2fe", "#075985"),
    ]

    for i, (label, val, icon, bg, icon_color) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
                <div style="background: {bg}; padding: 1.5rem; border-radius: 12px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <i class="fa-solid {icon}" style="font-size: 1.5rem; margin-bottom: 10px; color: {icon_color}; display: block;"></i>
                    <p style="margin: 0; font-size: 0.8rem; color: #475569;">{label}</p>
                    <h3 style="margin: 0; color: #1e293b;">{val}</h3>
                </div>
            """, unsafe_allow_html=True)

with tab_archive:
    st.markdown("### Archivio Analisi")

    # List saved analyses
    analyses = list_analyses()

    if not analyses:
        st.info("Nessuna analisi salvata. Esegui un'analisi e clicca 'Salva in Archivio' per memorizzarla.")
    else:
        # Check if viewing a specific analysis
        if 'viewing_archive' in st.session_state and st.session_state.viewing_archive:
            archive_id = st.session_state.viewing_archive
            archived = load_analysis(archive_id)

            if archived:
                # Back button
                if st.button("← Torna all'elenco", type="secondary"):
                    st.session_state.viewing_archive = None
                    st.rerun()

                st.markdown(f"### {archived['filename']}")
                st.caption(f"Analizzato il: {archived['timestamp']}")

                # Results layout (readonly)
                res_col_imgs, res_col_data = st.columns([1.2, 0.8])

                with res_col_imgs:
                    # Buttons row
                    btn1, btn2 = st.columns(2)
                    with btn1:
                        if archived.get('reasoning_data'):
                            if st.button("Visualizza Ragionamento", use_container_width=True, type="primary", key="archive_reasoning"):
                                show_reasoning_modal(archived['reasoning_data'])
                    with btn2:
                        if archived.get('reasoning_data') and archived.get('cls_data'):
                            pdf_bytes = generate_pdf_report(
                                archived['reasoning_data'],
                                archived['cls_data'],
                                archived.get('detections', [])
                            )
                            st.download_button(
                                label="Scarica Report PDF",
                                data=pdf_bytes,
                                file_name=f"report_{archive_id}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )

                    # Image tabs
                    img_tabs = st.tabs(["Rilevamenti YOLO", "Analisi Processata", "Vista Originale"])
                    with img_tabs[0]:
                        if archived.get('yolo_img'):
                            st.image(archived['yolo_img'], use_container_width=True)
                    with img_tabs[1]:
                        if archived.get('processed_img'):
                            st.image(archived['processed_img'], use_container_width=True)
                    with img_tabs[2]:
                        if archived.get('original_img'):
                            st.image(archived['original_img'], use_container_width=True)

                with res_col_data:
                    st.markdown("#### Sintesi Diagnostica")
                    cls_data = archived.get('cls_data', {})
                    is_pos = cls_data.get('is_positive', False)
                    conf = cls_data.get('confidence', 0) * 100
                    detections = archived.get('detections', [])

                    diag_class = "badge-positive" if is_pos else "badge-negative"
                    diag_icon = "fa-triangle-exclamation" if is_pos else "fa-circle-check"
                    diag_text = "POSITIVO (Polmonite Rilevata)" if is_pos else "NEGATIVO (Reperti Normali)"

                    st.markdown(f"""
                        <div>
                            <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Diagnosi Primaria</p>
                            <div class="status-badge {diag_class}">
                                <i class="fa-solid {diag_icon}"></i> {diag_text}
                            </div>
                            <div style="margin-top: 20px;">
                                <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Punteggio di Confidenza</p>
                                <h2 style="margin: 0; font-weight: 700;">{conf:.1f}%</h2>
                            </div>
                            <div style="margin-top: 20px;">
                                <p style="font-size: 0.8rem; color: #64748b; margin: 0;">Anomalie Focali</p>
                                <h4 style="margin: 0;">{len(detections)} Aree</h4>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            else:
                st.error("Analisi non trovata.")
                st.session_state.viewing_archive = None
        else:
            # Show list of analyses
            st.markdown(f"**{len(analyses)} analisi salvate**")

            for analysis in analyses:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                with col1:
                    # Filename and date
                    timestamp = analysis['timestamp'][:16].replace('T', ' ') if analysis['timestamp'] else ''
                    st.markdown(f"**{analysis['filename']}**")
                    st.caption(timestamp)

                with col2:
                    # Status badge
                    if analysis['is_positive']:
                        st.markdown("🔴 Positivo")
                    else:
                        st.markdown("🟢 Negativo")

                with col3:
                    # View button
                    if st.button("Visualizza", key=f"view_{analysis['archive_id']}", use_container_width=True):
                        st.session_state.viewing_archive = analysis['archive_id']
                        st.rerun()

                with col4:
                    # Delete button
                    if st.button("🗑️", key=f"del_{analysis['archive_id']}", help="Elimina"):
                        delete_analysis(analysis['archive_id'])
                        st.rerun()

                st.divider()

with tab_analysis:
    st.markdown("""
        <div class="info-box">
            <i class="fa-solid fa-circle-info"></i>
            <strong>Protocollo Operativo:</strong> Carica una radiografia del torace (CXR) ad alta risoluzione per avviare la pipeline diagnostica multi-fase.
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Carica una radiografia",
        type=['png', 'jpg', 'jpeg'],
        help="Puoi trascinare il file direttamente qui o cliccare per selezionarlo dal tuo dispositivo."
    )

    if not uploaded_file:
        # Reset session state when no file is uploaded
        if 'analysis_results' in st.session_state:
            del st.session_state.analysis_results
        if 'current_file' in st.session_state:
            del st.session_state.current_file
    else:
        # Save temporary file
        temp_path = f"/app/temp/{uploaded_file.name}"
        os.makedirs("/app/temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.divider()

        # Check if we need to run the pipeline (new file or first run)
        need_analysis = (
            'current_file' not in st.session_state or
            st.session_state.current_file != uploaded_file.name
        )

        # Run Pipeline if needed - show live reasoning modal
        if need_analysis:
            metadata = user_pos if user_pos != "Non Specificata" else None

            pipeline_gen = agent.run_full_pipeline_streaming(
                temp_path, "Analisi Clinica Completa", metadata
            )

            # Open the live reasoning modal (results are saved to session_state inside)
            show_live_reasoning_modal(pipeline_gen, uploaded_file.name)

        # Retrieve results from session state
        if 'analysis_results' not in st.session_state:
            st.warning("Nessun risultato disponibile. Ricarica la pagina.")
            st.stop()

        results = st.session_state.analysis_results
        reasoning_data = results['reasoning_data']
        processed_img = results['processed_img']
        yolo_img = results.get('yolo_img', processed_img)
        detections = results['detections']
        cls_data = results['cls_data']

        # Layout for Results (after analysis)
        res_col_imgs, res_col_data = st.columns([1.2, 0.8])

        with res_col_imgs:
            # Buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("Visualizza Ragionamento", use_container_width=True, type="primary"):
                    show_reasoning_modal(reasoning_data)
            with btn_col2:
                pdf_bytes = generate_pdf_report(reasoning_data, cls_data, detections)
                st.download_button(
                    label="Scarica Report PDF",
                    data=pdf_bytes,
                    file_name=f"report_xray_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with btn_col3:
                # Compute image hash and check if already archived
                uploaded_file.seek(0)
                image_hash = compute_image_hash(uploaded_file)
                uploaded_file.seek(0)
                existing_archive = is_already_archived(image_hash)

                if existing_archive:
                    st.button("Già in Archivio", use_container_width=True, disabled=True)
                else:
                    if st.button("Salva in Archivio", use_container_width=True):
                        original_img = Image.open(uploaded_file)
                        archive_id = save_analysis(
                            filename=uploaded_file.name,
                            original_img=original_img,
                            processed_img=processed_img,
                            yolo_img=yolo_img,
                            cls_data=cls_data,
                            detections=detections,
                            reasoning_data=reasoning_data,
                            metadata={"proiezione": user_pos},
                            image_hash=image_hash
                        )
                        st.toast("Analisi salvata in archivio!", icon="✅")
                        st.rerun()

            # Image tabs
            img_tabs = st.tabs(["Rilevamenti YOLO", "Analisi Processata", "Vista Originale"])
            with img_tabs[0]:
                _, img_col, _ = st.columns([0.1, 0.8, 0.1])
                with img_col:
                    st.image(yolo_img, use_container_width=True, caption=f"{len(detections)} aree rilevate")
            with img_tabs[1]:
                _, img_col, _ = st.columns([0.1, 0.8, 0.1])
                with img_col:
                    st.image(processed_img, use_container_width=True)
            with img_tabs[2]:
                _, img_col, _ = st.columns([0.1, 0.8, 0.1])
                with img_col:
                    st.image(uploaded_file, use_container_width=True)

        with res_col_data:
            st.markdown("#### Sintesi Diagnostica")

            # Results Styling
            is_pos = cls_data['is_positive']
            conf = cls_data['confidence'] * 100

            diag_class = "badge-positive" if is_pos else "badge-negative"
            diag_icon = "fa-triangle-exclamation" if is_pos else "fa-circle-check"
            diag_text = "POSITIVO (Polmonite Rilevata)" if is_pos else "NEGATIVO (Reperti Normali)"

            st.markdown(f"""
                <div class="">
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Diagnosi Primaria</p>
                    <div class="status-badge {diag_class}">
                        <i class="fa-solid {diag_icon}"></i> {diag_text}
                    </div>
                    <div style="margin-top: 20px;">
                        <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Punteggio di Confidenza</p>
                        <h2 style="margin: 0; font-weight: 700;">{conf:.1f}%</h2>
                        <div style="background: #e2e8f0; height: 8px; border-radius: 4px; margin-top: 8px;">
                            <div style="background: {'#ef4444' if is_pos else '#22c55e'}; width: {conf}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <div style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="font-size: 0.8rem; color: #64748b; margin: 0;">Anomalie Focali</p>
                            <h4 style="margin: 0;">{len(detections)} Aree</h4>
                        </div>
                        <i class="fa-solid fa-microscope" style="color: #cbd5e1; font-size: 1.5rem;"></i>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if is_pos:
                st.error("""
                    **Avviso Clinico Urgente:** Rilevata alta probabilità di polmonite. Si raccomanda revisione immediata del reparto pneumologia.
                """)