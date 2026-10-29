# Tâche Codex 334 : trois empreintes de monde rouges sur l'intégration

Lis `AGENTS.md`, `docs/etat-dev.md`, puis les rapports 313 (attribution des 23 incidents de la suite `61ced73`) et
331 (même démarche pour l'achat de planches).

## Constat
Trois sous-tests sont rouges sur l'intégration elle-même ; le lot 313 les a attribués « préexistants »
(rejeux isolés sous `PYTHONHASHSEED=313`) :
- `tests/test_occasions_scenarios.py`, inverse du scénario `crue_hameau` : empreinte divergente ;
- `tests/test_etapes_chainees.py`, capture de la mine : empreinte du monde ;
- `tests/test_etapes_chainees.py`, capture de l'auberge : empreinte du monde.

## Ce qui est demandé
1. **Bissection** sur les parents directs pour chacun : le commit qui fait passer le sous-test du vert au rouge, et
   le champ du monde qui diffère.
2. **Trancher** pour chacun : défaut (une écriture inattendue, un champ hors contrat, une dépendance au hachage du
   processus) ou empreinte périmée par un changement légitime déjà fusionné. Vérifie l'indépendance au hachage
   sous au moins deux valeurs de `PYTHONHASHSEED`.
3. **Défaut** : corrige l'invariant commun, sans cas propre au scénario. **Empreinte périmée** : remplace-la
   seulement avec la preuve du champ changé et du lot qui l'a changé légitimement. Garde toutes les autres
   assertions (plans, visites, rendus, recharges).

## Contraintes
- Le lot 313 (`codex-contact-inconnu`, non fusionné) a recalé dans `tests/test_etapes_chainees.py` les **visites**
  de ces deux captures, pas leurs mondes. Ne touche pas aux visites et signale le recouvrement de fichier.
- Tests des deux fichiers, puis des fichiers que touche un éventuel correctif. Pas de suite complète.
- Si le moteur change : empreintes 2 h sur les scénarios touchés et le Relais, quatre graines, références lues du
  cache. Ni Luna ni banc PNJ.
- **Poste : le PC fixe.** Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-empreintes-monde`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-334-empreintes-monde.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\empreintes-334\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
