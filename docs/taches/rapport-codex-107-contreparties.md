# Lot 107 — Demandes et contreparties proportionnées

Branche `codex-contreparties`, **non fusionnée**, base `303d38c`. Aucun Luna,
aucun changement de délibération ou de planification.

**Invariant et fonctions.** `demande_utile` borne une demande à une part ou au
manque monétaire propre (`besoin_d_argent` moins richesse) ; `demande_financee`
limite les pièces au prix offert. Le terme `pieces` peut nommer sa source :
propriété, garde, port et quantité sont validés avant paiement et affichage,
sans céder le contenant ni débiter une autre réserve. `offre_sensee` contrôle
aussi les plans rechargés : contrôle inversé du lot 57, puis anticipation des
P/G et du DD de disproportion communs à `evaluer_proposition`. Prix publics et
pièces connues sont utilisés ; dispositions privées adverses neutralisées.
Une offre sans chance par la valeur est écartée. Une bourse entière compte ses
pièces connues. `erreur_terme` est l'unique validation structurelle des marchés
et des audits de narration.

**Preuves.** Mine 1985 reproduite avant correction à **253** : outils contre
la paie entière, 200 pièces. Capture versionnée : ancien plan écarté, manque
borné à 45 puis au prix offert (une pièce), ou aucun recours. Après recharge,
paie et propriétaire corrects, aucune offre de bourse entière affichée. Auberge :
ballot de 200 contre outil d'une pièce écarté ; paiement partiel raisonnable
exécuté, état, parole entendue et mémoire relus après sauvegarde. Audit : terme
partiel admis, formes invalides refusées ; dispositions adverses cachées sans
effet sur l'estimation. Scènes raisonnables du lot 45 conservées.

Banc **4 h × quatre scénarios × quatre graines**, référence calculée une fois
puis cachée : **16 états finaux, chroniques, mesures et indicateurs de boucle
identiques**, aucun plantage/usurpation. Propositions/acceptées (base = branche) :
Relais **0/0**, mine **12/1**, auberge **3/1**, crue **9/0**. Le cas 253, hors banc,
est couvert par capture. Suite complète unique : **2 001 tests, 16 ignorés, 213 fichiers, 1 870,08 s** ;
une erreur temporaire Windows TUI avant action, reprise isolée verte (**2,66 s**).
Reprises finales : **34 tests verts, un ignoré, cinq fichiers, 31,34 s**, dont
l’audit commun. Aucun défaut restant reproduit, aucune seconde suite.

**Limites.** Anticipation neutre, sans garantie d'accord réel ; budget fourni par
les mécaniques existantes, sans déduction narrative nouvelle. Source portée
exigée : aucune livraison différée de pièces. Les tâches ne sont toujours pas
générées comme contreparties de recours. Récits historiques conservés.
Bruts : `artifacts/contreparties-107/`. Vérification lourde laissée à l'intégration.
