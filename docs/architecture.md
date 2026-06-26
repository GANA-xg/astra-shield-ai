# Astra Shield AI Architecture

## Overview

Astra Shield AI follows a modular, service-oriented architecture. The backend is responsible for API orchestration, AI agent execution, authentication, data persistence, and communication with external services.

The architecture is designed to be scalable, secure, and production-ready.

---

# High-Level Architecture

```
                    Internet
                         │
                    HTTPS / TLS
                         │
                  Reverse Proxy
                    (Nginx)
                         │
                ┌─────────────────┐
                │     FastAPI      │
                │  API Gateway     │
                └─────────────────┘
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
 Authentication     Business Logic     AI Orchestrator
      │                  │                  │
      └──────────────┬───┴──────────────────┘
                     │
         ┌───────────┼────────────┐
         │           │            │
     PostgreSQL     Redis      Background Jobs
         │                        │
         └────────────┬───────────┘
                      │
             AI Agent Layer
                      │
   ┌────────┬────────┬────────┬────────┬────────┐
   │        │        │        │        │
Citizen  Scam   Phishing Currency Fraud Graph
 Agent    Agent    Agent     Agent      Agent
                      │
          External AI Models / APIs
```

---

# Request Flow

```
Client

↓

FastAPI Router

↓

Authentication Middleware

↓

Request Validation

↓

Service Layer

↓

AI Agent (if required)

↓

Database / Cache

↓

Response Formatter

↓

Client
```

---

# AI Agent Flow

```
User Request

↓

Agent Router

↓

Determine Required Agent

↓

Execute AI Model

↓

Confidence Scoring

↓

Explanation Generation

↓

Save Results

↓

Return Response
```

---

# Database Flow

```
API

↓

Service Layer

↓

Repository Layer

↓

PostgreSQL

↓

Return Data
```

---

# Vector Search Flow (Future)

```
Document Upload

↓

Chunking

↓

Embedding Generation

↓

Vector Database

↓

Semantic Search

↓

Relevant Chunks

↓

LLM Response
```

---

# File Processing Flow

```
File Upload

↓

Validation

↓

Virus Scan

↓

Temporary Storage

↓

AI Processing

↓

Permanent Storage

↓

Database Metadata
```

---

# Background Jobs

Used for:

- AI processing
- File processing
- Notifications
- Report generation
- Scheduled cleanup
- Analytics aggregation

---

# External Integrations

- LLM providers
- Threat intelligence APIs
- URL reputation services
- Email services
- Object storage
- Monitoring services

---

# Security Layers

1. HTTPS
2. JWT Authentication
3. RBAC Authorization
4. Request Validation
5. Rate Limiting
6. Secure File Handling
7. Audit Logging

---

# Design Principles

- Clean Architecture
- Separation of Concerns
- Stateless Services
- Dependency Injection
- Repository Pattern
- Service Layer Pattern
- Modular AI Agents
- API-First Design
