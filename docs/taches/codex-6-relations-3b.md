# Tâche Codex 6 : les relations graduées (sous-étape 3b)

Branche `codex-relations-3b`, worktree dans `tmp-worktrees/`. Chantier important : prends le temps
de lire. `AGENTS.md`, `docs/etat-dev.md` (« Décisions prises le 2026-10-22 », entrée
`relations-socle`), et surtout `docs/plan-relations.md` en entier, dont « 9. Sous-étapes », 3a
(fait, branche `relations-socle`) et **3b**, que tu réalises. `donjon/relations.py` est le seul accès
à ce qu'un personnage éprouve envers un autre ; `tests/test_relations_socle.py` le garantit et doit
continuer de passer.

## Décisions de l'utilisateur (à appliquer)
- Cinq axes : confiance, affection, rancune, peur, dette (§ 12, décision 1, (a)).
- Toutes les autres décisions du § 12 : la recommandation du plan. Seule précision : un PNJ donne
  son avis sans qu'on le lui demande seulement si l'autre risque d'agir contre et qu'il s'en soucie
  (décision 13 (a) ; cela relève de 3f, pas de 3b).
- Seuils (méfiance sous 30, confiance dès 60, hystérésis, demi-vies) : la méthode du plan, les
  nombres réglés au banc.
- Pas de migration des anciennes sauvegardes ; les profils des PNJ peuvent être modifiés.

## Périmètre : 3b seulement
Ce que dit la section 3b du plan : `relations` dans l'esprit, `profil["liens"]`, la table
`EPREUVES` branchée sur les souvenirs, modulations par les valeurs, estompement, hystérésis, lectures
graduées (§ 3.5), `fiable` quitte les croyances (et les relations entrent dans
`planification._entrees` pour la mémoire des recherches : `VERIFIER` doit rester sans écart), liens
de départ de la crue en données, récit « Ce qu'ils pensent les uns des autres », rejeu, mesures
nouvelles (`mefiances`, `mefiances_levees`, `rancunes`, `dettes`, `dettes_honorees`,
`relations_changees`). Pas de signes (3c), d'empathie (3d), de propositions (3e), d'avis (3f), ni de
changement du MJ au-delà de ce que reçoit déjà `esprits_interlocuteurs` (qui doit rester juste).

## Vérifications
- Les épreuves et le critère de 3b, tels que le plan les écrit (tests après rechargement : Brune et
  Gorm à la crue, Odon et Mathe à la mine, le joueur surpris à voler qui rend l'objet ; et un autre
  cas de même nature pour chaque règle nouvelle).
- Suite complète verte (en priorité réduite, ou par `tools/tests.py` s'il est fusionné) ;
  `planification.VERIFIER` et `spatial.VERIFICATION` 0,2 sur une nuit de 8 h de chaque scénario.
- Bancs : changement profond, donc le banc complet que demande le plan (Relais 8 graines, mine,
  auberge, crue 4 graines, 8 h), `main` puis la branche, `--processus 4` au plus (d'autres agents
  tournent sur la machine). `tools/comparer_bancs.py` s'il est fusionné.
- Docs : `docs/plan-relations.md` (3b « Fait », limites), `docs/etat-dev.md` (« Branche
  `codex-relations-3b`, non fusionnée », compte de tests), `docs/mecaniques.md` si le joueur voit
  une différence.

## Rapport
Dans `docs/taches/rapport-codex-6-relations-3b.md` : règles, fonctions, cas vérifiés, mesures
avant → après, critère de 3b atteint ou non, limites, réglages proposés.
