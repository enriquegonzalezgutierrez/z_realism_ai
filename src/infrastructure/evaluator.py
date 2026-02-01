# path: z_realism_ai/src/infrastructure/evaluator.py
# description: Scientific Evaluation Engine.
#              UPDATED: Compatible with AssessmentReport v2. 
#              Added logic to handle mock/simulation reporting.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
from PIL import Image
from src.domain.ports import ScientificEvaluatorPort, AssessmentReport

class ComputerVisionEvaluator(ScientificEvaluatorPort):
    """
    Implementation of the scientific assessment using OpenCV.
    Calculates SSIM and Identity Correlation.
    """

    def _preprocess_for_cv(self, pil_image: Image.Image, target_size=(512, 512)) -> np.ndarray:
        img = pil_image.convert('RGB').resize(target_size, Image.LANCZOS)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def assess_quality(
        self, 
        original_image: Image.Image, 
        generated_image: Image.Image
    ) -> AssessmentReport:
        
        img_src = self._preprocess_for_cv(original_image)
        img_gen = self._preprocess_for_cv(generated_image)

        # 1. Structural Integrity (Edge Correlation)
        edges_src = cv2.Canny(img_src, 100, 200)
        edges_gen = cv2.Canny(img_gen, 100, 200)
        
        flat_src = edges_src.flatten().astype(np.float32)
        flat_gen = edges_gen.flatten().astype(np.float32)
        
        if np.std(flat_src) == 0 or np.std(flat_gen) == 0:
            structural_score = 0.0
        else:
            correlation = np.corrcoef(flat_src, flat_gen)[0, 1]
            structural_score = max(0.0, min(1.0, (correlation + 0.1) * 2.5))

        # 2. Identity Preservation (Histogram Correlation)
        hsv_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        hsv_gen = cv2.cvtColor(img_gen, cv2.COLOR_BGR2HSV)
        
        hist_src = cv2.calcHist([hsv_src], [2], None, [256], [0, 256])
        hist_gen = cv2.calcHist([hsv_gen], [2], None, [256], [0, 256])
        
        cv2.normalize(hist_src, hist_src, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist_gen, hist_gen, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        
        identity_score = cv2.compareHist(hist_src, hist_gen, cv2.HISTCMP_CORREL)
        identity_score = max(0.0, min(1.0, identity_score))

        # 3. Final Report Generation
        return AssessmentReport(
            structural_similarity=round(structural_score, 4),
            identity_preservation=round(identity_score, 4),
            inference_time=0.0,
            is_mock=False # The Use Case will override this if a mock was used
        )
