# path: z_realism_ai/src/main.py
# description: System Entry Point & ASGI Server Orchestrator v21.0.
#
# ARCHITECTURAL ROLE (Hexagonal/DDD):
# This script acts as the "Bootstrapper" for the Z-Realism ecosystem. Its sole 
# responsibility is to initialize the Primary Driving Adapter (FastAPI) and 
# bind it to the network layer via the Uvicorn ASGI server.
#
# DESIGN PHILOSOPHY:
# 1. Environment-Awareness: Dynamically maps network interfaces based on Docker context.
# 2. Production Stability: Disables debugging overhead in production mode.
# 3. Network Resilience: Configures keep-alive durations for large AI data transfers.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import uvicorn
import os

# --- 1. DRIVING ADAPTER IMPORT ---
# We import the 'app' instance from the Infrastructure Layer.
# In Hexagonal terms, this is the 'Primary Adapter' that translates
# HTTP protocol into Application Layer commands.
from src.infrastructure.api import app

# --- 2. RUNTIME CONFIGURATION ---
# These parameters are injected via Environment Variables in the Docker layer.

# HOST: '0.0.0.0' instructs Uvicorn to listen on all available network interfaces.
# This is mandatory for Docker networking to allow the Nginx container to 
# communicate with the API container via the bridge network.
HOST = os.getenv("APP_HOST", "0.0.0.0")

# PORT: The internal listening port (standard research port: 8000).
PORT = int(os.getenv("APP_PORT", 8000))

# RELOAD: Controls the Hot-Reload watcher.
# - Enabled: For active code refactoring in development.
# - Disabled: For immutable process execution in production.
RELOAD = os.getenv("ENVIRONMENT", "production").lower() == "development"

if __name__ == "__main__":
    """
    Main Execution Block.
    
    Triggered when the Docker entrypoint executes 'python src/main.py'.
    Initializes the Uvicorn engine with a standard ASGI configuration.
    """
    
    # Telemetry: System Boot Log
    print(f"SYSTEM_BOOT: Z-Realism AI Service v21.0 initialized.")
    print(f"NETWORK_BIND: Binding to interface [{HOST}:{PORT}]")
    print(f"EXECUTION_MODE: {'DEBUG/RELOAD_ACTIVE' if RELOAD else 'STABLE/IMMUTABLE_MODE'}")
    
    # Launch the ASGI Server
    # Note: We use the string path "src.main:app" to allow Uvicorn's
    # master process to manage worker lifecycles and reload signals.
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info",
        
        # TIMEOUT CONFIGURATION:
        # High-fidelity synthesis results (Images/Videos) generate large 
        # Base64 payloads. We increase the keep-alive timeout to prevent 
        # early termination during the transmission of these manifolds.
        timeout_keep_alive=65
    )