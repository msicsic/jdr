# Lot 62 — salles d'intérêt : arrêt au diagnostic

Branche `codex-salles-interet`, non fusionnée ; base `04bca30`, brief `491b6bf`.
Le 2026-10-25, `origin/integration` était encore à cette base au début du lot.
**Aucun filtre appliqué au moteur : la domination exigée du trajet direct est fausse.**
Pas de Luna, de modification des coûts, des plafonds ou de `main`.

**Mesure préalable.** Deux nuits de 12 h, graine 1985, lancées ensemble, deux
processus à priorité réduite. `tools/mesurer_salles_interet.py` observe les états
effectivement examinés, sans rappeler les buts ni les gestes. Les données du brief
venaient de `5c2ce81` ; elles ne se reproduisent pas à l'identique sur `04bca30`.

| Nuit | Nœuds, 12 h | Bornées, 12 h / 8–12 h | CPU instrumenté, 12 h |
|---|---:|---:|---:|
| Mine, tiré | 963 265 | 3 / 0 | 170,58 s |
| Auberge, fixe | 1 712 879 | 289 / 289 | 429,00 s |

Après 8 h, Rémy/faim : **299 recherches épuisées, 600 694 nœuds**, 84,4 % des
711 348 nœuds des recherches neuves de la mine. À l'auberge, Joss/faim :
**165 bornées**, Tilo/faim : **118**, Joss/chaleur : **6**. Les deux faims
totalisent 1 447 329 des 1 599 785 nœuds, soit 90,5 %. Les combinaisons
d'acquisitions préparatoires dominent les états : 97,4 % à la mine, 86,9 % à l'auberge.
Ces faims représentent 60,7 % / 79,5 % du temps observé des recherches neuves après 8 h.

| États observés, 8–12 h, passes de découverte incluses | Mine | Auberge |
|---|---:|---:|
| Examinés | 711 438 | 1 601 479 |
| Arrivée par `aller` | 492 231 | 1 216 994 |
| Arrivée sans but atteint ni suite non mobile offerte | 136 342 (19,2 %) | 381 814 (23,8 %) |
| Arrivée dans une salle sans action observée dans toute la passe | 8 014 (1,1 %) | 31 976 (2,0 %) |
| Arrivée non développée, notamment profondeur atteinte | 219 566 | 370 932 |

Dans les seules passes bornées de l'auberge : 252 031 arrivées sans suite non
mobile sur 1 156 000 états (21,8 %). Ces comptes ne prouvent pas qu'un arrêt
est supprimable : une action portée peut être offerte partout, une salle peut
être utile dans un autre état, et les feuilles non développées restent inconnues.
Ils **n'établissent pas les salles sans intérêt comme cause principale** ; le fait
dominant mesuré est la répétition des recherches alimentaires sans résultat sous
la borne. Les CPU incluent l'observation, sans prétention à mesurer un gain.

**Preuve contraire.** `trajet_estime.parcours` choisit sa route sur `cout_route`,
puis `_mesurer` ajoute la pression intégrée de `Vue.prix_route`. Dans un losange
A–B–D / A–C–D, B est sombre et C est vide. Route directe A→D par B : durée
0,153333 min, pression 0,230000, total **0,383333**. Avec C de largeur 5 puis 9,
les deux allers A→C→D coûtent **0,203333 / 0,303333**, sans pression. C ne porte
aucun geste ni but. La complète choisit ces deux allers ; filtrer sur D seul lui
impose 0,383333, sans aucun plafond atteint. Le contrat des lots 46/48/51 échouerait.
Il faudrait d'abord garantir les routes sur leur coût complet et leur admissibilité,
portes et départs intermédiaires compris ; aucune correction de ce contrat n'est
introduite sous couvert d'un filtre d'intérêt.

**Vérification.** Deux tests nouveaux : instrumentation contre témoin sur les deux
captures réelles à 480, puis contre-exemple avec deux géométries, recherche complète,
exécution, état, perception et rendu identiques après sauvegarde/rechargement.
Suite complète unique (`tools/tests.py --processus 3`) : **1 807 tests, quatre
ignorés, 177 fichiers, aucun échec ni erreur**, priorité réduite, 677,7 s.
Les campagnes comparatives d'une optimisation (16 empreintes, trois versions sur
12 h, `VERIFIER` continu) ne sont pas lancées : arrêt à l'étape diagnostic prévue
par le brief, aucune optimisation livrée. Bruts locaux : `artifacts/p3/` ; commandes
reproductibles dans l'en-tête de l'outil ; résumés par `resumer(json_charge)`.
