# Tâche Codex 348 : E1, une obligation conserve une référence temporelle canonique

Premier lot de l'échéance négociée. Conception et découpage : `docs/conception-menace-echeance.md`
(lot 347), sections 3 (contrat minimal), 5 (tableau E1 à E6, preuve commune P) et 6. Les six arbitrages
de la section 6 sont **acceptés par l'utilisateur le 2026-10-30** ; ne les rouvre pas.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), puis la conception 347. Pour un lot ancien (242 suivi des
délégations, 252 filiation, 256 jugement de mandat), cherche dans `docs/historique-lots.md` par mot-clé,
sans le lire en entier.

## Invariant (un seul)
Une obligation enregistrée par `agendas` porte une référence temporelle canonique et facultative : une
limite absolue en temps de jeu (dixièmes), avec son identité et sa version, distincte de l'échéance
générique existante, de la durée physique du devis (`duree_devis`, lot 242) et du coût pondéré. Elle est
lue par une seule fonction de `agendas`, validée à la recharge (`attendu` en cas de refus), et absente
quand rien ne l'a établie : **aucune date inventée**.

Ce lot est un **socle interne** : aucun appelant ne crée encore de limite négociée (E4 et suivants),
aucun schéma joueur nouveau, aucune consigne au MJ, aucun rendu nouveau. Les obligations actuelles
(parts, tâches payées, mandats, protection, garde) gardent leur comportement exact.

## Épreuves
- Ancienne sauvegarde sans le champ : chargée telle quelle, aucune limite lue, mêmes décisions.
- Deux obligations distinctes créées à la même minute, une seule avec limite : identités et limites
  distinctes, conservées après sauvegarde/recharge et laps continu ou découpé.
- Limite mal formée (type, négative, antérieure à la création, version incohérente) : refus à la recharge
  avec `attendu` ; une cause par refus.
- Mandat (lot 252/256) et protection inchangés : leurs tests ciblés verts.
- Contrôle AST du socle des agendas (`test_agendas_socle`) toujours vert : aucun accès hors du module.

## Vérification
Tests ciblés et fichiers voisins (`test_agendas_socle`, tests d'engagements, de délégation, de mandat).
Changement censé neutre : **empreintes 2 h, quatre graines, Relais, auberge et mine**
(`tools/comparer_bancs.py --empreintes --reference main`, références du cache). Pas de suite complète,
ni Luna, ni banc long.

## Contraintes
**Poste : le PC fixe.** Fichiers prévus : `donjon/agendas.py`, validation d'état dans `donjon/esprits.py`,
tests. Ne touche ni `narration.py`, ni `paroles.py`, ni `page.html`, ni `moteur.py` (lots 344 et 345 en
cours). Priorité réduite, deux processus au plus.

## Livraison
- Branche `codex-e1-reference-temporelle`, base `integration`, poussée vers origin
  (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-348-e1-reference-temporelle.md` ; entrée « non
  fusionnée » de 8 lignes au plus dans `docs/etat-dev.md`, section « Lots non fusionnés ».
- Bruts dans `C:\Users\msics\donjon\artifacts\e1-348\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
