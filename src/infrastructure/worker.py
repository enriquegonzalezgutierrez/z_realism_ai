# path: z_realism_ai/src/infrastructure/worker.py
# description: Distributed Inference Worker v19.0 - Multi-Modal Orchestration.
#
# ABSTRACT:
# This module implements the asynchronous processing consumer for the Z-Realism 
# ecosystem. It manages two primary pipelines: Static Image Transformation 
# and Temporal Video Animation. 
#
# ARCHITECTURAL FEATURES:
# 1. Dual-Singleton Architecture: Implements lazy-loading for both the 
#    Static Generator and the Video Generator to optimize VRAM/RAM lifecycle.
# 2. VRAM Safety: Coordinated with the API Gateway's Redis Mutex to ensure 
#    the GTX 1060 (6GB) is never over-allocated.
# 3. Temporal Telemetry: Provides real-time progress updates for multi-frame 
#    synthesis (Video).
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import os
import io
import base64
import torch
import time
from celery import Celery
from PIL import Image

# Domain & Infrastructure Layer Imports
from src.application.use_cases import TransformCharacterUseCase
from src.infrastructure.sd_generator import StableDiffusionGenerator
from src.infrastructure.video_generator import StableVideoAnimateDiffGenerator
from src.infrastructure.evaluator import ComputerVisionEvaluator

# --- 1. CELERY INFRASTRUCTURE CONFIGURATION ---
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://z-realism-broker:6379/0")

celery_app = Celery("z_realism_worker", broker=BROKER_URL, backend=RESULT_BACKEND)

celery_app.conf.update(
    task_track_started=True, 
    worker_prefetch_multiplier=1, # Strict hardware single-tenancy
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

# --- 2. SINGLETON INITIALIZATION (Lazy Loading) ---
_use_case_instance = None
_video_gen_instance = None

def get_use_case(task_instance):
    """Retrieves or initializes the Static Image Case singleton."""
    global _use_case_instance
    if _use_case_instance is None:
        task_instance.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'LOADING_IMAGE_MODELS'})
        device = "cuda" if torch.cuda.is_available() else "cpu"
        evaluator = ComputerVisionEvaluator()
        generator = StableDiffusionGenerator(device=device)
        _use_case_instance = TransformCharacterUseCase(generator, evaluator)
    return _use_case_instance

def get_video_generator(task_instance):
    """Retrieves or initializes the Video Animation Generator singleton."""
    global _video_gen_instance
    if _video_gen_instance is None:
        task_instance.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'LOADING_TEMPORAL_MODELS'})
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # The Video Generator is specifically tuned for 6GB VRAM offloading
        _video_gen_instance = StableVideoAnimateDiffGenerator(device=device)
    return _video_gen_instance

# --- 3. TASK DEFINITIONS ---

@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(self, image_b64, character_name, feature_prompt, resolution_anchor, hyper_params):
    """Orchestrates the Image-to-Image photorealism pipeline."""
    total_steps = int(hyper_params.get("steps", 30))

    def on_progress(current, total=total_steps, preview_b64=None):
        pct = min(max(int((current / total) * 100), 0), 100)
        self.update_state(state='PROGRESS', meta={'percent': pct, 'preview_b64': preview_b64, 'status_text': 'SYNTHESIZING_IMAGE'})

    try:
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'INITIALIZING'})
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        use_case = get_use_case(self)

        result_pil, report = use_case.execute(
            image_file=source_pil, 
            character_name=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            callback=on_progress
        )

        self.update_state(state='PROGRESS', meta={'percent': 100, 'status_text': 'FINALIZING'})
        time.sleep(0.5) 

        buffered = io.BytesIO()
        result_pil.save(buffered, format="PNG")
        
        return {
            "result_image_b64": base64.b64encode(buffered.getvalue()).decode('utf-8'),
            "metrics": {
                "structural_similarity": report.structural_similarity,
                "identity_preservation": report.identity_preservation,
                "textural_realism": report.textural_realism,
                "inference_time": report.inference_time,
                "full_prompt": report.full_prompt
            }
        }
    except Exception as e:
        print(f"WORKER_IMAGE_FAILURE: {str(e)}")
        raise e

@celery_app.task(name="animate_character_task", bind=True)
def animate_character_task(self, image_b64, character_name, video_params):
    """Orchestrates the Temporal (Video) synthesis pipeline."""
    
    def on_progress(current, total, status_msg="ANIMATING"):
        pct = min(max(int((current / total) * 100), 0), 100)
        self.update_state(state='PROGRESS', meta={'percent': pct, 'status_text': status_msg})

    try:
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'DECODING_SOURCE'})
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # Load Video Generator (Supports Sequential CPU Offloading)
        video_gen = get_video_generator(self)
        
        # Note: In a production DDD environment, this would go through a Use Case.
        # For this implementation, we call the Infrastructure Generator directly.
        report = video_gen.animate_image(
            source_image=source_pil,
            motion_prompt=video_params.get("motion_prompt"),
            character_lore={"name": character_name}, # Simplified lore link
            duration_frames=video_params.get("duration_frames", 24),
            fps=video_params.get("fps", 8),
            hyper_params=video_params,
            progress_callback=on_progress
        )

        self.update_state(state='PROGRESS', meta={'percent': 100, 'status_text': 'ENCODING_VIDEO'})
        time.sleep(0.5)

        return {
            "video_b64": report.video_b64,
            "metrics": {
                "inference_time": report.inference_time,
                "total_frames": report.total_frames,
                "fps": report.fps
            }
        }
    except Exception as e:
        print(f"WORKER_VIDEO_FAILURE: {str(e)}")
        raise e