/**
 * path: z_realism_ai/src/presentation-custom/app.js
 * description: Research Controller v19.7 - Final Interaction & Display Sync.
 *
 * ABSTRACT:
 * This script controls the logic for the Z-REALISM laboratory. It manages 
 * subject analysis, neural fusion triggering, and the optimization loop.
 *
 * KEY FIXES (v19.7):
 * 1. Interaction Logic: Uses direct .style.display = 'none' to hide the progress 
 *    overlay, ensuring it doesn't block mouse events on the download button.
 * 2. Layout Sync: Uses .style.display = 'flex' to show the overlay, maintaining 
 *    the centered alignment defined in the CSS.
 * 3. Event Propagation: Download button now uses e.stopPropagation() to prevent 
 *    triggering gallery selection events when saving a result.
 *
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const API_BASE_URL = 'http://localhost:8000';

// =============================================================================
// 1. GLOBAL STATE
// =============================================================================
const state = {
    taskId: null,
    isProcessing: false,
    selectedFile: null,
    previewImgElement: null,
    
    // Core parameters for the synthesis manifold
    recommendedParams: {
        cn_depth: 0.75, 
        cn_pose: 0.40, 
        strength: 0.70,
        negative_prompt: "anime, cartoon, low quality", 
        seed: 42
    },

    // Auto-pilot / Optimization loop state
    optimization: {
        active: false,
        attempts: 0,
        maxAttempts: 5,
        targetThreshold: 0.92,
        bestScore: 0,
        history: [] // Stores candidate objects for the gallery
    }
};

// =============================================================================
// 2. UI ELEMENTS MAPPING
// =============================================================================
const ui = {
    charName: document.getElementById('char-name'),
    fileInput: document.getElementById('file-upload'),
    fileLabel: document.getElementById('file-label'),
    btnAnalyze: document.getElementById('btn-analyze'),
    btnGenerate: document.getElementById('btn-generate'),
    
    resSlider: document.getElementById('input-res'),
    stepsSlider: document.getElementById('input-steps'),
    cfgSlider: document.getElementById('input-cfg'),
    strengthSlider: document.getElementById('input-strength'),
    cnDepthSlider: document.getElementById('input-cn-depth'),
    cnPoseSlider: document.getElementById('input-cn-pose'),
    seedInput: document.getElementById('input-seed'),
    
    promptInput: document.getElementById('input-prompt'),
    chkAutoPilot: document.getElementById('chk-autotune'),
    optStatus: document.getElementById('opt-status'),
    optCount: document.getElementById('opt-count'),
    optScore: document.getElementById('opt-score'),
    essenceTag: document.getElementById('essence-tag'),
    sourcePreview: document.getElementById('source-preview'),
    resultDisplay: document.getElementById('result-display'),
    gallery: document.getElementById('candidate-gallery'),
    
    progressContainer: document.getElementById('progress-container'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),
    
    metricsPanel: document.getElementById('metrics-panel'),
    metricSsim: document.getElementById('metric-ssim'),
    metricId: document.getElementById('metric-id'),
    metricTime: document.getElementById('metric-time'),
    
    accTrigger: document.getElementById('acc-trigger'),
    accContent: document.getElementById('acc-content')
};

// =============================================================================
// 3. INITIALIZATION
// =============================================================================
function initLaboratory() {
    // Accordion Logic
    ui.accTrigger.addEventListener('click', () => {
        ui.accContent.classList.toggle('open');
        ui.accTrigger.querySelector('.arrow').classList.toggle('rotate');
    });

    // Slider Label Sync
    const link = (id, valId) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            document.getElementById(valId).innerText = val % 1 === 0 ? val : val.toFixed(2);
        });
    };
    link('input-res', 'val-res'); 
    link('input-steps', 'val-steps'); 
    link('input-cfg', 'val-cfg');
    link('input-strength', 'val-strength');
    link('input-cn-depth', 'val-cn-depth');
    link('input-cn-pose', 'val-cn-pose');

    // File Upload Preview
    ui.fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.fileLabel.querySelector('.text').innerText = file.name.toUpperCase();
            const reader = new FileReader();
            reader.onload = (ev) => { ui.sourcePreview.innerHTML = `<img src="${ev.target.result}">`; };
            reader.readAsDataURL(file);
        }
    });

    ui.btnAnalyze.addEventListener('click', executeDNAAnalysis);
    ui.btnGenerate.addEventListener('click', initializeFusion);

    updateRecommendedParamsFromUI();
}

/**
 * Reads values from UI sliders and updates the internal manifold state.
 */
function updateRecommendedParamsFromUI() {
    state.recommendedParams = {
        cn_depth: parseFloat(ui.cnDepthSlider.value),
        cn_pose: parseFloat(ui.cnPoseSlider.value),
        strength: parseFloat(ui.strengthSlider.value),
        negative_prompt: state.recommendedParams.negative_prompt,
        seed: parseInt(ui.seedInput.value)
    };
}

// =============================================================================
// 4. CORE WORKFLOWS
// =============================================================================

function initializeFusion() {
    state.optimization.attempts = 0;
    state.optimization.bestScore = 0;
    state.optimization.active = ui.chkAutoPilot.checked;
    state.optimization.history = [];
    ui.gallery.innerHTML = ''; 
    
    // UI Feedback for Auto-Pilot
    if(state.optimization.active) {
        ui.optStatus.style.display = 'block';
        ui.optScore.innerText = "0%";
    } else {
        ui.optStatus.style.display = 'none';
    }
    
    updateRecommendedParamsFromUI();
    startFusingSequence();
}

async function executeDNAAnalysis() {
    if (!state.selectedFile || state.isProcessing) return;
    ui.essenceTag.innerText = "SEQUENCING DNA...";
    const body = new FormData();
    body.append('file', state.selectedFile);
    body.append('character_name', ui.charName.value);
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, { method: 'POST', body });
        const data = await response.json();
        
        if (data.status === 'success') {
            const r = data.recommendations;
            // Update State
            state.recommendedParams = {
                cn_depth: r.cn_scale_depth, 
                cn_pose: r.cn_scale_pose,
                strength: r.strength, 
                negative_prompt: r.negative_prompt,
                seed: parseInt(ui.seedInput.value)
            };
            
            // Sync UI Sliders
            ui.strengthSlider.value = r.strength;
            document.getElementById('val-strength').innerText = r.strength.toFixed(2);
            ui.cnDepthSlider.value = r.cn_scale_depth;
            document.getElementById('val-cn-depth').innerText = r.cn_scale_depth.toFixed(2);
            ui.cnPoseSlider.value = r.cn_scale_pose;
            document.getElementById('val-cn-pose').innerText = r.cn_scale_pose.toFixed(2);
            
            ui.promptInput.value = r.texture_prompt;
            ui.essenceTag.innerText = `STRATEGY: ${data.detected_essence}`;
        }
    } catch (err) { ui.essenceTag.innerText = "OFFLINE: Analysis Failure."; }
}

async function startFusingSequence() {
    if (!state.selectedFile || state.isProcessing) return; 
    toggleControls(true);
    resetWorkspace();
    
    const body = new FormData();
    body.append('file', state.selectedFile);
    body.append('character_name', ui.charName.value);
    body.append('feature_prompt', ui.promptInput.value);
    body.append('resolution_anchor', ui.resSlider.value);
    body.append('steps', ui.stepsSlider.value);
    body.append('cfg_scale', ui.cfgSlider.value);
    body.append('cn_depth', state.recommendedParams.cn_depth);
    body.append('cn_pose', state.recommendedParams.cn_pose);
    body.append('strength', state.recommendedParams.strength);
    body.append('negative_prompt', state.recommendedParams.negative_prompt);
    body.append('seed', state.recommendedParams.seed);

    try {
        const response = await fetch(`${API_BASE_URL}/transform`, { method: 'POST', body });
        if (response.status === 429) { alert("HARDWARE_LOCK: CUDA Engine Busy."); toggleControls(false); return; }
        const data = await response.json();
        state.taskId = data.task_id;
        pollInferenceTelemetry();
    } catch (err) { toggleControls(false); }
}

function pollInferenceTelemetry() {
    const pollInterval = setInterval(async () => {
        if (!state.taskId) return clearInterval(pollInterval);
        try {
            const response = await fetch(`${API_BASE_URL}/status/${state.taskId}`);
            const data = await response.json();
            
            if (data.status === 'PROGRESS') {
                const pct = data.progress.percent;
                ui.progressBar.style.width = `${pct}%`;
                ui.progressText.innerText = `${data.progress.status_text.replace(/_/g, ' ')}: ${pct}%`;
                
                // Real-time latent preview
                if (data.progress.preview_b64) {
                    if (!state.previewImgElement) {
                        ui.resultDisplay.innerHTML = ''; 
                        state.previewImgElement = new Image();
                        state.previewImgElement.style.cssText = "width:100%; height:100%; object-fit:contain; filter:blur(4px);";
                        ui.resultDisplay.appendChild(state.previewImgElement);
                    }
                    state.previewImgElement.src = `data:image/jpeg;base64,${data.progress.preview_b64}`;
                }
            } 
            else if (data.status === 'SUCCESS') {
                clearInterval(pollInterval);
                ui.progressBar.style.width = '100%'; 
                ui.progressText.innerText = "SYNC COMPLETE.";
                setTimeout(() => { renderFinalMasterwork(); }, 600);
            } 
            else if (data.status === 'FAILURE') {
                clearInterval(pollInterval);
                state.optimization.active = false;
                toggleControls(false);
            }
        } catch (err) { clearInterval(pollInterval); toggleControls(false); }
    }, 1000); 
}

async function renderFinalMasterwork() {
    try {
        const response = await fetch(`${API_BASE_URL}/result/${state.taskId}`);
        if (response.status === 202) { setTimeout(renderFinalMasterwork, 500); return; }

        const result = await response.json();
        const candidate = {
            id: state.taskId,
            b64: result.result_image_b64,
            metrics: result.metrics,
            params: { ...state.recommendedParams }
        };

        addCandidateToGallery(candidate);
        displayCandidate(candidate);
        
        // CRITICAL FIX: Direct display style to hide overlay and unlock interaction
        ui.progressContainer.style.display = 'none';

        if (state.optimization.active) {
            handleOptimizationLoop(candidate);
        } else {
            toggleControls(false);
        }
    } catch (err) { state.optimization.active = false; toggleControls(false); }
}

function handleOptimizationLoop(candidate) {
    const m = candidate.metrics;
    const currentScore = (m.structural_similarity + m.identity_preservation) / 2;
    state.optimization.attempts++;
    ui.optCount.innerText = state.optimization.attempts;

    if (currentScore > state.optimization.bestScore) {
        state.optimization.bestScore = currentScore;
        ui.optScore.innerText = `${Math.round(currentScore * 100)}%`;
    }

    if (currentScore >= state.optimization.targetThreshold || state.optimization.attempts >= state.optimization.maxAttempts) {
        ui.essenceTag.innerText = "OPTIMIZATION COMPLETE.";
        state.optimization.active = false;
        toggleControls(false);
        return;
    }

    // Adaptive Sampling Logic
    if (m.structural_similarity < 0.88) state.recommendedParams.cn_depth = Math.min(1.2, state.recommendedParams.cn_depth + 0.03);
    if (m.identity_preservation < 0.90) state.recommendedParams.strength = Math.max(0.50, state.recommendedParams.strength - 0.02);
    else state.recommendedParams.strength = Math.min(0.95, state.recommendedParams.strength + 0.01);

    state.recommendedParams.seed = Math.floor(Math.random() * 1000000);

    setTimeout(() => { state.isProcessing = false; startFusingSequence(); }, 800);
}

// =============================================================================
// 5. VIEWPORT & GALLERY MANAGEMENT
// =============================================================================

function displayCandidate(candidate) {
    ui.resultDisplay.innerHTML = `
        <img src="data:image/png;base64,${candidate.b64}" style="width:100%; height:100%; object-fit:contain;">
        <button id="download-btn" class="btn-secondary" style="position:absolute; bottom:10px; right:10px; z-index:20; margin:0; width:auto; padding:8px 15px;">💾 SAVE DATA</button>
    `;

    document.getElementById('download-btn').onclick = (e) => {
        // Prevent click from bubbling to the image container
        e.stopPropagation();
        const a = document.createElement('a');
        a.href = `data:image/png;base64,${candidate.b64}`;
        a.download = `result_${candidate.id}.png`;
        a.click();
    };

    const m = candidate.metrics;
    ui.metricSsim.innerText = `${(m.structural_similarity * 100).toFixed(0)}%`;
    ui.metricId.innerText = `${(m.identity_preservation * 100).toFixed(0)}%`;
    ui.metricTime.innerText = `${m.inference_time}s`;
    ui.metricsPanel.classList.remove('hidden');
}

function addCandidateToGallery(candidate) {
    const score = Math.round(((candidate.metrics.structural_similarity + candidate.metrics.identity_preservation) / 2) * 100);
    const wrapper = document.createElement('div');
    wrapper.className = 'gallery-item';
    state.optimization.history.push(candidate); 

    wrapper.innerHTML = `
        <img src="data:image/png;base64,${candidate.b64}">
        <div class="gallery-score">${score}%</div>
    `;
    
    wrapper.onclick = () => {
        const target = state.optimization.history.find(c => c.id === candidate.id);
        if (target) {
            displayCandidate(target);
            document.querySelectorAll('.gallery-item').forEach(item => item.classList.remove('active'));
            wrapper.classList.add('active');
        }
    };
    ui.gallery.prepend(wrapper);
}

function toggleControls(locked) {
    state.isProcessing = locked; 
    ui.btnGenerate.disabled = locked;
    ui.btnAnalyze.disabled = locked;
    ui.btnGenerate.querySelector('.btn-text').innerText = locked ? "⚡ SEQUENCING..." : "INITIATE NEURAL FUSION";
    ui.chkAutoPilot.disabled = locked;
    if (!locked) ui.seedInput.value = state.recommendedParams.seed; 
}

function resetWorkspace() {
    // CRITICAL FIX: Show overlay using flex to match CSS layout
    ui.progressContainer.style.display = 'flex';
    ui.progressBar.style.width = '0%';
    ui.progressText.innerText = "INITIALIZING...";
    state.previewImgElement = null;
    document.querySelectorAll('.gallery-item').forEach(item => item.classList.remove('active'));
}

document.addEventListener('DOMContentLoaded', initLaboratory);