# Tâche Codex 202 : céder un outil compte la capacité qu'on perd

Décision de l'utilisateur du 2026-10-27 après le lot 198 (valeur des biens, **non intégrable** dans ses deux variantes) : le lot
198 mêlait deux invariants. On ne garde ici **que le premier** : la protection de ses outils. **La convoitise des biens sans
pièces (`devis_enrichissement`) est hors lot**, remise après le contrat d'engagement (lots 196) et une mesure de la saillance :
elle quadruplait le coût et appauvrissait les nuits (rapport `docs/taches/rapport-codex-198-valeur-des-biens.md` sur la branche
`origin/codex-valeur-biens-sol`, `ca3086d`).

Cas réels (revue 187, 4 h, départ tiré, graine 1) : **mine 1, Gaspard affamé propose son seul briquet contre un quignon de pain
(137 min)** ; **auberge 1, Lucien propose ses crochets à Anselme contre une besace (239 min)**. Cause : `echanges.necessaire` ne
protège un objet que s'il sert le plan de la minute, jamais les capacités durables de son porteur.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille ;
une suite y tourne) : au plus 2 processus, priorité réduite. Fichiers : `biens.py`, `echanges.py` (évaluation des cessions,
`necessaire`, offres et contreparties), `caractere.py` si la pesée par les valeurs y vit, et leurs tests ; **pas**
`planification.py`, `deliberation.py`, `esprits.py` (lot 201 en cours). **Bruts dans
`C:\Users\msics\donjon\artifacts\outil-202\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, le rapport 198 Sol (partie « contrat implémenté » : `biens.valeur_bien`, capacité marginale, doublons, prêt ≠
cession) et réutilise ce qui sert **seulement** à l'évaluation d'une cession ; les rapports 45, 57, 107, 110 (contreparties
sensées), puis `echanges.necessaire`, `evaluer_proposition`, `offre_sensee`.

## L'invariant
**Quand un PNJ envisage de céder un bien (vente, troc, don, contrepartie d'une proposition, des deux côtés), la perte compte la
capacité que ce bien lui assure au-delà du plan en cours (flamme, lumière, crochetage maîtrisé, coupe, clé connue), sauf s'il en
garde une autre équivalente ; le désespoir peut l'emporter selon ses valeurs.** Un prêt n'est pas une cession : il garde
l'obligation de rendre et ne fait perdre que l'usage pendant sa durée. Même règle pour ce que le joueur propose ou demande et
pour les PNJ ; aucune règle propre à Gaspard, Lucien, un objet ou un scénario ; aucune lecture de ce que le PNJ ignore.

## Vérification
- Tests après rechargement : Gaspard ne cède plus son seul briquet pour un repas tant qu'il lui sert, mais le cède s'il garde une
  autre flamme ou au désespoir selon ses valeurs ; Lucien ne cède plus ses crochets contre une besace ; un autre cas de même
  nature (autre outil, autre scénario) ; un bien sans capacité utile pour son porteur reste cessible ; un prêt reste possible ;
  même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, quatre scénarios × quatre graines (références du cache), avec le compteur des changements d'avis : trocs
  d'outils, propositions/acceptées, minutes sans recours, S/F/D du lot 183 ; la richesse ne doit pas baisser nettement ; aucune
  usurpation, plantage ni boucle nouvelle ; coût (`tools/mesure_cout.py`, mine 4 h) relevé, sans hausse notable attendue.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-ceder-outil` poussée (pas `main`) ; `docs/etat-dev.md`
(« Branche `codex-ceder-outil`, non fusionnée ») ; rapport d'une page `docs/taches/rapport-codex-202-ceder-outil.md`.
