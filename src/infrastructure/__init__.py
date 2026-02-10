# path: z_realism_ai/src/infrastructure/__init__.py
# description: Infrastructure Layer Package Marker v21.0.
#
# ARCHITECTURAL ROLE (Hexagonal/DDD):
# This package encapsulates the Infrastructure Layer (also known as the 
# "Adapters" layer). Its primary responsibility is to implement the 
# technical details defined by the Domain Ports.
#
# CONTENTS:
# - API Adapters: FastAPI gateways for external communication.
# - Inference Adapters: Concrete implementations of Stable Diffusion and AnimateDiff.
# - Task Adapters: Distributed worker orchestration via Celery/Redis.
# - Analytics Adapters: Heuristic analysis and scientific evaluation engines.
#
# author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>

"""
Infrastructure Package for the Z-Realism AI Ecosystem.
This layer provides concrete implementations for the abstract domain contracts.
"""