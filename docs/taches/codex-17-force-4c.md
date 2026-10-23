# Tâche Codex 17 : se défendre, fuir, protéger, se rendre (plan force, étape 4c)

Branche `codex-force-4c` (elle porte ce fichier, issue de `main` 9520f77), worktree dans `tmp-worktrees/`.
Lis `AGENTS.md`, `docs/etat-dev.md` (« Décisions prises le 2026-10-22 », plan force ; entrées `codex-force-4a`,
`codex-force-4b` et leurs lignes « Fusionné après … »), `docs/taches/rapport-codex-12-force-4b.md`, et
`docs/plan-force.md` en entier, dont « Le prix et le risque », « Quand frapper », « Se défendre, fuir, se
rendre », « Le protecteur qui accourt », « Découpage » et **4c**, que tu réalises.

## Décisions de l'utilisateur (à appliquer)
- Les coups ne tuent jamais : PV 0 = hors de combat ; seul « tuer » (4e) donne la mort.
- **Douceur 100 peut frapper pour se défendre ou défendre un protégé** (écart à la recommandation du plan) :
  c'est en 4c que cette défense devient un geste ; `combat.prix_violence` la prévoit déjà.
- Joueur assommé : le temps passe jusqu'au réveil (4a).
- Le reste selon les recommandations du plan. Rancunes et peurs nées d'une agression par `relations.EPREUVES`,
  une cause par épreuve.

## Périmètre : 4c seulement
Danger perçu ; buts fuir, riposter, se dégager, se rendre ; cri et appel ; le protecteur fondu dans l'ouïe
commune (but protéger) ; force crue (`force.force_crue`) ; poursuite et renoncement de l'agresseur. Le joueur :
ce qu'il peut faire face à un agresseur (fuir, riposter, se rendre) par les actions communes, avec fiche et
`attendu`. Pas de lien (4d), de `tuer` (4e), ni de consignes Luna au-delà du typage des actions (4f).

Au passage, une règle dupliquée relevée à la fusion de 4b : `combat.prix_violence` n'est employé que par les
tests, le planificateur réécrit la même règle (`2 * v.degat <= ENJEU`, `abime = 2 * doux`). Une seule règle,
au même endroit, pour l'agression et pour la défense.

## Vérifications
- L'épreuve et le critère de 4c tels que le plan les écrit : Brune frappe Aubin sous les yeux d'Ilse, Gorm à
  l'échoppe ; Ilse fuit ou s'abrite, Aubin riposte ou se dégage, Gorm vient à l'appel et intervient ; tout
  affrontement finit (hors de combat, fuite, reddition ou renoncement) en moins de 10 minutes de jeu ; aucun
  meurtre. Tests après rechargement (cas de l'épreuve et un autre de même nature par règle), même laps d'un
  bloc ou découpé, ce que lit le joueur.
- Les bancs de référence (quatre scénarios) restent identiques tant que rien n'y frappe : empreintes 2 h et 8 h
  (`tools/comparer_bancs.py --empreintes`) ; tout écart expliqué.
- `rixe` 8 graines, 8 h : minutes urgentes sans recours pas plus de 10 % au-dessus de celles du Relais ; aucune
  usurpation, violation ni mort.
- `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42, chaque scénario et
  `rixe` : sans écart (toute lecture nouvelle dans `_entrees` ; graphes `sombre`/`lumiere` et certificat
  `_sans_plan` exacts).
- Luna (connexion sur ce poste, `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, plusieurs exécutions en
  parallèle permises, sur des copies seulement) : une scène où un PNJ attaque le joueur (préparée dans
  `tests/data/bancs`) : « je m'enfuis », « je me défends », « je me rends » ; typés, issue du moteur seule.
- Suite complète verte (`tools/tests.py`). Docs : `docs/plan-force.md` (4c « Fait », limites),
  `docs/mecaniques.md`, `docs/etat-dev.md` (« Branche `codex-force-4c`, non fusionnée », compte de tests).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-17-force-4c.md` : règles, fonctions, cas vérifiés, mesures, critère, limites.
Trois branches sont en cours de fusion (Luna et noms, restes des fusions, signalements) et deux en cours
(relations 3c, part estimée) : garde les changements localisés.
