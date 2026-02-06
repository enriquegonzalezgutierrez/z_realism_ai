# path: z_realism_ai/src/infrastructure/evaluator.py
# description: Scientific Evaluation Engine v5.0.
#              Implements Structural Similarity (SSIM) and HSV Histogram 
#              Correlation for precise identity tracking.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
from PIL import Image
from src.domain.ports import ScientificEvaluatorPort, AssessmentReport

class ComputerVisionEvaluator(ScientificEvaluatorPort):
    """
    Expert implementation of scientific quality assessment using OpenCV.
    Quantifies structural and chromatic fidelity between source and output.
    """

    def _preprocess_for_cv(self, pil_image: Image.Image, target_size=(512, 512)) -> np.ndarray:
        """Standardizes images for mathematical comparison."""
        img = pil_image.convert('RGB').resize(target_size, Image.LANCZOS)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def assess_quality(
        self, 
        original_image: Image.Image, 
        generated_image: Image.Image
    ) -> AssessmentReport:
        """
        Calculates SSIM and Identity Correlation using multi-stage CV heuristics.
        """
        
        # 1. Domain Standardization
        img_src = self._preprocess_for_cv(original_image)
        img_gen = self._preprocess_for_cv(generated_image)

        # 2. Structural Integrity Assessment (Gaussian SSIM Proxy)
        # We compare structural gradients while ignoring high-frequency noise.
        gray_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
        gray_gen = cv2.cvtColor(img_gen, cv2.COLOR_BGR2GRAY)
        
        # Focus on major structural forms (muscles, clothes, pose)
        blur_src = cv2.GaussianBlur(gray_src, (5, 5), 0)
        blur_gen = cv2.GaussianBlur(gray_gen, (5, 5), 0)
        
        # Cross-correlation metric (1.0 = perfect structural match)
        structural_score = cv2.matchTemplate(blur_src, blur_gen, cv2.TM_CCOEFF_NORMED)[0][0]
        structural_score = max(0.0, float(structural_score))

        # 3. Identity Preservation (HSV Histogram Correlation)
        # We use HSV space because it separates 'Color' (Identity) from 'Lighting'.
        hsv_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        hsv_gen = cv2.cvtColor(img_gen, cv2.COLOR_BGR2HSV)
        
        # Calculate Hue and Saturation histograms
        hist_src = cv2.calcHist([hsv_src], [0, 1], None, [50, 60], [0, 180, 0, 256])
        hist_gen = cv2.calcHist([hsv_gen], [0, 1], None, [50, 60], [0, 180, 0, 256])
        
        cv2.normalize(hist_src, hist_src, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist_gen, hist_gen, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        
        # Correlation measures how similar the color 'DNA' is.
        identity_score = cv2.compareHist(hist_src, hist_gen, cv2.HISTCMP_CORREL)
        identity_score = max(0.0, min(1.0, float(identity_score)))

        # 4. Final Scientific Packaging
        return AssessmentReport(
            structural_similarity=round(structural_score, 4),
            identity_preservation=round(identity_score, 4),
            inference_time=0.0, # Filled by Use Case after execution
            is_mock=False
        )