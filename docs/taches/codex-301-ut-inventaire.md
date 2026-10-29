# Tâche Codex 301 (refonte U-T inventaire) : au terminal, les gestes d'inventaire se choisissent comme sur la page

Lot d'interface de la refonte du MJ, après U-M inventaire et U-T premier geste (lots 298 et 299, fusionnés). Lis
`AGENTS.md` (« Contrat du MJ »), `docs/plan-refonte-mj.md` (ligne U-T inventaire) et les rapports
`rapport-codex-298-um-inventaire.md` et `rapport-codex-299-ut-premier-geste.md`.

## Le constat
La page web propose les gestes d'inventaire (poser, remettre à une personne choisie, manger une portion,
allumer/éteindre, prélever une pièce d'un lot) par un descripteur public. Le terminal (console et TUI) liste depuis le
lot 299 les gestes de la carte, numérotés, mais pas ceux de l'inventaire. Le joueur doit les taper.

## L'invariant
**Console et TUI proposent les gestes d'inventaire dans la liste numérotée ; le choix transmet le même descripteur
public que le menu d'inventaire de la page (lot 298) : même bien, même quantité, même destinataire, sans analyse de
texte ni appel au modèle.** La liste vient de la même source que la page (`pont.inventaire_public`,
`destinataires_publics`, catalogue commun `donjon/gestes_publics.py`). Elle ne contient aucune identité privée ni
entité non perçue. Un second choix (destinataire, quantité) se fait par numéro, sans saisie libre. Un choix périmé
reçoit le refus public du moteur, jamais un autre bien ni un autre destinataire.

## Fichiers attendus
`jeu.py`, `donjon/tui.py`, `donjon/gestes_publics.py`, et la projection commune déplacée hors de `web/pont.py` si le
terminal doit la lire (sans dupliquer la règle). Ne touche pas au MJ (`mj.py`, `compilateur.py`, `paroles.py`,
`sources.py`) ni à `donjon/web/page.html` (un lot U-M y travaille).

## Vérification
- Console et TUI, pour chaque geste d'inventaire, vérifie :
  - la parité avec la page (même descripteur, même plan, même texte rendu) ;
  - deux biens de même nom ;
  - deux destinataires homonymes ;
  - la quantité d'un lot ;
  - un destinataire parti ;
  - un numéro inconnu ;
  - zéro appel au modèle ;
  - monde, scène, fiche et carte identiques après recharge.
- Les tests TUI existants restent verts.
- Mesure : touches jusqu'à l'effet.
- Pas de Luna, pas de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-ut-inventaire` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur : la
  poussée est autorisée) ; si elle échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-301-ut-inventaire.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\ut-inventaire-301\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
