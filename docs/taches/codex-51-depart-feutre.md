# Tâche Codex 51 : l'allure feutrée ne s'explore que si un geste sans témoin peut en avoir besoin

Branche `codex-depart-feutre` (elle porte ce fichier, issue de l'intégration **d60b80a** : lots 38 à 49 compris),
worktree dans `tmp-worktrees/`. Lot de coût, demandé expressément par l'utilisateur (« les bancs sont trop lents »).
Pas de Luna.

Lots en même temps : 50 sur l'autre poste (`paroles.py`, `mj.py`, `couverture_action.py`, `echanges.py`) ; le lot 46
(`planification.py` : `Vue.capacite`, `Vue.couvre`, `Vue.doublon`, gestes de prise de lumière) se termine et sera
fusionné avant toi ; garde tes changements loin de ces fonctions.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-cout-12h` lot 38, `codex-borne-rester` lot 48 et son contrat,
`codex-trajet-estime` lot 30 : l'allure dans l'état), `docs/plan-planificateur.md`, puis `donjon/planification.py`
(`_departs`, `_explorer`, `_explorer_etats`, `_normaliser_suites`, `_sans_plan`, `_parcours`, `_GRAPHES`, la
découverte de lumière comme modèle de marque dans un graphe, `_entrees`, `VERIFIER`, `REFERENCE`, `BORNES`).

## Le diagnostic (mesuré sur l'intégration, graine 1985, 12 h)
Chez Rémy `faim` (mine, fin de nuit), **1 358 des 2 711 états sont à l'allure 30 (feutrée) sans aucun geste sans
témoin possible** : le départ feutré double l'espace pour rien. Prototype (« départ feutré seulement si un geste sans
témoin admissible est découvert ») : **0 résultat changé sur 105 rejeux**, fenêtre 480-570 de la mine −23 %, chronique
identique ; à l'auberge +12 % parce que le prototype faisait deux passes : il faut **retenir la découverte par PNJ et
par but** (dans le graphe repris, comme la lumière employée), pas refaire une passe à chaque recherche.

## L'invariant
**Une recherche n'explore l'allure feutrée que si un geste qu'elle peut offrir a besoin de discrétion** (un geste sans
témoin ou qui veut ne pas être entendu, selon ce que lisent déjà les gestes). La découverte se fait par les lectures
communes, est retenue dans le graphe repris (marque, comme `emploie_lumiere`) et relue quand ses entrées changent ;
`_sans_plan`/`_parcours` emploient les mêmes départs ; ce que lit la règle entre dans `_entrees` ; `VERIFIER` fait la
même chose. Ne change aucun coût, prix, borne ni donnée.

**Contrat** (celui des lots 46 et 48) : décisions identiques partout où la recherche de référence n'atteint pas son
plafond ; là où elle l'atteint (`BORNES`), le résultat doit égaler celui de la recherche complète (`REFERENCE`) ;
divergences localisées à leur première recherche et justifiées ainsi ; après bifurcation, mesures seulement.

## Vérification (demandée expressément)
- Tests après rechargement : Rémy (capture `tests/data/cout-12h/mine-1985-480.json.gz`) : moins d'états, même
  résultat ; un voleur dont le plan a besoin de discrétion (crue ou Relais, Brune devant la réserve) : l'allure feutrée
  reste explorée et le plan identique ; la marque retenue puis relue quand un geste discret devient possible.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference d60b80a`), quatre scénarios × 4 graines.
- **Temps sur 12 h** : `42bb9c0`, la base `d60b80a` et la branche **lancés ensemble**
  (`tools/empreintes_nuits.py jouer --heures 12 --scenarios mine auberge --graines 42 1985 --processus 2`), CPU par
  nuit et par tranche, nœuds, bornées ; `comparer --calcul` base contre branche, divergences justifiées.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la règle, sa marque), `docs/etat-dev.md`
(« Branche `codex-depart-feutre`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-51-depart-feutre.md` (règle, fonctions, temps par tranche, nœuds, divergences, limites).
