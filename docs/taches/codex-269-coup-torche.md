# Tâche Codex 269 (diagnostic) : Aubin assomme Gorm pour prendre la torche (hameau 1985, 652)

La vérification d'intégration 241 (`docs/taches/rapport-codex-241-verif-integ.md`, l. 47-49 ; bruts
`C:\Users\msics\donjon\artifacts\verif-integ-c870c8b\`) relève le seul coup porté des 49 nuits : **hameau 1985 à
652 min, Aubin assomme Gorm puis prend la torche ; Gorm est inconscient au relevé 655.** Absent de la même nuit sur
`4306c14`. Un coup n'est pas en soi une violation : le recours « assommer pour prendre » (lot 4b) compare son prix
de violence (douceur, peur d'être vu, témoins crus) aux autres moyens.

Invariant en jeu : **la violence n'est choisie que si aucun moyen moins coûteux n'est admissible selon les croyances de
l'auteur** (demander, acheter, proposer faute de mieux, attendre), au prix commun de la faute et de la violence
(`combat.prix_violence`, `planification.prix_gardes`, refus retenus).

**Diagnostic seul : aucun code du jeu modifié.**

## Ce que le rapport doit établir
1. **Reproduire** sur l'intégration actuelle (hameau 1985, départ tiré, joueur et durée de l'audit 241) ; sinon sur
   `c870c8b` (worktree détaché). Si le coup n'a plus lieu, dire ce qui a changé (premier écart de chronique) et
   s'arrêter là. Capturer avant la décision d'Aubin ; monde et rendu identiques après rechargement.
2. **Le choix d'Aubin** : son but et son palier (besoin, agenda, désespoir), les recours essayés avant et leur issue
   (demandes, achats, propositions, refus retenus), le coût de chaque plan candidat au moment du choix et ce qu'il
   croit de Gorm (regard, témoins, force). Rejouer la recherche sur la capture pour donner ces coûts.
3. **Verdict** : violence justifiée par le contrat (dire quel moyen moins coûteux manquait et pourquoi), ou défaut (la
   règle commune en cause en une phrase, sans exception propre à Aubin, à Gorm, à la torche ou au hameau) et le petit
   lot de correction proposé.

Lot de 30 à 45 minutes. **Poste : le laptop** (l'utilisateur y travaille), un processus à priorité réduite, une nuit à
la fois. Pas de Luna, pas de suite complète, pas de banc comparatif.

## Livraison
- Branche `codex-coup-torche` : seulement `docs/taches/rapport-codex-269-coup-torche.md` (une page) et une entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\coup-269\`. Commite ; pousse si
  tu peux, sinon laisse le commit local et dis-le. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
