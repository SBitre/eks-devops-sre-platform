# 🚀 EKS DevOps SRE Platform

> Production-grade DevOps Metrics & Incident Management Platform on AWS EKS — built with FastAPI, Terraform, and modern SRE practices.

[![CI/CD](https://github.com/SBitre/eks-devops-sre-platform/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/SBitre/eks-devops-sre-platform/actions/workflows/ci-cd.yaml)
[![Terraform](https://github.com/SBitre/eks-devops-sre-platform/actions/workflows/terraform.yaml/badge.svg)](https://github.com/SBitre/eks-devops-sre-platform/actions/workflows/terraform.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📋 Overview

A cloud-native platform that tracks **deployments**, **incidents**, **SLOs**, and calculates **DORA metrics** — the four key metrics used by elite engineering teams worldwide. Built to demonstrate production-grade DevOps and SRE practices on AWS EKS.

### Key Features

- **DORA Metrics Dashboard** — Deployment Frequency, Lead Time, Change Failure Rate, MTTR
- **Incident Lifecycle Management** — Create, track, and resolve incidents with full timeline
- **SLO Tracking & Error Budgets** — Define SLOs, monitor SLIs, and track error budget burn
- **Deployment Tracking** — Register, monitor, and analyze deployment events
- **Prometheus Metrics** — Custom business metrics with Grafana dashboards
- **Production Kubernetes** — HPA, PDB, Network Policies, RBAC, Pod Security

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AWS Cloud (us-east-1)                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                        VPC (10.0.0.0/16)                      │   │
│  │                                                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │   │
│  │  │  Public      │  │  Public      │  │  Public      │          │   │
│  │  │  Subnet AZ-a │  │  Subnet AZ-b │  │  Subnet AZ-c │          │   │
│  │  │  + NAT GW    │  │  + NAT GW    │  │  + NAT GW    │          │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │   │
│  │         │                  │                  │                  │   │
│  │  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐          │   │
│  │  │  Private     │  │  Private     │  │  Private     │          │   │
│  │  │  Subnet AZ-a │  │  Subnet AZ-b │  │  Subnet AZ-c │          │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │   │
│  │         │                  │                  │                  │   │
│  │  ┌──────┴──────────────────┴──────────────────┴───────┐        │   │
│  │  │              Amazon EKS Cluster (v1.30)             │        │   │
│  │  │                                                     │        │   │
│  │  │  ┌─────────────────────────────────────────────┐   │        │   │
│  │  │  │         devops-platform namespace            │   │        │   │
│  │  │  │                                              │   │        │   │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │        │   │
│  │  │  │  │ FastAPI  │ │ FastAPI  │ │ FastAPI  │    │   │        │   │
│  │  │  │  │ Pod (1)  │ │ Pod (2)  │ │ Pod (3)  │    │   │        │   │
│  │  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘    │   │        │   │
│  │  │  │       └─────────────┼─────────────┘          │   │        │   │
│  │  │  │                     │                        │   │        │   │
│  │  │  │              ┌──────┴──────┐                 │   │        │   │
│  │  │  │              │  ClusterIP  │                 │   │        │   │
│  │  │  │              │   Service   │                 │   │        │   │
│  │  │  │              └─────────────┘                 │   │        │   │
│  │  │  └──────────────────────────────────────────────┘   │        │   │
│  │  │                                                     │        │   │
│  │  │  ┌─────────────────────────────────────────────┐   │        │   │
│  │  │  │          monitoring namespace                │   │        │   │
│  │  │  │  ┌────────────┐  ┌─────────┐  ┌──────────┐ │   │        │   │
│  │  │  │  │ Prometheus │  │ Grafana │  │ OTel     │ │   │        │   │
│  │  │  │  │            │  │         │  │ Collector│ │   │        │   │
│  │  │  │  └────────────┘  └─────────┘  └──────────┘ │   │        │   │
│  │  │  └──────────────────────────────────────────────┘   │        │   │
│  │  └─────────────────────────────────────────────────────┘        │   │
│  │                                                                │   │
│  │  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐    │   │
│  │  │  RDS Postgres  │  │  ECR Registry │  │ Secrets Manager  │    │   │
│  │  │  (Multi-AZ)    │  │              │  │                  │    │   │
│  │  └───────────────┘  └──────────────┘  └──────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌───────────────┐                                                   │
│  │  AWS ALB       │ ◄── Internet Traffic (HTTPS:443)                 │
│  │  (Ingress)     │                                                   │
│  └───────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────┐
        │           GitHub Actions CI/CD               │
        │                                              │
        │  Test → Build → Scan → Push → Deploy → Smoke│
        └─────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Application** | Python 3.12, FastAPI, SQLAlchemy (async), Pydantic v2 |
| **Database** | PostgreSQL 16 (RDS Multi-AZ), Redis |
| **Container** | Docker (multi-stage), ECR (immutable tags, scan-on-push) |
| **Orchestration** | Kubernetes 1.30 (AWS EKS), Helm |
| **Infrastructure** | Terraform 1.8+ (modular, S3 backend, DynamoDB locking) |
| **CI/CD** | GitHub Actions (OIDC auth, multi-stage, auto-rollback) |
| **Observability** | Prometheus, Grafana, OpenTelemetry, CloudWatch |
| **Security** | IRSA, Network Policies, RBAC, KMS encryption, Trivy, Bandit |

---

## 📁 Project Structure

```
eks-devops-sre-platform/
├── app/                          # FastAPI application
│   ├── api/                      # API route handlers
│   │   ├── deployments.py        # Deployment tracking endpoints
│   │   ├── incidents.py          # Incident management endpoints
│   │   ├── slos.py               # SLO tracking endpoints
│   │   ├── metrics.py            # DORA metrics endpoints
│   │   └── health.py             # K8s probe endpoints
│   ├── core/                     # Core configuration
│   │   ├── config.py             # Pydantic Settings
│   │   ├── database.py           # Async SQLAlchemy engine
│   │   └── middleware.py         # Prometheus metrics middleware
│   ├── models/                   # SQLAlchemy ORM models
│   └── schemas/                  # Pydantic request/response schemas
│
├── terraform/                    # Infrastructure as Code
│   ├── modules/
│   │   ├── vpc/                  # VPC, subnets, NAT, flow logs
│   │   ├── eks/                  # EKS cluster, node groups, addons
│   │   ├── iam/                  # IRSA roles (app, ALB, autoscaler)
│   │   └── rds/                  # PostgreSQL RDS, secrets manager
│   └── environments/
│       └── prod/                 # Production environment config
│
├── k8s/                          # Kubernetes manifests
│   ├── base/                     # Deployment, Service, HPA, PDB, Ingress
│   ├── security/                 # Network Policies, RBAC
│   └── monitoring/               # Prometheus config, alerts, Grafana dashboard
│
├── .github/workflows/            # CI/CD pipelines
│   ├── ci-cd.yaml                # Test → Build → Deploy pipeline
│   └── terraform.yaml            # Infrastructure pipeline
│
├── tests/                        # API tests
├── Dockerfile                    # Multi-stage production build
├── docker-compose.yml            # Local development stack
└── Makefile                      # Common operations
```

---

## 🔌 API Endpoints

### Health & Probes
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Kubernetes liveness probe |
| `GET` | `/readyz` | Kubernetes readiness probe |
| `GET` | `/health` | Detailed health check |
| `GET` | `/metrics` | Prometheus metrics |

### Deployments
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/deployments` | Register a deployment |
| `GET` | `/api/v1/deployments` | List deployments (filterable) |
| `GET` | `/api/v1/deployments/{id}` | Get deployment details |
| `PATCH` | `/api/v1/deployments/{id}` | Update deployment status |
| `GET` | `/api/v1/deployments/stats/summary` | Deployment statistics |

### Incidents
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/incidents` | Create an incident |
| `GET` | `/api/v1/incidents` | List incidents (filterable) |
| `PATCH` | `/api/v1/incidents/{id}` | Update incident status |
| `POST` | `/api/v1/incidents/{id}/timeline` | Add timeline event |

### SLOs & Metrics
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/slos` | Define an SLO |
| `GET` | `/api/v1/slos` | List SLOs |
| `PATCH` | `/api/v1/slos/{id}` | Update SLI measurement |
| `GET` | `/api/v1/metrics/dora` | DORA four key metrics |
| `GET` | `/api/v1/metrics/summary` | Platform summary |

---

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/SBitre/eks-devops-sre-platform.git
cd eks-devops-sre-platform

# Start the full stack (app + postgres + redis + prometheus + grafana)
make dev

# Access the API docs
open http://localhost:8000/docs

# Access Grafana dashboards
open http://localhost:3000  # admin/admin

# Run tests
make test
```

### Deploy to AWS

```bash
# 1. Initialize and apply Terraform
make tf-init
make tf-plan
make tf-apply

# 2. Deploy Kubernetes manifests
make k8s-apply

# 3. Check status
make k8s-status
```

---

## 📊 DORA Metrics

This platform tracks the [DORA four key metrics](https://dora.dev/), which measure software delivery performance:

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| **Deployment Frequency** | Multiple/day | Weekly–Monthly | Monthly–6mo | < 6mo |
| **Lead Time for Changes** | < 1 hour | 1 day–1 week | 1–6 months | > 6 months |
| **Change Failure Rate** | 0–15% | 16–30% | 31–45% | > 45% |
| **MTTR** | < 1 hour | < 1 day | 1 day–1 week | > 1 week |

---

## 🔒 Security Features

- **IRSA (IAM Roles for Service Accounts)** — Pod-level AWS permissions via OIDC
- **KMS Encryption** — EKS secrets encrypted at rest
- **Network Policies** — Default deny with explicit allow rules
- **RBAC** — Least-privilege service account permissions
- **Pod Security** — Non-root, read-only filesystem, dropped capabilities
- **Image Scanning** — Trivy in CI/CD + ECR scan-on-push
- **Secret Management** — AWS Secrets Manager for database credentials
- **VPC Flow Logs** — Network traffic monitoring
- **TLS 1.3** — ALB SSL policy enforcement
- **Dependency Scanning** — Safety + Bandit in CI pipeline

---

## 📈 Observability Stack

```
Application  ──►  Prometheus  ──►  Grafana Dashboards
    │                                    │
    ├── HTTP request metrics             ├── DORA Metrics Dashboard
    ├── Business metrics (deployments)   ├── Request Rate & Latency
    ├── Incident MTTR tracking           ├── Error Budget Burn
    └── SLO compliance                   └── Active Incidents
                                         
Alerting Rules:
  • High error rate (> 5%)
  • P95 latency > 1s
  • Error budget burn rate
  • Pod restart loops
  • High CPU/Memory usage
  • MTTR degradation
```

---

## 🔄 CI/CD Pipeline

```
PR Created ──► Test & Lint ──► Security Scan
                                    │
Merge to Main ──► Build Docker ──► Push to ECR ──► Trivy Scan
                                                       │
                                              Deploy to EKS ──► Smoke Tests
                                                       │              │
                                                  (on failure)   (on success)
                                                       │              │
                                                  Auto Rollback    ✅ Done
```

**Pipeline Features:**
- OIDC authentication (no long-lived AWS keys)
- Multi-stage Docker builds with layer caching
- Automated security scanning (Trivy, Bandit, Safety, tfsec)
- Rolling deployments with automatic rollback
- Post-deploy smoke tests
- Terraform plan comments on PRs

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ for the DevOps & SRE community
</p>
