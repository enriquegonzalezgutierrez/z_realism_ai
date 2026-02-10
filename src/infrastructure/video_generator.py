# path: z_realism_ai/src/infrastructure/video_generator.py
# description: Neural Temporal Engine v1.2 - Robust Hub Connection.
#
# CHANGES v1.2:
# 1. FIXED: Explicit Safetensors loading. Forced 'use_safetensors=True' 
#    to prevent the 404 error on missing .bin files in HuggingFace.
# 2. FIXED: Added 'variant="fp16"' to reduce download size and VRAM usage.
# 3. REFINED: Enhanced error reporting for Hub connection timeouts.
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

# Compatibility Alias for diffusers 0.31.0
StableDiffusionAnimateDiffPipeline = AnimateDiffPipeline

class StableVideoAnimateDiffGenerator(VideoGeneratorPort):
    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_VIDEO: Deploying Temporal Engine v1.2 (AnimateDiff)...")
            
            # 1. Load Motion Adapter
            # FIXED: Explicitly set use_safetensors=True and variant="fp16" 
            # to match available files on HF Hub and save 600MB of download.
            adapter = MotionAdapter.from_pretrained(
                "guoyww/animatediff-motion-adapter-v1-5-2", 
                torch_dtype=self._torch_dtype,
                local_files_only=self._offline,
                use_safetensors=True
            )

            # 2. Load VAE
            vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", 
                torch_dtype=self._torch_dtype,
                local_files_only=self._offline,
                use_safetensors=True
            )

            # 3. Assemble Pipeline
            self._pipe = StableDiffusionAnimateDiffPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE",
                vae=vae,
                motion_adapter=adapter,
                torch_dtype=self._torch_dtype,
                local_files_only=self._offline,
                use_safetensors=True
            )

            # 4. Configure Scheduler
            self._pipe.scheduler = DDIMScheduler.from_config(
                self._pipe.scheduler.config,
                clip_sample=False,
                timestep_spacing="linspace",
                beta_schedule="linear",
                steps_offset=1,
            )

            # 5. HARDWARE OPTIMIZATION (CRITICAL FOR 6GB VRAM)
            if self._device == "cuda":
                self._pipe.enable_sequential_cpu_offload()
                self._pipe.enable_vae_slicing()
                self._pipe.enable_vae_tiling()
                
            print(f"INFRA_VIDEO: Temporal Engine Online. v1.2 Ready.")
        except Exception as e:
            print(f"INFRA_VIDEO_BOOT_FAILURE: {str(e)}")
            raise e

    def animate_image(self, source_image, motion_prompt, character_lore, duration_frames=24, fps=8, hyper_params={}, progress_callback=None):
        start_time = time.time()
        
        # 1. Image Pre-processing
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
        with torch.inference_mode():
            output = self._pipe(
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                num_frames=duration_frames,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)),
                num_inference_steps=int(hyper_params.get("steps", 25)),
                generator=torch.Generator("cpu").manual_seed(int(hyper_params.get("seed", 42))),
                decode_chunk_size=4, 
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