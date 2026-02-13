# path: src/infrastructure/sd_generator.py
# description: Neural Synthesis Core v26.6 - Full Transparency Release.
#              This version has zero hardcoded values in the inference pipeline.
#
# ARCHITECTURAL ROLE (Infrastructure Adapter):
# This module implements the 'ImageGeneratorPort', serving as the primary 
# high-fidelity synthesis engine. It uses a Dual-Anchor conditioning system 
# (Depth + Canny) with fully dynamic weight and sensitivity balancing.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import cv2
import os
import io
import base64
import math
import warnings
from typing import Callable, Optional, Tuple, Dict, Any
from PIL import Image

from controlnet_aux import MidasDetector, CannyDetector
from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline,
    ControlNetModel, 
    DPMSolverMultistepScheduler,
    AutoencoderKL
)
from src.domain.ports import ImageGeneratorPort

class StableDiffusionGenerator(ImageGeneratorPort):
    """
    Expert Neural Core for Stylized-to-Photorealistic Transformation.
    Engineered for precision, stability, and character-DNA integrity.
    """

    def __init__(self, device: str = "cpu"):
        warnings.filterwarnings("ignore", category=UserWarning, message=".*Plan failed with a cudnnException.*")
        
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Deploying Engine v26.6 [Full_Transparency] on [{self._device.upper()}]...")
            
            if self._device == "cuda":
                torch.backends.cudnn.benchmark = False
                torch.backends.cudnn.deterministic = True

            vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=self._torch_dtype, local_files_only=self._offline).to(self._device)
            depth_net = ControlNetModel.from_pretrained("lllyasviel/control_v11f1p_sd15_depth", torch_dtype=self._torch_dtype, local_files_only=self._offline)
            canny_net = ControlNetModel.from_pretrained("lllyasviel/control_v11p_sd15_canny", torch_dtype=self._torch_dtype, local_files_only=self._offline)
            
            self.depth_estimator = MidasDetector.from_pretrained('lllyasviel/ControlNet')
            self.canny_detector = CannyDetector()

            self._pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE", 
                vae=vae, controlnet=[depth_net, canny_net],
                torch_dtype=self._torch_dtype, safety_checker=None, local_files_only=self._offline
            )
            
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(self._pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++")
            if self._device == "cuda":
                self._pipe.enable_model_cpu_offload() 
                
            print(f"INFRA_AI: v26.6 Online. Ready for dynamic Subject DNA injection.")
        except Exception as e:
            print(f"INFRA_AI_BOOT_FAILURE: {e}")
            raise e

    def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str, 
        feature_prompt: str, 
        resolution_anchor: int, 
        hyper_params: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[Image.Image, str, str]:
        
        strength = float(hyper_params.get("strength", 0.55))
        nominal_steps = int(hyper_params.get("steps", 30))
        effective_steps = math.floor(nominal_steps * strength)
        
        cn_depth_weight = float(hyper_params.get("cn_depth", 0.80))
        cn_canny_weight = float(hyper_params.get("cn_pose", 0.70)) # Mapped from 'cn_pose'
        
        canny_low = int(hyper_params.get("canny_low", 100))
        canny_high = int(hyper_params.get("canny_high", 200))
        
        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        
        if source_image.mode == 'RGBA':
            background = Image.new("RGB", source_image.size, (255, 255, 255))
            background.paste(source_image, mask=source_image.split()[3])
            input_image = background.convert("RGB")
        else:
            input_image = source_image.convert("RGB")
            
        input_image = input_image.resize((target_w, target_h), Image.Resampling.LANCZOS)

        depth_map = self.depth_estimator(input_image).resize((target_w, target_h))
        canny_map = self.canny_detector(input_image, low_threshold=canny_low, high_threshold=canny_high).resize((target_w, target_h))

        final_prompt = f"photorealistic cinematic photo, {prompt_guidance}, {feature_prompt}, highly detailed, 8k, realistic lighting"
        neg_prompt = hyper_params.get("negative_prompt", "anime, drawing, plastic, low quality, illustration")

        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback: progress_callback(i + 1, effective_steps, None)
            return callback_kwargs

        with torch.inference_mode():
            output = self._pipe(
                prompt=final_prompt, 
                negative_prompt=neg_prompt,
                image=input_image,
                control_image=[depth_map, canny_map], 
                strength=strength, 
                height=target_h, 
                width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=[cn_depth_weight, cn_canny_weight],
                num_inference_steps=nominal_steps,
                generator=torch.Generator(device="cpu").manual_seed(int(hyper_params.get("seed", 42))),
                callback_on_step_end=internal_callback
            ).images[0]

        return output, final_prompt, neg_prompt

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        """
        Calculates manifold dimensions aligned to a 64-pixel grid while minimizing 
        aspect ratio distortion through nearest-multiple rounding.
        """
        aspect = width / height
        if width >= height:
            new_w = resolution_anchor
            new_h = resolution_anchor / aspect
        else:
            new_h = resolution_anchor
            new_w = resolution_anchor * aspect
            
        # THE DOCTORAL FIX: Using round() instead of floor (//) to reach the 
        # closest 64-pixel boundary, preserving original proportions.
        return (int(round(new_w / 64) * 64), int(round(new_h / 64) * 64))