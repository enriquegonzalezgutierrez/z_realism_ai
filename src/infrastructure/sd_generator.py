# path: z_realism_ai/src/infrastructure/sd_generator.py
# description: Neural Computational Core v19.1 - High-Fidelity Depth Refinement.
#
# CHANGES v19.1:
# 1. Replaced Gaussian Blur depth approximation with Midas Neural Depth Estimation.
# 2. Enhanced Prompt Blending to prioritize cinematic lighting over flat anime colors.
# 3. Optimized ControlNet scaling to balance structural integrity and realism.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import torch
import numpy as np
import cv2
import os
import io
import base64
import math
from typing import Callable, Optional, Tuple, Dict, Any, List
from PIL import Image, ImageOps

from controlnet_aux import OpenposeDetector, MidasDetector
from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline, 
    ControlNetModel, 
    DPMSolverMultistepScheduler,
    AutoencoderKL
)
from src.domain.ports import ImageGeneratorPort

# Linear Latent-to-RGB projection factors for real-time visual telemetry
LATENT_RGB_FACTORS = [[0.298, 0.187, -0.158],[0.207, 0.286, 0.189],[0.208, 0.189, 0.266],[-0.149, -0.071, -0.045]]

class StableDiffusionGenerator(ImageGeneratorPort):
    """
    Advanced Multi-Conditioning Engine for Photorealistic Character Synthesis.
    Utilizes Dual ControlNet (Depth + Pose) to transform stylized inputs into cinematic realism.
    """

    def __init__(self, device: str = "cpu"):
        self._offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        self._device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        self._torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

        try:
            print(f"INFRA_AI: Deploying Engine v19.1 (Neural Structural Depth)...")
            
            # 1. High-Fidelity Reconstruction Components (MSE-tuned for skin textures)
            vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", torch_dtype=self._torch_dtype, local_files_only=self._offline
            ).to(self._device)

            # 2. Structural Anchors (ControlNet Models)
            depth_net = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11f1p_sd15_depth", torch_dtype=self._torch_dtype, local_files_only=self._offline
            )
            openpose_net = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11p_sd15_openpose", torch_dtype=self._torch_dtype, local_files_only=self._offline
            )
            
            # 3. Neural Pre-processors (Estimators)
            # MidasDetector provides real 3D depth maps instead of simple blurs.
            self.depth_estimator = MidasDetector.from_pretrained('lllyasviel/ControlNet')
            self.openpose_detector = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

            # 4. Agnostic Pipeline Assembly
            # Realistic_Vision_V5.1 is the industry standard for human fotorrealism.
            self._pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                "SG161222/Realistic_Vision_V5.1_noVAE", 
                vae=vae, 
                controlnet=[depth_net, openpose_net], 
                torch_dtype=self._torch_dtype, 
                safety_checker=None, 
                local_files_only=self._offline
            ).to(self._device)
            
            # Optimized Convergence Schedule (DPM++ 2M Karras)
            self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++"
            )
            
            # 5. Hardware Acceleration Profiles
            if self._device == "cuda":
                self._pipe.enable_xformers_memory_efficient_attention()
                self._pipe.enable_model_cpu_offload() 
                self._pipe.enable_vae_tiling()
                
            print(f"INFRA_AI: v19.1 Online. Structural fidelity engaged.")
        except Exception as e:
            print(f"INFRA_AI_BOOT_FAILURE: {e}")
            raise e

    def _decode_preview(self, latents: torch.Tensor) -> str:
        """Linear approximation of the VAE decoding process for UI feedback."""
        with torch.no_grad():
            latent_img = latents[0].permute(1, 2, 0).cpu() 
            factors = torch.tensor(LATENT_RGB_FACTORS, dtype=latent_img.dtype)
            rgb_img = ((latent_img @ factors) + 1.0) / 2.0
            image = (rgb_img.clamp(0, 1).numpy() * 255).astype("uint8")
            buffered = io.BytesIO()
            Image.fromarray(image).resize((256, 256)).save(buffered, format="JPEG", quality=40)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str, 
        feature_prompt: str, 
        resolution_anchor: int, 
        hyper_params: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[Image.Image, str, str]:
        """
        Executes character-specific synthesis by leveraging neural depth maps 
        to ensure background consistency and cinematic fotorrealism.
        """
        
        # --- 1. TACTICAL PARAMETER EXTRACTION ---
        # Denoising strength is critical: < 0.5 stays too close to anime, > 0.7 loses character.
        strength = float(hyper_params.get("denoising_strength", 0.65))
        nominal_steps = int(hyper_params.get("steps", 30))
        effective_steps = math.floor(nominal_steps * strength)
        
        # Aligned weights for Multi-ControlNet: [Depth, Pose]
        cn_scales = [
            float(hyper_params.get("weights", {}).get("depth", 0.60)), 
            float(hyper_params.get("weights", {}).get("openpose", 0.75))
        ]
        
        # --- 2. MANIFOLD PRE-PROCESSING ---
        target_w, target_h = self._calculate_proportional_dimensions(
            source_image.width, source_image.height, resolution_anchor
        )
        
        # Robust handling of input image modes (esp. Palette/Transparent PNGs)
        if source_image.mode in ('P', 'LA') or (source_image.mode == 'RGBA' and 'transparency' in source_image.info.get('transparency', ())):
            # If image is Palette or RGBA with transparency, convert to RGBA first for clean handling
            source_image = source_image.convert("RGBA")
            # Create a white background to paste the cutout character onto
            background = Image.new("RGB", source_image.size, (255, 255, 255))
            # Paste using the Alpha channel as mask, ensuring no transparency leaks into the final RGB input
            background.paste(source_image, mask=source_image.split()[3])
            input_image = background.convert("RGB")
        else:
            # If it's already RGB or simple grayscale, just ensure it is RGB
            input_image = source_image.convert("RGB")
            
        # Resize to final diffusion dimension
        input_image = input_image.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # --- 3. NEURAL MAP GENERATION (Structural Guidance) ---
        # Depth Map: Captures 3D geometry of the character and background.
        depth_map = self.depth_estimator(input_image)
        
        # Pose Map: Ensures anatomical consistency with the source character.
        openpose_map = self.openpose_detector(input_image)

        # --- 4. PROMPT ENGINEERING (Semantic Calibration) ---
        # Combine base character lore with global cinematic quality features.
        final_prompt = f"{prompt_guidance}, {feature_prompt}, high detailed skin, 8k uhd, cinematic lighting, dslr, soft bokeh"
        neg_prompt = hyper_params.get("negative_prompt", "anime, cartoon, drawing, illustration, plastic")

        # Telemetry linkage
        def internal_callback(pipe, i, t, callback_kwargs):
            if progress_callback and i % 2 == 0:
                preview_b64 = self._decode_preview(callback_kwargs["latents"])
                progress_callback(i + 1, effective_steps, preview_b64)
            return callback_kwargs

        # --- 5. NEURAL INFERENCE (Img2Img + Multi-ControlNet) ---
        with torch.inference_mode():
            output = self._pipe(
                prompt=final_prompt, 
                negative_prompt=neg_prompt,
                image=input_image,              # Starting manifold (Color & Composition)
                control_image=[depth_map, openpose_map], 
                strength=strength,              # How much of the "anime" pixels to destroy
                height=target_h, 
                width=target_w,
                guidance_scale=float(hyper_params.get("cfg_scale", 7.5)), 
                controlnet_conditioning_scale=cn_scales,
                num_inference_steps=nominal_steps,
                generator=torch.Generator(device=self._device).manual_seed(int(hyper_params.get("seed", 42))),
                callback_on_step_end=internal_callback
            ).images[0]

        return output, final_prompt, neg_prompt

    def _calculate_proportional_dimensions(self, width: int, height: int, resolution_anchor: int) -> Tuple[int, int]:
        """Calculates dimensions proportional to the anchor, divisible by 8 (required for VAE)."""
        aspect = width / height
        if width >= height:
            new_w = resolution_anchor
            new_h = int(resolution_anchor / aspect)
        else:
            new_h = resolution_anchor
            new_w = int(resolution_anchor * aspect)
        return (new_w // 8) * 8, (new_h // 8) * 8