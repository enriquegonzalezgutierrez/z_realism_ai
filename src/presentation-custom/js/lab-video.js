/**
 * path: src/presentation-custom/js/lab-video.js
 * description: Logic for the Temporal Fusion Laboratory v20.2.
 * 
 * ABSTRACT:
 * Orchestrates the Image-to-Video neural pipeline. Manages motion 
 * guidance parameters and video container rendering.
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. UI ELEMENT MAPPING ---
    const ui = {
        charName: document.getElementById('char-name'),
        fileInput: document.getElementById('file-upload'),
        dropZone: document.getElementById('drop-zone'),
        motionPrompt: document.getElementById('motion-prompt'),
        
        // Temporal Sliders
        durationSlider: document.getElementById('input-duration'),
        durationVal: document.getElementById('val-duration'),
        bucketSlider: document.getElementById('input-bucket'),
        bucketVal: document.getElementById('val-bucket'),
        fpsSlider: document.getElementById('input-fps'),
        fpsVal: document.getElementById('val-fps'),
        
        btnAnimate: document.getElementById('btn-animate'),
        
        // Viewports
        sourcePreview: document.getElementById('source-preview'),
        resultDisplay: document.getElementById('result-display'),
        
        // Progress Overlay
        progressOverlay: document.getElementById('progress-overlay'),
        progressBar: document.getElementById('progress-bar'),
        statusText: document.getElementById('status-text')
    };

    let state = {
        selectedFile: null,
        isProcessing: false
    };

    // --- 2. FILE HANDLING ---
    ui.dropZone.onclick = () => ui.fileInput.click();

    ui.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            state.selectedFile = file;
            ui.dropZone.classList.add('has-file');
            
            // Show Source Still
            const url = createPreviewURL(file);
            ui.sourcePreview.innerHTML = `
                <span class="viewport-label">SOURCE_STILL_MANIFOLD</span>
                <img src="${url}" style="width:100%; height:100%; object-fit:contain;">
            `;
        }
    };

    // --- 3. TEMPORAL FUSION WORKFLOW ---
    ui.btnAnimate.onclick = async () => {
        if (!state.selectedFile || state.isProcessing) {
            alert("Please upload a generated still first.");
            return;
        }

        // Initialize UI State
        state.isProcessing = true;
        ui.btnAnimate.disabled = true;
        ui.btnAnimate.innerText = "ANIMATING...";
        ui.progressOverlay.classList.remove('hidden');
        ui.progressBar.style.width = '0%';
        ui.resultDisplay.innerHTML = '<span class="viewport-label">TEMPORAL_MONITOR_ACTIVE</span>';

        // Collect Manifold Parameters
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('character_name', ui.charName.value || "Unknown");
        formData.append('motion_prompt', ui.motionPrompt.value);
        formData.append('duration_frames', ui.durationSlider.value);
        formData.append('fps', ui.fpsSlider.value);
        formData.append('motion_bucket', ui.bucketSlider.value);

        // Dispatch to Neural Gateway
        const data = await postToGateway('/animate', formData);
        
        if (data && data.task_id) {
            pollNeuralTask(data.task_id, 
                // On Progress Update
                (progress) => {
                    ui.progressBar.style.width = `${progress.percent}%`;
                    // Prettify status for the UI (e.g. "DECODING_VAE" -> "Decoding Vae")
                    const msg = progress.status_text.replace(/_/g, ' ');
                    ui.statusText.innerText = `${msg} [${progress.percent}%]`;
                }, 
                // On Task Completion
                (result) => {
                    state.isProcessing = false;
                    ui.btnAnimate.disabled = false;
                    ui.btnAnimate.innerText = "INITIATE TEMPORAL FUSION";
                    ui.progressOverlay.classList.add('hidden');
                    
                    if (result && result.video_b64) {
                        // Render the high-performance video container
                        ui.resultDisplay.innerHTML = `
                            <span class="viewport-label">TEMPORAL_MONITOR_ACTIVE</span>
                            <video autoplay loop muted controls style="width:100%; height:100%; object-fit:contain; border-radius:12px;">
                                <source src="data:video/mp4;base64,${result.video_b64}" type="video/mp4">
                            </video>
                            <button id="btn-download-vid" class="btn btn-primary" style="position:absolute; bottom:20px; right:20px; z-index:10; font-size:0.7rem; padding:8px 15px;">🎬 SAVE MP4</button>
                        `;
                        
                        // Setup Download Logic
                        document.getElementById('btn-download-vid').onclick = () => {
                            const link = document.createElement('a');
                            link.href = `data:video/mp4;base64,${result.video_b64}`;
                            link.download = `z_anim_${Date.now()}.mp4`;
                            link.click();
                        };
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

    // --- 4. SLIDER SYNCHRONIZATION ---
    ui.durationSlider.oninput = (e) => ui.durationVal.innerText = e.target.value;
    ui.bucketSlider.oninput = (e) => ui.bucketVal.innerText = e.target.value;
    ui.fpsSlider.oninput = (e) => ui.fpsVal.innerText = e.target.value;
});