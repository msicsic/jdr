# Les signes et leur lecture — relations 3c

Branche `codex-relations-3c`, non fusionnée, worktree `tmp-worktrees/codex-relations-3c`.
Base `df39e5d`, issue de `origin/main` `a7ecb50` (relations 3b et corps 4a intégrés).
Le `main` local de ce poste reste à `06602a6` ; la référence des bancs est donc le `main`
distant récupéré au démarrage, fixé à `a7ecb50`, sans avancer ni modifier `main`.

## Règles et fonctions

`donjon/relations.py` reste l'unique lecture des cinq axes. Son crochet de souvenir,
après déduplication de la preuve et application du tort, appelle `signes.eprouver` pour
la colère immédiate. L'émotion garde une ancre, une cible et une intensité ; sa demi-vie
est de quinze minutes et sa lecture est pure. Un refus n'y entre que pour méfiance et
avec une fierté d'au moins 60.

`donjon/signes.py` porte la table `SIGNES`, les comportements choisis, leur perception,
les jets et les projections. Les signes de place et de regard viennent d'une décision
notée dans `intention.attitude` (`place` et `regard`, chacune avec signe, cible et sens).
L'affichage vérifie encore la distance ou l'orientation physique : une intention périmée
ne suffit pas à raconter une position. Les signes n'inventent aucune entité.

- `place` évalue les cases voisines permettant encore le séjour, d'après les personnes
  crues présentes ; le pas passe par le trajet commun. Une égalité ne fait pas bouger.
- `surveiller` et `regarder` tournent réellement le PNJ libre vers une menace crue ;
  la rotation prend le temps commun et change son cône. Un guetteur qui cache son
  intention regarde ailleurs.
- `de`, `percus` et `publics` distinguent production, accès sensoriel et données publiques.
  Les expressions demandent leur lumière et leur portée ; les tons proviennent des mots
  réellement saisis par l'ouïe commune. Un tiers mécanique caché n'est pas dévoilé par
  la cible d'un signe. Les identifiants des signes sont opaques.
- `lire` compte un essai par signe et par dix minutes, échec compris, avec PSY modulée,
  proximité, lumière, familiarité, dissimulation par VOL et mensonge par ELO. Le tirage
  est séparé et compté dans `data`, sans consommer les jets ordinaires.
- `actives` applique la péremption des croyances ; `impressions` exige encore le signe
  actuel pour le rendu. La source directe est `devine`, le récit transmis reste du
  ouï-dire. La vérité et les détails du jet restent réservés à la chronique omnisciente.
- `bilan_signes`, la commande `observer`, `rendu.regarder` et `scene_percue` projettent les
  observations et impressions du joueur ; les listes et infobulles de la page les montrent.
  L'humeur et sa réaction au bruit sont retirées, le compteur `vols_surpris` reste distinct.
- `intentions_lues`, `hostile_cru`, `flairer` et la nouvelle `intention_lue` alimentent les
  décisions communes : garde, regard, place et doute d'une affirmation. Une intention
  supposée ne devient pas un vol constaté et ne sanctionne pas la relation.
- `banc_pnj --regler gorm.PSY=16` surcharge les caractéristiques ou valeurs du profil,
  sans changer le scénario. Le nom court ou l'identifiant peut désigner le PNJ.

Les lectures des PNJ sont déclenchées aux événements et aux minutes du moteur, pas lors
d'une consultation de la vue. C'est nécessaire pour que découper une attente en rotations
et recharger en cours donne les mêmes esprits. `planification._entrees` inclut les lectures
encore actives et leur cible. `spatial.etat_signes` est une clé sociale séparée de la clé
physique : les relations, émotions et intentions peuvent changer pendant la perception
sans invalider une ligne de vue inchangée. La vérification spatiale recompare les signes
mis en cache à leur calcul pur.

Le rejeu conserve les croyances et émotions ainsi que, pour chaque jet, le signe perçu,
l'observateur, l'instant, PSY, dé, marge et interprétation. Les projections envoyées à Luna
ne contiennent aucun de ces résultats cachés ni les axes.

## Vérifications et mesures

Les résultats définitifs de la suite, des huit contrôles et des bancs sont consignés ci-dessous.
Les mesures versionnées dans `mesures-codex-11-relations-3c.json` donnent les dénominateurs,
la configuration et les empreintes des fichiers du moteur mesuré. Les journaux détaillés du poste
restent dans `artifacts/relations-3c/` (ignoré par git).

Suite finale : **1 437 tests, 4 ignorés**, aucun échec ni erreur, 218,503 s,
avec `python tools/tests.py --processus 3` (priorité réduite). Les quatre ignorés sont
des dépendances facultatives, pas des vérifications Luna prétendument passées.
Les commits fonctionnels signés sont `21061d4` et `29decf6`, avec la mesure de registre `05b3720`, après le correctif de
simulations `4ecec03` ; signatures ED25519 vérifiées avec la clé publique du poste.

### Cas et contrats vérifiés

- `tests/test_signes.py` : 18 tests, avec sauvegarde/rechargement. Déplacement réel d’Ilse
  à l’écart de Brune et cas inversé ; texte, carte, commande locale et impressions ; noir,
  dos et cible cachée ; colère dédupliquée et décroissance ; méprise persistante, parfois
  nette ; pas de relance gratuite ; péremption des lectures directes et transmises ;
  flux aléatoires distincts du moteur et entre observateurs ; tons seulement entendus ;
  PSY réglable ; soupçon d’un gardien suivi de sa rotation ; deux mensonges typés sans
  apprendre la vérité ; perte de perception distincte d’un changement d’attitude.
- Le guet historique vers 122 min n’est plus celui de la nuit actuelle. Une capture réellement obtenue pendant ce chantier
  du Relais graine 7 à **441 min**, sans déplacer les acteurs ni retoucher leur profil,
  est versionnée dans `tests/data/scenes/guet_relais7.json.gz`. Le test reprend ce monde,
  applique le même dé contrôlé **18** à Gorm : PSY 14 lit le guet, PSY 8 ne tire rien ;
  puis passage moteur, sauvegarde, rechargement et contrôle de la vue du joueur éloigné
  (aucune fuite de Brune). Le prochain dé naturel de cette capture vaut **20**, qui peut
  réussir dans les deux variantes : ce test prouve la différence de seuil, pas une
  séparation garantie de chaque paire de nuits. Un autre test applique la même règle
  à Lucien/Hugues dans l’auberge, au même dé contrôlé 13.
- Les références publiques des signes sont opaques ; projection limitée aux observations
  et impressions actuellement accessibles. Aucun axe, vérité, DD, dé ou marge dans ces
  champs du contexte envoyé au MJ. La chronique et le rejeu omniscient conservent les
  preuves du jet pour l’auteur. Les lectures du joueur restent dans un journal séparé,
  pour que consulter/observer ne change pas la chronique des PNJ à temps égal.

### Contrôles des caches et de la perception

Les quatre scénarios, graine 42, ont passé successivement **2 h avec `VERIFIER=1`
et `VERIFICATION=1`**, puis **8 h avec les deux à 0,2** : huit nuits sans écart,
aucun arrêt par `planification.BORNES`. Le planificateur traite toute valeur vraie
comme une vérification complète ; 0,2 échantillonne seulement le contrôle spatial.
Les temps de ces contrôles instrumentés sont exclus de la comparaison de performance.

Un contrôle à l’entrée de `signes.lire` recompare chaque signal visuel fourni avec
les signes réellement perceptibles du même observateur à cet instant : **18 321
signaux soumis au circuit**, répétitions comprises, aucun sans support perceptible.
Les 36 signaux de mots passent par le circuit d’ouïe ; les tests contrôlent séparément
que les tons ne sont reçus qu’après mots saisis. Ce contrôle moteur et les preuves
conservées dans la chronique/rejeu ne remplacent pas un audit sémantique de Luna.

### Adaptations de tests existants

Les anciennes assertions d’`humeur` sont remplacées par les signes physiques et la mémoire
réelle du bruit/vol. Les événements `lecture` sont comptés séparément des gestes. Le test
qui isole le choix d’un confident attend que la colère immédiate soit retombée ; la nuit
libre de sécurité peut maintenant rapprocher réellement Ilse de sa compagnie.
Le test de remboursement d’une tâche charge toujours l’archive à 151 min, mais immobilise
Aubin pour isoler ce contrat : dans la nuit libre actuelle, surveiller Brune peut empêcher
Aubin de constater le départ de Gorm avec la torche. Sa promesse reste alors crue faisable,
et l’ancien remboursement exact cinq minutes après n’est plus garanti. Ce changement
social n’est pas présenté comme une correction de l’information manquante.

La crue graine 7 continue de prendre les planches et d’alimenter/allumer le poêle,
avec les charges et propriétés attendues après rechargement, mais ne demande plus
les bûches de Gorm sur ce parcours. Le test ne fige plus cette réplique intermédiaire.
Dans la crue graine 500, Aubin appelle à 187 min au sec puis 227 min avec **12 cm**
d’eau au refuge ; à 360 min il y reste avec **9 cm**, les trois autres sont au sec.
Ce lieu ne devient pas noyé. Le contrôle prend désormais les profondeurs à l’instant
réel des événements : aucun appel depuis une salle noyée, aucun chauffage dans l’eau,
et positions finales sous le seuil de noyade après rechargement. L’ancienne affirmation
« aucun appel avec la moindre eau aux pieds » n’est plus garantie, ni revendiquée.

Six échecs MiMo/fournisseurs étaient déjà présents sur `a7ecb50` lorsque `jsonschema` est
installé. Le commit signé séparé `4ecec03` remet les simulations au contrat courant
(`presentation` dans l’audit et mémoire visuelle canonique du monde chargé) ; il ne change
ni fournisseur ni nombre d’appels du jeu.

### Banc complet avant → après

Référence `a7ecb50`, puis branche `05b3720`, **8 h**, départ tiré, joueur passif.
Relais : 1985, 7, 42, 2024, 3, 11, 99, 500 ; mine, auberge, crue : 1985, 7, 42, 2024.
Vingt nuits de référence puis vingt de branche, lots successifs à **trois processus**,
priorité réduite, aucun appel modèle. Aucun plantage, aucune violation de `Monde.verifier`
ni usurpation. Les durées ci-dessous sont les moyennes **CPU**, hors audits et rejeu,
sur ce poste partagé ; une seule paire finale, sans estimation d’intervalle de confiance.

| Scénario | CPU s/nuit avant → après | Écart CPU | Tentatives avant → après | Vols vus sur la nuit avant → après | Vols encore en mémoire, branche |
|---|---:|---:|---:|---:|---:|
| relais | 5,33 → 6,865 | +28,802 % | 1,5 → 1,125 | 0,875 → 1 | 1 |
| mine | 16,363 → 22,852 | +39,651 % | 0,75 → 0,75 | 0,5 → 0,25 | 0 |
| auberge | 16,113 → 18,828 | +16,848 % | 2,25 → 2,25 | 1,25 → 1 | 1 |
| crue | 10,156 → 13,496 | +32,885 % | 3,25 → 3,25 | 1,5 → 1 | 1 |

Le nouveau `vols_vus_nuit` observe les témoins visuels du registre commun pendant
**toute** la nuit ; `temoins_vols_nuit` distingue aussi le témoin. La paire auteur/objet
n’est comptée qu’une fois. Le comparateur applique la même instrumentation à l’ancienne
référence. `vols_vus` garde son ancien sens de souvenir encore en mémoire finale, pour
ne pas changer silencieusement les mesures existantes. Les lectures peuvent évincer
ces souvenirs bornés : à la mine, 0 en mémoire n’est donc pas 0 vol réellement vu.
Le test d’éviction couvre Brune puis Ilse, par le registre réel, avec rechargement.
Les **40 empreintes d’état final sont identiques** à la passe précédente sans ces
compteurs : ils ne changent aucune décision ni donnée du monde.

| Scénario | Lectures/nuit | Méprises/nuit | Justes / lectures (PSY 10–12) | Guets repérés/nuit | Minutes sous regard/nuit |
|---|---:|---:|---:|---:|---:|
| relais | 61,125 | 23,125 | 304 / 489 = 0,622 | 1,25 | 10,82 |
| mine | 258,5 | 104,75 | 615 / 1034 = 0,595 | 10,25 | 114,445 |
| auberge | 31,5 | 16,5 | 60 / 126 = 0,476 | 1 | 33,058 |
| crue | 86,5 | 38,5 | 192 / 346 = 0,555 | 0,25 | 18,059 |

Ces nuits par défaut ne contiennent aucune lecture en tranche PSY basse ou haute :
les zéros correspondants dans le JSON signifient **pas d’échantillon**, pas une
justesse nulle. L’étude réglée ci-dessous porte ces tranches. Au total, 824 méprises
sur 1 995 lectures par défaut (**41,3 %**), donc bien au-dessus de la borne de 20 %.

| Scénario | Place | Regard | Expression | Ton | Durée |
|---|---:|---:|---:|---:|---:|
| relais | 22,5 | 34,75 | 18,5 | 3,25 | 3,875 |
| mine | 96,75 | 91,5 | 101,25 | 7 | 46,25 |
| auberge | 2 | 23,75 | 4,25 | 1 | 12,5 |
| crue | 25,5 | 53,25 | 26,75 | 16 | 5 |

Les `signes_<sorte>` comptent les signes soumis à un **nouvel essai**, même si celui-ci
ne donne aucune interprétation, pas toutes les projections/consultations. Les
`guets_reperes` sont des lectures réussies d’une intention illicite avant le geste ;
un même guet peut être relu dix minutes plus tard. `attentes_sous_regard` mesure la
durée réelle d’attente en présence d’un surveillant qui le perçoit.

Le Relais améliore les vols vus avec moins de paires tentées. La mine, l’auberge et
la crue gardent leur nombre moyen de tentatives mais voient moins de vols ; les
attentes surveillées et les guets lus attestent un changement de conduite, **pas**
une preuve causale suffisante que ces trois baisses viennent de guets dissuadés.
Le critère des vols vus n’est donc pas déclaré atteint dans ces scénarios.
La borne CPU +20 % passe seulement à l’auberge, manque les trois autres.

Les constats de l’audit ne sont pas tous verts : nouvelles attentes pressantes sans
recours (Relais 42/11, crue 7), passages longs dans le noir (Relais 2024), avertissement
répété (crue 42), et autres constats déjà présents sur la référence. Les alertes
`repetition` de la mine et de la crue portent aussi sur les lignes de chronique
« Lecture de … », relues à dix minutes ; elles ne prouvent pas à elles seules une
boucle de gestes. Le JSON versionné conserve tous les constats par graine ; ils ne
sont ni supprimés ni assimilés à des plantages.

Le contrôle du rejeu sur la capture réelle à 441 min conserve le signe `attend`, le dé
18, la marge **+1 à PSY 14** (guet) et **−2 à PSY 8** (aucune impression), à l’instant
264 600. Le signe figure dans la perception de Gorm au moment du jet ; les données
exportées du rejeu gardent cette preuve. Après sauvegarde/rechargement, la vue éloignée
du joueur ne révèle toujours aucun signe de Brune. Les deux pages autonomes produites
sur le poste sont `artifacts/relations-3c/guet-psy14.html` et `guet-psy8.html` ; les
résultats du contrôle sont aussi versionnés dans le JSON des mesures.

### Variation de PSY, sans Luna

Relais/Gorm puis auberge/Hugues, PSY 8, 14, 16, chacun sur les quatre graines
1985, 7, 42, 2024, 8 h : **24 nuits supplémentaires**, lots successifs à trois
processus au plus. Cette table ne compte que le lecteur dont la PSY est réglée,
pas tous les PNJ de la nuit. La justesse se mesure parmi les interprétations retenues ;
un échec de 1 à 5 ne produit pas de lecture.

| Lecteur | PSY | Essais | Lectures retenues | Justes | Méprises | Justesse |
|---|---:|---:|---:|---:|---:|---:|
| Gorm | 8 | 104 | 82 | 47 | 35 | 0,573 |
| Gorm | 14 | 104 | 81 | 59 | 22 | 0,728 |
| Gorm | 16 | 104 | 80 | 64 | 16 | 0,800 |
| Hugues | 8 | 38 | 31 | 14 | 17 | 0,452 |
| Hugues | 14 | 39 | 28 | 16 | 12 | 0,571 |
| Hugues | 16 | 39 | 30 | 19 | 11 | 0,633 |

La tendance croissante est observée, avec peu d’essais pour Hugues ; ce n’est pas une
preuve statistique sur toutes les scènes. Le plafond bas ≤ 0,6 est atteint ici. La
borne haute ≥ 0,8 n’est atteinte que par Gorm à 16, pas par Gorm à 14 ni Hugues à 14/16.
Même Gorm à 16 a exactement 20 % de méprises, donc manque la borne **strictement**
inférieure à 20 %. Aucun réglage propre à un PNJ ou une scène n’a été ajouté pour
faire passer ces chiffres.

### Reproduire les mesures

Employer le Python du dépôt, en UTF-8 pour les tableaux Windows. Les lots ci-dessous
sont à lancer **l’un après l’autre**, jamais au-delà de trois processus. L’outil refait
référence puis branche pour chaque lot ; la passe rapportée a groupé les vingt nuits
de référence avant les vingt nuits de branche. Ne pas utiliser le `main` local antérieur.

```powershell
python tools/tests.py --processus 3
python -X utf8 tools/comparer_bancs.py --reference a7ecb50 --scenarios relais --graines 1985 7 42 2024 3 11 99 500 --heures 8 --processus 3 --sortie artifacts/relations-3c-relais.json
python -X utf8 tools/comparer_bancs.py --reference a7ecb50 --scenarios mine auberge crue --graines 1985 7 42 2024 --heures 8 --processus 3 --sortie artifacts/relations-3c-autres.json
python -X utf8 -m donjon.banc_pnj --scenario relais --joueur chambre_cloche --graines 1985 7 42 2024 --heures 8 --processus 3 --regler gorm.PSY=8 --sortie artifacts/relations-3c-gorm8.json
python -X utf8 -m donjon.banc_pnj --scenario auberge --joueur dortoir --graines 1985 7 42 2024 --heures 8 --processus 3 --regler hugues.PSY=8 --sortie artifacts/relations-3c-hugues8.json
```

Répéter les deux dernières commandes avec PSY 14 puis 16 et des sorties distinctes.
Extraire les entrées `nature=lecture` du seul `observateur` réglé pour reproduire la
table de PSY. Ne pas activer `--stratege` : ces bancs n’appellent aucun modèle.
Les contrôles se reproduisent avec `banc_pnj.nuit(scenario, 42, heures, salle)`, après
`banc_pnj.ceder()`, en affectant `planification.VERIFIER` et `spatial.VERIFICATION`
aux taux indiqués, pour les quatre salles de joueur de la configuration versionnée.

## Critère et réglages proposés

**Critère global de 3c non atteint.** La cohérence de la perception, la persistance,
les flux de dés et les contrôles de cache passent ; la justesse haute, la part des
méprises, trois coûts CPU et les baisses non expliquées des vols vus manquent les bornes. La réalisation est livrée sur sa branche pour examen,
sans déclarer la calibration acquise et sans fusionner `main`.

Les valeurs du jet restent celles du plan : DD 10 + force (0/2/3), dissimulation
`mod(VOL ou ELO)+5`, pénombre −4, distance −2, familiarité +2, observation +2,
relecture après 10 min. Colère demi-vie 15 min ; signes d’expression à 4 cases en
lumière 2 ; guet prolongé à une minute. Le cumul pénombre/dissimulation rend en
particulier la lecture d’intention difficile. Les échecs profonds sont encore trop
souvent une interprétation erronée plutôt qu’une absence d’impression.

Pour une passe de calibration distincte, mesurer une grille **commune à tous** de
pénombre −4/−3/−2 et dissimulation +5/+4/+3, en contrôlant ensemble justesse haute,
justesse basse, méprises et taux d’abstention. Aucun de ces réglages candidats n’est
validé ni appliqué ici. Le coût restant mérite une invalidation sociale incrémentale,
au lieu de reconstruire la signature de tous les esprits, avec les mêmes contrôles
`VERIFIER`/`VERIFICATION`. Ni exception de scénario ni instruction de prompt ne peut
remplacer ces mesures. Les constats de nuit libre ci-dessus restent des limites à
examiner, pas des preuves d’absence de boucle.

## Limites et périmètre

Aucune empathie décisionnelle (3d), proposition (3e), dispute ou avis spontané (3f).
`PRET` reste inchangé. L'audit par citation d'attitude de 3g n'est pas réalisé ici : le
contrôle déterministe de ce chantier porte sur les données transmises au MJ, la perception
et l'absence de vérité cachée dans ces données, pas sur toute interprétation de prose libre.
Aucune migration d’ancienne sauvegarde n’est ajoutée.

Limites conservatrices du modèle : les expressions et tons dissimulés sont entièrement
supprimés ; les comportements persistants restent lisibles avec le DD relevé. Il n’y a
pas encore de détection distincte d’une micro-expression cachée. Le mensonge flairé porte
sur une affirmation typée contraire à ce que croit un auteur identifié ; une voix inconnue
ne reçoit pas une identité par ce chemin. Pour le joueur, seules les propriétés actuellement
visibles servent de connaissance contraire, pas une pensée ou une vérité cachée. Sa place
implicite et son ton ne forment pas un esprit artificiel : seule l’observation explicite
émet un comportement. Le bonus de familiarité repose sur les relations/compagnie des PNJ ;
le seul fait d’avoir appris un nom ne donne pas ce bonus au joueur.


## Vérification Luna à faire

**Non effectuée, sur instruction de l’utilisateur : aucune connexion utilisable sur ce poste,
aucune tentative de connexion à faire ici.** Les anciennes tentatives n’ont fourni aucune
réponse Luna réussie. La validation suivante doit être exécutée sur l’autre poste à la fusion,
avec `gpt-6-luna`, sur des copies et sans comparaison de modèles.

Depuis la racine du dépôt ou du worktree, créer `artifacts` s’il manque, puis :

```powershell
Copy-Item tests/data/scenes/signes_ecart_relais.json artifacts/luna-signes.json
python jeu.py --defi --cases --console --save artifacts/luna-signes.json --connexion chatgpt
```

Utiliser le Python du dépôt (`.venv\Scripts\python.exe` ; depuis ce worktree,
`..\..\.venv\Scripts\python.exe`). Le coffre sera celui déjà disponible sur l’autre poste.
Ne jamais tester sur une sauvegarde utilisateur. Forme complète de la perception locale :

```json
{"action":"observer","cible":"ilse","outil":"","methode":"simple","difficulte":0,"justification":""}
```


| Saisie exacte, dans cet ordre | Forme/route attendue | Appels attendus | Ce que le joueur doit lire |
|---|---|---:|---|
| `observer Brune` | locale `{action: observer, cible: brune, outil: "", methode: simple, difficulte: 0}` | 0 | Les signes d’Ilse peuvent apparaître au bilan automatique : « Ilse se tient à l’écart de Brune. », baisse les yeux, tremble. Aucune attitude inventée pour Brune. |
| `observer Ilse` | même forme, `cible: ilse` | 0 | Ces signes et « Ilse semble craindre Brune. », « Ilse semble avoir peur. » ; impressions, jamais certitudes. Chaque observation consomme trois secondes. |
| `Que remarques-tu dans la façon dont Ilse se tient ?` | interprétation dialogue, `proposition: null` | 2 si premier audit accepté | Décrire seulement les signes reçus ; pas d’axe ou de projet caché. |
| `Ilse a-t-elle peur de Brune ?` | dialogue, `proposition: null` | 2 si premier audit accepté | Peut rappeler l’impression de crainte, en conservant son incertitude. |
| `Veut-elle attaquer Brune ?` | dialogue, `proposition: null` | 2 si premier audit accepté | Aucun projet d’attaque établi ; ne pas en inventer. |

Deux appels est le chemin nominal interprétation + audit narratif, pas une mesure obtenue
sur ce poste. Relever le compte réel et les relances/replis éventuels. Quitter/recharger la
copie puis `observer Ilse` : même mémoire de lecture, pas de nouveau dé gratuit dans les
dix minutes, observations encore compatibles avec les positions et la lumière.

Repartir d’une **autre copie** de `tests/data/scenes/signes_ecart_relais_noir.json` :
`observer Ilse` doit être refusé localement (0 appel), puisque non visible ; `regarder`
ne donne aucun signe ni impression ; `Ilse a-t-elle peur de Brune ?` reste un dialogue
(2 appels nominaux), sans renseigner une attitude invisible. Le nom connu ne suffit pas
à rendre sa présence ou son état actuel perceptible.

Enfin, décompresser `tests/data/scenes/guet_relais7.json.gz` vers une copie de sauvegarde
et saisir `Que fait Brune ?` depuis la position initiale du joueur éloigné : dialogue,
`proposition: null`, 2 appels nominaux ; aucune description du guet caché. Ne pas déplacer
le joueur pour ce contrôle de non-fuite. La différence PSY du guet se vérifie au moteur
par les tests précédents, sans demander à Luna de connaître les esprits privés.
