# path: z_realism_ai/src/main.py
# description: System Entry Point & ASGI Server Orchestrator v18.0.
#
# ABSTRACT:
# This script initializes the production-grade Uvicorn server to host the 
# FastAPI application. It serves as the process entry point for the 
# Docker container, managing the transition from static code to a 
# stateful, network-accessible service.
#
# ARCHITECTURAL ROLE:
# 1. Environment Parsing: Loads runtime configurations (Host, Port, Mode) 
#    from the container's environment variables.
# 2. Dependency Resolution: Imports the 'app' instance from the 
#    Infrastructure layer, fulfilling the ASGI specification.
# 3. Server Management: Configures the Uvicorn engine with optimal 
#    concurrency and logging parameters for high-latency AI workloads.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import uvicorn
import os

# --- 1. CORE COMPONENT IMPORT ---
# We import 'app' from the infrastructure layer. This instance is the 
# primary driving adapter that contains all route registrations and 
# middleware configurations.
from src.infrastructure.api import app

# --- 2. RUNTIME CONFIGURATION ---
# These parameters are extracted from the Environment Variables, 
# allowing the same code to behave differently across Development, 
# Staging, and Production environments without modification.

# HOST: 0.0.0.0 is critical for Docker networking, as it tells the 
# server to listen on all available network interfaces within the container.
HOST = os.getenv("APP_HOST", "0.0.0.0")

# PORT: The internal network port for the API gateway.
PORT = int(os.getenv("APP_PORT", 8000))

# RELOAD: Determines if the server should monitor source files for 
# changes and restart automatically (Hot-Reload). Disabled in production 
# for performance and stability.
RELOAD = os.getenv("ENVIRONMENT", "development") == "development"

if __name__ == "__main__":
    """
    Main Execution Block.
    
    Invoked when the container starts via 'python src/main.py'.
    Initializes the Uvicorn event loop with the following specifications:
    - app: The FastAPI ASGI application.
    - host/port: Network binding configuration.
    - log_level: Information density for system telemetry.
    """
    
    # System Initialization Log
    print(f"SYSTEM_BOOT: Z-Realism AI Service initialized.")
    print(f"NETWORK_BIND: Attempting to host on {HOST}:{PORT}")
    print(f"EXECUTION_MODE: {'DEBUG/RELOAD' if RELOAD else 'STABLE/PRODUCTION'}")
    
    # Launch the ASGI Server
    # We use the string reference "src.main:app" to support Uvicorn's 
    # internal multi-process worker management if necessary.
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info",
        # Increase timeout-keep-alive for heavy neural inference traffic
        timeout_keep_alive=65
    )