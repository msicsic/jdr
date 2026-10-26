# Tâche Codex 134 (force 4d, suite) : traîner une personne sans défense ou une dépouille

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. Ce lot touche `tenir.py`, `pnj.py` (gestes, registre), `commandes.py`/`moteur.py` (action du joueur) et leurs
tests ; **pas** `narration.py`, `mj.py`, `consignes.py` (lot 132), ni `echanges.py`, `agendas.py` (lot 133). Termine ton dernier
message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-force.md` (« Retenir, ligoter, délier, traîner », « Les gestes longs sur une personne », 4d), le
rapport du lot 126 (`docs/taches/rapport-codex-126-force-4d-tenir.md`), puis `donjon/tenir.py`, `pnj.CONTRAINTES`,
`pnj.finir_gestes` et le pas commun (`temps.duree_pas`, `spatial.trajet`).

## La règle (plan force, décidée)
**Traîner** une personne sans défense (inconsciente, ligotée, rendue) ou une dépouille, d'une case par geste, **4,5 s par case** ;
elle prend la case que quitte celui qui traîne. Un personnage n'est pas porté (sa masse dépasse ce qu'on porte). Même règle pour
le joueur et les PNJ, une seule fonction de validation : contact, mains libres, cible sans défense, case d'arrivée libre et
atteignable par le pas commun (portes, obstacles, eau), refus avec `attendu` sinon (une cause par refus). Traîner une personne
vivante est une contrainte (`CONTRAINTES` contient déjà `trainer`) : témoins, souvenirs et relations par les voies communes ;
une dépouille non. Le geste porte son issue dans le registre comme les autres gestes longs : un coup reçu ou la perte de
connaissance de l'auteur l'interrompt ; la victime qui se réveille en cours de geste n'est pas déplacée pour cette case.
Aucun PNJ ne choisit de traîner quelqu'un de son propre chef dans ce lot (les décisions autonomes restent à l'étape 5).

## Vérification
- Le joueur assomme ou trouve Brune inconsciente au Relais, la traîne sur plusieurs cases jusqu'à une autre salle : positions,
  durée, orientation, témoins et souvenirs, rendu ; tout tient après rechargement, et le même laps découpé donne le même monde.
- Autre cas de même nature : une dépouille traînée (aucune contrainte), et une victime ligotée à l'auberge ; refus justes :
  cible consciente et libre, case occupée, porte fermée, mains prises ; réveil en cours de geste.
- Banc rapide 4 h, Relais et `rixe` × quatre graines contre la base (cache) : nuits identiques attendues (personne ne traîne de
  son propre chef). Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-trainer` poussée (pas `main`). `docs/plan-force.md` (4d :
traîner fait), `docs/mecaniques.md` si les règles du joueur y sont décrites, `docs/etat-dev.md` (« Branche `codex-trainer`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-134-trainer.md`.
