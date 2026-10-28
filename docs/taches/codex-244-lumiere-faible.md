# Tâche Codex 244 : une source qui faiblit ne fait pas exploser la recherche

Diagnostic du lot 243 (`docs/taches/rapport-codex-243-bornes-garde.md`) : auberge 42, à 435 min, la lanterne d'Hugues est
lue `faible=True`. Cette lecture déclenche la découverte des moyens de lumière et multiplie les états (porteur/lieu,
ouverture/verrou, effets combinés) : les recherches de garde de Lucien atteignent le plafond de 4 000 nœuds sans plan
(7 000 à 12 000 pour la recherche complète). **Sans cette lecture, la même recherche prend 336 nœuds** (656/663 pour la
chambre). Conséquence sur l'intégration : **Lucien reste 44 min 17,8 s sans intention entre 435 et 480**.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le PC fixe** ; au plus 2 processus, priorité réduite. Captures et sondes du lot 243 sur ce poste :
`C:\Users\msics\donjon\artifacts\bornes-243\`.

**Fichiers** : la découverte des moyens de lumière et la pertinence des sources dans `planification.py` (`Vue.capacite`,
`couvre`, `doublon` du lot 46, découverte de lumière du lot 9/10, `emplois`), leurs tests. **Pas** : la durée du devis de
service et `Vue.aides` (lot 242), `Vue.detresses` (lot 240), le plafond de recherche, `pnj_propositions`, `biens`,
`echanges` (lot 228), `pnj.py` (lot 234), le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\lumiere-244\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## Ce qu'on te demande
1. Dire précisément quels gestes la lecture « faible » ouvre et pourquoi ils multiplient les états : une source faible
   compte-t-elle comme absente de capacité, ouvrant toutes les sources de lumière comme capacités nouvelles ?
2. **Invariant** (prolongement du lot 46, « une capacité nouvelle ou rien ») : une source portée qui faiblit garde la
   capacité qu'elle a encore ; seuls les moyens qui apportent une capacité réellement absente (durée de lumière couvrant
   le plan, recharge possible) ouvrent des gestes. Mêmes décisions là où la recherche complète ne plafonne pas ; aucune
   règle propre à Lucien, Hugues ou l'auberge, aucun plafond changé.
3. Si l'invariant change des décisions, dire lesquelles et pourquoi elles restent justes.

## Vérification
- Capture réelle 435 : recherche sous le plafond avec le résultat de la complète ; Lucien ne reste plus sans but ; un
  autre cas de même nature (autre PNJ ou scénario dont la lampe faiblit). Monde et rendu rechargés, même laps d'un bloc
  ou découpé.
- `VERIFIER` + `spatial.VERIFICATION` 0,2 auberge 42 sur 8 h ; empreintes 2 h (`tools/comparer_bancs.py --empreintes`)
  auberge/mine/Relais × quatre graines ; coût mine 1985 4 h (`tools/mesure_cout.py`) ; banc rapide 4 h cinq scénarios ×
  quatre graines si des décisions changent ; suite complète une fois.

## Livraison
- Branche `codex-lumiere-faible` poussée (pas `main`). Si la poussée est bloquée, laisse le commit local et dis-le.
- `docs/etat-dev.md` : « Branche `codex-lumiere-faible`, non fusionnée ». Rapport d'une page
  `docs/taches/rapport-codex-244-lumiere-faible.md`.
