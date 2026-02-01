# path: z_realism_ai/src/application/use_cases.py
# description: Application Business Logic - SDXL Orchestration.
#              UPDATED: Simplified prompt and execution to fit SDXL parameters.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from typing import Callable, Optional
from PIL import Image
from src.domain.ports import ImageGeneratorPort

class TransformCharacterUseCase:
    """
    UseCase: TransformCharacterUseCase
    
    Orchestrates the SDXL generation process, combining base cinematic prompt 
    with user-defined features and resolution.
    """

    def __init__(self, generator: ImageGeneratorPort):
        self._generator = generator

    async def execute(
        self, 
        image_file: Image.Image, 
        character_name: str,
        feature_prompt: str,
        resolution_anchor: int,
        callback: Optional[Callable[[int, int], None]] = None
    ) -> Image.Image:
        """
        Executes the SDXL synthesis using a powerful base prompt.
        """
        
        # SDXL Base Prompt: Focus on high-quality human texture and lighting
        base_prompt = (
            f"cinematic full body shot of a real human person as {character_name}, "
            f"hyper-realistic skin texture, movie character makeup, "
            f"natural lighting, professional photography, masterpiece"
        )

        print(f"USE_CASE: Orchestrating SDXL synthesis for: {character_name}")
        
        # Dispatch to the generator with all user-defined parameters
        return await self._generator.generate_live_action(
            source_image=image_file, 
            prompt_guidance=base_prompt,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            progress_callback=callback
        )