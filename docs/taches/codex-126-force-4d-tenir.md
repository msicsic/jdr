# Tâche Codex 126 (force 4d, partie 1) : saisir, se dégager, ligoter, délier, traîner

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots ») ; s'il déborde, livre d'abord saisir/se dégager/ligoter/délier et
dis ce qui reste. Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
D'autres lots tournent sur ce poste et ailleurs : au plus 2 processus de calcul, priorité réduite. Ce lot touche `combat.py`,
`defense.py`, `corps.py`, `pnj.py` (registre des gestes en cours, `finir_gestes`), le moteur du joueur (`moteur.py`,
`commandes.py`, actions) ; **pas** `paroles.py`, `mj.py`, `consignes.py`, `social.py`, `esprits.py` (lot 124), ni
`pnj_propositions.py`, `echanges.py`, `relations.py` (lot 122), ni `planification.py`. Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-force.md` (« Retenir, ligoter, délier, traîner », « Les gestes longs sur une personne »,
« 4d », « Décisions » : toutes retenues sauf la n° 6), les rapports des lots 4a, 4b et 4c (`rapport-codex-7-force-4a.md`,
`rapport-codex-12-force-4b.md`, `rapport-codex-17-force-4c.md`), puis `donjon/combat.py`, `donjon/defense.py` (prise
déclarée, `degager`), `donjon/corps.py`, le registre des gestes en cours dans `donjon/pnj.py`.

## Ce qui manque
Coups, assommer, fuir, riposter, se rendre et se dégager d'une prise déclarée existent (4b, 4c). Personne ne peut encore
**saisir** quelqu'un, le **ligoter**, le **délier** ou le **traîner**, et les gestes longs sur une personne n'ont pas
d'issue différée.

## L'invariant
**Les gestes sur une personne passent par une règle commune au joueur et aux PNJ, et un geste long n'a d'effet qu'à sa fin,
si ses conditions tiennent encore.**
- Saisir : d20 + FOR contre d20 + max(FOR, DEX) de la victime, contre 10 par surprise ; `tenu_par` ; tenu, on ne quitte pas
  sa case (pas refusé avec `attendu`), on frappe à −2, on parle, on crie ; qui tient lâche s'il marche ou fait autre chose
  que frapper, parler ou ligoter avec un aide. Se dégager : la règle existante de 4c, contre la FOR de qui tient.
- Ligoter (30 s, sans jet) : un lien en main (forme `lien` d'au moins 1 m, `matiere.py`, ou usage lien) sur quelqu'un de
  sans défense, tenu par un autre, ou rendu. Ligoté : ni pas ni geste des mains ; parle, crie ; se libérer DEX contre 18,
  un essai par 10 minutes. Délier : au contact, mains libres, 10 s ; couper le lien d'une lame, 3 s ; le lien revient à qui délie.
- Traîner : une personne sans défense ou une dépouille, une case par geste, 4,5 s par case ; elle prend la case quittée.
- **Gestes longs** (ligoter, délier, se libérer) : l'entrée du registre porte l'issue, appliquée à l'instant de fin par
  `pnj.finir_gestes` si la victime est toujours sans défense ou tenue et l'auteur conscient et au contact ; un coup reçu ou
  la perte de connaissance interrompt l'auteur et l'issue tombe. Témoins comptés pour les gestes de `CONTRAINTES` seulement.
- PNJ : ils délient un protégé (avec la réanimation existante), se libèrent ; **ils ne ligotent ni ne saisissent personne
  de leur propre chef** (décision 14). Le joueur : actions et commandes `saisir`, `ligoter`, `delier`, `traîner`, avec
  fiche avant tentative et `attendu` pour chaque refus (une cause par refus).

## Vérification
- Tests après rechargement, même laps découpé : `--etat aubin:ligote`, Gorm délie Aubin ; le joueur assomme Brune, la
  ligote (lien de l'atelier ou ficelle), la traîne ; un ligotage interrompu par un réveil n'a pas lieu ; saisir par surprise
  et de face ; tenu, un pas refusé avec `attendu` ; se libérer seul après dix minutes ; état et rendu après rechargement.
- Banc rapide 4 h, Relais et `rixe` × quatre graines contre la base (cache) : aucune usurpation, aucun ligotage spontané.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée sur ce poste (sinon le dire), branche poussée (pas `main`). `docs/plan-force.md`
(4d, partie faite), `docs/mecaniques.md` (gestes du joueur), `docs/etat-dev.md` (« Branche `codex-force-4d-tenir`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-126-force-4d-tenir.md`.
