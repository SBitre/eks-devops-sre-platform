.PHONY: help dev test lint build deploy clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Development ────────────────────────────────────────
dev: ## Start local development environment
	docker compose up --build

dev-down: ## Stop local development environment
	docker compose down -v

# ─── Testing ────────────────────────────────────────────
test: ## Run tests
	pytest tests/ -v --tb=short

lint: ## Run linter
	ruff check app/
	ruff format --check app/

format: ## Auto-format code
	ruff format app/

# ─── Docker ─────────────────────────────────────────────
build: ## Build Docker image
	docker build -t devops-sre-platform:latest .

scan: ## Scan Docker image for vulnerabilities
	trivy image devops-sre-platform:latest

# ─── Terraform ──────────────────────────────────────────
tf-init: ## Initialize Terraform
	cd terraform/environments/prod && terraform init

tf-plan: ## Plan Terraform changes
	cd terraform/environments/prod && terraform plan

tf-apply: ## Apply Terraform changes
	cd terraform/environments/prod && terraform apply

tf-destroy: ## Destroy Terraform resources
	cd terraform/environments/prod && terraform destroy

# ─── Kubernetes ─────────────────────────────────────────
k8s-apply: ## Apply Kubernetes manifests
	kubectl apply -f k8s/base/
	kubectl apply -f k8s/security/
	kubectl apply -f k8s/monitoring/

k8s-status: ## Check deployment status
	kubectl get pods,svc,ingress -n devops-platform

k8s-logs: ## View application logs
	kubectl logs -n devops-platform -l app=devops-platform --tail=100 -f

# ─── Clean ──────────────────────────────────────────────
clean: ## Clean up local artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
