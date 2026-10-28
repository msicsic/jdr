# Tâche Codex 263 (diagnostic) : le service payé de Brune s'éteint à 41 min (hameau 1985)

La vérification d'intégration 241 (`docs/taches/rapport-codex-241-verif-integ.md`, fusionnée, « Petits lots à
instruire » ; bruts `C:\Users\msics\donjon\artifacts\verif-integ-c870c8b\`, dont `analyse/suivis241.json`) relève un
cas nouveau du compteur 227 : **hameau 1985, Ilse paie Brune à 1 min pour la torche allumée, réussite à `2436`,
extinction à 41 min (`24600`)** ; avant le geste, Ilse et la torche sont crues en crypte, `parti=false`. Sur `4306c14`,
le même service était perdu physiquement à 64 min, sans extinction. Invariant à vérifier : **la clôture d'un service
payé et la réutilisation de son résultat partagent la même preuve de départ du bénéficiaire** (lots 224, 227, 238 :
`biens.services_proteges`, `services_rendus.lieu_beneficiaire`). La sonde 227 garde le paiement mais pas l'historique
des clôtures, et son critère n'intègre pas l'ancrage du 238 : la violation n'est pas certifiée.

**Diagnostic seul : aucun code du jeu modifié.**

## Ce que le rapport doit établir
1. **Reproduire** sur l'intégration actuelle (hameau 1985, départ tiré, joueur et durée de l'audit 241) ; sinon sur
   `c870c8b` (worktree détaché). Capturer juste avant l'extinction ; monde et rendu identiques après rechargement.
2. **Qui éteint, par quel geste et pourquoi** : la trace du service (création, clôture éventuelle et sa cause), le lieu
   cru d'Ilse au constat et au moment du geste, la décision qui mène à l'extinction (but, plan, `menager_flamme`).
3. **Verdict** : extinction légitime (Ilse crue partie selon une preuve valable, ou service clos pour une cause juste) ou
   défaut (clôture sans preuve de départ, ancrage 238 ignoré, résultat défait par le prestataire) ; dans ce cas la règle
   commune en cause en une phrase, sans exception propre à Brune, à la torche ou au hameau.

Lot de 30 à 45 minutes. **Poste : le PC fixe**, un processus à priorité réduite. Pas de Luna, pas de suite complète, pas
de banc comparatif.

## Livraison
- Branche `codex-torche-eteinte` : seulement `docs/taches/rapport-codex-263-torche-eteinte.md` (une page) et une entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\torche-263\`. Commite ; pousse si
  tu peux, sinon laisse le commit local et dis-le. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou
  `QUESTION : …`.
