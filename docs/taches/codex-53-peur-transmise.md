# Tâche Codex 53 : un allié en détresse visible ne rassure pas

Branche `codex-peur-transmise` (elle porte ce fichier, issue de l'intégration **5125d06** : lots 38 à 51 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant,
vérification minimale, rapport d'une page. Pas de Luna.

Lots en même temps : 52 sur ce même poste (`planification.py` : gestes d'acquisition et `Vue.capacite`) ; un autre
sur l'autre poste (MJ : `noms.py`, `francais.py`, `social.py` peut-être). Ce lot touche `deliberation.autour` et
`ecart_securite`, et lit les signes (`signes.py`) ; ne touche ni `planification.py` ni les fichiers du MJ.

Lis `AGENTS.md`, `docs/etat-dev.md` (« À revoir » : **à vérifier, la compagnie d'un allié qui a peur** ; entrées
`codex-relations-3c` (signes et impressions, « tremble »), `codex-force-4c` (fuite, `defense.dangers`),
`codex-signalements`), `docs/plan-relations.md` (3c), puis `donjon/deliberation.py` (`autour`, `ecart_securite`,
`SECURITE`, `taux`), `donjon/signes.py` (émission, `percevoir_tous`, `lire`), `donjon/vecu.py` (le temps vécu de la
sécurité).

## Le constat (vérifié dans le code)
`deliberation.autour` calcule la compagnie d'après les seuls liens (confiance et affection envers ceux qu'il voit ou
entend tout près) : un allié fiable rassure de la même façon qu'il soit calme, qu'il tremble de peur, qu'il fuie un
agresseur ou qu'il appelle à l'aide. Une revue externe (2026-10-24) l'a relevé ; l'utilisateur l'a retenu.

## L'invariant
**La détresse d'un allié que le PNJ perçoit ne le rassure pas : elle l'inquiète.** Ce qu'il perçoit, et seulement
cela : le signe émis et perçu (« tremble », « semble avoir peur »), une fuite qu'il voit, un appel à l'aide qu'il
entend ; jamais l'état privé de l'allié. Un allié perçu en détresse ne compte pas dans la compagnie et ajoute une
part de son inquiétude (une fraction réglée une fois, dite dans le rapport), d'autant plus que le lien est fort.
Une seule règle, dans `autour`/`ecart_securite`, au temps vécu comme le reste de la sécurité (même laps découpé, même
monde). Si cela fait demander « qu'est-ce qu'il y a ? » ou regarder vers ce que l'allié fuit, ce n'est pas dans ce
lot : signale-le seulement.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : la scène d'épreuve de la force (Brune frappe Aubin, Ilse témoin) :
  Ilse, qui voit Aubin trembler, n'est pas rassurée par lui et sa sécurité monte ; un autre cas de même nature (un
  allié qui fuit, ou un appel à l'aide entendu d'un proche, à l'auberge ou à la mine) ; un allié calme rassure comme
  avant ; un allié dont le signe n'est pas perçu (dans le noir, de dos hors du cône) rassure comme avant.
- Banc rapide (`tools/comparer_bancs.py --reference 5125d06`, 4 h, 4 graines, quatre scénarios et `rixe`) : aucune
  usurpation, violation, plantage ni boucle nouvelle ; écarts lus en deux lignes.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` (la règle), `docs/etat-dev.md` (« Branche
`codex-peur-transmise`, non fusionnée » ; retirer l'entrée « à vérifier » de « À revoir »). Rapport d'une page :
`docs/taches/rapport-codex-53-peur-transmise.md` (invariant, fraction retenue, fonctions, mesures, limites).
