# path: z_realism_ai/src/domain/ports.py
# description: Domain Boundary Interfaces.
#              Defines strict contracts for Hexagonal Architecture.
#              UPDATED: Added traceability fields (prompts) to AssessmentReport.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, Dict, Tuple
from dataclasses import dataclass
from PIL import Image

@dataclass
class AssessmentReport:
    """Container for scientific metrics and traceability data."""
    structural_similarity: float
    identity_preservation: float
    inference_time: float
    is_mock: bool = False
    full_prompt: str = ""
    negative_prompt: str = ""

@dataclass
class AnalysisResult:
    """Container for heuristic analysis results."""
    recommended_steps: int
    recommended_cfg: float
    recommended_cn: float
    detected_essence: str
    suggested_prompt: str

class ImageGeneratorPort(ABC):
    """
    Abstract contract for the Neural Diffusion Engine.
    Ensures any generator implementation follows this input/output structure.
    """
    @abstractmethod
    def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        hyper_params: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[Image.Image, str, str]: 
        # Must return: (Generated Image, Positive Prompt Used, Negative Prompt Used)
        pass

class ImageAnalyzerPort(ABC):
    """
    Abstract contract for the Expert Heuristic Engine.
    """
    @abstractmethod
    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        """
        Determines optimal synthesis parameters based on visual and semantic data.
        """
        pass

class ScientificEvaluatorPort(ABC):
    """
    Abstract contract for Quality Metrics.
    """
    @abstractmethod
    def assess_quality(self, original: Image.Image, generated: Image.Image) -> AssessmentReport:
        pass