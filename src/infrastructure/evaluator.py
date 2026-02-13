# path: src/infrastructure/evaluator.py
# description: Scientific Assessment Engine v22.2 - Multi-Scale Perceptual Analytics.
#              Provides objective quantification of generative fidelity gain.
#
# ARCHITECTURAL ROLE (Infrastructure Adapter):
# This module implements the 'ScientificEvaluatorPort'. It serves as the 
# empirical validation layer, quantifying the delta between stylized source 
# manifolds and photorealistic latent outputs across varying resolutions.
#
# SCIENTIFIC METHODOLOGY (v22.2):
# 1. Multi-Scale Structural Fidelity: Implements an internal downsampling 
#    protocol to establish a "Geometric Ground Truth." By analyzing edge maps 
#    at a normalized 256px grid, the engine filters out photorealistic 
#    micro-noise (pores, hair strands) and focuses on character silhouette 
#    and macro-anatomy alignment.
# 2. Normalized Cross-Correlation (NCC): Replaces standard Pearson coefficients 
#    with NCC to ensure mathematical stability in regions of flat chromatic 
#    variance (common in anime source data).
# 3. Perceptual Chromatic Identity: Utilizes HSV Histogram Correlation to 
#    validate color family consistency (Hue-preservation) despite complex 
#    realistic lighting injections.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import cv2
import numpy as np
import time
from PIL import Image
from src.domain.ports import ScientificEvaluatorPort, AssessmentReport

class ComputerVisionEvaluator(ScientificEvaluatorPort):
    """
    Expert Perceptual Evaluation Engine for Neural Synthesis.
    
    This engine quantifies structural and chromatic fidelity using resolution-agnostic 
    heuristics, ensuring that high-resolution textural realism does not 
    negatively impact the underlying geometric identity score.
    """

    def _preprocess(self, pil_image: Image.Image, target_size=(512, 512)) -> np.ndarray:
        """Standardizes input manifolds into BGR domain for consistent OpenCV analysis."""
        # Using High-Quality LANCZOS resampling to establish the comparison baseline.
        img = pil_image.convert('RGB').resize(target_size, Image.LANCZOS)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def _calculate_edge_fidelity(self, src: np.ndarray, gen: np.ndarray) -> float:
        """
        Structural Fidelity via Multi-Scale Edge Correlation (MSEC).
        
        This method resolves the 'Resolution Penalty' by downsampling Sobel 
        gradient maps to a macro-feature grid. This allows the engine to 
        validate the character's pose and facial structure while being 'blind' 
        to high-resolution skin textures that would otherwise lower the score.
        """
        # 1. Grayscale Conversion
        gray_src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        gray_gen = cv2.cvtColor(gen, cv2.COLOR_BGR2GRAY)

        # 2. Gradient Extraction (Sobel Operators)
        # We capture the structural 'skeleton' using a 5x5 kernel for robustness.
        sobel_src = cv2.Sobel(gray_src, cv2.CV_64F, 1, 1, ksize=5)
        sobel_gen = cv2.Sobel(gray_gen, cv2.CV_64F, 1, 1, ksize=5)
        
        # 3. Dynamic Range Normalization
        sobel_src = cv2.convertScaleAbs(sobel_src)
        sobel_gen = cv2.convertScaleAbs(sobel_gen)

        # 4. INTERNAL MULTI-SCALE DOWNSAMPLING (The Resolution Fix)
        # We resize both structural maps to 256x256. This filters out 
        # high-frequency realistic noise and retains the Subject's DNA.
        eval_grid = (256, 256)
        low_res_src = cv2.resize(sobel_src, eval_grid, interpolation=cv2.INTER_AREA)
        low_res_gen = cv2.resize(sobel_gen, eval_grid, interpolation=cv2.INTER_AREA)

        # 5. Normalized Cross-Correlation (NCC)
        # TM_CCOEFF_NORMED is used to provide an intensity-invariant 
        # correlation score between the source and generated geometry.
        res = cv2.matchTemplate(low_res_gen, low_res_src, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        
        return max(0.0, float(max_val))

    def _calculate_perceptual_color(self, src: np.ndarray, gen: np.ndarray) -> float:
        """
        Chromatic Identity via HSV Histogram Correlation.
        
        Focuses on the Hue (H) channel to ensure the Subject's base colors 
        (e.g., Red skin, Black hair) are preserved regardless of 
        shading or highlights added by the diffusion process.
        """
        hsv_src = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        hsv_gen = cv2.cvtColor(gen, cv2.COLOR_BGR2HSV)
        
        # Hue histograms (180 bins covering the full 360-degree color wheel)
        hist_src = cv2.calcHist([hsv_src], [0], None, [180], [0, 180])
        hist_gen = cv2.calcHist([hsv_gen], [0], None, [180], [0, 180])
        
        cv2.normalize(hist_src, hist_src, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist_gen, hist_gen, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        
        # Compute Correlation coefficient (1.0 = Chromatic match)
        similarity = cv2.compareHist(hist_src, hist_gen, cv2.HISTCMP_CORREL)
        return (float(similarity) + 1.0) / 2.0

    def _calculate_entropy(self, image: np.ndarray) -> float:
        """
        Normalized Shannon Entropy (Information Density Gain).
        
        Measures the complexity of the output signal. Successful transformations 
        should exhibit an entropy gain indicating the successful injection 
        of real-world textural information.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = np.histogram(gray.ravel(), bins=256)[0] / gray.size
        hist = hist[hist > 0]
        return -np.sum(hist * np.log2(hist)) / 8.0

    def assess_quality(
        self, 
        original_image: Image.Image, 
        generated_image: Image.Image
    ) -> AssessmentReport:
        """
        Primary entry point for multivariate scientific evaluation.
        
        Analyzes the transformation quality by comparing structural, 
        chromatic, and informational fidelity across resolutions.
        """
        start_time = time.time()

        # Standardize manifolds for baseline comparison
        img_src = self._preprocess(original_image)
        img_gen = self._preprocess(generated_image)

        # 1. Evaluate Geometry (Silhouette Alignment)
        edge_fidelity = self._calculate_edge_fidelity(img_src, img_gen)

        # 2. Evaluate Chromatics (Subject DNA Color)
        color_fidelity = self._calculate_perceptual_color(img_src, img_gen)

        # 3. Evaluate Realism (Information Entropy Gain)
        entropy_src = self._calculate_entropy(img_src)
        entropy_gen = self._calculate_entropy(img_gen)
        realism_score = entropy_gen / max(entropy_src, 1e-6) 

        elapsed_time = time.time() - start_time

        return AssessmentReport(
            structural_similarity=round(float(edge_fidelity), 4),
            identity_preservation=round(float(color_fidelity), 4),
            textural_realism=round(float(realism_score), 4),
            inference_time=round(float(elapsed_time), 4),
            is_mock=False,
            full_prompt="Scientific Perceptual Multi-Scale Analysis finalized. Metrics synchronized."
        )