# path: z_realism_ai/src/infrastructure/analyzer.py
# description: Universal Heuristic Analyzer v10.6 - STABLE DEPTH EDITION.
#              FIXED: Restored Depth-based weights for the v13.1 Stable Engine.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
import json
import glob
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
                print(f"LORE ERROR: {e}")
        return library

    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        img_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        edge_density = np.sum(cv2.Canny(gray, 100, 200)) / (gray.size * 255)
        
        query_name = character_name.lower()
        library = self._load_lore_library()
        match = next((c for c in library if any(a in query_name for a in c.get("aliases", []))), None)
        
        if match:
            essence = match.get("essence", "custom_entity")
            prompt = match.get("prompt_base", "")
            # We restore 'depth' weight from JSON (or default to 0.70)
            base_depth = match["weights"].get("depth", 0.70)
            final_cn = base_depth + (edge_density * 0.1)
        else:
            essence = "unknown_entity"
            final_cn = 0.60
            prompt = f"cinematic film still, a real life human version of {character_name}, 8k uhd"

        return AnalysisResult(
            recommended_steps=30,
            recommended_cfg=7.5,
            recommended_cn=round(min(final_cn, 0.85), 2), # This is for the DEPTH slider
            detected_essence=f"{essence} (Stable v10.6)",
            suggested_prompt=prompt
        )