import os
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "vicinocasa-demo-change-this-secret")

# V1 DEMO: sample data and messages are kept in RAM and reset when the process restarts.
# No real professional is represented. Replace these profiles only after obtaining consent.
PROFESSIONALS = {
    "p1": {
        "name": "Marco Rossi", "business": "Rossi Pronto Intervento",
        "category": "Fabbro", "area": "Prima Porta", "areas": "Prima Porta, Labaro",
        "description": "Piccoli interventi su porte, serrature e chiusure.",
        "status": "green", "updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "badge": "Profilo dimostrativo"
    },
    "p2": {
        "name": "Luca Bianchi", "business": "Bianchi Idraulica",
        "category": "Idraulico", "area": "Prima Porta", "areas": "Prima Porta, Labaro, Saxa Rubra",
        "description": "Riparazioni idrauliche, rubinetti e piccole perdite.",
        "status": "yellow", "updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "badge": "Profilo dimostrativo"
    },
    "p3": {
        "name": "Andrea Verdi", "business": "Verdi Impianti",
        "category": "Elettricista", "area": "Prima Porta", "areas": "Prima Porta, Labaro",
        "description": "Interventi elettrici domestici e piccoli guasti.",
        "status": "red", "updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "badge": "Profilo dimostrativo"
    },
    "p4": {
        "name": "Sara Neri", "business": "Neri Tuttofare",
        "category": "Tuttofare", "area": "Prima Porta", "areas": "Prima Porta, Labaro",
        "description": "Montaggio, riparazioni domestiche e piccoli lavori.",
        "status": "green", "updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "badge": "Profilo dimostrativo"
    },
}

STATUS = {
    "green": ("Disponibile", "Può ricevere richieste"),
    "yellow": ("Impegnato", "Potrebbe rispondere più tardi"),
    "red": ("Non disponibile", "Al momento non riceve richieste"),
}
CATEGORIES = ["Tutte", "Fabbro", "Idraulico", "Elettricista", "Tuttofare"]
MESSAGES = {}  # demo-only RAM storage


def status_dot(value):
    return {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(value, "⚪")


def base_context():
    return {
        "categories": CATEGORIES,
        "status": STATUS,
        "status_dot": status_dot,
        "demo": True,
    }


SHELL = r"""
<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#123b35">
<title>{{ title }} · VicinoCasa</title>
<style>
:root{--ink:#18312e;--muted:#63716e;--green:#176b53;--green2:#dff4e9;--cream:#f7f7f2;--line:#e3e9e4;--white:#fff;--gold:#f5c85b;--red:#d9534f}
*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
a{color:inherit;text-decoration:none}.top{background:#123b35;color:#fff}.nav{max-width:1100px;margin:auto;padding:16px 20px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{font-size:1.25rem;font-weight:850;letter-spacing:-.04em}.brand span{color:#f5c85b}.navlinks{display:flex;gap:18px;align-items:center;font-size:.92rem}.navlinks a{opacity:.94}
.wrap{max-width:1100px;margin:auto;padding:28px 20px 56px}.hero{padding:32px 0 22px}.eyebrow{font-size:.78rem;text-transform:uppercase;letter-spacing:.12em;font-weight:800;color:var(--green)}
h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.05;letter-spacing:-.055em;margin:10px 0 16px;max-width:760px}
h2{font-size:1.45rem;letter-spacing:-.03em;margin:0 0 10px}h3{margin:0 0 6px;font-size:1.08rem}
p{margin:0 0 12px}.muted{color:var(--muted)}.small{font-size:.84rem}.demo{background:#fff6d9;border:1px solid #f1df9e;border-radius:12px;padding:11px 14px;font-size:.86rem;margin:12px 0 22px}
.panel{background:var(--white);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 5px 18px #173c3510}
.filters{display:grid;grid-template-columns:1fr 1fr auto;gap:12px;align-items:end;margin:20px 0 24px}
label{display:block;font-size:.83rem;font-weight:750;margin-bottom:6px}
select,input,textarea{font:inherit;width:100%;padding:12px 13px;border:1px solid #ccd8d1;border-radius:10px;background:#fff;color:var(--ink)}
.btn{display:inline-flex;justify-content:center;align-items:center;gap:8px;border:0;border-radius:11px;padding:12px 17px;background:var(--green);color:#fff;font-weight:750;cursor:pointer;font:inherit;font-weight:750}
.btn.secondary{background:#eaf2ed;color:var(--ink)}.btn.dark{background:#123b35}.btn:disabled{opacity:.45;cursor:not-allowed}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.prohead{display:flex;gap:13px;align-items:flex-start}.avatar{width:52px;height:52px;border-radius:15px;display:grid;place-items:center;background:#e1f1e7;color:#176b53;font-weight:850;font-size:1.15rem;flex-shrink:0}
.tag{display:inline-block;font-size:.73rem;font-weight:800;padding:4px 8px;border-radius:999px;background:#f0f2ef;color:#58645f;margin:4px 0 10px}
.status{font-size:.88rem;font-weight:800;margin:8px 0 3px}.status.green{color:#16734f}.status.yellow{color:#9a6c00}.status.red{color:#b63d39}
.cardfoot{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:16px;padding-top:14px;border-top:1px solid var(--line)}
.pill{border-radius:999px;background:#f1f5f2;padding:5px 9px;font-size:.78rem}
.empty{padding:28px;text-align:center;color:var(--muted);background:#fff;border:1px dashed #cbd7cf;border-radius:16px}
.two{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(300px,.95fr);gap:20px;align-items:start}
.chatbox{display:flex;flex-direction:column;gap:10px;min-height:210px;max-height:390px;overflow:auto;padding:12px;background:#f6f8f5;border-radius:12px;margin:14px 0}
.bubble{max-width:88%;background:#fff;border:1px solid var(--line);border-radius:13px;padding:10px 12px;align-self:flex-start;overflow-wrap:anywhere}
.bubble.mine{align-self:flex-end;background:#dff4e9;border-color:#c5e7d4}.bubble small{display:block;color:var(--muted);font-size:.72rem;margin-top:4px}
.row{display:flex;gap:9px}.row>*{min-width:0}.row input{flex:1}
.status-options{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:12px 0}.status-option{padding:12px 8px;text-align:center;border:1px solid var(--line);border-radius:12px;background:#fff;cursor:pointer}.status-option strong{display:block;font-size:.88rem}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:18px 0}.kpi{background:#f5f8f5;border-radius:12px;padding:13px}.kpi strong{display:block;font-size:1.35rem}
footer{border-top:1px solid var(--line);padding:22px 20px;color:var(--muted);font-size:.82rem;text-align:center}
@media(max-width:700px){.nav{align-items:flex-start}.navlinks{gap:10px;flex-wrap:wrap;justify-content:flex-end;font-size:.83rem}.filters,.grid,.two{grid-template-columns:1fr}.wrap{padding:20px 15px 42px}.hero{padding-top:22px}.panel{padding:16px}.cardfoot{align-items:flex-start;flex-direction:column}.status-options{grid-template-columns:1fr}.row{flex-direction:column}}
</style>
</head>
<body>
<header class="top"><div class="nav">
<a class="brand" href="{{ url_for('home') }}">Vicino<span>Casa</span></a>
<nav class="navlinks"><a href="{{ url_for('home') }}">Trova un professionista</a><a href="{{ url_for('professional_area') }}">Area artigiano</a></nav>
</div></header>
<main class="wrap">
{% block content %}{% endblock %}
</main>
<footer>VicinoCasa · Nome provvisorio · Demo dimostrativa, non ancora un servizio operativo.</footer>
</body></html>
"""

HOME = r"""
{% extends "shell" %}{% block content %}
<section class="hero">
<div class="eyebrow">Il quartiere, le persone giuste</div>
<h1>Un professionista vicino.<br>Un contatto diretto.</h1>
<p class="muted" style="max-width:650px">Trova fabbri, idraulici, elettricisti e altri professionisti della zona. Guarda il loro stato di disponibilità e avvia una conversazione senza intermediari.</p>
<div class="demo"><strong>Anteprima dimostrativa:</strong> i professionisti mostrati sono profili di esempio. Disponibilità e messaggi non sono reali.</div>
</section>
<form class="filters panel" method="get" action="{{ url_for('home') }}">
<div><label for="category">Di cosa hai bisogno?</label><select id="category" name="categoria">{% for c in categories %}<option value="{{ c }}" {% if c==selected_category %}selected{% endif %}>{{ c }}</option>{% endfor %}</select></div>
<div><label for="area">Quartiere</label><select id="area" name="zona"><option {% if selected_area=='Prima Porta' %}selected{% endif %}>Prima Porta</option><option {% if selected_area=='Labaro' %}selected{% endif %}>Labaro</option><option {% if selected_area=='Saxa Rubra' %}selected{% endif %}>Saxa Rubra</option><option {% if selected_area=='Tutte le zone' %}selected{% endif %}>Tutte le zone</option></select></div>
<button class="btn" type="submit">Cerca</button>
</form>
<div style="display:flex;align-items:end;justify-content:space-between;gap:12px;margin-bottom:14px"><div><h2>Professionisti della zona</h2><p class="muted small">Lo stato è indicato dal professionista e può cambiare.</p></div><span class="pill">{{ pros|length }} profili demo</span></div>
{% if pros %}
<div class="grid">{% for id,p in pros %}
<article class="panel">
<div class="prohead"><div class="avatar">{{ p.name.split()[0][0] }}{{ p.name.split()[-1][0] }}</div><div style="flex:1"><h3>{{ p.business }}</h3><div class="muted small">{{ p.name }} · {{ p.category }}</div><span class="tag">{{ p.badge }}</span></div></div>
<div class="status {{ p.status }}">{{ status_dot(p.status) }} {{ status[p.status][0] }}</div><p class="muted small">{{ status[p.status][1] }} · Aggiornato {{ p.updated }}</p>
<p>{{ p.description }}</p><p class="muted small"><strong>Zone servite:</strong> {{ p.areas }}</p>
<div class="cardfoot"><span class="pill">📍 {{ p.area }}</span><a class="btn" href="{{ url_for('professional_profile', pro_id=id) }}">Vedi profilo e scrivi</a></div>
</article>
{% endfor %}</div>
{% else %}<div class="empty"><h3>Nessun professionista trovato</h3><p>Prova un'altra categoria o zona.</p><a class="btn secondary" href="{{ url_for('home') }}">Mostra tutti</a></div>{% endif %}
<section class="panel" style="margin-top:22px"><h2>Sei un artigiano?</h2><p class="muted">Gestisci la tua disponibilità e fai conoscere la tua attività nel quartiere.</p><a class="btn dark" href="{{ url_for('professional_area') }}">Apri l'area artigiano</a></section>
{% endblock %}
"""

PROFILE = r"""
{% extends "shell" %}{% block content %}
<p class="small muted"><a href="{{ url_for('home') }}">← Torna ai professionisti</a></p>
<div class="demo"><strong>Profilo di esempio.</strong> Questo contatto è simulato e non invia messaggi a una persona reale.</div>
<div class="two">
<section class="panel">
<div class="prohead"><div class="avatar" style="width:64px;height:64px;font-size:1.3rem">{{ p.name.split()[0][0] }}{{ p.name.split()[-1][0] }}</div><div><h1 style="font-size:2rem;margin:0 0 6px">{{ p.business }}</h1><p class="muted">{{ p.name }} · {{ p.category }}</p><span class="tag">{{ p.badge }}</span></div></div>
<div class="status {{ p.status }}" style="margin-top:20px;font-size:1rem">{{ status_dot(p.status) }} {{ status[p.status][0] }}</div><p class="muted small">{{ status[p.status][1] }} · Ultimo aggiornamento: {{ p.updated }}</p>
<hr style="border:0;border-top:1px solid var(--line);margin:18px 0">
<h3>Di cosa si occupa</h3><p>{{ p.description }}</p><h3 style="margin-top:18px">Zone servite</h3><p>{{ p.areas }}</p>
<p class="muted small">Prezzo, tempi e intervento vengono concordati direttamente tra cliente e professionista.</p>
</section>
<section class="panel">
<h2>Scrivi al professionista</h2><p class="muted small">Nella versione reale questa chat sarà privata e accessibile solo alle persone autorizzate.</p>
<div class="chatbox" aria-live="polite">
{% for m in messages %}<div class="bubble {% if m.sender=='Tu' %}mine{% endif %}">{{ m.text }}<small>{{ m.sender }} · {{ m.time }}</small></div>{% else %}<div class="bubble">Buongiorno! Come possiamo aiutarti?<small>Messaggio automatico demo</small></div>{% endfor %}
</div>
<form method="post" action="{{ url_for('send_message', pro_id=pro_id) }}">
<label for="message">Il tuo messaggio</label><textarea id="message" name="message" rows="3" maxlength="600" placeholder="Descrivi brevemente di cosa hai bisogno…" required></textarea>
<button class="btn" style="width:100%;margin-top:10px" type="submit">Invia messaggio demo</button>
</form>
<p class="muted small" style="margin-top:10px">Non inserire dati personali o informazioni sensibili nella demo.</p>
</section>
</div>
{% endblock %}
"""

PRO_AREA = r"""
{% extends "shell" %}{% block content %}
<section class="hero"><div class="eyebrow">Area artigiano · demo</div><h1>La tua disponibilità,<br>chiara a tutti.</h1><p class="muted" style="max-width:650px">In un servizio reale, da qui potrai aggiornare il semaforo e gestire i messaggi ricevuti. Per ora puoi provare le funzioni dimostrative.</p></section>
<div class="demo"><strong>Attenzione:</strong> quest'area non ha ancora login né account personali. Le modifiche sono temporanee e visibili nella demo.</div>
<div class="two">
<section class="panel">
<h2>Seleziona un profilo demo</h2>
<form method="get" action="{{ url_for('professional_area') }}">
<label for="pro">Professionista</label><select name="pro" id="pro">{% for id,p in all_pros %}<option value="{{ id }}" {% if id==selected_id %}selected{% endif %}>{{ p.business }} — {{ p.category }}</option>{% endfor %}</select>
<button class="btn secondary" style="margin-top:10px" type="submit">Apri profilo</button>
</form>
<hr style="border:0;border-top:1px solid var(--line);margin:20px 0">
<h2>Il tuo semaforo</h2><p class="muted small">Stato attuale: <strong>{{ status[selected_pro.status][0] }}</strong></p>
<form method="post" action="{{ url_for('update_status', pro_id=selected_id) }}">
<div class="status-options">
<button class="status-option" name="status" value="green" type="submit"><span style="font-size:1.4rem">🟢</span><strong>Disponibile</strong><span class="small muted">Ricevo richieste</span></button>
<button class="status-option" name="status" value="yellow" type="submit"><span style="font-size:1.4rem">🟡</span><strong>Impegnato</strong><span class="small muted">Rispondo dopo</span></button>
<button class="status-option" name="status" value="red" type="submit"><span style="font-size:1.4rem">🔴</span><strong>Non disponibile</strong><span class="small muted">Pausa richieste</span></button>
</div></form>
</section>
<section class="panel">
<h2>Richieste dimostrative</h2>
<p class="muted small">Questi messaggi provengono soltanto dalla demo e non da clienti reali.</p>
{% set found = namespace(count=0) %}
{% for m in inbox %}
<div style="padding:13px 0;border-bottom:1px solid var(--line)"><div style="display:flex;justify-content:space-between;gap:10px"><strong>Richiesta demo</strong><span class="muted small">{{ m.time }}</span></div><p style="margin:6px 0">{{ m.text }}</p><span class="pill">Chat dimostrativa</span></div>
{% set found.count = found.count + 1 %}
{% endfor %}
{% if found.count==0 %}<div class="empty"><p>Non ci sono messaggi demo per questo profilo.</p><p class="small">Apri il profilo dalla vetrina e invia un messaggio di prova.</p><a class="btn secondary" href="{{ url_for('professional_profile', pro_id=selected_id) }}">Prova la chat</a></div>{% endif %}
</section>
</div>
{% endblock %}
"""

# Register the parent template in Jinja's in-memory loader.
from jinja2 import DictLoader
app.jinja_loader = DictLoader({"shell": SHELL, "home.html": HOME, "profile.html": PROFILE, "professional.html": PRO_AREA})


@app.route("/")
def home():
    category = request.args.get("categoria", "Tutte")
    area = request.args.get("zona", "Prima Porta")
    pros = []
    for pid, p in PROFESSIONALS.items():
        if category != "Tutte" and p["category"] != category:
            continue
        if area != "Tutte le zone" and area not in p["areas"].split(", "):
            continue
        pros.append((pid, p))
    return render_template_string(HOME, title="Professionisti del quartiere", pros=pros,
        selected_category=category, selected_area=area, **base_context())


@app.route("/professionista/<pro_id>")
def professional_profile(pro_id):
    p = PROFESSIONALS.get(pro_id)
    if not p:
        abort(404)
    messages = MESSAGES.get(pro_id, [])
    return render_template_string(PROFILE, title=p["business"], p=p, pro_id=pro_id,
        messages=messages, **base_context())


@app.route("/professionista/<pro_id>/messaggio", methods=["POST"])
def send_message(pro_id):
    if pro_id not in PROFESSIONALS:
        abort(404)
    text = request.form.get("message", "").strip()
    if not text:
        return redirect(url_for("professional_profile", pro_id=pro_id))
    if len(text) > 600:
        text = text[:600]
    MESSAGES.setdefault(pro_id, []).append({
        "sender": "Tu", "text": text,
        "time": datetime.now().strftime("%H:%M")
    })
    # The demo intentionally does not deliver messages to any real person.
    return redirect(url_for("professional_profile", pro_id=pro_id))


@app.route("/area-artigiano")
def professional_area():
    selected_id = request.args.get("pro", "p1")
    if selected_id not in PROFESSIONALS:
        selected_id = "p1"
    inbox = MESSAGES.get(selected_id, [])
    return render_template_string(PRO_AREA, title="Area artigiano", all_pros=list(PROFESSIONALS.items()),
        selected_id=selected_id, selected_pro=PROFESSIONALS[selected_id], inbox=inbox, **base_context())


@app.route("/area-artigiano/<pro_id>/disponibilita", methods=["POST"])
def update_status(pro_id):
    if pro_id not in PROFESSIONALS:
        abort(404)
    new_status = request.form.get("status")
    if new_status not in STATUS:
        abort(400)
    PROFESSIONALS[pro_id]["status"] = new_status
    PROFESSIONALS[pro_id]["updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    return redirect(url_for("professional_area", pro=pro_id))


@app.errorhandler(404)
def not_found(_):
    return render_template_string(SHELL.replace("{% block content %}{% endblock %}", """
    <section class="panel"><h1 style="font-size:2rem">Pagina non trovata</h1><p>Il contenuto richiesto non è disponibile.</p><a class="btn" href="/">Torna alla home</a></section>
    """), title="Pagina non trovata"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
