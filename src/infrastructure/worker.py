# path: z_realism_ai/src/infrastructure/worker.py
# description: Celery Worker v16.0 - Live Telemetry Edition.
#              FEATURING: Real-time transmission of latent previews.
#              FIXED: Removed double-loading by disabling pre-warmup.
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
    worker_prefetch_multiplier=1, # Strict serial processing for 6GB VRAM
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

# SINGLETON: Ensures the engine stays in memory after first use to avoid reload overhead
_use_case_instance = None

def get_use_case():
    """
    Lazy initialization of the Neural Engine.
    Loads the full Master Engine (Dual ControlNet + Shielded IP-Adapter) on first use.
    """
    global _use_case_instance
    if _use_case_instance is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"WORKER_SYSTEM: Deploying Neural Engine on {device}...")
        
        evaluator = ComputerVisionEvaluator()
        generator = StableDiffusionGenerator(device=device)
        _use_case_instance = TransformCharacterUseCase(generator, evaluator)
        
    return _use_case_instance

@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(self, image_b64, character_name, feature_prompt, resolution_anchor, hyper_params):
    """
    Asynchronous synthesis pipeline with Live Telemetry support.
    """
    total_steps = int(hyper_params.get("steps", 30))

    def on_progress(current, total=total_steps, preview_b64=None):
        """
        Updates the task state in Redis with the current percentage 
        and an optional low-resolution preview image.
        """
        pct = min(max(int((current / total) * 100), 0), 100)
        
        # We store the metadata including the intermediate image
        self.update_state(
            state='PROGRESS', 
            meta={
                'percent': pct,
                'preview_b64': preview_b64 # Transmitted to the frontend
            }
        )

    try:
        # 1. Image De-serialization
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # 2. Use Case Execution
        use_case = get_use_case()
        result_pil, report = use_case.execute(
            image_file=source_pil, 
            character_name=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            callback=on_progress # Linked to the telemetry function
        )

        # 3. Final Result Packaging
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