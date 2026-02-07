# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Engine v12.3 - THE FINAL STAND.
#              FIXED: Re-integrated Scheduler patch to prevent ImportError.
#              This version combines all previous fixes into a stable master.
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
        base_model_id = "SG161222/Realistic_Vision_V5.1_noVAE" 
        depth_control_id = "lllyasviel/control_v11f1p_sd15_depth"
        openpose_control_id = "lllyasviel/control_v11p_sd15_openpose"
        
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Deploying Dual ControlNet Engine v12.3 (Final Stand)...")
            
            # 1. Load ControlNet Models
            depth_net = ControlNetModel.from_pretrained(depth_control_id, torch_dtype=self._torch_dtype, local_files_only=self._offline)
            openpose_net = ControlNetModel.from_pretrained(openpose_control_id, torch_dtype=self._torch_dtype, local_files_only=self._offline)
            
            # 2. Load OpenPose Preprocessor
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # 3. Load Pipeline
            self._pipe = StableDiffusionControlNetPipeline.from_pretrained(
                base_model_id, 
                controlnet=[depth_net, openpose_net], 
                torch_dtype=self._torch_dtype, 
                safety_checker=None, 
                local_files_only=self._offline
            )
            
            # 4. Load IP-Adapter
            self._pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.bin")
            
            # 5. --- CRITICAL FIX RESTORED ---
            # Re-adding the full scheduler config to prevent the 'deis' error
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, 
                use_karras_sigmas=True,
                algorithm_type="dpmsolver++",
                final_sigmas_type="sigma_min" # This was missing
            )
            
            self._pipe.enable_model_cpu_offload() 
                
            print(f"INFRA_AI: Face Rescue Engine (v12.3) Stable and Online.")
            
        except Exception as e:
            print(f"INFRA_AI_CRITICAL: {e}")
            raise e

    def generate_live_action(self, source_image, prompt_guidance, feature_prompt, resolution_anchor, hyper_params, progress_callback=None):
        steps = int(hyper_params.get("steps", 30)) 
        guidance_scale = float(hyper_params.get("cfg_scale", 7.5))
        seed = int(hyper_params.get("seed", 42))
        ip_scale = float(hyper_params.get("ip_scale", 0.65))
        
        controlnet_weights = [0.5, 0.8] # [Depth, OpenPose]

        self._pipe.set_ip_adapter_scale(ip_scale)

        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        # --- PRE-PROCESSING ---
        gray = cv2.cvtColor(np.array(input_image), cv2.COLOR_RGB2GRAY)
        depth_map = Image.fromarray(np.stack([cv2.GaussianBlur(gray, (9, 9), 0)]*3, axis=-1))
        openpose_map = self.openpose_detector(input_image)

        full_prompt = f"cinematic film still, raw photo, {feature_prompt}, highly detailed skin, 8k"

        # --- ROBUST CALLBACK ---
        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback:
                progress_callback(i + 1, steps)
            return callback_kwargs

        with torch.no_grad():
            gen = torch.Generator(device=self._device)
            if seed != -1: gen.manual_seed(seed)

            output = self._pipe(
                prompt=full_prompt, 
                negative_prompt=hyper_params.get("negative_prompt", "anime, cartoon, bad anatomy"),
                image=[depth_map, openpose_map], 
                ip_adapter_image=input_image, 
                height=target_h, width=target_w,
                guidance_scale=guidance_scale, 
                controlnet_conditioning_scale=controlnet_weights,
                num_inference_steps=steps, 
                generator=gen,
                callback_on_step_end=internal_callback
            ).images[0]

        return output, "v12.3 Final Stand", "Dual ControlNet"

    def _calculate_proportional_dimensions(self, width, height, resolution_anchor):
        aspect = width / height
        new_w, new_h = (resolution_anchor, int(resolution_anchor / aspect)) if width >= height else (int(resolution_anchor * aspect), resolution_anchor)
        return (new_w // 8) * 8, (new_h // 8) * 8