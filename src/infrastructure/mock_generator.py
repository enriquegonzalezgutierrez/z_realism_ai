# path: z_realism_ai/src/infrastructure/mock_generator.py
# description: Resilient Fallback Engine v21.0 - Simulation Adapter.
#
# ARCHITECTURAL ROLE (Infrastructure Adapter):
# This module implements the 'ImageGeneratorPort' as a deterministic fallback 
# mechanism. It is architected to ensure "Graceful Degradation" of the 
# system, allowing researchers to test the application lifecycle and UI 
# telemetry without the presence of a CUDA-enabled neural environment.
#
# KEY PRINCIPLES:
# 1. System Resilience: Decouples the Application Layer from strict hardware 
#    dependencies during non-inference testing.
# 2. Visual Transparency: Employs technical watermarking to communicate the 
#    "Engine Offline" status to the researcher.
# 3. Protocol Alignment: Adheres strictly to the Domain Port contracts 
#    (Liskov Substitution Principle).
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from PIL import Image, ImageOps, ImageDraw
from src.domain.ports import ImageGeneratorPort
from typing import Callable, Optional, Dict, Any, Tuple

class MockImageGenerator(ImageGeneratorPort):
    """
    Simulated Neural Engine (Deterministic Fallback).
    
    Provides a procedurally generated visual output that satisfies the 
    domain's interface contracts while bypassing GPU-intensive inference.
    """
    
    def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        hyper_params: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[Image.Image, str, str]:
        """
        Executes a procedural simulation of the generative pipeline.
        
        Args:
            source_image: The source character image manifold.
            prompt_guidance: Semantic subject name.
            feature_prompt: Target material descriptors.
            resolution_anchor: Target manifold dimension.
            hyper_params: Numerical hyperparameters.
            progress_callback: Telemetry link for UI synchronization.
            
        Returns:
            Tuple: (Modified Image, Mock Prompt, Mock Negative Prompt).
        """
        
        print(f"MOCK_SYSTEM: CUDA Engine is OFFLINE. Executing Simulation Protocol.")
        
        # 1. Telemetry Simulation
        # We invoke the callback to verify the frontend's async polling logic.
        if progress_callback:
            # Simulate a 100% completion event
            progress_callback(100, 100, None)
        
        # 2. Procedural Transformation (Visual Indicator)
        # Convert the image to RGB to ensure canvas compatibility.
        canvas = source_image.convert("RGB")
        
        # Apply a Grayscale filter as a visual indicator of "Simulation Mode".
        processed = ImageOps.grayscale(canvas).convert("RGB")
        
        # 3. Technical Watermarking (Structural Transparency)
        # Prevents mistaking mock outputs for actual neural inference.
        draw = ImageDraw.Draw(processed)
        width, height = processed.size
        
        # Define the warning bar dimensions (8% of the total height)
        bar_height = max(20, height // 12)
        
        # Draw a high-contrast warning banner at the inferior edge
        # Semantic 'Danger' Red (ef4444)
        draw.rectangle(
            [0, height - bar_height, width, height], 
            fill=(239, 68, 68) 
        )
        
        # Inscribe the Warning Text
        warning_message = "SIMULATION MODE: NO CUDA ENGINE DETECTED"
        text_pos = (15, height - (bar_height // 1.5))
        
        # Draw text shadow for legibility in basic environments
        draw.text((text_pos[0]+1, text_pos[1]+1), warning_message, fill=(0, 0, 0))
        draw.text(text_pos, warning_message, fill=(255, 255, 255))
        
        # 4. Interface Signature Fulfillment
        return (
            processed, 
            "N/A (Simulation Protocol Active)", 
            "N/A (Simulation Protocol Active)"
        )