# Rapport Codex 16 — la part de combustible estimée

Branche `codex-part-estimee`, non fusionnée, tâche `91f907a`, moteur de départ
`4fc5212` (`main` intégré avec `GARDE`/`PRET` et force 4b). Worktree
`tmp-worktrees/codex-part-estimee`. Aucun appel à Luna, aucune sauvegarde utilisateur
touchée. Les campagnes lancent référence et branche ensemble, quatre calculs au
plus, à priorité réduite. Ni fusion ni modification de `main`.

**Livraison mesurée, critères non tous atteints.** Le gain de calcul et la majorité
des choix sont établis ; le facteur deux CPU, le non-accroissement strict du sans
recours et du noir dans tous les bancs, et une suite entièrement verte ne le sont
pas. Les écarts sont chiffrés ci-dessous, sans correction propre à une graine.

## Règle livrée

Une demande, un achat ou l'attente d'une part de combustible peut terminer la
recherche par un devis de la suite. Le graphe garde en détail le chemin jusqu'au
donneur, ses risques, la demande et sa chance, le prix et l'attente de remise.
Il ne développe plus les états combinant la part acquise, les sources rechargées,
les allumages et leurs continuations. Le candidat estimé est terminal, son prix
est mis dans la même file pondérée que les autres voies.

La même règle couvre les sources compatibles par `recharge`, huile comme bois,
sans nom de substance, de personnage ou de scénario. `Vue.attente_part` continue
de compter la livraison promise au lieu de remise. Les services où le donneur
entretient lui-même un foyer gardent leur contrat. Le moteur exécute seulement
le préfixe jusqu'à l'accord, puis attend la part réelle et replanifie : aucun
effet du devis n'est appliqué au monde ni sauvegardé comme une action accomplie.

Le devis conserve la scène crue du début de recherche, déplacée au lieu de remise,
avec les possessions, droits acquis, fautes déjà comptées et budget engagé du
préfixe. Il est calculé une fois pour ces moyens, ce lot et l'emploi de lumière.
Une source déjà empruntée n'est pas à redemander. Pour chaque source compatible
et non contrariée, il compte : trajet, prise, emprunt ou achat éventuel,
recharge, accès à une flamme et allumage, puis un trajet et au plus un geste
conclusif du contrat commun `_suites`. Il ne développe pas les successeurs de ce
geste. Les trajets entre salles sont évalués sur les routes connues, à inventaire
et faits constants, en comptant la pression de chaque étape ; ce calcul ne génère
aucun geste. Une source fixe demande une flamme en main ; une source mobile peut aller
à une flamme fixe ou demander du feu à son porteur connu, avec ses refus. Prendre,
emprunter ou acheter la flamme suit les mêmes permissions, chances, prix et
réservations de budget que l'accès à la source. Les fautes autorisées sont
comptées une fois par personne lésée, comme dans les gestes ordinaires.

Les minutes, chances et coûts sociaux restent ceux des gestes. Les segments
comptent leur durée multipliée par `Vue.pression` à l'arrivée, comme les trajets
ordinaires : noir avant allumage, eau, éloignement des biens et présence crainte.
La fin compte la combustion de la source nouvellement portée et, pour un but à
tenir, `RESTER * pression(final)`. L'attente compte au lieu de remise, avant la
lumière espérée. Le prix des fautes et des dégâts reste séparé et appliqué par
la recherche, donc absent des comparaisons internes du devis.

Ce devis **n'est pas une borne admissible de l'optimum détaillé**. Il peut être
pessimiste en ignorant une ouverture ou un déplacement hypothétique du préfixe.
Il peut exclure une voie dont le reste exige plusieurs préparatifs.
Il peut être optimiste sur les délais,
les mouvements des autres, l'évolution des chemins, le temps des détours et les
préparatifs qu'il ne représente pas. La faisabilité future générale n'est donc
pas garantie ; seule l'action réelle revalidée fait autorité.

## Caches et contrôle

`_entrees` conserve les croyances, objets, profils, permissions, relations, prix,
routes et point de départ déjà lus par les gestes. Il explicite en plus l'identité
de cette règle, les pressions d'eau et les pressions sociales. Les recherches
avec `depuis` restent sans mémoire. Le devis ne choisit pas selon le prix d'une
faute ; les arêtes des graphes gardés restent indépendantes de ce prix.

Les lectures de lumière du devis passent par les méthodes communes et participent
à la découverte, aux deux graphes `sombre`/`lumiere` et à leur reprise. Le certificat
d'impossibilité conserve sa prudence : un candidat terminal sans nœud développé
est une lacune, pas une preuve d'absence. `VERIFIER` compare mémoire, graphe et
restriction de portage à une recherche neuve avec **la même règle estimée**.

## Auberge, 12 h, huit graines

Référence intégrée `4fc5212`, graines `1985 7 42 2024 3 11 99 500`, départ tiré.
Les minutes sont des min·PNJ ; valeurs moyennes par nuit, hors contre-épreuve.

| Mesure | Avant | Après |
|---|---:|---:|
| CPU (s) | 108,711 | 68,279 |
| Nœuds | 1 521 695 | 614 622 |
| Minutes dans le noir | 1 050,625 | 989,375 |
| Minutes sans recours | 174,375 | 176,25 |
| Minutes en attente | 493,125 | 389,375 |
| Demandes de combustible | 11,5 | 11,625 |
| Achats acceptés de combustible | 1,5 | 1,75 |
| Parts physiques livrées | 4,25 | 4,625 |
| Recharges de lampes | 0,375 | 1,125 |
| Recharges de foyers | 24,125 | 24,125 |
| Foyers rallumés | 1 | 1 |
| Usurpations / violations / plantages | 0 | 0 |

CPU **−37,2 %, ×1,59**, nœuds **−59,6 %, ×2,48**. Le facteur deux visé est dépassé
sur les nœuds, **pas atteint sur le CPU**. Les ressources ne baissent pas. Le critère strict
« sans recours pas pire en moyenne » est **manqué de 1,875 min·PNJ** : le gain de 55
minutes de la graine 1985 ne compense pas les 60 supplémentaires de la graine 7
et les 10 de la graine 500. Les cinq autres graines gardent leur compte. Ce petit
écart ne doit pas être effacé par l'arrondi.

| Graine | Noir avant → après | Sans recours avant → après |
|---|---:|---:|
| 1985 | 1 215 → 925 | 170 → 115 |
| 7 | 1 000 → 905 | 235 → 295 |
| 42 | 1 170 → 1 130 | 105 → 105 |
| 2024 | 950 → 860 | 95 → 95 |
| 3 | 925 → 920 | 210 → 210 |
| 11 | 945 → 1 060 | 120 → 120 |
| 99 | 960 → 1 080 | 240 → 240 |
| 500 | 1 240 → 1 035 | 220 → 230 |

Les audits de ces seize nuits n'ont aucun plantage ni usurpation. Ils donnent
35 → 33 constats `fige_presse`, 29 → 25 `noir_long`, 4 → 8 `voir_alterne` et
1 → 2 `appels_nombreux`. Les bascules restent à 1,125 par nuit ; le
maximum de bascules répétées baisse de 2 à 1, les passages par heure moyens de
26,875 à 26,25 (pires 40 → 36), les avertissements redits restent à 0,625.
Les nouvelles alertes ponctuelles d'alternance sont conservées, pas présentées
comme corrigées : Anselme (1985, minute 300), Lucien (11, 180), Anselme et Odile
(99, 10 et 20), Mireille (7, 135). Anselme (500) atteint aussi dix appels, répartis
sur plusieurs heures, tandis que ceux d'Odile (99) sont rapprochés. L'absence de
toute nouvelle alerte de boucle n'est donc **pas démontrée** ; les constats et
leur chronologie sont conservés, sans les déclarer résolus.

### Les nuits qui empirent

- **Sans recours, 7 : +60**, tous attribués à la faim de Tilo (relevés 660–715).
  Lucien garde ses 235 minutes de biens, comme avant. Tilo essuie les refus de
  soupe (624) et de vivres (625) ; la nouvelle recherche lui trouve ensuite un
  plan de repas, mais il renonce à manger les vivres à 658 (souvenir sauvegardé).
  Le répit de 60 minutes laisse la faim urgente sans action ; les enquêtes
  reprennent à 719. La référence épuisait ses recherches de faim et classait ce
  temps en attente. Ce n'est pas une absence de part lumineuse corrigée par un
  réglage : c'est un effet des occasions et renoncements différents, non supprimé.
- **Sans recours, 500 : +10**, faim de Joss, relevés 695 et 700. Après les refus de
  soupe et de vivres (656 et 661), il renonce à manger la marmite à 693. Les 220
  minutes de biens de Lucien restent identiques. Le noir de la nuit baisse
  néanmoins de 205 minutes ; cela ne compense pas le critère distinct de recours.
- **Noir, 11 : +115**. Lucien +65, Anselme +60 et Hugues +10 ; Odile −10,
  Mireille −5 et Tilo −5, les autres égaux. À 500, Anselme reçoit ici du bois
  de Joss (refus gratuit, puis achat), alors que la référence refusait le service
  comme impossible. La suite des feux et des rencontres diffère ; la demande d'huile pour
  sa lanterne a lieu à 585 au lieu de 541, et il rejoint la chambre au poêle à
  602 au lieu de 576. Une recherche de lumière perdue par pessimisme du devis
  à 585 est détaillée ci-dessous ; les autres décisions n'y sont pas ramenées.
- **Noir, 99 : +120**. Joss +70, Mireille +55, Odile +45, Tilo +30 et Hugues +5 ;
  Anselme −45, Mathurine −35 et Lucien −5. Les relevés situent surtout Joss à
  l'étable et les séjours tardifs de la cuisine dans le noir. Les demandes et
  gardes ne mènent plus aux mêmes rencontres, et les appels d'Odile changent de
  graine. Ce bilan établit où se font les 120 minutes, pas un manque uniforme de
  combustible ; les compteurs de livraison et de recharge ne baissent pas.

## Justesse contre l'ancienne chaîne

Huit mêmes graines, 12 h, sur les mondes de la branche. Toute recherche qui évalue
le devis, y compris ses reprises de mémoire, est rejouée avec l'ancienne fonction
`_parts_remises` de `4fc5212`, dans des mémoires indépendantes. La borne jouée reste
4 000 nœuds : « détaillée » ne signifie pas un optimum sans limite. Les appels
de contrôle n'affectent ni le monde ni le tirage aléatoire. Leurs temps sont exclus
des mesures de vitesse.

Sur **24 178 recherches** concernées, **23 177 (95,86 %)** gardent le même premier
geste et le même lieu/ensemble d'effets terminaux du but ; 23 187 gardent le même
premier geste seul. Sur les **8 849 recherches où les deux donnent un plan**,
8 833 (99,82 %) gardent aussi ces choix et effets. Les 14 344 absences communes
ne doivent pas être prises pour autant de décisions positives validées.
L'étape estimée est choisie par 245 recherches, pas exécutée 245 fois : le choix
de la délibération et la validation réelle viennent ensuite.

Écarts de coût, quand les deux coûts existent : médiane signée et médiane absolue
**0**, pire absolu **1,74101 minute** (Odile, graine 1985, minute 707, garde du
cellier : 39,61229 contre 37,87128 ; même premier geste). Le minimum est −7,1e−15,
un arrondi de somme. Une absence de plan n'a pas un coût nul et ne rentre pas dans
ces statistiques.

Les **1 001 divergences**, lues et regroupées sans supprimer leurs répétitions :

- **981 anciennes bornes** contre un plan trouvé. Lucien : 576 gardes du grenier
  (42), 242 (11), 103 de l'étable et 16 du grenier (1985), 24 de l'étable et 9
  du grenier (7), 3 du grenier (3), 3 abris (42), 5 placements du ballot (99).
  Ce sont des plans rendus accessibles avant la borne, pas 981 erreurs de prix
  mesurées contre un optimum connu.
- **Trois anciennes recherches épuisées** : Mireille, fourneau, graine 7 minute
  702, 2024 minute 664, 500 minute 543. Le plan nouveau recherche Odile puis
  propose de lui confier la tâche. L'étape estimée était évaluée, mais ne figure
  pas dans le plan retenu. Les espaces et découvertes de moyens ne sont plus ceux
  de l'ancienne règle ; son épuisement n'est pas un certificat pour le nouveau modèle.
- **Un recours perdu ponctuellement** : Anselme, lumière, 11, minute 585. L'ancien
  plan prend la lanterne, demande l'huile, revient au poêle puis recharge et
  allume, coût 44,04759. Le devis recharge avant d'aller chercher la flamme :
  cet ordre fixe peut payer le noir plus longtemps. La recherche trouve alors
  une voie trop chère et choisit `endure`. Plus tard dans la même minute, après
  acquisition réelle, une recherche de lumière retrouve un plan. L'estimation
  n'est donc pas conservatrice de tous les recours de la chaîne détaillée.
- **Seize divergences entre deux plans**, détaillées dans le tableau suivant.

| Graine, minute | PNJ, but | Lecture de la divergence |
|---|---|---|
| 11, 500 (2 appels) | Anselme, poêle | Même coût 16 ; remise puis travail propre au lieu du service du donneur ; le second premier geste change de contenu typé. |
| 11, 571 | Odile, âtre | Même trajet et coût ; achat livré plutôt que service. |
| 1985, 652 | Joss, garde | Même coût 39,416 ; achète l'huile avant l'emprunt de la lanterne plutôt qu'après. |
| 2024, 507 | Anselme, poêle | Même premier geste et prix ; le service et la remise n'ont pas le même fait terminal `part`. |
| 2024, 623 | Anselme, garde | Même coût à l'arrondi près ; prend la lanterne avant la demande d'huile plutôt qu'après. |
| 3, 446 et 476 | Mireille, fourneau | Même coût ; remise à entretenir soi-même au lieu du service ; le premier geste de 476 change de contenu typé. |
| 42, 317 (2 appels) | Anselme, poêle | Même premier geste et coût ; service ou remise dans la continuation. |
| 42, 625 | Odile, âtre | Même premier geste et coût ; achat livré ou service. |
| 500, 323 | Anselme, poêle | Même premier geste et coût ; service ou remise. |
| 500, 540 | Anselme, garde | Prend la lanterne avant l'achat ; 44,2 contre 42,7, ordre de recharge et d'allumage plus pessimiste. |
| 7, 508 | Anselme, poêle | Même premier geste et coût ; service ou remise. |
| 7, 562 | Odile, âtre | Même premier geste et coût ; achat livré ou service. |
| 7, 596 | Joss, garde | Même coût 39,982 ; achat d'huile avant la prise de la lanterne, plutôt qu'après. |

Les dix lignes de comparaison où seul l'effet terminal diffère sont conservées
dans le taux conservateur de 95,86 %. Aucune variante de substance ou de scénario
n'a été ajoutée pour retrouver un des choix de ce tableau. Les traces complètes
sont dans `verifie-justesse-12h/` et `verifie-differences.json`.

## Vérifications et reproduction

### Quatre scénarios, 8 h, quatre graines

Graines `1985 7 42 2024`, départ tiré, références et branche lancées ensemble,
quatre processus au plus. Comparaison isolant le lot : base intégrée `4fc5212`.
Le banc réutilise `comparer_bancs.jouer_nuit`, ses contrôles et son audit ; les
fichiers sont aussi relus par `tools/audit_nuits.py analyser`.

| Scénario | CPU (s) | Nœuds | Noir (min·PNJ) | Sans recours | En attente |
|---|---:|---:|---:|---:|---:|
| Relais | 5,54 → 5,58 | 18 723 → 18 366 | 8,75 → 16,25 | 100 → 97,5 | 31,25 → 26,25 |
| Mine | 19,67 → 21,00 | 221 328 → 211 588 | 258,75 → 258,75 | 13,75 → 13,75 | 283,75 → 285 |
| Auberge | 19,49 → 18,35 | 249 077 → 203 430 | 146,25 → 146,25 | 125 → 121,25 | 8,75 → 8,75 |
| Crue | 11,15 → 10,47 | 57 373 → 40 396 | 67,5 → 67,5 | 112,5 → 112,5 | 62,5 → 62,5 |

| Scénario | Sollicitations de combustible | Achats acceptés | Parts livrées | Recharges de foyers | Foyers rallumés |
|---|---:|---:|---:|---:|---:|
| Relais | 1,75 → 1,75 | 0,75 → 0,75 | 0,75 → 0,5 | 3 → 2,75 | 0,5 → 0,5 |
| Mine | 3 → 3 | 0,5 → 0,5 | 0 → 0 | 4 → 4 | 0 → 0 |
| Auberge | 6,25 → 6,25 | 1,5 → 1,5 | 3,75 → 3,75 | 21,5 → 21,5 | 1 → 1 |
| Crue | 3,25 → 3,25 | 0 → 0 | 0 → 0 | 4,25 → 4,25 | 1,25 → 1,25 |

Pas de recharge de lampe dans ces seize nuits de chaque côté. Les sollicitations
comptent les appels gratuits et payants ; les achats sont leur sous-ensemble
accepté, pas un deuxième total de demandes gratuites.

Les **32 nuits** n'ont aucun plantage, violation ni usurpation. L'audit retrouve
les mêmes familles de constats : Relais, `voir_alterne` 3 → 2 et `fige_presse` 1 → 1 ;
mine, quatre `fige_presse` de chaque côté ; auberge, dix `fige_presse`, deux
`noir_long` et deux `voir_alterne` de chaque côté ; crue, trois `voir_alterne`.
Les bascules sont inchangées par scénario ; les passages horaires maximaux moyens
passent de 9,25 à 8,25 au Relais, de 11,75 à 15 à la mine, restent 19,75 à l'auberge
et 31,25 à la crue. Ces alertes descriptives ne sont pas des violations du monde.

**La nuit du Relais 7 reste une régression partielle.** Le noir passe de 15 à 45
minutes : Brune −5, Aubin +5, Ilse +30 (échoppe, relevés 420–430 et 460–470).
L'achat à Aubin est accepté à 154 des deux côtés ; la référence compte une remise
à Gorm à 162, puis trois recharges du brasero (162, 223, 344). La branche rallume
le brasero plus tôt (155), compte deux recharges (155, 246) et aucune remise de
combustible dans cette nuit. Les mêmes achats acceptés n'établissent donc pas la
même livraison physique. Le gain de dix minutes sans recours ne masque ni les
trente minutes de noir supplémentaires ni la livraison en moins. Les autres
graines des quatre scénarios ne dégradent pas le noir ou le sans recours à 8 h.

La vitesse n'est pas uniformément meilleure : la mine coûte ici environ 6,8 % de
CPU supplémentaire, malgré moins de nœuds. Le devis a lui-même un coût ; le gros
gain à l'auberge après huit heures ne doit pas être étendu aux autres recherches.

Une seconde comparaison demandée contre **`origin/main` 5594028**, également
32 nuits lancées ensemble, reste distincte : cette référence ne contient pas
encore `GARDE`/`PRET` et 4b déjà présents dans la branche de tâche.

| Scénario | CPU main → branche (s) | Noir | Sans recours |
|---|---:|---:|---:|
| Relais | 6,47 → 5,61 | 38,75 → 16,25 | 102,5 → 97,5 |
| Mine | 16,92 → 20,76 | 258,75 → 258,75 | 13,75 → 13,75 |
| Auberge | 16,92 → 17,71 | 140 → 146,25 | 131,25 → 121,25 |
| Crue | 10,35 → 9,97 | 66,25 → 67,5 | 112,5 → 112,5 |

Zéro plantage, violation ou usurpation également. Ces écarts ne sont pas attribués
au seul lot 16 ; le tableau précédent l'isole.

### Suite et contrôles finaux

`tools/tests.py --processus 2` : **1 469 tests, six échecs, quatre sautés**, aucune
erreur, 393,983 s. Les six échecs sont exactement ceux de MiMo reproduits sur
`4fc5212` (`test_mimo` et `test_fournisseurs_jeu` : 16 tests, mêmes six échecs,
un sauté). Quatre portent sur la normalisation des anciennes lettres d'affichage
au chargement (`I/G` devenant `L`), deux sur six appels de transport au lieu de
cinq. Aucun n'est ignoré ni corrigé hors périmètre pour rendre le lot vert.
**La suite entière reste donc non verte**, malgré l'absence de nouvel échec.

Sur chacun des quatre scénarios, graine 42 : `planification.VERIFIER=True` et
`spatial.VERIFICATION=1` sur 2 h, puis 0,2 sur 8 h : **huit nuits sans écart,
sans borne signalée**, sans usurpation ni plantage. Les deux fichiers moteur sont
restés identiques pendant les campagnes finales (empreintes SHA-256 conservées).
Le lanceur est aussi vérifié sur un scénario invalide : le plantage est consigné
et renvoie un code d'échec, distinct des nuits réussies. La correction de ce code
de retour intervient après l'enregistrement des résultats, sans changer la nuit.

Les tests des lampes et `tests/test_part_estimee.py` suivent demande, réception,
identité et propriété de la part réelle, recharge, allumage et but après sauvegarde
et rechargement. Le bois reçu pour le poêle passe par les mêmes gestes ; la voie
vers un bureau réellement éclairé est préférée à la demande plus chère ; sans
flamme connue accessible, aucun allumage n'est prévu. Un cinquième test emprunte
la source avant de la recharger : l'emprunt reste à son propriétaire et les
accords sont replanifiés séparément après rechargement. L'état des ressources et
le rendu du joueur après rechargement sont vérifiés.

Deux attentes historiques sont adaptées : la sauvegarde bornée de Lucien (42)
trouve désormais son plan de placement du ballot, contrôlé par `VERIFIER` ; la
cuisinière peut recevoir le bois et alimenter le fourneau elle-même, au lieu de faire
faire ce service par Joss. Le test contrôle la consommation d'une seule charge
et la propriété de la réserve plutôt que l'identité de celui qui alimente. Les assertions de conservation, de livraison et
d'engagements tenus restent contrôlées.

Les résultats bruts non versionnés sont dans `artifacts/part-estimee/`. L'outil
versionné `tools/mesurer_part_estimee.py` réutilise `comparer_bancs.jouer_nuit` et
ses relevés d'audit. Les livraisons se comptent après déplacement effectif ; les
accords ne sont pas des livraisons. Les recharges et allumages se comptent après
succès du geste réel. Les durées instrumentées de justesse ne sont pas incluses
dans les temps CPU avant/après.

```powershell
$py = 'C:/Users/msics/donjon/.venv/Scripts/python.exe'
$env:PYTHONIOENCODING = 'utf-8'
# Depuis le worktree de la branche ; références détachées créées au préalable.
& $py tools/mesurer_part_estimee.py --reference ../codex-part-estimee-ref --scenarios auberge --graines 1985 7 42 2024 3 11 99 500 --heures 12 --processus 4 --dossier artifacts/part-estimee/auberge-12h
& $py tools/mesurer_part_estimee.py --reference ../codex-part-estimee-ref --scenarios auberge --graines 1985 7 42 2024 3 11 99 500 --heures 12 --processus 2 --justesse --dossier artifacts/part-estimee/justesse-12h
& $py tools/mesurer_part_estimee.py --reference ../codex-part-estimee-main-ref --graines 1985 7 42 2024 --heures 8 --processus 2 --dossier artifacts/part-estimee/main-8h
& $py tools/mesurer_part_estimee.py --reference ../codex-part-estimee-ref --graines 1985 7 42 2024 --heures 8 --processus 4 --dossier artifacts/part-estimee/base-8h
& $py tools/mesurer_part_estimee.py --reference ../codex-part-estimee-ref --graines 42 --heures 2 --processus 2 --verifier --verification 1 --dossier artifacts/part-estimee/controles-2h
& $py tools/mesurer_part_estimee.py --reference ../codex-part-estimee-ref --graines 42 --heures 8 --processus 2 --verifier --verification 0.2 --dossier artifacts/part-estimee/controles-8h
```

Références temporaires : `codex-part-estimee-ref` à `4fc5212`,
`codex-part-estimee-main-ref` à `5594028` (`origin/main` après le fetch demandé).
La seconde comparaison inclut donc la force 4b déjà portée par la branche de tâche.
Les sauvegardes historiques de preuve sont celles versionnées dans les tests,
jamais `sauvegardes/`.

Les archives finales portent le préfixe `verifie-` ; les autres dossiers de travail
gardent les essais intermédiaires et ne fondent pas les tableaux ci-dessus. Les
worktrees détachés de référence sont retirés après livraison ; on peut les recréer
aux deux révisions indiquées. Les temps restent ceux d'une passe sur ce poste,
pas une promesse de facteur constant. Le contrat général de replanification réelle
est préservé ; l'estimation et tous les critères de comportement ne sont pas
garantis au-delà des limites et échecs explicités ici.
