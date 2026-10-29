# Lot 300 — U-M outils et destinations

Branche `codex-um-outils`, base intégration `2d893e0`, **non fusionnée**.

## Invariant et changement

Le clic choisit explicitement un outil, une clé, un combustible ou une
destination parmi les ressources connues, sous sa référence publique exacte.
`pont.ressources_publiques` projette seulement nom, référence et type, plus
le caractère de foyer déjà vu : affaires directement portées, objets vus à
portée, contenus ouverts vus. Ni bien d'un PNJ, ni contenu fermé, ni capacité
ou précondition transmis. Les outils de même nom reçoivent un numéro de choix.

Les menus de la carte et de la besace offrent déverrouiller, crocheter,
forcer/frapper un objet, alimenter et mettre dans. Une serrure cartographiée
peut être ciblée directement. Le choix ne garantit aucune aptitude ; un outil posé peut
être proposé puis refusé parce que le geste exige de le tenir en main.
`DescripteurPublic` admet `frapper`, `alimenter`, `mettre` et `destination`.
Les références sont revalidées à réception sans recherche de nom ou substitut.
Les affaires portées restent connues dans le noir ; corps et personnes sont
hors de ces nouveaux gestes.

`geste_local` construit les mêmes propositions pour le texte et le clic.
L'opération moteur de dépôt existait, mais aucune commande locale « mettre
dans » : elle est ajoutée comme entrée vers `deplacer`. Alimenter partage
aussi ce constructeur. Un dépôt de combustible dans une source conserve
la conversion moteur existante vers alimenter. Aucun changement du MJ,
de `jeu.py`, de `tui.py` ou des mécaniques PNJ.

## Vérification et mesures

Bilan retenu : **69 tests distincts / six fichiers verts**, zéro échec,
erreur ou ignoré, 241,451 s cumulées pour les résultats retenus. Première
passe groupée : 65 tests en 146,024 s ; après
les parcours supplémentaires, neuf tests outils verts en 90,855 s et les
neuf tests web verts. Deux travailleurs réduits au plus. Interpréteur du dépôt principal,
la `.venv` étant absente de ce worktree. Callbacks Node réels puis boucle de
jeu avec analyseur interdit pour les clics et MJ interdit d'appel ; mêmes
plans, effets, texte public et monde/scène/fiche/carte après recharge.

Cas : coffre et porte, deux outils homonymes, deux destinations homonymes,
foyer au bois et lampe à huile, ressource partie/supprimée/éloignée, mauvais
outil, contenant fermé, besace dans le noir, propriété de coupe inconnue
laissée à l'admission distincte. Les échecs initiaux venaient de trois fixtures
incorrectes (contenant fermé, foyer utilisé comme contenant, serrure sans
projection cartographique), corrigées sans changement moteur. Un lancement sous bac à sable
ne pouvait pas écrire ses fichiers temporaires ; les passes avec accès disque
et leurs résultats sont conservées.

`mesures.json` : **10 parcours, 10 saisies évitées, 3 clics** jusqu'à l'effet
avec cible déjà à portée (cible, geste, ressource). Marche éventuelle en sus.
Zéro appel modèle sur les parcours exécutés ; aucun gain de délai réseau
déduit. Ni Luna, ni banc PNJ, ni suite complète : entrée d'interface seule.

## Limites et livraison

**Le cas « destination pleine » n'est pas garanti** : le moteur ne définit
aucune capacité maximale des contenants/réservoirs. Il contrôle fermeture,
accès et charge de portage ; aucune règle de remplissage n'est ajoutée par
ce lot. Les menus n'inventent ni propriété ni combustible compatible.

Bruts et sonde : `C:/Users/msics/donjon/artifacts/um-outils-300/`.
Bilan retenu : `fin-cloture.json`, avec les résultats sources par fichier.
Branche livrée sur `origin/codex-um-outils`. Fusion et suite complète laissées
au superviseur ; aucun calcul actif, aucun calcul long lancé.
