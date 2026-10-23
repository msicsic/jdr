# Lot 26 — Désignations enrichies

24 octobre 2026. Branche `codex-designations`, **non fusionnée**, base `42bb9c0`.
Correctif signé **6fbdda2** ; aucun fichier des lots réservés ni donnée de scénario modifié.

**Causes relues dans les fils du lot 22.** `livraison-r1/…-soir-noir.json` : le garde
retirait une chaîne exacte et refusait « la voix toute proche qui se dit Ilse » ;
sept appels et repli. `livraison-r2/…-atelier.json` : sans lien lexical entre les
formes, la contre-revue jugeait « bobine de ficelle solide » différente de
« bobine de ficelle » ; six appels.

**Invariant et fonctions.** Le noyau public désigne l'entité ; les qualificatifs restent
des assertions à contrôler. `noms.motif_designation`, `plages_designation` et
`hors_designations` reconnaissent le noyau, avec insertion après la tête nominale,
sans liste d'adjectifs. Le garde `narration._noms_voix_recit` et la
projection `noms.texte` protègent seulement ses mots : un nom privé intercalé reste
contrôlé. `noms.reperes_designations`, `mj._appeler` et `couverture_action.entree`
joignent référence, nom canonique, noyau/alias, forme écrite et faits publics aux
auditeurs. Le texte reste entier ; les candidats ambigus restent distincts.

**Preuves après recharge.** Sept tests nouveaux dans `tests/test_designations.py` :
voix d'Ilse toute proche et de Gorm basse et lointaine ; ficelle et vieux couteau pris,
référence, matière et rendu conservés ; « qu’on appelle » typographique ; identités
ajoutées, revendication niée, chanvre contraire au lin et couteau en cire refusés
avec `attendu`, dans la narration et la contre-revue simulées. Le garde est refait à
l'écriture. Segment exact avec réplique aussi rejoué : parole entendue et texte
sauvegardés, projection inchangée, aucun nom appris.
Tests ciblés et voisins : **88 tests finaux verts** (28,8 s).
Suite complète unique : **1 597 tests, 15 ignorés, verte, 560,1 s**, trois processus.
Le complément typographique final est couvert par les 88 tests ciblés.

**Luna, une passe par version.** `gpt-6-luna`, ChatGPT, effort `medium`, référence puis
**6fbdda2**, suite à priorité réduite en fond. Références absentes calculées une fois,
dans `artifacts/references/42bb9c0344f1c943f5b1d9ea40c012810380ee9a/designations/`.

| Script | Appels/tour, avant → après | Secondes/tour | Replis |
|---|---:|---:|---:|
| soir-noir | 3,40 → 3,60 | 11,0 → 12,3 | 0 → 0 |
| atelier | 3,45 → 3,09 | 12,8 → 10,9 | 0 → 0 |
| echanges | 3,20 → 5,50 | 10,4 → 24,0 | 0 → 0 |

**Textes relus.** Bobine prise en quatre appels, portée après recharge ; aucun refus nominal
dans le noir. Aucun arrêt ni recharge invalide. Restent le sifflement joyeux (huit appels)
et « je pousse Aubin » sans lien nominal (dix appels) ; l'identité d'Ilse inventée au
premier échange est refusée avant affichage. Les moyennes ne prouvent aucun gain de temps.
Fils, `mesures.json` et `relecture.txt` dans `artifacts/designations/` du worktree.

**Limites.** Complément canonique contigu, sans reconnaissance générale des paraphrases.
Matière et position restent des jugements sémantiques : les simulations prouvent leur
traitement lorsqu'ils sont corrects, sans les rendre déterministes. Complément
typographique final vérifié sans seconde passe Luna. La référence ne reproduit aucun
des deux faux refus rares ; une passe ne prouve pas leur disparition générale.
Le critère d'ambiance sans précaution reste ouvert.
