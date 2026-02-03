# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Synthesis Engine v5.1 - Research Traceability Edition.
#              FEATURING: Hardcoded Quality-Enforcement negative prompting and 
#              DPM++ 2M Karras-style scheduling for high-speed CPU inference.
#              UPDATED: Now returns full prompts for fine-tuning analysis.
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
    """
    State-of-the-art Generative Adapter. 
    Implements strict quality controls to ensure photorealistic human outputs 
    while maintaining the structural 'DNA' of artistic source images.
    """

    def __init__(self, device: str = "cpu"):
        """
        Initializes the pipeline with adaptive precision and speed optimizations.
        """
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        
        # Proven research-grade model identifiers
        base_model_id = "SG161222/Realistic_Vision_V6.0_B1_noVAE"
        controlnet_id = "lllyasviel/control_v11p_sd15_canny"
        
        # Hardware Detection & Precision Policy
        if torch.cuda.is_available() and device == "cuda":
            self._device = "cuda"
            self._torch_dtype = torch.float16
        else:
            self._device = "cpu"
            self._torch_dtype = torch.float32 # High precision for CPU stability

        try:
            # 1. Structural Anchor Loading
            self._controlnet = ControlNetModel.from_pretrained(
                controlnet_id, torch_dtype=self._torch_dtype, local_files_only=self._offline
            ).to(self._device)
            
            # 2. Diffusion Pipeline Initialization
            self._pipe = StableDiffusionControlNetPipeline.from_pretrained(
                base_model_id, controlnet=self._controlnet, torch_dtype=self._torch_dtype, 
                safety_checker=None, local_files_only=self._offline
            ).to(self._device)
            
            # 3. High-Speed Research Scheduler
            # DPMSolverMultistep with 'use_karras_sigmas' mimics the professional 
            # DPM++ 2M Karras, providing superior facial clarity in fewer steps.
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, use_karras_sigmas=True
            )
            
            # 4. Memory/Latency Optimizations
            if self._device == "cuda":
                self._pipe.enable_attention_slicing() 
                self._pipe.enable_model_cpu_offload() 
            else:
                self._pipe.enable_attention_slicing("max")
            
            print(f"INFRA_AI: v5.1 Research Engine ready on {self._device.upper()}")
            
        except Exception as e:
            print(f"INFRA_AI_CRITICAL: Initialization failed. {str(e)}")
            raise e

    def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str, 
        feature_prompt: str, 
        resolution_anchor: int, 
        hyper_params: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[Image.Image, str, str]:
        """
        Synthesizes a humanized version of the character using v5.1 quality gates.
        Returns the generated image, the full positive prompt, and the negative prompt.
        """
        
        # --- DYNAMIC PARAMETERS ---
        steps = int(hyper_params.get("steps", 20)) 
        guidance_scale = float(hyper_params.get("cfg_scale", 7.0))
        controlnet_scale = float(hyper_params.get("cn_scale", 0.40))

        # 1. Domain Standardization
        target_w, target_h = self._calculate_proportional_dimensions(
            source_image.width, source_image.height, resolution_anchor
        )
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        
        # 2. Structural Pre-processing (Canny Edge Detection)
        img_np = np.array(input_image)
        img_blur = cv2.GaussianBlur(img_np, (5, 5), 0) 
        img_canny = cv2.Canny(img_blur, 50, 150)
        img_canny = np.stack([img_canny]*3, axis=-1)
        control_image = Image.fromarray(img_canny)

        # 3. FINAL v5.1 PROMPT ENGINEERING
        # Identity and Heuristics combined with quality-booster keywords
        full_prompt = (
            f"raw photo, {prompt_guidance}, {feature_prompt}, "
            "photorealistic human details, cinematic studio lighting, 8k, fujifilm"
        )
        
        # QUALITY-ENFORCEMENT (Negative Prompt Gate)
        # These keywords are hardcoded to ensure the 'Doll/Plastic' look is always avoided.
        negative_prompt = (
            "anime, cartoon, doll, plastic, 3d render, toy, wax, cgi, illustration, "
            "glitter eyes, shiny skin, airbrushed, unnatural eyes, "
            "(worst quality, low quality:1.4), malformed anatomy, blurry, "
            "digital artifacts, over-saturated"
        )
        
        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback: progress_callback(i + 1, steps)
            return callback_kwargs

        # 4. Neural Inference
        with torch.no_grad():
            # Seed 42 for research reproducibility
            generator = torch.Generator(device=self._device).manual_seed(42)

            output = self._pipe(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                image=control_image,
                height=target_h,
                width=target_w,
                guidance_scale=guidance_scale,
                controlnet_conditioning_scale=controlnet_scale,
                num_inference_steps=steps,
                generator=generator,
                callback_on_step_end=internal_callback
            ).images[0]

        return output, full_prompt, negative_prompt

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        aspect = width / height
        if width >= height: 
            new_w = resolution_anchor
            new_h = int(resolution_anchor / aspect)
        else: 
            new_h = resolution_anchor
            new_w = int(resolution_anchor * aspect)
        return (new_w // 8) * 8, (new_h // 8) * 8