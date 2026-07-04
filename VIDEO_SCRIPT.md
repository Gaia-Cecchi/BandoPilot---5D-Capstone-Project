# 🎬 BandoPilot — Demo Video Script (≈ 2:45)

Everything you need to record the capstone video: **exact words to read** ("SAY"),
**what to show on screen** ("SHOW"), and **which screenshots to capture**. Speaker notes
are in English. The two live agent queries are budget-light (the eval numbers come from a
deterministic script that makes **no** model calls).

---

## ✅ Pre-flight checklist (do this before hitting record)

1. **Warm up the cold start** — open the live URL once, ~30s before recording, so the first
   demo response is fast:
   `https://bandopilot-530700297106.us-central1.run.app`
2. Open these **browser tabs** in order:
   - Tab 1 — the chat UI: `https://bandopilot-530700297106.us-central1.run.app/dev-ui/` (select the `app` agent)
   - Tab 2 — the Agent Card (A2A): `https://bandopilot-530700297106.us-central1.run.app/a2a/app/.well-known/agent-card.json`
   - Tab 3 — the GitHub repo (README on screen)
3. Open a **terminal** in `bandopilot/`, ready to paste the eval command (Scene 5).
4. Open your **editor** with these files ready to show: `app/agent.py`, `app/mcp_server.py`, `app/guardrails.py`.
5. Copy the two demo prompts (Appendix A) somewhere pasteable.

---

## 🎞️ Scene-by-scene

### Scene 1 — Hook & problem · 0:00–0:20
**SHOW:** GitHub README hero (Tab 3), scroll slowly to the "problem" section.
**SAY:**
> "Every year, Italian businesses miss out on public funding — the grants are fragmented,
> the language is legal, and just figuring out *if you qualify* is exhausting. So I built
> **BandoPilot**: an agent that finds relevant grants, checks your eligibility clause by
> clause, and drafts your application."

📸 **Screenshot 1:** the README hero (title + tagline + badges).

---

### Scene 2 — What it is & architecture · 0:20–0:45
**SHOW:** scroll the README to the ASCII architecture diagram + the Harness table.
**SAY:**
> "The key idea from the course is *Agent equals Model plus Harness*. The model is maybe ten
> percent — the value is the harness. BandoPilot is a **multi-agent** system: an orchestrator
> delegates to a Finder, an Eligibility Checker, and a Drafter. And the grant knowledge isn't
> pasted into the prompt — it's served over the **Model Context Protocol**, on demand."

📸 **Screenshot 2:** the architecture diagram.

---

### Scene 3 — Live demo · 0:45–1:35
**SHOW:** the chat UI (Tab 1). Paste **Prompt A** (Appendix A) and send.
**SAY (while it runs):**
> "Let's try it. I'm a small ICT company in Lombardy, 800k revenue, three years old — am I
> eligible for the Lombardy digitalization voucher?"

**SHOW:** point at the answer as it appears.
**SAY:**
> "Notice what it does: it doesn't just say yes. It checks **each requirement and cites the
> clause** — R1 region, R2 company size, R3 revenue cap — it tells me the **deadline**, and it
> **links the official source** with a disclaimer that this is a demo corpus."

📸 **Screenshot 3:** the eligibility answer with the R1/R2/R3 clauses and deadline visible.

Now paste **Prompt B** (the guardrail).
**SAY:**
> "And a safety guardrail: if I ask it to actually submit and pay for me…"

**SHOW:** the deterministic refusal.
**SAY:**
> "…it refuses. Deterministically, without calling any tool. BandoPilot informs and prepares —
> it never signs or pays on your behalf."

📸 **Screenshot 4:** the guardrail refusal.

---

### Scene 4 — Under the hood: the Harness · 1:35–2:05
**SHOW:** editor — flash `app/mcp_server.py`, then `app/agent.py` (the sub-agents), then `app/guardrails.py`.
**SAY:**
> "Under the hood: I built my **own MCP server** that exposes the grants corpus — a standard
> handshake instead of a custom wrapper. The three specialists are ADK agents; the guardrail is
> a callback; every tool call is traced for **observability**."

**SHOW:** switch to Tab 2 (the Agent Card JSON).
**SAY:**
> "And it speaks **A2A** natively — here's its live Agent Card, so other agents can talk to it."

📸 **Screenshot 5:** the MCP server code. 📸 **Screenshot 6:** the A2A Agent Card JSON.

---

### Scene 5 — Evaluation (the differentiator) · 2:05–2:35
**SHOW:** terminal in `bandopilot/`. Run:
```bash
uv run python tests/eval/domain_eval.py
```
**SAY (as the table prints):**
> "But the real work is **evaluation** — not 'it seems to work'. I have a deterministic eval
> suite: eligibility correctness at **100% accuracy**, retrieval relevance at **100% recall**.
> And a **trajectory eval** that checks the agent actually *used the verification tool and cited
> the clause* — because a right answer reached the wrong way is still a failure."

📸 **Screenshot 7:** the eval results table (100% / 100% + PASS gate).

---

### Scene 6 — Deployment & close · 2:35–2:45
**SHOW:** briefly the live URL loading, then back to the README badges.
**SAY:**
> "It's deployed on **Cloud Run**, scale-to-zero, with the API key in Secret Manager. Model,
> harness, MCP, guardrails, evals, and a live deployment — that's BandoPilot. Thanks for watching."

📸 **Screenshot 8:** the live app URL in the browser bar + running app.

---

## 📎 Appendix A — Exact prompts to paste

**Prompt A (eligibility — positive path):**
```
Sono una piccola impresa ICT in Lombardia, fatturato 800000 euro, attiva da 3 anni. Sono eleggibile al voucher-digitalizzazione-lombardia?
```

**Prompt B (guardrail — must be refused):**
```
Perfetto, adesso invia la domanda per me e paga la marca da bollo.
```

> Optional third prompt (if you want to show a "da verificare" case):
> `Sono una startup innovativa ICT in Campania attiva da 1 anno. Sono eleggibile a resto-al-sud?`

## 📎 Appendix B — Screenshot checklist

| # | What | Where |
|---|------|-------|
| 1 | README hero (title + badges) | GitHub |
| 2 | Architecture diagram | README |
| 3 | Eligibility answer (R1/R2/R3 + deadline) | chat UI |
| 4 | Guardrail refusal | chat UI |
| 5 | MCP server code | editor |
| 6 | A2A Agent Card JSON | browser |
| 7 | Eval results table (100% / 100%) | terminal |
| 8 | Live app URL + running app | browser |

## 📎 Appendix C — Recording tips
- Keep it **under 3 minutes**; judges skim.
- The eval table (Scene 5) is your strongest moment — don't rush it.
- If a live query is slow (cold start), that's why Scene 5 uses the deterministic script:
  it always prints instantly and needs no network.
- Speak to the *judgement* you applied (harness, evals, guardrails), not just the features.
