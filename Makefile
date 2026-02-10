# path: z_realism_ai/Makefile
# description: Ultimate Orchestrator v9.0 - Full Stack Management.
#              Manages: Custom UI (80), Expert Dashboard (8501), API (8000), 
#              Worker (Inference), Broker (Redis), and Remote Sharing (Ngrok).
#
# NEW FEATURE (v9.0): 
# - Added 'make share' to expose the local lab to the internet via Ngrok.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

# -----------------------------------------------------------------------------
# Configuration & Service Names
# -----------------------------------------------------------------------------
UI_SERVICE        = z-realism-ui
DASHBOARD_SERVICE = z-realism-dashboard
APP_SERVICE       = z-realism-api
WORKER_SERVICE    = z-realism-worker
BROKER_SERVICE    = z-realism-broker
MODEL_CACHE_VOL   = hf_cache

# -----------------------------------------------------------------------------
# Hardware Detection Logic
# -----------------------------------------------------------------------------
HAS_GPU := $(shell nvidia-smi > /dev/null 2>&1 && echo "yes" || echo "no")

ifeq ($(HAS_GPU),yes)
    DOCKER_COMPOSE_CMD = docker-compose -f docker-compose.yml -f docker-compose.gpu.yml
    HW_STATUS = "SYSTEM: [NVIDIA GPU] detected. Activating CUDA acceleration."
else
    DOCKER_COMPOSE_CMD = docker-compose -f docker-compose.yml
    HW_STATUS = "SYSTEM: [CPU ONLY] detected. Running in legacy mode."
endif

# -----------------------------------------------------------------------------
# UI Styling (Colors)
# -----------------------------------------------------------------------------
CLR_RESET   = \033[0m
CLR_CYAN    = \033[36m
CLR_YELLOW  = \033[33m
CLR_GREEN   = \033[32m
CLR_RED     = \033[31m
CLR_BOLD    = \033[1m

# -----------------------------------------------------------------------------
# Help / Documentation
# -----------------------------------------------------------------------------
.PHONY: help
help: ## Display this help message
	@printf "$(CLR_BOLD)Z-Realism AI - Full Stack Management v9.0$(CLR_RESET)\n"
	@printf "Detected Environment: $(CLR_GREEN)$(HW_STATUS)$(CLR_RESET)\n"
	@printf "Custom UI (8080):    $(CLR_CYAN)http://localhost:8080$(CLR_RESET)\n"
	@printf "Expert Dashboard:    $(CLR_CYAN)http://localhost:8501$(CLR_RESET)\n"
	@printf "Backend API (8000):  $(CLR_CYAN)http://localhost:8000$(CLR_RESET)\n\n"
	@printf "Usage: make $(CLR_CYAN)[target]$(CLR_RESET)\n\n"
	
	@printf "$(CLR_CYAN)$(CLR_BOLD)CORE LIFECYCLE:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## CORE .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## CORE "}; {printf "  $(CLR_CYAN)%-25s$(CLR_RESET) %s\n", $$1, $$2}'
	
	@printf "\n$(CLR_YELLOW)$(CLR_BOLD)DEVELOPMENT & MONITORING:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## DEV .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## DEV "}; {printf "  $(CLR_YELLOW)%-25s$(CLR_RESET) %s\n", $$1, $$2}'
	
	@printf "\n$(CLR_RED)$(CLR_BOLD)DANGER ZONE:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## DANGER .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## DANGER "}; {printf "  $(CLR_RED)%-25s$(CLR_RESET) %s\n", $$1, $$2}'

# -----------------------------------------------------------------------------
# Core Lifecycle
# -----------------------------------------------------------------------------
.PHONY: build
build: ## CORE Build images using the detected hardware profile
	@echo $(HW_STATUS)
	$(DOCKER_COMPOSE_CMD) build

.PHONY: up
up: ## CORE Start the entire ecosystem (UI, Dashboard, API, Worker, Redis)
	@echo $(HW_STATUS)
	$(DOCKER_COMPOSE_CMD) up -d
	@printf "\n$(CLR_GREEN)System Online at http://localhost:8080 and http://localhost:8501$(CLR_RESET)\n"

.PHONY: down
down: ## CORE Stop and remove all active containers
	$(DOCKER_COMPOSE_CMD) down

.PHONY: restart
restart: ## CORE Restart all core services to apply changes
	$(DOCKER_COMPOSE_CMD) restart $(UI_SERVICE) $(DASHBOARD_SERVICE) $(APP_SERVICE) $(WORKER_SERVICE)

# -----------------------------------------------------------------------------
# Development & Monitoring
# -----------------------------------------------------------------------------
.PHONY: logs-api
logs-api: ## DEV Stream live logs from the FastAPI service
	$(DOCKER_COMPOSE_CMD) logs -f $(APP_SERVICE)

.PHONY: logs-worker
logs-worker: ## DEV Stream live logs from the AI Inference Worker
	$(DOCKER_COMPOSE_CMD) logs -f $(WORKER_SERVICE)

.PHONY: shell-worker
shell-worker: ## DEV Access the terminal inside the Worker container
	$(DOCKER_COMPOSE_CMD) exec $(WORKER_SERVICE) bash

.PHONY: stats
stats: ## DEV Show resource usage (CPU/GPU/RAM)
	docker stats

.PHONY: share
share: ## DEV Expose the Laboratory UI via Ngrok for mobile testing
	@printf "$(CLR_YELLOW)Initializing Ngrok Tunnel on Port 8080...$(CLR_RESET)\n"
	@printf "$(CLR_CYAN)ARCHITECT NOTE:$(CLR_RESET) Ensure API_BASE_URL in js/api.js matches your public API tunnel or local IP.\n"
	ngrok http 8080

# -----------------------------------------------------------------------------
# Danger Zone (Maintenance)
# -----------------------------------------------------------------------------
.PHONY: clean-model
clean-model: ## DANGER Purge model cache volume (forces re-download)
	@printf "$(CLR_RED)$(CLR_BOLD)WARNING: Removing Persistent AI Models!$(CLR_RESET)\n"
	$(DOCKER_COMPOSE_CMD) down
	docker volume rm z_realism_ai_hf_cache || true
	@printf "$(CLR_RED)Cache Purged. Run 'make up' to restart.$(CLR_RESET)\n"

.PHONY: prune
prune: ## DANGER Complete system wipe: containers, volumes, and images
	@printf "$(CLR_RED)$(CLR_BOLD)DANGER: Full System Reset Initiated!$(CLR_RESET)\n"
	$(DOCKER_COMPOSE_CMD) down -v --rmi all
	@printf "$(CLR_RED)--- Deep Clean Complete ---$(CLR_RESET)\n"