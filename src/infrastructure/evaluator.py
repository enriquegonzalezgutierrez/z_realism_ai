# path: z_realism_ai/src/infrastructure/evaluator.py
# description: Scientific Assessment Engine v21.0 - Multivariate Analytics.
#              Provides objective quantification of generative fidelity.
#
# ARCHITECTURAL ROLE (Infrastructure Adapter):
# This module implements the 'ScientificEvaluatorPort'. It provides the 
# empirical evidence required to validate the transformation success.
# It measures the delta between stylized source and photorealistic output.
#
# SCIENTIFIC METRICS:
# 1. Structural Fidelity: Laplacian variance for edge preservation.
# 2. Chromatic Identity: Euclidean distance in the CIELAB color space.
# 3. Information Density: Relative Shannon Entropy gain (Textural Realism).
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
import time
from PIL import Image
from src.domain.ports import ScientificEvaluatorPort, AssessmentReport

class ComputerVisionEvaluator(ScientificEvaluatorPort):
    """
    Expert Multivariate Evaluation Engine for Neural Synthesis.

    Quantifies the "Realism" and "Identity Preservation" of a subject 
    by comparing structural, chromatic, and informational tensors.
    """

    def _preprocess(self, pil_image: Image.Image, target_size=(512, 512)) -> np.ndarray:
        """Standardizes input tensors into BGR domain for consistent CV analysis."""
        # Using LANCZOS (high-quality) to avoid aliasing artifacts during evaluation
        img = pil_image.convert('RGB').resize(target_size, Image.LANCZOS)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def _calculate_edge_fidelity(self, src: np.ndarray, gen: np.ndarray) -> float:
        """
        Structural Edge Retention using Laplacian Variance.
        
        Evaluates the preservation of high-frequency structural elements 
        (outlines and silhouettes). It measures if the 'skeleton' of the 
        anime character survived the diffusion process.
        """
        gray_src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        gray_gen = cv2.cvtColor(gen, cv2.COLOR_BGR2GRAY)

        # Calculate variance of the Laplacian (measures focus/edge strength)
        edge_src = cv2.Laplacian(gray_src, cv2.CV_64F).var()
        edge_gen = cv2.Laplacian(gray_gen, cv2.CV_64F).var()

        max_edge = max(edge_src, edge_gen, 1e-6)
        return min(edge_src, edge_gen) / max_edge

    def _calculate_color_dna(self, src: np.ndarray, gen: np.ndarray) -> float:
        """
        Perceptual Color DNA via CIELAB Moments.
        
        Measures the chromatic distance in the LAB color space, which is 
        designed to mimic human visual perception. High scores indicate 
        that the character's primary color palette remained intact.
        """
        lab_src = cv2.cvtColor(src, cv2.COLOR_BGR2LAB)
        lab_gen = cv2.cvtColor(gen, cv2.COLOR_BGR2LAB)

        mu_src, sigma_src = cv2.meanStdDev(lab_src)
        mu_gen, sigma_gen = cv2.meanStdDev(lab_gen)

        # Distance between means and standard deviations across L, A, and B
        dist = np.linalg.norm(mu_src - mu_gen) + np.linalg.norm(sigma_src - sigma_gen)
        
        # Normalize to a 0.0-1.0 scale (higher is better)
        return 1.0 / (1.0 + (dist / 100.0))

    def _calculate_entropy(self, image: np.ndarray) -> float:
        """
        Normalized Shannon Entropy (Information Density).
        
        Quantifies the randomness and complexity of the image data. 
        Photorealistic outputs should exhibit significantly higher entropy 
        than flat-shaded source drawings due to micro-textures (skin pores, 
        hair strands, fabric weave).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = np.histogram(gray.ravel(), bins=256)[0] / gray.size
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))
        
        return entropy / 8.0  # Normalized for 8-bit signal depth

    def assess_quality(
        self, 
        original_image: Image.Image, 
        generated_image: Image.Image,
        measure_time: bool = True
    ) -> AssessmentReport:
        """
        Primary entry point for multivariate scientific evaluation.
        
        RETURNS:
            AssessmentReport: A structured manifold of objective metrics.
        """
        start_time = time.time() if measure_time else None

        # Standardize manifolds
        img_src = self._preprocess(original_image)
        img_gen = self._preprocess(generated_image)

        # 1. Analyze Geometry (Structural Fidelity)
        edge_fidelity = self._calculate_edge_fidelity(img_src, img_gen)

        # 2. Analyze Chromatics (Identity Preservation)
        color_fidelity = self._calculate_color_dna(img_src, img_gen)

        # 3. Analyze Information Density (Textural Realism)
        # We calculate the gain: Entropy(Result) / Entropy(Source)
        # A ratio > 1.0 indicates a successful injection of real-world detail.
        entropy_src = self._calculate_entropy(img_src)
        entropy_gen = self._calculate_entropy(img_gen)
        realism_score = entropy_gen / max(entropy_src, 1e-6) 

        elapsed_time = time.time() - start_time if measure_time else 0.0

        return AssessmentReport(
            structural_similarity=round(float(edge_fidelity), 4),
            identity_preservation=round(float(color_fidelity), 4),
            textural_realism=round(float(realism_score), 4),
            inference_time=round(elapsed_time, 4),
            is_mock=False,
            full_prompt="Scientific analysis finalized. Metrics synchronized to domain."
        )