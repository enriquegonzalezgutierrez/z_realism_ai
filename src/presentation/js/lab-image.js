/**
 * path: src/presentation/js/lab-image.js
 * description: Static Image Production Controller v1.0 - Commercial Product.
 *
 * ABSTRACT:
 * Orchestrates the neural transformation of 2D artistic concepts into 
 * high-fidelity photorealistic still images. This version ensures that 
 * real-time production feedback and asset intelligence are streamlined 
 * for commercial users.
 *
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. UI ELEMENT MAPPING (Creative Control Panel)
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
        dynamicContentViewport: document.getElementById('dynamic-content-viewport'), 
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
        currentLatentPreview: null 
    };

    // =========================================================================
    // 3. UTILITY & UI HANDLERS
    // =========================================================================

    /**
     * Resets the production workspace to its initial state before a new task.
     */
    const resetWorkspace = () => {
        // 1. Sanitize ONLY the dynamic content viewport
        ui.dynamicContentViewport.innerHTML = `
            <div style="color: rgba(255,255,255,0.02); font-family: var(--font-code); font-size: 2.5rem; font-weight: 800; letter-spacing: 10px;">
                OFFLINE
            </div>
        `;
        state.currentLatentPreview = null; 

        // 2. Reactivate and Reset Progress Overlay
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        ui.statusText.innerText = "INITIALIZING PRODUCTION RUN..."; // Updated text

        const telemetryHud = document.getElementById('telemetry-hud');
        if (telemetryHud) {
            telemetryHud.classList.add('hidden');
        }
        
        console.log("PRODUCTION_UI: Workspace sanitized for new synthesis task."); // Updated log
    };
    
    // Accordion Logic remains the same.
    if (ui.adjTrigger && ui.adjContent) {
        ui.adjTrigger.onclick = () => {
            ui.adjContent.classList.toggle('open');
            ui.adjTrigger.classList.toggle('active');
        };
    }

    // Slider Synchronization remains the same.
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
                <span class="viewport-label">SOURCE_ARTWORK_INPUT</span>
                <img src="${url}" alt="Source">
            `;
            ui.essenceTag.innerText = "ARTWORK_LOADED // READY FOR ANALYSIS"; // Updated text
        }
    };

    // DNA Analysis
    ui.btnAnalyze.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) return;
        ui.essenceTag.innerText = "ANALYZING_ARTWORK_DNA..."; // Updated text
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
            // NEW: Update Canny sliders from analysis recommendations
            ui.cannySlider.value = rec.cn_scale_pose; // cn_pose is now Canny weight
            ui.cannyVal.innerText = rec.cn_scale_pose.toFixed(2);
            ui.cannyLowSlider.value = rec.canny_low;
            ui.cannyLowVal.innerText = rec.canny_low;
            ui.cannyHighSlider.value = rec.canny_high;
            ui.cannyHighVal.innerText = rec.canny_high;

            ui.promptInput.value = rec.texture_prompt;
            ui.cfgSlider.value = rec.cfg_scale;
            ui.cfgVal.innerText = rec.cfg_scale.toFixed(1);
            ui.stepsSlider.value = rec.steps;
            ui.stepsVal.innerText = rec.steps;
            ui.essenceTag.innerText = `DNA_PROFILE_LOADED: ${data.detected_essence}`; // Updated text
        }
    };

    // Neural Fusion (Main Generation Task)
    ui.btnGenerate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert("SYSTEM_ERROR: Please upload your source artwork."); // Updated text
            return;
        }

        // --- STATE RESET PROTOCOL ---
        resetWorkspace(); 

        state.isProcessing = true;
        ui.btnGenerate.disabled = true;
        ui.btnGenerate.innerText = "INITIATING PRODUCTION..."; // Updated text
        
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
                    ui.statusText.innerText = progress.status_text.replace(/_/g, ' '); // Keep original status message from backend
                }, 
                // Completion Callback
                (result) => {
                    state.isProcessing = false;
                    ui.btnGenerate.disabled = false;
                    ui.btnGenerate.innerText = "INITIATE PRODUCTION"; // Updated text
                    ui.progressOverlay.classList.add('hidden'); 

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
            ui.btnGenerate.innerText = "INITIATE PRODUCTION"; // Updated text
            ui.progressOverlay.classList.add('hidden');
        }
    };
});