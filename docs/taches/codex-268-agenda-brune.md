# Tâche Codex 268 (diagnostic) : l'agenda de Brune s'active et s'endort huit à neuf fois (hameau 2024)

Deux lots fusionnés relèvent la même alerte, jamais instruite :
- **205** (`docs/taches/rapport-codex-205-evacuation-juge.md`, « Limites avant fusion ») : hameau 2024, huit
  activations/sommeils de l'agenda `a1` de Brune, deux alertes de répétition ;
- **218** (`docs/taches/rapport-codex-218-restauration-charges.md`) : même nuit, neuf activations et neuf sommeils.
Bruts : `C:\Users\msics\donjon\artifacts\evacuation-205\`, `...\charges-218\`.

Invariant en jeu (lot 213, arbitrage utilisateur) : **un agenda sans plan admissible au coût passe en sommeil et
libère son palier ; il ne se réveille que sur une croyance ou un moyen nouveaux, jamais par le délai seul.** Huit
réveils peuvent être autant d'entrées nouvelles réelles (eau qui monte, personne revue) ou un réveil sans entrée.

**Diagnostic seul : aucun code du jeu modifié.**

## Ce que le rapport doit établir
1. **Reproduire** sur l'intégration actuelle (`crue_hameau`, graine 2024, départ tiré, joueur passif, 4 h comme les
   bancs des lots) ; si l'alerte a disparu, dire depuis quand en rejouant la base du 218 (`881db69`, worktree détaché)
   et s'arrêter là. Capturer avant deux réveils au moins ; monde et rendu identiques après rechargement.
2. **Pour chaque réveil** : la nature et le but de l'agenda, la cause du sommeil précédent, et l'entrée qui autorise le
   réveil (croyance changée, moyen nouveau, palier) ou son absence. Tableau compact, une ligne par cycle.
3. **Verdict** : cycles justifiés (dire si le compteur 219 devrait les reconnaître), ou défaut (la règle commune en cause
   en une phrase, sans exception propre à Brune, à son agenda ou au hameau) et le petit lot de correction proposé.

Lot de 30 à 45 minutes. **Poste : le laptop** (l'utilisateur y travaille), un processus à priorité réduite, une nuit à
la fois. Pas de Luna, pas de suite complète, pas de banc comparatif.

## Livraison
- Branche `codex-agenda-brune` : seulement `docs/taches/rapport-codex-268-agenda-brune.md` (une page) et une entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\agenda-268\`. Commite ; pousse
  si tu peux, sinon laisse le commit local et dis-le. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
  ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
