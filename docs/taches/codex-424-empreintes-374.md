# Tâche Codex 424 : empreintes changées par le lot 374 (famille E du 414)

Le lot 414 (`docs/taches/rapport-codex-414-suite-4539dd68.md`, fusionné) a attribué les rouges de la suite `4539dd68`.
Les familles R et C sont traitées (lots 417, 419). Reste la **famille E** : deux tests dont les empreintes changent avec
le comportement du lot 374 (position crue comme hypothèse datée, `c3f0c2d5`) :

- `test_completion_preuves` : `captures_reelles_plans_et_absences_prix_recharge_et_rendu` (quatre empreintes du monde) ;
- `test_gestes_par_noeud` : `successeurs_ordre_couts_et_noeuds_de_la_base` (successeurs et empreintes).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 414 et celui du 374 (`docs/taches/rapport-codex-374-*.md`).

## Invariant (un seul)
**Une empreinte de test ne se réancre que si chaque différence est attribuée à une décision voulue du 374 (preuve
citée : la position crue périmée change le plan, le successeur ou le coût) ; toute différence non attribuée est un
défaut à corriger dans le code, pas dans l'oracle.**

Méthode : rejoue chaque capture sur `c3f0c2d5^` et `c3f0c2d5` (copies), compare plan par plan, successeur par successeur.
Pour chaque écart, cite la croyance de position datée qui le cause. Réancre seulement les écarts voulus, en gardant les
autres assertions telles quelles. Si un écart révèle un défaut, corrige le contrat commun (aucun cas de scénario) et
garde l'empreinte d'origine sur ce point.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : ces deux fichiers de tests ; code du jeu seulement si un défaut est établi.
Lots en cours : 402 (vérification d'intégration, calcul seul), 419 (vérification de contact), 425 (découpe des
combustibles), 426 (K0). Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite.

## Vérification
Les deux méthodes vertes ; tests voisins (`test_planification`, `test_completion_preuves`, `test_gestes_par_noeud`)
verts. Si le code du jeu change : empreintes 2 h, quatre graines, Relais et scénarios touchés. Pas de suite complète, ni Luna.

## Livraison
Branche `codex-empreintes-374`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-424-empreintes-374.md` (tableau des
écarts : voulu ou défaut, preuve) ; entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - »
qui nomme la branche entre accents graves). Bruts dans `C:\Users\msics\donjon\artifacts\empreintes-374-424\`. Termine par
`LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
