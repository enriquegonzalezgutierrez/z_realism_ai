# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Engine v14.0 - THE SOUL RESTORATION.
#              FIXED: Restored IP-Adapter using Manual Injection to prevent 'tuple' bugs.
#              FEATURING: Dual ControlNet (Depth + OpenPose) for facial and body volume.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import cv2
import os
from typing import Callable, Optional, Tuple, Dict, Any
from PIL import Image
from transformers import CLIPVisionModelWithProjection, CLIPImageProcessor
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
        depth_id = "lllyasviel/control_v11f1p_sd15_depth"
        openpose_id = "lllyasviel/control_v11p_sd15_openpose"
        vision_id = "laion/CLIP-ViT-H-14-laion2B-s32B-b79K"
        
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Deploying Master Engine v14.0...")
            
            # 1. Vision Stack for Manual Injection
            self._feature_extractor = CLIPImageProcessor.from_pretrained(vision_id, local_files_only=self._offline)
            self._image_encoder = CLIPVisionModelWithProjection.from_pretrained(
                vision_id, torch_dtype=self._torch_dtype, local_files_only=self._offline
            ).to(self._device)

            # 2. ControlNets
            depth_net = ControlNetModel.from_pretrained(depth_id, torch_dtype=self._torch_dtype, local_files_only=self._offline)
            openpose_net = ControlNetModel.from_pretrained(openpose_id, torch_dtype=self._torch_dtype, local_files_only=self._offline)
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # 3. Pipeline (image_encoder=None to bypass bugs)
            self._pipe = StableDiffusionControlNetPipeline.from_pretrained(
                base_model_id, controlnet=[depth_net, openpose_net], image_encoder=None,
                torch_dtype=self._torch_dtype, safety_checker=None, local_files_only=self._offline
            ).to(self._device)
            
            # 4. IP-Adapter (The Soul)
            self._pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.bin")
            
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++", final_sigmas_type="sigma_min"
            )
            
            self._pipe.enable_model_cpu_offload() 
            self._pipe.enable_vae_tiling()
            self._pipe.enable_attention_slicing("max")
                
            print(f"INFRA_AI: v14.0 Ready. Identity Transfer Active.")
            
        except Exception as e:
            print(f"INFRA_AI_CRITICAL: {e}")
            raise e

    @torch.no_grad()
    def _create_embeddings(self, image: Image.Image):
        """Manual injection logic to bypass 'tuple' error."""
        clip_input = self._feature_extractor(images=image, return_tensors="pt").pixel_values
        clip_input = clip_input.to(self._device, dtype=self._torch_dtype)
        outputs = self._image_encoder(clip_input)
        image_embeds = outputs.image_embeds.unsqueeze(1)
        return torch.cat([torch.zeros_like(image_embeds), image_embeds], dim=0)

    def generate_live_action(self, source_image, prompt_guidance, feature_prompt, resolution_anchor, hyper_params, progress_callback=None):
        steps = int(hyper_params.get("steps", 30)) 
        self._pipe.set_ip_adapter_scale(float(hyper_params.get("ip_scale", 0.65)))

        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        # Maps
        gray = cv2.cvtColor(np.array(input_image), cv2.COLOR_RGB2GRAY)
        depth_map = Image.fromarray(np.stack([cv2.GaussianBlur(gray, (9, 9), 0)]*3, axis=-1))
        openpose_map = self.openpose_detector(input_image)
        
        # Manual Identity Injection
        ip_embeds = self._create_embeddings(input_image)

        # CLEAN PROMPT: No more repetitions
        full_prompt = f"{feature_prompt}"

        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback: progress_callback(i + 1, steps)
            return callback_kwargs

        with torch.no_grad():
            gen = torch.Generator(device=self._device).manual_seed(int(hyper_params.get("seed", 42)))

            output = self._pipe(
                prompt=full_prompt, 
                negative_prompt=hyper_params.get("negative_prompt", "anime, cartoon, bad anatomy"),
                image=[depth_map, openpose_map], 
                ip_adapter_image_embeds=[ip_embeds], # INJECTION
                height=target_h, width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=[float(hyper_params.get("cn_scale", 0.7)), 0.85],
                num_inference_steps=steps, 
                generator=gen,
                callback_on_step_end=internal_callback
            ).images[0]

        return output, full_prompt, "v14.0 Identity Restoration"

    def _calculate_proportional_dimensions(self, width, height, resolution_anchor):
        aspect = width / height
        new_w, new_h = (resolution_anchor, int(resolution_anchor / aspect)) if width >= height else (int(resolution_anchor * aspect), resolution_anchor)
        return (new_w // 8) * 8, (new_h // 8) * 8