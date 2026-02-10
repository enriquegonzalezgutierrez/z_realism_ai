# path: z_realism_ai/src/application/use_cases.py
# description: Application Orchestration Layer v20.0 - Multi-Modal Pipeline.
#
# ABSTRACT:
# This module implements the primary business logic for the Z-Realism engine. 
# It acts as a Pure Application Service that coordinates the interaction 
# between Generative Engines (Static & Temporal), Analyzers, and Evaluators.
#
# ARCHITECTURAL ROLE:
# 1. Multi-Modal Orchestration: Manages both the Static Transformation (Img2Img)
#    and the Temporal Animation (Img2Video) lifecycles.
# 2. Lore Synchronization: Ensures that character-specific DNA (from JSON files)
#    is correctly injected into both static and temporal generation tasks.
# 3. Hardware Sensitivity: Designed to facilitate Sequential CPU Offloading 
#    via infrastructure ports to accommodate 6GB VRAM environments.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

import time
from typing import Callable, Optional, Tuple, Dict, Any
from PIL import Image
from src.domain.ports import (
    ImageGeneratorPort, 
    VideoGeneratorPort,
    ImageAnalyzerPort,
    ScientificEvaluatorPort, 
    AssessmentReport,
    AnimationReport
)

class TransformCharacterUseCase:
    """
    Orchestrator for the Neural-Scientific Transformation Pipeline (Stills).
    
    Coordinates the synthesis of 2D subjects into Live-Action manifolds 
    and subsequently quantifies the fidelity of the resulting output.
    """

    def __init__(self, generator: ImageGeneratorPort, evaluator: ScientificEvaluatorPort):
        """
        Dependency Injection via Domain Ports (SOLID Principles).
        """
        self._generator = generator
        self._evaluator = evaluator

    def execute(
        self, 
        image_file: Image.Image, 
        character_name: str, 
        feature_prompt: str, 
        resolution_anchor: int,
        hyper_params: Dict[str, Any],
        callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[Image.Image, AssessmentReport]:
        """
        Executes the three-phase transformation lifecycle for static images.
        """
        start_time = time.time()

        # Phase 1: Generative Inference
        generated_image, full_prompt, negative_prompt = self._generator.generate_live_action(
            source_image=image_file,
            prompt_guidance=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            progress_callback=callback
        )

        # Phase 2: Scientific Assessment
        report: AssessmentReport = self._evaluator.assess_quality(image_file, generated_image)
        
        # Phase 3: Telemetry Enrichment
        elapsed_time = time.time() - start_time
        report.inference_time = round(elapsed_time, 2)
        report.is_mock = "Mock" in self._generator.__class__.__name__
        report.full_prompt = full_prompt
        report.negative_prompt = negative_prompt

        return generated_image, report


class AnimateCharacterUseCase:
    """
    Orchestrator for the Temporal Synthesis Pipeline (Video).
    
    Bridges the gap between a high-fidelity static manifold and a fluid 
    cinematic clip by injecting motion guidance while preserving identity.
    """

    def __init__(self, video_generator: VideoGeneratorPort, analyzer: ImageAnalyzerPort):
        """
        Args:
            video_generator: The temporal synthesis engine adapter.
            analyzer: The heuristic analyzer used to fetch character lore.
        """
        self._video_generator = video_generator
        self._analyzer = analyzer

    def execute(
        self,
        image_file: Image.Image,
        character_name: str,
        video_params: Dict[str, Any],
        callback: Optional[Callable[[int, int, str], None]] = None
    ) -> AnimationReport:
        """
        Executes the temporal transformation lifecycle.
        
        PHASE 1: LORE RECOVERY
        Invokes the analyzer to retrieve the character's DNA strategy 
        (prompts and weights) to ensure visual consistency during motion.
        
        PHASE 2: TEMPORAL SYNTHESIS
        Invokes the video generator to synthesize frames based on the 
        source image, character lore, and motion prompt.
        """
        
        # 1. Identity Anchoring: Retrieve Lore from the Analyzer
        # We perform a lightweight analysis to get the strategy manifold
        strategy = self._analyzer.analyze_source(image_file, character_name)
        
        lore_packet = {
            "name": character_name,
            "prompt_base": strategy.suggested_prompt,
            "negative_prompt": strategy.suggested_negative
        }

        # 2. Execute Animation Pipeline
        report: AnimationReport = self._video_generator.animate_image(
            source_image=image_file,
            motion_prompt=video_params.get("motion_prompt", "subtle movement"),
            character_lore=lore_packet,
            duration_frames=int(video_params.get("duration_frames", 24)),
            fps=int(video_params.get("fps", 8)),
            hyper_params=video_params,
            progress_callback=callback
        )

        return report