#!/bin/bash

concurrently \
"cd backend && source .venv/bin/activate && uvicorn api.main:app --reload" \
"cd frontend/citizen-app && npm run dev"