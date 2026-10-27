# Tâche Codex 204 : la portée de la main ne s'arrête pas au seuil d'une salle

Décision de l'utilisateur du 2026-10-27 (`docs/plan-prompt.md`, « Décisions », n° 1) : **la salle n'est plus une unité de capacité
ni une frontière ; tout est borné à la perception et à la proximité.** Le diagnostic 203 (`docs/taches/rapport-codex-203-capacites-salle.md`,
bruts `C:\Users\msics\donjon\artifacts\capacites-203\` sur ce poste) établit l'écart principal **P1** : la portée manuelle
(`spatial.proche`, `_salle_position`, `proximite.exiger`, `monde.present_physique`/`accessible`, et côté PNJ `pnj._accessible`,
`_a_toucher`, `_approcher`) exige que l'objet soit **dans la salle de l'acteur**. Cas reproduit : Relais calme, Corvus à
`antichambre (0,3)` face à l'ouest, l'échoppe adjacente par un passage ouvert sans porte ; trousse de crochets ou torche sur la case
voisine `echoppe (8,3)` : `je prends la torche` → « Approche-toi… », alors que l'objet est vu et que le contact avec Gorm sur cette
même case est accepté (combat, prises, traîner, pousser passent déjà par un contact topologique, `passage.au_contact`).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot calcule sur ce poste (201 : `esprits.py`, `deliberation.py`,
`planification.py`) : au plus 2 processus, priorité réduite. Fichiers : `spatial.py`, `proximite.py`, `monde.py` (présence et
accès), `pnj.py` (accès et approche), `operations.py` si besoin, et leurs tests ; **pas** les fichiers du lot 201, ni `biens.py`
/`echanges.py` (lot 202), ni le MJ (`mj.py`, `narration.py`, en veille). **Bruts dans `C:\Users\msics\donjon\artifacts\portee-204\`.**
Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

## L'invariant
**Un objet est à portée de main quand il est sur une case au contact de l'acteur par un pas praticable (passage ouvert, sans mur
ni porte fermée entre eux, diagonale permise selon la règle des pas), ou porté, quelle que soit la salle à laquelle appartient sa
case ; la même règle de contact topologique que pour les personnages (`passage.au_contact`), pour le joueur et les PNJ, à
l'exécution comme dans la préparation des gestes.** Un contenant fermé reste fermé ; une porte fermée ou un mur séparent ; la
salle reste un secteur pour l'eau, l'acoustique, l'estimation des trajets du planificateur et les croyances de lieu. Aucune règle
propre à une salle, un objet ou un scénario.

## Vérification
- Tests après rechargement : le cas réel (torche et crochets au seuil antichambre/échoppe) devient prenable, et un autre cas de
  même nature (autre seuil, autre scénario, autre verbe : allumer, ouvrir, donner) ; une porte fermée entre l'acteur et l'objet
  le rend inaccessible ; une diagonale à travers un angle de mur reste refusée ; un PNJ au seuil atteint l'objet voisin ; même laps
  d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Empreintes 2 h, quatre scénarios × quatre graines (références du cache) : identiques ou écarts expliqués (un PNJ qui atteignait
  désormais un objet au seuil) ; banc rapide 4 h si des écarts apparaissent, avec le compteur des changements d'avis ; aucune
  usurpation, plantage ni boucle nouvelle ; `VERIFIER` + `spatial.VERIFICATION` 0,2, Relais 2 h.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-portee-sans-salle` poussée (pas `main`) ;
`docs/plan-prompt.md` (décision n° 1 : P1 fait) et `docs/etat-dev.md` (« Branche `codex-portee-sans-salle`, non fusionnée ») ;
rapport d'une page `docs/taches/rapport-codex-204-portee-sans-salle.md`.
