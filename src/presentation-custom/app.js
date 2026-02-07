/**
 * path: z_realism_ai/src/presentation-custom/app.js
 * description: Research Controller v19.5 - Advanced Manifold Control and Gallery Management.
 *
 * ABSTRACT:
 * This revision expands the client-side controller to manage the full tactical 
 * hyper-parameter manifold (including Denoising Strength and decoupled ControlNet weights).
 * It introduces a robust mechanism for managing the Candidate Gallery, allowing 
 * users to inspect historical results while the optimization loop continues 
 * in the background.
 *
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const API_BASE_URL = 'http://localhost:8000';

const state = {
    taskId: null,
    isProcessing: false,
    selectedFile: null,
    previewImgElement: null,
    
    // Default values for the full tactical manifold
    recommendedParams: {
        cn_depth: 0.75, cn_pose: 0.40, strength: 0.70,
        negative_prompt: "anime, cartoon, low quality", seed: 42
    },

    optimization: {
        active: false,
        attempts: 0,
        maxAttempts: 5,
        targetThreshold: 0.92,
        bestScore: 0,
        history: [] // Holds all generated candidates
    }
};

const ui = {
    charName: document.getElementById('char-name'),
    fileInput: document.getElementById('file-upload'),
    fileLabel: document.getElementById('file-label'),
    btnAnalyze: document.getElementById('btn-analyze'),
    btnGenerate: document.getElementById('btn-generate'),
    
    // New Sliders and inputs (Full Manifold)
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

function initLaboratory() {
    // 1. Accordion Setup
    ui.accTrigger.addEventListener('click', () => {
        ui.accContent.classList.toggle('open');
        ui.accTrigger.querySelector('.arrow').classList.toggle('rotate');
    });

    // 2. Slider Value Linking
    const link = (id, valId) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', (e) => document.getElementById(valId).innerText = parseFloat(e.target.value).toFixed(2));
    };
    link('input-res', 'val-res'); 
    link('input-steps', 'val-steps'); 
    link('input-cfg', 'val-cfg');
    link('input-strength', 'val-strength');
    link('input-cn-depth', 'val-cn-depth');
    link('input-cn-pose', 'val-cn-pose');

    // 3. File Handling
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

    // 4. Button Actions
    ui.btnAnalyze.addEventListener('click', executeDNAAnalysis);
    ui.btnGenerate.addEventListener('click', initializeFusion);

    // Set initial values from the UI (in case the user modifies defaults before analysis)
    updateRecommendedParamsFromUI();
}

function updateRecommendedParamsFromUI() {
    state.recommendedParams = {
        cn_depth: parseFloat(ui.cnDepthSlider.value),
        cn_pose: parseFloat(ui.cnPoseSlider.value),
        strength: parseFloat(ui.strengthSlider.value),
        negative_prompt: state.recommendedParams.negative_prompt, // Kept from state for defaults
        seed: parseInt(ui.seedInput.value)
    };
}

function initializeFusion() {
    // Reset optimization state
    state.optimization.attempts = 0;
    state.optimization.bestScore = 0;
    state.optimization.active = ui.chkAutoPilot.checked;
    state.optimization.history = [];
    ui.gallery.innerHTML = ''; // Clear previous session
    
    // Display/hide optimization status panel
    if(state.optimization.active) {
        ui.optStatus.classList.remove('hidden');
        ui.optScore.innerText = "0%";
    } else {
        ui.optStatus.classList.add('hidden');
    }
    
    // Ensure the current UI settings are loaded into the tactical manifold
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
            
            // 1. Update State's Recommended Manifold
            state.recommendedParams = {
                cn_depth: r.cn_scale_depth, 
                cn_pose: r.cn_scale_pose,
                strength: r.strength, 
                negative_prompt: r.negative_prompt,
                seed: parseInt(ui.seedInput.value) // Use existing UI seed
            };
            
            // 2. Update UI Sliders/Inputs to reflect recommendations
            ui.strengthSlider.value = r.strength;
            document.getElementById('val-strength').innerText = r.strength.toFixed(2);
            ui.cnDepthSlider.value = r.cn_scale_depth;
            document.getElementById('val-cn-depth').innerText = r.cn_scale_depth.toFixed(2);
            ui.cnPoseSlider.value = r.cn_scale_pose;
            document.getElementById('val-cn-pose').innerText = r.cn_scale_pose.toFixed(2);
            
            ui.promptInput.value = r.texture_prompt;
            ui.essenceTag.innerText = `STRATEGY: ${data.detected_essence}`;
        }
    } catch (err) { ui.essenceTag.innerText = "OFFLINE: Analysis Failure."; console.error(err); }
}

async function startFusingSequence() {
    if (!state.selectedFile || state.isProcessing) return; 
    toggleControls(true);
    resetWorkspace();
    
    if (state.optimization.active) {
        state.optimization.attempts++;
        ui.optCount.innerText = state.optimization.attempts;
    }
    
    // Prepare the full request body using the latest state/UI values
    const body = new FormData();
    body.append('file', state.selectedFile);
    body.append('character_name', ui.charName.value);
    body.append('feature_prompt', ui.promptInput.value);
    body.append('resolution_anchor', ui.resSlider.value);
    body.append('steps', ui.stepsSlider.value);
    body.append('cfg_scale', ui.cfgSlider.value);
    
    // Critical Hyperparameters from the tactical manifold (state.recommendedParams)
    // These are often modified by the optimization loop, overriding the UI sliders.
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
    } catch (err) { toggleControls(false); console.error("Fusion Dispatch Failed:", err); }
}

function pollInferenceTelemetry() {
    const pollInterval = setInterval(async () => {
        if (!state.taskId) return clearInterval(pollInterval);
        
        try {
            const response = await fetch(`${API_BASE_URL}/status/${state.taskId}`);
            const data = await response.json();
            
            if (data.status === 'PROGRESS') {
                const pct = data.progress.percent;
                requestAnimationFrame(() => {
                    ui.progressBar.style.width = `${pct}%`;
                    ui.progressText.innerText = `${data.progress.status_text.replace(/_/g, ' ')}: ${pct}%`;
                });
                
                // Show intermediate preview
                if (data.progress.preview_b64) {
                    if (!state.previewImgElement) {
                        ui.resultDisplay.innerHTML = ''; 
                        state.previewImgElement = new Image();
                        state.previewImgElement.id = 'active-preview';
                        state.previewImgElement.style.cssText = "width:100%; height:100%; object-fit:contain; filter:blur(4px);";
                        ui.resultDisplay.appendChild(state.previewImgElement);
                    }
                    state.previewImgElement.src = `data:image/jpeg;base64,${data.progress.preview_b64}`;
                }
            } 
            else if (data.status === 'SUCCESS') {
                clearInterval(pollInterval);
                requestAnimationFrame(() => { ui.progressBar.style.width = '100%'; ui.progressText.innerText = "SYNC COMPLETE."; });
                // Delay rendering slightly to allow final metrics to propagate
                setTimeout(() => { renderFinalMasterwork(); }, 600);
            } 
            else if (data.status === 'FAILURE') {
                clearInterval(pollInterval);
                state.optimization.active = false;
                ui.essenceTag.innerText = "CRITICAL FAILURE";
                toggleControls(false);
            }
        } catch (err) { 
            clearInterval(pollInterval); 
            // Only stop processing if the error is severe (e.g., connection lost)
            // If optimization is active, a failure might stop the loop.
            if (!state.optimization.active) toggleControls(false); 
        }
    }, 1000); 
}

async function renderFinalMasterwork() {
    try {
        const response = await fetch(`${API_BASE_URL}/result/${state.taskId}`);
        if (response.status === 202) {
             // Task still pending in broker, try again (shouldn't happen after SUCCESS)
             setTimeout(renderFinalMasterwork, 500); 
             return;
        }

        const result = await response.json();
        const m = result.metrics;
        const b64 = result.result_image_b64;
        
        // Combine data for history
        const candidate = {
            id: state.taskId,
            b64: b64,
            metrics: m,
            params: { ...state.recommendedParams, seed: state.recommendedParams.seed } // Record params used
        };

        // 1. ADD TO POPULATION GALLERY
        addCandidateToGallery(candidate);

        // 2. RENDER MAIN PREVIEW (and make it sharp)
        displayCandidate(candidate);
        ui.progressContainer.classList.add('hidden');
        
        // 3. 🤖 EVOLUTIONARY SUPERVISOR
        if (state.optimization.active) {
            const currentScore = (m.structural_similarity + m.identity_preservation) / 2;
            
            // Log for debugging the loop
            console.log(`[ATTEMPT ${state.optimization.attempts}] Score: ${currentScore.toFixed(3)} | Params: Depth=${candidate.params.cn_depth.toFixed(2)}, Str=${candidate.params.strength.toFixed(2)}, Seed=${candidate.params.seed}`);

            if (currentScore > state.optimization.bestScore) {
                state.optimization.bestScore = currentScore;
                ui.optScore.innerText = `${Math.round(currentScore * 100)}%`;
            }
            if (currentScore >= state.optimization.targetThreshold) {
                ui.essenceTag.innerText = "🎯 TARGET REACHED! OPTIMIZATION HALTED.";
                state.optimization.active = false;
                toggleControls(false);
                return;
            }
            if (state.optimization.attempts >= state.optimization.maxAttempts) {
                ui.essenceTag.innerText = "⚠️ POPULATION LIMIT REACHED. OPTIMIZATION HALTED.";
                state.optimization.active = false;
                toggleControls(false);
                return;
            }

            // --- MUTATION PROTOCOL (Adaptive Sampling) ---
            // Randomly adjust parameters based on performance deviations
            
            // If structural fidelity is low, increase depth constraint
            if (m.structural_similarity < 0.85) {
                state.recommendedParams.cn_depth = Math.min(1.2, state.recommendedParams.cn_depth + 0.05);
            }
            
            // If identity preservation is low, slightly reduce denoising strength
            if (m.identity_preservation < 0.90) {
                state.recommendedParams.strength = Math.max(0.40, state.recommendedParams.strength - 0.03);
            } else {
                 // Or slightly increase strength if identity is good, seeking more realism
                 state.recommendedParams.strength = Math.min(1.0, state.recommendedParams.strength + 0.01);
            }

            // Introduce stochastic noise by randomizing the seed for the next iteration
            state.recommendedParams.seed = Math.floor(Math.random() * 1000000);
            
            // Apply a small random perturbation to pose constraint to explore subtle anatomical variations
            state.recommendedParams.cn_pose = Math.max(0.2, Math.min(0.8, state.recommendedParams.cn_pose + (Math.random() - 0.5) * 0.05));
            
            setTimeout(() => { 
                state.isProcessing = false; 
                startFusingSequence(); 
            }, 1000); // 1s buffer before next GPU task
        } else {
            // Not in autopilot mode
            toggleControls(false);
        }
    } catch (err) { 
        console.error("Result Fetch/Render Failure:", err); 
        state.optimization.active = false; // Stop loop on failure
        toggleControls(false); 
    }
}

/**
 * UI UTILITY: Adds a result to the history strip
 */
function addCandidateToGallery(candidate) {
    const score = Math.round(((candidate.metrics.structural_similarity + candidate.metrics.identity_preservation) / 2) * 100);
    const wrapper = document.createElement('div');
    wrapper.className = 'gallery-item glass-panel';
    wrapper.setAttribute('data-candidate-id', candidate.id);
    
    // Store the candidate data in the global history array
    state.optimization.history.push(candidate); 

    wrapper.innerHTML = `
        <img src="data:image/png;base64,${candidate.b64}">
        <div class="gallery-score">${score}%</div>
    `;
    
    // Allow clicking on candidates to review results without interrupting the loop
    wrapper.onclick = () => {
        // Find the candidate from history
        const targetCandidate = state.optimization.history.find(c => c.id === candidate.id);
        if (targetCandidate) {
            displayCandidate(targetCandidate);
            // Highlight active gallery item
            document.querySelectorAll('.gallery-item').forEach(item => item.classList.remove('active'));
            wrapper.classList.add('active');
        }
    };
    
    ui.gallery.prepend(wrapper); // Latest first
}

/**
 * UI UTILITY: Renders a specific candidate (from history or active result)
 */
function displayCandidate(candidate) {
    // Stop any live preview blur effect
    ui.resultDisplay.innerHTML = `<img src="data:image/png;base64,${candidate.b64}" style="animation: fadeIn 0.4s ease-out;">`;
    
    // Update Metrics Panel
    const m = candidate.metrics;
    ui.metricSsim.innerText = `${(m.structural_similarity * 100).toFixed(0)}%`;
    ui.metricId.innerText = `${(m.identity_preservation * 100).toFixed(0)}%`;
    ui.metricTime.innerText = `${m.inference_time}s`;
    ui.metricsPanel.classList.remove('hidden');
    
    // If not in processing state, update the sidebar controls to show selected candidate's params
    if (!state.isProcessing) {
         // Optionally, update sliders to selected candidate's params if needed for inspection
         // For now, we only display metrics.
    }
}

function toggleControls(locked) {
    state.isProcessing = locked; 
    ui.btnGenerate.disabled = locked;
    ui.btnAnalyze.disabled = locked;
    ui.btnGenerate.innerText = locked ? "⚡ SEQUENCING..." : "INITIATE NEURAL FUSION";
    ui.chkAutoPilot.disabled = locked;
    
    // If unlocked, ensure the UI reflects the parameters currently loaded in the state for the next run.
    if (!locked) {
        // Sync the UI seeds back to the state's calculated seed if autopilot was running
        ui.seedInput.value = state.recommendedParams.seed; 
    }
}

function resetWorkspace() {
    ui.progressContainer.classList.remove('hidden');
    ui.progressBar.style.width = '0%';
    state.previewImgElement = null;
    
    // Clear the active candidate highlight
    document.querySelectorAll('.gallery-item').forEach(item => item.classList.remove('active'));
}

document.addEventListener('DOMContentLoaded', initLaboratory);