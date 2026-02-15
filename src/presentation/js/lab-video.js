/**
 * path: src/presentation/js/lab-video.js
 * description: Temporal Motion Production Controller v2.1 - i18n & SOLID Edition.
 * 
 * ABSTRACT:
 * Orchestrates the Image-to-Video neural pipeline. This controller manages 
 * the production of cinematic sequences, handling asset ingestion, 
 * hyperparameter coordination, and real-time temporal telemetry.
 * 
 * SOLID PRINCIPLES:
 * - SRP: Exclusively handles the Temporal Production UI and task lifecycle.
 * - DIP: Depends on the I18nEngine for localized string resolution.
 *
 * MODIFICATION LOG v2.1:
 * Implemented the "FUSING" state logic for the motion production button. 
 * The button now disables itself and displays the localized fusing label 
 * during the asynchronous animation lifecycle to prevent redundant 
 * requests and improve UX feedback.
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
        motionPrompt: document.getElementById('motion-prompt'),
        
        // Temporal Hyperparameter Sliders
        durationSlider: document.getElementById('input-duration'),
        durationVal: document.getElementById('val-duration'),
        bucketSlider: document.getElementById('input-bucket'),
        bucketVal: document.getElementById('val-bucket'),
        fpsSlider: document.getElementById('input-fps'),
        fpsVal: document.getElementById('val-fps'),
        
        // Action Triggers
        btnAnimate: document.getElementById('btn-animate'),
        
        // Neural Viewports
        sourcePreview: document.getElementById('source-preview'),
        resultDisplay: document.getElementById('result-display'),
        dynamicContentViewport: document.getElementById('dynamic-content-viewport'),
        
        // Telemetry & Progress Overlays
        progressOverlay: document.getElementById('progress-overlay'),
        progressBar: document.getElementById('progress-bar'),
        statusText: document.getElementById('status-text'),

        // Telemetry HUD Elements
        telemetryHud: document.getElementById('telemetry-hud'),
        hudFrames: document.getElementById('hud-frames'),
        hudFps: document.getElementById('hud-fps'),
        hudTime: document.getElementById('hud-time')
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
    // 3. UTILITY & UI HANDLERS
    // =========================================================================

    /**
     * Resets the temporal production workspace to its initial state.
     * Localized status messages are retrieved from the I18nEngine.
     */
    const resetWorkspace = () => {
        // 1. Sanitize Result Viewport with localized placeholder
        ui.dynamicContentViewport.innerHTML = ` 
            <div style="color: rgba(255,255,255,0.02); font-family: var(--font-code); font-size: 2.5rem; font-weight: 800; user-select: none; letter-spacing: 10px;">
                WAITING FOR ASSET
            </div>
        `;
        
        // 2. Reactivate and Reset Progress Overlay
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        ui.statusText.innerText = i18n.translate('status_init_motion');

        // 3. Hide previous telemetry
        if (ui.telemetryHud) ui.telemetryHud.classList.add('hidden');
        
        console.log(`PRODUCTION_UI: Temporal workspace sanitized [${i18n.currentLang.toUpperCase()}]`);
    };

    // Standard Slider Synchronization
    const syncSlider = (slider, label) => {
        if (!slider || !label) return;
        slider.oninput = (e) => {
            label.innerText = e.target.value;
        };
    };

    syncSlider(ui.durationSlider, ui.durationVal);
    syncSlider(ui.bucketSlider, ui.bucketVal);
    syncSlider(ui.fpsSlider, ui.fpsVal);

    // =========================================================================
    // 4. CORE WORKFLOWS
    // =========================================================================

    // Still Asset Ingestion
    ui.dropZone.onclick = () => ui.fileInput.click();

    ui.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.dropZone.classList.add('has-file');
            
            const url = URL.createObjectURL(file);
            ui.sourcePreview.innerHTML = `
                <span class="viewport-label" data-i18n="lab_viewport_source">${i18n.translate('lab_viewport_source')}</span>
                <img src="${url}" style="width:100%; height:100%; object-fit:contain;">
            `;
            console.log("PRODUCTION_VIDEO: Still asset synchronized for temporal expansion.");
        }
    };

    // Temporal Fusion (Main Animation Task)
    ui.btnAnimate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert(i18n.translate('alert_no_still'));
            return;
        }

        resetWorkspace(); 

        state.isProcessing = true;

        // Toggle UI state to FUSING
        ui.btnAnimate.disabled = true;
        ui.btnAnimate.innerText = i18n.translate('btn_fusing');
        
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");
        formData.append('motion_prompt', ui.motionPrompt.value);
        formData.append('duration_frames', ui.durationSlider.value);
        formData.append('fps', ui.fpsSlider.value);
        formData.append('motion_bucket', ui.bucketSlider.value);

        const data = await postToGateway('/animate', formData);
        
        if (data && data.task_id) {
            state.lastTaskId = data.task_id;

            pollNeuralTask(data.task_id, 
                // Progress Telemetry Callback
                (progress) => {
                    ui.progressBar.style.width = `${progress.percent}%`;
                    const msg = progress.status_text.replace(/_/g, ' ');
                    ui.statusText.innerText = `${msg} [${progress.percent}%]`;
                }, 
                // Final Delivery Callback
                (result) => {
                    state.isProcessing = false;

                    // Restore UI state
                    ui.btnAnimate.disabled = false;
                    ui.btnAnimate.innerText = i18n.translate('btn_initiate_motion');
                    ui.progressOverlay.classList.add('hidden');
                    
                    if (result && result.video_b64) {
                        ui.dynamicContentViewport.innerHTML = `
                            <video autoplay loop muted controls style="width:100%; height:100%; object-fit:contain; border-radius:12px; z-index:5; position:relative;">
                                <source src="data:video/mp4;base64,${result.video_b64}" type="video/mp4">
                            </video>
                            <button id="btn-save-vid" class="btn btn-primary" style="position:absolute; bottom:20px; right:20px; z-index:10; font-size:0.75rem; padding:10px 20px;">🎬 SAVE MP4</button>
                        `;

                        // Update HUD with Production Telemetry
                        if (result.metrics) {
                            ui.hudFrames.innerText = result.metrics.total_frames;
                            ui.hudFps.innerText = result.metrics.fps;
                            ui.hudTime.innerText = result.metrics.inference_time.toFixed(1) + "s";
                            ui.telemetryHud.classList.remove('hidden');
                        }

                        document.getElementById('btn-save-vid').onclick = () => {
                            const link = document.createElement('a');
                            link.href = `data:video/mp4;base64,${result.video_b64}`;
                            link.download = `z_animation_${Date.now()}.mp4`;
                            link.click();
                        };
                    }
                }
            );
        } else {
            state.isProcessing = false;
            ui.btnAnimate.disabled = false;
            ui.btnAnimate.innerText = i18n.translate('btn_initiate_motion');
            ui.progressOverlay.classList.add('hidden');
        }
    };
});