/**
 * path: src/presentation/js/lab-video.js
 * description: Temporal Fusion Controller v21.9 - State Management Fix.
 * 
 * ABSTRACT:
 * Orchestrates the Image-to-Video neural pipeline. This version introduces 
 * a robust State Reset Protocol to ensure the temporal workspace is 
 * sanitized before each new animation synthesis task.
 *
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. UI ELEMENT MAPPING
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
        statusText: document.getElementById('status-text')
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
     * Resets the temporal laboratory workspace to its initial state.
     * CRITICAL FIX: Clears previous video results and resets the progress overlay.
     */
    const resetWorkspace = () => {
        // 1. Sanitize Result Viewport
        ui.resultDisplay.innerHTML = `
            <span class="viewport-label">TEMPORAL_OUTPUT_MONITOR</span>
            <div style="color: rgba(255,255,255,0.02); font-family: var(--font-code); font-size: 2.5rem; font-weight: 800; user-select: none; letter-spacing: 10px;">
                WAITING
            </div>
        `;
        // Ensure the background placeholder is visible again, handled by CSS .temporal-lab .viewport-card#result-display
        
        // 2. Reactivate and Reset Telemetry Overlay
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        ui.statusText.innerText = "INITIALIZING...";
        
        console.log("LAB_UI: Temporal workspace sanitized for new animation task.");
    };

    // Slider Synchronization
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
                <span class="viewport-label">STILL_INPUT_MANIFOLD</span>
                <img src="${url}" style="width:100%; height:100%; object-fit:contain;">
            `;
            console.log("LAB_VIDEO: Still manifold loaded for temporal expansion.");
        }
    };

    // Temporal Fusion (Main Animation Task)
    ui.btnAnimate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert("SYSTEM_ERROR: Please load a generated subject still first.");
            return;
        }

        // --- STATE RESET PROTOCOL ---
        resetWorkspace(); 

        // Initialize UI for temporal synthesis (long latency)
        state.isProcessing = true;
        ui.btnAnimate.disabled = true;
        ui.btnAnimate.innerText = "ANIMATING...";
        
        // Construct Temporal Manifold Payload
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
                    ui.btnAnimate.innerText = "INITIATE TEMPORAL FUSION";
                    ui.progressOverlay.classList.add('hidden');
                    
                    if (result && result.video_b64) {
                        ui.resultDisplay.innerHTML = `
                            <span class="viewport-label">TEMPORAL_OUTPUT_MONITOR</span>
                            <video autoplay loop muted controls style="width:100%; height:100%; object-fit:contain; border-radius:12px; z-index:5; position:relative;">
                                <source src="data:video/mp4;base64,${result.video_b64}" type="video/mp4">
                            </video>
                            <button id="btn-save-vid" class="btn btn-primary" style="position:absolute; bottom:20px; right:20px; z-index:10; font-size:0.75rem; padding:10px 20px;">🎬 SAVE MP4</button>
                            <div class="metrics-overlay" style="position:absolute; bottom:20px; left:20px; font-family:var(--font-code); font-size:0.65rem; color:rgba(255,255,255,0.5); z-index:6; background:rgba(0,0,0,0.4); padding:5px 10px; border-radius:4px;">
                                TOTAL_FRAMES: ${result.metrics.total_frames} | 
                                FPS: ${result.metrics.fps} | 
                                INF_TIME: ${result.metrics.inference_time}s
                            </div>
                        `;
                        document.getElementById('btn-save-vid').onclick = () => {
                            const link = document.createElement('a');
                            link.href = `data:video/mp4;base64,${result.video_b64}`;
                            link.download = `z_animation_${Date.now()}.mp4`;
                            link.click();
                        };
                    } else {
                        console.error("LAB_VIDEO: Synthesis error. Consult worker telemetry.");
                    }
                }
            );
        } else {
            state.isProcessing = false;
            ui.btnAnimate.disabled = false;
            ui.btnAnimate.innerText = "INITIATE TEMPORAL FUSION";
            ui.progressOverlay.classList.add('hidden');
        }
    };
});