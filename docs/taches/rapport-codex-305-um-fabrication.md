# Lot 305 — U-M fabrication

Branche `codex-um-fabrication`, base intégration `37f68d4`, **non fusionnée**.

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
`jeu.py` et `tui.py` restent inchangés.

## Vérification et mesures

**95 tests distincts / neuf fichiers verts** : fabrication 305, assemblage,
artisanat, matière, descripteur U-D, menus d'outils, inventaire, web/Node et
premiers gestes terminal. Deux travailleurs au plus, priorité réduite,
interpréteur du dépôt principal (`.venv` absente du worktree).
Les huit fichiers existants donnent 88 tests verts ; les sept nouveaux sont
repris après correction des fixtures de propriétaire et initialisation de
scène. Bilan retenu dans `tests-retenus.json`, traces initiales conservées.

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

Bruts : `C:/Users/msics/donjon/artifacts/um-fabrication-305/`, fichier final
`fin.json`. Branche livrée sur `origin/codex-um-fabrication` ; fusion laissée
au superviseur. Aucun calcul actif ni calcul long lancé.
