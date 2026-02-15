# path: src/infrastructure/video_generator.py
# description: Neural Temporal Engine v28.0 - "Channels Last" Performance Tune.
#              Mirroring the static generator optimizations for the AnimateDiff pipeline.
#
# ARCHITECTURAL ROLE (Infrastructure Adapter):
# Implements the 'VideoGeneratorPort'. Focuses on maximizing throughput for
# temporal tensor operations on GTX 10-series hardware.
#
# MODIFICATION LOG v28.0:
# - Enabled torch.backends.cudnn.benchmark = True.
# - Converted 3D UNet and Motion Modules to 'channels_last' format.
# - Maintained Sequential CPU Offload for VRAM safety.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import imageio
import io
import base64
import time
import os
import warnings
from typing import Callable, Optional, Tuple, Dict, Any, List
from PIL import Image

# Essential for memory efficient attention check
import xformers

from diffusers import (
    AnimateDiffPipeline, 
    MotionAdapter, 
    DDIMScheduler,
    AutoencoderKL
)
from src.domain.ports import VideoGeneratorPort, AnimationReport

class StableVideoAnimateDiffGenerator(VideoGeneratorPort):
    """
    Advanced Temporal Synthesis Engine based on the AnimateDiff framework.
    
    Optimized for high-latency video generation on consumer-grade hardware (GTX 1060)
    via aggressive memory orchestration and precision management.
    """

    def __init__(self, device: str = "cpu"):
        warnings.filterwarnings("ignore", category=UserWarning, message=".*Plan failed with a cudnnException.*")
        
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_VIDEO: Deploying Temporal Engine v28.0 [Channels_Last_Optimized] on [{self._device.upper()}]...")
            
            # --- PERFORMANCE TUNING v28.0 ---
            if self._device == "cuda":
                # Benchmark: Allows CuDNN to find the fastest convolution algorithm for your GPU.
                # First run might be slightly slower (warmup), subsequent runs are faster.
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False # Relax determinism slightly for speed

            # COMPONENT LOADING
            adapter = MotionAdapter.from_pretrained(
                "guoyww/animatediff-motion-adapter-v1-5-2", 
                torch_dtype=self._torch_dtype,
                local_files_only=self._offline,
                use_safetensors=True
            )

            vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", 
                torch_dtype=self._torch_dtype, 
                local_files_only=self._offline,
                use_safetensors=True
            )

            # PIPELINE ASSEMBLY
            self._pipe = AnimateDiffPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE",
                vae=vae,
                motion_adapter=adapter,
                torch_dtype=self._torch_dtype,
                local_files_only=self._offline,
                use_safetensors=True
            )

            self._pipe.scheduler = DDIMScheduler.from_config(
                self._pipe.scheduler.config,
                clip_sample=False,
                timestep_spacing="linspace",
                beta_schedule="linear",
                steps_offset=1,
            )

            # --- CRITICAL OPTIMIZATION SUITE v28.0 ---
            if self._device == "cuda":
                # 1. xFormers (Essential for Temporal Attention)
                try:
                    self._pipe.enable_xformers_memory_efficient_attention()
                    print("INFRA_VIDEO: xFormers Active.")
                except Exception as e:
                    print(f"INFRA_VIDEO: WARNING - xFormers failed: {e}")

                # 2. Channels Last Memory Format (Speed Boost)
                # Applying this to the 3D UNet is tricky but beneficial.
                self._pipe.unet.to(memory_format=torch.channels_last)
                print("INFRA_VIDEO: 3D UNet converted to Channels Last format.")

                # 3. Sequential CPU Offload (VRAM Safety Net)
                # Mandatory for 6GB VRAM. Unloads modules aggressively to RAM.
                self._pipe.enable_sequential_cpu_offload()
                
                # 4. VAE Slicing (Decoding Safety)
                self._pipe.enable_vae_slicing()
                
            else:
                self._pipe.to("cpu")
                
            print(f"INFRA_VIDEO: v28.0 Online. Performance Tuning Complete.")
        except Exception as e:
            print(f"INFRA_VIDEO_BOOT_FAILURE: {str(e)}")
            raise e

    def animate_image(
        self, 
        source_image: Image.Image, 
        motion_prompt: str, 
        subject_metadata: Dict[str, Any], 
        duration_frames: int = 24, 
        fps: int = 8, 
        hyper_params: Dict[str, Any] = {}, 
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> AnimationReport:
        
        start_time = time.time()
        
        # 1. Manifold Pre-processing (Enforced 64-px grid)
        width, height = source_image.size
        target_w = (width // 64) * 64
        target_h = (height // 64) * 64
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)

        # 2. Prompt Synthesis
        dna_base = subject_metadata.get("prompt_base", "")
        final_prompt = f"photorealistic cinematic video, {dna_base}, {motion_prompt}, high quality, 8k, detailed skin texture, natural light"
        negative_prompt = subject_metadata.get("negative_prompt", "anime, plastic, flicker, low quality, cartoon, drawing")

        # 3. Temporal Neural Inference
        if progress_callback: 
            progress_callback(0, duration_frames, "status_generating")

        with torch.inference_mode():
            output = self._pipe(
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                num_frames=duration_frames,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)),
                num_inference_steps=int(hyper_params.get("steps", 25)),
                generator=torch.Generator("cpu").manual_seed(int(hyper_params.get("seed", 42))),
                decode_chunk_size=1, # Decode one frame at a time to save VRAM
            )
            frames = output.frames[0]

        # 4. Container Encoding
        video_buffer = io.BytesIO()
        writer = imageio.get_writer(
            video_buffer, 
            format='MP4', 
            fps=fps, 
            codec='libx264', 
            quality=8
        )
        
        for i, frame in enumerate(frames):
            writer.append_data(np.array(frame))
            if progress_callback:
                progress_callback(i + 1, duration_frames, "status_encoding")
        writer.close()

        # 5. Report Generation
        video_b64 = base64.b64encode(video_buffer.getvalue()).decode('utf-8')
        
        return AnimationReport(
            video_b64=video_b64,
            inference_time=round(time.time() - start_time, 2),
            total_frames=duration_frames,
            fps=fps
        )