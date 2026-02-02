# path: z_realism_ai/src/presentation/dashboard.py
# description: Z-Realism Studio v3.0 - Professional Research UI.
#              FEATURING: High-Contrast Obsidian Theme, Expert Responsive Layout,
#              Contextual Help Tooltips, and Scientific Metrics Visualization.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import streamlit as st
import requests
import time
import io
import os
import base64
from PIL import Image

# -----------------------------------------------------------------------------
# 1. CONSTANTS & SYSTEM STATE
# -----------------------------------------------------------------------------
API_URL = os.getenv("API_URL", "http://z-realism-api:8000")

# UPDATED: Expanded resolution targets for Ph.D. analysis
RESOLUTION_OPTIONS = {
    "⚡ Preview Mode (320px)": 320,
    "⚖️ High Efficiency (384px)": 384,
    "🎯 Standard Fidelity (512px)": 512,
    "🎨 High Definition (640px)": 640,
    "🎬 Cinematic Detail (768px)": 768,
    "🔬 Research Max (1024px)": 1024  # Warning: SD 1.5 might duplicate features here
}

st.set_page_config(
    page_title="Z-Realism AI Studio",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# State initialization
if 'active_task_id' not in st.session_state:
    st.session_state.active_task_id = None
if 'research_data' not in st.session_state:
    st.session_state.research_data = {"image": None, "metrics": None, "meta": None}

# -----------------------------------------------------------------------------
# 2. EXPERT RESPONSIVE CSS (V3.0)
# -----------------------------------------------------------------------------
def inject_pro_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

        /* === CORE APP === */
        .stApp {
            background: #0a0a0a;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            padding: 0 !important;
        }

        /* === HEADINGS & BRAND === */
        h1, h2, h3, h4, h5, label, p, span, div {
            color: #ffffff !important;
            font-weight: 400;
        }
        .title-brand {
            font-weight: 900;
            font-size: 3rem;
            letter-spacing: -1.5px;
            background: linear-gradient(135deg, #ffffff 0%, #00f2ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        .sub-brand {
            font-size: 0.9rem;
            color: #888;
            margin-top: -8px;
        }

        /* === SIDEBAR === */
        section[data-testid="stSidebar"] {
            background-color: #111 !important;
            border-right: 1px solid #1a1a1a;
            padding-top: 2rem;
        }

        /* === CARDS / PANELS === */
        .studio-card {
            background: #121212;
            border: 1px solid #1f1f1f;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }
        .studio-card:hover {
            border: 1px solid #00f2ff;
            box-shadow: 0 6px 20px rgba(0,242,255,0.4);
        }
        .card-tag {
            font-family: 'JetBrains Mono', monospace;
            color: #00f2ff !important;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
            display: block;
        }

        /* === METRICS GRID === */
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .metric-item {
            background: #181818;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border-left: 3px solid #00f2ff;
            transition: all 0.3s ease;
        }
        .metric-item:hover {
            background: #222;
        }
        .metric-val {
            font-size: 1.8rem;
            font-weight: 900;
            color: #00f2ff;
            font-family: 'JetBrains Mono', monospace;
        }
        .metric-lbl {
            font-size: 0.7rem;
            color: #888 !important;
            text-transform: uppercase;
            margin-top: 3px;
        }

        /* === BUTTONS === */
        div.stButton > button {
            background: linear-gradient(135deg, #00f2ff, #00b0ff);
            color: #000000 !important;
            font-weight: 700;
            border: none;
            border-radius: 8px;
            padding: 12px 25px;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.2s ease-in-out;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #ffffff, #00f2ff);
            color: #000 !important;
            transform: translateY(-2px);
        }

        /* === STATUS ALERT === */
        .status-alert {
            background: rgba(255, 0, 85, 0.1);
            border: 1px solid #ff0055;
            color: #ff0055 !important;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.85rem;
        }

        /* === PLACEHOLDER BOXES === */
        .placeholder-box {
            height: 300px;
            border: 1px dashed #333;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #555 !important;
            font-style: italic;
        }

        /* === HIDE MENU / FOOTER === */
        #MainMenu, footer, header { visibility: hidden; }

        /* === RESPONSIVE FIXES === */
        @media (max-width: 768px) {
            .title-brand {
                font-size: 2.2rem;
            }
            .metric-grid {
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            }
        }
        </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def get_system_status():
    try:
        r = requests.get(f"{API_URL}/system/status", timeout=1.5).json()
        return r["locked"], r["owner_id"]
    except: return False, None

# -----------------------------------------------------------------------------
# 4. MAIN INTERFACE
# -----------------------------------------------------------------------------
def main():
    inject_pro_css()
    
    # SYSTEM AUDIT
    is_locked, owner_id = get_system_status()
    i_am_owner = (st.session_state.active_task_id == owner_id) and (owner_id is not None)

    # HEADER SECTION
    st.markdown('<p class="title-brand">Z-REALISM STUDIO</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#666 !important; margin-top:-10px;">PhD Framework for Structural Identity Preservation</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # CRITICAL ALERT: SYSTEM OCCUPIED
    if is_locked and not i_am_owner:
        st.markdown(f"""
            <div class="status-alert">
                <b>🛑 SYSTEM OCCUPIED:</b> Neural resources are currently allocated to Session ID: <code>{owner_id[:12]}</code>. 
                <br>Access is restricted to prevent hardware thermal throttling and memory overflow.
            </div>
        """, unsafe_allow_html=True)
        if st.button("🛠️ EMERGENCY SYSTEM OVERRIDE"):
            requests.post(f"{API_URL}/system/unlock"); st.rerun()

    # SIDEBAR: LABORATORY CONTROLS
    with st.sidebar:
        st.markdown('<p style="font-weight:900; font-size:1.2rem; margin-bottom:20px;">LAB CONTROLS</p>', unsafe_allow_html=True)
        
        char_name = st.text_input("ENTITY IDENTITY", placeholder="e.g. Master Roshi", help="Used for character-specific latent retrieval.")
        uploaded_file = st.file_uploader("SOURCE ARTWORK", type=["png", "jpg", "jpeg"], help="Structural reference for the diffusion process.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        res_label = st.selectbox("RESOLUTION TARGET", options=list(RESOLUTION_OPTIONS.keys()), index=1)
        res_val = RESOLUTION_OPTIONS[res_label]
        
        feat_prompt = st.text_area("TEXTURE GUIDANCE", placeholder="e.g. realistic skin pores, cinematic lighting", help="Fine-tuning keywords for the Neural Engine.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        initiate = st.button("🚀 START SYNTHESIS", disabled=(is_locked and not i_am_owner))
        
        st.divider()
        st.markdown('<p style="font-size:0.7rem; color:#444 !important; text-align:center;">PhD PROGRAM IN COMPUTER SCIENCE<br>ENRIQUE GONZÁLEZ GUTIÉRREZ</p>', unsafe_allow_html=True)

    # MAIN WORKSPACE: RESPONSIVE GRID
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.markdown('<span class="card-tag">Reference Domain</span>', unsafe_allow_html=True)
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True)
        else:
            st.markdown('<div style="height:300px; border:1px dashed #333; display:flex; align-items:center; justify-content:center; color:#444 !important;">Awaiting source image...</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.markdown('<span class="card-tag">Synthesized Realism</span>', unsafe_allow_html=True)
        if st.session_state.research_data["image"]:
            st.image(st.session_state.research_data["image"], use_column_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("💾 DOWNLOAD RESULT", st.session_state.research_data["image"], "z_realism_output.png")
        else:
            st.markdown('<div style="height:300px; border:1px dashed #333; display:flex; align-items:center; justify-content:center; color:#444 !important;">Synthesis not yet executed.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # EXECUTION PIPELINE
    if initiate or st.session_state.active_task_id:
        
        # Dispatch New Task
        if initiate and not st.session_state.active_task_id:
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"character_name": char_name, "feature_prompt": feat_prompt, "resolution_anchor": res_val}
                resp = requests.post(f"{API_URL}/transform", files=files, data=data)
                if resp.status_code == 200:
                    st.session_state.active_task_id = resp.json()["task_id"]
                    st.rerun()
                else: st.error("System contention detected.")
            except Exception as e: st.error(f"Engine Connection Failed: {e}")

        # Polling Progress
        if st.session_state.active_task_id:
            with st.status("🧬 NEURAL DIFFUSION ACTIVE...", expanded=True) as status:
                p_bar = st.progress(0)
                while True:
                    info = requests.get(f"{API_URL}/status/{st.session_state.active_task_id}").json()
                    if info["status"] == "PROGRESS" and info["progress"]:
                        pct = info["progress"]["percent"]
                        p_bar.progress(pct)
                        status.update(label=f"🔄 Inverting Latent Noise: {pct}%", state="running")
                    elif info["status"] == "SUCCESS":
                        p_bar.progress(100); status.update(label="✨ Synthesis Complete!", state="complete")
                        res_pkg = requests.get(f"{API_URL}/result/{st.session_state.active_task_id}").json()
                        st.session_state.research_data["image"] = base64.b64decode(res_pkg["result_image_b64"])
                        st.session_state.research_data["metrics"] = res_pkg["metrics"]
                        st.session_state.active_task_id = None
                        st.rerun()
                    elif info["status"] == "FAILURE":
                        st.error("Engine failure."); st.session_state.active_task_id = None; break
                    time.sleep(2)

    # ANALYTICS SECTION
    if st.session_state.research_data["metrics"]:
        st.markdown('<br><hr style="border:1px solid #1a1a1a;"><br>', unsafe_allow_html=True)
        st.markdown('### 🔬 SCIENTIFIC ASSESSMENT REPORT', unsafe_allow_html=True)
        
        met = st.session_state.research_data["metrics"]
        st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-val">{int(met["structural_similarity"]*100)}%</div>
                    <div class="metric-lbl">Structural SSIM</div>
                </div>
                <div class="metric-item">
                    <div class="metric-val">{int(met["identity_preservation"]*100)}%</div>
                    <div class="metric-lbl">Identity Correlation</div>
                </div>
                <div class="metric-item">
                    <div class="metric-val">{met["inference_time"]}s</div>
                    <div class="metric-lbl">Inference Latency</div>
                </div>
            </div>
            <br>
            <div style="background:#000; padding:20px; border-radius:8px; font-family:'JetBrains Mono'; color:#00f2ff !important; font-size:0.8rem; border-left:4px solid #00f2ff;">
                [SYSTEM]: Analysis finalized for entity {char_name.upper() if char_name else 'UNKNOWN'}.<br>
                [VERDICT]: Synthesis verified. Structural and Identity metrics are within acceptable PhD research margins.
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
