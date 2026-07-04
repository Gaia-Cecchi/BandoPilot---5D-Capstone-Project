"""Deterministic domain eval for BandoPilot.

Scores the two logic-level metrics that the badge cares about, without any LLM
call or GCP dependency:

  1. Eligibility correctness  -> accuracy + macro precision/recall over the
     three classes (eleggibile / non_eleggibile / da_verificare).
  2. Retrieval relevance      -> recall@k and hit-rate@k against labeled queries.

Run:  uv run python tests/eval/domain_eval.py
Exit code is non-zero if a metric falls below its threshold, so this doubles as
a CI gate. The LLM-level trajectory eval lives in the ADK eval flow separately.
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import bandi_data  # noqa: E402

DATASETS = ROOT / "tests" / "eval" / "labeled"
CLASSI = ["eleggibile", "non_eleggibile", "da_verificare"]

# Quality gates.
SOGLIA_ELIG_ACCURACY = 0.90
SOGLIA_RET_RECALL = 0.90


def _load(name: str) -> dict:
    with open(DATASETS / name, encoding="utf-8") as fh:
        return json.load(fh)


def eval_eligibility() -> tuple[float, dict]:
    cases = _load("eligibility_labeled.json")["cases"]
    # confusion[atteso][predetto]
    confusion = {a: {p: 0 for p in CLASSI} for a in CLASSI}
    corretti = 0
    errori = []
    for c in cases:
        res = bandi_data.check_eligibility(c["profilo"], c["bando_id"])
        pred = res["esito"]
        atteso = c["atteso"]
        confusion[atteso][pred] = confusion[atteso].get(pred, 0) + 1
        if pred == atteso:
            corretti += 1
        else:
            errori.append((c["id"], c["bando_id"], atteso, pred))

    accuracy = corretti / len(cases)

    # Macro precision/recall.
    prec_per_classe, rec_per_classe = {}, {}
    for cl in CLASSI:
        tp = confusion[cl][cl]
        fn = sum(confusion[cl][p] for p in CLASSI if p != cl)
        fp = sum(confusion[a][cl] for a in CLASSI if a != cl)
        prec_per_classe[cl] = tp / (tp + fp) if (tp + fp) else 1.0
        rec_per_classe[cl] = tp / (tp + fn) if (tp + fn) else 1.0
    macro_prec = sum(prec_per_classe.values()) / len(CLASSI)
    macro_rec = sum(rec_per_classe.values()) / len(CLASSI)

    return accuracy, {
        "n": len(cases),
        "accuracy": accuracy,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "precision_per_classe": prec_per_classe,
        "recall_per_classe": rec_per_classe,
        "errori": errori,
    }


def eval_retrieval() -> tuple[float, dict]:
    cases = _load("retrieval_labeled.json")["cases"]
    recall_totale = 0.0
    hit = 0
    dettagli = []
    for c in cases:
        risultati = bandi_data.search_bandi(**c["params"], top_k=c["k"])
        trovati = {r["id"] for r in risultati}
        attesi = set(c["attesi"])
        recall = len(attesi & trovati) / len(attesi)
        recall_totale += recall
        if attesi <= trovati:
            hit += 1
        else:
            dettagli.append((c["id"], sorted(attesi - trovati), [r["id"] for r in risultati]))

    mean_recall = recall_totale / len(cases)
    hit_rate = hit / len(cases)
    return mean_recall, {
        "n": len(cases),
        "mean_recall_at_k": mean_recall,
        "hit_rate_at_k": hit_rate,
        "mancati": dettagli,
    }


def _pct(x: float) -> str:
    return f"{100 * x:5.1f}%"


def main() -> int:
    elig_acc, elig = eval_eligibility()
    ret_recall, ret = eval_retrieval()

    print("=" * 60)
    print("BANDOPILOT — DOMAIN EVAL (deterministica)")
    print("=" * 60)
    print(f"\n[1] Eligibility  (n={elig['n']})")
    print(f"    accuracy         : {_pct(elig['accuracy'])}")
    print(f"    macro precision  : {_pct(elig['macro_precision'])}")
    print(f"    macro recall     : {_pct(elig['macro_recall'])}")
    for cl in CLASSI:
        print(
            f"      - {cl:<16} P={_pct(elig['precision_per_classe'][cl])}"
            f"  R={_pct(elig['recall_per_classe'][cl])}"
        )
    if elig["errori"]:
        print("    errori:")
        for cid, bid, atteso, pred in elig["errori"]:
            print(f"      {cid} [{bid}] atteso={atteso} predetto={pred}")

    print(f"\n[2] Retrieval  (n={ret['n']})")
    print(f"    mean recall@k    : {_pct(ret['mean_recall_at_k'])}")
    print(f"    hit-rate@k       : {_pct(ret['hit_rate_at_k'])}")
    if ret["mancati"]:
        print("    query con bandi attesi mancanti:")
        for cid, mancanti, got in ret["mancati"]:
            print(f"      {cid} mancanti={mancanti} risultati={got}")

    ok = elig_acc >= SOGLIA_ELIG_ACCURACY and ret_recall >= SOGLIA_RET_RECALL
    print("\n" + "-" * 60)
    print(
        f"GATE: eligibility>={_pct(SOGLIA_ELIG_ACCURACY)} e retrieval>={_pct(SOGLIA_RET_RECALL)}"
        f"  ->  {'PASS' if ok else 'FAIL'}"
    )
    print("-" * 60)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
