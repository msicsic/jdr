# Tâche Codex 7 : le corps blessable (étape 4a du plan force)

Branche `codex-force-4a` (ce fichier y est déjà ; travaille dessus, à partir d'elle). Lis d'abord
`AGENTS.md` (règles de conception et de travail), `docs/etat-dev.md` (dont « Décisions prises le
2026-10-22 », entrées `temps-reel` et `relations-socle`), puis `docs/plan-force.md` **en entier** :
tu réalises la sous-étape **4a. Le corps blessable**, et seulement elle.

## Décisions de l'utilisateur (à appliquer)
- Les coups ne tuent jamais : PV 0 met hors de combat, seule l'action `tuer` (étape 4e) donne la mort.
- Douceur 100 peut frapper pour se défendre ou défendre un protégé (écart à la recommandation 6 du plan ;
  sans effet en 4a, où personne ne frappe, mais ne ferme pas cette porte).
- Joueur inconscient : le temps passe jusqu'au réveil dans la même action.
- Pas de mort par faim, froid ou eau à cette étape (le corps garde au moins 1 PV).
- Toutes les autres décisions du plan (« Décisions à trancher ») : la recommandation du plan.
- Pas de migration des anciennes sauvegardes ; les profils des PNJ peuvent être modifiés.

## Points d'attention
- Le corps vit déjà au temps vécu (`donjon/vecu.py`, `corps.py`, branche `temps-reel`) : le repos qui
  soigne et l'inconscience s'y branchent, sans revenir à une vie minute par minute.
- `donjon/relations.py` est le seul accès à ce qu'un personnage éprouve envers un autre
  (`tests/test_relations_socle.py`) ; une branche parallèle (`codex-relations-3b`) le fait évoluer :
  n'y ajoute que des causes nommées si tu en as besoin.
- L'inconscience coupe perception, ouïe, délibération et parole : passe par les points d'entrée
  communs (`esprits.percevoir_tous`, `ouie`, `deliberation`, `pnj.peuvent_se_parler`, `appel`), jamais
  par un test sur un nom.
- Critère de 4a : bancs de référence (Relais 8 graines, mine, auberge, crue 4 graines, 8 h) identiques à
  `main` (empreintes ; l'état final ne diffère que par les champs ajoutés). Utilise
  `tools/comparer_bancs.py --empreintes` s'il est sur `main` (branche `codex-outils`, sinon depuis
  `origin/codex-outils`). Épreuves avec `banc_pnj --etat` : `ilse:inconscient` et `aubin:mort` au Relais.

## Vérifications
- Ce que demande la sous-étape 4a du plan (critères communs du « Découpage » compris : `Monde.verifier`
  avec les invariants nouveaux, même laps découpé, nuit au plus 10 % plus lente, tests après
  rechargement sur le cas qui guide la règle et un autre de même nature).
- Suite complète verte (`tools/tests.py` s'il est sur `main`, sinon unittest), en priorité réduite ;
  `planification.VERIFIER` et `spatial.VERIFICATION` 0,2 sur une nuit de 8 h de chaque scénario.
- Bancs : `--processus 4` au plus (une session Claude mesure des temps de calcul sur cette machine).
- Docs : `docs/plan-force.md` (4a « Fait », limites), `docs/mecaniques.md` (ce que voit le joueur),
  `docs/etat-dev.md` (« Branche `codex-force-4a`, non fusionnée », compte de tests).

## Livraison
Pousse la branche `codex-force-4a` sur `origin` (jamais `main`, pas de PR). Rapport dans
`docs/taches/rapport-codex-7-force-4a.md` : règles, fonctions, cas vérifiés, mesures, critère atteint ou
non, limites.
