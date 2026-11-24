# Relecture des questions — HORS SUJET (jeu de soirée)

Le jeu : chaque joueur reçoit une question en secret. La majorité a la question A, l'intrus a la question B, très proche. Chacun répond à voix haute, puis le groupe cherche l'intrus. Une bonne paire : A et B attendent le même type de réponse, sont proches mais différentes, et la réponse de l'intrus peut passer inaperçue au premier tour puis se trahir quand on en discute. Les questions doivent être concrètes, du quotidien, et donner envie d'y répondre en soirée.

Le créateur du jeu veut **retirer les questions nulles**, en étant précis mais pas trop sévère : on enlève ce qui est clairement raté, on garde ce qui est correct même si ce n'est pas génial.

## Ta mission pour chaque paire
1. **Verdict** : `G` (garder) ou `R` (retirer).
2. **Public** : `T` (tout public, un ado de 12-17 ans peut y répondre sans problème) ou `A` (adultes seulement).

### Retirer (`R`) une paire quand :
- **Absurde ou bizarre** : la question n'a pas vraiment de sens ou personne ne la poserait (« Quel outil choisirais-tu pour marcher ? »).
- **Intrus trop facile** : A et B proposent des options différentes (« Plutôt un dîner improvisé ou un grand restaurant ? » / « Plutôt une activité sportive ou un atelier créatif ? ») ; ou A et B attendent des types de réponse différents (une durée contre un lieu) ; ou B n'a presque rien à voir avec A.
- **A et B quasi identiques** : aucune différence utile, l'intrus ne peut jamais être trouvé.
- **Trop vague ou abstraite** pour répondre vite (« Quelle serait ta priorité si tu devais choisir une journée aux thermes ? », « Quel critère compterait le plus… » sur un sujet sans intérêt).
- **Ennuyeuse** : sujet administratif ou technique sans intérêt en soirée (« Quel détail vérifierais-tu avant de comparer des fournisseurs d'électricité ? »).
- **Mal formulée** : répétition maladroite (« demanderais-tu conseil pour avoir un conseil »), faute, phrase lourde.
- **Doublon** : même question (ou presque) qu'une autre paire déjà vue dans ton fichier ; garde la meilleure, retire les autres.
- **Gênante ou déplacée** : intime au-delà du flirt léger, vulgaire, blessante.

Ne retire pas une paire seulement parce qu'elle suit un modèle courant (« Combien coûte… ? », « Que dirais-tu si… ? ») : ces modèles plaisent au créateur. Retire-la si elle est ratée pour une des raisons ci-dessus.

Lignes marquées `ancienne` : ce sont les paires **déjà choisies par le créateur**. Ne les retire jamais (verdict `G`), donne seulement le public.

### Public `A` (adultes seulement) quand la question :
- parle d'alcool, de bars ou de boîtes de nuit, de sexualité ou de séduction au-delà d'un simple crush ;
- suppose une vie d'adulte : travail, salaire, patron, collègues de bureau, loyer, crédit, impôts, assurance, banque, démarches administratives, conduire une voiture, élever ses enfants, organiser son mariage ;
- parle de jeux d'argent, de tabac.
Sinon `T`. En cas de doute, `T` si un ado peut y répondre naturellement.

## Fichier d'entrée
`/home/claude/hs-work/rev/in/<n>.txt`, une ligne par paire : `id|pack|ancienne ou nouvelle|question A|question B` (environ 600 lignes). Lis-le par blocs de 100 lignes (outil Read avec offset/limit).

## Fichier de sortie
`/home/claude/hs-work/rev/out/<n>.txt` : **une ligne par paire, toutes les paires, dans le même ordre**, au format strict
`id|verdict|public|raison`
- `verdict` : `G` ou `R` ; `public` : `T` ou `A`.
- `raison` : obligatoire pour `R`, quelques mots en français (« absurde », « intrus trop facile : options différentes », « doublon de bouffe-712 », « trop vague »…) ; vide pour `G`.

Écris le fichier par blocs de 100 lignes (Write pour le premier, puis ajout avec `cat >> fichier <<'EOF'`). **Si le fichier de sortie existe déjà** (travail interrompu), garde ce qui est fait et reprends à la première paire manquante.

## Vérification (obligatoire)
`node /home/claude/hs-work/rev-check.mjs <n>` doit afficher OK. Corrige jusqu'à OK.
Ne modifie aucun autre fichier.
Réponds en une ligne : partie, nombre de paires, nombre de retirées, nombre en public adulte, résultat du check.
