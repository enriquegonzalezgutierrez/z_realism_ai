# path: z_realism_ai/src/infrastructure/mock_generator.py
# description: Technical Mock Implementation v5.1.
#              UPDATED: Replaced simple inversion with a "Safe Simulation Mode".
#              It now applies grayscale and a technical watermark to indicate 
#              that the Neural Engine is not active.
#              UPDATED: Complies with the new Port signature returning empty prompts.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

from PIL import Image, ImageOps, ImageDraw, ImageFont
from src.domain.ports import ImageGeneratorPort
import asyncio
from typing import Callable, Optional, Dict, Any, Tuple

class MockImageGenerator(ImageGeneratorPort):
    """
    MockImageGenerator (Safe Mode)
    
    A fallback adapter that visually communicates its status to the researcher.
    Used when hardware requirements (VRAM/RAM) are not met.
    """
    
    def generate_live_action(
        self, 
        source_image: Image.Image, 
        prompt_guidance: str,
        feature_prompt: str,
        resolution_anchor: int,
        hyper_params: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[Image.Image, str, str]:
        """
        Simulates AI processing by applying a grayscale filter and a 
        'MOCK MODE' watermark for system transparency.
        Returns the image and empty prompts to match the port signature.
        """
        # Simulate neural latency (0.5s)
        # In a real async context, we would use `await asyncio.sleep(0.5)`
        # but Celery runs this synchronously, so we remove await.
        
        print(f"MOCK_SYSTEM: AI Engine is OFFLINE. Generating safe simulation.")
        
        # 1. Base Transformation (Grayscale for visual distinction)
        canvas = source_image.convert("RGB")
        processed = ImageOps.grayscale(canvas).convert("RGB")
        
        # 2. Apply Technical Watermark
        draw = ImageDraw.Draw(processed)
        width, height = processed.size
        
        # Draw a semi-transparent warning bar at the bottom
        bar_height = height // 8
        draw.rectangle([0, height - bar_height, width, height], fill=(255, 0, 0))
        
        # Add warning text (Using basic drawing if custom fonts are missing in Docker)
        warning_text = "SIMULATION MODE: NO AI ENGINE DETECTED"
        
        # Center the text approximately
        text_pos = (width // 10, height - (bar_height // 1.5))
        draw.text(text_pos, warning_text, fill=(255, 255, 255))
        
        # Return image and empty prompts as per the port contract
        return processed, "N/A (Mock Mode)", "N/A (Mock Mode)"