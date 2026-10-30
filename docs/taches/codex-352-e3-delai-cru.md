# Tâche Codex 352 : E3, le jugement d'un délai utilise les moyens crus du contractant

Troisième lot de l'échéance négociée, après E1 (348, référence temporelle) et E2 (350, réalisation datée unique),
fusionnés. Conception : `docs/conception-menace-echeance.md`, sections 3, 5 (ligne E3 et preuve commune P) et 6
(arbitrages acceptés le 2026-10-30, à ne pas rouvrir ; l'arbitrage 4 s'applique ici). Lis `AGENTS.md`,
`docs/etat-dev.md` (court), la conception et les rapports 348 et 350. Pour les lots anciens (242 durée du devis,
257/258 devis vu par un observateur), cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant (un seul)
**Juger si un délai proposé est tenable (crédible, impossible ou indéterminé) se fait sur les moyens que le
contractant croit avoir (devis commun sur ses croyances, `planification.duree_devis`), jamais sur l'état réel ni sur
les croyances privées d'un autre.** La durée estimée reste distincte du coût pondéré. Un délai indéterminé (le devis ne
permet pas de se prononcer) n'est jamais accepté comme garantie datée : l'incertitude est exposée et l'accord reste
possible sans limite (arbitrage 4), sans abandon silencieux de la clause. Un refus porte une cause par refus et son
`attendu`.

Encore sans schéma joueur ni rendu nouveau (E4 à E6) : la fonction de jugement est appelée par les épreuves et par
le seul point d'évaluation d'une proposition datée, si E1/E2 en ont préparé un ; sinon interne.

## Épreuves (preuve P en plus)
Huile à livrer et feu à entretenir ponctuellement : délai crédible, impossible, indéterminé. Un changement caché des
moyens du contractant (que lui ignore) n'a aucun effet sur l'estimation ; un changement qu'il connaît la périme et la
recalcule. Un autre PNJ et un autre scénario pour le même cas. Recharge et laps découpé identiques ; aucune lecture
hors `_entrees` si la recherche est touchée (`planification.VERIFIER` sur les épreuves).

## Vérification
Tests ciblés et voisins (propositions, refus retenus, devis observateur, durée des devis, socle des agendas). Banc
rapide 4 h, quatre graines, Relais, auberge et mine (`tools/comparer_bancs.py --reference main`, références du cache) :
aucune décision des nuits ne doit changer sans explication. Pas de suite complète, ni Luna, ni banc long.

## Contraintes
**Poste : le PC fixe.** Fichiers prévus : `donjon/echanges.py`, `donjon/planification.py` (devis et entrées concernés),
refus de `donjon/deliberation.py` concernés, `donjon/agendas.py` si la limite d'E1 est lue. Ne touche ni `paroles.py`,
ni `narration.py`, ni `page.html` (lots 349 et 351 en cours). Priorité réduite, deux processus au plus.

## Livraison
- Branche `codex-e3-delai-cru`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-352-e3-delai-cru.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md`, section « Lots non fusionnés ».
- Bruts dans `C:\Users\msics\donjon\artifacts\e3-352\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
