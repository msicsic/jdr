# Contrat entre le MJ et le monde

Ce document décrit le contrat appliqué entre Luna (le MJ) et le moteur, et ce qui reste à
construire. Il découle de la section « Contrat du MJ » d'[AGENTS.md](../AGENTS.md).

## Trois niveaux de vérité

| Niveau | Contenu | Autorité | Contrôle avant affichage |
|---|---|---|---|
| Mécanique | entités identifiées, positions, sorties et passages, portes et attaches, possession, ressources, lumière, présence des PNJ, missions, résultats d'action, indices | moteur | doit découler des faits fournis ; une invention est refusée et passe par un fait typé |
| Interactif | objet ou détail que le joueur peut cibler | moteur, après proposition typée | validation des faits typés ci-dessous |
| Ambiance | aspect, odeur, son de fond, texture, impression | Luna | libre, enregistrée avec son lieu, ne crée aucune entité mécanique |

## Contrôle de la prose

Chaque réponse libre de Luna (dialogue, avis de clarification, explication d'un refus)
est découpée en segments et relue par un auditeur, qui classe chaque segment :

| Verdict | Traitement |
|---|---|
| `neutre` (salutation, conseil, question) | affiché tel quel |
| `hypothese` (possibilité présentée comme incertaine) | affiché tel quel |
| `ambiance` (description sensorielle) | affiché tel quel ; enregistré dans `ambiances[lieu]` avec les éléments évoqués |
| `parole` (propos d'un PNJ présent) | locuteur présent et citation exacte exigés ; enregistrée avec lieu, instant et auditeurs ; son contenu n'est pas une vérité |
| `mecanique` | doit citer au moins une clé de fait fournie (`objet:<id>`, `perception`, `salle`…) |
| `invention_protegee`, `contradictoire` | révision demandée à Luna ; jamais affiché |

Le texte accepté est affiché **tel que Luna l'a écrit**. Les ambiances du lieu courant
reviennent dans le contexte suivant (`ambiance_etablie`), ce qui permet à Luna de rester
cohérente et à l'auditeur de refuser une ambiance qui les contredit.

**Garde-fou déterministe.** Les noms et alias de toutes les entités du monde, y compris
cachées, et les noms des salles forment un lexique dérivé de l'état
([donjon/lexique.py](../donjon/lexique.py)). Un terme du lexique présent dans le texte mais
absent de tout ce que Luna a reçu (faits, conversation récente, message du joueur) entraîne
une révision, quel que soit le verdict de l'auditeur. Le même contrôle s'applique aux
textes des ajouts persistants (détail, objet, inscription, parole, portrait, savoir), le
nom de l'élément créé faisant partie de l'ajout. Il est refait au moment de l'enregistrement. Ce que croient les
personnages présents (`esprits_interlocuteurs`) n'est pas un fondement pour la narration : un
nom connu seulement par leurs croyances n'est admis que dans une réplique, entre guillemets.
Ce qu'un personnage croit ne se dit que par sa bouche.

Une réponse refusée est révisée au plus deux fois ; aucun texte refusé n'est affiché. Après
trois échecs, le jeu affiche une phrase sûre du moteur. La réponse acceptée, ses paroles et
ses ambiances sont enregistrées et sauvegardées avant l'affichage.

**Ce que le MJ reçoit d'un refus d'audit** (branche `audits-attendu`). Un refus d'audit suit le
contrat des refus du moteur (`donjon/refus.py`) : un `motif`, la règle, et un `attendu`, qui dit
où (`partie`, `segment` : l'indice du segment tel que l'auditeur l'a reçu, ou le champ d'un
ajout comme `proposition.ajouts[0].texte`), ce qui a été reçu (la phrase, le nom ou la citation
en cause, tels qu'écrits) et ce qui serait accepté, en identifiants ou citations exactes ; une
cause par refus (un mot d'auteur, un nom sans fondement, une parole racontée, une citation
nouvelle : chacun le sien). Pour un verdict d'auditeur (narratif, portée, capacités, contre-revue
d'action), `attendu` donne sa catégorie et son motif tels quels (« selon l'auditeur (verdict
invention_protegee) : « … » »), sans prétendre à plus de certitude que ce jugement. Un rapport
illisible (`refus.RapportIllisible`) ne reproche rien au texte : son `attendu` le dit. Chaque
relance reçoit tous les refus du tour dans `controle_narratif`, et la contre-revue d'action passe
par `retour_moteur` comme un refus du moteur. Ni le motif ni `attendu` ne s'affichent : un texte
refusé n'est jamais montré, et le repli ne cite que le moteur ou des phrases admises.

| Voie | Refus (une cause chacun) | `attendu` cite |
|---|---|---|
| texte vide | texte vide | la partie |
| voix d'auteur (`voix_auteur`) | un mot (« Corvus », « les faits »…) | segment, mot |
| nom sans fondement (`mentions`, `mentions_proposees`) | un nom | segment ou champ de l'ajout, nom tel qu'écrit ; jamais l'identifiant de l'entité cachée |
| parole sans moteur (`paroles_sans_moteur`) | une parole racontée de Corvus ; une citation nouvelle | segment, mots ou citation ; `parole_prevue.personnage` |
| voix inconnue (`voix_inconnues`) | le récit la nomme ; sa réplique nomme quelqu'un | segment, nom, `interlocuteurs.<voix>.nom` |
| verdicts (`controler`) | mécanique sans source, locuteur absent ou non destinataire, engagement sans appui, parole mal citée, invention, contradiction | segment, phrase, verdict et motif de l'auditeur ; clés `objet:<id>` qui la nommeraient, présents, destinataires, engagements prévus mot pour mot |
| portée (`portee_narrative.controler`) | représentation, capacité, fixation, impact, preuve, fragment sans preuve | description et sujet, ce que l'auditeur a lu |
| capacités (`coherence_physique.controler`) | qualification incompatible | qualification, objet, champs proposés |
| contre-revue d'action (`couverture_action.verifier`) | plan non conforme | titre, action et cible du plan, motif de la revue |
| rapport illisible | — | « aucune phrase n'est en cause » |

**Ce que dit une parole de Corvus validée** (branche `parole-corrections`). `conversation_validee`
porte `issue`, la phrase du moteur sur ce qui a eu lieu (Corvus a dit ces mots, à qui, qui lui
répond, qui l'a entendu sans être interpellé ; « Aucune réponse ne te parvient » sinon), ajoutée aux
attestations, et `repondent`, ceux qui répondent : ses destinataires, et à la cantonade ceux qui l'ont
entendue et ont choisi de répondre (`paroles.repondants`). Seuls ceux de `repondent` parlent
(`narration.destinataires_parole`) ; l'auditeur sait que leur réplique est une parole permise sans
« parole prévue », et que les dire muets contredit l'issue. Les objets reçus disent ce qu'ils
mesurent : `a_portee_de_main` (toucher d'ici), `a_portee_de_voix` pour un personnage ; la salle,
`sorties_connues` en cases (n'en connaître aucune n'atteste pas qu'il n'y en a pas).

**Ce qui reste probabiliste.** Le classement des segments par l'auditeur. Une affirmation
mécanique fausse formulée sans nom d'entité (« la pièce est plongée dans le noir » alors
qu'elle est éclairée), ou un objet manipulable présenté comme ambiance, dépend de son
jugement. Le banc de parties (`tools/banc_parties.py`) mesure ce résidu. Un élément
d'ambiance ciblé par le joueur doit être matérialisé ou déclaré non manipulable : voir la
matérialisation à la demande, quand elle sera en place.

## Contrôle des actions

Avant l'exécution d'une action proposée par Luna, une contre-revue indépendante compare
la demande du joueur aux opérations du plan. Elle ne juge que l'état : action et cibles,
changement durable demandé mais absent, changement durable ajouté sans demande. La
manière du geste (style, position des mains, caractère d'un son) relève du récit, portée
par l'outil et la méthode. En cas de doute, le plan est accepté : le moteur garde
l'autorité sur chaque effet. Les conséquences affichées viennent du journal du moteur.

## Faits typés persistants

Luna peut proposer un groupe de faits structurés : détail visible, inscription ou parole. Le
moteur vérifie les supports et locuteurs disponibles, la perception et la forme des données.
Les descriptions de détail et les facettes de personnage passent aussi par une contre revue.
Le nom et chaque phrase sont soumis séparément. Luna découpe chaque entrée en fragments
contigus et cherche les affirmations vérifiables indépendamment du sujet proposé. Le moteur
vérifie que les fragments couvrent tout le texte. Un fragment porte sur le sujet, sur une
attestation exacte de l'état courant, sur l'ambiance autour du sujet, ou il est sans preuve ;
un fragment sans preuve entraîne une révision avant toute mutation.
L'inscription et la parole sont conservées comme textes cités ; leur contenu n'établit pas
la vérité de ce qu'elles disent. Le moteur applique ensuite le groupe sur une copie.
Les détails deviennent des cibles ; une parole est
enregistrée avec son auteur, son lieu et ses auditeurs, sans transformer son contenu en vérité.
Le texte affiché est construit à partir des faits acceptés. Si la proposition est refusée,
Luna reçoit la raison et peut la corriger. La TUI et la console sauvegardent la
transaction avant affichage.

Un fait typé ne permet pas encore de créer le support lui-même. Le contenu d'une inscription
est établi comme **texte gravé**, pas comme vérité de ce qu'il affirme.

## Ce qu'une phrase engage

- Une affirmation mécanique du MJ doit être compatible avec l'état déterministe. Une ambiance (une odeur, un aspect décoratif) est enregistrée avec son lieu avant affichage. Si le joueur la cible, elle doit recevoir une identité et des interactions générales, ou être déclarée non manipulable ; une gravure lisible porte son texte et les conditions de lecture.
- Une parole attribuée à un PNJ établit que ce PNJ a prononcé ces mots, à cet endroit et à cet instant. Le contenu peut être faux. Le moteur détermine les témoins capables de l'entendre et conserve cette parole dans leur mémoire ; elle ne devient pas automatiquement une vérité du monde.
- Une phrase du joueur établit son intention ou sa parole, pas la réussite du geste ni la vérité de ce qu'il affirme.
- Une hypothèse, une métaphore ou une possibilité annoncée par le MJ doit rester marquée comme telle. Elle ne peut être réutilisée comme observation certaine.

## Portée des ajouts

1. **Ambiance et détail local** : ajouter un fait descriptif compatible, situé et persistant, sans modifier une mission ni créer une solution.
2. **Élément interactif** : créer ou compléter une entité du monde avec identité, position, propriétés perceptibles et actions possibles. La validation du moteur précède sa première mention affirmative.
3. **Évolution du scénario** : exiger un déclencheur établi, une cause et des conséquences explicites. Un objet de remplacement ou un nouvel indice de quête ne peut pas naître d'une description destinée à combler un silence. Un obstacle provisoire, comme le manque de lumière, ne rend pas automatiquement l'objectif inaccessible.

Le Relais des crues désigne une cloche précise comme objectif. Une seconde cloche peut exister si une évolution de l'histoire le justifie et si l'état de la mission est mis à jour explicitement. Une seconde cloche affirmée dans la prose est une `invention_protegee`.

## Objets, capacités et évolutions

Le type `objet`
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

Un refus de forme (`refus.RefusDeForme` : un champ, une borne, la mauvaise action, « impossible »
sans réexamen) ne dit rien du monde : il revient au MJ avec son `attendu`, avec une correction à
part de la correction ordinaire (trois propositions au plus), et ne se montre jamais au joueur ; à
une question de faisabilité, le joueur ne lit tel quel que le refus d'une raison du monde.

Un refus de validation survient **avant** l'action. Seul un plan exécuté peut produire un
échec du personnage, du temps écoulé ou une conséquence physique. Après deux propositions
invalides, Luna peut expliquer les conditions attestées sans annoncer une tentative de
Corvus ; si cette réponse échoue aussi, un message sûr précise qu'aucun geste n'a été tenté.
