# Lot 104 — N3, opérations contestées par leur propre revue

Branche `codex-n3-reformule`, non fusionnée ; base `e4dbc6a`.

Rejeu exact du tour 1 de `n3-soir-noir-lot102`, avant correction : trois appels,
« Ta demande n'a pas été exécutée. Reformule-la. », aucune parole sauvegardée.
Les trois réponses enregistrées sont conservées dans `tests/data/n3-lot102.json`.
La revue refuse `contenu=[qui]` (présence demandée, identité proposée), tout en
cochant `operations_demandees.qui=true`. Le cumul transformait ce typage contesté
en obligation ; la correction `propos`, puis le secours vide échouaient localement.

**Contrat commun.** `couverture_action.verifier` ne confirme plus les opérations
présentes dans un contenu dont la même revue refuse le sens. Les opérations
absentes qu'elle relève restent exigées, comme les obligations déjà confirmées
ou non examinées. `MJ._verifier_fidelite_parole` dispense de nouvelle revue le
secours aux mots exacts, sans contenu typé ni obligation restante. Aucun cas
de formulation, de personnage ou de scénario, aucun prompt supplémentaire.
Le rejeu, la salle éclairée, deux corrections refusées et une saisie
inintelligible passent dans la console avec sauvegarde/recharge.

**Sorties examinées.** Une seule occurrence de la phrase exacte existait dans
`mj.py`, dans le secours refusé pour couverture manquante. Elle ne correspondait
pas nécessairement à une saisie inintelligible : supprimée. Le refus restant
dit qu'aucune parole n'est prononcée et demande d'en préciser le contenu ; il
conserve les obligations non examinées au lieu de simuler leur exécution.
Les autres demandes de précision concernent une parole sans mots fournis,
une adresse impossible ou les références que Corvus ne connaît pas ; le refus
de manœuvre ne déclenche pas cette phrase. Le moteur ne prétend pas avoir agi.

**Mesures.** Tests ciblés finaux : **21 tests verts**, cinq fichiers :
12 en 48,05 s, puis 9 en 37,68 s.
Suite complète unique : **1 990 tests, 16 ignorés, 210 fichiers, 2 133,20 s**,
deux processus réduits ; quatre échecs d'attentes obsolètes (deux libellés,
deux comptes d'appels en sous-tests), corrigés, puis reprise des deux fichiers
**9 tests verts** ci-dessus. Aucun défaut restant reproduit ; aucune seconde suite.
Passe Luna unique, `soir-noir` et `noms-dialogue` sur copies : **9 tours MJ,
38 appels, 120,57 s, 13,40 s/tour** ; N3 absent, aucun arrêt, erreur technique,
repli ni défaut de recharge. Le premier appel de présence est prononcé après
un refus de fidélité. Bruts : `artifacts/reproduction-104.txt`,
`artifacts/cibles-104.json`, `artifacts/reprises-104.json`, `artifacts/tests-104.json`,
`artifacts/bancs-multi/20261026-030701-45472/`.

**Limites.** La revue du sens demeure probabiliste ; une opération présente dans
un contenu rejeté n'est pas une preuve de demande, même si son code est coché.
Les opérations sans contenu exécutable ou non examinées restent refusées : ce
lot ne garantit pas la compréhension de toute saisie. L'incohérence ultérieure
« Je ne te dirai pas qui je suis » après le nom donné reste observable, hors
invariant. La passe Luna précède le dernier ajustement qui dispense le secours
d'une revue redondante ; celui-ci est couvert par le test à deux refus, sans
seconde passe Luna.
