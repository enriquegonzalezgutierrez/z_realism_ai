# path: z_realism_ai/src/infrastructure/analyzer.py
# description: Universal Dragon Ball Heuristic Analyzer v5.5.
#              FEATURING: Specific Form Detection (Black/Golden) and 
#              expanded character knowledge base (Tien, Krillin, Jiren).
#              FIXED: Majin detection now requires high pink saturation 
#              to avoid false positives with skin tones or warm lighting.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
from PIL import Image
from src.domain.ports import ImageAnalyzerPort, AnalysisResult

class HeuristicImageAnalyzer(ImageAnalyzerPort):
    """
    Final PhD-Grade Analyzer. 
    Handles species, specific transformations, and environment noise filtering.
    """

    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        img_np = np.array(image.convert('RGB'))
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        name = character_name.lower()
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (gray.size * 255)

        # --- ADVANCED COLOR DNA (v5.5) ---
        # Majin Pink (More specific range to avoid skin false positives)
        mask_pink = cv2.inRange(img_hsv, np.array([145, 80, 80]), np.array([165, 255, 255]))
        # Frost Demon Purple/Obsidian
        mask_purple = cv2.inRange(img_hsv, np.array([120, 50, 50]), np.array([140, 255, 255]))
        # Namekian Green
        mask_green = cv2.inRange(img_hsv, np.array([35, 40, 40]), np.array([90, 255, 255]))
        
        pink_ratio = np.sum(mask_pink > 0) / mask_pink.size
        purple_ratio = np.sum(mask_purple > 0) / mask_purple.size
        green_ratio = np.sum(mask_green > 0) / mask_green.size

        # --- EXPERT REASONING ENGINE ---

        # 1. HUMANOIDS & MONKS (Ten Shin Han, Krillin, Roshi, Chi-Chi, Videl, etc.)
        if any(k in name for k in ["ten", "tien", "han", "krillin", "roshi", "chi", "videl", "satan", "yamcha", "chiaotzu", "jiren", "bulma", "17", "18"]):
            essence = "species_humanoid_monk"
            proposed_cn = 0.42 + (edge_density * 0.3)
            suggested_prompt = (
                "raw photo, human facial features, realistic skin texture, "
                "martial arts uniform, fabric fibers, cinematic soft lighting"
            )

        # 2. SAIYANS (Goku, Vegeta, Gohan, Trunks, Broly)
        elif any(k in name for k in ["goku", "vegeta", "gohan", "trunks", "broly", "kakarot"]):
            essence = "species_saiyan_warrior"
            proposed_cn = 0.45 + (edge_density * 0.4)
            suggested_prompt = (
                "raw photo, muscular human build, intense eyes, skin pores, "
                "messy real hair texture, combat gi, cinematic lighting"
            )

        # 3. FROST DEMONS & FORMS (Frieza, Cooler)
        elif any(k in name for k in ["frieza", "freezer", "cooler"]):
            if "black" in name:
                essence = "form_black_frieza"
                proposed_cn = 0.68
                suggested_prompt = (
                    "raw photo, black obsidian biological armor, metallic silver plates, "
                    "purple bio-gems, dark reptilian skin, cinematic rim lighting"
                )
            elif "gold" in name:
                essence = "form_golden_frieza"
                proposed_cn = 0.65
                suggested_prompt = "raw photo, polished gold organic armor, purple gems, glowing skin"
            else:
                essence = "species_frost_demon_base"
                proposed_cn = 0.62
                suggested_prompt = "raw photo, white reptilian skin, purple bio-gems, polished biological armor"

        # 4. MAJINS (Buu) - Strong verification required
        elif "buu" in name or (pink_ratio > 0.15):
            essence = "species_majin_entity"
            proposed_cn = 0.50
            suggested_prompt = (
                "raw photo, pink rubbery skin, organic smooth surface, "
                "muscular anatomy, realistic steam vents, accurate attire"
            )

        # 5. BIO-ANDROIDS (Cell)
        elif "cell" in name or (green_ratio > 0.05 and edge_density > 0.07):
            essence = "species_bio_android"
            proposed_cn = 0.72
            suggested_prompt = (
                "raw photo, biological exoskeleton, chitinous plates, "
                "insectoid skin, organic spots, cinematic studio lighting"
            )

        # 6. NAMEKIANS (Piccolo)
        elif "piccolo" in name or "picolo" in name:
            essence = "species_namekian"
            proposed_cn = 0.52
            suggested_prompt = "raw photo, smooth green alien skin, damp amphibian texture, pointed ears"

        # 7. UNIVERSAL FALLBACK
        else:
            essence = "fallback_heuristic"
            proposed_cn = 0.50
            suggested_prompt = "raw photo, detailed face, cinematic lighting, high resolution"

        # Global Clamps
        proposed_cn = min(max(proposed_cn, 0.40), 0.85)
        proposed_cfg = min(max(8.5 - (gray.std() / 20.0), 6.0), 8.5)

        return AnalysisResult(
            recommended_steps=20,
            recommended_cfg=round(proposed_cfg, 2),
            recommended_cn=round(proposed_cn, 2),
            detected_essence=f"{essence} (Expert Logic v5.5)",
            suggested_prompt=suggested_prompt
        )