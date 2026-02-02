# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: AI Engine utilizing Realistic Vision V6.0 (SD 1.5).
#              REFINED: Lowered ControlNet scale to 0.38 for anatomical humanization.
#              REFINED: Forced footwear semantics and banned barefoot/toes.
#              REFINED: Increased sampling steps for facial clarity.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import cv2
import os
from typing import Callable, Optional, Tuple
from PIL import Image
from diffusers import (
    StableDiffusionControlNetPipeline,
    ControlNetModel, 
    DDIMScheduler
)
from src.domain.ports import ImageGeneratorPort

class StableDiffusionGenerator(ImageGeneratorPort):
    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        base_model_id = "SG161222/Realistic_Vision_V6.0_B1_noVAE"
        controlnet_id = "lllyasviel/control_v11p_sd15_canny"
        
        if torch.cuda.is_available():
            self._device = "cuda"
            torch_dtype = torch.float16
        else:
            self._device = "cpu"
            torch_dtype = torch.float32

        try:
            self._controlnet = ControlNetModel.from_pretrained(
                controlnet_id, torch_dtype=torch_dtype, local_files_only=self._offline
            ).to(self._device)
            
            self._pipe = StableDiffusionControlNetPipeline.from_pretrained(
                base_model_id, controlnet=self._controlnet, torch_dtype=torch_dtype, 
                safety_checker=None 
            ).to(self._device)
            
            self._pipe.scheduler = DDIMScheduler.from_config(self._pipe.scheduler.config)
            
            if self._device == "cuda":
                self._pipe.enable_attention_slicing() 
                self._pipe.enable_model_cpu_offload() 
            
            print(f"INFRA_AI: Engine ready. DEVICE: {self._device.upper()}")
            
        except Exception as e:
            raise e

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        aspect = width / height
        if width >= height: 
            new_w = resolution_anchor
            new_h = int(resolution_anchor / aspect)
        else: 
            new_h = resolution_anchor
            new_w = int(resolution_anchor * aspect)
        return (new_w // 8) * 8, (new_h // 8) * 8

    def generate_live_action(
        self, source_image, prompt_guidance, feature_prompt, resolution_anchor, progress_callback=None
    ) -> Image.Image:
        
        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        img_np = np.array(input_image)
        # Stronger blur to remove small facial anime lines before edge detection
        img_blur = cv2.GaussianBlur(img_np, (7, 7), 0) 
        img_canny = cv2.Canny(img_blur, 50, 150)
        img_canny = np.stack([img_canny]*3, axis=-1)
        control_image = Image.fromarray(img_canny)

        # TUNED PROMPT: Explicitly asking for boots and human face realism
        full_prompt = (
            f"RAW photo of a real person as {prompt_guidance}, {feature_prompt}, "
            "wearing traditional martial arts gi and blue combat boots, "
            "detailed human face, symmetrical eyes, realistic skin texture, pores, "
            "cinematic studio lighting, high resolution, dslr, 8k uhd, Fujifilm"
        )
        
        # TUNED NEGATIVE: Banning bare feet and digital artifacts
        negative_prompt = (
            "anime, cartoon, drawing, illustration, 3d, render, cgi, toy, "
            "barefoot, toes, feet, plastic skin, wax, shiny, smooth skin, "
            "glowing eyes, stylized hair, (worst quality, low quality:1.4), "
            "malformed face, blurry face"
        )
        
        num_inference_steps = 40 # Increased steps for better facial reconstruction
        
        # CRITICAL CHANGE: 0.38 allows the AI to ignore anime eye lines 
        # while keeping the overall body structure and pose.
        controlnet_conditioning_scale = 0.38 
        
        guidance_scale = 9.0 # Increased to strictly follow the "human face" prompt

        def callback_on_step_end(pipe, i, t, callback_kwargs):
            if progress_callback: progress_callback(i + 1, num_inference_steps)
            return callback_kwargs

        with torch.no_grad():
            generator = torch.Generator(device=self._device).manual_seed(42)

            if self._device == "cuda":
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