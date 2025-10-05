# AI Requirements Management Platform

This project provides a FastAPI backend that orchestrates LLM-powered agents to intake expectations, derive requirements, manage change requests, and query the system via natural language. It uses SQLAlchemy for persistence, OpenAI chat completions for reasoning agents, and includes an automated workflow test suite.

## Prerequisites

- Python 3.11+
- An OpenAI API key with access to the configured chat-completions model (default: `gpt-4o-mini`).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

The application reads the following environment variables:

- `OPENAI_API_KEY` – **required** for production use; the service refuses to start without it.
- `OPENAI_MODEL` – optional override for the chat-completions model name.
- `OPENAI_BASE_URL` – optional base URL if you proxy requests through a compatible endpoint.

For local testing without hitting the real API, the workflow tests inject a deterministic fake LLM, so no API key is needed when running `pytest`.

## Database

By default the service persists data to `app.db` (SQLite) in the project root. The schema is created automatically on startup.

To reset the database during development simply remove `app.db`:

```bash
rm -f app.db
```

## Running the API locally

Use Uvicorn to run the FastAPI application:

```bash
export OPENAI_API_KEY="your_api_key"
uvicorn main:app --reload
```

The OpenAPI documentation is available at `http://127.0.0.1:8000/docs` once the server is running. All endpoints are namespaced under `/api`.

## Running Tests

Execute the automated test suite to validate the workflow orchestration end-to-end:

```bash
pytest -q
```

The tests stub the LLM calls, so they run deterministically and do not require network access.

## Linting and Formatting

The project does not yet include dedicated lint/format tooling. Feel free to integrate tools such as Ruff or Black following your team's conventions.
