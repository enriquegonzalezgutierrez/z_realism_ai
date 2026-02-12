# path: src/application/use_cases.py
# description: Application Orchestration v22.0 - Doctoral Thesis Candidate.
#              FIXED: Corrected parameter mismatch in the temporal use case.
#
# ARCHITECTURAL ROLE (Hexagonal / DDD):
# This module acts as the Application Service. It coordinates the interaction 
# between Generative Adapters, Heuristic Analyzers, and Scientific Evaluators.
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
    """
    def __init__(self, generator: ImageGeneratorPort, evaluator: ScientificEvaluatorPort):
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
        start_time = time.time()
        generated_image, full_prompt, negative_prompt = self._generator.generate_live_action(
            source_image=image_file,
            prompt_guidance=character_name,
            feature_prompt=feature_prompt,
            resolution_anchor=resolution_anchor,
            hyper_params=hyper_params,
            progress_callback=callback
        )
        report: AssessmentReport = self._evaluator.assess_quality(image_file, generated_image)
        elapsed_time = time.time() - start_time
        report.inference_time = round(elapsed_time, 2)
        report.full_prompt = full_prompt
        report.negative_prompt = negative_prompt
        return generated_image, report


class AnimateCharacterUseCase:
    """
    Orchestrator for the Temporal Synthesis Pipeline (Video).
    
    Injects motion guidance while preserving the subject's core identity by
    retrieving and applying the Subject DNA from the Knowledge Base.
    """

    def __init__(self, video_generator: VideoGeneratorPort, analyzer: ImageAnalyzerPort):
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
        Executes the two-phase temporal synthesis lifecycle:
        1. METADATA RECOVERY: Fetches Subject DNA.
        2. TEMPORAL SYNTHESIS: Generates the video manifold.
        """
        
        # 1. Identity Anchoring: Retrieve Subject DNA from the Analyzer.
        strategy = self._analyzer.analyze_source(image_file, character_name)
        
        metadata_packet = {
            "name": character_name,
            "prompt_base": strategy.suggested_prompt,
            "negative_prompt": strategy.suggested_negative
        }

        # 2. Execute Temporal Pipeline.
        # This triggers the AnimateDiff engine with the correct identity packet.
        report: AnimationReport = self._video_generator.animate_image(
            source_image=image_file,
            motion_prompt=video_params.get("motion_prompt", "subtle movement"),
            
            # --- CRITICAL FIX: Changed 'character_lore' to 'subject_metadata' ---
            subject_metadata=metadata_packet, 
            
            duration_frames=int(video_params.get("duration_frames", 24)),
            fps=int(video_params.get("fps", 8)),
            hyper_params=video_params,
            progress_callback=callback
        )

        return report