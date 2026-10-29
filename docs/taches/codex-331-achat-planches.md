# Tâche Codex 331 : l'échec préexistant de l'achat de planches (`test_audience`)

Lis `AGENTS.md` et `docs/etat-dev.md`, puis le rapport 320 (il relève cet échec comme préexistant sur sa base
`0fcc99e`).

## Constat
`tests/test_audience.py`, cas « je paie Aubin trois pièces pour une de ses planches » (vers la ligne 155) : la
bourse de Corvus vaut **23 au lieu des 26 attendus** (`self.assertEqual(m.joueur["or"], pieces)`). L'échec est
présent sur l'intégration depuis au moins `0fcc99e` et persiste après les fusions 320 à 327. Ni l'oracle ni sa
cause n'ont été instruits.

## Ce qui est demandé
1. **Bissection** sur les parents directs : identifier le commit qui fait passer ce test du vert au rouge, et dire
   ce qui a changé dans la chaîne parole → proposition → paiement → livraison.
2. **Trancher** : défaut du moteur, ou attente périmée par un changement légitime. Un paiement exécuté sans
   livraison, ou une livraison refusée après paiement, est un défaut du contrat commun des échanges ; une simple
   différence de trajectoire légitime ne l'est pas.
3. **Défaut** : corrige l'invariant commun (pas de cas propre à Aubin, aux planches ou à cette phrase). Vérifie le
   cas réel et un autre achat de même nature, avec la bourse, l'inventaire, l'engagement et le rendu identiques après
   recharge.
   **Attente périmée** : ajuste la prémisse de la scène avec la preuve de la cause, sans affaiblir les assertions
   (bourse, charges, appels).

## Vérification
- Le fichier entier `tests/test_audience.py`, puis les fichiers de tests que touche le correctif. Pas de suite
  complète.
- Si le moteur change : empreintes 2 h Relais et auberge, quatre graines, références lues du cache.
- Ni Luna ni banc PNJ.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Recouvrement possible avec le lot 326 (G17,
comptes parlés, livré, non fusionné, `paroles.py` et `dialogues.py`) : signale-le.

## Livraison
- Branche `codex-achat-planches`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-331-achat-planches.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\planches-331\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
