# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Engine v16.1 - MASTER STABLE PREVIEW.
#              FIXED: 'image_embeds' error by using Manual Injection Bypass.
#              FEATURING: Dual ControlNet + IP-Adapter + Real-time Preview.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import cv2
import os
import io
import base64
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
            print(f"INFRA_AI: Deploying Master Stable Engine v16.1...")
            # 1. Manual Vision Components
            self._feature_extractor = CLIPImageProcessor.from_pretrained(vision_id, local_files_only=self._offline)
            self._image_encoder = CLIPVisionModelWithProjection.from_pretrained(vision_id, torch_dtype=self._torch_dtype, local_files_only=self._offline).to(self._device)

            # 2. ControlNets
            depth_net = ControlNetModel.from_pretrained(depth_id, torch_dtype=self._torch_dtype, local_files_only=self._offline)
            openpose_net = ControlNetModel.from_pretrained(openpose_id, torch_dtype=self._torch_dtype, local_files_only=self._offline)
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # 3. Assembly (image_encoder=None kills the 'tuple' bug)
            self._pipe = StableDiffusionControlNetPipeline.from_pretrained(
                base_model_id, controlnet=[depth_net, openpose_net], 
                image_encoder=None, torch_dtype=self._torch_dtype, 
                safety_checker=None, local_files_only=self._offline
            ).to(self._device)
            
            self._pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.bin")
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(self._pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++", final_sigmas_type="sigma_min")
            
            self._pipe.enable_model_cpu_offload() 
            self._pipe.enable_vae_tiling()
                
            print(f"INFRA_AI: v16.1 Master Engine Online.")
        except Exception as e:
            raise e

    def _decode_preview(self, latents):
        """Converts math noise into a base64 thumbnail."""
        with torch.no_grad():
            latents = 1 / 0.18215 * latents
            image = self._pipe.vae.decode(latents).sample
            image = (image / 2 + 0.5).clamp(0, 1).cpu().permute(0, 2, 3, 1).float().numpy()
            image = (image * 255).round().astype("uint8")[0]
            pil_img = Image.fromarray(image).resize((256, 256))
            buffered = io.BytesIO()
            pil_img.save(buffered, format="JPEG", quality=60)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    @torch.no_grad()
    def _manual_identity_injection(self, image: Image.Image):
        """Calculates 3D tensors for identity transfer without using buggy pipeline paths."""
        clip_input = self._feature_extractor(images=image, return_tensors="pt").pixel_values.to(self._device, dtype=self._torch_dtype)
        output = self._image_encoder(clip_input)
        image_embeds = output.image_embeds.unsqueeze(1)
        return torch.cat([torch.zeros_like(image_embeds), image_embeds], dim=0)

    def generate_live_action(self, source_image, prompt_guidance, feature_prompt, resolution_anchor, hyper_params, progress_callback=None):
        steps = int(hyper_params.get("steps", 30)) 
        self._pipe.set_ip_adapter_scale(float(hyper_params.get("ip_scale", 0.65)))

        target_w, target_h = self._calculate_proportional_dimensions(source_image.width, source_image.height, resolution_anchor)
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        # Pre-process
        gray = cv2.cvtColor(np.array(input_image), cv2.COLOR_RGB2GRAY)
        depth_map = Image.fromarray(np.stack([cv2.GaussianBlur(gray, (9, 9), 0)]*3, axis=-1))
        openpose_map = self.openpose_detector(input_image)
        ip_embeds = self._manual_identity_injection(input_image)

        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback:
                preview = self._decode_preview(callback_kwargs["latents"]) if i % 5 == 0 else None
                progress_callback(i + 1, steps, preview)
            return callback_kwargs

        with torch.no_grad():
            output = self._pipe(
                prompt=f"raw photo, muscular man, {feature_prompt}, masculine facial features, highly detailed skin pores, 8k uhd", 
                negative_prompt=hyper_params.get("negative_prompt", "woman, female, girl, drawing"),
                image=[depth_map, openpose_map], 
                ip_adapter_image_embeds=[ip_embeds], # CRITICAL FIX: Injection
                height=target_h, width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=[float(hyper_params.get("cn_scale", 0.70)), 0.85],
                num_inference_steps=steps, 
                generator=torch.Generator(device=self._device).manual_seed(int(hyper_params.get("seed", 42))),
                callback_on_step_end=internal_callback
            ).images[0]

        return output, f"v16.1 Master: {feature_prompt}", "Stable Injection"

    def _calculate_proportional_dimensions(self, width, height, resolution_anchor):
        aspect = width / height
        new_w, new_h = (resolution_anchor, int(resolution_anchor / aspect)) if width >= height else (int(resolution_anchor * aspect), resolution_anchor)
        return (new_w // 8) * 8, (new_h // 8) * 8