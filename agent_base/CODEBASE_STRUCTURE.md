# CODEBASE STRUCTURE — BandoPilot

Mappa aggiornata del repository. Aggiornare a ogni creazione/spostamento/rinomina di file.

```
capstoneproject_kagglecourse/
├── SUBMISSION.md                 # Writeup Kaggle (deliverable)
├── .gitignore
├── agent_base/                   # Documentazione per i coding agent
│   ├── AGENT_INSTRUCTIONS.md       # Regole di lavoro sul repo (leggere per primo)
│   ├── HISTORY.md                  # Storico decisioni e fasi
│   └── CODEBASE_STRUCTURE.md        # Questo file
├── kaggle-instructions/          # Report/linee guida del corso (contesto, non codice)
└── bandopilot/                   # Progetto ADK — l'agente
    ├── AGENTS.md                   # Contratto agente (deliverable capstone)
    ├── README.md
    ├── agents-cli-manifest.yaml    # Config CLI (deployment_target: cloud_run)
    ├── pyproject.toml / uv.lock
    ├── Dockerfile                  # Container Cloud Run (uvicorn app.fast_api_app)
    ├── .env / .env.example         # Auth (GOOGLE_API_KEY AI Studio) — .env NON committato
    ├── app/
    │   ├── agent.py                # root_agent + 3 sub-agenti + guardrails (PUNTO PRINCIPALE)
    │   ├── bandi_data.py           # Logica dominio deterministica (search/eligibility/deadline)
    │   ├── tools.py                # Function tool ADK (verifica_eleggibilita, dettaglio_bando)
    │   ├── mcp_server.py           # Server MCP (FastMCP stdio) sul corpus
    │   ├── guardrails.py           # blocca_azioni_vietate + traccia_tool_call
    │   ├── data/bandi.json         # Corpus curato (12 bandi)
    │   ├── fast_api_app.py         # Server FastAPI/A2A (generato; guard logging locale)
    │   └── app_utils/              # a2a, services, telemetry (generato)
    ├── deployment/terraform/       # Infra Cloud Run (single-project) — generato da enhance
    └── tests/
        ├── unit/test_domain.py     # Unit test deterministici (9)
        ├── integration/            # test_agent, test_server_e2e (LLM gate: RUN_LLM_TESTS=1)
        └── eval/
            ├── domain_eval.py      # Eval deterministiche: eligibility + retrieval
            ├── trajectory_eval.py  # Trajectory eval LLM (ADK Runner)
            ├── eval_config.yaml     # Metrica custom locale trajectory_eleggibilita
            ├── datasets/basic-dataset.json   # Dataset inferenza ADK (3 casi)
            └── labeled/            # Dataset etichettati (eligibility 20, retrieval 10)
```
