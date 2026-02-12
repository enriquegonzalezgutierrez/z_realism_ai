# path: src/infrastructure/worker.py
# description: Distributed Inference Worker v22.0 - Doctoral Thesis Candidate.
#              FIXED: Temporal task now correctly invokes AnimateCharacterUseCase.
#
# ARCHITECTURAL ROLE (Infrastructure Layer):
# This component acts as the primary computational node. It manages the 
# lifecycle of the GPU and implements the "Context-Aware Resource Management" 
# pattern to support multi-modal inference on limited hardware (6GB VRAM).
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import os
import io
import base64
import torch
import time
import gc 
from celery import Celery
from PIL import Image

# Domain & Application Layer Imports
from src.application.use_cases import TransformCharacterUseCase, AnimateCharacterUseCase # <-- Added AnimateCharacterUseCase
from src.infrastructure.sd_generator import StableDiffusionGenerator
from src.infrastructure.video_generator import StableVideoAnimateDiffGenerator
from src.infrastructure.evaluator import ComputerVisionEvaluator
from src.infrastructure.analyzer import HeuristicImageAnalyzer # <-- Added HeuristicImageAnalyzer

# --- CELERY INFRASTRUCTURE CONFIGURATION ---
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://z-realism-broker:6379/0")

celery_app = Celery("z_realism_worker", broker=BROKER_URL, backend=RESULT_BACKEND)

celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1, 
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

# --- GLOBAL STATE FOR RESOURCE ORCHESTRATION ---
_current_model_instance = None
_current_model_type = None  # ENUM: 'STATIC' | 'TEMPORAL'

def manage_hardware_resources(target_type: str):
    """
    Hybrid Resource Manager.
    
    Dynamically adapts the worker's memory profile based on the incoming 
    neural task. It implements a "Warm Start" cache for identical task types 
    and a "Deep Purge" for context switches.
    """
    global _current_model_instance, _current_model_type

    if _current_model_instance is not None and _current_model_type == target_type:
        print(f"WORKER_SYS: Manifold Hit. Reusing {target_type} engine.")
        return _current_model_instance

    if _current_model_instance is not None:
        print(f"WORKER_SYS: Context Switch ({_current_model_type} -> {target_type}).")
        del _current_model_instance
        _current_model_instance = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            print(f"WORKER_SYS: CUDA VRAM Purged.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"WORKER_SYS: Deploying {target_type} engine on [{device.upper()}]...")

    if target_type == 'STATIC':
        evaluator = ComputerVisionEvaluator()
        generator = StableDiffusionGenerator(device=device)
        _current_model_instance = TransformCharacterUseCase(generator, evaluator)
        _current_model_type = 'STATIC'
        
    elif target_type == 'TEMPORAL':
        # --- CRITICAL FIX: Instantiate AnimateCharacterUseCase ---
        # This ensures the Analyzer is called and Subject DNA is injected.
        video_generator = StableVideoAnimateDiffGenerator(device=device)
        analyzer = HeuristicImageAnalyzer() # Instantiate the analyzer
        _current_model_instance = AnimateCharacterUseCase(video_generator, analyzer)
        _current_model_type = 'TEMPORAL'

    return _current_model_instance

# --- ASYNCHRONOUS TASK DEFINITIONS ---

@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(self, image_b64, character_name, feature_prompt, resolution_anchor, hyper_params):
    """
    Orchestrates the Image-to-Image static transformation pipeline.
    """
    total_steps = int(hyper_params.get("steps", 30))

    def on_progress(current, total=total_steps, preview_b64=None):
        pct = min(max(int((current / total) * 100), 0), 100)
        self.update_state(state='PROGRESS', meta={
            'percent': pct, 
            'preview_b64': preview_b64, 
            'status_text': 'SYNTHESIZING_IMAGE'
        })

    try:
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'INITIALIZING'})
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        use_case = manage_hardware_resources('STATIC')
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
        print(f"WORKER_ERROR: Static transformation failed. Details: {str(e)}")
        raise e

@celery_app.task(name="animate_character_task", bind=True)
def animate_character_task(self, image_b64, character_name, video_params):
    """
    Orchestrates the Temporal (Video) synthesis pipeline.
    """
    
    def on_progress(current, total, status_msg="ANIMATING"):
        pct = min(max(int((current / total) * 100), 0), 100)
        self.update_state(state='PROGRESS', meta={'percent': pct, 'status_text': status_msg})

    try:
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'DECODING_MANIFOLD'})
        
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # --- CRITICAL FIX: Use the AnimateCharacterUseCase ---
        # This ensures the Analyzer is called and metadata is properly injected.
        use_case = manage_hardware_resources('TEMPORAL')
        
        # The use case will handle fetching metadata and calling the video_generator
        report = use_case.execute(
            image_file=source_pil,
            character_name=character_name,
            video_params=video_params,
            callback=on_progress # Pass the progress callback
        )

        self.update_state(state='PROGRESS', meta={'percent': 100, 'status_text': 'ENCODING_CONTAINER'})
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
        print(f"WORKER_ERROR: Temporal synthesis failed. Details: {str(e)}")
        raise e