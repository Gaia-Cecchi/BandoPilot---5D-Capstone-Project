"""Unit tests for the deterministic domain layer (no LLM, no network)."""

from __future__ import annotations

import datetime

from app import bandi_data


def test_corpus_loads() -> None:
    bandi = bandi_data.load_bandi()
    assert len(bandi) >= 10
    # ogni bando ha i campi chiave
    for b in bandi:
        assert {"id", "titolo", "requisiti", "scadenza", "regioni", "dimensioni"} <= set(b)


def test_get_bando_found_and_missing() -> None:
    assert bandi_data.get_bando("nuova-sabatini")["id"] == "nuova-sabatini"
    assert bandi_data.get_bando("inesistente") is None


def test_search_hard_filters_region() -> None:
    # Un bando solo-Toscana non deve comparire per una ricerca in Lombardia.
    ids = {r["id"] for r in bandi_data.search_bandi(regione="Lombardia")}
    assert "toscana-innovazione-pmi" not in ids


def test_search_ranks_specific_regional_grant() -> None:
    res = bandi_data.search_bandi(
        settore="ICT", regione="Lombardia", dimensione="piccola",
        query="digitalizzazione ecommerce",
    )
    ids = [r["id"] for r in res]
    assert "voucher-digitalizzazione-lombardia" in ids


def test_eligibility_eleggibile() -> None:
    prof = {"settore": "manifatturiero", "regione": "Toscana", "dimensione": "media", "fatturato": 2_000_000}
    res = bandi_data.check_eligibility(prof, "toscana-innovazione-pmi")
    assert res["esito"] == "eleggibile"
    assert all(r["codice"] for r in res["requisiti"])  # ogni requisito e citato


def test_eligibility_non_eleggibile_regione() -> None:
    prof = {"settore": "ICT", "regione": "Lombardia", "dimensione": "piccola", "fatturato": 500_000}
    res = bandi_data.check_eligibility(prof, "toscana-innovazione-pmi")
    assert res["esito"] == "non_eleggibile"


def test_eligibility_da_verificare_manuale() -> None:
    # smart-start ha un requisito manuale -> al massimo 'da_verificare'
    prof = {"settore": "ICT", "regione": "Lombardia", "dimensione": "startup", "anni_attivita": 2}
    res = bandi_data.check_eligibility(prof, "smart-start-italia")
    assert res["esito"] == "da_verificare"


def test_eligibility_fatturato_max() -> None:
    prof = {"settore": "commercio", "regione": "Lombardia", "dimensione": "media", "fatturato": 60_000_000}
    res = bandi_data.check_eligibility(prof, "voucher-digitalizzazione-lombardia")
    assert res["esito"] == "non_eleggibile"


def test_deadline_status_past_and_future() -> None:
    today = datetime.date(2026, 7, 4)
    past = bandi_data.deadline_status(bandi_data.get_bando("bando-turismo-veneto"), today=today)
    assert past["scaduto"] is True
    future = bandi_data.deadline_status(bandi_data.get_bando("nuova-sabatini"), today=today)
    assert future["scaduto"] is False
    assert future["giorni_rimanenti"] > 0
