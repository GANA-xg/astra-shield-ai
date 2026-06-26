Development Guidelines

Purpose

This document defines the development standards for Astra Shield AI. Every contribution must follow these guidelines to ensure consistency, maintainability, and production readiness.

⸻

Project Architecture

The project follows a layered architecture.

API
↓
Service
↓
Repository
↓
Database

AI-related functionality is implemented through dedicated AI agents.

⸻

Folder Responsibilities

api/

* Define API routes only.
* Perform request validation.
* Call service layer.
* Do not contain business logic.

services/

* Implement business logic.
* Coordinate repositories and AI agents.
* Return structured results.

repositories/

* Handle all database interactions.
* Do not contain business logic.

models/

* SQLAlchemy ORM models.

schemas/

* Pydantic request and response models.

agents/

* AI agent implementations.
* Each agent should have a single responsibility.

db/

* Database configuration.
* Session management.
* Migrations.

middleware/

* Authentication.
* Logging.
* Request ID.
* Rate limiting.

core/

* Configuration.
* Security.
* Exception handling.
* Logging setup.

utils/

* Shared helper functions only.

⸻

Coding Standards

* Follow PEP 8.
* Use type hints for all functions.
* Keep functions small and focused.
* Avoid duplicated code.
* Prefer composition over inheritance.
* Write self-explanatory code.

⸻

Naming Conventions

Files

snake_case.py

Examples:

user_service.py
fraud_graph_agent.py
currency_detector.py

⸻

Classes

PascalCase

Examples:

UserService
FraudGraphAgent
CurrencyDetector

⸻

Functions

snake_case

Examples:

create_user()
detect_scam()
verify_currency()

⸻

Variables

snake_case

Examples:

user_id
risk_score
confidence_score

⸻

Constants

UPPER_CASE

Examples:

MAX_UPLOAD_SIZE
JWT_EXPIRE_MINUTES

⸻

API Standards

Success Response

{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}

⸻

Error Response

{
  "success": false,
  "message": "Validation failed.",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email address."
    }
  ]
}

⸻

Logging Rules

Log:

* Incoming requests
* Response time
* Errors
* Authentication events
* AI inference metadata
* Background jobs

Never log:

* Passwords
* Tokens
* OTPs
* API keys
* Sensitive personal information

⸻

Git Workflow

Main Branches

main
develop

Feature branches:

feature/<feature-name>

Bug fixes:

fix/<bug-name>

Hotfixes:

hotfix/<issue-name>

⸻

Commit Convention

feat:
fix:
docs:
refactor:
test:
perf:
ci:
chore:

Example:

feat: add phishing detection endpoint

⸻

Pull Request Checklist

Before opening a pull request:

* Code builds successfully.
* Tests pass.
* No linting errors.
* Documentation updated.
* No secrets committed.
* Code reviewed.
* API changes documented.

⸻

Security Guidelines

* Validate all user input.
* Use parameterized database queries.
* Hash passwords using Argon2.
* Never trust client-side validation.
* Enforce role-based authorization.
* Store secrets in environment variables.
* Sanitize uploaded files.

⸻

Testing Guidelines

Every new feature should include:

* Unit tests
* Integration tests (where applicable)
* API endpoint tests

Target minimum test coverage:

* 80%

⸻

Documentation Rules

Every public function should include:

* Purpose
* Parameters
* Return value
* Raised exceptions (if any)

Complex features should be documented in the docs/ directory.

⸻

General Principles

* Keep modules small and focused.
* Prefer readability over cleverness.
* Follow the Single Responsibility Principle.
* Avoid premature optimization.
* Write code for maintainability.
* Build production-ready features from the start.