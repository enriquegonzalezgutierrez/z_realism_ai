# path: z_realism_ai/src/main.py
# description: Application Entry Point.
#              This script initializes and runs the Uvicorn ASGI server 
#              hosting the Z-Realism FastAPI application.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import uvicorn
import os
from src.infrastructure.api import app

# -----------------------------------------------------------------------------
# Execution Configuration
# -----------------------------------------------------------------------------
# We extract configuration from environment variables to follow 
# Twelve-Factor App methodology.

# HOST: 0.0.0.0 is necessary for the container to be accessible from the outside.
HOST = os.getenv("APP_HOST", "0.0.0.0")

# PORT: Standard internal port for our API.
PORT = int(os.getenv("APP_PORT", 8000))

# RELOAD: Enabled only in development to allow hot-reloading code changes.
RELOAD = os.getenv("ENVIRONMENT", "development") == "development"

if __name__ == "__main__":
    """
    Main entry point for the Z-Realism AI service.
    
    This block is executed when running 'python -m src.main'.
    It starts the production-ready Uvicorn server.
    """
    print(f"SYSTEM: Starting Z-Realism AI Service on {HOST}:{PORT}...")
    print(f"SYSTEM: Hot-reload is {'ENABLED' if RELOAD else 'DISABLED'}.")
    
    # We pass the 'app' instance from the infrastructure layer.
    # The 'src.infrastructure.api:app' string format is used by Uvicorn 
    # to support the 'reload' feature correctly.
    uvicorn.run(
        "src.infrastructure.api:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info"
    )