# Lot 314 — achat promis après annulation

Branche `codex-achat-promis`, base `integration c4f6d46`.
**Lot terminé, vérification validée sur le moteur `b7b6bf8`.**

**Cause et invariant.** Une livraison annulée reste dans `agendas.en_cours`
jusqu'à l'annonce de son abandon. `_remettre_part` prenait cette inscription
pour une livraison encore due et retournait `promis`. `echanges.executer`
publiait alors un accord et effaçait les refus du demandeur ; celui-ci
rechoisissait le même achat, sans paiement ni progrès. La voie commune de
livraison de parts transmet désormais la cause d'annulation enregistrée.
L'exécution mémorise ce refus selon ses moyens ou son échéance habituels.
Pas de délai ajouté, de nouvelle mémoire, de règle de scénario ni de
modification des données du hameau ; réclamations du lot 315 inchangées.

**Preuve réelle.** Capture 306/reprise-309 `0038-23110-aubin`, rechargée à
38 min, avant t=36582, conservée sans retouche dans les tests. Rejeu de
30 min avec la fonction de base chargée en mémoire : **28 achats promis**
entre t=36582 et 39282, aucun paiement. Même capture corrigée : **un refus
à t=36477, zéro achat**, aucun nouveau prélèvement ou paiement ; annulation
ensuite annoncée et retirée. Le monde entier est identique entre un laps
de 30 min et trente laps de 1 min, recharges intermédiaires comprises.
Les observations visibles ont la même multiplicité ; leur ordre varie avec
le regroupement du bilan des présences à la fin de chaque action joueur.
Monde, rendu et scène identiques avant/après sauvegarde et recharge.

**Autre scénario.** Auberge : Odile promet une part d'huile à Joss,
constate la perte de la part réservée, puis annule par le cycle commun.
Un achat préparé reçoit `impossible`, retenu et non répété durant cinq
minutes ; ni argent, ni charge supplémentaire consommée, ni source allumée.
Laps entier/découpé, monde/rendu/scène rechargés contrôlés aussi. Les deux
causes d'annulation, demande gratuite/achat, livraison active puis soldée
sont couvertes. **Quatre nouveaux tests verts, 24,699 s**, un travailleur
réduit. La sonde de reproduction utilise les instants, car la chronique
est bornée ; ses premiers résultats vides ne sont pas une preuve retenue.

**Vérification achevée.** **49 tests / six fichiers verts**, sans échec,
erreur ni saut, 285,625 s : nouveaux tests, parts achetées, lampes/parts,
tâches payées, socle des agendas et refus retenus. **16/16 paires
d'empreintes 2 h identiques**, Relais/mine/auberge/crue × 1985/7/42/2024
contre `c4f6d46` : chronique, mesures et état final complet ; mêmes avis,
aucun plantage. Seize références absentes calculées une fois et rangées,
puis seize nuits de branche.

**Hameau avec le 306, 4 h × quatre graines.** Fusion locale de
`0a12fd1` dans un worktree temporaire, supprimé après mesure ; données du
306 contrôlées identiques, absentes de la branche livrée. Les quatre nuits
de référence archivées du 306 sont réutilisées, sans relance. Les écarts
de source antérieurs sont le tri des mesures 310 et l'interface de
fabrication 305, sans entrée dans la simulation PNJ ; diff brut conservé.
En **graine 7, les 28 achats promis ont disparu sur toute la nuit** : une
seule demande de part, refusée à **t=36477**, aucun achat d'Aubin ni paiement.
La sonde retrouve la livraison de minute 0 annulée et reçoit `impossible` ;
**zéro accord sur annulation** dans les quatre nuits. Suspects 219
**0/0/0/7 → 0/0/0/7**, avis à expliquer **7/5/0/10 inchangés**, aucun
plantage ni constat d'usurpation. Les graines 1985/42/2024 gardent les mêmes
chroniques, mesures et empreintes finales ; seule la graine 7 change.

**Limites des résultats.** En graine 7, dérives ouvertes **31 → 33**,
tentatives de vol **1 → 2**, minutes dans le noir **15 → 65**, mandats
proposés **5 → 2** ; ces conséquences ne sont pas certifiées bénéfiques.
Les deux alertes grossières de répétition restantes sont antérieures au
refus (agendas Aubin/Gorm), déjà présentes dans la référence. Les sept
suspects de Sève en 2024 restent au lot 315. Pas de preuve universelle
d'absence de répétition de toute parole ; un refus suit la réévaluation
commune existante et une nouvelle demande après clôture peut établir un
nouvel accord.

Calcul détaché, deux travailleurs réduits au plus, séquences successives,
**969,696 s** au total ; aucun temps comparé aux références archivées.
Ni Luna ni suite complète, aucun calcul actif. Bruts :
`C:/Users/msics/donjon/artifacts/achat-314/` (`fin.json` : **ok=true**,
codes tests/empreintes/hameau **0/0/0**, `analyse-cloture.json`).
Rapport et état de développement complétés, branche poussée vers origin.
