# path: z_realism_ai/Dockerfile
# description: Production-grade container definition for the Z-Realism AI Service.
#              Builds a lightweight yet capable Python environment for Deep Learning.
#              Optimized for caching and minimized layer sizes.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

# -----------------------------------------------------------------------------
# Base Image
# -----------------------------------------------------------------------------
# We use python:3.10-slim to keep the image size manageable while maintaining
# compatibility with standard PyTorch wheels. 'slim' lacks some build tools
# but is much smaller than the full image.
FROM python:3.10-slim

# -----------------------------------------------------------------------------
# Environment Configuration
# -----------------------------------------------------------------------------
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk.
# This is irrelevant in a container and saves I/O operations.
ENV PYTHONDONTWRITEBYTECODE=1

# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal (logs).
# Critical for monitoring Docker logs in real-time without buffering delays.
ENV PYTHONUNBUFFERED=1

# HF_HOME: defines where Hugging Face libraries save downloaded models.
# We point this to a specific directory so we can mount it as a Volume later.
# This prevents re-downloading 4GB+ models every time the container restarts.
ENV HF_HOME=/app/model_cache

# Set the working directory for all subsequent commands
WORKDIR /app

# -----------------------------------------------------------------------------
# System Dependencies
# -----------------------------------------------------------------------------
# We install essential system libraries required by OpenCV (used indirectly)
# and general build tools.
# CRITICAL FIX: Added build-essential and g++ for compiling native Python 
# dependencies (like insightface and onnxruntime) inside the container.
# - gcc: C Compiler required for building some Python extensions.
# - git: Required by 'diffusers' to download configurations from repositories.
# - libgl1: Replacement for libgl1-mesa-glx (OpenGL support for image processing).
# - libglib2.0-0: Core library for data structure handling, required by many ML libs.
# --no-install-recommends: Avoids installing documentation and extras to save space.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Application Dependencies
# -----------------------------------------------------------------------------
# We copy requirements first to leverage Docker Layer Caching.
# If code changes but requirements don't, this step is skipped on rebuilds.
COPY requirements.txt .

# Install Python packages.
# --no-cache-dir: Don't save the pip cache (saves image space).
# --timeout 1000: PyTorch downloads are huge; standard timeout often fails.
RUN pip install --no-cache-dir -r requirements.txt --timeout 1000

# -----------------------------------------------------------------------------
# Source Code & Execution
# -----------------------------------------------------------------------------
# Copy the actual application source code into the container.
COPY src/ ./src/

# Expose port 8000 to the host network.
EXPOSE 8000

# Command to launch the application using Uvicorn (ASGI Server).
# --host 0.0.0.0: Bind to all network interfaces (required inside Docker).
# --port 8000: Listen on standard API port.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]