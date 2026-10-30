# Lot 344 — U-M corps

Branche `codex-um-corps`, base initiale `78766d9`, **terminée, non fusionnée**.
Intégration exacte `014fc35` fusionnée sans rebase par **`b2c8f53`**, à deux
parents (`85e39a8`, `014fc35`).

## Invariant et changement

Le catalogue `gestes_publics.formulaires_corps` pilote treize gestes sur
une personne perçue, avec méthode simple/assommer, moyen connu et direction
explicite. Il ne décide pas de leur aptitude. Les homonymes gardent leurs
références exactes ; la surprise reste calculée par le moteur.
`commandes.proposition_descripteur` produit la même proposition que la
commande locale. Les réactions apparaissent seulement sur les auteurs de
`defense.dangers_vus` encore perçus, sans approche vers l'agresseur.

Le raccord de `moteur.py` réutilise la gravité U-C et la fiche « Compris ».
Le descripteur conservé jusqu'à confirmation est refusé si sa référence,
l'état ou le plan changent, même sans nouvelle révision ; annuler ne
publie aucun effet. Sauvegarde et résultat empruntent la boucle existante.
Le lot ne modifie ni MJ, `jeu.py`, `tui.py`, ni règles de corps/violence.

## Fusion et vérification

Le conflit de `commandes.py` conserve direction corporelle et parcours
structuré G7 ; leur mélange est refusé. Les auto-fusions de `moteur.py`,
`web/page.html` et `tests/clic_page.js` conservent les deux intentions.
Mandats 341, provenance 346, conception 347 et correctif « Compris » sont
présents. `etat-dev.md` reprend l'intégration courte avec huit lignes du lot.

**180 tests distincts / 20 fichiers : 179 verts, une erreur antérieure,
zéro échec et zéro saut**. Les treize nouveaux tests sont verts : 30 paires
clic/commande au Relais et à l'auberge, scènes réelles frapper/assommer/fuir
et ligature 4d, homonymes, références périmées, annulation et confidentialité.
Plans, effets, textes, monde/scène/fiche/carte comparés après recharge ;
sauvegarde avant affichage et zéro appel au modèle sur les parcours.
Mandats **12/12**, repli/appel **10/10**, consentement **9/9**, compréhension
**5/5**, web/Node et déplacements G7 verts.

Première passe de fusion : **179 tests, 14 échecs de sous-cas, une erreur,
1 370,972 s**. Référence **014fc35 exacte : 28 tests, mêmes 15 incidents,
75,045 s** ; mêmes piles hors chemins/numéros de ligne, tests identiques.
Les 14 attentes G4 ignoraient « Compris » après le résultat confirmé.
L'auxiliaire attend maintenant résultat exact + plan admis et contrôle le
champ sauvegardé ; assertions mécaniques, recharge, affichage et absence
d'appel après confirmation conservées. **Reprise : 19/19 tests, trois
fichiers, 77,032 s**. Résultats des 17 autres fichiers conservés après
contrôle des empreintes ; production inchangée depuis `b2c8f53`.

Réserve inchangée : `test_tenir.test_joueur_tenu_ne_peut_pas_marcher_et_se_degage`
épuise deux jets simulés pendant une persuasion PNJ (`StopIteration`),
également sur 014fc35. Aucun nouvel incident dans la sélection.

**14 parcours mesurés : 14 saisies évitées, 3–5 clics confirmation comprise**,
cible à portée ; approche éventuelle en sus. Mesure initiale conservée.

## Limites et livraison

Une offre ne garantit pas sa réussite. L'inconscience est jugée par les
règles existantes ; si elle survient après l'aperçu, elle invalide le
consentement. U-T corps reste à faire. Ni Luna, suite complète ou banc PNJ ;
deux travailleurs réduits au plus, aucun calcul actif.

Bruts : `C:/Users/msics/donjon/artifacts/um-corps-344/fusion-014fc35/` :
`tests.json`, `reference-tests.json`, `reprise-g4.json`, `analyse-cloture.json`,
`fin-cloture.json`. Les fins rouges initiales restent intactes. La livraison
initiale (123/124, réserve prouvée sur 78766d9), les premières prémisses
corporelles corrigées avec assertions intactes et les incidents de droits
temporaires restent archivés dans le dossier parent.
