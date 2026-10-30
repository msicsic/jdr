# Lot 353 — U-T corps et passage

Branche `codex-ut-corps-passage`, base `integration 57c9771d`, **validation en cours, non fusionnée**.

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

Premiers contrôles : projection corporelle complète dans deux scènes conforme
aux vrais callbacks Node ; frappe avec consentement exécutée et rechargée en
console et TUI, avec descripteur, plan, état et vues identiques au web.
Annulation et référence devenue périmée validées en console.

La sélection complète est **lancée en fond**, sur le laptop, deux travailleurs
au plus à priorité réduite. Elle comprend les nouveaux parcours terminal,
les tests des menus corps et passage, les choix terminaux précédents et les
tests TUI existants inchangés. Ni Luna, banc PNJ ou suite complète.
Les parcours couvrent les treize gestes dans les deux scènes, les méthodes
et armes, les trois scènes réelles de force, les sept scènes sous obstacle,
les deux sens d'échelle, la perche portée/au sol, annulation, cible/moyen/forme
périmés et danger expiré. Comparaison du monde, de la scène, de la fiche, de
la carte et de l'état public après recharge. Analyseur et modèle interdits.

Les touches mesurées incluent les chiffres du numéro, Entrée et, si nécessaire,
`tenter` puis Entrée ; F7 ajoute une touche en TUI. Les mesures détaillées et
le bilan final seront lus dans `mesures.json`, `tests.json` et `fin.json`.
Bruts : `C:/Users/msics/donjon/artifacts/ut-corps-passage-353/`.
Les essais rouges sont conservés : droits temporaires Windows, cadrage de
l'aperçu affiché, puis mutation de la référence avant la vue initiale du témoin
au lieu de la réception du choix. Les assertions d'état sont conservées ; le
témoin reçoit maintenant la mutation au même instant que le terminal.

## Limites et reprise

Une offre ne promet aucune réussite. Le premier arbitrage d'un appui mobile
et une forme inconnue restent sur les voies existantes. Les choix sont à portée
de numéro dans la liste ; lecture, défilement et déplacement préalable ne sont
pas comptés. La liste peut être longue : un numéro fige chaque combinaison
complète, comme les offres terminales d'outils et de remise.

**Ne pas déclarer le lot validé avant lecture de `fin.json`.** À la reprise,
examiner ses incidents éventuels et les mesures, mettre à jour ce rapport et
`etat-dev.md`, puis pousser la livraison finale. La fusion reste au superviseur.
