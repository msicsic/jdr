# Tâche Codex 140 (force 4d, fin) : la captivité inquiète et brise la volonté

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. **Base voulue : la branche du lot 136 (`codex-enfermer`, non fusionnée).** Ce lot touche `corps.py`,
`vecu.py`, `deliberation.py` (sécurité ressentie) et `tenir.py` si besoin, avec leurs tests ; **pas** `paroles.py`, `mj.py`,
`narration.py` (lot 138), ni les scénarios ou `banc_pnj.py` (lot 139). Termine ton dernier message par `LOT TERMINÉ` (résumé
d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-force.md` (« Enfermer et s'évader », 4d, décision 15), les rapports des lots 126, 134 et 136, puis
`corps.briser`, `corps.volonte_brisee` (déjà lu par la VOL effective), `vecu` (temps vécu) et `deliberation.ecart_securite`.

## Les règles (plan force, décidées ; décision 15 : dès 4d)
- **Inquiétude captive** : enfermé ou ligoté, **à ce qu'il croit**, un PNJ s'inquiète chaque minute (`captif`), par le temps
  vécu commun (comme le noir ou une présence crainte), sans délai fixe ni règle propre à une salle ; libre ou se croyant libre,
  l'inquiétude cesse. Le joueur captif vit la même chose par son corps.
- **Volonté brisée** : chaque heure ligoté ou enfermé ôte un point (`corps.briser`), deux heures au calme et libre en rendent un ;
  compté au temps vécu, sans dépendre du découpage. Son seul effet aujourd'hui est la VOL effective déjà lue par la persuasion ;
  aucun nouvel emploi (l'étape 5 l'utilisera).
- Aucun choix autonome nouveau (ni enfermer, ni ligoter) ; l'évasion du lot 136 reste la réponse.

## Vérification
- Épreuves du lot 136 (bureau ou réserve de la mine, `--etat personne:enferme:salle`, et `--etat aubin:ligote`) : sécurité qui
  monte chaque minute, un point de volonté par heure de captivité, récupération après deux heures libre ; même laps d'un bloc
  ou découpé avec recharges donne le même `data` ; état et rendu après rechargement.
- Un PNJ qui se croit enfermé à tort (porte en fait ouverte) s'inquiète ; un autre, enfermé sans le savoir, non.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache) : nuits identiques attendues (personne n'est captif
  dans les nuits libres). Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-captivite` poussée (pas `main`). `docs/plan-force.md`
(4d terminé), `docs/etat-dev.md` (« Branche `codex-captivite`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-140-captivite.md`.
