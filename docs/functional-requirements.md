# Functional Requirements

## Overview

Astra Shield AI provides AI-powered tools for detecting cyber fraud, phishing, fake currency, and suspicious activities while enabling citizens, investigators, and administrators to interact through dedicated interfaces.

---

# Citizen Features

## Authentication
- User registration
- Secure login
- Password reset
- JWT authentication
- Profile management

---

## Dashboard
- View recent analyses
- View submitted reports
- AI safety recommendations
- Notification center

---

## Scam Detection
Users can submit:

- SMS
- Email
- WhatsApp message
- Social media message
- Screenshot
- Document

The system should:
- Detect scam indicators
- Explain why it is suspicious
- Provide a confidence score
- Recommend next steps

---

## Phishing Detection

Users can submit:

- URL
- Website screenshot
- Email content

The system should:

- Detect phishing indicators
- Check domain reputation
- Analyze suspicious content
- Generate a risk score

---

## Fake Currency Detection

Users can upload images of currency notes.

The system should:

- Detect denomination
- Verify authenticity
- Highlight suspicious regions
- Return confidence score

---

## Cybercrime Reporting

Users can:

- Create a report
- Attach evidence
- Track report status
- View report history

---

## AI Assistant

The assistant should:

- Answer cybersecurity questions
- Explain scam techniques
- Guide users through reporting
- Provide prevention tips

---

# Investigator Features

## Case Dashboard

Investigators can:

- View assigned cases
- Search reports
- Update case status
- Add investigation notes

---

## Fraud Graph

Investigators can visualize:

- Accounts
- Phone numbers
- Email addresses
- Devices
- Wallet addresses
- IP addresses

Relationships between entities should be displayed as an interactive graph.

---

## Evidence Management

Investigators can:

- View uploaded evidence
- Organize files
- Add comments
- Export evidence

---

## AI Investigation Assistant

The assistant should:

- Summarize reports
- Identify fraud patterns
- Recommend related cases
- Generate investigation insights

---

# Administrator Features

Administrators can:

- Manage users
- Manage investigators
- Configure AI models
- Monitor system health
- View analytics
- Review logs
- Manage permissions

---

# AI Agent Features

## Citizen Agent
- General cybersecurity guidance

## Scam Detection Agent
- Scam classification
- Risk scoring

## Phishing Agent
- URL analysis
- Domain inspection

## Currency Agent
- Fake currency verification

## Fraud Graph Agent
- Relationship discovery
- Entity linking

---

# System Features

- File uploads
- Image processing
- Background jobs
- Audit logging
- Notifications
- API authentication
- Rate limiting
- Health monitoring