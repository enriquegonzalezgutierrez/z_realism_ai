# 🐉 Z-Realism AI: Dragon Ball Live-Action Engine (v16.5 Stable)

[![Docker](https://img.shields.io/badge/Docker-Enabled-blue?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Queue-Celery-37814A?logo=celery)](https://docs.celeryq.dev/)
[![Frontend](https://img.shields.io/badge/Interface-Cyber--Capsule%20UI-black)](http://localhost)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal%20%2F%20DDD-orange)](#system-architecture-hexagonal--ddd)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Z-Realism AI** is a professional-grade, domain-driven generative AI ecosystem engineered for the photorealistic synthesis of 2D characters into high-fidelity "Live Action" human counterparts. This research platform utilizes a meticulously optimized **Stable Diffusion (SD) 1.5** pipeline augmented with dual structural and identity conditioning, designed specifically for consumer-grade GPU environments (e.g., NVIDIA GTX 1060).

**Author:** Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

---

## 🔬 Scientific & Technical Thesis

The core thesis of Z-Realism is the solution to the **Structural Drift Problem**—the tendency of style transfer models to distort source geometry. By coupling **ControlNet (Depth + OpenPose)** for structural fidelity with **IP-Adapter** for identity and color preservation, we achieve cinematic realism while maintaining proportional integrity.

### Key Architectural Features:
*   **Hierarchical Conditioning:** Utilizes a dual-stage neural architecture where ControlNet anchors pose and geometry, while the IP-Adapter preserves facial features and color DNA.
*   **Multivariate Evaluation:** Implements a scientific assessment engine using **Laplacian Edge Fidelity** and **LAB Color Moment Analysis** to quantitatively track the preservation of structural and chromatic identity.
*   **Adaptive Heuristics:** The system incorporates a **Visual Complexity Scoring (VCS) Analyzer** which dynamically adjusts generation hyper-parameters (ControlNet scale, steps) based on the structural density of the input image.
*   **Low-VRAM Optimization:** Features a **Linear Latent Approximation** bypass for real-time previews, mitigating the VAE decoding bottleneck which often stalls inference on 6GB GPUs.
*   **Granular Telemetry:** The Celery worker reports detailed **Lifecycle States** (`LOADING_MODELS`, `ALLOCATING_VRAM`, `SYNTHESIZING`) for full transparency during the "Cold Start" phase.

---

## 🏗 System Architecture (Hexagonal / DDD)

The system adheres strictly to Domain-Driven Design (DDD) principles, ensuring that the core business logic (Use Cases) remains independent of the underlying technology (PyTorch/FastAPI).

### Domain-Driven Design Layers

```mermaid
graph TD
    A[Presentation: UI / Nginx] --> B(Application: Use Cases);
    B --> C[Domain: Ports & Entities];
    C --> D[Infrastructure: Adapters];

    subgraph Domain Boundary
        C
        B
    end

    subgraph Infrastructure
        D
        E[Adapter: StableDiffusionGenerator]
        F[Adapter: Celery / Redis]
        G[Adapter: FastAPI Gateway]
        D --> E;
        D --> F;
        D --> G;
    end
    
    style C fill:#f9f,stroke:#333,stroke-width:2px;
    style B fill:#ccf,stroke:#333;
    style E fill:#faa,stroke:#f66,stroke-width:2px;
```

### Asynchronous Data Flow & Task Orchestration

```mermaid
sequenceDiagram
    participant UI as Cyber-Capsule UI
    participant API as FastAPI Gateway
    participant Redis as Broker / Cache
    participant Worker as Celery Worker (CUDA)
    
    UI->>API: 1. /transform (Upload & Params)
    API->>API: 2. Acquire Hardware Mutex (Redis Lock)
    API->>Redis: 3. Dispatch transform_character_task
    Note over Worker: 4. Cold Start Check (30s delay if necessary)
    Redis->>Worker: 5. Task Received (ID: T1)
    Worker->>Worker: 6. Inference Loop (U-Net, ControlNet, IP-Adapter)
    loop Every 5 Steps
        Worker->>Redis: 7. Status Update (PROGRESS, % Completion, Latent Preview)
        UI->>API: 8. Poll /status/T1
        API->>UI: 9. Return Progress & Preview (base64)
    end
    Worker->>Redis: 10. Final Result (SUCCESS, Image PNG, Metrics)
    UI->>API: 11. Poll /result/T1
    API->>UI: 12. Return Final Data
    API->>API: 13. Release Hardware Mutex
```

---

## 🛠 Tech Stack

- **AI Core:** Stable Diffusion 1.5 (Realistic Vision V5.1), IP-Adapter, PyTorch, Hugging Face Diffusers, ControlNet.
- **Backend/Gateway:** FastAPI (Python).
- **Task Management:** Celery & Redis (Broker/Backend).
- **Frontend:** Custom Nginx (HTML/CSS/JS Cyber-Capsule UI).
- **DevOps:** Docker, Docker Compose, GNU Make (Hardware-aware deployment).

---

## 🚦 Getting Started (GPU Accelerated)

### Prerequisites
- Docker & Docker Compose.
- NVIDIA Container Toolkit (required for CUDA access).
- Minimum 16GB RAM (for system stability during model loading).
- NVIDIA GPU with at least 6GB VRAM (GTX 1060 or better).

### Installation & Launch

1.  **Clone the repository and enter the directory.**
2.  **Build the ecosystem:** This step downloads the multi-gigabyte models (SD, ControlNets, IP-Adapter) and builds the CUDA-ready Python environment.
    ```bash
    make build
    ```
3.  **Start all services:** The `Makefile` automatically detects the NVIDIA GPU and loads the `docker-compose.gpu.yml`.
    ```bash
    make up
    ```
4.  **Monitor the AI Cold Start:** Wait for the `z-realism-worker` to finish loading the models before using the UI.
    ```bash
    make logs-worker
    ```

### Accessing the System
- **Control Studio (Custom UI):** [http://localhost](http://localhost)
- **API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Expert Dashboard (Streamlit):** [http://localhost:8501](http://localhost:8501)

---

## 🧪 Development & Maintenance (Advanced Commands)

| Command | Description |
| :--- | :--- |
| `make logs-worker` | Stream the AI's internal processing and lifecycle telemetry. |
| `make shell-worker` | Access the terminal inside the CUDA worker container. |
| `make restart` | Quick restart of all services (use after code changes in mounted volumes). |
| `make down` | Stop and remove all containers gracefully. |
| `make clean-model` | **DANGER:** Removes the `hf_cache` model volume (forces re-download on next startup). |

---

## 🔒 Privacy & Licensing

**Z-Realism AI** is designed for local, offline operation. No data leaves your machine once the initial models are downloaded, ensuring input/output privacy.

**Code License:** MIT License (Copyright 2024 Enrique González Gutiérrez)

**AI Model License Notice:**
The core models (Stable Diffusion 1.5, T2I-Adapter) are subject to the **CreativeML Open RAIL-M License**. Users must ensure compliance with these terms, which govern responsible usage.

---
