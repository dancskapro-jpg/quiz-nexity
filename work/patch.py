"""Construit la V6.5 de HORS SUJET à partir du build V6.4 (v64/) :
- ne garde que les paires choisies par Dan (final_fr.json), avec ses corrections FR et 5 nouvelles paires ;
- traductions revues (out/<lang>.<n>.txt si présent, sinon traduction actuelle) ;
- sélecteur de langue en haut à droite de l'accueil ;
- icône « changer de question » en jeu.
Usage : python3 patch.py <dossier de sortie>
"""
import json, os, re, subprocess, sys

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

# Banque du 12/11/2026 : les 9 000 nouvelles paires (les anciennes sont déjà dans fr)
TYPE_MAP = [
    (('montant', 'budget', 'euros', 'prix'), 'prix'),
    (('minutes',), 'minutes'),
    (('jours', 'heure', 'heures', 'durée'), 'heures'),
    (('fréquence', 'nombre'), 'nombre'),
    (('moment', 'mois'), 'moment'),
    (('personne', 'surnom'), 'personne'),
    (('ville',), 'ville'),
    (('mot / objet / lieu', 'mot / adjectif', 'réplique', 'réaction', 'conseil', 'excuse', 'phrase', 'question',
      'compliment', 'message', 'secret', 'vérité', 'mot'), 'expression'),
    (('lieu', 'enseigne', 'site', 'pièce'), 'lieu'),
    (('plat', 'boisson'), 'aliment'),
    (('chanson', 'danse'), 'musique'),
    (('vêtement', 'accessoire'), 'vetement'),
    (('objet', 'outil', 'cadeau', 'photo', 'emoji'), 'objet'),
    (('activité',), 'activite'),
]


def map_type(t):
    t = (t or '').strip().lower()
    for keys, v in TYPE_MAP:
        words = set(re.findall(r'\w+', t))
        if any(k == t or (' ' in k and k in t) or k in words for k in keys):
            return v
    return 'reponse'


bank = json.load(open(f'{W}/banque.json', encoding='utf8'))
bank_new = [r for r in bank if r[5] == 'Création nouvelle']
BANK = {}
for r in bank_new:
    pk = r[0].rsplit('-', 1)[0]
    BANK.setdefault(pk, []).append([r[0], map_type(r[4]), r[2].strip(), r[3].strip()])
NEW_PACKS = json.load(open(f'{W}/new_packs.json', encoding='utf8'))
MERGE = json.load(open(f'{W}/merge.json', encoding='utf8'))
final_pack = lambda pk: MERGE['map'].get(pk, pk)

src = open(f'{W}/v64/index.html', encoding='utf8').read()


def sub(old, new_, count=1):
    global src
    n = src.count(old)
    if n != count:
        raise SystemExit(f'ancre trouvée {n} fois (attendu {count}) : {old[:90]!r}')
    src = src.replace(old, new_)


# 1. Données : liste blanche + corrections + nouvelles paires, packs vides retirés
data = ('var HS_KEEP=new Set(' + json.dumps(keep, ensure_ascii=False) + '),HS_FR=' + json.dumps(fr_over, ensure_ascii=False)
        + ',HS_NEW=' + json.dumps(new, ensure_ascii=False)
        + ',HS_BANK=' + json.dumps(BANK, ensure_ascii=False, separators=(',', ':'))
        + ',HS_PACKS=' + json.dumps([{k: o[k] for k in ('id', 'accent', 'title', 'description')} for o in NEW_PACKS if o['id'] in MERGE['order']], ensure_ascii=False, separators=(',', ':'))
        + ',HS_MERGE=' + json.dumps(MERGE['map'], separators=(',', ':'))
        + ',HS_ORDER=' + json.dumps(MERGE['order'], separators=(',', ':'))
        + ',HS_ESS=' + json.dumps(MERGE['essentiels'], separators=(',', ':'))
        + ',HS_RENAME=' + json.dumps({k: v['fr'] for k, v in MERGE['titles'].items()}, ensure_ascii=False, separators=(',', ':')) + ';')
sub('"use strict";(()=>{', '"use strict";(()=>{' + data)
sub('return u?{...e,answersA:u[0],answersB:u[1]}:e});function nu(',
    'return u?{...e,answersA:u[0],answersB:u[1]}:e}).filter(e=>HS_KEEP.has(e.id)).map(e=>{let o=HS_FR[e.id];return o?{...e,a:Ga(o[0]),b:Ga(o[1])}:e}).concat(HS_NEW.map(e=>({...e,a:Ga(e.a),b:Ga(e.b)}))).concat(hsBank()).map(hsRemap);hsAddPacks();hsPrune();function nu(')
# Visuels des nouveaux packs
sub('return s+((o=i[e])!=null?o:i.classique)+"</svg>"}', 'return s+((o=hsArt(e,u,a))!=null?o:(o=i[e])!=null?o:i.classique)+"</svg>"}')
# Nouveau type de réponse générique (« une réponse courte »)
sub('moment:r("Moment")});var Ua=', 'moment:r("Moment"),reponse:r("R\\xE9ponse")});var Ua=')
# Hors français : une paire pas encore traduite est retirée (au lieu d'être montrée en français)
sub('if(s&&s.length===e.length)return s;', 'if(s&&s.__n===e.length)return s;')
sub('if(!l)return d;let m=i.get(d.id)', 'if(!l)return d.pack==="perso"?d:null;let m=i.get(d.id)')
sub('{}}});return bn.set(u,o),o}', '{}}}).filter(Boolean);o.__n=e.length;return bn.set(u,o),o}')

# 2. Icône « changer de question » à gauche de la barre du jeu (à la place de l'espace vide)
sub(""":'<span class="icon-spacer"></span>'}
    <div class="topbar-mid">""", """:hsLeft(e)}
    <div class="topbar-mid">""")

# 3. Sélecteur de langue en haut à droite de l'accueil
sub("""<main class="page home-page">""", """<main class="page home-page">${hsLangPill()}""")

helpers = r'''
function hsBank(){let out=[];for(let[pk,rows]of Object.entries(HS_BANK))for(let[id,ty,a,b]of rows){let m=pk==="miroir";out.push({id,a:Ga(a),b:Ga(b),pack:pk,difficulty:m?3:2,theme:pk,answerType:ty,mirror:m,tags:[ty,pk,...m?["miroir"]:[]],compat:4})}return out}
function hsRemap(e){let m=HS_MERGE[e.pack];return m?{...e,pack:m,theme:e.theme===e.pack?m:e.theme}:e}
function hsHeart(x,y,s){return`M${x} ${y+s*.9} C${x-s*1.4} ${y+s*.1} ${x-s*.9} ${y-s*.9} ${x} ${y-s*.25} C${x+s*.9} ${y-s*.9} ${x+s*1.4} ${y+s*.1} ${x} ${y+s*.9} Z`}
function hsArt(e,u,a){switch(e){
case"argent-shopping":return`<path d="M28 34 L76 34 L80 72 L24 72 Z" fill="#fff"/><path d="M40 36 C40 16 64 16 64 36" stroke="${a}" stroke-width="3.6" fill="none" stroke-linecap="round"/><circle cx="40" cy="38" r="2.6" fill="${a}"/><circle cx="64" cy="38" r="2.6" fill="${a}"/><text x="52" y="61" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="16" fill="${a}">€</text><g stroke="${a}" stroke-width="2"><ellipse cx="98" cy="68" rx="13" ry="4.6" fill="${v.gold}"/><ellipse cx="98" cy="61" rx="13" ry="4.6" fill="${v.gold}"/><ellipse cx="98" cy="54" rx="13" ry="4.6" fill="${v.gold}"/></g><g transform="rotate(-14 98 24)"><rect x="83" y="15" width="30" height="17" rx="3" fill="#fff" stroke="${a}" stroke-width="2"/><circle cx="98" cy="23.5" r="4.2" fill="none" stroke="${a}" stroke-width="2"/></g>`+oe(16,20,4,"#fff")+oe(14,58,3,"#fff",.8)
case"amour-couple":return`<path d="${hsHeart(48,38,22)}" fill="#fff"/><path d="${hsHeart(76,46,18)}" fill="${a}"/><path d="${hsHeart(100,18,7)}" fill="${v.rose}" stroke="#fff" stroke-width="1.6"/>`+oe(20,20,4,"#fff")+oe(104,62,3.5,"#fff",.8)
case"psychologie-personnalite":return`<path d="M38 76 L38 63 C26 57 23 41 29 28 C37 11 65 9 76 23 C80 29 80 35 82 40 L89 49 L82 51 L82 58 C82 62 78 64 72 63 L66 62 L66 76 Z" fill="${a}"/><path d="M54 36 m-2 0 a2 2 0 1 1 4 0 a5 5 0 1 1 -10 0 a8 8 0 1 1 16 0 a11 11 0 1 1 -22 0" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round"/><text x="101" y="32" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="22" fill="#fff">?</text><text x="106" y="64" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="16" fill="${v.gold}">!</text>`+oe(14,18,3.5,"#fff",.8)
case"spicy":return`<path d="M30 30 C46 25 70 33 84 51 C92 61 93 72 86 72 C76 60 54 48 34 44 C25 42 23 32 30 30 Z" fill="#B0102C" stroke="${a}" stroke-width="2.4"/><path d="M31 31 C27 24 29 17 36 14" stroke="${v.mint}" stroke-width="4" fill="none" stroke-linecap="round"/><ellipse cx="31" cy="34" rx="6" ry="4.4" fill="${v.mint}" stroke="${a}" stroke-width="2"/><path d="M38 34 C52 33 66 40 76 50" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".55"/><path d="M100 10 C109 21 111 30 105 38 C101 42 92 42 90 36 C88 30 94 28 94 21 C98 25 99 28 99 31 C103 24 103 17 100 10 Z" fill="${v.gold}" stroke="${a}" stroke-width="2"/><circle cx="99" cy="59" r="13" fill="${a}"/><text x="99" y="62.5" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="9" fill="#fff">18+</text>`+oe(16,62,3.5,"#fff",.8)
}return null}
function hsFlag(c){let F={fr:'<rect width="10" height="20" fill="#0055A4"/><rect x="10" width="10" height="20" fill="#fff"/><rect x="20" width="10" height="20" fill="#EF4135"/>',en:'<rect width="30" height="20" fill="#012169"/><path d="M0 0 L30 20 M30 0 L0 20" stroke="#fff" stroke-width="4"/><path d="M0 0 L30 20 M30 0 L0 20" stroke="#C8102E" stroke-width="1.4"/><path d="M15 0 V20 M0 10 H30" stroke="#fff" stroke-width="6.4"/><path d="M15 0 V20 M0 10 H30" stroke="#C8102E" stroke-width="3.6"/>',es:'<rect width="30" height="20" fill="#AA151B"/><rect y="5" width="30" height="10" fill="#F1BF00"/>',it:'<rect width="10" height="20" fill="#009246"/><rect x="10" width="10" height="20" fill="#fff"/><rect x="20" width="10" height="20" fill="#CE2B37"/>',de:'<rect width="30" height="7" fill="#000"/><rect y="6.6" width="30" height="7" fill="#DD0000"/><rect y="13.3" width="30" height="6.7" fill="#FFCE00"/>',pt:'<rect width="30" height="20" fill="#009C3B"/><path d="M15 2.6 L27.4 10 L15 17.4 L2.6 10 Z" fill="#FFDF00"/><circle cx="15" cy="10" r="4.7" fill="#002776"/><path d="M10.5 9.2 Q15 7.9 19.6 10.8" stroke="#fff" stroke-width="1" fill="none"/>',nl:'<rect width="30" height="7" fill="#AE1C28"/><rect y="6.6" width="30" height="7" fill="#fff"/><rect y="13.3" width="30" height="6.7" fill="#21468B"/>'};return`<span class="hs-flag" aria-hidden="true"><svg viewBox="0 0 30 20" preserveAspectRatio="none">${F[c]||F.fr}</svg></span>`}
function hsAddPacks(){for(let p of HS_PACKS){Se.some(x=>x.id===p.id)||Se.push({id:p.id,title:r(p.title),description:r(p.description),free:!1,productId:"pack:"+p.id,accent:p.accent,category:"thematiques"});if(typeof su!="undefined"&&su&&!su.some(x=>x.id==="pack:"+p.id)){let i=su.findIndex(x=>x.id==="tout");su.splice(i<0?su.length:i,0,{id:"pack:"+p.id,title:r(p.title),description:"",referencePrice:"2,99 \u20AC",grants:["pack:"+p.id]})}}for(let x of Se){let n=HS_RENAME[x.id];n&&(x.title=r(n[0]),x.description=r(n[1]));HS_ORDER.includes(x.id)&&(x.category=HS_ESS.includes(x.id)?void 0:"thematiques")}if(typeof su!="undefined"&&su)for(let x of su){let n=x.grants&&x.grants.length===1&&HS_RENAME[x.grants[0].slice(5)];n&&(x.title=r(n[0]))}let rk=new Map(Se.map((x,i)=>[x.id,HS_ORDER.includes(x.id)?HS_ORDER.indexOf(x.id):100+i]));Se.sort((x,y)=>rk.get(x.id)-rk.get(y.id))}
function hsPrune(){let has=p=>Ss.some(x=>x.pack===p);for(let i=Se.length-1;i>=0;i--)has(Se[i].id)||Se.splice(i,1);for(let i=qu.length-1;i>=0;i--)has(qu[i].id)||qu.splice(i,1);if(typeof su!="undefined"&&su)for(let i=su.length-1;i>=0;i--){let g=su[i].grants||[];if(g.length===1&&g[0].startsWith("pack:")){if(!has(g[0].slice(5)))su.splice(i,1);else su[i].description=""}}}
function hsCanReroll(){let g=_();return!!g&&g.config&&g.config.mode!=="survie"&&["DISTRIBUTION","REPONSES","DEBAT","VOTE"].includes(g.phase)}
function hsLeft(e){return e.right&&String(e.right).includes('data-act="quit"')&&hsCanReroll()?`<button class="icon-btn hs-reroll" data-hs="reroll" aria-label="${t("Changer de question")}" title="${t("Changer de question")}"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 3.5V8h4.5"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20.5V16h-4.5"/></svg></button>`:'<span class="icon-spacer"></span>'}
function hsLangPill(){let cur=Q.data.settings.lang||"fr",L=pt.find(x=>x.id===cur)||pt[0];return`<details class="hs-lang"><summary aria-label="${t("Changer de langue")}">${hsFlag(cur)}<span class="hs-lang-code">${cur.toUpperCase()}</span><svg class="hs-chev" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary><div class="hs-lang-menu" role="menu">${pt.map(x=>`<button role="menuitemradio" aria-checked="${x.id===cur}" class="hs-lang-item ${x.id===cur?"on":""}" data-hs="lang" data-arg="${x.id}" lang="${x.id}">${hsFlag(x.id)}<span class="hs-lang-name">${x.name}</span>${x.id===cur?'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>':""}</button>`).join("")}</div></details>`}
async function hsSetLang(s){let cur=Q.data.settings.lang||"fr";if(s===cur||!pt.some(x=>x.id===s))return;try{ut()}catch{}if(s!=="fr"&&!await Nt(s)){P(t("Impossible de charger cette langue pour le moment."),"error");return}ct(s),Q.data.settings.lang=s,T(),zu(),j()}
async function hsReroll(){if(!hsCanReroll())return;let g=_();if(!await te({title:t("Changer de question ?"),text:t("Tout le monde re\xE7oit une nouvelle question. M\xEAmes joueurs, m\xEAmes r\xE8gles : on repasse juste le t\xE9l\xE9phone."),ok:t("Nouvelle question")}))return;try{ut()}catch{}try{ie==null||ie.stop()}catch{}let cfg=JSON.parse(JSON.stringify(g.config));try{Q.data.game=null,Ku(cfg)}catch(err){Q.data.game=g,T(!0),P(err instanceof Error?err.message:String(err),"error");return}T(!0),ru(),x(lu,{replace:!0,anim:"fade"}),P(t("Nouvelle question ! Repassez le t\xE9l\xE9phone."),"success")}
document.addEventListener("click",ev=>{let b=ev.target.closest&&ev.target.closest("[data-hs]");document.querySelectorAll("details.hs-lang[open]").forEach(d=>{d.contains(ev.target)||d.removeAttribute("open")});if(!b)return;ev.preventDefault(),ev.stopPropagation();b.dataset.hs==="reroll"?hsReroll():b.dataset.hs==="lang"&&(b.closest("details")&&b.closest("details").removeAttribute("open"),hsSetLang(b.dataset.arg))},!0);
'''
sub('function lr(){var s,a;let e=document.getElementById("app");', 'function lr(){var s,a;hsAddPacks();hsPrune();let e=document.getElementById("app");')
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
.hs-flag { display: inline-block; flex: none; width: 24px; height: 16px; border-radius: 4px; overflow: hidden; box-shadow: 0 0 0 1px rgba(255,255,255,.22), 0 1px 3px rgba(0,0,0,.3); }
.hs-flag svg { display: block; width: 100%; height: 100%; }
.hs-lang-item .hs-flag { width: 30px; height: 20px; border-radius: 5px; }
.hs-lang-item .hs-flag svg { margin: 0; color: inherit; }
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
NCLASS = sum(1 for o in fr if o['pack'] == 'classique') + len(BANK.get('classique', []))
sub('les 610 paires du pack Classique', f'les {NCLASS} paires du pack Classique')
sub('sl="6.3"', 'sl="6.7"')
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
 'Réponse': {'en': 'Answer', 'es': 'Respuesta', 'it': 'Risposta', 'de': 'Antwort', 'pt': 'Resposta', 'nl': 'Antwoord'},
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
            packs.setdefault(final_pack(pack_of[i]), []).append(f'{i}|{rev[i][0]}|{rev[i][1]}')
    # Nouvelles paires de la banque : seulement les parties traduites qui passent la vérification
    nnew = 0
    for n in range(1, 16):
        f = f'{W}/trad/out/{l}.{n}.txt'
        if not os.path.exists(f) or subprocess.run(['node', f'{W}/trad-check.mjs', l, str(n)], capture_output=True).returncode:
            continue
        for line in open(f, encoding='utf8'):
            p = line.rstrip('\n').split('|')
            if len(p) == 4:
                packs.setdefault(final_pack(p[0].rsplit('-', 1)[0]), []).append(f'{p[0]}|{p[1].strip()}|{p[2].strip()}')
                nnew += 1
    print(l, 'nouvelles traduites :', nnew)
    j['pairs']['pairs'] = {pk: '\n'.join(v) for pk, v in packs.items()}
    ans = [a for a in j['pairs'].get('answers', '').split('\n') if a.split('|')[0] in set(order)]
    j['pairs']['answers'] = '\n'.join(ans)
    for k, v in UI.items():
        j['ui'][k] = v[l]
    for o in NEW_PACKS:
        j['ui'][o['title']], j['ui'][o['description']] = o[l]
    for k, v in MERGE['titles'].items():
        j['ui'][v['fr'][0]], j['ui'][v['fr'][1]] = v[l]
    for k in list(j['ui']):
        if '610 paires du pack Classique' in k:
            j['ui'][k.replace('610', str(NCLASS))] = j['ui'].pop(k).replace('610', str(NCLASS))
    open(f'{OUT}/lang/{l}.js', 'w', encoding='utf8').write(f'window.__hsLang&&window.__hsLang("{l}",' + json.dumps(j, ensure_ascii=False, separators=(',', ':')) + ');')
    print(l, 'revues:', sum(1 for i in order if os.path.exists(f'{W}/out/{l}.1.txt')), 'paires:', sum(len(v) for v in packs.values()), 'sans traduction revue:', len(missing), 'sans aucune:', still)
print('index', len(src), 'paires FR', len(keep) + len(new) + len(bank_new), 'classique', NCLASS)
