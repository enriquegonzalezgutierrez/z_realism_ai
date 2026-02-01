# path: z_realism_ai/src/infrastructure/api.py
# description: FastAPI Web Controller with Smart Mutex.
#              UPDATED: The lock now stores the specific Task ID to allow 
#              the owner to track progress while blocking others.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import io
import base64
import redis
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from celery.result import AsyncResult

from src.infrastructure.worker import transform_character_task, celery_app

app = FastAPI(title="Z-Realism Research API", version="1.9.5")

redis_client = redis.from_url(os.getenv("CELERY_BROKER_URL", "redis://z-realism-broker:6379/0"))
SYSTEM_LOCK_KEY = "z_realism_global_mutex"
LOCK_TIMEOUT = 900 

@app.post("/transform")
async def transform_image(
    file: UploadFile = File(...),
    character_name: str = Form(...),
    feature_prompt: str = Form(""),
    resolution_anchor: int = Form(512)
):
    # Check if a lock exists
    if redis_client.exists(SYSTEM_LOCK_KEY):
        raise HTTPException(status_code=429, detail="SYSTEM_LOCKED")

    try:
        content = await file.read()
        image_b64 = base64.b64encode(content).decode('utf-8')

        task = transform_character_task.delay(
            image_b64, character_name, feature_prompt, resolution_anchor
        )

        # PH.D. FIX: Store the task_id as the lock value
        redis_client.set(SYSTEM_LOCK_KEY, task.id, ex=LOCK_TIMEOUT)

        return {"task_id": task.id, "status": "QUEUED"}
    except Exception as e:
        redis_client.delete(SYSTEM_LOCK_KEY)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    # Auto-release if the task assigned to the lock is finished
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

@app.get("/system/status")
async def get_system_status():
    lock_owner = redis_client.get(SYSTEM_LOCK_KEY)
    return {
        "locked": bool(lock_owner),
        "owner_id": lock_owner.decode('utf-8') if lock_owner else None
    }

@app.post("/system/unlock")
async def manual_unlock():
    redis_client.delete(SYSTEM_LOCK_KEY)
    return {"message": "Unlocked"}

@app.get("/result/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if not task_result.ready(): raise HTTPException(status_code=202)
    return JSONResponse(content=task_result.result)

@app.get("/health")
async def health_check():
    return {"status": "online", "hardware": "cpu", "api_version": "1.9.5-mutex"}
