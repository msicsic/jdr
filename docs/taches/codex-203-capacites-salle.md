# Tâche Codex 203 (diagnostic) : quelles capacités dépendent encore de la salle plutôt que de la proximité ?

Décision de l'utilisateur du 2026-10-27 (`docs/plan-prompt.md`, « Décisions », n° 1) : **côté MJ et joueur, la salle n'est plus une
unité de capacité ni une frontière ; aucune règle ni aucun dossier ne dépend de la salle ; tout est borné à la perception et à la
proximité (`spatial.proche`).** Le moteur garde ses salles pour ce qui est un secteur (eau, acoustique, estimation des trajets du
planificateur, croyances de lieu des PNJ). Les lots L4 (152, dossiers proches), L5 (151, refus local de portée) et L8 (154, poser
au sol) l'ont appliqué en partie ; **personne n'a vérifié l'ensemble.** **Diagnostic seul : aucun fichier du jeu modifié.**

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot calcule sur ce poste : un seul processus, priorité réduite.
**Bruts dans `C:\Users\msics\donjon\artifacts\capacites-203\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-prompt.md`, les rapports 151, 152 et 154, puis le code des capacités du joueur et des PNJ :
`commandes.py`, `moteur.py` (actions et leurs préparateurs), `proximite.py`, `operations.py`, `deplacement_objet.py`,
`obstacles.py`, `perception.py`, `paroles.py`, `ecoute.py`, `pnj.py` (gestes et contact), et les dossiers envoyés au MJ (`mj.py`,
`monde.contexte`).

## Ce qu'on te demande
1. **Inventaire** de chaque règle qui décide si Corvus ou un PNJ **peut** faire quelque chose (prendre, poser, ouvrir, fouiller,
   examiner, écouter, parler, chuchoter, frapper, crocheter, allumer, alimenter, assembler, franchir, passer un obstacle,
   improviser, donner, demander…), avec la condition qu'elle teste : proximité/contact, perception (vue, lumière, ouïe), ou
   **appartenance à une salle**. Fichier, fonction, ligne.
2. Pour chaque règle qui teste la salle : est-ce une **capacité** (contraire à la décision : par exemple « tout objet de la salle
   est manipulable », « on fouille la salle entière », « on parle à qui est dans la salle ») ou un **secteur** légitime (l'eau, la
   portée de la voix par les passages, la croyance de lieu d'un PNJ) ? Montre un cas concret reproductible (scène, saisie,
   résultat) pour chaque capacité contraire.
3. Les **dossiers et faits envoyés au MJ** qui restent bornés à la salle plutôt qu'à la perception et à la proximité (dont les
   surfaces génériques murs/sol/plafond, L7 en attente).
4. **Proposition** : pour chaque écart, l'invariant général à rétablir et un découpage en petits lots (un invariant chacun),
   classés par effet sur le joueur ; ce qui relève du MJ gelé (en veille, décision du 2026-10-27) est signalé à part.

## Livraison
Branche `codex-capacites-salle` : `docs/taches/rapport-codex-203-capacites-salle.md` (deux pages au plus : tableau règle →
condition testée → capacité ou secteur → cas → proposition) et une ligne dans `docs/etat-dev.md`. Commit et poussée ; si la
poussée est bloquée, laisse le commit local et dis-le.
