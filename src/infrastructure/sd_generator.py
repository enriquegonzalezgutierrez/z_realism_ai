# path: src/infrastructure/sd_generator.py
# description: Static Neural Core v21.6 - Contrast & Chromatic Fix.
#              Optimized for high-fidelity Subject DNA synthesis.
#
# ARCHITECTURAL ROLE (Infrastructure Adapter):
# This module implements the 'ImageGeneratorPort'. It acts as the primary 
# synthesis engine, transforming stylized 2D manifolds into high-entropy 
# cinematic environments while preserving structural and chromatic DNA.
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

# Linear Latent-to-RGB projection factors for high-performance telemetry.
LATENT_RGB_FACTORS = [
    [0.298, 0.187, -0.158],
    [0.207, 0.286, 0.189],
    [0.208, 0.189, 0.266],
    [-0.149, -0.071, -0.045]
]

class StableDiffusionGenerator(ImageGeneratorPort):
    """
    Advanced Multi-Conditioning Engine for Photorealistic Character Synthesis.
    
    Optimized for high-fidelity transformation of stylized manifolds via 
    context-aware pre-processing and VRAM-efficient orchestration.
    """

    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Deploying Static Engine on [{self._device.upper()}]...")
            
            # 1. Load Vision Components
            vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", 
                torch_dtype=self._torch_dtype, 
                local_files_only=self._offline
            )

            # 2. Load ControlNet Adapters (Geometry + Anatomy)
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
            
            self.depth_estimator = MidasDetector.from_pretrained('lllyasviel/ControlNet')
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # 3. Assemble Pipeline: Realistic_Vision_V5.1
            self._pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE", 
                vae=vae, 
                controlnet=[depth_net, openpose_net], 
                torch_dtype=self._torch_dtype, 
                safety_checker=None, 
                local_files_only=self._offline
            )
            
            self._pipe.to(self._device)
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, 
                use_karras_sigmas=True, 
                algorithm_type="dpmsolver++"
            )
            
            # --- 4. HARDWARE ORCHESTRATION (GTX 1060 Candidate) ---
            if self._device == "cuda":
                try:
                    self._pipe.enable_xformers_memory_efficient_attention()
                except Exception: pass
                
                # Model CPU Offload: Streams weights layer-by-layer to VRAM.
                self._pipe.enable_model_cpu_offload() 
                self._pipe.enable_vae_tiling()
                
            print(f"INFRA_AI: Static Engine Online v21.6.")
        except Exception as e:
            print(f"INFRA_AI_BOOT_FAILURE: {e}")
            raise e

    def _decode_preview(self, latents: torch.Tensor) -> str:
        """Linear latent projection for real-time visual telemetry."""
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
        Executes Subject Transformation with context-aware pre-processing.
        """
        
        # --- 1. PARAMETER EXTRACTION ---
        strength = float(hyper_params.get("strength", 0.65))
        nominal_steps = int(hyper_params.get("steps", 30))
        effective_steps = math.floor(nominal_steps * strength)
        
        cn_depth = float(hyper_params.get("cn_depth", 0.75))
        cn_pose = float(hyper_params.get("cn_pose", 0.40))
        
        # --- 2. MANIFOLD PRE-PROCESSING (Context-Aware Fix) ---
        target_w, target_h = self._calculate_proportional_dimensions(
            source_image.width, source_image.height, resolution_anchor
        )
        
        # FIX v21.6: Only apply background restoration for transparent manifolds (RGBA).
        # This prevents desaturation leaks on characters with naturally black backgrounds.
        if source_image.mode == 'RGBA':
            source_image = source_image.convert("RGBA")
            background = Image.new("RGB", source_image.size, (255, 255, 255))
            background.paste(source_image, mask=source_image.split()[3])
            input_image = background.convert("RGB")
        else:
            # Respect the original contrast of the Subject (e.g., pure black void).
            input_image = source_image.convert("RGB")
            
        input_image = input_image.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # --- 3. NEURAL CONDITIONING ---
        depth_map = self.depth_estimator(input_image)
        openpose_map = self.openpose_detector(input_image)

        # --- 4. SEMANTIC SYNTHESIS ---
        # Identity Anchor + Textural Guidance
        final_prompt = f"{prompt_guidance}, {feature_prompt}, highly detailed textures, 8k, cinematic lighting"
        neg_prompt = hyper_params.get("negative_prompt", "anime, drawing, plastic, low quality")

        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback and i % 2 == 0:
                preview_b64 = self._decode_preview(callback_kwargs["latents"])
                progress_callback(i + 1, effective_steps, preview_b64)
            return callback_kwargs

        # --- 5. NEURAL INFERENCE ---
        with torch.inference_mode():
            output = self._pipe(
                prompt=final_prompt, 
                negative_prompt=neg_prompt,
                image=input_image, 
                control_image=[depth_map, openpose_map], 
                strength=strength, 
                height=target_h, 
                width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=[cn_depth, cn_pose],
                num_inference_steps=nominal_steps,
                generator=torch.Generator(device="cpu").manual_seed(int(hyper_params.get("seed", 42))),
                callback_on_step_end=internal_callback
            ).images[0]

        return output, final_prompt, neg_prompt

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        """Calculates dimensions divisible by 8 for latent manifold consistency."""
        aspect = width / height
        if width >= height:
            new_w = resolution_anchor
            new_h = int(resolution_anchor / aspect)
        else:
            new_h = resolution_anchor
            new_w = int(resolution_anchor * aspect)
        return (new_w // 8) * 8, (new_h // 8) * 8