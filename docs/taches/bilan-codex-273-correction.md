# Lot 273 — résultats de la correction fournitures/sommeil

29 octobre 2026. Branche `codex-demande-adoptee`, moteur **`4047c16`**, non
fusionnée. **Deux critères non tenus : fusion à différer.** Ce bilan ajoute
des diagnostics et de la documentation ; aucun moteur, test ou oracle modifié.

## Sources et portée

`C:/Users/msics/donjon/artifacts/demande-273-sol/correction/` : `fin.json`,
`tests.json`, `banc.json`, `synthese-finale.json`, `sources.json`.
Vingt nuits de branche seules, cinq scénarios × quatre graines × 4 h,
un processus réduit ; référence **`0e3e626`** strictement relue dans les vingt
nuits archivées du banc précédent. Aucun nouveau banc de référence, Luna
ou suite complète. Sonde actuelle 265/271, compteur 219 ; S/F/D par `cats`
du lot 183, sans changement de définition. Temps total de la passe :
**2 126,692 s**, dont compléments **1 138,406 s**, à deux processus réduits.
Le SHA-256 du nouveau banc est
`6bdbcc492dfbabae072bdd1c3bb03089e0c95216c08451ab7f8a038fbd19cc98`.

## Tests : cinq échecs instruits, assertions conservées

**449 tests dans 47 fichiers : 444 succès, quatre échecs d'assertion et une
erreur** ; les 16 cas ciblés des deux autres fichiers étaient verts avant
le lancement. Les cinq cas en échec ont été rejoués avec les mêmes assertions
sur une extraction isolée de **`9a1ba3e`**, parent de la correction, sans
changement de branche. Trois y passent, deux y échouent déjà. Les traces et
captures sont dans `correction/instruction/` ; les noms abrégés ci-dessous
renvoient aux noms complets du JSON des tests.

| Cas | Parent | Correction | Diagnostic |
|---|---|---|---|
| `test_detecter_changements_avis`, réveils Brune | Vert | `KeyError: 929` | Le retour à 591 est toujours certifié ; celui de 929 n'a plus lieu. |
| `test_dynamique_besoins`, recherche Lucien | Vert | Recherche incomplète à 120 min | Lucien trouve réellement Anselme à 115 min ; la recherche n'est pas épuisée. |
| `test_pas_compagnons`, ordre des ventes | Même échec | Mael avant Aubin | Écart hérité du lot avant fournitures/sommeil ; aucune cession indue observée. |
| `test_pas_compagnons`, lieu du service | Même échec | `None`, attendu antichambre | Ilse n'est plus localisée dans la croyance de Brune au constat. |
| `test_service_repropose`, capture/laps | Vert | Deux services rejetés | Défaut commun d'admission atteint par la nouvelle trajectoire. |

**Brune.** En parent, les retours d'agenda à 591 et 929 ont les preuves
respectives `possession_nouvelle` et `lieu_cru_change`. En correction,
l'épisode d'agenda est continu **591–1003** ; il n'y a pas l'intermède de
faim du parent à 747, donc pas de retour à 929 à classifier. Le retour 591
reste `entree_publiee_utilisee`, avec possession/propriété des crochets et
plan de vente admissible. Les mondes, rendus et scènes rechargés sont égaux
dans les deux moteurs (six contrôles). Le test dépend d'une trajectoire
datée qui n'est plus exercée ; aucune preuve manquante n'est inventée et
son oracle n'est pas affaibli. Une capture de départ assurant les deux
vrais réveils serait nécessaire pour conserver sa prémisse.

**Lucien.** La reprise du ballot par Anselme a bien lieu à **113 min**, puis
il le dépose dans la chambre au poêle. Le sommeil de sa demande de restitution
sans moyen à 109 min libère d'autres choix ; l'entretien du poêle sans moyen
dort également à 113 min. À **115 min**, Lucien entre dans la chambre,
voit Anselme et reprend le ballot ; à 116 il le redépose à l'étable. À 120,
sa croyance d'Anselme est donc connue dans la chambre (vue à 115), et seules
cinq salles figurent dans sa recherche. L'assertion « toutes les salles
recherchées » échoue pour une prémisse fausse, pas pour une recherche
épuisée oubliée : le personnage recherché a été trouvé. Six contrôles de
recharge monde/rendu/scène sont verts à 110 et 120. Le cas ne certifie plus
l'attente après épuisement ; ses assertions restent intactes, sans prolonger
arbitrairement le temps ni déplacer un PNJ pour les satisfaire.

**Deux écarts hérités.** L'ordre de vente est exactement
`ilse, mael, aubin, marchand` sur les deux moteurs. L'instrumentation de la
correction confirme à cinq minutes : crochets toujours possédés et portés
par Brune, aucune parole de service prise, aucun service cédé ; le test
continue néanmoins d'échouer sur l'ordre attendu. Pour la torche payée,
`retenir_service` est appelé à **3 min** : lieu cru d'Ilse **inconnu**,
bien que sa position réelle soit l'antichambre. `lieu_beneficiaire=None`
est donc compatible avec les connaissances du prestataire ; le placement
d'auteur ne garantit plus la connaissance attendue au constat. Le service
tenu reste enregistré et les laps/recharges restent égaux. Ces deux
échecs préexistent à `4047c16`, pas nécessairement à la base entière du 273.

**Tilo : défaut réel, fusion bloquée.** Sur la capture auberge 235, à
**226 min + 352 dixièmes**, le plan propose `servir marmite_1_1 pour mathurine`.
Tilo est en cuisine, Mathurine au cellier, son lieu cru est **inconnu**.
Pourtant `_mesurer_direct` admet ce geste et `pnj.refus_etape` renvoie `None` ;
`echanges.servir` le rejette. Il réussit la minute suivante après déplacement.
Le rejet se reproduit dans le laps entier et découpé : deux rejets, pas deux
causes distinctes. Sur **la même capture rechargée**, le parent et la correction
produisent tous deux ce plan, la même admission et le même refus absent ;
six égalités monde/rendu/scène passent. La nouvelle trajectoire expose donc
une lacune commune déjà présente : un participant requis non touché dont le
lieu est inconnu échappe au contrôle de présence de `_mesurer_direct`.
Correction proposée : imposer une présence crue ou une venue convenue pour
tous les participants requis ; sinon rechercher/rejoindre avant le service,
avec la même admission dans la reprise et l'exécution. Ne pas consulter
sa position réelle cachée ni ajouter de cas pour ce repas ou ce bénéficiaire.
**Non corrigé dans ce bilan**, aucun oracle changé.

## Compteur 219 : critère par nuit non tenu

**19/20 paires sans hausse**, mais crue 42 **0→3** : trois répétitions de Gorm
(`marchand`) entre interpositions pour `vivres` et `aubin`, toutes contre
Brune dans l'antichambre. Retours à **32490, 33234, 33255** ; classe
`repetition_sans_entree_nouvelle`, état initial retrouvé exactement,
aucune preuve certifiée. Le seul suspect initial d'Aubin, Relais 2024
`117518`, disparaît toujours. Total **1→3**, donc le critère échoue malgré
cette correction d'Aubin. La causalité fine des trois interpositions n'a
pas été isolée par rejeu et elles ne sont pas reclassées comme bénignes.

| Scénario | Graine | Suspects réf→corr. | À expliquer réf→corr. |
|---|---:|---:|---:|
| Relais | 1985 | 0→0 | 0→5 |
| Relais | 7 | 0→0 | 0→0 |
| Relais | 42 | 0→0 | 1→1 |
| Relais | 2024 | 1→0 | 1→0 |
| Mine | 1985 | 0→0 | 1→0 |
| Mine | 7 | 0→0 | 1→0 |
| Mine | 42 | 0→0 | 1→1 |
| Mine | 2024 | 0→0 | 2→0 |
| Auberge | 1985 | 0→0 | 0→3 |
| Auberge | 7 | 0→0 | 0→0 |
| Auberge | 42 | 0→0 | 0→0 |
| Auberge | 2024 | 0→0 | 1→1 |
| Crue | 1985 | 0→0 | 0→1 |
| Crue | 7 | 0→0 | 0→0 |
| Crue | 42 | 0→3 | 6→14 |
| Crue | 2024 | 0→0 | 1→1 |
| Hameau | 1985 | 0→0 | 2→1 |
| Hameau | 7 | 0→0 | 2→2 |
| Hameau | 42 | 0→0 | 2→2 |
| Hameau | 2024 | 0→0 | 0→3 |

## Richesse : mine toujours hors critère, perte non légitimée globalement

| Scénario | S réf→corr. | F réf→corr. | D réf→corr. |
|---|---:|---:|---:|
| Relais | 15,25→14 | 4,25→4,5 | 1,750→1,750 |
| Mine | **25,75→16** | **5→4,5** | **1,964→1,679** |
| Auberge | 9,25→14,75 | 4→4,25 | 1,000→1,156 |
| Crue | 23,5→21,5 | 6,75→7,5 | 3,063→3,250 |
| Hameau | 22,75→22 | 7,25→7,25 | 2,167→2,125 |

Mine : S **32→16 / 19→16 / 24→19 / 28→13** (1985/7/42/2024).
S moyen **16** reste sous le minimum de référence **19** ; F **4,5** sous
**5**. D revient dans l'étendue des références (1,571–2,714), mais perd
encore **14,5 %** en moyenne. Par rapport à la version avant fournitures/
sommeil, S gagne seulement 0,75 et D 0,214 ; cela ne valide pas le critère.

Signatures exactes : **60 perdues, 21 gagnées, solde −39** (−9,75/nuit).
Pertes/gains par famille : demandes **32/6**, offres **15/3**, appels **5/7**,
services **4/5**, interpositions **4/0**. Auteurs des pertes : Josse 17,
Rémy 16, Odon 11, Gaspard 6, Mathé 5, Bram 3, Lucien 2. Interpositions
absentes en mine 1985 et 7 : quatre familles au lieu de cinq. Détail par
nuit et toutes les signatures dans `instruction/bilan-correction-273.json`.

Le défaut 373 est bien corrigé dans les chroniques : Josse nourrit Odon dès
la minute zéro dans les quatre graines. Les repas effectivement racontés
restent **19→19**, et les crédits `service` **8→9**. En 1985, le repas de Josse
à Odon remplace notamment le repas de Josse par Bram et celui d'Odon par
Mathé à 31 min. Ces substitutions expliquent des interactions différentes,
mais ne prouvent pas la légitimité des 60 signatures perdues. **Aucune
certification globale de perte légitime**, donc second critère non tenu.

## Entrées, alertes et hypothèse du sommeil

Les entrées `a_expliquer` passent de **21 à 35** : hausses Relais 1985
**0→5**, Auberge 1985 **0→3**, Crue 1985 **0→1**, Crue 42 **6→14**, Hameau
2024 **0→3**. Respectivement : alternance secours/ronde d'Aubin avec nouvelles
croyances ; secours de Mathurine/Mireille vers Tilo ; ronde de Gorm à 132000 ;
agendas/entretien et nombreuses interpositions de Gorm ; abri de Brune,
secours de Mael et interposition de Gorm. Les entrées changées sont conservées
comme indices, jamais promues en certificats causaux. Crue 7 et Hameau 42
ne dépassent plus leur référence ; Crue 2024 reste à un.

Autres constats : `voir_alterne` de Gorm au Relais 2024 (une observation),
`fige_presse` **3→2**, `repetition` **4→2**, `noir_long` **1→1** (Lucien en
auberge 1985 dans la correction). Cinq cessations physiques de services payés
contre trois, et aucun départ du bénéficiaire contre un : ce sont les classes
de la sonde, pas des preuves de maintien indéfini promis. Dérives ouvertes
totales **203→172**, cycles accomplis **503→498**, minutes urgentes en attente
**695→1060** ; **zéro plantage et zéro usurpation**, sans garantie que chaque
plan proposé est admissible (contre-exemple Tilo ci-dessus).

L'hypothèse « demande typée sans moyen qui attend sans borne » est
**confirmée et corrigée sur les cas rechargés**, avec sommeil, palier libéré,
réveil sur moyens nouveaux et absence de réveil par seule horloge. Le rejeu
Lucien observe effectivement les sommeils d'Anselme à 109 et 113. Cela
n'établit pas qu'elle expliquait les dérives de Gorm : ses dérives ouvertes
font **62→88→77** (référence / avant correction / correction). Par scénario :
Relais **5→14→14**, Crue **18→34→37**, Hameau **39→40→26**. Les gardes avec
plan vide admissible restent actives ; les ventes sans demande typée ne
sont pas changées en demandes dormantes, et les agendas gardent leur propre
sommeil. Les archives ne tracent pas individuellement les transitions du
nouveau stock de sommeil. **Pas de preuve que l'immobilisation de toute garde
ou vente était une demande épuisée ; pas de résolution générale annoncée.**

Suite nécessaire avant fusion : contrat commun de présence des participants,
prémisses stables des tests de trajectoire, attribution/correction des trois
suspects et explication du recul de mine restant. Aucun calcul actif à la
clôture de ce bilan ; `fin.json` reste **`ok=false`**.
