# HISTORY — BandoPilot

Storico delle decisioni e delle fasi del capstone. Voce piu recente in alto.

---

## 2026-07-04 — Setup iniziale

**Decisioni prese:**
- Capstone del corso Kaggle/Google "5-Day AI Agents: Intensive Vibe Coding", track **a tema libero**.
- Idea scelta: **BandoPilot** — agente che trova bandi pubblici italiani, verifica eleggibilita (citando la clausola), segnala scadenze, imbastisce bozza domanda.
- Architettura multi-agente: Orchestrator -> Finder -> EligibilityChecker -> Drafter.
- Stack: **ADK (Google Agent Development Kit)**, Python. Motivo: eval framework, MCP e multi-agente/A2A nativi.
- Git **solo locale** (niente GitHub / push).
- **Deadline: 6 luglio 2026** -> scope MVP strettissimo.

**Fatto:**
- `git init` locale (branch `main`, user Gaia Cecchi).
- Scaffold ADK con `agents-cli scaffold create bandopilot --agent adk --prototype --region us-central1 --agent-guidance-filename AGENTS.md`.
  - Genera agente ReAct di esempio (`get_weather`, `get_current_time`), modello `gemini-flash-latest`, A2A nativo (`is_a2a: true`), deployment target `none` (prototype).
- Riscritto `agent_base/AGENT_INSTRUCTIONS.md` per il progetto BandoPilot + workflow git locale.
- Toolchain verificata: Python 3.12, uv 0.10.12, agents-cli 0.6.1, gcloud 575.

**Prossimi passi:**
1. Corpus curato `bandi.json` (~15 bandi realistici).
2. Tools reali (`search_bandi`, `get_bando_details`, `check_eligibility`, `draft_section`) al posto dei placeholder meteo.
3. Server MCP che espone il corpus.
4. Sub-agenti Finder/EligibilityChecker/Drafter + guardrails.
5. Suite di Evals (eligibility, retrieval, trajectory).
6. `scaffold enhance` per Cloud Run + deploy.
7. Video + writeup Kaggle.

**Bug noti / rischi:**
- Lo scaffold usa Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=True` + `google.auth.default()`): per lo sviluppo locale senza progetto GCP conviene valutare la modalita API key (AI Studio). Da decidere in fase di build.
- agents-cli 0.6.1: disponibile update a 1.0.0 (non applicato per stabilita durante il crunch).
- Deadline ambigua nelle fonti web (30 giu vs 6 lug): confermata 6 lug dall'utente, da riverificare sulla pagina Kaggle loggata.
