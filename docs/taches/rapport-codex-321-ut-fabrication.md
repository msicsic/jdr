# Lot 321 — U-T fabrication

Branche `codex-ut-fabrication`, base `integration 0fcc99e`, **non fusionnée**.

## Invariant et changement

Console et TUI composent la recette du formulaire web depuis le même catalogue :
usage, pièces par rôle, lien, outil, dimensions et rythme. `0` dans la liste des
gestes ouvre les recettes ; chaque numéro choisit une valeur de la projection
publique figée. Les dimensions sont saisies dans les bornes du catalogue.
Le dernier champ valide le choix ; cette conséquence est annoncée dans le
formulaire. `annuler` ferme sans effet, sans abandonner une proposition moteur
déjà en attente. Aucun choix intermédiaire ne fait avancer le monde.

`fabrication_terminal.py` porte la projection et le parcours commun, sans liste
de recettes, verbes, rôles ou capacités propre au terminal. Il lit
`catalogue_public()["fabrication"]` et `ressources_publiques(...,
decrire_physique=True)`, également employés par le web. Les noms et références
publiques distinguent les pièces ; les formes et dimensions connues sont
affichées, les descriptions manquantes signalées sans compléter leurs valeurs.
Le descripteur U-D est construit par les chemins des champs du catalogue ;
aucune analyse de texte, compilation libre ou consultation du MJ.

Le moteur conserve ses contrôles d'accès, d'aptitude et de propriété, à réception
des références exactes. Un choix devenu périmé ne recherche aucun substitut.
La TUI ne met rien dans la file du jeu pendant le formulaire, bloque les
déplacements et l'attente, et ferme la recette lors d'une nouvelle vue.
Les gestes numérotés précédents gardent leurs numéros.

## Vérification et mesures

**10 nouveaux tests verts**, zéro échec, erreur ou saut, 58,216 s. Les neuf
fichiers voisins, dont les **28 tests TUI existants inchangés**, restent en
cours : aucun bilan global revendiqué. Suivi détaché à priorité réduite,
`fin.json` écrit en dernier même en échec ; processus des tests déjà lancé,
sans relance. Ni Luna, ni banc PNJ, ni suite complète ; deux travailleurs
réduits au plus au total, sur copies.

Les quatre parcours du 305 sont refaits par les vraies saisies des deux
interfaces : échelles de perches normale et de planches soignée, ficelle et
barre découpées à un mètre. Les callbacks Node du vrai formulaire fournissent
les descripteurs témoins. Proposition de commande, plan, effets, texte exact,
monde, scène, fiche, carte et état web sont comparés après recharge. Les tests
couvrent aussi les pièces supprimées et éloignées après sélection, la physique
inconnue et les biens d'autrui pour les deux gestes, l'annulation et les
dimensions invalides. Le catalogue modifié et les références figées sont
contrôlés ; analyseur et appels du modèle sont interdits sur la voie choisie.
Les premiers essais non retenus restent archivés : positions et initialisation
des fixtures corrigées, comparaison après la vraie sauvegarde de fermeture.

Huit parcours mesurés : **23 touches par assemblage, 12 par découpe** depuis
la liste, ouverture `0` et Entrée comprises, chiffres des dimensions compris.
**24 et 13 avec F7** en TUI. Une commande composée évitée par parcours,
zéro appel modèle ; hors lecture, défilement et déplacement préalable.
Aucun délai humain ou réseau déduit de ces mesures.

## Limites et livraison

L'échelle reste le seul usage moteur modélisé. Les choix ne promettent ni
aptitude ni droits ; aucune qualification physique, aucun prélèvement de lot
ou rapprochement de matériaux automatique. La recette se ferme à la première
exécution ou annulation ; les paramètres se ressaisissent pour recommencer.

**Recouvrement avec le lot 319 : `jeu.py`**, autour de la boucle de saisie
console ; ni `executer_local`, ni `conclure`, ni `rendu.py` ne sont modifiés.
Web, MJ, règles d'atelier et moteur inchangés. Fusion au superviseur.
Bruts : `C:/Users/msics/donjon/artifacts/ut-fabrication-321/`.
Reprise : lire `fin.json`, puis les résultats détaillés et mettre ce rapport
et `docs/etat-dev.md` à jour avant de déclarer le lot terminé.
