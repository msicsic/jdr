# Tâche Codex 316 : une nuit et sa sonde ne dépendent pas du hachage du processus

Défaut relevé par le lot 310 (`docs/taches/rapport-codex-310-ordre-mesures.md`). Lis aussi `AGENTS.md`.

## Le constat
Sous `PYTHONHASHSEED=310`, `tests/test_detecter_changements_avis.py::test_reveils_brune_reels_et_recharges` lève
`KeyError: 929` : le retour de l'agenda de Brune attendu à t=929 (hameau 2024, départ tiré, joueur chambre de la
cloche, 2 min) n'est pas dans le relevé de la sonde. Le défaut existe aussi sur la base du 310 (`13ce328`) ; il ne
vient pas de ce lot. Bruts du 310 : `C:\Users\msics\donjon\artifacts\ordre-310\` (`diagnostic-base.log`).

## L'invariant
**Une nuit à graine donnée, et ce que la sonde 219 en relève, sont les mêmes quel que soit le hachage du processus
(`PYTHONHASHSEED`).** Établis d'abord où se trouve la dépendance :
- soit **la nuit elle-même** diffère (un parcours d'ensemble ou de `dict` construit depuis un ensemble décide d'un choix,
  d'un ordre de délibération, d'un tirage) : c'est un défaut de déterminisme du moteur, le plus grave ;
- soit **la sonde ou l'audit** (`tools/audit_nuits.py`, `tools/detecter_changements_avis.py`) classe ou date différemment
  le même déroulement.

Compare chronique, empreintes et état final de la nuit sous deux ou trois hachages (1, 42, 310, 2024) avant toute
correction. Corrige à la source par un ordre défini (tri sur une clé stable), sans figer `PYTHONHASHSEED` dans les
tests ni dans les outils, sans cas propre à Brune ou au hameau.

## Vérification
- Le test d'origine vert sous `PYTHONHASHSEED` 1, 42, 310 et 2024, sans changement de son oracle.
- Si le moteur est en cause : la même nuit (hameau 2024) identique sous ces quatre hachages (chronique, empreintes,
  état final complet), et une autre nuit de même nature (autre scénario ou graine) également.
- Empreintes 2 h, Relais, mine, auberge, crue et hameau, 4 graines, contre la référence de l'intégration (cache) :
  identiques si seul l'outil change ; sinon dis exactement quoi change et pourquoi.
- Calcul long détaché avec un fichier de fin. Pas de Luna ni de suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. D'autres lots touchent en ce moment `echanges.py`
(315), `pnj.py` et `trajet_estime.py` (313) : si ta correction doit y entrer, dis-le avant.

## Livraison
- Branche `codex-hachage-reveils`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-316-hachage-reveils.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\hachage-316\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
