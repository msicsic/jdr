# Tâche 217 (revue vierge) : les PNJ décident-ils comme des personnes ? Cohérence, entêtement, revirements

Revue en **lecture seule**, regard neuf hors de l'enchaînement des lots (décision de l'utilisateur du 2026-10-27 : une revue
vierge à chaque jalon). Aucun code du jeu, scénario, outil ou test modifié ; aucune fusion. **Poste : le PC fixe**
(`C:\Users\msics\donjon` ; d'autres calculs tournent) : **un seul processus de calcul**, priorité réduite. Pas de Luna. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`, `PYTHONIOENCODING=utf-8`. Bruts dans
`C:\Users\msics\donjon\artifacts\revue-217\`, jamais dans le worktree.

## Le jeu en deux lignes
« Le Seuil » : une aventure textuelle où un MJ (le modèle Luna) raconte, et où un moteur Python tient le monde et fait vivre
des PNJ autonomes (besoins, perception, ouïe, relations, échanges, planificateur, agendas). Priorité de l'auteur : **la richesse
du comportement des PNJ**. Toute la journée, des lots ont corrigé des **changements d'avis intempestifs** (un PNJ qui choisit un
but, l'abandonne sans raison nouvelle, puis le reprend) et des **fuites de l'état réel** dans ce que croient les PNJ.

## Ce qu'on te demande
1. **Observe d'abord, sans lire l'historique.** Joue quelques nuits sans joueur et lis leurs récits :
   `python -m donjon.banc_pnj --scenario <relais|mine|auberge|crue|crue_hameau> --heures 4 --graine <n>` (`--help`,
   `--chronique`, `--diagnostic`), quatre à six nuits au plus, une à la fois. Lis le code de décision : `deliberation.py`
   (`choisir`, `_candidats`), `planification.py`, `agendas.py`, `esprits.py`. Note ta première impression **avant** d'ouvrir
   `docs/etat-dev.md` (très long) et les rapports de `docs/taches/`.
2. **Ensuite seulement**, lis `docs/plan-decision.md`, `docs/plan-agendas.md`, le rapport 196 (contrat d'engagement proposé),
   les rapports 209, 210 (saillance) et 215 (richesse de la crue).
3. **Rends un rapport** `docs/taches/rapport-codex-217-revue-vierge-decisions.md` (deux à trois pages au plus) :
   - où les décisions paraissent humaines, où elles paraissent mécaniques, figées, entêtées ou capricieuses, avec des extraits
     de récits réels (scénario, graine, minute) ;
   - si l'approche suivie (contrat d'engagement dans `choisir`, juge unique par famille de but, compteur des retours) est la
     bonne pour obtenir des décisions stables mais vivantes, ou s'il existe une architecture plus simple (par exemple un
     engagement porté par l'intention elle-même, une utilité commune, des habitudes) ;
   - ce qui manque de plus important, classé par effet attendu et par coût, avec pour chaque idée l'invariant général qu'elle
     établirait (jamais un cas propre à un personnage ou un scénario) ;
   - deux sections séparées : **compatible avec les décisions actuelles** / **remettrait une décision en cause** (dis
     laquelle et pourquoi) ;
   - ce que tu n'as pas pu vérifier.
   Sois franc : un constat dérangeant vaut mieux qu'une liste polie.

## Ce qui est fixe
`AGENTS.md` (règles de conception : pas de cas particulier pour l'exemple, invariant général, contrat du MJ), Luna reste le
MJ, le moteur garde l'autorité sur le monde. Tu peux les critiquer dans la section « remettrait une décision en cause ».

## Livraison
Branche `codex-revue-vierge-decisions` : le seul rapport (et une ligne dans `docs/etat-dev.md` « Revue vierge 217, lecture
seule »). Commit et poussée ; si la poussée est bloquée, laisse le commit local et dis-le. Termine par `LOT TERMINÉ`
(résumé d'une ligne) ou `QUESTION : …`.
