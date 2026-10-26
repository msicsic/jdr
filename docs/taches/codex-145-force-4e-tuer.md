# Tâche Codex 145 (force 4e) : tuer, et les biens du mort

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** : si le lot déborde, livre le geste `tuer` commun et sa
chaîne (dépouille, témoins, nouvelle) et dis précisément ce qui reste. Pas de Luna (4f la vérifiera). **Poste : le PC fixe**
(`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste :
au plus 2 processus de calcul, priorité réduite. Ce lot touche `corps.py`, `combat.py`/`force.py`/`tenir.py` selon le lieu des
gestes de force, `pnj.py` (registre, témoins), `moteur.py` (action du joueur), `social.py` (nouvelles), `biens.py` si besoin, et
leurs tests ; **pas** `deliberation.py`, `planification.py`, `agendas.py` (lot 144), ni `mj.py`, `paroles.py`, `narration.py`,
`consignes.py` (lots 142 et 143). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-force.md` (« Tuer, le corps, la découverte », 4e, décisions), les rapports des lots 4a
(`rapport-codex-7-force-4a.md`), 4b (`rapport-codex-12-force-4b.md`), 126, 134 et 140, puis `corps.mourir` (la mort existe
déjà : dépouille, esprit retiré, fin du joueur), `esprits` (découverte `mort_vue`), `social.GESTES` et le registre des gestes
illicites (`pnj._temoins`).

## Les règles (plan force, décidées)
- **Tuer** : au contact d'une personne **sans défense** (inconsciente ou ligotée), sans jet ; avec une arme, 5 s ; à mains nues,
  30 s. Contre un ligoté conscient, geste long et bruyant : il crie (ouïe commune). Personne d'autre ne se tue : contre une
  personne qui peut se défendre, refus avec `attendu` (cible sans défense parmi…). Le coup ne tue jamais (décision du
  2026-10-22) : seul ce geste donne la mort. Même validation pour le joueur et les PNJ ; aucun PNJ ne choisit de tuer (le geste
  est déclaré pour eux, sans raison de s'en servir : aucun but ni recours ne le propose).
- **La mort passe par `corps.mourir`** (auteur noté) ; le geste est illicite : registre, témoins par la vue et l'ouïe communs,
  `vu_agir` `tuer`, souvenirs, relations (épreuve commune d'une violence vue) ; interruption comme les autres gestes longs.
- **La nouvelle** : `social.GESTES` reçoit `tuer` (et tout geste de force qui manque encore, avec son verbe) ; une mort vue ou
  découverte se dit par les contenus typés existants, la croyance d'un ouï-dire a la confiance d'un ouï-dire. Sans témoin, le
  moteur ne désigne aucun coupable.
- **Dépouiller** : les biens du mort restent les siens ; les prendre est une faute d'honnêteté (comme prendre le bien d'un
  absent), avec ses témoins, sans victime qui réagisse. Vérifie que la règle commune de propriété s'y applique déjà ; corrige le
  contrat commun si une dépouille y échappe.
- **Le joueur tué** : `corps.mourir` clôt déjà la partie ; vérifie la chaîne complète (fin sauvegardée, aucune action ensuite,
  rendu après rechargement).
- Le devoir du protecteur dont le protégé est mort (`relancer`, comme une atteinte) est dans `deliberation.py` : **hors lot**,
  à consigner comme reste si la découverte ne le déclenche pas déjà.

## Vérification
- Tests après rechargement : le joueur tue Brune ligotée sous les yeux d'Ilse (cri entendu, dépouille, témoin, méfiance,
  nouvelle répétée à un tiers) ; un PNJ inconscient tué sans témoin, découvert ensuite par la vue, sans coupable désigné ;
  Brune qui prend sur un corps (faute, témoin) ; refus contre une personne consciente libre ; même laps d'un bloc ou découpé.
- `--etat aubin:mort` au Relais et à `rixe` (épreuves existantes) sans plantage ; banc rapide 4 h, quatre scénarios et `rixe`
  × quatre graines contre la base (cache) : nuits identiques attendues (personne ne tue), aucun meurtre.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-force-4e-tuer` poussée (pas `main`).
`docs/plan-force.md` (4e : fait et reste), `docs/etat-dev.md` (« Branche `codex-force-4e-tuer`, non fusionnée »). Rapport d'une
page : `docs/taches/rapport-codex-145-force-4e-tuer.md`.
