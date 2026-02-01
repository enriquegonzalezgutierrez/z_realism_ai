# 🐉 Z-Realism AI: Dragon Ball Live-Action Engine

[![Docker](https://img.shields.io/badge/Docker-Enabled-blue?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Queue-Celery-37814A?logo=celery)](https://docs.celeryq.dev/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Architecture](https://img.shields.io/badge/Architecture-DDD%20%2F%20SOLID-orange)](#architecture)

**Z-Realism AI** is a professional-grade generative AI ecosystem designed to transform Dragon Ball characters from 2D/3D art into photorealistic "Live Action" human versions. By leveraging Stable Diffusion and a robust asynchronous architecture, it bridges the gap between anime aesthetics and cinematic realism.

**Author:** Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

---

## 🚀 The Vision

Traditional style transfer often loses the essence of the character or stays too close to the "cartoon" look. **Z-Realism** uses a sophisticated **Image-to-Image (Img2Img)** pipeline combined with **Expert Prompt Engineering** to reinterpret character features as human anatomy, realistic textures, and cinematic lighting.

### Key Capabilities:
- **Photorealistic Synthesis:** Converts anime strokes into skin pores, real hair textures, and fabric dynamics.
- **Structural Integrity:** Maintains character poses and silhouettes using structural guidance.
- **Asynchronous Processing:** Handles heavy AI workloads in background workers, ensuring a responsive user experience.
- **Hardware Agnostic:** Automatically detects and utilizes NVIDIA GPUs (CUDA), Apple Silicon (MPS), or fallback to optimized CPU inference.

---

## 🏗 Architecture

The project is built following **Domain-Driven Design (DDD)** and strictly adheres to **SOLID principles**, ensuring maintainability and scalability.

### Layers:
1.  **Domain Layer (`src/domain`):** Contains the technology-agnostic interfaces (Ports). The core business logic doesn't know about Stable Diffusion; it only knows about `ImageGeneratorPort`.
2.  **Application Layer (`src/application`):** Implements Use Cases. This is where the **"Secret Sauce"** (Prompt Engineering) lives, orchestrating the transformation strategy.
3.  **Infrastructure Layer (`src/infrastructure`):** The technical implementations. Includes the FastAPI controller, the Stable Diffusion adapter, and the Celery/Redis worker logic.
4.  **Presentation Layer (`src/presentation`):** A reactive Streamlit dashboard for end-user interaction.

### Data Flow:
`User Upload` ➡️ `FastAPI (Producer)` ➡️ `Redis Queue` ➡️ `Celery Worker (AI Engine)` ➡️ `Result Storage` ➡️ `Streamlit (Polling)`

---

## 🛠 Tech Stack

- **AI Core:** PyTorch, Hugging Face Diffusers (Stable Diffusion v1.5), Transformers.
- **Backend:** FastAPI (Asynchronous Python).
- **Task Management:** Celery & Redis.
- **Frontend:** Streamlit.
- **DevOps:** Docker, Docker Compose, GNU Make.

---

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose.
- At least 8GB of RAM (16GB recommended).
- Internet connection (Only for the **initial** build to download the 4GB model).

### Installation & Launch

1.  **Clone the repository.**
2.  **Build the ecosystem:**
    ```bash
    make build
    ```
3.  **Start the services:**
    ```bash
    make up
    ```
4.  **Monitor the AI loading process:**
    ```bash
    make logs-worker
    ```

### Accessing the System
- **User Interface:** [http://localhost:8501](http://localhost:8501)
- **API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redis Monitor:** `make redis-cli`

---

## 🧪 Development & Maintenance

Standardized tasks via `Makefile`:

| Command | Description |
| :--- | :--- |
| `make logs-worker` | View the AI "thinking" process and diffusion steps. |
| `make format` | Automatically format code with Black/Isort. |
| `make test` | Execute the Pytest suite. |
| `make clean` | Stop containers and clear temporary networks. |
| `make prune` | **Danger:** Wipe all data, including downloaded AI models. |

---

## 🔒 Privacy & Independence

Unlike external AI services (Midjourney/OpenAI), **Z-Realism AI** runs entirely on your hardware. Once the model weights are cached in the `hf_cache` volume, the system can operate **100% offline**. Your images never leave your local environment.

---

## ⚖️ License & Credits

Designed and developed by **Enrique González Gutiérrez**.  
Special thanks to the Open Source community at **Hugging Face** and **CompVis** for the Stable Diffusion weights.

*Disclaimer: This project is a fan-made AI tool. Dragon Ball is a trademark of Akira Toriyama / Toei Animation.*
