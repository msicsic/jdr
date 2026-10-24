# Lot 63 — recherches sans plan : diagnostic, pas de nouvelle clé

Branche `codex-faim-sans-plan`, **non fusionnée** ; base `de3e986`, brief `99de564`.
`origin/integration` était déjà ancêtre du brief au départ. **Arrêt à l'issue
« mesure et plan, sans code moteur » prévue par la tâche** : la couverture des
lectures n'est pas prouvée. Aucun moteur, cache, scénario ou modèle modifié ;
aucun appel à Luna ; `main` inchangée.

**Mesure.** L'outil `tools/mesurer_lectures_recherche.py` relève les lectures Python
des dictionnaires pendant l'exploration et les changements des 44 composantes
de `_entrees`. Deux nuits de 12 h, graine 1985, priorité réduite ;
les comptes ci-dessous portent sur les recherches neuves de faim de 480 à 720.

| Mesure | Rémy, mine tirée | Joss, auberge fixe |
|---|---:|---:|
| Recherches neuves observées | 293 | 188 |
| Épuisées / bornées / plans | 292 / 1 / 0 | 150 / 31 / 7 |
| Nœuds de ces recherches | 543 981 | 281 820 |
| Paires successives, même résultat sans plan | 292 | 178 |
| Sans lecture **observée** changée | 2 (0,68 %) | 126 (70,79 %) |
| Dont épuisées / bornées | 2 / 0 | 119 / 7 |
| Seul `Vue.degat` change | 266 | 0 |
| CPU de toute la nuit instrumentée | 285,11 s | 557,58 s |

Les chiffres du lot 62 sur `04bca30` ne se reproduisent pas sur `de3e986`.
Dans les paires identiques, positions crues/croyances changent 20/17 fois à la mine,
30/26 à l'auberge ; détresses 11/13, refus 8/6, relations et chances 8/8 et 13/15.
`_entrees` est même inchangé dans **245/292 et 124/178 paires**. Le prix de casse,
effectivement lu, change dans 289 paires de la mine : il est **hors `_entrees`,
dans l'autre partie de la clé exacte**. Autres lectures changées : souvenirs,
personnes, moyens, lumière, garde et poste.

**Limite décisive.** Dépendances invisibles : valeurs dérivées par `Vue.__init__`,
refus/prix préchauffés par `_entrees`, graphes repris (218/99 recherches), caches
géométriques, arguments scalaires dont `faute`. Un lecteur natif contourne aussi
les méthodes substituées de `dict` (testé). Listes/ensembles sont au contraire
relevés trop largement. Les fractions observées ne garantissent ni ne bornent
la part réutilisable ; **zéro reprise nouvelle autorisée**. Aucun gain revendiqué.

**Règle et suite.** Une trace complète du résultat pondéré doit inclure ses prix.
Un certificat d'absence peut s'affranchir de certains prix seulement par la
preuve de couverture du graphe admissible jusqu'à la profondeur. L'épuisement
pondéré ne suffit pas : la mine présente encore des preuves à issue `lacune`.
Le [plan détaillé](../plan-planificateur.md#clé-par-lectures--diagnostic-du-lot-63-non-fusionné)
décrit façade immuable, provenance consommée à la demande, dépendances des caches,
repli automatique sur la clé actuelle, deux traces distinctes et preuve inductive.
Les recherches bornées conservent leurs règles actuelles.

**Vérification.** Quatre tests nouveaux verts, dont deux captures réelles jouées
une minute et rechargées : résultat, monde complet, perception et rendu identiques
au témoin. Les deux nuits de 12 h ont aussi les mêmes mesures et tous les mêmes
résultats de recherche que sans instrumentation. Suite complète unique :
**1 822 tests, quatre ignorés, 180 fichiers, aucun échec ni erreur**, 814,3 s,
`tools/tests.py --processus 3`, priorité réduite. La matrice d'empreintes 2 h,
les trois versions simultanées de coût et `VERIFIER` continu sont réservés à
l'implémentation : aucune optimisation livrée, comme au lot 62. Bruts non versionnés :
`artifacts/lectures/` ; commandes reproductibles en tête de l'outil.
