# Tâche 187 (revue vierge) : pourquoi les PNJ semblent-ils prévisibles, et que faudrait-il pour qu'ils vivent ?

Revue en **lecture seule** demandée par l'utilisateur : un regard neuf sur le projet, hors de l'enchaînement des lots.
Aucun code du jeu, scénario, outil ou test modifié ; aucune fusion. **Poste : le laptop** (`C:\Users\msics\donjon`,
l'utilisateur y travaille ; d'autres calculs tournent) : au plus 2 processus de calcul, priorité réduite. Pas de Luna.
Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`, `PYTHONIOENCODING=utf-8`. Bruts dans
`C:\Users\msics\donjon\artifacts\revue-187\`, jamais dans le worktree.

## Le jeu en deux lignes
« Le Seuil » : une aventure textuelle où un MJ (le modèle Luna) raconte, et où un moteur Python tient le monde et fait vivre
des PNJ autonomes (besoins, perception, ouïe, relations, échanges, planificateur, agendas). Priorité actuelle de l'auteur :
**la richesse du comportement des PNJ** — qu'ils aient l'air de personnes avec des projets, des alliances, des conflits,
des choix surprenants mais compréhensibles, plutôt que des automates qui satisfont leurs besoins.

## Ce qu'on te demande
1. **Observe d'abord, sans lire l'historique.** Joue quelques nuits sans joueur et lis leurs récits, par exemple
   `python -m donjon.banc_pnj --scenario <relais|mine|auberge|crue|crue_hameau> --heures 4 --graine <n>` (voir `--help`,
   `--chronique`, `--diagnostic`), quatre à six nuits au plus. Lis les scénarios (`donjon/scenario_*.json`), puis le code de
   décision : `deliberation.py`, `planification.py`, `agendas.py`, `esprits.py`, `relations.py`, `social.py`, `echanges.py`.
   Note ta première impression **avant** d'ouvrir `docs/etat-dev.md` (très long, historique des lots) et les rapports de
   `docs/taches/`.
2. **Ensuite seulement**, lis `docs/plan-agendas.md`, `docs/plan-relations.md`, `docs/plan-social.md` et ce que tu jugeras
   utile de `docs/etat-dev.md`, pour savoir ce qui est déjà prévu ou décidé.
3. **Rends un rapport** `docs/taches/rapport-codex-187-revue-vierge-pnj.md` (deux à trois pages au plus) :
   - ce qui rend les PNJ prévisibles ou plats, avec des extraits de récits réels (scénario, graine, minute) ;
   - ce qui manque de plus important, classé par effet attendu sur la richesse et par coût ; pour chaque idée, l'invariant
     général qu'elle établirait (pas un cas propre à un personnage ou un scénario) ;
   - ce que tu ferais autrement dans l'architecture si cela freine la richesse (complexité, coût de calcul, couches) ;
   - deux sections séparées : **compatible avec les décisions actuelles** / **remettrait une décision en cause** (dis
     laquelle et pourquoi) ;
   - ce que tu n'as pas pu vérifier.
   Sois franc : un constat dérangeant vaut mieux qu'une liste polie.

## Ce qui est fixe
`AGENTS.md` (règles de conception : pas de cas particulier pour l'exemple, invariant général, contrat du MJ), Luna reste le
MJ, le moteur garde l'autorité sur le monde. Tu peux les critiquer dans la section « remettrait une décision en cause ».

## Livraison
Branche `codex-revue-vierge-pnj` : le seul rapport (et une ligne dans `docs/etat-dev.md` « Revue vierge 187, lecture
seule »). Commit et poussée ; si la poussée est bloquée, laisse le commit local et dis-le. Termine par `LOT TERMINÉ`
(résumé d'une ligne) ou `QUESTION : …`.
