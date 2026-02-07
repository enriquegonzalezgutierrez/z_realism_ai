# path: z_realism_ai/src/domain/ports.py
# description: Domain Boundary Interfaces v19.0 - Dynamic Hyperparameter Schema.
#
# ABSTRACT:
# This module represents the formal specification of the system's operational 
# boundaries. It defines the schemas required for cross-domain communication 
# in a Hexagonal Architecture. 
#
# ARCHITECTURAL EVOLUTION (v19.0):
# To mitigate "Semantic Over-Drift" and "Anatomic Distortion," the AnalysisResult 
# has been expanded to decouple structural conditioning (Depth vs. Pose) and 
# to explicitly control the stochastic intensity (Denoising Strength). This 
# ensures that the lore-specific JSON manifolds have total authority over 
# the synthesis engine.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, Dict, Tuple
from dataclasses import dataclass
from PIL import Image

@dataclass
class AssessmentReport:
    """
    Multivariate data container for post-inference quality quantification.
    """
    structural_similarity: float
    identity_preservation: float
    inference_time: float
    is_mock: bool = False
    full_prompt: str = ""
    negative_prompt: str = ""

@dataclass
class AnalysisResult:
    """
    Heuristic Strategy Manifold.
    
    Contains the recommended hyperparameters derived from the subject's 
    visual DNA and domain lore.
    
    Attributes:
        recommended_steps: Optimal iteration count for the de-noising schedule.
        recommended_cfg: Classifier-Free Guidance scale for prompt adherence.
        recommended_cn_depth: Conditioning intensity for the geometric depth map.
        recommended_cn_pose: Conditioning intensity for the anatomical pose map.
        recommended_strength: Stochastic refinement ratio (Img2Img Strength).
        detected_essence: Semantic classification of the subject.
        suggested_prompt: Canonical positive prompt synthesized from lore.
        suggested_negative: Customized exclusion tokens to prevent artifacts.
    """
    recommended_steps: int
    recommended_cfg: float
    recommended_cn_depth: float
    recommended_cn_pose: float
    recommended_strength: float
    detected_essence: str
    suggested_prompt: str
    suggested_negative: str

class ImageGeneratorPort(ABC):
    """
    Abstract contract for the Neural Computational Engine.
    """
    @abstractmethod
    def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        hyper_params: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[Image.Image, str, str]: 
        pass

class ImageAnalyzerPort(ABC):
    """
    Abstract contract for the Heuristic Intelligence Layer.
    """
    @abstractmethod
    def analyze_source(self, image: Image.Image, character_name: str) -> AnalysisResult:
        pass

class ScientificEvaluatorPort(ABC):
    """
    Abstract contract for Multivariate Quality Assessment.
    """
    @abstractmethod
    def assess_quality(self, original: Image.Image, generated: Image.Image) -> AssessmentReport:
        pass