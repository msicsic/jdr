# Lot 110 — Refus de propositions retenus

Branche `codex-propositions-redites`, non fusionnée, base `61a4406`.
Sans Luna, sans changement des buts ni des scénarios.

**Cause reproduite.** Mine 7, capture à 240 : Josse propose deux fois sa lampe
à Lucien à 244, refus « garde ». Crue 11, capture à 340 : Brune refait à 347
son offre de deux pièces à Gorm, refus « mefiance ». Les refus sont retenus,
mais une ouverture incidente (bureau, réserve) compte comme un moyen nouveau.
Captures et traces avant correction rejouées sur la base, départs tirés.

**Correction.** `pnj_propositions.refus_tient` distingue les moyens de livraison
du jugement du marché : les ouvertures pertinentes concernent les contenants
de la demande et leurs clés ; elles ne lèvent pas une garde ou une réticence.
La force offerte et l'inventaire sont retenus ; seul le nouveau bien effectivement
offert relance à valeur égale. `offre_refusee` revalide propositions et achats
avant exécution (`echanges.executer`), sans parole ni jet redondant. Aucun délai ajouté.

**Vérifications.** **34 tests ciblés verts, cinq fichiers, 109,50 s** : captures,
monde/rendu rechargés, laps découpé, plan refusé sans publication, offre plus forte
et nouveau bien offert.
Banc final 4 h × quatre scénarios × quatre graines : 16 références relues du
cache, 16 nuits de branche. Propositions/acceptées : Relais **0/0 → 0/0**,
mine **11/1 → 13/1**, auberge **3/1 → 3/1**, crue **9/0 → 9/0**.
Offres identiques à moins de 60 min **1 → 0** ; aucun plantage, violation,
usurpation ou nouveau code de boucle. Mine 1985 : la seconde lampe devient trois
pièces ; mine 2024 : Odon offre à deux personnes la lampe ramassée à 37.
`voir_alterne` crue **2 → 1**, autres constats inchangés. Temps du cache non comparés.
Suite complète unique : **2 013 tests, 16 ignorés, 216 fichiers, 1 870,76 s**,
deux processus réduits. Une erreur Windows `os.replace` du fichier temporaire
TUI ; reprise du seul test **verte en 6,13 s**, sans modification de code.
Aucun autre échec ni erreur ; aucune seconde suite. Créneau dépassé par les vérifications.

**Limites.** Une sauvegarde ancienne sans inventaire au refus reste
conservatrice sur un nouveau bien de valeur égale. Méfiance sociale inchangée ;
une offre permise ne garantit pas l'acceptation.
Les bruts sont dans `artifacts/redites-110/` ; les captures de régression dans
`tests/data/redites-*.json.gz`. Code signé SSH **91f618f**, signature vérifiée.
