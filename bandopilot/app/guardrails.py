"""Guardrails and lightweight observability for BandoPilot.

- ``blocca_azioni_vietate``: an input guardrail (before_model_callback) that
  refuses requests to actually submit/pay/sign on the user's behalf. BandoPilot
  informs and drafts; it never performs binding actions.
- ``traccia_tool_call``: records every tool invocation into session state, giving
  a simple, inspectable trajectory for observability and trajectory evals.
"""

from __future__ import annotations

import logging

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import BaseTool, ToolContext
from google.genai import types as genai_types

logger = logging.getLogger("bandopilot")

# Intenti che BandoPilot non deve mai eseguire (solo informare/redigere bozze).
_AZIONI_VIETATE = [
    "invia la domanda",
    "inviare la domanda",
    "invia per me",
    "presenta la domanda",
    "presentare la domanda",
    "manda la domanda",
    "firma per me",
    "firmare per me",
    "paga",
    "pagare",
    "bonifico",
    "effettua il pagamento",
    "carica sul portale",
]

_RIFIUTO = (
    "Non posso inviare, firmare o presentare domande ne effettuare pagamenti al posto tuo. "
    "Posso pero aiutarti a verificare l'eleggibilita, prepararti una bozza della domanda e "
    "indicarti i passi e la fonte ufficiale su cui completare la procedura."
)


async def blocca_azioni_vietate(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """Blocca gli intenti di azione vincolante prima della chiamata al modello."""
    ultimo_utente = ""
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            ultimo_utente = " ".join(p.text or "" for p in content.parts).lower()
            break

    if any(azione in ultimo_utente for azione in _AZIONI_VIETATE):
        logger.warning("Guardrail: bloccato intento di azione vietata.")
        callback_context.state["guardrail_triggered"] = True
        return LlmResponse(
            content=genai_types.Content(
                role="model", parts=[genai_types.Part(text=_RIFIUTO)]
            )
        )
    return None


async def traccia_tool_call(
    tool: BaseTool, args: dict, tool_context: ToolContext
) -> dict | None:
    """Registra la chiamata a tool nello stato di sessione (observability)."""
    trace = tool_context.state.get("tool_trace", [])
    trace.append(tool.name)
    tool_context.state["tool_trace"] = trace
    logger.info("tool_call: %s args=%s", tool.name, args)
    return None
