# Tâche Codex 369 : U-T social information, l'acte d'information au terminal

Lot U-T social information de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md). Le formulaire web de
l'information existe (lot 354, U-M social information) ; le terminal n'y a pas encore accès. Lis `AGENTS.md`,
`docs/etat-dev.md` (court) et les rapports 354 (U-M social information), 345 (G16), 353 (U-T corps et passage), 325 (U-C).

## L'invariant
**Console et TUI transmettent le même acte d'information que le formulaire web (demander où est quelqu'un, demander qui
parle, dire où est une chose, demander si l'autre a une ressource), avec les seuls paramètres publics : destinataire
perçu ou voix connue, sujet parmi ce que Corvus connaît ; le choix envoie le même descripteur U-D et passe par la même
entrée commune de parole typée que le web (raccord de `jeu.py` et adresse structurée du lot 354), sans analyse de texte
ni modèle.** La réponse est celle du moteur (G16). Limite conservée : « où est » d'un objet reste indisponible (décision
du 354, règle joueur inchangée).

## Vérification
- Parité avec le web et la saisie typée : mêmes contenus, même réponse, mêmes croyances apprises, mêmes refus (voix qui
  se nomme, croyance fausse, méfiance, destinataire parti) ; zéro appel au modèle ; monde, paroles, scène et fiche après
  recharge ; mesure des touches jusqu'à la réponse.
- Tests ciblés, dont les tests TUI existants inchangés et ceux du lot 354. Pas de Luna, de banc ni de suite complète.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `jeu.py`, `donjon/tui.py`, `donjon/dialogues.py` et le descripteur U-D
seulement si un paramètre public manque. Lots en cours : 365 (catalogue des choix, laptop) touche probablement
`paroles.py`/catalogue ; signale tout recouvrement. Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-ut-social-information`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-369-ut-social-information.md`, entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\ut-social-information-369\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
