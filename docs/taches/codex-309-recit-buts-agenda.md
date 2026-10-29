# Tâche Codex 309 : le récit et l'audit rendent tout but d'agenda, avec ou sans cible

Petit lot révélé par le lot 306 (`codex-a5-agenda-hameau`, non fusionné). Lis son rapport
`docs/taches/rapport-codex-306-a5-agenda-hameau.md` sur sa branche, section « Échec hors périmètre ».

## Le constat
Hameau, graine 42, minute 5 : `tools/audit_nuits._releve` appelle `donjon/recit_pnj._but`, qui lève `KeyError: 'qui'`
sur le but valide d'Aubin `{"type": "agenda", "agenda": "a1"}`. L'observateur suppose qu'un but d'agenda a toujours une
cible, alors que le but d'un sous-mandat (ici `amener`, confié par Gorm à Aubin) ne la porte pas dans le but lui-même.
L'état, le rendu joueur et la scène sont valides : seul le récit, et avec lui le banc, s'arrête.

## L'invariant
**Le récit des PNJ et l'audit des nuits rendent tout but que le moteur produit, d'après les données de l'agenda
référencé (sorte, paramètres, parent) lues par l'accès commun `donjon/agendas.py`, sans supposer de champ absent du
but.** Aucun champ n'est ajouté au but pour l'observateur, et aucun cas propre à une sorte d'agenda ou à un PNJ n'est
écrit. La règle s'étend à tous les buts d'agenda : `amener`, `informer`, `garder`, `protéger`, `obtenir`, `récupérer`,
et les sous-mandats.

## Fichiers attendus
`donjon/recit_pnj.py` (et `tools/audit_nuits.py`, seulement s'il lit le but en direct). Aucun moteur de décision, ni MJ,
ni scénario.

## Vérification
- La capture de la minute 5 du lot 306 rechargée (bruts dans `C:\Users\msics\donjon\artifacts\agenda-hameau-306\`) :
  récit et relevé rendus.
- Une scène par sorte d'agenda et un sous-mandat.
- Contrôle AST qu'aucun accès direct aux agendas n'est ajouté hors du socle (test existant).
- Empreintes 2 h, Relais et crue, 4 graines : chronique, mesures et état identiques ; seul le texte du récit peut changer
  là où il plantait.
- Pas de Luna ni de suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-recit-buts-agenda`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-309-recit-buts-agenda.md`.
- Entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\recit-309\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
