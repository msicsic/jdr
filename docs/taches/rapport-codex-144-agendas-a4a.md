# Lot 144 — A4a partiel, activation et informer

Branche `codex-agendas-a4a`, non fusionnée, base `8ec3ace` du lot 140
`codex-captivite` : dépendance voulue. Aucun fichier du worktree d'intégration modifié.

## Invariant et réalisation

Un projet déclaré persiste dans l'esprit ; son état et sa cause sont enregistrés, son score
et son plan ne le sont jamais. Tout accès est dans `agendas.py`. `actualiser` active une seule
fois, borne à trois actifs, garde les causes d'échéance/supplantation, atteint après parole
transmise. Une croyance nouvelle autorise un essai ; le réveil attend un plan admissible,
sans bascule actif/sommeil quand l'obstacle persiste. Une simple nouvelle date d'observation
ne suffit pas. Les esprits sans déclaration gardent exactement leurs champs.
`esprits` accepte le champ facultatif ; la validation de profil admet les déclarations.

`deliberation._candidats` place le projet sur le palier des besoins pressants, derrière
désespoir/alarme/eau ; poids courant par valeurs/situation/affection, échéance et stabilité
du projet selon VOL. Les besoins déjà poursuivis bénéficient d'INERTIE. `planifier` choisit
le destinataire le plus proche sur les routes crues, puis passe une condition de salle à
`chercher`, avec `endurer` (règle commune `_endure`). Il n'utilise jamais sa position réelle.
La parole finale utilise `echanges.executer` ; ajout du contenu avis, réception et dispute
par `social`, sans toucher aux fichiers MJ réservés. Les faits pris en charge sont les
affirmations sujet/attribut/valeur déjà crues, les avis ceux de menace d'un lieu (3f existant).
La fin exige `social.transmission_attestee`, une preuve positive ; l'abstention du registre
plein ne suffit jamais à déclarer un destinataire informé.
Gorm reçoit en données l'objectif de prévenir Ilse et Brune de la menace du refuge.

## Vérifications

Deux processus de calcul au plus, priorité réduite, aucun Luna. Les premiers lancements
sandboxés ont échoué sur les droits des répertoires temporaires des sous-processus ; les
tests sont ensuite exécutés avec l'autorisation d'exécution hors bac à sable.
Suite complète unique : **2 105 tests, 231 fichiers, 1 169,75 s**, deux échecs MiMo
historiques `6 != 5` (`fournisseurs_jeu`, `restes_fusions`), zéro erreur. Les deux tests
ajoutés après son lancement sont couverts par la reprise ciblée finale, pas par ce compte.
**40 ciblés consolidés verts** : activation, garde AST, social, avis et disputes. La première
reprise trouvait un placement d'auteur hors du sol dans le nouveau test ; correction du
placement seulement, puis les **six tests d'activation verts** en 0,76 s. Gorm prévient
Ilse et Brune et s'arrête atteint ; trois minutes d'un bloc ou en six laps, même `data`
et rendu rechargés. Aubin transmet un avis, Gorm une affirmation : état, preuve de parole,
ouïe et rendu rechargés. Sommeil/réveil sans position crue, désespoir, plafond, activation
unique et registre plein contrôlés. Traces dans `artifacts/agendas-144/`.

Empreintes de 2 h : **12/12 nuits strictement identiques** à `8ec3ace`, Relais/mine/auberge
× graines 1985/7/42/2024, chronique, mesures et `data` complet. Douze références manquantes
calculées une fois puis cachées ; aucune référence rejouée. Après le banc, correction du
réveil et extension du palier désespéré aux gardes : **11 ciblés verts**, puis **10 tests
activation/échelle verts (36,57 s)**, sans seconde suite. Les changements finaux ne concernent
que les porteurs d'agendas ; les empreintes hors crue précèdent cette reprise.

Banc rapide crue, 4 h × quatre graines : zéro plantage/usurpation/violation, mêmes deux
observations historiques (`voir_alterne`, `eau_longue`). Le premier passage révélait neuf
alertes de répétition de réveil : correction du cycle commun, puis branche seule rejouée,
**quatre références cachées réutilisées** ; aucune répétition nouvelle au passage final.
Moyennes : attente urgente **22,50 → 20,00 min**, eau **123,75 → 128,75 min**, maximum
de passages horaires **17,50 → 13,25**, au sec à la fin **3,5 → 4 PNJ**. Ilse/Brune à la
galerie à 4 h : **1/8 → 3/8 présences** ; ce n'est pas une preuve d'arrivée avant l'eau.
Gorm atteint son objectif d'information à 144 min sur 1985 ; il reste en sommeil, contenu
non cru, sur 7/42/2024. **L'évacuation générale n'est pas acquise.**

`mesure_cout.py`, crue 1985, 4 h, départ fixe, base puis `36d2b82`, une fois chacune :
recherches **1 475 → 1 459**, neuves **1 195 → 1 089**, nœuds **101 145 → 89 838** ;
CPU instrumenté indicatif **23,05 → 20,08 s** sur poste partagé. Nuits différentes :
aucune mesure isolée du surcoût ni garantie d'une recherche supplémentaire au plus.

## Limites et suite

Livraison partielle explicitement permise : **activation + informer**, pas `amener` ni
évacuation accompagnée. Les autres noyaux événementiels de nouvelles ne sont pas encore
des paramètres de cette sorte. Restent l'impossibilité crue comme cause d'abandon, les manières
générales, une condition vocale dans le graphe (actuellement condition de salle puis parole
revalidée à l'exécution), et le plafond d'une recherche supplémentaire par choix. Le réveil
ne suit pas encore les seules relations nouvelles. Les engagements historiques ne sont pas
convertis en projets. Le poids est une première règle commune, sans calibration individuelle.
`garder`/`protéger`, s'interposer et le remplacement de l'aiguillage `retenu` par l'hystérésis
générale dans le score restent à faire. **A4 et l'invariant complet du brief ne sont pas acquis.**

Aucune clé de signature Git configurée ; commits non signés, branche poussée seulement,
sans fusion ni modification de `main`.
