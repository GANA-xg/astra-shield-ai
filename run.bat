@echo off

start cmd /k "cd /d backend && call .venv\Scripts\activate && python -m uvicorn api.main:app --reload"

start cmd /k "cd /d frontend\citizen-app && npm run dev"