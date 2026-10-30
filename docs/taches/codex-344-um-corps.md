# Tâche Codex 344 (refonte U-M corps) : les gestes de corps et de violence se choisissent au menu

Lot d'interface de la refonte du MJ, après U-D, U-M outils et U-C (lots 293, 300 et 325, fusionnés). Lis `AGENTS.md`
(« Contrat du MJ »), `docs/plan-refonte-mj.md` (ligne U-M corps), `docs/conception-valeur-llm.md` (section 2) et les
rapports 293, 300 et 325.

## Le constat
Le menu au clic d'une personne ne propose que l'examen et la parole. Frapper, assommer, saisir, ligoter, délier,
traîner, pousser, se dégager, fuir, riposter, se rendre, tuer s'écrivent en texte libre, qui part au modèle. Ces gestes
existent tous dans le moteur, avec leurs méthodes (mains nues ou arme, assommer, par surprise) et leur risque.

## L'invariant
**Le menu propose, sur une personne perçue, les gestes de corps que le moteur sait exécuter, avec leur méthode et leur
arme choisies parmi les seules ressources connues de Corvus ; le descripteur U-D transmis donne au moteur le même plan
que la commande équivalente, sans analyse de texte ni appel au modèle.** Le menu ne juge pas si le geste est possible :
le moteur tranche, par un refus public (G2) ou un résultat rendu (G4). Un geste lourd ou irréversible (frapper,
assommer, ligoter, tuer, d'après ses effets typés) passe par le consentement U-C : aperçu du plan entier, puis
confirmation revalidée ; un clic n'est pas réinterprété.

Les réactions à une agression (fuir, riposter, se rendre, se dégager) apparaissent seulement quand le moteur établit un
danger perçu (`defense.dangers_vus`). Le menu ne reçoit ni précondition, ni entité non perçue, ni force ou PV cachés.

## Fichiers attendus
`donjon/web/page.html`, `donjon/web/pont.py`, le catalogue commun `donjon/gestes_publics.py`, `donjon/commandes.py`
seulement si le descripteur manque d'un paramètre public. Ne touche pas au MJ (`mj.py`, `compilateur.py`, `paroles.py`,
`sources.py`) ni à `jeu.py`/`tui.py` (U-T corps viendra ensuite), ni aux règles de `force.py`, `combat.py`, `tenir.py`.

## Vérification
- Pour chaque geste couvert : parité avec la commande textuelle (même plan, même effet, même texte rendu) ; deux
  personnes de même désignation ; cible partie ou inconsciente à la réception (refus public, aucun substitut) ; arme
  absente ; consentement demandé pour les gestes lourds, annulation sans effet ; zéro appel au modèle ; monde, scène,
  fiche et carte identiques après recharge.
- Scènes réelles : `force-4b-frapper`, `force-4b-assommer`, `force-4c-fuir`, une ligature (4d) ; un autre cas de même
  nature dans un autre scénario.
- Ce que reçoit la page ne contient ni précondition, ni entité non perçue, ni état caché. Tests du clic (Node) verts.
- Mesure : saisies évitées, clics jusqu'à l'effet (consentement compris).
- Pas de Luna (aucun chemin du modèle), pas de suite complète.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Signale tout fichier commun avec les lots en cours
(338 recours, 341 mandat du joueur, 342 attribution du groupe 1, 343 G7).

## Livraison
- Branche `codex-um-corps`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-344-um-corps.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\um-corps-344\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
