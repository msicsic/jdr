# Lot 229 — Régressions des tests après le réessai causal

28 octobre 2026. **Branche `codex-reessai-regressions`, non fusionnée**,
base `1e09926`. Tests et documentation seulement ; aucun moteur ni MJ
modifié, aucun Luna. Deux calculs simultanés au plus, priorité réduite.
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

**Prémisse de vente explicitement changée**, pas la nuit ni les ressources :
après huit heures, dans la scène préparée pour Corvus, Odile accepte de ne
garder qu'**une part** pour elle. Contrôle avant demande : ni usage
nécessaire ni garde de réserve. On exige la livraison, la pièce payée,
la perte d'exactement une part du lot, la recharge et la perception après
rechargement. La valeur absolue `2` est remplacée par `charges_avant - 1`
car la nuit peut déjà avoir détaché une part. La part suivie est celle
créée par la vente, pas celle préparée pour Lucien. Aucune huile ajoutée ; aucune assertion
de paiement, possession ou lumière retirée.
Les cas auberge/mine du même fichier vérifient aussi refus à la réserve,
vente du surplus, monde et rendu rechargés.

**Vérifications et limites.** Première passe : 36 ciblés verts en 396,162 s.
Suite complète finale unique : **2 498 tests / 289 fichiers, 3 637,727 s**,
**un échec, zéro erreur, 16 ignorés** ; les **45 tests des cinq fichiers
ciblés sont verts**, dernières assertions comprises. Seul échec :
`test_constater_rumeurs...test_le_joueur_qui_ne_les_connait_pas_n_entend_que_des_voix`
(Mathurine en plus), identique au relevé antérieur
`artifacts/integ-225/suite.log`, laissé intact. **Suite non verte.**
Scène de vente révisée rejouée sur la capture réelle `881db69`, avec son
moteur historique : vente, nouvelle part, recharge et rendu verts, sans
rejouer la nuit. Pas de seconde suite complète ni de banc rapide (moteur
inchangé). Créneau dépassé par les vérifications, dont une heure de suite.
Aucune garantie générale d'absence de boucles au-delà des entrées examinées.
La garde compte le lot demandé ; le traitement de la part séparée après
annulation reste hors de ce lot (échanges/biens réservés au 228).
