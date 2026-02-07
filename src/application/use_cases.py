# path: z_realism_ai/src/application/use_cases.py
# description: Application Orchestration Layer v18.0 - Transformation Pipeline.
#
# ABSTRACT:
# This module implements the primary business logic for the Z-Realism engine. 
# It acts as a Pure Application Service that coordinates the interaction 
# between the Generative Engine and the Scientific Evaluator.
#
# ARCHITECTURAL ROLE:
# 1. Orchestration: Manages the sequential lifecycle of a transformation task 
#    (Synthesis -> Assessment -> Metadata Enrichment).
# 2. Decoupling: Utilizes Inversion of Control (IoC) to interact with domain 
#    ports, allowing the underlying technology (e.g., Stable Diffusion vs. Mock) 
#    to be swapped without modifying the use case logic.
# 3. Telemetry Aggregation: Captures execution metrics (inference latency) and 
#    aggregates scientific data into a unified traceability report.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import time
from typing import Callable, Optional, Tuple, Dict, Any
from PIL import Image
from src.domain.ports import ImageGeneratorPort, ScientificEvaluatorPort, AssessmentReport

class TransformCharacterUseCase:
    """
    Orchestrator for the Neural-Scientific Transformation Pipeline.
    
    Coordinates the synthesis of 2D subjects into Live-Action manifolds 
    and subsequently quantifies the fidelity of the resulting output.
    """

    def __init__(self, generator: ImageGeneratorPort, evaluator: ScientificEvaluatorPort):
        """
        Dependency Injection via Domain Ports (SOLID Principles).
        
        Args:
            generator: The abstract neural synthesis engine adapter.
            evaluator: The abstract scientific assessment adapter.
        """
        self._generator = generator
        self._evaluator = evaluator

    def execute(
        self, 
        image_file: Image.Image, 
        character_name: str, 
        feature_prompt: str, 
        resolution_anchor: int,
        hyper_params: Dict[str, Any],
        callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[Image.Image, AssessmentReport]:
        """
        Executes the three-phase transformation lifecycle.
        
        PHASE 1: NEURAL SYNTHESIS
        Invokes the generator to perform latent diffusion based on the 
        source image and semantic guidance.
        
        PHASE 2: SCIENTIFIC QUANTIFICATION
        Invokes the evaluator to measure structural and chromatic fidelity 
        using Computer Vision (CV) metrics.
        
        PHASE 3: TRACEABILITY ENRICHMENT
        Calculates execution latency and maps technical prompts to the 
        final report for research transparency.
        
        Returns:
            Tuple: (Final Generated Image, Detailed Assessment Report).
        """

        # Initialize latency tracking
        start_time = time.time()

        # ---------------------------------------------------------------------
        # PHASE 1: GENRATIVE INFERENCE
        # ---------------------------------------------------------------------
        # The generator produces the pixel manifold and returns the exact 
        # prompts utilized (for flight data recording).
        generated_image, full_prompt, negative_prompt = self._generator.generate_live_action(
            source_image=image_file,
            prompt_guidance=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            progress_callback=callback
        )

        # ---------------------------------------------------------------------
        # PHASE 2: MULTIVARIATE SCIENTIFIC ASSESSMENT
        # ---------------------------------------------------------------------
        # Quantification of SSIM and Identity preservation between Source and Output.
        report: AssessmentReport = self._evaluator.assess_quality(image_file, generated_image)
        
        # ---------------------------------------------------------------------
        # PHASE 3: METADATA CONSOLIDATION
        # ---------------------------------------------------------------------
        elapsed_time = time.time() - start_time
        
        # Enrich the report with operational telemetry
        report.inference_time = round(elapsed_time, 2)
        
        # Determine if the execution was generative or a procedural simulation (Mock)
        report.is_mock = "Mock" in self._generator.__class__.__name__
        
        # Populate traceability fields
        report.full_prompt = full_prompt
        report.negative_prompt = negative_prompt

        return generated_image, report