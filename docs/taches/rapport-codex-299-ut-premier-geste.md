# Lot 299 — U-T : premier geste au terminal

Branche `codex-ut-premier-geste`, **non fusionnée**. Base initiale `83a2e89` ;
reprise après `f758eee` : fusion **sans rebase** d'`origin/integration`
`2d893e0`, qui contient le lot 298 (U-M inventaire).

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

**Reprise : réécriture du HTML supprimée.** `catalogue_public()` fournit des
données JSON copiées ; `PontWeb` les joint à l'état public sous
`catalogue_gestes`, sérialisé par le flux habituel du serveur. Dans le fichier
`page.html`, `gestes` et `gestesPorte` lisent directement ce catalogue commun.
Les réponses `/` et `/index.html` servent les **octets exacts du fichier**.
Aucune génération de JavaScript ni transformation du HTML. Les boutons de
besace, quantités et destinataires du 298 sont conservés. Le conflit de sonde
Node conserve ses callbacks d'inventaire et les clics sur objets muraux.

## Vérification et mesures

**95 tests / huit fichiers**, zéro échec, erreur ou ignoré, deux travailleurs
au plus à priorité réduite. Rejoués seulement : terminal, matrice de refus,
les **28 TUI existants inchangés**, web/Node, U-D, inventaire 298, diagonales
de la sonde et matière prélevée. Bruts de reprise :
`C:/Users/msics/donjon/artifacts/ut-299/tests-reprise-integration.json` ;
bilan `fin-reprise-integration.json`.

Les quatorze couples famille/geste passent par les saisies réelles console et
TUI : second homonyme, descripteur exact, même plan/journal, même texte,
monde, scène et carte après recharge que le parcours U-D. Pour chacun,
numéro inconnu, numéros multiples et cible devenue hors de vue à réception
restent sans effet ni modèle. Deux suppressions réelles (`prendre`, `lire`),
ouverture/fermeture à portée, référence de personnage inconnu et sorties
mémorisées complètent ces preuves. HTTP contrôle les octets du HTML et le
catalogue reçu par SSE ; Node exécute les callbacks du fichier, y compris
les objets muraux. Inventaire 298 : biens et destinataires homonymes, lots,
portions, sources, choix périmés, noir et contenus cachés.

**Touches mesurées sur les quatorze choix : 3** (deux chiffres et Entrée),
contre **17 à 27** pour la commande explicite avec la même référence publique.
En TUI, **4 avec F7** pour ouvrir la liste. C'est le coût de soumission du
geste, jusqu'au résultat ou au refus, hors déplacement préalable ; aucune
mesure de délai humain ou réseau. **Zéro appel modèle** et analyseur interdit
dans les parcours numérotés.

Première livraison : 59 tests verts, résultats et essais préliminaires
archivés sans les compter à nouveau. Aucun calcul actif à la clôture.

## Portée et limites

Ce lot couvre les neuf gestes d'objet et cinq gestes de porte du menu de carte
existant. « Lui parler » reste une saisie libre dans le web ; aucun formulaire
social, d'inventaire, d'outil ou de corps ajouté au terminal. La liste est une
offre de geste : portée, droits, outillage et faisabilité restent vérifiés par
le moteur. L'approche automatique du clic reste propre à la carte web ; le
terminal conserve ses déplacements directs et peut recevoir un refus de portée.

La numérotation est renouvelée à chaque nouvelle vue, sans conserver un numéro
comme identité durable. L'identité conservée jusqu'à l'exécution est celle du
descripteur capturé dans cette vue. Le catalogue vient du flux du jeu,
sans catalogue concurrent dans la page. Aucun changement du MJ ni des
mécaniques PNJ. Pas de Luna, de banc PNJ ni de suite complète : parcours
d'interface seulement. Fusion sur l'intégration laissée au superviseur.
