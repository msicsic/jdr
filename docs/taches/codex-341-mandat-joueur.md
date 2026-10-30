# Tâche Codex 341 : A5.9, le joueur mandant et mandaté

Lot 9 de la [conception d'A5](rapport-codex-245-conception-a5.md). Lis `AGENTS.md` (contrat du MJ du
2026-10-29) et `docs/etat-dev.md`. Lis aussi les rapports 252 (filiation), 256 (jugement du mandat), 283 (compte
rendu), 297 (réaffectation) et 340 (évolution de l'ascendant), et le [plan de refonte du MJ](../plan-refonte-mj.md)
(G15/G17, actes de parole typés).

## Constat
Entre PNJ, un mandat se propose, se juge, s'accepte avec filiation, se suit, se rend compte et se réaffecte. Le
joueur n'a aucune voie typée pour cela :
- il ne peut confier une charge (amener quelqu'un, informer quelqu'un) à un PNJ, qui la jugerait par le même jet ;
- un PNJ ne peut lui confier une charge qu'il accepterait ou refuserait.

## L'invariant
**Mandater ou recevoir un mandat, côté joueur, passe par le même contrat qu'entre PNJ.**
- **Corvus mandant.** Un contenu de parole typé (charge `amener`/`informer`, destinataire, cible) est jugé par
  `echanges.confier` et le jugement commun : autorité perçue, dette, refus d'accueil. Accepté, il ouvre chez le
  PNJ un agenda d'origine `mandat` dont le parent est une charge de Corvus. Le PNJ en rend compte par la voie du
  lot 283.
- **Corvus mandaté.** Un PNJ qui confie une charge à Corvus le fait par une parole typée que le joueur reçoit. Une
  mission acceptée est enregistrée dans les comptes et la fiche du joueur, sans exécution forcée. Le mandant suit,
  réaffecte et voit son ascendant évoluer par les mêmes règles que pour un PNJ.

Une voix inconnue ou prétendue garde ses règles (pas d'identité inventée). Aucun agenda secret ne fuit au MJ.
Les répliques dont le moteur fixe le contenu sont formulées par le moteur (contrat du MJ).

## Contraintes de conception
- `paroles.py`, `agendas.py`, `echanges.py` ; extensions possibles : schéma et contexte de `mj.py`, `rendu.py`.
- Pas de nouveau modèle, ni de choix autonome nouveau des PNJ au-delà de ce qu'A5 fait déjà entre PNJ.
- **Ne modifie pas `jeu.py`** : le lot 325 y a une fusion en cours. Si c'est indispensable, pose la question.

## Vérification
- Corvus confie à Aubin d'amener Brune : jugement, acceptation, exécution, compte rendu. Un autre cas : un refus,
  ou une charge `informer`. Gorm confie une charge à Corvus : la fiche et les comptes après recharge. Cas négatifs :
  une voix inconnue qui mandate, un refus d'accueil, une prétention d'autorité fausse. Contrôle du monde, du rendu
  et du texte affiché après rechargement, avec le MJ simulé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Empreintes 2 h sur le Relais et le hameau, quatre graines, références lues du cache : les nuits sans joueur
  actif doivent rester identiques.
- Luna : une passe, seulement sur un script qui exerce le mandat du joueur (crée-le dans `tests/data/bancs/`).

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Calcul détaché, avec un fichier de fin écrit en
dernier.

## Livraison
- Branche `codex-mandat-joueur`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-341-mandat-joueur.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\mandat-joueur-341\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
