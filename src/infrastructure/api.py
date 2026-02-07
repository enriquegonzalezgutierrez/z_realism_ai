# path: z_realism_ai/src/infrastructure/api.py
# description: FastAPI Gateway v10.0 - Stealth Protocol Edition.
#              Orchestrates complex parameter marshalling from the Custom UI 
#              to the asynchronous CUDA workers.
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
from src.infrastructure.worker import transform_character_task, celery_app
from src.infrastructure.analyzer import HeuristicImageAnalyzer

app = FastAPI(title="Z-Realism Expert Gateway", version="10.0")

# --- 1. CROSS-ORIGIN RESOURCE SHARING (CORS) ---
# Allows the Custom UI (Port 80) to securely communicate with the API (Port 8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permissive for development laboratory environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. HARDWARE RESOURCE COORDINATION ---
# Redis client for task tracking and hardware mutex locks.
redis_client = redis.from_url(os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0"))
SYSTEM_LOCK_KEY = "z_realism_v10_mutex"
LOCK_TIMEOUT = 900 # 15-minute safety timeout for high-res renders

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
                "cn_scale": analysis.recommended_cn,
                "texture_prompt": analysis.suggested_prompt 
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Failure: {str(e)}")

# --- 4. TRANSFORMATION ENDPOINT ---
@app.post("/transform")
async def transform_image(
    file: UploadFile = File(...),
    character_name: str = Form(...),
    feature_prompt: str = Form(""),
    resolution_anchor: int = Form(512),
    steps: int = Form(30),
    cfg_scale: float = Form(7.5),
    cn_scale: float = Form(0.70),
    stealth_stop: float = Form(0.60), # NEW: Temporal control parameter
    seed: int = Form(42),
    ip_scale: float = Form(0.65),
    negative_prompt: str = Form("anime, cartoon")
):
    """
    Dispatches the heavy dimensional fusion task to the asynchronous CUDA queue.
    Ensures single-task execution to protect 6GB VRAM hardware.
    """
    if redis_client.exists(SYSTEM_LOCK_KEY):
        raise HTTPException(status_code=429, detail="HARDWARE_LOCK: CUDA Engine Busy.")

    try:
        content = await file.read()
        image_b64 = base64.b64encode(content).decode('utf-8')

        # Package the full 10-parameter hyper-param dictionary
        hyper_params = {
            "steps": steps,
            "cfg_scale": cfg_scale,
            "cn_scale": cn_scale,
            "stealth_stop": stealth_stop, # Injected into the task payload
            "seed": seed,
            "ip_scale": ip_scale,
            "negative_prompt": negative_prompt
        }

        # Dispatch to Celery Worker
        task = transform_character_task.delay(
            image_b64, character_name, feature_prompt, resolution_anchor, hyper_params
        )

        # Secure the hardware lock
        redis_client.set(SYSTEM_LOCK_KEY, task.id, ex=LOCK_TIMEOUT)
        
        return {"task_id": task.id, "status": "QUEUED"}
    except Exception as e:
        redis_client.delete(SYSTEM_LOCK_KEY)
        raise HTTPException(status_code=500, detail=str(e))

# --- 5. TELEMETRY & SYSTEM CONTROL ---
@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Real-time monitoring of de-noising progress."""
    task_result = AsyncResult(task_id, app=celery_app)
    # Release lock automatically if the task is finished
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
    """Retrieves finalized base64 image and scientific metrics."""
    task_result = AsyncResult(task_id, app=celery_app)
    if not task_result.ready(): raise HTTPException(status_code=202)
    return JSONResponse(content=task_result.result)

@app.post("/system/unlock")
async def manual_unlock():
    """Safety manual override to release hardware resources."""
    redis_client.delete(SYSTEM_LOCK_KEY)
    return {"message": "System Unlocked. Ready for next session."}

@app.get("/system/status")
async def get_system_status():
    """Returns true if the GPU is currently processing a task."""
    lock_owner = redis_client.get(SYSTEM_LOCK_KEY)
    return {"locked": bool(lock_owner)}