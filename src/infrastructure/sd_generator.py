# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: AI Engine implementation utilizing RealVisXL V4.0.
#              FIXED: Optimized prompt structure for SDXL dual-encoder attention
#              and adjusted logic for "extreme" character synthesis.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
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

    def generate_live_action(
        self, source_image, prompt_guidance, feature_prompt, resolution_anchor, progress_callback=None
    ) -> Image.Image:
        
        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        img_np = np.array(input_image)
        img_blur = cv2.GaussianBlur(img_np, (5, 5), 0)
        img_canny = cv2.Canny(img_blur, 50, 150)
        img_canny = np.stack([img_canny]*3, axis=-1)
        control_image = Image.fromarray(img_canny)

        # PH.D. TOKEN OPTIMIZATION: Key features first. No filler.
        # This structure ensures all quality modifiers are seen by CLIP.
        full_prompt = (
            "RAW photo, live action, ultra realistic, cinematic lighting, "
            "real skin texture, visible pores, natural imperfections, subsurface scattering, "
            "35mm lens, shallow depth of field, sharp focus, "
            f"{prompt_guidance}, {feature_prompt}"
        )
        
        negative_prompt = (
            "anime, manga, cartoon, illustration, drawing, 2d, "
            "cgi, 3d render, unreal engine, video game, toy, doll, statue, "
            "plastic skin, smooth skin, wax skin, neon, glowing aura, "
            "oversaturated, low detail, worst quality"
        )
        
        num_inference_steps = 30
        controlnet_conditioning_scale = 0.70
        guidance_scale = 6.0

        def callback_on_step_end(pipe, i, t, callback_kwargs):
            if progress_callback: progress_callback(i + 1, num_inference_steps)
            return callback_kwargs

        with torch.no_grad():
            generator = torch.Generator(device=self._device).manual_seed(42)

            if self._device.startswith("cuda"):
                with torch.autocast("cuda"):
                    output = self._pipe(
                        prompt=full_prompt,
                        negative_prompt=negative_prompt,
                        image=control_image,
                        height=target_h,
                        width=target_w,
                        guidance_scale=guidance_scale,
                        controlnet_conditioning_scale=controlnet_conditioning_scale,
                        num_inference_steps=num_inference_steps,
                        generator=generator,
                        callback_on_step_end=callback_on_step_end
                    ).images[0]
            else:
                output = self._pipe(
                    prompt=full_prompt,
                    negative_prompt=negative_prompt,
                    image=control_image,
                    height=target_h,
                    width=target_w,
                    guidance_scale=guidance_scale,
                    controlnet_conditioning_scale=controlnet_conditioning_scale,
                    num_inference_steps=num_inference_steps,
                    generator=generator,
                    callback_on_step_end=callback_on_step_end
                ).images[0]


        return output
