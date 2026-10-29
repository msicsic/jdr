# Tâche Codex 280 : la réclamation d'un prêt échu au joueur, après la réunion des lots 266 et 275

La suite complète sur l'intégration `01d32e5` (lots 266 et 275 réunis ; journal
`C:\Users\msics\donjon\artifacts\suite-integ-01d32e5\suite.log` sur le PC fixe) a un seul échec propre au jeu :
`tests.test_echanges_suite.PretReclameTests.test_gaspard_la_redemande_et_le_joueur_qui_la_garde_perd_sa_confiance`.
Gaspard (mine 1985, départ fixe) a prêté sa lampe au joueur il y a plus de 240 minutes et se tient à côté de lui ; il
devait la réclamer dans les deux minutes (« Gaspard te demande de lui rendre la lampe de Gaspard… »). Il quitte la vue du
joueur, avec Odon, sans rien réclamer. Le test passe sur la fusion d'essai du lot 275 seul (`c95676f`) et sur celle du
lot 266 seul (`1951fb9`) ; il échoue sur la réunion des deux (reproduit sur le laptop dans
`C:\Users\msics\donjon\.worktrees\integration`, base 700622c).

## L'invariant
Établis d'abord **quel choix de Gaspard prend le pas sur la réclamation** et pourquoi la réunion des deux lots le produit :
la proximité d'un proche en détresse (266, « rester près ») et l'appel d'un interlocuteur inaccessible (275) interagissent
dans `deliberation`/`planification`. Si le nouveau choix est légitime selon les règles (palier supérieur, détresse réelle
perçue), la réclamation est seulement différée : prouve-le sur la scène et adapte la prémisse du test (placement d'auteur
explicite), toutes ses assertions conservées. Sinon, corrige le contrat commun sans cas propre à Gaspard, à la lampe ou à
la mine : **un prêt échu se réclame dès que le prêteur croit l'emprunteur à portée et qu'aucun but de palier supérieur ne
l'occupe.** Aucun oracle affaibli.

Lot de 30 à 45 minutes. Pas de Luna, pas de suite complète (le superviseur la lance). **Poste : le laptop**, deux
processus au plus, priorité réduite (un banc du lot 277 y tourne : un seul processus tant qu'il n'est pas fini).

**Fichiers attendus** : `donjon/deliberation.py`, `donjon/planification.py`, `donjon/echanges.py` selon la cause.
Le lot 277 (non fusionné) modifie `planification.py`/`echanges.py` et le lot 278 `deliberation.py`/`pnj.py` :
raccords minimaux, dis chaque fonction touchée.

## Vérification
- Le test en échec, sur la scène exacte, avec monde/rendu/scène identiques après recharge ; un autre prêt échu
  (autre prêteur ou scénario). Les fichiers de tests des lots 266 et 275 et `test_echanges_suite` entiers.
- Si le moteur change : banc rapide 4 h, cinq scénarios × quatre graines, référence de l'intégration à ta base (cache si
  présent), suspects 219 par nuit sans hausse ; calcul long détaché.

## Livraison
- Branche `codex-pret-reclame` poussée. Rapport d'une page `docs/taches/rapport-codex-280-pret-reclame.md` ; entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\pret-280\`. Termine par
  `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
