# path: z_realism_ai/src/infrastructure/analyzer.py
# description: Expert Heuristic Analyzer v20.0 - Multi-Modal Strategy Synthesis.
#
# ABSTRACT:
# This module serves as the intelligence layer for the Z-Realism ecosystem. 
# It performs heuristic analysis on pixel manifolds and retrieves character-specific 
# lore from the JSON library to synthesize optimal generation strategies.
#
# ARCHITECTURAL EVOLUTION (v20.0):
# 1. Temporal Lore Support: Refactored lore retrieval to support the 
#    AnimateCharacterUseCase, ensuring visual consistency in video synthesis.
# 2. Token Safety (Maintained): Ensures synthesized prompts remain within 
#    the high-priority CLIP window (max 70 segments).
# 3. Hierarchical Merging: Character-specific JSONs always override the 
#    default.json manifold for precision targeting.
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
    hyperparameter space for both Stills and Video.
    """

    def __init__(self):
        # Path to the Domain-Specific Lore Library
        self.lore_dir = "/app/src/domain/lore/"
        # Load the global default lore once to optimize performance
        self._default_lore = self._load_default_lore()

    def _load_default_lore(self) -> dict:
        """Loads the global default lore configuration including realism fragments."""
        default_path = os.path.join(self.lore_dir, "default.json")
        if os.path.exists(default_path):
            try:
                with open(default_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"WARNING: Could not load default lore file. Using invariants. Error: {e}")
        
        # Emergency Procedural Invariants (Safety Fallback)
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
        
        # Start with a copy of the default lore
        merged_lore = self._default_lore.copy()

        # Search for specific subject manifold
        for file_path in json_files:
            if "default.json" in file_path: 
                continue
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Check if the character name matches any alias in the JSON
                    if any(alias in query for alias in data.get("aliases", [])):
                        # Character-specific lore overrides defaults
                        merged_lore.update(data)
                        return merged_lore
            except: 
                continue

        # If no specific lore found, return the sanitized default
        return merged_lore

    def _synthesize_prompt(self, lore: dict, lighting: str) -> str:
        """
        Creates a final, prioritized, and token-safe prompt manifold.
        Priority: Character Lore -> Realism Fragments -> Contextual Lighting.
        """
        # 1. CORE IDENTITY (Highest Priority)
        character_lore = lore.get('prompt_base', '')

        # 2. GLOBAL REALISM (Character overrides default if exists)
        realism_fragments = lore.get('realism_fragments', self._default_lore.get('realism_fragments', []))
        
        # 3. LIGHTING (Contextual Aesthetic from CV Analysis)
        lighting_fragment = lighting.strip()
        
        # Combine in priority order
        raw_fragments = [character_lore] + realism_fragments
        if lighting_fragment:
            raw_fragments.append(lighting_fragment)
        
        # Token Cleaning and De-duplication Protocol
        all_words = []
        for frag_group in raw_fragments: 
            all_words.extend([w.strip().lower() for w in frag_group.split(',')])
        
        seen = set()
        clean_tokens = [w for w in all_words if w and not (w in seen or seen.add(w))]
        
        # Enforce a soft limit (70 tokens) for CLIP safety
        return ", ".join(clean_tokens[:70]) 
    
    def _detect_background_policy(self, image: Image.Image) -> str:
        """Determines whether to preserve original background or generate a new one."""
        # Detect Transparent backgrounds (PNG)
        if image.mode == "RGBA":
            alpha = np.array(image)[..., 3]
            if np.mean(alpha) < 15:
                return "preserve"

        # Detect nearly black backgrounds
        gray = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2GRAY)
        if np.mean(gray) < 15:
            return "preserve"

        return "generate"

    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        """
        Primary entry point for feature extraction and strategy synthesis.
        Works for both static Image2Image and temporal Video generation.
        """
        # Pixel-level Computer Vision analysis
        img_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        background_policy = self._detect_background_policy(image)
        
        # Domain Lore Retrieval
        lore = self._get_lore_by_name(character_name)
        weights = lore.get("weights", {})
        
        # Hyperparameter Extraction
        cn_depth = float(weights.get("depth", 0.75))
        cn_pose = float(weights.get("openpose", 0.40))
        strength = float(lore.get("denoising_strength", 0.70))
        
        # Semantic Lighting Analysis
        avg_brightness = np.mean(gray)
        lighting = ""
        if background_policy == "generate":
            lighting = "cinematic film still lighting"
            if avg_brightness < 80:
                lighting = "dramatic chiaroscuro lighting, rim light, deep shadows"
            elif avg_brightness > 180:
                lighting = "soft studio lighting, professional high-key photography"

        # Construct the final synthesized prompt manifold
        final_suggested_prompt = self._synthesize_prompt(lore, lighting)
        
        # Negative prompt consolidation
        base_negative = lore.get("negative_prompt", "anime, cartoon, low quality")
        
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