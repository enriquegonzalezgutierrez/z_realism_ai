# path: z_realism_ai/Dockerfile
# description: Production-grade Container Definition v21.8 - Final Candidate.
#              Defines the immutable runtime environment for the Z-Realism engine.
#
# ARCHITECTURAL ROLE:
# This Dockerfile encapsulates the entire research ecosystem. It provides the 
# necessary system-level libraries for Computer Vision (OpenCV) and Neural 
# Hand Tracking/Face Detection (Mediapipe), while ensuring the Python 
# environment is isolated and reproducible.
#
# KEY OPTIMIZATIONS:
# 1. Vision Support: Includes X11 and GLib extensions for headless processing.
# 2. Performance: Configured for high-latency neural workloads (CUDA-ready).
# 3. Size: Based on python:3.10-slim to balance compatibility and footprint.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

# -----------------------------------------------------------------------------
# Base Image Selection
# -----------------------------------------------------------------------------
FROM python:3.10-slim

# -----------------------------------------------------------------------------
# Environment Configuration
# -----------------------------------------------------------------------------
# Prevents Python from writing .pyc files to the container filesystem.
ENV PYTHONDONTWRITEBYTECODE=1

# Ensures terminal logs are delivered in real-time without buffering.
ENV PYTHONUNBUFFERED=1

# Defines the persistent model cache location for Hugging Face weights.
ENV HF_HOME=/app/model_cache

# Set the working directory for the application lifecycle.
WORKDIR /app

# -----------------------------------------------------------------------------
# System Dependencies (Linux OS Layer)
# -----------------------------------------------------------------------------
# Install essential build tools and visual processing libraries.
# - gcc/g++/build-essential: Required for compiling native Python extensions.
# - libgl1/libglib2.0-0: Core requirements for OpenCV manifold analysis.
# - libsm6/libxext6/libxrender-dev: MANDATORY for Mediapipe and ONNX Runtime.
# - ffmpeg: Required for the Temporal Fusion (MP4) encoding pipeline.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Application Dependencies (Python Layer)
# -----------------------------------------------------------------------------
# Copy the dependency manifest first to utilize Docker's cache.
# This prevents re-downloading PyTorch (2GB+) unless requirements.txt changes.
COPY requirements.txt .

# Install Python packages.
# --timeout 1000: Prevents failures during large neural weight downloads.
# --no-cache-dir: Reduces final image size by not storing the wheel cache.
RUN pip install --no-cache-dir -r requirements.txt --timeout 1000

# -----------------------------------------------------------------------------
# Source Code Injection
# -----------------------------------------------------------------------------
# Copy the refactored source code into the container filesystem.
COPY src/ ./src/

# -----------------------------------------------------------------------------
# Network Exposure & Execution
# -----------------------------------------------------------------------------
# Expose the API Gateway port (RESTful interface).
EXPOSE 8000

# Default command launches the ASGI Server (Uvicorn).
# The --host 0.0.0.0 is critical for Docker bridge networking.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]