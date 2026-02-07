# path: z_realism_ai/src/infrastructure/mock_generator.py
# description: Resilient Fallback Engine v18.0 - Simulation Adapter.
#
# ABSTRACT:
# This module implements the ImageGeneratorPort as a deterministic fallback 
# mechanism. It is architected to ensure the "Graceful Degradation" of the 
# system, allowing researchers to test the application lifecycle and UI 
# telemetry without the presence of a CUDA-enabled neural environment.
#
# ARCHITECTURAL ROLE:
# 1. System Resilience: Decouples the Application Layer from strict hardware 
#    dependencies during testing or restricted deployments.
# 2. Visual Transparency: Employs procedural grayscale filters and technical 
#    watermarking to communicate the "Engine Offline" status to the end user.
# 3. Protocol Alignment: Adheres strictly to the multi-parameter signature 
#    of the domain ports, ensuring seamless swap-ability (Liskov Substitution).
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from PIL import Image, ImageOps, ImageDraw
from src.domain.ports import ImageGeneratorPort
from typing import Callable, Optional, Dict, Any, Tuple

class MockImageGenerator(ImageGeneratorPort):
    """
    Simulated Neural Engine (Safe Mode Fallback).
    
    Provides a procedurally generated visual output that adheres to the 
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
            source_image: The 2D subject image.
            prompt_guidance: Semantic subject name.
            feature_prompt: Target material descriptors.
            resolution_anchor: Target manifold dimension.
            hyper_params: Numerical hyperparameters.
            progress_callback: Optional telemetry link for UI synchronization.
            
        Returns:
            Tuple: (Procedurally Modified Image, Positive Prompt Mock, Negative Prompt Mock).
        """
        
        print(f"MOCK_SYSTEM: AI Engine is currently OFFLINE. Executing Procedural Simulation Protocol.")
        
        # 1. Telemetry Simulation (Simulating cold-start latency)
        # We invoke the callback to verify the frontend's polling logic.
        if progress_callback:
            progress_callback(100, 100, None)
        
        # 2. Procedural Transformation (Identity Preservation)
        # We convert the image to RGB to ensure canvas compatibility.
        canvas = source_image.convert("RGB")
        
        # We apply a Grayscale filter as a visual indicator of "Simulation Mode".
        processed = ImageOps.grayscale(canvas).convert("RGB")
        
        # 3. Technical Watermarking (UI Transparency)
        # This prevents researchers from mistaking the mock for a neural output.
        draw = ImageDraw.Draw(processed)
        width, height = processed.size
        
        # Define the warning bar dimensions (8% of the total height)
        bar_height = max(20, height // 12)
        
        # Draw a high-contrast warning banner at the inferior edge
        draw.rectangle(
            [0, height - bar_height, width, height], 
            fill=(239, 68, 68) # Semantic 'Danger' Red (ef4444)
        )
        
        # Inscribe the Warning Text
        # Note: We use basic drawing for maximum compatibility within Docker images.
        warning_message = "SIMULATION MODE: NO GPU ENGINE DETECTED"
        text_pos = (15, height - (bar_height // 1.5))
        
        # Draw text shadow for legibility
        draw.text((text_pos[0]+1, text_pos[1]+1), warning_message, fill=(0, 0, 0))
        # Draw text
        draw.text(text_pos, warning_message, fill=(255, 255, 255))
        
        # 4. Signature Fulfillment
        # We return the modified image and placeholder strings to satisfy the port requirements.
        return (
            processed, 
            "N/A (Simulation Protocol Active)", 
            "N/A (Simulation Protocol Active)"
        )