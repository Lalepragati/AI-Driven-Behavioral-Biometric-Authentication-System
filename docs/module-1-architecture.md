# Module 1 Architecture

Module 1 implements the behavioral biometric authentication slice for the hospital ecosystem.

## Flow

1. A user registers with a hashed password.
2. The browser captures keystroke dynamics during login.
3. The backend extracts dwell, flight, rhythm, entropy, and error features.
4. A per-user local model scores the session.
5. The risk engine converts the anomaly signal into a 0-100 risk score.
6. Ollama explains the security decision in plain language.
7. The event is logged to Google Sheets or the offline spool.

## Modules

- `auth`: registration, login, session decisions
- `behavior`: keystroke capture, feature extraction, behavioral summaries
- `ml_engine`: local model training and inference
- `risk_engine`: weighted risk decisions
- `sheets_integration`: operational logging and offline fallback
- `services`: shared repository, container, and explanation services

## Data handling

- Passwords are hashed with bcrypt.
- Behavioral events are stored locally and can be mirrored to Google Sheets.
- Ollama is used only for explanations, not for the security decision itself.
