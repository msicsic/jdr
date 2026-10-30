# Tâche Codex 363 : E6, le texte libre conserve chaque clause temporelle de l'accord

Sixième lot de l'échéance négociée, après E1 à E5 (348, 350, 352 et 357, 355, 359), fusionnés : l'accord daté existe dans
le moteur, se juge sur les moyens crus, se choisit au menu et au terminal. Conception : `docs/conception-menace-echeance.md`,
sections 3, 5 (ligne E6 et preuve commune P) et 6 (arbitrages acceptés le 2026-10-30, à ne pas rouvrir). Lis `AGENTS.md`
(contrat du MJ : contenu typé, rendu par le moteur), `docs/etat-dev.md` (court), la conception et les rapports 355 (E4),
359 (E5), 325 (U-C) et 345 (G16).

## Invariant (un seul)
**Une saisie libre qui propose un accord daté (« je te paie trois pièces si tu me livres une part d'huile dans dix
minutes ») est compilée en contenu typé portant chaque clause (prestation, limite, prix) ; l'aperçu « Compris » les montre
toutes et l'accord engagé est exactement celui-là.** Une clause que le moteur ne porte pas (« payer demain », « tenir
jusqu'à », prêt daté, clause alternative) est refusée en entier avec une raison publique, sans exécution partielle ni
clause silencieusement abandonnée ; « demain » sans repère établi demande une précision (arbitrage 6). Mêmes accords,
comptes et paroles que le choix direct d'E5 pour la même intention.

## Vérification
- « Part livrée dans dix minutes » puis une tâche différente ; refus de « payer demain », de « tenir jusqu'à » et d'une
  clause alternative non portée ; consentement, annulation ; parité avec E5 ; monde, comptes, paroles et rendu après
  recharge. Tests ciblés et voisins (E1 à E5, compilateur, comprehension, consentement, G16/G17).
- **Luna, une passe ciblée** sur copies, seulement les scripts qui exercent le changement : prépare les scripts de banc
  et dépose la commande exacte dans `C:\Users\msics\donjon\artifacts\e6-363\luna-a-jouer.txt` ; si la revue automatique
  bloque l'appel, laisse la commande, l'orchestrateur la jouera. Banc rapide 4 h si des effets moteur changent.
- Pas de suite complète.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : schéma de `donjon/paroles.py`, compilateur et consignes communs en vigueur,
`donjon/comprehension.py`, `donjon/consentement.py`, `donjon/transactions.py`. Lots en cours : 360 (régressions du 337,
PC fixe), 362 (rouges restants, laptop) ; signale tout fichier commun. Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-e6-libre-date`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-363-e6-libre-date.md` ; entrée « non fusionnée » de 8 lignes au plus dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\e6-363\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
