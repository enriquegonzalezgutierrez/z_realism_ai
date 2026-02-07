# path: z_realism_ai/src/infrastructure/evaluator.py
# description: Advanced Scientific Evaluation Engine v18.1 - Robust Multivariate Analysis.
#
# ABSTRACT:
# Enhanced version of the ScientificEvaluatorPort.
# Adds robust handling for flat images, relative entropy comparison, 
# and optional inference timing.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
import time
from PIL import Image
from src.domain.ports import ScientificEvaluatorPort, AssessmentReport

class ComputerVisionEvaluator(ScientificEvaluatorPort):
    """
    Robust Multivariate Assessment Engine for Generative Synthesis.

    Provides objective scientific metrics for "Realism" and "Identity"
    by comparing structural, chromatic, and informational fidelity.
    """

    def _preprocess(self, pil_image: Image.Image, target_size=(512, 512)) -> np.ndarray:
        """Standardizes input tensors into BGR domain for consistent CV analysis."""
        img = pil_image.convert('RGB').resize(target_size, Image.LANCZOS)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def _calculate_edge_fidelity(self, src: np.ndarray, gen: np.ndarray) -> float:
        """Structural Edge Retention using Laplacian variance, normalized."""
        gray_src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        gray_gen = cv2.cvtColor(gen, cv2.COLOR_BGR2GRAY)

        edge_src = cv2.Laplacian(gray_src, cv2.CV_64F).var()
        edge_gen = cv2.Laplacian(gray_gen, cv2.CV_64F).var()

        # Avoid division by zero
        max_edge = max(edge_src, edge_gen, 1e-6)
        return min(edge_src, edge_gen) / max_edge

    def _calculate_color_dna(self, src: np.ndarray, gen: np.ndarray) -> float:
        """Perceptual Color DNA via LAB moments."""
        lab_src = cv2.cvtColor(src, cv2.COLOR_BGR2LAB)
        lab_gen = cv2.cvtColor(gen, cv2.COLOR_BGR2LAB)

        mu_src, sigma_src = cv2.meanStdDev(lab_src)
        mu_gen, sigma_gen = cv2.meanStdDev(lab_gen)

        dist = np.linalg.norm(mu_src - mu_gen) + np.linalg.norm(sigma_src - sigma_gen)
        return 1.0 / (1.0 + (dist / 100.0))

    def _calculate_entropy(self, image: np.ndarray) -> float:
        """Normalized Shannon entropy (0.0–1.0) over grayscale channel."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = np.histogram(gray.ravel(), bins=256)[0] / gray.size
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))
        return entropy / 8.0  # normalize for 8-bit images

    def assess_quality(
        self, 
        original_image: Image.Image, 
        generated_image: Image.Image,
        measure_time: bool = True
    ) -> AssessmentReport:
        """Performs a robust multivariate evaluation of generative fidelity."""
        start_time = time.time() if measure_time else None

        img_src = self._preprocess(original_image)
        img_gen = self._preprocess(generated_image)

        # Structural fidelity
        edge_fidelity = self._calculate_edge_fidelity(img_src, img_gen)

        # Identity preservation
        color_fidelity = self._calculate_color_dna(img_src, img_gen)

        # Textural realism (entropy relative to source)
        entropy_src = self._calculate_entropy(img_src)
        entropy_gen = self._calculate_entropy(img_gen)
        realism_score = entropy_gen / max(entropy_src, 1e-6)  # relative entropy

        elapsed_time = time.time() - start_time if measure_time else 0.0

        return AssessmentReport(
            structural_similarity=round(float(edge_fidelity), 4),
            identity_preservation=round(float(color_fidelity), 4),
            inference_time=round(elapsed_time, 4),
            is_mock=False,
            full_prompt=f"Textural Information Density (relative): {round(realism_score, 3)}"
        )
