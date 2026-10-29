# Tâche Codex 339 : les échecs préexistants de la suite sur l'intégration

Lis `AGENTS.md`, `docs/etat-dev.md`, puis l'[attribution du 319](attribution-codex-319-up-recapitulatif.md) et les
rapports 331 et 334, qui ont suivi la même démarche.

## Constat
Sur l'intégration seule (référence `9237e14`), sept incidents de la suite reviennent, attribués « préexistants » par
le lot 319 :
- cinq erreurs du rejeu et un échec d'audit : `_retentir` est appelé sans son argument `emission` (signature changée
  par G15, `emissions`) ; le lot 315 a vu de même `tests/test_detecter_changements_avis.py`,
  `test_audit_ecrit_une_nuit_mesurée` ;
- le refus de vendre de l'huile après 8 h dans la voie directe `preparer_parole`
  (`tests/test_lampes_parts.py`, cas réel de l'auberge après huit heures).

## Ce qui est demandé
1. Pour chaque incident : le commit de bascule (parents directs), puis le verdict, défaut ou attente périmée par un
   changement légitime déjà fusionné.
2. **Défaut** : corrige l'invariant commun. Le rejeu et les outils d'audit doivent passer par l'accès commun des
   émissions, comme le jeu, sans signature parallèle ni cas propre au test. **Attente périmée** : remplace-la
   seulement avec la preuve du champ ou du comportement changé et du lot qui l'a changé, en gardant les autres
   assertions.
3. Une cause par correctif. Si la vente d'huile révèle un comportement de PNJ discutable plutôt qu'une attente
   périmée, décris-le et propose un lot, sans le corriger ici.

## Contraintes
- Tests des fichiers concernés, puis des fichiers que touche un correctif. Pas de suite complète.
- Si le moteur change : empreintes 2 h sur le Relais et les scénarios touchés, quatre graines, références lues du
  cache. Ni Luna ni banc PNJ.
- **Poste : le laptop.** Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-suite-rouge`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-339-suite-rouge-integration.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\suite-rouge-339\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
