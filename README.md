# Requirements Management Platform

This repository hosts the MVP implementation assets for the intelligent requirements control tower described in the planning documents under `docs/`. The initial drop includes:

- **Frontend (`frontend/`)** – a Svelte + Tailwind + Flowbite dashboard that implements the workspace, intake wizard, requirement studio, search, metrics configuration and AI copilot screens.
- **Backend scaffold (`main.py`)** – placeholder for the forthcoming FastAPI service layer.
- **Methodology & technical plans (`docs/`)** – architecture, workflow and system requirements driving the build.

## Local development

### Frontend UI
Follow the instructions in [`frontend/README.md`](frontend/README.md) to install dependencies, run the Vite dev server and produce a production build. The dev server exposes the SPA on `http://localhost:5173` and mirrors the Flowbite-Svelte admin layout referenced in the specifications.

### Backend placeholder
`main.py` currently only holds a stub entry point. FastAPI endpoints, data models and AI orchestrator bindings will be added in subsequent iterations according to the technical specification.

## Repository structure
```
requirements-management/
├── docs/                # Product vision, workflow and technical specification
├── frontend/            # Svelte/Tailwind Flowbite admin dashboard implementation
└── main.py              # Backend bootstrap placeholder
```

## Next steps
1. Flesh out the FastAPI backend following the entity model defined in `docs/ai_requirements_technical_spec.md`.
2. Replace the mock data used by the frontend (`src/lib/data.js`) with real REST integrations.
3. Containerize the stack (`docker-compose` with frontend, backend, Postgres/PGVector) for one-command local deployment.

The repository is structured so each component can evolve independently while staying aligned with the architecture and workflow baselines.
