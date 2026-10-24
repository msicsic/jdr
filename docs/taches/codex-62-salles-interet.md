# Tâche Codex 62 : un plan ne s'arrête que dans une salle où il agit

Branche `codex-salles-interet` (elle porte ce fichier, issue de l'intégration **04bca30** : lots 38 à 56 compris),
worktree dans `tmp-worktrees/`. Lot de coût, demandé expressément par l'utilisateur (« les bancs sont trop lents »).
Pas de Luna. Les lots 57, 58 et 59 entrent dans l'intégration pendant ton lot : `git merge origin/integration` au
début si elle a avancé (58 touche `eau.py`, 57 `pnj_propositions.py`/`echanges.py`).

Lot en même temps sur ce poste : 60 (`appel.py`). Ce lot touche `planification.gestes` (le geste `aller`) et la
`Vue` ; pas `appel.py`. Deux lots font des bancs : priorité réduite, au plus 4 processus.

Lis `AGENTS.md`, `docs/etat-dev.md` (« À revoir », volet coût : **P3** et le principe « réduire l'espace plutôt
qu'ajouter un cache » ; entrées `codex-une-source` 46, `codex-borne-rester` 48, `codex-depart-feutre` 51 et leur
contrat ; `codex-capacite-nouvelle` 52 non fusionné : pourquoi C1 n'a rien gagné), `docs/plan-planificateur.md`,
puis `donjon/planification.py` (`gestes`, la boucle `for s, longueur in v.allers(e, v.ouvertes(e))`, `Vue.allers`,
`Vue.route`, la pression par minute, `_entrees`, `VERIFIER`, `REFERENCE`, `BORNES`).

## Le constat
Le coût est concentré sur quelques nuits (lot 52, 12 h, CPU ancien / base) : mine 1985 tiré 78 / 490 s avec 137
recherches bornées, auberge 1985 fixe 72 / 363 s avec 203 bornées, alors que mine 42 tiré est **plus rapide** que
`main` (87 / 61 s). 68 à 88 % du coût de fin de nuit vient de recherches **sans plan**, que seul un espace plus
petit rend moins chères. Or `gestes` offre, depuis chaque état, un `aller` vers **chaque** salle accessible, même
vide de tout ce que le plan peut employer ; les trajets directs de `allers` (route entière, plusieurs salles)
rendent ces arrêts inutiles.

## D'abord, mesurer
Sur les deux nuits lourdes (mine 1985 tiré, auberge 1985 fixe), fin de nuit : quelles recherches sont bornées
(PNJ, but), combien d'états y viennent d'un `aller` vers une salle où le plan n'agit pas ensuite. Si ce n'est pas
la cause principale, dis ce qui l'est, chiffres à l'appui, et arrête-toi là (diagnostic).

## L'invariant
**Un `aller` ne mène qu'à une salle d'intérêt pour la recherche en cours** : une salle où se trouve (cru) un objet ou
une porte que les gestes peuvent employer pour ce but, une personne utile (porteur, donneur, cible), le lieu du but,
ou un abri/lieu qui se tient en restant ; toute autre salle n'est traversée que par un trajet direct. Démontre que
c'est exact avec les coûts réels : route directe au plus aussi chère que l'arrêt intermédiaire (pression, noir, eau
par minute, route admissible du lot 41), gestes qui agissent sans objet (inspecter, appeler, chercher quelqu'un,
regarder) ; un arrêt nécessaire pour ces gestes reste offert. L'ensemble se calcule une fois par `Vue` et par but ;
ce qu'il lit entre dans `_entrees` ; `VERIFIER` applique la même règle.

**Contrat** (lots 46, 48, 51) : décisions identiques là où la référence n'atteint pas son plafond ; là où elle
l'atteint, résultat égal à la recherche complète (`REFERENCE`) ; divergences localisées et justifiées ; après
bifurcation, mesures seulement.

## Vérification (demandée expressément)
- Tests après rechargement : une recherche réelle de chacune des deux nuits lourdes (capture) : moins d'états, même
  résultat que la complète ; un plan qui doit s'arrêter pour inspecter ou appeler dans une salle vide : arrêt gardé.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference 04bca30`), quatre scénarios × 4 graines.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche **lancés ensemble** (`tools/empreintes_nuits.py jouer
  --heures 12 --scenarios mine auberge --graines 42 1985 --processus 2`, tiré et fixe), CPU par nuit et par tranche,
  nœuds, bornées ; `comparer --calcul` base contre branche, divergences justifiées.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la règle et sa preuve),
`docs/etat-dev.md` (« Branche `codex-salles-interet`, non fusionnée » ; P3 dans « À revoir » mis à jour). Rapport
d'une page : `docs/taches/rapport-codex-62-salles-interet.md` (mesure préalable, règle, temps, nœuds, limites).
