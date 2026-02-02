
# Main CSS
MAIN_STYLES = """
    <style>
        /* Global Styles */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            color: #1e293b;
        }

        .main {
            background-color: #f8fafc;
        }

        /* Reduce top padding */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 5rem;
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

        /* Hide specific Streamlit elements but keep sidebar button */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeader"] {background: transparent;}

        /* Custom Progress Bar Style */
        .progress-step {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 10px;
            background: #1e293b; /* Grigio scuro per contrasto */
            color: #ffffff;      /* Testo bianco leggibile */
            border: 1px solid #334155;
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

        /* Custom Primary Button Color */
        div.stButton > button[kind="primary"] {
            background-color: #1d4ed8;
            border-color: #1d4ed8;
            color: white;
            transition: all 0.3s ease;
        }

        div.stButton > button[kind="primary"]:hover {
            background-color: #1e40af;
            border-color: #1e40af;
            color: white;
            box-shadow: 0 4px 6px -1px rgba(29, 78, 216, 0.4);
        }

        div.stButton > button[kind="primary"]:focus:not(:active) {
            background-color: #1d4ed8;
            border-color: #1d4ed8;
            color: white;
        }

        /* Custom Tab Styling */
        div[data-baseweb="tab-list"] button[aria-selected="true"] {
             color: #1d4ed8 !important;
             background-color: transparent !important;
        }

        div[data-baseweb="tab-highlight"] {
             background-color: #1d4ed8 !important;
        }

        div[data-baseweb="tab-list"] button:hover {
            color: #1d4ed8 !important;
        }
    </style>
"""

# HTML Fragments
EXTERNAL_LINKS = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
"""

SPINNER_CSS = """
    <style>
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .analyzing-spinner {
            width: 16px; height: 16px;
            border: 2px solid #bfdbfe; border-top-color: #2563eb;
            border-radius: 50%; animation: spin 0.8s linear infinite;
            display: inline-block; margin-right: 8px;
        }
    </style>
"""

SIDEBAR_HEADER = """
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <img src="https://img.icons8.com/ink/color/96/lungs.png" width="60" style="filter: drop-shadow(0 0 8px rgba(37, 99, 235, 0.6));">
        <h1 style="margin-top: 8px; font-weight: 700; font-size: 1.6rem;
                   background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            XRayAnalyzer
        </h1>
        <p style="color: #64748b; font-size: 0.8rem; margin-top: -5px;">
            Motore di Ragionamento Clinico
        </p>
    </div>
"""

# Custom Loading Screen
LOADING_HTML = """
<style>
    .loader-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 70vh;
        width: 100%;
        background: transparent;
        font-family: 'Outfit', sans-serif;
    }

    .scanner-box {
        position: relative;
        width: 120px;
        height: 120px;
        margin-bottom: 2rem;
    }

    .lung-icon {
        width: 100%;
        height: 100%;
        opacity: 0.8;
        filter: drop-shadow(0 0 10px rgba(37, 99, 235, 0.5));
    }

    .scan-line {
        position: absolute;
        top: 0;
        left: -10%;
        width: 120%;
        height: 4px;
        background: #00f2fe;
        box-shadow: 0 0 15px #00f2fe, 0 0 5px #4facfe;
        animation: scan 2s ease-in-out infinite;
        border-radius: 50%;
        opacity: 0.8;
    }

    @keyframes scan {
        0% { top: 0%; opacity: 0; }
        15% { opacity: 1; }
        50% { top: 100%; }
        85% { opacity: 1; }
        100% { top: 0%; opacity: 0; }
    }

    .loader-text {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        letter-spacing: 1px;
        margin-top: 10px;
        background: linear-gradient(90deg, #2563eb, #00f2fe, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: shine 3s linear infinite;
    }

    .loader-subtext {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 8px;
    }

    @keyframes shine {
        to {
            background-position: 200% center;
        }
    }
</style>

<div class="loader-container">
    <div class="scanner-box">
        <img src="https://img.icons8.com/ink/color/96/lungs.png" class="lung-icon">
        <div class="scan-line"></div>
    </div>
    <div class="loader-text">INIZIALIZZAZIONE SISTEMI</div>
    <div class="loader-subtext">Caricamento modelli neurali e pipeline diagnostica...</div>
</div>
"""

# Timeline Step Template
TIMELINE_STEP_TEMPLATE = """
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
    <i class="fa-solid {icon}" style="font-size: 1.2rem; color: #60a5fa;"></i>
    <strong style="color: #ffffff; font-size: 1.05rem;">{title}</strong>
    <span style="margin-left: auto; background: #dcfce7; color: #166534;
                 padding: 3px 10px; border-radius: 10px; font-size: 0.75rem;">
        <i class="fa-solid fa-check"></i> Completato
    </span>
</div>
<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2); color: #e2e8f0; line-height: 1.7;">
    {content}
</div>
"""

# Timeline Active Step Template
TIMELINE_ACTIVE_TEMPLATE = """
<div style="margin-top: 10px; border: 1px solid #3b82f6; border-radius: 12px; overflow: hidden;">
    <div style="background: rgba(59, 130, 246, 0.1); padding: 12px 16px; display: flex; align-items: center; gap: 12px;">
        <div class="analyzing-spinner" style="width: 16px; height: 16px;"></div>
        <strong style="color: #93c5fd;">{title}</strong>
    </div>
    <div style="padding: 16px; background: rgba(30, 41, 59, 0.5);">
        <p style="color: #94a3b8; font-style: italic; margin: 0;">Analisi in corso...</p>
    </div>
</div>
"""

# Metric Card Template
METRIC_CARD_TEMPLATE = """
<div style="background-color: {color}10; border: 1px solid {color}40; padding: 1.5rem; border-radius: 12px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: all 0.3s ease;">
    <div style="background-color: {color}20; padding: 12px; border-radius: 50%; margin-bottom: 15px;">
        <i class="fa-solid {icon}" style="font-size: 1.5rem; color: {color}; display: block;"></i>
    </div>
    <p style="margin: 0; font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{title}</p>
    <h3 style="margin: 5px 0 0 0; color: #1e293b; font-size: 2rem; font-weight: 800;">{value}</h3>
</div>
"""

# Result Badge Template
RESULT_BADGE_TEMPLATE = """
<div class="">
    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Diagnosi Primaria</p>
    <div class="status-badge {diag_class}">
        <i class="fa-solid {diag_icon}"></i> {diag_text}
    </div>
    <div style="margin-top: 20px;">
        <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 0px;">Punteggio di Confidenza</p>
        <div style="margin: 0; font-weight: 700; font-size: 1.8rem; line-height: 1.2;">{conf:.1f}%</div>
        <div style="background: #e2e8f0; height: 8px; border-radius: 4px; margin-top: 8px;">
            <div style="background: {bar_color}; width: {conf}%; height: 100%; border-radius: 4px;"></div>
        </div>
    </div>
    <div style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <p style="font-size: 0.8rem; color: #64748b; margin: 0;">Anomalie Focali</p>
            <div style="margin: 0; font-size: 1.2rem; font-weight: 600;">{num_detections} Aree</div>
        </div>
        <i class="fa-solid fa-microscope" style="color: #cbd5e1; font-size: 1.5rem;"></i>
    </div>
    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between;">
    <div>
    <p style="font-size: 0.8rem; color: #64748b; margin: 0;">Livello di Gravità</p>
    <div style="margin: 2px 0 0 0; color: #475569; font-weight: 600; font-size: 1rem;">{severity}</div>
    </div>
    <div style="text-align: right;">
    <p style="font-size: 0.8rem; color: #64748b; margin: 0;">Qualità Scansione</p>
    <div style="margin: 2px 0 0 0; color: #475569; font-weight: 600; font-size: 1rem;">Ottimale (HD)</div>
    </div>
    </div>
</div>
"""
