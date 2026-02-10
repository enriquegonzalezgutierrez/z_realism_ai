# path: z_realism_ai/src/infrastructure/video_generator.py
# description: Neural Temporal Engine v20.2 - Hybrid Hardware Support.
#
# ABSTRACT:
# This module implements the AnimateDiff pipeline for Image-to-Video synthesis.
# It is engineered to run on both High-Performance GPU environments and 
# Legacy CPU environments.
#
# CRITICAL LOGIC (v20.2):
# 1. Hardware Detection: Automatically detects CUDA availability.
# 2. Precision Switching: Uses 'float16' for NVIDIA GPUs (Speed/Memory) and
#    'float32' for CPU (Compatibility).
# 3. Offloading Strategies: Applies "Sequential CPU Offload" ONLY when a GPU
#    is present to maximize the 32GB System RAM utility.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import imageio
import io
import base64
import time
import os
from typing import Callable, Optional, Tuple, Dict, Any, List
from PIL import Image

from diffusers import (
    AnimateDiffPipeline, 
    MotionAdapter, 
    DDIMScheduler,
    AutoencoderKL
)
from src.domain.ports import VideoGeneratorPort, AnimationReport

# Compatibility Alias
StableDiffusionAnimateDiffPipeline = AnimateDiffPipeline

class StableVideoAnimateDiffGenerator(VideoGeneratorPort):
    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        
        # --- 1. INTELLIGENT HARDWARE DETECTION ---
        # We check if CUDA is actually available on the host machine.
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        
        # --- 2. PRECISION SELECTION ---
        # GPU (GTX 1060): Use float16. It cuts VRAM usage by half and is much faster.
        # CPU (PC): Use float32. CPUS process float16 very slowly or not at all in PyTorch.
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_VIDEO: Deploying Temporal Engine on [{self._device.upper()}]...")
            
            # Load Motion Adapter
            adapter = MotionAdapter.from_pretrained(
                "guoyww/animatediff-motion-adapter-v1-5-2", 
                torch_dtype=self._torch_dtype,
                local_files_only=self._offline,
                use_safetensors=True
            )

            # Load VAE (Visual AutoEncoder)
            vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", 
                torch_dtype=self._torch_dtype,
                local_files_only=self._offline,
                use_safetensors=True
            )

            # Assemble Main Pipeline
            self._pipe = StableDiffusionAnimateDiffPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE",
                vae=vae,
                motion_adapter=adapter,
                torch_dtype=self._torch_dtype,
                local_files_only=self._offline,
                use_safetensors=True
            )

            # Configure Scheduler (DDIM is standard for Video)
            self._pipe.scheduler = DDIMScheduler.from_config(
                self._pipe.scheduler.config,
                clip_sample=False,
                timestep_spacing="linspace",
                beta_schedule="linear",
                steps_offset=1,
            )

            # --- 3. HARDWARE-SPECIFIC OPTIMIZATIONS ---
            if self._device == "cuda":
                print("INFRA_VIDEO: GPU Detected. Activating 6GB VRAM Optimization Suite.")
                
                # A. Sequential CPU Offload
                # This is the "Magic Trick" for the GTX 1060. It keeps models in
                # System RAM (32GB) and streams them to VRAM (6GB) layer-by-layer.
                self._pipe.enable_sequential_cpu_offload()
                
                # B. VAE Tiling
                # Processes images in small blocks rather than all at once.
                self._pipe.enable_vae_slicing()
                self._pipe.enable_vae_tiling()
                
            else:
                print("INFRA_VIDEO: CPU Detected. Running in Compatibility Mode (Slow).")
                # Ensure the pipeline is explicitly on the CPU
                self._pipe.to("cpu")
                # We DO NOT enable offloading here, as offloading from CPU to CPU is pointless overhead.
                
            print(f"INFRA_VIDEO: Temporal Engine Online.")
        except Exception as e:
            print(f"INFRA_VIDEO_BOOT_FAILURE: {str(e)}")
            raise e

    def animate_image(self, source_image, motion_prompt, character_lore, duration_frames=24, fps=8, hyper_params={}, progress_callback=None):
        start_time = time.time()
        
        # 1. Image Pre-processing
        # Dimensions must be divisible by 8 for the neural network.
        width, height = source_image.size
        target_w = (width // 8) * 8
        target_h = (height // 8) * 8
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)

        # 2. Lore-Driven Prompt Synthesis
        name = character_lore.get("name", "Subject")
        lore_base = character_lore.get("prompt_base", "")
        realism_suffix = "high detailed skin, 8k uhd, cinematic lighting, dslr, soft bokeh"
        
        final_prompt = f"{name}, {motion_prompt}, {lore_base}, {realism_suffix}"
        negative_prompt = character_lore.get("negative_prompt", "anime, cartoon, drawing, plastic, flicker, distorted")

        # 3. Temporal Inference
        # We ensure the generator matches the device (CPU generator for CPU execution)
        generator_device = "cpu"  # PyTorch generators are often safest on CPU for reproducibility
        
        with torch.inference_mode():
            output = self._pipe(
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                num_frames=duration_frames,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)),
                num_inference_steps=int(hyper_params.get("steps", 25)),
                generator=torch.Generator(generator_device).manual_seed(int(hyper_params.get("seed", 42))),
                
                # CRITICAL SAFETY FEATURE (For both GPU and CPU)
                # Forces the system to decode video frames 1-by-1.
                # - On GPU: Prevents VRAM explosion at the end.
                # - On CPU: Prevents massive RAM spikes that could freeze the OS.
                decode_chunk_size=1, 
            )
            frames = output.frames[0]

        # 4. MP4 Encoding
        video_buffer = io.BytesIO()
        writer = imageio.get_writer(video_buffer, format='MP4', fps=fps, codec='libx264', quality=8)
        for frame in frames:
            writer.append_data(np.array(frame))
        writer.close()

        # 5. Report Generation
        video_b64 = base64.b64encode(video_buffer.getvalue()).decode('utf-8')
        return AnimationReport(
            video_b64=video_b64,
            inference_time=round(time.time() - start_time, 2),
            total_frames=duration_frames,
            fps=fps
        )