# Tâche Codex 296 (refonte G1 b) : le compilateur ne perd aucune intention que l'ancien interprète tenait

Suite du lot 294 (G1), sur sa branche `codex-g1-compilateur`, non fusionnée. Lis son rapport
`docs/taches/rapport-codex-294-g1-compilateur.md` et ses bruts `C:\Users\msics\donjon\artifacts\g1-294\`
(`tours-analyses.json`, `analyse-passe.json`, `rapport-detaille.md`).

## Le constat
Le compilateur raccordé divise l'entrée par deux (22 572 → 11 082 jetons, consignes 40 364 → 3 547 caractères), sans
gain de vitesse. Mais il dégrade l'interprétation, premier critère du gameplay. Sur les six scripts :
- admission au premier coup 22 → 18/30 ;
- fidélité au contrat 20 → 14/30 ;
- refus de validation 8 → 14 ;
- abandons 1 → 3.

Pertes relevées :
- une odeur devenue parole ;
- une consigne connue remplacée par une lecture ;
- un fredonnement sans son ;
- une mauvaise opération sous la poutre ;
- « Gorm a le dos tourné » inventé ;
- le prix de la mission devenu `negocier/0` au plafond (22 contre 20) ;
- le gardien abandonné, avec « Réponse du MJ sans contrôle narratif. » affiché au joueur ;
- l'achat de planche perdu ;
- l'écoute toujours perdue.

## L'invariant
**Pour chaque famille d'acte, le compilateur reçoit les informations publiques et les règles de contrat dont la
validité ou la fidélité de l'acte dépend : aucune intention que la référence admettait fidèlement n'est perdue, et
aucun fait n'est inventé pour rendre un acte admissible.** Aucun message interne n'est montré au joueur.

Méthode : pour chaque tour perdu ou infidèle, établis la cause. Ce peut être :
- un fait public absent du petit contexte ;
- une règle du contrat de l'ancienne consigne qui manque au prompt ou au schéma du compilateur ;
- une normalisation qui change le sens ;
- une correction qui perd l'intention ;
- un message de secours affiché.

Corrige la cause commune : la règle passe dans le contrat dérivé (`section_contenu`, schéma), le fait dans le contexte
public, par famille. Jamais de cas propre à une saisie, un objet ou un scénario. La taille du contexte n'est pas un
objectif en soi : réintroduis ce dont un acte dépend, et mesure ce que cela coûte. « Réponse du MJ sans contrôle
narratif. » ne doit jamais atteindre le joueur : trouve la voie qui l'affiche et ramène-la au contrat (refus public ou
précision du moteur).

## Préalable
Fusionne d'abord `origin/integration` (4808942 ou plus récent) dans ta branche, sans rebase. Il apporte le lot 295 :
les tests de transport adaptés à G2/G4 et le repli perceptible rétabli dans `MJ._appeler`. Résous les conflits (dont
`test_cache_kv_local`) en gardant les deux garanties. Les tests de transport touchés par la requête d'interprétation
doivent passer sur le nouveau compilateur.

## Vérification
- Tests ciblés : pour chaque cause corrigée, le tour réel et un autre cas de même nature, en console avec MJ simulé,
  plan admis, monde et rendu après recharge ; plus les fichiers touchés par la fusion du lot 295.
- **Luna, une passe**, mêmes six scripts (`relais`, `crypte`, `echanges`, `ressources`, `soir-appel`, `avis-joueur`),
  contre la même référence `230e7b3`, lue du cache. Critères de fusion, contre la référence :
  - admission au premier coup et fidélité au contrat au moins égales ;
  - abandons au plus égaux ;
  - aucune nouvelle famille de refus ;
  - mission : prix demandé fidèle ;
  - taille et préfixe mesurés.

  Si un critère n'est pas atteint, dis lequel et pourquoi, sans présenter le lot comme prêt.
- Passe Luna détachée, fichier de fin écrit même en cas d'échec, démarrage vérifié avant de rendre la main.
- Pas de suite complète (le superviseur la lance).

## Contraintes
**Poste : le laptop.** La vérification d'intégration (lot 284) y tourne peut-être encore : deux processus au plus,
priorité réduite.

## Livraison
- Même branche `codex-g1-compilateur`, poussée.
- Rapport d'une page `docs/taches/rapport-codex-296-g1b-fidelite.md` : un tableau tour → cause → correction → résultat.
- Entrée etat-dev mise à jour.
- Bruts dans `C:\Users\msics\donjon\artifacts\g1b-296\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
