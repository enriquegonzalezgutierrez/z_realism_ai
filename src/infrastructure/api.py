# path: z_realism_ai/src/infrastructure/api.py
# description: FastAPI Controller v2.9.5 - Universal Expert Edition.
#              FEATURING: Support for specific character forms (Black, Golden) 
#              and secondary archetypes (Monks/Humanoids like Tien).
#              OPTIMIZED: Enhanced lore-based reasoning via character name injection.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import io
import base64
import redis
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from PIL import Image

# Implementation Imports
from src.infrastructure.worker import transform_character_task, celery_app
from src.infrastructure.analyzer import HeuristicImageAnalyzer

app = FastAPI(title="Z-Realism Universal API", version="2.9.5")

# --- Infrastructure Persistence ---
# Global Mutex (Redis) for hardware resource coordination.
redis_client = redis.from_url(os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0"))
SYSTEM_LOCK_KEY = "z_realism_global_mutex"
LOCK_TIMEOUT = 1800 

# Instantiate the v5.5 Universal Heuristic Engine
image_analyzer = HeuristicImageAnalyzer()

# -----------------------------------------------------------------------------
# 1. UNIVERSAL HEURISTIC ANALYSIS ENDPOINT
# -----------------------------------------------------------------------------
@app.post("/analyze")
async def analyze_visual_dna(
    file: UploadFile = File(...),
    character_name: str = Form("Unknown")
):
    """
    Performs universal heuristic analysis.
    Uses the character name string to detect specific forms (e.g., 'Black Frieza')
    and archetypes (e.g., 'Tien' as a Humanoid Monk).
    """
    try:
        content = await file.read()
        pil_image = Image.open(io.BytesIO(content))
        
        # Execute the v5.5 Universal Analysis logic
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
        raise HTTPException(status_code=500, detail=f"Universal analysis failure: {str(e)}")

# -----------------------------------------------------------------------------
# 2. NEURAL PIPELINE ENDPOINTS
# -----------------------------------------------------------------------------
@app.post("/transform")
async def transform_image(
    file: UploadFile = File(...),
    character_name: str = Form(...),
    feature_prompt: str = Form(""),
    resolution_anchor: int = Form(512),
    steps: int = Form(20),
    cfg_scale: float = Form(7.5),
    cn_scale: float = Form(0.38)
):
    """
    Dispatches the neural transformation task to the asynchronous queue.
    Ensures that only one hardware-heavy task is processed at a time.
    """
    if redis_client.exists(SYSTEM_LOCK_KEY):
        raise HTTPException(status_code=429, detail="SYSTEM_LOCKED: Hardware resources busy.")

    try:
        content = await file.read()
        image_b64 = base64.b64encode(content).decode('utf-8')

        # Encapsulate hyper-parameters for the neural engine
        hyper_params = {
            "steps": steps,
            "cfg_scale": cfg_scale,
            "cn_scale": cn_scale
        }

        # Dispatch task to Celery
        task = transform_character_task.delay(
            image_b64, character_name, feature_prompt, resolution_anchor, hyper_params
        )

        # Secure the global hardware lock
        redis_client.set(SYSTEM_LOCK_KEY, task.id, ex=LOCK_TIMEOUT)

        return {"task_id": task.id, "status": "QUEUED"}
    except Exception as e:
        # Cleanup lock on critical failure
        redis_client.delete(SYSTEM_LOCK_KEY)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Monitors task progress and releases lock on completion."""
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        current_lock_owner = redis_client.get(SYSTEM_LOCK_KEY)
        if current_lock_owner and current_lock_owner.decode('utf-8') == task_id:
            redis_client.delete(SYSTEM_LOCK_KEY)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "ready": task_result.ready(),
        "progress": task_result.info if task_result.status == 'PROGRESS' else None
    }

@app.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """Retrieves the finalized synthesis and Metrics."""
    task_result = AsyncResult(task_id, app=celery_app)
    if not task_result.ready(): raise HTTPException(status_code=202)
    return JSONResponse(content=task_result.result)

# -----------------------------------------------------------------------------
# 3. ADMINISTRATIVE TOOLS
# -----------------------------------------------------------------------------
@app.get("/system/status")
async def get_system_status():
    lock_owner = redis_client.get(SYSTEM_LOCK_KEY)
    return {"locked": bool(lock_owner), "owner_id": lock_owner.decode('utf-8') if lock_owner else None}

@app.post("/system/unlock")
async def manual_unlock():
    """Safety override for maintenance."""
    redis_client.delete(SYSTEM_LOCK_KEY)
    return {"message": "System unlocked."}

@app.get("/health")
async def health_check():
    return {"status": "online", "api_version": "2.9.5-universal-lore"}