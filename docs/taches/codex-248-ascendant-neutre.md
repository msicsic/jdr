# Tâche Codex 248 (A5, lot 1) : l'ascendant, sixième axe des relations, neutre

Premier lot d'A5, mandat et autorité. Conception : `docs/taches/rapport-codex-245-conception-a5.md` (lot 1) ;
autorité à trois sources : `docs/plan-agendas.md` § 5 (« L'autorité ») et § 10 décision 1 ; arbitrages du 2026-10-28
dans `docs/etat-dev.md` (« A5, arbitrages »). Lis-les d'abord.

## L'invariant
**Un sixième axe `ascendant` (ce que B reconnaît d'autorité à A) existe dans les relations, avec lecture et écriture par
`relations.py` seul, et, neutre, ne change aucune décision.** Comme les cinq axes existants : valeur graduée, bandes et
hystérésis communes, liens de départ du scénario qui peuvent le fixer, estompement, signature, validation de la
sauvegarde. Valeur de départ neutre sauf lien déclaré (arbitrage du 28). Les anciennes sauvegardes et scénarios sans
ce champ se chargent sans migration (absence = neutre).

Ce lot **n'ajoute aucune épreuve qui le fasse bouger** (lot 8) et **aucun lecteur qui décide** (lots 4 et 5) : il pose
l'axe, sa lecture pure (`relations.envers`, lecture nommée de l'autorité reconnue) et ses signatures dans les clés qui
lisent déjà les relations, pour que les lots suivants n'aient qu'à le consommer.

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le PC fixe**, au plus 2 processus, priorité réduite.

**Fichiers autorisés d'avance** : `relations.py` ; la validation des profils et des liens de départ
(`deliberation.py`, `esprits.py`) en raccord ; les consommateurs qui énumèrent les axes (`AXES`, récit, rejeu, mesures
du banc) pour qu'ils tolèrent le sixième ; `tests/test_relations_*` et le contrôle AST de `test_relations_socle`
(aucun accès à l'axe hors de `relations.py`). **Pas** : `echanges.py`, `agendas.py`, `planification.py` (hors clé
`_entrees` si une signature des relations y est lue), le MJ, les scénarios.

## Vérification
- Tests : deux liens orientés (A envers B, B envers A) qui ne se confondent pas ; lecture pure sans écriture ; lien de
  départ déclaré dans un profil de test, puis sauvegarde et rechargement identiques (monde et rendu) ; ancienne
  sauvegarde sans le champ chargée neutre ; contrôle AST vert.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes`), Relais, mine, auberge, crue et hameau, quatre graines,
  référence `1006204` du cache (manquantes calculées une fois) : chronique et mesures identiques ; l'état complet ne
  diffère que par le champ nouveau, à montrer en le retirant.
- Pas de suite complète.

## Livraison
- Branche `codex-ascendant-neutre` poussée. Rapport d'une page `docs/taches/rapport-codex-248-ascendant-neutre.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\ascendant-248\`.
  Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
