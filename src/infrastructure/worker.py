# path: z_realism_ai/src/infrastructure/worker.py
# description: Celery Worker v4.8 with Adaptive Progress Tracking.
#              Optimized for Deep Learning workloads in parallel processes.
#              Supports dynamic step-counts for the new DPM Multistep Scheduler.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import os
import io
import base64
import torch
import multiprocessing
from celery import Celery
from celery.signals import worker_ready
from PIL import Image

# --- Process Architecture Configuration ---
# 'spawn' is mandatory for stable PyTorch/CUDA execution in multi-worker setups.
try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    pass

# Import Hexagonal Layers
from src.application.use_cases import TransformCharacterUseCase
from src.infrastructure.sd_generator import StableDiffusionGenerator
from src.infrastructure.mock_generator import MockImageGenerator
from src.infrastructure.evaluator import ComputerVisionEvaluator

# --- Celery Infrastructure Setup ---
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://z-realism-broker:6379/0")

celery_app = Celery("z_realism_worker", broker=BROKER_URL, backend=RESULT_BACKEND)
celery_app.conf.update(
    task_track_started=True, 
    worker_prefetch_multiplier=1, # One task per worker to protect RAM/VRAM
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

# Use-Case Singleton for Model Persistence
_use_case_instance = None

def get_use_case():
    """
    Lazy initialization of the Neural Engine.
    Keeps weights in memory to avoid reloading overhead per task.
    """
    global _use_case_instance
    if _use_case_instance is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        evaluator = ComputerVisionEvaluator()
        try:
            generator = StableDiffusionGenerator(device=device)
            _use_case_instance = TransformCharacterUseCase(generator, evaluator)
        except Exception as e:
            print(f"WORKER_CRITICAL: AI Engine failed to load. Using Mock fallback. {str(e)}")
            generator = MockImageGenerator()
            _use_case_instance = TransformCharacterUseCase(generator, evaluator)
    return _use_case_instance

@worker_ready.connect
def at_start(sender, **k):
    """Warm up the neural model immediately upon worker initialization."""
    with sender.app.connection() as conn:
        print("WORKER_SYSTEM: Scaling neural weights into memory...")
        get_use_case()

@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(self, image_b64, character_name, feature_prompt, resolution_anchor, hyper_params):
    """
    Asynchronous synthesis pipeline.
    Matches the progress reporting to the dynamic DPM step configuration.
    """
    # Recover dynamic step count for accurate percentage reporting
    dynamic_total_steps = int(hyper_params.get("steps", 30))

    def on_adaptive_progress(current, total=dynamic_total_steps):
        """Calculates and pushes progress updates to the Redis backend."""
        if total <= 0: pct = 0
        else: pct = min(max(int((current / total) * 100), 0), 100)
        self.update_state(state='PROGRESS', meta={'percent': pct})

    try:
        # 1. Input De-serialization
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))

        # 2. Logic Execution
        use_case = get_use_case()
        result_pil, report = use_case.execute(
            image_file=source_pil, 
            character_name=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            callback=on_adaptive_progress
        )

        # 3. Output Serialization
        buffered = io.BytesIO()
        result_pil.save(buffered, format="PNG")
        final_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 4. Success Package
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
        print(f"WORKER_TASK_FAILURE: {str(e)}")
        raise e