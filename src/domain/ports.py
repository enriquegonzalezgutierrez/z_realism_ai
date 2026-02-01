# path: z_realism_ai/src/domain/ports.py
# description: Domain Boundary Interfaces. 
#              UPDATED: Added 'is_mock' flag to AssessmentReport for 
#              system transparency.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from abc import ABC, abstractmethod
from typing import Callable, Any, Optional
from dataclasses import dataclass
from PIL import Image

@dataclass
class AssessmentReport:
    """
    Data Transfer Object holding scientific metrics.
    """
    structural_similarity: float
    identity_preservation: float
    inference_time: float
    is_mock: bool = False  # NEW: Flag to indicate if AI was actually used

class ImageGeneratorPort(ABC):
    @abstractmethod
    async def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Image.Image:
        pass

class ScientificEvaluatorPort(ABC):
    @abstractmethod
    def assess_quality(
        self, 
        original_image: Image.Image, 
        generated_image: Image.Image
    ) -> AssessmentReport:
        pass
