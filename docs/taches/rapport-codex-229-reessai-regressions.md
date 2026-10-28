# Lot 229 — Régressions des tests après le réessai causal

28 octobre 2026. **Branche `codex-reessai-regressions`, non fusionnée**,
base `1e09926`, première livraison `ad785cf`, puis merge demandé de
`origin/integration` **`c9d8c05`** (230/231), sans rebase. Le 229 ne modifie
que tests/documentation ; moteur de 230 repris intact, aucun MJ ni Luna. Deux calculs simultanés au plus, priorité réduite.
Bruts : `C:/Users/msics/donjon/artifacts/reessai-229/`.

**Lucien : comportement juste.** Comparaison avec `346c1aa`, même scène
`lucien_au_grenier_noir`, pas de cinq minutes avec rechargement : première
sélection différente à **95 min, 0 dixième**. L'ancien code réadopte le vol
du ballot après les 60 minutes suivant son abandon à 35 ; Anselme est
pourtant toujours cru dans la chambre. Le nouveau conserve la cause
`temoins`, crochetage du coffre, Anselme et Hugues, bruit `bruyant`.
Il reprend à **107 min 228 dixièmes**, après avoir entendu Anselme dans la
salle commune et vu Hugues dans cette salle. Nouveau renoncement à 139
(Anselme cru présent), puis reprise à **167 min 90 dixièmes**, après avoir
entendu Anselme au couloir. Les retours sont donc précédés d'une nouvelle,
non autorisés par le seul temps ou l'obtention d'une lampe.

**Oracle de garde explicitement réancré : 150 → 165 minutes.** L'ancienne
fenêtre 130–150 coupe le trajet chambre → cuisine → grenier. La fenêtre
145–165 reste au grenier ; cinq changements de salle depuis le départ
(limite de six conservée). L'assertion conditionnelle sur la lanterne est
remplacée par des exigences : but `garder/grenier`, bougeoir de Mireille
porté et allumé, lumière effective, état complet et rendu identiques après
rechargement. À 95 min, le test contrôle aussi que la cause reste opposable
et que le vol n'a pas repris. Le cas de Bram conserve l'autre preuve de
lumière ramenée à la garde, dans la mine ; les cas causaux de 225 couvrent
le laps entier/découpé, les témoins et un passage obstrué.

**Huile : refus historique juste, réserve nécessaire.** Première divergence
entre `346c1aa` et `881db69` : **222 min, 0 dixième, Lucien**. Après
renoncement devant Anselme et Hugues, il adopte l'inspection périodique du
grenier (autre but/moyen), quand le verrou temporel sur tous les buts
`biens` le laissait sans plan. À **464 min**, il demande une part d'huile
à Odile pour éclairer sa garde. Une part est détachée, puis la promesse
est annulée à 466 ; la part séparée reste chez Odile. Le lot garde
à huit heures **2 parts**, soit
exactement sa réserve de **2** : `garde` déclenche donc justement
`necessaire`, même sans plan actif (`necessaire(...)` seul vaut faux).
Rejeu exact du test en un bloc sur copie de `881db69` : refus reproduit ;
vente sur la capture de l'intégration actuelle, qui garde trois parts.
Sur `881db69`, état complet identique en bloc et par relevés de cinq minutes.

**Après 230, le test d'huile passe inchangé.** Le fichier final est
strictement identique à `c9d8c05:tests/test_lampes_parts.py`. Le test renommé
`...recharge_une_lanterne_a_sec` conserve la nuit de 480 min et la déclaration
230 de la lanterne à sec et au contact. Il passe sur le moteur fusionné
**sans changer la réserve d'Odile** : une passe, 194,531 s. Aucun changement
229 de ce fichier n'est retenu. Le refus de `881db69` reste justifié par
la cause établie ci-dessus ; une nuit différente ne rend pas ce refus faux.

**Vérifications et limites.** Avant 230, suite complète unique sur
`ad785cf` : **2 498 tests / 289 fichiers, 3 637,727 s**, un échec, zéro erreur,
16 ignorés ; 45 tests des cinq fichiers ciblés verts. Seul échec :
`test_constater_rumeurs...test_le_joueur_qui_ne_les_connait_pas_n_entend_que_des_voix`
(Mathurine en plus), identique au relevé antérieur
`artifacts/integ-225/suite.log` ; **suite non verte avant 230**.
Après merge : **34 tests verts / quatre fichiers, 225,369 s**, plus le test
d'huile exact de 230 vert, soit **35 ciblés verts**. Aucune seconde suite
complète ni nouveau banc : 229 n'a aucun fichier moteur commun avec 230.
Créneau dépassé par les vérifications, dont une heure de suite avant merge.
La garde compte le lot demandé ; la part séparée après annulation relève
des échanges/biens réservés au 228. Pas de garantie universelle des boucles.
