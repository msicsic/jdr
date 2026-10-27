# Tâche Codex 178 (force 4f, suite des lots 172/177) : le dossier d'une porte dit qui sera retenu après l'opération

Petit lot issu de la validation Luna du lot 177 (jouée par l'orchestrateur ; fils copiés dans
`C:\Users\msics\donjon\artifacts\contre-revue-177\`) : enfermer reste refusé 2/2 par la contre-revue (« Bram est déjà dans le
bureau et l'action ne le met pas à l'intérieur »). Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna dans le lot (coffre
illisible depuis les agents de ce poste) : écris la commande exacte dans `C:\Users\msics\donjon\artifacts\retenus-178\luna-a-jouer.txt`
(deux passes `force-4f-enfermer`, `force-4f-trainer`, une passe des neuf autres bancs de force, référence `cdaf371`).
**Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur
ce poste (179, agendas/esprits) et une vérification d'intégration sur le laptop (174) : au plus 2 processus de calcul, priorité
réduite. Ce lot touche `tenir.py` (enfermement) et `couverture_action.py` (dossier de contre-revue) et leurs tests ; **pas**
`agendas.py`, `esprits.py`, `deliberation.py` (lot 179), `narration.py`, `consignes.py`. **Bruts dans
`C:\Users\msics\donjon\artifacts\retenus-178\`, jamais dans le worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé
d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 136, 140, 172 et 177, puis `tenir.enfermer`, `tenir.sorties_crues`,
`tenir.captif` et `couverture_action._passages`.

## L'invariant
**Qui sera retenu derrière une porte qu'on ferme ou verrouille est calculé par une seule fonction pure, d'après les présences et
issues crues de l'auteur ; l'exécution (`tenir.enfermer`) et le dossier de la contre-revue l'emploient tous deux, de sorte que la
contre-revue lit, pour chaque opération de porte, les personnes que le moteur tiendra pour retenues après elle.** Rien n'est lu
des présences ou verrous réels au-delà de ce que croit l'auteur ; une issue inconnue n'est jamais tenue pour verrouillée ; aucune
règle propre à Bram, à un bureau ou à la formulation « enfermer ».

## Vérification
- Tests MJ simulé/console après rechargement : cas réel (Bram dans le bureau, porte fermée puis verrouillée : le dossier le
  dit retenu, plan admis) ; un autre cas (réserve de la mine ou autre porte) ; une porte dont l'autre issue est ouverte ou
  inconnue : personne de retenu, le plan qui prétend enfermer reste refusé ; exécution identique à la base (mêmes personnes
  enfermées, mêmes événements) ; dossier sans mutation.
- Empreintes 2 h Relais/mine/rixe × quatre graines identiques (référence du cache, aucun comportement de PNJ changé).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-retenus-apres` poussée (pas `main`).
`docs/plan-force.md` (4f), `docs/etat-dev.md` (« Branche `codex-retenus-apres`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-178-retenus-apres.md`.
