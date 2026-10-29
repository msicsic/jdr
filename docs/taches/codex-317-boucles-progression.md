# Tâche Codex 317 : deux boucles de déplacement sans progression (diagnostic)

Défaut révélé par la vérification d'intégration 284 (`docs/taches/rapport-codex-284-verif-integ.md`, « Contrôles et
alerte d'intégration »). Lis aussi `AGENTS.md`. Bruts de la vérification sur le laptop :
`C:\Users\msics\donjon\artifacts\verif-integ-27ff8c4\` (archives `audit-12h`, `crue-hameau-12h`).

## Les deux cas
1. **Hameau 1985** (scénario `crue_hameau`, 12 h, départ tiré, joueur passif) : entre 540 et 649 min, Aubin reprend
   **109 fois sans entrée nouvelle** le but `rejoindre Sève au beffroi`. Il reste relevé dans la crypte pendant que Sève
   est au beffroi ; **120 passages en une heure** autour des salles des vannes.
2. **Crue graine 3** (scénario `crue`, 12 h) : Gorm fait **299 passages en une heure** sur un circuit de cinq salles,
   alors que son but relevé reste « informer Ilse ».

Aucun des deux n'existe dans les mêmes nuits du témoin `0bad227`. Commit vérifié : `27ff8c4` (lots 266 à 282 :
rester près 266, appeler le donneur 275, sonde perceptive 276, allumage 277, protection 281…).

## Ce qui est demandé : diagnostic seul
1. Reproduis chaque cas sur `27ff8c4` (worktree détaché) avec la même commande que l'archive, puis vérifie que la
   chronique et les empreintes égalent l'archive. Capture le monde juste avant le premier tour de boucle ; recharge-le
   et vérifie que monde, rendu et scène sont identiques et que la boucle se reproduit d'un bloc et découpée.
2. Établis la cause : quel choix relance le trajet à chaque tour (candidat, plan, revalidation, interruption
   d'approche, appel/rendez-vous, recherche de contact), et pourquoi aucune progression vers la cible n'est
   constatée ni retenue. Dis si les deux cas ont la même cause.
3. Trouve le lot introducteur par bissection sur les fusions de `0bad227..27ff8c4` (une nuit à la fois, priorité
   réduite), en contrôlant chaque frontière sur le parent direct.
4. Vérifie si le cas existe encore sur l'intégration actuelle (`origin/integration`), qui contient en plus les lots
   303 (contact avant un service), 305, 309, 310 et 314.
5. Propose l'invariant et le petit lot de correction (contrat commun de progression d'un but de déplacement : un but
   qui ne rapproche pas de sa cible ne reconduit pas un trajet cyclique ; reprise seulement sur une entrée nouvelle),
   sans l'implémenter.

Aucun code du jeu modifié. Ni Luna, ni suite complète, ni banc comparatif.

## Contraintes
**Poste : le laptop.** Un calcul de nuit à la fois, priorité réduite, détaché avec fichier de fin. Le lot 313 (PC fixe)
modifie l'approche d'une position inconnue (`pnj._approcher`, `trajet_estime.approche`) : signale si ces fonctions
sont en cause.

## Livraison
- Branche `codex-boucles-progression`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-317-boucles-progression.md`, entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\boucles-317\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
