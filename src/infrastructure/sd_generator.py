# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: AI Engine implementation using SDXL and IP-Adapter.
#              CRITICAL FIX: Corrected the model identifier for the T2I adapter 
#              to ensure successful download and loading on startup.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import asyncio
from typing import Callable, Optional, Tuple
from PIL import Image
from diffusers import (
    StableDiffusionXLAdapterPipeline, 
    T2IAdapter, 
    DDIMScheduler
)
from src.domain.ports import ImageGeneratorPort

# -----------------------------------------------------------------------------
# SDXL Generator (IP-Adapter based)
# -----------------------------------------------------------------------------

class StableDiffusionGenerator(ImageGeneratorPort):
    """
    Adapter for Stable Diffusion XL utilizing the IP-Adapter technique.
    Provides high-resolution photorealism while maintaining the 
    character's pose and aesthetic from the source image.
    """

    def __init__(self, device: str = "cpu"):
        print(f"INFRA_AI: Initializing SDXL + IP-Adapter on {device}...")
        
        # Core SDXL Model for Photorealism
        base_model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        # CRITICAL FIX: Correct and robust model ID for the structural adapter (Canny)
        adapter_model_id = "Tencent/t2i-adapter-sdxl-canny-mid"
        
        self._device = device
        
        # 1. Load the Adapter (using float32 for CPU stability)
        self._adapter = T2IAdapter.from_pretrained(adapter_model_id, torch_dtype=torch.float32)

        # 2. Load the Pipeline (Combining Adapter and Base Model)
        self._pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
            base_model_id,
            adapter=self._adapter,
            torch_dtype=torch.float32, 
            use_safetensors=True
        ).to(self._device)

        self._pipe.scheduler = DDIMScheduler.from_config(self._pipe.scheduler.config)
        self._pipe.safety_checker = None
        
        # Memory optimization
        if self._device == "cpu":
            self._pipe.enable_attention_slicing()
            
        print(f"INFRA_AI: SDXL + IP-Adapter Engine Loaded.")

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        """
        Calculates optimal dimensions (multiples of 8) strictly preserving aspect ratio.
        """
        short_side_anchor = resolution_anchor
        aspect_ratio = width / height
        max_dim = 1024 # SDXL max standard resolution
        
        if width < height: 
            new_w = short_side_anchor
            new_h = int(short_side_anchor / aspect_ratio)
        else: 
            new_h = short_side_anchor
            new_w = int(short_side_anchor * aspect_ratio)
            
        # Snap to nearest multiple of 8
        new_w = (min(new_w, max_dim) // 8) * 8
        new_h = (min(new_h, max_dim) // 8) * 8
        
        return new_w, new_h

    async def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Image.Image:
        """
        Generates HD image using the source image's structure via the Adapter.
        """
        orig_w, orig_h = source_image.size
        target_w, target_h = self._calculate_proportional_dimensions(orig_w, orig_h, resolution_anchor)
        
        input_image = source_image.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
        control_image = input_image 
        
        full_prompt = f"{prompt_guidance}, {feature_prompt}, 8k UHD, photorealistic"
        
        negative_prompt = (
            "drawing, 2d, illustration, sketch, low quality, deformed anatomy, "
            "ugly, jpeg artifacts, monochrome, cartoon, animation, signature, "
            "deformed face, melted head, plastic"
        )
        
        num_inference_steps = 30
        
        def callback_on_step_end(pipe, i, t, callback_kwargs):
            if progress_callback:
                progress_callback(i + 1, num_inference_steps)
            return callback_kwargs

        print(f"INFRA_AI: Starting SDXL Synthesis ({target_w}x{target_h}, {num_inference_steps} steps)...")

        with torch.no_grad():
            output = self._pipe(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                image=control_image, # Source image provides structure/style reference
                height=target_h,
                width=target_w,
                guidance_scale=7.5,
                num_inference_steps=num_inference_steps,
                callback_on_step_end=callback_on_step_end
            ).images[0]

        return output