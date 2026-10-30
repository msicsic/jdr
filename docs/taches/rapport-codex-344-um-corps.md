# Lot 344 — U-M corps

Branche `codex-um-corps`, base `origin/integration 78766d9`, **terminée,
non fusionnée**. Code et tests : `91cd96d`, `b34315e`.

## Invariant et changement

Le catalogue `gestes_publics.formulaires_corps` pilote treize gestes sur
une personne perçue : méthode simple/assommer, moyen connu, direction
explicite. Il ne décide pas de leur aptitude. Les homonymes gardent leurs
références exactes ; la surprise reste calculée par le moteur.
`commandes.proposition_descripteur` revalide les références et construit
la même proposition que la commande locale. Assommer, riposter, se rendre
à et fuir disposent de commandes explicites. Les réactions apparaissent
seulement sur les auteurs de `defense.dangers_vus` encore perçus, sans
approche automatique vers l'agresseur.

Le raccord limité dans `moteur.py`, nécessaire en plus des fichiers prévus,
réutilise la gravité U-C et la fiche « Compris ». Le descripteur est conservé
jusqu'à confirmation : référence perdue ou état/plan changé imposent un
nouveau choix et aperçu, même sans nouvelle révision. Annuler ne publie
aucun effet. Sauvegarde et résultat empruntent la boucle existante. MJ,
`jeu.py`, `tui.py`, `force.py`, `combat.py` et `tenir.py` sont inchangés.

## Vérification et mesures

**124 tests distincts / 13 fichiers : 123 verts, une erreur antérieure,
zéro échec et zéro saut**, 2 417,830 s cumulées des deux lancements ; aucun
bilan de performance. **Les 13 nouveaux tests sont verts** : 30 paires
clic/commande au Relais et à l'auberge, personnes/moyens homonymes,
annulation, refus périmés, référence opaque après présentation, danger
disparu et données cachées. Plans, effets, textes, monde/scène/fiche/carte
comparés après recharge ; sauvegarde avant affichage, analyseur interdit
au clic, zéro appel au modèle sur les parcours exécutés. Callbacks Node
verts. Scripts réels frapper/assommer/fuir et ligature 4d couverts.

Réserve : `test_tenir.test_joueur_tenu_ne_peut_pas_marcher_et_se_degage`
épuise ses deux jets simulés dans la persuasion d'une rumeur entre PNJ.
**Reproduit sur 78766d9 exact : 10 tests, même erreur, 8,906 s** ; test
inchangé, mêmes fonctions de pile et exception `StopIteration`. Aucun
nouvel incident dans la sélection. Sources/tests conformes aux empreintes
finales ; aucun calcul actif.

**14 parcours mesurés : 14 saisies évitées, 3 à 5 clics jusqu'à l'effet,
confirmation comprise**, cible à portée : frappes 5, moyen/direction 4,
sans paramètre 3. Approche éventuelle en sus.

## Limites et intégration

Moyen inadéquat ou préalable manquant : refus moteur. L'inconscience
n'interdit pas tout geste : frapper une personne sans défense reste
autorisé ; survenant après l'aperçu, elle invalide le consentement.
Les gestes propres à Corvus gardent leur cible moteur propre, la personne
du menu servant de contexte perçu. U-T corps reste à faire. Ni Luna,
suite complète ou banc PNJ.

Recouvrement **343/G7 : `moteur.py`**, dont le rendu devra être conservé à
la fusion ; documentation commune avec 338/341/342. Bruts :
`C:/Users/msics/donjon/artifacts/um-corps-344/`, bilans, mesures,
`analyse-cloture.json`, `reference-78766d9.json`, `fin-cloture.json`.
`fin-validation.json ok=false` intact. Première passe corporelle rouge
conservée (27 échecs de sous-cas, 5 erreurs, 519,474 s) : prémisses
références/placement/contact/mains/date corrigées, assertions intactes,
fichiers nouveaux entièrement rejoués. Incidents de droits temporaires
du bac à sable conservés dans le point de reprise.
