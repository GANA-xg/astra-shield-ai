# Functional Requirements

## Overview

Astra Shield AI provides AI-powered tools for detecting cyber fraud, phishing, fake currency, and suspicious activities while enabling citizens, investigators, and administrators to interact through dedicated interfaces.

**Implementation Status (Hackathon Prototype):**
- Core AI agents: Implemented
- Database persistence: SQLite (PostgreSQL for production)
- Authentication: API key-based for sensitive endpoints (dev mode: open)
- Background jobs: Synchronous processing (async for production)

---

# Citizen Features

## Scam Detection
Users can submit call transcripts or messages for analysis.

**Implemented:**
- Text transcript analysis via Gemini LLM + keyword detection
- Digital arrest scam pattern recognition (rule-based + LLM)
- Risk scoring with confidence levels
- Actionable recommendations
- Alert generation for critical patterns

**API:** `POST /scam/analyze`, `POST /scam/analyze-and-alert`

---

## Phishing Detection

Users can submit URLs for phishing analysis.

**Implemented:**
- ML-based URL classification (XGBoost, 27-feature pipeline)
- Domain reputation analysis
- Legitimacy scoring
- Top contributing factors explanation
- SMS phishing detection

**API:** `POST /api/phishing/analyze`, `POST /api/phishing/check-sms`

---

## Fake Currency Detection

Users can upload images of currency notes.

**Implemented:**
- CNN-based image classification (EfficientNetB3)
- Binary genuine/fake detection
- Visual feature extraction (sharpness, security thread)
- Grad-CAM heatmap visualization (optional)
- Denomination detection (requires retraining)

**API:** `POST /currency/predict`

---

## AI Safety Advisor

The citizen agent provides cybersecurity guidance.

**Implemented:**
- Gemini-powered conversational AI responses
- Keyword-based fallback when Gemini unavailable
- Category classification (OTP, UPI, KYC, phishing, etc.)
- Risk level assessment
- Indian-specific resources (Cyber Crime Portal, 1930 helpline)
- Conversation history support

**API:** `POST /citizen/advice`

---

# Investigator Features

## Fraud Graph Analysis

Investigators can visualize fraud networks.

**Implemented:**
- Neo4j graph database for entity relationships
- Accounts, persons, devices, transactions
- Fraud ring detection (circular, star, velocity patterns)
- Money flow tracing
- Shortest path between accounts
- Money mule identification
- Shared device detection

**API:** `GET /fraud/money-mules`, `GET /fraud/rings`, `GET /fraud/money-flow/{account}`, `GET /fraud/shortest-path/{source}/{target}`

---

## Risk Scoring

Investigators can assess account risk levels.

**Implemented:**
- Multi-signal risk engine (6 signal types)
- Money mule detection, fraud rings, velocity analysis
- Risk bands: LOW (<30), MEDIUM (30-60), HIGH (60-85), CRITICAL (>85)
- Detailed breakdown of risk factors
- Batch risk analysis for all accounts

**API:** `GET /fraud/risk/{account}`, `GET /fraud/risk/{account}/detailed`, `GET /fraud/risk-all`

---

## Court-Admissible Evidence Export

Investigators can generate evidence packages for legal proceedings.

**Implemented:**
- Subgraph extraction for target accounts
- Structured JSON evidence package
- PDF report with cover page, risk table, entities, relationships
- SHA-256 integrity hash for tamper detection
- Audit logging of evidence generation
- Case ID generation

**API:** `GET /fraud/evidence/{account}` (PDF), `GET /fraud/evidence/{account}/json`

---

# AI Agent Features

## Citizen Safety Agent
- Gemini-powered conversational responses
- Category classification (9 scam types)
- Risk level assessment
- Indian-specific safety guidance

## Scam Detection Agent
- Gemini-based scam classification
- Digital arrest pattern recognition (rule-based + LLM)
- Call metadata analysis
- Alert generation for critical patterns

## Phishing Detection Agent
- XGBoost ML model (27 features)
- URL, domain, and content analysis
- Feature importance explanation
- OpenPhish feed integration

## Currency Detection Agent
- EfficientNetB3 CNN model
- Visual feature extraction (sharpness, security thread)
- Grad-CAM visualization
- Denomination detection (requires retraining)

## Fraud Graph Agent
- Neo4j graph queries
- Multi-signal risk engine
- Fraud ring detection
- Court-admissible evidence export

---

# System Features

## Implemented
- FastAPI REST API
- SQLite database (PostgreSQL for production)
- API key authentication for sensitive endpoints
- CORS configuration
- Request ID tracking
- Structured logging
- Health monitoring endpoint
- File upload handling

## Production Scope (Future)
- Rate limiting
- Background job queue
- Real-time notifications
- Comprehensive audit logging

---

# Future Scope

## Authentication (Not Implemented)
The following authentication features are planned for production:

- User registration
- Secure login
- Password reset
- JWT authentication
- Profile management
- Role-based access control (RBAC)
- OAuth2 / social login
- Session management
