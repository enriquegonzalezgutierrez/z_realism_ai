# path: z_realism_ai/src/application/use_cases.py
# description: Orchestration Logic v5.1 for realistic character transformation.
#              This layer is technology-agnostic and relies on Ports.
#              UPDATED: Now enriches the final report with the exact prompts used
#              for synthesis, enabling full research traceability.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import time
from typing import Callable, Optional, Tuple, Dict, Any
from PIL import Image
from src.domain.ports import ImageGeneratorPort, ScientificEvaluatorPort, AssessmentReport

class TransformCharacterUseCase:
    """
    Orchestrates the transformation of a character into a realistic human.
    Coordinates the generation process and the subsequent scientific evaluation.
    """

    def __init__(self, generator: ImageGeneratorPort, evaluator: ScientificEvaluatorPort):
        """
        Dependency Injection via Ports (DIP - SOLID).
        """
        self._generator = generator
        self._evaluator = evaluator

    def execute(
        self, 
        image_file: Image.Image, 
        character_name: str, 
        feature_prompt: str, 
        resolution_anchor: int,
        hyper_params: Dict[str, Any], # Dynamic tuning parameters
        callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[Image.Image, AssessmentReport]:
        """
        Executes the full transformation pipeline.
        
        1. Prepares the identity prompt.
        2. Executes the neural generation (Live Action Synthesis).
        3. Measures latency and scientific metrics.
        4. Enriches the report with full traceability data (prompts).
        """

        # Identity Logic: Focus on human translation.
        # Minimalist prompt to avoid CLIP token truncation (77-token limit).
        identity_prompt = f"real life human {character_name}"

        start_time = time.time()

        # Phase 1: Neural Generation
        # The generator now returns the image and the exact prompts used.
        generated_image, full_prompt, negative_prompt = self._generator.generate_live_action(
            source_image=image_file,
            prompt_guidance=identity_prompt,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            progress_callback=callback
        )

        elapsed_time = time.time() - start_time

        # Phase 2: Scientific Assessment
        # Computes SSIM and Identity preservation using Computer Vision
        report: AssessmentReport = self._evaluator.assess_quality(image_file, generated_image)
        
        # Phase 3: Metadata Enrichment & Traceability
        report.inference_time = round(elapsed_time, 2)
        report.is_mock = "Mock" in self._generator.__class__.__name__
        report.full_prompt = full_prompt
        report.negative_prompt = negative_prompt

        return generated_image, report