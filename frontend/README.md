# Requirements Control Tower Frontend

This package implements the MVP user interface for the requirements management system described in the technical specification and workflow plans located in `../docs`. The UI mirrors the Flowbite-Svelte admin dashboard layout and exposes the key workspaces (expectations triage, requirement studio, change control, NLQ search, metrics configuration and AI copilot).

## Tech stack
- [Svelte 4](https://svelte.dev/) powered by [Vite](https://vitejs.dev/)
- [Tailwind CSS 3](https://tailwindcss.com/) with the Flowbite design system (`flowbite-svelte` components)
- npm based toolchain (Node.js ≥ 18 recommended)

## Getting started
1. Install dependencies:
   ```bash
   npm install
   ```
2. Launch the development server with hot module reload:
   ```bash
   npm run dev -- --host 0.0.0.0 --port 5173
   ```
   The `--host` flag allows access from Docker/WSL environments. Open [http://localhost:5173](http://localhost:5173) in your browser.
3. Build the production bundle and preview it locally:
   ```bash
   npm run build
   npm run preview -- --host 0.0.0.0 --port 4173
   ```

## Project layout
```
frontend/
├── public/              # Static assets served as-is
├── src/
│   ├── App.svelte       # Main dashboard layout and screen logic
│   ├── app.css          # Tailwind entry file
│   ├── lib/data.js      # Mock data seeds that emulate backend payloads
│   └── main.js          # Svelte bootstrap
├── tailwind.config.cjs  # Tailwind + Flowbite presets
├── postcss.config.cjs   # PostCSS pipeline
└── vite.config.js       # Vite configuration
```

## Available screens
- **Workspace** – KPI cards, expectation triage, requirement list and change control board.
- **Intake wizard** – form for transcripts, impact scoring options, dynamic metric configuration and duplicate/conflict toggles.
- **Requirement Studio** – One-pager, user story, acceptance criteria and metrics tabs with readiness checklist.
- **Search & Filters** – natural language query canvas and recent result list.
- **Metrics Config** – catalogue of metric definitions with inline creation form.
- **Settings** – placeholders for authentication and AI provider switches.
- **AI Copilot panel** – persistent sidebar with conversation history and composer for backend-integrated responses.

## Next steps for backend integration
- Replace the mock data in `src/lib/data.js` with API calls to the FastAPI backend endpoints.
- Wire chat actions (`sendChatMessage`) to the orchestration endpoint and stream responses.
- Connect intake submissions to the extractor API and populate triage queues with server responses.
- Persist metric catalogue changes through REST mutations.

All styling and layout primitives follow the Flowbite-Svelte admin dashboard vocabulary, so additional modules (impact analysis, approval workflows, etc.) can be slotted into the existing sections without restructuring the app.
