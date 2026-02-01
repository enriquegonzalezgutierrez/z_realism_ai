# path: z_realism_ai/src/presentation/dashboard.py
# description: Professional Visual Interface with Dynamic Control Suite.
#              FIXED: Corrected Python function definition order (NameError).
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import streamlit as st
import requests
import time
import io
from PIL import Image

# -----------------------------------------------------------------------------
# Configuration & Global Constants
# -----------------------------------------------------------------------------
API_URL = "http://z-realism-api:8000"

st.set_page_config(
    page_title="Z-Realism AI | Pro Studio",
    page_icon="⚡",
    layout="wide"
)

# Resolution mapping
RESOLUTION_OPTIONS = {
    "Fast Draft (384px)": 384,
    "Standard Quality (512px)": 512,
    "High Detail (640px)": 640,
    "Ultra HD (768px)": 768
}

# -----------------------------------------------------------------------------
# FINAL HIGH-CONTRAST STYLING DEFINITION
# -----------------------------------------------------------------------------
def apply_pro_styles():
    """
    Modern cinematic UI – high contrast, responsive, pro-grade.
    Logic untouched.
    """
    st.markdown("""
    <style>

    /* ---------------------------------------------------------
    GLOBAL RESET / HIDE STREAMLIT UI
    --------------------------------------------------------- */
    #MainMenu, footer, header { visibility: hidden; }
    div[data-testid="stStatusWidget"] { visibility: hidden; }

    /* ---------------------------------------------------------
    ROOT THEME
    --------------------------------------------------------- */
    .stApp {
        background: radial-gradient(1200px at 20% 0%, #0f172a 0%, #020617 60%);
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 2.5rem;
        max-width: 1400px;
    }

    /* ---------------------------------------------------------
    TYPOGRAPHY
    --------------------------------------------------------- */
    h1, h2, h3 {
        color: #f8fafc;
        letter-spacing: 0.5px;
    }

    p, label {
        color: #cbd5f5;
    }

    .main-title {
        font-size: clamp(2.4rem, 5vw, 3.6rem);
        font-weight: 800;
        text-align: center;
        letter-spacing: 4px;
        color: #22d3ee;
        text-shadow: 0 0 25px rgba(34,211,238,.45);
        margin-bottom: .5rem;
    }

    .sub-title {
        text-align: center;
        color: #94a3b8;
        margin-bottom: 3rem;
        font-size: 1.05rem;
    }

    /* ---------------------------------------------------------
    SIDEBAR
    --------------------------------------------------------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617, #020617);
        border-right: 1px solid rgba(148,163,184,.15);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: #e5e7eb;
    }

    /* ---------------------------------------------------------
    INPUTS
    --------------------------------------------------------- */
    .stTextInput input,
    .stTextArea textarea {
        background: rgba(15,23,42,.9);
        color: #f8fafc;
        border: 1px solid rgba(148,163,184,.25);
        border-radius: 10px;
        padding: 0.65rem 0.75rem;
        transition: all .2s ease;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #22d3ee;
        box-shadow: 0 0 0 1px rgba(34,211,238,.35);
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #64748b;
    }

    .stSelectbox div[data-baseweb="select"] {
        background: rgba(15,23,42,.9);
        border: 1px solid rgba(148,163,184,.25);
        border-radius: 10px;
    }

    /* ---------------------------------------------------------
    BUTTONS (PRIMARY ACTION)
    --------------------------------------------------------- */
    .stButton > button {
        width: 100%;
        height: 4.2rem;
        border-radius: 14px;
        border: none;
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: 1px;
        color: #020617;
        background: linear-gradient(135deg, #22d3ee, #38bdf8);
        box-shadow:
            0 10px 30px rgba(56,189,248,.35),
            inset 0 1px 0 rgba(255,255,255,.4);
        transition: all .25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 15px 40px rgba(56,189,248,.45);
    }

    /* ---------------------------------------------------------
    CARDS / IMAGES
    --------------------------------------------------------- */
    .img-card {
        background: linear-gradient(
            180deg,
            rgba(15,23,42,.85),
            rgba(2,6,23,.95)
        );
        border-radius: 20px;
        padding: 22px;
        border: 1px solid rgba(148,163,184,.18);
        box-shadow:
            0 20px 50px rgba(0,0,0,.6),
            inset 0 1px 0 rgba(255,255,255,.04);
    }

    .label-card {
        margin-top: 1rem;
        text-align: center;
        font-size: .85rem;
        letter-spacing: 3px;
        font-weight: 700;
        color: #22d3ee;
    }

    /* ---------------------------------------------------------
    ALERTS / STATUS / PROGRESS
    --------------------------------------------------------- */
    .stAlert {
        background: #f8fafc !important;
        border-radius: 12px;
    }

    .stAlert p {
        color: #020617 !important;
        font-weight: 600;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #22d3ee, #38bdf8);
    }

    /* ---------------------------------------------------------
    DIVIDERS
    --------------------------------------------------------- */
    hr {
        border-color: rgba(148,163,184,.2);
        margin: 2rem 0;
    }

    /* ---------------------------------------------------------
    RESPONSIVE TWEAKS
    --------------------------------------------------------- */
    @media (max-width: 768px) {
        .main-title {
            letter-spacing: 2px;
        }
        .img-card {
            padding: 16px;
        }
    }

    </style>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# EXECUTION START
# -----------------------------------------------------------------------------
# FIX: Call the styling function immediately after its definition
apply_pro_styles()


# -----------------------------------------------------------------------------
# Sidebar - Control Suite UX
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ GENERATION CONTROLS")
    st.divider()
    
    st.markdown("#### 1. Input & Identity")
    char_name = st.text_input("Character Name", placeholder="e.g. Son Goku")
    uploaded_file = st.file_uploader("Upload Anime Source (Image)", type=["png", "jpg", "jpeg"])
    
    st.divider()
    st.markdown("#### 2. Advanced Fine-Tuning")

    resolution_label = st.selectbox(
        "Output Resolution Anchor (Shortest Side)",
        options=list(RESOLUTION_OPTIONS.keys()),
        index=2
    )
    resolution_anchor = RESOLUTION_OPTIONS[resolution_label]
    
    if resolution_anchor >= 768:
        st.error("⚠️ High resolution selected. Expect long processing times.")
    
    feature_prompt = st.text_area(
        "Key Features (e.g., boots, armor, facial details)",
        value="",
        placeholder="e.g., wearing yellow boots, fierce expression, dynamic cape, sharp jawline"
    )

    st.divider()
    
    try:
        health = requests.get(f"{API_URL}/health", timeout=1.0).json()
        st.success(f"🟢 API Status: Online ({health['hardware'].upper()})")
    except:
        st.error("🔴 API Status: Offline")

# -----------------------------------------------------------------------------
# Main Dashboard
# -----------------------------------------------------------------------------
st.markdown('<h1 class="main-title">Z-REALISM STUDIO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI Powered Cinematic Character Synthesis</p>', unsafe_allow_html=True)

if uploaded_file and char_name:
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<div class="img-card">', unsafe_allow_html=True)
        st.image(Image.open(uploaded_file), use_column_width=True)
        st.markdown('<p class="label-card">INPUT REFERENCE</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔥 INITIATE SYNTHESIS"):
        try:
            # 1. Dispatch Task
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"character_name": char_name, "feature_prompt": feature_prompt, "resolution_anchor": resolution_anchor}
            dispatch = requests.post(f"{API_URL}/transform", files=files, data=data)
            dispatch.raise_for_status()
            task_id = dispatch.json()["task_id"]

            # 2. Real-time Feedback Loop
            with st.status("🔮 Analyzing Source and Preparing Latent Space...", expanded=True) as status_box:
                progress_bar = st.progress(0)
                status_text = st.empty()
                start_time = time.time()
                
                while True:
                    status_info = requests.get(f"{API_URL}/status/{task_id}").json()
                    current_state = status_info["status"]
                    progress_meta = status_info.get("progress")
                    
                    elapsed = int(time.time() - start_time)

                    if current_state == "PROGRESS" and progress_meta:
                        curr, total, pct = progress_meta["current"], progress_meta["total"], progress_meta["percent"]
                        progress_bar.progress(pct)
                        status_text.info(f"🧠 **AI Step:** {curr} / {total} | Progress: {pct}% | Time: {elapsed}s")
                        status_box.update(label=f"⚡ Synthesis In Progress... {pct}%", state="running")

                    elif current_state == "SUCCESS":
                        progress_bar.progress(100)
                        status_text.success(f"✅ Synthesis Complete! Total Time: {elapsed}s")
                        status_box.update(label="✨ Result Ready!", state="complete", expanded=False)
                        break
                    
                    elif current_state == "FAILURE":
                        st.error("❌ Synthesis Failed. Check the worker logs (make logs-worker).")
                        break
                    
                    time.sleep(1.0) 

            # 3. Final Result Retrieval
            result_resp = requests.get(f"{API_URL}/result/{task_id}")
            if result_resp.status_code == 200:
                with col_right:
                    st.markdown('<div class="img-card">', unsafe_allow_html=True)
                    st.image(Image.open(io.BytesIO(result_resp.content)), use_column_width=True)
                    st.markdown('<p class="label-card">Z-REALISM OUTPUT</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.download_button(
                        label="📥 Download Photo Reality",
                        data=result_resp.content,
                        file_name=f"z_realism_{char_name}_{resolution_anchor}px.png",
                        mime="image/png"
                    )
            
        except Exception as e:
            st.error(f"⚠️ Synthesis Error: {str(e)}")

else:
    st.divider()
    intro_col = st.columns([1, 2, 1])
    with intro_col[1]:
        st.info("👈 Use the Control Suite in the sidebar to upload and configure.")
        st.markdown("""
        ### Current Architecture:
        - **Model:** Stable Diffusion v1.5 (Calibrated for Structural Integrity)
        - **Engine:** Asynchronous Celery Worker (Optimized for CPU Performance)
        """)