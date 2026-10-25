# Tâche Codex 78 : une pièce d'un lot se désigne comme le lot, pour le moteur et pour la revue

Branche `codex-piece-de-lot` (elle porte ce fichier, issue de l'intégration **38e5d7e**), worktree dans `tmp-worktrees/`.
**Lot de 30 à 45 minutes**. **Luna disponible** (copies seulement ; `tools/banc_multi.py --connexion chatgpt`). Un seul poste :
priorité réduite, au plus 3 processus, Luna en 4 exécutions au plus.

Ce lot touche `donjon/mj.py` (contre-revue de fidélité), `donjon/couverture_action.py` (`contenu_conforme`), `donjon/noms.py`
ou `donjon/francais.py` (désignation d'une pièce de lot) ; pas `echanges.py` ni `deliberation.py` (lot 77 en même temps).

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-comptes-issue` 73 (sa limite : l'achat du soir), `codex-ressource` 50,
`fabrication-generale` (lots : « un nom de pièce, un seul compte », `prelever`), `codex-elision` 54), `docs/contrat-mj.md`.
Bruts : le worktree du lot 73 (`tmp-worktrees/codex-comptes-issue/artifacts/`, banc `soir-appel`, achat d'une planche) et
`C:\Users\msics\donjon\artifacts\verif-luna-fbcf0ff\` (même saisie).

## Le constat
`soir-appel`, achat d'une planche à Aubin : la contre-revue de fidélité **oppose la planche singulière au lot `planches`**
(« les planches de bac ») et demande une précision ; l'achat n'est jamais exécuté en ligne (validé seulement avec MJ simulé
au lot 73).

## L'invariant
**Une pièce ou une part d'un lot se désigne indifféremment par le nom de la pièce (singulier) ou par le lot, pour la saisie,
le moteur et la contre-revue** : le sens partagé d'un contenu typé (lot 50) porte le lot et la quantité ; « une planche » des
« planches de bac » est la même chose que « une part des planches » ; la revue juge sur ce sens. Pas de cas des planches :
même règle pour une part de vivres, une charge de bûches, une bûche d'un fagot.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : achat d'une planche (pièce au singulier) accepté et exécuté ;
  demande d'une bûche d'une réserve à l'auberge ; un objet vraiment autre que le lot toujours refusé.
- Luna, **une passe** : `soir-appel`, `ressources`, `noms-dialogue`, référence l'intégration fbcf0ff lue du cache ; textes
  affichés et appels par tour.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-piece-de-lot`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-78-piece-de-lot.md`.
