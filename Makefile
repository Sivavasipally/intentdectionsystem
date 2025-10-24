.PHONY: help install run test clean docker-build docker-run ingest eval lint format verify smoke

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python
DOCS ?= ./kb/*.pdf
TENANT ?= bank-asia

help: ## Show this help message
	@echo "GenAI Intent Detection System - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run: ## Run the application
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run in production mode
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-quick: ## Run tests without coverage
	$(PYTHON) -m pytest tests/ -v

ingest: ## Ingest documents (usage: make ingest DOCS=./kb/*.pdf TENANT=bank-asia)
	@echo "Ingesting documents from: $(DOCS)"
	@echo "Tenant: $(TENANT)"
	$(PYTHON) scripts/ingest_cli.py --tenant $(TENANT) $(DOCS)

eval: ## Run offline evaluation
	$(PYTHON) eval/evaluate.py

lint: ## Run linters
	$(PYTHON) -m ruff check app/ tests/
	$(PYTHON) -m mypy app/ --ignore-missing-imports

format: ## Format code
	$(PYTHON) -m black app/ tests/
	$(PYTHON) -m ruff check --fix app/ tests/

clean: ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

docker-build: ## Build Docker image
	docker build -t intent-detection-system:latest .

docker-run: ## Run with Docker Compose
	docker-compose up -d

docker-stop: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f intent-system

db-init: ## Initialize database
	$(PYTHON) scripts/init_db.py

db-migrate: ## Run database migrations (if using Alembic)
	alembic upgrade head

setup: install db-init ## Complete setup
	@echo "Setup complete! Run 'make run' to start the server"

dev: ## Start development environment
	@echo "Starting development environment..."
	make clean
	make install
	make db-init
	make run

.PHONY: docs
docs: ## Generate API documentation
	@echo "API documentation available at http://localhost:8000/docs after starting the server"

verify: ## Verify system setup
	$(PYTHON) scripts/verify_setup.py

smoke: ## Run smoke tests
	$(PYTHON) scripts/test_system.py smoke

test-system: ## Interactive system testing
	$(PYTHON) scripts/test_system.py
