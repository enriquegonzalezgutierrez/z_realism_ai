# path: z_realism_ai/src/domain/ports.py
# description: Domain Boundary Interfaces v5.4.
#              UPDATED: Added 'character_name' to the analyzer port 
#              to enable Multi-Modal Expert heuristics.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass
from PIL import Image

@dataclass
class AssessmentReport:
    """Scientific metrics container."""
    structural_similarity: float
    identity_preservation: float
    inference_time: float
    is_mock: bool = False

@dataclass
class AnalysisResult:
    """Optimized hyper-parameters based on name and visual DNA."""
    recommended_steps: int
    recommended_cfg: float
    recommended_cn: float
    detected_essence: str
    suggested_prompt: str

class ImageGeneratorPort(ABC):
    """Abstract port for the Neural Diffusion Engine."""
    @abstractmethod
    async def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        hyper_params: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Image.Image:
        pass

class ImageAnalyzerPort(ABC):
    """
    Expert Heuristic Engine.
    Combines Entity Name (Semantic) + Visual DNA (CV) to determine 
    the species-specific synthesis strategy.
    """
    @abstractmethod
    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        """
        Calculates optimal parameters by identifying character species.
        """
        pass

class ScientificEvaluatorPort(ABC):
    """Port for High-Precision metric calculation."""
    @abstractmethod
    def assess_quality(self, original: Image.Image, generated: Image.Image) -> AssessmentReport:
        pass