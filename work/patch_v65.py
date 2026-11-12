"""Construit la V6.5 de HORS SUJET à partir du build V6.4 (v64/) :
- ne garde que les paires choisies par Dan (final_fr.json), avec ses corrections FR et 5 nouvelles paires ;
- traductions revues (out/<lang>.<n>.txt si présent, sinon traduction actuelle) ;
- sélecteur de langue en haut à droite de l'accueil ;
- icône « changer de question » en jeu.
Usage : python3 patch.py <dossier de sortie>
"""
import json, os, re, sys

W = '/home/claude/hs-work'
OUT = sys.argv[1]
LANGS = ['en', 'es', 'it', 'de', 'pt', 'nl']
fr = json.load(open(f'{W}/final_fr.json', encoding='utf8'))
keep = [o['id'] for o in fr if o['status'] != 'new']
fr_over = {o['id']: [o['a'], o['b']] for o in fr if o['status'] == 'edited'}
NEW_THEME = {'bouffe-681': 'plats', 'boulot-613': 'vie étudiante', 'boulot-614': 'vie de bureau',
             'boulot-615': 'travail et études', 'soiree-593': 'célébrités'}
new = [dict(id=o['id'], a=o['a'], b=o['b'], pack=o['pack'], difficulty=2, theme=NEW_THEME[o['id']],
            answerType=o['type'], mirror=False, tags=[o['type'], NEW_THEME[o['id']]], compat=4)
       for o in fr if o['status'] == 'new']

src = open(f'{W}/v64/index.html', encoding='utf8').read()


def sub(old, new_, count=1):
    global src
    n = src.count(old)
    if n != count:
        raise SystemExit(f'ancre trouvée {n} fois (attendu {count}) : {old[:90]!r}')
    src = src.replace(old, new_)


# 1. Données : liste blanche + corrections + nouvelles paires, packs vides retirés
data = ('var HS_KEEP=new Set(' + json.dumps(keep, ensure_ascii=False) + '),HS_FR=' + json.dumps(fr_over, ensure_ascii=False)
        + ',HS_NEW=' + json.dumps(new, ensure_ascii=False) + ';')
sub('"use strict";(()=>{', '"use strict";(()=>{' + data)
sub('return u?{...e,answersA:u[0],answersB:u[1]}:e});function nu(',
    'return u?{...e,answersA:u[0],answersB:u[1]}:e}).filter(e=>HS_KEEP.has(e.id)).map(e=>{let o=HS_FR[e.id];return o?{...e,a:Ga(o[0]),b:Ga(o[1])}:e}).concat(HS_NEW.map(e=>({...e,a:Ga(e.a),b:Ga(e.b)})));hsPrune();function nu(')

# 2. Icône « changer de question » à gauche de la barre du jeu (à la place de l'espace vide)
sub(""":'<span class="icon-spacer"></span>'}
    <div class="topbar-mid">""", """:hsLeft(e)}
    <div class="topbar-mid">""")

# 3. Sélecteur de langue en haut à droite de l'accueil
sub("""<main class="page home-page">""", """<main class="page home-page">${hsLangPill()}""")

helpers = r'''
function hsPrune(){let has=p=>Ss.some(x=>x.pack===p);for(let i=Se.length-1;i>=0;i--)has(Se[i].id)||Se.splice(i,1);for(let i=qu.length-1;i>=0;i--)has(qu[i].id)||qu.splice(i,1);if(typeof su!="undefined"&&su)for(let i=su.length-1;i>=0;i--){let g=su[i].grants||[];if(g.length===1&&g[0].startsWith("pack:")){if(!has(g[0].slice(5)))su.splice(i,1);else su[i].description=""}}}
function hsCanReroll(){let g=_();return!!g&&g.config&&g.config.mode!=="survie"&&["DISTRIBUTION","REPONSES","DEBAT","VOTE"].includes(g.phase)}
function hsLeft(e){return e.right&&String(e.right).includes('data-act="quit"')&&hsCanReroll()?`<button class="icon-btn hs-reroll" data-hs="reroll" aria-label="${t("Changer de question")}" title="${t("Changer de question")}"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 3.5V8h4.5"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20.5V16h-4.5"/></svg></button>`:'<span class="icon-spacer"></span>'}
function hsLangPill(){let cur=Q.data.settings.lang||"fr",L=pt.find(x=>x.id===cur)||pt[0];return`<details class="hs-lang"><summary aria-label="${t("Changer de langue")}"><svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9S9.4 5.6 12 3z"/></svg><span class="hs-lang-code">${cur.toUpperCase()}</span><svg class="hs-chev" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary><div class="hs-lang-menu" role="menu">${pt.map(x=>`<button role="menuitemradio" aria-checked="${x.id===cur}" class="hs-lang-item ${x.id===cur?"on":""}" data-hs="lang" data-arg="${x.id}" lang="${x.id}"><span class="hs-lang-badge">${x.id.toUpperCase()}</span><span class="hs-lang-name">${x.name}</span>${x.id===cur?'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>':""}</button>`).join("")}</div></details>`}
async function hsSetLang(s){let cur=Q.data.settings.lang||"fr";if(s===cur||!pt.some(x=>x.id===s))return;try{ut()}catch{}if(s!=="fr"&&!await Nt(s)){P(t("Impossible de charger cette langue pour le moment."),"error");return}ct(s),Q.data.settings.lang=s,T(),zu(),j()}
async function hsReroll(){if(!hsCanReroll())return;let g=_();if(!await te({title:t("Changer de question ?"),text:t("Tout le monde re\xE7oit une nouvelle question. M\xEAmes joueurs, m\xEAmes r\xE8gles : on repasse juste le t\xE9l\xE9phone."),ok:t("Nouvelle question")}))return;try{ut()}catch{}try{ie==null||ie.stop()}catch{}let cfg=JSON.parse(JSON.stringify(g.config));try{Q.data.game=null,Ku(cfg)}catch(err){Q.data.game=g,T(!0),P(err instanceof Error?err.message:String(err),"error");return}T(!0),ru(),x(lu,{replace:!0,anim:"fade"}),P(t("Nouvelle question ! Repassez le t\xE9l\xE9phone."),"success")}
document.addEventListener("click",ev=>{let b=ev.target.closest&&ev.target.closest("[data-hs]");document.querySelectorAll("details.hs-lang[open]").forEach(d=>{d.contains(ev.target)||d.removeAttribute("open")});if(!b)return;ev.preventDefault(),ev.stopPropagation();b.dataset.hs==="reroll"?hsReroll():b.dataset.hs==="lang"&&(b.closest("details")&&b.closest("details").removeAttribute("open"),hsSetLang(b.dataset.arg))},!0);
'''
sub('function lr(){var s,a;let e=document.getElementById("app");', 'function lr(){var s,a;hsPrune();let e=document.getElementById("app");')
sub('document.readyState==="loading"?document.addEventListener("DOMContentLoaded",lr):lr();})();',
    helpers + 'document.readyState==="loading"?document.addEventListener("DOMContentLoaded",lr):lr();})();')

css = '''
.hs-lang { position: absolute; top: calc(env(safe-area-inset-top, 0px) + 14px); right: 16px; z-index: 20; }
.page.home-page { position: relative; }
.hs-lang > summary { list-style: none; display: inline-flex; align-items: center; gap: 7px; height: 38px; padding: 0 12px 0 11px; border-radius: 999px; cursor: pointer; color: var(--text); font: 800 .82rem/1 var(--f-display); letter-spacing: .06em; background: color-mix(in srgb, var(--card) 70%, transparent); border: 1px solid color-mix(in srgb, var(--text) 14%, transparent); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); box-shadow: 0 6px 20px rgba(0,0,0,.18); -webkit-tap-highlight-color: transparent; }
.hs-lang > summary::-webkit-details-marker { display: none; }
.hs-lang > summary:active { transform: scale(.96); }
.hs-lang .hs-chev { opacity: .7; transition: transform .2s; }
.hs-lang[open] .hs-chev { transform: rotate(180deg); }
.hs-lang-menu { position: absolute; right: 0; top: 46px; min-width: 214px; padding: 6px; border-radius: 18px; background: var(--card); border: 1px solid color-mix(in srgb, var(--text) 12%, transparent); box-shadow: 0 18px 50px rgba(0,0,0,.35); animation: hsPop .16s ease-out; transform-origin: top right; }
@keyframes hsPop { from { opacity: 0; transform: scale(.94) translateY(-4px); } to { opacity: 1; transform: none; } }
.hs-lang-item { display: flex; align-items: center; gap: 12px; width: 100%; padding: 10px 12px; border-radius: 12px; color: var(--text); font: 600 .95rem/1.2 var(--f-body, inherit); text-align: left; background: transparent; }
.hs-lang-item:active, .hs-lang-item:hover { background: color-mix(in srgb, var(--text) 8%, transparent); }
.hs-lang-item.on { background: color-mix(in srgb, var(--accent, #A78BFA) 18%, transparent); }
.hs-lang-item svg { margin-left: auto; color: var(--accent, #A78BFA); }
.hs-lang-badge { display: inline-grid; place-items: center; min-width: 34px; height: 24px; padding: 0 6px; border-radius: 8px; font: 800 .72rem/1 var(--f-display); letter-spacing: .06em; background: color-mix(in srgb, var(--text) 10%, transparent); }
.hs-lang-item.on .hs-lang-badge { background: var(--accent, #A78BFA); color: #fff; }
.hs-reroll { color: var(--accent, #A78BFA); }
.hs-reroll svg { transition: transform .35s; }
.hs-reroll:active svg { transform: rotate(-180deg); }
@media (prefers-reduced-motion: reduce) { .hs-lang-menu { animation: none; } .hs-reroll svg { transition: none; } }
'''
sub('\n</style>\n<div id="app"', css + '\n</style>\n<div id="app"')

# Logo : le S de HORS (incliné) était coupé en haut -> marge du viewBox agrandie
sub('viewBox="0 -100 ${a} 215"', 'viewBox="0 -132 ${a} 247"')
sub('viewBox="0 -125 ${s} 135"', 'viewBox="0 -152 ${s} 162"')

# 4. Version et textes chiffrés
NCLASS = sum(1 for o in fr if o['pack'] == 'classique')
sub('les 610 paires du pack Classique', f'les {NCLASS} paires du pack Classique')
sub('sl="6.3"', 'sl="6.5"')
src = src.replace("version {v} (web, test)", "version {v} (web, test)")
os.makedirs(f'{OUT}/lang', exist_ok=True)
open(f'{OUT}/index.html', 'w', encoding='utf8').write(src)

# 5. Fichiers de langue : seulement les paires choisies, traductions revues, textes de l'interface ajoutés
UI = {
 'Changer de question': {'en': 'Change question', 'es': 'Cambiar de pregunta', 'it': 'Cambia domanda', 'de': 'Frage wechseln', 'pt': 'Trocar de pergunta', 'nl': 'Andere vraag'},
 'Changer de question ?': {'en': 'Change the question?', 'es': '¿Cambiar de pregunta?', 'it': 'Cambiare domanda?', 'de': 'Frage wechseln?', 'pt': 'Trocar de pergunta?', 'nl': 'Andere vraag?'},
 'Tout le monde reçoit une nouvelle question. Mêmes joueurs, mêmes règles : on repasse juste le téléphone.': {
   'en': 'Everyone gets a new question. Same players, same rules: just pass the phone around again.',
   'es': 'Todos reciben una pregunta nueva. Mismos jugadores, mismas reglas: solo hay que volver a pasar el móvil.',
   'it': 'Tutti ricevono una nuova domanda. Stessi giocatori, stesse regole: basta ripassare il telefono.',
   'de': 'Alle bekommen eine neue Frage. Gleiche Spieler, gleiche Regeln: Das Handy geht einfach noch mal reihum.',
   'pt': 'Todo mundo recebe uma pergunta nova. Mesmos jogadores, mesmas regras: é só passar o celular de novo.',
   'nl': 'Iedereen krijgt een nieuwe vraag. Dezelfde spelers, dezelfde regels: geef de telefoon gewoon nog een keer door.'},
 'Nouvelle question': {'en': 'New question', 'es': 'Nueva pregunta', 'it': 'Nuova domanda', 'de': 'Neue Frage', 'pt': 'Nova pergunta', 'nl': 'Nieuwe vraag'},
 'Nouvelle question ! Repassez le téléphone.': {'en': 'New question! Pass the phone around again.', 'es': '¡Nueva pregunta! Volved a pasar el móvil.', 'it': 'Nuova domanda! Ripassate il telefono.', 'de': 'Neue Frage! Gebt das Handy wieder herum.', 'pt': 'Nova pergunta! Passem o celular de novo.', 'nl': 'Nieuwe vraag! Geef de telefoon weer door.'},
 'Changer de langue': {'en': 'Change language', 'es': 'Cambiar de idioma', 'it': 'Cambia lingua', 'de': 'Sprache ändern', 'pt': 'Mudar de idioma', 'nl': 'Taal wijzigen'},
}
order = [o['id'] for o in fr]
pack_of = {o['id']: o['pack'] for o in fr}
for l in LANGS:
    j = json.load(open(f'{W}/orig-{l}.json', encoding='utf8'))
    cur = {}
    for pk, txt in j['pairs']['pairs'].items():
        for line in txt.split('\n'):
            p = line.split('|')
            if len(p) == 3:
                cur[p[0]] = (p[1], p[2])
    rev = {}
    for n in (1, 2):
        f = f'{W}/out/{l}.{n}.txt'
        if os.path.exists(f):
            for line in open(f, encoding='utf8'):
                p = line.rstrip('\n').split('|')
                if len(p) == 3 and p[1].strip() and p[2].strip():
                    rev[p[0].strip()] = (p[1].strip(), p[2].strip())
    for line in open(f'{W}/in/{l}.1.txt', encoding='utf8').read().splitlines() + open(f'{W}/in/{l}.2.txt', encoding='utf8').read().splitlines():
        p = line.split('|')
        if p[0] not in rev and p[3].strip() and p[5] != 'fr-modifie':
            rev[p[0]] = (p[3], p[4])
    missing = [i for i in order if i not in rev]
    # Paire sans traduction valable : l'ancienne traduction plutôt que rien (signalé)
    for i in missing:
        if i in cur:
            rev[i] = cur[i]
    still = [i for i in order if i not in rev]
    packs = {}
    for i in order:
        if i in rev:
            packs.setdefault(pack_of[i], []).append(f'{i}|{rev[i][0]}|{rev[i][1]}')
    j['pairs']['pairs'] = {pk: '\n'.join(v) for pk, v in packs.items()}
    ans = [a for a in j['pairs'].get('answers', '').split('\n') if a.split('|')[0] in set(order)]
    j['pairs']['answers'] = '\n'.join(ans)
    for k, v in UI.items():
        j['ui'][k] = v[l]
    for k in list(j['ui']):
        if '610 paires du pack Classique' in k:
            j['ui'][k.replace('610', str(NCLASS))] = j['ui'].pop(k).replace('610', str(NCLASS))
    open(f'{OUT}/lang/{l}.js', 'w', encoding='utf8').write(f'window.__hsLang&&window.__hsLang("{l}",' + json.dumps(j, ensure_ascii=False, separators=(',', ':')) + ');')
    print(l, 'revues:', sum(1 for i in order if os.path.exists(f'{W}/out/{l}.1.txt')), 'paires:', sum(len(v) for v in packs.values()), 'sans traduction revue:', len(missing), 'sans aucune:', still)
print('index', len(src), 'paires FR', len(keep) + len(new))
