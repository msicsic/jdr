# Tâche Codex 198 : un bien vaut ce qu'il sert, pas seulement ses pièces

Issue de la revue vierge 187 (`docs/taches/rapport-codex-187-revue-vierge-pnj.md`, § 1.1 et P3), décision du 2026-10-27.
**Ce lot est joué en double, Sol et Terra, sur deux branches, même brief et même base, pour comparer les modèles** : travaille
comme si tu étais seul, ne regarde pas l'autre branche.

Cas relevés par la revue (4 h, départ tiré, graine 1 ; bruts sur le laptop, rejoue-les ici) :
- **auberge 1** : Lucien, voleur au crochet, ne tente ni vol ni crochetage en 4 h ; affamé et refusé par Anselme, il propose
  ses fins crochets à Anselme contre sa besace (239 min) ;
- **mine 1** : Gaspard affamé brade son briquet à amadou contre un quignon de pain (137 min), puis reste 100 min sans moyen.
Causes relevées : `planification.devis_enrichissement` ne convoite que la croyance `pieces` (un ballot, un reliquaire n'existent
pas comme objets de convoitise) ; `echanges.necessaire` ne protège un outil que s'il sert le plan **de la minute**, jamais les
capacités durables de son porteur (lumière, allumage, crochetage, coupe).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste : au plus 2 processus, priorité réduite.
Fichiers : `biens.py`, `echanges.py`, `caractere.py` (valeur), `planification.py` (devis d'acquisition), `argent_projet.py` si
utile, et leurs tests ; **pas** `deliberation.py`, `esprits.py`, `services.py` (lot 197), `ouie.py` (lot 195). **Bruts dans
`C:\Users\msics\donjon\artifacts\valeur-198-<sol|terra>\`** (selon ton modèle, indiqué dans ta consigne de lancement).
Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-social.md` (« Argent, prêts et garde confiée », « Suite des échanges »), les rapports 45, 57, 107,
110 (propositions et contreparties sensées), 184 (projet de pièces), puis `devis_enrichissement`, `echanges.necessaire`,
`evaluer_proposition`, `offre_sensee`, `caractere.valeur_piece`.

## L'invariant
**La valeur qu'un PNJ prête à un bien, pour le convoiter, l'acquérir ou le céder, est une seule estimation commune fondée sur
ses croyances : son prix connu ou sa valeur d'usage, et les capacités qu'il apporte à son porteur (lumière, flamme, crochetage,
coupe, clé), pesées par ses valeurs ; jamais ses seules pièces.** Céder un outil compte la perte de la capacité qu'il assurait,
même hors du plan en cours ; un bien de valeur sans pièces peut être convoité au même prix commun de la faute que les pièces.
Même règle pour le joueur (ce qu'un PNJ accepte de lui céder ou de lui prendre) et les PNJ ; aucune règle propre à Lucien,
Gaspard, un objet ou un scénario ; aucune lecture de ce que le PNJ ignore (valeur cachée, contenu non su).

## Vérification
- Tests après rechargement : Gaspard ne brade plus son seul briquet pour un repas tant qu'il lui sert (et le cède si un autre
  moyen de flamme lui reste ou si la faim le désespère, selon ses valeurs) ; Lucien n'échange plus ses crochets contre une
  besace et peut convoiter un bien de valeur sans pièces ; un autre cas de même nature (autre scénario, autre outil) ; un bien
  sans usage pour son porteur reste cessible ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, quatre scénarios × quatre graines (références du cache) : propositions/acceptées, vols tentés, ventes
  d'outils, minutes sans recours, richesse S/F/D du lot 183 (`C:/Users/msics/donjon/artifacts/dormants-183/analyser.py`, mêmes
  définitions) à base identique ; aucune usurpation, plantage ni boucle nouvelle ; `VERIFIER` + `spatial.VERIFICATION` 0,2 sur
  une nuit de 2 h si le devis du planificateur change (toute lecture nouvelle entre dans `_entrees`). Coût
  (`tools/mesure_cout.py`, mine 4 h) relevé.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche indiquée dans ta consigne de lancement, poussée (pas `main`) ;
`docs/etat-dev.md` (une entrée « non fusionnée ») ; rapport d'une page `docs/taches/rapport-codex-198-valeur-des-biens.md`, avec
le temps passé et les difficultés rencontrées.
