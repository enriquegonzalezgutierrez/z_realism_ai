# path: z_realism_ai/src/infrastructure/mock_generator.py
# description: Mock implementation of the AI generator.
#              FIXED: Updated signature to comply with the final ImageGeneratorPort 
#              contract, accepting feature_prompt and resolution_anchor.
#              This ensures the system's safety net works, upholding the DIP principle.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from PIL import Image, ImageOps
from src.domain.ports import ImageGeneratorPort
import asyncio
from typing import Callable, Optional

class MockImageGenerator(ImageGeneratorPort):
    """
    MockImageGenerator
    
    A temporary adapter that simulates AI behavior by applying a simple filter.
    It exists primarily to validate the data pipeline and the Dependency Inversion Principle.
    """
    
    async def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Image.Image:
        """
        Simulates an AI transformation by inverting the image colors.
        All new parameters are accepted but ignored for simplicity.
        """
        # Simulate AI processing time
        await asyncio.sleep(0.5) 
        
        print(f"MOCK AI: Transformation requested for prompt: '{prompt_guidance}'")
        print(f"MOCK AI: Ignoring features: '{feature_prompt}' at anchor: {resolution_anchor}px")
        
        # Simple transformation (Invert + Grayscale) to confirm the pipeline execution
        try:
            return ImageOps.invert(source_image.convert("RGB"))
        except Exception as e:
            print(f"MOCK AI ERROR: Failed to apply mock filter: {str(e)}")
            raise RuntimeError("Mock Generator pipeline failure.")