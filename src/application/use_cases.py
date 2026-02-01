# path: z_realism_ai/src/application/use_cases.py
# description: Optimized Business Logic.
#              FIXED: Shortened base prompt to avoid CLIP token truncation (77 limit).
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import time
from typing import Callable, Optional, Tuple
from PIL import Image
from src.domain.ports import ImageGeneratorPort, ScientificEvaluatorPort, AssessmentReport

class TransformCharacterUseCase:
    def __init__(self, generator: ImageGeneratorPort, evaluator: ScientificEvaluatorPort):
        self._generator = generator
        self._evaluator = evaluator

    async def execute(
        self, image_file, character_name, feature_prompt, resolution_anchor, callback=None
    ) -> Tuple[Image.Image, AssessmentReport]:
        
        # Dense keywords only. No filler words like "cinematic full body shot of a..."
        base_prompt = f"cinematic human {character_name}, realistic skin, movie makeup, natural light"

        start_time = time.time()
        generated_image = await self._generator.generate_live_action(
            source_image=image_file, 
            prompt_guidance=base_prompt,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            progress_callback=callback
        )
        
        elapsed_time = time.time() - start_time
        report = self._evaluator.assess_quality(image_file, generated_image)
        report.inference_time = round(elapsed_time, 2)
        report.is_mock = "Mock" in self._generator.__class__.__name__
        
        return generated_image, report
