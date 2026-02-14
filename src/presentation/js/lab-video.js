/**
 * path: src/presentation/js/lab-video.js
 * description: Temporal Motion Production Controller v1.0 - Commercial Product.
 * 
 * ABSTRACT:
 * Orchestrates the Image-to-Video neural pipeline. This version ensures 
 * that production feedback and asset intelligence are streamlined for 
 * commercial users.
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
     * Ensures previous video results are cleared and feedback overlays are reset.
     */
    const resetWorkspace = () => {
        // 1. Sanitize ONLY the dynamic content viewport
        // FIX: Ensure to target dynamic-content-viewport, not resultDisplay for innerHTML
        ui.dynamicContentViewport.innerHTML = ` 
            <div style="color: rgba(255,255,255,0.02); font-family: var(--font-code); font-size: 2.5rem; font-weight: 800; user-select: none; letter-spacing: 10px;">
                WAITING FOR ASSET
            </div>
        `;
        
        // 2. Reactivate and Reset Progress Overlay
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        ui.statusText.innerText = "INITIALIZING MOTION ENGINE..."; // Updated text

        if (ui.telemetryHud) ui.telemetryHud.classList.add('hidden');
        
        console.log("PRODUCTION_UI: Temporal workspace sanitized for new motion task."); // Updated log
    };

    // Slider Synchronization remains the same.
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

    // File Handling
    ui.dropZone.onclick = () => ui.fileInput.click();

    ui.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.dropZone.classList.add('has-file');
            
            const url = createPreviewURL(file);
            ui.sourcePreview.innerHTML = `
                <span class="viewport-label">SOURCE_STILL_INPUT</span> {/* Updated text */}
                <img src="${url}" style="width:100%; height:100%; object-fit:contain;">
            `;
            console.log("PRODUCTION_VIDEO: Still asset loaded for motion expansion."); // Updated log
        }
    };

    // Temporal Fusion (Main Animation Task)
    ui.btnAnimate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert("SYSTEM_ERROR: Please upload a source still asset first."); // Updated text
            return;
        }

        // --- STATE RESET PROTOCOL ---
        resetWorkspace(); 

        state.isProcessing = true;
        ui.btnAnimate.disabled = true;
        ui.btnAnimate.innerText = "INITIATING MOTION..."; // Updated text
        
        // Construct Temporal Asset Payload
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

            // Start Polling Loop for temporal status
            pollNeuralTask(data.task_id, 
                // Progress Callback
                (progress) => {
                    ui.progressBar.style.width = `${progress.percent}%`;
                    const msg = progress.status_text.replace(/_/g, ' ');
                    ui.statusText.innerText = `${msg} [${progress.percent}%]`;
                }, 
                // Completion Callback
                (result) => {
                    state.isProcessing = false;
                    ui.btnAnimate.disabled = false;
                    ui.btnAnimate.innerText = "INITIATE MOTION PRODUCTION"; // Updated text
                    ui.progressOverlay.classList.add('hidden');
                    
                    if (result && result.video_b64) {
                        const viewport = ui.resultDisplay.querySelector('#dynamic-content-viewport');
                        viewport.innerHTML = `
                            <video autoplay loop muted controls style="width:100%; height:100%; object-fit:contain; border-radius:12px; z-index:5; position:relative;">
                                <source src="data:video/mp4;base64,${result.video_b64}" type="video/mp4">
                            </video>
                            <button id="btn-save-vid" class="btn btn-primary" style="position:absolute; bottom:20px; right:20px; z-index:10; font-size:0.75rem; padding:10px 20px;">🎬 SAVE MP4</button>
                        `;

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
                    } else {
                        console.error("PRODUCTION_VIDEO: Motion synthesis error. Consult backend telemetry."); // Updated log
                    }
                }
            );
        } else {
            state.isProcessing = false;
            ui.btnAnimate.disabled = false;
            ui.btnAnimate.innerText = "INITIATE MOTION PRODUCTION"; // Updated text
            ui.progressOverlay.classList.add('hidden');
        }
    };
});