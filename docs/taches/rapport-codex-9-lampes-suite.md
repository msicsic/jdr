# Rapport Codex 9 — les moyens d'éclairer suivent le but

Branche `codex-lampes-suite`, non fusionnée, issue de `main` **9075aea** (tâche portée par
f123463). Worktree `tmp-worktrees/codex-lampes-suite`. Références détachées pour les mesures :
9075aea, et f1eee53 avant les lampes. Aucune fusion ni modification de `main`, aucun appel à Luna,
aucune sauvegarde utilisateur modifiée. Quatre calculs lourds au maximum, en priorité réduite ;
référence puis branche, sur le poste où une autre intégration travaille aussi.

## Invariant et fonctions changées

Une capacité n'est pas un besoin de lumière. La lumière est un moyen quand elle change le coût
du noir, atteint le but explicite, ou intervient dans une lecture du but ou des gestes explorés.
La disponibilité d'une part pour ce moyen passe ensuite par les mêmes règles de compatibilité,
de propriété, de prix, de refus et de livraison que les autres consommables.

`Vue.lumiere` et `lumiere_devant` constatent une dépendance quand le niveau cru peut être amélioré
par une source. `Vue.emploie_lumiere` la rassemble avec le coût du noir et `vises.eclairer`.
`Vue.pertinent`, `gestes` et `_parts_remises` partagent ce contrat : aucune de ces décisions de
pertinence ne déduit désormais le besoin de lumière de la capacité `crochetage`. Cette capacité
autorise toujours le geste de crocheter ; sa chance lit la lumière devant la serrure.

`_explorer` découvre les lectures, arrête cette passe dès la première dépendance révélée,
puis reprend depuis le départ si des moyens avaient été
écartés avant cette découverte. Une seule reprise, avec toute la borne de recherche ; listes
d'objets pertinents et graphe devenus incomplets sont vidés. Le graphe final garde son marqueur
de dépendance, et `VERIFIER` recompare avec une recherche neuve. Le corps de la recherche de
moindre coût devient `_explorer_etats`, sans modification de ses comparaisons ni de ses égalités.
`_entrees` regroupe à sa fin les deux entrées explicites du coût du noir et du but de lumière,
pour rester lisible lors de la fusion après les relations 3b. Les autres lectures dépendent des
objets, profils, croyances et buts déjà décrits par la clé.

Les frontières de `_couper` restent appliquées : une demande ne remplit pas une lampe ; la
recherche se refait sur l'identifiant réellement livré avant `alimenter` et `allumer`.

## Cas vérifiés

`tests/test_lampes_buts.py`, cinq tests :

- Mine, lampe vide de Rémy et bidon de Gaspard : crochetage sans peur du noir ; la chance du
  geste découvre la lumière, le PNJ demande une part, la reçoit, recharge, allume et crochète.
- Mine et auberge : inspection éclairée demandée par le but, sans peur du noir ni capacité de
  crochetage. La part réelle reçue sert à la recharge et à l'allumage, puis le lieu est inspecté.
  L'inspection ordinaire n'a pas reçu une nouvelle obligation de lumière : le test compose
  explicitement les deux conditions du but. Il vérifie ainsi un autre emploi de lumière que la
  chance d'une serrure, avec les gestes et l'exécution réels.
- Contrat d'extension d'un geste : la fixture rend seulement son inspection visuelle dépendante
  de `Vue.lumiere`, et son but ne lit plus du tout la lumière. Le même parcours de remise,
  recharge et rendu aboutit sans peur ni crochetage. Cette règle de fixture n'entre pas dans le jeu.
- Une capacité de crocheter seule ne rend ni le combustible pertinent ni la remise de part
  disponible pour un but sans emploi de lumière.
- Mémoire exacte et graphe repris à la troisième recherche, malgré la découverte différée de
  lumière ; `VERIFIER` compare à la recherche fraîche et à celle sans restriction de portage.

La chaîne demande → livraison → replanification → recharge → allumage → geste final est exécutée
avec sauvegarde/rechargement entre les gestes ; propriété, deux charges conservées dans le lot,
part consommée, source chargée/allumée, visite ou serrure et rendu « éclaire la pièce » contrôlés.
Les tests de parts existants conservent les parcours autonomes au temps vécu, les lots posés,
les achats, la livraison différée et le cas réel de lanterne vide après huit heures.

Suite complète finale : **1 377 tests, OK, 14 sautés**, `tools/tests.py --processus 4`, 383,3 s écoulées,
après l'allègement et le cinquième test. Première passe avant eux : 1 376 tests, 14 sautés, 456,1 s.
`pyflakes` sur les deux fichiers Python : sans constat. Contrôles sur chacun des quatre scénarios,
départ tiré, graine 42 : `VERIFIER` + `spatial.VERIFICATION=1` sur 2 h, puis `VERIFIER` + 0,2 sur 8 h,
sans erreur ; contrôles refaits sur le code final. Les limites reconnues de borne ne sont pas
une preuve d'optimalité globale.

## Pourquoi le noir de l'ancienne crue augmentait

Les chroniques et relevés conservés du chantier initial sont dans
`tmp-worktrees/codex-lampes/artifacts/codex-lampes/{main-8h,branche-finale-8h}`. Comparaison historique
f1eee53 → 9688e34, quatre graines, 8 h :

| Graine | Noir (min·PNJ) | Sans recours (min·PNJ) | En attente (min·PNJ) |
|---|---:|---:|---:|
| 1985 | 115 → 140 | 0 → 0 | 100 → 100 |
| 7 | 15 → 10 | 70 → 70 | 120 → 50 |
| 42 | 0 → 5 | 0 → 75 | 135 → 0 |
| 2024 | 5 → 40 | 0 → 60 | 75 → 70 |
| Moyenne | 33,75 → 48,75 | 17,5 → 51,25 | 107,5 → 55 |

La graine 2024 isole une cause concrète. À la minute 82, les deux foyers sont crus chargés et
allumés. Après avoir trouvé la porte verrouillée, l'ancienne recherche de chaleur donne un plan
de coût 10 : rejoindre le refuge et demander des planches à Aubin ; son état final ne contient
que la promesse et la part reçue, **aucun fait de chauffage**. L'ancien `rechauffe` tenait pourtant
ce but pour atteint. La branche des lampes refuse ce raccourci : elle trouve un plan de coût
12,9067, prendre les crochets, crocheter dans la pénombre (niveau 1), rejoindre le poêle et s'y
chauffer. La trace des deux moteurs confirme les plans et leurs faits ; ce n'est pas une
déduction des seuls textes.

Brune crochète à 87 et se chauffe à 88, au lieu de demander des planches puis de trouver la clé et
se chauffer à 84. L'ouverture, les bruits, les trajets et les rencontres suivants diffèrent.
Ilse entre au palier des vannes (identifiant `beffroi`) à 287 et y apparaît dans le noir aux relevés 290–320 ; sa sécurité reste
sous le seuil d'urgence jusqu'à 315, devient urgente à 320 (61), puis elle rejoint la galerie
éclairée. La référence la laissait au refuge. Sept relevés supplémentaires expliquent 35 min·PNJ
sur les 60 supplémentaires des quatre nuits ; les autres différences viennent notamment des
séjours d'Aubin (1985), de Brune attendant une part au beffroi (42) et d'une fin de nuit améliorée
pour Gorm (7). Les graines 42 et 2024 changent également les attentes et renoncements de faim de
Brune : « sans recours » ne mesure pas seulement l'absence de combustible lumineux.

Il ne faut donc pas rétablir l'ancien raccourci pour faire baisser un compteur. La distinction
entre une part de combustible et une chaleur réellement reçue est voulue et déjà corrigée par
les lampes. Un PNJ qui craint le noir n'entreprend pas nécessairement un but de sécurité avant
son seuil ; la recherche et le choix restent soumis aux croyances, aux coûts et aux priorités.
Ces traces n'établissent aucune amélioration uniforme du noir ou des recours.

## Mesures actuelles et coût de calcul

Référence actuelle 9075aea → branche, départ tiré, graines 1985, 7, 42, 2024. Toutes les valeurs
sont des moyennes par nuit, les minutes sont des min·PNJ. Les audits contrôlent `Monde.verifier`
au fil des pas. Les campagnes de référence et de branche sont successives, à quatre processus.

### Comparateur rapide, 4 h

| Scénario | Noir | Sans recours | En attente | CPU (s) |
|---|---:|---:|---:|---:|
| Relais | 5 → 5 | 45 → 45 | 0 → 0 | 6,51 → 5,04 |
| Mine | 23,75 → 23,75 | 26,25 → 26,25 | 0 → 0 | 11,62 → 10,77 |
| Auberge | 110 → 110 | 20 → 20 | 1,25 → 1,25 | 12,43 → 10,18 |
| Crue | 12,5 → 12,5 | 0 → 0 | 16,25 → 16,25 | 7,48 → 5,45 |

Les **16 couples** gardent la même chronique, les mêmes mesures et l'empreinte du même état final
complet. Zéro usurpation, violation ou plantage. Les signalements d'audit restent les mêmes :
Relais et mine, un `fige_presse` chacun ; auberge, un `noir_long` et un `fige_presse` ; crue,
un `voir_alterne`, trois `fige_presse` et un `eau_longue`.
Le JSON conserve aussi les minima/maxima ; les écarts de CPU changent de sens selon les passes
(première passe auberge 12,07 → 13,54 s, finale 12,43 → 10,18 s), à nuits identiques.
Ce n'est donc pas une preuve de gain de vitesse. Les événements de recharge et de livraison
sont observés séparément dans les audits longs ci-dessous.

### Audit 12 h : auberge et crue

| Mesure | Auberge | Crue |
|---|---:|---:|
| Noir | 882,5 → 882,5 | 43,75 → 43,75 |
| Sans recours | 200 → 200 | 108,75 → 108,75 |
| En attente | 540 → 540 | 276,25 → 276,25 |
| Recharges de lampes (hors foyers) | 0,5 → 0,5 | 0 → 0 |
| Demandes gratuites de combustible | 4,25 → 4,25 | 0 → 0 |
| Achats de combustible acceptés | 3,75 → 3,75 | 0,5 → 0,5 |
| Parts physiques livrées gratuitement | 0,75 → 0,75 | 0 → 0 |
| Parts physiques livrées (gratuites et payées) | 3 → 3 | 0,25 → 0,25 |
| Dont payées | 2,25 → 2,25 | 0,25 → 0,25 |
| Usurpations / violations / plantages | 0 → 0 | 0 → 0 |
| CPU avec instrumentation d'audit (s) | 219,77 → 231,40 | 42,34 → 36,33 |

Les demandes et achats comptent tous les combustibles, tous les refus de demandes gratuites,
et les demandes de service au foyer ; les livraisons comptent seulement les parts physiques
effectivement remises, sans confondre un accord avec une livraison. Ces comptes ne sont donc
pas directement ceux du tableau historique limité aux parts pour les lampes. Une recharge de
foyer est conservée dans les événements mais exclue de la ligne « lampes ».

Les huit couples de nuits ont les mêmes chroniques, mesures, récits, souvenirs, empreintes
physiques du banc, bilans finaux d'audit et événements de ressources. L'audit long n'enregistre
pas l'état complet `data` : il ne faut pas appeler cette égalité une empreinte intégrale de la
sauvegarde. Les nombres de recherches, de nœuds et de reprises sont également identiques.
L'analyseur rend exactement les mêmes signalements sur les huit nuits de chaque côté :
`appels_nombreux` 1, `voir_alterne` 7, `fige_presse` 23, `noir_long` 11,
`illicite_entendu` 11, `illicite_sans_temoin_avec_present` 4, `eau_longue` 2.
Ce sont ses constats descriptifs, pas des violations de `Monde.verifier` ; ils ne sont pas
présentés comme corrigés par cette branche.
Les temps CPU d'une seule passe sur un poste chargé ne prouvent pas un gain ou une régression
de quelques pourcents : la crue baisse de 14 %, l'auberge monte de 5 %, à trajectoires identiques.

### Coût actuel contre la base avant les lampes

Même outil `empreintes_nuits.py`, sans l'observateur d'audit, 12 h, quatre graines, f1eee53 →
9075aea (après `cout-calcul`) :

| Mesure moyenne | Avant les lampes | Main actuel |
|---|---:|---:|
| Auberge, CPU (s) | 106,88 | 195,63 |
| Auberge, nœuds | 552 745 | 1 393 045 |
| Auberge, recherches neuves | 1 641,5 | 1 548 |
| Mine, CPU (s) | 117,57 | 139,99 |
| Mine, nœuds | 1 109 278 | 1 402 286 |
| Mine, recherches neuves | 1 529,5 | 1 524 |

L'écart subsiste donc, surtout à l'auberge. Cette comparaison traverse aussi les autres fusions
depuis f1eee53, et quatre graines seulement ; elle ne mesure pas isolément leur effet ni un
gain contre les huit graines du rapport initial (temps écoulés).

Sur le main actuel, la recherche examine en moyenne 1 393 045 nœuds à l'auberge et 1 402 286 à
la mine. Les durées de planification cumulées par l'outil sont de 163,68 s et 117,22 s ; ce sont
des durées écoulées de recherches, pas une ventilation du CPU. Dans l'audit détaillé de l'auberge,
les deux plus gros groupes, cumulés sur quatre nuits, sont la faim de Tilo (1 118 527 nœuds,
149 bornes) et celle de Joss (1 455 710 nœuds, 179 bornes), puis la garde du grenier et de l'étable
par Lucien (729 276 et 625 591 nœuds, 160 et 144 bornes). Les moyens lumineux restent des moyens
de ces buts par le coût du noir, même quand le plan choisi ne finit pas par demander une part.

L'allègement de cette branche porte sur la découverte de dépendance : arrêter dès la première
lecture utile, au lieu de finir une passe dont le graphe sera jeté. La passe finale, ses coûts,
ses égalités et sa borne restent les mêmes. Contre le premier commit de correction b2a8268,
`comparer_bancs.py --empreintes`, quatre scénarios × quatre graines × 2 h : **16 nuits identiques**,
chronique, mesures et état final complet. Cette optimisation ne prétend pas résoudre à elle
seule le coût des grandes recherches de fin de nuit.

### Contre-épreuve : coût des remises simulées

Pour isoler ce poste, une seconde campagne reprend **le même main 9075aea**, les mêmes données,
graines et durées, en remplaçant seulement `_parts_remises` par un générateur vide, hors du code
livré. Aucun autre geste n'est retiré, aucune autre fusion ne sépare les deux côtés.

| 12 h, moyenne de quatre graines | Main normal | Sans cette projection |
|---|---:|---:|
| Auberge, CPU (s) | 195,63 | 67,57 |
| Auberge, nœuds | 1 393 045 | 311 187 |
| Auberge, noir (min·PNJ) | 882,5 | 973,75 |
| Auberge, nuits dont l'état complet change | — | 4 / 4 |
| Mine, CPU (s) | 139,99 | 115,85 |
| Mine, nœuds | 1 402 286 | 1 120 330 |
| Mine, nuits dont l'état complet change | — | 0 / 4 |

À l'auberge, chronique, mesures, récit, souvenirs, état complet et empreintes physiques changent
pour **chacune** des quatre graines. Le noir passe respectivement de 1 190 à 870 (1985), de 795 à
855 (7), de 985 à 1 170 (42), de 560 à 1 000 (2024). Le retirer ne serait donc pas un allègement
qui conserve les nuits. À la mine, toutes ces empreintes restent identiques ; l'exploration
supplémentaire représente des alternatives non retenues sur ces quatre tirages, pas de nouveaux
gestes exécutés. Les tests de lampes vides établissent néanmoins leur emploi réel dans ce scénario.

L'élargissement de l'espace exploré explique ainsi une grande partie du surcoût, et la différence
entre auberge et mine. Il reste le prix actuel du comportement conservé. Cela ne prouve pas que
tout ce calcul est irréductible : une élimination générale d'états dominés pourrait alléger ces
recherches, mais elle devrait conserver les moyens de recharge et les nuits. Cette branche ne
prétend pas avoir fourni cette preuve ni supprimé le coût résiduel. Les temps absolus restent
sensibles à la charge du poste ; les nombres d'états et les différences d'empreintes ne le sont pas.

## Reproduction et limites

Les fichiers non versionnés sont conservés dans `artifacts/lampes-suite/` : références de coût,
contrôles, comparaison rapide, audits longs, traces historiques, logs et mesures agrégées.
`artifacts/trace_lampes.py` observe les recherches historiques ;
`artifacts/lampes_audit_suite.py` utilise `tools/audit_nuits.py` et observe les échanges et
recharges sans écrire dans le monde ; `artifacts/campagnes_lampes_suite.py` enchaîne les campagnes.
Les compteurs d'événements et le temps CPU sont ajoutés au fichier d'audit après la nuit.
`artifacts/fin_lampes_suite.py` rejoue les contrôles, la suite et le comparateur sur le code final ;
`artifacts/cout_remises_lampes.py` réalise la contre-épreuve, consignée dans
`sans-remises-12h.json` et `contre-epreuve.json`. `gel.json` garde les empreintes des fichiers moteur.
Les trois worktrees de référence temporaires ont été nettoyés après les mesures. Pour réutiliser
ces scripts depuis le worktree de livraison, recréer leurs références :

```powershell
git worktree add --detach .worktrees/lampes-base 9075aea
git worktree add --detach .worktrees/lampes-avant f1eee53
git worktree add --detach .worktrees/lampes-decouverte b2a8268
```

Les campagnes utilisent `C:/Users/msics/donjon/.venv/Scripts/python.exe`, `--processus 4`, départ
`tire` et graines `1985 7 42 2024` ; les contrôles de perception prennent seulement la graine 42.
Le comparateur rapide final utilise `--reference 9075aea --scenarios relais mine auberge crue
--heures 4`. Le contrôle d'identité utilise `--reference b2a8268 --empreintes --heures 2` avec les
mêmes scénarios. Les audits longs passent par `audit_nuits.py jouer --heures 12` puis `analyser`.

La recherche reste bornée en profondeur et en nœuds. Une lecture jamais explorée ne révèle pas
son besoin ; le comptage des nœuds et le statut de borne décrivent la passe finale, alors que le
temps comprend une éventuelle découverte préalable. Une fonction de but doit lire les méthodes
communes de lumière pour déclarer cette dépendance ; une lecture directe des données du monde
ne constitue pas ce contrat. `memo` doit continuer à déterminer le but. Aucun nouveau geste,
mode de jeu, cas de scénario, nom de substance ou consigne à Luna n'a été introduit.
