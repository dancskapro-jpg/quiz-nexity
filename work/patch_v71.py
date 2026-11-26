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
# Nouveaux thèmes (sans questions pour l'instant) et sous-thèmes
THEMES = json.load(open(f'{W}/themes.json', encoding='utf8'))
MERGE['order'] = THEMES['order']
MERGE['cats'].update({o['id']: o['cat'] for o in THEMES['packs']})
# Relecture : paires retirées et paires « adultes » (seulement les parties qui passent rev-check)
REMOVED, ADULT, REMOVED_WHY = set(), set(), {}
for _n in range(1, 18):
    _f = f'{W}/rev/out/{_n}.txt'
    if not os.path.exists(_f) or subprocess.run(['node', f'{W}/rev-check.mjs', str(_n)], capture_output=True).returncode:
        continue
    for _line in open(_f, encoding='utf8'):
        _p = [x.strip() for x in _line.rstrip('\n').split('|')]
        if len(_p) == 4:
            if _p[1] == 'R':
                REMOVED.add(_p[0]); REMOVED_WHY[_p[0]] = _p[3]
            if _p[2] == 'A':
                ADULT.add(_p[0])
print('relecture : retirées', len(REMOVED), 'adultes', len(ADULT))
# Les paires retirées ne sont plus du tout embarquées (page plus légère)
for _pk in BANK:
    BANK[_pk] = [r for r in BANK[_pk] if r[0] not in REMOVED]
ADULT = {i for i in ADULT if i not in REMOVED}

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
        + ',HS_PACKS=' + json.dumps([{k: o[k] for k in ('id', 'accent', 'title', 'description')} for o in NEW_PACKS if o['id'] in MERGE['order']] + [{k: o[k] for k in ('id', 'accent', 'title', 'description')} for o in THEMES['packs']], ensure_ascii=False, separators=(',', ':'))
        + ',HS_XP=new Set(' + json.dumps([o['id'] for o in THEMES['packs']], separators=(',', ':')) + ')'
        + ',HS_PARENT=' + json.dumps({o['id']: o['parent'] for o in THEMES['packs'] if o['parent']}, separators=(',', ':'))
        + ',HS_LOTACC=' + json.dumps(THEMES['lot_accent'], separators=(',', ':'))
        + ',HS_MERGE=' + json.dumps(MERGE['map'], separators=(',', ':'))
        + ',HS_ORDER=' + json.dumps(MERGE['order'], separators=(',', ':'))
        + ',HS_ESS=' + json.dumps(MERGE['essentiels'], separators=(',', ':'))
        + ',HS_RENAME=' + json.dumps({k: v['fr'] for k, v in MERGE['titles'].items()}, ensure_ascii=False, separators=(',', ':'))
        + ',HS_CAT=' + json.dumps(MERGE['cats'], separators=(',', ':'))
        + ',HS_LOTS=' + json.dumps([{'id': o['id'], 'cat': o['cat'], 'price': o['price'], 'title': o['fr'][0], 'description': o['fr'][1]} for o in MERGE['lots']], ensure_ascii=False, separators=(',', ':'))
        + ',HS_REMOVED=new Set(' + json.dumps(sorted(i for i in REMOVED if i in set(keep)), separators=(',', ':')) + ')'
        + ',HS_ADULT=new Set(' + json.dumps(sorted(ADULT), separators=(',', ':')) + ');')
sub('"use strict";(()=>{', '"use strict";(()=>{' + data)
sub('return u?{...e,answersA:u[0],answersB:u[1]}:e});function nu(',
    'return u?{...e,answersA:u[0],answersB:u[1]}:e}).filter(e=>HS_KEEP.has(e.id)).map(e=>{let o=HS_FR[e.id];return o?{...e,a:Ga(o[0]),b:Ga(o[1])}:e}).concat(HS_NEW.map(e=>({...e,a:Ga(e.a),b:Ga(e.b)}))).concat(hsBank()).filter(e=>!HS_REMOVED.has(e.id)).map(hsRemap);hsAddPacks();hsPrune();function nu(')
# Moins de 18 ans : packs adultes et questions adultes masqués
sub('function Lu(e){return e==="perso"?wn():Ke(e)?nu().filter(u=>u.pack===e):[]}function Dn(e){return e==="perso"?wn().length:nu().filter(u=>u.pack===e).length}',
    'function Lu(e){return e==="perso"?wn():Ke(e)&&!hsBlocked(e)?nu().filter(u=>(u.pack===e||HS_PARENT[u.pack]===e)&&hsOkPair(u)):[]}function Dn(e){return e==="perso"?wn().length:nu().filter(u=>(u.pack===e||HS_PARENT[u.pack]===e)&&hsOkPair(u)).length}')
sub('function ye(e){return mi(Q.data.entitlements,e,Va())}', 'function ye(e){return mi(Q.data.entitlements,HS_PARENT[e]||e,Va())}')
sub('function Jr(e){let u=pa([...nu(),...wn()],{packs:e.packs,unlocked:n=>ye(n)&&Ke(n),',
    'function Jr(e){let u=pa([...nu().filter(hsOkPair),...wn()],{packs:hsExpand(e.packs),unlocked:n=>ye(n)&&Ke(n)&&!hsBlocked(n),')
sub('o=b=>{let f=ye(b.id),h=Ke(b.id),C=Lu(b.id).length', 'o=b=>{let f=ye(b.id),h=Ke(b.id)&&!hsBlocked(b.id)&&!hsSoon(b.id),C=Lu(b.id).length')
sub('t("Bient\\xF4t dans cette langue"):t("Verrouill\\xE9")', '(hsBlocked(b.id)?t("R\\xE9serv\\xE9 aux adultes"):t("Bient\\xF4t dans cette langue")):t("Verrouill\\xE9")')
sub('d=b=>ye(b)&&Ke(b),l=s.filter', 'd=b=>ye(b)&&Ke(b)&&!hsBlocked(b)&&!hsSoon(b),l=s.filter')
# thèmes sans questions : « Questions bientôt », sous-thème annoncé par son parent
sub('${f&&!h?"soon":""}', '${(f||hsSoon(b.id))&&!h?"soon":""}')
sub('<span class="pack-sub">${f?', '<span class="pack-sub">${hsSoon(b.id)?t("Questions bient\\xF4t"):f?')
sub('A(f?"clock":"lock")', 'A(f||hsSoon(b.id)?"clock":"lock")')
sub('${Ge(b.id,b.accent)}<span class="pack-title">', '${Ge(b.id,b.accent)}${hsKicker(b.id)}<span class="pack-title">')
sub('m?t("{n} de plus",{n:l.length}):t("{n} \\xE0 d\\xE9bloquer",{n:l.length})', '(L=>L?m?t("{n} de plus",{n:L}):t("{n} \\xE0 d\\xE9bloquer",{n:L}):t("Th\\xE8mes \\xE0 venir"))(l.filter(b=>!hsSoon(b.id)).length)')
sub('pack:b=>{let f=b.dataset.arg;if(!ye(f)){', 'pack:b=>{let f=b.dataset.arg;if(hsSoon(f)){P(t("Les questions de ce th\\xE8me arrivent bient\\xF4t."));return}if(!ye(f)){')
# boutique : visuels des lots, nombre de paires des lots
sub('${l?Ge(l.id,l.accent,"shop-art"):', '${l?Ge(l.id,l.accent,"shop-art"):HS_LOTACC[a]?Ge(a,HS_LOTACC[a],"shop-art"):')
sub('m=d&&d!=="perso"?Dn(d):null', 'm=d&&d!=="perso"?Dn(d):HS_LOTACC[a]&&i?i.grants.reduce((S,g)=>S+(g.startsWith("pack:")?Dn(g.slice(5)):0),0):null')
# compteurs de packs (réglages, à propos) sans les thèmes vides
_i = src.find('let n=Se.filter(s=>Ke(s.id)).length;')
_j = src.find('{done:n,total:Se.length})', _i) + len('{done:n,total:Se.length})')
_old = src[_i:_j]
sub(_old, _old.replace('let n=Se.filter(s=>Ke(s.id)).length;', 'let S=Se.filter(s=>!hsSoon(s.id)),n=S.filter(s=>Ke(s.id)).length;').replace('Se.length', 'S.length'))
sub('pairs:nu().length,packs:Se.length', 'pairs:nu().length,packs:Se.filter(x=>!hsSoon(x.id)).length')
sub('<p class="muted small">${t("Touchez un pack pour le cocher. Les questions sont tir\\xE9es dans les packs coch\\xE9s.")}</p>',
    '${hsAgeToggle()}<p class="muted small">${t("Touchez un pack pour le cocher. Les questions sont tir\\xE9es dans les packs coch\\xE9s.")}</p>')
# Catégories par public dans le choix des packs et dans la boutique
sub('[["essentiels",r("Essentiels")],["thematiques",r("Th\\xE9matiques")],["saisons",r("Collections saisonni\\xE8res")],["perso",r("Personnel")]]',
    '[["famille",r("En famille")],["potes",r("Entre potes")],["adultes",r("Adultes (18+)")],["saisons",r("Collections saisonni\\xE8res")],["perso",r("Personnel")]]')
sub('<h2 class="h-sec">${t("Packs essentiels")}</h2>\n      <div class="shop-list">${Se.filter(a=>{var i;return!a.free&&((i=a.category)!=null?i:"essentiels")==="essentiels"}).map(a=>n(a.productId)).join("")}</div>\n      <h2 class="h-sec">${t("Packs th\\xE9matiques")}</h2>\n      <div class="shop-list">${Se.filter(a=>a.category==="thematiques").map(a=>n(a.productId)).join("")}</div>',
    '${hsShop(n)}')
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
function hsMinors(){return!!(Q.data.settings&&Q.data.settings.hsMinors)}
function hsBlocked(pk){return hsMinors()&&HS_CAT[pk]==="adultes"}
function hsOkPair(p){return!hsMinors()||!(HS_ADULT.has(p.id)||HS_CAT[p.pack]==="adultes")}
function hsAgeToggle(){let m=hsMinors();return`<div class="hs-age"><span class="hs-age-q">${t("Des moins de 18 ans jouent ?")}</span><span class="hs-seg" role="group"><button class="${m?"on":""}" data-hs="minors" data-arg="1" aria-pressed="${m}">${t("Oui")}</button><button class="${m?"":"on"}" data-hs="minors" data-arg="0" aria-pressed="${!m}">${t("Non")}</button></span><span class="muted small hs-age-hint">${m?t("Packs et questions pour adultes masqu\xE9s."):t("Toutes les questions sont disponibles.")}</span></div>`}
function hsShop(n){let cats=[["famille",r("En famille")],["potes",r("Entre potes")],["adultes",r("Adultes (18+)")]];return`<h2 class="h-sec">${t("Lots par public")}</h2><p class="muted small">${t("Tous les packs d’un m\xEAme public, moins cher qu’\xE0 l’unit\xE9.")}</p><div class="shop-list">${HS_LOTS.filter(L=>su.some(x=>x.id===L.id)).map(L=>n(L.id)).join("")}</div>`+cats.map(([k,lab])=>{let ps=Se.filter(a=>!a.free&&a.category===k&&!hsSoon(a.id)),so=Se.filter(a=>a.category===k&&hsSoon(a.id));return ps.length||so.length?`<h2 class="h-sec">${t(lab)}</h2>${ps.length?`<div class="shop-list">${ps.map(a=>n(a.productId)).join("")}</div>`:""}${so.length?`<p class="pack-section-title hs-soon-h">${t("Th\xE8mes \xE0 venir")}</p><div class="shop-list">${so.map(hsSoonCard).join("")}</div>`:""}`:""}).join("")}
function hsSoon(p){if(!HS_XP.has(p))return!1;let c=hsSoon.c||(hsSoon.c=new Set(Ss.map(x=>x.pack)));return!c.has(p)&&!Object.keys(HS_PARENT).some(k=>HS_PARENT[k]===p&&c.has(k))}
function hsExpand(ps){return[...ps,...Object.keys(HS_PARENT).filter(k=>ps.includes(HS_PARENT[k])&&!ps.includes(k))]}
function hsParent(id){let p=HS_PARENT[id];return p&&Se.find(x=>x.id===p)}
function hsKicker(id){let P=hsParent(id);return P?`<span class="hs-kicker">${c(P.title)}</span>`:""}
function hsSoonCard(a){let P=hsParent(a.id);return`<article class="shop-card hs-soon-card">${Ge(a.id,a.accent,"shop-art")}<div class="shop-body"><h3>${c(a.title)}</h3><p class="muted small">${c(a.description)}</p>${P?`<span class="shop-meta">${c(t("Inclus avec le pack {p}",{p:P.title}))}</span>`:""}</div><span class="hs-soon-tag">${A("clock")} ${t("Bient\xF4t")}</span></article>`}
function hsRemap(e){let m=HS_MERGE[e.pack];return m?{...e,pack:m,theme:e.theme===e.pack?m:e.theme}:e}
function hsHeart(x,y,s){return`M${x} ${y+s*.9} C${x-s*1.4} ${y+s*.1} ${x-s*.9} ${y-s*.9} ${x} ${y-s*.25} C${x+s*.9} ${y-s*.9} ${x+s*1.4} ${y+s*.1} ${x} ${y+s*.9} Z`}
function hsArt(e,u,a){switch(e){
case"argent-shopping":return`<path d="M28 34 L76 34 L80 72 L24 72 Z" fill="#fff"/><path d="M40 36 C40 16 64 16 64 36" stroke="${a}" stroke-width="3.6" fill="none" stroke-linecap="round"/><circle cx="40" cy="38" r="2.6" fill="${a}"/><circle cx="64" cy="38" r="2.6" fill="${a}"/><text x="52" y="61" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="16" fill="${a}">€</text><g stroke="${a}" stroke-width="2"><ellipse cx="98" cy="68" rx="13" ry="4.6" fill="${v.gold}"/><ellipse cx="98" cy="61" rx="13" ry="4.6" fill="${v.gold}"/><ellipse cx="98" cy="54" rx="13" ry="4.6" fill="${v.gold}"/></g><g transform="rotate(-14 98 24)"><rect x="83" y="15" width="30" height="17" rx="3" fill="#fff" stroke="${a}" stroke-width="2"/><circle cx="98" cy="23.5" r="4.2" fill="none" stroke="${a}" stroke-width="2"/></g>`+oe(16,20,4,"#fff")+oe(14,58,3,"#fff",.8)
case"amour-couple":return`<path d="${hsHeart(48,38,22)}" fill="#fff"/><path d="${hsHeart(76,46,18)}" fill="${a}"/><path d="${hsHeart(100,18,7)}" fill="${v.rose}" stroke="#fff" stroke-width="1.6"/>`+oe(20,20,4,"#fff")+oe(104,62,3.5,"#fff",.8)
case"psychologie-personnalite":return`<path d="M38 76 L38 63 C26 57 23 41 29 28 C37 11 65 9 76 23 C80 29 80 35 82 40 L89 49 L82 51 L82 58 C82 62 78 64 72 63 L66 62 L66 76 Z" fill="${a}"/><path d="M54 36 m-2 0 a2 2 0 1 1 4 0 a5 5 0 1 1 -10 0 a8 8 0 1 1 16 0 a11 11 0 1 1 -22 0" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round"/><text x="101" y="32" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="22" fill="#fff">?</text><text x="106" y="64" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="16" fill="${v.gold}">!</text>`+oe(14,18,3.5,"#fff",.8)
case"beaute-apparence":return`<ellipse cx="48" cy="36" rx="20" ry="25" fill="#fff" stroke="${a}" stroke-width="3"/><ellipse cx="48" cy="36" rx="14" ry="19" fill="${v.lilac}" opacity=".45"/><path d="M41 23 Q45 19 50 21" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round"/><rect x="45" y="60" width="6" height="16" rx="3" fill="${a}"/><rect x="84" y="46" width="15" height="26" rx="3" fill="${a}"/><rect x="84" y="42" width="15" height="6" rx="1.5" fill="${v.gold}"/><path d="M86 42 L86 30 Q91 24 97 28 L97 42 Z" fill="${v.rose}" stroke="${a}" stroke-width="2"/>`+oe(18,18,4,"#fff")+oe(104,18,3,"#fff",.8)
case"spicy":return`<path d="M30 30 C46 25 70 33 84 51 C92 61 93 72 86 72 C76 60 54 48 34 44 C25 42 23 32 30 30 Z" fill="#B0102C" stroke="${a}" stroke-width="2.4"/><path d="M31 31 C27 24 29 17 36 14" stroke="${v.mint}" stroke-width="4" fill="none" stroke-linecap="round"/><ellipse cx="31" cy="34" rx="6" ry="4.4" fill="${v.mint}" stroke="${a}" stroke-width="2"/><path d="M38 34 C52 33 66 40 76 50" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".55"/><path d="M100 10 C109 21 111 30 105 38 C101 42 92 42 90 36 C88 30 94 28 94 21 C98 25 99 28 99 31 C103 24 103 17 100 10 Z" fill="${v.gold}" stroke="${a}" stroke-width="2"/><circle cx="99" cy="59" r="13" fill="${a}"/><text x="99" y="62.5" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="9" fill="#fff">18+</text>`+oe(16,62,3.5,"#fff",.8)
case"football":return`<path d="M80 70 H116" stroke="#fff" stroke-width="2" opacity=".5" stroke-linecap="round"/><path d="M86 66 L86 26 L112 26 L112 66" stroke="#fff" stroke-width="3.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M92 26 V66 M99 26 V66 M106 26 V66 M86 36 H112 M86 46 H112 M86 56 H112" stroke="#fff" stroke-width="1.2" opacity=".55"/><circle cx="48" cy="42" r="24" fill="#fff" stroke="${a}" stroke-width="3"/><path d="M48 32 L57 38.5 L53.5 49 L42.5 49 L39 38.5 Z" fill="${a}"/><path d="M48 32 V19 M57 38.5 L69 34 M53.5 49 L61 60 M42.5 49 L35 60 M39 38.5 L27 34" stroke="${a}" stroke-width="2.4"/>`+oe(16,16,4,"#fff")+oe(74,14,3,"#fff",.8)
case"basket":return`<circle cx="44" cy="46" r="22" fill="#FF8A3D" stroke="${a}" stroke-width="3"/><path d="M44 24 V68 M22 46 H66 M29 30 Q40 46 29 62 M59 30 Q48 46 59 62" stroke="${a}" stroke-width="2.4" fill="none"/><path d="M36 32 Q40 29 45 29" stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".7"/><rect x="82" y="8" width="30" height="22" rx="3" fill="#fff" stroke="${a}" stroke-width="2"/><rect x="91" y="15" width="12" height="9" fill="none" stroke="${v.rose}" stroke-width="1.8"/><path d="M88 32 L91 48 L103 48 L106 32 M94 32 L95.5 48 M100 32 L98.5 48 M89.5 40 H104.5" stroke="#fff" stroke-width="1.5" fill="none"/><ellipse cx="97" cy="32" rx="10" ry="2.6" fill="none" stroke="${v.rose}" stroke-width="3"/>`+oe(14,16,4,"#fff")+oe(76,64,3,"#fff",.8)
case"tennis":return`<defs><clipPath id="hs-cp-tennis"><ellipse cx="50" cy="28" rx="15" ry="19"/></clipPath></defs><g transform="rotate(-35 50 42)"><ellipse cx="50" cy="28" rx="15" ry="19" fill="#fff"/><g clip-path="url(#hs-cp-tennis)" stroke="${a}" stroke-width="1.3" opacity=".55"><path d="M40 6 V50 M45 6 V50 M50 6 V50 M55 6 V50 M60 6 V50 M32 14 H68 M32 20 H68 M32 26 H68 M32 32 H68 M32 38 H68 M32 44 H68"/></g><ellipse cx="50" cy="28" rx="17" ry="21" fill="none" stroke="${a}" stroke-width="4"/><path d="M44 47 L50 58 L56 47" fill="none" stroke="${a}" stroke-width="3.4" stroke-linejoin="round"/><rect x="47" y="56" width="6" height="20" rx="3" fill="${a}"/></g><circle cx="94" cy="52" r="12" fill="#D7F24A" stroke="${a}" stroke-width="2"/><path d="M84 46 Q93 52 85 60 M104 44 Q95 52 103 60" stroke="#fff" stroke-width="2" fill="none"/>`+oe(100,18,4,"#fff")+oe(16,64,3,"#fff",.8)
case"formule1":return`<path d="M4 34 H20 M2 42 H14 M6 50 H16" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity=".6"/><path d="M98 8 V32" stroke="${a}" stroke-width="2.4" stroke-linecap="round"/><rect x="98" y="8" width="18" height="12" fill="#fff" stroke="${a}" stroke-width="1.6"/><path d="M98 8 h6 v6 h-6 Z M110 8 h6 v6 h-6 Z M104 14 h6 v6 h-6 Z" fill="${a}"/><ellipse cx="62" cy="66" rx="48" ry="3" fill="${a}" opacity=".25"/><rect x="10" y="38" width="13" height="5" rx="1.5" fill="${a}"/><path d="M17 43 L19 52" stroke="${a}" stroke-width="3"/><path d="M16 56 L30 48 L50 46 L57 38 L69 38 L73 46 L98 48 L108 56 Z" fill="#fff" stroke="${a}" stroke-width="2.4" stroke-linejoin="round"/><circle cx="63" cy="40" r="4" fill="${v.gold}" stroke="${a}" stroke-width="1.6"/><path d="M36 52 H90" stroke="${u}" stroke-width="3" stroke-linecap="round"/><rect x="100" y="55" width="14" height="4" rx="1.5" fill="${a}"/><circle cx="34" cy="58" r="9" fill="${a}"/><circle cx="34" cy="58" r="3.4" fill="#fff"/><circle cx="90" cy="58" r="9" fill="${a}"/><circle cx="90" cy="58" r="3.4" fill="#fff"/>`+oe(80,16,4,"#fff")
case"musculation":return`<rect x="28" y="37" width="64" height="6" rx="3" fill="${a}"/><rect x="22" y="22" width="11" height="36" rx="3" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="13" y="28" width="9" height="24" rx="2.5" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="87" y="22" width="11" height="36" rx="3" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="98" y="28" width="9" height="24" rx="2.5" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="44" y="33" width="32" height="14" rx="7" fill="${v.gold}" stroke="${a}" stroke-width="2"/><path d="M60 10 Q64 16 60 19 Q56 16 60 10 Z M72 6 Q75 11 72 13 Q69 11 72 6 Z" fill="#8FD3FF"/>`+oe(16,14,4,"#fff")+oe(104,68,3.5,"#fff",.8)
case"technologie":return`<rect x="24" y="10" width="32" height="60" rx="6" fill="${a}"/><rect x="28" y="17" width="24" height="44" rx="2" fill="#fff"/><rect x="36" y="12.5" width="8" height="2" rx="1" fill="#fff" opacity=".5"/><rect x="31" y="21" width="8" height="8" rx="2" fill="${v.violet}"/><rect x="41" y="21" width="8" height="8" rx="2" fill="${v.mint}"/><rect x="31" y="31" width="8" height="8" rx="2" fill="${v.gold}"/><rect x="41" y="31" width="8" height="8" rx="2" fill="${v.rose}"/><rect x="31" y="45" width="18" height="3" rx="1.5" fill="${a}" opacity=".25"/><rect x="31" y="51" width="12" height="3" rx="1.5" fill="${a}" opacity=".25"/><path d="M78 24 V18 M86 24 V18 M94 24 V18 M78 62 V56 M86 62 V56 M94 62 V56 M70 32 H64 M70 40 H64 M70 48 H64 M102 32 H108 M102 40 H108 M102 48 H108" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><rect x="70" y="24" width="32" height="32" rx="4" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="79" y="33" width="14" height="14" rx="2" fill="${a}"/>`+oe(110,12,3.5,"#fff",.8)
case"ia":return`<path d="M58 22 V12" stroke="${a}" stroke-width="3" stroke-linecap="round"/><circle cx="58" cy="10" r="4.4" fill="${v.gold}" stroke="${a}" stroke-width="2"/><rect x="26" y="34" width="7" height="16" rx="2.5" fill="${a}"/><rect x="83" y="34" width="7" height="16" rx="2.5" fill="${a}"/><rect x="32" y="22" width="52" height="42" rx="11" fill="#fff" stroke="${a}" stroke-width="3"/><circle cx="47" cy="40" r="6.4" fill="${v.mint}" stroke="${a}" stroke-width="2.2"/><circle cx="69" cy="40" r="6.4" fill="${v.mint}" stroke="${a}" stroke-width="2.2"/><circle cx="48.5" cy="38.5" r="1.8" fill="#fff"/><circle cx="70.5" cy="38.5" r="1.8" fill="#fff"/><rect x="46" y="52" width="24" height="5" rx="2.5" fill="${a}"/><path d="M94 58 H104 V68 M104 68 H112" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" opacity=".7"/><circle cx="112" cy="68" r="2.6" fill="#fff"/>`+oe(104,22,6,"#fff")+oe(16,16,3.5,"#fff",.8)
case"luxe":return`<path d="M40 30 L52 16 L76 16 L88 30 Z" fill="#fff"/><path d="M40 30 L88 30 L64 68 Z" fill="#ECE6FF"/><path d="M40 30 L52 16 L76 16 L88 30 L64 68 Z M40 30 H88 M52 16 L58 30 L64 16 L70 30 L76 16 M58 30 L64 68 L70 30" fill="none" stroke="${a}" stroke-width="2.4" stroke-linejoin="round"/><path d="M47 33 L58 52" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".9"/>`+oe(100,22,6,"#fff")+oe(22,56,4,"#fff")+oe(104,60,3,"#fff",.8)
case"millionnaire":return`<g stroke="${a}" stroke-width="2"><rect x="14" y="48" width="50" height="22" rx="3" fill="${v.mint}"/><rect x="18" y="40" width="50" height="22" rx="3" fill="${v.mint}"/><rect x="22" y="32" width="50" height="22" rx="3" fill="#fff"/></g><circle cx="47" cy="43" r="6" fill="none" stroke="${a}" stroke-width="2"/><path d="M28 38 H34 M60 48 H66" stroke="${a}" stroke-width="2" stroke-linecap="round"/><g stroke="${a}" stroke-width="2" stroke-linejoin="round"><path d="M76 68 L81 58 L101 58 L106 68 Z" fill="${v.gold}"/><path d="M86 58 L91 48 L107 48 L111 58 Z" fill="${v.gold}"/></g><path d="M80 18 L86 26 L92 14 L98 26 L104 18 L102 34 L82 34 Z" fill="${v.gold}" stroke="${a}" stroke-width="2" stroke-linejoin="round"/>`+oe(16,18,4,"#fff")+oe(66,14,3,"#fff",.8)
case"mode":return`<path d="M60 20 L60 15 Q60 10 64 10 Q68 10 68 14 Q68 17 64 18" stroke="${a}" stroke-width="2.6" fill="none" stroke-linecap="round"/><path d="M60 20 L32 34 H88 Z" stroke="${a}" stroke-width="3" fill="none" stroke-linejoin="round"/><path d="M51 34 H69 L66 44 L80 72 H40 L54 44 Z" fill="#fff" stroke="${a}" stroke-width="2.4" stroke-linejoin="round"/><path d="M54 44 H66" stroke="${v.rose}" stroke-width="3"/><path d="M46 62 Q60 66 74 62" stroke="${v.lilac}" stroke-width="2" fill="none"/><g transform="rotate(18 100 54)"><path d="M92 44 H106 L110 48 V66 H92 Z" fill="${v.gold}" stroke="${a}" stroke-width="2"/><circle cx="104" cy="50" r="2" fill="${a}"/></g>`+oe(18,18,4,"#fff")+oe(18,60,3,"#fff",.8)
case"culture":return`<path d="M60 30 C48 24 32 24 22 28 V66 C32 62 48 62 60 68 Z" fill="#fff" stroke="${a}" stroke-width="2.4" stroke-linejoin="round"/><path d="M60 30 C72 24 88 24 98 28 V66 C88 62 72 62 60 68 Z" fill="#F1EAFF" stroke="${a}" stroke-width="2.4" stroke-linejoin="round"/><path d="M30 38 Q40 35 52 38 M30 46 Q40 43 52 46 M30 54 Q40 51 52 54 M68 38 Q80 35 90 38 M68 46 Q80 43 90 46" stroke="${a}" stroke-width="1.8" fill="none" opacity=".4"/><circle cx="96" cy="14" r="6" fill="${v.gold}" stroke="${a}" stroke-width="1.8"/><ellipse cx="96" cy="14" rx="11" ry="3.4" fill="none" stroke="#fff" stroke-width="1.8" transform="rotate(-18 96 14)"/>`+oe(24,14,4,"#fff")+oe(60,12,3,"#fff",.8)
case"histoire":return`<path d="M26 26 L60 10 L94 26 Z" fill="#fff" stroke="${a}" stroke-width="2.4" stroke-linejoin="round"/><rect x="26" y="26" width="68" height="6" fill="${a}"/><g fill="#fff" stroke="${a}" stroke-width="2"><rect x="32" y="32" width="8" height="30"/><rect x="48" y="32" width="8" height="30"/><rect x="64" y="32" width="8" height="30"/><rect x="80" y="32" width="8" height="30"/></g><rect x="24" y="62" width="72" height="5" fill="${a}"/><rect x="20" y="67" width="80" height="6" rx="1.5" fill="#fff" stroke="${a}" stroke-width="2"/><circle cx="60" cy="20" r="3" fill="${v.gold}"/>`+oe(104,14,4,"#fff")+oe(12,40,3,"#fff",.8)
case"science":return`<path d="M42 12 V34 L26 64 Q24 70 30 70 H62 Q68 70 66 64 L50 34 V12 Z" fill="#fff" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><path d="M34 50 H58 L66 64 Q68 70 62 70 H30 Q24 70 26 64 Z" fill="${v.rose}"/><path d="M42 12 V34 L26 64 Q24 70 30 70 H62 Q68 70 66 64 L50 34 V12" fill="none" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><rect x="39" y="9" width="14" height="4" rx="2" fill="${a}"/><circle cx="40" cy="60" r="3" fill="#fff"/><circle cx="50" cy="56" r="2" fill="#fff"/><circle cx="54" cy="63" r="2.4" fill="#fff"/><g fill="none" stroke="#fff" stroke-width="2"><ellipse cx="94" cy="32" rx="17" ry="6"/><ellipse cx="94" cy="32" rx="17" ry="6" transform="rotate(60 94 32)"/><ellipse cx="94" cy="32" rx="17" ry="6" transform="rotate(120 94 32)"/></g><circle cx="94" cy="32" r="3.6" fill="${v.gold}"/>`+oe(98,66,4,"#fff")+oe(14,18,3,"#fff",.8)
case"espace":return`<circle cx="24" cy="58" r="11" fill="${v.gold}" stroke="${a}" stroke-width="2"/><ellipse cx="24" cy="58" rx="19" ry="5" fill="none" stroke="#fff" stroke-width="2.2" transform="rotate(-16 24 58)"/><g transform="rotate(32 66 40)"><path d="M58 50 Q66 70 74 50 Z" fill="${v.gold}"/><path d="M66 6 C76 16 78 32 74 50 H58 C54 32 56 16 66 6 Z" fill="#fff" stroke="${a}" stroke-width="2.4" stroke-linejoin="round"/><circle cx="66" cy="26" r="5" fill="${v.lilac}" stroke="${a}" stroke-width="2"/><path d="M58 38 L50 54 L58 50 Z M74 38 L82 54 L74 50 Z" fill="${v.rose}" stroke="${a}" stroke-width="2" stroke-linejoin="round"/></g>`+oe(100,14,4,"#fff")+oe(18,18,3,"#fff",.9)+oe(104,62,2.6,"#fff",.7)+oe(44,12,2.4,"#fff",.7)
case"generations":return`<rect x="10" y="24" width="52" height="34" rx="4" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="16" y="29" width="40" height="9" rx="2" fill="${v.rose}"/><rect x="20" y="42" width="32" height="10" rx="5" fill="none" stroke="${a}" stroke-width="2"/><circle cx="27" cy="47" r="3" fill="${a}"/><circle cx="45" cy="47" r="3" fill="${a}"/><path d="M66 41 H78 M73 36 L78 41 L73 46" stroke="#fff" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/><rect x="84" y="14" width="26" height="50" rx="5" fill="${a}"/><rect x="87" y="19" width="20" height="38" rx="2" fill="#fff"/><path d="${hsHeart(97,36,6)}" fill="${v.rose}"/>`+oe(18,12,4,"#fff")+oe(70,66,3,"#fff",.8)
case"annees80":return`<rect x="20" y="14" width="80" height="52" rx="6" fill="${a}"/><rect x="28" y="20" width="64" height="18" rx="3" fill="#fff"/><path d="M28 32 H92" stroke="${v.rose}" stroke-width="3"/><path d="M28 35.5 H92" stroke="${v.gold}" stroke-width="2"/><text x="60" y="30" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="9" fill="${a}">80</text><rect x="38" y="42" width="44" height="14" rx="7" fill="#fff"/><circle cx="48" cy="49" r="4.4" fill="none" stroke="${a}" stroke-width="2.4"/><circle cx="72" cy="49" r="4.4" fill="none" stroke="${a}" stroke-width="2.4"/><path d="M54 49 H66" stroke="${a}" stroke-width="1.4" opacity=".4"/><path d="M36 66 L42 59 H78 L84 66" fill="#fff" opacity=".25"/>`+oe(10,16,4,"#fff")+oe(110,62,3,"#fff",.8)
case"annees90":return`<circle cx="46" cy="40" r="27" fill="#EDEBFF" stroke="${a}" stroke-width="2.4"/><path d="M28 24 A24 24 0 0 1 52 16" stroke="${v.rose}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/><path d="M66 52 A24 24 0 0 1 50 63" stroke="${v.mint}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/><path d="M24 46 A22 22 0 0 0 30 56" stroke="${v.gold}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/><circle cx="46" cy="40" r="10" fill="#fff" stroke="${a}" stroke-width="2"/><circle cx="46" cy="40" r="4.4" fill="${u}" stroke="${a}" stroke-width="2"/><circle cx="98" cy="22" r="14" fill="${a}"/><text x="98" y="26.5" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="12" fill="#fff">90</text>`+oe(96,60,4,"#fff")+oe(12,70,3,"#fff",.8)
case"annees2000":return`<path d="M60 10 V3" stroke="${a}" stroke-width="2.6" stroke-linecap="round"/><rect x="38" y="8" width="30" height="31" rx="6" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="43" y="13" width="20" height="19" rx="2" fill="${v.mint}"/><path d="M46 26 L51 20 L55 24 L58 21 L61 26" stroke="${a}" stroke-width="1.6" fill="none" opacity=".5"/><rect x="38" y="38" width="30" height="4" rx="2" fill="${a}"/><rect x="38" y="42" width="30" height="30" rx="6" fill="#fff" stroke="${a}" stroke-width="2.4"/><g fill="${a}"><circle cx="46" cy="51" r="1.9"/><circle cx="53" cy="51" r="1.9"/><circle cx="60" cy="51" r="1.9"/><circle cx="46" cy="58" r="1.9"/><circle cx="53" cy="58" r="1.9"/><circle cx="60" cy="58" r="1.9"/><circle cx="46" cy="65" r="1.9"/><circle cx="53" cy="65" r="1.9"/><circle cx="60" cy="65" r="1.9"/></g><circle cx="98" cy="22" r="14" fill="${a}"/><text x="98" y="26.5" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="12" fill="#fff">00</text>`+oe(96,60,4,"#fff")+oe(16,58,3,"#fff",.8)
case"annees2010":return`<path d="M28 52 C28 18 84 18 84 52" stroke="${a}" stroke-width="5" fill="none" stroke-linecap="round"/><rect x="20" y="44" width="16" height="26" rx="7" fill="#fff" stroke="${a}" stroke-width="2.6"/><rect x="76" y="44" width="16" height="26" rx="7" fill="#fff" stroke="${a}" stroke-width="2.6"/><rect x="24" y="50" width="8" height="14" rx="4" fill="${v.rose}"/><rect x="80" y="50" width="8" height="14" rx="4" fill="${v.rose}"/><circle cx="52" cy="60" r="4" fill="#fff"/><path d="M56 60 V44 L66 46 V52" stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="104" cy="18" r="13" fill="${a}"/><text x="104" y="22.5" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="12" fill="#fff">10</text>`+oe(14,18,4,"#fff")+oe(106,62,3,"#fff",.8)
case"genz":return`<rect x="40" y="8" width="34" height="64" rx="7" fill="${a}"/><rect x="44" y="14" width="26" height="52" rx="3" fill="#fff"/><circle cx="50" cy="21" r="3.6" fill="none" stroke="${v.rose}" stroke-width="1.8"/><circle cx="57" cy="21" r="3.6" fill="none" stroke="${v.gold}" stroke-width="1.8"/><circle cx="64" cy="21" r="3.6" fill="none" stroke="${v.violet}" stroke-width="1.8"/><rect x="47" y="29" width="20" height="18" rx="2" fill="${v.lilac}" opacity=".6"/><rect x="47" y="51" width="14" height="3" rx="1.5" fill="${a}" opacity=".3"/><rect x="47" y="57" width="18" height="3" rx="1.5" fill="${a}" opacity=".3"/><circle cx="74" cy="10" r="6" fill="${v.rose}" stroke="#fff" stroke-width="1.6"/><path d="${hsHeart(94,48,8)}" fill="${v.rose}" stroke="#fff" stroke-width="1.6"/><path d="${hsHeart(104,28,5)}" fill="#fff"/><circle cx="22" cy="26" r="13" fill="#fff"/><text x="22" y="31" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="14" fill="${a}">Z</text>`+oe(18,62,4,"#fff")
case"gen-enfance":return`<rect x="18" y="46" width="24" height="24" rx="3" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="44" y="46" width="24" height="24" rx="3" fill="${v.gold}" stroke="${a}" stroke-width="2.4"/><rect x="31" y="21" width="24" height="24" rx="3" fill="${v.mint}" stroke="${a}" stroke-width="2.4" transform="rotate(-6 43 33)"/><g font-family="Unbounded,sans-serif" font-weight="800" font-size="13" text-anchor="middle" fill="${a}"><text x="30" y="63">A</text><text x="56" y="63">B</text><text x="43" y="38" transform="rotate(-6 43 33)">C</text></g><path d="M92 40 Q88 52 94 62 Q98 70 92 76" stroke="#fff" stroke-width="1.8" fill="none"/><ellipse cx="92" cy="26" rx="12" ry="14" fill="${v.rose}" stroke="${a}" stroke-width="2"/><path d="M89 40 L92 37 L95 40 Z" fill="${v.rose}" stroke="${a}" stroke-width="1.6"/><path d="M86 18 Q88 14 92 14" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" opacity=".8"/>`+oe(16,16,4,"#fff")+oe(110,56,3,"#fff",.8)
case"politesse":return`<path d="M46 30 Q42 24 46 18 M56 30 Q52 24 56 18" stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".8"/><ellipse cx="52" cy="66" rx="30" ry="5" fill="#fff" stroke="${a}" stroke-width="2.4"/><path d="M72 42 Q86 42 82 52 Q79 57 70 56" stroke="${a}" stroke-width="3" fill="none"/><path d="M32 36 H72 L68 58 Q66 64 60 64 H44 Q38 64 36 58 Z" fill="#fff" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><path d="M36 44 H70" stroke="${v.lilac}" stroke-width="3"/><path d="M84 18 L99 25 L84 32 Z M114 18 L99 25 L114 32 Z" fill="${v.gold}" stroke="${a}" stroke-width="2" stroke-linejoin="round"/><circle cx="99" cy="25" r="3.4" fill="${a}"/>`+oe(16,16,4,"#fff")+oe(104,60,3.5,"#fff",.8)
case"infractions":return`<rect x="35" y="66" width="6" height="12" fill="${a}"/><rect x="26" y="6" width="24" height="62" rx="8" fill="${a}"/><circle cx="38" cy="19" r="7" fill="#FF4D4D"/><circle cx="38" cy="37" r="7" fill="${v.gold}" opacity=".35"/><circle cx="38" cy="55" r="7" fill="${v.mint}" opacity=".35"/><circle cx="36" cy="17" r="2" fill="#fff" opacity=".8"/><g transform="rotate(8 86 44)"><rect x="68" y="20" width="36" height="46" rx="3" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="68" y="20" width="36" height="9" rx="3" fill="${v.rose}"/><path d="M74 36 H98 M74 43 H94 M74 50 H98" stroke="${a}" stroke-width="2" stroke-linecap="round" opacity=".45"/><circle cx="94" cy="58" r="4.4" fill="none" stroke="${a}" stroke-width="2"/></g>`+oe(108,12,4,"#fff")+oe(12,40,3,"#fff",.8)
case"mangas":return`<rect x="14" y="10" width="48" height="60" rx="3" fill="#fff" stroke="${a}" stroke-width="2.4"/><path d="M14 34 H62 M40 10 V34 M34 34 L28 70" stroke="${a}" stroke-width="2.4"/><path d="M44 40 L58 38 M44 46 L60 50 M44 52 L56 60 M46 58 L52 66" stroke="${a}" stroke-width="1.4" opacity=".5"/><path d="M20 16 L34 28 M22 26 L30 18" stroke="${v.rose}" stroke-width="2.4" stroke-linecap="round"/><circle cx="51" cy="22" r="6" fill="${v.gold}"/><path d="M92 12 L96 22 L106 16 L104 27 L116 30 L106 36 L112 46 L100 43 L98 54 L90 45 L80 50 L82 39 L72 34 L82 29 L78 18 L88 22 Z" fill="#fff" stroke="${a}" stroke-width="2.2" stroke-linejoin="round"/><text x="94" y="38" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="12" fill="${a}">!?</text>`+oe(104,64,4,"#fff")+oe(74,66,2.6,"#fff",.8)
case"business":return`<path d="M16 66 H66" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity=".6"/><rect x="20" y="50" width="9" height="16" rx="2" fill="#fff"/><rect x="34" y="42" width="9" height="24" rx="2" fill="#fff"/><rect x="48" y="32" width="9" height="34" rx="2" fill="#fff"/><path d="M16 44 L30 32 L42 36 L60 16" stroke="${v.gold}" stroke-width="3.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M52 15 L61 15 L61 24" stroke="${v.gold}" stroke-width="3.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M86 36 V30 Q86 27 89 27 H97 Q100 27 100 30 V36" stroke="${a}" stroke-width="3" fill="none"/><rect x="74" y="36" width="38" height="30" rx="4" fill="${a}"/><path d="M74 48 H112" stroke="#fff" stroke-width="1.6" opacity=".35"/><rect x="90" y="44" width="6" height="8" rx="1.5" fill="${v.gold}"/>`+oe(104,14,4,"#fff")
case"inacceptable":return`<circle cx="50" cy="40" r="25" fill="${v.gold}" stroke="${a}" stroke-width="2.6"/><circle cx="41" cy="34" r="5" fill="#fff" stroke="${a}" stroke-width="2"/><circle cx="59" cy="34" r="5" fill="#fff" stroke="${a}" stroke-width="2"/><circle cx="41" cy="34" r="2" fill="${a}"/><circle cx="59" cy="34" r="2" fill="${a}"/><path d="M34 26 L44 24 M66 26 L56 24" stroke="${a}" stroke-width="2.4" stroke-linecap="round"/><rect x="38" y="46" width="24" height="9" rx="3" fill="#fff" stroke="${a}" stroke-width="2"/><path d="M44 46 V55 M50 46 V55 M56 46 V55 M38 50.5 H62" stroke="${a}" stroke-width="1.4"/><path d="M76 16 Q81 25 76 28 Q71 25 76 16 Z" fill="#8FD3FF" stroke="${a}" stroke-width="1.4"/><circle cx="98" cy="54" r="14" fill="#fff" stroke="#E5484D" stroke-width="4.4"/><path d="M88 44 L108 64" stroke="#E5484D" stroke-width="4.4"/>`+oe(104,16,4,"#fff")+oe(14,66,3,"#fff",.8)
case"quel-prix":return`<g transform="rotate(-12 58 40)"><path d="M26 22 H72 L92 40 L72 58 H26 Q22 58 22 54 V26 Q22 22 26 22 Z" fill="#fff" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><circle cx="78" cy="40" r="4" fill="${u}" stroke="${a}" stroke-width="2"/><text x="48" y="50" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="26" fill="${a}">?</text></g><path d="M80 34 Q96 22 102 8" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/><g stroke="${a}" stroke-width="2"><ellipse cx="98" cy="68" rx="12" ry="4.4" fill="${v.gold}"/><ellipse cx="98" cy="61" rx="12" ry="4.4" fill="${v.gold}"/></g>`+oe(14,66,4,"#fff")+oe(110,32,3,"#fff",.8)
case"annulation":return`<rect x="16" y="34" width="12" height="14" rx="2" fill="${a}"/><path d="M28 34 L62 20 V62 L28 48 Z" fill="#fff" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><path d="M34 48 L38 64 H46 L42 50" fill="${a}"/><path d="M70 30 Q76 41 70 52 M78 24 Q88 41 78 58" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/><rect x="86" y="8" width="28" height="18" rx="9" fill="${v.rose}" stroke="${a}" stroke-width="2"/><text x="100" y="21.5" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="11" fill="#fff">!?</text><rect x="88" y="56" width="24" height="16" rx="8" fill="#fff" stroke="${a}" stroke-width="2"/><path d="M96 60 L104 68 M104 60 L96 68" stroke="#E5484D" stroke-width="2.6" stroke-linecap="round"/>`+oe(14,14,4,"#fff")
case"lot:famille":return`<rect x="8" y="14" width="34" height="50" rx="6" fill="#fff" opacity=".22" transform="rotate(-10 25 39)"/><rect x="78" y="14" width="34" height="50" rx="6" fill="#fff" opacity=".22" transform="rotate(10 95 39)"/><path d="M28 40 L60 14 L92 40 Z" fill="${a}" stroke="${a}" stroke-width="2.4" stroke-linejoin="round"/><rect x="76" y="18" width="7" height="14" fill="${a}"/><rect x="34" y="40" width="52" height="32" rx="2" fill="#fff" stroke="${a}" stroke-width="2.4"/><rect x="54" y="52" width="12" height="20" rx="2" fill="${v.gold}" stroke="${a}" stroke-width="2"/><rect x="39" y="46" width="10" height="10" rx="1.5" fill="${v.lilac}" stroke="${a}" stroke-width="1.6"/><rect x="71" y="46" width="10" height="10" rx="1.5" fill="${v.lilac}" stroke="${a}" stroke-width="1.6"/><path d="${hsHeart(60,29,6)}" fill="${v.rose}"/>`+oe(14,70,3,"#fff",.8)+oe(108,8,3.5,"#fff")
case"lot:potes":return`<rect x="8" y="14" width="34" height="50" rx="6" fill="#fff" opacity=".2" transform="rotate(-10 25 39)"/><rect x="78" y="14" width="34" height="50" rx="6" fill="#fff" opacity=".2" transform="rotate(10 95 39)"/><g transform="rotate(-14 46 48)"><path d="M33 26 H57 L53 70 H37 Z" fill="#fff" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><path d="M35 40 H55 L53 70 H37 Z" fill="${v.gold}"/><path d="M33 26 H57 L53 70 H37 Z" fill="none" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><circle cx="42" cy="52" r="1.8" fill="#fff"/><circle cx="48" cy="60" r="1.5" fill="#fff"/></g><g transform="rotate(14 74 48)"><path d="M61 26 H85 L81 70 H65 Z" fill="#fff" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><path d="M63 40 H83 L81 70 H65 Z" fill="${v.rose}"/><path d="M61 26 H85 L81 70 H65 Z" fill="none" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><circle cx="72" cy="54" r="1.8" fill="#fff"/><circle cx="76" cy="62" r="1.5" fill="#fff"/></g><path d="M60 16 V8 M52 18 L47 12 M68 18 L73 12" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>`+oe(16,70,3,"#fff",.8)+oe(106,70,3,"#fff",.8)
case"lot:adultes":return`<rect x="8" y="14" width="34" height="50" rx="6" fill="#fff" opacity=".2" transform="rotate(-10 25 39)"/><path d="M42 14 H66 Q68 36 54 42 Q40 36 42 14 Z" fill="#fff" stroke="${a}" stroke-width="2.6" stroke-linejoin="round"/><path d="M43 24 H65 Q64 36 54 40 Q44 36 43 24 Z" fill="#B0102C"/><path d="M54 42 V64" stroke="${a}" stroke-width="3"/><ellipse cx="54" cy="66" rx="11" ry="3.2" fill="${a}"/><path d="M104 10 A11 11 0 1 0 112 28 A9 9 0 1 1 104 10 Z" fill="${v.gold}"/><circle cx="92" cy="52" r="16" fill="${a}"/><text x="92" y="56" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" font-size="11" fill="#fff">18+</text>`+oe(80,18,3,"#fff",.8)+oe(18,70,3,"#fff",.8)
}return null}
function hsFlag(c){let F={fr:'<rect width="10" height="20" fill="#0055A4"/><rect x="10" width="10" height="20" fill="#fff"/><rect x="20" width="10" height="20" fill="#EF4135"/>',en:'<rect width="30" height="20" fill="#012169"/><path d="M0 0 L30 20 M30 0 L0 20" stroke="#fff" stroke-width="4"/><path d="M0 0 L30 20 M30 0 L0 20" stroke="#C8102E" stroke-width="1.4"/><path d="M15 0 V20 M0 10 H30" stroke="#fff" stroke-width="6.4"/><path d="M15 0 V20 M0 10 H30" stroke="#C8102E" stroke-width="3.6"/>',es:'<rect width="30" height="20" fill="#AA151B"/><rect y="5" width="30" height="10" fill="#F1BF00"/>',it:'<rect width="10" height="20" fill="#009246"/><rect x="10" width="10" height="20" fill="#fff"/><rect x="20" width="10" height="20" fill="#CE2B37"/>',de:'<rect width="30" height="7" fill="#000"/><rect y="6.6" width="30" height="7" fill="#DD0000"/><rect y="13.3" width="30" height="6.7" fill="#FFCE00"/>',pt:'<rect width="30" height="20" fill="#009C3B"/><path d="M15 2.6 L27.4 10 L15 17.4 L2.6 10 Z" fill="#FFDF00"/><circle cx="15" cy="10" r="4.7" fill="#002776"/><path d="M10.5 9.2 Q15 7.9 19.6 10.8" stroke="#fff" stroke-width="1" fill="none"/>',nl:'<rect width="30" height="7" fill="#AE1C28"/><rect y="6.6" width="30" height="7" fill="#fff"/><rect y="13.3" width="30" height="6.7" fill="#21468B"/>'};return`<span class="hs-flag" aria-hidden="true"><svg viewBox="0 0 30 20" preserveAspectRatio="none">${F[c]||F.fr}</svg></span>`}
function hsAddPacks(){for(let p of HS_PACKS){Se.some(x=>x.id===p.id)||Se.push({id:p.id,title:r(p.title),description:r(p.description),free:!1,productId:"pack:"+p.id,accent:p.accent,category:"thematiques"});if(typeof su!="undefined"&&su&&!HS_XP.has(p.id)&&!su.some(x=>x.id==="pack:"+p.id)){let i=su.findIndex(x=>x.id==="tout");su.splice(i<0?su.length:i,0,{id:"pack:"+p.id,title:r(p.title),description:"",referencePrice:"2,99 \u20AC",grants:["pack:"+p.id]})}}for(let x of Se){let n=HS_RENAME[x.id];n&&(x.title=r(n[0]),x.description=r(n[1]));HS_CAT[x.id]&&(x.category=HS_CAT[x.id])}if(typeof su!="undefined"&&su)for(let L of HS_LOTS)if(!su.some(x=>x.id===L.id)){let i=su.findIndex(x=>x.id==="tout");su.splice(i<0?su.length:i,0,{id:L.id,title:r(L.title),description:r(L.description),referencePrice:L.price.replace(" \u20AC","\xA0\u20AC"),grants:Object.keys(HS_CAT).filter(k=>HS_CAT[k]===L.cat&&k!=="classique"&&!HS_PARENT[k]).map(k=>"pack:"+k)})}if(typeof su!="undefined"&&su)for(let x of su){let n=x.grants&&x.grants.length===1&&HS_RENAME[x.grants[0].slice(5)];n&&(x.title=r(n[0]))}let rk=new Map(Se.map((x,i)=>[x.id,HS_ORDER.includes(x.id)?HS_ORDER.indexOf(x.id):100+i]));Se.sort((x,y)=>rk.get(x.id)-rk.get(y.id))}
function hsPrune(){let has=p=>Ss.some(x=>x.pack===p);for(let i=Se.length-1;i>=0;i--)has(Se[i].id)||HS_XP.has(Se[i].id)||Se.splice(i,1);for(let i=qu.length-1;i>=0;i--)has(qu[i].id)||qu.splice(i,1);if(typeof su!="undefined"&&su)for(let i=su.length-1;i>=0;i--){let g=su[i].grants||[];if(g.length===1&&g[0].startsWith("pack:")){if(!has(g[0].slice(5)))su.splice(i,1);else su[i].description=""}}}
function hsCanReroll(){let g=_();return!!g&&g.config&&g.config.mode!=="survie"&&["DISTRIBUTION","REPONSES","DEBAT","VOTE"].includes(g.phase)}
function hsLeft(e){return e.right&&String(e.right).includes('data-act="quit"')&&hsCanReroll()?`<button class="icon-btn hs-reroll" data-hs="reroll" aria-label="${t("Changer de question")}" title="${t("Changer de question")}"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 3.5V8h4.5"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20.5V16h-4.5"/></svg></button>`:'<span class="icon-spacer"></span>'}
function hsLangPill(){let cur=Q.data.settings.lang||"fr",L=pt.find(x=>x.id===cur)||pt[0];return`<details class="hs-lang"><summary aria-label="${t("Changer de langue")}">${hsFlag(cur)}<span class="hs-lang-code">${cur.toUpperCase()}</span><svg class="hs-chev" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary><div class="hs-lang-menu" role="menu">${pt.map(x=>`<button role="menuitemradio" aria-checked="${x.id===cur}" class="hs-lang-item ${x.id===cur?"on":""}" data-hs="lang" data-arg="${x.id}" lang="${x.id}">${hsFlag(x.id)}<span class="hs-lang-name">${x.name}</span>${x.id===cur?'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>':""}</button>`).join("")}</div></details>`}
async function hsSetLang(s){let cur=Q.data.settings.lang||"fr";if(s===cur||!pt.some(x=>x.id===s))return;try{ut()}catch{}if(s!=="fr"&&!await Nt(s)){P(t("Impossible de charger cette langue pour le moment."),"error");return}ct(s),Q.data.settings.lang=s,T(),zu(),j()}
async function hsReroll(){if(!hsCanReroll())return;let g=_();if(!await te({title:t("Changer de question ?"),text:t("Tout le monde re\xE7oit une nouvelle question. M\xEAmes joueurs, m\xEAmes r\xE8gles : on repasse juste le t\xE9l\xE9phone."),ok:t("Nouvelle question")}))return;try{ut()}catch{}try{ie==null||ie.stop()}catch{}let cfg=JSON.parse(JSON.stringify(g.config));try{Q.data.game=null,Ku(cfg)}catch(err){Q.data.game=g,T(!0),P(err instanceof Error?err.message:String(err),"error");return}T(!0),ru(),x(lu,{replace:!0,anim:"fade"}),P(t("Nouvelle question ! Repassez le t\xE9l\xE9phone."),"success")}
document.addEventListener("click",ev=>{let b=ev.target.closest&&ev.target.closest("[data-hs]");document.querySelectorAll("details.hs-lang[open]").forEach(d=>{d.contains(ev.target)||d.removeAttribute("open")});if(!b)return;ev.preventDefault(),ev.stopPropagation();b.dataset.hs==="minors"?(Q.data.settings.hsMinors=b.dataset.arg==="1",T(),j()):b.dataset.hs==="reroll"?hsReroll():b.dataset.hs==="lang"&&(b.closest("details")&&b.closest("details").removeAttribute("open"),hsSetLang(b.dataset.arg))},!0);
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
.hs-age { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; padding: 12px 14px; border-radius: 16px; background: color-mix(in srgb, var(--text) 6%, transparent); }
.hs-age-q { font-weight: 700; }
.hs-seg { display: inline-flex; padding: 3px; border-radius: 999px; background: color-mix(in srgb, var(--text) 10%, transparent); }
.hs-seg button { min-width: 58px; padding: 7px 14px; border-radius: 999px; color: var(--text); font: 700 .9rem/1 var(--f-body, inherit); background: transparent; }
.hs-seg button.on { background: var(--accent, #A78BFA); color: #fff; }
.hs-age-hint { flex-basis: 100%; }
.hs-kicker { display: block; margin-top: 2px; font: 800 .62rem/1.2 var(--f-display); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.hs-kicker + .pack-title { margin-top: 2px; }
.hs-soon-card { opacity: .92; }
.hs-soon-card .shop-art { filter: saturate(.9); }
.hs-soon-tag { display: inline-flex; align-items: center; gap: 4px; flex: none; padding: 6px 10px; border-radius: 999px; font: 700 .78rem/1 var(--f-body, inherit); color: var(--gold, #FFC857); background: color-mix(in srgb, var(--gold, #FFC857) 14%, transparent); }
.hs-soon-tag svg { width: 14px; height: 14px; }
.hs-soon-h { margin-top: 6px; }
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
NCLASS = sum(1 for o in fr if o['pack'] == 'classique' and o['id'] not in REMOVED) + sum(1 for r in BANK.get('classique', []) if r[0] not in REMOVED)
sub('les 610 paires du pack Classique', f'les {NCLASS} paires du pack Classique')
sub('sl="6.3"', 'sl="7.1"')
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
            if len(p) == 4 and p[0] not in REMOVED:
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
    for o in MERGE['lots']:
        j['ui'][o['fr'][0]], j['ui'][o['fr'][1]] = o[l]
    for k, v in MERGE['ui'].items():
        j['ui'][k] = v[l]
    for o in THEMES['packs']:
        j['ui'][o['title']], j['ui'][o['description']] = o[l]
    for k, v in THEMES['ui'].items():
        j['ui'][k] = v[l]
    for k in list(j['ui']):
        if '610 paires du pack Classique' in k:
            j['ui'][k.replace('610', str(NCLASS))] = j['ui'].pop(k).replace('610', str(NCLASS))
    open(f'{OUT}/lang/{l}.js', 'w', encoding='utf8').write(f'window.__hsLang&&window.__hsLang("{l}",' + json.dumps(j, ensure_ascii=False, separators=(',', ':')) + ');')
    print(l, 'revues:', sum(1 for i in order if os.path.exists(f'{W}/out/{l}.1.txt')), 'paires:', sum(len(v) for v in packs.values()), 'sans traduction revue:', len(missing), 'sans aucune:', still)
print('index', len(src), 'paires FR', len(keep) + len(new) + len(bank_new), 'classique', NCLASS)
