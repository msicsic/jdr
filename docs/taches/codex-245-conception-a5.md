# Tâche Codex 245 (conception) : état des lieux et découpage d'A5, mandat et autorité

Décision du 2026-10-28 (`docs/etat-dev.md`, « Feuille de route ») : après la consolidation, ouvrir **A5, mandat et
autorité**. Ce lot prépare A5 **sans code du jeu** : il dit ce qui existe déjà, ce qui manque, et propose les lots.

Sources : `docs/plan-agendas.md` (§ 6.6 le mandat, § 9 « A5 », § 10 décisions 1 à 7 du 2026-10-23, dont l'autorité à
trois sources), `docs/plan-relations.md` (axes, `chance_demande`), et ce qui est déjà livré : `confier` (lots 146 e,
122 intermédiaires), aides acceptées et attente (lot 240), suivi d'une délégation à échéance (lot 242, branche
`codex-suivi-delegation`, peut-être non fusionnée : lis son rapport s'il existe), contrat d'engagement (213), agendas
`amener`/`informer`/`garder`/`protéger` (144–167 c). Épreuve prévue : la crue étendue au hameau, Gorm, responsable des
lieux, confie Brune à Aubin.

Lot de 30 à 45 minutes. **Pas de calcul long, pas de banc, pas de suite** : lecture du code et des rapports, au plus des
scènes courtes pour vérifier qu'une pièce existe.

**Poste : le PC fixe** ; un seul processus, priorité réduite.

## Ce que le rapport doit donner (une à deux pages)
1. **Inventaire** : pour chaque élément du § 6.6 (mandater, jugement du mandaté, agenda d'origine `mandat`, suivi et
   compte rendu, réaffectation, parole et voix, récursion bornée) et de l'autorité (statut du scénario, sixième axe
   « ascendant », lecture dérivée) : **existe** (fonction, fichier), **partiel** (ce qui manque), **absent**.
2. **Découpage en lots** de 30 à 45 minutes, **un invariant par lot**, dans l'ordre : pour chacun, l'invariant, les
   fichiers touchés, les fichiers à ne pas toucher, le cas réel ou la scène d'épreuve, ce qui prouvera le lot (tests
   après rechargement, banc rapide), et **les extensions de périmètre prévisibles à autoriser d'avance** (raccords,
   tests voisins).
3. Les décisions qui reviennent à l'utilisateur (ce qui changerait une règle établie côté joueur, une valeur de
   scénario, une donnée d'autorité à déclarer), formulées en options.

## Livraison
- Branche `codex-conception-a5` : seulement `docs/taches/rapport-codex-245-conception-a5.md` et une entrée « Branche
  `codex-conception-a5`, non fusionnée » dans `docs/etat-dev.md`. Poussée (pas `main`) ; si la revue bloque, laisse le
  commit local et dis-le. Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
