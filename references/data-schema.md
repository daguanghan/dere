# Data schema

One JSON file per board. Only `items` is required; everything else is optional.

```jsonc
{
  "lang": "en",                 // "en" or "zh" — labels on the page
  "title": "dere board",
  "form_id": "2026-05-04_board",// answers are saved as answers/<form_id>.json
  "today": "2026-05-04",        // drives countdowns; defaults to the system date
  "lead": "One line on how to use this page",
  "stats": [ {"value": "4", "label": "decisions for you"} ],
  "top3":  [ "The three things that deserve the next hour" ],

  "items": [
    {
      "id": "launch_date",      // unique, stable across rounds (answers are keyed by it)
      "bucket": "A",            // A important & urgent | B important, not urgent | C urgent, less important
      "line": "Launch",         // workstream; used by the filter
      "owner": "you",           // who acts
      "deadline": "2026-05-06", // YYYY-MM-DD or null
      "action": "Pick the launch date",
      "why": "The venue releases the room on Wednesday",
      "bg": "Plain-text background (collapsed)",
      "bg_html": false,         // true only if bg contains trusted HTML you wrote yourself
      "options": [              // present → a decision card
        {"key": "A", "text": "20 May", "recommended": true},
        {"key": "B", "text": "13 May"}
      ],
      "mine": true              // no options + mine → shows a "Done" tick for the user
    }
  ],

  "calendar": [ {"date": "2026-05-05", "events": [ {"time": "11:00", "what": "Supplier call", "where": "video"} ]} ],
  "lines":    [ {"name": "Launch", "light": "g|y|r", "status": "short", "now": "where it stands", "next": "next step"} ],
  "sessions": [ {"name": "agent: docs", "latest": "what it did last", "waiting": "what it waits for"} ],
  "done_today": [ "Things finished since the last board" ]
}
```

## Answers file

`answers/<form_id>.json` (plus a timestamped copy on every submit):

```json
{
  "_form": "2026-05-04_board",
  "answers": {
    "launch_date": {"choice": "A", "choice_text": "20 May — one more week of testing", "note": "", "title": "Pick the launch date"}
  },
  "done": {"sign_supplier": true},
  "free": "Anything the user typed in the final box",
  "_answered": 1,
  "_total": 4,
  "_submitted_at": "2026-05-04T10:12:44"
}
```

Read `note` as carefully as `choice`. A card the user left empty has no key in `answers`.
