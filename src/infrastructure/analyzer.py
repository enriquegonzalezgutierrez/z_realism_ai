# path: src/infrastructure/analyzer.py
# description: Heuristic Intelligence Layer v22.0 - Doctoral Thesis Candidate.
#              This version implements adaptive Canny thresholding based on Subject DNA.
#
# ARCHITECTURAL ROLE (Infrastructure Adapter):
# This module implements the 'ImageAnalyzerPort'. It performs a multivariate 
# analysis of the source manifold to determine the optimal stochastic 
# parameters and lighting guidance for the diffusion process.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
import json
import glob
import os
from PIL import Image
from src.domain.ports import ImageAnalyzerPort, AnalysisResult

class HeuristicImageAnalyzer(ImageAnalyzerPort):
    """
    Expert Analytical Engine for Predictive Diffusion Tuning.
    
    Synthesizes a transformation strategy by merging pixel-level computer 
    vision metrics with high-fidelity subject DNA stored in the Metadata KB.
    """

    def __init__(self):
        self.metadata_dir = "/app/src/domain/metadata/"
        self._default_metadata = self._load_default_metadata()

    def _load_default_metadata(self) -> dict:
        """Loads the global baseline configuration."""
        default_path = os.path.join(self.metadata_dir, "default.json")
        if os.path.exists(default_path):
            try:
                with open(default_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"METADATA_ERROR: Baseline load failure. {e}")
        
        return {
            "essence": "unknown_entity",
            "prompt_base": "cinematic portrait, realistic features",
            "weights": {"depth": 0.75, "canny": 0.50},
            "canny_thresholds": [100, 200],
            "denoising_strength": 0.70,
            "negative_prompt": "anime, cartoon, drawing, plastic, low quality",
            "realism_fragments": ["hyper-realistic, 8k, detailed skin texture"]
        }

    def _get_metadata_by_name(self, name: str) -> dict:
        """Implements the Hierarchical Metadata Dispatcher."""
        query = name.lower()
        json_files = glob.glob(os.path.join(self.metadata_dir, "*.json"))
        merged_strategy = self._default_metadata.copy()

        for file_path in json_files:
            if "default.json" in file_path: continue
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if any(alias in query for alias in data.get("aliases", [])):
                        merged_strategy.update(data)
                        return merged_strategy
            except Exception: continue
        return merged_strategy

    def _detect_background_policy(self, image: Image.Image) -> str:
        """Heuristic analysis to determine if the background is a void/studio black."""
        if image.mode == "RGBA":
            alpha = np.array(image)[..., 3]
            if np.mean(alpha) < 20: return "preserve"

        gray = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2GRAY)
        if np.mean(gray) < 25:
            return "preserve"

        return "generate"

    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        """
        Synthesizes the strategy manifold based on pixel heuristics and subject DNA.
        """
        img_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        background_policy = self._detect_background_policy(image)
        
        metadata = self._get_metadata_by_name(character_name)
        weights = metadata.get("weights", {})
        
        # --- NEW: Adaptive Canny Thresholding ---
        # 1. Get thresholds from JSON (Subject DNA).
        # 2. Fallback to a safe default if not specified.
        canny_cfg = metadata.get("canny_thresholds", [100, 200])
        
        avg_brightness = np.mean(gray)
        lighting = ""

        if background_policy == "preserve":
            if avg_brightness < 60:
                lighting = "dramatic rim lighting, high contrast, pure black background"
            else:
                lighting = "ambient cinematic lighting, studio environment"
        else:
            lighting = "cinematic film lighting"
            if avg_brightness < 80:
                lighting = "dramatic chiaroscuro lighting, deep shadows"
            elif avg_brightness > 180:
                lighting = "soft studio lighting, high-key photography"

        subject_dna = metadata.get('prompt_base', '')
        realism_fragments = metadata.get('realism_fragments', [])
        raw_prompt = [subject_dna] + realism_fragments + [lighting]
        
        seen = set()
        clean_tokens = []
        for frag in raw_prompt:
            for word in frag.split(','):
                w = word.strip().lower()
                if w and w not in seen:
                    seen.add(w)
                    clean_tokens.append(w)
        
        final_suggested_prompt = ", ".join(clean_tokens[:70])
        base_negative = metadata.get("negative_prompt", "anime, drawing, plastic, low quality")
        
        return AnalysisResult(
            recommended_steps=30,
            recommended_cfg=7.5,
            recommended_cn_depth=float(weights.get("depth", 0.75)),
            recommended_cn_pose=float(weights.get("canny", 0.40)), # Map 'canny' to 'cn_pose'
            recommended_strength=float(metadata.get("denoising_strength", 0.70)),
            
            # --- Passing new parameters to the DTO ---
            canny_low=int(canny_cfg[0]),
            canny_high=int(canny_cfg[1]),
            
            detected_essence=metadata.get("essence", "unknown").upper(),
            suggested_prompt=final_suggested_prompt,
            suggested_negative=base_negative
        )