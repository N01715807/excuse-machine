MODEL            ?= phi3:mini
OLLAMA_CONTAINER ?= ollama-appECM
BACKEND_CONTAINER?= excuse-backend

ifeq ($(OS),Windows_NT)
  PY  = backend/.venv/Scripts/python
  PIP = backend/.venv/Scripts/pip
else
  PY  = backend/.venv/bin/python
  PIP = backend/.venv/bin/pip
endif

.PHONY: help up down restart ps logs pull-model models \
        venv install test-import

help:
	@echo "Available commands:"
    @echo "  make up           # Build and start Docker containers (backend + ollama)"
    @echo "  make down         # Stop and remove all containers"
    @echo "  make restart      # Restart all containers"
    @echo "  make ps           # Show container status"
    @echo "  make logs         # Follow all service logs"
    @echo "  make pull-model   # Pull model inside ollama container (default: $(MODEL))"
    @echo "  make models       # List all downloaded models"
    @echo "  make venv         # Create Python virtual environment in backend/"
    @echo "  make install      # Install backend dependencies into venv"
    @echo "  make test-import  # Verify fastapi/httpx/uvicorn imports in venv"
    @echo ""
    @echo "Example: make pull-model MODEL=gemma:2b-instruct"


# ===== Docker =====
up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose down && docker compose up -d --build

ps:
	docker compose ps

logs:
	docker compose logs -f

pull-model:
	docker exec -it $(OLLAMA_CONTAINER) ollama pull $(MODEL)

models:
	docker exec -it $(OLLAMA_CONTAINER) ollama list

# ===== venv =====
venv:
	python -m venv backend/.venv
	@echo "finish。PowerShell: .\\.venv\\Scripts\\Activate.ps1"
	@echo "Git Bash: source backend/.venv/Scripts/activate"

install: venv
	"$(PIP)" install -r backend/requirements.txt

test-import:
	"$(PY)" -c "import fastapi, httpx, uvicorn; print('venv ok')"
