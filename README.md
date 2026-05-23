# AI-Driven-Behavioral-Biometric-Authentication-System

Module 1 delivers the behavioral biometric authentication slice of the larger AI platform.

## What is included

- FastAPI backend for registration, login, behavioral assessment, anomaly scoring, and audit logging
- Keystroke dynamics capture flow for the browser
- Local machine learning pipeline for baseline training and anomaly detection
- Risk engine with allow, step-up, and block decisions
- Ollama explanation layer for human-readable security summaries
- Google Sheets adapter with offline-first local fallback
- Next.js dashboard for secure login capture and risk review

## Repository layout

- `backend/` FastAPI service and ML pipeline
- `frontend/` Next.js dashboard
- `docs/` Architecture and operational notes

## Module 1 goals

- Capture keystroke dynamics safely in the browser
- Train a per-user behavioral baseline locally
- Detect anomalous typing and compute a 0-100 risk score
- Explain the decision with Ollama when available
- Log security events to Google Sheets or the offline spool

## Run strategy

This workspace is scaffolded for local development. Install dependencies in `backend/` and `frontend/`, then start the API and dashboard separately.

