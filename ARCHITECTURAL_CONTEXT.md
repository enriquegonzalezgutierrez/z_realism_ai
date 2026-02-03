# Z-REALISM AI: ARCHITECTURAL CONTEXT & STATE (v5.6)

## 1. Project Identity
*   **Name:** Z-Realism AI Studio
*   **Goal:** Photorealistic transformation of Dragon Ball characters using SD 1.5 + ControlNet.
*   **Architecture:** Hexagonal (DDD) + SOLID Principles.
*   **Current Version:** v5.6 (Universal Windows/Linux + Expert Heuristics).

## 2. Core Heuristic Logic (The "Brain")
The system uses a **Multi-Modal Expert Analyzer (v5.5)** located in `src/infrastructure/analyzer.py`.
It combines **Semantic Lookups** (Character Name) with **Computer Vision** (HSV/YCrCb Analysis).

### Heuristic Strategy Table
| Archetype | Trigger Conditions | ControlNet | CFG | Key Prompts |
| :--- | :--- | :--- | :--- | :--- |
| **Saiyan** | Name: Goku, Vegeta, Gohan, Broly | **0.60** | 7.0 | `detailed boots`, `messy hair`, `combat gi` |
| **Humanoid** | Name: Krillin, Tien, Bulma, Videl | **0.50** | 7.0 | `human facial features`, `fabric details` |
| **Bio-Android** | Name: Cell OR (Green > 5% & High Edge Density) | **0.75** | 7.0 | `biological exoskeleton`, `chitinous plates` |
| **Namekian** | Name: Piccolo OR (Green > 3% & Low Edge Density) | **0.55** | 7.0 | `smooth green alien skin`, `damp amphibian texture` |
| **Majin** | Name: Buu OR (Pink > 15%) | **0.55** | 7.0 | `pink rubbery skin`, `steam vents`, `organic smooth` |
| **Frost Demon** | Name: Frieza/Cooler | **0.65** | 7.0 | `biological armor`, `polished texture`, `bio-gems` |
| **Black Form** | Name contains "Black" | **0.68** | 7.0 | `black obsidian armor`, `metallic silver` |

## 3. Neural Pipeline Configuration
*   **Model:** `SG161222/Realistic_Vision_V6.0_B1_noVAE` (SD 1.5).
*   **ControlNet:** `lllyasviel/control_v11p_sd15_canny`.
*   **Scheduler:** `DPMSolverMultistepScheduler` (Karras Sigmas).
*   **Target Steps:** 20 (Optimized for CPU latency).
*   **Token Safety:** Prompts are compressed to avoid the CLIP 77-token limit.
*   **Hardware:** Hybrid CPU/CUDA detection via `Makefile` and `sd_generator.py`.

## 4. Scientific Metrics (v5.0)
*   **SSIM:** Calculated using Gaussian Blur + Structural Cross-Correlation (Lighting Agnostic).
*   **Identity:** Calculated using HSV Histogram Correlation (Color DNA).

## 5. File Structure & Responsibilities
```text
z_realism_ai/
├── Makefile                   # Universal Orchestration (Windows/Linux detection)
├── docker-compose.yml         # Base Topology (CPU safe)
├── docker-compose.gpu.yml     # NVIDIA Override (Injected by Makefile)
├── src/
│   ├── domain/
│   │   └── ports.py           # Abstract Interfaces (Analyzer, Generator, Evaluator)
│   ├── application/
│   │   └── use_cases.py       # Logic Orchestration (Prompt injection)
│   ├── infrastructure/
│   │   ├── api.py             # FastAPI + Redis Mutex + Endpoints (/analyze, /transform)
│   │   ├── analyzer.py        # v5.5 Expert Heuristic Engine (OpenCV + Logic)
│   │   ├── sd_generator.py    # v5.6 Neural Engine (PyTorch + Diffusers)
│   │   ├── evaluator.py       # v5.0 Scientific Metrics (OpenCV)
│   │   └── worker.py          # Celery Async Worker (Spawn method)
│   └── presentation/
│       └── dashboard.py       # v5.5 Minimalist White-Labeled UI (Streamlit)
```

## 6. Known Constraints & Fixes
*   **Windows:** Makefile uses `where` instead of `command -v` to detect NVIDIA drivers.
*   **Docker:** Requires `nvidia-container-toolkit` for GPU access.
*   **API:** Uses a Global Redis Mutex (`LOCK_TIMEOUT = 1800s`) to prevent hardware crashes.
*   **Latency:** ~6-8 mins on CPU (20 steps @ 640px). ~15s on GPU.

## 7. Change Log Summary
*   **v4.0:** Dynamic UI Parameters.
*   **v4.8:** Organic vs Mechanical Detection (YCrCb).
*   **v4.9:** Token Safety (CLIP limit fix).
*   **v5.2:** High Sensitivity Alien Detection (3% threshold).
*   **v5.3:** Species Differentiation (Smooth vs Complex Aliens).
*   **v5.5:** Expert Lore-Awareness (Character Name Lookup + Multi-modal).
*   **v5.6:** Universal Windows/Linux Orchestration + Diagnostics.
