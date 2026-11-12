// node gen-check.mjs <pack> — vérifie gen/out/<pack>.txt
import { readFileSync, existsSync } from 'node:fs';
const pack = process.argv[2];
const W = '/home/claude/hs-work';
const plan = JSON.parse(readFileSync(`${W}/gen/plan.json`, 'utf8'))[pack];
if (!plan) { console.log(`pack inconnu : ${pack}`); process.exit(2); }
const f = `${W}/gen/out/${pack}.txt`;
if (!existsSync(f)) { console.log(`AUCUN FICHIER ${f}`); process.exit(1); }
const TYPES = 'nombre minutes heures pays ville objet activite aliment application marque animal couleur nom expression lieu age prix personne film musique vetement metier moment'.split(' ');
const themes = new Set(readFileSync(`${W}/gen/in/${pack}.themes.txt`, 'utf8').split('\n').filter(Boolean).map((l) => l.split('|')[0]));
const norm = (s) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
const all = JSON.parse(readFileSync(`${W}/all_fr.json`, 'utf8'));
const known = new Set(all.flatMap((p) => [norm(p.a), norm(p.b)]));
const errors = []; const warns = []; const seen = new Set();
const lines = readFileSync(f, 'utf8').split('\n').filter((l) => l.trim());
lines.forEach((line, i) => {
  const w = `ligne ${i + 1}`;
  const p = line.split('|');
  if (p.length !== 5) { errors.push(`${w} : ${p.length} champs au lieu de 5 : ${line.slice(0, 80)}`); return; }
  const [type, diff, theme, a, b] = p.map((x) => x.trim());
  if (!TYPES.includes(type.replace('*', ''))) errors.push(`${w} : type inconnu « ${type} »`);
  if (!['1', '2', '3'].includes(diff)) errors.push(`${w} : difficulté « ${diff} » (1, 2 ou 3)`);
  if (!themes.has(theme)) errors.push(`${w} : thème « ${theme} » absent de ${pack}.themes.txt`);
  for (const [s, q] of [['A', a], ['B', b]]) {
    if (!/\?$/.test(q)) errors.push(`${w} ${s} ne finit pas par « ? » : ${q}`);
    if (q.length < 15) errors.push(`${w} ${s} trop courte : ${q}`);
    if (/[`]/.test(q)) errors.push(`${w} ${s} caractère interdit`);
    const n = norm(q);
    if (known.has(n)) errors.push(`${w} ${s} existe déjà dans le jeu : ${q}`);
    if (seen.has(n)) errors.push(`${w} ${s} en double dans ton fichier : ${q}`);
    seen.add(n);
  }
  if (norm(a) === norm(b)) errors.push(`${w} : A identique à B`);
});
if (lines.length < plan.need) errors.push(`${lines.length} paires, il en faut au moins ${plan.need}`);
const types = {}; lines.forEach((l) => { const t = l.split('|')[0].replace('*', '').trim(); types[t] = (types[t] || 0) + 1; });
if (errors.length) { console.log(`${pack} : ${errors.length} erreur(s), ${lines.length}/${plan.need} paires`); errors.slice(0, 40).forEach((e) => console.log('  ✗ ' + e)); process.exit(1); }
console.log(`${pack} : OK — ${lines.length} paires (minimum ${plan.need}) · types : ${Object.entries(types).sort((x, y) => y[1] - x[1]).map(([t, n]) => `${t} ${n}`).join(', ')}`);
