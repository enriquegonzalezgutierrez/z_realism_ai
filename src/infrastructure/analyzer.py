# path: z_realism_ai/src/infrastructure/analyzer.py
# description: Expert Heuristic Analyzer v19.7 - Hierarchical Strategy Synthesis & Token Safety.
#
# ABSTRACT:
# This revision centralizes the prompt construction logic. It now retrieves 
# generic "Realism Fragments" from the default lore configuration, combines 
# them with the character's specific "prompt_base" (lore), and synthesizes 
# a single, token-safe final prompt (max ~70 segments) to ensure the 
# generative engine (SD) receives prioritized instructions.
#
# TECHNICAL IMPROVEMENTS (v19.7):
# 1. Prompt Synthesis: Combines Character Lore, Lighting Analysis, and Global Realism Fragments.
# 2. Token Safety: Ensures the most critical information is placed first.
# 3. Lore Integration: Loads 'realism_fragments' list from default.json.
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
    
    Acts as the bridge between raw pixel manifolds and the latent diffusion 
    hyperparameter space.
    """

    def __init__(self):
        # Path to the Domain-Specific Lore Library
        self.lore_dir = "/app/src/domain/lore/"
        # Load the global default lore once
        self._default_lore = self._load_default_lore()

    def _load_default_lore(self) -> dict:
        """Loads the global default lore configuration, including realism fragments."""
        default_path = os.path.join(self.lore_dir, "default.json")
        if os.path.exists(default_path):
            try:
                with open(default_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"WARNING: Could not load default lore file. Using hardcoded invariants. Error: {e}")
        
        # Emergency Procedural Invariants (matching default.json structure)
        return {
            "essence": "unknown_entity",
            "prompt_base": "cinematic portrait, realistic human features",
            "weights": {"depth": 0.70, "openpose": 0.45},
            "denoising_strength": 0.70,
            "negative_prompt": "anime, cartoon, low quality, drawing, flat colors, deformed",
            "realism_fragments": ["hyper-realistic, highly detailed, 8k", "photorealistic skin texture, dramatic light"]
        }

    def _get_lore_by_name(self, name: str) -> dict:
        """
        Implements the Hierarchical Dispatcher.
        Loads character-specific JSON and merges it with default values.
        """
        query = name.lower()
        json_files = glob.glob(os.path.join(self.lore_dir, "*.json"))
        
        # Start with default lore
        merged_lore = self._default_lore.copy()

        # Phase 1: Search for specific subject manifold
        for file_path in json_files:
            if "default.json" in file_path: 
                continue
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if any(alias in query for alias in data.get("aliases", [])):
                        # Character-specific lore overrides defaults
                        merged_lore.update(data)
                        return merged_lore
            except: 
                continue

        # If no specific lore found, return the default
        return merged_lore

    def _synthesize_prompt(self, lore: dict, lighting: str) -> str:
        """
        Creates a final, prioritized, and token-safe prompt manifold.
        
        Priority Order: Character Lore -> Realism Fragments -> Lighting/Aesthetics
        """
        
        # 1. CORE IDENTITY & LORE (Highest Priority)
        character_lore = lore.get('prompt_base', '')

        # 2. GLOBAL REALISM FRAGMENTS (Character overrides default if exists)
        realism_fragments = lore.get('realism_fragments', self._default_lore.get('realism_fragments', []))
        
        # 3. LIGHTING (Contextual Aesthetic)
        lighting_fragment = lighting.strip()  # Evita fragmentos vacíos
        
        # Combine in priority order: LORE -> REALISM -> LIGHTING
        raw_fragments = [character_lore] + realism_fragments
        if lighting_fragment:
            raw_fragments.append(lighting_fragment)
        
        # Token Cleaning and De-duplication Protocol
        all_words = []
        for frag_group in raw_fragments: 
            all_words.extend([w.strip().lower() for w in frag_group.split(',')])
        
        seen = set()
        clean_tokens = [w for w in all_words if w and not (w in seen or seen.add(w))]
        
        # Enforce a soft limit (70 tokens/segments) for safety
        final_prompt = ", ".join(clean_tokens[:70]) 
        
        return final_prompt
    
    def _detect_background_policy(self, image: Image.Image) -> str:
        """
        Determines whether to preserve background or generate new one.
        """
        # Transparent background
        if image.mode == "RGBA":
            alpha = np.array(image)[..., 3]
            if np.mean(alpha) < 15:  # Ajustado de 5 a 15
                return "preserve"

        # Nearly black background
        gray = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2GRAY)
        if np.mean(gray) < 15:
            return "preserve"

        return "generate"

    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        """
        Performs non-generative feature extraction and synthesizes the 
        final transformation strategy.
        """
        # Pixel Analysis
        img_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        background_policy = self._detect_background_policy(image)
        
        # Lore Ingestion (merging character + default)
        lore = self._get_lore_by_name(character_name)
        weights = lore.get("weights", {})
        
        # Dynamic Weight Extraction
        cn_depth = float(weights.get("depth", 0.75))
        cn_pose = float(weights.get("openpose", 0.40))
        strength = float(lore.get("denoising_strength", 0.70))
        
        # Semantic Signal Processing (Lighting)
        avg_brightness = np.mean(gray)
        lighting = ""
        if background_policy == "generate":
            lighting = "cinematic film still lighting"
            if avg_brightness < 80:
                lighting = "dramatic chiaroscuro lighting, rim light, deep shadows"
            elif avg_brightness > 180:
                lighting = "soft studio lighting, professional high-key photography"

        # Prompt Manifold Synthesis
        final_suggested_prompt = self._synthesize_prompt(lore, lighting)
        
        # Negative Prompt
        base_negative = lore.get("negative_prompt", "anime, cartoon, bad proportions")
        
        return AnalysisResult(
            recommended_steps=30,
            recommended_cfg=7.5,
            recommended_cn_depth=cn_depth,
            recommended_cn_pose=cn_pose,
            recommended_strength=strength,
            detected_essence=lore.get("essence", "unknown").upper(),
            suggested_prompt=final_suggested_prompt,
            suggested_negative=base_negative
        )
