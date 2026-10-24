# Tâche Codex 52 : un objet non visé par le but n'est acquis que s'il apporte une capacité nouvelle

Branche `codex-capacite-nouvelle` (elle porte ce fichier, issue de l'intégration **5c2ce81** : lots 38 à 49 et 46
compris), worktree dans `tmp-worktrees/`. Lot de coût, demandé expressément par l'utilisateur (« les bancs sont trop
lents »). Pas de Luna.

**Lots en même temps** : 51 sur ce même poste (`planification._departs`, `_explorer`, `_normaliser_suites`,
`_sans_plan`, `_parcours` : l'allure feutrée) ; 50 sur l'autre poste (`paroles.py`, `mj.py`). Ce lot touche les gestes
d'acquisition et la `Vue` (`gestes`, `_aide_sur_place`, `Vue.capacite`, `Vue.couvre`, `Vue.doublon`) ; ne touche pas
aux fonctions du lot 51. Deux lots font des bancs sur ce poste : priorité réduite, au plus 4 processus.

Lis `AGENTS.md`, `docs/etat-dev.md` (« À revoir », volet coût : **C1** ; entrées `codex-une-source` lot 46,
`codex-borne-rester` lot 48 et leur contrat, `planif-rapide` : « l'on ne porte que ce qui peut servir le but »),
`docs/plan-planificateur.md` (la règle du lot 46 et sa définition de la capacité), le rapport
`docs/taches/rapport-codex-46-une-source.md`, puis `donjon/planification.py` (`Vue.sources_seules`, `capacite`,
`couvre`, `capacites_portees`, `doublon`, `gestes`, `_aide_sur_place`, `emplois`, `_entrees`, `VERIFIER`, `REFERENCE`,
`BORNES`).

## Le constat
Le diagnostic du coût (fin de nuit de 12 h) a mesuré que 94 à 99 % des états développés portent des préparatifs :
les combinaisons d'inventaire font exploser les recherches. Le lot 46 a traité les sources de lumière (une seconde
lampe sans capacité nouvelle n'ouvre aucun geste) : mine −34 % sur 12 h, auberge inchangée. Les autres catégories
restent : outils (couper, frapper, forcer, crocheter), combustibles, clés, contenants, monnaie d'échange.

## L'invariant
**Généraliser la règle du lot 46 : un objet que le but ne vise pas n'ouvre aucun geste d'acquisition (prendre,
demander, acheter, saisir sur un porteur, faire remettre) s'il n'apporte aucune capacité absente de ce que le PNJ
porte.** Une seule définition de la capacité, lue de ce que lisent les gestes (l'outil d'une opération et sa qualité,
la substance d'un combustible et ce qu'il recharge, ce qu'ouvre une clé, ce que peut contenir un contenant, la
faute), dont la lumière du lot 46 devient un cas, sans liste d'objets ni de scénarios. Une capacité couverte par la
réunion de ce qu'il porte compte comme couverte si la preuve est simple ; sinon, dis la limite. La règle passe par
le même point que celle du lot 46 pour que la référence de `VERIFIER` l'applique ; ce qu'elle lit est dans
`_entrees`. Ne change aucun coût, prix, borne ni donnée.

**Contrat** (celui des lots 46 et 48) : décisions identiques partout où la recherche de référence n'atteint pas son
plafond ; là où elle l'atteint (`BORNES`), le résultat doit égaler celui de la recherche complète (`REFERENCE`) ;
divergences localisées à leur première recherche et justifiées ainsi ; après bifurcation, mesures seulement.

## Vérification (demandée expressément)
- Mesure d'abord, sur les captures `tests/data/cout-12h/mine-1985-480.json.gz` et `auberge-1985-480.json.gz` : quelles
  catégories d'objets portent les inventaires des états développés, pour viser les bonnes.
- Tests après rechargement : un outil en double (deux objets qui coupent) : le second jamais pris ; un outil meilleur
  (la qualité que lit le geste) : pris ; un combustible d'une autre substance : pris s'il recharge ce que l'autre ne
  recharge pas ; une seconde clé de la même serrure : jamais ; l'objet visé par le but : toujours ; même résultat que
  la recherche complète sur les captures, en moins d'états.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference 5c2ce81`), quatre scénarios × 4 graines.
- **Temps sur 12 h** : `42bb9c0`, la base `5c2ce81` et la branche **lancés ensemble**
  (`tools/empreintes_nuits.py jouer --heures 12 --scenarios mine auberge --graines 42 1985 --processus 2`), CPU par
  nuit et par tranche, nœuds, bornées ; `comparer --calcul` base contre branche, divergences justifiées.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la capacité généralisée),
`docs/etat-dev.md` (« Branche `codex-capacite-nouvelle`, non fusionnée » ; C1 dans « À revoir » mis à jour). Rapport
d'une page : `docs/taches/rapport-codex-52-capacite-nouvelle.md` (catégories mesurées, définition, fonctions, temps
par tranche, nœuds, divergences, limites).
