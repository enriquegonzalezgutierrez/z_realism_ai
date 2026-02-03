# path: z_realism_ai/src/presentation/dashboard.py
# description: Z-Realism Research Studio v5.7 - Batch Tuning Edition.
#              FEATURING: Implementation of a batch execution mode to compare 
#              hyper-parameter effects (CN/CFG/Steps) simultaneously.
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
    page_title="Z-Realism Expert Studio v5.7",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Hyper-parameter Sets for Automated Research ---
GOKU_TUNING_SETS = [
    {"name": "Test A: Default/Balanced", "cn_scale": 0.60, "cfg_scale": 7.5, "steps": 20},
    {"name": "Test B: High Structure (CN)", "cn_scale": 0.80, "cfg_scale": 7.5, "steps": 20},
    {"name": "Test C: Low Guidance (CFG)", "cn_scale": 0.60, "cfg_scale": 5.0, "steps": 20},
    {"name": "Test D: Max Structure/Low Guidance", "cn_scale": 0.85, "cfg_scale": 5.5, "steps": 30},
]


# --- Session State Persistence ---
if 'cfg_val' not in st.session_state: st.session_state.cfg_val = 7.5
if 'cn_val' not in st.session_state: st.session_state.cn_val = 0.40
if 'steps_val' not in st.session_state: st.session_state.steps_val = 20
if 'prompt_val' not in st.session_state: st.session_state.prompt_val = "detailed human face"
if 'last_analyzed_file' not in st.session_state: st.session_state.last_analyzed_file = None
if 'last_analyzed_name' not in st.session_state: st.session_state.last_analyzed_name = ""
if 'analysis_essence' not in st.session_state: st.session_state.analysis_essence = "Awaiting Input"
# NEW: Storage for batch results
if 'tuning_results' not in st.session_state: st.session_state.tuning_results = []
# NEW: Flag to track if we are running a batch
if 'batch_running' not in st.session_state: st.session_state.batch_running = False


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
        
        /* Specific panel for batch results */
        .batch-panel {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid #00f2ff;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 20px;
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
        
        /* Batch Button Styling */
        #batch-button button {
            background: linear-gradient(135deg, #ff9900 0%, #cc5500 100%) !important;
            color: white !important;
            height: 40px !important;
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
        
        /* === CODE/PROMPT BLOCK STYLING === */
        .prompt-block {
            background-color: #0d0d1a;
            border: 1px dashed #333;
            padding: 15px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #e0e0e0;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .negative-prompt-block {
            background-color: #1a0d0d;
            border: 1px dashed #553333;
            color: #ff8888;
            padding: 15px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
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


def run_single_synthesis_task(data, files, status_box, progress_bar, task_name):
    """Handles dispatching a single task and monitoring its progress."""
    
    # 1. Dispatch Task
    resp = requests.post(f"{API_URL}/transform", files=files, data=data)
    if resp.status_code == 429:
        status_box.write(f"SKIPPING {task_name}: Hardware resources busy.")
        return None
    elif resp.status_code != 200:
        status_box.error(f"Failed to dispatch {task_name}: {resp.text}")
        return None
        
    task_id = resp.json()["task_id"]
    status_box.update(label=f"🔄 Latent De-noising: {task_name}", state="running")
    
    # 2. Monitor Loop
    while True:
        info = requests.get(f"{API_URL}/status/{task_id}").json()
        if info["status"] == "PROGRESS":
            pct = info["progress"]["percent"]
            progress_bar.progress(pct)
            status_box.update(label=f"🔄 {task_name}: {pct}%")
        elif info["status"] == "SUCCESS":
            progress_bar.progress(100)
            status_box.update(label=f"✨ {task_name} Finished!", state="complete")
            pkg = requests.get(f"{API_URL}/result/{task_id}").json()
            
            # 3. Compile Result Package
            result_package = {
                "name": task_name,
                "params": data,
                "metrics": pkg["metrics"],
                "image_data": base64.b64decode(pkg["result_image_b64"])
            }
            return result_package
        elif info["status"] == "FAILURE":
            status_box.error(f"{task_name} Engine failure.");
            return None
        time.sleep(2)


# --- Main Application Layout ---
def main():
    inject_white_labeled_styles()
    
    # 1. Branding (Custom Logo/Header)
    st.markdown('''
        <div style="text-align: left; padding: 20px 0 40px 0;">
            <h1 style="font-weight: 900; font-size: 3rem; margin-bottom: 0; letter-spacing: -2px;">Z-REALISM <span style="color:#00f2ff">STUDIO</span></h1>
            <p style="color:#444 !important; letter-spacing: 6px; font-size: 0.8rem; font-weight: 900;">UNIVERSAL NEURAL TRANSFORMER v5.7 (BATCH)</p>
        </div>
    ''', unsafe_allow_html=True)

    # 2. Sidebar: Expert Input & Triggers
    with st.sidebar:
        st.markdown("### 🔬 ENTITY DEFINITION")
        char_name = st.text_input("ENTITY NAME", "Goku", help="Species-specific heuristics will be applied based on this name.")
        uploaded_file = st.file_uploader("SOURCE ARTWORK", type=["png", "jpg", "jpeg"])
        
        # UNIVERSAL REACTIVITY: Triggered by Name or File changes
        file_changed = uploaded_file and st.session_state.last_analyzed_file != uploaded_file.name
        name_changed = char_name != st.session_state.last_analyzed_name
        
        if uploaded_file and (file_changed or name_changed):
            # Clear previous tuning results when a new file/name is loaded
            st.session_state.tuning_results = []
            with st.spinner("🧬 Consulting Knowledge Base..."):
                if trigger_universal_analysis(uploaded_file.getvalue(), uploaded_file.name, char_name):
                    st.toast(f"Status: {st.session_state.analysis_essence}", icon="👽")
                    st.rerun()

        st.divider()
        
        # PARAMETERS: Pre-filled by v5.5 Expert Logic (Used for manual runs only)
        with st.expander("🛠️ MANUAL ENGINE CONFIG", expanded=True):
            res_val = st.select_slider("Resolution Anchor", options=[384, 512, 640, 768, 1024], value=640)
            steps = st.slider("Sampling Steps", 10, 80, st.session_state.steps_val)
            cfg = st.slider("Guidance Scale (CFG)", 1.0, 20.0, st.session_state.cfg_val, 0.5)
            cn_weight = st.slider("Structural Adherence", 0.0, 1.0, st.session_state.cn_val, 0.01)
            prompt = st.text_area("Textural Booster", st.session_state.prompt_val, height=130)

        st.divider()
        
        # System Hardware Guard & Action Buttons
        try:
            status = requests.get(f"{API_URL}/system/status", timeout=0.5).json()
            is_locked = status["locked"] or st.session_state.batch_running
        except: 
            is_locked = True # Assume locked if API is down
            status = {"owner_id": "N/A"}

        
        col_m, col_t = st.columns(2)
        with col_m:
            initiate = st.button("🚀 MANUAL SYNTHESIS", disabled=is_locked or not uploaded_file)
        with col_t:
            st.markdown('<div id="batch-button">', unsafe_allow_html=True)
            batch_initiate = st.button("🧪 RUN BATCH EXPERIMENT", disabled=is_locked or not uploaded_file)
            st.markdown('</div>', unsafe_allow_html=True)

        if is_locked:
            if st.session_state.batch_running:
                 st.caption("Batch Experiment in progress...")
            else:
                st.caption(f"Hardware Priority: task_{status['owner_id'][:6]}")
                if st.button("Unlock Hardware"): requests.post(f"{API_URL}/system/unlock"); st.rerun()

    # 3. Main Workspace: Multi-Domain Canvas (Hidden if batch running)
    if not st.session_state.batch_running:
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
            st.markdown('<div class="glass-panel"><h5>MANUAL SYNTHETIC OUTPUT</h5>', unsafe_allow_html=True)
            if "final_img_data" in st.session_state and 'tuning_results' not in st.session_state:
                st.image(st.session_state.final_img_data, use_column_width=True)
                st.download_button("💾 SAVE RESEARCH (PNG)", st.session_state.final_img_data, "z_realism_v57.png")
            else:
                st.caption("Engine awaiting lore-aware tuning.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # 4. Manual Execution Pipeline
        if initiate and uploaded_file:
            st.session_state.tuning_results = [] # Clear previous batch results
            st.session_state.batch_running = False # Ensure batch flag is off
            
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {
                "character_name": char_name, "feature_prompt": prompt, "resolution_anchor": res_val,
                "steps": steps, "cfg_scale": cfg, "cn_scale": cn_weight
            }
            
            with st.status("🧬 NEURAL DIFFUSION ACTIVE...", expanded=True) as status_box:
                p_bar = st.progress(0)
                
                # Use the helper function for single run logic
                result = run_single_synthesis_task(data, files, status_box, p_bar, "MANUAL RUN")
                
                if result:
                    st.session_state.final_img_data = result["image_data"]
                    st.session_state.metrics = result["metrics"]
                    st.rerun()

        # 5. Scientific Assessment Report (Manual Run)
        if "metrics" in st.session_state and not st.session_state.tuning_results:
            st.divider()
            m = st.session_state.metrics
            st.markdown("### 🔬 SCIENTIFIC ASSESSMENT REPORT")
            c1, c2, c3 = st.columns(3)
            c1.metric("Structural SSIM", f"{int(m['structural_similarity']*100)}%")
            c2.metric("Identity Preservation", f"{int(m['identity_preservation']*100)}%")
            c3.metric("Research Latency", f"{m['inference_time']}s" + (" (Mock)" if m['is_mock'] else ""))

            st.subheader("Traceability Data (v5.6)")
            
            with st.expander("PROMPT DATA"):
                st.markdown("#### POSITIVE PROMPT (Input to Engine)")
                st.markdown(f'<div class="prompt-block">{m["full_prompt"]}</div>', unsafe_allow_html=True)
                
                st.markdown("#### NEGATIVE PROMPT (Quality Gate)")
                st.markdown(f'<div class="negative-prompt-block">{m["negative_prompt"]}</div>', unsafe_allow_html=True)
    
    # 6. BATCH EXECUTION LOGIC
    if batch_initiate and uploaded_file:
        st.session_state.tuning_results = [] # Clear previous results
        st.session_state.batch_running = True
        st.rerun() # Rerun to lock the UI
    
    if st.session_state.batch_running and uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        st.title("🧪 Batch Experimentation In Progress...")
        
        # Use a single status container for the entire batch job
        with st.status(f"Executing {len(GOKU_TUNING_SETS)} Tasks for {char_name}", expanded=True) as batch_status:
            
            # Loop through the predefined sets
            for i, test_set in enumerate(GOKU_TUNING_SETS):
                task_name = f"{i+1}. {test_set['name']}"
                
                # Compile data for this specific test
                task_data = {
                    "character_name": char_name, 
                    "feature_prompt": prompt, 
                    "resolution_anchor": res_val,
                    "steps": test_set["steps"], 
                    "cfg_scale": test_set["cfg_scale"], 
                    "cn_scale": test_set["cn_scale"]
                }
                
                # Update status bar within the batch status context
                batch_status.write(f"Starting {task_name}...")
                p_bar = st.progress(0, text=task_name)
                
                # Execute single task
                result = run_single_synthesis_task(task_data, files, batch_status, p_bar, task_name)
                
                if result:
                    st.session_state.tuning_results.append(result)
                    batch_status.write(f"{task_name} completed.")
                
            batch_status.update(label="Batch Complete! Analyzing results...", state="complete", expanded=False)
            st.session_state.batch_running = False
            st.session_state.metrics = {} # Clear single run metrics
            st.rerun()

    # 7. BATCH COMPARISON VIEW
    if st.session_state.tuning_results:
        st.divider()
        st.title("📊 Batch Results Comparison")
        st.caption(f"Tested {len(st.session_state.tuning_results)} combinations against Source DNA.")

        cols = st.columns(len(st.session_state.tuning_results))
        
        for i, result in enumerate(st.session_state.tuning_results):
            with cols[i]:
                st.markdown(f'<div class="batch-panel">', unsafe_allow_html=True)
                
                st.subheader(result["name"])
                
                # Parameters used
                p = result["params"]
                m = result["metrics"]
                st.markdown(f"""
                    <small>
                    CN: {p['cn_scale']} | CFG: {p['cfg_scale']} | Steps: {p['steps']}<br>
                    Latency: {m['inference_time']}s
                    </small>
                """, unsafe_allow_html=True)
                
                st.image(result["image_data"], use_column_width=True)
                
                # Metrics
                st.metric("SSIM (Structure)", f"{int(m['structural_similarity']*100)}%")
                st.metric("Identity Pres.", f"{int(m['identity_preservation']*100)}%")
                
                # Traceability
                with st.expander("Full Prompts"):
                    st.caption("Positive:")
                    st.markdown(f'<div class="prompt-block">{m["full_prompt"][:100]}...</div>', unsafe_allow_html=True)
                    st.caption("Negative:")
                    st.markdown(f'<div class="negative-prompt-block">{m["negative_prompt"][:50]}...</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()