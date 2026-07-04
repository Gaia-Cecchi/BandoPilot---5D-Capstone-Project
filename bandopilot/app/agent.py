# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pathlib
import sys

from dotenv import load_dotenv

load_dotenv()

# Auth mode is driven by .env.
# - Local dev (AI Studio): GOOGLE_API_KEY set, GOOGLE_GENAI_USE_VERTEXAI=False
# - Cloud Run (Vertex): GOOGLE_CLOUD_PROJECT/LOCATION set, GOOGLE_GENAI_USE_VERTEXAI=True
# When Vertex is requested but no project is configured, fall back to ADC discovery.
if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "False").lower() == "true":
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        import google.auth

        _, project_id = google.auth.default()
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types as genai_types
from mcp import StdioServerParameters

from .guardrails import blocca_azioni_vietate, traccia_tool_call
from .tools import dettaglio_bando, verifica_eleggibilita

# gemini-2.5-flash is the default: reliable multi-agent tool-calling and cheap
# enough under the budget cap. gemini-2.5-flash-lite was tested but is too shy
# about tool use here (even with a thinking budget), so it is not the default.
# Override via BANDOPILOT_MODEL (e.g. gemini-2.5-flash-lite, gemini-flash-latest).
MODEL = os.environ.get("BANDOPILOT_MODEL", "gemini-2.5-flash")

# Optional thinking budget (helps weaker models reason about delegation/tools).
# Off by default; enable with BANDOPILOT_THINKING=1 (useful if you switch to lite).
_THINKING = os.environ.get("BANDOPILOT_THINKING", "0") != "0"
GEN_CONFIG = (
    genai_types.GenerateContentConfig(
        thinking_config=genai_types.ThinkingConfig(thinking_budget=1024)
    )
    if _THINKING
    else None
)
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
_MCP_SERVER = str(_PROJECT_ROOT / "app" / "mcp_server.py")

# --- Knowledge retrieval over MCP -------------------------------------------
# The Finder talks to the grants corpus through our own MCP server (stdio),
# a standard handshake instead of a bespoke wrapper.
bandi_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[_MCP_SERVER],
        ),
    ),
    tool_filter=["search_bandi", "get_bando"],
)

# --- Specialist sub-agents ---------------------------------------------------
finder_agent = Agent(
    name="finder_agent",
    model=MODEL,
    description="Trova e seleziona i bandi pubblici piu pertinenti a un profilo di impresa.",
    instruction=(
        "Sei il Finder di BandoPilot. Dato un profilo (settore, regione, dimensione, "
        "obiettivo di spesa), usa lo strumento search_bandi per trovare i bandi piu "
        "pertinenti e get_bando per i dettagli. Restituisci una rosa sintetica con: "
        "id, titolo, ente, tipo di agevolazione e scadenza. Non inventare bandi che non "
        "risultano dagli strumenti. Se il profilo e incompleto, dillo e indica quali dati "
        "servono per affinare la ricerca."
    ),
    tools=[bandi_mcp],
    generate_content_config=GEN_CONFIG,
    before_tool_callback=traccia_tool_call,
)

eligibility_agent = Agent(
    name="eligibility_agent",
    model=MODEL,
    description="Verifica l'eleggibilita di un profilo a uno specifico bando citando le clausole.",
    instruction=(
        "Sei l'Eligibility Checker di BandoPilot. Per valutare l'eleggibilita DEVI SEMPRE "
        "chiamare lo strumento verifica_eleggibilita con il bando_id e il profilo. "
        "Non dichiarare MAI un profilo eleggibile o non eleggibile senza aver usato lo "
        "strumento. Riporta l'esito per ogni requisito citando il codice della clausola "
        "(R1, R2, ...) e la motivazione, poi l'esito complessivo. Segnala sempre la "
        "scadenza e se e gia scaduta. Ricorda che il corpus e dimostrativo e va verificato "
        "sulla fonte ufficiale indicata."
    ),
    tools=[verifica_eleggibilita],
    generate_content_config=GEN_CONFIG,
    before_tool_callback=traccia_tool_call,
)

drafter_agent = Agent(
    name="drafter_agent",
    model=MODEL,
    description="Redige una bozza della sezione descrittiva della domanda per un bando.",
    instruction=(
        "Sei il Drafter di BandoPilot. Usa dettaglio_bando per recuperare requisiti e spese "
        "ammissibili, poi redigi una BOZZA in italiano della sezione descrittiva della "
        "domanda, coerente col profilo e con le spese ammissibili del bando. Marca "
        "chiaramente il testo come bozza e inserisci segnaposto [DA COMPLETARE] dove servono "
        "dati specifici dell'impresa. Non affermare che la domanda e stata inviata."
    ),
    tools=[dettaglio_bando],
    generate_content_config=GEN_CONFIG,
    before_tool_callback=traccia_tool_call,
)

# --- Orchestrator ------------------------------------------------------------
root_agent = Agent(
    name="root_agent",
    model=MODEL,
    description="Orchestratore di BandoPilot: guida l'utente da profilo a bozza di domanda.",
    instruction=(
        "Sei BandoPilot, un assistente che aiuta imprese e professionisti italiani a "
        "orientarsi tra i bandi pubblici di finanziamento.\n\n"
        "Flusso di lavoro:\n"
        "1. Raccogli il profilo dell'utente: settore, regione, dimensione (startup/micro/"
        "piccola/media/grande), eventuale fatturato e anni di attivita, e l'obiettivo di "
        "spesa. Se mancano dati essenziali, chiedili.\n"
        "2. Usa finder_agent per trovare i bandi pertinenti.\n"
        "3. Se l'utente chiede se e eleggibile a uno o piu bandi specifici (o quando serve "
        "confermare l'eleggibilita di un bando che consigli), chiama SEMPRE eligibility_agent. "
        "Nel messaggio a eligibility_agent includi il bando_id e il profilo completo "
        "(settore, regione, dimensione, fatturato, anni_attivita) cosi come lo conosci.\n"
        "4. Se l'utente lo chiede, usa drafter_agent per una bozza di domanda.\n"
        "5. Dopo aver usato i sub-agenti, sintetizza TU una risposta finale chiara per "
        "l'utente: non limitarti a inoltrare l'output grezzo di un sub-agente.\n\n"
        "Regole d'oro (inviolabili):\n"
        "- Non dichiarare MAI un'eleggibilita senza che eligibility_agent abbia usato lo "
        "strumento di verifica; riporta sempre i codici delle clausole.\n"
        "- Segnala SEMPRE la scadenza del bando e avvisa se e gia scaduta.\n"
        "- Ricorda che i dati provengono da un corpus dimostrativo e vanno verificati sulla "
        "fonte ufficiale.\n"
        "- Non inviare, firmare o presentare domande, ne effettuare pagamenti per conto "
        "dell'utente.\n"
        "Rispondi sempre in italiano, in modo chiaro e sintetico."
    ),
    tools=[
        AgentTool(finder_agent),
        AgentTool(eligibility_agent),
        AgentTool(drafter_agent),
    ],
    generate_content_config=GEN_CONFIG,
    before_model_callback=blocca_azioni_vietate,
    before_tool_callback=traccia_tool_call,
)

app = App(
    root_agent=root_agent,
    name="app",
)
