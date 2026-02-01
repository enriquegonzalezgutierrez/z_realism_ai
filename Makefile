# path: z_realism_ai/Makefile
# description: Task automation tool for the Dockerized Z-Realism AI environment.
#              Abstracts complex Docker commands into simple shortcuts.
# Author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

# --------------------------------------------------------------------------
# Variables
# --------------------------------------------------------------------------
DOCKER_COMPOSE = docker-compose
APP_SERVICE = z-realism-api
WORKER_SERVICE = z-realism-worker
BROKER_SERVICE = z-realism-broker
DASHBOARD_SERVICE = z-realism-dashboard
MODEL_CACHE_VOLUME = hf_cache

# Colors for help output (using printf for better portability)
CLR_RESET   = \033[0m
CLR_CYAN    = \033[36m
CLR_YELLOW  = \033[33m
CLR_GREEN   = \033[32m
CLR_RED     = \033[31m
CLR_BOLD    = \033[1m

# --------------------------------------------------------------------------
# Default Target
# --------------------------------------------------------------------------
.PHONY: help
help: ## Shows this help message
	@printf "$(CLR_BOLD)Z-Realism AI - Management Console$(CLR_RESET)\n"
	@printf "Usage: make $(CLR_CYAN)[target]$(CLR_RESET)\n\n"
	
	@printf "$(CLR_CYAN)$(CLR_BOLD)CORE & DOCKER LIFECYCLE:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | grep -v "shell\|logs\|test\|format\|lint\|redis\|clean-model\|prune" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_CYAN)%-25s$(CLR_RESET) %s\n", $$1, $$2}'
	
	@printf "\n$(CLR_YELLOW)$(CLR_BOLD)DEVELOPMENT & ACCESS:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep "shell\|logs\|redis" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_YELLOW)%-25s$(CLR_RESET) %s\n", $$1, $$2}'
	
	@printf "\n$(CLR_GREEN)$(CLR_BOLD)QUALITY & UTILITIES:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep "test\|format\|lint" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_GREEN)%-25s$(CLR_RESET) %s\n", $$1, $$2}'
	
	@printf "\n$(CLR_RED)$(CLR_BOLD)MAINTENANCE & DANGER ZONE:$(CLR_RESET)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep "clean\|prune" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_RED)%-25s$(CLR_RESET) %s\n", $$1, $$2}'

# --------------------------------------------------------------------------
# Docker Lifecycle
# --------------------------------------------------------------------------
.PHONY: build
build: ## Builds the Docker images for all services (API, Worker, Dashboard)
	$(DOCKER_COMPOSE) build

.PHONY: up
up: ## Starts the application and its infrastructure (API, Worker, Redis, Dashboard)
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down: ## Stops and removes all application containers
	$(DOCKER_COMPOSE) down

.PHONY: restart
restart: ## Restarts all core services (API and Worker)
	$(DOCKER_COMPOSE) restart $(APP_SERVICE) $(WORKER_SERVICE) $(DASHBOARD_SERVICE)

# --------------------------------------------------------------------------
# Development & Access
# --------------------------------------------------------------------------
.PHONY: logs
logs: ## Shows live logs from the API service
	$(DOCKER_COMPOSE) logs -f $(APP_SERVICE)

.PHONY: logs-worker
logs-worker: ## Shows live logs from the AI Worker (Neural Network process)
	$(DOCKER_COMPOSE) logs -f $(WORKER_SERVICE)

.PHONY: logs-dashboard
logs-dashboard: ## Shows live logs from the Streamlit Dashboard
	$(DOCKER_COMPOSE) logs -f $(DASHBOARD_SERVICE)

.PHONY: shell-api
shell-api: ## Opens a Bash shell inside the API container
	@printf "$(CLR_YELLOW)--- Entering API Container Shell ---$(CLR_RESET)\n"
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) bash

.PHONY: shell-worker
shell-worker: ## Opens a Bash shell inside the Worker container
	@printf "$(CLR_YELLOW)--- Entering Worker Container Shell ---$(CLR_RESET)\n"
	$(DOCKER_COMPOSE) exec $(WORKER_SERVICE) bash

.PHONY: redis-cli
redis-cli: ## Access the Redis CLI to monitor the task queue
	$(DOCKER_COMPOSE) exec $(BROKER_SERVICE) redis-cli

# --------------------------------------------------------------------------
# Quality & Utilities (Python Focus)
# --------------------------------------------------------------------------
.PHONY: format
format: ## Formats Python code using Black and Isort
	@printf "$(CLR_GREEN)--- Formatting Code ---$(CLR_RESET)\n"
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) black src/
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) isort src/

.PHONY: lint
lint: ## Checks code style without modifying files (using flake8)
	@printf "$(CLR_GREEN)--- Linting Code ---$(CLR_RESET)\n"
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) flake8 src/

.PHONY: test
test: ## Runs Unit Tests (pytest)
	@printf "$(CLR_GREEN)--- Running Tests ---$(CLR_RESET)\n"
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) pytest

# --------------------------------------------------------------------------
# Maintenance & Danger Zone
# --------------------------------------------------------------------------
.PHONY: clean
clean: ## Stops containers and removes network artifacts
	$(DOCKER_COMPOSE) down --remove-orphans
	@printf "$(CLR_RED)--- Environment cleaned ---$(CLR_RESET)\n"

.PHONY: clean-model
clean-model: ## Removes ONLY the large AI model cache volume (forces re-download)
	@printf "$(CLR_RED)$(CLR_BOLD)!!! WARNING: Purging 4GB+ AI Model Cache !!!$(CLR_RESET)\n"
	$(DOCKER_COMPOSE) down
	docker volume rm $(MODEL_CACHE_VOLUME) || true
	@printf "$(CLR_RED)--- AI Model Cache Cleared. Run 'make up' to re-download ---$(CLR_RESET)\n"

.PHONY: prune
prune: ## Deep clean: Removes containers, volumes, and images
	@printf "$(CLR_RED)$(CLR_BOLD)!!! WARNING: Removing ALL Images and Volumes !!!$(CLR_RESET)\n"
	$(DOCKER_COMPOSE) down -v --rmi all
	@printf "$(CLR_RED)--- Deep clean complete ---$(CLR_RESET)\n"