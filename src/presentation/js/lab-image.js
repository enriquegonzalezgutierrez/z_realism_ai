/**
 * path: src/presentation/js/lab-image.js
 * description: Static Fusion Controller v21.2 - Neural Image Research Lab.
 *
 * ABSTRACT:
 * Orchestrates the neural transformation of 2D character manifolds into 
 * photorealistic stills. This script manages the state of the Laboratory UI, 
 * handles heuristic DNA analysis, and coordinates asynchronous inference 
 * tasks with the FastAPI gateway.
 *
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as the Primary Controller for the Image-to-Image research hub. 
 * It ensures the "Advanced Metadata" manifold is correctly encapsulated 
 * and maintains the integrity of the neural synthesis lifecycle.
 *
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. UI ELEMENT MAPPING (Neural Control Manifold)
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

        // Visual Workspace (Viewports)
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
    // 3. UI INTERACTION LOGIC (ACCORDION & SLIDERS)
    // =========================================================================

    /**
     * Toggles the Advanced Metadata Accordion.
     * Manages the transition from closed (max-height 0) to expanded.
     */
    if (ui.adjTrigger && ui.adjContent) {
        ui.adjTrigger.onclick = () => {
            const isOpen = ui.adjContent.classList.toggle('open');
            ui.adjTrigger.classList.toggle('active', isOpen);
            
            // Visual feedback for the researcher
            console.log(`LAB_UI: Advanced Metadata Manifold ${isOpen ? 'Expanded' : 'Collapsed'}.`);
        };
    }

    /**
     * Utility to synchronize range sliders with their numeric value displays.
     */
    const syncSlider = (slider, label, isFloat = true) => {
        if (!slider || !label) return;
        slider.oninput = (e) => {
            const val = e.target.value;
            label.innerText = isFloat ? parseFloat(val).toFixed(2) : val;
        };
    };

    // Binding laboratory instrumentation
    syncSlider(ui.strengthSlider, ui.strengthVal);
    syncSlider(ui.depthSlider, ui.depthVal);
    syncSlider(ui.resSlider, ui.resVal, false); 
    syncSlider(ui.cfgSlider, ui.cfgVal);
    syncSlider(ui.stepsSlider, ui.stepsVal, false);

    // =========================================================================
    // 4. DATA INGESTION (FILE HANDLING)
    // =========================================================================

    ui.dropZone.onclick = () => ui.fileInput.click();

    ui.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.dropZone.classList.add('has-file');
            
            // Render source preview URL
            const url = URL.createObjectURL(file);
            ui.sourcePreview.innerHTML = `
                <span class="viewport-label">SOURCE_INPUT_MANIFOLD</span>
                <img src="${url}" style="width:100%; height:100%; object-fit:contain; animation: fadeIn 0.5s ease-out;">
            `;
            ui.essenceTag.innerText = "SOURCE_SYNCED // READY_FOR_ANALYSIS";
        }
    };

    // =========================================================================
    // 5. SUBJECT DNA ANALYSIS (HEURISTICS)
    // =========================================================================

    ui.btnAnalyze.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) return;

        ui.essenceTag.innerText = "SEQUENCING_DNA...";
        
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");

        // Request strategy from the Heuristic Analyzer (api.js bridge)
        const data = await postToGateway('/analyze', formData);
        
        if (data && data.status === 'success') {
            const rec = data.recommendations;
            
            // Dynamic UI Synchronization
            ui.strengthSlider.value = rec.strength;
            ui.strengthVal.innerText = rec.strength.toFixed(2);
            ui.depthSlider.value = rec.cn_scale_depth;
            ui.depthVal.innerText = rec.cn_scale_depth.toFixed(2);
            ui.promptInput.value = rec.texture_prompt;
            
            // Advanced parameters sync
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

    ui.btnGenerate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert("SYSTEM_ERROR: Please upload a source manifold input first.");
            return;
        }

        // Initialize inference UI state
        state.isProcessing = true;
        ui.btnGenerate.disabled = true;
        ui.btnGenerate.innerText = "FUSING_SEQUENCE...";
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        
        // Dispatch transformation task
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");
        formData.append('feature_prompt', ui.promptInput.value);
        formData.append('strength', ui.strengthSlider.value);
        formData.append('cn_depth', ui.depthSlider.value);
        formData.append('resolution_anchor', ui.resSlider.value);
        formData.append('cfg_scale', ui.cfgSlider.value);
        formData.append('steps', ui.stepsSlider.value);
        formData.append('seed', ui.seedInput.value);

        const data = await postToGateway('/transform', formData);
        
        if (data && data.task_id) {
            state.lastTaskId = data.task_id;
            
            // Polling Loop for telemetry and result retrieval
            pollNeuralTask(data.task_id, 
                // PROGRESS: Intermediate Latent Previewing
                (progress) => {
                    ui.progressBar.style.width = `${progress.percent}%`;
                    ui.statusText.innerText = progress.status_text.replace(/_/g, ' ');
                    
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
                // SUCCESS: Masterwork Rendering
                (result) => {
                    state.isProcessing = false;
                    ui.btnGenerate.disabled = false;
                    ui.btnGenerate.innerText = "INITIATE NEURAL FUSION";
                    ui.progressOverlay.classList.add('hidden');
                    
                    if (result && result.result_image_b64) {
                        ui.resultDisplay.innerHTML = `
                            <span class="viewport-label">ACTIVE_CANDIDATE_MONITOR</span>
                            <img src="data:image/png;base64,${result.result_image_b64}" style="width:100%; height:100%; object-fit:contain; z-index:5; position:relative;">
                            
                            <button id="btn-save" class="btn btn-secondary" style="position:absolute; bottom:20px; right:20px; z-index:10; font-size:0.75rem; border-color:var(--accent);">💾 SAVE PNG</button>
                            
                            <div class="metrics-overlay" style="position:absolute; bottom:20px; left:20px; font-family:var(--font-code); font-size:0.65rem; color:rgba(255,255,255,0.5); z-index:6; background:rgba(0,0,0,0.4); padding:5px 10px; border-radius:4px;">
                                SSIM: ${(result.metrics.structural_similarity * 100).toFixed(0)}% | 
                                INF_TIME: ${result.metrics.inference_time}s
                            </div>
                        `;
                        
                        document.getElementById('btn-save').onclick = () => {
                            const link = document.createElement('a');
                            link.href = `data:image/png;base64,${result.result_image_b64}`;
                            link.download = `z_fusion_${Date.now()}.png`;
                            link.click();
                        };
                    }
                }
            );
        } else {
            state.isProcessing = false;
            ui.btnGenerate.disabled = false;
            ui.btnGenerate.innerText = "INITIATE NEURAL FUSION";
            ui.progressOverlay.classList.add('hidden');
        }
    };
});