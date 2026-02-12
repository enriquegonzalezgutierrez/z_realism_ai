/**
 * path: src/presentation/js/lab-image.js
 * description: Static Fusion Controller v21.10 - DOM Integrity & Telemetry Fix.
 *
 * ABSTRACT:
 * Orchestrates the neural transformation of 2D character manifolds into 
 * photorealistic stills. This version ensures that the real-time telemetry 
 * (progress bar) remains consistently visible by manipulating only the 
 * dynamic content viewport.
 *
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. UI ELEMENT MAPPING (Neural Control Manifold)
    // =========================================================================
    const ui = {
        charName: document.getElementById('char-name'),
        fileInput: document.getElementById('file-upload'),
        dropZone: document.getElementById('drop-zone'),
        promptInput: document.getElementById('prompt-input'),
        essenceTag: document.getElementById('essence-tag'),
        strengthSlider: document.getElementById('input-strength'),
        strengthVal: document.getElementById('val-strength'),
        depthSlider: document.getElementById('input-depth'),
        depthVal: document.getElementById('val-depth'),
        adjTrigger: document.getElementById('adj-trigger'),
        adjContent: document.getElementById('adj-content'),
        resSlider: document.getElementById('input-res'),
        resVal: document.getElementById('val-res'),
        cfgSlider: document.getElementById('input-cfg'),
        cfgVal: document.getElementById('val-cfg'),
        stepsSlider: document.getElementById('input-steps'),
        stepsVal: document.getElementById('val-steps'),
        seedInput: document.getElementById('input-seed'),
        sourcePreview: document.getElementById('source-preview'),
        resultDisplay: document.getElementById('result-display'),
        dynamicContentViewport: document.getElementById('dynamic-content-viewport'), // NEW: Dynamic content target
        progressOverlay: document.getElementById('progress-overlay'),
        progressBar: document.getElementById('progress-bar'),
        statusText: document.getElementById('status-text'),
        btnGenerate: document.getElementById('btn-generate'),
        btnAnalyze: document.getElementById('btn-analyze'),
        cannySlider: document.getElementById('input-canny'),
        cannyVal: document.getElementById('val-canny'),
        cannyLowSlider: document.getElementById('input-canny-low'),
        cannyLowVal: document.getElementById('val-canny-low'),
        cannyHighSlider: document.getElementById('input-canny-high'),
        cannyHighVal: document.getElementById('val-canny-high'),
    };

    // =========================================================================
    // 2. INTERNAL STATE MANAGEMENT
    // =========================================================================
    const state = {
        selectedFile: null,
        isProcessing: false,
        lastTaskId: null,
        currentLatentPreview: null // Keep track of the preview image element
    };

    // =========================================================================
    // 3. UTILITY & UI HANDLERS
    // =========================================================================

    /**
     * Resets the laboratory workspace to its initial state before a new task.
     * CRITICAL FIX: Ensures telemetry overlays remain in the DOM.
     */
    const resetWorkspace = () => {
        // 1. Sanitize ONLY the dynamic content viewport
        ui.dynamicContentViewport.innerHTML = `
            <div style="color: rgba(255,255,255,0.02); font-family: var(--font-code); font-size: 2.5rem; font-weight: 800; letter-spacing: 10px;">
                OFFLINE
            </div>
        `;
        state.currentLatentPreview = null; // Reset the reference

        // 2. Reactivate and Reset Telemetry Overlay (it's always in the DOM)
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        ui.statusText.innerText = "INITIALIZING...";

        const telemetryHud = document.getElementById('telemetry-hud');
        if (telemetryHud) {
            telemetryHud.classList.add('hidden');
        }
        
        console.log("LAB_UI: Workspace sanitized for new synthesis task.");
    };
    
    // Accordion Logic
    if (ui.adjTrigger && ui.adjContent) {
        ui.adjTrigger.onclick = () => {
            ui.adjContent.classList.toggle('open');
            ui.adjTrigger.classList.toggle('active');
        };
    }

    // Slider Synchronization
    const syncSlider = (slider, label, isFloat = true) => {
        if (!slider || !label) return;
        slider.oninput = (e) => {
            label.innerText = isFloat ? parseFloat(e.target.value).toFixed(2) : e.target.value;
        };
    };

    syncSlider(ui.strengthSlider, ui.strengthVal);
    syncSlider(ui.depthSlider, ui.depthVal);
    syncSlider(ui.resSlider, ui.resVal, false);
    syncSlider(ui.cfgSlider, ui.cfgVal);
    syncSlider(ui.stepsSlider, ui.stepsVal, false);
    syncSlider(ui.cannySlider, ui.cannyVal);
    syncSlider(ui.cannyLowSlider, ui.cannyLowVal, false);
    syncSlider(ui.cannyHighSlider, ui.cannyHighVal, false);

    // =========================================================================
    // 4. CORE WORKFLOWS
    // =========================================================================

    // File Handling
    ui.dropZone.onclick = () => ui.fileInput.click();
    ui.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.dropZone.classList.add('has-file');
            const url = URL.createObjectURL(file);
            ui.sourcePreview.innerHTML = `
                <span class="viewport-label">SOURCE_INPUT_MANIFOLD</span>
                <img src="${url}" alt="Source">
            `;
            ui.essenceTag.innerText = "SOURCE_SYNCED // READY";
        }
    };

    // DNA Analysis
    ui.btnAnalyze.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) return;
        ui.essenceTag.innerText = "SEQUENCING_DNA...";
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");
        const data = await postToGateway('/analyze', formData);
        if (data && data.status === 'success') {
            const rec = data.recommendations;
            ui.strengthSlider.value = rec.strength;
            ui.strengthVal.innerText = rec.strength.toFixed(2);
            ui.depthSlider.value = rec.cn_scale_depth;
            ui.depthVal.innerText = rec.cn_scale_depth.toFixed(2);
            ui.promptInput.value = rec.texture_prompt;
            ui.cfgSlider.value = rec.cfg_scale;
            ui.cfgVal.innerText = rec.cfg_scale.toFixed(1);
            ui.stepsSlider.value = rec.steps;
            ui.stepsVal.innerText = rec.steps;
            ui.essenceTag.innerText = `STRATEGY_FOUND: ${data.detected_essence}`;
        }
    };

    // Neural Fusion (Main Generation Task)
    ui.btnGenerate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert("SYSTEM_ERROR: Please upload a source manifold.");
            return;
        }

        // --- STATE RESET PROTOCOL ---
        resetWorkspace(); 

        state.isProcessing = true;
        ui.btnGenerate.disabled = true;
        ui.btnGenerate.innerText = "FUSING...";
        
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
        formData.append('cn_canny', ui.cannySlider.value);
        formData.append('canny_low', ui.cannyLowSlider.value);
        formData.append('canny_high', ui.cannyHighSlider.value);

        const data = await postToGateway('/transform', formData);
        
        if (data && data.task_id) {
            state.lastTaskId = data.task_id;
            
            pollNeuralTask(data.task_id, 
                // Progress Callback
                (progress) => {
                    ui.progressBar.style.width = `${progress.percent}%`;
                    ui.statusText.innerText = progress.status_text.replace(/_/g, ' ');
                    
                    if (progress.preview_b64) {
                        if (!state.currentLatentPreview) {
                            state.currentLatentPreview = document.createElement('img');
                            state.currentLatentPreview.className = 'latent-preview';
                            state.currentLatentPreview.style.cssText = "position:absolute; inset:0; width:100%; height:100%; object-fit:contain; filter:blur(6px); opacity:0.6; z-index:1;";
                            ui.dynamicContentViewport.appendChild(state.currentLatentPreview); // Insert into dynamic viewport
                        }
                        state.currentLatentPreview.src = `data:image/jpeg;base64,${progress.preview_b64}`;
                    }
                }, 
                // Completion Callback
                (result) => {
                    state.isProcessing = false;
                    ui.btnGenerate.disabled = false;
                    ui.btnGenerate.innerText = "INITIATE NEURAL FUSION";
                    ui.progressOverlay.classList.add('hidden'); // Hide progress overlay

                    if (result && result.metrics) {
                        const m = result.metrics;
                        
                        const applyMetric = (elementId, value, okThreshold, warnThreshold, isRatio = false) => {
                            const row = document.getElementById(elementId);
                            const indicator = row.querySelector('.status-indicator');
                            const valueDisplay = row.querySelector('.hud-value');
                            
                            const percent = (value * 100).toFixed(0) + '%';
                            valueDisplay.innerText = percent;
                            
                            indicator.classList.remove('status-ok', 'status-warn', 'status-error');
                            
                            if (value >= okThreshold) {
                                indicator.classList.add('status-ok');
                            } else if (value >= warnThreshold) {
                                indicator.classList.add('status-warn');
                            } else {
                                indicator.classList.add('status-error');
                            }
                        };

                        applyMetric('stat-structural', m.structural_similarity, 0.70, 0.40);
                        
                        applyMetric('stat-identity', m.identity_preservation, 0.80, 0.60);
                        
                        applyMetric('stat-realism', m.textural_realism, 1.20, 1.00);

                        document.getElementById('hud-time').innerText = m.inference_time.toFixed(1) + "s";

                        ui.telemetryHud = document.getElementById('telemetry-hud');
                        ui.telemetryHud.classList.remove('hidden');
                    }
                    
                    if (result && result.result_image_b64) {
                        ui.dynamicContentViewport.innerHTML = `
                            <img src="data:image/png;base64,${result.result_image_b64}" alt="Result">
                            <button id="btn-save" class="btn btn-secondary" style="position:absolute; bottom:20px; right:20px; z-index:10;">💾 SAVE</button>
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