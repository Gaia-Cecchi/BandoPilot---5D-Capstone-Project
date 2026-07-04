# BandoPilot — ADK agent

Multi-agent copilot for Italian public grants, built on the Google Agent Development Kit.
For the project overview, architecture, and eval results see the [root README](../README.md)
and the [capstone writeup](../SUBMISSION.md). This file is the developer guide.

## Requirements

- **uv** — Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **agents-cli** — `uv tool install google-agents-cli`
- **Google Cloud SDK** — only needed for deployment

## Setup

```bash
cp .env.example .env      # add your GOOGLE_API_KEY from https://aistudio.google.com/apikey
agents-cli install        # install dependencies with uv
agents-cli playground     # local chat UI (auto-reloads on save)
```

## Commands

| Command | Description |
|---|---|
| `agents-cli playground` | Local chat UI |
| `agents-cli run "prompt"` | One-shot smoke test |
| `uv run python tests/eval/domain_eval.py` | Deterministic evals (eligibility + retrieval), no model calls |
| `uv run python tests/eval/trajectory_eval.py` | LLM trajectory eval via the ADK Runner |
| `uv run pytest tests/unit tests/integration` | Tests (LLM tests are opt-in: `RUN_LLM_TESTS=1`) |
| `agents-cli lint` | Code quality checks |

## Configuration (env)

| Variable | Purpose | Default |
|---|---|---|
| `GOOGLE_API_KEY` | AI Studio key (local dev) | — |
| `GOOGLE_GENAI_USE_VERTEXAI` | `False` = AI Studio, `True` = Vertex (Cloud Run) | `False` |
| `BANDOPILOT_MODEL` | Model override | `gemini-2.5-flash` |
| `BANDOPILOT_THINKING` | `1` enables a thinking budget | `0` |

## Project structure

```
app/
├── agent.py          # Orchestrator + Finder/Eligibility/Drafter sub-agents + guardrails
├── bandi_data.py     # Deterministic domain logic (search / eligibility / deadline)
├── tools.py          # ADK function tools (verifica_eleggibilita, dettaglio_bando)
├── mcp_server.py     # MCP server (FastMCP, stdio) exposing the grants corpus
├── guardrails.py     # Forbidden-action block + tool tracing
├── data/bandi.json   # Curated demo corpus (12 grants)
└── fast_api_app.py   # FastAPI / A2A server (generated)
tests/
├── unit/ integration/  # pytest
└── eval/               # domain_eval, trajectory_eval, eval_config, labeled datasets
deployment/terraform/   # Cloud Run infrastructure
```

## Deployment (Cloud Run)

```bash
gcloud config set project <YOUR_PROJECT_ID>
agents-cli deploy \
  --secrets GOOGLE_API_KEY=bandopilot-api-key \
  --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=False \
  --min-instances 0
```

The API key is injected from **Secret Manager**; `min-instances 0` keeps idle cost near zero.
Native telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.

## A2A

The agent is served as an A2A service. Inspect the Agent Card at
`/<host>/a2a/app/.well-known/agent-card.json` or use the
[A2A Inspector](https://github.com/a2aproject/a2a-inspector).
