# Tâche Codex 298 (refonte U-M inventaire) : le menu d'inventaire soumet le même geste qu'une commande

Lot d'interface de la refonte du MJ, après U-D (lot 293, fusionné). Lis `AGENTS.md` (« Contrat du MJ » : une action
choisie par clic ou menu n'est pas réinterprétée), `docs/plan-refonte-mj.md` (ligne U-M inventaire),
`docs/conception-valeur-llm.md` (section 2, ligne « Poser, toucher, écouter, remettre, actions d'inventaire ») et le
rapport `docs/taches/rapport-codex-293-ud-descripteur.md` (`commandes.DescripteurPublic`, `Moteur.preparer`).

## Le constat
Le menu au clic de la page agit sur la carte : objets, portes, marche, regard. Ce que porte Corvus n'y a aucun geste :
poser, remettre à quelqu'un, manger, allumer ou éteindre une source portée, prendre une part d'un lot. Pour ces gestes
courants, le joueur doit taper une phrase, qui peut partir au modèle.

## L'invariant
**Un geste choisi dans le menu d'inventaire transmet un descripteur public (U-D) qui donne au moteur le même plan
que la commande équivalente : même cible, même quantité, même destinataire, sans analyse de texte ni appel au
modèle.** Le menu ne propose que des biens portés, connus du joueur, sous leurs références publiques. Un destinataire
de remise est une personne perçue et à portée, sans destinataire inventé. Le moteur tranche à la réception : refus
public (G2) ou résultat rendu (G4). Le menu annonce un verbe, pas une faisabilité.

Ce que le lot ne fait pas : pas d'outils ni de destinations (U-M outils), pas de corps ni de violence (U-M corps), pas
de social (après G15 à G18), pas de terminal (U-T). Aucun geste nouveau pour le moteur : seulement ceux qu'une
commande permet déjà.

## Fichiers attendus
`donjon/web/page.html` (panneau ou menu d'inventaire), `donjon/web/pont.py`, `donjon/commandes.py` seulement si le
descripteur manque d'un paramètre public (quantité, destinataire). Le descripteur reste indépendant du web. Ne touche
pas au MJ (`mj.py`, `compilateur.py`, `paroles.py`, `sources.py`) ni à `jeu.py`/`tui.py` (un lot U-T y travaille).

## Vérification
- Pour chaque geste d'inventaire, vérifie :
  - la parité avec la commande textuelle : même plan, même effet, même texte rendu ;
  - deux biens de même nom : le geste porte sur celui qu'on a choisi ;
  - la quantité d'un lot ;
  - la remise à une personne perçue, et le refus si elle est partie ;
  - zéro appel au modèle ;
  - monde, scène, fiche et carte identiques après recharge.
- Tests du clic (Node) verts ; ce que reçoit la page ne contient ni précondition ni entité non perçue.
- Mesure : saisies évitées, clics jusqu'à l'effet.
- Pas de Luna (aucun chemin du modèle), pas de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots et une suite complète y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-um-inventaire` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ; si
  la poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-298-um-inventaire.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\um-inventaire-298\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
