# Tâche Codex 305 (refonte U-M fabrication) : assembler et découper se choisissent au menu

Lot d'interface de la refonte du MJ, après U-D, U-M inventaire et U-M outils (lots 293, 298 et 300, fusionnés). Lis
`AGENTS.md` (« Contrat du MJ »), `docs/plan-refonte-mj.md` (ligne U-M fabrication), `docs/plan-fabrication.md` et le
rapport `rapport-codex-300-um-outils.md`.

## Le constat
La fabrication passe par les actions `assembler` (usage, pièces par rôle, lien, outil) et `decouper` (barre ou lien,
longueur, outil). Elle n'est accessible que par une phrase libre, que Luna doit composer. C'est l'une des saisies les plus
coûteuses en appels et en refus du banc atelier.

## L'invariant
**Le formulaire propose les usages que le moteur sait assembler, les pièces candidates par rôle et l'outil parmi les
seules ressources connues de Corvus (portées ou à portée, perçues), sous leurs références publiques. Le descripteur U-D
donne au moteur le même plan que la commande équivalente, sans analyse de texte ni appel au modèle.** Le formulaire ne
juge pas si une pièce convient : le moteur tranche, par un refus public ou un résultat rendu. Une propriété physique
inconnue d'une pièce (forme, dimensions non établies) n'est pas inventée pour activer un choix. Elle reste une admission
distincte, et le formulaire dit qu'elle manque, sans proposer de valeur. Les droits sur les biens d'autrui sont
conservés, comme pour toute autre commande.

## Fichiers attendus
- `donjon/web/page.html`, `donjon/web/pont.py` (projection publique) et le catalogue `donjon/gestes_publics.py` ;
- `donjon/commandes.py`, seulement si le descripteur manque d'un paramètre public.

Ne touche pas :

- au MJ (`mj.py`, `compilateur.py`, `paroles.py`, `sources.py`) ;
- à `jeu.py` ni `tui.py` (un lot U-T y travaille) ;
- aux règles de l'atelier (`atelier.py`, `matiere.py`), sauf une lecture publique qui manquerait.

## Vérification
- Atelier, échelle de perches et ficelle coupée d'un mètre : parité avec la commande (même plan, même effet, même texte
  rendu).
- Cas limites :
  - pièce absente ou partie à la réception : refus public, sans substitut ;
  - pièce de forme inconnue : admission manquante dite ;
  - bien d'autrui : faute ou refus, comme la commande ;
  - deux pièces de même nom.
- Zéro appel au modèle ; monde, scène, fiche et carte identiques après recharge.
- Tests du clic (Node) verts.
- Mesures : saisies évitées et clics jusqu'à l'effet. Pas de Luna (aucun chemin du modèle), pas de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-um-fabrication`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur : la
  poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-305-um-fabrication.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\um-fabrication-305\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
