# Tâche Codex 311 (refonte G1 d) : la revue ne confond plus « non admis » et « infidèle », puis les trois pertes restantes

Dernière passe décidée par l'utilisateur le 29 octobre, sur la branche `codex-g1-compilateur`, non fusionnée. Si elle
échoue, l'utilisateur choisira entre accepter G1 avec ses pertes et le repenser : **pas de G1 e**. Lis les rapports
`rapport-codex-294-g1-compilateur.md`, `rapport-codex-296-g1b-fidelite.md` et `rapport-codex-304-g1c-familles.md`, et
les bruts `C:\Users\msics\donjon\artifacts\g1c-304\`.

## Le constat
G1 c donne le prix juste, une requête plus légère et l'admission au premier coup 23/30. Mais :

- **la revue de fidélité de l'action** passe de 1 à 4 refus. Trois sont faux : elle lit un candidat que le moteur
  n'admet pas (proximité, visibilité) comme une infidélité à la saisie (« non admis = absent »). Cela coûte des appels
  (3,30 → 3,83 par tour) et fait perdre l'écoute de crypte/9 et le passage de relais/20 ;
- **trois intentions restent perdues** :
  - le son fredonné (relais/2) n'est pas exécuté, après deux refus nouveaux (cible vide, catégorie acoustique vide) ;
  - l'odeur (crypte/1) est éludée ;
  - la question au MJ (crypte/41) devient une parole.

## L'invariant
**La fidélité juge si une proposition dit ce que demande la saisie, et seulement cela. Qu'un geste fidèle ne puisse pas
être admis (portée, visibilité, ressource) est le refus public du moteur, qui garde l'intention, et jamais un refus de
fidélité.** La fidélité et l'admission sont deux contrôles distincts, appelés dans un ordre fixé par le contrat commun.
Un refus d'admission ne relance pas la fidélité.

Ensuite seulement, pour chacune des trois pertes, établis sa cause (contexte réduit, contrat ambigu, revue trop large)
et corrige le contrat commun. Aucun mot-clé ni cas de scénario, aucun retour de l'ancien interprète, et la requête ne
revient pas à sa taille d'avant.

## Critères de fusion
Ceux des briefs 296 et 304, avec une précision : **une intention conservée par un refus public du moteur (portée,
visibilité) compte comme fidèle**, puisque c'est le comportement visé par G2.

Plus deux critères :

- les appels par tour ne dépassent pas ceux de la référence (3,30) ;
- aucune famille de refus nouvelle, comptée comme au 304.

## Vérification
- Rejeu exact, sans Luna, des tours concernés sur les fils archivés du 304, avant et après.
- Une passe Luna des six scripts, référence `230e7b3` en cache sans rejeu.
- Tests ciblés des fichiers touchés ; monde et rendu après recharge pour l'écoute et un autre refus de portée.
- Pas de suite complète.

## Contraintes
**Poste : le laptop.** Luna sur copies seulement, priorité réduite.

## Livraison
- Même branche, après fusion sans rebase d'`origin/integration` ; poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-311-g1d-revue.md`, avec les tableaux par famille d'intention et par
  famille de refus.
- Entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g1d-311\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
