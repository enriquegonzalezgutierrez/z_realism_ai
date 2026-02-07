# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Computational Core v19.0 - Lore-Compliant Agnostic Engine.
#
# ABSTRACT:
# This module implements a high-fidelity, multi-modal Stable Diffusion engine. 
# In version 19.0, the architecture is 'Agnostic,' meaning it possesses no 
# internal heuristics; instead, it utilizes a lore-driven hyper-parameter 
# payload to execute character-specific synthesis strategies.
#
# KEY ARCHITECTURAL FEATURES:
# 1. Stochastic Identity Inheritance: Utilizes Img2Img refinement to preserve 
#    the source color manifold without relying on unstable external adapters.
# 2. Granular Conditioning: Dynamically maps decoupled weights (Depth vs. Pose) 
#    as specified by the Domain Lore to mitigate anatomical distortion.
# 3. Micro-Textural Fidelity: Employs an MSE-tuned Variational Autoencoder (VAE) 
#    to synthesize realistic skin pores and professional cinematic lighting.
# 4. Telemetry Calibration: Synchronizes internal diffusion steps with effective 
#    de-noising iterations to ensure 100% UI progress bar accuracy.
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
from PIL import Image, ImageOps

from controlnet_aux import OpenposeDetector 
from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline, 
    ControlNetModel, 
    DPMSolverMultistepScheduler,
    AutoencoderKL
)
from src.domain.ports import ImageGeneratorPort

# Linear Latent-to-RGB projection factors for real-time visual telemetry
LATENT_RGB_FACTORS = [[0.298, 0.187, -0.158],[0.207, 0.286, 0.189],[0.208, 0.189, 0.266],[-0.149, -0.071, -0.045]]

class StableDiffusionGenerator(ImageGeneratorPort):
    """
    Advanced Multi-Conditioning Engine for Photorealistic Character Synthesis.
    """

    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Deploying Engine v19.0 (Agnostic Lore-Centric)...")
            
            # 1. High-Fidelity Reconstruction Components
            vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", torch_dtype=self._torch_dtype, local_files_only=self._offline
            ).to(self._device)

            # 2. Structural Anchors
            depth_net = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11f1p_sd15_depth", torch_dtype=self._torch_dtype, local_files_only=self._offline
            )
            openpose_net = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11p_sd15_openpose", torch_dtype=self._torch_dtype, local_files_only=self._offline
            )
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # 3. Agnostic Pipeline Assembly
            # Img2Img is used for maximum identity preservation and crash-proof stability.
            self._pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE", 
                vae=vae, 
                controlnet=[depth_net, openpose_net], 
                torch_dtype=self._torch_dtype, 
                safety_checker=None, 
                local_files_only=self._offline
            ).to(self._device)
            
            # Optimized Convergence Schedule
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++"
            )
            
            # 4. Hardware Acceleration Profiles
            if self._device == "cuda":
                self._pipe.enable_xformers_memory_efficient_attention()
                self._pipe.enable_model_cpu_offload() 
                self._pipe.enable_vae_tiling()
                
            print(f"INFRA_AI: v19.0 Online. Ready for tactical instructions.")
        except Exception as e:
            print(f"INFRA_AI_BOOT_FAILURE: {e}")
            raise e

    def _decode_preview(self, latents: torch.Tensor) -> str:
        """Linear approximation of the VAE decoding process for UI feedback."""
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
        Executes character-specific synthesis based on dynamic tactical constraints.
        """
        
        # --- 1. TACTICAL PARAMETER EXTRACTION ---
        strength = float(hyper_params.get("strength", 0.70))
        nominal_steps = int(hyper_params.get("steps", 30))
        effective_steps = math.floor(nominal_steps * strength)
        
        # Aligned weights for Multi-ControlNet: [Depth, Pose]
        cn_scales = [
            float(hyper_params.get("cn_depth", 0.75)), 
            float(hyper_params.get("cn_pose", 0.45))
        ]
        
        # --- 2. MANIFOLD PRE-PROCESSING ---
        target_w, target_h = self._calculate_proportional_dimensions(
            source_image.width, source_image.height, resolution_anchor
        )
        
        # Contextual infilling for transparency support (Cinematic Neutral)
        if source_image.mode == "RGBA":
            bg = Image.new("RGBA", source_image.size, (255, 255, 255, 255))
            bg.paste(source_image, (0, 0), source_image)
            source_image = bg.convert("RGB")
        else:
            source_image = source_image.convert("RGB")

        input_image = ImageOps.fit(source_image, (target_w, target_h), method=Image.LANCZOS)
        
        # Structural signal generation
        gray = cv2.cvtColor(np.array(input_image), cv2.COLOR_RGB2GRAY)
        depth_map = Image.fromarray(np.stack([cv2.GaussianBlur(gray, (7, 7), 0)]*3, axis=-1))
        openpose_map = self.openpose_detector(input_image)

        # --- 3. CLIP TOKEN SANITIZATION (The 77-Token Guard) ---
        raw_fragments = [
            "raw photo, cinematic film still", 
            feature_prompt, 
            "masterpiece, 8k uhd, highly detailed skin pores"
        ]
        all_words = []
        for frag in raw_fragments: all_words.extend([w.strip().lower() for w in frag.split(',')])
        seen = set()
        clean_tokens = [w for w in all_words if w and not (w in seen or seen.add(w))]
        
        final_prompt = ", ".join(clean_tokens[:70])
        neg_prompt = hyper_params.get("negative_prompt", "anime, cartoon, low quality")

        # Telemetry linkage
        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback and i % 2 == 0:
                preview_b64 = self._decode_preview(callback_kwargs["latents"])
                progress_callback(i + 1, effective_steps, preview_b64)
            return callback_kwargs

        # --- 4. NEURAL INFERENCE (Img2Img + ControlNet) ---
        with torch.no_grad():
            output = self._pipe(
                prompt=final_prompt, 
                negative_prompt=neg_prompt,
                image=input_image,              # Color/Identity anchor
                control_image=[depth_map, openpose_map], 
                strength=strength,              # Stochastic ratio from lore
                height=target_h, 
                width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=cn_scales, # Decoupled weights from lore
                num_inference_steps=nominal_steps,
                generator=torch.Generator(device=self._device).manual_seed(int(hyper_params.get("seed", 42))),
                callback_on_step_end=internal_callback
            ).images[0]

        return output, final_prompt, neg_prompt

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        aspect = width / height
        if width >= height:
            new_w = resolution_anchor
            new_h = int(resolution_anchor / aspect)
        else:
            new_h = resolution_anchor
            new_w = int(resolution_anchor * aspect)
        return (new_w // 8) * 8, (new_h // 8) * 8