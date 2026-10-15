# Instructions de développement — Le Seuil

## Règle de conception prioritaire

Ne corrige pas un comportement du jeu en ajoutant un cas particulier pour l'exemple qui l'a révélé. Cela inclut les branches liées à un objet, un lieu, un personnage, une formulation du joueur, un type de fait narratif ou une consigne supplémentaire au prompt de Luna.

Pour chaque bug, identifie l'invariant général en cause et corrige le contrat commun entre la saisie, le MJ, le moteur, le rendu et la sauvegarde. Une règle propre au scénario peut exister comme donnée ou mécanique explicite du scénario ; elle ne doit pas masquer une lacune du moteur général.

Avant de déclarer la correction terminée, vérifie la chaîne complète avec le cas réel qui a révélé le problème et au moins un autre cas de même nature. Les tests doivent contrôler l'état du monde et ce que le joueur voit après rechargement, pas seulement la réponse d'une fonction isolée.

Si l'invariant ne peut pas encore être garanti, indique clairement cette limite. Ne présente pas un traitement partiel ou une liste élargie de cas comme une solution générale.

## Contrat du MJ

Toute affirmation factuelle du MJ affichée au joueur doit être compatible avec l'état du monde et ses conséquences doivent être enregistrées avant l'affichage. Cette exigence s'applique à toutes les voies de narration, y compris le dialogue ordinaire, les descriptions et les résultats d'action. Une parole de PNJ établit qu'elle a été prononcée et entendue, sans établir que son contenu est vrai.

Luna reste le MJ du jeu avec le modèle `gpt-6-luna`. Le moteur conserve l'autorité sur les positions, la perception, les ressources, les actions et les sauvegardes. La comparaison entre modèles reste désactivée.

Le code actuel ne garantit pas encore la validation sémantique de toutes les phrases du MJ. Ne contourne pas ce manque en ajoutant un nouveau mode, un nouveau mot-clé ou une exception propre à un exemple ; traite-le par un mécanisme commun à toutes les réponses du MJ.
