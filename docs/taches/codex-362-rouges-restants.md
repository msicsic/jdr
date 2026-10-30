# Tâche Codex 362 : les rouges restants de la suite, hors lot 337

Après les lots 356 (attribution) et 361 (attentes périmées portées), la suite de l'intégration garde des rouges hors de
la famille du lot 337 (confiée au lot 360) :
- **6 méthodes apparues depuis `7eb45ff`** (fusions des lots 341 à 358 : groupe 1, 335, 353, 354, 355, 357, 358, 306…) :
  `C:\Users\msics\donjon\artifacts\suite-f014c80\nouveaux.txt` ;
- **10 méthodes anciennes classées « régression réelle » ou « non reproduit »** par le lot 356, hors 337 : 341 (3), U-C
  325 (2), 330 (1), G6 328 (1), trois incidents non reproduits sur le laptop (installation gardée, enfermement, rappel du
  prêt) : `C:\Users\msics\donjon\artifacts\suite-f014c80\autres-regressions.txt`. Les échecs cache KV (G6) et N9 (U-C)
  laissés par le lot 361 en font partie.
Suite brute : `C:\Users\msics\donjon\artifacts\suite-f014c80\suite.log`. Annexe d'attribution du lot 356 :
`docs/taches/attribution-codex-356-suite-rouge.md`.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 356 et 361 et ceux des lots en cause. Pour un lot ancien,
cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Ce qu'on attend
1. Pour chacune des 16 méthodes, sur l'intégration actuelle : rouge ou verte ; si rouge, fusion de bascule (pour les 6
   nouvelles : bissection sur les fusions `--first-parent` depuis `7eb45ff`), cause en une ligne.
2. **Corriger** chaque défaut dont l'invariant est clair et local (une cause, dans le contrat commun, sans cas
   particulier), avec le cas réel et un autre de même nature après recharge. **Adapter** un test seulement si son attente
   est devenue fausse par un changement voulu et documenté (preuve citée), sans changer ses assertions de sécurité.
3. Lister ce qui demande un arbitrage ou un lot plus large, avec la question précise. Les incidents non reproduits :
   les rejouer aussi par fichier entier ; s'ils restent non reproduits, le dire.

## Vérification
Les fichiers touchés et voisins verts sur l'intégration actuelle ; empreintes 2 h, quatre graines, scénarios touchés et
Relais, si le code du jeu change. Pas de suite complète (le superviseur la relance), ni Luna.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite, calculs longs détachés. Le lot 360 (PC fixe) traite les
23 régressions du 337, dont `tests/test_passage.py` (méthode `LaisserPasserJoueurTests`) : ne touche pas à ses fichiers
de tests ; le lot 359 (E5) touche menus et terminal.

## Livraison
- Branche `codex-rouges-restants`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-362-rouges-restants.md` (tableau des 16 méthodes en annexe) ; entrée
  « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\rouges-restants-362\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
