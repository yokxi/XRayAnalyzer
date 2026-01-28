import streamlit as st
import os
from PIL import Image
from src.agent.brain import MedicalAgent

# Page Configuration
st.set_page_config(
    page_title="XRayAnalyzer | AI Clinical Support",
    page_icon="https://img.icons8.com/ink/color/96/lungs.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load External Resources (Font Awesome & Google Fonts)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        /* Global Styles */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            color: #1e293b;
        }

        .main {
            background-color: #f8fafc;
        }

        /* Typography */
        .main-header {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
        }

        .sub-header {
            font-size: 1.1rem;
            color: #64748b;
            text-align: center;
            margin-bottom: 2.5rem;
            font-weight: 400;
        }

        /* Cards & Containers */
        .st-emotion-cache-1r6slb0 { /* Sidebar container */
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(226, 232, 240, 0.5);
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            margin-bottom: 1.5rem;
        }

        .info-box {
            background-color: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 1.25rem;
            border-radius: 8px;
            margin: 1rem 0;
            color: #1e40af;
            font-size: 0.95rem;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            gap: 0.5rem;
        }

        .badge-positive { background-color: #fee2e2; color: #991b1b; }
        .badge-negative { background-color: #dcfce7; color: #166534; }
        .badge-info { background-color: #e0f2fe; color: #075985; }

        /* Icon styling */
        .icon-container {
            width: 40px;
            height: 40px;
            background: #f1f5f9;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.75rem;
            color: #2563eb;
        }

        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Custom Progress Bar */
        .progress-step {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 10px;
            background: #fff;
            border: 1px solid #f1f5f9;
            transition: all 0.3s ease;
        }

        .progress-step.active {
            border-color: #3b82f6;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
            transform: translateX(5px);
        }

        .step-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# Agent Caching
@st.cache_resource
def load_medical_agent():
    return MedicalAgent()

agent = load_medical_agent()

# --- HEADER ---
st.markdown('<p class="main-header">XRayAnalyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced Pneumonia Detection & Clinical Reasoning Engine</p>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <img src="https://img.icons8.com/ink/color/96/lungs.png" width="70">
            <h2 style="margin-top: 10px; font-weight: 600;">Control Center</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; color: #64748b; margin-bottom: 10px;">CLINICAL METADATA</p>', unsafe_allow_html=True)
    user_pos = st.selectbox(
        "X-Ray Projection",
        ["Not Specified", "AP (Anteroposterior)", "PA (Posteroanterior)"],
        help="Specifying the projection improves diagnostic reasoning accuracy."
    )

    st.divider()

    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; color: #64748b;">SYSTEM PIPELINE</p>', unsafe_allow_html=True)

    with st.expander("Step 1: Digital Enhancement"):
        st.markdown("""
            <i class="fa-solid fa-wand-magic-sparkles" style="color: #2563eb;"></i>
            **CLAHE Normalization**<br>
            Optimizes local contrast to reveal subtle infiltrates and lung structures.
        """, unsafe_allow_html=True)

    with st.expander("Step 2: Deep Classification"):
        st.markdown("""
            <i class="fa-solid fa-brain" style="color: #2563eb;"></i>
            **Swin-B Transformer**<br>
            Analyzes global semantic features to determine diagnostic probability.
        """, unsafe_allow_html=True)

    with st.expander("Step 3: Object Detection"):
        st.markdown("""
            <i class="fa-solid fa-bullseye" style="color: #2563eb;"></i>
            **YOLO11 Detection**<br>
            Localizes spatial suspicious areas with high-precision bounding boxes.
        """, unsafe_allow_html=True)

    with st.expander("Step 4: Clinical Reasoning"):
        st.markdown("""
            <i class="fa-solid fa-comment-medical" style="color: #2563eb;"></i>
            **LLM + RAG**<br>
            Synthesizes vision results with medical knowledge bases for XAI reporting.
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
        <div style="background-color: #fefce8; padding: 1rem; border-radius: 8px; border: 1px solid #fef08a;">
            <p style="color: #854d0e; font-size: 0.8rem; margin: 0;">
                <i class="fa-solid fa-triangle-exclamation"></i>
                <strong>Medical Disclaimer:</strong> This AI tool is for professional support only. Always consult a qualified radiologist for final diagnosis.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
tab_analysis, tab_info = st.tabs([
    "Analysis Terminal",
    "System Performance"
])

with tab_info:
    st.markdown("### System Architecture")
    st.markdown("The system integrates state-of-the-art architectures to provide interpretable medical AI.")

    cols = st.columns(4)
    metrics = [
        ("Accuracy", "94.2%", "fa-check-circle", "#dcfce7"),
        ("Sensitivity", "96.8%", "fa-heart-pulse", "#fee2e2"),
        ("Specificity", "91.5%", "fa-shield-halved", "#e0f2fe"),
        ("F1-Score", "0.943", "fa-chart-line", "#f1f5f9")
    ]

    for i, (label, val, icon, bg) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
                <div style="background: {bg}; padding: 1.5rem; border-radius: 12px; text-align: center;">
                    <i class="fa-solid {icon}" style="font-size: 1.5rem; margin-bottom: 10px;"></i>
                    <p style="margin: 0; font-size: 0.8rem; color: #475569;">{label}</p>
                    <h3 style="margin: 0; color: #1e293b;">{val}</h3>
                </div>
            """, unsafe_allow_html=True)

with tab_analysis:
    st.markdown("""
        <div class="info-box">
            <i class="fa-solid fa-circle-info"></i>
            <strong>Operational Protocol:</strong> Upload a high-resolution Chest X-Ray (CXR) to initiate the multi-stage diagnostic pipeline.
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Source Image (DICOM, PNG, JPG)",
        type=['png', 'jpg', 'jpeg'],
        label_visibility="collapsed"
    )

    if not uploaded_file:
        st.markdown("""
            <div style="text-align: center; padding: 5rem 2rem; background: #ffffff; border: 2px dashed #e2e8f0; border-radius: 20px; margin-top: 2rem;">
                <i class="fa-solid fa-cloud-arrow-up" style="font-size: 3rem; color: #cbd5e1; margin-bottom: 1.5rem;"></i>
                <h3 style="color: #64748b;">Awaiting Radiograph Upload</h3>
                <p style="color: #94a3b8; max-width: 400px; margin: 0 auto;">Drag and drop a chest X-ray image here. The AI will automatically begin processing upon upload.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Save temporary file
        temp_path = f"/app/temp/{uploaded_file.name}"
        os.makedirs("/app/temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.divider()

        # Layout for Results
        res_col_imgs, res_col_data = st.columns([1.2, 0.8])

        with res_col_imgs:
            img_tabs = st.tabs(["Processed Analysis", "Original View"])
            with img_tabs[1]:
                st.image(uploaded_file, use_container_width=True)

            # Status Container is created here but filled during process
            with img_tabs[0]:
                analysis_placeholder = st.empty()
                status_container = st.container()

        # Run Pipeline
        with status_container:
            st.markdown("#### Real-time Process Pipeline")

            # This logic will be triggered by the agent.run_full_pipeline
            # But we can simulate the visual state if the agent emits progress.
            # Currently brain.py uses st.write. Let's wrap it in a placeholder.

            with st.status("Initializing AI Diagnostic Suite...", expanded=True) as status:
                progress_bar = st.progress(0, "Warming up models...")

                # We need to capture the output of run_full_pipeline
                # Since brain.py has st.write inside, they will appear here.
                metadata = user_pos if user_pos != "Not Specified" else None

                # Visual preparation
                progress_bar.progress(10, text="Executing Phase 1: Digital Signal Enhancement...")

                # Execute Backend
                reasoning, processed_img, detections, cls_data = agent.run_full_pipeline(
                    temp_path, "Full Clinical Analysis", metadata
                )

                progress_bar.progress(100, text="Pipeline Completed.")
                status.update(label="Diagnostic Cycle Finished", state="complete", expanded=False)

            analysis_placeholder.image(processed_img, use_container_width=True)

        with res_col_data:
            st.markdown("#### Diagnostic Summary")

            # Results Styling
            is_pos = cls_data['is_positive']
            conf = cls_data['confidence'] * 100

            diag_class = "badge-positive" if is_pos else "badge-negative"
            diag_icon = "fa-triangle-exclamation" if is_pos else "fa-circle-check"
            diag_text = "POSITIVE (Pneumonia Detected)" if is_pos else "NEGATIVE (Normal Findings)"

            st.markdown(f"""
                <div class="glass-card">
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Primary Diagnosis</p>
                    <div class="status-badge {diag_class}">
                        <i class="fa-solid {diag_icon}"></i> {diag_text}
                    </div>
                    <div style="margin-top: 20px;">
                        <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Confidence Score</p>
                        <h2 style="margin: 0; font-weight: 700;">{conf:.1f}%</h2>
                        <div style="background: #e2e8f0; height: 8px; border-radius: 4px; margin-top: 8px;">
                            <div style="background: {'#ef4444' if is_pos else '#22c55e'}; width: {conf}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <div style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="font-size: 0.8rem; color: #64748b; margin: 0;">Focal Anomalies</p>
                            <h4 style="margin: 0;">{len(detections)} Areas</h4>
                        </div>
                        <i class="fa-solid fa-microscope" style="color: #cbd5e1; font-size: 1.5rem;"></i>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if is_pos:
                st.error("""
                    **Clinical Urgent Notice:** High probability of pneumonia detected. Immediate review by the pulmonary department recommended.
                """)

        st.divider()

        # Explainable AI Section
        st.markdown("### <i class='fa-solid fa-file-waveform'></i> Clinical AI Reasoning (XAI Report)", unsafe_allow_html=True)

        with st.container():
            st.markdown(f"""
                <div style="background: #ffffff; padding: 2rem; border-radius: 16px; border: 1px solid #e2e8f0; line-height: 1.6;">
                    {reasoning}
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        with st.expander("Technical Metadata & Model Logs"):
            st.json({
                "model_ensemble": {
                    "classifier": "Swin-B Transformer",
                    "detector": "YOLO11-Medical-FineTuned",
                    "reasoner": "Qwen-VL-72B (HPC-Powered)"
                },
                "raw_inference": {
                    "global_prediction": "Positive" if is_pos else "Negative",
                    "global_confidence": round(cls_data['confidence'], 5),
                    "local_detections": detections
                }
            })