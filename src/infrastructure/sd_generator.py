# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Computational Core v19.7 - Restored Original Soul & Fidelity.
#
# ABSTRACT:
# This version serves as the definitive synthesis engine. It meticulously clones 
# the logic of the highly successful v19.1, restoring the "lucky" hyper-parameter 
# balances and prompt structures that provided superior color fidelity.
#
# KEY ARCHITECTURAL FEATURES (RESTORED):
# 1. White Background Protocol: Re-implemented the pasting of alpha-channel 
#    subjects onto solid white backgrounds. This is critical for preventing 
#    color "muddying" and keeping anime colors vibrant.
# 2. Rigid Prompt Anchoring: Restored the hardcoded cinematic suffix and 
#    the subject-name prefix. This ensures the Neural Engine locks onto the 
#    identity before applying textures.
# 3. Parameter Synchronization: Correctly maps 'strength', 'cn_depth', and 
#    'cn_pose' from the API/JSON manifold, while defaulting to the stable 
#    v19.1 ratios (0.65 / 0.60 / 0.75).
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
    stylized anime inputs into cinematic realism without losing subject identity.
    """

    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Deploying Engine v19.7 (Restored v19.1 Logic)...")
            
            # 1. Load VAE: ft-MSE is the gold standard for high-fidelity skin reconstruction.
            vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", torch_dtype=self._torch_dtype, local_files_only=self._offline
            ).to(self._device)

            # 2. Load ControlNet Weights: Depth (Geometry) + OpenPose (Anatomy).
            depth_net = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11f1p_sd15_depth", torch_dtype=self._torch_dtype, local_files_only=self._offline
            )
            openpose_net = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11p_sd15_openpose", torch_dtype=self._torch_dtype, local_files_only=self._offline
            )
            
            # 3. Load Pre-processors: Midas (3D Depth) and OpenPose detectors.
            self.depth_estimator = MidasDetector.from_pretrained('lllyasviel/ControlNet')
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # 4. Pipeline Assembly: Realistic_Vision_V5.1 is chosen for its superior human rendering.
            self._pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE", 
                vae=vae, 
                controlnet=[depth_net, openpose_net], 
                torch_dtype=self._torch_dtype, 
                safety_checker=None, 
                local_files_only=self._offline
            ).to(self._device)
            
            # Use DPM++ 2M Karras for clean convergence in fewer steps.
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++"
            )
            
            # 5. Hardware Acceleration (Memory optimizations)
            if self._device == "cuda":
                self._pipe.enable_xformers_memory_efficient_attention()
                self._pipe.enable_model_cpu_offload() 
                self._pipe.enable_vae_tiling()
                
            print(f"INFRA_AI: v19.7 Online. Original Soul Synchronized.")
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
        Main inference entry point. Executes character transformation using 
        v19.1's original image manifold and prompt synthesis rules.
        """
        
        # --- 1. TACTICAL PARAMETER EXTRACTION ---
        # Strength (Denoising) is defaulted to 0.65 to mirror v19.1's stable look.
        strength = float(hyper_params.get("strength", 0.65))
        nominal_steps = int(hyper_params.get("steps", 30))
        effective_steps = math.floor(nominal_steps * strength)
        
        # ControlNet Weights: Aligned with v19.1's stable defaults (0.60 Depth / 0.75 Pose)
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
        depth_map = self.depth_estimator(input_image)
        openpose_map = self.openpose_detector(input_image)

        # --- 4. PROMPT SYNTHESIS (Restored Original Architecture) ---
        # [Identity Anchor], [Custom Details], [Hardcoded Realism Suffix]
        # This exact structure ensures colors are locked before textures are applied.
        final_prompt = f"{prompt_guidance}, {feature_prompt}, high detailed skin, 8k uhd, cinematic lighting, dslr, soft bokeh"
        neg_prompt = hyper_params.get("negative_prompt", "anime, cartoon, drawing, illustration, plastic")

        # Telemetry linkage
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
                image=input_image,              # Starting manifold
                control_image=[depth_map, openpose_map], 
                strength=strength,              # Fidelity factor
                height=target_h, 
                width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=[cn_depth, cn_pose],
                num_inference_steps=nominal_steps,
                generator=torch.Generator(device=self._device).manual_seed(int(hyper_params.get("seed", 42))),
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