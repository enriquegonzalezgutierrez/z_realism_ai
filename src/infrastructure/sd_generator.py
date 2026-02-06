# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Engine v11.2 - DEPTH + STABILITY FIX.
#              FIXED: 'final_sigmas_type' error by enforcing dpmsolver++ config.
#              STATUS: Depth ControlNet enabled. IP-Adapter disabled.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import cv2
import os
from typing import Callable, Optional, Tuple, Dict, Any
from PIL import Image
from diffusers import (
    StableDiffusionControlNetPipeline, 
    ControlNetModel, 
    DPMSolverMultistepScheduler
)
from src.domain.ports import ImageGeneratorPort

class StableDiffusionGenerator(ImageGeneratorPort):
    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        base_model_id = "SG161222/Realistic_Vision_V5.1_noVAE" 
        controlnet_id = "lllyasviel/control_v11f1p_sd15_depth"
        
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"[v11.2] --- INITIALIZING DEPTH ENGINE (STABLE) ---")
            
            # 1. Load ControlNet
            self._controlnet = ControlNetModel.from_pretrained(
                controlnet_id, torch_dtype=self._torch_dtype, local_files_only=self._offline
            ).to(self._device)
            
            # 2. Load Pipeline
            self._pipe = StableDiffusionControlNetPipeline.from_pretrained(
                base_model_id, 
                controlnet=self._controlnet, 
                torch_dtype=self._torch_dtype, 
                safety_checker=None, 
                local_files_only=self._offline
            ).to(self._device)
            
            # 3. CRITICAL FIX: Explicit Scheduler Configuration
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, 
                use_karras_sigmas=True,
                algorithm_type="dpmsolver++", # Forces stable algorithm
                final_sigmas_type="sigma_min" # Fixes the ValueError
            )
            
            if self._device == "cuda":
                self._pipe.enable_vae_tiling()
                self._pipe.enable_attention_slicing("max")
                self._pipe.enable_model_cpu_offload() 
                
            print(f"[v11.2] Engine Online. Scheduler Fixed.\n")
            
        except Exception as e:
            print(f"[v11.2] CRITICAL ERROR: {e}")
            raise e

    def generate_live_action(self, source_image, prompt_guidance, feature_prompt, resolution_anchor, hyper_params, progress_callback=None):
        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        # Depth Map Generation
        img_np = np.array(input_image)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        depth_blur = cv2.GaussianBlur(gray, (9, 9), 0)
        control_image = Image.fromarray(np.stack([depth_blur]*3, axis=-1))
        
        full_prompt = f"cinematic film still, raw photo, {feature_prompt}, 8k"
        steps = int(hyper_params.get("steps", 25))

        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback: progress_callback(i + 1, steps)
            return callback_kwargs

        with torch.no_grad():
            gen = torch.Generator(device=self._device).manual_seed(int(hyper_params.get("seed", 42)))

            output = self._pipe(
                prompt=full_prompt, 
                negative_prompt=hyper_params.get("negative_prompt", "anime, cartoon"),
                image=control_image, # Using Depth Map
                height=target_h, width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=float(hyper_params.get("cn_scale", 0.70)),
                num_inference_steps=steps, 
                generator=gen,
                callback_on_step_end=internal_callback
            ).images[0]

        return output, "v11.2 Depth Active", "Success"

    def _calculate_proportional_dimensions(self, width, height, resolution_anchor):
        aspect = width / height
        new_w, new_h = (resolution_anchor, int(resolution_anchor / aspect)) if width >= height else (int(resolution_anchor * aspect), resolution_anchor)
        return (new_w // 8) * 8, (new_h // 8) * 8