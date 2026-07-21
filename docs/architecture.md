# Astra Shield AI Architecture

## Overview

Astra Shield AI follows a modular, service-oriented architecture. The backend is built with FastAPI, using SQLite for persistence (PostgreSQL for production), Neo4j for graph relationships, and multiple AI agents for specialized tasks.

---

# High-Level Architecture

```
                    Internet
                         │
                    HTTPS / TLS
                         │
                  ┌─────────────────┐
                  │     FastAPI      │
                  │  API Gateway     │
                  └─────────────────┘
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
 API Key Auth      Business Logic     AI Agents
 (sensitive)           │                  │
      └──────────────┬─┴──────────────────┘
                     │
         ┌───────────┼────────────┐
         │           │            │
     SQLite       Neo4j       Gemini API
   (metadata)   (graph)       (LLM)
         │           │
         └───────────┘
```

---

# AI Agent Architecture

```
User Request
     │
     ▼
Agent Router
     │
     ├── Citizen Agent ──────► Gemini + keyword fallback
     ├── Scam Agent ─────────► Gemini + rule-based patterns
     ├── Phishing Agent ─────► XGBoost ML model
     ├── Currency Agent ─────► EfficientNetB3 CNN
     └── Fraud Graph Agent ──► Neo4j + risk engine
```

---

# Data Flow

## Phishing Detection
```
URL → Feature Extraction (27 features) → XGBoost Model → Risk Score + Explanation
```

## Scam Detection
```
Transcript → Rule-based Patterns + Gemini LLM → Classification + Recommendations
```

## Fraud Analysis
```
Account → Neo4j Query → Signal Collection → Risk Engine → Risk Score + Breakdown
```

## Evidence Export
```
Account → Subgraph Extraction → JSON Assembly → PDF Rendering → Integrity Hash
```

---

# Database Schema

## SQLite (Primary)
- `analyses` - Phishing analysis history
- `evidence_logs` - Evidence export audit trail

## Neo4j (Graph)
- `:Person` - Individual entities
- `:Account` - Bank accounts
- `:Device` - Devices (phones, laptops)
- `[:OWNS]` - Person → Account relationships
- `[:USED]` - Person → Device relationships
- `[:TRANSFERRED]` - Account → Account transactions

---

# Security Layers

1. **API Key Authentication** - For sensitive fraud endpoints
2. **CORS Configuration** - Configurable origins
3. **Request Validation** - Pydantic models
4. **Integrity Hashing** - SHA-256 for evidence packages
5. **Audit Logging** - Evidence generation tracking

---

# External Integrations

- **Google Gemini** - LLM for scam detection and citizen advice
- **Neo4j** - Graph database for fraud networks
- **OpenPhish** - Phishing URL feed (cached)
- **XGBoost** - ML model for phishing classification
- **TensorFlow/EfficientNet** - CNN for currency detection

---

# Design Principles

- Modular AI agents with clear responsibilities
- Graceful degradation (Gemini unavailable → keyword fallback)
- Evidence integrity for legal admissibility
- API-first design with OpenAPI docs
- Separation of ML training and inference
