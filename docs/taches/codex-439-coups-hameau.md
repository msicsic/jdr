# Tâche Codex 439 : pourquoi les coups montent au hameau 2024 (diagnostic)

Constat de la vérification d'intégration 402 (`docs/taches/rapport-codex-402-verif-integ.md`, fusionné, « Contrôles » ;
bruts `C:\Users\msics\donjon\artifacts\verif-integ-4539dd68\`, PC fixe) : frappes/touchées par nuit **15/6 → 50/27**
entre `0bad227` et `4539dd68`, dont **hameau de la crue 2024 : 35 frappes, 18 touchées, contre zéro** ; deux assommés.
La décision de frapper passe par la règle commune (force 4b/4c : prix de la violence, désespoir, témoins, défense).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 402, `docs/plan-force.md`, et le rapport 269 (coup d'Aubin pour
la torche, hameau 1985 : méthode de diagnostic d'un coup, recours pacifiques épuisés ou non).

## Question (une seule)
**Chaque coup du hameau 2024 est-il une décision légitime selon les croyances de son auteur (danger, défense, désespoir
sans recours pacifique admissible, riposte), ou une régression d'un lot fusionné depuis `0bad227` ?** Rejoue la nuit sur
copie (`4539dd68` détaché, et `0bad227` si utile), capture avant le premier coup et avant chaque nouvel épisode : auteur,
cible, but, palier, recours pacifiques essayés ou exclus (avec leur cause), témoins, prix de la violence. Regroupe les
35 frappes en épisodes. Si un lot est en cause, localise le premier commit qui change la décision (bissection bornée sur
les fusions entre les deux commits) et propose un petit lot de correction (invariant, fonctions), sans le réaliser.

## Contraintes
**Diagnostic seul : aucun code du jeu modifié.** Poste : le PC fixe. **Ne pousse pas vers origin** : le PC fixe n'a plus
d'identifiants Git en ce moment ; commite dans ta branche locale et donne le commit final dans ton dernier message, le
superviseur la récupère par SSH. Lots en cours : 431, 435, 436, 437, 438. Deux processus au plus, priorité réduite,
calculs longs détachés. Pas de Luna ni de suite complète.

## Livraison
Branche `codex-coups-hameau`, base `integration` (locale). Rapport d'une page `docs/taches/rapport-codex-439-coups-hameau.md`
(tableau des épisodes : auteur, cible, cause, légitime ou défaut, preuve) ; entrée « non fusionnée » de 8 lignes au plus
dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves). Bruts dans
`C:\Users\msics\donjon\artifacts\coups-hameau-439\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou
`QUESTION : …`.
