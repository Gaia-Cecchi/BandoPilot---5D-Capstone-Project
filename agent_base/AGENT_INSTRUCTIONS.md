# AGENT INSTRUCTIONS — BandoPilot (Capstone Kaggle AI Agents)

> **Per tutti i coding agent** (Claude, Gemini, Copilot, DeepSeek, etc.)
> che lavorano su questo repository.
>
> Leggi **SEMPRE** questo file prima di iniziare qualsiasi task.
> Aggiornalo se trovi nuove best practice o correzioni.

---

## 0. Cos'e questo progetto

**BandoPilot** e il capstone project per il corso Kaggle/Google *"5-Day AI Agents: Intensive Vibe Coding"* (track a tema libero).

E un **agente multi-agente in ADK** (Google Agent Development Kit, Python) che:
1. **Trova** bandi/finanziamenti pubblici italiani pertinenti a un profilo (settore, regione, dimensione, obiettivo di spesa).
2. **Verifica l'eleggibilita** citando sempre la clausola specifica del bando.
3. **Segnala le scadenze**.
4. **Imbastisce una bozza** della sezione descrittiva della domanda.

Architettura: Orchestrator -> `Finder` -> `EligibilityChecker` -> `Drafter`.

Il valore per il badge non sta nella UI, ma nel **rigore del Harness e delle Evals**.

---

## 1. Requisiti del capstone (checklist da soddisfare)

- [x] File **AGENTS.md** (contratto dell'agente) — in `bandopilot/AGENTS.md`.
- [ ] **Harness** esplicito: Tools, Sandbox, Guardrails, Observability, Orchestration.
- [ ] Almeno un **server MCP** (espone il corpus bandi: `search_bandi`, `get_bando`).
- [ ] Interazione **A2A** — gia integrata nativamente da ADK (`is_a2a: true`).
- [ ] Suite di **Evals** sistematica con dataset etichettati + **trajectory eval**.
- [ ] Deploy su **Cloud Run** con gestione sicura delle API key.
- [ ] Deliverable Kaggle: **writeup + video + rationale + link codice**.

Le 3 eval previste:
1. **Eligibility** precision/recall (~20 coppie `(profilo, bando)` etichettate).
2. **Retrieval** relevance@k (~15 query -> bandi attesi in top-k).
3. **Trajectory**: l'agente ha citato la fonte prima di asserire eleggibilita? ha controllato la scadenza?

**Deadline: 6 luglio 2026** -> scope MVP strettissimo. Se qualcosa salta, salta dal fondo della lista, MAI dalle Evals.

---

## 2. Workflow obbligatorio (IN ORDINE)

### 2.1 Prima di iniziare
1. **Leggi `agent_base/HISTORY.md`** — storico, decisioni, bug noti, fasi completate.
2. **Leggi `agent_base/CODEBASE_STRUCTURE.md`** — mappa aggiornata della struttura.
3. **Leggi `bandopilot/README.md`** e **`bandopilot/AGENTS.md`**.
4. **Fai `git status` e `git log --oneline -5`** per capire lo stato attuale.

### 2.2 Durante il lavoro
5. **Commit atomici** — un commit = una feature/fix/refactor. Non accumulare modifiche eterogenee.
6. **Loop di sviluppo ADK** (dalla dir `bandopilot/`):
   ```bash
   agents-cli install                              # installa deps con uv (una tantum / dopo add)
   agents-cli playground                           # test interattivo locale
   agents-cli eval generate && agents-cli eval grade   # loop di valutazione (fase principale)
   uv run pytest tests/unit tests/integration      # test pre-deploy
   agents-cli lint                                 # qualita del codice
   ```
   Se `pytest` o `lint` falliscono, NON procedere finche non e fixato.
7. **Mai interrompere il flusso** — se trovi un problema, risolvilo e continua. Chiedi conferma solo per scelte architetturali davvero ambigue.

### 2.3 Al termine di ogni task
8. **Commit (SOLO git locale, niente GitHub / niente push):**
   ```bash
   git add <files>
   git commit -m "tipo: descrizione breve senza apostrofi"
   ```
   ⚠️ **MAI apostrofi nei commit message** — rompono bash heredoc.
   ⚠️ **NIENTE `git push` / niente remote** — per ora si lavora solo con git locale.
9. **Aggiorna `agent_base/HISTORY.md`** con stato, cosa e stato fatto, nuovi bug noti.
10. **Aggiorna `agent_base/CODEBASE_STRUCTURE.md`** se hai creato/spostato/rinominato file.
11. **Aggiorna `bandopilot/README.md`** se hai cambiato deps, comandi o funzionalita.

---

## 3. Regole di codice (ADK / Python)

### 3.1 Preservazione del codice
- **Modifica solo cio che il task richiede.** Preserva codice, config (specialmente `model`), commenti e formattazione circostanti.
- **NON cambiare MAI il modello** (`gemini-2.5-flash`) se non esplicitamente richiesto.
- **Non riscrivere a mano il layer A2A** ne l'infra runtime generata (`app/fast_api_app.py`, `app/app_utils/*`, `Dockerfile`): sono cablati dallo scaffold.

### 3.2 Convenzioni
- **Segui le convenzioni esistenti** — guarda il codice circostante prima di scrivere.
- **Import dei tool ADK**: importa l'istanza del tool, non il modulo (es. `from google.adk.tools.load_web_page import load_web_page`).
- **Esegui Python con `uv`**: `uv run python script.py` (dopo `agents-cli install`).
- **Aggiungi pacchetti** con `uv add <pkg>` (non pip diretto).
- **Stop dopo 3 errori uguali**: se lo stesso errore si ripete 3+ volte, fixa la causa radice invece di ritentare.

### 3.3 Gemini API — minimizzare costi
- **Modello primario**: `gemini-2.5-flash` (default per TUTTO; scelto per costo contenuto).
- **Model routing**: usa modelli piu potenti solo dove serve ragionamento architetturale; task deterministici (estrazione, check) restano sul flash.
- **Errore 404 sul modello**: NON cambiare il nome del modello, correggi `GOOGLE_CLOUD_LOCATION` (es. `global`).

### 3.4 API key e sicurezza
- **Mai committare chiavi**: le API key vanno in `bandopilot/.env` (gia in `.gitignore`).
- Per lo sviluppo locale si puo usare la chiave Google AI Studio (`GOOGLE_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI=False`); per Cloud Run si usa Vertex/ADC.

---

## 4. Struttura del progetto

```
capstoneproject_kagglecourse/
├── agent_base/                ← Istruzioni e documentazione per AI agents
│   ├── AGENT_INSTRUCTIONS.md    ← Questo file
│   ├── HISTORY.md               ← Storico completo del progetto
│   └── CODEBASE_STRUCTURE.md    ← Mappa dei file e delle directory
├── kaggle-instructions/       ← Report/linee guida del corso (contesto)
└── bandopilot/                ← Progetto ADK (l'agente vero e proprio)
    ├── AGENTS.md                ← Contratto dell'agente (deliverable capstone)
    ├── agents-cli-manifest.yaml ← Config CLI (NON editare a mano)
    ├── app/
    │   ├── agent.py             ← Logica agente (instruction, tools, model)
    │   ├── fast_api_app.py      ← Server FastAPI (generato, non toccare)
    │   └── app_utils/           ← A2A, services, telemetry (generato)
    ├── tests/
    │   ├── unit/ integration/   ← pytest
    │   └── eval/                ← dataset e config delle Evals
    ├── Dockerfile               ← (generato)
    └── pyproject.toml
```

---

## 5. Comandi rapidi

```bash
cd "/home/gaia-cecchi/Desktop/Projects/Altre API etc/capstoneproject_kagglecourse/bandopilot"

# Sviluppo ADK
agents-cli install                              # deps via uv
agents-cli playground                           # UI locale di test
agents-cli run "prompt di prova"                # smoke test rapido
agents-cli eval generate && agents-cli eval grade   # loop di valutazione
uv run pytest tests/unit tests/integration      # test
agents-cli lint                                 # qualita codice

# Deploy (solo dopo conferma umana)
agents-cli scaffold enhance . --deployment-target cloud_run
agents-cli deploy

# Git (SOLO locale, MAI push, MAI apostrofi nei messaggi)
git status
git log --oneline -10
git commit -m "tipo: descrizione"
```

---

## 6. Vincoli inviolabili

- ✅ **SOLO git locale** — niente GitHub, niente `git push`, niente remote.
- ✅ **MAI cambiare il modello** senza richiesta esplicita.
- ✅ **MAI committare API key** — sempre in `.env`.
- ✅ **Evals prima di tutto** — sono il cuore del badge; non tagliarle.
- ✅ **`pytest` + `lint` verdi** prima di considerare un task chiuso.
- ✅ **SEMPRE** aggiornare HISTORY.md e CODEBASE_STRUCTURE.md a fine task.

---

*Ultimo aggiornamento: 04/07/2026 — riscritto per il capstone BandoPilot (ADK).*
