# path: z_realism_ai/src/infrastructure/api.py
# description: FastAPI Web Controller. 
#              UPDATED: /transform endpoint now accepts feature prompt and 
#              dynamic resolution control parameters.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import io
import torch
import base64
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from celery.result import AsyncResult

# Import the task and celery app for communication
from src.infrastructure.worker import transform_character_task, celery_app

# -----------------------------------------------------------------------------
# API Configuration & Metadata
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Z-Realism AI API",
    description="Photorealistic transformation engine for Dragon Ball characters.",
    version="1.4.0"
)

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.post(
    "/transform", 
    summary="Accepts image and configuration to start the AI process.",
    response_description="Returns a Task ID for tracking."
)
async def transform_image(
    file: UploadFile = File(..., description="The source anime image."),
    character_name: str = Form(..., description="The name of the character."),
    # NEW PARAMETERS FROM UI:
    feature_prompt: str = Form("", description="User-guided features (e.g., 'wearing specific boots', 'barefoot')."),
    resolution_anchor: int = Form(512, description="Target pixel size for the shortest side (e.g., 512, 640).")
):
    """
    Validates input and dispatches a background task with full configuration.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="The uploaded file must be an image.")

    # Validation: Ensure resolution is sensible and multiple of 8
    if resolution_anchor < 256 or resolution_anchor % 8 != 0:
        raise HTTPException(status_code=400, detail="Resolution anchor must be a multiple of 8 (min 256).")

    try:
        content = await file.read()
        image_b64 = base64.b64encode(content).decode('utf-8')

        # Dispatch task with all user-defined parameters
        task = transform_character_task.delay(
            image_b64, 
            character_name,
            feature_prompt,
            resolution_anchor
        )

        return {
            "task_id": task.id,
            "status": "QUEUED",
            "message": f"Task queued at {resolution_anchor}px anchor."
        }
    except Exception as e:
        print(f"API_ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during task dispatch.")

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "ready": task_result.ready(),
        "progress": None
    }

    if task_result.status == 'PROGRESS':
        response["progress"] = task_result.info
    
    return response

@app.get("/result/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    if not task_result.ready(): raise HTTPException(status_code=202)
    if task_result.failed(): raise HTTPException(status_code=500, detail="AI worker failed.")

    result_b64 = task_result.result
    image_data = base64.b64decode(result_b64)
    
    return StreamingResponse(io.BytesIO(image_data), media_type="image/png")

@app.get("/health")
async def health_check():
    return {"status": "online", "hardware": "cuda" if torch.cuda.is_available() else "cpu"}