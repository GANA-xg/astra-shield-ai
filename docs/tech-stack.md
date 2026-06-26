# Astra Shield AI Tech Stack

## Philosophy

The technology stack is selected to prioritize security, scalability, maintainability, developer productivity, and production readiness.

---

# Frontend

## Framework
- Next.js 15 (App Router)

## Language
- TypeScript

## Styling
- Tailwind CSS

## UI Components
- shadcn/ui

## Icons
- Lucide React

## State Management
- Zustand

## Data Fetching
- TanStack Query

## Forms
- React Hook Form
- Zod

## Charts
- Recharts

## Graph Visualization
- React Flow

---

# Backend

## Framework
- FastAPI

## Language
- Python 3.13+

## ASGI Server
- Uvicorn

## Validation
- Pydantic v2

## ORM
- SQLAlchemy 2.0

## Database Migrations
- Alembic

## Authentication
- JWT

## Password Hashing
- Argon2

---

# Database

## Primary Database
- PostgreSQL

## Cache
- Redis

## Vector Database
- Qdrant

---

# AI Stack

## LLM Framework
- LangGraph

## AI Framework
- LangChain

## Embedding Model
- BAAI/bge-small-en-v1.5 (MVP)

## OCR
- PaddleOCR

## Image Processing
- OpenCV

## ML Framework
- PyTorch

---

# AI Models

## Primary LLM
- Gemini 2.5 Flash

## Fallback LLM
- OpenAI GPT-5.5 (optional)

## Local Models (Future)
- Ollama

---

# Storage

## Object Storage
- MinIO (development)
- AWS S3 compatible (production)

---

# Background Processing

## Task Queue
- Celery

## Message Broker
- Redis

---

# API Documentation

- OpenAPI
- Swagger UI
- ReDoc

---

# Logging

- Structlog
- Python Logging

---

# Monitoring

## Metrics
- Prometheus

## Dashboards
- Grafana

## Error Tracking
- Sentry

---

# Testing

## Unit Tests
- Pytest

## API Testing
- HTTPX

## Coverage
- pytest-cov

---

# Code Quality

## Formatting
- Ruff

## Linting
- Ruff

## Type Checking
- MyPy

## Pre-Commit Hooks
- pre-commit

---

# DevOps

## Containerization
- Docker

## Local Development
- Docker Compose

## Reverse Proxy
- Nginx

## CI/CD
- GitHub Actions

---

# Deployment

## Backend
- Docker

## Frontend
- Vercel

## Database
- PostgreSQL

## Cache
- Redis

## Object Storage
- S3 Compatible Storage

---

# Secrets Management

- Environment Variables
- GitHub Secrets
- Docker Secrets (production)

---

# Version Control

## Git Workflow
- Feature Branch Workflow

## Branches

- main
- develop
- feature/*
- hotfix/*
- release/*

---

# Commit Convention

feat:
fix:
docs:
refactor:
test:
chore:
perf:
ci:

---

# Package Management

## Python
- uv

## Node.js
- npm