# Tâche Codex 121 (3f) : les disputes entre PNJ

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna (la parole typée `avis` du joueur viendra dans un lot
suivant). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de
calcul ; le lot 120 (`pnj_propositions`, `propositions`, `echanges`) tourne en même temps. Ce lot touche `social.py` (avis,
nouvelles), `ouie.py` (nature « éclat »), `relations.py` (épreuves), `esprits.py` si besoin ; pas `planification.py`. Termine ton
dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (§ 7.3 les avis, **§ 7.4 les disputes**, 3f et ses lots 55, 64, 80, 88, 108), les rapports
des lots 80, 88 et 108, puis `donjon/social.py` (avis de menace, `nouvelles`, `recevoir`, `faits_dits`), `donjon/ouie.py` (natures,
`retentir`), `donjon/relations.py`, `donjon/eau.py` (`attendue`, prévision).

## Ce qui manque
Les avis (aujourd'hui : la menace d'un lieu par l'eau) se disent et se reçoivent, mais un auditeur qui pense le contraire avec plus
de conviction se tait. Le plan (§ 7.4) prévoit la **dispute** : il **contredit** ; le locuteur, s'il tient encore au sien, répond une
fois ; la fierté (> 60) ou la colère le font répéter une troisième fois et **la voix monte** (nature d'ouïe « éclat », entre voix et
bruyant : la dispute s'entend de la salle voisine et fait venir voir par la règle commune). Les **témoins** qui saisissent les mots
pèsent chaque côté par la règle des avis (leur constat, leur confiance et leur affection envers chacun ; jet opposé CHA + ELO à
égalité de poids) et adoptent, gardent ou doutent. **Suites** : le désavoué éprouve « dispute perdue » (rancune × fierté), qui a pris
son parti gagne un peu d'affection ; se tromper n'est pas mentir (`mensonge_dementi` faible seulement).

## L'invariant
**Un avis contraire entendu se conteste par la parole commune, et ses suites passent par les règles communes** (nouvelles, ouïe,
relations, registre de ce qui a été dit) : pas de boucle (une contradiction et une réponse par épisode, une troisième seulement par
fierté ou colère, jamais de redite sans fait nouveau, registre du lot 108) ; aucun prédicat d'avis nouveau (seulement ceux que le
moteur sait évaluer : menace d'un lieu) ; aucune règle de scénario. Le joueur voit et entend la dispute par l'ouïe et la vue
communes (texte de chronique et de rendu).

## Vérification
- Tests après rechargement, même laps découpé : en crue, deux PNJ aux prévisions d'eau opposées (capture réelle si une nuit le
  montre, sinon scène d'auteur) se disputent ; un témoin adopte le côté le mieux étayé ; la voix monte avec un locuteur fier et
  s'entend de la salle voisine ; le désavoué éprouve « dispute perdue » ; aucune redite au tour suivant ; le joueur présent lit la
  dispute.
- Banc rapide 4 h, crue et Relais × quatre graines contre la base (cache) : disputes, éclats, avis adoptés, aucune boucle ni usurpation.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` (§ 7.4, 3f), `docs/etat-dev.md` (« Branche `codex-disputes`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-121-disputes.md`.
