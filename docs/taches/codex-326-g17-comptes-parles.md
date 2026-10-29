# Tâche Codex 326 : G17, les comptes parlés

Lot G17 de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md), après G15 (lot 320, fusionné : registre
unique des émissions, `donjon/emissions.py`). Lis `AGENTS.md` (contrat du MJ : une réplique dont le moteur fixe le contenu
est formulée par le moteur), `docs/conception-refonte-mj.md` (ligne G17) et `docs/conception-valeur-llm.md` (ligne G17),
puis les rapports 180 (comptes écrits par le moteur) et 320 (G15).

## L'invariant
**Les mots d'une réplique qui porte un compte (dette, offre, prix, règlement, remboursement, refus de payer) gardent
exactement les rôles, les termes et le règlement de l'issue décidée par le moteur, et sont fixés avant publication.**
Le moteur formule la réplique à contenu comptable typé à partir de l'émission G15 et de l'issue ; Luna ne réécrit ni ne
paraphrase un compte, aucune opération n'est perdue, aucun paiement n'est montré au stade de brouillon. L'audit des
répliques comptables typées se retire dans ce lot, pour ces seules répliques, puisque ce lot fournit la garantie qui le
remplace ; les autres voies gardent leurs contrôles.

## Vérification
- Remboursement de Gorm et achat de planche (cas `comptes` et `soir-appel`), puis une autre dette et une autre offre :
  mots, soldes et citations identiques après recharge, MJ simulé sans réseau ; une inversion débiteur/créancier est
  impossible par construction (test).
- Luna : **une passe** de `comptes` et `soir-appel`, référence lue du cache : zéro réécriture des comptes, zéro repli
  comptable. Si la revue automatique bloque Luna, laisse la commande exacte dans
  `C:\Users\msics\donjon\artifacts\g17-326\luna-a-jouer.txt`.
- Tests ciblés des fichiers touchés ; pas de suite complète ni de banc PNJ (aucune décision des PNJ ne change).

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Recouvrement possible avec le lot 327 (G19,
`narration.py`) : signale-le.

## Livraison
- Branche `codex-g17-comptes`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-326-g17-comptes-parles.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g17-326\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
