# Lot 236 — ne pas greffer un ancien recours sur un but tenu

28 octobre 2026, branche `codex-navettes-garde`, non fusionnée, base `ecbf1a1`.
Diagnostic `6bed2a0`, correctif `3f217d0`. Extension à `plan_recours` et son
raccord dans `deliberation.choisir` autorisée par le superviseur. Aucun changement
de `recours`, des registres négatifs, des services protégés ni du MJ ; aucun Luna.

**Cause et invariant.** Un résultat ordinaire vide signifie « but tenu sans
geste », pas « aucun moyen trouvé ». Le raccord transmettait pourtant `[]`
dans les deux cas. Une contre-offre ancienne, associée au même besoin, remplaçait
alors le résultat d'un autre but. `plan_recours` reçoit désormais `None` pour
l'absence de solution ; une liste reste le résultat du but choisi. Tout résultat
ordinaire sans faute est prioritaire, même vide. Un recours reste possible après
absence de solution ou moyen sans témoin ; offres, prix et refus restent retenus.
Aucune règle propre au gardien, au scénario ou au bien demandé.

**Reproduction**, priorité réduite, une nuit à la fois : auberge 7, départ tiré,
joueur au dortoir ; `4306c14` détaché, puis intégration `ecbf1a1`. Captures 415/435,
choix avant/après, plans et croyances archivés. Sur la référence :

| Minute | Cause du départ ou du retour d'Anselme |
|---|---|
| 420–421 | Lanterne recherchée, ballot découvert déplacé, puis remis au poste. |
| 422–423 | Pas de navette commerciale relevée. |
| 424–425 | Poêle à rétablir ; demandes de lanterne et d'huile, contre-offres à 425. |
| 426–428 | Retour au poste et démarches autour du poêle. |
| 429 | Garde vide remplacée par l'achat d'huile chez Joss ; quatre passages. |
| 430 | À l'étable avant l'achat, reconstruction du retour ; au poste, réinjection de l'achat ; sept passages. |
| 431 | Même inversion depuis la cuisine ; sept passages. |
| 432 | Même inversion depuis l'étable ; sept passages. |
| 433 | Même inversion depuis la cuisine ; sept passages. |
| 434 | Même inversion depuis l'étable ; sept passages. |
| 435 | Nouvelle inversion depuis la cuisine ; capture finale. |

Même garde `chambre_chaude`, née à 429, aucun geste manqué ni déplacement cru
de la charge. La fonction de garde rend bien `[]` au poste ; c'est le recours
commercial qui injecte l'achat. Nouvelle nuit actuelle : aucun passage entre
426 et 435, garde née à 426. Mais la capture historique rechargée sur le moteur
actuel reproduisait encore la greffe avant correction.

**35 tests ciblés verts** : 32 existants (47,044 s), trois nouveaux (5,967 s).
Les appels isolés « pas de solution » passent de `[]` à `None`, assertions
conservées. Capture historique : retour achevé, aucun nouveau départ sur six
minutes. Brune au Relais : contre-offre alimentaire sans greffe sur sa garde,
argent conservé. Monde complet identique en bloc ou par minute ; état et rendus
public/de scène identiques après sauvegarde/recharge. Achat de clé sans second
jet conservé ; service conditionnel poursuivi par le moteur toujours vérifié.

**Banc rapide : vingt paires de 4 h**, cinq scénarios, quatre graines, contre
`ecbf1a1` ; références manquantes calculées une fois et rangées. Aucun plantage.
Ordre Relais/mine/auberge/crue/hameau : suspects 219 **0/0/2/0/0 → 0/0/2/0/0**,
sans hausse par nuit ; maxima PNJ/heure **9/11/17/62/22 → 9/11/17/62/22**.
Cycles **507 → 507**, préemptions **58 → 58**, entrées à expliquer **87 → 87**.
Dix-huit états finaux identiques ; seuls auberge 1985 (chronique identique) et 7
diffèrent. Auberge 7 : proposition de Mireille absente à 187, recherches
**1 078 → 1 070**, dérives ouvertes **8 → 9** ; réserve conservée. Temps non comparés.

**Suite complète unique : 2 524 tests / 292 fichiers, 3 643,527 s**, un échec,
zéro erreur, 16 ignorés ; **suite non verte**. Le seul échec, torche hameau 1985
(`test_detecter_changements_avis`), est reproduit seul sur `ecbf1a1` (16,293 s) :
même réussite à 3188 et perte fautive à 3615. Aucun oracle modifié pour l'effacer.
Deux travailleurs réduits au plus ; créneau dépassé par les vérifications.
Pas de garantie sur toutes les causes de navette, ni mesure des 246 passages de
l'heure historique entière ; la nouvelle nuit n'est suivie que jusqu'à 435.
Bruts : `C:/Users/msics/donjon/artifacts/navettes-236/`. Les déplacements manuels
du script causal isolent l'injection ; ils ne valent pas test de nuit corrigée.
