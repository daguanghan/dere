#!/usr/bin/env python3
"""dere — build one interactive decision board (a single HTML file) from a JSON data file.

  python3 build_board.py examples/sample_board.json --out ./board/board.html

The page has five tabs: the three-bucket list (decisions are answered inside their cards,
own-actions get a "done" tick), the calendar, the status board, who-is-doing-what, and done-today.
Answers are kept in the browser while typing and POSTed to /submit (see serve.py).
Schema: references/data-schema.md.  Labels: "lang": "en" (default) or "zh".
"""
import argparse, datetime, html, json, pathlib

L = {
 "en": {"buckets": [("A", "🔴 Important & urgent", "Due within 7 days, or directly affects a job, money, a qualification or a commitment"),
                    ("B", "🟠 Important, not urgent", "High impact; due later than 7 days or no deadline"),
                    ("C", "🟡 Urgent, less important", "Time-bound but low impact")],
        "tabs": ["Buckets", "Calendar", "Status board", "Who is doing what", "Done today"],
        "why": "Why it matters", "bg": "Background", "rec": "recommended", "note": "Note (optional)", "done": "Done",
        "top": "Do these three first", "all_b": "All buckets", "all_l": "All lines", "only_q": "Only my decisions",
        "search": "Search", "free_h": "Anything else to tell me or ask me to do?", "free_p": "New decisions, corrections, change of direction",
        "submit": "Submit", "saved": "Saved. You can keep editing and submit again.", "fail": "Submit failed: ",
        "kept": "Your answers stay on this page even if you close it.", "answered": "answered",
        "over": "overdue", "today": "today", "left": "left", "days": "d", "next": "Next:",
        "th": ["Session / person", "Latest", "Waiting for"], "wk": "MTWTFSS", "tomorrow": "tomorrow"},
 "zh": {"buckets": [("A", "🔴 重要且紧急", "7 天内到期，或直接影响职位、钱、资格、承诺"),
                    ("B", "🟠 重要不紧急", "影响大，但截止在 7 天以后或没有截止"),
                    ("C", "🟡 紧急但没那么重要", "有时限，影响小")],
        "tabs": ["三档清单", "日程", "全貌看板", "各方在做什么", "今天已办完"],
        "why": "值什么", "bg": "背景", "rec": "推荐", "note": "补充（选填）", "done": "做完了",
        "top": "今天最该动的三件", "all_b": "全部档", "all_l": "全部线", "only_q": "只看要我定的",
        "search": "搜索", "free_h": "还有什么要告诉我或要我做的？", "free_p": "新的决定、补充或要调的方向",
        "submit": "提交", "saved": "已提交，可以继续改、再提交。", "fail": "提交失败：",
        "kept": "可以分次提交；关掉页面答案也会保留", "answered": "已选",
        "over": "已过", "today": "今天", "left": "还剩", "days": "天", "next": "下一步：",
        "th": ["会话／人", "最近做了什么", "在等什么"], "wk": "一二三四五六日", "tomorrow": "明天"},
}

ap = argparse.ArgumentParser()
ap.add_argument("data")
ap.add_argument("--out", default="board.html")
a = ap.parse_args()
D = json.loads(pathlib.Path(a.data).read_text("utf-8"))
T = L.get(D.get("lang", "en"), L["en"])
E = lambda s: html.escape(str(s if s is not None else ""))
TODAY = datetime.date.fromisoformat(D.get("today") or datetime.date.today().isoformat())


def left(d):
    try:
        return (datetime.date.fromisoformat(d) - TODAY).days if d else None
    except ValueError:
        return None


def due(d):
    n = left(d)
    if n is None:
        return ""
    md = d[5:]
    if n < 0:
        return f'<span class="due hot">{T["over"]} {md} ({-n}{T["days"]})</span>'
    if n == 0:
        return f'<span class="due hot">{T["today"]} {md}</span>'
    cls = "hot" if n <= 2 else ("warm" if n <= 7 else "cool")
    return f'<span class="due {cls}">{md} · {T["left"]} {n}{T["days"]}</span>'


items = D.get("items", [])
for i in items:  # basic validation: every card needs these
    for k in ("id", "bucket", "action"):
        if k not in i:
            raise SystemExit(f"item missing '{k}': {i}")


def card(i):
    top = (f'<span class="tag">{E(i.get("line",""))}</span>' if i.get("line") else "") + \
          (f'<span class="tag own">{E(i.get("owner",""))}</span>' if i.get("owner") else "") + due(i.get("deadline"))
    body = f'<div class="act">{E(i["action"])}</div>'
    if i.get("why"):
        body += f'<div class="why">{T["why"]}: {E(i["why"])}</div>'
    if i.get("bg"):
        body += f'<details class="bgd"><summary>{T["bg"]}</summary><div>{i["bg"] if i.get("bg_html") else E(i["bg"])}</div></details>'
    ctl = ""
    if i.get("options"):
        ctl = '<div class="opts">' + "".join(
            f'<label class="opt"><input type="radio" name="{E(i["id"])}" value="{E(o["key"])}"><span><b>{E(o["key"])}.</b> {E(o["text"])}'
            + (f'<span class="rec">{T["rec"]}</span>' if o.get("recommended") else "") + "</span></label>"
            for o in i["options"]) + f'</div><textarea data-note="{E(i["id"])}" placeholder="{T["note"]}"></textarea>'
    elif i.get("mine"):
        ctl = f'<label class="done"><input type="checkbox" data-done="{E(i["id"])}"> {T["done"]}</label>'
    q = 1 if i.get("options") else 0
    return (f'<div class="card" data-b="{E(i["bucket"])}" data-line="{E(i.get("line",""))}" data-q="{q}" id="c_{E(i["id"])}">'
            f'<div class="top">{top}</div>{body}{ctl}</div>')


def sortkey(i):
    n = left(i.get("deadline"))
    return (0 if i.get("options") else 1, n if n is not None else 999)


cols = ""
for b, title, note in T["buckets"]:
    bi = sorted([i for i in items if i["bucket"] == b], key=sortkey)
    cols += (f'<section class="col" data-col="{b}"><h2>{title} <span class="cnt">{len(bi)}</span></h2><p class="note">{note}</p>'
             + "".join(card(i) for i in bi) + "</section>")

cal = ""
for d in D.get("calendar", []):
    n = left(d["date"])
    wd = T["wk"][datetime.date.fromisoformat(d["date"]).weekday()]
    tag = f' · {T["today"]}' if n == 0 else (f' · {T["tomorrow"]}' if n == 1 else "")
    evs = "".join(f'<li><span class="t">{E(e.get("time",""))}</span> {E(e["what"])}'
                  + (f' <span class="mute">| {E(e["where"])}</span>' if e.get("where") else "") + "</li>" for e in d["events"])
    cal += f'<div class="day{" today" if n == 0 else ""}"><div class="dh">{d["date"][5:]} ({wd}){tag}</div><ul>{evs}</ul></div>'

board = "".join(f'<div class="lc"><h3>{E(l["name"])}<span class="st {E(l.get("light","g"))}">{E(l.get("status",""))}</span></h3>'
                f'<p>{E(l.get("now",""))}</p><p class="nx">{T["next"]} {E(l.get("next",""))}</p></div>' for l in D.get("lines", []))
sess = "".join(f'<tr><td class="k">{E(s["name"])}</td><td>{E(s.get("latest",""))}</td><td>{E(s.get("waiting",""))}</td></tr>'
               for s in D.get("sessions", []))
done = "".join(f"<li>{E(x)}</li>" for x in D.get("done_today", []))
top3 = "".join(f"<li>{E(x)}</li>" for x in D.get("top3", []))
stats = "".join(f'<div class="num"><b>{E(s["value"])}</b>{E(s["label"])}</div>' for s in D.get("stats", []))
lines = sorted({i.get("line", "") for i in items if i.get("line")})
lopt = "".join(f'<option value="{E(x)}">{E(x)}</option>' for x in lines)
tabs = "".join(f'<button{" class=\"on\"" if k == 0 else ""} data-p="{k}">{E(t)}</button>' for k, t in enumerate(T["tabs"]))
bopt = "".join(f'<option value="{b}">{t}</option>' for b, t, _ in T["buckets"])

CSS = """
:root{--bg:#f5f6f8;--card:#fff;--ink:#17212b;--mute:#5d6a78;--line:#dde3ea;--acc:#1f6f8b;--accs:#e6f1f5;
--A:#c0392b;--As:#fdecea;--B:#b9770e;--Bs:#fef5e7;--C:#6f7d00;--Cs:#f6f9e3;--rec:#2e7d4f;--recs:#e7f4ec}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11161c;--card:#1a2129;--ink:#e6ebf0;--mute:#9aa7b4;--line:#2c3540;--acc:#5fb3d0;--accs:#1c2f38;--As:#3a1f1c;--Bs:#3a2e17;--Cs:#2c3117;--recs:#1d3226;--rec:#6cc28f}}
:root[data-theme="dark"]{--bg:#11161c;--card:#1a2129;--ink:#e6ebf0;--mute:#9aa7b4;--line:#2c3540;--acc:#5fb3d0;--accs:#1c2f38;--As:#3a1f1c;--Bs:#3a2e17;--Cs:#2c3117;--recs:#1d3226;--rec:#6cc28f}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15.5px/1.6 -apple-system,"Segoe UI","PingFang SC","Hiragino Sans GB",sans-serif}
.wrap{max-width:1280px;margin:0 auto;padding:12px 16px 110px}h1{font-size:22px;margin:4px 0}.lead{color:var(--mute);margin:0 0 10px;font-size:14px}
.nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:8px 0}.num{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}.num b{font-size:26px;display:block;color:var(--acc)}
.top3{background:var(--card);border:2px solid var(--A);border-radius:10px;padding:8px 14px;margin:10px 0}.top3 h2{font-size:16px;margin:4px 0;color:var(--A)}
.tabs{display:flex;gap:6px;margin:12px 0 4px;flex-wrap:wrap}.tabs button{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:20px;padding:5px 14px;cursor:pointer}.tabs button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.pane{display:none}.pane.on{display:block}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.bar select,.bar input[type=search]{font:inherit;padding:5px 8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
.prog{flex:1;min-width:120px;height:8px;background:var(--line);border-radius:4px;overflow:hidden}.prog i{display:block;height:100%;background:var(--acc);width:0}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;align-items:start}@media (max-width:980px){.grid{grid-template-columns:1fr}}
.col h2{font-size:17px;margin:6px 0 2px}.col .note{color:var(--mute);font-size:13px;margin:0 0 6px}.cnt{font-size:13px;color:var(--mute)}
.col[data-col=A] h2{color:var(--A)}.col[data-col=B] h2{color:var(--B)}.col[data-col=C] h2{color:var(--C)}
.card{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0}
.card[data-b=A]{border-left-color:var(--A)}.card[data-b=B]{border-left-color:var(--B)}.card[data-b=C]{border-left-color:var(--C)}.card.answered{outline:2px solid var(--acc)}.card.hide{display:none}
.top{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:4px}.tag{font-size:12px;padding:0 7px;border-radius:10px;background:var(--accs);color:var(--acc)}.tag.own{background:var(--bg);color:var(--mute);border:1px solid var(--line)}
.due{font-size:12px;padding:0 7px;border-radius:10px;margin-left:auto}.due.hot{background:var(--As);color:var(--A);font-weight:700}.due.warm{background:var(--Bs);color:var(--B)}.due.cool{background:var(--Cs);color:var(--C)}
.act{font-weight:600}.why,.mute{color:var(--mute);font-size:14px}details.bgd summary{cursor:pointer;color:var(--acc);font-size:13px}details.bgd div{font-size:14px;color:var(--mute);margin-top:4px}
.opt{display:flex;gap:8px;align-items:flex-start;padding:6px 8px;border:1px solid var(--line);border-radius:8px;margin:5px 0;cursor:pointer;font-size:14.5px}.opt input{margin-top:4px}.opt.sel{background:var(--accs);border-color:var(--acc)}
.rec{font-size:11px;margin-left:6px;padding:0 5px;border-radius:4px;background:var(--recs);color:var(--rec);font-weight:700}
textarea{width:100%;min-height:40px;margin-top:6px;padding:6px 8px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);font:inherit;font-size:14px}#free{min-height:70px}
label.done{display:inline-flex;gap:6px;margin-top:6px;font-size:14px;color:var(--mute)}
.days{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}.day{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 12px}.day.today{border:2px solid var(--A)}.dh{font-weight:700}.day ul{margin:4px 0 0 16px;padding:0}.day li{font-size:14px;margin:3px 0}.t{color:var(--acc);font-weight:600}
.lines{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}.lc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 12px}.lc h3{font-size:16px;margin:2px 0;display:flex;gap:8px;align-items:center}.lc p{margin:3px 0;font-size:14px}.lc .nx{color:var(--acc)}
.st{font-size:12px;padding:0 7px;border-radius:10px;margin-left:auto}.st.g{background:var(--recs);color:var(--rec)}.st.y{background:var(--Bs);color:var(--B)}.st.r{background:var(--As);color:var(--A)}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);font-size:14px}td,th{padding:6px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{background:var(--accs);color:var(--acc)}.k{font-weight:600;white-space:nowrap}
.foot{position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--line);padding:10px 16px;z-index:6}.foot .in{max-width:1280px;margin:0 auto;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.foot button{font:inherit;font-weight:700;padding:9px 18px;border-radius:8px;border:0;background:var(--acc);color:#fff;cursor:pointer}#msg{font-size:14px;color:var(--mute)}#msg.ok{color:var(--rec)}#msg.err{color:var(--A)}
"""

JS = """
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const store={get(){try{return JSON.parse(localStorage.getItem(FORM_ID)||"{}")}catch(e){return{}}},set(v){try{localStorage.setItem(FORM_ID,JSON.stringify(v))}catch(e){}}};
let st=store.get();st.answers=st.answers||{};st.done=st.done||{};
const qs=$$(".card[data-q='1']");
function restore(){Object.entries(st.answers).forEach(([k,a])=>{if(a.choice){const r=document.querySelector(`input[name="${k}"][value="${a.choice}"]`);if(r)r.checked=true}const t=document.querySelector(`[data-note="${k}"]`);if(t&&a.note)t.value=a.note});
 Object.entries(st.done).forEach(([k,v])=>{const c=document.querySelector(`[data-done="${k}"]`);if(c)c.checked=!!v});if(st.free)$("#free").value=st.free}
function collect(){qs.forEach(c=>{const id=c.id.slice(2),r=c.querySelector("input[type=radio]:checked"),n=c.querySelector("textarea").value.trim();
 if(r||n){st.answers[id]={choice:r?r.value:"",choice_text:r?r.closest("label").innerText.replace(/^\\S+\\.\\s*/,"").trim():"",note:n,title:c.querySelector(".act").innerText}}else delete st.answers[id]});
 $$("[data-done]").forEach(c=>st.done[c.dataset.done]=c.checked);st.free=$("#free").value.trim();store.set(st)}
function refresh(){let n=0;qs.forEach(c=>{const r=c.querySelector("input[type=radio]:checked");c.querySelectorAll(".opt").forEach(l=>l.classList.toggle("sel",l.querySelector("input").checked));c.classList.toggle("answered",!!r);if(r)n++});
 $("#pcount").textContent=`${n} / ${qs.length} ${LBL.answered}`;$("#pbar").style.width=(qs.length?n/qs.length*100:0)+"%"}
function filt(){const b=$("#fb").value,l=$("#fl").value,q=$("#fq").checked,s=$("#fs").value.trim().toLowerCase();
 $$(".card").forEach(c=>{const ok=(!b||c.dataset.b===b)&&(!l||c.dataset.line===l)&&(!q||c.dataset.q==="1")&&(!s||c.innerText.toLowerCase().includes(s));c.classList.toggle("hide",!ok)})}
$$(".tabs button").forEach(b=>b.onclick=()=>{$$(".tabs button").forEach(x=>x.classList.toggle("on",x===b));$$(".pane").forEach(p=>p.classList.toggle("on",p.dataset.p===b.dataset.p))});
["#fb","#fl","#fq","#fs"].forEach(s=>$(s).addEventListener("input",filt));
document.addEventListener("change",()=>{collect();refresh()});document.addEventListener("input",e=>{if(e.target.tagName==="TEXTAREA")collect()});
$("#submit").onclick=async()=>{collect();const m=$("#msg");m.className="";m.textContent="…";
 const payload={_form:FORM_ID,answers:st.answers,done:st.done,free:st.free,_answered:Object.values(st.answers).filter(a=>a.choice).length,_total:qs.length};
 try{const r=await fetch("/submit",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});const j=await r.json();if(!r.ok||!j.ok)throw new Error(j.error||r.status);
  m.className="ok";m.textContent="✅ "+j.saved_at.replace("T"," ")+" — "+LBL.saved}
 catch(e){m.className="err";m.textContent=LBL.fail+e.message}};
restore();refresh();
"""

wd = T["wk"][TODAY.weekday()]
page = f"""<!doctype html><html lang="{E(D.get('lang','en'))}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(D.get('title','dere board'))}</title><style>{CSS}</style></head><body><div class="wrap">
<h1>{E(D.get('title','dere board'))} · {TODAY.isoformat()} ({wd})</h1><p class="lead">{E(D.get('lead',''))}</p>
<div class="nums">{stats}</div>{f'<div class="top3"><h2>{T["top"]}</h2><ol>{top3}</ol></div>' if top3 else ''}
<div class="tabs">{tabs}</div>
<div class="pane on" data-p="0"><div class="bar"><select id="fb"><option value="">{T['all_b']}</option>{bopt}</select>
<select id="fl"><option value="">{T['all_l']}</option>{lopt}</select><label><input type="checkbox" id="fq"> {T['only_q']}</label>
<input type="search" id="fs" placeholder="{T['search']}"><div class="prog"><i id="pbar"></i></div><span id="pcount"></span></div>
<div class="grid">{cols}</div><h2>{T['free_h']}</h2><textarea id="free" placeholder="{T['free_p']}"></textarea></div>
<div class="pane" data-p="1"><div class="days">{cal}</div></div>
<div class="pane" data-p="2"><div class="lines">{board}</div></div>
<div class="pane" data-p="3"><table><tr>{''.join(f'<th>{h}</th>' for h in T['th'])}</tr>{sess}</table></div>
<div class="pane" data-p="4"><ul>{done}</ul></div>
</div><div class="foot"><div class="in"><button id="submit">{T['submit']}</button><span id="msg">{T['kept']}</span></div></div>
<script>const FORM_ID={json.dumps(D.get('form_id','board'), ensure_ascii=False)};const LBL={json.dumps({k: T[k] for k in ('answered','saved','fail')}, ensure_ascii=False)};{JS}</script>
</body></html>"""

out = pathlib.Path(a.out)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(page, "utf-8")
nq = sum(1 for i in items if i.get("options"))
print(f"dere: wrote {out} | {len(items)} cards, {nq} decisions, {sum(1 for i in items if i.get('mine'))} own actions")
