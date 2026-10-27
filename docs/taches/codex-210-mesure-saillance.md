# Tâche Codex 210 (mesure) : ce que changerait une recherche limitée aux moyens saillants pour le but

Décision de l'utilisateur du 2026-10-27 (revue 187) : **mesurer d'abord** la réflexion limitée avant de décider. Le lot 190
(`docs/taches/rapport-codex-190-mesure-reflexion-limitee.md`) a mesuré la **profondeur** (INT, enjeu) mais **pas la saillance**,
désignée comme « le vrai levier » par `docs/plan-decision.md` § 4 : ne voir que ce qui vient à l'esprit, avec pour critère premier
**l'utilité pour le but**, avant la proximité, afin de garder les trouvailles émergentes (Gorm qui demande les planches d'Aubin
pour le feu ; allumer avant de crocheter). Le lot 190 demandait de reprendre la saillance après le lot 189 (fusionné) et de
comparer les choix entiers à entrées égales et à `REFERENCE`. **Mesure seule : aucun fichier de `donjon/` modifié** ; la variante
vit dans une sonde de `tools/` (comme le lot 190), désactivée par défaut.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (205, 209) : **un seul processus**,
priorité réduite. **Bruts dans `C:\Users\msics\donjon\artifacts\saillance-210\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne)
ou `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-decision.md`, le rapport 190 (sondes, témoins appariés, captures), les rapports 46 et 52 (une capacité
nouvelle ou rien, `Vue.pertinent`, `emplois`), puis `planification.chercher`, `Vue.pertinent`, `emplois`, `_entrees`.

## Ce qu'on te demande
1. **Une règle de saillance** définie une fois, en grandeurs du modèle (jamais en nœuds) : un moyen (objet, personne, source,
   flamme, porte) est saillant s'il est **utile au but** d'après les gestes communs (il lève une condition du but ou d'un
   préparatif) **et** vient à l'esprit (vu ou entendu récemment, dans la salle, ou lié au but par un souvenir) ; un rayon selon la
   PER si tu en proposes un. Le dire précisément, avec ses lectures (à mettre dans `_entrees` si elle devenait réelle).
2. **Mesurer avec la sonde** sur les nuits du lot 190 (mine, auberge, hameau 1985 fixes, 12 h), puis un banc 4 h cinq scénarios
   × quatre graines, témoins appariés : coût (`tools/mesure_cout.py` : recherches, nœuds), **plans changés** (premier geste et coût
   contre `REFERENCE`, à entrées égales), **plans perdus** (une recherche qui trouvait un plan n'en trouve plus), comportements
   (S/F/D du lot 183, sans recours, en attente, retours suspects du compteur 199). Les trouvailles émergentes de référence (Gorm et
   les planches, lumière avant crochetage) doivent être vérifiées une à une, en capture rechargeable.
3. **Recommandation** à l'utilisateur, chiffrée : gain de coût contre plans perdus et changement de comportement ; ce que le récit
   pourrait dire (« il n'a pas pensé à… ») ; ce qu'il faudrait pour l'implémenter (clés, `VERIFIER` en trois parties du § 6).

## Livraison
Branche `codex-mesure-saillance` (depuis `integration`) : la sonde dans `tools/`, ses tests courts,
`docs/taches/rapport-codex-210-mesure-saillance.md` (une page) et une ligne dans `docs/etat-dev.md`. Commit et poussée ; si la
poussée est bloquée, laisse le commit local et dis-le.
