# path: z_realism_ai/src/infrastructure/analyzer.py
# description: Universal Heuristic Analyzer v9.7 - NAMEKIAN FIX.
#              ADDED: Specific logic for Piccolo to prevent fallback.
#              SAFETY: Additive change with no modification to existing rules.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
from PIL import Image
from src.domain.ports import ImageAnalyzerPort, AnalysisResult

class HeuristicImageAnalyzer(ImageAnalyzerPort):
    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        img_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        
        name = character_name.lower()
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (gray.size * 255)

        # --- RECALIBRATED HEURISTIC ENGINE v9.7 ---

        # 1. SAIYAN WARRIORS (Goku, Vegeta, etc.) - UNCHANGED
        if any(k in name for k in ["goku", "vegeta", "gohan", "broly", "trunks", "kakarot"]):
            essence = "species_saiyan_warrior"
            proposed_cn = [0.5, 0.8] # [Depth, OpenPose] - Balanced
            suggested_prompt = (
                "cinematic film still, a powerful muscular asian martial artist, "
                "hyper-detailed skin pores, sweat, realistic messy black hair, "
                "weathered heavy linen gi, intense warrior eyes, epic lighting"
            )

        # 2. DEITIES (Beerus, Champa, etc.) - UNCHANGED
        elif any(k in name for k in ["beerus", "bills", "champa", "destruction"]):
            essence = "species_deity_feline"
            proposed_cn = [0.6, 0.8] # More Depth for non-human head
            suggested_prompt = (
                "raw photo, realistic purple sphynx cat skin texture, "
                "muscular humanoid deity, gold egyptian artifacts, silk robes, "
                "glowing yellow eyes, divine atmosphere, cinematic rim lighting"
            )

        # --- NEW: NAMEKIAN SPECIES (PICCOLO) ---
        # This new block will catch Piccolo before the fallback
        elif any(k in name for k in ["piccolo", "picolo", "nail", "kami"]):
            essence = "species_namekian"
            # High weights for both to preserve alien anatomy
            proposed_cn = [0.7, 0.85] 
            suggested_prompt = (
                "raw photo, realistic green alien man, damp amphibian skin texture, "
                "organic pointed ears, muscular anatomy, realistic purple martial arts gi, "
                "cinematic lighting, masterpiece"
            )

        # 3. ANGELS & CELESTIALS - UNCHANGED
        elif any(k in name for k in ["whis", "vados", "priest", "angel"]):
            essence = "species_celestial"
            proposed_cn = [0.4, 0.75]
            suggested_prompt = (
                "cinematic portrait, ethereal pale celeste skin, youthful refined face, "
                "glowing halo, elegant silk robes, white vertical natural hair, "
                "soft volumetric studio lighting, high-end photography"
            )

        # 4. ANCIENT & ELITE VILLAINS - UNCHANGED
        elif any(k in name for k in ["moro", "jiren", "hit", "black", "zamasu"]):
            essence = "species_elite_adversary"
            proposed_cn = [0.6, 0.8]
            suggested_prompt = (
                "cinematic still, hyper-detailed musculature, real alien skin texture, "
                "weathered combat suit fibers, dramatic lighting, cinematic film grain"
            )

        # 5. HUMAN-TYPES - UNCHANGED
        elif any(k in name for k in ["18", "17", "bulma", "videl", "roshi", "yamcha"]):
            essence = "species_human_android"
            proposed_cn = [0.45, 0.85] # High OpenPose for human faces
            suggested_prompt = (
                "raw photography, realistic human face, sharp focus on eyes, "
                "highly detailed skin texture, individual hair strands, "
                "authentic clothing fabric, masterpiece, 8k uhd"
            )

        # 6. UNIVERSAL FALLBACK - UNCHANGED
        else:
            essence = "cinematic_fallback"
            proposed_cn = [0.5, 0.8]
            suggested_prompt = "cinematic film still, highly detailed human version, realistic textures, 8k"

        # The Analyzer no longer suggests ControlNet weights, as they are fixed in sd_generator
        return AnalysisResult(
            recommended_steps=30,
            recommended_cfg=7.5,
            recommended_cn=0.0, # This value is now ignored
            detected_essence=f"{essence} (Lore-Aware v9.7)",
            suggested_prompt=suggested_prompt
        )