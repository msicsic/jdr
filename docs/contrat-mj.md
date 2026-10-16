# Contrat entre le MJ et le monde

Ce document décrit le contrat appliqué et ce qui reste à construire. Les réponses libres
de Luna sont relues avant affichage. Une affirmation factuelle doit reprendre exactement
une phrase attestée par le moteur depuis l'état courant ; une clé d'objet vaguement liée
ne suffit plus. Luna classe encore les phrases, mais ne peut pas faire accepter une nouvelle
affirmation en citant simplement une source existante.

## Première tranche implémentée

Luna peut proposer un groupe de faits structurés : détail visible, inscription ou parole. Le
moteur vérifie les supports et locuteurs disponibles, la perception et la forme des données.
Les descriptions de détail et les facettes de personnage passent aussi par une contre revue.
Le nom et chaque phrase sont soumis séparément. Luna découpe chaque entrée en fragments
contigus et cherche les affirmations vérifiables indépendamment du sujet proposé. Le moteur
vérifie que les fragments couvrent tout le texte et qu'une preuve tirée de l'état courant
correspond exactement à une attestation. Un fragment sans preuve entraîne une révision
avant toute mutation.
L'inscription et la parole sont conservées comme textes cités ; leur contenu n'établit pas
la vérité de ce qu'elles disent. Le moteur applique ensuite le groupe sur une copie.
Les détails deviennent des cibles ; une parole est
enregistrée avec son auteur, son lieu et ses auditeurs, sans transformer son contenu en vérité.
Le texte affiché est construit à partir des faits acceptés. Si la proposition est refusée,
Luna reçoit la raison et peut la corriger. La TUI et la console sauvegardent la
transaction avant affichage.

Cette tranche ne permet pas encore de créer le support lui-même, de décrire une ambiance sans
ancrage. Le contenu d'une inscription
est établi comme **texte gravé**, pas comme vérité de ce qu'il affirme.

## Contrôle commun actuellement appliqué

Chaque réponse finale libre est découpée en segments et relue par Luna. L'auditeur classe
chaque segment comme établi, hypothétique, neutre, parole attribuée, nouveau fait ou
contradiction. Le moteur vérifie la couverture, le locuteur et la correspondance exacte
entre chaque segment factuel établi et une attestation de l'état courant. Les paroles sont
reformulées avec leur locuteur, les hypothèses sont annoncées comme possibilités et les
formules neutres deviennent une réponse prudente. Une affirmation nouvelle ou contradictoire
entraîne une révision, au plus deux fois ; aucun texte rejeté n'est affiché.
Si les trois formulations échouent, le jeu affiche une phrase déjà attestée depuis l'état
courant, sans créer le fait proposé.

La réponse acceptée et ses références sont enregistrées avant affichage. Une parole nouvelle
attribuée à un PNJ présent est conservée avec son lieu, son instant et ses auditeurs ; son
contenu ne devient pas une vérité du monde. Le contrôle ajoute des appels à Luna et leur
consommation est additionnée dans la trace debug.

La classification de la prose par l'auditeur reste probabiliste. Une erreur de classement
ne peut toutefois plus faire passer une phrase factuelle libre pour une attestation : le
moteur exige le texte exact. La contre revue impose désormais une couverture textuelle et
des preuves vérifiables. La contre revue classe maintenant aussi la représentation nécessaire
de chaque nom et phrase : aspect local, objet autonome, texte lisible, état du monde ou portrait.
Le moteur refuse une classification incompatible avec le type d'ajout proposé, même si Luna
a couvert tout le texte en le qualifiant de propriété du sujet. Luna peut encore se tromper
sur cette classification ou manquer une implication. Un contrat de faits plus riche sera
nécessaire pour garantir que toute entité sous-entendue devient une cible. Les tests simulés vérifient le rejet, la révision,
l'affichage et le rechargement ; un essai avec Luna réel vérifie le parcours d'un détail
créé sur une partie temporaire.

Les résultats exécutés suivent un contrat plus strict : le moteur rédige les conséquences
pendant l'application de ses effets et les enregistre dans son journal. La console et la TUI
affichent ces phrases après sauvegarde, sans demander à Luna de les paraphraser. Les lignes
de calcul des jets restent consultables dans le journal. Ce rendu est moins libre que le
dialogue, mais les effets affichés proviennent de l'exécution réelle. Pour une improvisation,
le brouillon narratif et la formulation de l'intention de Luna ne sont ni affichés ni
réinjectés comme faits : le moteur décrit le type de geste, ses cibles et les effets
validés de la branche réellement résolue.
Avant l'exécution d'une action proposée par Luna, une contre-revue indépendante compare
l'intention entière du joueur aux opérations du plan préparé par le moteur. Un effet
perceptible nécessaire mais absent entraîne une correction du plan avant toute mutation.
Le contrôle peut se tromper sur le sens de la phrase ; le moteur conserve l'autorité sur
la possibilité et l'application de chaque effet.
Pour un son improvisé, Luna choisit une catégorie acoustique contrôlée par le moteur.
Le souvenir d'un PNJ conserve cette forme et l'intensité, sans attribuer au personnage
des paroles que le joueur n'a pas prononcées.

## Ce qu'une phrase engage

- Une affirmation du MJ sur le monde établit un fait. Elle doit être compatible avec l'état déterministe et enregistrée avant affichage. Une odeur ou une gravure décorative a au minimum un lieu, une origine et une description persistante. Si le joueur peut la cibler, elle reçoit une identité et des interactions générales ; une gravure lisible porte son texte et les conditions de lecture.
- Une parole attribuée à un PNJ établit que ce PNJ a prononcé ces mots, à cet endroit et à cet instant. Le contenu peut être faux. Le moteur détermine les témoins capables de l'entendre et conserve cette parole dans leur mémoire ; elle ne devient pas automatiquement une vérité du monde.
- Une phrase du joueur établit son intention ou sa parole, pas la réussite du geste ni la vérité de ce qu'il affirme.
- Une hypothèse, une métaphore ou une possibilité annoncée par le MJ doit rester marquée comme telle. Elle ne peut être réutilisée comme observation certaine.

## Portée des ajouts

1. **Ambiance et détail local** : ajouter un fait descriptif compatible, situé et persistant, sans modifier une mission ni créer une solution.
2. **Élément interactif** : créer ou compléter une entité du monde avec identité, position, propriétés perceptibles et actions possibles. La validation du moteur précède sa première mention affirmative.
3. **Évolution du scénario** : exiger un déclencheur établi, une cause et des conséquences explicites. Un objet de remplacement ou un nouvel indice de quête ne peut pas naître d'une description destinée à combler un silence. Un obstacle provisoire, comme le manque de lumière, ne rend pas automatiquement l'objectif inaccessible.

Le Relais des crues désigne une cloche précise comme objectif. Une seconde cloche peut exister si une évolution de l'histoire le justifie et si l'état de la mission est mis à jour explicitement. Un test vérifie désormais que la phrase « une seconde cloche » est refusée même lorsque l'auditeur cite la cloche existante comme source.

## Contrat complet encore visé

1. Luna propose une réponse et les assertions qu'elle contient : faits observés, ajouts proposés, paroles attribuées, hypothèses et résultats d'action.
2. La relecture relève les assertions oubliées ou mal classées, sans avoir autorité sur l'état du monde.
3. Le moteur vérifie lui-même la compatibilité de chaque assertion avec le lieu, la perception, les objets, les connaissances, les effets réellement exécutés et les contraintes du scénario. Il prépare les ajouts admissibles sur une copie.
4. Si une assertion est contradictoire ou incomplète, Luna reçoit les motifs précis et reformule ou propose un autre ajout. Aucune phrase rejetée n'est montrée au joueur.
5. Les faits, paroles et témoins acceptés sont sauvegardés avant affichage. La réponse finale est construite depuis cet état ; en cas d'échec répété, le jeu donne un compte rendu sûr tiré des seuls faits validés.

La réponse factuelle libre est désormais limitée aux formulations attestées. Le type `objet`
crée une entité physique située, dotée d'une masse, d'une matière, d'une mobilité et d'une
relation au support : `pose`, `fixe` ou `contenu`. Le support annonce les relations possibles ;
les sols portent les objets et seuls les contenants ouverts peuvent en recevoir. Le moteur
formule cette relation depuis l'état enregistré. Un objet fixé et amovible doit être détaché
avant ramassage ; une attache simple se libère à la main, tandis que les fixations du scénario
déclarent une extraction avec outil. La contre revue classe séparément les relations affirmées
par le nom et la description et refuse celles qui ne correspondent pas à la transaction. Le type
`evolution` ne contient qu'un identifiant de transition déclarée par le scénario : ses
conditions et ses effets physiques ou son nouvel objectif sont définis dans la partie,
validés par le moteur et appliqués une seule fois. Chaque condition doit porter sur un objet
actuellement visible ; le déplacement déclare son lieu de départ et l'évolution d'objectif
nomme la cible précédente. Une transition devenue périmée cesse d'être proposée. Luna ne
peut pas soumettre librement un
nouvel objectif ou téléporter un objet par une phrase descriptive.

Les objets inventés déclarent aussi une liste de capacités physiques : son avec intensité,
lumière avec niveau et combustible, ou outil avec les usages `couper`, `levier`, `allumage`
et une puissance bornée. La contre revue vérifie que le nom ou la description
annonce ces capacités et qu'aucune capacité annoncée ne manque à l'état. Le moteur borne les
valeurs, crée la source lumineuse éteinte et emploie les opérations ordinaires pour la faire
sonner ou l'allumer. Les outils improvisés passent par les mêmes contrôles de portée,
portage et usages que les outils du scénario. Le déplacement des objets, y compris lors d'une transition de scénario,
passe par la même mutation du lieu, de l'attache et de l'ancrage visuel.

La cible d'une coupe peut déclarer `tranchable` avec un seuil de puissance et une
ténacité. Le moteur compare l'outil à ce seuil, puis réduit l'intégrité à chaque geste
réussi. Le nom du matériau n'est plus une condition codée. Une coupe partielle est
annoncée comme une entaille ; l'intégrité nulle signifie que l'objet est brisé. Ce
modèle ne crée pas encore deux fragments réutilisables à partir d'un objet sectionné.

Une capacité manquante sur un objet déjà connu peut aussi passer par le même contrat
de faits persistants : `qualification` vise son identifiant et propose des capacités
bornées. Le moteur exige un objet observable à portée et refuse d'écraser une capacité
établie. Pour la coupe d'un objet existant, Luna déclare `moyen` et `coupe_possible` :
le jugement porte sur la paire cible–outil dans leur état présent et ne réécrit ni
l'intégrité ni le maximum. Il est sauvegardé avant la tentative.
Une contre revue distincte juge sa compatibilité avec la matière et la description.
Le MJ réexamine alors l'intention initiale ; le joueur n'a pas à la répéter. Cette
contre revue sémantique peut se tromper, donc ses jugements ne garantissent pas à eux
seuls la justesse physique d'une propriété nouvellement inventée.
Les objets créés avec un seuil de coupe, ainsi que ceux des scénarios qui en possèdent
un, suivent cette règle numérique déclarée. Un objet existant sans seuil reçoit un
jugement limité au moyen examiné : une scie peut donc couper après qu'une hache a été
écartée, même si sa puissance numérique est inférieure. La puissance règle encore les
dégâts ; elle ne sert pas de preuve de compatibilité entre moyens différents.

Le même type `qualification` peut consigner un jugement positif ou négatif de coupe.
Le refus conserve l'état physique de l'objet et de l'outil : il cesse de s'appliquer
si l'un change. Une aptitude positive subsiste après une entaille tant que la structure
des deux objets et leur usage restent les mêmes. Les jugements anciens restent des
souvenirs, signalés comme tels dans la description. Ils sont relus par la contre revue,
enregistrés avant affichage et repris après rechargement.
Si Luna ne formule pas correctement la réponse qui suit, le compte rendu déterministe
du fait validé reste affichable et sauvegardé ; aucune action fictive n'est créée.

Un support mural peut déclarer une case d'affichage distincte de la case de contact.
Cette case est validée comme mur voisin, héritée par les objets qui y sont fixés et conservée
dans le souvenir visuel. La portée et la visibilité continuent à partir de la face accessible.

Ces mécanismes ne donnent pas encore toutes les capacités d'un objet improvisé : d'autres
usages comme ouvrir une serrure demandent encore des propriétés et opérations validées.
Une fixation improvisée
amovible utilise pour l'instant un détachement manuel ; les fixations nécessitant un outil
demandent une propriété physique plus précise. Le classement
sémantique de la prose reste probabiliste. Les tests couvrent la chaîne
saisie → proposition → rejet ou persistance → affichage → rechargement, avec des réponses
simulées qui contredisent volontairement l'état du monde.

## Refus et échecs

Un refus de validation survient **avant** l'action. Seul un plan exécuté peut produire un
échec du personnage, du temps écoulé ou une conséquence physique. Après deux propositions
invalides, Luna peut expliquer les conditions attestées sans annoncer une tentative de
Corvus ; si cette réponse échoue aussi, un message sûr précise qu'aucun geste n'a été tenté.
