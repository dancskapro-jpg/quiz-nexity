// node rev-check.mjs <n> — vérifie rev/out/<n>.txt
import { readFileSync, existsSync } from 'node:fs';
const n = process.argv[2];
const W = '/home/claude/hs-work';
const inp = readFileSync(`${W}/rev/in/${n}.txt`, 'utf8').split('\n').filter(Boolean).map((l) => l.split('|'));
const f = `${W}/rev/out/${n}.txt`;
if (!existsSync(f)) { console.log(`AUCUN FICHIER ${f}`); process.exit(1); }
const lines = readFileSync(f, 'utf8').split('\n').filter((l) => l.trim());
const errors = [];
const seen = new Map();
lines.forEach((line, i) => {
  const p = line.split('|');
  if (p.length !== 4) { errors.push(`ligne ${i + 1} : ${p.length} champs au lieu de 4 : ${line.slice(0, 90)}`); return; }
  const [id, v, pub, why] = p.map((x) => x.trim());
  if (seen.has(id)) errors.push(`ligne ${i + 1} : id en double ${id}`);
  seen.set(id, { v, pub, why });
  if (!['G', 'R'].includes(v)) errors.push(`${id} : verdict « ${v} » (G ou R)`);
  if (!['T', 'A'].includes(pub)) errors.push(`${id} : public « ${pub} » (T ou A)`);
  if (v === 'R' && !why) errors.push(`${id} : raison manquante pour R`);
});
inp.forEach(([id, , st]) => {
  const o = seen.get(id);
  if (!o) { errors.push(`id manquant : ${id}`); return; }
  if (st === 'ancienne' && o.v === 'R') errors.push(`${id} est une paire ancienne : verdict G obligatoire`);
});
const ids = inp.map(([id]) => id).filter((id) => seen.has(id)).join(',');
if (lines.map((l) => l.split('|')[0].trim()).join(',') !== ids) errors.push('lignes pas dans le même ordre que l’entrée (ou ids inconnus)');
if (errors.length) { console.log(`rev.${n} : ${errors.length} erreur(s), ${seen.size}/${inp.length} paires`); errors.slice(0, 40).forEach((e) => console.log('  ✗ ' + e)); process.exit(1); }
const nr = [...seen.values()].filter((o) => o.v === 'R').length;
const na = [...seen.values()].filter((o) => o.pub === 'A').length;
const nNew = inp.filter((r) => r[2] === 'nouvelle').length;
console.log(`rev.${n} : OK — ${lines.length} paires, ${nr} retirées (${nNew ? Math.round(100 * nr / nNew) : 0} % des nouvelles), ${na} en public adulte`);
