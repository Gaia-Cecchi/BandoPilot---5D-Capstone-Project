# CODEBASE STRUCTURE — BandoPilot

Mappa aggiornata del repository. Aggiornare a ogni creazione/spostamento/rinomina di file.

```
capstoneproject_kagglecourse/
├── agent_base/                   # Documentazione per i coding agent
│   ├── AGENT_INSTRUCTIONS.md       # Regole di lavoro sul repo (leggere per primo)
│   ├── HISTORY.md                  # Storico decisioni e fasi
│   └── CODEBASE_STRUCTURE.md        # Questo file
│
├── kaggle-instructions/          # Report/linee guida del corso (contesto, non codice)
│   ├── Rapporto Tecnico ...md
│   ├── Report Enciclopedico ...md
│   └── Report Tecnico e Guida Strategica ...md
│
└── bandopilot/                   # Progetto ADK — l'agente
    ├── AGENTS.md                   # Contratto agente (deliverable capstone)
    ├── README.md                   # Setup e comandi del progetto
    ├── agents-cli-manifest.yaml    # Config CLI (NON editare a mano)
    ├── pyproject.toml              # Dipendenze (google-adk, a2a-sdk, ...)
    ├── Dockerfile                  # Container (generato)
    ├── .gitignore
    ├── app/
    │   ├── __init__.py
    │   ├── agent.py                # root_agent + tools + model (PUNTO DI LAVORO PRINCIPALE)
    │   ├── fast_api_app.py         # Server FastAPI (generato, non toccare)
    │   └── app_utils/
    │       ├── a2a.py              # Superficie A2A (generato)
    │       ├── services.py         # Sessioni/servizi (generato)
    │       ├── telemetry.py        # Observability/tracing (generato)
    │       └── typing.py
    └── tests/
        ├── unit/test_dummy.py
        ├── integration/
        │   ├── test_agent.py
        │   └── test_server_e2e.py
        └── eval/
            ├── eval_config.yaml
            └── datasets/
                ├── basic-dataset.json   # placeholder (greeting/weather) -> da sostituire
                └── README.md
```

## Da creare (roadmap MVP)
- `bandopilot/app/data/bandi.json` — corpus curato dei bandi.
- `bandopilot/app/tools.py` — tool: search_bandi, get_bando_details, check_eligibility, draft_section.
- Server MCP per il corpus bandi.
- Sub-agenti Finder / EligibilityChecker / Drafter.
- Dataset eval: eligibility, retrieval, trajectory.
