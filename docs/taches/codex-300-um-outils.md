# Tâche Codex 300 (refonte U-M outils) : outil et destination d'un geste se choisissent parmi les ressources connues

Lot d'interface de la refonte du MJ, après U-D et U-M inventaire (lots 293 et 298, fusionnés). Lis `AGENTS.md`
(« Contrat du MJ »), `docs/plan-refonte-mj.md` (ligne U-M outils), `docs/conception-valeur-llm.md` (section 2, ligne
« Outil/destination/combustible pour un geste ») et les rapports `rapport-codex-293-ud-descripteur.md` et
`rapport-codex-298-um-inventaire.md`.

## Le constat
Le menu au clic propose un verbe sans ses paramètres. Par exemple, « Crocheter » ne choisit pas l'outil,
« Déverrouiller » pas la clé, et il n'y a ni « Forcer avec », ni « Mettre dans » (contenant, foyer à alimenter). Pour
choisir un outil ou une destination, le joueur doit taper une phrase, qui peut partir au modèle.

## L'invariant
**Le menu propose, pour un geste qui en a besoin, l'outil ou la destination parmi les seules ressources connues de
Corvus (portées ou à portée, perçues), sous leurs références publiques ; le descripteur U-D transmis donne au moteur le
même plan que la commande équivalente, sans analyse de texte ni appel au modèle.** Le menu ne sait pas si l'outil
convient. Il propose ce que Corvus a, et le moteur tranche : refus public (G2) ou résultat rendu (G4). Il ne lit aucun
inventaire privé d'un PNJ et ne reçoit aucune précondition. Une propriété inconnue d'un objet (sa capacité à couper,
par exemple) n'est pas inventée pour activer un bouton : elle reste une admission distincte, hors de ce lot.

Gestes couverts : ceux qu'une commande accepte déjà avec un outil ou une destination (crocheter, déverrouiller,
forcer ou frapper un objet, mettre dans un contenant, alimenter un foyer ou une source). Pas de corps ni de violence
contre une personne (U-M corps), pas de passage (U-M passage), pas de fabrication (U-M fabrication), pas de social.

## Fichiers attendus
`donjon/web/page.html`, `donjon/web/pont.py` (projection publique des ressources), `donjon/commandes.py` seulement si
le descripteur manque d'un paramètre public. Ne touche pas au MJ (`mj.py`, `compilateur.py`, `paroles.py`,
`sources.py`) ni à `jeu.py`/`tui.py` (un lot U-T y travaille).

## Vérification
- Pour chaque geste couvert, vérifie :
  - la parité avec la commande textuelle (même plan, même effet, même texte rendu) ;
  - deux outils de même nom ;
  - un outil absent ou parti à la réception (refus public, aucun substitut) ;
  - une destination fermée ou pleine (refus public) ;
  - zéro appel au modèle ;
  - monde, scène, fiche et carte identiques après recharge.
- Ce que reçoit la page ne contient ni précondition, ni entité non perçue, ni bien privé d'un PNJ. Tests du clic (Node)
  verts.
- Mesure : saisies évitées, clics jusqu'à l'effet.
- Pas de Luna (aucun chemin du modèle), pas de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots et une suite complète y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-um-outils` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ; si la
  poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-300-um-outils.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\um-outils-300\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
