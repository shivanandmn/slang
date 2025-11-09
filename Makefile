# Slang LiveKit Agent - Development Commands

.PHONY: help install test run docker-build docker-run clean lint

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and setup virtual environment
	python -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Dependencies installed. Activate with: source venv/bin/activate"

test: ## Run local validation tests
	python test_local.py

run: ## Run the agent locally
	python multi_agent.py

docker-build: ## Build Docker image
	docker build -t slang-agent .

docker-run: ## Run Docker container with .env file
	docker run --env-file .env -p 8080:8080 slang-agent

docker-test: ## Build and run Docker container for testing
	make docker-build
	make docker-run

clean: ## Clean up temporary files and containers
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: ## Run code formatting and linting
	python -m black multi_agent.py test_local.py
	python -m flake8 multi_agent.py test_local.py --max-line-length=88

dev-setup: ## Complete development setup
	make install
	cp .env.example .env
	@echo "✅ Development setup complete!"
	@echo "📝 Edit .env with your API keys, then run: make test"

# Quick development workflow
dev: ## Quick development test (validate + run)
	make test
	make run
