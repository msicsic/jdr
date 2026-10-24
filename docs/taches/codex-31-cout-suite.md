# Tâche Codex 31 : deux coûts exacts révélés par le profil (trajet estimé, ce que retient le joueur)

Branche `codex-cout-exact` (elle porte ce fichier, issue de l'intégration **2590c4a** : lots 27, 28 et 30
fusionnés), worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »).
Pas de Luna sur ce poste.

Lis `AGENTS.md`, `docs/etat-dev.md` (lots 28 et 30, « À revoir »), `docs/taches/rapport-codex-30-trajet-estime.md`.

## L'invariant
**Mêmes décisions, même monde, moins de calcul** : chronique, mesures, état final complet et recherches
identiques à 2590c4a ; seules des lectures gardées sous des clés qui disent tout ce qu'elles lisent, chacune
recomparée à son calcul pur par `spatial.VERIFICATION`.

## Ce que montre le profil (py-spy, 100 Hz, mine 4 h graine 42, 42bb9c0 → 2590c4a, échantillons ×1,49)
1. **`trajet_estime` : 13,9 % de la nuit**, dans `_explorer_etats`. L'estimation ne dépend que de la
   géométrie de la salle, des obstacles crus, de la cible et de l'allure (vérifie-le) : elle se recalcule
   pourtant à chaque développement. La recherche entière passe de 3 257 à 10 880 échantillons.
2. **Côté joueur, hors de la vie des PNJ** (hors `pnj._avancer`) : 531 → environ 8 000 échantillons (2 % →
   20 % de la nuit) :
   - `moteur._terminer_etape` → `spatial.memoriser` → `_memoriser` → `carte.symbole_objet_cases` : 152 → 2 363 ;
   - `moteur.executer` → `noms.texte` → `_remplacer_noms` → `_designation_texte` (`voix.designation`,
     `noms.nom`) : 41 → 1 282 ;
   - `_clore_bilan` 51 → 700 ; `monde.actualiser_souvenirs_personnages` → `presents` → `visible` 27 → 538 ;
     `monde.copier` 45 → 475 ; `deliberation.autour` appelé par le banc 25 → 642.
   Trouve d'abord quel lot l'a fait croître (`git bisect` ou mesure aux fusions entre 42bb9c0 et 2590c4a :
   Q, R, lots 25 à 27, 30), puis la cause (lecture répétée, invalidation trop large, cache perdu).
   Ce coût vaut aussi pour le jeu réel, à chaque action du joueur.
Profil par toi-même d'abord (`py-spy record --format raw`, ou `tools/` existants) pour confirmer.

## Vérification (minimale)
- Empreintes 2 h, quatre scénarios × 4 graines, contre 2590c4a (`tools/comparer_bancs.py --empreintes`) :
  identiques, recherches et nœuds compris.
- `spatial.VERIFICATION` 1 + `VERIFIER`, 2 h, graine 42, mine et auberge : sans écart.
- Temps : 42bb9c0, 2590c4a et la branche **lancés ensemble** (`--sans-cache`), 4 h, graines 42 et 1985, mine
  et auberge ; profil final (parts des postes ci-dessus avant → après).
- Tests ciblés ; suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés (un par levier), branche poussée (pas `main`). `docs/etat-dev.md` (« Branche
`codex-cout-exact`, non fusionnée » ; « À revoir » : coût). Rapport d'une page :
`docs/taches/rapport-codex-31-cout-exact.md` (lot fautif et cause, clés, mesures, ce qui reste).
