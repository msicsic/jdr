# Codex 10 — coût de calcul, suite

**Actualisation après la contre-épreuve lampes-suite :** `origin/main` **a7ecb50** est
fusionné dans la branche par **1efbb12**. Les **32 nuits de 8 h et les quatre nuits de
12 h de l'auberge sont identiques à cette nouvelle référence**. La dominance de dépense
essayée hors du moteur change des résultats bornés et n'est pas livrée. Voir le
complément en fin de rapport ; les mesures initiales ci-dessous restent celles de 9075aea.

Branche `codex-cout-suite`, non fusionnée, issue de `main` **9075aea** via la tâche
5910b44. Le `pull --ff-only origin codex-cout-suite` demandé a confirmé la branche à jour.
Travail dans `tmp-worktrees/codex-cout-suite` ; référence détachée dans
`tmp-worktrees/codex-cout-suite-ref`. Aucun changement de `main`.

## Première livraison — référence 9075aea

Les **32 nuits de 8 h sont identiques** à la référence : quatre scénarios, graines
1985, 7, 42, 2024, départs tiré et fixe. Chronique, mesures du jeu, récit, souvenirs,
état final complet, repères du banc et résultats exacts de chaque recherche logique
coïncident. Temps CPU total de cette passe : **368,48 → 358,11 s, soit −2,8 %**.
Le gain est modeste ; la majorité des grosses recherches de la mine reste à recalculer.

Les deux contrôles renforcés sont également identiques, sans assertion :

- `planification.VERIFIER=True`, `spatial.VERIFICATION=1`, 2 h, graine 42,
  chacun des quatre scénarios ;
- `VERIFIER=True`, `VERIFICATION=0.2`, 8 h, graine 42, mêmes scénarios.

Suite complète : **1 383 tests, 4 sautés, six échecs de sous-tests préexistants**,
reproduits à l'identique sur `main` 9075aea ; détail ci-dessous. **37 tests ciblés verts**.

## Ce qui change

### Recherches sans plan

La sonde sur la mine 7 retrouve **44 recherches lourdes de Rémy** dont les entrées
structurelles successives sont identiques. Les prix de faute et de dégât, tirés de la
détresse, changent la clé du résultat ; le graphe existant peut être repris mais sa
recherche pondérée reste à refaire. Chez Josse et Mathe, les croyances, refus, positions
et moyens changent également : les supprimer de la clé serait incorrect.

Deux limites empêchent de reprendre aveuglément ces absences :

1. Certaines recherches atteignent **4 000 nœuds** : elles sont bornées, sans preuve
   qu'aucun plan n'existe.
2. Même une recherche pondérée épuisée n'est pas une preuve indépendante des prix.
   Elle garde le coût minimal d'un état sans sa profondeur. Un chemin peu cher mais
   long peut en empêcher un plus court de se développer avant la profondeur limite.
   Un changement de prix peut alors faire apparaître un plan. Le contre-exemple est
   couvert par un test, sans changer le comportement existant du planificateur.

La branche ajoute donc un **certificat par parcours en largeur du graphe gardé**,
à profondeur minimale par état. Il couvre tous les chemins autorisés jusqu'à la
profondeur limite et ne conclut que si aucun n'atteint le but. Une lacune, un but ou
le plafond de 16 000 états rendent le certificat inutilisable. Aucun geste nouveau
n'est calculé pour le compléter. Les entrées structurelles et les permissions restent
dans la clé ; les prix seuls peuvent varier. `VERIFIER` refait chaque reprise à partir
de zéro, avec exactement les paramètres joués et la même borne.

Une première variante complétait les graphes pour construire davantage de certificats :
à la mine 7, 46 613 états de preuve et environ 122 Mo au pic, sans gain CPU mesurable.
Elle a été écartée. La variante retenue examine seulement les graphes existants, puis
libère le graphe si le certificat suffit. Un échec de certificat n'est tenté qu'une fois
pour la même signature structurelle.

La clé des visites conserve leur **ordre avec les égalités**, plutôt que leurs dates
absolues : `_chercher` ne les utilise que pour classer les destinations, avant la
longueur de trajet et le nom de salle. Aucune autre entrée n'est retirée.

### Empreinte visuelle

Les signatures d'objets inchangés sont partagées. Des instantanés isolent les positions
et les propriétés composées lues par la vue ; une comparaison des dictionnaires en C
détecte les changements. Quand tous les objets sont inchangés, la liste entière des
signatures est partagée. L'ordre des objets et le texte des propriétés composées sont
contrôlés séparément, car l'égalité des dictionnaires ignore l'ordre de leurs clés.

Les mutations en place, les ajouts/retraits, l'extinction faute de combustible et les
changements de joueur sont couverts. Les conteneurs de `monde.data` restent ordinaires,
sans remplacement ni instrumentation. Une empreinte identique retrouve directement le
mémo courant sans en rehacher tous les tuples. `spatial.VERIFICATION` recompare aussi
l'empreinte à sa construction complète, en plus des contrôles existants de perception.

## Mesures CPU et mémoire

CPython **3.13.7**, même interpréteur `.venv/Scripts/python.exe` des deux côtés.
Nuits de la référence et de la branche entrelacées dans le même pool, **quatre nuits
au plus**, priorité réduite. `time.process_time`, une passe sur les 32 nuits ; les
tests et contrôles renforcés sont lancés après les mesures. Aucun temps mural n'est
utilisé pour le gain. Ces petits écarts restent sensibles au bruit de mesure.

Moyennes sur quatre graines, secondes CPU par nuit de 8 h, référence → branche :

| Scénario | Départ tiré | Départ fixe | Moyenne des 8 nuits | Pic mémoire maximal des 8 nuits |
|---|---:|---:|---:|---:|
| Relais | 4,19 → 4,04 | 4,20 → 4,06 | 4,20 → 4,05 | 43,8 → 43,8 Mo |
| Mine | 21,37 → 20,47 | 21,32 → 21,02 | 21,35 → 20,74 | 91,0 → 89,5 Mo |
| Auberge | 12,83 → 12,46 | 11,12 → 10,75 | 11,97 → 11,60 | 130,0 → 129,3 Mo |
| Crue | 8,19 → 8,02 | 8,90 → 8,72 | 8,54 → 8,37 | 59,0 → 59,4 Mo |

Les pics sont ceux du processus (`PeakWorkingSetSize`) ; pas une somme de quatre
processus. Exemple de gain plus visible : mine 1985, départ tiré, **11,72 → 10,30 s** ;
mine 2024, **31,97 → 31,56 s**, reste presque inchangée.

Comptes cumulés sur les **8 nuits de chaque scénario** :

| Scénario | Recherches calculées | Nœuds de recherche | Reprises mémoire | Recherches sur graphe gardé | Recherches bornées effectivement calculées | Reprises par certificat |
|---|---:|---:|---:|---:|---:|---:|
| Relais | 4 152 → 3 948 | 175 434 → 166 142 | 6 520 → 6 724 | 1 984 → 1 800 | 0 → 0 | 191 |
| Mine | 5 137 → 4 866 | 1 832 748 → 1 829 693 | 9 170 → 9 441 | 1 006 → 808 | 308 → 308 | 228 |
| Auberge | 4 473 → 4 452 | 690 779 → 690 743 | 3 944 → 3 965 | 1 397 → 1 397 | 35 → 35 | 0 |
| Crue | 4 613 → 4 175 | 789 927 → 773 241 | 4 223 → 4 661 | 1 196 → 777 | 0 → 0 | 439 |

Une recherche sur graphe gardé est comprise dans les recherches calculées ; une reprise
par certificat est comprise dans les reprises mémoire. **858 reprises par certificat**
au total. Construction des certificats : 13 / 56 / 3 / 155 tentatives, 590 / 6 512 /
371 / 48 354 états examinés (Relais / mine / auberge / crue), aucune borne de preuve
atteinte. Ces états de preuve sont comptés séparément des nœuds de recherche.

## Profils avant → après

`py-spy 0.4.2`, 400 Hz, mêmes quatre nuits de 8 h, graine 7, départ tiré. Deux samplers
et deux nuits au plus, référence et branche du même scénario ensemble. Le lanceur
Windows du venv n'étant pas reconnu par `py-spy`, les profils emploient directement
le même CPython 3.13.7 installé. Le même outil de mesure est utilisé des deux côtés.

Parts inclusives en % de la nuit ; les lignes se recouvrent, elles ne s'additionnent pas :

| Poste | Relais | Mine | Auberge | Crue |
|---|---:|---:|---:|---:|
| Choix du but | 34,9 → 35,8 | 65,0 → 65,1 | 29,9 → 30,4 | 36,2 → 35,2 |
| Recherche `_explorer` | 17,0 → 17,7 | 55,8 → 55,2 | 20,7 → 20,5 | 24,2 → 23,0 |
| Percevoir | 16,3 → 17,0 | 11,5 → 10,9 | 26,3 → 24,1 | 15,6 → 16,6 |
| Gestes et marche | 15,7 → 12,3 | 8,1 → 7,5 | 14,9 → 14,4 | 15,7 → 14,4 |
| Ouïe | 8,0 → 5,6 | 4,1 → 3,5 | 8,5 → 7,1 | 7,7 → 5,4 |
| Empreinte `etat_vue` | **7,7 → 6,3** | **3,6 → 2,9** | **8,8 → 5,9** | **6,5 → 5,7** |
| Perception complète `_percus` | 3,7 → 4,1 | 2,8 → 2,8 | 6,3 → 5,5 | 3,1 → 3,6 |
| Perception incrémentale | 1,9 → 1,9 | 1,7 → 1,8 | 4,7 → 4,4 | 1,9 → 1,9 |

Les certificats occupent moins de 0,2 % des échantillons de chacune de ces nuits.
Le profil comporte 2 318 à 8 536 échantillons par nuit : ne pas attribuer une petite
variation d'un poste non modifié à une accélération démontrée de ce poste.

**Qui bouge revoit toute sa perception : conservé.** La fonction complète représente
2,8 à 6,3 % avant, y compris les appels qui ne sont pas dus à un déplacement. Son gain
potentiel et la complexité d'une différence de champs ne justifient pas cette extension
dans ce chantier. L'empreinte partagée améliore déjà le coût commun des lectures.

## Vérification et reproduction

`tools/empreintes_nuits.py` observe tous les appels extérieurs au planificateur, dans
l'ordre : PNJ, but, description de mémoire et résultat (coût exact, étapes, salle,
objets portés, faits). Les appels récursifs internes ne sont pas comptés une seconde
fois : une reprise peut précisément les éviter. `comparer --calcul` vérifie cette
trace et son nombre d'appels, ainsi que toutes les empreintes physiques. Le mode strict
antérieur garde aussi la comparaison des nœuds et recherches neuves ; il reste disponible.
Une trace, une empreinte ou une nuit manquante fait échouer le mode `--calcul`.

Les tests couvrent le contre-exemple de profondeur, les permissions, les graphes incomplets
et bornés, l'ordre des visites, les mutations visuelles en place et l'ordre des dictionnaires.
Deux sauvegardes complètes du banc étaient versionnées dans `tests/data/cout-suite` :
Rémy, mine 7, minute 365 ; Brune, crue 7, minute 349. Les reprises y sont contrôlées
par `VERIFIER`, puis le monde vit cinq minutes et est rechargé : même état complet,
mêmes lignes produites, même rendu et même scène perçue avec ou sans certificat.
Ces captures sont régénérées sur la nouvelle base dans le complément ci-dessous.

La découverte complète par `tools/tests.py --processus 4` exécute **1 383 tests en
171 s**, 4 sautés (SDK Anthropic facultatif absent), aucune erreur technique, mais
**six échecs de sous-tests** dans `test_fournisseurs_jeu.py` et `test_mimo.py` :

- deux sous-tests attendent cinq appels MiMo et en reçoivent six (crypte et atelier) ;
- quatre sous-tests de rejeu constatent une initiale `L` au lieu de `I` ou `G` après
  chargement/sauvegarde des scènes de rejet réelles.

Les deux fichiers sont rejoués sur le worktree de référence, même Python : **16 tests,
six échecs identiques, un sauté**, mêmes assertions et mêmes différences. Ils sont
préexistants et ne sont pas corrigés dans ce chantier de calcul. Les 37 tests ciblés
(`test_cout_suite`, `test_empreintes_nuits`, `test_planif_cout`, `test_spatial`) passent.
Résultats détaillés : `tests-complets.json` et `tests-fournisseurs-main.json` dans les
artefacts locaux. La suite entière n'est donc pas présentée comme verte.

Commandes de contrôle des résultats locaux (artefacts non versionnés) :

```powershell
$env:PYTHONIOENCODING='utf-8'
$python = 'C:\Users\msics\donjon\.venv\Scripts\python.exe'
& $python tools/empreintes_nuits.py comparer artifacts/cout-suite/retenu-main.json artifacts/cout-suite/retenu-branche.json --calcul
& $python tools/empreintes_nuits.py comparer artifacts/cout-suite/controle2h-main.json artifacts/cout-suite/controle2h-branche.json --calcul
& $python tools/empreintes_nuits.py comparer artifacts/cout-suite/controle8h-main.json artifacts/cout-suite/controle8h-branche.json --calcul
& $python tools/tests.py --processus 4 --sortie artifacts/cout-suite/tests-complets.json
```

Le lanceur local `artifacts/cout-suite/campagne.py` alterne les couples
(référence, branche) dans un `ThreadPoolExecutor(max_workers=4)` et appelle
`empreintes_nuits._lancer` avec le même outil et l'interpréteur partagé. Pour reproduire
sans ce lanceur, deux `jouer --processus 2` simultanés, l'un avec `--depot` sur la
référence et l'autre sur la branche, donnent le même protocole. Paramètres :
`--heures 8 --graines 1985 7 42 2024 --departs tire fixe` et les quatre scénarios.
Les profils bruts et sorties sont sous `artifacts/cout-suite/{avant,apres}-final-*`.

## Limites et fusion

Les recherches lourdes bornées restent présentes, et les croyances ou refus qui changent
continuent d'invalider les graphes. Le gain de cette livraison est donc d'environ 2 à 4 %
par scénario sur la passe mesurée, pas une résolution complète du coût de la mine.
Une optimisation future doit préserver l'algorithme joué, ses égalités et ses limites,
ou faire l'objet d'un changement de comportement explicitement séparé.

Les axes de relations 3b sont désormais intégrés par la fusion de a7ecb50 ; les
vérifications sur cette nouvelle référence sont détaillées ci-dessous. Aucun appel à
Luna ni comparaison de modèles dans ce chantier.

## Complément — fusion de a7ecb50 et piste de dominance

`git fetch origin`, puis `git merge --no-edit origin/main` : fusion **1efbb12**, sans
conflit. La clé des recherches conserve les axes et bandes des relations 3b ; la pression
sociale, les états corporels et les gestes de réanimation de 4a sont conservés. La branche
locale `main` n'est pas déplacée. La projection `_parts_remises` reste strictement celle de
la référence : ni retrait de geste, ni modification de la pertinence lumineuse de lampes-suite.

### Identité et coût après fusion

Nouvelle campagne contre le worktree détaché a7ecb50, même outil et même CPython 3.13.7 :

- **32 nuits de 8 h, zéro différence**, quatre scénarios × quatre graines × tiré/fixe ;
- **quatre nuits de 12 h à l'auberge, zéro différence**, graines 1985, 7, 42, 2024, départ tiré.

Les empreintes couvrent toujours l'état complet et tous les résultats logiques de recherche.
Temps CPU des 32 nuits : **453,03 → 439,51 s (−3,0 %)**. Moyennes par nuit, huit nuits
par scénario ; pics maximaux par processus :

| Scénario | CPU main → branche | Nœuds cumulés main → branche | Pics mémoire |
|---|---:|---:|---:|
| Relais | 5,17 → 5,02 s | 270 362 → 262 452 | 44,0 → 43,8 Mo |
| Mine | 20,17 → 19,44 s | 1 434 658 → 1 425 749 | 92,0 → 88,7 Mo |
| Auberge | 19,50 → 19,06 s | 2 102 915 → 2 099 318 | 181,9 → 181,5 Mo |
| Crue | 11,79 → 11,43 s | 997 786 → 841 856 | 59,5 → 58,3 Mo |

Reprises mémoire cumulées, main → branche : 4 381 → 4 527 au Relais, 7 695 → 8 498 à la
mine, 3 331 → 3 382 à l'auberge, 11 751 → 14 438 à la crue. Parmi elles, 139 / 779 / 44 /
2 967 reprises par certificat. Recherches sur graphe gardé : 1 484 → 1 349, 1 154 → 421,
1 838 → 1 801, 5 542 → 2 857. Recherches bornées effectivement calculées : 0 / 185 / 234 /
0 de chaque côté. Les reprises d'absence ne masquent donc pas de nouvelles réussites bornées.

**Auberge 12 h**, moyenne des quatre graines : **86,85 → 84,66 s CPU**,
**1 680 560 → 1 673 688 nœuds** ; pics 183,2 → 184,2 Mo. 946 recherches bornées de chaque
côté, 327 reprises par certificat sur la branche. Ces valeurs ne se comparent pas directement
aux 196 s du rapport lampes-suite : la référence, les trajectoires et les conditions de calcul
ont changé. Seuls les couples simultanés de cette nouvelle campagne mesurent l'effet de la branche.
Les grandes recherches et le coût de la projection subsistent.

Le pool des mesures longues contient quatre nuits au plus. Celui des 32 nuits contient deux
nuits appariées, avec au plus deux contre-épreuves en parallèle : quatre calculs lourds au total.
Les tests et contrôles renforcés viennent ensuite, hors des mesures CPU. Une passe seulement ;
les gains de quelques pourcents restent sensibles au bruit de mesure.

### Contre-épreuve de dominance, non livrée

Prototype local `artifacts/cout-suite/essai-dominance.py` : à salle, objets portés et faits
identiques hors `depense`, un état déjà développé domine un autre si son coût est strictement
plus faible, sa dépense moindre ou égale et sa profondeur moindre ou égale. Il ne supprime
aucune projection de part. Chaque résultat est recomparé à la recherche originale fraîche,
avec le même départ, le même but, les mêmes paramètres et la même borne.

Deux divergences réelles, après arrêt au premier résultat différent de chaque nuit :

| Auberge | Recherche de Lucien | Référence | Prototype |
|---|---|---|---|
| Graine 7, minute 644 | Abri dans la salle commune | aucun plan, 4 000 nœuds | coût 130, 3 007 nœuds |
| Graine 42, minute 627 | Placer le ballot à l'étable | aucun plan, 4 000 nœuds | coût 130,5, 3 378 nœuds |

Le premier cas est rejoué depuis la sauvegarde : `abri` rend `None` dans la référence et
un trajet vers la salle commune dans le prototype, même après la règle `endurer`.
Les deux états complets et les détails des résultats sont versionnés dans
`tests/data/cout-suite/auberge-*-borne*`. Le test recharge ces mondes, contrôle le résultat
borné original, le rendu, la scène perçue et la vie du monde après rechargement.

La dominance peut conserver un optimum théorique tout en faisant apparaître un plan avant
la borne, là où la référence n'en trouvait aucun. Un contre-exemple synthétique teste aussi
ce contrat : retirer un état plus cher, plus dépensier et sans moyens supplémentaires
conserve l'optimum illimité de coût 10, mais change la réponse à cinq nœuds de `None` en plan.
La profondeur est prise en compte dans le prototype ; l'écart ne vient donc pas d'un
simple oubli de ce critère. Une seconde contre-épreuve compte même les états dominés
retirés dans le budget : elle trouve encore les deux plans, à 3 047 et 3 458 nœuds.
Compter les états retirés ne rétablit pas les descendants qu'ils auraient fait explorer.

**Cette règle est écartée**, sans conclure que toute optimisation par dominance est impossible.
Une future optimisation doit aussi préserver l'ordre et le budget de la recherche jouée,
ou faire l'objet d'un changement de comportement distinct. Partager le calcul des transitions
en conservant les états et leur comptage reste une autre piste. Aucun gain hypothétique du
prototype n'est ajouté aux gains mesurés de la branche.

### Sauvegardes et contrôles de la fusion

Les anciennes captures de preuve contenaient les croyances `fiable`, remplacées par les
relations 3b : elles sont régénérées par le banc sur a7ecb50, sans compatibilité ad hoc dans
le moteur. Cas actuels : Rémy, mine 7, minute 365 ; Aubin, crue 7, minute 443. Le contrôle
de reprise, d'état complet et de rendu après rechargement passe sur ces nouvelles captures.

**Suite complète après fusion : 1 431 tests en 210,4 s, 4 sautés, six échecs MiMo**,
aucune erreur technique. Les deux fichiers concernés sont rejoués sur le worktree
a7ecb50, même interpréteur : 16 tests, un sauté, mêmes six échecs. Les identifiants
des sous-tests et les messages d'assertion sont comparés automatiquement : identiques.
Les 39 tests ciblés du calcul et de la perception passent dans cette suite, dont les
11 de `test_cout_suite.py`. La suite complète reste explicitement non verte.

**Contrôles renforcés après fusion :** `VERIFIER=True` et `VERIFICATION=1` sur 2 h,
puis `VERIFIER=True` et `VERIFICATION=0.2` sur 8 h, graine 42, départ tiré, chacun des
quatre scénarios : aucune assertion, quatre nuits identiques de chaque côté pour
chaque durée. Les contrôles sont séparés des mesures CPU.

**Profil de l'auberge 12 h**, graine 7, départ tiré, `py-spy` 400 Hz, référence et branche
ensemble, deux samplers et deux nuits au plus. CPython 3.13.7 direct, même outil des deux
côtés, 23 382 / 23 288 échantillons. Parts inclusives main → branche :

| Poste | Part de la nuit |
|---|---:|
| Choix du but | 71,7 → 72,4 % |
| Recherche `_explorer` | 61,5 → 62,1 % |
| Construction `_suites` | 55,6 → 56,6 % |
| Gestes simulés | 49,4 → 50,1 % |
| Dont `_parts_remises` | 11,0 → 11,1 % |
| Percevoir | 10,3 → 10,2 % |
| Gestes et marche réels | 6,7 → 6,3 % |
| Ouïe | 3,7 → 3,4 % |
| Empreinte `etat_vue` | 3,4 → 2,2 % |

Ces parts se recouvrent. Le coût causal des remises ne se limite pas au temps passé
dans leur générateur : les états supplémentaires font aussi travailler les autres
gestes, coûts et tests de la recherche. Le profil confirme donc la recherche dominante,
sans démontrer une réduction du coût des remises dans cette livraison.

Artefacts de cette passe : `fusion32-{main,branche}.json`,
`fusion-auberge12-{main,branche}.json`, `dominance-ecart-{7,42}.json`,
`fusion-tests.json`, `fusion-controle{2h,8h}-{main,branche}.json` et
`fusion-profil12-{main,branche}.raw`, sous `artifacts/cout-suite`.
Reproduction des comparaisons finales : mêmes commandes `empreintes_nuits.py comparer
--calcul`, avec les préfixes `fusion32`, `fusion-auberge12`, `fusion-controle2h` et
`fusion-controle8h`. Les six résultats des rejeux (original, dominance, dominance
comptée, deux graines) sont conservés dans `dominance-rejeux.json` ; seules les deux
variantes expérimentales diffèrent, et aucune n'est chargée par le moteur livré.
