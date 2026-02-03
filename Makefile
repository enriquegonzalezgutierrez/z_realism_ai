# path: z_realism_ai/Makefile
# description: Task automation tool for the Hardware-Aware Z-Realism AI environment.
#              Automatically detects GPU availability to select the correct
#              Docker Compose orchestration profile.
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

# -----------------------------------------------------------------------------
# Configuration & Service Names
# -----------------------------------------------------------------------------
APP_SERVICE       = z-realism-api
WORKER_SERVICE    = z-realism-worker
BROKER_SERVICE    = z-realism-broker
DASHBOARD_SERVICE = z-realism-dashboard
MODEL_CACHE_VOL   = hf_cache

# -----------------------------------------------------------------------------
# Hardware Detection Logic
# -----------------------------------------------------------------------------
# Checks if nvidia-smi exists and returns successfully.
# This determines if we inject the GPU resource reservations.
HAS_GPU := $(shell nvidia-smi > /dev/null 2>&1 && echo "yes" || echo "no")

ifeq ($(HAS_GPU),yes)
    DOCKER_COMPOSE_CMD = docker-compose -f docker-compose.yml -f docker-compose.gpu.yml
    HW_STATUS = "SYSTEM: [NVIDIA GPU] detected. Activating CUDA acceleration."
else
    DOCKER_COMPOSE_CMD = docker-compose -f docker-compose.yml
    HW_STATUS = "SYSTEM: [CPU ONLY] detected. Running in legacy mode."
endif

# -----------------------------------------------------------------------------
# UI Styling
# -----------------------------------------------------------------------------
CLR_RESET   = \033[0m
CLR_CYAN    = \033[36m
CLR_YELLOW  = \033[33m
CLR_GREEN   = \033[32m
CLR_RED     = \033[31m
CLR_BOLD    = \033[1m

# -----------------------------------------------------------------------------
# Default Target: Help Documentation
# -----------------------------------------------------------------------------
.PHONY: help
help: ## Display this help message
	@printf "$(CLR_BOLD)Z-Realism AI - Multi-Hardware Management Console$(CLR_RESET)\n"
	@printf "Detected Environment: $(CLR_GREEN)$(HW_STATUS)$(CLR_RESET)\n\n"
	@printf "Usage: make $(CLR_CYAN)[target]$(CLR_RESET)\n\n"
	
	@printf "$(CLR_CYAN)$(CLR_BOLD)CORE LIFECYCLE:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "build|up|down|restart" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_CYAN)%-25s$(CLR_RESET) %s\n", $$1, $$2}'
	
	@printf "\n$(CLR_YELLOW)$(CLR_BOLD)DEVELOPMENT & MONITORING:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "logs|shell|redis" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_YELLOW)%-25s$(CLR_RESET) %s\n", $$1, $$2}'
	
	@printf "\n$(CLR_GREEN)$(CLR_BOLD)QUALITY ASSURANCE:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "format|lint|test" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_GREEN)%-25s$(CLR_RESET) %s\n", $$1, $$2}'
	
	@printf "\n$(CLR_RED)$(CLR_BOLD)DANGER ZONE:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "clean|prune" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_RED)%-25s$(CLR_RESET) %s\n", $$1, $$2}'

# -----------------------------------------------------------------------------
# Core Lifecycle
# -----------------------------------------------------------------------------
.PHONY: build
build: ## Build images using the detected hardware profile
	@echo $(HW_STATUS)
	$(DOCKER_COMPOSE_CMD) build

.PHONY: up
up: ## Start the ecosystem (API, Worker, Redis, Dashboard)
	@echo $(HW_STATUS)
	$(DOCKER_COMPOSE_CMD) up -d

.PHONY: down
down: ## Stop and remove all active containers
	$(DOCKER_COMPOSE_CMD) down

.PHONY: restart
restart: ## Restart all core application services
	$(DOCKER_COMPOSE_CMD) restart $(APP_SERVICE) $(WORKER_SERVICE) $(DASHBOARD_SERVICE)

# -----------------------------------------------------------------------------
# Development & Monitoring
# -----------------------------------------------------------------------------
.PHONY: logs
logs: ## Stream live logs from the API service
	$(DOCKER_COMPOSE_CMD) logs -f $(APP_SERVICE)

.PHONY: logs-worker
logs-worker: ## Stream live logs from the AI Inference Worker
	$(DOCKER_COMPOSE_CMD) logs -f $(WORKER_SERVICE)

.PHONY: shell-api
shell-api: ## Access the terminal inside the API container
	$(DOCKER_COMPOSE_CMD) exec $(APP_SERVICE) bash

.PHONY: shell-worker
shell-worker: ## Access the terminal inside the Worker container
	$(DOCKER_COMPOSE_CMD) exec $(WORKER_SERVICE) bash

.PHONY: redis-cli
redis-cli: ## Open Redis CLI to inspect task queues
	$(DOCKER_COMPOSE_CMD) exec $(BROKER_SERVICE) redis-cli

# -----------------------------------------------------------------------------
# Quality Assurance
# -----------------------------------------------------------------------------
.PHONY: format
format: ## Format Python code (Black & Isort)
	$(DOCKER_COMPOSE_CMD) exec $(APP_SERVICE) black src/
	$(DOCKER_COMPOSE_CMD) exec $(APP_SERVICE) isort src/

.PHONY: lint
lint: ## Run style and syntax checks (Flake8)
	$(DOCKER_COMPOSE_CMD) exec $(APP_SERVICE) flake8 src/

.PHONY: test
test: ## Execute unit and integration tests (Pytest)
	$(DOCKER_COMPOSE_CMD) exec $(APP_SERVICE) pytest

# -----------------------------------------------------------------------------
# Danger Zone (Maintenance)
# -----------------------------------------------------------------------------
.PHONY: clean
clean: ## Remove containers and network artifacts
	$(DOCKER_COMPOSE_CMD) down --remove-orphans
	@printf "$(CLR_RED)--- Environment Cleaned ---$(CLR_RESET)\n"

.PHONY: clean-model
clean-model: ## Force re-download of AI models by purging hf_cache volume
	@printf "$(CLR_RED)$(CLR_BOLD)WARNING: Removing 10GB+ Model Cache!$(CLR_RESET)\n"
	$(DOCKER_COMPOSE_CMD) down
	docker volume rm $(MODEL_CACHE_VOL) || true
	@printf "$(CLR_RED)--- Cache Purged. Run 'make up' to rebuild ---$(CLR_RESET)\n"

.PHONY: prune
prune: ## Complete system wipe: containers, volumes, and images
	@printf "$(CLR_RED)$(CLR_BOLD)DANGER: Full System Reset Initiated!$(CLR_RESET)\n"
	$(DOCKER_COMPOSE_CMD) down -v --rmi all
	@printf "$(CLR_RED)--- Deep Clean Complete ---$(CLR_RESET)\n"