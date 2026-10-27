# Lot 185 — une observation borne la prévision d'eau ancienne

27 octobre 2026, PC fixe, branche `codex-prevision-bornee`, **non fusionnée**,
base `integration 4efb277`. Aucun Luna ni fichier réservé au lot 184 modifié.
Bruts exclusivement `C:/Users/msics/donjon/artifacts/prevision-185/`.

**Invariant.** `eau.borner` abaisse une droite de montée extrapolée lorsqu'une
observation postérieure la contredit : niveau vu pour une mesure, plafond à
l'altitude pour un sol sec. La vitesse et ses deux repères restent inchangés.
Le niveau commun est borné, donc aussi ses projections dans les autres salles,
sans lire leur eau cachée. Sans preuve contraire, la prévision demeure.
`estimation` et `esprits.prevision_propre` partagent cette borne ; la provenance
propre inclut la preuve du plafond. Une prévision quantitative reçue suit la
même borne à la lecture, sans transformer un avis en observation. Les avis
qualitatifs restent une menace future sans profondeur. `attendue`, les routes,
`Vue.descente` et les coefficients de `_entrees` suivent la même lecture ;
aucun changement des algorithmes de recherche ni format de sauvegarde.

**Captures 182, relues sans reproduction.** Sève 345, Ilse 420 et Maël 450 :
ancienne lecture restaurée temporairement sur copies, puis correction ;
routes précédemment refusées rétablies, plan alimentaire de Sève/Ilse et abri
de Maël disponibles. Sève et Ilse regagnent le refuge ; Maël atteint la galerie
à 451, puis retourne auprès de Gorm à 453. Dix minutes d'un bloc ou minute par
minute : monde complet et rendu identiques après sauvegarde/recharge.
Trois entrées exactes 343/418/448 : état, rendu et plans également relus.
Les scripts et résultats restent dans `captures185.py` et `captures.json`.

**Vérifications.** **38 ciblés finaux verts**, dont les routes réellement menacées
des lots 41/58 et les avis du lot 80 ; cinq tests nouveaux, deux PNJ,
preuve sèche dans une autre salle de crue, niveau mesuré, pente persistante,
absence de preuve contraire, avis sans pente propre, clé et sauvegarde/rendu.
Le réancrage exact à la borne évite une trace d'eau positive par arrondi.
La capture historique crue 7 du test de coût retrouve aussi son recours ;
le test compare désormais les plans et la continuation avec/sans cache.
**12/12 empreintes 2 h** Relais/mine/auberge × quatre graines identiques aux
archives finales du lot 181 : état complet, chronique, mesures, récit,
souvenirs, empreintes internes ; monde et rendu rechargés identiques.
Aucune référence rejouée, aucun temps du cache comparé.

Bancs rapides **4 h × quatre graines**, attente/eau/noir en PNJ·minutes,
passages = moyenne des maxima PNJ/heure :

| Scénario et référence relue | Attente | Eau | Noir | Passages |
| --- | ---: | ---: | ---: | ---: |
| Hameau, lot 181 | 31,25 → 31,25 | 15 → 15 | 76,25 → 76,25 | 23,75 → 23,75 |
| Crue, cache `main 812ebe5` | 20 → 17,5 | 128,75 → 17,5 | 82,5 → 55 | 13,25 → 20 |

Aucun plantage/usurpation ni nouvelle alerte de boucle ; observation historique
`fige_presse` de Gorm hameau 1985 conservée. **La référence crue précède la
base du lot** : ses écarts ne sont pas attribuables au seul correctif 185.
Le hameau reste identique sur ces quatre premières heures ; les captures
tardives prouvent la correction du défaut diagnostiqué.

**Suite unique : 2 293 tests, 264 fichiers, 1 464,334 s**, trois échecs bruts,
aucune erreur ni test ignoré : deux MiMo historiques `6 != 5` et l'ancienne
attente « aucun plan » de la capture crue 7, adaptée au recours rétabli.
L'attente adaptée et le réancrage passent dans les 38 ciblés finaux ; les
captures et bancs affectés sont repris, sans seconde suite complète.
`VERIFIER` + spatial 0,2, crue 2024/hameau 42, 2 h : reprise finale terminée,
zéro écart/plantage. Au plus deux calculs, priorité réduite.
Aucune clé de signature configurée : commit non signé. Livraison sur la
branche seule, sans fusion ni modification de `main`.

**Limites.** Une observation sèche ne mesure pas la décrue ; la montée
historique reste extrapolée après cette preuve. Les anciennes observations
d'eau présente restent un minimum cru jusqu'à révision. Ni l'accès durable
aux ressources, ni la fin générale des attentes/navettes ne sont garantis.
