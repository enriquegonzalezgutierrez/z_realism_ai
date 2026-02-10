# path: z_realism_ai/src/infrastructure/worker.py
# description: Distributed Inference Worker v20.2 - Hybrid Hardware Orchestration.
#
# ABSTRACT:
# This module implements the asynchronous processing consumer for the Z-Realism 
# ecosystem. It manages two primary pipelines: Static Image Transformation 
# and Temporal Video Animation.
#
# CRITICAL FEATURE (v20.2):
# Implements "Context-Aware Resource Management". 
# - If NVIDIA Hardware is detected, it enforces strict single-model VRAM usage
#   and aggressive cache clearing to support 6GB cards.
# - If CPU-only is detected, it gracefully degrades to standard RAM management.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import os
import io
import base64
import torch
import time
import gc  # Standard Python Garbage Collector
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
    # CRITICAL: 'prefetch_multiplier=1' ensures the worker only takes one task 
    # at a time. This is vital for GPU workloads where VRAM is a shared resource.
    worker_prefetch_multiplier=1, 
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

# --- 2. GLOBAL STATE FOR MEMORY MANAGEMENT ---
# We track the active model type to avoid reloading if the task type hasn't changed.
_current_model_instance = None
_current_model_type = None  # Values: 'STATIC', 'TEMPORAL', or None

def manage_hardware_resources(target_type: str):
    """
    Hybrid Resource Manager.
    
    Dynamically adapts to the underlying hardware (CPU vs GPU) to ensure
    stability during model switching.
    
    Args:
        target_type (str): 'STATIC' for Image Generation, 'TEMPORAL' for Video.
        
    Returns:
        The requested model instance (initialized or cached).
    """
    global _current_model_instance, _current_model_type

    # 1. CACHE HIT: If the requested model is already loaded, return it.
    if _current_model_instance is not None and _current_model_type == target_type:
        print(f"WORKER_SYS: Cache Hit. Reusing {target_type} model.")
        return _current_model_instance

    # 2. CONTEXT SWITCH (CACHE MISS):
    # We need to unload the current model to free up resources for the new one.
    if _current_model_instance is not None:
        print(f"WORKER_SYS: Context Switch ({_current_model_type} -> {target_type}). Releasing memory...")
        
        # A. Explicitly delete object references
        del _current_model_instance
        _current_model_instance = None
        
        # B. Standard RAM Cleanup (CPU/System RAM)
        # This is necessary on both Laptop and PC to free up main memory.
        gc.collect()
        
        # C. GPU VRAM Cleanup (Conditional)
        # Only runs if NVIDIA hardware is detected. Prevents "Out of Memory" on the 1060.
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            print(f"WORKER_SYS: GPU VRAM Purged. Free VRAM: {torch.cuda.mem_get_info()[0] / 1024**3:.2f} GB")
        else:
            print(f"WORKER_SYS: System RAM Collected.")

    # 3. INITIALIZATION: Load the new requested model.
    # Automatic Hardware Detection:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"WORKER_SYS: Initializing {target_type} engine on [{device.upper()}]...")

    if target_type == 'STATIC':
        # Initialize Static Pipeline Components
        evaluator = ComputerVisionEvaluator()
        generator = StableDiffusionGenerator(device=device)
        # Wrap in Use Case
        _current_model_instance = TransformCharacterUseCase(generator, evaluator)
        _current_model_type = 'STATIC'
        
    elif target_type == 'TEMPORAL':
        # Initialize Temporal Pipeline Components
        _current_model_instance = StableVideoAnimateDiffGenerator(device=device)
        _current_model_type = 'TEMPORAL'

    return _current_model_instance

# --- 3. TASK DEFINITIONS ---

@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(self, image_b64, character_name, feature_prompt, resolution_anchor, hyper_params):
    """
    Orchestrates the Image-to-Image photorealism pipeline.
    """
    total_steps = int(hyper_params.get("steps", 30))

    def on_progress(current, total=total_steps, preview_b64=None):
        pct = min(max(int((current / total) * 100), 0), 100)
        self.update_state(state='PROGRESS', meta={'percent': pct, 'preview_b64': preview_b64, 'status_text': 'SYNTHESIZING_IMAGE'})

    try:
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'INITIALIZING'})
        
        # 1. Decode Input
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # 2. Resource Management (Switch to Static Mode)
        self.update_state(state='PROGRESS', meta={'percent': 5, 'status_text': 'LOADING_STATIC_ENGINE'})
        # Uses the Hybrid Manager to safely load the model
        use_case = manage_hardware_resources('STATIC')

        # 3. Execution
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

        # 4. Encoding Output
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
    """
    Orchestrates the Temporal (Video) synthesis pipeline.
    """
    
    def on_progress(current, total, status_msg="ANIMATING"):
        pct = min(max(int((current / total) * 100), 0), 100)
        self.update_state(state='PROGRESS', meta={'percent': pct, 'status_text': status_msg})

    try:
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'DECODING_SOURCE'})
        
        # 1. Decode Input
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # 2. Resource Management (Switch to Temporal Mode)
        # Automatically purges VRAM if switching from Static to Temporal
        self.update_state(state='PROGRESS', meta={'percent': 5, 'status_text': 'LOADING_TEMPORAL_ENGINE'})
        video_gen = manage_hardware_resources('TEMPORAL')
        
        # 3. Execution
        # The logic inside video_gen handles further hardware-specific details (like offloading)
        report = video_gen.animate_image(
            source_image=source_pil,
            motion_prompt=video_params.get("motion_prompt"),
            character_lore={"name": character_name}, 
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