# Rapport Codex 23 — A0, l'échelle du choix

Branche `codex-a0-echelle`, **non fusionnée**, base `main` **42bb9c0**, brief **6772f31**.
Worktree `tmp-worktrees/codex-a0-echelle`. Livraison par commit signé SSH, poussée sur cette
branche ; aucune fusion dans `main`. Seuls `donjon/deliberation.py`, les tests et la doc changent.

**Invariant.** Chaque `Candidat` porte une `Urgence(palier, valeur, departage)` ; `_candidats`
ne décide de l'ordre que par le tri `(palier, -valeur, departage)`. Les treize paliers sont :
péril de l'eau, alarme, ranimer, besoin pressant, parole due, prévenir, rejoindre, attendre
l'appelant, bruit à voir, pulsion rompue, progrès en cours, routine, argent. Au palier des
besoins pressants, la valeur est besoin − seuil, exactement comme `urgents`. Ailleurs elle
vaut zéro. Aucun agenda ni nouveau traitement du désespoir n'est ajouté.

**Égalités.** Besoins : ordre `BESOINS`, puis ordre déclaré des recours. Protégés à ranimer :
ordre inverse du profil, conservant les anciennes insertions en tête. Paroles dues : ordre
enregistré, sans tri nouveau des échéances. Pulsions : ordre du profil, rétablissement avant
enquête. Progrès : ordre `PROGRES`. Routines : celles issues des besoins pressants d'abord,
par écart décroissant, `BESOINS` et recours ; puis les autres, par ordre du profil. Argent :
créance avant pièces. Ces départages figurent dans la clé ; le tri stable ne décide plus.
`candidats` conserve son contrat public ; dans `choisir`, seul le déballage du cinquième champ
change. Hystérésis, `INERTIE`, plans et sauvegardes restent les mêmes. L'urgence est recalculée.

**Preuves.** `tests/test_echelle_choix.py` copie l'ancienne `_candidats` de 42bb9c0 ; son AST
est identique, à part le nom et les imports absolus nécessaires au test. Comparaison ordonnée
besoin/routine/recours/identité de méthode (corps et arguments liés pour les fonctions anonymes) :
chaque choix de dix nuits de 2 h, Relais, mine, auberge, crue et `rixe`, graines 1985 et 7.
Scènes couvrant les treize paliers, plusieurs protégés et engagements, besoins à égalité et
au seuil ; clés sans égalité résiduelle. Même ordre après sauvegarde/rechargement. Deux parcours
réels Relais/auberge jouent aussi l'ancien et le nouveau choix : mêmes actions, données complètes,
textes du moteur, fiche et perception après chaque rechargement. **4 tests ciblés verts (64,4 s).**

Suite complète, une seule passe, `tools/tests.py --processus 3` : **1 595 tests, 15 ignorés, verte (864,7 s)**.
Empreintes prescrites contre **42bb9c0**, 2 h, quatre scénarios × quatre graines
(1985, 7, 42, 2024) : **16 paires identiques**, chronique, mesures et état final complet.
CPU moyen par nuit, référence → branche : Relais 3,44 → 3,76 s ; mine 8,14 → 9,80 s ;
auberge 5,38 → 7,08 s ; crue 5,74 → 7,14 s. Ces temps ne démontrent pas une stabilité du coût ;
la charge du poste n'était pas isolée et le surcoût n'a pas été attribué dans ce lot.

**Traces et limites.** Dans `artifacts/` du worktree : `a0-tests-cibles.json`, `a0-suite.json`,
`a0-empreintes.json`. Référence conservée une fois dans
`artifacts/references/42bb9c0344f1c943f5b1d9ea40c012810380ee9a/a0-empreintes-2h.json` du dépôt
principal. Aucune Luna, aucun banc de 8 h, aucune sauvegarde de partie utilisée. Les dix nuits
ne constituent pas une exploration exhaustive ; l'équivalence observée porte sur ces choix,
scènes et empreintes. La vérification longue appartient à l'intégration. Le contrat privé de
`_candidats` passe de quatre à cinq champs ; tous ses consommateurs de production sont dans
`deliberation.py` et sont adaptés. Les règles futures d'agendas restent hors de ce lot.
