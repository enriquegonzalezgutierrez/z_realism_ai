# path: src/domain/ports.py
# description: Domain Boundary Interfaces v21.4 - Thesis Candidate.
#              Defines the abstract contracts for the Z-Realism ecosystem.
#
# ARCHITECTURAL ROLE (Hexagonal / DDD):
# This module defines the formal specifications for the Z-Realism engine.
# It utilizes Hexagonal Architecture principles to decouple core domain logic
# from specific infrastructure implementations (Stable Diffusion, FFmpeg, etc.).
#
# NOMENCLATURE REFACTOR (v21.4):
# Purged all "Lore" terminology. Replaced with "Subject Metadata" to align with 
# informatics engineering standards for structured data management.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, Dict, Tuple, List
from dataclasses import dataclass
from PIL import Image

@dataclass
class AssessmentReport:
    """
    Multivariate data container for post-inference quality quantification.
    
    Provides objective scientific metrics regarding structural, chromatic, 
    and informational fidelity gain.
    """
    structural_similarity: float
    identity_preservation: float
    textural_realism: float
    inference_time: float
    is_mock: bool = False
    full_prompt: str = ""
    negative_prompt: str = ""

@dataclass
class AnimationReport:
    """
    Data container for temporal synthesis (Video) results.
    
    Encapsulates the resulting MP4 manifold and associated telemetry.
    """
    video_b64: str
    inference_time: float
    total_frames: int
    fps: int
    status: str = "success"

@dataclass
class AnalysisResult:
    """
    Heuristic Strategy Manifold containing recommended hyperparameters.
    
    Bridging the gap between raw pixel data and the subject DNA 
    retrieved from the Metadata Knowledge Base.
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
    Abstract contract for the Neural Computational Engine (Static Images).
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

class VideoGeneratorPort(ABC):
    """
    Abstract contract for the Temporal Synthesis Engine (Video Animation).
    
    NOMENCLATURE: Uses 'subject_metadata' to anchor identity during motion.
    """
    @abstractmethod
    def animate_image(
        self,
        source_image: Image.Image,
        motion_prompt: str,
        subject_metadata: Dict[str, Any],
        duration_frames: int,
        fps: int,
        hyper_params: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> AnimationReport:
        pass

class ImageAnalyzerPort(ABC):
    """
    Abstract contract for the Heuristic Intelligence Layer.
    Responsible for retrieving Subject DNA from the Metadata Knowledge Base.
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