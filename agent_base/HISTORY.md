# HISTORY — BandoPilot

Build log and key decisions. Most recent on top.

---

## 2026-07-04 — Public repo prep + English docs
- Model: `gemini-2.5-flash-lite` tested but too shy about tool use (empty/over-cautious even
  with a thinking budget) → kept **`gemini-2.5-flash`** as the reliable default. Model and an
  optional thinking budget are env-overridable (`BANDOPILOT_MODEL`, `BANDOPILOT_THINKING`).
- All public docs rewritten in **English**: root `README.md` (showcase), `SUBMISSION.md`
  (writeup), `VIDEO_SCRIPT.md` (shot-by-shot), `bandopilot/AGENTS.md` + `README.md`, and this
  `agent_base` set. Added MIT `LICENSE`.
- `kaggle-instructions/` removed from tracking (local-only, gitignored). Secret audit: clean,
  no keys tracked. `.gitignore` hardened for a public repo.
- Prepared for GitHub push (author: Gaia Cecchi only — no AI co-author).

## 2026-07-04 — Cloud Run deploy (live, public)
- GCP project `gen-lang-client-0803727006`; enabled run/cloudbuild/secretmanager/artifactregistry.
- API key stored in **Secret Manager** (`bandopilot-api-key`); `secretAccessor` to the runtime SA.
- Deployed to Cloud Run: `https://bandopilot-530700297106.us-central1.run.app` — public
  (`allUsers` → `run.invoker`), scale-to-zero (`min 0`, `max 2`), key from Secret Manager.
- Verified live: A2A Agent Card HTTP 200; chat UI at `/dev-ui/`; end-to-end query over A2A OK.
- Official requirements confirmed (writeup + video + rationale + code link); only the video
  remains (user). MCP/evals/deploy exceed the minimum for a strong submission.

## 2026-07-04 — Eval suite + tests
- Deterministic evals (`tests/eval/domain_eval.py`, no model calls): **eligibility 100%
  accuracy**, **retrieval recall@k 100%**. Gate at 90%.
- LLM **trajectory eval** (`tests/eval/trajectory_eval.py`, ADK Runner): checks tool use +
  clause citation + deadline. Validated at score 1.00. Local custom metric in `eval_config.yaml`.
- Unit tests (`tests/unit/test_domain.py`, 9). LLM tests opt-in via `RUN_LLM_TESTS=1`.
  `pytest`: 11 passed. Fixed local FastAPI boot when no GCP project is present.

## 2026-07-04 — Multi-agent system
- `app/mcp_server.py`: MCP server (FastMCP, stdio) exposing `search_bandi` / `get_bando`.
- `app/tools.py`: ADK function tools (`verifica_eleggibilita`, `dettaglio_bando`).
- `app/guardrails.py`: forbidden-action block (before_model_callback) + tool tracing.
- `app/agent.py`: Finder (MCP) / Eligibility / Drafter orchestrated by `root_agent` via
  `AgentTool`. AI Studio auth via `.env`. Tested end-to-end.

## 2026-07-04 — Foundation
- Idea: BandoPilot (open-theme track). Stack: ADK, Python. Git local + (later) GitHub.
- Scaffolded with `agents-cli scaffold create ... --agent adk --agent-guidance-filename AGENTS.md`.
- Curated corpus `app/data/bandi.json` (12 grants) + deterministic domain logic
  (`app/bandi_data.py`: search, eligibility with clause citations, deadline status).
