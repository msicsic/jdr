# Tâche Codex 361 : les attentes périmées encore rouges après le lot 356

La suite complète de l'intégration `f014c80` reste rouge (101 échecs, 3 erreurs). Parmi les méthodes rouges, **32 sont
classées par le lot 356 « attente périmée prouvée » (ou harnais du consentement) mais n'ont pas été adaptées** : 18
basculent à la fusion de G5 (lot 323, perception canonique, `49608db0`), 6 à G16 (lot 345, `17212940`), 6 à U-C (lot
325, `37dccfa3`), une à G7 (`d20fce9b`), une à G6 (`64130fa1`). Liste exacte :
`C:\Users\msics\donjon\artifacts\suite-f014c80\attentes-perimees.txt` ; suite brute `suite-f014c80\suite.log`.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 356 et son annexe (`docs/taches/attribution-codex-356-suite-rouge.md` :
preuve de changement voulu pour chaque ligne), et les rapports 323 (G5), 345 (G16), 325 (U-C), 343 (G7), 328 (G6).

## Invariant (un seul)
**Un test dont l'attente est devenue fausse par un changement voulu et documenté est porté au contrat actuel sans
changer ce qu'il vérifie** : mêmes assertions de sécurité, d'état du monde, de recharge et de ce que le joueur voit ;
seules changent les prémisses ou la forme attendue que le lot d'origine a explicitement changées (perception canonique de
G5, mots formulés par le moteur de G16, confirmation « tenter » de U-C via `suite=("tenter",)` du harnais `jouer` de
`tests/test_repli_et_appel.py` ou `tests/consentement_support.py`). Chaque adaptation cite sa preuve. Si la preuve ne tient
pas sur le code actuel (le test révèle un vrai défaut), ne l'adapte pas : liste-le comme régression.

## Vérification
Les fichiers de tests adaptés verts sur l'intégration actuelle ; contrôle AST que les assertions sont inchangées hors
prémisses documentées (comme le 356). Pas de suite complète, ni Luna, ni banc. Aucun fichier de code du jeu modifié.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Le lot 360 (PC fixe) corrige les régressions du 337 :
ne touche pas aux fichiers de `regressions-337.txt` ; le lot 359 (E5, laptop) touche menus et terminal.

## Livraison
- Branche `codex-attentes-perimees`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-361-attentes-perimees.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\attentes-perimees-361\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
