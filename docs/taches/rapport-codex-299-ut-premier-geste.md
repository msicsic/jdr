# Lot 299 — U-T : premier geste au terminal

Branche `codex-ut-premier-geste`, base intégration `83a2e89`, **non fusionnée**.

## Invariant et changement

Le numéro choisi en console ou en TUI désigne le descripteur public U-D
de la liste effectivement affichée, sans résolution de nom, analyse de texte,
compilation ni modèle. Le moteur conserve ses contrôles à réception ; une
référence périmée ne se reporte jamais sur un homonyme.

`donjon/gestes_publics.py` porte le catalogue des objets et portes, les offres
sur les seuls champs de `scene_percue`, la liste figée, son rendu et le choix
exact du numéro. La référence publique et les coordonnées de carte distinguent
les homonymes. Souvenirs, inventaires et données privées ne servent pas de
cibles. Numéro inconnu ou plusieurs numéros : refus local, sans effet.

`jeu.py` affiche la liste avant chaque invite de console en mode cases ;
`PontTerminal` transmet sa projection à un onglet **Gestes (F7)**. Les chiffres
puis Entrée envoient le descripteur à `executer_local`, partagé avec le web.
La saisie libre suit son parcours habituel.

Le serveur applique `adapter_page` au HTML servi : les deux fonctions de menu
utilisent le catalogue commun sérialisé en JavaScript. `page.html` reste
inchangé pour le chantier U-M concurrent ; les tests Node exécutent le HTML
adapté, comme le serveur. Aucun fichier du MJ ni mécanique PNJ modifié.

## Vérification et mesures

**59 tests distincts, cinq fichiers**, zéro échec, erreur ou ignoré ; deux
travailleurs au plus, priorité réduite. Les **28 tests TUI existants sont
inchangés et verts**. Bilan retenu : `tests-cibles.json` pour TUI/U-D,
`tests-cloture.json` pour terminal/web, `tests-perimes.json` pour la matrice
des refus ; assemblage sans rejeu dans `fin-cloture.json`.

Les quatorze couples famille/geste passent par les saisies réelles console et
TUI : second homonyme, descripteur exact, même plan/journal, même texte,
monde, scène et carte après recharge que le parcours U-D. Pour chacun,
numéro inconnu, numéros multiples et cible devenue hors de vue à réception
restent sans effet ni modèle. Deux suppressions réelles (`prendre`, `lire`),
ouverture/fermeture à portée, référence de personnage inconnu et sorties
mémorisées complètent ces preuves. Node exécute les callbacks du HTML servi,
y compris les objets muraux que la sonde omettait auparavant.

**Touches mesurées sur les quatorze choix : 3** (deux chiffres et Entrée),
contre **17 à 27** pour la commande explicite avec la même référence publique.
En TUI, **4 avec F7** pour ouvrir la liste. C'est le coût de soumission du
geste, jusqu'au résultat ou au refus, hors déplacement préalable ; aucune
mesure de délai humain ou réseau. **Zéro appel modèle** et analyseur interdit
dans les parcours numérotés.

Les essais préliminaires sont archivés mais exclus du bilan : instrumentation
des appels récursifs corrigée, puis sonde des murs complétée. Bruts et mesures :
`C:/Users/msics/donjon/artifacts/ut-299/`. Aucun calcul actif à la clôture.

## Portée et limites

Ce lot couvre les neuf gestes d'objet et cinq gestes de porte du menu de carte
existant. « Lui parler » reste une saisie libre dans le web ; aucun formulaire
social, d'inventaire, d'outil ou de corps ajouté au terminal. La liste est une
offre de geste : portée, droits, outillage et faisabilité restent vérifiés par
le moteur. L'approche automatique du clic reste propre à la carte web ; le
terminal conserve ses déplacements directs et peut recevoir un refus de portée.

La numérotation est renouvelée à chaque nouvelle vue, sans conserver un numéro
comme identité durable. L'identité conservée jusqu'à l'exécution est celle du
descripteur capturé dans cette vue. L'adaptateur de page redéfinit les fonctions
de menu à la fin du script ; une extension de ces fonctions par U-M devra passer
par le catalogue commun. Le fichier HTML ouvert seul hors serveur conserve son
ancien catalogue. Pas de Luna, de banc PNJ ni de suite complète : parcours
d'interface seulement. Fusion et vérification d'intégration laissées au superviseur.
