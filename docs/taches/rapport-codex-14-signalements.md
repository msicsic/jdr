# Codex 14 — expliquer les signalements des nuits

Branche `codex-signalements`, non fusionnée, issue de `main` **43fa7ac** par le commit de tâche
809bd0b. Moteur seul, aucun appel à Luna. Les campagnes ont été lancées successivement, avec
`--processus 3` au maximum ; les tests utilisent la priorité réduite de `tools/tests.py`.

## Résultat et méthode

Deux défauts corrigés : le même désarroi réarmait l'appel à l'aide sans apaisement du besoin ;
une réponse à une recherche pouvait entretenir une tournée au lieu de conduire au rendez-vous
convenu. Le résultat d'un recours reste désormais enregistré hors des quarante souvenirs.
Les autres familles sont expliquées ci-dessous. Les codes bruts restent visibles : leur disparition
par reclassement n'est jamais présentée comme une amélioration du jeu.

Audit de référence : **32 nuits de 12 h**, quatre scénarios × graines **1985, 7, 42, 2024, 3, 11,
99, 500**, départ tiré ; joueur à `chambre_cloche` (Relais/crue), `galerie` (mine), `dortoir`
(auberge). Chroniques, récits et données des pages `--rejeu` ont servi à examiner les causes,
positions, regards, niveaux de lumière et sources sonores. Quatre états de `main` sont conservés
dans `tests/data/signalements-*.json.gz` : Relais 42 à 160 min, Relais 1985 à 120 min, auberge 11 à
500 min et auberge 3 à 570 min. Ce sont des copies de banc, aucune sauvegarde de partie utilisée.

Une seconde passe de référence ajoute les seuls diagnostics de lecture (fonction `inactivite`,
relevés et observateur du rejeu). **Les 32 nuits restent identiques**, sur chronique, mesures,
empreintes, récit et souvenirs, à la première passe non enrichie. Cette contre-épreuve distingue
l'explication d'un signalement d'un changement du moteur. L'audit après correction rejoue les
mêmes 32 nuits avec ces diagnostics.

## Signalements bruts, avant → après

Nombre de constats, pas nombre de nuits ni nombre de minutes. Un PNJ peut avoir plusieurs plages.

| Famille | Avant | Après | Cause et suite |
|---|---:|---:|---|
| `fige_presse` | 80 | 82 | Besoin haut avec attente de moyen, charge confiée ou charge déjà satisfaite. Aucun de ces longs intervalles ne comporte de relevé `sans_recours`. Diagnostic commun, sans modification du choix. |
| `noir_long` | 57 | 67 | Durée réellement vécue, ressources finies, refus, garde ou absence de moyen sur les croyances. Observation physique conservée, pas preuve d'un plan oublié. Hausse à l'auberge : aucune promesse d'amélioration uniforme de la lumière. |
| `illicite_entendu` | 81 | 106 | Ce sont des témoignages auditifs réussis, d'une certitude moindre que la vue. Observation conservée. |
| `voir_alterne` | 25 | 19 | Le compte compare des buts condensés sur toute la nuit, sans identifier un même bruit ni imposer un délai. Revenir garder puis examiner un autre bruit est normal. Le code reste descriptif. |
| `illicite_sans_temoin_avec_present` | 21 | 22 | Aucun témoin attendu au début du geste. Vue absente ; bruit sous le seuil ou objet non situé. Diagnostic précis par présent ; pas d'élargissement de la perception. |
| `eau_longue` | 5 | 5 | Eau réellement présente, comprenant des flaques en décrue ; la durée seule ne prouve pas un piège. Le détail indique désormais toute la plage de profondeurs. |
| `appels_nombreux` | 3 | 4 | Une vraie boucle à l'auberge 3, corrigée ; les autres sont des tournées ou des demandes distinctes. Le nombre de constats augmente malgré la baisse du pire cas, 108 → 16 appels par PNJ-nuit. |
| `appels_a_l_aide` | 1 | 0 | Gorm, Relais 42 : besoin de sécurité toujours urgent mais appel réarmé à chaque sortie du refuge menacé. Correction de l'épisode de désarroi. |
| `repetition` | 6 | 0 | Six textes de la même boucle Anselme/Joss, auberge 3. Correction commune de la recherche et du rendez-vous. |
| `passages_rafale` | 1 | 0 | Même boucle, auberge 3 : maximum de 93 → 38 passages/h dans les huit auberges. |
| `buts_alternes` | 3 | 3 | Gorm, deux crues et Relais 42 : entretien/garde, examen/garde et entretien/abri, sur des besoins et événements distincts. Rien n'assimile désormais leur seule alternance à un défaut démontré. |
| `dette_fin` | 1 | 0 | Dette correctement née d'une tâche devenue impossible, avec refus de remboursement. Elle disparaît dans la nouvelle trajectoire, sans interdire les dettes. |

Tous les autres codes sont à zéro avant et après : plantage, demande en boucle, va-et-vient,
but hors besoin, croyance fausse vue, agitation, bascule, avertissement redit, engagement ancien.
**Zéro usurpation et zéro violation de `Monde.verifier`**, appelé après chaque pas de cinq minutes.

### Les inactivités

Le classement commun est celui de l'ancien `_oisifs_urgents`, extrait en lecture seule dans
`deliberation.inactivite`. Le banc garde donc son sens et ses comptes ; le récit ajoute « Charge
confiée à autrui » et « Charge déjà satisfaite ». L'audit enregistre aussi les besoins en attente et
les renoncements. Sur toutes les minutes urgentes inactives des 32 nuits, avant → après : attente
**19 915 → 19 685**, charge satisfaite **14 200 → 13 950**, sans recours entrepris
**4 185 → 4 025**, charge confiée **2 775 → 3 000** min·PNJ. Les intervalles longs signalés
`fige_presse` ne couvrent que les trois catégories expliquées.

Cas réel : Mireille, auberge 11, 500–725 min, a confié le fourneau par une tâche payée ; son devoir
reste haut, mais elle n'a pas à refaire cette tâche. Hugues, dans la même sauvegarde, a ses rondes
à jour. Au Relais 1985, 120–330 min, Gorm attend notamment la charge confiée au joueur. Le test de
besoin sans aucun recours vérifie séparément l'état `attente` après rechargement.

### Perception et eau

Les 21 gestes de référence sans témoin malgré un présent correspondent à **40 observations de
présents** : 38 sans vue et sous le seuil d'audition (`feutre`), deux sans vue avec son entendu mais
objet non situé. Après : **38 observations**, 32 sous le seuil et six avec objet non situé.
Aucun présent inconscient dans ces cas réels. L'inconscience reste traitée par la règle commune,
comme les exclusions d'un témoin déjà tranché par le moteur. Le registre de rejeu note conscience,
vue de l'auteur, nature du bruit, niveau entendu, objet situé et exclusion. L'analyseur garde
`a_expliquer` si un témoin attendu manque ou si l'ancien fichier ne porte pas ce diagnostic.
La mesure porte sur le début du geste ; les listes de témoins continuent à suivre toute sa durée.

À la crue 500, Gorm, Ilse et Aubin restent 235 minutes dans **1–14 cm** d'eau, au refuge,
sans salle condamnée à être noyée. L'autre plage de Gorm est de **21–57 cm** pendant 75 minutes,
et celle d'Ilse à la crue 11 de **19–43 cm** pendant 75 minutes. La hauteur évolue pendant la plage :
le chiffre du premier relevé ne suffisait pas. L'eau continue de mouiller et d'inquiéter suivant
les règles existantes ; ce lot ne crée ni immunité ni déplacement propre à une profondeur d'exemple.

### Appels et recherches

Gorm, Relais 42 : appels à 154, 193, 225, 254, 280, 309, 337, 365, 391, 423 et 625 min sur la
référence. Entre 154 et 391, la sécurité ne descend jamais sous 71, mais sortir du lieu menacé et
rester sous `DESESPOIR` marquait l'appel « apaisé ». Le moteur attend désormais la fin de l'urgence
de sécurité. `secours` garde ce suivi en sauvegarde, même après éviction du souvenir d'appel.
Un vrai apaisement permet toujours un nouvel appel ; l'abri et le répit gardent leur priorité.

Anselme, auberge 3 : après la réponse de Joss et « J'arrive ! », le plan de biens cherchait encore
Joss dans d'autres salles ; la réponse anonyme ne localisait pas son corps. Une salle visitée
n'était écartée que par un appel *sans réponse*, dont le souvenir pouvait aussi sortir de la mémoire.
Le lieu convenu devient maintenant le moyen du plan qui vise ce même interlocuteur. Une inspection
achevée sans le retrouver est retenue dans `recherches`, avec le même délai d'oubli et la même
révision par une croyance nouvelle que les anciens appels vains. L'échec sur place termine le
rendez-vous, même dans sa minute de création. Le planificateur inclut les résultats actifs dans sa
clé de reprise. Aucun de ces faits n'établit l'identité d'une voix inconnue.

Anselme passe de **108 à 15 appels** dans sa nuit ; les 102 « quelqu'un ? » de la boucle deviennent
neuf appels répartis dans les lieux examinés, dont un rappel après le délai. Odile, auberges 42 et
2024, conserve ses **16 appels** : deux tournées de huit lieux à au moins 60 minutes d'écart pour
chercher Joss qui se tait. L'analyseur sait expliquer une tournée quand chaque appel a un souvenir
sans réponse correspondant et qu'aucun couple personne/lieu n'est rappelé avant `APPEL_OUBLI`.

Le quatrième constat après correction est Lucien, mine 42, **14 appels** : recherche de Gaspard,
réception de sa lampe à 451, nouvelle recherche pour les bûches puis le briquet à 452, tournée pour
Odon, appel à Mathe, puis Gaspard plus tard. Les rencontres et les demandes distinctes sont
enregistrées. L'analyseur conserve prudemment `a_expliquer` pour ce cas et Anselme ; le rapport
les explique sans filtrer un personnage ou un scénario. Les trois alternances de buts restantes
sont également conservées comme repères de lecture, sans blacklist.

La dette de Lucien à Odile (auberge 3) vient d'une tâche acceptée à 630, devenue due à 669,
après une rumeur d'absence de la burette à 663 puis l'allumage de la lampe d'Odile à 668, et refusée
à 671. Ce n'est ni une dette créée à l'instant du marché
ni une disparition de la promesse : l'abandon est annoncé et le défaut de paiement circule.

## Vérifications

`tests/test_signalements.py` : **14 tests**, quatre scènes historiques comprimées ; état complet
identique pour un laps entier ou découpé, rechargements réels, rendu de l'ouïe et récit, mémoire
bornée dépassée, migration, et conservation des alertes quand un diagnostic manque.
La contre-épreuve sur le moteur de référence fait échouer les deux régressions d'appel à l'aide,
le rappel sans nouvelle croyance avant le délai du cas Anselme et la conservation du résultat
du cas de recherche au Relais.
Ce dernier contrôle porte sur la persistance du résultat, pas sur une seconde rafale historique.

Adaptations de tests : la réserve d'Odile reste le fournisseur d'Anselme après 300 min dans
`test_ressources`, au lieu du lot de Mireille ; les assertions de charges finies et de trois foyers
allumés après rechargement restent présentes. Six échecs de tests MiMo simulés se reproduisaient
aussi sur `main` 43fa7ac avec la dépendance facultative `jsonschema` installée : le faux auditeur
narratif omettait `presentation`, et deux captures anciennes comparaient les symboles de carte
avant leur actualisation par `spatial.installer`. Les réponses simulées portent le champ requis ;
les scènes sont initialisées comme à l'ouverture du jeu avant de comparer leur état entier après
rejet. Aucun adaptateur ou appel réel au modèle n'est modifié. Les quatre fichiers ajustés passent
ensemble : **32 tests, un saut**.

Suite complète finale : **1 438 tests, OK, quatre sautés, aucun échec ni erreur**, 134 fichiers,
trois processus en priorité réduite, **241,3 s**. Trace : `artifacts/signalements-suite-finale.json`.

Contrôles : **huit nuits sans écart**, quatre scénarios, graine 42 ; `VERIFIER` et
`spatial.VERIFICATION=1` sur 2 h, puis `VERIFIER` et 0,2 sur 8 h. Aucun plantage, usurpation ni
recherche jouée arrêtée à sa borne dans ces huit nuits. Les observations supplémentaires du rejeu
n'entrent ni dans les décisions ni dans les sauvegardes.

### Banc 8 h, référence puis branche

`tools/comparer_bancs.py`, quatre scénarios × **1985, 7, 42, 2024**, départ tiré, trois processus.
Chaque valeur est une moyenne par nuit ; minutes = min·PNJ. Référence git 43fa7ac, puis fichiers
du worktree. **Zéro plantage, violation ou usurpation** dans les 32 nuits comparées.

| Mesure, avant → après | Relais | Mine | Auberge | Crue |
|---|---:|---:|---:|---:|
| Minutes urgentes sans recours | 102,5 → 101,25 | 13,75 → 13,75 | 131,25 → 125 | 112,5 → 112,5 |
| Minutes urgentes en attente | 31,25 → 31,25 | 283,75 → 283,75 | 8,75 → 8,75 | 62,5 → 66,25 |
| Échanges | 16,25 → 13,5 | 43,25 → 45,25 | 24 → 27 | 19,75 → 19,5 |
| Vols vus | 1,25 → 1,25 | 0,5 → 0,5 | 1,25 → 1,5 | 1,5 → 1,5 |
| Appels à l'aide | 2,5 → 0,25 | 0,75 → 0,5 | 0,5 → 0,5 | 0,5 → 0,25 |
| Minutes dans le noir | 38,75 → 23,75 | 258,75 → 255 | 140 → 141,25 | 66,25 → 66,25 |
| CPU, secondes | 6,61 → 5,66 | 16,95 → 27,32 | 17,27 → 18,75 | 10,62 → 10,38 |
| Temps écoulé, secondes | 6,84 → 5,74 | 17,16 → 27,67 | 17,47 → 19,02 | 10,76 → 10,49 |

Le surcoût de la mine est réel sur cette passe : graines 7 **20,94 → 32,48 s CPU**, 42
**16,92 → 24,38**, 2024 **14,34 → 36,55**, contre **15,59 → 15,89** pour 1985. Les recherches
neuves passent respectivement de 714 → 774, 566 → 634, 710 → 749 et 570 → 569 ; les gestes et
trajectoires divergent. Ce n'est pas une preuve d'un coût constant du nouveau suivi, ni une
optimisation de la mine. Aucun profilage causal du surcoût n'a été ajouté à ce lot.

Pour situer les effets plus tardifs, audit **12 h × huit graines**, mêmes mesures :

| Mesure, avant → après | Relais | Mine | Auberge | Crue |
|---|---:|---:|---:|---:|
| Minutes urgentes sans recours | 179,38 → 160 | 23,75 → 38,13 | 181,25 → 166,25 | 138,75 → 138,75 |
| Minutes urgentes en attente | 190,63 → 188,13 | 1 401,88 → 1 389,38 | 478,75 → 464,38 | 418,13 → 418,75 |
| Échanges | 23,63 → 22,13 | 64,13 → 59,25 | 82,25 → 81,25 | 24,38 → 23,38 |
| Vols vus | 1,63 → 1,75 | 0,25 → 0,13 | 1,75 → 1,25 | 1,63 → 1,63 |
| Appels à l'aide | 1,5 → 0,38 | 4,5 → 1,75 | 1,38 → 1,25 | 1,38 → 0,75 |
| Minutes dans le noir | 181,25 → 173,13 | 1 320,63 → 1 373,13 | 836,88 → 956,25 | 93,75 → 88,13 |
| Temps écoulé avec rejeu, secondes | 13,69 → 13,63 | 87,55 → 85,1 | 119,04 → 120,91 | 20,18 → 20,27 |

La hausse du « sans recours » et du noir à la mine sur 12 h, et du noir à l'auberge, reste visible.
Les corrections portent sur le renouvellement injustifié de recours, pas sur une amélioration
uniforme des nuits. Les quatre graines de 8 h ne comprennent pas la boucle rare de l'auberge 3.

## Reproduction et limites

Python : `C:/Users/msics/donjon/.venv/Scripts/python.exe`. Depuis chaque worktree, successivement :

```text
python tools/audit_nuits.py jouer --scenarios relais mine auberge crue --graines 1985 7 42 2024 3 11 99 500 --heures 12 --processus 3 --rejeu --dossier artifacts/signalements-apres
python tools/audit_nuits.py analyser --dossier artifacts/signalements-apres --sortie artifacts/constats-apres.json
python tools/audit_nuits.py jouer --scenarios relais mine auberge crue --graines 42 --heures 2 --processus 3 --verifier --verification 1 --dossier artifacts/signalements-controle-2h
python tools/audit_nuits.py jouer --scenarios relais mine auberge crue --graines 42 --heures 8 --processus 3 --verifier --verification 0.2 --dossier artifacts/signalements-controle-8h
python tools/comparer_bancs.py --reference 43fa7ac --scenarios relais mine auberge crue --graines 1985 7 42 2024 --heures 8 --processus 3 --sortie artifacts/signalements-banc-8h.json
python tools/tests.py --processus 3 --sortie artifacts/signalements-suite-finale.json
```

Les données détaillées sont locales dans `artifacts/` (non versionné), ainsi que dans le worktree
`tmp-worktrees/signalements-reference/artifacts/signalements-avant` et `signalements-observe`.
Les seuils de l'analyseur restent des indices de lecture, pas une preuve universelle d'absence de
boucle. Une recherche bornée qui ne trouve pas de plan ne prouve pas qu'aucun plan n'existe ; le
suivi `attente` décrit le jugement actuel du moteur. Les ressources ne deviennent pas renouvelables,
la crainte du noir ne s'émousse pas et les PNJ n'identifient pas un corps au seul contact dans le noir.
La migration ne peut reconstituer un ancien recours déjà oublié avant ce lot. Les temps sont ceux
d'une machine partagée avec les autres agents ; aucun gain uniforme n'est promis.
