# path: z_realism_ai/src/application/use_cases.py
# description: Orchestration Logic for realistic character transformation.
#              This layer is technology-agnostic and relies on Ports.
#              Updated to support dynamic hyper-parameter passthrough for 
#              real-time research tuning.
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
        """

        # Identity Logic: Focus on human translation.
        # Minimalist prompt to avoid CLIP token truncation (77-token limit).
        identity_prompt = f"real life human {character_name}"

        start_time = time.time()

        # Phase 1: Neural Generation
        # We pass hyper_params (steps, cfg_scale, etc.) directly to the generator
        generated_image = self._generator.generate_live_action(
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
        
        # Phase 3: Metadata Enrichment
        report.inference_time = round(elapsed_time, 2)
        # Type-checking class name for system transparency (Mock vs Real AI)
        report.is_mock = "Mock" in self._generator.__class__.__name__

        return generated_image, report