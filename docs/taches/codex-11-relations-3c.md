# Tâche Codex 11 : les signes et leur lecture (relations, sous-étape 3c)

Branche `codex-relations-3c` (elle porte ce fichier, issue de `main` après la fusion des relations 3b et
du corps blessable 4a), worktree dans `tmp-worktrees/`. Chantier important : prends le temps de lire.
`AGENTS.md`, `docs/etat-dev.md` (« Décisions prises le 2026-10-22 », entrées `relations-socle`,
`codex-relations-3b`), `docs/taches/rapport-codex-6-relations-3b.md`, et surtout `docs/plan-relations.md`
en entier, dont § 5 et § 6 (signes, lectures, usages des PNJ), « 9. Sous-étapes » et **3c**, que tu
réalises. `donjon/relations.py` reste le seul accès à ce qu'un personnage éprouve envers un autre.

## Décisions de l'utilisateur (à appliquer)
- Le joueur perçoit signes et impressions (commande `observer`) ; sa PSY peut le tromper (méprises).
- Toutes les autres décisions du § 12 : la recommandation du plan. Seuils et constantes réglés au banc.
- Pas de migration des anciennes sauvegardes ; les profils des PNJ peuvent être modifiés.

## Périmètre : 3c seulement
Ce que dit la section 3c : `emotions` (colère), source « devine », lectures dans les croyances,
`data["lectures"]` du joueur, attitude dans l'intention, tirage à part pour les lectures (les autres jets
de la nuit ne se décalent pas) ; table `SIGNES`, place et regard, expressions et ton, dissimulation, jet de
lecture, méprises, usages des PNJ (§ 6.3, sauf la chance estimée qui remplace `PRET`, réservée à 3e) ;
le joueur : `bilan_signes`, `observer`, la carte et le rendu ; l'humeur retirée ; l'outil
`banc_pnj --regler gorm.PSY=16` ; les mesures nouvelles. Pas d'empathie (3d), de propositions (3e),
d'avis (3f). Le MJ reçoit ce que le joueur perçoit (signes, lectures du joueur), jamais les axes ni la
lecture vraie : contrôle déterministe que rien d'autre ne fuit vers Luna.

## Vérifications
- L'épreuve et le critère de 3c tels que le plan les écrit (tests après rechargement : le guet de Brune
  lu par Gorm à PSY 14 et manqué à PSY 8 ; Ilse à l'écart de Brune vue par le joueur puis `observer` ; la
  même scène dans le noir sans signe ni impression ; un autre cas de même nature par règle nouvelle).
- Les lectures entrent dans `planification._entrees` et dans les clés de perception de `cout-calcul` :
  `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42, de chaque
  scénario, sans écart.
- Suite complète verte (`tools/tests.py`). Bancs : changement profond, banc complet du plan (Relais 8
  graines, mine, auberge, crue 4 graines, 8 h), `main` puis la branche, `--processus 4` au plus
  (`tools/comparer_bancs.py`). Mesures du plan (`signes`, `lectures`, `justesse` par tranche de PSY,
  `meprises`, `guets_reperes`, `attentes_sous_regard`), vols tentés et vus, temps (au plus +20 %).
- Luna (plusieurs exécutions en parallèle permises, sur des copies) : « observer Brune », une scène où le
  joueur voit un signe ; Luna ne raconte pas plus que ce que le moteur a établi.
- Docs : `docs/plan-relations.md` (3c « Fait », limites), `docs/mecaniques.md` (`observer`, ce que le
  joueur voit), `docs/etat-dev.md` (« Branche `codex-relations-3c`, non fusionnée », compte de tests).

## Rapport
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-11-relations-3c.md` : règles, fonctions, cas vérifiés, mesures avant → après,
critère atteint ou non, limites, réglages proposés.
