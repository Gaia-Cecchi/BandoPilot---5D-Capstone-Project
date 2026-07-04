"""ADK function tools for BandoPilot (business logic layer).

Grant *retrieval* is served over MCP (see ``app/mcp_server.py``); these native
function tools cover the deterministic business logic — eligibility checking and
full-record lookup — that the Eligibility and Drafter sub-agents rely on.
"""

from __future__ import annotations

from app import bandi_data


def verifica_eleggibilita(bando_id: str, profilo: dict) -> dict:
    """Verifica l'eleggibilita di un profilo a un bando, requisito per requisito.

    Ogni requisito viene valutato in modo deterministico e riporta il codice
    della clausola (R1, R2, ...) come citazione. L'esito complessivo e
    'eleggibile', 'non_eleggibile' o 'da_verificare'.

    Args:
        bando_id: identificativo del bando (es. "nuova-sabatini").
        profilo: dati dell'impresa. Chiavi supportate: settore, regione,
            dimensione (startup|micro|piccola|media|grande|persona_fisica),
            fatturato (numero EUR), anni_attivita (numero). Le chiavi ignote
            possono essere omesse: verranno segnalate come 'da_verificare'.

    Returns:
        Dizionario con esito complessivo, elenco requisiti (codice, esito,
        motivazione), stato scadenza e fonte ufficiale.
    """
    return bandi_data.check_eligibility(profilo, bando_id)


def dettaglio_bando(bando_id: str) -> dict:
    """Restituisce il record completo di un bando dato il suo id.

    Args:
        bando_id: identificativo del bando (es. "smart-start-italia").

    Returns:
        Il bando completo (requisiti, spese ammissibili, importi, scadenza,
        fonte), oppure un errore se l'id non esiste.
    """
    bando = bandi_data.get_bando(bando_id)
    if bando is None:
        return {"errore": f"Bando '{bando_id}' non trovato nel corpus."}
    return bando
