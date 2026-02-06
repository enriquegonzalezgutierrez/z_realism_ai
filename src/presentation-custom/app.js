/**
 * path: z_realism_ai/src/presentation-custom/app.js
 * description: Ultimate Neural Orchestrator v9.2 - Full Feature Set.
 *              This script manages the entire user interaction lifecycle:
 *              - Automated Heuristic Analysis
 *              - Expert Parameter Injection
 *              - Asynchronous Task Polling with Visual Feedback
 *              - Hardware Stress Monitoring
 *              - Flight Data Recording for Telemetry
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

// --- GLOBAL CONFIGURATION ---
const API_BASE_URL = 'http://localhost:8000';

// --- CENTRAL UI STATE MANAGEMENT ---
const state = {
    taskId: null,
    isProcessing: false,
    selectedFile: null,
    lastRequestData: null // For the Flight Recorder
};

// --- DOM ELEMENT MAPPING (SINGLE SOURCE OF TRUTH) ---
const ui = {
    // Identity & Triggers
    charName: document.getElementById('char-name'),
    fileInput: document.getElementById('file-upload'),
    fileLabel: document.getElementById('file-label'),
    btnAnalyze: document.getElementById('btn-analyze'),
    btnGenerate: document.getElementById('btn-generate'),
    
    // Neural Tuning Sliders
    resSlider: document.getElementById('input-res'),
    resValue: document.getElementById('val-res'),
    resWarning: document.getElementById('resolution-warning'),
    gpuStatus: document.getElementById('gpu-warning'),
    stepsSlider: document.getElementById('input-steps'),
    cfgSlider: document.getElementById('input-cfg'),
    cnSlider: document.getElementById('input-cn'),
    
    // Expert Engineering Inputs
    seedInput: document.getElementById('input-seed'),
    ipSlider: document.getElementById('input-ip'),
    negPrompt: document.getElementById('input-negative'),
    posPrompt: document.getElementById('input-prompt'),

    // Visual Displays
    sourcePreview: document.getElementById('source-preview'),
    resultDisplay: document.getElementById('result-display'),
    essenceTag: document.getElementById('essence-tag'),
    
    // Progress Telemetry
    progressContainer: document.getElementById('progress-container'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),

    // Analytical Metrics & Debugging
    metricsPanel: document.getElementById('metrics-panel'),
    metricSsim: document.getElementById('metric-ssim'),
    metricId: document.getElementById('metric-id'),
    metricTime: document.getElementById('metric-time'),
    debugSection: document.getElementById('debug-section'),
    systemLog: document.getElementById('system-log'),
    btnCopy: document.getElementById('btn-copy-log')
};

/**
 * Main function to bootstrap all UI event listeners.
 */
function initializeEngineUI() {
    
    // 1. HARDWARE STRESS MONITOR (Resolution Slider)
    ui.resSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        ui.resValue.innerText = val;
        
        if (val <= 512) {
            ui.resWarning.innerText = "STABLE ZONE (Optimized for 6GB)";
            ui.resWarning.style.color = "var(--accent-ui)";
            ui.gpuStatus.innerText = "SYSTEM STATUS: READY";
            ui.gpuStatus.style.color = "var(--accent-ui)";
            ui.gpuStatus.style.animation = "none";
        } else if (val <= 768) {
            ui.resWarning.innerText = "HIGH FIDELITY (Moderate VRAM Load)";
            ui.resWarning.style.color = "var(--accent-goku)";
            ui.gpuStatus.innerText = "SYSTEM STATUS: HEAVY LOAD";
            ui.gpuStatus.style.color = "var(--accent-goku)";
            ui.gpuStatus.style.animation = "none";
        } else {
            ui.resWarning.innerText = "🚨 SMOKE ZONE (Extreme VRAM Stress)";
            ui.resWarning.style.color = "#ff0000";
            ui.gpuStatus.innerText = "SYSTEM STATUS: OVERCLOCKING";
            ui.gpuStatus.style.color = "#ff0000";
            // Animation for dramatic effect (defined in CSS)
            ui.gpuStatus.style.animation = "pulse 0.5s infinite alternate";
        }
    });

    // 2. Link other sliders to their display labels
    const linkSlider = (id, valId) => {
        document.getElementById(id).addEventListener('input', (e) => {
            document.getElementById(valId).innerText = e.target.value;
        });
    };
    linkSlider('input-steps', 'val-steps');
    linkSlider('input-cfg', 'val-cfg');
    linkSlider('input-cn', 'val-cn');
    linkSlider('input-ip', 'val-ip');

    // 3. Custom File Upload Logic
    ui.fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.fileLabel.innerText = `📂 ${file.name.toUpperCase()}`;
            ui.fileLabel.style.borderColor = "var(--accent-goku)";
            const reader = new FileReader();
            reader.onload = (ev) => {
                ui.sourcePreview.innerHTML = `<img src="${ev.target.result}" style="animation: fadeIn 0.5s ease;">`;
            };
            reader.readAsDataURL(file);
        }
    });

    // 4. Attach Core Action Listeners
    ui.btnAnalyze.addEventListener('click', runLoreAnalysis);
    ui.btnGenerate.addEventListener('click', initiateFusionSequence);
    ui.btnCopy.addEventListener('click', copyLogToClipboard);
}

/**
 * Calls the /analyze endpoint and injects recommended parameters into the UI.
 */
async function runLoreAnalysis() {
    if (!state.selectedFile) return alert("Please upload a source image first.");
    ui.essenceTag.innerText = "ANALYZING VISUAL DNA...";
    ui.essenceTag.style.color = "var(--accent-ui)";
    
    const formData = new FormData();
    formData.append('file', state.selectedFile);
    formData.append('character_name', ui.charName.value);

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, { method: 'POST', body: formData });
        const data = await response.json();
        if (data.status === 'success') {
            const recs = data.recommendations;
            // Inject parameters into sliders and text areas
            ui.stepsSlider.value = recs.steps;
            ui.cfgSlider.value = recs.cfg_scale;
            ui.cnSlider.value = recs.cn_scale;
            ui.posPrompt.value = recs.texture_prompt;
            
            // Manually update the visual labels
            document.getElementById('val-steps').innerText = recs.steps;
            document.getElementById('val-cfg').innerText = recs.cfg_scale;
            document.getElementById('val-cn').innerText = recs.cn_scale;
            
            ui.essenceTag.innerText = `DETECTED: ${data.detected_essence}`;
            ui.essenceTag.style.color = "var(--accent-goku)";
        }
    } catch (err) { ui.essenceTag.innerText = "API LINK ERROR"; }
}

/**
 * Packages all parameters and sends the transformation request to the API.
 */
async function initiateFusionSequence() {
    if (!state.selectedFile || state.isProcessing) return;
    state.isProcessing = true;
    updateUIState(true);

    const formData = new FormData();
    const requestData = {
        character_name: ui.charName.value,
        feature_prompt: ui.posPrompt.value,
        resolution_anchor: ui.resSlider.value,
        steps: ui.stepsSlider.value,
        cfg_scale: ui.cfgSlider.value,
        cn_scale: ui.cnSlider.value,
        seed: ui.seedInput.value,
        ip_scale: ui.ipSlider.value,
        negative_prompt: ui.negPrompt.value
    };
    state.lastRequestData = requestData;

    formData.append('file', state.selectedFile);
    for (const key in requestData) {
        formData.append(key, requestData[key]);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/transform`, { method: 'POST', body: formData });
        const data = await response.json();
        if (data.task_id) {
            state.taskId = data.task_id;
            pollTelemetry();
        }
    } catch (err) {
        console.error(err);
        updateUIState(false);
    }
}

/**
 * Periodically checks the task status and updates the progress bar.
 */
function pollTelemetry() {
    const poll = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${state.taskId}`);
            const data = await response.json();
            if (data.status === 'PROGRESS') {
                const pct = data.progress.percent;
                ui.progressBar.style.width = `${pct}%`;
                ui.progressText.innerText = `CHARGING AURA: ${pct}%`;
            } else if (data.status === 'SUCCESS') {
                clearInterval(poll);
                renderOutput();
            } else if (data.status === 'FAILURE') {
                clearInterval(poll);
                alert("Transformation Failed. Check worker logs for details.");
                updateUIState(false);
            }
        } catch (err) {
            clearInterval(poll);
            updateUIState(false);
        }
    }, 1200);
}

/**
 * Fetches the final result, renders the image and metrics, and populates the Flight Recorder.
 */
async function renderOutput() {
    try {
        const response = await fetch(`${API_BASE_URL}/result/${state.taskId}`);
        const pkg = await response.json();
        
        ui.resultDisplay.innerHTML = `<img src="data:image/png;base64,${pkg.result_image_b64}" style="animation: auraPulse 2s infinite alternate;">`;
        
        const m = pkg.metrics;
        ui.metricSsim.innerText = `${Math.round(m.structural_similarity * 100)}%`;
        ui.metricId.innerText = `${Math.round(m.identity_preservation * 100)}%`;
        ui.metricTime.innerText = `${m.inference_time}s`;
        
        // Populate Flight Data Recorder
        const logData = {
            timestamp: new Date().toISOString(),
            configuration: state.lastRequestData,
            performance: m
        };
        ui.systemLog.value = JSON.stringify(logData, null, 2);
        ui.debugSection.classList.remove('hidden');
        ui.metricsPanel.classList.remove('hidden');

    } catch (err) { console.error(err); } 
    finally { updateUIState(false); }
}

/**
 * Central function to manage the UI's visual state during processing.
 */
function updateUIState(isWorking) {
    ui.btnGenerate.disabled = isWorking;
    ui.btnGenerate.innerText = isWorking ? "🧬 FUSING DIMENSIONS..." : "🚀 INITIATE TRANSFORMATION";
    
    if (isWorking) {
        ui.progressContainer.classList.remove('hidden');
        ui.metricsPanel.classList.add('hidden');
        ui.debugSection.classList.add('hidden');
        ui.resultDisplay.innerHTML = '<p style="color: var(--accent-ui); animation: auraPulse 1s infinite alternate;">ACCESSING LATENT SPACE...</p>';
        ui.progressBar.style.width = '0%';
    } else {
        ui.progressContainer.classList.add('hidden');
        state.isProcessing = false;
        ui.gpuStatus.style.animation = "none";
    }
}

/**
 * Copies the Flight Recorder content to the user's clipboard.
 */
function copyLogToClipboard() {
    if (!ui.systemLog.value) return;
    ui.systemLog.select();
    document.execCommand('copy');
    alert("Telemetry Log Copied to Clipboard!");
}

// Start the Console when the DOM is fully loaded.
document.addEventListener('DOMContentLoaded', initializeEngineUI);