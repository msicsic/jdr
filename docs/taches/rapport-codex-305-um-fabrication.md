# Lot 305 — U-M fabrication

Branche `codex-um-fabrication`, base intégration `37f68d4`, **non fusionnée**.
Reprise par fusion sans rebase d'`origin/integration` figé à `01a95e0`
(U-T inventaire 301 inclus).

## Invariant et changement

Le formulaire transmet les ressources choisies sous leurs références publiques,
avec les rôles, dimensions souhaitées et rythme. Le moteur décide de la
faisabilité, des droits, des consommations et du résultat. Aucune analyse du
clic ni aucun appel au modèle ; aucune propriété physique inventée.

`gestes_publics.formulaires_fabrication` tire les usages, rôles, nombres de
pièces et bornes des schémas existants d'`artisanat`. Le catalogue commun
alimente la page par SSE. Le bouton « Assembler / découper… » ouvre un
formulaire sans ressource ni dimension présélectionnée. Les homonymes sont
distingués par référence. Le choix affiche la forme et les mesures établies,
ou signale la description physique manquante, à établir séparément.

`ressource_connue` fournit la même frontière à la projection et à la réception :
affaires directement portées ou objets actuellement perçus à portée, sans
inventaire de PNJ ni contenu fermé. Les candidats ne sont filtrés ni par
aptitude ni par propriété ; le moteur conserve ses refus, notamment pour un
outil posé, une mauvaise pièce, un lot non prélevé ou un bien d'autrui.
Une référence périmée est refusée sans recherche de nom ni substitut.

Le descripteur U-D admet les paramètres publics d'`assembler` et `decouper`.
`fabrication_locale` construit aussi les commandes explicites correspondantes
(syntaxe dans l'aide locale). La difficulté normale reprend la convention 12
de la fabrication existante ; le rythme soigné reprend 0 et ses contrôles.
Le joueur ne choisit pas une difficulté. Les règles de l'atelier, le MJ,
`jeu.py` et `tui.py` ne sont pas modifiés par le lot.

À la reprise, le pont réexporte `inventaire_public` et `destinataires_publics`
depuis `donjon/inventaire_public.py`, la projection commune du 301. Les copies
locales sont retirées ; la projection des ressources de fabrication reste
intacte. Le catalogue conserve les gestes de besace du 301 et les formulaires
du 305. `jeu.py`, `tui.py`, la projection commune et les tests du 301 sont
identiques à `01a95e0`. Seul conflit de code : `web/pont.py` ; les entrées
d'état des lots 305, 301 et 302 sont conservées ensemble.

## Vérification et mesures

**Reprise : 133 tests / onze fichiers verts, 573,705 s**, zéro échec, erreur
ou ignoré. Les neuf fichiers du 305 sont tous relancés : fabrication,
assemblage, artisanat, matière, descripteur U-D, outils, inventaire web,
web/Node et premiers gestes terminal. S'y ajoutent les dix tests d'inventaire
terminal 301 et les **28 tests TUI existants inchangés**. La vérification
syntaxique Node de `tests/clic_page.js` passe ; les callbacks réels sont exécutés.
Identité des deux fonctions réexportées avec le module commun contrôlée.
Deux travailleurs au plus, priorité réduite, interpréteur du dépôt principal
(`.venv` absente du worktree). Aucun rejeu de référence, ni Luna, ni suite
complète. Bruts : `tests-reprise-integration.json` ; les 24 parcours 301
extraits de cette relance sont dans `mesures-reprise-301.json`.
Le bilan initial 95 tests / neuf fichiers reste dans `tests-retenus.json`.

Callbacks Node réels, puis vraie boucle de jeu sur copies, analyseur interdit
pour les clics et MJ interdit d'appel. Échelles de perches et de planches
(normal et soigné), ficelle coupée d'un mètre et barre : mêmes propositions,
plans, effets, textes et monde/scène/fiche/carte après recharge ; sauvegarde
avant affichage contrôlée. Cas limites : pièce supprimée, partie ou éloignée,
bien passé chez un PNJ, propriétaire tiers, physique inconnue, mauvais outil,
rôles dupliqués, homonymes et paramètres mal formés. La projection exclut
aussi les mesures des objets cachés. Formulaire incomplet, occupation et double
soumission n'envoient pas de geste ; les flèches dans les champs ne déplacent
pas Corvus. Un nouvel état ferme le formulaire.

`mesures.json` et quatre fils détaillés : **4 commandes composées évitées**,
**17 clics par assemblage**, **8 par découpe**. Convention explicite : deux
clics d'ouverture, deux par liste native, un focus par dimension, une
validation ; sans déplacement, défilement ni frappe des chiffres. Deux
dimensions restent à saisir pour assembler, une pour découper. Zéro appel
modèle ; aucun délai réseau déduit de ces mesures Node.

## Limites et livraison

Seul l'usage actuellement modélisé, l'échelle, est proposé. La sélection
ne garantit pas l'aptitude ; aucune qualification physique ni prélèvement
automatique. Le formulaire ne prépare pas les approches vers plusieurs
matériaux éloignés. Ni Luna, ni banc PNJ, ni suite complète : entrée
d'interface, sans changement de mécanique.

Bruts : `C:/Users/msics/donjon/artifacts/um-fabrication-305/`, clôture initiale
`fin.json`, reprise `fin-reprise-integration.json`. Branche livrée sur
`origin/codex-um-fabrication` ; fusion dans l'intégration laissée
au superviseur. Aucun calcul actif ni calcul long lancé.
