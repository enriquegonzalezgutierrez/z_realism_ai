/**
 * path: src/presentation-custom/js/lab-image.js
 * description: Static Fusion Controller v20.2 - Image-to-Image Research Hub.
 *
 * ABSTRACT:
 * This script orchestrates the neural transformation of 2D characters into 
 * photorealistic stills. It manages the communication with the FastAPI 
 * gateway, handles heuristic DNA analysis, and provides real-time visual 
 * telemetry during the diffusion denoising process.
 *
 * KEY FEATURES:
 * 1. Advanced Manifold Control: Dynamic hyperparameter adjustments (Steps, CFG, Res).
 * 2. Visual Telemetry: Real-time latent preview rendering during inference.
 * 3. Identity Anchoring: Integration with the Heuristic DNA Analyzer.
 *
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. UI ELEMENT MAPPING
    // =========================================================================
    const ui = {
        // Identity & Guidance
        charName: document.getElementById('char-name'),
        fileInput: document.getElementById('file-upload'),
        dropZone: document.getElementById('drop-zone'),
        promptInput: document.getElementById('prompt-input'),
        essenceTag: document.getElementById('essence-tag'),
        
        // Primary Research Sliders
        strengthSlider: document.getElementById('input-strength'),
        strengthVal: document.getElementById('val-strength'),
        depthSlider: document.getElementById('input-depth'),
        depthVal: document.getElementById('val-depth'),

        // Advanced Configuration (Accordion)
        adjTrigger: document.getElementById('adj-trigger'),
        adjContent: document.getElementById('adj-content'),
        resSlider: document.getElementById('input-res'),
        resVal: document.getElementById('val-res'),
        cfgSlider: document.getElementById('input-cfg'),
        cfgVal: document.getElementById('val-cfg'),
        stepsSlider: document.getElementById('input-steps'),
        stepsVal: document.getElementById('val-steps'),
        seedInput: document.getElementById('input-seed'),

        // Visual Workspace
        sourcePreview: document.getElementById('source-preview'),
        resultDisplay: document.getElementById('result-display'),
        
        // Inference Telemetry
        progressOverlay: document.getElementById('progress-overlay'),
        progressBar: document.getElementById('progress-bar'),
        statusText: document.getElementById('status-text'),

        // Primary Action Triggers
        btnGenerate: document.getElementById('btn-generate'),
        btnAnalyze: document.getElementById('btn-analyze')
    };

    // =========================================================================
    // 2. INTERNAL STATE MANAGEMENT
    // =========================================================================
    const state = {
        selectedFile: null,
        isProcessing: false,
        lastTaskId: null
    };

    // =========================================================================
    // 3. UI INTERACTION LOGIC
    // =========================================================================

    /**
     * Toggles the visibility of the Advanced Hyperparameter Manifold.
     */
    ui.adjTrigger.onclick = () => {
        ui.adjTrigger.classList.toggle('active');
        ui.adjContent.classList.toggle('open');
    };

    /**
     * Utility to synchronize range sliders with their numeric value displays.
     */
    const syncSlider = (slider, label, isFloat = true) => {
        slider.oninput = (e) => {
            const val = e.target.value;
            label.innerText = isFloat ? parseFloat(val).toFixed(2) : val;
        };
    };

    // Bind all sliders to their respective labels
    syncSlider(ui.strengthSlider, ui.strengthVal);
    syncSlider(ui.depthSlider, ui.depthVal);
    syncSlider(ui.resSlider, ui.resVal, false); // Resolution is an integer
    syncSlider(ui.cfgSlider, ui.cfgVal);
    syncSlider(ui.stepsSlider, ui.stepsVal, false); // Steps are integers

    // =========================================================================
    // 4. DATA INGESTION (FILE HANDLING)
    // =========================================================================

    /**
     * Triggers the hidden file input when the visual drop zone is clicked.
     */
    ui.dropZone.onclick = () => ui.fileInput.click();

    /**
     * Processes the uploaded image and renders the source preview.
     */
    ui.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.dropZone.classList.add('has-file');
            
            // Generate visual preview URL
            const url = URL.createObjectURL(file);
            ui.sourcePreview.innerHTML = `
                <span class="viewport-label">SOURCE_INPUT_MANIFOLD</span>
                <img src="${url}" style="width:100%; height:100%; object-fit:contain; animation: fadeIn 0.5s ease-out;">
            `;
            ui.essenceTag.innerText = "SOURCE_SYNCED // READY_FOR_ANALYSIS";
        }
    };

    // =========================================================================
    // 5. DNA ANALYSIS WORKFLOW (HEURISTICS)
    // =========================================================================

    /**
     * Dispatches the source image to the Heuristic Image Analyzer.
     * Automatically populates the UI with recommended neural weights.
     */
    ui.btnAnalyze.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) return;

        ui.essenceTag.innerText = "SEQUENCING_DNA...";
        
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value);

        // postToGateway is provided by api.js
        const data = await postToGateway('/analyze', formData);
        
        if (data && data.status === 'success') {
            const rec = data.recommendations;
            
            // Synchronize Primary Parameters
            ui.strengthSlider.value = rec.strength;
            ui.strengthVal.innerText = rec.strength.toFixed(2);
            ui.depthSlider.value = rec.cn_scale_depth;
            ui.depthVal.innerText = rec.cn_scale_depth.toFixed(2);
            ui.promptInput.value = rec.texture_prompt;
            
            // Synchronize Advanced Parameters
            ui.cfgSlider.value = rec.cfg_scale;
            ui.cfgVal.innerText = rec.cfg_scale.toFixed(1);
            ui.stepsSlider.value = rec.steps;
            ui.stepsVal.innerText = rec.steps;

            ui.essenceTag.innerText = `STRATEGY_FOUND: ${data.detected_essence}`;
        }
    };

    // =========================================================================
    // 6. NEURAL FUSION WORKFLOW (INFERENCE)
    // =========================================================================

    /**
     * Dispatches the main Image-to-Image task to the CUDA worker.
     * Manages polling and real-time visual telemetry.
     */
    ui.btnGenerate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert("SYSTEM_ERROR: Please upload a source image manifold first.");
            return;
        }

        // 1. Prepare UI for long-latency task
        state.isProcessing = true;
        ui.btnGenerate.disabled = true;
        ui.btnGenerate.innerText = "FUSING_SEQUENCE...";
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        
        // 2. Construct Multi-modal Payload
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");
        formData.append('feature_prompt', ui.promptInput.value);
        
        // Gather parameters from both Standard and Advanced panels
        formData.append('strength', ui.strengthSlider.value);
        formData.append('cn_depth', ui.depthSlider.value);
        formData.append('resolution_anchor', ui.resSlider.value);
        formData.append('cfg_scale', ui.cfgSlider.value);
        formData.append('steps', ui.stepsSlider.value);
        formData.append('seed', ui.seedInput.value);

        // 3. Dispatch to FastAPI Gateway
        const data = await postToGateway('/transform', formData);
        
        if (data && data.task_id) {
            state.lastTaskId = data.task_id;
            
            // 4. Start Polling Loop (logic defined in api.js)
            pollNeuralTask(data.task_id, 
                // PROGRESS CALLBACK: Handles real-time telemetry
                (progress) => {
                    ui.progressBar.style.width = `${progress.percent}%`;
                    ui.statusText.innerText = progress.status_text.replace(/_/g, ' ');
                    
                    // Render Intermediate Latent Preview (Visual feedback during denoising)
                    if (progress.preview_b64) {
                        let latentImg = ui.resultDisplay.querySelector('img.latent-preview');
                        if (!latentImg) {
                            latentImg = document.createElement('img');
                            latentImg.className = 'latent-preview';
                            latentImg.style.cssText = "position:absolute; inset:0; width:100%; height:100%; object-fit:contain; filter:blur(6px); z-index:1; opacity:0.6;";
                            ui.resultDisplay.appendChild(latentImg);
                        }
                        latentImg.src = `data:image/jpeg;base64,${progress.preview_b64}`;
                    }
                }, 
                // COMPLETION CALLBACK: Renders final masterwork
                (result) => {
                    state.isProcessing = false;
                    ui.btnGenerate.disabled = false;
                    ui.btnGenerate.innerText = "INITIATE NEURAL FUSION";
                    ui.progressOverlay.classList.add('hidden');
                    
                    if (result && result.result_image_b64) {
                        // Success: Display High-Fidelity Output with scientific metrics
                        ui.resultDisplay.innerHTML = `
                            <span class="viewport-label">ACTIVE_CANDIDATE_MONITOR</span>
                            <img src="data:image/png;base64,${result.result_image_b64}" style="width:100%; height:100%; object-fit:contain; z-index:5; position:relative;">
                            
                            <div class="metrics-overlay" style="position:absolute; bottom:20px; left:20px; font-family:var(--font-code); font-size:0.65rem; color:rgba(255,255,255,0.5); z-index:6; background:rgba(0,0,0,0.4); padding:5px 10px; border-radius:4px;">
                                SSIM_FIDELITY: ${(result.metrics.structural_similarity * 100).toFixed(0)}% | 
                                INF_TIME: ${result.metrics.inference_time}s
                            </div>
                            
                            <button id="btn-save" class="btn btn-secondary" style="position:absolute; bottom:20px; right:20px; z-index:10; padding:8px 15px; font-size:0.75rem; border-color:var(--accent); color:var(--accent);">💾 SAVE PNG</button>
                        `;
                        
                        // Setup Result Preservation Handler
                        document.getElementById('btn-save').onclick = () => {
                            const link = document.createElement('a');
                            link.href = `data:image/png;base64,${result.result_image_b64}`;
                            link.download = `z_fusion_${result.metrics.structural_similarity}_${Date.now()}.png`;
                            link.click();
                        };
                    } else {
                        ui.essenceTag.innerText = "INFERENCE_FAILURE // CHECK_SYSTEM_LOGS";
                    }
                }
            );
        } else {
            // Task initiation failed
            state.isProcessing = false;
            ui.btnGenerate.disabled = false;
            ui.btnGenerate.innerText = "INITIATE NEURAL FUSION";
            ui.progressOverlay.classList.add('hidden');
        }
    };
});