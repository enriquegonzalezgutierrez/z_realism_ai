# path: z_realism_ai/src/domain/ports.py
# description: Domain Boundary Interfaces (Ports).
#              UPDATED: Expanded the contract to support user-defined resolution 
#              and specific feature guidance for professional-level control.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from abc import ABC, abstractmethod
from typing import Callable, Any, Optional
from PIL import Image

class ImageGeneratorPort(ABC):
    """
    Interface defining the AI generation contract. 
    Following DDD, this port decouples the core logic from the AI framework and
    now includes parameters for advanced user control.
    """

    @abstractmethod
    async def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Image.Image:
        """
        Transforms a character image into a photorealistic 'Live Action' version.
        
        Args:
            source_image (Image.Image): The input character art.
            prompt_guidance (str): The base cinematic prompt from the Use Case.
            feature_prompt (str): User-provided keywords for specific details (e.g., boots, armor).
            resolution_anchor (int): The pixel size for the image's shortest side, controlling quality.
            progress_callback (Callable): Optional function to report (current, total) progress.
            
        Returns:
            Image.Image: The processed PIL image, resized to the user's specification.
        """
        pass