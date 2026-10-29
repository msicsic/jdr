# Lot 300 — U-M outils et destinations

Branche `codex-um-outils`, base `2d893e0`, **non fusionnée**. Reprise par
fusion sans rebase d'`origin/integration` figé à `f1cb8fd` (U-T 299 inclus).

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

Après la fusion de 299, `gestes_publics.OBJETS` et `PORTES` portent aussi les
offres paramétrées : libellé, conditions publiques, champ outil/destination
et sélection publique des ressources. Le catalogue est transmis par SSE ;
`page.html` le lit pour les gestes de carte et leurs sous-menus, sans liste
de verbes parallèle. Le terminal premier geste conserve les entrées simples ;
les formulaires ne deviennent jamais des descripteurs incomplets. Le choix
des ressources au terminal reste le futur lot U-T outils.

`geste_local` construit les mêmes propositions pour le texte et le clic.
L'opération moteur de dépôt existait, mais aucune commande locale « mettre
dans » : elle est ajoutée comme entrée vers `deplacer`. Alimenter partage
aussi ce constructeur. Un dépôt de combustible dans une source conserve
la conversion moteur existante vers alimenter. Aucun changement du MJ,
de `jeu.py`, de `tui.py` ou des mécaniques PNJ.

## Vérification et mesures

Bilan de reprise : **90 tests / huit fichiers verts**, zéro échec, erreur
ou ignoré. Outils, inventaire 298, terminal 299 et cibles périmées, TUI,
web/Node, descripteur : 77 tests en 299,178 s ; diagonales de la sonde Node :
13 tests en 1,036 s. Les **28 TUI existants sont inchangés**. Deux travailleurs
réduits au plus. Interpréteur du dépôt principal, `.venv` absente du worktree.
Callbacks Node réels puis boucle de
jeu avec analyseur interdit pour les clics et MJ interdit d'appel ; mêmes
plans, effets, texte public et monde/scène/fiche/carte après recharge.

Cas : coffre et porte, deux outils homonymes, deux destinations homonymes,
foyer au bois et lampe à huile, ressource partie/supprimée/éloignée, mauvais
outil, contenant fermé, besace dans le noir, propriété de coupe inconnue
laissée à l'admission distincte. Les résultats antérieurs (69 tests) et
les essais préliminaires restent dans les bruts, sans être recomptés.

La reprise compare les offres paramétrées Python aux callbacks de la carte
sur les cinq gestes et leurs deux scènes. Retirer les formulaires des données
SSE retire les sous-menus ; modifier leur libellé ou leur sélection de
ressources change effectivement la page. Les premiers gestes terminal et
leurs descripteurs restent inchangés, y compris leurs refus sans outil.

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
Bilan initial : `fin-cloture.json` ; reprise : `fin-reprise-integration.json`.
Branche livrée sur `origin/codex-um-outils`. Fusion et suite complète laissées
au superviseur ; aucun calcul actif, aucun calcul long lancé.
