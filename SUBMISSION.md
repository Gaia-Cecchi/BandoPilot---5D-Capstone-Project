# BandoPilot — Capstone Writeup

> 5-Day AI Agents: Intensive Vibe Coding Course (Google × Kaggle) — open-theme track.

- **Submission track:** Agents for Business — BandoPilot helps Italian SMEs and
  professionals find, qualify for, and apply to public funding, so it's built to
  support a business function, not a personal/lifestyle or general-good use case.
- **App URL (Cloud Run, public):** https://bandopilot-530700297106.us-central1.run.app
  (the root redirects to the **chat UI** at `/dev-ui/`; no password required)
- **Demo video:** https://youtu.be/AOttBc413wY
- **Code:** https://github.com/Gaia-Cecchi/BandoPilot---5D-Capstone-Project

> **How to try the demo:** open the App URL in a browser, select the `app` agent, and
> describe your profile (e.g. *"Small ICT company in Lombardy, €800k revenue, 3 years old
> — am I eligible for voucher-digitalizzazione-lombardia?"*). The service is scale-to-zero
> (first request ~30s cold start) and protected by a spending cap on the API key.

---

## 1. The problem

Every year Italian companies and freelancers miss public funding because the landscape of
grants (*bandi*) — national, regional, agency-level — is fragmented, the language is dense,
and understanding *whether you actually qualify* means reading legal clauses. BandoPilot is
an agent that:

1. **finds** the grants relevant to a profile (sector, region, size, spending goal);
2. **checks eligibility** requirement by requirement, **citing the specific clause**;
3. **flags deadlines** (and whether a grant has already closed);
4. **drafts** the descriptive section of the application.

It is not an "AI that files applications for you": it informs, verifies, and prepares,
leaving the signature and submission to the human.

## 2. Architecture: Agent = Model + Harness

The model (`gemini-2.5-flash`) is ~10%. The value is the **Harness**: an orchestrated
multi-agent system with knowledge served over **MCP**.

**`root_agent`** (orchestrator — guardrails + observability) receives the user request and
delegates to three specialists via `AgentTool`:

| Sub-agent | Talks to | Via |
|---|---|---|
| `finder_agent` | **MCP server** → grants corpus (`search` / `get`) | MCP (stdio) |
| `eligibility_agent` | `verifica_eleggibilita()` — deterministic eligibility check | function tool |
| `drafter_agent` | `dettaglio_bando()` — grant detail lookup | function tool |

The orchestrator stays in control throughout and synthesizes the final answer from the
three specialists' outputs.

### The 6 context pillars → where they live in the code

| Pillar | Implementation |
|---|---|
| **Instructions** | `bandopilot/AGENTS.md` + each agent's `instruction` in `app/agent.py` |
| **Knowledge** | curated corpus `app/data/bandi.json`, served over **MCP** (`app/mcp_server.py`) |
| **Memory** | `session.state` (user profile and `tool_trace` across turns) |
| **Examples** | flow patterns embedded in the orchestrator instructions |
| **Tools** | `app/tools.py` (eligibility check, grant detail) + MCP tools (search, get) |
| **Guardrails** | `app/guardrails.py` (blocks binding actions) |

### Harness components

- **Orchestration** — `root_agent` delegates Finder → EligibilityChecker → Drafter via
  `AgentTool` (parent stays in control and synthesizes the answer).
- **Tools** — deterministic ADK functions + tools exposed over MCP.
- **MCP** — our own server (`FastMCP`, stdio transport) exposes the corpus through a
  standard handshake instead of a bespoke wrapper. The Finder consumes it via `McpToolset`.
- **A2A** — native ADK: the agent is served as an A2A service with an Agent Card at the
  well-known URI (verified HTTP 200 in production).
- **Guardrails** — a `before_model_callback` that **deterministically** refuses requests to
  submit / sign / pay on the user's behalf, without calling any tool.
- **Observability** — a `before_tool_callback` records every tool call into `tool_trace`
  (also used by the trajectory eval) + native Cloud Trace/Logging.
- **Sandbox** — eligibility logic runs as an isolated deterministic function; the runtime is
  isolated on Cloud Run.

## 3. Context engineering: static vs dynamic

- **Static** (`AGENTS.md`, instructions): immutable rules and persona.
- **Dynamic** (MCP): grants are fetched **on-demand** from the MCP server, not pasted into
  the prompt — avoiding *context rot* and keeping the model focused. Only relevant grants
  enter the context.

## 4. Evaluations (the core of the project)

Systematic validation, not "it seems to work". Three levels:

### 4.1 Eligibility — correctness (deterministic)
`tests/eval/domain_eval.py` over 20 labeled `(profile, grant) → outcome` cases.

| Metric | Value |
|---|---|
| Accuracy | **100%** |
| Macro precision | **100%** |
| Macro recall | **100%** |

(3 classes: `eleggibile` / `non_eleggibile` / `da_verificare`.)

### 4.2 Retrieval — relevance (deterministic)
10 labeled queries with the grants that must appear in the top-k.

| Metric | Value |
|---|---|
| mean recall@k | **100%** |
| hit-rate@k | **100%** |

### 4.3 Trajectory — the path, not just the output (LLM)
`tests/eval/trajectory_eval.py` runs the real agent via the ADK Runner and checks that, for
an eligibility question, the agent **(a)** actually uses the verification tool, **(b)** cites
a clause code (R1, R2, …), and **(c)** surfaces the deadline. Observed result: **score 1.00**
on validated cases. The same logic is available as a **local custom metric** for the ADK eval
flow in `tests/eval/eval_config.yaml`.

> Why it matters: a correct answer reached without verifying the requirements or citing the
> source is a trajectory failure, even if it "looks right".

### 4.4 Deterministic tests
`pytest tests/unit tests/integration` → **11 passed, 3 skipped** (the tests that call the
model are opt-in via `RUN_LLM_TESTS=1` to preserve quota).

## 5. Security and key management

- API key never committed (`.env` is gitignored; template in `.env.example`).
- Two env-driven auth modes: AI Studio (dev) and Vertex (Cloud Run).
- On Cloud Run the key is injected from **Secret Manager**, never baked into the image.
- Deterministic guardrail against binding actions (submit / pay / sign).
- Systematic disclaimer: the corpus is a demo; every outcome points back to the official source.

## 6. Deployment

Prototype-first with `agents-cli`. **Deployed and live on Cloud Run** (isolated container,
scale-to-zero, `min-instances 0` for ~0 idle cost). The `GOOGLE_API_KEY` is injected from
**Secret Manager**. Public service (`allUsers` → `run.invoker`) with a chat UI at `/dev-ui/`
and an A2A Agent Card at `/a2a/app/.well-known/agent-card.json` (verified HTTP 200).
Tested end-to-end in production over A2A.

```bash
agents-cli scaffold enhance . --deployment-target cloud_run
agents-cli deploy --secrets GOOGLE_API_KEY=bandopilot-api-key \
  --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=False --min-instances 0
```

## 7. Limitations and intellectual honesty

- **Demo corpus**: 12 realistic but simplified grants; not an official source. In production
  the MCP corpus would be fed by real open data (incentivi.gov.it, regional portals, EU
  Funding & Tenders).
- **Free-tier quota / cost**: the multi-agent makes several model calls per query; a budget
  cap on the API key bounds total spend.
- **"Manual" requirements** (e.g. female-led ownership, applicant age) cannot be machine-checked
  and are correctly marked `da_verificare` rather than guessed.

## 8. How to run

```bash
cd bandopilot
cp .env.example .env            # add GOOGLE_API_KEY (AI Studio)
agents-cli install
agents-cli playground           # local UI
uv run python tests/eval/domain_eval.py       # deterministic evals
uv run python tests/eval/trajectory_eval.py   # trajectory eval (LLM)
uv run pytest tests/unit tests/integration    # tests
```
