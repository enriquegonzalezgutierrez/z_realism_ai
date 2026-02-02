# path: z_realism_ai/src/application/use_cases.py
# description: Optimized Business Logic for realistic character transformation.
#              FIXED: Removed await for synchronous generator and improved prompts for Dragon Ball characters.
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
        Transform a character image into a hyper-realistic live-action style version.

        Args:
            image_file (Image.Image): Source PIL image of the character.
            character_name (str): Name of the character to guide generation.
            feature_prompt (str): Additional detailed features for SDXL.
            resolution_anchor (int): Base resolution to scale output image.
            callback (Callable, optional): Progress callback (current_step, total_steps).

        Returns:
            Tuple[Image.Image, AssessmentReport]: Generated image and quality assessment.
        """

        # Optimized prompt: avoids filler words, emphasizes realism and human features
        base_prompt = (
            f"Ultra realistic photo of a human version of {character_name}, "
            "realistic skin texture, natural pores, natural lighting, "
            "cinematic lens, subtle facial expressions, high-resolution, "
            "movie makeup, lifelike hair and eyes"
        )

        start_time = time.time()

        # Call synchronous generator directly (no await)
        generated_image = self._generator.generate_live_action(
            source_image=image_file,
            prompt_guidance=base_prompt,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            progress_callback=callback
        )

        elapsed_time = time.time() - start_time

        # Generate quality report
        report: AssessmentReport = self._evaluator.assess_quality(image_file, generated_image)
        report.inference_time = round(elapsed_time, 2)
        report.is_mock = "Mock" in self._generator.__class__.__name__

        return generated_image, report
