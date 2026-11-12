# Révision des traductions — HORS SUJET (jeu de soirée)

Le jeu : chaque joueur reçoit une question en secret. La majorité a la question A, l'intrus a la question B, très proche. Chacun répond à voix haute, puis le groupe cherche l'intrus. A et B doivent donc attendre le même type de réponse (un nombre, une heure, un lieu…) et rester proches.

## La consigne du créateur du jeu (à respecter strictement)
« Je veux exactement les mêmes questions [que le français], sauf que tu changes 2-3 détails. Si c'est des trucs spécifiques à la France, tu changes vite fait, mais sinon c'est les mêmes questions. »

Donc, pour chaque paire :
1. La traduction doit dire **la même chose que le français** : même sujet, même objet, même situation, même niveau de détail. Pas de question différente, pas d'idée ajoutée ou retirée.
2. Tu adaptes **uniquement** ce qui est spécifiquement français et n'aurait pas de sens dans le pays : villes françaises, plats ou marques purement français, fêtes françaises (14 juillet, Chandeleur…), système scolaire français (collège, bac, brevet…), émissions françaises, « en euros » quand la monnaie du pays est autre. Tu remplaces par l'équivalent le plus proche et le plus connu dans le pays, et rien d'autre.
3. Tout le reste reste fidèle au français, même si l'ancienne traduction avait « adapté » davantage : si l'ancienne traduction a changé de sujet, d'objet ou d'exemple sans raison culturelle, **tu la refais fidèle au français**.
4. Le ton reste oral, naturel, entre amis, tutoiement (you / tú / tu / du / você / je). Une question doit sonner comme une vraie phrase de la langue, pas comme du mot-à-mot.
5. A et B : la différence entre A et B doit être la même qu'en français.

Monnaie, selon la langue : en = Royaume-Uni (pounds) ; es = Espagne (euros) ; it = Italie (euros) ; de = Allemagne (Euro) ; pt = Brésil (reais) ; nl = Pays-Bas (euro). Si le français dit « (en euros) » et que la monnaie est la même, garde-la.

## Fichier d'entrée
`/home/claude/hs-work/in/<lang>.<n>.txt`, une ligne par paire :
`id|FR question A|FR question B|traduction actuelle A|traduction actuelle B|statut`

Statut :
- `inchange` : le français n'a pas changé. Garde la traduction actuelle si elle est fidèle (règles 1 à 5), sinon corrige-la.
- `fr-modifie` : le créateur a modifié le français. La traduction actuelle correspond à l'ANCIEN français : **refais-la** à partir du français actuel.
- `nouvelle` : nouvelle paire, la traduction peut être vide : traduis-la.

Pack « reflexe » (id qui commencent par `reflexe-`) : ce sont des consignes, pas des questions ; elles se terminent par un point (ou un point d'exclamation), jamais par « ? ».
Toutes les autres se terminent par « ? ». En espagnol, les questions commencent par « ¿ ».

## Fichier de sortie
`/home/claude/hs-work/out/<lang>.<n>.txt` : **une ligne par paire, toutes les paires, dans le même ordre**, au format strict
`id|traduction A|traduction B`
Pas de `|` ni de backtick dans les textes. Écris le fichier par morceaux (Write pour le premier bloc d'environ 150 lignes, puis ajoute les suivants avec un petit script ou des écritures successives) pour ne pas perdre le travail si tu es interrompu. Si le fichier de sortie existe déjà en partie (travail interrompu), lis-le, garde ce qui est fait et continue à partir de la première paire manquante.

Lis le fichier d'entrée par blocs (outil Read avec offset/limit d'environ 150 lignes). Pour chaque paire, décide : garder ou corriger.

À la fin, écris aussi `/home/claude/hs-work/out/<lang>.<n>.changes.txt` : une ligne par paire que tu as modifiée (statut `inchange` uniquement), au format `id|raison courte en français` (ex. `bouffe-012|l'ancienne traduction parlait de pizza au lieu de quiche`). Pas besoin de lister les `fr-modifie` ni les `nouvelle`.

## Vérification (obligatoire)
`node /home/claude/hs-work/review-check.mjs <lang> <n>` doit afficher OK. Corrige jusqu'à OK.
Ne modifie aucun autre fichier.
Réponds en une ligne : langue, partie, nombre de paires, nombre de corrections, résultat du check.
