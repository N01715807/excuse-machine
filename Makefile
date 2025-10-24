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
	@echo "可用命令："
	@echo "  make up           # 构建并启动 docker（backend + ollama）"
	@echo "  make down         # 停止并清理容器"
	@echo "  make restart      # 重启所有容器"
	@echo "  make ps           # 查看容器状态"
	@echo "  make logs         # 跟随查看所有服务日志"
	@echo "  make pull-model   # 在 ollama 容器内拉取模型（默认 $(MODEL)）"
	@echo "  make models       # 列出已下载模型"
	@echo "  make venv         # 在 backend/ 创建 Python 虚拟环境"
	@echo "  make install      # 在 venv 安装后端依赖"
	@echo "  make test-import  # 在 venv 验证 fastapi/httpx/uvicorn 是否可用"
	@echo ""
	@echo "示例：make pull-model MODEL=gemma:2b-instruct"

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
