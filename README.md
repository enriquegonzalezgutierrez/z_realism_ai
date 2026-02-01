# 🐉 Z-Realism AI: Dragon Ball Live-Action Engine

[![Docker](https://img.shields.io/badge/Docker-Enabled-blue?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Queue-Celery-37814A?logo=celery)](https://docs.celeryq.dev/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-00d0ff?logo=streamlit)](https://streamlit.io/)
[![Architecture](https://img.shields.io/badge/Architecture-DDD%20%2F%20SOLID-orange)](#architecture)

**Z-Realism AI** is a professional-grade generative AI ecosystem designed to transform Dragon Ball characters from 2D/3D art into photorealistic "Live Action" human versions. By leveraging **Stable Diffusion XL (SDXL) and IP-Adapter** in an asynchronous pipeline, it delivers unprecedented realism and structural fidelity.

**Author:** Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

---

## 🚀 The Vision

The previous generation of style transfer struggled with structural distortion and low resolution. **Z-Realism** uses **SDXL's 1024px** native capacity combined with the **IP-Adapter's** superior structural recognition to eliminate the "uncanny valley" and achieve cinematic-quality human synthesis.

### Key Capabilities:
- **Photorealistic Synthesis (HD):** Uses SDXL's advanced training to generate highly detailed skin textures, realistic eyes, and natural fabric folds.
- **Structural Integrity (IP-Adapter):** Maintains the character's original pose, proportion, and visual composition by using the input image as a structural reference.
- **Dynamic Resolution Control:** Allows the user to select the output quality (384px to 768px), with the system automatically preserving the original image's aspect ratio.
- **Asynchronous Processing:** Handles heavy AI workloads (9GB+ model) in background workers, ensuring a responsive user experience.
- **Hardware Agnostic:** Automatically detects and utilizes NVIDIA GPUs (CUDA) or optimized CPU inference.

---

## 🏗 Architecture

The project is built following **Domain-Driven Design (DDD)** and strictly adheres to **SOLID principles**, ensuring maintainability and scalability.

### Layers:
1.  **Domain Layer (`src/domain`):** Contains the technology-agnostic interfaces (`ImageGeneratorPort`).
2.  **Application Layer (`src/application`):** Implements Use Cases, orchestrating the generation strategy and managing the user-defined controls (Resolution, Features).
3.  **Infrastructure Layer (`src/infrastructure`):** The technical implementations (SDXL adapter, Celery/Redis worker, FastAPI producer).
4.  **Presentation Layer (`src/presentation`):** A high-contrast, professional Streamlit dashboard providing dynamic controls and real-time progress feedback.

### Data Flow:
`User Upload (w/ Resolution/Features)` ➡️ `FastAPI (Producer)` ➡️ `Redis Queue` ➡️ `Celery Worker (SDXL Engine)` ➡️ `Redis Result Cache` ➡️ `Streamlit (Polling)`

---

## 🛠 Tech Stack

- **AI Core:** Stable Diffusion XL (SDXL Base 1.0), IP-Adapter, PyTorch, Hugging Face Diffusers.
- **Backend:** FastAPI (Asynchronous Python).
- **Task Management:** Celery & Redis.
- **Frontend:** Streamlit (High-Contrast/Responsive UI).
- **DevOps:** Docker, Docker Compose, GNU Make.

---

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose.
- At least 16GB of RAM (required for loading the 9GB+ SDXL model).
- Internet connection (Only for the **initial** build to download the models).

### Installation & Launch

1.  **Clone the repository and enter the directory.**
2.  **Build the ecosystem:** (This step downloads SDXL and IP-Adapter, requiring several GB).
    ```bash
    make build
    ```
3.  **Start all services (API, Worker, Dashboard, Redis):**
    ```bash
    make up
    ```
4.  **Monitor the AI loading process:** (Wait for the process to complete before using the UI).
    ```bash
    make logs-worker
    ```

### Accessing the System
- **User Interface (Control Studio):** [http://localhost:8501](http://localhost:8501)
- **API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Development & Maintenance

Standardized tasks via `Makefile`:

| Command | Description |
| :--- | :--- |
| `make logs-worker` | View the AI "thinking" process (diffusion steps). |
| `make clean-model` | **Removes ONLY the 9GB+ AI model cache volume.** (Forces re-download on next `make up`). |
| `make format` | Automatically format code with Black/Isort. |
| `make test` | Execute the Pytest suite. |
| `make clean` | Stop containers and clear temporary networks. |
| `make prune` | **Danger:** Wipe all containers, networks, and volumes (full reset). |

---

## 🔒 Privacy & Licensing

**Z-Realism AI** runs entirely on your local hardware. Once the models are downloaded, the system operates **100% offline**, guaranteeing privacy for your inputs and outputs.

**Code License:** MIT License (Copyright 2024 Enrique González Gutiérrez)

**AI Model License Notice:**
The core models, **Stable Diffusion XL (SDXL) Base 1.0** and the **T2I-Adapter**, are licensed under the **CreativeML Open RAIL-M License**. Users must comply with these terms, which prohibit the creation of harmful or illegal content.