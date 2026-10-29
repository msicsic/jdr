# Lot 292 — G4 : résultat public du moteur

2026-10-29. Branche `codex-g4-resultat-public`, base `9e52df4`.
**Lot terminé, non fusionné ; tous les tests retenus sont verts.**

`jeu.conclure` mémorise et sauvegarde le rendu moteur avant affichage,
sans récit ni audit après exécution ; même boucle console/TUI/web.
Propositions, contre-revues, confirmations et petits pas silencieux restent.
Le rendu complète les blessures visibles et les dépôts au sol.
`raconter`, `demande_initiale`, `--recit-moteur` sont retirés ;
`MJ.raconter_resultat` reste pour les outils/comparateur, sans appel par le jeu.
Les valeurs de dé restent masquées comme avant, l’issue est complète et le
journal conserve le calcul ; le test TUI original est inchangé et vert.

**Défenses perçues, correction finale.** Garder le test de prise rouge était
une mauvaise clôture : le manque de rendu était bien dans G4. La prise
réussit, puis Brune se dégage légitimement pendant le geste du joueur.
`defense._rendre_issue` écrit maintenant les issues communes de dégagement
(réussi ou manqué), reddition et fuite dans le fil des événements, au moment
de leur exécution. La perception est contrôlée à cet instant : une défense
non vue n’ajoute aucune phrase visuelle ; la voie des paroles effectivement
entendues reste inchangée. Coups et interpositions gardent leurs rendus moteur.
Aucun choix, jet, déplacement, durée ni effet de défense n’est modifié.
Pas de règle propre à un personnage, une formulation ou un scénario.

**Vérifications.** La console avec MJ simulé vérifie la prise puis le
dégagement perçu, dans cet ordre, et l’état sauvegardé non tenu : Brune et
Gorm ; autre issue sur Aubin, dégagement manqué et prise conservée. L’ancienne
assertion de prise forcément persistante est remplacée par ces conséquences
réelles, sans supprimer la vérification de monde. **Neuf scènes** couvrent
les trois défenses communes vues, dos tourné et dans le noir. Chaque scène
contrôle texte sauvegardé avant affichage, état complet, scène, fiche et
carte rechargés, avec zéro appel après exécution.

Dernière reprise : **29 tests / trois fichiers**, **0 échec, erreur ou ignoré**,
**125,374 s**, un travailleur réduit (`test_recit_resultat`,
`test_defenses_publiques`, `test_defense`). Bilan retenu des vérifications
successives : **384 tests / 27 fichiers, tous verts**. La TUI originale
avait été rejouée verte (28/28). Les dix comparaisons déterministes au moteur
exact de la base conservaient les états/vues rechargés (textes du journal
exclus). Ni suite complète ni banc PNJ supplémentaire ; **aucune repasse Luna**.

**Mesures Luna conservées.** Une passe de trois scripts sur copies,
`integ=9e52df4` → `lot=.` sur `d1e50c4`, référence absente jouée puis rangée
une fois. Trois exécutions conformes : Gorm assommé et blessé de 1 PV,
Brune ligotée, torche déposée aux pieds du joueur ; pour chacune,
**1 récit + 1 audit après exécution → zéro**. Aucun incident.
Les plans admis avaient aussi été rejoués sans modèle après correction
d’affichage des dés. Les défenses sont vérifiées par les tests ciblés ci-dessus.

Global : **12 → 7 appels**, **28,65 → 22,20 s** ; sur les mêmes huit saisies
hors quitter : **1,50 → 0,875 appel/saisie**, **3,58 → 2,78 s**. Le résumé par
tour avec appels change de dénominateur (cinq → trois) : 2,40 → 2,33 appels,
5,73 → 7,40 s. Régression observée avant ligature : `impossible` corrigé
dans la même saisie, refus **0 → 1**, compilation/revue **2 → 3 appels**,
**6,35 → 8,99 s** ; replis et relances narratives **0 → 0**. Pas de gain
causal de durée déduit d’une seule passe.

Bruts, six parties/fils, états/vues, attribution, reprises et manifeste :
`C:/Users/msics/donjon/artifacts/g4-292/`. Les échecs historiques sont gardés ;
`fin-defenses.json` et `fin-cloture.json` donnent le bilan final vert.
Aucun calcul actif du lot.
