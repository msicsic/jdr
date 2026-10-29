# Tâche Codex 324 : G1 forme A, lot A0, l'oracle de sens

Premier lot de G1 sous la forme A ([conception G1](../conception-g1.md), sections 5 et 6 ; décision du 2026-10-29 :
U-P puis U-C sur la voie actuelle, puis la forme A, et « préparer A0 » dès maintenant). Lis `AGENTS.md`,
`docs/conception-g1.md` (corpus des 91 positions, axes I/V/F/P et leurs seuils, liste des cas obligatoires) et le
[rapport 318](rapport-codex-318-g1-repense.md).

## L'invariant
**Un même classement, outillé et déterministe, juge chaque position du corpus G1 sur cinq issues distinctes : proposition
fidèle à la saisie, admission par le moteur, exécution ou refus, attente de consentement, texte réellement vu par le
joueur.** Les références et les attentes par famille sont figées une fois depuis les fils archivés
(`C:\Users\msics\donjon\artifacts\g1-318\saisies.json` et les campagnes 294/296/304/311), puis réutilisées par chaque lot
A1 à A6 sans rejouer la référence. Les oracles sont figés avant tout résultat de branche.

Pas de changement de jeu : aucun fichier de `donjon/` modifié. Un outil dans `tools/` (relecture d'une campagne et
classement), ses tests, les attentes figées versionnées (petit fichier JSON dans `tests/data/` ou `docs/`), le rapport.

## Vérification
- Le classement rejoue les quatre campagnes 294/296/304/311 et la référence c9459ce depuis leurs fils, sans appel au
  modèle, et retrouve les chiffres du rapport 318 (admissions, intentions fidèles par famille) ; écart expliqué sinon.
- Chaque cas obligatoire de la conception (prix, avis, part contre pièces, question au MJ sans exécution, perche puis
  saut, vol avec attente) a son attente explicite ; un faux pendant de chaque issue est classé autrement (tests).
- Les seuils I/V/F/P de la conception deviennent des contrôles du rapport de l'outil, sans les changer.
- Pas de Luna, de banc ni de suite complète.

## Contraintes
**Poste : le laptop.** Un processus au plus, priorité réduite. Aucun recouvrement de code attendu.

## Livraison
- Branche `codex-g1-a0-oracle`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-324-g1-a0-oracle.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g1-a0-324\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
