# Lot 354 — U-M social information

Branche `codex-um-social-information`, base intégration `57c9771d`, non fusionnée.

## Invariant et changement

Le formulaire web choisit l'interlocuteur perçu (voix comprise), l'acte
d'information et ses seuls paramètres connus de Corvus. `information_publique`
ne transporte que des couples identifiant/nom : aucune position du sujet,
croyance du répondant, possession cachée ou condition sociale. Les lieux sont
des choix d'assertion, sans valeur présélectionnée ; annoncer un lieu faux reste possible.

`parole_information` construit le contenu typé et les mots du joueur sans
analyse de texte. `preparer_information` constitue l'unique entrée U-D vers
les transactions de parole : même `preparer_parole`, même préparation sur copie,
émissions G16, contrôle de publication, consentement U-C et sauvegarde avant affichage.
Les questions restent légères ; une affirmation attend « tenter » ou « annuler ».
L'adresse et tous les paramètres sont revalidés après l'aperçu, sans remplacement
de l'interlocuteur parti par un autre personnage.

## Raccord autorisé et recouvrement

Le brief initial ne prévoyait pas d'entrée de parole dans la boucle des
descripteurs. Le superviseur a autorisé explicitement deux extensions :
neuf lignes dans `jeu.py` appellent la fonction commune ; `preparer_parole`
accepte l'adresse structurée interne après contrôle exact du contenu canonique.
Le chemin texte conserve son analyseur ; les deux entrées rejoignent les mêmes
validateurs d'adresse, de portée, de contenu et de réception.
**Fichier commun avec 353 : `jeu.py`**, bloc des descripteurs uniquement.
`comprehension.contenu` rend une ressource connue par sa désignation publique,
y compris si le moteur utilise son identifiant privé derrière une référence masquée.
Aucune règle de réponse, d'audience ou de localisation n'est changée.
Ni `mj.py`, `compilateur.py`, `tui.py`, ni le catalogue des autres gestes ne sont modifiés.

## Vérification et mesures

Validation finale **en cours**, dix fichiers distincts : onze nouveaux tests,
G16, paroles/voix/contenus, consentement, compréhension et web/Node.
Les tests comparent les contenus, les rapports et le monde du clic à ceux de
la saisie typée, puis les paroles entendues, la scène, la fiche et le regard
après sauvegarde et recharge. Ils exercent les vrais callbacks Node et la vraie
boucle de jeu, avec analyse du clic et appels au modèle interdits.
Les quatre actes sont exercés au Relais et à l'auberge : voix qui se nomme,
croyances fausses, méfiance, homonymes, annulation, départ à réception et à confirmation.
Node mesure **une saisie évitée par acte**, **6 clics** pour l'identité,
**8** pour ressource/localisation, **11** pour annoncer un lieu (confirmation comprise).
Deux clics par liste déroulante sont comptés, ouverture puis choix, sans temps humain simulé.
Les passes intermédiaires rouges restent dans les bruts : raccord de voix,
texte vide interdit à la sauvegarde, puis harnais initial ne réinstallant pas la
mémoire du mode cases comme la vraie boucle. Le dernier harnais conserve tous les
champs et normalise seulement tuples/listes JSON ; aucun oracle mécanique n'est retiré.

## Limites et livraison

**Demander la localisation d'un objet n'est pas disponible** : la règle actuelle
de `paroles.py` réserve cet acte aux personnes. Limite explicitement acceptée
par le superviseur et annoncée dans le formulaire ; aucune extension du jeu
n'est introduite pour contourner cette borne. Dire où se trouve un objet connu
reste une affirmation typée. Une déclaration n'invente aucune réplique libre du PNJ.
Le formulaire n'étend pas les types de parole ni les demandes économiques.
Pas de Luna, de suite complète ou de banc PNJ. Bruts :
`C:/Users/msics/donjon/artifacts/um-social-information-354/`.
Deux travailleurs réduits au plus ; la consolidation détachée écrit en dernier
`fin-calcul.json` (statut, empreintes, contrats AST et mesures). Livraison en attente
de lecture de cette fin et d'attribution de tout incident éventuel.
