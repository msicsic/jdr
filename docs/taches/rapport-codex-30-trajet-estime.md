# Rapport Codex 30 — trajet estimé

Branche `codex-trajet-estime`, **non fusionnée**, base d'intégration `ecbbed7`
(brief `e282120`). Code signé SSH : `9f4bf2f`, `500d917`. Aucun appel à Luna.

**Invariant.** La recherche estime les trajets par salle ; seule l'exécution
mesure le parcours depuis la position réelle. `Etat` porte salle, possessions,
faits et allure ; l'allure reste nécessaire aux gestes sans témoin.
`trajet_estime` utilise la moyenne des distances métriques depuis les entrées
vers les contacts et les autres sorties ; une entrée unique emploie la moyenne
sur le sol accessible pour sortir. Ce critère conserve les différences de taille
et les détours géométriques sans multiplier les états selon l'ordre des approches.
Les tables d'`obstacles.distances` sont partagées par géométrie et obstacles crus,
avec les suppléments de franchissement, gabarit et équipement utile. Rotation
moyenne : 90°, soit 1 s, au déplacement puis au geste ciblé.
`Vue.route`, `allers`, `approche`, `trajet`, les parts et `part_estimee` passent
par ces estimations et l'unique `obstacles.cout_route` ; portes, noir et pression
restent payés par salle. `_entrees` porte le modèle et ses lectures.
`pnj.parcours`, `_marcher` et `defense.chemin_fuite` restent réels.

**Erreur.** Sur les quatre plans initiaux, graine 42, **1 898 trajets locaux**
entre points accessibles et sorties : erreur absolue médiane **3,20 s**,
pire **14,05 s** (galerie de la mine, départ déjà au seuil, durée réelle nulle).
Comparaison aux chemins métriques du monde réel, rotations internes comprises ;
occupation mobile, portes et choix global d'itinéraire exclus de cet échantillon.
Ce n'est donc pas une borne d'erreur de tout plan.

**CPU et recherche.** Trois versions démarrées ensemble, sans cache, 4 h,
graines 42/1985, un travailleur chacune afin de respecter le plafond de quatre
avec le contrôle spatial séparé ; tous les calculs à priorité réduite.

| Scénario | `42bb9c0` | Base | Branche | Branche / ancien |
|---|---:|---:|---:|---:|
| Mine, CPU moyen (s) | 7,102 | 12,484 | 11,648 | ×1,64 |
| Auberge, CPU moyen (s) | 5,992 | 12,508 | 11,109 | ×1,85 |

Nœuds par nuit, graines 42 / 1985 : mine **4 186 / 3 713 → 15 001 / 15 414
→ 7 538 / 7 896** ; auberge **3 445 / 15 147 → 23 987 / 52 300
→ 13 495 / 25 979**. Zéro recherche bornée sur ces douze nuits.
Gain CPU contre la base : **6,7 % / 11,2 %** ; **cible ×1,3 non atteinte**.
Une dominance sur la position n'apporterait plus de fusion : elle est déjà absente
de l'identité. Aucune autre dominance ni réflexion limitée ajoutée.

**Vérification.** 74 tests ciblés verts, dont deux nouveaux : Relais et mine,
même plan depuis deux positions après recharge, temps exécuté et perception
persistés ; grande salle plus chère. Suite complète unique : **1 663 tests,
quatre ignorés**, 729 s ; cinq échecs initiaux résolus, **96 tests en seules
reprises ciblées, tous verts**. Adaptations de Q : approches toujours ordonnées,
durées réelles vérifiées séparément ; détour réel à deux portes distinct de la
route estimée ; corruption du cache contrôlée sur `pnj.parcours`. Montages :
porte déjà ouverte par un PNJ, case libre pour Odile ; refus vérifiés par les
moyens nouvellement appris plutôt qu'un nombre fixe d'offres ; secours sans
rappel pour le même désarroi, indépendamment du choix d'abri.
Le contrôle d'eau a fait corriger une restriction intermédiaire ajoutée par
erreur : mêmes salles crues noyées exclues que `parcours_cru`, descente attendue
de destination jugée par `Vue.allers`. `VERIFIER` + contrôle spatial 1, 2 h,
mine/auberge 42 : aucun écart ; auberge sans borne. Une erreur de nom de salle
dans le script après la mine a nécessité la seule reprise de l'auberge.

Banc rapide : **16 nuits de 4 h** contre la base, aucun plantage, usurpation ou
violation ; bascules maximales ≤ 1 ; passages/heure maximaux Relais **9→9**,
mine **8→8**, auberge **15→15**, crue **36→32**. Les choix plus approximatifs
changent quelques interactions : sans recours mine **6,25→16,25 min**, crue
**75→75 min**, attente crue **27,5→26,25 min** (moyennes). Mine 7 : huit lectures
sociales identiques « méfiance » de Rémy sur Lucien et une alternance de but
supplémentaire. Aucune rafale détectée, mais l'absence
stricte de toute répétition nouvelle n'est **pas acquise**.

**Limites.** Sans position, une salle coupée perd la composante de l'acteur :
une sortie sans origine moyenne accessible est refusée ; un contact sans entrée
accessible est estimé dans sa composante et peut échouer à l'exécution. Les
détours locaux par une autre salle et les occupants mobiles restent à l'exécution.
Bruts consolidés : `artifacts/codex-30-consolide.json` (seule la crue a été
reprise après correction, référence réemployée) ; autres mesures `codex-30-*`.
Scripts, tous dans `artifacts/` : `mesurer_erreur.py`,
`cpu_worker.py`, `cpu_ensemble.py`, `verifier.py`. Pas de fusion ni banc long.
