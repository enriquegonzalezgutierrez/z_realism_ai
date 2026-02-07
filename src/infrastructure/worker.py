# path: z_realism_ai/src/infrastructure/worker.py
# description: Optimized Research Worker v16.2.
#              FEATURING: Granular Lifecycle Telemetry (Cold Start vs Active Synthesis).
#              FEATURING: Real-time transmission of latent previews for PhD visibility.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import os
import io
import base64
import torch
from celery import Celery
from PIL import Image

# Infrastructure Imports
from src.application.use_cases import TransformCharacterUseCase
from src.infrastructure.sd_generator import StableDiffusionGenerator
from src.infrastructure.evaluator import ComputerVisionEvaluator

# --- CELERY INFRASTRUCTURE SETUP ---
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://z-realism-broker:6379/0")

celery_app = Celery("z_realism_worker", broker=BROKER_URL, backend=RESULT_BACKEND)
celery_app.conf.update(
    task_track_started=True, 
    worker_prefetch_multiplier=1, # Strict serial processing to protect 6GB VRAM
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

# SINGLETON: Persists the Neural Engine in memory to avoid repeated loading
_use_case_instance = None

def get_use_case(task_instance):
    """
    Lazy initialization of the Neural Engine with real-time status updates.
    This manages the 'Cold Start' phase (loading ~10GB of models).
    """
    global _use_case_instance
    if _use_case_instance is None:
        # Emit 'LOADING_MODELS' status to inform the UI of the 30-40s delay
        task_instance.update_state(
            state='PROGRESS', 
            meta={'percent': 0, 'status_text': 'LOADING_MODELS'}
        )
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"WORKER_SYSTEM: Initiating Cold Start on {device}...")
        
        evaluator = ComputerVisionEvaluator()
        generator = StableDiffusionGenerator(device=device)
        _use_case_instance = TransformCharacterUseCase(generator, evaluator)
        
    return _use_case_instance

@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(self, image_b64, character_name, feature_prompt, resolution_anchor, hyper_params):
    """
    Asynchronous synthesis pipeline with granular state reporting.
    """
    total_steps = int(hyper_params.get("steps", 30))

    def on_progress(current, total=total_steps, preview_b64=None):
        """
        Internal callback to update Redis with current denoising progress.
        """
        pct = min(max(int((current / total) * 100), 0), 100)
        
        self.update_state(
            state='PROGRESS', 
            meta={
                'percent': pct,
                'preview_b64': preview_b64,
                'status_text': 'SYNTHESIZING' # Active computation state
            }
        )

    try:
        # Phase 1: Task Initialization
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'INITIALIZING'})
        
        # Phase 2: Image Reconstruction
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # Phase 3: Engine Warmup (Handles Cold Start if necessary)
        use_case = get_use_case(self)
        
        # Phase 4: Hardware Allocation
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'ALLOCATING_VRAM'})

        # Phase 5: Neural Synthesis Execution
        result_pil, report = use_case.execute(
            image_file=source_pil, 
            character_name=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            callback=on_progress # Linked to on_progress above
        )

        # Phase 6: Result Serialization
        buffered = io.BytesIO()
        result_pil.save(buffered, format="PNG")
        
        return {
            "result_image_b64": base64.b64encode(buffered.getvalue()).decode('utf-8'),
            "metrics": {
                "structural_similarity": report.structural_similarity,
                "identity_preservation": report.identity_preservation,
                "inference_time": report.inference_time,
                "is_mock": report.is_mock,
                "full_prompt": report.full_prompt,
                "negative_prompt": report.negative_prompt
            }
        }
    except Exception as e:
        print(f"WORKER_TASK_FAILURE: {str(e)}")
        raise e