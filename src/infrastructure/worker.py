# path: src/infrastructure/worker.py
# description: Distributed Inference Worker v21.4 - Hybrid Hardware Orchestration.
#              Consumes tasks from the Redis Queue and executes Neural Workloads.
#
# ARCHITECTURAL ROLE (Infrastructure Layer):
# This component acts as the primary computational node. It manages the 
# lifecycle of the GPU and implements the "Context-Aware Resource Management" 
# pattern to support multi-modal inference on limited hardware (6GB VRAM).
#
# KEY FEATURES:
# 1. Dynamic Engine Loading: Switches between Static and Temporal generators.
# 2. Aggressive VRAM Purging: Explicitly clears CUDA cache during context switches.
# 3. Metadata Integration: Coordinates the injection of Subject DNA into tasks.
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
    # worker_prefetch_multiplier=1: Vital for GPU safety. Prevents the worker
    # from pulling multiple CUDA tasks simultaneously.
    worker_prefetch_multiplier=1, 
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

# --- 2. GLOBAL STATE FOR RESOURCE ORCHESTRATION ---
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

    # 1. CACHE HIT: Resume execution with the existing manifold.
    if _current_model_instance is not None and _current_model_type == target_type:
        print(f"WORKER_SYS: Manifold Hit. Reusing {target_type} engine.")
        return _current_model_instance

    # 2. CONTEXT SWITCH (CACHE MISS):
    # Unload the current engine to liberate VRAM for the incoming manifold.
    if _current_model_instance is not None:
        print(f"WORKER_SYS: Context Switch ({_current_model_type} -> {target_type}).")
        
        # Dereference and invoke Python Garbage Collector
        del _current_model_instance
        _current_model_instance = None
        gc.collect()
        
        # GPU VRAM Purge (NVIDIA Specific)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            free_vram = torch.cuda.mem_get_info()[0] / 1024**3
            print(f"WORKER_SYS: CUDA VRAM Purged. Available: {free_vram:.2f} GB")

    # 3. INITIALIZATION: Deploy the requested engine.
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"WORKER_SYS: Deploying {target_type} engine on [{device.upper()}]...")

    if target_type == 'STATIC':
        # Initialize Static Fusion components (SD1.5 + Heuristics)
        evaluator = ComputerVisionEvaluator()
        generator = StableDiffusionGenerator(device=device)
        # Encapsulate in Application Use Case
        _current_model_instance = TransformCharacterUseCase(generator, evaluator)
        _current_model_type = 'STATIC'
        
    elif target_type == 'TEMPORAL':
        # Initialize Temporal Fusion components (AnimateDiff)
        _current_model_instance = StableVideoAnimateDiffGenerator(device=device)
        _current_model_type = 'TEMPORAL'

    return _current_model_instance

# --- 3. ASYNCHRONOUS TASK DEFINITIONS ---

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
        
        # Decode Input Manifold
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # Load Application Service
        use_case = manage_hardware_resources('STATIC')

        # Execute Transformation Lifecycle
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

        # Encode Output Manifold
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
        
        # Decode Input Still
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # Deploy Temporal Engine
        video_gen = manage_hardware_resources('TEMPORAL')
        
        # Execute Temporal Synthesis
        # NOMENCLATURE FIX: Passing 'subject_metadata' to match the updated adapter.
        report = video_gen.animate_image(
            source_image=source_pil,
            motion_prompt=video_params.get("motion_prompt"),
            subject_metadata={"name": character_name}, 
            duration_frames=video_params.get("duration_frames", 24),
            fps=video_params.get("fps", 8),
            hyper_params=video_params,
            progress_callback=on_progress
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