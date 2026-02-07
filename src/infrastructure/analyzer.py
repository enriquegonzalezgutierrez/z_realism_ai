# path: z_realism_ai/src/infrastructure/analyzer.py
# description: Expert Heuristic Analyzer v11.0 - Feature Extraction Edition.
#              Performs Visual Complexity Analysis (VCS) and Perceptual 
#              Luminance Mapping for dynamic hyper-parameter scaling.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
import json
import glob
import os
from PIL import Image
from src.domain.ports import ImageAnalyzerPort, AnalysisResult

class HeuristicImageAnalyzer(ImageAnalyzerPort):
    def __init__(self):
        self.lore_path = "/app/src/domain/lore/*.json"

    def _load_lore_library(self):
        library = []
        json_files = glob.glob(self.lore_path)
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    library.append(json.load(f))
            except Exception as e:
                print(f"LORE_SYSTEM_ERROR: {e}")
        return library

    def _analyze_visual_complexity(self, gray_img: np.ndarray) -> float:
        """
        Calculates Visual Complexity Score (VCS).
        Measures the entropy of edges to determine how much 'control' the AI needs.
        """
        edges = cv2.Canny(gray_img, 100, 200)
        vcs = np.sum(edges > 0) / gray_img.size
        return float(vcs)

    def _determine_lighting_strategy(self, gray_img: np.ndarray) -> str:
        """Perceptual Luminance Mapping."""
        avg_brightness = np.mean(gray_img)
        if avg_brightness < 80:
            return "dramatic chiaroscuro lighting, cinematic shadows, rim light"
        elif avg_brightness > 180:
            return "soft studio lighting, high-key, professional photography"
        return "cinematic film still lighting, realistic shadows"

    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        """
        Performs Heuristic Feature Extraction to synthesize the optimal 
        Diffusion Strategy.
        """
        # 1. Image Pre-processing for CV
        img_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # 2. Extract Features
        vcs = self._analyze_visual_complexity(gray)
        lighting_token = self._determine_lighting_strategy(gray)
        
        # 3. Search Lore Context
        query_name = character_name.lower()
        library = self._load_lore_library()
        match = next((c for c in library if any(a in query_name for a in c.get("aliases", []))), None)
        
        # 4. Strategy Synthesis (Doctorate Logic)
        if match:
            essence = match.get("essence", "custom_entity")
            prompt_base = match.get("prompt_base", "")
            weights = match.get("weights", {})
            
            # Base ControlNet weight adjusted by Visual Complexity
            # Complex drawings (high VCS) need more CN strength.
            base_cn = float(weights.get("depth", 0.65))
            final_cn = base_cn + (vcs * 0.2) # Dynamic boost
            
            # Complex species (Namekians, Aliens) get more steps for texture
            recommended_steps = 35 if "human" not in essence else 28
        else:
            essence = "unknown_entity"
            prompt_base = f"raw photo, hyper-detailed portrait of {character_name}, realistic skin"
            final_cn = 0.60 + (vcs * 0.15)
            recommended_steps = 30

        # 5. Final Assembly
        full_suggested_prompt = f"{prompt_base}, {lighting_token}, 8k, highly detailed"
        
        # Clamp values for stability on 6GB VRAM
        safe_cn = round(min(max(final_cn, 0.45), 0.90), 2)
        
        return AnalysisResult(
            recommended_steps=recommended_steps,
            recommended_cfg=7.5,
            recommended_cn=safe_cn,
            detected_essence=f"{essence.upper()} (VCS: {round(vcs, 3)})",
            suggested_prompt=full_suggested_prompt
        )