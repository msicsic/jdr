# Tâche Codex 12 : le coup et assommer (plan force, étape 4b)

Branche `codex-force-4b` (elle porte ce fichier, issue de `main` après la fusion des relations 3b et du
corps blessable 4a), worktree dans `tmp-worktrees/`. Lis `AGENTS.md`, `docs/etat-dev.md` (« Décisions
prises le 2026-10-22 », plan force ; entrées `codex-force-4a`, `codex-relations-3b`),
`docs/taches/rapport-codex-7-force-4a.md`, et `docs/plan-force.md` en entier, dont « Découpage » (le
scénario d'épreuve `rixe`, `--etat`, les mesures et critères communs) et **4b**, que tu réalises.

## Décisions de l'utilisateur (à appliquer)
- Les coups ne tuent jamais : PV 0 = hors de combat ; seul « tuer » (4e) donne la mort.
- **Douceur 100 peut frapper pour se défendre ou défendre un protégé** (écart à la recommandation du
  plan) ; en 4b, la défense elle-même est 4c : prévois seulement que la faute de violence ne l'interdise
  pas à douceur 100 quand ce sera une défense.
- Joueur assommé : le temps passe jusqu'au réveil (fait en 4a, `Moteur._attendre_reveil`).
- Le reste selon les recommandations du plan. Les rancunes et peurs nées d'un coup passent par
  `relations.EPREUVES` (3b), une cause par épreuve.

## Périmètre : 4b seulement
Règle du coup (armes, surprise, esquive, dégâts, cri, interruption), assommer ; action `frapper` du
joueur sur un personnage, fiche et `attendu` (`donjon/refus.py`) ; geste exécutable des PNJ ; registre et
témoins (vue et ouïe) ; souvenirs `subi` et `a_frappe` ; faute de violence au prix de la douceur ;
premier recours qui frappe : **assommer pour prendre** dans le planificateur, avec l'étape `dans_le_dos`.
Le scénario `rixe` et sa variante douce (données seules, dérivées du Relais comme la crue). Mesures et
section « Violences » du récit, rejeu. Pas de fuite, riposte, reddition (4c), de lien (4d), de `tuer` (4e),
ni de consignes Luna au-delà du typage de `frapper` (4f).

## Vérifications
- L'épreuve et le critère de 4b tels que le plan les écrit : Brune, affamée et refusée, devant Gorm qui
  porte la clé de la réserve ; la variante douce ne frappe jamais ; Brune n'assomme Gorm que dans son dos,
  au pas feutré, sans témoin cru (sauf désespoir), et préfère demander d'abord ; qui la voit se méfie ;
  Gorm réveillé sait qui l'a frappé seulement s'il l'a perçue ; aucun mort. Tests après rechargement, le
  cas réel et un autre de même nature, même laps d'un bloc ou découpé.
- Les bancs de référence (quatre scénarios) restent identiques à `main` : empreintes 2 h et 8 h
  (`tools/comparer_bancs.py --empreintes`), aucun PNJ n'y frappe.
- `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42, de chaque
  scénario et de `rixe`, sans écart. `Monde.verifier` à chaque pas.
- `rixe` et sa variante, 8 graines, 8 h ; coût du planificateur (nœuds, temps) dans la marge (+10 %).
- Luna (plusieurs exécutions en parallèle permises, sur des copies) : « je frappe Brune », « j'assomme
  Gorm par derrière » : typés `frapper`, résultat établi par le moteur, rien de plus raconté.
- Suite complète verte (`tools/tests.py`). Docs : `docs/plan-force.md` (4b « Fait », limites),
  `docs/mecaniques.md` (frapper), `docs/etat-dev.md` (« Branche `codex-force-4b`, non fusionnée »).

## Rapport
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-12-force-4b.md` : règles, fonctions, cas vérifiés, mesures, critère, limites.
