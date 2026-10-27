# Lot 186 — Occasions asymétriques

`codex-occasions-asymetriques`, non fusionnée ; données/tests `0bfa49a`, branche
comparée `16c0ff1`, base exacte `12a936d`. Aucun `donjon/*.py`, trait, valeur,
garde, réserve, pulsion, agenda ou bien matériel historique modifié. Aucun Luna ;
deux travailleurs réduits au plus. Bruts :
`C:/Users/msics/donjon/artifacts/occasions-186/`.

| Donnée → mécanisme visé | Effet observé |
|---|---|
| Quatre galettes portées par Gorm/Mathe/Odile, prix 2 → marché, paiement, don | Trois marchés du joueur validés ; service Odile/Joss à 657 min (auberge 7), méfiance conservée. |
| Deux charges de bois propres à Brune/Odon/Joss, foyer connu → promesse, service | Crue 1985 : Brune recharge à 496, méfiance levée, repas à 498 ; recours enregistré. |
| Affection Gorm → Aubin, Mathe → Josse, Odile → Mireille à 60, sourire interprété connu → commission | Une commission aboutie à 4 h ; deux dans les nuits longues. Défiances directes conservées. |
| Ilse au guet sec, Aubin dans la crypte → observations inégales | Deux adoptions à 4 h comme à 12 h, aucune dispute. |

Les lots et triangles communs sont recopiés dans les dérivés du Relais. La faim
du propriétaire peut toujours rendre un nouveau lot incessible.

**Comparaison finale à base identique.**
`tools/comparer_bancs.py --reference 12a936d --scenarios relais mine auberge crue
--graines 1985 7 42 2024 --heures 4 --processus 2`. **16 paires**, départ tiré,
mêmes salles passives ; 16 références calculées une fois puis rangées dans le
cache commun, 16 nuits de branche rejouées. Moteur et outils strictement
identiques entre les deux commits. Aucune modification de données pendant ce
complément ; aucun temps comparé.

S/F/D : moyennes du classificateur exact du lot 183, dix familles, PNJ inactifs
compris. Propositions/acceptations : sommes sur quatre graines, promesses incluses.
Toutes les flèches ci-dessous vont de **12a936d → branche**, à **4 h** uniquement.

| Scénario | S | F | D | Propositions / acceptées |
|---|---:|---:|---:|---|
| Relais | 3 → 3,75 | 2 → 1,5 | 0,625 → 0,563 | 0/0 → 0/0 |
| Mine | 13,5 → 10,5 | 4,5 → 4,25 | 1,286 → 1,036 | 10/1 → 3/0 |
| Auberge | 6,5 → 6,25 | 2,75 → 2,75 | 0,625 → 0,594 | 3/1 → 3/0 |
| Crue | 10,75 → 11,5 | 5,5 → 5,75 | 1,75 → 2 | 5/0 → 5/0 |

**Comptes des 16 nuits.** Propositions **18/2 → 11/0**, dont offres matérielles
**17/2 → 11/0** ; promesses **1/0 → 0/0**. Tâches payées
proposées/acceptées/tenues **3/0/0 → 11/0/0** ; commissions
sollicitées/acceptées/abouties **0/0/0 → 1/1/1** ; avis/adoptions **11/2 → 2/2** ;
disputes **0 → 0** ; services crédités **3 → 3**. Les achats ordinaires,
**15 → 20**, sont exclus des dix familles S/F/D ; ce compteur auxiliaire ne
change pas la définition de S/F/D.

**Pourquoi les baisses persistent.** Les deux marchés acceptés ne sont plus
proposés, plutôt que devenus refusés :

- **Mine 7** : Odon cédait ses outils à Mathe contre des vivres à **13 min** ;
  il reçoit désormais une galette à **0 min** par demande ordinaire. Trois
  signatures de proposition disparaissent ; S **11 → 10** après les ajouts.
- **Auberge 42** : Lucien obtenait la besace d'Anselme contre ses crochets puis
  mangeait son contenu à **212 min** ; il reçoit une galette d'Odile à **213**.
  Son offre ultérieure vise le ballot, refusé `necessaire`. S reste **9 → 9**,
  mais l'acceptation disparaît.
- **Mine 2024** : S **17 → 9**, soit huit des douze signatures perdues en net
  dans les quatre mines. Odon et Gaspard reçoivent les galettes dès **0/1 min** :
  quatre signatures de propositions alimentaires et les interpositions de Josse
  et Mathe disparaissent. **Mine 1985**, S **17 → 14** : la promesse refusée de
  Josse à 205 min disparaît, après une demande de galette accordée à 191.
- **Auberge 7** explique seule son −0,25 moyen : S **6 → 5**. À 123 min,
  Tilo reçoit directement la soupe de Mireille au lieu de la livraison de vivres
  par Odile : la signature « Odile appelle Tilo et lui donne… » disparaît.
  Joss achète ensuite sa soupe à 157 au lieu d'une demande accordée.

Les mines divergent dès **0 min**, les auberges entre **9 et 17 min**. Ces
substitutions ne prouvent pas l'effet indépendant de chaque ajout : **parcours
alimentaires raccourcis, moins de négociations, gain social partiel**.

**Audit des paires.** Zéro plantage, usurpation ou violation signalée.
`fige_presse` **5 → 4**, `noir_long` **1 → 1** ; nouveaux `repetition` (Odon,
mine 42 : dix lectures de méfiance, sans bascule) et `voir_alterne` (Gorm,
crue 2024 : une alternance). Quatre bascules isolées de chaque côté, aucune
boucle motrice nouvelle établie. Détails par nuit et PNJ :
`richesse-base-identique.json` ; signatures perdues/ajoutées et premiers écarts
inclus. Séquences probantes : `episodes-base-identique.json`. Rapport moteur
complet : `comparaison-base-identique.json`.

**Validation initiale conservée.** 24 recharges complètes identiques, deux
réparations prouvées. Suite unique : 2 291 tests, 16 ignorés, bruts 74 échecs/six
erreurs ; 80 ciblés puis six et une reprises, **bilan consolidé vert**.
[Entrées contractuelles justifiées](../../tests/fixtures/README-occasions-186.md).
Aucune suite ni nuit de 12 h relancée. Les anciens écarts contre `ee835d2` à
12 h restent **non attribuables** aux données : la comparaison à 4 h ne les
valide pas. Les deux prévisions contraires nécessaires aux disputes restent absentes.

**Livraison.** Le superviseur a poussé `16c0ff1`. Ce complément reste commité
localement pour sa poussée ; aucune clé de signature Git configurée.
