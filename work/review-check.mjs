// node review-check.mjs <lang> <n> — vérifie out/<lang>.<n>.txt contre in/<lang>.<n>.txt
import { readFileSync, existsSync } from 'node:fs';
const [lang, n] = process.argv.slice(2);
const dir = '/home/claude/hs-work';
const inp = readFileSync(`${dir}/in/${lang}.${n}.txt`, 'utf8').split('\n').filter(Boolean).map((l) => l.split('|'));
const of = `${dir}/out/${lang}.${n}.txt`;
if (!existsSync(of)) { console.log(`AUCUN FICHIER ${of}`); process.exit(1); }
const out = readFileSync(of, 'utf8').split('\n').filter((l) => l.trim());
const errors = [];
const seen = new Map();
out.forEach((line, i) => {
  const p = line.split('|');
  if (p.length !== 3) { errors.push(`ligne ${i + 1} mal formée (${p.length} champs) : ${line.slice(0, 80)}`); return; }
  const [id, a, b] = p.map((x) => x.trim());
  if (seen.has(id)) errors.push(`${id} en double`);
  seen.set(id, [a, b]);
  if (!a || !b) errors.push(`${id} vide`);
  if (a.toLowerCase() === b.toLowerCase()) errors.push(`${id} A identique à B`);
  if (/[`]/.test(line)) errors.push(`${id} caractère interdit`);
  const end = id.startsWith('reflexe-') ? /[.!]["”»“]?$/ : /\?["”»“]?$/;
  for (const [s, q] of [['A', a], ['B', b]]) {
    if (!end.test(q)) errors.push(`${id} ${s} mauvaise ponctuation finale : ${q}`);
    if (lang === 'es' && q.endsWith('?') && !q.includes('¿')) errors.push(`${id} ${s} sans ¿ : ${q}`);
  }
});
const ids = inp.map((x) => x[0]);
const missing = ids.filter((id) => !seen.has(id));
const extra = [...seen.keys()].filter((id) => !ids.includes(id));
if (missing.length) errors.push(`${missing.length} id manquants : ${missing.slice(0, 10).join(', ')}`);
if (extra.length) errors.push(`${extra.length} id inconnus : ${extra.slice(0, 10).join(', ')}`);
if (!missing.length && [...seen.keys()].join() !== ids.join()) errors.push('ordre différent de l’entrée');
if (errors.length) { console.log(`${lang}.${n} : ${errors.length} erreur(s), ${seen.size}/${ids.length}`); errors.slice(0, 30).forEach((e) => console.log('  ✗ ' + e)); process.exit(1); }
const changed = out.filter((l, i) => { const [id, a, b] = l.split('|'); const x = inp[i]; return x && (a !== x[3] || b !== x[4]); }).length;
console.log(`${lang}.${n} : OK — ${seen.size} paires, ${changed} différentes de la traduction actuelle`);
