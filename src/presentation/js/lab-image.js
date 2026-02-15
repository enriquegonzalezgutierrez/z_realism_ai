/**
 * path: src/presentation/js/lab-image.js
 * description: Static Image Production Controller v2.3 - Advanced Telemetry HUD.
 *
 * ABSTRACT:
 * Orchestrates the neural transformation of 2D artwork into photorealistic stills.
 * This version enhances the Telemetry HUD by injecting character-specific DNA 
 * metadata and detected essence classification alongside neural metrics.
 *
 * SOLID PRINCIPLES:
 * - SRP: Manages Image Production UI logic and HUD telemetry updates.
 * - DIP: Depends on the I18nEngine for localized string resolution.
 * 
 * MODIFICATION LOG v2.3:
 * Added support for character DNA projection. The HUD now displays the 
 * character name and the semantic essence detected by the Asset Intelligence 
 * engine (e.g., "human_demonic_martial_artist").
 *
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. UI ELEMENT MAPPING (Control Panel & Telemetry HUD)
    // =========================================================================
    const ui = {
        charName: document.getElementById('char-name'),
        fileInput: document.getElementById('file-upload'),
        dropZone: document.getElementById('drop-zone'),
        promptInput: document.getElementById('prompt-input'),
        essenceTag: document.getElementById('essence-tag'),
        
        // Control Sliders
        strengthSlider: document.getElementById('input-strength'),
        strengthVal: document.getElementById('val-strength'),
        depthSlider: document.getElementById('input-depth'),
        depthVal: document.getElementById('val-depth'),
        cannySlider: document.getElementById('input-canny'),
        cannyVal: document.getElementById('val-canny'),
        
        // Advanced Settings
        adjTrigger: document.getElementById('adj-trigger'),
        adjContent: document.getElementById('adj-content'),
        resSlider: document.getElementById('input-res'),
        resVal: document.getElementById('val-res'),
        cfgSlider: document.getElementById('input-cfg'),
        cfgVal: document.getElementById('val-cfg'),
        stepsSlider: document.getElementById('input-steps'),
        stepsVal: document.getElementById('val-steps'),
        seedInput: document.getElementById('input-seed'),
        cannyLowSlider: document.getElementById('input-canny-low'),
        cannyLowVal: document.getElementById('val-canny-low'),
        cannyHighSlider: document.getElementById('input-canny-high'),
        cannyHighVal: document.getElementById('val-canny-high'),
        
        // Viewports & Overlays
        sourcePreview: document.getElementById('source-preview'),
        resultDisplay: document.getElementById('result-display'),
        dynamicContentViewport: document.getElementById('dynamic-content-viewport'), 
        progressOverlay: document.getElementById('progress-overlay'),
        progressBar: document.getElementById('progress-bar'),
        statusText: document.getElementById('status-text'),
        
        // Advanced Telemetry HUD Elements (v2.3)
        telemetryHud: document.getElementById('telemetry-hud'),
        valHudDna: document.getElementById('val-hud-dna'),
        valHudEssence: document.getElementById('val-hud-essence'),
        hudTime: document.getElementById('hud-time'),
        
        // Action Triggers
        btnGenerate: document.getElementById('btn-generate'),
        btnAnalyze: document.getElementById('btn-analyze')
    };

    // =========================================================================
    // 2. INTERNAL STATE MANAGEMENT
    // =========================================================================
    const state = {
        selectedFile: null,
        isProcessing: false,
        lastTaskId: null,
        // Character DNA Metadata
        detectedName: "UNKNOWN",
        detectedEssence: "NULL"
    };

    // =========================================================================
    // 3. UTILITY & UI HANDLERS
    // =========================================================================

    /**
     * Resets the production workspace and hides telemetry.
     */
    const resetWorkspace = () => {
        ui.dynamicContentViewport.innerHTML = `
            <div style="color: rgba(255,255,255,0.02); font-family: var(--font-code); font-size: 2.5rem; font-weight: 800; letter-spacing: 10px;">
                OFFLINE
            </div>
        `;
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        ui.statusText.innerText = i18n.translate('status_processing');

        if (ui.telemetryHud) {
            ui.telemetryHud.classList.add('hidden');
        }
        
        console.log(`PRODUCTION_UI: Workspace sanitized [${i18n.currentLang.toUpperCase()}]`);
    };
    
    // Accordion Logic for Advanced Settings
    if (ui.adjTrigger && ui.adjContent) {
        ui.adjTrigger.onclick = () => {
            ui.adjContent.classList.toggle('open');
            ui.adjTrigger.classList.toggle('active');
        };
    }

    // High-Fidelity Slider Sync
    const syncSlider = (slider, label, isFloat = true) => {
        if (!slider || !label) return;
        slider.oninput = (e) => {
            label.innerText = isFloat ? parseFloat(e.target.value).toFixed(2) : e.target.value;
        };
    };

    syncSlider(ui.strengthSlider, ui.strengthVal);
    syncSlider(ui.depthSlider, ui.depthVal);
    syncSlider(ui.cannySlider, ui.cannyVal);
    syncSlider(ui.resSlider, ui.resVal, false);
    syncSlider(ui.cfgSlider, ui.cfgVal);
    syncSlider(ui.stepsSlider, ui.stepsVal, false);
    syncSlider(ui.cannyLowSlider, ui.cannyLowVal, false);
    syncSlider(ui.cannyHighSlider, ui.cannyHighVal, false);

    // =========================================================================
    // 4. CORE WORKFLOWS
    // =========================================================================

    // Asset Ingestion
    ui.dropZone.onclick = () => ui.fileInput.click();
    ui.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.dropZone.classList.add('has-file');
            const url = URL.createObjectURL(file);
            ui.sourcePreview.innerHTML = `
                <span class="viewport-label" data-i18n="lab_viewport_source">${i18n.translate('lab_viewport_source')}</span>
                <img src="${url}" alt="Source Asset">
            `;
            ui.essenceTag.innerText = i18n.translate('status_ready');
        }
    };

    // Asset Intelligence: DNA Extraction & DNA Profile Storage (e.g., Akuma)
    ui.btnAnalyze.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) return;
        ui.essenceTag.innerText = "ANALYZING_ARTWORK_DNA..."; 

        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");

        const data = await postToGateway('/analyze', formData);
        if (data && data.status === 'success') {
            const rec = data.recommendations;
            
            // Map AI Recommendations to UI Controls
            ui.strengthSlider.value = rec.strength;
            ui.strengthVal.innerText = rec.strength.toFixed(2);
            ui.depthSlider.value = rec.cn_scale_depth;
            ui.depthVal.innerText = rec.cn_scale_depth.toFixed(2);
            ui.cannySlider.value = rec.cn_scale_pose; 
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

            // Store DNA metadata in local state for HUD projection
            state.detectedName = ui.charName.value || "UNKNOWN";
            state.detectedEssence = data.detected_essence;
            ui.essenceTag.innerText = `DNA_PROFILE: ${data.detected_essence}`;
        }
    };

    // Neural Production Execution
    ui.btnGenerate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert(i18n.translate('alert_no_artwork'));
            return;
        }

        resetWorkspace(); 
        state.isProcessing = true;
        ui.btnGenerate.disabled = true;
        ui.btnGenerate.innerText = i18n.translate('btn_fusing');
        
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");
        formData.append('feature_prompt', ui.promptInput.value);
        formData.append('strength', ui.strengthSlider.value);
        formData.append('cn_depth', ui.depthSlider.value);
        formData.append('cn_canny', ui.cannySlider.value);
        formData.append('canny_low', ui.cannyLowSlider.value);
        formData.append('canny_high', ui.cannyHighSlider.value);
        formData.append('resolution_anchor', ui.resSlider.value);
        formData.append('cfg_scale', ui.cfgSlider.value);
        formData.append('steps', ui.stepsSlider.value);
        formData.append('seed', ui.seedInput.value);

        const data = await postToGateway('/transform', formData);
        
        if (data && data.task_id) {
            state.lastTaskId = data.task_id;
            
            pollNeuralTask(data.task_id, 
                // Progress & ETA Telemetry Callback
                (progress) => {
                    ui.progressBar.style.width = `${progress.percent}%`;
                    const etaText = progress.eta ? ` | ${i18n.translate('status_eta')} ${progress.eta}` : '';
                    ui.statusText.innerText = `${progress.status_text}${etaText}`;
                }, 
                // Completion & HUD Injection Callback
                (result) => {
                    state.isProcessing = false;
                    ui.btnGenerate.disabled = false;
                    ui.btnGenerate.innerText = i18n.translate('btn_initiate');
                    ui.progressOverlay.classList.add('hidden'); 

                    if (result && result.metrics) {
                        const m = result.metrics;
                        const applyMetric = (elementId, value, okThreshold, warnThreshold) => {
                            const row = document.getElementById(elementId);
                            const indicator = row.querySelector('.status-indicator');
                            const valueDisplay = row.querySelector('.hud-value');
                            valueDisplay.innerText = (value * 100).toFixed(0) + '%';
                            indicator.classList.remove('status-ok', 'status-warn', 'status-error');
                            if (value >= okThreshold) indicator.classList.add('status-ok');
                            else if (value >= warnThreshold) indicator.classList.add('status-warn');
                            else indicator.classList.add('status-error');
                        };

                        // Project Character DNA metadata onto the HUD
                        ui.valHudDna.innerText = state.detectedName.toUpperCase();
                        ui.valHudEssence.innerText = state.detectedEssence.toUpperCase();

                        // Apply Analytical Metrics
                        applyMetric('stat-structural', m.structural_similarity, 0.70, 0.40);
                        applyMetric('stat-identity', m.identity_preservation, 0.80, 0.60);
                        applyMetric('stat-realism', m.textural_realism, 1.20, 1.00);
                        ui.hudTime.innerText = m.inference_time.toFixed(1) + "s";
                        
                        ui.telemetryHud.classList.remove('hidden');
                    }
                    
                    if (result && result.result_image_b64) {
                        ui.dynamicContentViewport.innerHTML = `
                            <img src="data:image/png;base64,${result.result_image_b64}" alt="Production Result">
                            <button id="btn-save" class="btn btn-secondary" style="position:absolute; bottom:20px; right:20px; z-index:10;">💾 SAVE</button>
                        `;
                        document.getElementById('btn-save').onclick = () => {
                            const link = document.createElement('a');
                            link.href = `data:image/png;base64,${result.result_image_b64}`;
                            link.download = `z_production_${Date.now()}.png`;
                            link.click();
                        };
                    }
                }
            );
        } else {
            state.isProcessing = false;
            ui.btnGenerate.disabled = false;
            ui.btnGenerate.innerText = i18n.translate('btn_initiate');
            ui.progressOverlay.classList.add('hidden');
        }
    };
});