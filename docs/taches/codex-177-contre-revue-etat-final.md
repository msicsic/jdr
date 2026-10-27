# Tâche Codex 177 (force 4f, suite du lot 172) : la contre-revue juge l'état final établi par le moteur

Petit lot issu de la validation Luna du lot 172 (jouée par l'orchestrateur, bruts
`C:\Users\msics\donjon\.worktrees\integration\artifacts\bancs-multi\20261027-081252-19684\` du laptop, copiés dans
`C:\Users\msics\donjon\artifacts\force-172\` si présents). Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna dans le lot (coffre
illisible depuis les agents de ce poste) : écris la commande exacte dans
`C:\Users\msics\donjon\artifacts\contre-revue-177\luna-a-jouer.txt`, l'orchestrateur la jouera. **Poste : le PC fixe**
(`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste
(175 agendas/perception, 176 audit narratif des attitudes) : au plus 2 processus de calcul, priorité réduite. Ce lot touche la
contre-revue d'action (`couverture_action.py` : instructions et dossier) et ses tests ; **pas** `narration.py` (lot 176),
`esprits.py`/`agendas.py`/`deliberation.py` (lot 175), `consignes.py`, `tenir.py`. **Bruts dans
`C:\Users\msics\donjon\artifacts\contre-revue-177\`, jamais dans le worktree.** Termine ton dernier message par `LOT TERMINÉ`
(résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, le rapport du lot 172 et la note de sa fusion dans `docs/etat-dev.md`, puis
`couverture_action.INSTRUCTIONS` et le dossier transmis (`_operations`, `deplacements`, `passages`).

## Les cas réels (lot 172, deux passes)
- **Traîner** (`force-4f-trainer`) : le moteur a préparé `trainer brune sud` ; la contre-revue le rejette 2/2 parce que « le plan
  fait aussi avancer le joueur d'un pas », alors que ce pas est la moitié du geste établie par le moteur (`deplacements`).
- **Enfermer** (`force-4f-enfermer`) : `fermer porte_bureau` est rejeté (p1) parce qu'il « ne déplace pas Bram », alors que Bram
  est déjà dans le bureau d'après le dossier.

## L'invariant
**La contre-revue compare la demande à l'état final que le moteur établira : les déplacements et effets que le moteur produit
lui-même pour accomplir l'action demandée en font partie et ne sont pas des changements ajoutés ; un état demandé qui est déjà
vrai avant le plan, d'après le dossier, n'exige aucune opération.** Règle commune de la contre-revue (comme celle des réactions à
un agresseur), fondée sur les champs du dossier, sans nom d'action, de personne ou de salle. Un plan qui ajoute réellement un
changement non demandé, ou qui omet un changement demandé et pas encore vrai, reste rejeté.

## Vérification
- Tests MJ simulé/console après rechargement : les deux cas réels admis ; un autre geste composé admis (un second seuil, une
  autre porte) ; un plan réellement non conforme toujours rejeté (déplacement d'un tiers non demandé, porte non fermée alors
  que la personne est dans le lieu) ; dossier sans mutation.
- Commande Luna à laisser : **deux passes** de `force-4f-trainer`, `force-4f-enfermer`, et **une passe** des neuf autres bancs
  de force, d'`atelier` et de `relais` (la règle touche toute contre-revue), référence `cdaf371`.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-contre-revue-etat-final` poussée (pas `main`).
`docs/plan-force.md` (4f), `docs/etat-dev.md` (« Branche `codex-contre-revue-etat-final`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-177-contre-revue-etat-final.md`.
