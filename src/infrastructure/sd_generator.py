# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Engine v13.3 - MASTER FINAL STABLE.
#              FIXED: 'NoneType' pop error by ensuring callback returns kwargs.
#              FIXED: Token truncation via clean prompt architecture.
#              STRATEGY: Dual ControlNet (Depth + OpenPose) for maximum fidelity.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import cv2
import os
from typing import Callable, Optional, Tuple, Dict, Any
from PIL import Image
from controlnet_aux import OpenposeDetector 
from diffusers import (
    StableDiffusionControlNetPipeline, 
    ControlNetModel, 
    DPMSolverMultistepScheduler
)
from src.domain.ports import ImageGeneratorPort

class StableDiffusionGenerator(ImageGeneratorPort):
    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        
        # --- PROVEN STABLE MODELS ---
        base_model_id = "SG161222/Realistic_Vision_V5.1_noVAE" 
        depth_id = "lllyasviel/control_v11f1p_sd15_depth"
        openpose_id = "lllyasviel/control_v11p_sd15_openpose"
        
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Loading Master Engine v13.3...")
            
            # 1. Load Controllers
            depth_net = ControlNetModel.from_pretrained(depth_id, torch_dtype=self._torch_dtype, local_files_only=self._offline)
            openpose_net = ControlNetModel.from_pretrained(openpose_id, torch_dtype=self._torch_dtype, local_files_only=self._offline)
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # 2. Load Pipeline
            self._pipe = StableDiffusionControlNetPipeline.from_pretrained(
                base_model_id, 
                controlnet=[depth_net, openpose_net], 
                torch_dtype=self._torch_dtype, 
                safety_checker=None, 
                local_files_only=self._offline
            ).to(self._device)
            
            # 3. Scheduler Stability
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, 
                use_karras_sigmas=True, 
                algorithm_type="dpmsolver++",
                final_sigmas_type="sigma_min"
            )
            
            # 4. VRAM Optimizations
            self._pipe.enable_model_cpu_offload() 
            self._pipe.enable_vae_tiling()
            self._pipe.enable_attention_slicing("max")
                
            print(f"INFRA_AI: Master Engine Online and Protected.")
            
        except Exception as e:
            print(f"INFRA_AI_CRITICAL: {e}")
            raise e

    def generate_live_action(self, source_image, prompt_guidance, feature_prompt, resolution_anchor, hyper_params, progress_callback=None):
        steps = int(hyper_params.get("steps", 30)) 
        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        # A. Create Control Maps
        gray = cv2.cvtColor(np.array(input_image), cv2.COLOR_RGB2GRAY)
        depth_map = Image.fromarray(np.stack([cv2.GaussianBlur(gray, (9, 9), 0)]*3, axis=-1))
        openpose_map = self.openpose_detector(input_image)
        
        # B. CLEAN PROMPT (Anti-Truncation Logic)
        # We rely 100% on the JSON prompt to stay under 77 tokens
        full_prompt = f"raw photo, {feature_prompt}"
        
        # C. Weights
        cn_scale = [float(hyper_params.get("cn_scale", 0.70)), 0.85]

        # --- D. ROBUST CALLBACK (FIXES 'pop' ERROR) ---
        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback:
                progress_callback(i + 1, steps)
            # CRITICAL: This return is mandatory for the pipeline to continue
            return callback_kwargs

        with torch.no_grad():
            gen = torch.Generator(device=self._device).manual_seed(int(hyper_params.get("seed", 42)))

            output = self._pipe(
                prompt=full_prompt, 
                negative_prompt=hyper_params.get("negative_prompt", "anime, cartoon, low quality, bad anatomy"),
                image=[depth_map, openpose_map], 
                height=target_h, width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=cn_scale,
                num_inference_steps=steps, 
                generator=gen,
                callback_on_step_end=internal_callback # Robust callback link
            ).images[0]

        return output, full_prompt, "v13.3 Stable"

    def _calculate_proportional_dimensions(self, width, height, resolution_anchor):
        aspect = width / height
        new_w, new_h = (resolution_anchor, int(resolution_anchor / aspect)) if width >= height else (int(resolution_anchor * aspect), resolution_anchor)
        return (new_w // 8) * 8, (new_h // 8) * 8