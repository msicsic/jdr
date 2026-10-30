# Tâche Codex 322 : trois échecs nouveaux de la suite complète (diagnostic et oracle)

Lis `AGENTS.md`. La suite complète du lot 307 (`C:\Users\msics\donjon\artifacts\suite-307-9457ea5\suite.log`, PC fixe)
et un rejeu sur l'intégration `79fca6a` (`C:\Users\msics\donjon\artifacts\trois-echecs-integ.json`, laptop) montrent trois
échecs absents de la suite du lot 305 (`d1c0722`) : ils viennent d'un lot fusionné depuis, pas du 307.

1. `tests/test_rendez_vous_tenu.py::test_scene_reelle_sans_invitation_que_mireille_ne_peut_tenir` et
2. `tests/test_constater_rumeurs.py::test_le_joueur_qui_ne_les_connait_pas_n_entend_que_des_voix` :
   `joueur.data["entendus"]` vaut `['mathurine', 'mireille', 'odile']` au lieu de `['mireille', 'odile']`.
3. `tests/test_voix_inconnues.py::test_la_reserve_verrouillee_rend_la_part_impossible_quelle_que_soit_la_voix` :
   `_plan_pulsion(m, "mathe", {"objet": "vivres", "servir": "odon"})` rend maintenant un plan
   `inspecter reserve, cherche odon` au lieu de `None`.

Suspects probables : lot 303 (contact commun avant un service : `_chercher`, inspection, appel ou question quand un
participant a un lieu inconnu) et lot 312 (livraison à un destinataire de lieu inconnu).

## Ce qui est demandé
1. Établis par bissection sur les fusions entre `d1c0722` et `79fca6a` le lot qui fait passer chaque test au rouge,
   avec contrôle sur son parent direct.
2. Pour chaque test, dis si le changement est **légitime** (le moteur suit désormais l'invariant du lot introducteur ;
   l'oracle est périmé) ou une **régression**. Exemples de questions : Mathurine parle-t-elle réellement dans la scène,
   le joueur l'entend-il (ouïe commune) ? Chercher Odon à la réserve verrouillée est-il un moyen admissible d'après les
   croyances de Mathe, alors que la réserve est crue verrouillée, ou faut-il que le contact échoue d'abord ?
3. Si légitime : ajuste la prémisse de la scène (placement d'auteur, capture) **sans affaiblir l'assertion** que le test
   défend ; dis-le avec la preuve. Si régression : corrige le contrat commun dans le lot introducteur, cas réel et autre
   cas après recharge, sans cas propre à Mathurine, Mathe ou à l'auberge.
4. Tests ciblés des fichiers touchés ; si un fichier de code du jeu change, empreintes 2 h des scénarios touchés et du
   Relais, 4 graines, contre la référence de l'intégration (cache). Pas de Luna ni de suite complète.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Les lots 313 (contact de position inconnue) et 315
(réclamations) sont en cours de fusion et touchent `pnj.py`, `planification.py`, `deliberation.py` : si la correction
doit y entrer, dis-le d'abord.

## Livraison
- Branche `codex-trois-echecs`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-322-trois-echecs.md`, entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\trois-echecs-322\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
