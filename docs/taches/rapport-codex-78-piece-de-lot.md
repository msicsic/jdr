# Lot 78 — Une pièce et son lot

Branche `codex-piece-de-lot`, non fusionnée, base **6a49036** (brief issu de
l'intégration **38e5d7e**). Correctif signé SSH **69f04db**. Aucun changement de
`main`, des scénarios, du modèle, des instructions de Luna, d'`echanges.py` ou de
`deliberation.py`.

**Invariant.** Une part d'un lot garde l'identité du lot et une quantité distincte
de son nom, même au pluriel. `paroles.sens_contenu(contenu, monde)` fournit avant
transaction la référence publique, les noms connus, la quantité **1** et l'unité
**part** pour une demande de ressource comptée ou un terme `part` de marché.
Un objet entier reste une unité **objet**. Demande et contrepartie sont décrites
séparément. `mj._verifier_fidelite_parole` transmet ce sens à la contre-revue ;
`couverture_action.entree` nomme également les objets des termes imbriqués.

`noms.appellations` rassemble nom, alias et `physique.nom_piece` déclaré ;
`Monde.trouver`, `paroles.resoudre`, le lexique et les repères de désignation
emploient ces mêmes noms. Aucun singulier n'est deviné ; une réserve collective
peut ainsi contenir des pièces dont le nom est différent. Les contrôles existants
de connaissance, de perception et d'ambiguïté restent applicables. Le dossier ne
décrit pas une réserve inconnue et ne décide aucune acceptation ou mutation.

**Tests.** Quatre tests nouveaux : achat d'une planche par demande simple et marché
typé ; achat d'une bûche d'une réserve à l'auberge, sans alias manuel ; autre objet
refusé puis contenu corrigé sans transaction parasite ; unité et quantité distinctes,
réserve inconnue exclue. Vraie console avec MJ simulé, sauvegarde/recharge, paiement,
part détachée, compte de livraison, remise effective par le PNJ et inventaire rechargé.
Les trois tests fonctionnels passent (quatre parcours), ainsi que le complément ciblé.
Neuf tests existants ressource/comptes passent. Suite complète unique, **191 fichiers,
1 887 tests, 16 ignorés, aucun échec ni erreur**, trois processus à priorité réduite,
**1 576,9 s**. Elle avait chargé les trois tests fonctionnels avant l'ajout du
quatrième ; celui-ci, corrigé puis repris isolément, est vert (0,28 s).
**Bilan consolidé : 1 888 tests, 16 ignorés**, sans seconde suite complète.

**Luna.** ChatGPT, `gpt-6-luna`, medium/libre, une passe des trois scripts prescrits,
copies uniquement. Référence **fbcf0ff** relue intégralement du cache, budget 200.
Total **42 → 40 appels / 11 tours MJ**, **3,82 → 3,64 appels/tour** ; soir-appel
**19 → 19**, ressources **11 → 9**, noms-dialogue **12 → 12**. Relances narratives
**3 → 2**, replis **1 → 0**, aucun refus de fidélité/moteur, arrêt ou erreur de recharge.
L'achat réel « je paie Aubin trois pièces pour une de ses planches » est déclaré
conforme, exécuté puis raconté en six appels ; au premier `ouest`, Aubin remet
`planches_1`, présente dans les objets portés de l'état rechargé. Les autres demandes
de bois et de nourriture reçoivent leur réponse. Les temps du cache proviennent
d'une autre charge : aucune conclusion de vitesse. La référence précède aussi
les lots déjà intégrés depuis `fbcf0ff` ; l'écart global ne mesure pas le seul lot 78.

**Limites.** La fidélité reste un jugement sémantique sur ce dossier : aucune garantie
de toute paraphrase ou quantité libre. Un nom de pièce doit être déclaré ou déjà
fourni comme alias. Les autres causes de refus narratif restent possibles : un geste
de désignation et un acquiescement, puis des extractions de comptes rejetées, donnent
les deux relances du soir. Le texte final du marché dit « les trois pièces que tu me
devais » : une dette antérieure n'est pas attestée par le paiement ; cette formulation
non détectée reste une limite de portée/extraction, sans dette créée dans l'état.
Le harnais Luna vérifie l'état résumé rechargé ; les panneaux sont vérifiés par les
tests simulés. Le premier lancement, budget 500 incompatible avec le cache, a été
interrompu sans partie produite ; son worktree temporaire a été supprimé, puis la
présence des trois références en cache a été vérifiée avant le lancement retenu.

Bruts du worktree : `artifacts/tests-cibles.json`, `tests-piece.json`,
`tests-piece-final.json` (essai initial du complément, repris vert isolément),
`tests-complets.json`, `tests-complets.log`, `luna.log`, `relecture-luna.json`,
`verification-lot78.json` et
`bancs-multi/20261025-141931-43052/`. Les essais ciblés initiaux contiennent aussi
les erreurs de préparation corrigées ; la suite complète et le complément isolé
validé après correction font foi pour la livraison.
