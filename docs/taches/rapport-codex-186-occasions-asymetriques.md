# Lot 186 — Occasions asymétriques

`codex-occasions-asymetriques`, **non fusionnée**, base `12a936d`, 2026-10-27.
Données et tests seulement, aucun `donjon/*.py`, aucun Luna. Deux calculs
réduits au plus. Bruts, scripts, mondes et rendus exclusivement :
`C:/Users/msics/donjon/artifacts/occasions-186/`.

**Invariant.** Ajouter des moyens utilisables par les contrats existants, sans
affaiblir les gardes. Biens matériels historiques, traits, valeurs, réserves,
pulsions, agendas et finances conservés (contrôle des sept JSON contre la base).
La faim du propriétaire peut toujours rendre les nouveaux lots incessibles.

| Donnée | Mécanisme visé | Effet observé |
|---|---|---|
| Quatre galettes portées par Gorm/Mathe/Odile, prix 2, séparées des vivres gardés | Offre, paiement d'un travail, don utile | Trois marchés du joueur acceptés en test ; Odile donne une galette à Joss après refus social (auberge 7, 657 min), service crédité mais méfiance conservée. |
| Deux charges de petit bois propres portées par Brune/Odon/Joss ; foyer connu | Contrepartie, promesse autonome, réparation par service | Crue 1985 : Brune recharge le brasero à 496 min, une charge consommée, méfiance levée ; redemande puis repas à 498. Recours de service enregistré. |
| Affection Gorm → Aubin, Mathe → Josse, Odile → Mireille à 60 ; sourire interprété connu du demandeur | Triangle de commission perceptible | Crue longue : quatre sollicitations, quatre acceptations, deux aboutissements ; auberge : une sollicitation refusée. Défiances directes inchangées. |
| Ilse au guet sec, Aubin dans la crypte, positions connues cohérentes (crue) | Observations inégales, rencontres ordinaires | Deux avis rapides, un long ; deux adoptions dans chaque groupe, témoins compris. Aucune dispute. |

Les lots et triangles communs du Relais sont recopiés dans ses dérivés
crue/hameau/rixes ; les deux positions restent propres à la crue.

**Mesures.** 16 nuits de 4 h (1985/7/42/2024), huit de 12 h (1985/7), quatre
scénarios. Zéro plantage, usurpation ou violation signalée ; **24/24 états et
rendus identiques après recharge**. Aucune boucle motrice établie ; les
observations de noir/attente persistent. Deux alertes examinées : dix lectures
de méfiance de Rémy par Odon (mine 42, sans bascule), six annonces d'eau
normalisées d'Aubin (crue 1985, hauteurs/dates distinctes, une annonce connue).

S/F/D moyens à 12 h, **historique → branche**, deux nuits par scénario :

| Scénario | S | F | D |
|---|---:|---:|---:|
| Relais | 18 → 18 | 5 → 4,5 | 2,25 → 2,13 |
| Mine | 65 → 51,5 | 7 → 7,5 | 3,14 → 2,57 |
| Auberge | 69 → 61,5 | 5 → 5,5 | 2,50 → 2,56 |
| Crue | 26,5 → 23,5 | 5,5 → 6,5 | 3 → 3,25 |

Offres/acceptées : **18/2 → 11/0** à 4 h, **40/3 → 28/0** à 12 h.
À 12 h : promesses **4 → 6**, toutes refusées `garde` ; tâches payées proposées
**47 → 53**, aucune acceptée/tenue ; commissions sollicitées/acceptées/abouties
**0/0/0 → 5/4/2** ; avis/adoptions **9/2 → 1/2** ; disputes **0 → 0** ; services
crédités **2 → 5**, dont trois repas de Mathe à Lucien. Les deux réparations
ci-dessus sont attestées par `recours_services` et les effets perçus.

**Tests.** Suite unique : **2 291 tests, 264 fichiers, 16 ignorés, 2 238,67 s** ;
74 échecs et six erreurs bruts avant adaptation des scènes. **80 méthodes
ciblées**, puis six et une reprises finales : **bilan consolidé vert**, sans
seconde suite. Deux tests nouveaux couvrent sept créations/recharges et trois
marchés (part, pièces, vivres/pulsions conservés, parole et besace rechargées).
Les **24 descriptions, besaces et sons** restent identiques après recharge ;
les deux réparations naturelles et les sept états moteur contractuels sont
également vérifiés. Créneau dépassé par l'audit et les vérifications demandées.
Les scènes contractuelles historiques retrouvent leurs entrées exactes avant
186 ; justification de chaque fichier dans
[`tests/fixtures/README-occasions-186.md`](../../tests/fixtures/README-occasions-186.md).
Le banc, le récit, les parts connues et la scène perçue conservent les données
courantes et vérifient leurs nouvelles issues.

**Limites.** Classificateur S/F/D du lot 183 repris littéralement, dix familles,
PNJ inactifs compris ; détail 4 h et par PNJ dans `richesse.json`. Références
rapides : cache complet `219bc8d` ; longues : archives `ee835d2`, jamais rejouées.
Leur code diffère de la base : écarts descriptifs, pas de delta causal ni de
garantie générale d'absence de régression ; aucun temps du cache comparé.
Empreintes modifiées comme attendu. Gain de richesse partiel : ni offre ni
promesse autonome acceptée, et les deux prévisions contraires étayées demandées
pour les disputes ne sont pas établies. Aucune clé de signature Git configurée.
