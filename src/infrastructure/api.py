# path: z_realism_ai/src/infrastructure/api.py
# description: FastAPI Gateway v9.2 - Expert Mode & CORS Enabled.
#              FIXED: Added CORSMiddleware to allow Custom UI communication.
#              FEATURING: Full parameter pass-through (Seed, IP-Scale, Negatives).
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

from src.infrastructure.worker import transform_character_task, celery_app
from src.infrastructure.analyzer import HeuristicImageAnalyzer

app = FastAPI(title="Z-Realism Expert API", version="9.2")

# --- 1. CONFIGURACIÓN CORS (CRITICAL FIX FOR CORE LINK ERROR) ---
# Permite que tu interfaz custom (puerto 80) hable con esta API (puerto 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En desarrollo permitimos todo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.from_url(os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0"))
SYSTEM_LOCK_KEY = "z_realism_global_mutex"
LOCK_TIMEOUT = 600 # 10 minutos de seguridad

image_analyzer = HeuristicImageAnalyzer()

@app.post("/analyze")
async def analyze_visual_dna(
    file: UploadFile = File(...),
    character_name: str = Form("Unknown")
):
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transform")
async def transform_image(
    file: UploadFile = File(...),
    character_name: str = Form(...),
    feature_prompt: str = Form(""),
    resolution_anchor: int = Form(512),
    steps: int = Form(25),
    cfg_scale: float = Form(7.5),
    cn_scale: float = Form(0.70),
    seed: int = Form(42),
    ip_scale: float = Form(0.65),
    negative_prompt: str = Form("anime, cartoon")
):
    # Lock hardware for single-task processing (6GB VRAM protection)
    if redis_client.exists(SYSTEM_LOCK_KEY):
        raise HTTPException(status_code=429, detail="SYSTEM_LOCKED: Hardware busy.")

    try:
        content = await file.read()
        image_b64 = base64.b64encode(content).decode('utf-8')

        # Empaquetamos TODOS los parámetros para el Worker
        hyper_params = {
            "steps": steps,
            "cfg_scale": cfg_scale,
            "cn_scale": cn_scale,
            "seed": seed,
            "ip_scale": ip_scale,
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

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        current_lock_owner = redis_client.get(SYSTEM_LOCK_KEY)
        if current_lock_owner and current_lock_owner.decode('utf-8') == task_id:
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
    return {"message": "Hardware lock released."}

@app.get("/system/status")
async def get_system_status():
    lock_owner = redis_client.get(SYSTEM_LOCK_KEY)
    return {"locked": bool(lock_owner)}