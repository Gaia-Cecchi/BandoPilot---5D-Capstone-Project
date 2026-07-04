"""Domain layer for BandoPilot.

Pure, dependency-free logic over the curated grants corpus (``data/bandi.json``).
Both the MCP server and the ADK tools build on these functions, and the eval
suite exercises them directly. No LLM or ADK imports here on purpose: this must
stay deterministic and unit-testable.
"""

from __future__ import annotations

import datetime
import json
import unicodedata
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "bandi.json"

# Requirement types that can be checked deterministically against a profile.
_AUTO_TYPES = {
    "regione",
    "dimensione",
    "settore",
    "fatturato_max",
    "anni_attivita_max",
    "anni_attivita_min",
}


def _norm(value: str) -> str:
    """Lowercase + strip accents, for tolerant matching."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.strip().lower()


@lru_cache(maxsize=1)
def load_bandi() -> list[dict]:
    """Load and cache the grants corpus."""
    with open(DATA_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    return data["bandi"]


def get_bando(bando_id: str) -> dict | None:
    """Return the full record for a grant id, or None if not found."""
    target = _norm(bando_id)
    for bando in load_bandi():
        if _norm(bando["id"]) == target:
            return bando
    return None


def _regione_match(regione: str | None, allowed: list[str]) -> bool:
    allowed_norm = {_norm(a) for a in allowed}
    if "nazionale" in allowed_norm:
        return True
    return regione is not None and _norm(regione) in allowed_norm


def _settore_match(settore: str | None, allowed: list[str]) -> bool:
    allowed_norm = {_norm(a) for a in allowed}
    if "tutti" in allowed_norm:
        return True
    return settore is not None and _norm(settore) in allowed_norm


def search_bandi(
    settore: str | None = None,
    regione: str | None = None,
    dimensione: str | None = None,
    query: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Rank grants by relevance to a profile / free-text query.

    Scoring (higher = more relevant): region +3, size +3, explicit sector match
    +3 (generic 'tutti' only +1), and +2 per query keyword found in
    title/description/sectors/eligible-costs. Grants that clearly exclude the
    profile (wrong region or size) are dropped. Weighting an explicit sector and
    query hits above the generic 'tutti' keeps a targeted regional grant ahead of
    broad national ones for a specific query.
    """
    keywords = [_norm(k) for k in (query or "").split() if len(k) > 2]
    results = []
    for bando in load_bandi():
        score = 0

        if regione:
            if _regione_match(regione, bando["regioni"]):
                score += 3
            else:
                continue  # hard filter: wrong region
        if dimensione:
            if _norm(dimensione) in {_norm(d) for d in bando["dimensioni"]}:
                score += 3
            else:
                continue  # hard filter: wrong company size
        if settore and _settore_match(settore, bando["settori"]):
            score += 1 if "tutti" in {_norm(s) for s in bando["settori"]} else 3

        haystack = _norm(
            bando["titolo"]
            + " "
            + bando["descrizione"]
            + " "
            + " ".join(bando["settori"])
            + " "
            + " ".join(bando.get("spese_ammissibili", []))
        )
        score += 2 * sum(1 for kw in keywords if kw in haystack)

        if score == 0 and (settore or query):
            continue

        results.append(
            {
                "id": bando["id"],
                "titolo": bando["titolo"],
                "ente": bando["ente"],
                "tipo": bando["tipo"],
                "score": score,
                "scadenza": bando["scadenza"],
                "importo": bando["importo"],
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]


def deadline_status(bando: dict, today: datetime.date | None = None) -> dict:
    """Return scadenza info: days left and whether it is already past."""
    today = today or datetime.date.today()
    scad = datetime.date.fromisoformat(bando["scadenza"])
    giorni = (scad - today).days
    return {
        "scadenza": bando["scadenza"],
        "giorni_rimanenti": giorni,
        "scaduto": giorni < 0,
    }


def _check_requisito(req: dict, profile: dict) -> tuple[str, str]:
    """Evaluate one requirement against the profile.

    Returns (esito, motivazione) where esito is
    'soddisfatto' | 'non_soddisfatto' | 'da_verificare'.
    """
    tipo = req["tipo"]
    valore = req.get("valore")

    if tipo not in _AUTO_TYPES:
        return "da_verificare", "Requisito da verificare manualmente sui documenti del bando."

    if tipo == "regione":
        if profile.get("regione") is None:
            return "da_verificare", "Regione del profilo non specificata."
        ok = _regione_match(profile.get("regione"), valore)
        return (
            ("soddisfatto", f"Regione '{profile['regione']}' ammessa.")
            if ok
            else ("non_soddisfatto", f"Regione '{profile['regione']}' non tra quelle ammesse: {valore}.")
        )

    if tipo == "dimensione":
        if profile.get("dimensione") is None:
            return "da_verificare", "Dimensione impresa non specificata."
        ok = _norm(profile["dimensione"]) in {_norm(v) for v in valore}
        return (
            ("soddisfatto", f"Dimensione '{profile['dimensione']}' ammessa.")
            if ok
            else ("non_soddisfatto", f"Dimensione '{profile['dimensione']}' non ammessa (richiesto: {valore}).")
        )

    if tipo == "settore":
        if profile.get("settore") is None:
            return "da_verificare", "Settore non specificato."
        ok = _settore_match(profile["settore"], valore)
        return (
            ("soddisfatto", f"Settore '{profile['settore']}' ammesso.")
            if ok
            else ("non_soddisfatto", f"Settore '{profile['settore']}' non ammesso (richiesto: {valore}).")
        )

    if tipo == "fatturato_max":
        fatt = profile.get("fatturato")
        if fatt is None:
            return "da_verificare", "Fatturato non specificato."
        ok = fatt <= valore
        return (
            ("soddisfatto", f"Fatturato {fatt} entro il limite di {valore}.")
            if ok
            else ("non_soddisfatto", f"Fatturato {fatt} superiore al limite di {valore}.")
        )

    if tipo in ("anni_attivita_max", "anni_attivita_min"):
        anni = profile.get("anni_attivita")
        if anni is None:
            return "da_verificare", "Anni di attivita non specificati."
        if tipo == "anni_attivita_max":
            ok = anni <= valore
            msg_ok = f"Attivita da {anni} anni, entro il massimo di {valore}."
            msg_ko = f"Attivita da {anni} anni, oltre il massimo di {valore}."
        else:
            ok = anni >= valore
            msg_ok = f"Attivita da {anni} anni, almeno {valore} richiesti."
            msg_ko = f"Attivita da {anni} anni, meno dei {valore} richiesti."
        return ("soddisfatto", msg_ok) if ok else ("non_soddisfatto", msg_ko)

    return "da_verificare", "Requisito non riconosciuto."


def check_eligibility(profile: dict, bando_id: str) -> dict:
    """Check a profile against a grant, requirement by requirement.

    Overall esito:
    - 'non_eleggibile' if any requirement is not satisfied
    - 'eleggibile' if all requirements are satisfied
    - 'da_verificare' if none fail but some need manual verification
    Every requirement result cites its clause code (R1, R2, ...).
    """
    bando = get_bando(bando_id)
    if bando is None:
        return {"bando_id": bando_id, "esito": "non_trovato", "requisiti": [], "note": "Bando inesistente nel corpus."}

    dettagli = []
    has_fail = False
    has_unknown = False
    for req in bando["requisiti"]:
        esito, motivazione = _check_requisito(req, profile)
        if esito == "non_soddisfatto":
            has_fail = True
        elif esito == "da_verificare":
            has_unknown = True
        dettagli.append(
            {
                "codice": req["codice"],
                "descrizione": req["descrizione"],
                "esito": esito,
                "motivazione": motivazione,
            }
        )

    if has_fail:
        esito = "non_eleggibile"
    elif has_unknown:
        esito = "da_verificare"
    else:
        esito = "eleggibile"

    return {
        "bando_id": bando["id"],
        "titolo": bando["titolo"],
        "esito": esito,
        "requisiti": dettagli,
        "scadenza": deadline_status(bando),
        "fonte_url": bando["fonte_url"],
        "note": "Corpus dimostrativo: verificare sempre sulla fonte ufficiale.",
    }
