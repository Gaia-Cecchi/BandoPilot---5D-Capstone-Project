# BandoPilot — Capstone Writeup

> 5-Day AI Agents: Intensive Vibe Coding Course (Google × Kaggle) — track a tema libero.

- **App URL (Cloud Run, pubblico):** https://bandopilot-530700297106.us-central1.run.app
  (il root reindirizza alla **UI di chat** `/dev-ui/`; nessuna password richiesta)
- **Video demo:** _[DA INSERIRE — 2-3 min]_
- **Codice:** repository di questo progetto (`bandopilot/`)

> **Come provare la demo:** apri l'App URL nel browser, seleziona l'app `app` e scrivi
> il tuo profilo (es. *"Piccola impresa ICT in Lombardia, fatturato 800k, attiva da 3
> anni: sono eleggibile al voucher-digitalizzazione-lombardia?"*). Il servizio è in
> scale-to-zero (prima richiesta ~30s di cold start) ed è protetto da un tetto di spesa
> sulla API key.

---

## 1. Il problema

Le imprese e i professionisti italiani lasciano ogni anno sul tavolo finanziamenti
pubblici perché il panorama dei bandi (nazionali, regionali, di ente) è
frammentato, il linguaggio è ostico e capire *se si è davvero eleggibili* richiede
di leggere clausole legali. BandoPilot è un agente che:

1. **trova** i bandi pertinenti a un profilo (settore, regione, dimensione, obiettivo di spesa);
2. **verifica l'eleggibilità** requisito per requisito, **citando la clausola** specifica;
3. **segnala le scadenze** (e se un bando è già scaduto);
4. **imbastisce una bozza** della sezione descrittiva della domanda.

Non è un "AI che fa domande al posto tuo": è un copilota che informa, verifica e
prepara, lasciando all'umano la firma e l'invio.

## 2. Architettura: Agente = Modello + Harness

Il modello (`gemini-2.5-flash`) è ~il 10%. Il valore è nell'**Harness**. Sistema
multi-agente orchestrato, con la conoscenza servita via **MCP**:

```
                 ┌─────────────────────────────┐
   utente  ───▶  │        root_agent           │  orchestratore
                 │  (guardrails + observability)│
                 └──────┬───────────┬───────────┘
             AgentTool  │           │  AgentTool
               ┌────────▼──┐   ┌────▼──────────┐   ┌───────────────┐
               │ finder_   │   │ eligibility_  │   │ drafter_agent │
               │ agent     │   │ agent         │   │               │
               └────┬──────┘   └──────┬────────┘   └──────┬────────┘
             MCP    │        function │            function│
              (stdio)│          tool  │              tool  │
        ┌────────────▼───┐   ┌─────────▼─────────┐  ┌───────▼────────┐
        │  MCP server    │   │ verifica_         │  │ dettaglio_     │
        │  (corpus bandi)│   │ eleggibilita()    │  │ bando()        │
        │ search / get   │   │ (logica det.)     │  │                │
        └────────────────┘   └───────────────────┘  └────────────────┘
```

### I 6 pilastri del contesto → dove vivono nel codice

| Pilastro | Implementazione |
|---|---|
| **Instructions** | `bandopilot/AGENTS.md` + le `instruction` di ogni agente in `app/agent.py` |
| **Knowledge** | corpus curato `app/data/bandi.json`, servito via **MCP** (`app/mcp_server.py`) |
| **Memory** | `session.state` (profilo utente e `tool_trace` tra i turni) |
| **Examples** | pattern di flusso nelle istruzioni dell'orchestratore |
| **Tools** | `app/tools.py` (verifica eleggibilità, dettaglio) + tool MCP (ricerca, get) |
| **Guardrails** | `app/guardrails.py` (blocco azioni vincolanti) |

### Componenti dell'Harness

- **Orchestration** — `root_agent` delega a Finder → EligibilityChecker → Drafter (via `AgentTool`, il parent mantiene il controllo e sintetizza).
- **Tools** — funzioni ADK deterministiche + tool esposti via MCP.
- **MCP** — server proprio (`FastMCP`, transport stdio) che espone il corpus con un handshake standard, invece di un wrapper bespoke. Il Finder lo consuma via `McpToolset`.
- **A2A** — nativo ADK: l'agente è esposto come servizio A2A con Agent Card al well-known URI (test in `tests/integration/test_server_e2e.py`).
- **Guardrails** — `before_model_callback` che blocca in modo **deterministico** richieste di inviare/firmare/pagare, restituendo un rifiuto senza chiamare alcun tool.
- **Observability** — `before_tool_callback` registra ogni chiamata a tool in `tool_trace` (usato anche dalla trajectory eval) + telemetria nativa (Cloud Trace/Logging).
- **Sandbox** — la logica di eleggibilità gira come funzione deterministica isolata; il runtime è isolato su Cloud Run.

## 3. Context Engineering: statico vs dinamico

- **Statico** (`AGENTS.md`, istruzioni): regole immutabili e persona.
- **Dinamico** (MCP): i bandi vengono recuperati **on-demand** dal server MCP, non
  incollati nel prompt — così si evita il *context rot* e si tiene il modello
  focalizzato. Solo i bandi pertinenti entrano nel contesto.

## 4. Evaluations (il cuore del progetto)

Validazione **sistematica**, non "sembra funzionare". Tre livelli:

### 4.1 Eligibility — correttezza (deterministica)
`tests/eval/domain_eval.py` su 20 casi etichettati `(profilo, bando) → esito`.

| Metrica | Valore |
|---|---|
| Accuracy | **100%** |
| Macro precision | **100%** |
| Macro recall | **100%** |

(3 classi: `eleggibile` / `non_eleggibile` / `da_verificare`.)

### 4.2 Retrieval — pertinenza (deterministica)
10 query etichettate con i bandi che devono comparire in top-k.

| Metrica | Valore |
|---|---|
| mean recall@k | **100%** |
| hit-rate@k | **100%** |

### 4.3 Trajectory — il percorso, non solo l'output (LLM)
`tests/eval/trajectory_eval.py` gira l'agente reale via ADK Runner e verifica che,
per una domanda di eleggibilità, l'agente **(a)** usi davvero lo strumento di
verifica, **(b)** citi un codice clausola (R1, R2, …), **(c)** segnali la scadenza.
Risultato osservato: **2/3 casi con score 1.00** (il terzo bloccato dalla quota
free-tier, non da un difetto — vedi Limiti). La stessa logica è disponibile come
metrica **custom locale** ADK in `tests/eval/eval_config.yaml`.

> Perché conta: una risposta corretta ottenuta senza verificare i requisiti o
> senza citare la fonte è un fallimento di traiettoria, anche se "sembra giusta".

### 4.4 Test deterministici
`pytest tests/unit tests/integration` → **11 passed, 3 skipped** (i test che
chiamano il modello sono opt-in via `RUN_LLM_TESTS=1` per non consumare quota).

## 5. Sicurezza e gestione delle chiavi

- API key mai committata (`.env` in `.gitignore`; template in `.env.example`).
- Due modalità di auth guidate da env: AI Studio (dev) e Vertex (Cloud Run).
- Guardrail deterministico contro azioni vincolanti (invio/pagamento/firma).
- Disclaimer sistematico: il corpus è dimostrativo, ogni esito rimanda alla fonte ufficiale.

## 6. Deployment

Prototype-first con `agents-cli`. **Deployato e live su Cloud Run** (container isolato,
scale-to-zero, `min-instances 0` per costo idle ~0). La `GOOGLE_API_KEY` è iniettata da
**Secret Manager** (non in chiaro). Servizio pubblico (`allUsers` → `run.invoker`) con
UI di chat su `/dev-ui/` e Agent Card A2A su `/a2a/app/.well-known/agent-card.json`
(verificata HTTP 200). Testato end-to-end in produzione via A2A.
Comandi: `agents-cli scaffold enhance . --deployment-target cloud_run` →
`agents-cli deploy --secrets GOOGLE_API_KEY=bandopilot-api-key --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=False --min-instances 0`.

## 7. Limiti e onestà intellettuale

- **Corpus dimostrativo**: 12 bandi realistici ma semplificati; non è una fonte
  ufficiale. In produzione il corpus MCP andrebbe alimentato da open data reali
  (incentivi.gov.it, portali regionali, EU Funding & Tenders).
- **Quota free-tier**: `gemini-2.5-flash` su piano gratuito ha un limite giornaliero;
  il multi-agente fa più chiamate per query. Con billing attivo il limite sparisce.
- **Requisiti "manuali"**: alcune clausole (es. compagine femminile, età) non sono
  verificabili a macchina e sono correttamente marcate `da_verificare` anziché indovinate.

## 8. Come eseguire

```bash
cd bandopilot
cp .env.example .env            # inserisci GOOGLE_API_KEY (AI Studio)
agents-cli install
agents-cli playground           # UI locale
uv run python tests/eval/domain_eval.py       # eval deterministiche
uv run python tests/eval/trajectory_eval.py   # trajectory eval (LLM)
uv run pytest tests/unit tests/integration    # test
```
