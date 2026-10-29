# Tâche Codex 307 (refonte U-T outils) : au terminal, l'outil et la destination d'un geste se choisissent comme sur la page

Lot d'interface, après U-M outils (lot 300) et U-T inventaire (lot 301), fusionnés. Lis `AGENTS.md` (« Contrat du MJ »),
`docs/plan-refonte-mj.md` (ligne U-T outils), ainsi que les rapports `rapport-codex-300-um-outils.md` et
`rapport-codex-301-ut-inventaire.md`.

## Le constat
La page propose l'outil ou la destination d'un geste (crocheter, déverrouiller, forcer ou frapper un objet, mettre dans,
alimenter) parmi les ressources connues de Corvus. La console et la TUI listent les gestes de carte et d'inventaire, mais
pas ce second choix : le joueur doit le taper.

## L'invariant
**Console et TUI proposent, par numéro, le même second choix d'outil ou de destination que la page, depuis la même
projection publique et le catalogue `donjon/gestes_publics.py`. Le choix transmet le même descripteur U-D, sans analyse
de texte ni appel au modèle.** Aucune entité non perçue ni bien privé d'un PNJ n'apparaît dans la liste. Une propriété
inconnue n'est pas inventée. Un choix périmé reçoit le refus public du moteur, jamais un substitut.

## Fichiers attendus
`jeu.py`, `donjon/tui.py`, et la projection commune si le terminal doit lire ce que lit la page, sans dupliquer la règle.
Ne touche pas au MJ, ni à `donjon/web/page.html`. Un lot de fabrication (305) touche aussi `gestes_publics.py` : avant de
livrer, fusionne `origin/integration` et réutilise le catalogue tel qu'il sera.

## Vérification
- Console et TUI, pour chaque geste à outil ou à destination :
  - la parité avec la page (même descripteur, même plan, même texte rendu) ;
  - deux outils homonymes ;
  - un outil parti à la réception (refus, sans substitut) ;
  - une destination fermée ;
  - un numéro inconnu ;
  - zéro appel au modèle ;
  - monde, scène, fiche et carte identiques après recharge.
- Tests TUI existants verts.
- Mesure : touches jusqu'à l'effet. Pas de Luna, pas de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-ut-outils`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur : la
  poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-307-ut-outils.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\ut-outils-307\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
