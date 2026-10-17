---
name: dere
description: Turn long agent updates into one interactive local web page ("dere board") that a person can scan and answer in minutes. Use when an agent must report progress across many threads or needs several decisions from the user — e.g. the user says "too much text", "I keep missing things", "list what I need to decide", "make me a dashboard", "put the decisions on the right", 待我决定, 决策页, 总控台, 太长不看, dere. Lays every open item into three priority buckets (important & urgent / important, not urgent / urgent, less important), embeds each decision as a choice card with background and a recommended option, adds a tick-list of things only the user can do, a calendar, a status board and a who-is-doing-what table, serves it on 127.0.0.1, and reads the submitted answers back as JSON.
---

# dere — decide & report board

People stop reading long agent output. Things get missed, and decisions sit unanswered.
This skill replaces the wall of text with **one page**: every open item sorted by priority,
every decision answerable in its own card, and the answers returned as JSON the agent can act on.

It follows the "don't make people read raw model text" idea: controlled short sentences →
diagrams → an interactive page built for this reader and this moment, used and thrown away.
(The fourth rung, explainer video, is out of scope: costly and hard to fact-check.)

## When to use

| Situation | Use |
|---|---|
| 3+ decisions, or 5+ open items, or several workstreams to report | **dere board** |
| 1–2 questions that block your very next step | your native ask-the-user tool |
| A yes/no gate | one line in chat |

## Workflow

1. **Collect.** Pull open items from every source you own: to-do files, calendar, inbox scan,
   reports from sub-agents, earlier unanswered questions. Read primary sources; do not trust stale summaries.
2. **Triage each item** (see "Triage rules"). Merge duplicates. Drop what is done or merely informational
   (put "done" items in `done_today`).
3. **Write the cards** (see "Card rules"). One action or one decision per card.
4. **Write the data file** — schema in `references/data-schema.md`; example in `examples/sample_board.json`.
5. **Build** — `python3 scripts/build_board.py data.json --out board/board.html`
6. **Serve and open** — `python3 scripts/serve.py --dir board --answers answers --port 8795`,
   then open `http://127.0.0.1:8795/` in the browser pane / the user's browser. Check the console is clean.
7. **Read the answers** from `answers/<form_id>.json` when the user says they submitted.
   Read **both the choice and the note** — notes often override or refine the choice.
   If a choice and its note contradict, ask again in the next round instead of guessing.
8. **Act, then dispatch.** Do what was decided; hand work to the right sub-agent with the decision quoted.
9. **Next round.** Carry unanswered items forward, archive the old page (`board_<date>.html`),
   rebuild. Keep each round's decisions to ~15 where possible; everything else can still be listed.

## Triage rules

- `status`: done · open · stale (cannot tell — verify before listing) · info (no action).
- `bucket`:
  - **A — important & urgent**: due within 7 days, or directly affects a job, money, a qualification or a promise made to someone.
  - **B — important, not urgent**: high impact, due later or no deadline.
  - **C — urgent, less important**: time-bound but small.
- `owner`: the user, the agent, a named sub-agent, or an outside party. Every card has one.
- A card is a **decision** only if the user must choose. Otherwise it is an action (tick when done) or a status line.
- Never list something as open without checking it is still open (sent mail, submitted forms, calendar).
  The most common failure is re-asking a question the user already answered somewhere else.

## Card rules (controlled language)

- **Action**: starts with a verb; ≤ ~15 words; one thing only.
- **Why it matters**: one line — value gained or damage avoided. Not a restatement of the action.
- **Background**: collapsed by default; only what is needed to choose; quote the person's own words when they matter.
- **Options**: 2–4, mutually exclusive. Put the **recommended option first** and mark it. Always allow a note.
- **Deadline**: a real date. The page shows a countdown and colours it (≤2 days red, ≤7 amber).
- No hedging, no jargon the user did not use, no internal file paths in the action line.
- Write in the user's language (`"lang": "en"` or `"zh"`).

## Quality gates (run before you show the page)

- Build prints card / decision / own-action counts — sanity-check them against your triage.
- Open the page and check the browser console: **no errors**. Strings are JSON-encoded by the builder;
  if you hand-edit the HTML, unescaped quotes inside a script will blank the page.
- Every decision has a sensible default if left unanswered; say what it is in the background.
- Top three: the three things that most deserve the user's next hour.

## Privacy and safety

- The server binds to **127.0.0.1 only**. Do not expose it.
- Never put passwords, one-time codes, ID numbers or payment details on the board.
- The board is a working view, not a record of truth: the agent still updates its own files after acting.
- Do not publish a board; it usually contains private plans.

## Files

- `scripts/build_board.py` — builds the page from JSON (English and Chinese labels).
- `scripts/serve.py` — local server: serves `board.html`, stores POSTed answers.
- `references/data-schema.md` — field-by-field schema and the answers format.
- `examples/sample_board.json` — a fictional board to copy from.
