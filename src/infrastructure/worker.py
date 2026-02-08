# path: z_realism_ai/src/infrastructure/worker.py
# description: Distributed Inference Worker v18.1 - Neural Orchestration Layer.
#
# ABSTRACT:
# This module implements the asynchronous processing consumer using the Celery 
# distributed task queue framework. It acts as the "Heavy Compute" bridge 
# between the RESTful API and the Generative AI Domain. 
#
# CHANGES v18.1:
# 1. UPDATED: Serialization logic to include the new 'textural_realism' metric 
#    in the final task result payload.
# 2. MAINTAINED: Telemetry synchronization protocols and lazy-loading singletons.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import os
import io
import base64
import torch
import time  # Technical requirement for telemetry synchronization
from celery import Celery
from PIL import Image

# Domain & Infrastructure Layer Imports
from src.application.use_cases import TransformCharacterUseCase
from src.infrastructure.sd_generator import StableDiffusionGenerator
from src.infrastructure.evaluator import ComputerVisionEvaluator

# --- 1. CELERY INFRASTRUCTURE CONFIGURATION ---
# Defines the communication protocols for the message broker (Redis).
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://z-realism-broker:6379/0")

celery_app = Celery("z_realism_worker", broker=BROKER_URL, backend=RESULT_BACKEND)

# Optimization parameters for high-latency AI tasks
celery_app.conf.update(
    task_track_started=True, 
    worker_prefetch_multiplier=1, # Ensures the worker only takes one task at a time (VRAM protection)
    task_acks_late=True,          # Only acknowledge task completion after successful processing
    broker_connection_retry_on_startup=True
)

# --- 2. SINGLETON INITIALIZATION (Lazy Loading) ---
# Persists the neural weights in memory to avoid "Cold Start" penalties 
# on subsequent requests.
_use_case_instance = None

def get_use_case(task_instance):
    """
    Retrieves or initializes the TransformCharacterUseCase singleton.
    
    Args:
        task_instance: The current Celery task reference for state updates.
    Returns:
        TransformCharacterUseCase: The orchestrated application service.
    """
    global _use_case_instance
    if _use_case_instance is None:
        # Inform the system that we are in a 'Cold Start' phase (Model Loading)
        task_instance.update_state(
            state='PROGRESS', 
            meta={'percent': 0, 'status_text': 'LOADING_MODELS'}
        )
        
        # Hardware Target Detection
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"WORKER_SYSTEM: Initiating Neural Engine Deployment on {device}...")
        
        # Dependency Injection (Manual)
        evaluator = ComputerVisionEvaluator()
        generator = StableDiffusionGenerator(device=device)
        
        # Assemble Application Layer
        _use_case_instance = TransformCharacterUseCase(generator, evaluator)
        
    return _use_case_instance

# --- 3. TASK DEFINITION ---
@celery_app.task(name="transform_character_task", bind=True)
def transform_character_task(self, image_b64, character_name, feature_prompt, resolution_anchor, hyper_params):
    """
    Main entry point for the character transformation pipeline.
    
    This function manages the data transformation pipeline:
    Base64 Input -> PIL Tensor -> Neural Synthesis -> Scientific Eval -> Base64 Output.
    """
    total_steps = int(hyper_params.get("steps", 30))

    def on_progress(current, total=total_steps, preview_b64=None):
        """
        In-situ callback to update Redis with current diffusion state.
        
        Args:
            current: Current de-noising iteration.
            total: Target iteration count.
            preview_b64: Intermediate latent representation (Linear Approximation).
        """
        pct = min(max(int((current / total) * 100), 0), 100)
        
        self.update_state(
            state='PROGRESS', 
            meta={
                'percent': pct,
                'preview_b64': preview_b64,
                'status_text': 'SYNTHESIZING'
            }
        )

    try:
        # Phase 0: Data Preparation
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'INITIALIZING'})
        source_pil = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        
        # Ensure the heavy model is ready
        use_case = get_use_case(self)
        self.update_state(state='PROGRESS', meta={'percent': 0, 'status_text': 'ALLOCATING_VRAM'})

        # Phase 1: Execution & Quantitative Evaluation
        # The use_case handles the interaction between Stable Diffusion and OpenCV.
        result_pil, report = use_case.execute(
            image_file=source_pil, 
            character_name=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            callback=on_progress
        )

        # --- TELEMETRY SYNCHRONIZATION PROTOCOL (v18.0 Patch) ---
        # Problem: The transition from 100% Progress to SUCCESS is near-instant. 
        # In distributed environments, the "SUCCESS" result often overwrites 
        # the "100%" progress key in Redis before the Frontend can poll it.
        #
        # Solution: Explicitly update the state to 100% and suspend the thread 
        # for 500ms to allow the Redis I/O cycle to complete.
        self.update_state(
            state='PROGRESS', 
            meta={
                'percent': 100, 
                'status_text': 'FINALIZING_METRICS_AND_SERIALIZATION'
            }
        )
        time.sleep(0.5) 
        # -------------------------------------------------------

        # Phase 2: Serialization
        # High-resolution PNG encoding is a blocking CPU operation.
        buffered = io.BytesIO()
        result_pil.save(buffered, format="PNG")
        
        # Return final Result Payload
        return {
            "result_image_b64": base64.b64encode(buffered.getvalue()).decode('utf-8'),
            "metrics": {
                "structural_similarity": report.structural_similarity,
                "identity_preservation": report.identity_preservation,
                "textural_realism": report.textural_realism,  # NEW: Added for v18.1
                "inference_time": report.inference_time,
                "is_mock": report.is_mock,
                "full_prompt": report.full_prompt,
                "negative_prompt": report.negative_prompt
            }
        }
        
    except Exception as e:
        print(f"WORKER_TASK_CRITICAL_FAILURE: {str(e)}")
        # Raise exception to ensure Celery accurately reports the FAILURE state
        raise e