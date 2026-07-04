# HISTORY — BandoPilot

Storico delle decisioni e delle fasi del capstone. Voce piu recente in alto.

---

## 2026-07-04 — Modello economico, writeup, scaffolding Cloud Run

**Fatto:**
- Modello cambiato (richiesta esplicita utente) da `gemini-flash-latest` a **`gemini-2.5-flash`** (costo minore + bucket quota separato). Smoke test OK: orchestrazione buona, Finder+Eligibility anche in parallelo, esiti con citazione clausole.
- **`SUBMISSION.md`**: writeup Kaggle completo (problema, architettura Agent=Model+Harness, 6 pilastri, MCP, evals con numeri, guardrails, limiti). Segnaposto per URL Cloud Run e video.
- `agents-cli scaffold enhance . --deployment-target cloud_run`: aggiunta `deployment/terraform/single-project/`, Dockerfile Cloud Run (uvicorn su 8080), deps deploy. `uv.lock` rigenerato (build `uv sync --frozen` pronta). Nessun deploy eseguito.
- Piano utente: abilitare billing con cap ~3 EUR sulla chiave AI Studio per togliere il limite di quota.

**Da fare:** deploy Cloud Run vero (serve progetto GCP; scaffolding pronto), registrare il video, inserire URL nel writeup.

## 2026-07-04 — Suite di Evals + test + fix boot locale

**Fatto:**
- Eval deterministiche (no LLM, no GCP): `tests/eval/domain_eval.py` + dataset etichettati in `tests/eval/labeled/` (eligibility 20 casi, retrieval 10). Risultati: **eligibility accuracy 100% (macro P/R 100%)**, **retrieval recall@k 100% / hit-rate 100%**. Gate a 90%.
- Trajectory eval LLM: `tests/eval/trajectory_eval.py` via ADK Runner (solo API key). Verifica: tool di verifica usato + citazione clausola (R\\d) + scadenza menzionata. **2/3 casi score 1.00** prima del 429; harness reso resiliente al 429 (salta il caso e continua).
- Config ADK eval: `tests/eval/eval_config.yaml` con metrica **custom locale** `trajectory_eleggibilita` (in-process, niente GCP). Dataset inferenza ADK: `tests/eval/datasets/basic-dataset.json` (3 casi eleggibilita).
- Unit test deterministici: `tests/unit/test_domain.py` (9 casi). Test LLM (integration) gate-ati dietro `RUN_LLM_TESTS=1`. **pytest: 11 passed, 3 skipped.**
- Fix boot locale: `app/fast_api_app.py` ora tollera assenza di progetto GCP (Cloud Logging -> shim su logging standard in dev AI Studio). Su Cloud Run comportamento invariato.

**LIMITE IMPORTANTE — quota free-tier AI Studio:**
- `gemini-flash-latest` risolve a `gemini-3.5-flash`; free tier = **20 richieste/giorno**. Il multi-agente fa ~4-6 chiamate LLM per query -> ~3-4 query complete al giorno con la chiave gratuita.
- Impatta: ripetere le eval LLM, demo/video. Mitigazioni: attivare billing sulla chiave, oppure pianificare le run. Le eval deterministiche e i unit test NON consumano quota.

## 2026-07-04 — Agente multi-agente funzionante

**Fatto:**
- `app/mcp_server.py`: server MCP (FastMCP, stdio) che espone `search_bandi` e `get_bando` sul corpus.
- `app/tools.py`: function tool ADK `verifica_eleggibilita(bando_id, profilo)` e `dettaglio_bando(bando_id)`.
- `app/guardrails.py`: `blocca_azioni_vietate` (before_model_callback, blocca invio/pagamento/firma) e `traccia_tool_call` (before_tool_callback, tool_trace in stato = observability).
- `app/agent.py` riscritto: sub-agenti Finder (via MCP), EligibilityChecker, Drafter, orchestrati dal root_agent tramite AgentTool. Auth AI Studio via `.env` (`GOOGLE_GENAI_USE_VERTEXAI=False`).
- Dipendenze aggiunte: `mcp`, `python-dotenv`. `agents-cli install` OK.

**Testato end-to-end (`agents-cli run`, modello gemini-flash-latest):**
- Finder -> MCP search: rosa corretta (voucher Lombardia in cima per query digitalizzazione).
- Orchestratore -> eligibility_agent -> tool: esito eleggibile con citazione clausole R1/R2/R3, scadenza (103 gg, attivo), fonte ufficiale + disclaimer corpus.
- Guardrail: "invia la domanda e paga" -> rifiuto deterministico, nessun tool chiamato.

**Note/rischi:**
- Il chaining finder->eligibility in un solo turno con flash puo essere incostante (una run si e fermata al finder); rinforzata l'istruzione del root. Da coprire con eval.

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
