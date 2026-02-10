/**
 * path: src/presentation/js/lab-video.js
 * description: Temporal Fusion Controller v21.2 - Neural Video Research Lab.
 * 
 * ABSTRACT:
 * Orchestrates the neural transformation of static photorealistic manifolds into 
 * cinematic temporal sequences. This script manages the Image-to-Video 
 * research workspace, coordinates asynchronous temporal tasks, and 
 * handles the preservation of generated video candidates.
 *
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as the Primary Controller for the Temporal Fusion hub. 
 * It interfaces with the FastAPI gateway's specialized animation endpoints 
 * and provides frame-accurate telemetry during inference.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. UI ELEMENT MAPPING (Temporal Control Manifold)
    // =========================================================================
    const ui = {
        // Identity & Guidance
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
        
        // Neural Viewports (Workspaces)
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
    // 3. UI INTERACTION LOGIC (SLIDER SYNC)
    // =========================================================================

    /**
     * Utility to synchronize range sliders with their numeric value displays.
     */
    const syncSlider = (slider, label) => {
        if (!slider || !label) return;
        slider.oninput = (e) => {
            label.innerText = e.target.value;
        };
    };

    // Synchronize Laboratory Instrumentation
    syncSlider(ui.durationSlider, ui.durationVal);
    syncSlider(ui.bucketSlider, ui.bucketVal);
    syncSlider(ui.fpsSlider, ui.fpsVal);

    // =========================================================================
    // 4. DATA INGESTION (STILL IMAGE LOADING)
    // =========================================================================

    ui.dropZone.onclick = () => ui.fileInput.click();

    ui.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.dropZone.classList.add('has-file');
            
            // Render the source still manifold in the input viewport
            const url = URL.createObjectURL(file);
            ui.sourcePreview.innerHTML = `
                <span class="viewport-label">STILL_INPUT_MANIFOLD</span>
                <img src="${url}" style="width:100%; height:100%; object-fit:contain; animation: fadeIn 0.5s ease-out;">
            `;
            console.log("LAB_VIDEO: Still manifold loaded for temporal expansion.");
        }
    };

    // =========================================================================
    // 5. TEMPORAL FUSION WORKFLOW (INFERENCE)
    // =========================================================================

    /**
     * Dispatches the Image-to-Video task to the CUDA orchestrator.
     * Manages high-latency telemetry for sequential weight offloading.
     */
    ui.btnAnimate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert("SYSTEM_ERROR: Please load a generated subject still first.");
            return;
        }

        // 1. Initialize UI for temporal synthesis (long latency)
        state.isProcessing = true;
        ui.btnAnimate.disabled = true;
        ui.btnAnimate.innerText = "ANIMATING...";
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        
        // Reset output monitor label
        ui.resultDisplay.innerHTML = '<span class="viewport-label">TEMPORAL_MONITOR_ACTIVE</span>';

        // 2. Construct Temporal Manifold Payload
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");
        formData.append('motion_prompt', ui.motionPrompt.value);
        formData.append('duration_frames', ui.durationSlider.value);
        formData.append('fps', ui.fpsSlider.value);
        formData.append('motion_bucket', ui.bucketSlider.value);

        // 3. Dispatch to Neural Gateway (api.js)
        const data = await postToGateway('/animate', formData);
        
        if (data && data.task_id) {
            state.lastTaskId = data.task_id;

            // 4. Start Polling Loop for temporal status
            pollNeuralTask(data.task_id, 
                // PROGRESS: Frame-accurate telemetry
                (progress) => {
                    ui.progressBar.style.width = `${progress.percent}%`;
                    
                    // Prettify message (e.g., "ENCODING_VIDEO" -> "Encoding Video")
                    const msg = progress.status_text.replace(/_/g, ' ');
                    ui.statusText.innerText = `${msg} [${progress.percent}%]`;
                }, 
                // SUCCESS: Final MP4 Rendering
                (result) => {
                    state.isProcessing = false;
                    ui.btnAnimate.disabled = false;
                    ui.btnAnimate.innerText = "INITIATE TEMPORAL FUSION";
                    ui.progressOverlay.classList.add('hidden');
                    
                    if (result && result.video_b64) {
                        // Success: Inject high-performance cinematic video loop
                        ui.resultDisplay.innerHTML = `
                            <span class="viewport-label">TEMPORAL_MONITOR_ACTIVE</span>
                            
                            <video autoplay loop muted controls style="width:100%; height:100%; object-fit:contain; border-radius:12px; z-index:5; position:relative;">
                                <source src="data:video/mp4;base64,${result.video_b64}" type="video/mp4">
                            </video>
                            
                            <!-- Result Preservation -->
                            <button id="btn-save-vid" class="btn btn-primary" style="position:absolute; bottom:20px; right:20px; z-index:10; font-size:0.75rem; padding:10px 20px;">🎬 SAVE MP4</button>
                            
                            <!-- Telemetry Analytics -->
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
            // Failure fallback
            state.isProcessing = false;
            ui.btnAnimate.disabled = false;
            ui.btnAnimate.innerText = "INITIATE TEMPORAL FUSION";
            ui.progressOverlay.classList.add('hidden');
        }
    };
});