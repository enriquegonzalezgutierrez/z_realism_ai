# path: z_realism_ai/src/main.py
# description: Application Entry Point.
#              This script initializes and runs the Uvicorn ASGI server.
#              FIXED: Explicitly importing 'app' from the infrastructure layer 
#              to ensure the container can find the ASGI attribute.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import uvicorn
import os
# CRITICAL: We import 'app' here so it is available in the module scope
# for the command 'uvicorn src.main:app'
from src.infrastructure.api import app

# -----------------------------------------------------------------------------
# Execution Configuration
# -----------------------------------------------------------------------------
# HOST: 0.0.0.0 is necessary for the container to be accessible from the outside.
HOST = os.getenv("APP_HOST", "0.0.0.0")

# PORT: Standard internal port for our API.
PORT = int(os.getenv("APP_PORT", 8000))

# RELOAD: Enabled only in development to allow hot-reloading code changes.
RELOAD = os.getenv("ENVIRONMENT", "development") == "development"

if __name__ == "__main__":
    """
    Main entry point for the Z-Realism AI service.
    
    This block is executed when running 'python src/main.py'.
    It starts the production-ready Uvicorn server.
    """
    print(f"SYSTEM: Starting Z-Realism AI Service on {HOST}:{PORT}...")
    print(f"SYSTEM: Hot-reload is {'ENABLED' if RELOAD else 'DISABLED'}.")
    
    # We pass the string "src.main:app". 
    # Uvicorn will look for the 'app' variable inside this script.
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info"
    )