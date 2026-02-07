/**
 * path: z_realism_ai/src/presentation-custom/app.js
 * description: Research Laboratory Controller v16.2.1.
 *              FEATURING: Granular Lifecycle Decoding (Cold Start vs Active Synthesis).
 *              FEATURING: High-performance DOM rendering for real-time latent previews.
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const API_BASE_URL = 'http://localhost:8000';

// 1. RESEARCHER STATE
const state = {
    taskId: null,
    isProcessing: false,
    selectedFile: null,
    lastParams: null,
    previewImgElement: null // Persistent reference to avoid DOM thrashing
};

// 2. INTERFACE MAPPING
const ui = {
    charName: document.getElementById('char-name'),
    fileInput: document.getElementById('file-upload'),
    fileLabel: document.getElementById('file-label'),
    btnAnalyze: document.getElementById('btn-analyze'),
    btnGenerate: document.getElementById('btn-generate'),
    
    // Control Sliders
    resSlider: document.getElementById('input-res'),
    stepsSlider: document.getElementById('input-steps'),
    cfgSlider: document.getElementById('input-cfg'),
    cnSlider: document.getElementById('input-cn'),
    stealthSlider: document.getElementById('input-stealth'),
    ipSlider: document.getElementById('input-ip'),
    
    // Visual Domain Containers
    sourcePreview: document.getElementById('source-preview'),
    resultDisplay: document.getElementById('result-display'),
    essenceTag: document.getElementById('essence-tag'),
    
    // Telemetry Progress Components
    progressContainer: document.getElementById('progress-container'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),

    // Scientific Metrics & Logs
    metricsPanel: document.getElementById('metrics-panel'),
    metricSsim: document.getElementById('metric-ssim'),
    metricId: document.getElementById('metric-id'),
    metricTime: document.getElementById('metric-time'),
    debugSection: document.getElementById('debug-section'),
    systemLog: document.getElementById('system-log'),
    btnCopy: document.getElementById('btn-copy-log')
};

/**
 * Initializes the Laboratory Event Listeners.
 */
function initLaboratory() {
    // Dynamic Parameter Label Synchronization
    const linkValue = (id, valId) => {
        const input = document.getElementById(id);
        if (input) input.addEventListener('input', (e) => {
            document.getElementById(valId).innerText = e.target.value;
        });
    };
    linkValue('input-res', 'val-res'); linkValue('input-steps', 'val-steps');
    linkValue('input-cfg', 'val-cfg'); linkValue('input-cn', 'val-cn');
    linkValue('input-stealth', 'val-stealth'); linkValue('input-ip', 'val-ip');

    // Source Artwork Ingestion
    ui.fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.fileLabel.innerText = `📂 INPUT: ${file.name.toUpperCase()}`;
            const reader = new FileReader();
            reader.onload = (ev) => {
                ui.sourcePreview.innerHTML = `<img src="${ev.target.result}" style="animation: fadeIn 0.4s ease-out;">`;
            };
            reader.readAsDataURL(file);
        }
    });

    // Interaction Dispatchers
    ui.btnAnalyze.addEventListener('click', executeDNAAnalysis);
    ui.btnGenerate.addEventListener('click', startFusingSequence);
    ui.btnCopy.addEventListener('click', () => {
        ui.systemLog.select();
        document.execCommand('copy');
        alert("System Telemetry Copied.");
    });
}

/**
 * DNA ANALYSIS
 * Invokes the Heuristic Brain to determine optimal synthesis parameters.
 */
async function executeDNAAnalysis() {
    if (!state.selectedFile || state.isProcessing) return;
    ui.essenceTag.innerText = "SEQUENCING_VISUAL_DNA...";
    
    const body = new FormData();
    body.append('file', state.selectedFile);
    body.append('character_name', ui.charName.value);

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, { method: 'POST', body });
        const data = await response.json();
        if (data.status === 'success') {
            const r = data.recommendations;
            // Update Interface Inputs
            ui.stepsSlider.value = r.steps; document.getElementById('val-steps').innerText = r.steps;
            ui.cfgSlider.value = r.cfg_scale; document.getElementById('val-cfg').innerText = r.cfg_scale;
            ui.cnSlider.value = r.cn_scale; document.getElementById('val-cn').innerText = r.cn_scale;
            document.getElementById('input-prompt').value = r.texture_prompt;

            ui.essenceTag.innerText = `STRATEGY_FOUND: ${data.detected_essence.toUpperCase()}`;
        }
    } catch (err) { 
        ui.essenceTag.innerText = "HEURISTIC_OFFLINE"; 
    }
}

/**
 * FUSION SEQUENCE
 * Orchestrates the dispatch of parameters to the CUDA Inference Worker.
 */
async function startFusingSequence() {
    if (!state.selectedFile || state.isProcessing) return;

    state.isProcessing = true;
    toggleControls(true);
    resetWorkspace();

    const body = new FormData();
    body.append('file', state.selectedFile);
    body.append('character_name', ui.charName.value);
    body.append('feature_prompt', document.getElementById('input-prompt').value);
    body.append('resolution_anchor', ui.resSlider.value);
    body.append('steps', ui.stepsSlider.value);
    body.append('cfg_scale', ui.cfgSlider.value);
    body.append('cn_scale', ui.cnSlider.value);
    body.append('stealth_stop', ui.stealthSlider.value);
    body.append('seed', document.getElementById('input-seed').value);
    body.append('ip_scale', ui.ipSlider.value);
    body.append('negative_prompt', document.getElementById('input-negative').value);

    try {
        const response = await fetch(`${API_BASE_URL}/transform`, { method: 'POST', body });
        
        if (response.status === 429) {
            alert("HARDWARE_MUTEX: GPU is currently occupied by another researcher.");
            toggleControls(false);
            return;
        }

        const data = await response.json();
        state.taskId = data.task_id;
        pollInferenceTelemetry();
    } catch (err) {
        console.error("Fusion Protocol Interrupted:", err);
        toggleControls(false);
    }
}

/**
 * OPTIMIZED TELEMETRY POLLING
 * Decodes granular worker states and manages high-speed latent preview rendering.
 */
function pollInferenceTelemetry() {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${state.taskId}`);
            const data = await response.json();

            if (data.status === 'PROGRESS') {
                const pct = data.progress.percent;
                const statusStr = data.progress.status_text;

                // Sync UI Progress Bar
                requestAnimationFrame(() => {
                    ui.progressBar.style.width = `${pct}%`;
                    
                    // Decode Internal States into User-Friendly Research Messages
                    switch(statusStr) {
                        case 'LOADING_MODELS':
                            ui.progressText.innerText = "COLD_START: LOADING NEURAL WEIGHTS TO VRAM (40s)...";
                            ui.progressText.style.color = "var(--glow-orange)";
                            break;
                        case 'ALLOCATING_VRAM':
                            ui.progressText.innerText = "PRE-HEATING CUDA CORES & TENSORS...";
                            ui.progressText.style.color = "var(--glow-cyan)";
                            break;
                        case 'SYNTHESIZING':
                            ui.progressText.innerText = `NEURAL SYNTHESIS IN PROGRESS: ${pct}%`;
                            ui.progressText.style.color = "var(--glow-cyan)";
                            break;
                        default:
                            ui.progressText.innerText = "COMMUNICATING WITH DISTRIBUTED WORKER...";
                    }
                });

                // Render Intermediate Latent Snapshots
                if (data.progress.preview_b64) {
                    if (!state.previewImgElement) {
                        ui.resultDisplay.innerHTML = ''; 
                        state.previewImgElement = new Image();
                        state.previewImgElement.style.width = "100%";
                        state.previewImgElement.style.filter = "blur(2px) contrast(1.1)"; // Approximation is noisy
                        ui.resultDisplay.appendChild(state.previewImgElement);
                    }
                    state.previewImgElement.src = `data:image/jpeg;base64,${data.progress.preview_b64}`;
                }
            } 
            else if (data.status === 'SUCCESS') {
                clearInterval(pollInterval);
                renderFinalMasterwork();
            } 
            else if (data.status === 'FAILURE') {
                clearInterval(pollInterval);
                alert("CRITICAL_ENGINE_FAILURE: Check CUDA allocation logs.");
                toggleControls(false);
            }
        } catch (err) {
            clearInterval(pollInterval);
            toggleControls(false);
        }
    }, 1000); // Efficient polling frequency for 6GB VRAM hardware
}

/**
 * FINAL RENDERING
 * Retrieves the high-fidelity synthesis and computes scientific metrics.
 */
async function renderFinalMasterwork() {
    try {
        const response = await fetch(`${API_BASE_URL}/result/${state.taskId}`);
        const result = await response.json();
        
        // Final Output Presentation
        const finalImg = new Image();
        finalImg.src = `data:image/png;base64,${result.result_image_b64}`;
        finalImg.onload = () => {
            ui.resultDisplay.innerHTML = '';
            ui.resultDisplay.appendChild(finalImg);
            finalImg.style.animation = "fadeIn 1s cubic-bezier(0.23, 1, 0.32, 1)";
            state.previewImgElement = null; 
        };

        // Scientific Analytics Integration
        const m = result.metrics;
        ui.metricSsim.innerText = `${(m.structural_similarity * 100).toFixed(1)}%`;
        ui.metricId.innerText = `${(m.identity_preservation * 100).toFixed(1)}%`;
        ui.metricTime.innerText = `${m.inference_time}s`;
        
        ui.systemLog.value = JSON.stringify(result, null, 2);
        
        ui.metricsPanel.classList.remove('hidden');
        ui.debugSection.classList.remove('hidden');
    } catch (err) {
        console.error("Masterwork Retrieval Error:", err);
    } finally {
        toggleControls(false);
    }
}

/**
 * UI ORCHESTRATION UTILITIES
 */
function toggleControls(locked) {
    ui.btnGenerate.disabled = locked;
    ui.btnAnalyze.disabled = locked;
    ui.btnGenerate.style.filter = locked ? "grayscale(1) opacity(0.5)" : "none";
    ui.btnGenerate.innerText = locked ? "⚡ ENGINE_ENGAGED" : "🚀 INITIATE TRANSFORMATION";
}

function resetWorkspace() {
    ui.metricsPanel.classList.add('hidden');
    ui.debugSection.classList.add('hidden');
    ui.progressContainer.classList.remove('hidden');
    ui.progressBar.style.width = '0%';
    ui.resultDisplay.innerHTML = '<p class="aura-pulse" style="color:var(--glow-cyan); font-size: 0.7rem;">ESTABLISHING NEURAL LINK...</p>';
    state.previewImgElement = null;
}

document.addEventListener('DOMContentLoaded', initLaboratory);