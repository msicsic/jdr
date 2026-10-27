# Tâche Codex 188 (diagnostic) : appels répétés de Brune et alternances de Gorm

Deux alertes de la vérification d'intégration 174 (`docs/taches/rapport-codex-174-verif-integ.md`), jamais instruites :
**Brune, crue 1985, douze appels à Gorm entre 495 et 518 min, par paires dans la même minute** ; **Gorm, hameau 2024,
onze alternances de but, dont sept entre entretien et garde**. **Diagnostic seul : aucun code du jeu modifié**, sauf si la
cause tient en une correction évidente d'un seul invariant (dans ce cas, arrête-toi et pose la question avant de coder).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (180 b, 184 b) : **un seul processus
de calcul**, priorité réduite. **Bruts dans `C:\Users\msics\donjon\artifacts\appels-188\`, jamais dans le worktree.** Termine
par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, le rapport 174, puis les rapports 37, 60, 69 (appels, rendez-vous, indices de recherche) et 167 à 167 c, 175,
179 (garde, entretien). Code : `appel.py`, `deliberation.py` (choix, inertie, hystérésis), `pnj.heler`/`appeler`, `agendas.py`.

## Ce qu'il faut établir
1. **Reproduire** chaque alerte sur la base actuelle (`integration`), même scénario, graine, 12 h ; si l'une ne se reproduit
   plus, chercher le lot qui l'a fait disparaître (relire, pas bissecter longuement) et le dire.
2. **Pour Brune** : pourquoi deux appels dans la même minute (deux voies d'appel ? réveil à l'événement qui relance le même
   appel ? appel sans indice nouveau, contraire au lot 69 ?) ; ce que Brune croit de Gorm à chaque appel ; s'il existe un indice
   nouveau légitime entre deux appels.
3. **Pour Gorm** : ce qui fait basculer entre entretien et garde à chaque fois (seuils, inertie `INERTIE`/`REPRISE`, coût de
   garde `prix_gardes`, réveil d'agenda) ; s'il s'agit d'une boucle (même état, même décision inverse) ou d'arbitrages réels
   espacés.
4. Pour chacun : capture rechargeable juste avant le défaut, monde et rendu identiques après recharge, et **l'invariant général
   en cause** (pas une règle propre à Brune, Gorm ou la crue), avec la correction proposée et ce qu'elle risque.

## Livraison
Branche `codex-appels-alternances` : `docs/taches/rapport-codex-188-appels-alternances.md` (une page) et une entrée dans
`docs/etat-dev.md`. Commit et poussée ; si la poussée est bloquée, laisse le commit local et dis-le.
