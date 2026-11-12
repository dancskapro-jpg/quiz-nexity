# Écrire de nouvelles paires de questions — HORS SUJET

## Le jeu
Jeu de soirée sur un seul téléphone, entre amis ou en famille. Chaque joueur reçoit en secret une question. La majorité reçoit la question A ; l'intrus reçoit la question B, sans savoir qu'il est l'intrus. Chacun répond à voix haute, puis le groupe débat pour trouver l'intrus.

Une bonne paire :
- **A et B attendent le même type de réponse** (un prix, un nombre, une heure, un lieu, une phrase…) et des réponses **plausibles dans les deux cas** : la réponse de l'intrus doit pouvoir passer inaperçue au premier tour, puis se trahir quand on en discute.
- A et B sont **proches mais différentes** : même univers, un angle ou un détail qui change (ex. « Combien coûte une place de cinéma ? » / « Combien coûte un menu au fast-food ? »).
- Chacun peut répondre tout de suite, à partir de sa vie : pas de connaissances pointues, pas de calcul.
- **Questions intéressantes, concrètes, du quotidien.** Pas de questions farfelues, absurdes ou loufoques (« Combien de pigeons pourrais-tu battre ? » : non). Rien d'intime, de gênant, de politique, de religieux ou de vulgaire. Tout le monde peut y jouer, y compris en famille.
- Tutoiement, phrase orale et naturelle, en bon français, sans faute. Une question se termine par « ? » (espace fine ou normale avant, peu importe).

Le créateur du jeu aime particulièrement :
- les **prix** : « Combien coûte… ? », « Combien paierais-tu… ? », « Combien coûtait… quand tu étais petit ? » ;
- les **réactions** : « Que dis-tu quand… ? », « Que dis-tu si… ? » ;
- mais il veut **de la variété** : nombres, durées, heures, âges, lieux, objets, plats, marques, applis, personnes, films, musiques… Vise environ 1/4 de prix, 1/5 de « Que dis-tu… », et le reste varié.

## Ce que tu reçois (dossier /home/claude/hs-work/gen/in/)
- `<pack>.exemples.txt` : les paires de ce pack **choisies par le créateur** (format `type|thème|A|B`). C'est le niveau de qualité et le style attendus. Il y en a parfois très peu.
- `_style.txt` : 160 autres paires choisies par le créateur, tous packs confondus (format `type|A|B`) : inspire-toi du ton.
- `<pack>.refusees.txt` : des paires de ce pack que le créateur **n'a pas retenues** (format `A|B`). Ne les recopie pas et ne les reformule pas ; évite aussi le même genre de question quand elle est farfelue.
- `<pack>.themes.txt` : les thèmes autorisés pour ce pack (`thème|nombre`). Chaque paire doit utiliser un de ces thèmes, écrit exactement pareil.

## Ce que tu produis
Fichier `/home/claude/hs-work/gen/out/<pack>.txt`, une paire par ligne :
`type|difficulté|thème|question A|question B`
- `type` : un de nombre, minutes, heures, pays, ville, objet, activite, aliment, application, marque, animal, couleur, nom, expression, lieu, age, prix, personne, film, musique, vetement, metier, moment. Ajoute `*` au type (ex. `prix*`) seulement si A et B ne diffèrent que d'un tout petit détail (paire « miroir »).
- `difficulté` : 1 (facile à démasquer), 2 (moyen), 3 (difficile : A et B très proches).
- `thème` : un thème de `<pack>.themes.txt`.
- Pas de `|` dans les questions, pas de backtick. Toutes les paires doivent être différentes entre elles et des paires existantes.

Nombre de paires : **au moins** le nombre indiqué dans ta mission. Varie les thèmes du pack (répartis-toi sur beaucoup d'entre eux) et les types.

Écris le fichier par blocs de 40 à 60 paires (Write pour le premier bloc, puis ajoute les suivants) pour ne rien perdre si tu es interrompu. Si le fichier existe déjà (travail interrompu), lis-le et continue sans refaire ce qui existe.

## Vérification (obligatoire)
`node /home/claude/hs-work/gen-check.mjs <pack>` doit afficher OK. Corrige jusqu'à OK.
Relis enfin toutes tes paires une fois, en te demandant pour chacune : « est-ce qu'on a envie d'y répondre en soirée, et est-ce que l'intrus peut se cacher ? ». Remplace celles qui ne passent pas ce test.
Ne modifie aucun autre fichier. Réponds en une ligne : pack, nombre de paires, résultat du check.
