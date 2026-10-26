# Lot 100 — Réponses mal formées et opérations contestées

Branche `codex-sans-message-technique`, non fusionnée ; base `a86fdd7`.

**Reproductions avant correction : six échecs**, console, sauvegarde et recharge.
N1 réel : `etablir_faits`, `proposition=null`, sources citées dans `faits` ;
validation tardive héritée de `723d7d6`, antérieure aux lots suspects. N3 : cumul
de `qui=true` malgré sa contestation par la revue (`031a86e`, **lot 91**) ;
correction et secours étaient refusés localement. Le message venait du lot 82
(`3510d00`), pas des lots 95/96.

**Contrat commun, `donjon/mj.py`.** `verifier_forme_reponse` contrôle enveloppe et
collections structurées avant les audits : correction distincte `RefusDeForme`,
puis repli moteur si elle échoue. La fidélité distingue déclaration candidate et
opérations reconnues : le typage rejeté ne condamne plus les mots exacts ; une
omission locale, une préparation refusée ou une revue illisible conserve les
obligations non examinées. Aucun cas de scénario ni prompt supplémentaire.

**Validation.** Une passe Luna, quatre scripts, une exécution à priorité réduite :
**23 tours MJ, 81 appels, 250,23 s ; 3,52 appels et 10,88 s/tour** (médiane 10,65 s).
N1 : description de perception, trois appels ; N3 : mots exacts dits et réponse
reçue, cinq appels. Aucun arrêt, erreur technique ou défaut de recharge, aucun
repli. Quatre mentions heuristiques reprennent des noms saisis, sans fuite nouvelle.

| Script | Branche : appels/tour ; s/tour | Référence b0042c9, deux passes en cache |
|---|---|---|
| atelier | 3,09 ; 9,13 | 2,77 ; 9,85 |
| soir-noir | 4,80 ; 14,62 | 4,20 ; 13,12 |
| noms-dialogue | 3,25 ; 10,51 | 3,25 ; 11,23 |
| échanges | 3,33 ; 11,57 | 3,67 ; 13,24 |

Suite complète unique : **1 975 tests, 16 ignorés, 207 fichiers, 2 046,41 s**,
deux processus réduits ; quatre erreurs et deux échecs, corrigés pendant le lot.
Reprises finales : **96 tests verts,
10 fichiers, 133,73 s**, un processus réduit ; schémas vides des appels d'audit
internes acceptés, simulations de coupe/récit adaptées à la correction de forme,
second objet de description rendu non ambigu. Tests : état, parole, affichage et
conversation rechargés, avec un autre cas de chaque nature et protection des
paiements. Bruts : `artifacts/reproduction-100.txt`, `artifacts/tests-100.json`,
`artifacts/cibles-finaux-100.json`, `artifacts/bancs-multi/20261026-013940-3568/`,
`artifacts/analyse-100.json`. Aucun défaut restant reproduit ; aucune seconde suite complète.

**Limites.** Une opération exigée sans contenu exécutable reste inexécutée ; les
validateurs internes, erreurs de fournisseur et refus sémantiques ne sont pas
tous couverts. Pas de garantie générale sur toutes les voies historiques
d'abandon ni de gain de latence établi : référence sous une autre charge.
