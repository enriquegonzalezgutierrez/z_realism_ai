# path: z_realism_ai/src/infrastructure/worker.py
# description: Celery Worker with updated progress logic for SDXL (30 steps).
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import os
import io
import base64
import torch
import asyncio
from celery import Celery
from PIL import Image

# Import DDD layers
from src.application.use_cases import TransformCharacterUseCase
from src.infrastructure.sd_generator import StableDiffusionGenerator
from src.infrastructure.mock_generator import MockImageGenerator

# -----------------------------------------------------------------------------
# Celery Configuration
# -----------------------------------------------------------------------------
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://z-realism-broker:6379/0")

celery_app = Celery("z_realism_worker", broker=BROKER_URL, backend=RESULT_BACKEND)
celery_app.conf.update(task_track_started=True, worker_prefetch_multiplier=1)

# -----------------------------------------------------------------------------
# AI Engine Singleton
# -----------------------------------------------------------------------------
_use_case_instance = None

def get_use_case():
    """Lazy initializer for the SDXL Engine."""
    global _use_case_instance
    if _use_case_instance is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            generator = StableDiffusionGenerator(device=device)
        except Exception as e:
            print(f"WORKER_AI_ERROR: {e}")
            generator = MockImageGenerator()
        _use_case_instance = TransformCharacterUseCase(generator)
    return _use_case_instance

# -----------------------------------------------------------------------------
# Background Task with SDXL Parameters
# -----------------------------------------------------------------------------

@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(
    self, 
    image_b64: str, 
    character_name: str, 
    feature_prompt: str, 
    resolution_anchor: int
):
    """
    SDXL Worker task that executes the transformation and sends safe progress updates.
    """
    
    # SDXL standard step count for quality generation
    SDXL_TOTAL_STEPS = 30 

    def on_safe_progress(current, total=SDXL_TOTAL_STEPS):
        """Calculates and clamps percentage."""
        # We always report total steps as 30 for the UI to be stable
        raw_pct = int((current / total) * 100) if total > 0 else 0
        safe_pct = max(0, min(100, raw_pct))
        
        self.update_state(
            state='PROGRESS',
            meta={
                'current': current, 
                'total': SDXL_TOTAL_STEPS, 
                'percent': safe_pct,
                'status_msg': f"SDXL Synthesis Step {current} of {SDXL_TOTAL_STEPS}"
            }
        )

    try:
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        use_case = get_use_case()

        # Process with SDXL parameters
        result_pil = asyncio.run(use_case.execute(
            image_file=source_pil, 
            character_name=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            callback=on_safe_progress
        ))

        buffered = io.BytesIO()
        result_pil.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    except Exception as e:
        print(f"WORKER_LOG_ERROR: {str(e)}")
        raise e