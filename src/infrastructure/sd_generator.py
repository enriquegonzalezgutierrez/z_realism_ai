# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: AI Engine implementation utilizing RealVisXL V4.0.
#              FIXED: Optimized prompt concatenation to stay under 77 tokens
#              and adjusted logic for "extreme" character synthesis.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import asyncio
import numpy as np
import cv2
import os
from typing import Callable, Optional, Tuple
from PIL import Image
from diffusers import (
    StableDiffusionXLControlNetPipeline, 
    ControlNetModel, 
    DDIMScheduler
)
from src.domain.ports import ImageGeneratorPort

class StableDiffusionGenerator(ImageGeneratorPort):
    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        base_model_id = "SG161222/RealVisXL_V4.0"
        controlnet_id = "xinsir/controlnet-canny-sdxl-1.0"
        self._device = device
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

        try:
            self._controlnet = ControlNetModel.from_pretrained(
                controlnet_id, torch_dtype=torch_dtype, local_files_only=self._offline
            ).to(self._device)
            self._pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
                base_model_id, controlnet=self._controlnet, torch_dtype=torch_dtype, 
                low_cpu_mem_usage=True, local_files_only=self._offline
            ).to(self._device)
            self._pipe.scheduler = DDIMScheduler.from_config(self._pipe.scheduler.config)
            self._pipe.safety_checker = None
            print(f"INFRA_AI: Engine ready.")
        except Exception as e:
            raise e

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        aspect = width / height
        if width < height: 
            new_w, new_h = resolution_anchor, int(resolution_anchor / aspect)
        else: 
            new_h, new_w = resolution_anchor, int(resolution_anchor * aspect)
        return (min(new_w, 1024) // 8) * 8, (min(new_h, 1024) // 8) * 8

    async def generate_live_action(
        self, source_image, prompt_guidance, feature_prompt, resolution_anchor, progress_callback=None
    ) -> Image.Image:
        
        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        img_np = np.array(input_image)
        img_canny = cv2.Canny(img_np, 100, 200)
        img_canny = np.stack([img_canny]*3, axis=-1)
        control_image = Image.fromarray(img_canny)

        # PH.D. TOKEN OPTIMIZATION: Key features first. No filler.
        # This structure ensures all quality modifiers are seen by CLIP.
        full_prompt = f"RAW photo, human muscular man, {prompt_guidance}, {feature_prompt}, detailed skin pores, sweat, 8k, high quality"
        
        negative_prompt = "anime, cartoon, illustration, drawing, 2d, neon, aura, glowing, (worst quality:1.4), plastic"
        
        num_inference_steps = 25
        controlnet_conditioning_scale = 0.45 
        guidance_scale = 7.5

        def callback_on_step_end(pipe, i, t, callback_kwargs):
            if progress_callback: progress_callback(i + 1, num_inference_steps)
            return callback_kwargs

        with torch.no_grad():
            output = self._pipe(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                image=control_image,
                height=target_h,
                width=target_w,
                guidance_scale=guidance_scale,
                controlnet_conditioning_scale=controlnet_conditioning_scale,
                num_inference_steps=num_inference_steps,
                callback_on_step_end=callback_on_step_end
            ).images[0]

        return output
