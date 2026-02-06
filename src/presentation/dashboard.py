# path: z_realism_ai/src/presentation/dashboard.py
# description: Z-Realism Research Console v7.2 - Automated Identity Fusion.
#              FEATURING: Automatic parameter injection from the Heuristic Engine.
#              FIXED: High-contrast visibility for text and UI elements.
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
    page_title="Z-Realism Studio v7.2",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Automated Session State Initialization ---
# These variables store the "expert" configuration determined by the analyzer.
if 'cfg_val' not in st.session_state: st.session_state.cfg_val = 7.0
if 'cn_val' not in st.session_state: st.session_state.cn_val = 0.45
if 'steps_val' not in st.session_state: st.session_state.steps_val = 30
if 'prompt_val' not in st.session_state: st.session_state.prompt_val = "raw photo, highly detailed skin"
if 'analysis_essence' not in st.session_state: st.session_state.analysis_essence = "Awaiting Entity Input"

# --- Advanced Obsidian UI Styling ---
def inject_obsidian_styles():
    st.markdown("""
        <style>
        /* Base Domain Colors */
        .stApp {
            background-color: #050505;
            color: #ffffff !important;
        }

        /* High-Contrast Labels (Fixing Dark-on-Dark issues) */
        label, .stMarkdown p, .stSlider label, .stSelectbox label {
            color: #ffffff !important;
            font-weight: 700 !important;
            text-shadow: 2px 2px 5px rgba(0,0,0,1);
        }

        /* Sidepanel Aesthetics */
        section[data-testid="stSidebar"] {
            background-color: #111111 !important;
            border-right: 1px solid #ff7b00;
        }

        /* Glowing Metric Values */
        [data-testid="stMetricValue"] {
            color: #00f2ff !important;
            font-family: 'Source Code Pro', monospace;
            font-weight: 900;
        }

        /* Primary Action Button (Z-Realism Orange) */
        .stButton > button {
            background: linear-gradient(135deg, #ff7b00 0%, #ff4800 100%) !important;
            color: #ffffff !important;
            font-weight: 900 !important;
            border: 2px solid #ffffff !important;
            height: 3.5rem;
            width: 100%;
            border-radius: 8px;
            letter-spacing: 2px;
            transition: 0.3s all cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255, 123, 0, 0.4);
        }
        
        /* Analysis Info Panel */
        .essence-box {
            background-color: rgba(255, 123, 0, 0.1);
            border: 1px solid #ff7b00;
            padding: 10px;
            border-radius: 5px;
            font-size: 0.85rem;
            color: #ff7b00;
            margin-bottom: 20px;
        }

        /* Code/Prompt Traceability Container */
        .prompt-container {
            background-color: #000000;
            border: 1px dashed #333;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Source Code Pro', monospace;
            font-size: 0.8rem;
            color: #888;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Automation Logic: Visual DNA Analysis ---
def trigger_automated_analysis(file_bytes, file_name, char_name):
    """
    Communicates with the Heuristic Engine to retrieve expert parameters.
    Automatically updates the UI state.
    """
    try:
        files = {"file": (file_name, file_bytes)}
        data = {"character_name": char_name}
        resp = requests.post(f"{API_URL}/analyze", files=files, data=data).json()
        
        if resp.get("status") == "success":
            recs = resp["recommendations"]
            # Reactive UI Update: Injecting parameters into state
            st.session_state.cfg_val = recs["cfg_scale"]
            st.session_state.cn_val = recs["cn_scale"]
            st.session_state.steps_val = recs["steps"]
            st.session_state.prompt_val = recs["texture_prompt"]
            st.session_state.analysis_essence = resp["detected_essence"]
            return True
    except Exception as e:
        st.sidebar.error(f"Analysis Link Failed: {e}")
    return False

# --- Main Interface Orchestration ---
def main():
    inject_obsidian_styles()
    
    # 1. Dashboard Header
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 20px; margin-bottom: 30px;'>
            <h1 style='margin: 0; font-size: 3rem; font-weight: 900;'>🐉 Z-REALISM <span style='color:#ff7b00'>CONSOLE</span></h1>
            <div style='background: #ff7b00; color: black; padding: 4px 15px; border-radius: 5px; font-size: 0.8rem; font-weight: 900;'>AUTOMATED v7.2</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. SIDEBAR: RESEARCH CONTROLS
    with st.sidebar:
        st.markdown("### 🔬 ENTITY DEFINITION")
        char_name = st.text_input("IDENTITY NAME", "Goku")
        uploaded_file = st.file_uploader("SOURCE ARTWORK (2D)", type=["png", "jpg", "jpeg"])
        
        # Trigger for the Automation Logic
        if uploaded_file and st.button("🔍 ANALYZE VISUAL DNA"):
            with st.spinner("Decoding Species Heuristics..."):
                if trigger_automated_analysis(uploaded_file.getvalue(), uploaded_file.name, char_name):
                    st.toast("Expert parameters injected!", icon="🧬")

        st.divider()
        
        st.markdown("### ⚙️ NEURAL CORE TUNING")
        res_val = st.select_slider("Resolution Anchor", options=[384, 512, 640, 768], value=512)
        
        # Sliders are now linked to session_state defaults
        steps = st.slider("Inference Steps", 10, 60, st.session_state.steps_val)
        cfg = st.slider("Guidance (CFG)", 1.0, 15.0, st.session_state.cfg_val, 0.5)
        cn_weight = st.slider("Structural Weight (CN)", 0.0, 1.0, st.session_state.cn_val, 0.05)
        
        st.markdown("### ✍️ TEXTURAL GUIDANCE")
        prompt = st.text_area("Live-Action Prompt", st.session_state.prompt_val, height=130)

        st.divider()
        initiate_btn = st.button("🚀 INITIATE TRANSFORMATION", disabled=not uploaded_file)

    # 3. WORKSPACE: IMAGE DUAL-VIEW
    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.subheader("Source Domain")
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True)
            st.markdown(f"<div class='essence-box'><b>STRATEGY:</b> {st.session_state.analysis_essence}</div>", unsafe_allow_html=True)
        else:
            st.info("Upload 2D source artwork to begin the Live-Action mapping.")

    with col_r:
        st.subheader("Synthetic Domain")
        if initiate_btn and uploaded_file:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = {
                "character_name": char_name, "feature_prompt": prompt,
                "resolution_anchor": res_val, "steps": steps, 
                "cfg_scale": cfg, "cn_scale": cn_weight
            }
            
            try:
                with st.status("🧬 Identity Fusion Active...", expanded=True) as status:
                    st.write("Initializing Latent Tensors...")
                    resp = requests.post(f"{API_URL}/transform", files=files, data=data).json()
                    task_id = resp["task_id"]
                    
                    # Progress Polling
                    p_bar = st.progress(0)
                    while True:
                        info = requests.get(f"{API_URL}/status/{task_id}").json()
                        if info["status"] == "PROGRESS":
                            pct = info["progress"]["percent"]
                            p_bar.progress(pct)
                            status.update(label=f"🔄 Latent De-noising: {pct}%")
                        elif info["status"] == "SUCCESS":
                            p_bar.progress(100)
                            pkg = requests.get(f"{API_URL}/result/{task_id}").json()
                            img_bytes = base64.b64decode(pkg["result_image_b64"])
                            st.image(img_bytes, use_column_width=True)
                            
                            st.session_state.last_metrics = pkg["metrics"]
                            status.update(label="✨ Transformation Complete!", state="complete")
                            break
                        elif info["status"] == "FAILURE":
                            st.error("Engine failed. Check hardware logs.")
                            break
                        time.sleep(1.5)
            except Exception as e:
                st.error(f"Engine Link Failure: {e}")
        else:
            st.caption("Neural engine in standby mode.")

    # 4. SCIENTIFIC FIDELITY REPORT
    if "last_metrics" in st.session_state:
        st.divider()
        m = st.session_state.last_metrics
        st.markdown("### 📊 FIDELITY & PERFORMANCE ANALYSIS")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("SSIM (Structure)", f"{int(m['structural_similarity']*100)}%")
        c2.metric("Identity Retention", f"{int(m['identity_preservation']*100)}%")
        c3.metric("Research Latency", f"{m['inference_time']}s")
        c4.metric("Hardware", "CUDA / GTX 1060" if not m['is_mock'] else "MOCK")

        with st.expander("📝 Traceability Data (Prompts)"):
            st.markdown("**Positive Guidance:**")
            st.markdown(f"<div class='prompt-container'>{m['full_prompt']}</div>", unsafe_allow_html=True)
            st.markdown("**Negative Filter:**")
            st.markdown(f"<div class='prompt-container' style='color:#ff4444'>{m['negative_prompt']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()