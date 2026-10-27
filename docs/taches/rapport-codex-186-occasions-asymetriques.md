# Lot 186 — Occasions asymétriques, variante finale sans galettes

Branche `codex-occasions-asymetriques`, non fusionnée ; base **12a936d**.
Retrait des lots de quatre galettes de Gorm/Mathe/Odile et de leurs connaissances,
dans les sept JSON concernés. Aucun autre changement de données par rapport à
la variante `98c2a26` : bois, liens et positions conservés ; aucun `donjon/*.py`,
trait, valeur, garde ou réserve historique modifié. Aucun Luna ; deux travailleurs
réduits au plus. Bruts finaux : `C:/Users/msics/donjon/artifacts/occasions-186/sans-galettes/`.

| Donnée conservée → mécanisme visé | Résultat observé à 4 h |
|---|---|
| Deux charges de bois propres à Brune/Odon/Joss → contrepartie, promesse, service | Odon paie son repas avec une part de bois et conserve ses outils ; trois services crédités comme sur la base. |
| Affection Gorm → Aubin, Mathe → Josse, Odile → Mireille à 60, sourire interprété connu → commission | Une commission sollicitée, acceptée et aboutie, contre aucune sur la base. |
| Ilse au guet sec, Aubin dans la crypte → observations inégales | Trois avis, deux adoptions ; pas de dispute. |

**Comparaison finale à base identique.** Même commande :
`tools/comparer_bancs.py --reference 12a936d --scenarios relais mine auberge crue
--graines 1985 7 42 2024 --heures 4 --processus 2`.
Les **16 références sont exclusivement relues en cache**, seule la branche est
rejouée. Moteur/outils identiques à la base ; empreintes des données contrôlées
avant/après mesure. Aucun temps comparé. S/F/D : définition exacte du lot 183,
dix familles, PNJ inactifs compris ; moyennes sur quatre graines. Propositions :
sommes, promesses incluses. Flèches : **base → variante finale sans galettes**.

| Scénario | S | F | D | Propositions / acceptées |
|---|---:|---:|---:|---|
| Relais | 3 → 3 | 2 → 2 | 0,625 → 0,625 | 0/0 → 0/0 |
| Mine | 13,5 → 13,5 | 4,5 → 4,5 | 1,286 → 1,250 | 10/1 → 10/1 |
| Auberge | 6,5 → 6,5 | 2,75 → 2,75 | 0,625 → 0,625 | 3/1 → 3/1 |
| Crue | 10,75 → 11 | 5,5 → 5,75 | 1,75 → 2 | 5/0 → 8/0 |

**Comptes des 16 nuits.** Propositions **18/2 → 21/2**, dont offres matérielles
**17/2 → 21/2** ; promesses **1/0 → 0/0**. Tâches payées
proposées/acceptées/tenues **3/0/0 → 10/0/0** ; commissions
sollicitées/acceptées/abouties **0/0/0 → 1/1/1** ; avis/adoptions **11/2 → 3/2** ;
disputes **0 → 0** ; services crédités **3 → 3**.

**Effet du retrait.** La variante avec galettes donnait **11/0** et S mine
**10,5**, auberge **6,25**. Le retrait restaure les deux marchés acceptés :
Odon/Mathe à **13 min** (mine 7), désormais une part des chutes de bois contre
un repas ; Lucien/Anselme à **212 min** (auberge 42), crochets contre besace,
puis repas. Les deux ne sont plus court-circuités par une demande de galette.
Le S moyen revient à la base dans la mine et l'auberge ; la commission est conservée.

Le gain n'est pas uniforme : mine 1985 reste à **17 → 14**, avec des demandes
simples accordées à Gaspard/Josse à 118/191 min remplaçant des recours, dont la
promesse refusée de Josse à 205. Les trois autres mines gagnent chacune une
signature. Crue 7 passe de **13 à 8** : huit avis distincts disparaissent,
contre de nouveaux recours matériels et travaux proposés ; les observations
et rencontres diffèrent. Ni promesse acceptée ni dispute supplémentaire établie.
Les réparations naturelles à 12 h de l'ancienne variante restent des archives,
pas une mesure de fréquence de la variante finale ; aucune nuit de 12 h relancée.

**Audit.** Zéro plantage, usurpation ou violation signalée des deux côtés.
`fige_presse` **5 → 4**, `noir_long` **1 → 1** ; nouvelles répétitions de lectures
(mine 2024 : Josse, neuf méfiances de Lucien ; Rémy, huit dépendances de Lucien)
et une alternance de Gorm (crue 7). Quatre bascules isolées de chaque côté,
pire passage **30 → 42/h** ; aucune boucle motrice nouvelle établie.

**Tests.** 25 fichiers déjà concernés : **299 tests**, bruts cinq échecs/une erreur ;
les cinq fichiers repris passent **68 tests** après explicitation des stocks
vides. Les **25 méthodes dépendantes** déjà reprises au lot 186 donnent quatre
échecs/deux erreurs bruts ; les quatre fichiers concernés passent ensuite
**42 tests** après correction des entrées de positions/bois. **Bilan consolidé vert**.
Les modifications de galettes sont retirées des tests ; les contraintes restantes
sont justifiées dans [le README des fixtures](../../tests/fixtures/README-occasions-186.md).
Le test des sept variantes joue cinq minutes puis recharge état, description,
besace et sons ; le stock alimentaire est comparé à une référence déclarée de
12a936d. Les 54 inverses contractuels restants restituent exactement la base.
Pas de suite complète : les **16 fichiers de tests modifiés** sont tous dans les
**37 déjà repris** au lot 186, périmètre prouvé dans `controle.json`, conformément
à la consigne ; aucune modification du moteur.

Détails : `comparaison.json`, `richesse.json` (par nuit/PNJ, signatures perdues et
ajoutées), `controle.json`, `cibles*.json`, `dependances*.json`.
Complément commité localement pour la poussée du superviseur ; clé de signature
Git non configurée.
