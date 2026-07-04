<div align="center">

# 🧭 BandoPilot

### An agentic copilot that helps Italian businesses find public grants, check eligibility *with citations*, and draft their application — built on the Google Agent Development Kit.

**Capstone — 5-Day AI Agents: Intensive Vibe Coding Course (Google × Kaggle)**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google&logoColor=white)](https://adk.dev/)
[![Model](https://img.shields.io/badge/Model-gemini--2.5--flash-8E44AD)](https://ai.google.dev/)
[![MCP](https://img.shields.io/badge/Protocol-MCP-000000)](https://modelcontextprotocol.io/)
[![Cloud Run](https://img.shields.io/badge/Deployed-Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**🔗 [Live demo](https://bandopilot-530700297106.us-central1.run.app)** · **📄 [Capstone writeup](SUBMISSION.md)** · **🎬 [Video script](VIDEO_SCRIPT.md)**

</div>

---

## The problem

Every year Italian companies and freelancers leave public funding on the table. The
landscape of grants (*bandi*) — national, regional, agency-level — is fragmented, the
language is dense, and figuring out *whether you actually qualify* means reading legal
clauses. **BandoPilot** turns that into a conversation:

1. 🔎 **Finds** the grants relevant to a profile (sector, region, company size, spending goal)
2. ✅ **Checks eligibility** requirement-by-requirement, **citing the specific clause** (R1, R2, …)
3. ⏰ **Flags deadlines** (and warns when a grant has already closed)
4. ✍️ **Drafts** the descriptive section of the application

It is *not* an "AI that submits for you": it informs, verifies, and prepares — the human
keeps the signature and the send button. A deterministic guardrail refuses to submit,
sign, or pay on the user's behalf.

## Why it's interesting: **Agent = Model + Harness**

The model (`gemini-2.5-flash`) is ~10% of the value. The rest is the **Harness** — a
multi-agent system where knowledge is served over the **Model Context Protocol (MCP)**.

```
                 ┌─────────────────────────────┐
   user   ───▶   │        root_agent           │  orchestrator
                 │  (guardrails + observability)│
                 └──────┬───────────┬───────────┘
             AgentTool  │           │  AgentTool
               ┌────────▼──┐   ┌────▼──────────┐   ┌───────────────┐
               │ finder_   │   │ eligibility_  │   │ drafter_agent │
               │ agent     │   │ agent         │   │               │
               └────┬──────┘   └──────┬────────┘   └──────┬────────┘
              MCP    │        function │            function│
             (stdio) │          tool   │              tool  │
        ┌────────────▼───┐   ┌─────────▼─────────┐  ┌───────▼────────┐
        │  MCP server    │   │ verifica_         │  │ dettaglio_     │
        │  (grants corpus)│  │ eleggibilita()    │  │ bando()        │
        │  search / get  │   │ (deterministic)   │  │                │
        └────────────────┘   └───────────────────┘  └────────────────┘
```

| Harness component | How BandoPilot implements it |
|---|---|
| **Orchestration** | `root_agent` delegates Finder → EligibilityChecker → Drafter via `AgentTool`, staying in control and synthesizing the final answer |
| **Tools** | Deterministic ADK function tools + tools exposed over MCP |
| **MCP** | Our own `FastMCP` server (stdio) exposes the grants corpus through a standard handshake instead of a bespoke wrapper |
| **A2A** | Native ADK — the agent is served as an A2A service with an Agent Card at the well-known URI |
| **Guardrails** | `before_model_callback` deterministically blocks "submit / sign / pay" requests |
| **Observability** | `before_tool_callback` records every tool call into session state (used by the trajectory eval) + native Cloud Trace/Logging |
| **Context (static vs dynamic)** | Static rules in `AGENTS.md`; grants pulled **on-demand** via MCP to avoid *context rot* |

## 📊 Evaluation — the heart of the project

Systematic validation, not "it seems to work". Three levels:

| Eval | What it measures | Result |
|---|---|---|
| **Eligibility** (deterministic, 20 labeled cases) | Correctness of the eligibility engine | **100% accuracy**, macro P/R **100%** |
| **Retrieval** (deterministic, 10 labeled queries) | Relevance of grant search | **recall@k 100%**, hit-rate **100%** |
| **Trajectory** (LLM, ADK Runner) | Did the agent *use the verification tool*, *cite a clause*, and *surface the deadline*? | **score 1.00** on validated cases |
| **Tests** | `pytest tests/unit tests/integration` | **11 passed** |

```bash
uv run python tests/eval/domain_eval.py      # eligibility + retrieval precision/recall
uv run python tests/eval/trajectory_eval.py  # LLM trajectory eval
uv run pytest tests/unit tests/integration   # deterministic tests
```

> Why trajectory matters: a *correct* answer reached **without** verifying the requirements
> or citing the source is a trajectory failure — even if it looks right.

## 🚀 Quickstart

```bash
cd bandopilot
cp .env.example .env            # add your GOOGLE_API_KEY (Google AI Studio)
agents-cli install
agents-cli playground           # local chat UI (auto-reloads)
```

Try: *"Small ICT company in Lombardy, €800k revenue, 3 years old — am I eligible for
voucher-digitalizzazione-lombardia?"* (the agent replies in Italian, its target audience).

## 🧱 Tech stack

- **Google Agent Development Kit (ADK)** — multi-agent orchestration, A2A, eval framework
- **Gemini 2.5 Flash** — reasoning model (swappable via `BANDOPILOT_MODEL`)
- **Model Context Protocol (MCP)** — `FastMCP` server serving the grants corpus
- **FastAPI + Cloud Run** — serverless, scale-to-zero deployment
- **Secret Manager** — API key never stored in the image
- **uv** — dependency and environment management

## 📁 Project structure

```
bandopilot/
├── AGENTS.md                 # Agent contract (persona + golden rules)
├── app/
│   ├── agent.py              # Orchestrator + Finder/Eligibility/Drafter + guardrails
│   ├── bandi_data.py         # Deterministic domain logic (search / eligibility / deadline)
│   ├── tools.py              # ADK function tools
│   ├── mcp_server.py         # MCP server over the grants corpus
│   ├── guardrails.py         # Forbidden-action block + tool tracing
│   └── data/bandi.json       # Curated demo corpus (12 grants)
├── tests/
│   ├── unit/ integration/    # pytest
│   └── eval/                 # domain_eval, trajectory_eval, labeled datasets
└── deployment/terraform/     # Cloud Run infra
```

## ⚠️ Honest limitations

- **Demo corpus**: 12 realistic but simplified grants — *not* an official source. In
  production the MCP corpus would be fed by real open data (incentivi.gov.it, regional
  portals, EU Funding & Tenders).
- **"Manual" requirements** (e.g. female-led ownership, applicant age) are correctly marked
  `da_verificare` instead of being guessed.
- The public demo is backed by a **budget-capped API key**; total spend is bounded.

## 📜 License

[MIT](LICENSE) © Gaia Cecchi
