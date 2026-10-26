# Lot 115 — Une tâche promise en contrepartie de recours

Branche `codex-tache-promise`, **non fusionnée**, base **6910d8e**.
Code signé SSH **d3567d8**, **ee0ab0c**, **4167150**, signatures vérifiées.
Aucun Luna ni modification des scénarios, des besoins ou de l'algorithme de recherche.

**Invariant.** `pnj_propositions.recours` offre une tâche typée après les moyens
ordinaires, depuis une condition entendue ou un état connu, sans but privé
adverse. Un candidat et un devis partagé par recours ; propres moyens sans
demande ni délégation futures, jugement inversé, classement coût/chance et refus
retenus. `echanges.proposer` revalide avant transfert et inscription datée dans
`agendas`. Tenue, rupture, annonce et relations utilisent le cycle commun.

**Preuves fonctionnelles.** Brune recharge le brasero de Gorm avec son bois ;
Joss verrouille le garde-manger d'Odile contre un repas. Monde, journal, perception
et esprits rechargés, même laps découpé, rupture et confiance diminuée, tâche
impossible, fourniture d'un tiers et refus persistants contrôlés. Suite complète
unique : **2 033 tests, 16 ignorés, 219 fichiers, 2 266,85 s** ; trois échecs et
deux erreurs d'attentes de parcours corrigés dans leurs scènes. Reprises :
**101 tests**, puis dernière attente corrigée et **13 verts en 20,04 s** ; bilan
consolidé vert, un ignoré, aucune seconde suite. Neuf tests fonctionnels nouveaux.

Banc fonctionnel **4 h × quatre scénarios × quatre graines** : aucun plantage,
violation ou usurpation ; propositions/acceptées base → branche : Relais
**0/0 → 0/0**, mine **13/1 → 10/1**, auberge **3/1 → 3/1**, crue **9/0 → 5/0**.
Aucune tâche naturelle offerte/acceptée/tenue/rompue sur ces 16 nuits finales ;
les parcours ciblés et rejeux démontrent l'exécution. Mine : observation de
Rémy, 230 min de devoir déjà satisfait ; pas de boucle active nouvelle.

**Réserve CPU levée sur la mesure demandée.** Deux versions lancées ensemble,
un processus chacune, priorité réduite, `--sans-cache`, départ tiré, **4 h**.
Le lanceur non versionné utilise les mêmes `lancer`/`jouer_nuit` et audits que
`comparer_bancs.py`, dont le parcours standard est successif. Appels au lanceur
espacés de **0,96 ms** au premier passage, **0,89 ms** au second. Première mesure : crue
**75,953 → 87,844 s (+15,66 %)** ; auberge **62,625 → 61,750 s (−1,40 %)**.
Profil crue 2024 : **58,197 s instrumentées**, recours **7,206 s (12,4 %)**,
dont devis de proposition **6,770 s (11,6 %)** ; 32 devis, échecs répétés dominants.

**Levier exact.** `_charge_irrealisable` déduit l'échec avant copie et exploration :
le devis existant vise une source allumée **et chargée** ; sans réservoir
rechargeable, aucun geste autonome ne rend la charge vraie. Si elle est fausse
ou inconnue au départ, le but est inaccessible. `brule` et la projection datée
`_vu_avant_la_tache` restent communs au planificateur. Une charge encore crue
valable conserve la recherche normale. Aucun cache persistant, délai, nom de
source ou modification de décision.

**Secondes CPU par nuit : (1) avant levier, branche 5261663 ; (2) après levier,
branche 4167150 ; base 6910d8e dans les deux mesures.**

| Scénario | Graine | Base (1) | Branche (1) | Base (2) | Branche (2) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Crue | 1985 | 17,062 | 19,516 | 16,250 | 16,141 |
| Crue | 7 | 19,922 | 21,234 | 18,688 | 17,656 |
| Crue | 42 | 17,344 | 22,438 | 16,828 | 17,562 |
| Crue | 2024 | 21,625 | 24,656 | 21,156 | 21,281 |
| **Crue total** | | **75,953** | **87,844 (+15,66 %)** | **72,922** | **72,641 (−0,39 %)** |
| Auberge | 1985 | 15,094 | 14,969 | 14,594 | 14,750 |
| Auberge | 7 | 16,609 | 16,703 | 16,500 | 16,641 |
| Auberge | 42 | 16,469 | 16,062 | 16,312 | 16,094 |
| Auberge | 2024 | 14,453 | 14,016 | 14,000 | 14,094 |
| **Auberge total** | | **62,625** | **61,750 (−1,40 %)** | **61,406** | **61,578 (+0,28 %)** |
| **Ensemble** | | **138,578** | **149,594 (+7,95 %)** | **134,328** | **134,219 (−0,08 %)** |

**Équivalence.** **33 tests ciblés verts, un ignoré, 36,95 s**, capture réelle
crue 2024 à 17 min et bougeoir d'auberge comparés à la recherche non raccourcie,
monde et rendu rechargés. **16/16 états finaux, chroniques, audits et mesures
hors compteurs de recherche identiques avant/après optimisation**, 4 h et quatre
graines sur les quatre scénarios ; Relais/mine seuls rejoués en complément.
Crue : **127 recherches neuves évitées**, dont 31 en 2024 ; décisions inchangées.

**Limites.** Mesure ponctuelle sur poste partagé ; le seuil global **×1,5 contre
42bb9c0 n'est pas remesuré**. Un candidat peut masquer un autre service possible ;
verrouillage ponctuel, aucune garde permanente ni tarif en pièces nouveau.
Devis cru, moyens réels revalidés. Bruts : `artifacts/tache-115/`, mesures
appariées et profil dans `cpu/`. Le lourd reste à l'intégration.
