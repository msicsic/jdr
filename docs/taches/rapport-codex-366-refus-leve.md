# Lot 366 — levée d'un refus par contrepartie

Branche `codex-refus-leve-contrepartie`, issue d'`integration 60f857c5`,
travail commencé sur `dea991a5` (briefs ajoutés). PC fixe `msi-desktop`.
**Code livré ; validation voisine et empreintes en cours, lot non encore validé.**

**Invariant et cause.** Le lot 358 faisait passer les recours conservés par
`deliberation.refus_geste`, qui consultait le refus ordinaire sans reconnaître
la contre-offre honorée. Or `tient` conserve volontairement une contre-offre
sans délai : elle reste le moyen poursuivi par `plan_recours`, même après
prestation. La demande de clé après repas et l'achat de lampe au prix annoncé
étaient donc éliminés avant d'atteindre le juge de leur accord.

**Correction commune.** `refus_geste` réutilise désormais `offre_retenue` et
`condition_remplie`, comme le recours et la remise : une prestation effectivement
enregistrée libère la demande du bien convenu ; le prix effectivement proposé
libère son achat s'il satisfait la condition annoncée. Le contrôle ne produit
ni parole, perception, jet, remise ou paiement. Le refus reste en mémoire
jusqu'à sa résolution ; la recherche ordinaire ne le réessaie pas. Les enquêtes,
mandats et autres opérations conservent leurs juges. Les contrôles matériels,
financiers et de compensation restent appliqués lors de l'exécution.
Seul `donjon/deliberation.py` change dans le moteur ; aucun recouvrement de
code avec les lots 364/365/367/368 annoncés. `docs/etat-dev.md` reste commun.

**Preuves acquises.** Les deux méthodes réservées par le 362 sont reproduites
rouges, puis vertes sans modifier leurs assertions : **2/2, 26,937 s**.
Le prêt de clé est retrouvé après service, recharge et laps découpé ; la lampe
est vendue à Bram pour **17 pièces**, avec contrôle des finances, de la capacité
compensée, de la propriété et du rendu rechargé. Les **8 tests du 358 passent**,
dont la capture réelle du mandat refusé à Maël, sans réexécution ni effet.
Les bruts d'un premier lanceur à import erroné et d'une première attente de
test trop stricte restent conservés : payer après un refus gratuit d'humeur
peut ouvrir un nouveau jugement, même sous le prix de la contre-offre ; le
contrôle de répétition porte donc sur la même demande gratuite.

**Preuves ajoutées et validation restante.** Trois tests couvrent deux biens
achetés, la demande gratuite toujours bloquée, la prestation enregistrée
distincte d'une simple faim apaisée, l'enquête distincte et une seconde clé
prêtée après service dans un laps de cinq minutes, en bloc ou par minutes
rechargées. Ils comparent état des PNJ, finances, permissions, chronique et
vues publiques (regard, scène, écoute), ainsi que la persistance complète.
La passe finale porte sur **8 fichiers** : ces preuves, 358, contre-offres,
vérification eau, refus retenus, recours, compensation d'outils et contreparties.
Elle est suivie des empreintes **2 h, 4 graines, Relais/mine/auberge/crue**.
Référence `origin/main 0bad2272` (le `main` local est ancien), cache partagé
réutilisé ; les écarts à cette référence antérieure aux autres lots de la base
ne suffiront pas à attribuer une divergence au 366. Ni Luna ni suite complète.

**Calcul détaché.** Deux travailleurs réduits au plus, tests puis empreintes,
empreintes SHA-256 des sources enregistrées par le lanceur. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/refus-leve-366/` ; résultats attendus
`tests-final.json`, `empreintes.json`, puis **`fin-validation.json` écrit en dernier**.
La livraison ne déclare pas encore les voisins ou les empreintes validés ;
la lecture de ces résultats et l'explication des écarts restent nécessaires.
