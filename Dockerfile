# path: z_realism_ai/Dockerfile
# description: Production-grade container definition for the Z-Realism AI Service.
#              Optimized for CUDA-enabled environments and GTX 1060 support.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

# -----------------------------------------------------------------------------
# Base Image
# -----------------------------------------------------------------------------
# Using python:3.10-slim to keep the image size manageable while maintaining
# compatibility with standard PyTorch wheels.
FROM python:3.10-slim

# -----------------------------------------------------------------------------
# Environment Configuration
# -----------------------------------------------------------------------------
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk.
ENV PYTHONDONTWRITEBYTECODE=1

# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal logs.
ENV PYTHONUNBUFFERED=1

# HF_HOME: Defines where Hugging Face libraries save downloaded models.
# We point this to a specific directory to mount it as a Volume later.
ENV HF_HOME=/app/model_cache

# Set the working directory
WORKDIR /app

# -----------------------------------------------------------------------------
# System Dependencies
# -----------------------------------------------------------------------------
# Install system libraries required by OpenCV (libgl1, libglib) and build tools.
# --no-install-recommends: Avoids installing documentation/extras.
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
# Copy requirements first to leverage Docker Layer Caching.
COPY requirements.txt .

# Install Python packages.
# --timeout 1000: PyTorch downloads are huge; increased timeout prevents failures.
RUN pip install --no-cache-dir -r requirements.txt --timeout 1000

# -----------------------------------------------------------------------------
# Source Code & Execution
# -----------------------------------------------------------------------------
# Copy the application source code into the container.
COPY src/ ./src/

# Expose port 8000 (API) and 8501 (Streamlit) capabilities.
EXPOSE 8000
EXPOSE 8501

# Default command launches the API.
# Host 0.0.0.0 is required for container networking.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]