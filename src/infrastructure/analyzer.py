# path: z_realism_ai/src/infrastructure/analyzer.py
# description: Universal Heuristic Analyzer v10.7 - DATA DRIVEN & STABLE.
#              FIXED: Resolved hangs by ensuring all logic paths define required variables.
#              ARCHITECTURE: Loads character definitions from JSON.
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
        # Internal path inside the Docker container
        self.lore_path = "/app/src/domain/lore/*.json"

    def _load_lore_library(self):
        """Scans the lore folder and loads all character definitions."""
        library = []
        json_files = glob.glob(self.lore_path)
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    library.append(json.load(f))
            except Exception as e:
                print(f"LORE ERROR: Could not load {file_path}: {e}")
        return library

    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        """
        Analyzes the source image and name to return optimal hyper-parameters.
        """
        # 1. Visual Analysis
        img_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        
        # Calculate edge density for dynamic weight adjustment
        edge_map = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edge_map) / (gray.size * 255)
        
        query_name = character_name.lower()
        library = self._load_lore_library()
        
        # 2. Search for character in JSON library
        match = next((c for c in library if any(a in query_name for a in c.get("aliases", []))), None)
        
        # 3. Decision Logic
        if match:
            essence = match.get("essence", "custom_entity")
            suggested_prompt = match.get("prompt_base", "")
            
            # Extract weights from JSON
            # Note: We support both 'depth' and 'canny' keys for backwards compatibility
            weights_dict = match.get("weights", {})
            base_cn = weights_dict.get("canny", weights_dict.get("depth", 0.60))
            
            # Dynamic adjustment: complex drawings need slightly more control
            final_cn = base_cn + (edge_density * 0.05)
        else:
            # FALLBACK: If character is not in JSON
            essence = "unknown_entity_fallback"
            final_cn = 0.60
            suggested_prompt = f"raw photo, cinematic film still, a real life human version of {character_name}, highly detailed, 8k uhd"

        # 4. Final Safety Clamps
        safe_cn = round(min(max(final_cn, 0.40), 0.90), 2)

        return AnalysisResult(
            recommended_steps=30,
            recommended_cfg=7.5,
            recommended_cn=safe_cn,
            detected_essence=f"{essence} (v10.7 Online)",
            suggested_prompt=suggested_prompt
        )