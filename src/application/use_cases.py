# path: z_realism_ai/src/application/use_cases.py
# description: Optimized Business Logic for realistic character transformation.
#              FIXED: Shortened prompts to prevent CLIP token truncation.
#              FIXED: Strategic separation of Identity (Use Case) and Style (Infra).
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import time
from typing import Callable, Optional, Tuple
from PIL import Image
from src.domain.ports import ImageGeneratorPort, ScientificEvaluatorPort, AssessmentReport

class TransformCharacterUseCase:
    def __init__(self, generator: ImageGeneratorPort, evaluator: ScientificEvaluatorPort):
        self._generator = generator
        self._evaluator = evaluator

    def execute(
        self, image_file: Image.Image, character_name: str, feature_prompt: str, 
        resolution_anchor: int, callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[Image.Image, AssessmentReport]:
        """
        Orchestrates the transformation of a character into a realistic human.
        """

        # PH.D. OPTIMIZATION: Keep this extremely short. 
        # Redundant realism words are already handled inside the Generator class.
        # This ensures we stay under the 77-token CLIP limit.
        identity_prompt = f"real life human {character_name}"

        start_time = time.time()

        # Execute generation (Synchronous flow)
        generated_image = self._generator.generate_live_action(
            source_image=image_file,
            prompt_guidance=identity_prompt,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            progress_callback=callback
        )

        elapsed_time = time.time() - start_time

        # Quantitative Assessment
        report: AssessmentReport = self._evaluator.assess_quality(image_file, generated_image)
        report.inference_time = round(elapsed_time, 2)
        report.is_mock = "Mock" in self._generator.__class__.__name__

        return generated_image, report