# Tâche Codex 199 (lot 196 d) : la garantie contre les changements d'avis dans l'audit des nuits

Premier lot du découpage du diagnostic 196 (`docs/taches/rapport-codex-196-changements-avis.md`, § 3 à 5, branche
`codex-changements-avis`, base de ce lot). Demande de l'utilisateur du 2026-10-27 : **une parade générale aux changements d'avis
intempestifs, vérifiée comme une garantie.** Ce lot ne corrige aucune boucle : il en fait une **mesure déterministe** dans les
outils de vérification, avant les lots 196 a–c qui les corrigeront. **Aucun fichier de `donjon/` modifié.**

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille ;
une suite de tests y tourne) : au plus 2 processus, priorité réduite. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`,
`PYTHONIOENCODING=utf-8`. Fichiers : `tools/detecter_changements_avis.py`, `tools/audit_nuits.py`, leurs tests. **Bruts dans
`C:\Users\msics\donjon\artifacts\garantie-199\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, le rapport 196 en entier (Argon), `tools/detecter_changements_avis.py` et `tools/audit_nuits.py` (et
`tools/comparer_bancs.py`, qui l'emploie pour le banc rapide).

## L'invariant
**Tout banc et tout audit de nuits compte, de façon déterministe et sans changer une nuit, les retours d'un PNJ à une décision
qu'il vient de quitter alors qu'aucune entrée de cette décision n'a changé, avec pour chacun le PNJ, la minute, les deux
décisions et la raison de la classification ; une raison fermée (accomplie, démentie, palier supérieur, marge suffisante) le
justifie.** Le compteur entre dans les mesures et les alertes de `audit_nuits.py`, donc dans `comparer_bancs.py` et les
vérifications d'intégration, au même titre que les bascules et les passages par heure.

## Ce qu'il faut faire
1. Relire le détecteur d'Argon (il est écrit par un autre modèle) : vérifier sur deux ou trois cas tirés au hasard parmi les 359
   de la crue et les 5 du hameau que la classification « non justifié » est juste en relisant la chronique, et sur des cycles
   « accomplis » qu'ils le sont ; corriger ce qui est faux. Dire ce qu'il ne voit pas.
2. L'intégrer dans `audit_nuits.py` (mesure par nuit et par PNJ, exemples, alerte au-delà de zéro) et donc dans `comparer_bancs`,
   sans changer les nuits (empreintes identiques avec et sans la sonde), avec un coût de calcul raisonnable (mesuré).
3. Établir la mesure de départ sur la base : quatre scénarios et le hameau × quatre graines × 4 h (les nuits de référence en
   cache quand elles existent), tableau par scénario.

## Vérification
Tests du détecteur sur des chroniques construites (aller-retour justifié, non justifié, cycle accompli) et sur une capture
réelle ; empreintes identiques avec et sans la sonde sur les 20 nuits ; suite des tests des outils, et suite complète une fois
à la fin si `audit_nuits.py` est importé par d'autres tests.

## Livraison
Branche `codex-garantie-avis` poussée (si la poussée est bloquée, commit local et dis-le) ; entrée dans `docs/etat-dev.md`
(« Branche `codex-garantie-avis`, non fusionnée ») ; rapport d'une page `docs/taches/rapport-codex-199-garantie-avis.md`.
