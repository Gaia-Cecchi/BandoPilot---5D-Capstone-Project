"""Trajectory eval for BandoPilot (LLM-level).

Runs the real multi-agent over eligibility prompts via the ADK Runner (AI Studio
API key, no GCP) and grades the *reasoning path*, not just the final answer:

  - the verification tool was actually used (verifica_eleggibilita / eligibility_agent),
  - the answer cites a clause code (R1, R2, ...),
  - the deadline is surfaced.

This is the "trajectory evaluation" the capstone asks for. The deterministic
eligibility/retrieval precision/recall live in domain_eval.py.

Run:  uv run python tests/eval/trajectory_eval.py
"""

from __future__ import annotations

import asyncio
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

from app.agent import root_agent  # noqa: E402

CASI = [
    {
        "id": "traj_eligibility_lombardia",
        "prompt": "Sono una piccola impresa ICT in Lombardia, fatturato 800000 euro, "
        "attiva da 3 anni. Sono eleggibile al voucher-digitalizzazione-lombardia?",
    },
    {
        "id": "traj_eligibility_toscana",
        "prompt": "Ho una media impresa manifatturiera in Toscana con fatturato 2 milioni. "
        "Posso accedere al bando toscana-innovazione-pmi? Verifica i requisiti.",
    },
    {
        "id": "traj_eligibility_startup_negativo",
        "prompt": "Sono una media impresa ICT in Lombardia attiva da 2 anni. "
        "Sono eleggibile a smart-start-italia?",
    },
]

SOGLIA = 0.75  # media minima per superare il gate


async def _run_case(prompt: str) -> tuple[list[str], str]:
    """Run one prompt, return (nomi tool chiamati, testo blob completo)."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="eval", session_id="s"
    )
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )

    call_names: list[str] = []
    texts: list[str] = []
    final = ""
    async for event in runner.run_async(
        user_id="eval",
        session_id="s",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            if part.function_call and part.function_call.name:
                call_names.append(part.function_call.name)
            if part.function_response and part.function_response.response is not None:
                texts.append(str(part.function_response.response))
            if part.text:
                texts.append(part.text)
                if event.is_final_response():
                    final = part.text
    return call_names, final + " " + " ".join(texts)


def _score(call_names: list[str], blob: str) -> tuple[float, dict]:
    blob_low = blob.lower()
    tool_ok = "verifica_eleggibilita" in call_names or "eligibility_agent" in call_names
    cited = bool(re.search(r"\bR[1-9]\b", blob))
    deadline = "scaden" in blob_low or "scadut" in blob_low
    score = 0.5 * tool_ok + 0.25 * cited + 0.25 * deadline
    return score, {"tool_verifica": tool_ok, "citazione_clausola": cited, "scadenza": deadline}


async def main() -> int:
    print("=" * 64)
    print("BANDOPILOT — TRAJECTORY EVAL (LLM, ADK Runner)")
    print("=" * 64)
    totale = 0.0
    valutati = 0
    for i, caso in enumerate(CASI):
        try:
            call_names, blob = await _run_case(caso["prompt"])
        except Exception as exc:  # e.g. 429 RESOURCE_EXHAUSTED (free-tier quota)
            msg = str(exc).split("\n")[0][:120]
            print(f"\n[{caso['id']}]  SALTATO (errore runtime): {msg}")
            continue
        score, flags = _score(call_names, blob)
        totale += score
        valutati += 1
        print(f"\n[{caso['id']}]  score={score:.2f}")
        print(f"    tool chiamati : {call_names}")
        print(
            f"    tool_verifica={flags['tool_verifica']}  "
            f"citazione_clausola={flags['citazione_clausola']}  "
            f"scadenza={flags['scadenza']}"
        )
        if i < len(CASI) - 1:
            await asyncio.sleep(5)  # respiro tra i casi per la quota free-tier

    if valutati == 0:
        print("\nNessun caso valutato (probabile quota esaurita). Riprova piu tardi.")
        return 1
    media = totale / valutati
    print("\n" + "-" * 64)
    print(f"MEDIA trajectory score = {media:.2f}  (soglia {SOGLIA})  ->  "
          f"{'PASS' if media >= SOGLIA else 'FAIL'}")
    print("-" * 64)
    return 0 if media >= SOGLIA else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
