# Tâche Codex 328 : G6, les repères de position

Lot G6 de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md), après G5 (lot 323, branche
`codex-g5-perception`, livrée et en attente de fusion). **Base : la branche `codex-g5-perception`**, pas `integration`.
Lis `AGENTS.md` (contrat du MJ, « Mécanique » : positions et distances viennent d'un rendu déterministe du moteur),
`docs/conception-refonte-mj.md` (ligne G6), les rapports 61 (orientation), 171 (mesures résolues) et 323 (G5).

## L'invariant
**Une phrase de position (où se trouve un objet ou une personne, à quelle distance, de quel côté) vient du repère public
courant ou mémorisé de Corvus, rendu par le moteur sans réinterprétation : orientation relative au regard actuel, distance
en mètres, souvenir présenté comme passé.** Aucun repère inventé, aucune position privée divulguée, aucune relance de
position. L'audit de position se retire dans ce lot pour ces seules réponses moteur, la garantie étant fournie ; la prose
libre qui mentionne une position garde ses contrôles actuels.

## Vérification
- Cas 171 atelier et Aubin à 1 m, une autre orientation après rotation, et un souvenir de position : texte, scène et carte
  identiques après recharge ; un faux repère est impossible (test), MJ simulé sans réseau.
- Luna : **une passe** de `atelier` et `noms-dialogue`, référence lue du cache : zéro relance de position, noms et mémoire
  préservés. Si la revue automatique bloque Luna, laisse la commande exacte dans
  `C:\Users\msics\donjon\artifacts\g6-328\luna-a-jouer.txt`.
- Tests ciblés des fichiers touchés ; pas de suite complète ni de banc PNJ.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Recouvrements possibles avec 326 et 327 : signale-les.

## Livraison
- Branche `codex-g6-reperes`, base `origin/codex-g5-perception`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-328-g6-reperes.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g6-328\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
