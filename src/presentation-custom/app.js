/**
 * path: z_realism_ai/src/presentation-custom/app.js
 * description: Real-Time Lab Controller v16.0.
 *              Manages live preview streaming, state resets, and 
 *              hardware locking for the Z-Realism Master Engine.
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const API_BASE_URL = 'http://localhost:8000';

// 1. SYSTEM STATE
const state = {
    taskId: null,
    isProcessing: false,
    selectedFile: null,
    lastParams: null
};

// 2. DOM MAPPING
const ui = {
    charName: document.getElementById('char-name'),
    fileInput: document.getElementById('file-upload'),
    fileLabel: document.getElementById('file-label'),
    btnAnalyze: document.getElementById('btn-analyze'),
    btnGenerate: document.getElementById('btn-generate'),
    
    // Sliders
    resSlider: document.getElementById('input-res'),
    resValue: document.getElementById('val-res'),
    stepsSlider: document.getElementById('input-steps'),
    cfgSlider: document.getElementById('input-cfg'),
    cnSlider: document.getElementById('input-cn'),
    stealthSlider: document.getElementById('input-stealth'),
    
    // Expert Controls
    seedInput: document.getElementById('input-seed'),
    ipSlider: document.getElementById('input-ip'),
    negPrompt: document.getElementById('input-negative'),
    posPrompt: document.getElementById('input-prompt'),

    // Visual Displays
    sourcePreview: document.getElementById('source-preview'),
    resultDisplay: document.getElementById('result-display'),
    essenceTag: document.getElementById('essence-tag'),
    
    // Aura/Telemetry Progress
    progressContainer: document.getElementById('progress-container'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),

    // Analytics & Metrics
    metricsPanel: document.getElementById('metrics-panel'),
    metricSsim: document.getElementById('metric-ssim'),
    metricId: document.getElementById('metric-id'),
    metricTime: document.getElementById('metric-time'),
    debugSection: document.getElementById('debug-section'),
    systemLog: document.getElementById('system-log'),
    btnCopy: document.getElementById('btn-copy-log')
};

/**
 * Initializes the Interactive Laboratory.
 */
function initLaboratory() {
    // A. Reactive Parameter Sync
    const link = (id, valId) => {
        document.getElementById(id).addEventListener('input', (e) => {
            document.getElementById(valId).innerText = e.target.value;
        });
    };
    link('input-res', 'val-res'); link('input-steps', 'val-steps');
    link('input-cfg', 'val-cfg'); link('input-cn', 'val-cn');
    link('input-stealth', 'val-stealth'); link('input-ip', 'val-ip');

    // B. File Upload UX
    ui.fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.fileLabel.innerText = `📂 ${file.name.toUpperCase()}`;
            const reader = new FileReader();
            reader.onload = (ev) => {
                ui.sourcePreview.innerHTML = `<img src="${ev.target.result}" style="animation: fadeIn 0.5s ease;">`;
            };
            reader.readAsDataURL(file);
        }
    });

    // C. Interaction Hub
    ui.btnAnalyze.addEventListener('click', executeDNAAnalysis);
    ui.btnGenerate.addEventListener('click', startFusingSequence);
    ui.btnCopy.addEventListener('click', copyLog);
}

/**
 * EXECUTE ANALYSIS
 * Updates UI with expert lore-aware character presets.
 */
async function executeDNAAnalysis() {
    if (!state.selectedFile || state.isProcessing) return;
    ui.essenceTag.innerText = "DNA_SEQUENCING...";
    
    const body = new FormData();
    body.append('file', state.selectedFile);
    body.append('character_name', ui.charName.value);

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, { method: 'POST', body });
        const data = await response.json();
        if (data.status === 'success') {
            const r = data.recommendations;
            ui.stepsSlider.value = r.steps; ui.cfgSlider.value = r.cfg_scale;
            ui.cnSlider.value = r.cn_scale; ui.posPrompt.value = r.texture_prompt;
            
            // Sync Labels
            document.getElementById('val-steps').innerText = r.steps;
            document.getElementById('val-cfg').innerText = r.cfg_scale;
            document.getElementById('val-cn').innerText = r.cn_scale;

            ui.essenceTag.innerText = `IDENTIFIED: ${data.detected_essence.toUpperCase()}`;
        }
    } catch (err) { ui.essenceTag.innerText = "CORE_LINK_ERROR"; }
}

/**
 * START FUSION
 * Resets the UI and dispatches the task to CUDA.
 */
async function startFusingSequence() {
    if (!state.selectedFile || state.isProcessing) return;

    // 1. Immediate UI Reset & Lock
    state.isProcessing = true;
    lockUI(true);
    resetVisualState();

    // 2. Package Parameters
    const params = {
        character_name: ui.charName.value, feature_prompt: ui.posPrompt.value,
        resolution_anchor: ui.resSlider.value, steps: ui.stepsSlider.value,
        cfg_scale: ui.cfgSlider.value, cn_scale: ui.cnSlider.value,
        stealth_stop: ui.stealthSlider.value, seed: ui.seedInput.value,
        ip_scale: ui.ipSlider.value, negative_prompt: ui.negPrompt.value
    };
    state.lastParams = params;

    const body = new FormData();
    body.append('file', state.selectedFile);
    for (const key in params) body.append(key, params[key]);

    try {
        const response = await fetch(`${API_BASE_URL}/transform`, { method: 'POST', body });
        if (response.status === 429) {
            alert("Hardware Mutex Locked: Another task is active.");
            lockUI(false);
            return;
        }
        const data = await response.json();
        if (data.task_id) {
            state.taskId = data.task_id;
            ui.progressText.innerText = "INITIALIZING TENSORS...";
            pollRealTimeAura();
        }
    } catch (err) {
        console.error(err);
        lockUI(false);
    }
}

/**
 * REAL-TIME AURA POLLING
 * Streams intermediate previews and progress percentage.
 */
function pollRealTimeAura() {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${state.taskId}`);
            const data = await response.json();

            if (data.status === 'PROGRESS') {
                const pct = data.progress.percent;
                ui.progressBar.style.width = `${pct}%`;
                
                // UX: Show specific status based on percentage
                if (pct === 0) ui.progressText.innerText = "ALLOCATING VRAM...";
                else if (pct === 100) ui.progressText.innerText = "DECODING FINAL PNG...";
                else ui.progressText.innerText = `CHARGING AURA: ${pct}%`;

                // LIVE PREVIEW: Render intermediate snapshots from the latent space
                if (data.progress.preview_b64) {
                    ui.resultDisplay.innerHTML = `<img src="data:image/jpeg;base64,${data.progress.preview_b64}" style="filter: blur(2px); opacity: 0.7;">`;
                }
            } else if (data.status === 'SUCCESS') {
                clearInterval(pollInterval);
                renderFinalMaster();
            } else if (data.status === 'FAILURE') {
                clearInterval(pollInterval);
                alert("CUDA Engine Capacity Exceeded.");
                lockUI(false);
            }
        } catch (err) {
            clearInterval(pollInterval);
            lockUI(false);
        }
    }, 1500); // Efficient polling rate
}

/**
 * RENDER MASTER OUTPUT
 */
async function renderFinalMaster() {
    try {
        const response = await fetch(`${API_BASE_URL}/result/${state.taskId}`);
        const result = await response.json();
        
        // Final High-Res Image
        ui.resultDisplay.innerHTML = `<img src="data:image/png;base64,${result.result_image_b64}" style="animation: fadeIn 1s ease;">`;
        
        // Metrics & Log
        const m = result.metrics;
        ui.metricSsim.innerText = `${Math.round(m.structural_similarity * 100)}%`;
        ui.metricId.innerText = `${Math.round(m.identity_preservation * 100)}%`;
        ui.metricTime.innerText = `${m.inference_time}s`;
        
        ui.systemLog.value = JSON.stringify({
            timestamp: new Date().toISOString(),
            config: state.lastParams,
            metrics: m,
            engine: "Z-REALISM_V16_REALTIME"
        }, null, 2);
        
        ui.metricsPanel.classList.remove('hidden');
        ui.debugSection.classList.remove('hidden');
    } catch (err) {
        console.error(err);
    } finally {
        lockUI(false);
    }
}

/**
 * UI STATE ORCHESTRATION
 */
function lockUI(locked) {
    state.isProcessing = locked;
    ui.btnGenerate.disabled = locked;
    ui.btnAnalyze.disabled = locked;
    ui.btnGenerate.style.filter = locked ? "grayscale(1) opacity(0.5)" : "none";
}

function resetVisualState() {
    ui.metricsPanel.classList.add('hidden');
    ui.debugSection.classList.add('hidden');
    ui.progressContainer.classList.remove('hidden');
    ui.progressBar.style.width = '0%';
    ui.resultDisplay.innerHTML = '<p style="color:var(--accent-ui); animation: auraPulse 1s infinite alternate;">OPENING DIMENSIONAL PORTAL...</p>';
}

function copyLog() {
    ui.systemLog.select(); document.execCommand('copy');
    alert("Telemetry Copied!");
}

document.addEventListener('DOMContentLoaded', initLaboratory);