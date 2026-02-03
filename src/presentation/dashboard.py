# path: z_realism_ai/src/presentation/dashboard.py
# description: Z-Realism Research Studio v5.5 - Universal Edition.
#              FEATURING: White-labeled UI (No Streamlit branding) and 
#              Multi-Modal Expert reactivity for 50+ Dragon Ball archetypes.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import streamlit as st
import requests
import time
import base64
import os
import io
from PIL import Image

# --- System Environment ---
API_URL = os.getenv("API_URL", "http://z-realism-api:8000")

st.set_page_config(
    page_title="Z-Realism Expert Studio v5.5",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Persistence ---
if 'cfg_val' not in st.session_state: st.session_state.cfg_val = 7.5
if 'cn_val' not in st.session_state: st.session_state.cn_val = 0.40
if 'steps_val' not in st.session_state: st.session_state.steps_val = 20
if 'prompt_val' not in st.session_state: st.session_state.prompt_val = "detailed human face"
if 'last_analyzed_file' not in st.session_state: st.session_state.last_analyzed_file = None
if 'last_analyzed_name' not in st.session_state: st.session_state.last_analyzed_name = ""
if 'analysis_essence' not in st.session_state: st.session_state.analysis_essence = "Awaiting Input"

# --- White-Labeled Premium Obsidian CSS ---
def inject_white_labeled_styles():
    """Removes Streamlit branding and applies premium research aesthetics."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=JetBrains+Mono&display=swap');

        /* === HIDE STREAMLIT BRANDING === */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        [data-testid="stHeader"] {background: rgba(0,0,0,0); height: 0px;}

        /* === BASE DOMAIN THEME === */
        .stApp {
            background: radial-gradient(circle at top, #0d0d1a 0%, #050505 100%);
            color: #ffffff !important;
            font-family: 'Inter', sans-serif;
        }

        /* === TEXT VISIBILITY === */
        h1, h2, h3, h4, h5, p, label, span, div, .stMarkdown {
            color: #ffffff !important;
            text-shadow: 0px 2px 5px rgba(0,0,0,0.9);
        }

        /* === RESEARCH PANELS === */
        .glass-panel {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(0, 242, 255, 0.15);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(20px);
            margin-bottom: 24px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.8);
        }

        /* === INPUT STYLING === */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea {
            background-color: #000000 !important;
            color: #00f2ff !important;
            border: 1px solid #222 !important;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
        }
        
        .stSlider > div > div > div { background-color: #00f2ff !important; }

        /* === ACTION BUTTON === */
        .stButton > button {
            background: linear-gradient(135deg, #00f2ff 0%, #0077ff 100%) !important;
            color: #000000 !important;
            font-weight: 900 !important;
            border: none !important;
            border-radius: 6px !important;
            height: 54px;
            letter-spacing: 2px;
            text-transform: uppercase;
            transition: 0.3s all cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 30px rgba(0, 242, 255, 0.6);
        }
        
        [data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 1px solid #1a1a1a;
        }

        /* === METRICS === */
        .stMetric {
            background: rgba(0,0,0,0.4);
            padding: 15px;
            border-radius: 10px;
            border-left: 3px solid #00f2ff;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Logic: Universal Multi-Modal Analysis ---
def trigger_universal_analysis(file_bytes, file_name, char_name):
    """
    Communicates with the /analyze endpoint to retrieve expert lore parameters.
    """
    try:
        files = {"file": (file_name, file_bytes)}
        data = {"character_name": char_name}
        response = requests.post(f"{API_URL}/analyze", files=files, data=data).json()
        
        if response.get("status") == "success":
            recs = response["recommendations"]
            # Reactive Update of Session State
            st.session_state.cfg_val = recs["cfg_scale"]
            st.session_state.cn_val = recs["cn_scale"]
            st.session_state.steps_val = recs["steps"]
            st.session_state.prompt_val = recs["texture_prompt"]
            st.session_state.analysis_essence = response["detected_essence"]
            st.session_state.last_analyzed_file = file_name
            st.session_state.last_analyzed_name = char_name
            return True
    except Exception as e:
        st.sidebar.error(f"Universal Engine Link Failed: {e}")
    return False

# --- Main Application Layout ---
def main():
    inject_white_labeled_styles()
    
    # 1. Branding (Custom Logo/Header)
    st.markdown('''
        <div style="text-align: left; padding: 20px 0 40px 0;">
            <h1 style="font-weight: 900; font-size: 3rem; margin-bottom: 0; letter-spacing: -2px;">Z-REALISM <span style="color:#00f2ff">STUDIO</span></h1>
            <p style="color:#444 !important; letter-spacing: 6px; font-size: 0.8rem; font-weight: 900;">UNIVERSAL NEURAL TRANSFORMER v5.5</p>
        </div>
    ''', unsafe_allow_html=True)

    # 2. Sidebar: Expert Input & Triggers
    with st.sidebar:
        st.markdown("### 🔬 ENTITY DEFINITION")
        char_name = st.text_input("ENTITY NAME", "Ten Shin Han", help="Species-specific heuristics will be applied based on this name.")
        uploaded_file = st.file_uploader("SOURCE ARTWORK", type=["png", "jpg", "jpeg"])
        
        # UNIVERSAL REACTIVITY: Triggered by Name or File changes
        file_changed = uploaded_file and st.session_state.last_analyzed_file != uploaded_file.name
        name_changed = char_name != st.session_state.last_analyzed_name
        
        if uploaded_file and (file_changed or name_changed):
            with st.spinner("🧬 Consulting Knowledge Base..."):
                if trigger_universal_analysis(uploaded_file.getvalue(), uploaded_file.name, char_name):
                    st.toast(f"Status: {st.session_state.analysis_essence}", icon="👽")
                    st.rerun()

        st.divider()
        
        # PARAMETERS: Pre-filled by v5.5 Expert Logic
        with st.expander("🛠️ NEURAL ENGINE CONFIG", expanded=True):
            res_val = st.select_slider("Resolution Anchor", options=[384, 512, 640, 768, 1024], value=640)
            steps = st.slider("Sampling Steps", 10, 80, st.session_state.steps_val)
            cfg = st.slider("Guidance Scale (CFG)", 1.0, 20.0, st.session_state.cfg_val, 0.5)
            cn_weight = st.slider("Structural Adherence", 0.0, 1.0, st.session_state.cn_val, 0.01)
            prompt = st.text_area("Textural Booster", st.session_state.prompt_val, height=130)

        st.divider()
        
        # System Hardware Guard
        try:
            status = requests.get(f"{API_URL}/system/status", timeout=0.5).json()
            is_locked = status["locked"]
        except: is_locked = False
        
        initiate = st.button("🚀 EXECUTE SYNTHESIS", disabled=is_locked)
        if is_locked:
            st.caption(f"Hardware Priority: task_{status['owner_id'][:6]}")
            if st.button("Unlock Hardware"): requests.post(f"{API_URL}/system/unlock"); st.rerun()

    # 3. Main Workspace: Multi-Domain Canvas
    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown('<div class="glass-panel"><h5>SOURCE DOMAIN</h5>', unsafe_allow_html=True)
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True)
            st.caption(f"Expert Essense: {st.session_state.analysis_essence}")
        else:
            st.info("Upload character reference to begin.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="glass-panel"><h5>SYNTHETIC OUTPUT</h5>', unsafe_allow_html=True)
        if "final_img_data" in st.session_state:
            st.image(st.session_state.final_img_data, use_column_width=True)
            st.download_button("💾 SAVE RESEARCH (PNG)", st.session_state.final_img_data, "z_realism_v55.png")
        else:
            st.caption("Engine awaiting lore-aware tuning.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. Neural Execution Pipeline
    if initiate and uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {
            "character_name": char_name, "feature_prompt": prompt, "resolution_anchor": res_val,
            "steps": steps, "cfg_scale": cfg, "cn_scale": cn_weight
        }
        
        try:
            resp = requests.post(f"{API_URL}/transform", files=files, data=data)
            if resp.status_code == 200:
                task_id = resp.json()["task_id"]
                with st.status("🧬 NEURAL DIFFUSION ACTIVE...", expanded=True) as status_box:
                    p_bar = st.progress(0)
                    while True:
                        info = requests.get(f"{API_URL}/status/{task_id}").json()
                        if info["status"] == "PROGRESS":
                            pct = info["progress"]["percent"]
                            p_bar.progress(pct)
                            status_box.update(label=f"🔄 Latent De-noising: {pct}%")
                        elif info["status"] == "SUCCESS":
                            p_bar.progress(100)
                            status_box.update(label="✨ Synthesis Finished!", state="complete")
                            pkg = requests.get(f"{API_URL}/result/{task_id}").json()
                            st.session_state.final_img_data = base64.b64decode(pkg["result_image_b64"])
                            st.session_state.metrics = pkg["metrics"]
                            st.rerun()
                            break
                        elif info["status"] == "FAILURE":
                            st.error("Engine failure."); break
                        time.sleep(2)
        except Exception as e: st.error(f"Pipeline error: {e}")

    # 5. Scientific Assessment Report
    if "metrics" in st.session_state:
        st.divider()
        m = st.session_state.metrics
        st.markdown("### 🔬 SCIENTIFIC ASSESSMENT REPORT")
        c1, c2, c3 = st.columns(3)
        c1.metric("Structural SSIM", f"{int(m['structural_similarity']*100)}%")
        c2.metric("Identity Preservation", f"{int(m['identity_preservation']*100)}%")
        c3.metric("Research Latency", f"{m['inference_time']}s")

if __name__ == "__main__":
    main()