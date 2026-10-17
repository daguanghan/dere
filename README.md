# dere — DEcide & REport

**Stop making people read walls of AI text.** `dere` is an agent skill that turns long progress
updates into one interactive local web page: every open item sorted into three priority buckets,
every decision answerable inside its own card, and the answers returned as JSON the agent acts on.

```
🔴 Important & urgent      🟠 Important, not urgent      🟡 Urgent, less important
┌──────────────────────┐   ┌──────────────────────┐      ┌──────────────────────┐
│ Pick the launch date │   │ Fill the design gap  │      │ Approve the subject  │
│ why · background     │   │ ○ A contract ★       │      │ ○ A keep ★  ○ B short│
│ ○ A 20 May ★ ○ B 13  │   │ ○ B permanent role   │      │ note…                │
│ ⏰ 2 days left        │   │ ⏰ 16 days left       │      └──────────────────────┘
└──────────────────────┘   └──────────────────────┘
Tabs: Buckets · Calendar · Status board · Who is doing what · Done today        [Submit]
```

## Why

Agents now produce more text than people can read. Things get missed and decisions sit unanswered.
The fix is to change the *format*, not to write more: short controlled sentences, a picture where it helps,
and an interactive page made for this reader at this moment — used, answered, thrown away.

## What you get

- **Three buckets** (an Eisenhower-style split): important & urgent / important, not urgent / urgent, less important.
- **Decision cards**: one question, a one-line "why it matters", collapsible background, 2–4 options with the
  **recommended option first**, and a note box. Deadlines show as a coloured countdown.
- **Own-action ticks** for things only the person can do (sign, call, enter a code).
- **Top three**, **calendar**, **status board** per workstream, **who-is-doing-what** (sub-agents, people), **done today**.
- Filters (bucket, workstream, "only my decisions", search), progress bar, answers kept in the browser until submitted.
- English or Chinese labels; light and dark mode; works on a phone.
- A tiny local server (127.0.0.1 only) that stores each submission as JSON.

## Use it

```bash
# 1. build the page from a data file
python3 scripts/build_board.py examples/sample_board.json --out board/board.html
# 2. serve it locally and open http://127.0.0.1:8795/
python3 scripts/serve.py --dir board --answers answers --port 8795
# 3. after the person submits, read answers/<form_id>.json
```

As a Claude Code skill: copy this folder to `~/.claude/skills/dere/`. The agent follows `SKILL.md`:
collect → triage → write cards → build → serve → read answers → act → next round.

No dependencies beyond Python 3.8+.

## Files

| Path | What |
|---|---|
| `SKILL.md` | The method: when to use, triage rules, card-writing rules, quality gates |
| `scripts/build_board.py` | JSON → single self-contained HTML page |
| `scripts/serve.py` | Local server: serves the page, saves answers |
| `references/data-schema.md` | Data and answers formats |
| `examples/sample_board.json` | A fictional board to start from |

## Licence

MIT
