# Lot 366 — levée d'un refus par contrepartie

Branche `codex-refus-leve-contrepartie`, issue d'`integration 60f857c5`,
travail commencé sur `dea991a5` (briefs ajoutés). PC fixe `msi-desktop`.
**Lot terminé, non fusionné ; code validé `9c03d7ac`, branche poussée. Aucun calcul actif.**

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
Les essais préliminaires restent dans les bruts. Le nouveau test final contrôle
la répétition de la même demande gratuite : payer après un refus d'humeur
peut ouvrir un autre jugement, même sous le prix de la contre-offre.

**Preuves ajoutées et validation finale.** Trois tests couvrent deux biens
achetés, la demande gratuite toujours bloquée, la prestation enregistrée
distincte d'une simple faim apaisée, l'enquête distincte et une seconde clé
prêtée après service dans un laps de cinq minutes, en bloc ou par minutes
rechargées. Ils comparent état des PNJ, finances, permissions, chronique et
vues publiques (regard, scène, écoute), ainsi que la persistance complète.
**57/57 tests, 207,968 s, zéro échec, erreur ou saut**, sur **8 fichiers** : ces preuves, 358, contre-offres,
vérification eau, refus retenus, recours, compensation d'outils et contreparties.
Les empreintes **2 h, 4 graines, Relais/mine/auberge/crue** sont achevées :
**16 nuits de branche**, seize références `origin/main 0bad2272` toutes relues
du cache, **zéro plantage et zéro usurpation dans les deux versions**.

| Scénario | Retours non justifiés | À expliquer | Dérives ouvertes |
|---|---:|---:|---:|
| Relais | 0 → 0 | 1 → 0 | 24 → 33 |
| Mine | 0 → 0 | 4 → 4 | 48 → 57 |
| Auberge | 0 → 0 | 0 → 0 | 9 → 10 |
| Crue | 0 → 0 | 5 → 5 | 33 → 66 |

**Écarts et limites.** Aucun des seize états finaux n'est identique à `main`.
La première divergence (Relais 1985, minute 0 : chronique, mesures, état)
est déjà décrite dans le [rapport 360](rapport-codex-360-regressions-337.md),
fusionné dans la base : la confidence initiale d'Aubin sur la torche est absente,
selon le contrat des nouvelles initiales. La comparaison cumule les lots depuis
`main` ; elle n'attribue pas tous les écarts au 366, ne prouve pas une identité des
nuits ni l'absence générale de boucles. Une répétition est signalée sur la branche :
Aubin appelle huit fois Brune, crue 42 ; les appels de cette nuit étaient déjà une
limite du [358](rapport-codex-358-revalider-apres-refus.md). Les dérives restent
ouvertes, sans retours classés non justifiés. Pas de conclusion de performance
contre les temps mis en cache, ni Luna ni suite complète.

**Bruts et clôture.** `C:/Users/msics/donjon/artifacts/refus-leve-366/` :
`tests-final.json`, `empreintes.json`, `fin-validation.json`, `conclusion.json`
et lanceurs conservés. Exécution détachée **381,652 s**, deux travailleurs
réduits au plus. `fin-validation.json ok=false` est conservé : tests **0**,
empreintes **1** pour divergence, sans erreur de calcul. La synthèse explique
ce résultat ; les SHA-256 confirment le code et les tests inchangés depuis
validation. Aucun calcul restant ; clôture documentaire seule.
