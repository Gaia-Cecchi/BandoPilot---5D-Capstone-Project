# AGENT INSTRUCTIONS — BandoPilot (Kaggle AI Agents Capstone)

> For any coding agent working on this repository.
> **Always read this file before starting any task.** Update it when you find new best
> practices or corrections.

---

## 0. What this project is

**BandoPilot** is the capstone for the *5-Day AI Agents: Intensive Vibe Coding* course
(Google × Kaggle), open-theme track.

It is a **multi-agent system in ADK** (Google Agent Development Kit, Python) that:
1. **finds** Italian public grants relevant to a profile;
2. **checks eligibility** requirement by requirement, **citing the clause**;
3. **flags deadlines**;
4. **drafts** the descriptive section of the application.

Architecture: orchestrator (`root_agent`) → `finder_agent` (grants via MCP) →
`eligibility_agent` → `drafter_agent`. The badge value is in the **rigor of the harness and
the evals**, not the UI.

## 1. Capstone requirements (checklist)

- [x] **AGENTS.md** (agent contract) — `bandopilot/AGENTS.md`.
- [x] Explicit **harness**: tools, sandbox, guardrails, observability, orchestration.
- [x] At least one **MCP server** (`app/mcp_server.py`).
- [x] **A2A** interaction — native to ADK.
- [x] Systematic **eval** suite with labeled datasets + **trajectory eval**.
- [x] **Cloud Run** deployment with secure key management (Secret Manager).
- [x] Kaggle deliverables: **writeup** (`SUBMISSION.md`) + **video script** + code link.
- [ ] Record the **video** and submit on Kaggle (user).

Deadline: **6 July 2026**.

## 2. Workflow

### 2.1 Before starting
1. Read `agent_base/HISTORY.md` (log, decisions, known issues).
2. Read `agent_base/CODEBASE_STRUCTURE.md` (file map).
3. Read `bandopilot/README.md` and `bandopilot/AGENTS.md`.
4. Run `git status` and `git log --oneline -5`.

### 2.2 During work (from `bandopilot/`)
```bash
agents-cli install                              # install deps (uv)
agents-cli playground                           # local test UI
agents-cli run "prompt"                          # quick smoke test
uv run python tests/eval/domain_eval.py          # deterministic evals (no model calls)
uv run pytest tests/unit tests/integration       # tests
agents-cli lint                                  # code quality
```
- **Atomic commits** — one logical change per commit.
- If `pytest` or `lint` fail, fix before proceeding.

### 2.3 Ending a task
```bash
git add <files>
git commit -m "type: short message without apostrophes"
git push origin main
```
- ⚠️ **Never put Claude (or any AI) among the commit authors.** Author = Gaia Cecchi only.
  Do **not** add any `Co-Authored-By` trailer.
- ⚠️ **No apostrophes** in commit messages (they break bash heredoc).
- Update `HISTORY.md` and `CODEBASE_STRUCTURE.md`; update `README.md` if deps/commands/features changed.

## 3. Code rules (ADK / Python)

- **Only modify what the task requires.** Preserve surrounding code, config (especially the
  model), comments, formatting.
- **Never change the model** (`gemini-2.5-flash`) unless explicitly asked. Override via
  `BANDOPILOT_MODEL` env instead.
- **Do not hand-edit** the generated runtime/A2A infra (`app/fast_api_app.py`,
  `app/app_utils/*`, `Dockerfile`).
- ADK tool imports: import the tool instance, not the module.
- Run Python with `uv run`; add packages with `uv add`.
- Stop and fix the root cause if the same error appears 3+ times.
- **Model 404**: fix `GOOGLE_CLOUD_LOCATION` (e.g. `global`), not the model name.

## 4. Keys & security (public repo)

- **Never commit keys.** `.env` is gitignored; template in `.env.example`.
- Local dev: AI Studio (`GOOGLE_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI=False`).
- Cloud Run: key injected from **Secret Manager**.
- `kaggle-instructions/` is local-only (gitignored) — do not publish.

## 5. Inviolable constraints

- ✅ **Never** add Claude/AI as a commit author or `Co-Authored-By`.
- ✅ **Never** change the model without an explicit request.
- ✅ **Never** commit API keys.
- ✅ **Evals first** — they are the core of the badge; do not cut them.
- ✅ `pytest` + `lint` green before considering a task done.
- ✅ Always update `HISTORY.md` and `CODEBASE_STRUCTURE.md`.

---

*Last updated: 04/07/2026 — English rewrite; GitHub remote added (author: Gaia Cecchi only).*
