"""MCP server for the BandoPilot grants knowledge base.

Exposes the curated corpus over the Model Context Protocol (stdio transport),
so the agent retrieves grants through a standard MCP handshake instead of a
bespoke wrapper. Run standalone with:

    uv run python -m app.mcp_server

The Finder sub-agent connects to it via ADK's ``McpToolset``.
"""

from __future__ import annotations

import pathlib
import sys

# Make the ``app`` package importable regardless of the launch cwd.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from app import bandi_data  # noqa: E402

mcp = FastMCP("bandopilot-bandi")


@mcp.tool()
def search_bandi(
    settore: str | None = None,
    regione: str | None = None,
    dimensione: str | None = None,
    query: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Cerca i bandi piu pertinenti a un profilo o a una query testuale.

    Args:
        settore: settore dell'impresa (es. ICT, turismo, manifatturiero).
        regione: regione della sede operativa (es. Lombardia). Usa None se ignota.
        dimensione: dimensione impresa (startup, micro, piccola, media, grande).
        query: parole chiave libere sull'obiettivo (es. "digitalizzazione export").
        top_k: numero massimo di risultati.

    Returns:
        Lista di bandi con id, titolo, ente, tipo, punteggio, scadenza, importo.
    """
    return bandi_data.search_bandi(
        settore=settore,
        regione=regione,
        dimensione=dimensione,
        query=query,
        top_k=top_k,
    )


@mcp.tool()
def get_bando(bando_id: str) -> dict:
    """Restituisce il record completo di un bando dato il suo id.

    Args:
        bando_id: identificativo del bando (es. "nuova-sabatini").

    Returns:
        Il bando completo con requisiti, spese ammissibili, scadenza e fonte,
        oppure un errore se l'id non esiste.
    """
    bando = bandi_data.get_bando(bando_id)
    if bando is None:
        return {"errore": f"Bando '{bando_id}' non trovato nel corpus."}
    return bando


if __name__ == "__main__":
    mcp.run(transport="stdio")
