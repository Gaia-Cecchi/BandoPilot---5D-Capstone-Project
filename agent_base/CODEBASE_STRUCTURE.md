# CODEBASE STRUCTURE — BandoPilot

Up-to-date map of the repository. Update it whenever files are created/moved/renamed.

```
capstoneproject_kagglecourse/
├── README.md                     # Showcase README (project overview)
├── SUBMISSION.md                 # Kaggle capstone writeup
├── VIDEO_SCRIPT.md               # Shot-by-shot demo video script
├── LICENSE                       # MIT
├── .gitignore
├── agent_base/                   # Internal docs for coding agents
│   ├── AGENT_INSTRUCTIONS.md        # Working rules for this repo (read first)
│   ├── HISTORY.md                   # Build log / decisions
│   └── CODEBASE_STRUCTURE.md         # This file
└── bandopilot/                   # The ADK agent
    ├── AGENTS.md                   # Agent contract (persona + golden rules)
    ├── README.md                   # Developer guide
    ├── agents-cli-manifest.yaml    # CLI config (deployment_target: cloud_run)
    ├── pyproject.toml / uv.lock
    ├── Dockerfile                  # Cloud Run container (uvicorn app.fast_api_app)
    ├── .env / .env.example         # Auth (GOOGLE_API_KEY) — .env is NOT committed
    ├── app/
    │   ├── agent.py                # root_agent + 3 sub-agents + guardrails (main entry point)
    │   ├── bandi_data.py           # Deterministic domain logic (search/eligibility/deadline)
    │   ├── tools.py                # ADK function tools (verifica_eleggibilita, dettaglio_bando)
    │   ├── mcp_server.py           # MCP server (FastMCP stdio) over the corpus
    │   ├── guardrails.py           # blocca_azioni_vietate + traccia_tool_call
    │   ├── data/bandi.json         # Curated corpus (12 grants)
    │   ├── fast_api_app.py         # FastAPI/A2A server (generated; local logging guard)
    │   └── app_utils/              # a2a, services, telemetry (generated)
    ├── deployment/terraform/       # Cloud Run infra (single-project) — from `enhance`
    └── tests/
        ├── unit/test_domain.py     # Deterministic unit tests (9)
        ├── integration/            # test_agent, test_server_e2e (LLM gate: RUN_LLM_TESTS=1)
        └── eval/
            ├── domain_eval.py      # Deterministic evals: eligibility + retrieval
            ├── trajectory_eval.py  # LLM trajectory eval (ADK Runner)
            ├── eval_config.yaml     # Local custom metric: trajectory_eleggibilita
            ├── datasets/basic-dataset.json   # ADK inference dataset (3 cases)
            └── labeled/            # Labeled datasets (eligibility 20, retrieval 10)
```

> Note: `kaggle-instructions/` (course reference material) is kept locally and excluded from
> the public repo via `.gitignore`.
