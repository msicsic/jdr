# Tâche Codex 100 : un tour ne finit jamais sur un message technique ni sur une intention abandonnée

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul, Luna en
4 exécutions au plus ; un lot de coût (`planification.py`) tourne en même temps. Ce lot touche le MJ (`mj.py`, `narration.py`,
`paroles.py`, `couverture_action.py`), pas `planification.py`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

## Le constat (vérification Luna du lot 99, intégration b0042c9)
Deux régressions par rapport à 882907c, aux deux passes (bruts : `C:\Users\msics\donjon\artifacts\verif-luna-b0042c9\`,
`constats.md`, `preuves-incidents.json`) :
- **N1**, `atelier` n°8, « à quoi ressemble le mur de l'atelier ? » → le joueur lit **« Faits narratifs invalides. Aucun ajout
  enregistré. »** Un appel ; `faits` contient des libellés internes en liste au lieu de faits structurés ; la forme invalide sort
  de la chaîne de correction au lieu d'être redemandée.
- **N3**, `soir-noir` n°1, « il y a quelqu'un ? » → **« Ta demande n'a pas été exécutée. Reformule-la. »** Trois appels :
  interprétation `qui`, puis revue de fidélité refusée (présence/identité), sans récupération ; 882907c disait la parole et
  recevait une réponse.

## L'invariant
**Un tour ne se termine jamais sur un message technique ni sur l'abandon d'une intention valable** : une proposition mal formée
(forme des faits, contenu typé) est un refus de forme corrigé à part, jamais affiché (contrat `refus.RefusDeForme`) ; après les
corrections permises, le joueur lit ce que le moteur peut établir (la parole dite avec ses mots exacts, la perception que le
moteur fait de ce qu'il vise), comme le repli existant, jamais « Reformule » pour une saisie qu'un des chemins communs sait
traiter. Trouve pourquoi ces deux chemins sortent de la chaîne commune (probablement des lots 89, 91, 95 ou 96 : dis lequel) et
remets-les dedans ; pas d'exception de saisie ni de mot-clé.

## Vérification
- Tests après rechargement avec MJ simulé reproduisant les deux réponses de Luna (faits en liste de libellés ; `qui` refusé par la
  fidélité) : le joueur lit une réponse de jeu, état inchangé ou parole enregistrée selon le cas ; un autre cas de même nature
  pour chacun ; un message technique n'atteint jamais la sortie (garde de test sur les textes affichés).
- Luna, **une passe** de `atelier`, `soir-noir`, `noms-dialogue`, `echanges` sur la branche (références du lot 99 en cache) :
  N1 et N3 ne reviennent pas, appels et secondes par tour.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` si le contrat change, `docs/etat-dev.md` (« Branche
`codex-sans-message-technique`, non fusionnée »). Rapport d'une demi-page : `docs/taches/rapport-codex-100-sans-message-technique.md`.
