# Lot 233 — entendre le compagnon et reconsidérer l'occasion

28 octobre 2026. Branche `codex-pas-compagnons-c`, **non fusionnée**. Base
`adb52c4`, fusion du 195 `cf777e7` dans `241a38b` ; seul conflit documentaire.
**Candidat livré avec critères incomplets**, aucune garantie de richesse préservée.

**Invariant d'attention, raccord dans `ouie.entendre`** : expliquer un bruit ordinaire par
une présence crue dispense de se retourner, pas de lui prêter attention.
Après l'attribution, `esprits.reconsiderer` réveille le choix commun, sans
rotation, temps de geste ajouté, nouvelle position ni connaissance de l'auteur
réel. Une compatibilité de marche seule ne rajeunit toujours pas la preuve.
Présence crue, audibilité réciproque et identification restent celles de
`pnj.pourraient_se_parler` / `se_parler` et de l'accueil commun. Aucun raccord
hors périmètre ; `echanges.tenu` hérité du 195 reste intact dans cette reprise.

**Interactions perdues du 195, hameau 1985/42, quatre heures.** Relecture des
signatures et rejeu instrumenté de `346c1aa` ; exemples absents du candidat 195 :

| Graine, instant (dixièmes) | Interaction | Perception de référence et manque |
|---|---|---|
| 1985, 131 | Brune vend du bois à Aubin | À 50, rotation vers la voix de Maël, personne vue ; voix d'Aubin localisée `[1,5]`. Ce n'est pas une découverte visuelle d'Aubin. |
| 1985, 247 | Aubin demande des vivres à Gorm | À 207, rotation aux pas de Maël : Maël vu, lieu échoppe rafraîchi ; Gorm déjà vu. À 238, bruit attribué à Gorm, case `[4,2]`. |
| 1985, 561 | Brune promet d'allumer la torche à Ilse | Ilse vue auparavant ; à 539, bruit attribué à Ilse, case `[1,2]`, sans rotation. Perte en cascade, pas une vue manquante immédiate. |
| 42, 1039 | Brune propose la même tâche à Maël | Maël vu avant l'offre ; à 985, voix de Gorm entendue à l'échoppe, sans rotation. Trajectoire déjà divergente. |
| 42, 48672 | Ilse demande des vivres à Gorm | Rotations aux pas de Brune à 48625/48651 ; Gorm reste vu, lieu de Brune rafraîchi. Réveil sans nouveau fournisseur découvert. |
| 42, 48672 | Ilse offre deux pièces à Gorm | Même rencontre et même perception que la demande précédente. |

Ces traces excluent l'explication « chaque perte est une vue retirée » :
attributions, éveils et déplacements ultérieurs interviennent aussi. Les
préfixes rejoués sont identiques aux chroniques historiques jusqu'à la minute
30 (1985) et 147 (42), donc couvrent ces six exemples ; divergence ensuite,
aucune causalité individuelle certifiée au-delà. Les absences de signatures
ne prouvent pas qu'un besoin reste insatisfait.
Dans le banc 233, les deux promesses du tableau réapparaissent à **1 min**
(1985) et **139 min** (42) ; les quatre autres signatures restent absentes.

**Banc final : 20 paires × 4 h contre `adb52c4`**, références manquantes
constituées une fois et conservées en cache ; pas de comparaison de temps.

| Scénario | Suspects 219 | Retournements moyens | S/F/D moyens, référence → candidat |
|---|---:|---:|---|
| Relais | 0 → 0 | 68,50 → 28,25 | 10,75/4/1,563 → 12,25/4/1,500 |
| Mine | 0 → 0 | 81,50 → 22 | 26,75/5/1,893 → 25/5/1,929 |
| Auberge | 2 → 1 | 49,75 → 27,50 | 11,50/4,50/1,094 → 11,25/3,75/0,969 |
| Crue | 0 → 1 | 72,50 → 56 | 25,75/7,50/3,500 → 25,75/7,25/3,250 |
| Hameau | 0 → 0 | 116,50 → 46,75 | 35/8/2,625 → 27,75/7,25/2,375 |

Zéro plantage/usurpation. Suspects **2 → 2 au total**, mais nouvelle alerte
Aubin, crue 2024, retour au service de Brune à **23576** après demande manquée :
**absence de hausse par scénario non acquise**. Hameau : référence S
**[26–44]**, candidat **[17–37]** ; moyenne 27,75 dans l'étendue de référence,
mais **−20,7 %**, graines 7/42 à **17/24**, sous son minimum. **Richesse
restaurée non validée**, échanges acceptés **13 → 9**. Aucun réglage par PNJ
ou scénario pour atteindre le compteur.

**Tests.** 30 ciblés verts, puis **18 tests de pas finaux verts** : cas réel
Brune/Ilse hameau 1985, demande autonome d'Aubin à Gorm reconstituée au hameau
et au Relais, engagements effectifs, monde/rendu rechargés et laps découpés.
Présence sans rotation ni position inventée, inconnu anonyme et compagnon
absent couverts. **Contre-épreuve isolée** : remettre seulement `ouie.py` du
195 en mémoire sur le même moteur fait échouer les trois nouveaux tests de
rencontre/éveil (**cinq échecs avec sous-cas, zéro erreur**), cas réel compris.
**Suite complète unique : 2 542 tests / 293 fichiers, 2 925,970 s, dix échecs,
zéro erreur et zéro ignoré.** Le dernier cas ajouté est repris dans les 18
ciblés finaux ; aucun changement moteur après le banc. Le dernier fichier
de la suite, comparaison avec/sans cache spatial, passe en 702 s.
Comparaison ciblée sur `adb52c4` : **quatre préexistants reproduits** (torche,
stabilité de Lucien, deux MiMo). **Six écarts supplémentaires du candidat
195+233 restent non résolus** : empreintes mine/auberge, secours de Rémy
dans la capture 209, demande de lampe de Lucien, trajet injecté du témoin
pendant le vol, placement d'abri connu du 195 (lot 234). Oracles et assertions
historiques laissés intacts ; aucune garantie de non-régression globale.

Banc et suite à deux travailleurs réduits ; aucun Luna. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/pas-233/` (`comparaison.json`, `analyse.json`,
`perceptions-*.json`, `interactions-perdues.json`, `suite.json`,
`echecs-base*.json`, `contre-epreuve.json`, `cibles-finales.json`, `banc.log`).
Les limites du placement (234), des preuves du 195 et
des contradictions sémantiques restent hors de cette correction.
Créneau dépassé par la passe complète et son diagnostic ciblé.
