# Contrat entre le MJ et le monde

Ce document décrit le contrat visé. Une première tranche, limitée aux inscriptions sur un support
existant, est implémentée ; la vérification générale des dialogues libres reste à faire.

## Première tranche implémentée

Luna peut proposer le texte d'une inscription et l'identifiant de son support visible et proche.
Le moteur vérifie la lumière, le support, les doublons et la forme du texte, puis crée sur une copie
un objet lisible attaché au support. Il construit la réponse affichée à partir de cet objet. Si la
proposition est refusée, Luna reçoit la raison et peut la corriger une fois. La boucle de jeu
sauvegarde l'objet avant d'afficher la réponse. La TUI et la console suivent le même chemin.

Cette tranche ne permet pas encore de créer le support lui-même, d'enregistrer toute nouvelle
ambiance ou de vérifier chaque affirmation d'un dialogue ordinaire. Le contenu d'une inscription
est établi comme **texte gravé**, pas comme vérité de ce qu'il affirme.

## Ce qu'une phrase engage

- Une affirmation du MJ sur le monde établit un fait. Elle doit être compatible avec l'état déterministe et enregistrée avant affichage. Une odeur ou une gravure décorative a au minimum un lieu, une origine et une description persistante. Si le joueur peut la cibler, elle reçoit une identité et des interactions générales ; une gravure lisible porte son texte et les conditions de lecture.
- Une parole attribuée à un PNJ établit que ce PNJ a prononcé ces mots, à cet endroit et à cet instant. Le contenu peut être faux. Le moteur détermine les témoins capables de l'entendre et conserve cette parole dans leur mémoire ; elle ne devient pas automatiquement une vérité du monde.
- Une phrase du joueur établit son intention ou sa parole, pas la réussite du geste ni la vérité de ce qu'il affirme.
- Une hypothèse, une métaphore ou une possibilité annoncée par le MJ doit rester marquée comme telle. Elle ne peut être réutilisée comme observation certaine.

## Portée des ajouts

1. **Ambiance et détail local** : ajouter un fait descriptif compatible, situé et persistant, sans modifier une mission ni créer une solution.
2. **Élément interactif** : créer ou compléter une entité du monde avec identité, position, propriétés perceptibles et actions possibles. La validation du moteur précède sa première mention affirmative.
3. **Évolution du scénario** : exiger un déclencheur établi, une cause et des conséquences explicites. Un objet de remplacement ou un nouvel indice de quête ne peut pas naître d'une description destinée à combler un silence. Un obstacle provisoire, comme le manque de lumière, ne rend pas automatiquement l'objectif inaccessible.

Le Relais des crues désigne une cloche précise comme objectif. Une seconde cloche peut exister si une évolution de l'histoire le justifie et si l'état de la mission est mis à jour explicitement. Le test qui injecte une « seconde cloche » dans une réponse simulée révèle une faille de validation ; il ne démontre pas que Luna l'a inventée en partie.

## Boucle de rétroaction envisagée

1. Luna propose une réponse et les assertions qu'elle contient : faits observés, ajouts proposés, paroles attribuées, hypothèses et résultats d'action.
2. Une passe de contrôle relit la réponse pour relever les assertions oubliées ou mal classées. Cette passe peut utiliser Luna, mais son avis n'a pas autorité sur l'état du monde.
3. Le moteur vérifie la compatibilité avec le lieu, la perception, les objets, les connaissances, les effets réellement exécutés et les contraintes du scénario. Il prépare les ajouts admissibles sur une copie.
4. Si une assertion est contradictoire ou incomplète, Luna reçoit les motifs précis et reformule ou propose un autre ajout. Aucune phrase rejetée n'est montrée au joueur.
5. Les faits, paroles et témoins acceptés sont sauvegardés avant affichage. La réponse finale est contrôlée contre cet état ; en cas d'échec répété, le jeu donne un compte rendu sûr tiré de l'état validé.

Une relecture par LLM seule ne garantit pas la vérité d'une prose libre : elle peut oublier une assertion ou mal la classer. Pour une garantie stricte, le texte affiché devra être construit à partir d'éléments validés, ou être limité à des formulations que le moteur sait contrôler. La boucle proposée réduit le risque, mais ne prétend pas le supprimer tant que Luna peut rédiger librement la réponse finale. Les tests devront couvrir la chaîne saisie → proposition → rejet ou persistance → affichage → rechargement, avec des réponses simulées qui omettent ou contredisent volontairement des faits.

## Refus et échecs

Un refus de validation est un obstacle **avant** l'action. Seul un plan exécuté peut produire un échec du personnage, du temps écoulé ou une conséquence physique. Ce statut doit provenir du moteur et rester le même pour toute opération, qu'elle soit prévue, composée ou improvisée. Le texte présenté au joueur doit reprendre les conditions concrètes sans exposer la mécanique interne.
