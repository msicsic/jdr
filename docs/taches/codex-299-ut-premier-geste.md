# Tâche Codex 299 (refonte U-T) : au terminal, un geste choisi dans une liste numérotée garde son identité

Lot d'interface de la refonte du MJ, après U-D (lot 293, fusionné). Lis `AGENTS.md` (« Contrat du MJ »),
`docs/plan-refonte-mj.md` (ligne U-T premier geste), `docs/conception-valeur-llm.md` (fin de la section 2, ligne U-T)
et le rapport `docs/taches/rapport-codex-293-ud-descripteur.md`.

## Le constat
La page web passe désormais un geste choisi au moteur par un descripteur public (U-D) : zéro analyse de texte, zéro
appel au modèle. Au terminal (console et TUI), le joueur tape encore ses gestes, et une phrase non reconnue peut partir
au modèle. Le terminal a beaucoup de commandes, mais le joueur doit les connaître et nommer leurs cibles.

## L'invariant
**Console et TUI proposent les gestes publics de la scène dans une liste numérotée ; le choix transmet le même
descripteur public que le web (U-D) : mêmes références, même plan, sans analyse de texte ni appel au modèle.** La
liste vient de la même source que le menu web (scène perçue, gestes offerts) et ne contient aucune identité privée ni
entité non perçue. Deux cibles de même nom sont distinguées dans la liste, et le choix porte sur la bonne. Un choix
périmé reçoit le refus public du moteur, jamais une autre cible.

Premier geste seulement : les gestes que le menu web propose aujourd'hui sur la carte (objets, portes). Pas
d'inventaire, d'outils, de corps ni de social : ils viendront avec leurs familles. La saisie libre reste disponible.

## Fichiers attendus
`jeu.py`, `donjon/tui.py`, une source commune de la liste des gestes, partagée avec la page si elle n'existe pas encore
côté Python. Ne touche pas au MJ (`mj.py`, `compilateur.py`, `paroles.py`, `sources.py`) ni à `donjon/web/page.html`
(un lot U-M y travaille).

## Vérification
- Console et TUI, pour chaque geste de la liste, vérifie :
  - la parité avec le web : même descripteur, même plan, même texte rendu ;
  - deux cibles de même nom ;
  - un numéro inconnu ou ambigu ;
  - un choix périmé ;
  - zéro appel au modèle ;
  - monde, scène et carte identiques après recharge.
- Tests TUI existants verts (attente d'un état, pas de temporisation fragile).
- Mesure : touches jusqu'à l'effet.
- Pas de Luna, pas de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots et une suite complète y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-ut-premier-geste` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ;
  si la poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-299-ut-premier-geste.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\ut-299\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
