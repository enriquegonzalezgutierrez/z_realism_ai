# path: z_realism_ai/src/infrastructure/evaluator.py
# description: Advanced Scientific Evaluation Engine v10.5.
#              Implements Multivariate Analysis: Structural Edge Fidelity, 
#              Perceptual Color Moments, and Shannon Entropy.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
from PIL import Image
from src.domain.ports import ScientificEvaluatorPort, AssessmentReport

class ComputerVisionEvaluator(ScientificEvaluatorPort):
    """
    Multivariate Assessment Engine for Generative Synthesis.
    Quantifies the scientific delta between 2D source and Live-Action output.
    """

    def _preprocess(self, pil_image: Image.Image, target_size=(512, 512)) -> np.ndarray:
        """Standardizes inputs into the BGR/LAB domain."""
        img = pil_image.convert('RGB').resize(target_size, Image.LANCZOS)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def _calculate_edge_fidelity(self, src: np.ndarray, gen: np.ndarray) -> float:
        """
        Calculates the retention of the character's silhouette using 
        Laplacian Variance Analysis.
        """
        # Convert to grayscale
        gray_src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        gray_gen = cv2.cvtColor(gen, cv2.COLOR_BGR2GRAY)

        # Extract structural edges (high-frequency components)
        edge_src = cv2.Laplacian(gray_src, cv2.CV_64F).var()
        edge_gen = cv2.Laplacian(gray_gen, cv2.CV_64F).var()

        # Structural Edge Correlation
        # We use a normalized ratio to see how much 'definition' was maintained
        return min(edge_src, edge_gen) / max(edge_src, edge_gen)

    def _calculate_color_dna(self, src: np.ndarray, gen: np.ndarray) -> float:
        """
        Perceptual Color DNA analysis using LAB Color Space Moments.
        LAB is used because it separates Luminance from Chrominance (Identity).
        """
        lab_src = cv2.cvtColor(src, cv2.COLOR_BGR2LAB)
        lab_gen = cv2.cvtColor(gen, cv2.COLOR_BGR2LAB)

        # Calculate Mean and StdDev for each channel (L, A, B)
        (mu_src, sigma_src) = cv2.meanStdDev(lab_src)
        (mu_gen, sigma_gen) = cv2.meanStdDev(lab_gen)

        # Euclidean distance between color moments (Lower is better, then normalized)
        dist = np.linalg.norm(mu_src - mu_gen) + np.linalg.norm(sigma_src - sigma_gen)
        
        # Normalize: 0 (different) to 1 (identical color DNA)
        return 1.0 / (1.0 + (dist / 100.0))

    def _calculate_entropy(self, image: np.ndarray) -> float:
        """
        Calculates Shannon Entropy to measure the 'Realism Density'.
        High entropy suggests the addition of fine details (skin pores, textures).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        marg = np.histogramdd(gray.ravel(), bins=256)[0] / gray.size
        marg = list(filter(lambda p: p > 0, marg))
        entropy = -np.sum(np.multiply(marg, np.log2(marg)))
        return entropy / 8.0 # Normalized 0 to 1

    def assess_quality(
        self, 
        original_image: Image.Image, 
        generated_image: Image.Image
    ) -> AssessmentReport:
        """
        Executes a three-stage scientific assessment pipeline.
        """
        # 1. Image Normalization
        img_src = self._preprocess(original_image)
        img_gen = self._preprocess(generated_image)

        # 2. Extract Multivariate Metrics
        edge_fidelity = self._calculate_edge_fidelity(img_src, img_gen)
        color_fidelity = self._calculate_color_dna(img_src, img_gen)
        realism_score = self._calculate_entropy(img_gen)

        # 3. Weighted Result Assembly
        # SSIM Proxy = Edge Fidelity (Structure)
        # Identity = Color DNA (Identity)
        structural_ssim = round(float(edge_fidelity), 4)
        identity_retention = round(float(color_fidelity), 4)

        # In a PhD context, we can use the realism_score for the log, 
        # though the port only asks for SSIM and ID for now.
        return AssessmentReport(
            structural_similarity=structural_ssim,
            identity_preservation=identity_retention,
            inference_time=0.0, # Handled by Use Case
            is_mock=False,
            full_prompt=f"Detail Entropy: {round(realism_score, 2)}" # Traceability
        )