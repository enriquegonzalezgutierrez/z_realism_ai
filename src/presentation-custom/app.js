/**
 * path: z_realism_ai/src/presentation-custom/app.js
 * description: Research Controller v20.0 - Multi-Modal Temporal Integration.
 *
 * ABSTRACT:
 * This script orchestrates the Z-REALISM laboratory. It supports two primary 
 * neural pipelines: 
 * 1. Static Fusion (Img2Img): Transforming subjects into photorealistic stills.
 * 2. Temporal Fusion (Animate): Transforming generated stills into fluid clips.
 *
 * KEY FEATURES (v20.0):
 * 1. Temporal Orchestration: New logic to communicate with the '/animate' API.
 * 2. Multi-Format Display: The Result Monitor now dynamically switches between 
 *    PNG rendering and MP4 playback.
 * 3. Lore-Sync: Automatically pairs the animation with the character genome (JSON).
 * 4. Hardware Awareness: Manages the progress overlay and interaction locks 
 *    during long-latency video synthesis on the GTX 1060.
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
    currentTaskType: 'IMAGE', // 'IMAGE' or 'VIDEO'
    
    recommendedParams: {
        cn_depth: 0.75, 
        cn_pose: 0.40, 
        strength: 0.70,
        negative_prompt: "anime, cartoon, low quality", 
        seed: 42
    },

    optimization: {
        active: false,
        attempts: 0,
        maxAttempts: 5,
        targetThreshold: 0.92,
        bestScore: 0,
        history: [] 
    }
};

// =============================================================================
// 2. UI ELEMENTS MAPPING
// =============================================================================
const ui = {
    // Primary Controls
    charName: document.getElementById('char-name'),
    fileInput: document.getElementById('file-upload'),
    fileLabel: document.getElementById('file-label'),
    btnAnalyze: document.getElementById('btn-analyze'),
    btnGenerate: document.getElementById('btn-generate'),
    btnAnimate: document.getElementById('btn-animate'), // New trigger for video
    
    // Image Manifold Sliders
    resSlider: document.getElementById('input-res'),
    stepsSlider: document.getElementById('input-steps'),
    cfgSlider: document.getElementById('input-cfg'),
    strengthSlider: document.getElementById('input-strength'),
    cnDepthSlider: document.getElementById('input-cn-depth'),
    cnPoseSlider: document.getElementById('input-cn-pose'),
    seedInput: document.getElementById('input-seed'),
    
    // Temporal Manifold Sliders (Assumed IDs for the new UI section)
    motionPrompt: document.getElementById('input-motion-prompt'),
    durationSlider: document.getElementById('input-duration'),
    fpsSlider: document.getElementById('input-fps'),
    motionBucketSlider: document.getElementById('input-motion-bucket'),
    videoDenoisingSlider: document.getElementById('input-video-denoising'),
    
    // Generic UI
    promptInput: document.getElementById('input-prompt'),
    chkAutoPilot: document.getElementById('chk-autotune'),
    optStatus: document.getElementById('opt-status'),
    optCount: document.getElementById('opt-count'),
    optScore: document.getElementById('opt-score'),
    essenceTag: document.getElementById('essence-tag'),
    sourcePreview: document.getElementById('source-preview'),
    resultDisplay: document.getElementById('result-display'),
    gallery: document.getElementById('candidate-gallery'),
    
    // Telemetry UI
    progressContainer: document.getElementById('progress-container'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),
    
    // Metrics
    metricsPanel: document.getElementById('metrics-panel'),
    metricSsim: document.getElementById('metric-ssim'),
    metricId: document.getElementById('metric-id'),
    metricTime: document.getElementById('metric-time'),
    
    // Layout
    accTrigger: document.getElementById('acc-trigger'),
    accContent: document.getElementById('acc-content')
};

// =============================================================================
// 3. INITIALIZATION
// =============================================================================
function initLaboratory() {
    // Accordion Logic
    if (ui.accTrigger) {
        ui.accTrigger.addEventListener('click', () => {
            ui.accContent.classList.toggle('open');
            ui.accTrigger.querySelector('.arrow').classList.toggle('rotate');
        });
    }

    // Slider Value Linkage
    const link = (id, valId) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            const display = document.getElementById(valId);
            if (display) display.innerText = val % 1 === 0 ? val : val.toFixed(2);
        });
    };
    link('input-res', 'val-res'); 
    link('input-steps', 'val-steps'); 
    link('input-cfg', 'val-cfg');
    link('input-strength', 'val-strength');
    link('input-cn-depth', 'val-cn-depth');
    link('input-cn-pose', 'val-cn-pose');
    link('input-duration', 'val-duration');
    link('input-fps', 'val-fps');
    link('input-motion-bucket', 'val-motion-bucket');
    link('input-video-denoising', 'val-video-denoising');

    // Source File Handling
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

    // Primary Actions
    ui.btnAnalyze.addEventListener('click', executeDNAAnalysis);
    ui.btnGenerate.addEventListener('click', initializeFusion);
    
    // Video Action
    if (ui.btnAnimate) {
        ui.btnAnimate.addEventListener('click', initializeTemporalFusion);
    }

    updateRecommendedParamsFromUI();
}

function updateRecommendedParamsFromUI() {
    state.recommendedParams = {
        cn_depth: parseFloat(ui.cnDepthSlider?.value || 0.60),
        cn_pose: parseFloat(ui.cnPoseSlider?.value || 0.75),
        strength: parseFloat(ui.strengthSlider?.value || 0.65),
        negative_prompt: state.recommendedParams.negative_prompt,
        seed: parseInt(ui.seedInput?.value || 42)
    };
}

// =============================================================================
// 4. WORKFLOWS: STATIC & TEMPORAL
// =============================================================================

/**
 * Workflow A: Static Image Fusion (Img2Img)
 */
function initializeFusion() {
    state.currentTaskType = 'IMAGE';
    state.optimization.attempts = 0;
    state.optimization.history = [];
    ui.gallery.innerHTML = ''; 
    updateRecommendedParamsFromUI();
    startFusingSequence();
}

/**
 * Workflow B: Temporal Animation (Img2Video)
 */
function initializeTemporalFusion() {
    if (!state.selectedFile) { alert("ERROR: Please upload a generated image first."); return; }
    state.currentTaskType = 'VIDEO';
    toggleControls(true);
    resetWorkspace();
    startAnimateSequence();
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
            state.recommendedParams = {
                cn_depth: r.cn_scale_depth, 
                cn_pose: r.cn_scale_pose,
                strength: r.strength, 
                negative_prompt: r.negative_prompt,
                seed: parseInt(ui.seedInput.value)
            };
            ui.strengthSlider.value = r.strength;
            ui.cnDepthSlider.value = r.cn_scale_depth;
            ui.cnPoseSlider.value = r.cn_scale_pose;
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
        const data = await response.json();
        state.taskId = data.task_id;
        pollInferenceTelemetry();
    } catch (err) { toggleControls(false); }
}

async function startAnimateSequence() {
    const body = new FormData();
    body.append('file', state.selectedFile);
    body.append('character_name', ui.charName.value);
    body.append('motion_prompt', ui.motionPrompt?.value || "subtle realistic movement");
    body.append('duration_frames', ui.durationSlider?.value || 24);
    body.append('fps', ui.fpsSlider?.value || 8);
    body.append('motion_bucket', ui.motionBucketSlider?.value || 127);
    body.append('denoising_strength', ui.videoDenoisingSlider?.value || 0.20);
    body.append('seed', ui.seedInput?.value || 42);

    try {
        const response = await fetch(`${API_BASE_URL}/animate`, { method: 'POST', body });
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
                
                if (data.progress.preview_b64 && state.currentTaskType === 'IMAGE') {
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
        
        if (result.video_b64) {
            displayVideoCandidate(result);
        } else {
            const candidate = {
                id: state.taskId,
                b64: result.result_image_b64,
                metrics: result.metrics,
                params: { ...state.recommendedParams }
            };
            addCandidateToGallery(candidate);
            displayCandidate(candidate);
        }
        
        ui.progressContainer.style.display = 'none';
        toggleControls(false);
    } catch (err) { toggleControls(false); }
}

// =============================================================================
// 5. VIEWPORT & DISPLAY MANAGEMENT
// =============================================================================

function displayCandidate(candidate) {
    ui.resultDisplay.innerHTML = `
        <img src="data:image/png;base64,${candidate.b64}" style="width:100%; height:100%; object-fit:contain;">
        <button id="download-btn" class="btn-secondary" style="position:absolute; bottom:10px; right:10px; z-index:20; margin:0; width:auto; padding:8px 15px;">💾 SAVE DATA</button>
    `;
    
    document.getElementById('download-btn').onclick = (e) => {
        e.stopPropagation();
        const a = document.createElement('a');
        a.href = `data:image/png;base64,${candidate.b64}`;
        a.download = `result_${candidate.id}.png`;
        a.click();
    };

    const m = candidate.metrics;
    ui.metricSsim.innerText = m.structural_similarity ? `${(m.structural_similarity * 100).toFixed(0)}%` : '--';
    ui.metricId.innerText = m.identity_preservation ? `${(m.identity_preservation * 100).toFixed(0)}%` : '--';
    ui.metricTime.innerText = `${m.inference_time}s`;
    ui.metricsPanel.classList.remove('hidden');
}

function displayVideoCandidate(result) {
    ui.resultDisplay.innerHTML = `
        <video autoplay loop muted controls style="width:100%; height:100%; object-fit:contain; border-radius:12px;">
            <source src="data:video/mp4;base64,${result.video_b64}" type="video/mp4">
        </video>
        <button id="download-vid-btn" class="btn-secondary" style="position:absolute; bottom:10px; right:10px; z-index:20; margin:0; width:auto; padding:8px 15px;">🎬 SAVE VIDEO</button>
    `;

    document.getElementById('download-vid-btn').onclick = (e) => {
        e.stopPropagation();
        const a = document.createElement('a');
        a.href = `data:video/mp4;base64,${result.video_b64}`;
        a.download = `animation_${state.taskId}.mp4`;
        a.click();
    };
    
    const m = result.metrics;
    ui.metricTime.innerText = `${m.inference_time}s`;
    ui.metricSsim.innerText = "VIDEO";
    ui.metricId.innerText = `${result.total_frames}f`;
}

function addCandidateToGallery(candidate) {
    state.optimization.history.push(candidate); 
    const score = Math.round(((candidate.metrics.structural_similarity + candidate.metrics.identity_preservation) / 2) * 100);
    const wrapper = document.createElement('div');
    wrapper.className = 'gallery-item';
    wrapper.innerHTML = `<img src="data:image/png;base64,${candidate.b64}"><div class="gallery-score">${score}%</div>`;
    wrapper.onclick = () => {
        displayCandidate(candidate);
        document.querySelectorAll('.gallery-item').forEach(item => item.classList.remove('active'));
        wrapper.classList.add('active');
    };
    ui.gallery.prepend(wrapper);
}

function toggleControls(locked) {
    state.isProcessing = locked; 
    ui.btnGenerate.disabled = locked;
    ui.btnAnalyze.disabled = locked;
    if(ui.btnAnimate) ui.btnAnimate.disabled = locked;
    
    const fusionText = state.currentTaskType === 'IMAGE' ? "NEURAL FUSION" : "TEMPORAL FUSION";
    ui.btnGenerate.querySelector('.btn-text').innerText = locked ? "⚡ SEQUENCING..." : `INITIATE ${fusionText}`;
}

function resetWorkspace() {
    ui.progressContainer.style.display = 'flex';
    ui.progressBar.style.width = '0%';
    ui.progressText.innerText = "INITIALIZING...";
    state.previewImgElement = null;
    document.querySelectorAll('.gallery-item').forEach(item => item.classList.remove('active'));
}

document.addEventListener('DOMContentLoaded', initLaboratory);