# path: z_realism_ai/src/infrastructure/analyzer.py
# description: Universal Heuristic Analyzer v9.5 - Recalibrated Master Edition.
#              FEATURING: Precise parameters for Realistic Vision V5.1.
#              STRATEGY: Balanced steps (25-30) for high-fidelity skin textures.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
from PIL import Image
from src.domain.ports import ImageAnalyzerPort, AnalysisResult

class HeuristicImageAnalyzer(ImageAnalyzerPort):
    """
    Expert Visual Intelligence v9.5.
    Determines character-specific strategies for the full DBS roster.
    Recalibrated for the non-lightning Realistic Vision pipeline.
    """

    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        # Visual DNA Extraction via OpenCV
        img_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        
        name = character_name.lower()
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (gray.size * 255)

        # --- RECALIBRATED HEURISTIC ENGINE v9.5 ---
        # Target Architecture: Realistic Vision V5.1 (Standard Diffusion)
        # Optimal CFG: 7.0 - 8.0
        # Optimal Steps: 25 - 35

        # 1. SAIYAN WARRIORS (Goku, Vegeta, Broly, Gohan)
        if any(k in name for k in ["goku", "vegeta", "gohan", "broly", "trunks", "kakarot"]):
            essence = "species_saiyan_warrior"
            # Depth weight calibrated to allow IP-Adapter facial reconstruction
            proposed_cn = 0.62 + (edge_density * 0.1)
            suggested_prompt = (
                "cinematic film still, a powerful muscular asian martial artist, "
                "hyper-detailed skin pores, sweat, realistic messy black hair, "
                "weathered heavy linen gi, intense warrior eyes, epic lighting"
            )

        # 2. DEITIES (Beerus, Champa, Sidra)
        elif any(k in name for k in ["beerus", "bills", "champa", "destruction"]):
            essence = "species_deity_feline"
            proposed_cn = 0.78 # High depth weight for non-human head geometry
            suggested_prompt = (
                "raw photo, realistic purple sphynx cat skin texture, "
                "muscular humanoid deity, gold egyptian artifacts, silk robes, "
                "glowing yellow eyes, divine atmosphere, cinematic rim lighting"
            )

        # 3. ANGELS & CELESTIALS (Whis, Vados, Grand Priest)
        elif any(k in name for k in ["whis", "vados", "priest", "angel"]):
            essence = "species_celestial"
            proposed_cn = 0.58
            suggested_prompt = (
                "cinematic portrait, ethereal pale celeste skin, youthful refined face, "
                "glowing halo, elegant silk robes, white vertical natural hair, "
                "soft volumetric studio lighting, high-end photography"
            )

        # 4. ANCIENT & ELITE VILLAINS (Moro, Jiren, Hit, Goku Black)
        elif any(k in name for k in ["moro", "jiren", "hit", "black", "zamasu"]):
            essence = "species_elite_adversary"
            proposed_cn = 0.72
            suggested_prompt = (
                "cinematic still, hyper-detailed musculature, real alien skin texture, "
                "weathered combat suit fibers, dramatic lighting, cinematic film grain, "
                "terrifying presence, masterpiece photography"
            )

        # 5. HUMAN-TYPES (Android 18/17, Bulma, Videl, Roshi)
        elif any(k in name for k in ["18", "17", "bulma", "videl", "roshi", "yamcha"]):
            essence = "species_human_android"
            proposed_cn = 0.52
            suggested_prompt = (
                "raw photography, realistic human face, sharp focus on eyes, "
                "highly detailed skin texture, individual hair strands, "
                "authentic clothing fabric, masterpiece, 8k uhd"
            )

        # 6. UNIVERSAL FALLBACK
        else:
            essence = "cinematic_fallback"
            proposed_cn = 0.60
            suggested_prompt = "cinematic film still, highly detailed human version, realistic textures, 8k"

        # Final Parameter Logic for v9.5 Stability
        return AnalysisResult(
            recommended_steps=30,     # Standard steps for v5.1 Realism
            recommended_cfg=7.5,      # High contrast guidance
            recommended_cn=round(proposed_cn, 2),
            detected_essence=f"{essence} (Lore-Aware v9.5)",
            suggested_prompt=suggested_prompt
        )