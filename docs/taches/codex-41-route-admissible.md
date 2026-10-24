# Tâche Codex 41 : une seule admissibilité de route, pour la recherche et pour la marche

Branche `codex-route-admissible` (elle porte ce fichier, issue de l'intégration **750837a** : lots 38 et 39
compris), worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un
invariant, vérification minimale, rapport d'une page. Pas de Luna sur ce poste (aucun changement du MJ).

Un autre lot tourne sur l'autre poste (40, l'auditeur du MJ : `narration.py`, `mj.py`). Ne touche pas au MJ.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-refuge-mouille` et `codex-cout-12h`, `verifier-eau`),
**le rapport du lot 39** `docs/taches/rapport-codex-39-refuge-mouille.md` (le diagnostic, à suivre),
`docs/plan-crue.md` (« L'eau dans tous les plans »), `docs/plan-planificateur.md` (modèle de trajet de la
recherche, borne du lot 38), puis `donjon/planification.py` (`Vue.descente`, `Vue.piege`, `Vue.route`,
`Vue.allers`, `_entrees`), `donjon/trajet_estime.py` (`parcours`), `donjon/pnj.py` (`_marcher`, `chemin`),
`donjon/eau.py` (`attendue`, `en_peril`), et `tools/diagnostic_refuge_mouille.py`.

## Le constat (lot 39)
Crue 500 : Aubin choisit la galerie sèche à 156 min, Brune le poêle du guet à 160 ; leur route estimée (0,789 min)
passe par la conduite (84 cm, 124 attendus) et les vannes. La recherche ne contrôle la descente que pour la
destination ; la marche (`pnj._marcher`, renforcée par `8f60441` contre un vrai piège) l'applique aussi aux salles
traversées et refuse sans bouger. À 182 la conduite est noyée et tous restent au refuge mouillé jusqu'à 360-404.
La prévision de l'eau prend 60 minutes même pour une traversée de quelques secondes.

## L'invariant
**Une seule fonction juge si une route est praticable, sur les croyances du PNJ, salle par salle et porte par
porte, et la recherche comme la marche l'appellent.** Elle distingue :
- **traverser** une salle : le risque se juge à l'eau crue ou attendue **pendant le passage** (durée estimée du
  séjour, pas un horizon fixe de 60 min) ;
- **séjourner** au but : l'horizon du but qui se tient en restant, comme aujourd'hui ;
- **revenir ou évacuer** : ne pas descendre vers un lieu d'où le retour serait coupé (le piège que garde
  `8f60441`), y compris quand ouvrir une porte demande une attente ou un crochetage incertain.

Une route que la recherche accepte, la marche l'accepte dans le même état de croyances ; un refus de la marche ne
peut venir que d'un fait nouveau (eau montée, porte trouvée fermée), appris et suivi d'une nouvelle délibération.
La cause du refus ou de l'attente se lit dans le récit (« reste au refuge : la conduite est noyée »). Ne touche ni
aux personnages, ni aux ressources, ni à `REPIT`, ni aux seuils d'eau des scénarios. Ce que lit la fonction entre
dans `_entrees` ; `planification.VERIFIER` refait la recherche avec la même règle ; la borne du lot 38 reste
admissible (dis pourquoi).

## Vérification (minimale)
- Tests après rechargement, même laps découpé : les deux captures du lot 39
  (`tests/data/scenes/refuge-mouille-crue500-160.json.gz`, `refuge-mouille-auteur-100.json.gz`) : le PNJ part et
  arrive au sec ; une scène où la traversée serait vraiment trop longue ou le retour coupé : il ne part pas, et le
  récit dit pourquoi ; `tests.test_signes_calibration.TrajetsRevelesTests` reste vert (le détour dangereux).
- Banc rapide (`tools/comparer_bancs.py --reference 750837a`, 4 h, 4 graines, crue et Relais) : aucune
  usurpation, violation, plantage ni boucle nouvelle (`tools/audit_nuits.py` : bascules, passages par heure) ;
  écarts lus en deux lignes. Puis l'audit 12 h de la crue 500 et d'une autre graine de crue, branche seule, contre
  les nuits ffcc295 conservées (`artifacts/verif-integ-ffcc295/` du dépôt principal) : minutes dans l'eau, sans
  recours, constats « eau longue ».
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, crue 42 et 500 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-crue.md` (la règle de traversée, séjour, retour),
`docs/etat-dev.md` (« Branche `codex-route-admissible`, non fusionnée » ; « À revoir » mis à jour). Rapport d'une
page : `docs/taches/rapport-codex-41-route-admissible.md` (invariant, fonctions, mesures, limites, coût CPU si
la fonction pèse).
