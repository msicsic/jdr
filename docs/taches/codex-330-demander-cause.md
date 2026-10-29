# Tâche Codex 330 : 3d, demander à un proche ce qui l'effraie

Suite de la sous-étape 3d (l'empathie) du [plan des relations](../plan-relations.md), après les lots 53 (peur
transmise), 197 (secours sur faim et froid perçus), 266 (rester près d'un proche en détresse) et 221 (question de
localisation à un tiers). Lis `AGENTS.md`, `docs/etat-dev.md`, puis les rapports 53, 221 et 266.

## Constat
Un PNJ qui perçoit la détresse d'un proche (signe de peur, fuite) sans en percevoir la cause reste près de lui (266)
et s'inquiète (53), mais ne lui demande jamais ce qui se passe. Il ne peut donc pas apprendre le danger (agresseur,
eau, voix inconnue) que le proche connaît, ni réagir à ce danger.

## L'invariant
**Un PNJ qui perçoit la détresse d'un proche, sans en connaître lui-même la cause, peut lui demander ce qui
l'inquiète. Cette demande passe par la parole commune. La réponse vient des seules croyances datées du proche
(auteur d'une violence crue, menace d'eau crue, bruit inconnu retenu). L'auditeur l'apprend comme un ouï-dire
pondéré par sa confiance et peut ensuite y réagir par les recours existants (fuir, prévenir, secourir).** Il
n'y a ni lecture de la position ou de la cause réelle, ni question répétée sans entrée nouvelle. Un proche
inconscient, méfiant ou sans cause crue ne répond rien d'utile. Une réponse fausse, parce que la croyance du proche
est fausse, est transmise telle quelle.

## Contraintes de conception
- Même voie que la question de localisation 221 : contenu typé commun, réponse retenue hors des quarante souvenirs,
  sans réessai par le seul délai.
- Si le contenu typé du joueur exige de toucher au schéma du MJ (`paroles.py`, `CHAMPS_CONTENU`), limite ce lot aux
  PNJ et dis-le ; la voie du joueur sera un lot suivant.
- Aucun cas propre à un personnage, un lieu ou un scénario.
- Recouvrement probable avec le lot 326 (G17, `paroles.py`, `dialogues.py`, en cours) : signale tout fichier commun.

## Vérification
- Une scène réelle de crue ou du Relais (un proche fuit un agresseur ou l'eau, l'autre demande puis réagit), et un
  autre cas de même nature dans un autre scénario. Cas négatifs : cause déjà connue, proche inconscient, méfiance,
  croyance fausse transmise. Contrôle après rechargement du monde, du rendu et de la scène, avec le même laps entier
  ou découpé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Banc rapide : 4 h × cinq scénarios × quatre graines, références lues du cache. Aucune hausse des suspects 219 par
  nuit, zéro plantage ou usurpation. Mesure du nombre de demandes, de réponses utiles et de réactions qui suivent.
- Ni Luna ni suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Banc détaché, avec un fichier de fin écrit en
dernier.

## Livraison
- Branche `codex-demander-cause`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-330-demander-cause.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\cause-330\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
