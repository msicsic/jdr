# Tâche Codex 137 (données) : une ouverture est située dans les salles qu'elle relie

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. Ce lot touche les scénarios JSON (`donjon/scenario_*.json`), la validation de chargement (`monde.py`,
`Monde.verifier` ou la normalisation du scénario) et leurs tests ; **pas** `narration.py`, `mj.py`, `noms.py` (lot 135), ni
`tenir.py`, `pnj.py`, `moteur.py`, `commandes.py`, `planification.py` (lot 136). Termine ton dernier message par `LOT TERMINÉ`
(résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md` et le rapport du lot 133 (`docs/taches/rapport-codex-133-promesse-tenable.md`, sur la branche
`codex-promesse-tenable`, limites), puis `Monde.present_physique`, la géométrie des portes (`relie`, position, `spatial`) et la
lecture des `lieu` par la recherche (`planification.Vue`, croyances de lieu).

## Le défaut (révélé au lot 133)
Dans `scenario_relais.json`, `scenario_crue.json`, `scenario_rixe.json` et `scenario_rixe_douce.json`, l'objet `porte` déclare
`lieu: antichambre` mais `relie: [crypte, beffroi]`. `present_physique` la situe dans ses salles reliées, alors que les croyances
initiales et le devis la situaient dans l'antichambre ; le lot 133 a aligné le devis sur la présence physique, l'incohérence de
données demeure. Les autres scénarios n'ont pas d'ouverture dans ce cas (contrôle rapide de l'orchestrateur, à refaire).

## L'invariant
**Le `lieu` d'une ouverture (porte, trappe, tout objet à `relie`) est l'une des salles qu'elle relie, cohérent avec sa position
sur la carte ; le chargement d'un scénario le vérifie.** Établis d'abord où la carte place réellement cette porte et ce que le
joueur et les PNJ en voient (salle, case, côté). Corrige les données (le bon `lieu`, ses croyances et savoirs initiaux) et ajoute
la validation commune au chargement, avec un message qui nomme l'objet, le champ et les salles admises. Aucune exception propre à
la porte du Relais. Si la porte devait vraiment être vue depuis l'antichambre, dis-le et propose plutôt une règle de visibilité,
sans la coder.

## Vérification
- Test de chargement : les quatre scénarios corrigés se chargent ; un scénario forgé avec une ouverture mal située est refusé.
- Cas réel : la scène du lot 133 (capture crue 11 à 210) et une scène du Relais où un PNJ verrouille ou ouvre cette porte ;
  état, perception et rendu après rechargement.
- Banc rapide 4 h, Relais, crue et `rixe` × quatre graines contre la base (cache) : écarts expliqués nuit par nuit (le lieu change
  ce que croient les PNJ), aucune usurpation ni boucle nouvelle. Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-lieu-ouvertures` poussée (pas `main`).
`docs/etat-dev.md` (« Branche `codex-lieu-ouvertures`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-137-lieu-ouvertures.md`.
