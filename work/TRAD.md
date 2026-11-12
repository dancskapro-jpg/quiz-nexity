# Traduction des nouvelles paires — HORS SUJET (jeu de soirée)

Le jeu : chaque joueur reçoit une question en secret. La majorité a la question A, l'intrus a la question B, très proche. Chacun répond à voix haute, puis le groupe cherche l'intrus. A et B doivent donc attendre le même type de réponse (un prix, une durée, une personne, une phrase…) et rester proches.

## La consigne du créateur du jeu (à respecter strictement)
« Je veux exactement les mêmes questions [que le français]. Si c'est des trucs spécifiques à la France, tu adaptes, sinon ce sont les mêmes questions. »

Pour chaque paire :
1. La traduction dit **la même chose que le français** : même sujet, même objet, même situation, même niveau de détail. Pas d'idée ajoutée ou retirée.
2. Tu **adaptes** ce qui est spécifiquement français et n'aurait pas de sens dans le pays, en le remplaçant par l'équivalent le plus proche et le plus connu là-bas :
   - villes, quartiers, trajets (« un Paris–Lyon » → London–Manchester, Madrid–Barcelona, Milano–Roma, Berlin–München, São Paulo–Rio, Amsterdam–Rotterdam) ;
   - enseignes, marques, services et sites purement français (Leclerc, Fnac, Darty, SNCF, Doctolib, Leboncoin, La Poste…) ;
   - administration et vie pratique (CAF, mutuelle, impôts, URSSAF, Pôle emploi/France Travail, carte Vitale, préfecture…) ;
   - école et études (collège, lycée, bac, brevet, prépa, BTS…) ;
   - fêtes et traditions françaises (14 juillet, Chandeleur, galette des rois, muguet du 1er mai…), émissions et célébrités purement françaises ;
   - plats purement français quand ils sont inconnus du pays ;
   - **les prix** : monnaie du pays, et un montant qui reste plausible localement si on le cite dans la question.
   Quand rien n'est spécifique à la France, **tu n'adaptes rien**.
3. Le ton reste oral, naturel, entre amis, tutoiement (you / tú / tu / du / você / je). Une question doit sonner comme une vraie phrase de la langue, pas comme du mot-à-mot. Évite les tournures lourdes.
4. A et B : la différence entre A et B doit rester la même qu'en français, et les deux traductions doivent garder le même type de réponse. Si tu adaptes un élément, adapte-le de la même façon dans A et B quand il apparaît dans les deux.

Pays et monnaie, selon la langue : `en` = Royaume-Uni (anglais britannique, pounds £) ; `es` = Espagne (euros) ; `it` = Italie (euros) ; `de` = Allemagne (Euro) ; `pt` = Brésil (portugais du Brésil, reais R$) ; `nl` = Pays-Bas (euro). Si la monnaie est l'euro, garde « euros ».

Paires dont l'id commence par `reflexe-` : ce sont des consignes (« Réponds du tac au tac : … », « Cite … »), qui se terminent par un point, jamais par « ? ». Toutes les autres se terminent par « ? ». En espagnol, les questions commencent par « ¿ ».

## Fichier d'entrée
`/home/claude/hs-work/trad/in/<n>.txt`, une ligne par paire : `id|FR question A|FR question B` (600 lignes).
Lis-le par blocs (outil Read avec offset/limit de 100 lignes).

## Fichier de sortie
`/home/claude/hs-work/trad/out/<lang>.<n>.txt` : **une ligne par paire, toutes les paires, dans le même ordre**, au format strict
`id|traduction A|traduction B|adaptation`
- `adaptation` : vide si tu n'as rien adapté ; sinon une explication très courte **en français** de ce que tu as changé (ex. `Leclerc → Tesco`, `prix en livres`, `bac → A-levels`).
- Pas de `|` ni de backtick dans les textes, une seule ligne par paire.

Écris le fichier par blocs de 50 à 100 lignes : Write pour le premier bloc, puis ajoute les suivants (petit script `cat >> fichier <<'EOF'` ou Python en mode ajout). Ainsi rien n'est perdu si tu es interrompu. **Si le fichier de sortie existe déjà** (travail interrompu), lis-le, garde ce qui est fait et continue à partir de la première paire manquante ; ne réécris pas ce qui existe.

## Vérification (obligatoire)
`node /home/claude/hs-work/trad-check.mjs <lang> <n>` doit afficher OK. Corrige jusqu'à OK.
Ne modifie aucun autre fichier.
Réponds en une ligne : langue, partie, nombre de paires, nombre d'adaptations, résultat du check.
