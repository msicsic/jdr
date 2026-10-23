# Tâche Codex 16 : la part de combustible, une étape estimée dans la recherche

Branche `codex-part-estimee` (elle porte ce fichier, issue de `integration` 4fc5212 : `main` avec
`GARDE`/`PRET` et la force 4b), worktree dans `tmp-worktrees/`. Lis d'abord `AGENTS.md`, `docs/etat-dev.md`
(entrées `codex-lampes`, `codex-lampes-suite`, `codex-cout-suite`, `codex-garde-pret`, `pnj-lumiere-garde`),
`docs/plan-planificateur.md` (« Lumière », « Coût de calcul » et suites) et surtout
`docs/taches/rapport-codex-9-lampes-suite.md` (« Contre-épreuve : coût des remises simulées »).

**Pas de Luna sur ce poste** : ce lot n'en a pas besoin (moteur seul).

## Le constat
À l'auberge, une nuit de 12 h coûte ~196 s au processeur, dont l'essentiel vient de la projection des parts
remises (`planification._parts_remises`) : 1,39 M nœuds par nuit avec elle, 0,31 M avec un générateur vide
(68 s). Pour chaque PNJ qui emploie la lumière (peur du noir, but d'éclairer, lecture découverte), à chaque état
développé et pour chaque donneur, la recherche explore demander/acheter, attendre la remise, puis recharger,
allumer et finir le but. Or le plan exécuté **s'arrête déjà à la demande** : la suite est replanifiée sur la
part réellement reçue. Dans la recherche, la chaîne après la remise ne sert qu'à estimer le coût de cette voie.

## Décision de l'utilisateur (2026-10-23)
Option « étape estimée » : la recherche garde en détail le trajet jusqu'au donneur (avec tous ses coûts : noir,
eau, éloignement des biens, menaces) et la demande ou l'achat (chance de demande de `relations.chance_demande`,
prix) ; **ce qui suit la remise est un coût estimé une fois**, sans développer la chaîne recevoir → recharger →
allumer → finir le but dans la recherche. Elle se détaille après la remise, comme aujourd'hui. Les nuits
peuvent changer ; c'est accepté, dans les critères ci-dessous.

## L'invariant
- Une seule règle pour toute part remise (huile d'une lampe, bois d'un feu, toute part future), au même endroit
  que l'attente d'une part promise (`Vue.attente_part`) : pas de cas par substance, objet, personnage ou scénario.
- L'estimation est une borne raisonnée, écrite et justifiée dans le plan : ce que coûte, depuis le lieu de la
  remise, d'atteindre la source, de la recharger et de l'allumer, et ce qu'il reste du but (la pression de
  `Vue.pression` pendant ce temps : noir, eau, biens). Dis si elle peut sous-estimer, et quand.
- Ses lectures entrent dans `_entrees` ; la découverte de la lumière et les deux graphes (`sombre`/`lumiere`)
  et le certificat d'impossibilité (`_sans_plan`) restent exacts pour la nouvelle règle. `VERIFIER` compare
  désormais à la recherche complète **avec la même règle** (l'étape estimée fait partie du modèle).

## Mesures de la justesse de l'estimation
Instrumente une comparaison hors du jeu : pour chaque recherche où une étape estimée est choisie ou écartée,
refais la recherche avec la chaîne détaillée (l'ancienne règle) et compare le plan choisi (premier geste et but)
et les coûts. Rapporte : part des recherches au même choix, écarts de coût (médiane, pire cas), et les cas où le
choix diffère, lus un par un.

## Critères (au lieu de nuits identiques)
- Auberge 12 h, 8 graines : temps au processeur et nœuds avant → après (but : nettement moins, viser au moins
  ×2) ; recharges de lampes, demandes et achats de combustible, parts livrées pas en baisse notable ; minutes dans
  le noir et sans recours pas pires en moyenne (chaque nuit pire expliquée) ; foyers allumés.
- Les quatre scénarios, banc 8 h, 4 graines (`tools/comparer_bancs.py`) : mêmes contrôles ; aucune usurpation,
  violation, boucle nouvelle (`tools/audit_nuits.py analyser`).
- Choix identiques à la chaîne détaillée dans la grande majorité des recherches (mesure ci-dessus).

## Vérifications
- Tests après rechargement (`tests/test_part_estimee.py` et ceux des lampes existants, `test_lampes_parts`,
  `test_lampes_buts`) : le PNJ demande toujours la part, la reçoit, recharge, allume et finit son but ; un cas de
  bois pour un feu ; un cas où l'estimation fait préférer une autre voie et pourquoi c'est juste.
- Suite complète verte (`tools/tests.py`) ; `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis
  0,2 sur 8 h graine 42, chaque scénario, sans écart.
- Bancs `main` puis la branche l'un après l'autre (ou ensemble pour la mesure de temps), `--processus 4` au plus.
- Docs : `docs/plan-planificateur.md` (section nouvelle, l'estimation et ses limites), `docs/etat-dev.md`
  (« Branche `codex-part-estimee`, non fusionnée », compte de tests).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-16-part-estimee.md` : règle, estimation et sa justification, mesure de justesse,
temps et nœuds avant → après, mesures de comportement, limites.
