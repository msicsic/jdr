# Tâche Codex 84 : une part d'un lot porté se vend par proposition, sans devenir une tâche

Branche `codex-part-proposee` (elle porte ce fichier, issue de l'intégration **7cce974** : lots 38 à 82 compris), worktree
dans `tmp-worktrees/`. **Lot de 30 à 45 minutes**. **Luna disponible** (copies seulement ; `tools/banc_multi.py
--connexion chatgpt`). Un seul poste : priorité réduite, au plus 3 processus ; le lot 83 (`narration.py`) tourne en même
temps.

Ce lot touche `donjon/echanges.py` (`evaluer_proposition`, `proposer`, le devis d'une demande de part), `donjon/propositions.py`,
`donjon/biens.py` ; pas `narration.py` ni `mj.py`.

Lis `AGENTS.md`, le **rapport du lot 82** (`docs/taches/rapport-codex-82-paiement-effectif.md` : « Au soir n° 5, Luna propose
bien `proposition`, une part de `planches` contre trois pièces ; […] le moteur refuse « il ne voit pas comment faire la
tâche » »), `docs/etat-dev.md` (entrées `codex-propositions` 29, `codex-offre-sensee` 57 (`devis_service`),
`codex-piece-de-lot` 78, `codex-lampes` (parts détachées d'un lot porté)), `docs/plan-relations.md` § 7.1, puis
`donjon/echanges.py`, `donjon/propositions.py`. Bruts : le worktree du lot 82
(`tmp-worktrees/codex-paiement-effectif/artifacts/bancs-multi/20261025-173635-38776/`).

## Le constat
Le joueur propose trois pièces contre une part des planches d'Aubin (qu'Aubin porte ou a à portée) : le contenu est bien
`proposition`, mais le moteur la refuse avec « il ne voit pas comment faire la tâche » : la demande d'une **part d'un lot
porté** est évaluée comme une **tâche** à accomplir (devis d'un service), et le devis échoue. Une part détachée et remise se
fait pourtant déjà par la demande historique et par la vente au prix (lot `codex-lampes`).

## L'invariant
**Demander une part d'un lot qu'on porte ou qu'on a à portée, dans une proposition, c'est demander sa remise** : son coût pour
le donneur est la valeur propre de la part (prix propre, réticence, `necessaire`, `garde`), comme pour un objet, et son
exécution est la remise d'une part détachée (même chemin que la demande et la vente) ; seule une part qui suppose de faire
quelque chose (servir, aller chercher ailleurs) est une tâche avec devis. Une seule classification des demandes, partagée par
`evaluer_proposition`, `proposer` et le contre-offre du lot 77.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : trois pièces contre une part des planches d'Aubin : acceptée ou
  refusée selon sa valeur propre, jamais « il ne voit pas comment faire la tâche » ; acceptée, la part est remise, l'or payé ;
  une part de soupe à servir reste une tâche ; une part d'une réserve dans une autre salle (aller la chercher) reste une tâche.
- Luna, **une passe** : `soir-appel`, `ressources`, référence 7cce974 lue du cache si présente, sinon 882907c ; l'achat de la
  planche exécuté en ligne (or et planche après recharge).
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` § 7.1, `docs/etat-dev.md` (« Branche
`codex-part-proposee`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-84-part-proposee.md`.
