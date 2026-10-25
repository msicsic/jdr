# Tâche Codex 73 : ce que le moteur vient de payer ou de rendre est un compte de l'issue

Branche `codex-comptes-issue` (elle porte ce fichier, issue de l'intégration **fbcf0ff**), worktree dans `tmp-worktrees/`.
**Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). **Luna disponible sur ce poste** (copies seulement ;
`tools/banc_multi.py --connexion chatgpt`). Un seul poste : priorité réduite, au plus 3 processus ; Luna en 4 exécutions
au plus. `git merge origin/integration` au début si elle a avancé (lot 69 et la vérification 70).

Lot en même temps sur ce poste : 71 (`planification.py`, `obstacles.py`). Ce lot touche `donjon/narration.py` (contrôle
des comptes), `donjon/mj.py` (`conversation_validee.comptes`), `donjon/biens.py`, `donjon/echanges.py` (issue des achats
et remboursements) ; pas `planification.py`.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-sens-dette` 56, `codex-prime-offre` 67, `codex-contenu-vide` 59, et la
**vérification Luna fbcf0ff** : `docs/taches/rapport-codex-70-verif-luna.md` sur `origin/codex-verif-luna-fbcf0ff`,
constats 1, 2 et 3), `docs/contrat-mj.md`. Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-fbcf0ff\` (`constats.md`
points 5 et 6, `relecture.txt`, banc `soir-appel` saisies 4 et 5, les deux passes).

## Le constat (vérification Luna fbcf0ff, deux passes)
Les relances sont passées de 2,5 à 9 sur les onze scripts depuis f033364 ; une partie vient du contrôle des comptes :
1. `soir-appel` p1 n° 4, « je réclame à Aubin les deux pièces qu'il me doit » : le moteur rend 2 pièces
   (`conversation_validee.comptes` = absent + rendu ; or 26 au tour suivant), mais le joueur lit « Elles sont à moi, et
   elles ne t'ont pas été remises » : le remboursement effectif n'est pas raconté, une parole fausse passe (portée
   `aucune`, comptes vides).
2. `soir-appel` p1 n° 5, achat d'une planche : le paiement immédiat est dans l'issue **textuelle** mais **absent des
   comptes structurés** ; « Les pièces sont remises ; je te dois encore cette part » reçoit deux refus de compte ; huit
   appels et un secours.
3. `soir-appel` p2 n° 4 : huit appels ; une non-livraison est extraite comme dette-objet absente, puis l'effet que le
   moteur a produit est confondu avec un effet créé par la parole.

## L'invariant
**Tout transfert que le moteur vient d'opérer dans un échange (paiement, remboursement, remise, part promise ou due) figure
dans les comptes structurés de l'issue, avec ses rôles, et le récit doit le dire sans le contredire** ; une affirmation de
compte qui recopie l'issue n'est jamais un effet « créé par la parole ». Une seule source pour l'issue d'un échange : les
comptes de `conversation_validee` dérivent des opérations du moteur, pas d'un texte. Pas de cas d'Aubin ni de la planche.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : remboursement réclamé (raconté, aucune parole contraire
  admise) ; achat payé d'une part promise (le paiement et la part due dits sans refus) ; un compte vraiment inversé,
  toujours refusé.
- Luna, **une passe** : `soir-appel`, `ressources`, `comptes`, référence l'intégration fbcf0ff lue du cache
  (`artifacts/references/fbcf0ff…/banc_multi/`, rangée par le lot 70) ; appels et relances par tour, textes affichés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-comptes-issue`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-73-comptes-issue.md`.
