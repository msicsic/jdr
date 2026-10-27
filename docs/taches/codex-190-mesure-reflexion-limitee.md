# Tâche Codex 190 (mesure) : que changerait une réflexion limitée aux moyens saillants ?

Décision de l'utilisateur du 2026-10-27, après la revue vierge 187 (`docs/taches/rapport-codex-187-revue-vierge-pnj.md`,
§ 3 et § 4 « remettrait une décision en cause ») : **mesurer d'abord** ce qu'une recherche limitée aux moyens saillants
changerait, avant de décider si l'étage « réflexion limitée » de `docs/plan-decision.md` passe avant A5. **Mesure seule :
aucun fichier de `donjon/` modifié, aucune décision de PNJ changée dans le jeu.** Les variantes s'appliquent par une sonde
dans `tools/` (ou dans les bruts), qui enveloppe la recherche sans toucher au moteur livré.

Lot de 30 à 45 minutes (`AGENTS.md`), livraison partielle permise si elle dit ce qui reste. Pas de Luna. **Poste : le PC fixe**
(`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste
(180 b, 184 b) : **au plus 2 processus de calcul**, priorité réduite. **Bruts dans `C:\Users\msics\donjon\artifacts\reflexion-190\`.**
Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-decision.md` (en entier : § 4 saillance et budget, § 6 ce que deviendrait `VERIFIER`, § 7 critères,
§ 8 ter), `docs/plan-planificateur.md`, les rapports 92 à 92 c, 98, 109 et 127 (outil `tools/mesure_cout.py`), le rapport 187,
puis `planification.chercher`, `_explorer_etats`, `gestes`, `Vue.pertinent`, `emplois`, `_entrees`, `VERIFIER`/`REFERENCE`.

## Ce qu'il faut mesurer
Deux ou trois variantes au plus, chacune définie en grandeurs du modèle (jamais en nœuds) et sans règle propre à un
personnage ou un scénario, par exemple :
- **saillance** : ne voir comme moyens que ce qui est lié au but (critère premier, pour garder les trouvailles émergentes),
  puis ce qui a été vu récemment ou est dans la salle ; le reste existe en mémoire sans venir à l'idée ;
- **profondeur** bornée selon l'INT, rétrécie par la panique ou la faim ;
- **budget selon l'enjeu** : courte réflexion pour une routine ou un souhait (dont le palier « argent »), recherche entière
  pour une urgence vitale.

Pour chacune, sur des nuits existantes ou rejouées (mine 1985, auberge 1985, hameau 1985, 12 h ; références en cache quand
elles existent) :
1. **Coût** : recherches, neuves, nœuds, CPU indicatif (`tools/mesure_cout.py` ou sa sonde), dont le but `argent` d'Odon
   (68 % du CPU d'une nuit de mine selon la revue 187).
2. **Prix de la myopie** : sur chaque choix rejoué à l'identique (mêmes entrées), part des décisions changées, écart de coût
   entre le plan joué et celui de la recherche complète, plans perdus (complète trouve, limitée non) et leur raison racontable.
3. **Trouvailles émergentes** : les scènes enregistrées qui les prouvent (Gorm qui demande les planches d'Aubin pour le feu,
   la lumière avant de crocheter, etc.) restent-elles trouvées ?
4. **Comportement sur une nuit libre** (la variante jouée de bout en bout) : boucles et alertes de l'audit, minutes sans
   recours/en attente, et la richesse S/F/D du lot 183 (`C:/Users/msics/donjon/artifacts/dormants-183/analyser.py`,
   `richesse.json`, mêmes définitions).
5. Ce que deviendrait `VERIFIER` (exactitude sur l'ensemble saillant, déterminisme, prix de la myopie en mesure) et ce que
   chaque cache actuel (`_MEMOIRE`, graphes repris, certificat `_sans_plan`) rapporterait encore.

## Livraison
Branche `codex-mesure-reflexion` : la sonde dans `tools/` si elle sert à refaire la mesure, et
`docs/taches/rapport-codex-190-mesure-reflexion-limitee.md` (deux pages au plus : tableau variante → coût → myopie → trouvailles
→ boucles/richesse, puis une recommandation argumentée pour ou contre l'avancer avant A5, et ce qui n'a pas pu être mesuré).
Entrée dans `docs/etat-dev.md`. Commit et poussée ; si la poussée est bloquée, laisse le commit local et dis-le.
