import streamlit as st
import os
from datetime import datetime
from PIL import Image
import pandas as pd
import altair as alt
from src.agent.brain import MedicalAgent
from src.utils.pdf_generator import generate_pdf_report
from src.utils.archive import save_analysis, list_analyses, load_analysis, delete_analysis, is_already_archived, compute_image_hash, get_performance_stats

st.set_page_config(
    page_title="XRayAnalyzer | Supporto Clinico AI",
    page_icon="https://img.icons8.com/ink/color/96/lungs.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.ui.styles import (
    EXTERNAL_LINKS, MAIN_STYLES, SPINNER_CSS, SIDEBAR_HEADER, LOADING_HTML,
    TIMELINE_STEP_TEMPLATE, TIMELINE_STEP_HEADER, TIMELINE_ACTIVE_TEMPLATE, METRIC_CARD_TEMPLATE, RESULT_BADGE_TEMPLATE
)

st.markdown(EXTERNAL_LINKS + MAIN_STYLES, unsafe_allow_html=True)

# Agent Caching
@st.cache_resource(show_spinner=False)
def load_medical_agent():
    return MedicalAgent()

if "agent" not in st.session_state:
    placeholder = st.empty()
    placeholder.markdown(LOADING_HTML, unsafe_allow_html=True)
    st.session_state.agent = load_medical_agent()
    placeholder.empty()

agent = st.session_state.agent

@st.dialog("Ragionamento Diagnostico AI", width="large")
def show_reasoning_modal(reasoning_data):
    steps = reasoning_data["steps"]

    tab_titles = [f"{step['title'][:28]}..." if len(step['title']) > 28 else step['title'] for step in steps]
    tabs = st.tabs(tab_titles)

    for tab, step in zip(tabs, steps):
        with tab:
            st.markdown(TIMELINE_STEP_HEADER.format(
                icon=step['icon'],
                title=step['title']
            ), unsafe_allow_html=True)

            quoted_content = "\n".join([f"> {line}" for line in step['content'].split("\n")])
            st.markdown(quoted_content)

            if step.get('image') is not None:
                st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
                st.image(step['image'], caption="Area analizzata", width=300)


@st.dialog("Terminale di Ragionamento", width="large", dismissible=False)
def show_live_reasoning_modal(pipeline_generator, file_name):
    completed_steps = []
    processed_img = None
    detections = []
    cls_data = None

    # Spinner CSS
    st.markdown(SPINNER_CSS, unsafe_allow_html=True)

    # Main container for the tabs
    tabs_placeholder = st.empty()

    for step, is_final, final_data in pipeline_generator:
        # Se is_final è True, il generatore ha completato l'intero workflow (Vision + GPT-4o)
        if is_final:
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
            st.rerun() # Refresh to show results
            break

        # Terminal Header
        st.markdown(f"""
            <div style="background: #1e293b; color: #f8fafc; padding: 12px 20px; border-radius: 8px 8px 0 0; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <i class="fa-solid fa-terminal"></i>
                    <span style="font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;">DIAGNOSTIC_TERMINAL_V1.0.4</span>
                </div>
                <div style="display: flex; gap: 6px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #ef4444;"></div>
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #f59e0b;"></div>
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #10b981;"></div>
                </div>
            </div>
            <div style="background: #0f172a; border: 1px solid #1e293b; border-top: none; padding: 25px; border-radius: 0 0 8px 8px; min-height: 450px;">
        """, unsafe_allow_html=True)

        if not completed_steps:
            st.markdown("""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; color: #475569;">
                    <div class="spinner-modern"></div>
                    <p style="margin-top: 20px; font-family: 'JetBrains Mono', monospace;">Inizializzazione Core Neurale...</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            for i, step in enumerate(completed_steps):
                is_last = (i == len(completed_steps) - 1)
                st.markdown(f"""
                    <div style="margin-bottom: 25px; border-left: 2px solid {'#3b82f6' if is_last else '#1e293b'}; padding-left: 20px; position: relative;">
                        <div style="position: absolute; left: -11px; top: 0; width: 20px; height: 20px; border-radius: 50%; background: {'#3b82f6' if is_last else '#1e293b'}; color: white; display: flex; align-items: center; justify-content: center; font-size: 10px;">
                            <i class="fa-solid {step['icon']}"></i>
                        </div>
                        <h4 style="color: #cbd5e1; font-family: 'JetBrains Mono', monospace; margin: 0 0 10px 0; font-size: 1rem;">
                            Step {i+1}: {step['title']} {'<span style="background: #3b82f640; color: #60a5fa; font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; margin-left: 10px;">IN CORSO</span>' if is_last else ''}
                        </h4>
                        <div style="color: #94a3b8; font-size: 0.95rem; line-height: 1.6;">
                """, unsafe_allow_html=True)

                # Content as blockquote for contrast
                quoted_content = "\n".join([f"> {line}" for line in step['content'].split("\n")])
                st.markdown(quoted_content)

                if step.get('image') is not None:
                    if step.get('ref_image') is not None:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(step['image'], caption="Area Rilevata", use_container_width=True)
                        with col2:
                            st.image(step['ref_image'], caption="Riferimento Atlante", use_container_width=True)
                    else:
                        st.image(step['image'], width=250)

                st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Get intermediate data
        if final_data and final_data[1] is not None:
            processed_img = final_data[1]
            yolo_img = final_data[2]
            detections = final_data[3]
            cls_data = final_data[4]
        if step:
            # Update existing step if ID matches, otherwise append
            existing_idx = next((i for i, s in enumerate(completed_steps) if s['id'] == step['id']), None)
            if existing_idx is not None:
                completed_steps[existing_idx] = step
            else:
                completed_steps.append(step)

    # Analysis Complete - Show Close Button
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    if st.button("Chiudi e Visualizza Risultati", type="primary", width="stretch"):
        st.rerun()

@st.dialog("Salva in Archivio")
def show_save_archive_dialog(results, user_pos):
    st.markdown("Scegli un nome per identificare questa analisi nell'archivio:")

    current_filename = results['current_file']
    custom_name = st.text_input("Nome Archivio", value=current_filename)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Annulla", width="stretch", icon=":material/close:"):
            st.rerun()
    with col2:
        if st.button("Salva", type="primary", width="stretch", icon=":material/save:"):
            with st.spinner("Salvataggio in corso..."):
                # Prepare data
                image_hash = compute_image_hash(results['original_img'])

                # Save
                save_analysis(
                    filename=custom_name,
                    original_img=results['original_img'],
                    processed_img=results['processed_img'],
                    yolo_img=results['yolo_img'],
                    cls_data=results['cls_data'],
                    detections=results['detections'],
                    reasoning_data=results['reasoning_data'],
                    metadata={"proiezione": user_pos},
                    image_hash=image_hash
                )

                # Update session state to show "Archiviato"
                st.session_state.current_analysis_saved = True
                st.toast(f"Analisi '{custom_name}' salvata!", icon=":material/check_circle:")
                st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(SIDEBAR_HEADER, unsafe_allow_html=True)

    # Navigazione basata su session_state per mantenere lo stato al refresh
    if "page" not in st.session_state:
        st.session_state.page = "Terminale Analisi"

    def set_page(page_name):
        st.session_state.page = page_name

    # Navigation Buttons
    st.button(
        "Terminale Analisi",
        on_click=set_page,
        args=("Terminale Analisi",),
        type="primary" if st.session_state.page == "Terminale Analisi" else "secondary",
        width="stretch"
    )
    st.button(
        "Archivio",
        on_click=set_page,
        args=("Archivio",),
        type="primary" if st.session_state.page == "Archivio" else "secondary",
        width="stretch"
    )
    st.button(
        "Performance",
        on_click=set_page,
        args=("Performance",),
        type="primary" if st.session_state.page == "Performance" else "secondary",
        width="stretch"
    )

    nav_page = st.session_state.page

    st.divider()

    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; color: #64748b; margin-bottom: 10px;">METADATI CLINICI</p>', unsafe_allow_html=True)
    user_pos = st.selectbox(
        "Proiezione RX",
        ["Non Specificata", "AP (Antero-Posteriore)", "PA (Postero-Anteriore)"],
        help="Specificare la proiezione migliora la precisione del ragionamento diagnostico."
    )

    st.divider()

    st.markdown("""
        <div style="background-color: #fefce8; padding: 1rem; border-radius: 8px; border: 1px solid #fef08a;">
            <p style="color: #854d0e; font-size: 0.8rem; margin: 0;">
                <i class="fa-solid fa-triangle-exclamation"></i>
                <strong>Disclaimer Medico:</strong> Strumento AI per supporto professionale. Non sostituisce il parere medico.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---

st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
# 1. PAGE: Terminale Analisi
if nav_page == "Terminale Analisi":
    st.markdown("### Carica una radiografia")
    uploaded_file = st.file_uploader(
        "Carica Radiografia",
        type=['png', 'jpg', 'jpeg'],
        label_visibility="collapsed"
    )

    if not uploaded_file:
        st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem;">
                <div style="font-size: 5rem; color: #94a3b8; opacity: 0.5; margin-bottom: 20px;">
                    <i class="fa-solid fa-lungs"></i>
                </div>
                <h2 style="color: #94a3b8;">Nessuna Radiografia Caricata</h2>
                <p style="color: #64748b; margin-top: 10px;">Caricare un'immagine RX per avviare l'analisi.</p>
            </div>
        """, unsafe_allow_html=True)

        # Reset session state when no file is uploaded
        if 'analysis_results' in st.session_state:
            del st.session_state.analysis_results
        if 'current_file' in st.session_state:
            del st.session_state.current_file
        if 'current_analysis_saved' in st.session_state:
            del st.session_state.current_analysis_saved
    else:
        temp_path = f"/app/temp/{uploaded_file.name}"

        # Esecuzione della pipeline solo se il file è nuovo o non ancora analizzato
        need_analysis = (
            'current_file' not in st.session_state or
            st.session_state.current_file != uploaded_file.name
        )
        if need_analysis:
            # Reset dello stato salvataggio per la nuova analisi
            if 'current_analysis_saved' in st.session_state:
                del st.session_state.current_analysis_saved

            # Save temporary file ONLY when analysis is needed
            os.makedirs("/app/temp", exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            metadata = user_pos if user_pos != "Non Specificata" else None

            pipeline_gen = agent.run_full_pipeline_streaming(
                temp_path, "Analisi Clinica Completa", metadata
            )

            # Open the live reasoning modal (results are saved to session_state inside)
            show_live_reasoning_modal(pipeline_gen, uploaded_file.name)

            # Cleanup temporary file immediately after analysis
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Retrieve results from session state
        if 'analysis_results' not in st.session_state:
            st.warning("Elaborazione interrotta. Ricarica l'immagine.")
            st.stop()

        results = st.session_state.analysis_results
        reasoning_data = results['reasoning_data']
        processed_img = results['processed_img']
        yolo_img = results.get('yolo_img', processed_img)
        detections = results['detections']
        cls_data = results['cls_data']

        # Dati riassuntivi della classificazione globale
        cls_confidence = cls_data['confidence'] * 100
        is_positive = cls_data['is_positive']
        header_color = "#ef4444" if is_positive else "#22c55e"
        header_text = "Rilevata Polmonite" if is_positive else "Reperti Normali"

        # Header con esito rapido basato sulla classificazione globale
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #e2e8f0;">
                <div>
                    <h2 style="margin: 0; color: #1e293b;">Risultati Analisi</h2>
                    <p style="margin: 0; color: #64748b;">File: {uploaded_file.name}</p>
                </div>
                <div style="text-align: right;">
                    <span style="background: {header_color}20; color: {header_color}; padding: 5px 15px; border-radius: 20px; font-weight: 700;">
                        {header_text}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Layout for Results
        res_col_imgs, res_col_data = st.columns([1.2, 0.8])

        with res_col_imgs:
            # Action Buttons Area - Redesigned to 2 per row
            st.markdown('<div style="margin-top: 10px; margin-bottom: 25px;">', unsafe_allow_html=True)

            # Row 1: Observation and Export
            act_col1, act_col2 = st.columns(2)
            with act_col1:
                if st.button("Ragionamento", width="stretch", type="primary", icon=":material/psychology_alt:"):
                    show_reasoning_modal(reasoning_data)
            with act_col2:
                pdf_bytes = generate_pdf_report(reasoning_data, cls_data, detections)
                st.download_button(
                    label="Scarica PDF",
                    data=pdf_bytes,
                    file_name=f"report_xray_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    width="stretch",
                    icon=":material/picture_as_pdf:"
                )

            # Row 2: Archiving
            st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
            arc_col1, arc_col2 = st.columns(2)
            with arc_col1:
                if st.session_state.get('current_analysis_saved', False):
                    # Show "Salva un'altra copia" as a secondary action
                    if st.button("Salva Copia", width="stretch", icon=":material/library_add:"):
                        show_save_archive_dialog({
                            **results,
                            'current_file': uploaded_file.name,
                            'original_img': Image.open(uploaded_file)
                        }, user_pos)
                else:
                    if st.button("Archivia Analisi", width="stretch", type="primary", icon=":material/archive:"):
                        show_save_archive_dialog({
                            **results,
                            'current_file': uploaded_file.name,
                            'original_img': Image.open(uploaded_file)
                        }, user_pos)
            with arc_col2:
                if st.session_state.get('current_analysis_saved', False):
                    st.button("Archiviato", width="stretch", type="secondary", disabled=True, icon=":material/verified:")
                else:
                    st.button("Non Archiviato", width="stretch", type="secondary", disabled=True, icon=":material/history:")

            st.markdown('</div>', unsafe_allow_html=True)

            # Image Preview Tabs
            img_tabs = st.tabs(["Rilevamenti YOLO", "Immagine migliorata", "Immagine originale"])
            with img_tabs[0]:
                st.image(yolo_img, width="stretch", caption=f"{len(detections)} anomalie identificate")
            with img_tabs[1]:
                st.image(processed_img, width="stretch", caption="Immagine preprocessata (CLAHE)")
            with img_tabs[2]:
                st.image(uploaded_file, width="stretch", caption="Input originale")

        with res_col_data:
            st.markdown("#### Sintesi Diagnostica")

            # Calcolo della severità clinica basato sulla confidenza del classificatore
            if is_positive:
                if cls_confidence >= 80: severity_label = "Alta (Critica)"
                elif cls_confidence >= 50: severity_label = "Moderata"
                else: severity_label = "Bassa"
            else:
                severity_label = "Assente"

            st.markdown(RESULT_BADGE_TEMPLATE.format(
                diag_class="badge-positive" if is_positive else "badge-negative",
                diag_icon="fa-triangle-exclamation" if is_positive else "fa-circle-check",
                diag_text=header_text.upper(),
                conf=cls_confidence,
                bar_color=header_color,
                num_detections=len(detections),
                severity=severity_label
            ), unsafe_allow_html=True)

            if is_positive:
                st.error("""
                    **Avviso Clinico Urgente:** Rilevata alta probabilità di polmonite.
                    Si raccomanda revisione immediata del reparto pneumologia.
                """)
            else:
                st.success("""
                    **Esito:** Nessuna evidenza di consolidamenti o opacità sospette.
                    Quadro radiologico nei limiti della norma.
                """)

# 2. PAGE: Archivio
elif nav_page == "Archivio":
    st.markdown("### Archivio Analisi")

    # Callbacks for navigation (defined globally or here works too)
    if 'viewing_archive' not in st.session_state:
        st.session_state.viewing_archive = None

    def set_viewing_archive(archive_id):
        st.session_state.viewing_archive = archive_id

    def clear_viewing_archive():
        st.session_state.viewing_archive = None

    def delete_analysis_cb(archive_id):
        delete_analysis(archive_id)

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
                st.button("← Torna all'elenco", type="secondary", on_click=clear_viewing_archive)

                st.markdown(f"### {archived['filename']}")
                st.caption(f"Analizzato il: {archived['timestamp']}")

                # Visualizzazione in sola lettura dei risultati archiviati
                res_col_imgs, res_col_data = st.columns([1.2, 0.8])

                with res_col_imgs:
                    btn1, btn2 = st.columns(2)
                    with btn1:
                        if archived.get('reasoning_data'):
                            if st.button("Visualizza Ragionamento", width="stretch", type="primary", key="archive_reasoning"):
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
                                width="stretch"
                            )

                    img_tabs = st.tabs(["Rilevamenti YOLO", "Analisi Processata", "Vista Originale"])
                    with img_tabs[0]:
                        if archived.get('yolo_img'):
                            st.image(archived['yolo_img'], width="stretch")
                    with img_tabs[1]:
                        if archived.get('processed_img'):
                            st.image(archived['processed_img'], width="stretch")
                    with img_tabs[2]:
                        if archived.get('original_img'):
                            st.image(archived['original_img'], width="stretch")

                with res_col_data:
                    st.markdown("#### Sintesi Diagnostica")
                    cls_data = archived.get('cls_data', {})
                    is_pos = cls_data.get('is_positive', False)
                    conf = cls_data.get('confidence', 0) * 100
                    detections = archived.get('detections', [])

                    diag_class = "badge-positive" if is_pos else "badge-negative"
                    diag_icon = "fa-triangle-exclamation" if is_pos else "fa-circle-check"
                    diag_text = "POSITIVO (Polmonite Rilevata)" if is_pos else "NEGATIVO (Reperti Normali)"

                    if is_pos:
                        if conf >= 80: severity_label = "Alta (Critica)"
                        elif conf >= 50: severity_label = "Moderata"
                        else: severity_label = "Bassa"
                    else:
                        severity_label = "Assente"

                    st.markdown(RESULT_BADGE_TEMPLATE.format(
                        diag_class=diag_class,
                        diag_icon=diag_icon,
                        diag_text=diag_text,
                        conf=conf,
                        bar_color='#ef4444' if is_pos else '#22c55e',
                        num_detections=len(detections),
                        severity=severity_label
                    ), unsafe_allow_html=True)

            else:
                st.error("Analisi non trovata.")
                st.session_state.viewing_archive = None
        else:
            # Show list of analyses
            st.markdown(f"**{len(analyses)} analisi salvate**")

            for analysis in analyses:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                with col1:
                    timestamp = analysis['timestamp'][:16].replace('T', ' ') if analysis['timestamp'] else ''
                    st.markdown(f"**{analysis['filename']}**")
                    st.caption(timestamp)

                with col2:
                    # Status badge with Font Awesome
                    if analysis['is_positive']:
                        st.markdown('<span style="color: #ef4444;"><i class="fa-solid fa-circle-dot"></i> Positivo</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="color: #22c55e;"><i class="fa-solid fa-circle-check"></i> Negativo</span>', unsafe_allow_html=True)

                with col3:
                    # View button
                    st.button("Visualizza", key=f"view_{analysis['archive_id']}", width="stretch", on_click=set_viewing_archive, args=(analysis['archive_id'],), icon=":material/visibility:")

                with col4:
                    # Delete button
                    st.button("Elimina", key=f"del_{analysis['archive_id']}", help="Elimina", on_click=delete_analysis_cb, args=(analysis['archive_id'],), icon=":material/delete:")

                st.divider()

# 3. PAGE: Performance
elif nav_page == "Performance":
    st.markdown("### Dashboard Performance AI")

    stats = get_performance_stats()

    if stats['total'] == 0:
        st.info("Nessun dato disponibile. Salva delle analisi nell'archivio per popolare la dashboard.")
    else:
        # Riepilogo metriche principali (KPI) dell'intero archivio
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(METRIC_CARD_TEMPLATE.format(
                title="Totale Analisi",
                value=stats['total'],
                icon="fa-folder-open",
                color="#3b82f6"
            ), unsafe_allow_html=True)

        with col2:
            st.markdown(METRIC_CARD_TEMPLATE.format(
                title="Casi Positivi",
                value=stats['positive'],
                icon="fa-triangle-exclamation",
                color="#ef4444"
            ), unsafe_allow_html=True)

        with col3:
            st.markdown(METRIC_CARD_TEMPLATE.format(
                title="Casi Negativi",
                value=stats['negative'],
                icon="fa-shield-halved",
                color="#22c55e"
            ), unsafe_allow_html=True)

        with col4:
            st.markdown(METRIC_CARD_TEMPLATE.format(
                title="Confidenza Media",
                value=f"{stats['avg_confidence']:.1f}%",
                icon="fa-chart-line",
                color="#8b5cf6"
            ), unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        # Grafico di distribuzione dei casi (Positivi vs Negativi)
        chart_data = pd.DataFrame([
            {"Tipologia": "Polmonite (Positivi)", "Quantità": stats['positive'], "Color": "#ef4444"},
            {"Tipologia": "Sani (Negativi)", "Quantità": stats['negative'], "Color": "#22c55e"}
        ])

        c = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Tipologia', sort=None, axis=alt.Axis(labelAngle=0)),
            y='Quantità',
            color=alt.Color('Tipologia', scale=alt.Scale(
                domain=['Polmonite (Positivi)', 'Sani (Negativi)'],
                range=['#ef4444', '#22c55e']
            ), legend=None),
            tooltip=['Tipologia', 'Quantità']
        ).properties(height=300)

        st.altair_chart(c, theme="streamlit", width="stretch")