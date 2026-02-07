/**
 * path: z_realism_ai/src/presentation-custom/app.js
 * description: Advanced Neural Controller v10.0.
 *              Manages character identity transfer, temporal stealth control, 
 *              and real-time hardware telemetry for the DBS Master Engine.
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const API_BASE_URL = 'http://localhost:8000';

// 1. COMPONENT STATE MANAGEMENT
const state = {
    taskId: null,
    isProcessing: false,
    selectedFile: null,
    lastRequestParams: null
};

// 2. DOM ELEMENT MAPPING (Mission Control)
const ui = {
    // Identity & Triggers
    charName: document.getElementById('char-name'),
    fileInput: document.getElementById('file-upload'),
    fileLabel: document.getElementById('file-label'),
    btnAnalyze: document.getElementById('btn-analyze'),
    btnGenerate: document.getElementById('btn-generate'),
    
    // Neural Core Sliders
    resSlider: document.getElementById('input-res'),
    resValue: document.getElementById('val-res'),
    resWarning: document.getElementById('resolution-warning'),
    gpuStatus: document.getElementById('gpu-warning'),
    stepsSlider: document.getElementById('input-steps'),
    cfgSlider: document.getElementById('input-cfg'),
    cnSlider: document.getElementById('input-cn'),
    stealthSlider: document.getElementById('input-stealth'),
    
    // Expert Engineering Inputs
    seedInput: document.getElementById('input-seed'),
    ipSlider: document.getElementById('input-ip'),
    negPrompt: document.getElementById('input-negative'),
    posPrompt: document.getElementById('input-prompt'),

    // Visual Feedback Containers
    sourcePreview: document.getElementById('source-preview'),
    resultDisplay: document.getElementById('result-display'),
    essenceTag: document.getElementById('essence-tag'),
    
    // Aura Progress Telemetry
    progressContainer: document.getElementById('progress-container'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),

    // Analytics & Recording
    metricsPanel: document.getElementById('metrics-panel'),
    metricSsim: document.getElementById('metric-ssim'),
    metricId: document.getElementById('metric-id'),
    metricTime: document.getElementById('metric-time'),
    debugSection: document.getElementById('debug-section'),
    systemLog: document.getElementById('system-log'),
    btnCopy: document.getElementById('btn-copy-log')
};

/**
 * Attaches all event listeners and initializes the UI state.
 */
function bootstrapController() {
    
    // A. RESOLUTION & HARDWARE MONITORING
    ui.resSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        ui.resValue.innerText = val;
        
        if (val <= 512) {
            ui.resWarning.innerText = "STABLE_ZONE";
            ui.resWarning.style.color = "var(--glow-cyan)";
            ui.gpuStatus.innerText = "HARDWARE_LINK: NOMINAL";
            ui.gpuStatus.style.color = "var(--glow-cyan)";
            ui.gpuStatus.style.animation = "none";
        } else if (val <= 768) {
            ui.resWarning.innerText = "HIGH_FIDELITY_LOAD";
            ui.resWarning.style.color = "var(--glow-orange)";
            ui.gpuStatus.innerText = "HARDWARE_LINK: WARNING";
            ui.gpuStatus.style.color = "var(--glow-orange)";
            ui.gpuStatus.style.animation = "none";
        } else {
            ui.resWarning.innerText = "🚨 SMOKE_ZONE_DETECTION";
            ui.resWarning.style.color = "var(--glow-magenta)";
            ui.gpuStatus.innerText = "HARDWARE_LINK: CRITICAL_STRESS";
            ui.gpuStatus.style.color = "var(--glow-magenta)";
            ui.gpuStatus.style.animation = "auraPulse 0.5s infinite alternate";
        }
    });

    // B. SLIDER SYNCHRONIZATION
    const sync = (id, valId) => {
        document.getElementById(id).addEventListener('input', (e) => {
            document.getElementById(valId).innerText = e.target.value;
        });
    };
    sync('input-steps', 'val-steps');
    sync('input-cfg', 'val-cfg');
    sync('input-cn', 'val-cn');
    sync('input-stealth', 'val-stealth');
    sync('input-ip', 'val-ip');

    // C. FILE UPLOAD UX
    ui.fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.fileLabel.innerText = `📂 ${file.name.toUpperCase()}`;
            const reader = new FileReader();
            reader.onload = (ev) => {
                ui.sourcePreview.innerHTML = `<img src="${ev.target.result}" style="animation: fadeIn 0.8s ease;">`;
            };
            reader.readAsDataURL(file);
        }
    });

    // D. ACTION TRIGGERS
    ui.btnAnalyze.addEventListener('click', runDNAAnalysis);
    ui.btnGenerate.addEventListener('click', startFusionSequence);
    ui.btnCopy.addEventListener('click', copyTelemetryToClipboard);
}

/**
 * DNA ANALYSIS SEQUENCE
 * Communicates with the Heuristic Brain to auto-configure the engine.
 */
async function runDNAAnalysis() {
    if (!state.selectedFile) return alert("System Error: No dimensional input detected.");
    ui.essenceTag.innerText = "DNA_ANALYSIS_IN_PROGRESS...";
    
    const body = new FormData();
    body.append('file', state.selectedFile);
    body.append('character_name', ui.charName.value);

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, { method: 'POST', body });
        const data = await response.json();
        if (data.status === 'success') {
            const recs = data.recommendations;
            // MASTER PARAMETER INJECTION
            ui.stepsSlider.value = recs.steps;
            ui.cfgSlider.value = recs.cfg_scale;
            ui.cnSlider.value = recs.cn_scale;
            ui.posPrompt.value = recs.texture_prompt;
            
            // Sync Labels
            document.getElementById('val-steps').innerText = recs.steps;
            document.getElementById('val-cfg').innerText = recs.cfg_scale;
            document.getElementById('val-cn').innerText = recs.cn_scale;

            ui.essenceTag.innerText = `IDENTIFIED: ${data.detected_essence.toUpperCase()}`;
        }
    } catch (err) { ui.essenceTag.innerText = "CORE_LINK: OFFLINE"; }
}

/**
 * FUSION SEQUENCE
 * Packages all 10 hyper-parameters and starts the CUDA inference.
 */
async function startFusionSequence() {
    if (!state.selectedFile || state.isProcessing) return;
    state.isProcessing = true;
    updateUIForFusion(true);

    const formData = new FormData();
    const requestParams = {
        character_name: ui.charName.value,
        feature_prompt: ui.posPrompt.value,
        resolution_anchor: ui.resSlider.value,
        steps: ui.stepsSlider.value,
        cfg_scale: ui.cfgSlider.value,
        cn_scale: ui.cnSlider.value,
        stealth_stop: ui.stealthSlider.value, // NEW: Stealth Control
        seed: ui.seedInput.value,
        ip_scale: ui.ipSlider.value,
        negative_prompt: ui.negPrompt.value
    };
    state.lastRequestParams = requestParams;

    formData.append('file', state.selectedFile);
    for (const key in requestParams) formData.append(key, requestParams[key]);

    try {
        const response = await fetch(`${API_BASE_URL}/transform`, { method: 'POST', body: formData });
        const data = await response.json();
        if (data.task_id) {
            state.taskId = data.task_id;
            pollAuraStatus();
        }
    } catch (err) {
        console.error("Fusion Error:", err);
        updateUIForFusion(false);
    }
}

/**
 * AURA POLLING
 * Monitors the real-time charging of the de-noising steps.
 */
function pollAuraStatus() {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${state.taskId}`);
            const data = await response.json();
            if (data.status === 'PROGRESS') {
                const pct = data.progress.percent;
                ui.progressBar.style.width = `${pct}%`;
                ui.progressText.innerText = `CHARGING AURA: ${pct}%`;
            } else if (data.status === 'SUCCESS') {
                clearInterval(pollInterval);
                finalizeDimensionalRender();
            } else if (data.status === 'FAILURE') {
                clearInterval(pollInterval);
                alert("CUDA Engine Capacity Reached. Reduce resolution.");
                updateUIForFusion(false);
            }
        } catch (err) {
            clearInterval(pollInterval);
            updateUIForFusion(false);
        }
    }, 1200);
}

/**
 * FINAL RENDERING
 * Displays the high-fidelity output and the telemetry log.
 */
async function finalizeDimensionalRender() {
    try {
        const response = await fetch(`${API_BASE_URL}/result/${state.taskId}`);
        const result = await response.json();
        
        ui.resultDisplay.innerHTML = `<img src="data:image/png;base64,${result.result_image_b64}" style="animation: fadeIn 1s ease;">`;
        
        const m = result.metrics;
        ui.metricSsim.innerText = `${Math.round(m.structural_similarity * 100)}%`;
        ui.metricId.innerText = `${Math.round(m.identity_preservation * 100)}%`;
        ui.metricTime.innerText = `${m.inference_time}s`;
        
        // POPULATE FLIGHT RECORDER
        const telemetryData = {
            timestamp: new Date().toISOString(),
            config_profile: state.lastRequestParams,
            hardware_metrics: m,
            engine_build: "Z-REALISM_V10_STEALTH"
        };
        ui.systemLog.value = JSON.stringify(telemetryData, null, 2);
        
        ui.metricsPanel.classList.remove('hidden');
        ui.debugSection.classList.remove('hidden');

    } catch (err) { console.error("Telemetry Error:", err); } 
    finally { updateUIForFusion(false); }
}

/**
 * VISUAL STATE MANAGER
 */
function updateUIForFusion(isActive) {
    ui.btnGenerate.disabled = isActive;
    if (isActive) {
        ui.progressContainer.classList.remove('hidden');
        ui.metricsPanel.classList.add('hidden');
        ui.debugSection.classList.add('hidden');
        ui.resultDisplay.innerHTML = '<p style="color: var(--glow-cyan); font-family: Orbitron; font-size: 0.6rem; animation: auraPulse 1s infinite alternate;">ACCESSING_LATENT_TENSORS...</p>';
        ui.progressBar.style.width = '0%';
    } else {
        ui.progressContainer.classList.add('hidden');
        state.isProcessing = false;
    }
}

/**
 * TELEMETRY EXPORT
 */
function copyTelemetryToClipboard() {
    ui.systemLog.select();
    document.execCommand('copy');
    alert("Dimensional Telemetry Copied to Clipboard!");
}

// EXECUTE BOOTSTRAP
document.addEventListener('DOMContentLoaded', bootstrapController);