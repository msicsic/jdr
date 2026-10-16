# Instructions de développement — Le Seuil

## Règle de conception prioritaire

Ne corrige pas un comportement du jeu en ajoutant un cas particulier pour l'exemple qui l'a révélé. Cela inclut les branches liées à un objet, un lieu, un personnage, une formulation du joueur, un type de fait narratif ou une consigne supplémentaire au prompt de Luna.

Pour chaque bug, identifie l'invariant général en cause et corrige le contrat commun entre la saisie, le MJ, le moteur, le rendu et la sauvegarde. Une règle propre au scénario peut exister comme donnée ou mécanique explicite du scénario ; elle ne doit pas masquer une lacune du moteur général.

Avant de déclarer la correction terminée, vérifie la chaîne complète avec le cas réel qui a révélé le problème et au moins un autre cas de même nature. Les tests doivent contrôler l'état du monde et ce que le joueur voit après rechargement, pas seulement la réponse d'une fonction isolée.

Si l'invariant ne peut pas encore être garanti, indique clairement cette limite. Ne présente pas un traitement partiel ou une liste élargie de cas comme une solution générale.

## Contrat du MJ

Toute affirmation factuelle du MJ affichée au joueur doit être compatible avec l'état du monde et ses conséquences doivent être enregistrées avant l'affichage. Cette exigence s'applique à toutes les voies de narration, y compris le dialogue ordinaire, les descriptions et les résultats d'action. Une parole de PNJ établit qu'elle a été prononcée et entendue, sans établir que son contenu est vrai.

Les affirmations du MJ relèvent de trois niveaux. **Mécanique** : entités identifiées, positions, sorties et passages, possession, ressources, lumière, présence des PNJ, missions et résultats d'action. Ces affirmations doivent être compatibles avec l'état ; une invention dans ces domaines passe par une proposition typée validée avant affichage. **Interactif** : un objet ou un détail que le joueur peut cibler existe dans l'état avant d'être manipulé. **Ambiance** : aspect, odeur, son de fond, impression. L'ambiance est libre, enregistrée avec son lieu avant affichage, et ne crée aucune entité mécanique. Un élément d'ambiance ciblé par le joueur est matérialisé par le moteur ou déclaré non manipulable.

Luna reste le MJ du jeu avec le modèle `gpt-6-luna`. Le moteur conserve l'autorité sur les positions, la perception, les ressources, les actions et les sauvegardes. La comparaison entre modèles reste désactivée.

Le contrôle garantit de façon déterministe l'absence de fuite d'entités non perçues. La détection des contradictions mécaniques reste en partie sémantique. Ne contourne pas ce manque par un nouveau mode, un mot-clé ou une exception propre à un exemple ; renforce le mécanisme commun.
