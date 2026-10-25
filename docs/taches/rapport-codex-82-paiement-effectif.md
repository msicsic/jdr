# Lot 82 — La parole porte l'échange demandé

25 octobre 2026 — Branche `codex-paiement-effectif`, **non fusionnée**, base `a6f9368`
(brief sur l'intégration `3ffd72d`). **Validation Luna partielle : achat typé et arbitré,
mais aucun achat exécuté dans cette passe.** `main`, `planification.py`, scénarios,
modèle `gpt-6-luna` et prompts d'interprétation/narration inchangés ; protocole de revue étendu.

**Invariant et fonctions.** Le rapport de couverture sépare désormais
`operations_demandees` du verdict `contenu_conforme`. Son vocabulaire vient du sens
commun des contenus de `paroles`, sans reconnaître une liste de verbes dans la saisie.
`operations_contenu` lit les opérations effectivement portées ; une demande payée
utilise le même calcul `offre` que l'exécution, et couvre un échange comme `proposition`.
`couverture_action.verifier` refuse toute opération demandée manquante, même avec un
verdict favorable ; son `attendu` privé cite le contenu reçu et la forme attendue
(demande/contrepartie ou offre chiffrée positive). Le verdict sémantique continue de
comparer les biens, quantités et contreparties.

`MJ._verifier_fidelite_parole` contrôle aussi une adresse explicite et les mots exacts.
Le repli littéral repasse ce contrôle ; les opérations reconnues restent exigées pendant
les corrections de la même saisie. Une revue illisible est redemandée une fois, puis
bloque la parole ; les gestes conservent leur règle historique. Aucun essai rejeté sur
copie n'est enregistré ni affiché comme parole accomplie.

**Tests.** Cinq nouveaux tests de vraie console avec MJ simulé : `propos` déclaré conforme
malgré l'échange demandé, puis achat de planche exécuté ; autre formulation sur une part
de soupe, marché typé, adresse explicite et guillemets ; offre textuelle ou nulle corrigée
sans donation parasite ; opération conservée malgré son omission aux revues suivantes ;
salutation ordinaire et réclamation ; six revues illisibles sans parole ni paiement.
Ils contrôlent or, réserves, propriété, remise immédiate ou engagée, récit et inventaire
après recharge. Les anciens tests des raccourcis attendent désormais le contrôle.
Suite complète unique : **1 908 tests, 16 ignorés**, 194 fichiers, trois processus
à priorité réduite, **1 683,2 s**. Trois échecs et quatre erreurs dans trois anciennes
attentes (appel de couverture désormais présent) et la nouvelle scène de soupe
(repas servi par la demande historique, au lieu de la remise immédiate attendue).
Simulations corrigées, puis **102 tests sur huit fichiers repris verts**, deux processus,
**98,0 s**, y compris le code final. **Bilan consolidé : 1 908 tests, 16 ignorés,
aucun défaut restant connu**, sans seconde suite complète.

**Luna, une passe seulement.** ChatGPT, medium/libre, copies temporaires, priorité
réduite ; référence `882907c` intégralement relue du cache (trois parties, aucune rejouée).
Soir-appel **17 → 17 appels**, ressources **11 → 12**, noms-dialogue **16 → 15** :
**44 → 44 appels / 11 tours MJ**, **4,00 → 4,00 appels/tour**, **17,3 → 14,2 s/tour**,
relances narratives **4 → 0**, refus **0 → 2**, aucun arrêt, erreur technique/recharge
ou repli détecté par le harnais. Temps historiques sous une autre charge : aucun gain
de vitesse attribuable au lot.

Au soir n° 5, Luna propose bien `proposition`, une part de `planches` contre trois pièces ;
la revue extrait `proposition`, le moteur refuse « il ne voit pas comment faire la tâche »
et cette issue est affichée. La question préalable sur le bois a subi deux faux refus
de fidélité, confondant « quelqu'un » et l'audience fixée ; son repli sans opération est
désormais bloqué. Aubin n'a donc pas constaté sa réserve. Même faux refus à noms-dialogue ;
la demande nominative de ressources est exécutée et reçoit bien la réponse sur les planches.
Le critère **achat exécuté avec Luna n'est pas atteint** ; pas de seconde passe ni de
correctif d'audience hors lot. La fermeture du repli transforme ces faux refus en demandes
non exécutées : limite de jeu explicitement conservée.

**Limites et bruts.** La reconnaissance des opérations reste sémantique : une omission
dès la première analyse n'est pas rattrapée par la comparaison structurelle. Une extraction
erronée peut aussi contraindre les reprises ; aucune garantie de toute formulation ni de
l'absence de faux refus. Les derniers resserrements (conservation des opérations, montant
exécutable et rapport illisible) sont vérifiés par les tests, sans nouvelle passe Luna.
Bruts du worktree : `artifacts/tests-cibles.log`, `tests-complets.{log,json}`,
`tests-reprise-finale.{log,json}`, `verification-tests-lot82.json`,
`verification-lot82.json`, `luna.log` et
`bancs-multi/20261025-173635-38776/` (JSON, HTML et mesures).
