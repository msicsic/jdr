# Tâche Codex 340 : A5.8, l'ascendant évolue par l'issue perçue d'un mandat

Lot 8 de la [conception d'A5](rapport-codex-245-conception-a5.md). Lis `AGENTS.md`, `docs/etat-dev.md`, puis les
rapports 248 (sixième axe, ascendant neutre), 256 (jugement du mandat), 283 (compte rendu) et 297 (réaffectation).

## Constat
L'ascendant (ce que B reconnaît d'autorité à A, `relations.autorite_reconnue`) existe, s'estompe vers son lien
initial et pèse dans le jugement d'un mandat (bonus plafonné). Il ne change jamais par l'expérience : un mandat
mené à bien, un échec, ou un ordre abusif ne modifient pas ce qu'un PNJ reconnaît à celui qui l'a mandaté.

## L'invariant
**L'ascendant d'un mandant aux yeux d'un mandataire, et aux yeux des témoins, évolue une fois par issue perçue :
mandat abouti, échec, ou abus.** Ces issues sont définies par des prédicats du moteur, déjà sauvegardés :
- le compte rendu (283) ou le constat de la fin d'agenda ;
- l'abus : un mandat qui exposait le mandataire à un péril cru, ou un mandat contraire à ses valeurs, au prix
  commun de la faute.

L'épreuve passe par la table commune des relations (`relations.EPREUVES`), avec son hystérésis et son
estompement. Elle n'est appliquée qu'une fois par issue, même après recharge. Règles d'application :
- un témoin ignorant de l'issue ne change rien ;
- un compte rendu incertain (une parole, non un constat) pèse comme un ouï-dire, distinct d'un constat propre ;
- aucune réputation publique ni sanction : c'est A7, hors lot.

## Contraintes de conception
- `relations.py` et `agendas.py` ; extensions possibles : souvenirs dans `esprits.py`, transport dans `social.py`.
  Aucune nouvelle règle de violence, aucun cas propre à Gorm, Aubin ou au hameau.
- Toute lecture nouvelle de la recherche entre dans `_entrees`.

## Vérification
- Une scène Gorm → Aubin : mandat abouti, puis échec, puis abus. Un autre cas de même nature dans une autre
  relation ou un autre scénario. Cas négatifs : témoin ignorant, compte rendu incertain distinct du constat, pas de
  double gain après recharge. Contrôle après rechargement du monde, du rendu et de la scène, avec le même laps
  entier ou découpé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Banc rapide 4 h × cinq scénarios × quatre graines, références lues du cache : aucune hausse des suspects 219 par
  nuit, zéro plantage ou usurpation. Si aucun mandat n'aboutit naturellement dans les nuits, dis-le : la preuve
  passe par les scènes.
- Ni Luna ni suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Banc détaché, avec un fichier de fin écrit en
dernier. Recouvrement possible avec les lots 336 (occasion de protection) et 337 (fin de garde par ouï-dire), en
cours : signale tout fichier commun.

## Livraison
- Branche `codex-ascendant-evolue`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-340-ascendant-evolue.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\ascendant-340\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
