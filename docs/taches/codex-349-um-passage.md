# Tâche Codex 349 (refonte U-M passage) : les passages qualifiés se choisissent au menu

Lot d'interface de la refonte du MJ, après U-D, U-M outils, U-C, G6, G7 et U-M corps (lot 344, fusionné). Lis
`AGENTS.md` (« Contrat du MJ »), `docs/etat-dev.md` (court), `docs/plan-refonte-mj.md` (ligne U-M passage),
`docs/conception-valeur-llm.md` (section 2) et les rapports 293 (U-D), 325 (U-C) et 344 (U-M corps), dont tu reprends
la structure. Pour un lot ancien (sous-obstacle, franchissement), cherche dans `docs/historique-lots.md` par mot-clé,
sans le lire en entier.

## Le constat
Passer sous un obstacle, l'enjamber ou l'escalader (`passer_obstacle`, dessous/dessus, lot `codex-sous-obstacle`), ou
franchir avec une échelle ou une perche, s'écrit en texte libre, qui part au modèle, alors que le moteur connaît les
passages déjà qualifiés (forme établie, dimensions, gabarit, charge) et sait les exécuter.

## L'invariant
**Le menu propose, sur un obstacle ou un passage perçu, les seuls franchissements dont la forme est déjà établie dans
l'état connu de Corvus ; le descripteur U-D transmis donne au moteur le même plan que la commande équivalente, sans
analyse de texte ni appel au modèle.** Aucune dimension, forme ou appui n'est inventé par l'interface : une forme
inconnue n'offre pas de franchissement au menu (la qualification reste au chemin libre, G13). Le menu ne juge pas la
faisabilité : le moteur tranche (refus public G2, gabarit, charge, jet d'escalade) ou rend le résultat (G4, G7).
Un franchissement lourd au sens de U-C (selon ses effets typés) passe par le consentement ; un clic n'est pas
réinterprété.

## Fichiers attendus
`donjon/web/page.html`, `donjon/web/pont.py`, le catalogue commun `donjon/gestes_publics.py`, le descripteur U-D,
`donjon/commandes.py` seulement si un paramètre public manque. Ne touche ni au MJ (`mj.py`, `compilateur.py`,
`paroles.py`, `narration.py`, `sources.py`), ni à `jeu.py`/`tui.py` (U-T passage viendra ensuite), ni aux règles de
`obstacles.py`/`franchissement.py`.

## Vérification
- Pour chaque franchissement couvert : parité avec la commande textuelle (même plan, même effet, même texte rendu) ;
  passage trop bas, trop haut, encombré (refus public du moteur) ; forme inconnue (aucune proposition au menu) ;
  consentement si lourd, annulation sans effet ; zéro appel au modèle ; monde, scène, fiche et carte identiques après
  recharge.
- Scènes réelles : les bancs `sous-obstacle-*` (Relais, auberge, trop bas, encombré, inconnu) ; un autre cas de même
  nature dans un autre scénario.
- Ce que reçoit la page ne contient ni précondition, ni dimension non établie, ni entité non perçue. Tests du clic
  (Node) verts.
- Mesure : saisies évitées, clics jusqu'à l'effet.
- Pas de Luna (aucun chemin du modèle), pas de suite complète.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Lots en cours : 342 (attribution du groupe 1),
345 (G16, `paroles.py`/`narration.py`), 348 (E1, `agendas.py`) ; signale tout fichier commun.

## Livraison
- Branche `codex-um-passage`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-349-um-passage.md`, entrée « non fusionnée » de 8 lignes au plus dans
  `docs/etat-dev.md`, section « Lots non fusionnés ».
- Bruts dans `C:\Users\msics\donjon\artifacts\um-passage-349\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
