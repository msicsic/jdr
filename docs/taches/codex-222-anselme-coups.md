# Tâche Codex 222 (diagnostic) : Anselme entre poêle et garde, et les coups de la crue 2024

Deux constats de la vérification d'intégration 212 (`docs/taches/rapport-codex-212-verif-integ.md`, « Petits lots à instruire »),
sans attribution à un lot ni date d'apparition :
- **auberge 2024, Anselme dès 200 min** : onze alternances, dont dix entre entretenir son poêle et garder ses biens ;
- **crue 2024, 672–691 min** : **16 coups, sept touchés, Gorm inconscient** ; Brune alterne chaleur, abri et riposte. La violence
  seule n'est pas un défaut ; le rapport demande d'examiner la revalidation commune des remèdes face à une menace crue.
Le compteur 219 (fusionné) classe maintenant chaque retour ; le lot 213 (contrat d'engagement) est en cours et pourrait couvrir
une partie de ces alternances. **Diagnostic seul : aucun fichier du jeu modifié**, pour décider s'il faut un lot et lequel.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot calcule sur ce poste (213) : **un seul processus**, priorité
réduite. **Bruts dans `C:\Users\msics\donjon\artifacts\anselme-coups-222\`.** Les bruts de la nuit sont dans
`C:\Users\msics\donjon\artifacts\verif-integ-4d4c625\`. Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 212, 219, 209, 196 § 4, 155 (fuite et lumière, auteurs de violence actifs), 167 b et c (garder,
protéger, interposition), puis le code concerné.

## Ce qu'on te demande
1. **Reproduire** chaque cas sur `4d4c625` et sur l'intégration actuelle (`fa330e1`, avec 205, 207, 211, 214, 219, 220) : existe-t-il
   encore ? Classe 219 de chaque retour (préemption légitime ou répétition suspecte) ; captures rechargeables juste avant.
2. **Cause** : la chaîne de décisions, la fonction et la condition ; pour les coups, qui frappe qui et pourquoi (défense, riposte,
   prise), si chaque coup suit une décision justifiée par les croyances de son auteur, et si les remèdes de Brune (chaleur, abri,
   riposte) se défont l'un l'autre.
3. **Attribution** : ce que couvrira le contrat d'engagement du lot 213 (§ 4.1 du rapport 196), ce qui relève d'un autre invariant
   (un petit lot par invariant), ce qui est un comportement juste à garder.

## Livraison
Branche `codex-anselme-coups` (depuis `integration`) : `docs/taches/rapport-codex-222-anselme-coups.md` (une page) et une ligne dans
`docs/etat-dev.md`. Commit et poussée ; si la poussée est bloquée, laisse le commit local et dis-le.
