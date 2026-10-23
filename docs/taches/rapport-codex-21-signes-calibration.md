# Signes : coût, relectures et calibration

Branche `codex-signes-calibration`, non fusionnée. Base du moteur `8855312`,
brief `0ebb31a`. Worktree `tmp-worktrees/codex-signes-calibration` ; le dépôt
principal reste sur `main`. Aucun changement de `planification.py` ou `deliberation.py`.

## 1. Coût à comportement constant

`relations._lecture_pure` conserve le calcul de référence ; `_lecture` mémorise
la lecture par paire orientée, sous la minute, la relation enregistrée et les
valeurs du profil qui règlent l'estompement. `signature_signes` ne retient que
les bandes et seuils que les émissions consomment. `signes.de` dépend de cette
signature, de l'attitude, du guet, du seuil d'attente, du plan, de la fierté,
de la conscience et du seuil de colère ; la minute seule n'invalide plus une
émission inchangée. Pour le joueur : observation et intervalle actif.

`_percus_gardes` garde une entrée par observateur : personnes effectivement
perçues, émissions, lumière et distance, position et regard de l'émetteur,
présence perceptible ou crue de la cible et sa position requise par le geste.
Un esprit éloigné n'invalide plus tous les observateurs. Les mémoires sont
dérivées, hors `data`, et se reconstruisent après rechargement.
`spatial.VERIFICATION` recompare relations, émissions et perceptions au calcul
de référence. Les deux outils de nuits acceptent aussi `rixe`.

Preuves : 20 nuits de 2 h, puis 20 nuits de 8 h (quatre scénarios et `rixe`,
graines 1985, 7, 42, 2024), chronique, mesures et état final complet identiques
à `8855312`. Version d'optimisation figée : `bbf17cb`. L'ancienne clé globale
`spatial.etat_signes` n'est plus consommée par le cache des signes ; les clés
sont propres à chaque observateur. `relations.axes` isole aussi les bandes
renvoyées pour qu'un consommateur ne puisse modifier la lecture mémorisée.

Profil CPU de la mine 7, 2 h, version figée (instrumentation `cProfile`, pas
une mesure de vitesse absolue) : 39,98 s au total ; `percevoir_tous` des signes
4,17 s cumulées (10,4 %), dont `de` 1,31 s et `_percus_gardes` 1,95 s ;
préparation lumière/distance 0,89 s. Les lectures `_lecture` de toutes les
relations représentent 1,91 s et les signatures sociales des signes 0,63 s.
Ces temps se recouvrent, ils ne s'additionnent pas. La construction des clés
et l'accès sensoriel restent payés même quand la lecture pure est reprise.
Les mesures non instrumentées simultanées seront consignées ci-dessous.

## 2. Relectures

`signes._presence` enregistre les épisodes de perception par observateur dans
`data.suivi_signes` : signes présents, numéro d'épisode, conclusion et
lecture retenue par signe. Une réception partielle de tons ne fait pas disparaître
les autres signes. Une perception complète vide clôt les épisodes, y compris
quand personne n'émet plus rien. Les simples projections restent pures.

`lire` rafraîchit une lecture active équivalente (valeur et cible), sans souvenir
`intention_lue` ni ligne de chronique ; un échec n'écrit pas dans la lecture.
Un épisode nouveau ou une lecture périmée compte de nouveau. La date `apprise`
et l'épisode distinguent une nouvelle impression d'un rafraîchissement ;
`bilan_signes` ne répète que les faits physiques demandés, pas une même impression.
La carte et le contexte conservent l'impression actuelle avec son incertitude.

Tests ciblés : 32 tests des signes et de calibration, dont la capture réelle du
Relais 7 à 441 minutes et le guet de l'auberge, retour d'un signe, péremption, échec préservant la lecture,
deux observations du joueur et 20 minutes d'un bloc ou découpées avec reprise.
Le délai de dix minutes entre essais est conservé, même si le signe disparaît
puis revient ; son retour compte comme nouveau au prochain essai autorisé.
Une ancienne sauvegarde sans suivi reprend ses impressions actives sans les
réannoncer. Les projections restent pures ; seules les réceptions par le moteur
et les observations explicites mettent ce suivi à jour. La chronique conserve
les nouvelles conclusions avec leurs preuves, le corpus instrumenté conserve
aussi les essais qui ne produisent pas de nouvelle conclusion.
Mesure isolée des relectures, avant calibration : mêmes 8 h et graines, `8855312`
contre corpus au réglage historique 4/5/5. « Intentions » compte les créations
de souvenirs `intention_lue` (`guets_reperes`), pas ce qui reste en mémoire finale.
L'audit ci-dessous est sa partie textuelle `repetition` sur la chronique ; l'audit
avec tous les relevés est effectué séparément au banc rapide final.

| Mine, graine | Alertes `repetition` avant → après | Intentions avant → après | Confidences avant → après | Dont guets avant → après |
|---|---:|---:|---:|---:|
| 1985 | 1 → 0 | 15 → 13 | 30 → 35 | 24 → 24 |
| 7 | 3 → 0 | 11 → 8 | 14 → 12 | 13 → 11 |
| 42 | 1 → 0 | 9 → 8 | 10 → 10 | 9 → 9 |
| 2024 | 4 → 0 | 5 → 5 | 11 → 11 | 10 → 10 |
| Moyenne | 2,25 → 0 | 10 → 8,5 | 16,25 → 17 | 14 → 13,5 |

- **1985** : première différence hors lecture à 65 min : Rémy ne redit plus à
  Mathe qu'Odon guette la porte du bureau. Josse poursuit ses gestes vers la
  réserve à 75 min. Le réseau des paroles change ensuite ; les confidences de
  guet restent exactement 24. Les cinq confidences supplémentaires portent sur
  la part de pain mangée par Odon : quatre → neuf (Rémy/Josse 109 min,
  Mathe/Josse 111, Josse/Bram 191, puis Josse, Mathe et Lucien en fin de nuit).
  « Peu fiable » et la parole tenue restent une confidence chacun. La hausse
  totale n'est donc pas une répétition supplémentaire de guet.
- **7** : le guet relu de Rémy à 104 min, puis les relectures de Lucien et Rémy à
  190 min ne recréent pas de souvenir. Première différence hors lecture à
  190 min : Rémy ne redit plus le guet à Mathe ; deux confidences de guet en moins.
- **42** : seule une relecture de Mathe à 38 min cesse d'être nouvelle. Toute la
  chronique hors lecture est identique, confidences comprises.
- **2024** : aucune intention supprimée ni confidence changée, toute la chronique
  hors lecture est identique. Les alertes disparues portaient sur « aucune
  impression » et « dépendance » relues, pas sur des gestes.

Les neuf anciennes alertes portent toutes sur les lectures de Lucien : des
absences d'impression répétées 18 à 28 fois, et deux séries de « dépendance ».
Les créations réelles et les retours d'épisodes restent possibles ; cette règle
ne promet pas une baisse de toutes les paroles sociales d'une nuit.

## 3. Calibration

La grille est commune à tous : pénombre 4/3/2, dissimulation 5/4/3,
bande sans interprétation de 5 à 11 (63 combinaisons). Le dé, les bonus de familiarité et d'observation,
la distance, le seuil de réussite et les sens des méprises ne changent pas.
L'étude conditionnelle rejugera les jets d'un corpus enregistré ; une nuit libre
avec le réglage retenu vérifiera ensuite les rétroactions sur les décisions.
Ces deux mesures sont distinguées dans les résultats.

Corpus initial terminé : 48 nuits libres de 8 h, quatre graines, quatre scénarios
par défaut et Gorm/Hugues à PSY 8/11/14/16. Tous les essais, même les
rafraîchissements sans ligne de chronique, sont enregistrés par l'instrumentation
de `interpreter` et `_jet`. Aucun état de partie n'est retouché pour les recueillir.

Choix à confirmer en nuits libres : **pénombre −4, dissimulation +3,
bande rien 8**. Aucune des 63 combinaisons ne passe les trois bornes ensemble.
Le choix minimise le plus grand dépassement absolu d'une borne de probabilité,
puis leur somme ; aucune pondération par personnage ou scénario. Dans le corpus
rejugé : justesse Gorm 14/16 = 0,797/0,863, Hugues 14/16 = 0,750/0,815 ;
méprises par défaut 25,35 %, abstention 42,34 %. La borne basse manque pour
Gorm 8 = 0,630 (Hugues 8 = 0,583), pour un plafond de 0,6. Le critère global
n'est donc pas déclaré atteint. Le jet contrôlé de la capture réelle passe de
18 à 16 pour garder la même marge de frontière avec la DD abaissée de deux points.

## 4. Observer sans voir

La résolution locale des actions de `commandes.PERCEPTIONS` nomme aussi une
personne connue hors de vue, par le résolveur commun `_nomme`. Elle ne juge
plus sa visibilité avant le moteur. `Moteur._preparer` appelle `refus.perception` :
une seule cause (présence, lumière ou vue), « cette personne », et un `attendu`
contenant l'identifiant reçu et les valeurs acceptables. Le circuit en ligne
existant valide une proposition locale avant tout appel au MJ ; aucun nouveau
mot-clé, mode ni exception dans `jeu.py` n'a été nécessaire.

Six parcours console passent (trois causes × en ligne/hors ligne), sur le monde
réel `signes-noir` et une personne dans une autre salle, plus une occultation par
la géométrie. Une simple orientation de dos peut se corriger par la rotation
normale du moteur et n'est pas assimilée à une ligne de vue coupée. Le test
contrôle le refus, l'absence d'appel, le monde entier après rechargement et la
projection du joueur. Deux passes Luna de référence terminées sur copies :
`signes-ecart`, `signes-noir`, `signes-guet`. Les refus locaux de `signes-noir`
partent au MJ sur la référence.

## 5. Vols vus, vérifications et limites

Les mesures et constats finaux seront ajoutés après exécution.

### Accord minimal avec les trajets réels

La suite complète a révélé une vraie régression de trajet dans la crue 500 : à
160 min, Brune vise la galerie haute pour le poêle. La marche prend un détour
par la conduite puis la crypte, dont elle prévoit pourtant la noyade ; elle
s'acharne ensuite à crocheter la porte du beffroi jusqu'à 182 min, puis reste
piégée (109 cm à 360 min). La destination abstraite était sûre, pas son détour.

Correctif isolé dans `pnj._marcher` : le filtre des salles de la route réelle
réutilise `Vue.descente`, déjà autorité du plan, pour toutes les salles
intermédiaires. Il n'en réécrit pas la règle et ne lit pas une prévision réelle
à la place des croyances du PNJ. Aucune modification de `planification.py` ni de
`deliberation.py`. Ce petit accord devra être conservé par le lot Q qui refond
les trajets : ne pas remettre une route réelle qui ne respecte que sa destination.

Le test historique `test_crue_500_personne_ne_se_chauffe_dans_l_eau_ni_ne_reste_piege`
passe sans modification de ses assertions. La capture réelle avant le détour
(`tests/data/scenes/crue500-avant-descente.json.gz`, 160 min, `e1c018b`) et une
seconde lectrice, Ilse avec la même information d'eau et une porte crue praticable,
vérifient un vrai trajet géométrique tentant, son refus général, le monde et le
rendu après rechargement, puis la sécurité après vingt minutes de jeu.
