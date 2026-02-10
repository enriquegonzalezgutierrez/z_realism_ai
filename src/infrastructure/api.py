# path: z_realism_ai/src/infrastructure/api.py
# description: Expert Gateway v20.0 - Temporal Orchestration & Multi-Modal Gateway.
#
# ABSTRACT:
# This module implements the Primary Driving Adapter for the Z-Realism ecosystem. 
# It manages the ingestion of multi-part form data and marshals complex 
# hyperparameters into serialized task payloads for the distributed Celery queue.
#
# ARCHITECTURAL EVOLUTION (v20.0):
# 1. Introduced '/animate' endpoint to support Image-to-Video synthesis.
# 2. Implemented hardware orchestration for video tasks using the same 
#    Redis-based Mutex to prevent VRAM overflow on 6GB cards.
# 3. Maintained decoupled conditioning schema for both static and temporal tasks.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import io
import base64
import redis
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from PIL import Image

# Core Implementation Imports
from src.infrastructure.worker import transform_character_task, animate_character_task, celery_app
from src.infrastructure.analyzer import HeuristicImageAnalyzer

app = FastAPI(title="Z-Realism Expert Gateway", version="20.0")

# --- 1. CROSS-ORIGIN RESOURCE SHARING (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. HARDWARE RESOURCE COORDINATION ---
redis_client = redis.from_url(os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0"))
SYSTEM_LOCK_KEY = "z_realism_v19_mutex"
LOCK_TIMEOUT = 900 

# Neural Strategy Intelligence
image_analyzer = HeuristicImageAnalyzer()

# --- 3. ANALYTICAL ENDPOINT ---
@app.post("/analyze")
async def analyze_visual_dna(
    file: UploadFile = File(...),
    character_name: str = Form("Unknown")
):
    """
    Invokes the Heuristic Brain to determine the optimal synthesis strategy.
    Returns granular weights and stochastic ratios from Domain Lore.
    """
    try:
        content = await file.read()
        pil_image = Image.open(io.BytesIO(content))
        analysis = image_analyzer.analyze_source(pil_image, character_name)
        
        return {
            "status": "success",
            "detected_essence": analysis.detected_essence,
            "recommendations": {
                "steps": analysis.recommended_steps, 
                "cfg_scale": analysis.recommended_cfg,
                "cn_scale_depth": analysis.recommended_cn_depth,
                "cn_scale_pose": analysis.recommended_cn_pose,
                "strength": analysis.recommended_strength,
                "texture_prompt": analysis.suggested_prompt,
                "negative_prompt": analysis.suggested_negative
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Failure: {str(e)}")

# --- 4. TRANSFORMATION ENDPOINT (STATIC IMAGE) ---
@app.post("/transform")
async def transform_image(
    file: UploadFile = File(...),
    character_name: str = Form(...),
    feature_prompt: str = Form(""),
    resolution_anchor: int = Form(512),
    steps: int = Form(30),
    cfg_scale: float = Form(7.5),
    cn_depth: float = Form(0.75),
    cn_pose: float = Form(0.40),
    strength: float = Form(0.70),
    seed: int = Form(42),
    negative_prompt: str = Form("anime, cartoon")
):
    """
    Dispatches the high-fidelity synthesis job to the CUDA worker.
    Implements hardware single-tenancy via Redis Mutex.
    """
    if redis_client.exists(SYSTEM_LOCK_KEY):
        raise HTTPException(status_code=429, detail="HARDWARE_LOCK: CUDA Engine Busy.")

    try:
        content = await file.read()
        image_b64 = base64.b64encode(content).decode('utf-8')

        hyper_params = {
            "steps": steps,
            "cfg_scale": cfg_scale,
            "cn_depth": cn_depth,
            "cn_pose": cn_pose,
            "strength": strength,
            "seed": seed,
            "negative_prompt": negative_prompt
        }

        task = transform_character_task.delay(
            image_b64, character_name, feature_prompt, resolution_anchor, hyper_params
        )

        redis_client.set(SYSTEM_LOCK_KEY, task.id, ex=LOCK_TIMEOUT)
        return {"task_id": task.id, "status": "QUEUED"}
    except Exception as e:
        redis_client.delete(SYSTEM_LOCK_KEY)
        raise HTTPException(status_code=500, detail=str(e))

# --- 5. ANIMATION ENDPOINT (VIDEO CLIP) ---
@app.post("/animate")
async def animate_image(
    file: UploadFile = File(...),
    character_name: str = Form(...),
    motion_prompt: str = Form("subtle realistic movement, breathing"),
    duration_frames: int = Form(24),
    fps: int = Form(8),
    motion_bucket: int = Form(127),
    denoising_strength: float = Form(0.20),
    seed: int = Form(42)
):
    """
    Dispatches a temporal synthesis task (Video).
    Utilizes the same Hardware Mutex to protect VRAM on 6GB cards.
    """
    if redis_client.exists(SYSTEM_LOCK_KEY):
        raise HTTPException(status_code=429, detail="HARDWARE_LOCK: CUDA Engine Busy.")

    try:
        content = await file.read()
        image_b64 = base64.b64encode(content).decode('utf-8')

        # Temporal manifold parameters
        video_params = {
            "motion_prompt": motion_prompt,
            "duration_frames": duration_frames,
            "fps": fps,
            "motion_bucket": motion_bucket,
            "denoising_strength": denoising_strength,
            "seed": seed
        }

        # Dispatch specialized video task
        task = animate_character_task.delay(image_b64, character_name, video_params)

        redis_client.set(SYSTEM_LOCK_KEY, task.id, ex=LOCK_TIMEOUT)
        return {"task_id": task.id, "status": "QUEUED_TEMPORAL"}
    except Exception as e:
        redis_client.delete(SYSTEM_LOCK_KEY)
        raise HTTPException(status_code=500, detail=str(e))

# --- 6. TELEMETRY & SYSTEM CONTROL ---
@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        current_lock = redis_client.get(SYSTEM_LOCK_KEY)
        if current_lock and current_lock.decode('utf-8') == task_id:
            redis_client.delete(SYSTEM_LOCK_KEY)
    
    return {
        "status": task_result.status,
        "progress": task_result.info if task_result.status == 'PROGRESS' else None
    }

@app.get("/result/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if not task_result.ready(): raise HTTPException(status_code=202)
    return JSONResponse(content=task_result.result)

@app.post("/system/unlock")
async def manual_unlock():
    redis_client.delete(SYSTEM_LOCK_KEY)
    return {"message": "Hardware Mutex Released."}