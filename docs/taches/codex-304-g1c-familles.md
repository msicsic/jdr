# Tâche Codex 304 (refonte G1 c) : aucune famille d'intention perdue ni de refus nouveau

Troisième passe sur la branche `codex-g1-compilateur`, non fusionnée. Lis les rapports
`rapport-codex-294-g1-compilateur.md` et `rapport-codex-296-g1b-fidelite.md`, et les bruts
`C:\Users\msics\donjon\artifacts\g1b-296\` (`tours-analyses.json`, `analyse-passe.json`, `mission-jouee.json`).

## Le constat
G1 b atteint ses seuils agrégés : admission au premier coup 22 → 23/30, fidélité 20 → 20/30, abandons 1 → 1. La requête
passe aussi de 22 572 à 13 252 jetons par appel. Mais il échoue sur deux critères du brief 296 :

- **prix de mission** : la question « combien me donnes-tu ? » devient `negocier`, avec une offre à 22 pièces enregistrée
  au lieu des 20 de `prime_base` ;
- **familles de refus nouvelles** : issue improvisée, opération incompatible, cible vide, lieu d'avis inconnu, contenu de
  parole omis.

Trois intentions restent aussi perdues :

- fredonner (relais/2) n'a pas d'effet sonore, et la revue l'accepte ;
- attendre puis voler (crypte/26) devient éteindre puis fermer la lanterne ;
- le pied-de-biche est remplacé par le brasero (relais/21-22).

## L'invariant
**Pour chaque famille d'intention que l'ancien interprète tenait sur ce corpus, le compilateur la tient aussi, et il
n'introduit aucune famille de refus que la référence ne connaissait pas.** Le prix d'une mission vient de `prime_base`
ou d'un accord : une question sur le prix n'est pas une proposition. Ce point se corrige par un contrat typé commun au
compilateur et au moteur (une question de prix n'a pas d'effet de négociation), pas par un mot-clé ou un cas de scénario.
Une proposition étrangère à la saisie est refusée ; la correction ne doit pas la « réparer » en un autre geste.

Pour chaque perte, établis d'abord sa cause :

- ce qui manque au contexte réduit (une source que l'ancienne requête portait) ;
- un sens de contrat ambigu ;
- une revue qui accepte trop.

Corrige le contrat commun. **Ne réintroduis pas l'ancien interprète, ni une requête qui revient à sa taille**. Si une
famille exige une source, ajoute la seule source qui manque et mesure son coût en jetons.

## Vérification
- Rejeu exact des tours perdus et des cinq refus nouveaux, sur les fils archivés (sans Luna), avant et après.
- Puis une passe Luna des six scripts du brief 296, référence `230e7b3` lue du cache sans rejeu. Les critères de fusion
  sont ceux du brief 296, sans exception. La fidélité se compte **par famille** et non seulement en total.
- Tests ciblés des fichiers touchés ; monde et rendu après recharge pour la mission et un autre cas de prix (une part
  vendue, par exemple). Pas de suite complète.

Si un critère ne peut pas être tenu sans que la requête revienne à sa taille d'avant, arrête-toi et dis lequel, avec la
mesure. N'affaiblis pas un critère pour conclure.

## Contraintes
**Poste : le laptop**, où tournent une vérification d'intégration et un autre lot. Luna sur copies seulement, priorité
réduite.

## Livraison
- Même branche, après fusion sans rebase d'`origin/integration` ; poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-304-g1c-familles.md` : un tableau par famille d'intention et un par
  famille de refus.
- Entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g1c-304\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
