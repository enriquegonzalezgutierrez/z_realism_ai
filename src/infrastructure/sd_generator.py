# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Core v20.2 - Hybrid CPU/GPU Support.
#
# ABSTRACT:
# This module implements the Stable Diffusion pipeline for Static Image Generation.
# It acts as the definitive "Photorealism Engine" (restoring v19.1 logic).
#
# CRITICAL LOGIC (v20.2):
# 1. Hardware Agnostic: Automatically detects if CUDA is available.
# 2. Conditional Optimization: 
#    - GPU: Enables xFormers and Model CPU Offloading for 6GB VRAM support.
#    - CPU: Disables xFormers (incompatible) and uses standard execution.
# 3. Precision Management: Switches between float16 (GPU) and float32 (CPU).
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import cv2
import os
import io
import base64
import math
from typing import Callable, Optional, Tuple, Dict, Any, List
from PIL import Image

from controlnet_aux import OpenposeDetector, MidasDetector
from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline, 
    ControlNetModel, 
    DPMSolverMultistepScheduler,
    AutoencoderKL
)
from src.domain.ports import ImageGeneratorPort

# Linear Latent-to-RGB projection factors for real-time visual telemetry.
# Enables the UI to show the de-noising progress in real-time.
LATENT_RGB_FACTORS = [[0.298, 0.187, -0.158],[0.207, 0.286, 0.189],[0.208, 0.189, 0.266],[-0.149, -0.071, -0.045]]

class StableDiffusionGenerator(ImageGeneratorPort):
    """
    Advanced Multi-Conditioning Engine for Photorealistic Character Synthesis.
    
    A hybrid Img2Img + Dual ControlNet pipeline optimized for transforming 
    stylized anime inputs into cinematic realism.
    """

    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        
        # --- 1. INTELLIGENT HARDWARE DETECTION ---
        # We verify if CUDA is actually available on the host.
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        
        # --- 2. PRECISION SELECTION ---
        # GPU (GTX 1060): float16 (Standard for Stable Diffusion on GPU).
        # CPU (PC): float32. PyTorch operations on CPU often fail or are slow with float16.
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Deploying Static Engine on [{self._device.upper()}]...")
            
            # Load VAE (Variational Auto-Encoder)
            # ft-mse is crucial for realistic eyes and faces.
            vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", 
                torch_dtype=self._torch_dtype, 
                local_files_only=self._offline
            )

            # Load ControlNet Weights: Depth (Geometry) + OpenPose (Anatomy).
            depth_net = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11f1p_sd15_depth", 
                torch_dtype=self._torch_dtype, 
                local_files_only=self._offline
            )
            openpose_net = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11p_sd15_openpose", 
                torch_dtype=self._torch_dtype, 
                local_files_only=self._offline
            )
            
            # Load Pre-processors (Midas & OpenPose)
            self.depth_estimator = MidasDetector.from_pretrained('lllyasviel/ControlNet')
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # Pipeline Assembly: Realistic_Vision_V5.1
            self._pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE", 
                vae=vae, 
                controlnet=[depth_net, openpose_net], 
                torch_dtype=self._torch_dtype, 
                safety_checker=None, 
                local_files_only=self._offline
            )
            
            # Explicitly move pipe to device (Required for CPU execution too)
            self._pipe.to(self._device)
            
            # Scheduler Configuration
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, 
                use_karras_sigmas=True, 
                algorithm_type="dpmsolver++"
            )
            
            # --- 3. HARDWARE-SPECIFIC OPTIMIZATIONS ---
            if self._device == "cuda":
                # NVIDIA GPU Optimization (Laptop)
                try:
                    # xFormers is a specific library for NVIDIA GPUs. 
                    # If tried on CPU, it crashes the app.
                    self._pipe.enable_xformers_memory_efficient_attention()
                except Exception:
                    print("INFRA_AI: xFormers library not found, skipping optimization.")
                
                # Model CPU Offload: Moves inactive components to RAM. Critical for 6GB VRAM.
                self._pipe.enable_model_cpu_offload() 
                self._pipe.enable_vae_tiling()
                
            else:
                # CPU Optimization (PC)
                # We do NOT enable offloading or xformers.
                # Standard execution is safer for CPU.
                print("INFRA_AI: CPU Mode active. Disabling GPU-specific memory hacks.")
                
            print(f"INFRA_AI: Static Engine Online. v20.2 Ready.")
        except Exception as e:
            print(f"INFRA_AI_BOOT_FAILURE: {e}")
            raise e

    def _decode_preview(self, latents: torch.Tensor) -> str:
        """Linear approximation of the VAE decoding for intermediate UI feedback."""
        with torch.no_grad():
            latent_img = latents[0].permute(1, 2, 0).cpu() 
            factors = torch.tensor(LATENT_RGB_FACTORS, dtype=latent_img.dtype)
            rgb_img = ((latent_img @ factors) + 1.0) / 2.0
            image = (rgb_img.clamp(0, 1).numpy() * 255).astype("uint8")
            buffered = io.BytesIO()
            Image.fromarray(image).resize((256, 256)).save(buffered, format="JPEG", quality=40)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str, 
        feature_prompt: str, 
        resolution_anchor: int, 
        hyper_params: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[Image.Image, str, str]:
        """
        Main inference entry point. Executes character transformation.
        """
        
        # --- 1. TACTICAL PARAMETER EXTRACTION ---
        strength = float(hyper_params.get("strength", 0.65))
        nominal_steps = int(hyper_params.get("steps", 30))
        effective_steps = math.floor(nominal_steps * strength)
        
        cn_depth = float(hyper_params.get("cn_depth", 0.60))
        cn_pose = float(hyper_params.get("cn_pose", 0.75))
        
        # --- 2. MANIFOLD PRE-PROCESSING (White Background Restoration) ---
        target_w, target_h = self._calculate_proportional_dimensions(
            source_image.width, source_image.height, resolution_anchor
        )
        
        if source_image.mode in ('P', 'LA', 'RGBA'):
            source_image = source_image.convert("RGBA")
            # RESTORED: Pasting on solid white prevents muddy colors on transparent subjects.
            background = Image.new("RGB", source_image.size, (255, 255, 255))
            background.paste(source_image, mask=source_image.split()[3])
            input_image = background.convert("RGB")
        else:
            input_image = source_image.convert("RGB")
            
        input_image = input_image.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # --- 3. NEURAL MAP GENERATION ---
        # Note: Pre-processors usually run on CPU or GPU automatically depending on installation
        depth_map = self.depth_estimator(input_image)
        openpose_map = self.openpose_detector(input_image)

        # --- 4. PROMPT SYNTHESIS (Restored Original Architecture) ---
        final_prompt = f"{prompt_guidance}, {feature_prompt}, high detailed skin, 8k uhd, cinematic lighting, dslr, soft bokeh"
        neg_prompt = hyper_params.get("negative_prompt", "anime, cartoon, drawing, illustration, plastic")

        # Telemetry linkage
        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback and i % 2 == 0:
                preview_b64 = self._decode_preview(callback_kwargs["latents"])
                progress_callback(i + 1, effective_steps, preview_b64)
            return callback_kwargs

        # --- 5. NEURAL INFERENCE ---
        
        # Determine generator device (CPU generator is safer for reproducibility across hardware)
        # But for performance on GPU, we can use the GPU device.
        generator_device = self._device
        if self._device == "cpu":
             generator_device = "cpu"

        with torch.inference_mode():
            output = self._pipe(
                prompt=final_prompt, 
                negative_prompt=neg_prompt,
                image=input_image,              # Starting manifold
                control_image=[depth_map, openpose_map], 
                strength=strength,              # Fidelity factor
                height=target_h, 
                width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=[cn_depth, cn_pose],
                num_inference_steps=nominal_steps,
                generator=torch.Generator(device=generator_device).manual_seed(int(hyper_params.get("seed", 42))),
                callback_on_step_end=internal_callback
            ).images[0]

        return output, final_prompt, neg_prompt

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        """Calculates dimensions proportional to the anchor, divisible by 8."""
        aspect = width / height
        if width >= height:
            new_w = resolution_anchor
            new_h = int(resolution_anchor / aspect)
        else:
            new_h = resolution_anchor
            new_w = int(resolution_anchor * aspect)
        return (new_w // 8) * 8, (new_h // 8) * 8