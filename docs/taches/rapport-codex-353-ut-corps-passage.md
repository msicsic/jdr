# Lot 353 — U-T corps et passage

Branche `codex-ut-corps-passage`, base `integration 57c9771d`, **terminée, non fusionnée**.
Production `cbc4744d` inchangée depuis la validation.

## Invariant et changement

Console et TUI reçoivent les mêmes gestes corporels et franchissements que le
menu web. Le raccord est entièrement dans `gestes_publics.py` : les formulaires
du catalogue commun sont dépliés en choix complets (méthode, moyen, direction),
avec les seules ressources publiques. Les réactions exigent un danger encore
perçu. Les franchissements utilisent directement `passages_publics`, y compris
l'ancrage d'une échelle au palier et l'arbitrage mémorisé d'un appui mobile.
Aucune forme, dimension, aptitude ou difficulté n'est ajoutée par le terminal.

Les nouvelles lignes suivent les anciennes, sans renuméroter leur préfixe.
Le numéro capture un `DescripteurPublic` exact, sans analyseur ni modèle.
Les boucles existantes de `jeu.py` et `donjon/tui.py` transmettent déjà ce choix
à U-D : elles restent inchangées, comme le moteur, le consentement et le MJ.
Les homonymes gardent leurs références et leurs rangs visibles.
Aucun recouvrement de code avec le lot 354 (`page.html` / `dialogues.py`).

## Vérification et mesures

**126 tests distincts validés / douze fichiers**, zéro échec, erreur ou saut
dans le bilan retenu : 124 résultats conservés de la passe initiale, puis les
deux seules méthodes corrigées rejouées, **2/2 vertes en 33,298 s** (imports compris).
Les 28 tests TUI et cinq tests TUI cases existants sont inchangés et verts.
Les empreintes et la comparaison AST prouvent que seuls ces deux corps de
méthode ont changé ; les assertions mécaniques et de recharge sont intactes.

Les parcours réels console et TUI couvrent les treize gestes dans deux scènes, les méthodes
et armes, les trois scènes réelles de force, les sept scènes sous obstacle,
les deux sens d'échelle, la perche portée/au sol, annulation, cible/moyen/forme
périmés et danger expiré. Descripteurs des callbacks Node, propositions de
commande, plans, textes exacts, monde, scène, fiche, carte et état public sont
comparés après recharge. Consentement et annulation sont exercés dans les deux
terminaux ; analyseur et appels au modèle sont interdits sur les choix directs.

**80 parcours mesurés**, quarante par interface : **2–11 touches** depuis la
liste, confirmation comprise ; **3–12 avec F7**. Cela inclut les refus publics.
Zéro appel modèle ; chiffres, Entrée et éventuel `tenter` puis Entrée comptés.

Passe initiale : 3 084,916 s, six échecs de sous-cas dans deux méthodes de
sonde. Le web exposait un même geste par plusieurs points de carte ; une
ancienne comparaison omettait les offres de passage dans sa projection.
La reprise compare les ensembles exacts et vérifie l'unicité terminale ;
elle transmet les passages publics, sans exclure leurs descripteurs.
Un flux web mixte contient aussi des commandes textuelles : la sonde ne
cherche le champ `geste` que dans ses descripteurs structurés.
Les essais rouges antérieurs (droits temporaires, cadrage de l'aperçu et
instant de mutation du témoin) restent archivés. Aucun correctif moteur.
Laptop, deux travailleurs réduits au plus ; ni Luna, banc PNJ ou suite complète.
Bruts : `C:/Users/msics/donjon/artifacts/ut-corps-passage-353/` : `tests.json`,
`reprise-tests-2.json`, `mesures.json`, synthèse `fin-cloture.json` écrite en dernier.

## Limites et livraison

Une offre ne promet aucune réussite. Le premier arbitrage d'un appui mobile
et une forme inconnue restent sur les voies existantes. Les choix sont à portée
de numéro dans la liste ; lecture, défilement et déplacement préalable ne sont
pas comptés. La liste peut être longue : un numéro fige chaque combinaison
complète, comme les offres terminales d'outils et de remise.

Branche poussée vers `origin`, aucun calcul actif. La fusion reste au superviseur.
La première `fin.json` rouge est conservée ; `fin-cloture.json` porte le bilan retenu.
