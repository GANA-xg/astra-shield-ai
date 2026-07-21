# Astra Shield AI

## Vision

Build an AI-powered cybersecurity platform that helps citizens identify and report online scams, phishing attacks, fake currency, and financial fraud while assisting authorities with intelligent investigation tools.

---

## Problem Statement

Cyber fraud is increasing rapidly, yet most users struggle to recognize scams before becoming victims. Existing reporting systems are fragmented, slow, and reactive.

Astra Shield AI provides proactive AI-driven detection, guidance, and reporting in one platform.

---

## Target Users

### Citizens
- Scam detection (call transcripts, messages)
- Phishing URL analysis
- Fake currency verification
- Cybercrime reporting guidance
- AI-powered safety advisor

### Investigators
- Fraud graph visualization (Neo4j)
- Risk scoring for accounts
- Court-admissible evidence export
- Fraud ring detection
- Money flow tracing

### Administrators
- System health monitoring
- Agent performance tracking
- API usage analytics

---

## MVP Scope (Implemented)

### Core AI Agents
1. **Citizen Safety Agent** - Gemini-powered cybersecurity guidance
2. **Scam Detection Agent** - Transcript analysis with digital arrest detection
3. **Phishing Detection Agent** - ML-based URL classification (XGBoost)
4. **Currency Detection Agent** - CNN image classification (EfficientNetB3)
5. **Fraud Graph Agent** - Neo4j graph analysis with risk scoring

### Key Features
- Real-time scam pattern recognition
- Digital arrest scam detection (Indian-specific)
- Court-admissible evidence generation (PDF + JSON)
- Multi-signal fraud risk engine
- Grad-CAM visualization for explainability
- Indian-specific resources (Cyber Crime Portal, 1930 helpline)

### Technical Implementation
- FastAPI REST API
- SQLite + Neo4j databases
- API key authentication
- 34 passing tests
- Modular, extensible architecture

---

## Future Scope

- Voice scam detection (real-time call monitoring)
- Deepfake detection
- OCR document verification
- WhatsApp integration
- Mobile applications
- Multilingual support
- Government API integration (MHA, Cyber Crime Portal)
- JWT authentication with RBAC
- Background job queue
- Real-time notifications
