# Lot 307 — U-T outils et destinations

Branche `codex-ut-outils`, base `integration d7302a4`, **non fusionnée**.
Reprise par fusion sans rebase d'`origin/integration 43440c6` (lot 305 inclus),
commit **`958a5cc`**, **validée** ; bilan initial conservé sans cumul.

## Invariant et changement

Console et TUI proposent les mêmes couples geste–ressource que les menus
de carte et de besace : déverrouiller, crocheter, forcer/frapper, alimenter
et mettre dans. Un numéro choisit un descripteur U-D complet, avec l'outil
ou la destination sous sa référence publique exacte. Les homonymes restent
distinguables. Le moteur revalide le choix à réception ; aucun substitut,
aucune capacité ni propriété inconnue n'est déduite par l'interface.

`gestes_publics.gestes_materiels` lit les formulaires du catalogue commun,
leurs conditions publiques et leurs filtres de ressources. `liste_gestes`
ajoute les choix complets après les gestes simples, avec dédoublonnage des
portes apparaissant sur plusieurs sorties. `gestes_du_monde` dessert déjà
`jeu.py` et `tui.py` : aucun second chemin de sélection n'est nécessaire.
Les premiers gestes gardent leurs numéros dans une même projection.

La projection `ressources_publiques` quitte `web/pont.py` pour
`inventaire_public.py` ; le pont la réexporte. Web et terminaux lisent
ainsi les mêmes affaires portées et objets vus à portée, sans contenu
fermé ni inventaire privé d'un PNJ. La reprise conserve la projection
enrichie du 305 : `decrire_physique`, frontière `ressource_connue` et
description manquante sans valeur inventée. Formulaires du catalogue et
entrée SSE de fabrication conservés ; conflits pont/état résolus.
L'AST des fonctions du 305 est identique (imports relatifs adaptés pour
la projection déplacée), page et sonde Node identiques à `43440c6`.
Aucun changement propre au lot du MJ, des règles d'atelier ou des PNJ.

## Vérification et mesures

**Reprise : 105 tests distincts / dix fichiers verts**, aucun échec,
erreur ou test ignoré, **621,557 s**, deux travailleurs réduits au plus.
Les neuf fichiers précédents sont relancés, plus les sept tests de
`test_fabrication_publique.py` ; **28 TUI existants inchangés** et cinq
tests de cases verts. Syntaxe `tests/clic_page.js` verte, callbacks réels
exécutés. `tests-reprise-integration.json` et `fin-reprise-integration.json` :
**ok=true, code 0**, code testé `958a5cc`, inchangé depuis validation.
Les tests utilisent les vrais callbacks Node de la page,
les vrais numéros console et les touches de la TUI, avec analyseur et
appels du MJ interdits. Descripteur, plan et texte public exact, monde,
scène, fiche, carte et état web sont comparés après sauvegarde/recharge.

Deux scènes par geste : contenant/porte, foyer/lampe et destinations au
sol/portées, avec deux ressources homonymes. Ressource partie, destination
fermée, mauvais outil, propriété inconnue, numéro inconnu ou ambigu,
besace dans le noir et sans carte sont aussi exercés. Les filtres de
ressources et libellés du catalogue sont modifiés en test pour prouver
leur lecture effective par les deux interfaces.

`mesures-reprise-integration.json` : **20 parcours**, dix par interface ; **3 touches** pour
déverrouiller, crocheter, frapper et alimenter, **4 pour mettre dans**
(numéros à trois chiffres), depuis la liste jusqu'à l'effet. **4 à 5 avec
F7 en TUI**. Hors déplacement préalable et temps de lecture de la liste ;
zéro appel modèle, aucun délai humain ou réseau déduit.

## Limites et livraison

La liste énumère les couples complets ; sa longueur croît avec le nombre
de cibles et de ressources publiques. Elle ne promet pas la réussite.
Comme au lot 300, aucune capacité maximale des destinations n'existe dans
le moteur ; ce lot ne garantit donc pas le refus d'une destination pleine.
Les propriétés inconnues gardent leur voie d'admission distincte.

Les premiers essais de sauvegarde dans le bac à sable Windows ont été
refusés par les droits des dossiers temporaires ; les vérifications
retenues ont tourné hors de ce bac, sur copies, avec deux travailleurs
au plus, à priorité réduite. Ni Luna, ni banc PNJ, ni suite complète.
Bruts : `C:/Users/msics/donjon/artifacts/ut-outils-307/`.
Bilan initial : code/tests `79c9b89`, clôture `81c0d5e` poussée ;
98 tests verts en deux étapes, `bilan.json` et `fin-cloture.json` conservés.
Les trois échecs d'intégration signalés concernant les références opaques
et coordonnées restent hors périmètre, comme demandé ; aucun correctif
ni oracle affaibli. Branche poussée vers `origin/codex-ut-outils`, aucun
calcul actif ni relancé à la clôture. `fin-cloture-reprise-integration.json`
écrite en dernier ; intégration du lot et suite complète au superviseur.
