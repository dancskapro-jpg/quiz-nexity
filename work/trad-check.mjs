// node trad-check.mjs <lang> <n> — vérifie trad/out/<lang>.<n>.txt
import { readFileSync, existsSync } from 'node:fs';
const [lang, n] = process.argv.slice(2);
const W = '/home/claude/hs-work';
const inp = readFileSync(`${W}/trad/in/${n}.txt`, 'utf8').split('\n').filter(Boolean).map((l) => l.split('|'));
const f = `${W}/trad/out/${lang}.${n}.txt`;
if (!existsSync(f)) { console.log(`AUCUN FICHIER ${f}`); process.exit(1); }
const lines = readFileSync(f, 'utf8').split('\n').filter((l) => l.trim());
const errors = [];
const byId = new Map();
lines.forEach((line, i) => {
  const p = line.split('|');
  if (p.length !== 4) { errors.push(`ligne ${i + 1} : ${p.length} champs au lieu de 4 : ${line.slice(0, 90)}`); return; }
  if (byId.has(p[0])) errors.push(`ligne ${i + 1} : id en double ${p[0]}`);
  byId.set(p[0], p);
});
const FR = lang === 'it' ? /\b(combien|quelle?s? |est-ce|qu’est|qu'est|pourrais-tu|serais-tu|ferais-tu|dirais-tu|aujourd’hui|toujours|jamais)\b/i : /\b(combien|quel|quelle|quels|est-ce|qu’est|qu'est|pourrais-tu|serais-tu|ferais-tu|dirais-tu|aujourd’hui|toujours|jamais)\b/i;
const QS = { es: /^¿/ };
inp.forEach(([id, fa, fb], i) => {
  const p = byId.get(id);
  if (!p) { errors.push(`id manquant : ${id} (ligne ${i + 1} de l'entrée)`); return; }
  const [, a, b] = p.map((x) => x.trim());
  const refl = id.startsWith('reflexe-');
  for (const [s, q, fq] of [['A', a, fa], ['B', b, fb]]) {
    if (!q) { errors.push(`${id} ${s} vide`); continue; }
    if (/`/.test(q)) errors.push(`${id} ${s} : backtick interdit`);
    const end = fq.trim().slice(-1);
    if (end === '?' && !/\?$/.test(q)) errors.push(`${id} ${s} doit finir par « ? » : ${q}`);
    if (end !== '?' && /\?$/.test(q) && refl) errors.push(`${id} ${s} est une consigne, pas de « ? » : ${q}`);
    if (lang === 'es' && end === '?' && !QS.es.test(q)) errors.push(`${id} ${s} doit commencer par « ¿ » : ${q}`);
    if (lang !== 'fr' && FR.test(q)) errors.push(`${id} ${s} contient du français : ${q}`);
    if (q.length < fq.length * 0.4 || q.length > fq.length * 2.2) errors.push(`${id} ${s} longueur suspecte (${q.length} vs ${fq.length} en FR) : ${q}`);
  }
  if (a && a === b && fa.trim() !== fb.trim()) errors.push(`${id} : A identique à B`);
});
const extra = [...byId.keys()].filter((k) => !inp.some(([id]) => id === k));
if (extra.length) errors.push(`ids inconnus : ${extra.slice(0, 5).join(', ')}`);
const order = lines.map((l) => l.split('|')[0]).join(',') === inp.map(([id]) => id).filter((id) => byId.has(id)).join(',');
if (!order) errors.push('les lignes ne sont pas dans le même ordre que l’entrée');
if (errors.length) { console.log(`${lang}.${n} : ${errors.length} erreur(s), ${byId.size}/${inp.length} paires`); errors.slice(0, 40).forEach((e) => console.log('  ✗ ' + e)); process.exit(1); }
const adapt = lines.filter((l) => l.split('|')[3].trim()).length;
console.log(`${lang}.${n} : OK — ${lines.length} paires, ${adapt} adaptées`);
