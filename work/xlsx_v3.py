"""Classeur V2 : toutes les paires du jeu en FR (anciennes choisies en vert, nouvelles sans couleur) + traductions des paires déjà choisies."""
import json, os, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

W = '/home/claude/hs-work'
OUT = sys.argv[1]
F = 'Arial'
font = lambda **k: Font(name=F, **k)
HDR = PatternFill('solid', fgColor='2B2345')
IN = PatternFill('solid', fgColor='FFF7D6')
STATUTS = ['À vérifier', 'OK', 'À revoir', 'À supprimer']
LANGS = [('en', 'EN', 'Anglais (Royaume-Uni)'), ('es', 'ES', 'Espagnol (Espagne)'), ('it', 'IT', 'Italien'),
         ('de', 'DE', 'Allemand'), ('pt', 'PT', 'Portugais (Brésil)'), ('nl', 'NL', 'Néerlandais')]
TITLES = {'classique': 'Classique', 'bouffe': 'Bouffe', 'boulot': 'Boulot', 'voyage': 'Voyage', 'soiree': 'Soirée entre potes',
          'sport': 'Sport', 'ecrans': 'Cinéma & séries', 'musique': 'Musique', 'enfance': 'Enfance & école', 'tech': 'Tech & réseaux',
          'nature': 'Nature & animaux', 'famille': 'Famille (tous âges)', 'fetes': 'Fêtes & saisons', 'ville': 'Ville & transports',
          'imaginaire': 'Et si… ?', 'popculture': 'Pop culture', 'nostalgie': 'Nostalgie', 'reflexe': 'Réflexe', 'noel': 'Noël',
          'ete': 'Été', 'rentree': 'Rentrée', 'vacances': "Vacances d'hiver et de printemps",
          'gaming': 'Jeux vidéo', 'maison': 'Maison & déco', 'dilemmes': 'Dilemmes', 'miroir': 'Miroir / Expert', 'halloween': 'Halloween'}
for _o in json.load(open(f'{W}/new_packs.json', encoding='utf8')):
    TITLES[_o['id']] = _o['title']
GREEN = PatternFill('solid', fgColor='C6EFCE')

fr = json.load(open(f'{W}/final_fr.json', encoding='utf8'))
bank = json.load(open(f'{W}/banque.json', encoding='utf8'))
newp = [dict(id=r[0], pack=r[0].rsplit('-', 1)[0], type=r[4], a=r[2].strip(), b=r[3].strip()) for r in bank if r[5] == 'Création nouvelle']
MERGE = json.load(open(f'{W}/merge.json', encoding='utf8'))
FP = lambda pk: MERGE['map'].get(pk, pk)
FT = lambda pk: MERGE['titles'][FP(pk)]['fr'][0] if FP(pk) in MERGE['titles'] else TITLES[FP(pk)]
packs = MERGE['order'] + ['halloween', 'noel', 'ete', 'rentree', 'vacances']
assert all(FP(o['pack']) in packs for o in fr + newp)
_num = lambda i: int(i.rsplit('-', 1)[1])
allp = sorted([dict(o, origin='old') for o in fr] + [dict(o, origin='new') for o in newp],
              key=lambda o: (packs.index(FP(o['pack'])), list(TITLES).index(o['pack']), _num(o['id'])))
NA = len(allp)
tr, why = {}, {}
for l, _, _ in LANGS:
    m, w = {}, {}
    for n in (1, 2):
        for line in open(f'{W}/out/{l}.{n}.txt', encoding='utf8'):
            p = line.rstrip('\n').split('|')
            if len(p) == 3:
                m[p[0]] = (p[1], p[2])
        cf = f'{W}/out/{l}.{n}.changes.txt'
        if os.path.exists(cf):
            for line in open(cf, encoding='utf8'):
                p = line.rstrip('\n').split('|', 1)
                if len(p) == 2:
                    w[p[0].strip()] = p[1].strip()
    tr[l], why[l] = m, w
cur = {}
for l, _, _ in LANGS:
    c = {}
    for n in (1, 2):
        for line in open(f'{W}/in/{l}.{n}.txt', encoding='utf8'):
            p = line.rstrip('\n').split('|')
            c[p[0]] = (p[3], p[4])
    cur[l] = c


def revision(l, o):
    if o['status'] == 'new':
        return 'Nouvelle', 'Paire ajoutée par toi'
    if o['status'] == 'edited':
        return 'Refaite', 'Tu as modifié le français : traduction refaite'
    if tr[l][o['id']] != cur[l][o['id']]:
        return 'Corrigée', why[l].get(o['id'], 'Rendue plus fidèle au français')
    return 'Inchangée', ''


wb = Workbook()
ws = wb.active
ws.title = "Mode d'emploi"
ws.sheet_view.showGridLines = False
ws.column_dimensions['A'].width = 120
N = len(fr)
rows = [
    ('HORS SUJET — Questions du jeu (version 6.7)', 'title'),
    (f'{NA} paires en français dans le jeu, réparties en {len(packs)} packs (20 packs + 5 de saison, après regroupement) : les {N} que tu avais déjà choisies + {NA - N} nouvelles de la banque du 12/11/2026.', None),
    ('Onglet FR : les paires déjà choisies sont en VERT. Les nouvelles n’ont pas de couleur : colorie en vert celles que tu gardes, comme la dernière fois.', None),
    (f'Traductions : seules les {N} paires déjà choisies sont traduites. Hors français, les nouveaux packs s’affichent « bientôt » dans le jeu.', None),
    ('', None),
    ('Les onglets', 'h'),
    ('• FR : toutes les paires du jeu, une ligne par paire, avec le type de réponse attendu, l’origine (Déjà choisie / Nouvelle) et l’ancien pack quand il a été fusionné.', None),
    ('• EN, ES, IT, DE, PT, NL : le français à côté de la traduction (paires déjà choisies), pour relire une langue.', None),
    ('• Avancement : se calcule tout seul (paires par pack, déjà choisies, nouvelles, relecture des traductions).', None),
    ('', None),
    ('Colonne « Révision » (onglets de langue)', 'h'),
    ('• Inchangée : la traduction était déjà fidèle.', None),
    ('• Corrigée : la traduction s’éloignait du français (sujet ou exemple changé sans raison) ; la colonne « Pourquoi » explique.', None),
    ('• Refaite : tu avais modifié le français, la traduction a été refaite à partir du nouveau texte.', None),
    ('• Nouvelle : une des 5 paires que tu as ajoutées.', None),
    ('', None),
    ('Comment relire', 'h'),
    ('1. Ouvre l’onglet de la langue, filtre par Pack ou par Révision avec les flèches de la ligne d’en-tête.', None),
    ('2. Choisis un Statut dans la liste : À vérifier, OK, À revoir, À supprimer.', None),
    ('3. Si besoin, note un Commentaire ou une meilleure version dans Correction A / Correction B.', None),
    ('Seules les colonnes sur fond jaune pâle sont à remplir. Les autres reflètent ce qui est dans le jeu.', None),
    ('', None),
    ('Exemple de ligne relue (onglet EN)', 'h'),
]
for i, (t, kind) in enumerate(rows, start=1):
    c = ws.cell(row=i, column=1, value=t)
    c.font = font(size=16, bold=True, color='4B2BB5') if kind == 'title' else font(size=11, bold=True, color='2B2345') if kind == 'h' else font(size=10)
    c.alignment = Alignment(wrap_text=True, vertical='top')
ex_hdr = ['ID', 'Question FR', 'Traduction EN', 'Statut', 'Commentaire', 'Correction']
ex = ['classique-001', 'Combien de minutes passes-tu sous la douche ?', 'How many minutes do you spend in the shower?', 'OK', '', '']
r0 = len(rows) + 1
for j, (h, v) in enumerate(zip(ex_hdr, ex), start=1):
    hc = ws.cell(row=r0, column=j, value=h); hc.font = font(bold=True, color='FFFFFF', size=10); hc.fill = HDR
    vc = ws.cell(row=r0 + 1, column=j, value=v); vc.font = font(size=10, italic=True); vc.alignment = Alignment(wrap_text=True, vertical='top')
for j, w in zip('BCDEF', [44, 44, 14, 20, 20]):
    ws.column_dimensions[j].width = w


def header(s, head, widths):
    for j, (h, w) in enumerate(zip(head, widths), start=1):
        c = s.cell(row=1, column=j, value=h)
        c.font = font(bold=True, color='FFFFFF', size=10); c.fill = HDR
        c.alignment = Alignment(wrap_text=True, vertical='center')
        s.column_dimensions[get_column_letter(j)].width = w
    s.freeze_panes = 'D2'


# Onglet FR
s = wb.create_sheet('FR')
header(s, ['ID', 'Pack', 'Type de réponse', 'Question A (majorité)', 'Question B (intrus)', 'Origine', 'Modifiée par toi', 'Ancien pack'], [17, 24, 16, 60, 60, 15, 15, 24])
for i, o in enumerate(allp, start=2):
    old = o['origin'] == 'old'
    vals = [o['id'], FT(o['pack']), (o['type'] or '').replace('*', ''), o['a'], o['b'],
            'Déjà choisie' if old else 'Nouvelle',
            ('Ajoutée par toi' if o['status'] == 'new' else 'Oui' if o['status'] == 'edited' else '') if old else '',
            TITLES[o['pack']] if FP(o['pack']) != o['pack'] else '']
    for j, v in enumerate(vals, start=1):
        c = s.cell(row=i, column=j, value=v); c.font = font(size=10)
        c.alignment = Alignment(wrap_text=j in (4, 5), vertical='top')
        if old: c.fill = GREEN
s.auto_filter.ref = f'A1:H{NA + 1}'

HEAD = ['ID', 'Pack', 'Type', 'FR — Question A', 'Traduction A', 'FR — Question B', 'Traduction B', 'Révision', 'Pourquoi',
        'Statut', 'Commentaire', 'Correction A', 'Correction B']
WID = [15, 18, 11, 46, 46, 46, 46, 12, 34, 13, 26, 34, 34]
for l, code, name in LANGS:
    s = wb.create_sheet(code)
    header(s, [h if 'Traduction' not in h else f'{h} ({code})' for h in HEAD], WID)
    for i, o in enumerate(fr, start=2):
        t = tr[l][o['id']]
        rv, ww = revision(l, o)
        vals = [o['id'], FT(o['pack']), (o['type'] or '').replace('*', ''), o['a'], t[0], o['b'], t[1], rv, ww, 'À vérifier', None, None, None]
        for j, v in enumerate(vals, start=1):
            c = s.cell(row=i, column=j, value=v); c.font = font(size=10)
            c.alignment = Alignment(wrap_text=j in (4, 5, 6, 7, 9), vertical='top')
            if j >= 10: c.fill = IN
    dv = DataValidation(type='list', formula1='"' + ','.join(STATUTS) + '"', allow_blank=True)
    s.add_data_validation(dv); dv.add(f'J2:J{N + 1}')
    s.auto_filter.ref = f'A1:M{N + 1}'
    s.conditional_formatting.add(f'H2:H{N + 1}', FormulaRule(formula=['$H2="Corrigée"'], fill=PatternFill('solid', fgColor='E3F2E1')))
    s.conditional_formatting.add(f'H2:H{N + 1}', FormulaRule(formula=['$H2="Refaite"'], fill=PatternFill('solid', fgColor='DCEBFA')))
    s.conditional_formatting.add(f'H2:H{N + 1}', FormulaRule(formula=['$H2="Nouvelle"'], fill=PatternFill('solid', fgColor='EFE4FB')))
    s.conditional_formatting.add(f'A2:M{N + 1}', FormulaRule(formula=['$J2="À revoir"'], fill=PatternFill('solid', fgColor='FFE1D6')))
    s.conditional_formatting.add(f'A2:M{N + 1}', FormulaRule(formula=['$J2="À supprimer"'], fill=PatternFill('solid', fgColor='F5C6CB')))

# Avancement
a = wb.create_sheet('Avancement', 1)
a.sheet_view.showGridLines = False
a['A1'] = 'Questions du jeu par pack et avancement de la relecture'; a['A1'].font = font(size=14, bold=True, color='4B2BB5')
a['A2'] = 'Calculé automatiquement à partir des onglets (relues = Statut OK ; corrigées = colonne Révision « Corrigée »).'
a['A2'].font = font(size=9, italic=True)
hdr = ['Pack', 'Paires dans le jeu (FR)', 'Déjà choisies', 'Nouvelles', 'Traduites']
for _, code, _ in LANGS:
    hdr += [f'{code} corrigées', f'{code} OK', f'{code} à revoir']
for j, h in enumerate(hdr, start=1):
    c = a.cell(row=4, column=j, value=h); c.font = font(bold=True, color='FFFFFF', size=10); c.fill = HDR
    c.alignment = Alignment(wrap_text=True, horizontal='center')
    a.column_dimensions[get_column_letter(j)].width = 30 if j == 1 else 12 if j <= 5 else 10
rng = lambda sh, col: f"'{sh}'!${col}$2:${col}${(NA if sh == 'FR' else N) + 1}"
for i, p in enumerate(packs, start=5):
    a.cell(row=i, column=1, value=FT(p)).font = font(size=10)
    a.cell(row=i, column=2, value=f'=COUNTIF({rng("FR", "B")},$A{i})').font = font(size=10)
    a.cell(row=i, column=3, value=f'=COUNTIFS({rng("FR", "B")},$A{i},{rng("FR", "F")},"Déjà choisie")').font = font(size=10)
    a.cell(row=i, column=4, value=f'=COUNTIFS({rng("FR", "B")},$A{i},{rng("FR", "F")},"Nouvelle")').font = font(size=10)
    a.cell(row=i, column=5, value=f'=COUNTIF({rng("EN", "B")},$A{i})').font = font(size=10)
    col = 6
    for _, code, _ in LANGS:
        a.cell(row=i, column=col, value=f'=COUNTIFS({rng(code, "B")},$A{i},{rng(code, "H")},"Corrigée")')
        a.cell(row=i, column=col + 1, value=f'=COUNTIFS({rng(code, "B")},$A{i},{rng(code, "J")},"OK")')
        a.cell(row=i, column=col + 2, value=f'=COUNTIFS({rng(code, "B")},$A{i},{rng(code, "J")},"À revoir")')
        for k in range(3): a.cell(row=i, column=col + k).font = font(size=10)
        col += 3
tot = 5 + len(packs)
a.cell(row=tot, column=1, value='Total').font = font(bold=True, size=10)
for j in range(2, len(hdr) + 1):
    L = get_column_letter(j)
    a.cell(row=tot, column=j, value=f'=SUM({L}5:{L}{tot - 1})').font = font(bold=True, size=10)
a.freeze_panes = 'B5'
wb.save(OUT)
print('ok', NA, 'paires FR,', N, 'traduites', len(packs), 'packs', {l: sum(1 for o in fr if revision(l, o)[0] == 'Corrigée') for l, _, _ in LANGS})
