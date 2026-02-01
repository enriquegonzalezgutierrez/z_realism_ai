# path: z_realism_ai/src/infrastructure/worker.py
# description: Celery Worker with Multiprocessing Spawn support.
#              FIXED: Added set_start_method('spawn') to allow multiple 
#              AI workers to run in parallel without memory pointer conflicts.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import os
import io
import base64
import torch
import asyncio
import multiprocessing
from celery import Celery
from celery.signals import worker_ready
from PIL import Image

# -----------------------------------------------------------------------------
# PH.D. SCALING FIX: Ensure multiprocessing uses 'spawn' 
# This is critical for Deep Learning models in parallel workers.
# -----------------------------------------------------------------------------
try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    pass

# Import DDD layers
from src.application.use_cases import TransformCharacterUseCase
from src.infrastructure.sd_generator import StableDiffusionGenerator
from src.infrastructure.mock_generator import MockImageGenerator
from src.infrastructure.evaluator import ComputerVisionEvaluator

# -----------------------------------------------------------------------------
# Celery Configuration
# -----------------------------------------------------------------------------
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://z-realism-broker:6379/0")

celery_app = Celery("z_realism_worker", broker=BROKER_URL, backend=RESULT_BACKEND)
celery_app.conf.update(
    task_track_started=True, 
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

_use_case_instance = None

def get_use_case():
    global _use_case_instance
    if _use_case_instance is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        evaluator = ComputerVisionEvaluator()
        try:
            generator = StableDiffusionGenerator(device=device)
            _use_case_instance = TransformCharacterUseCase(generator, evaluator)
        except Exception as e:
            print(f"WORKER_INIT_ERROR: {str(e)}")
            generator = MockImageGenerator()
            _use_case_instance = TransformCharacterUseCase(generator, evaluator)
    return _use_case_instance

@worker_ready.connect
def at_start(sender, **k):
    with sender.app.connection() as conn:
        print("WORKER_SYSTEM: Scalable Warmup initiated...")
        get_use_case()

@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(self, image_b64, character_name, feature_prompt, resolution_anchor):
    SDXL_TOTAL_STEPS = 25 
    def on_safe_progress(current, total=SDXL_TOTAL_STEPS):
        pct = int((current / total) * 100) if total > 0 else 0
        self.update_state(state='PROGRESS', meta={'percent': pct})

    try:
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        use_case = get_use_case()
        result_pil, report = asyncio.run(use_case.execute(
            image_file=source_pil, 
            character_name=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            callback=on_safe_progress
        ))
        buffered = io.BytesIO()
        result_pil.save(buffered, format="PNG")
        final_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return {
            "result_image_b64": final_b64,
            "metrics": {
                "structural_similarity": report.structural_similarity,
                "identity_preservation": report.identity_preservation,
                "inference_time": report.inference_time,
                "is_mock": report.is_mock
            }
        }
    except Exception as e:
        print(f"WORKER_TASK_ERROR: {str(e)}")
        raise e
