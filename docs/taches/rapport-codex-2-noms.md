# Rapport Codex 2 — noms entendus

Branche `codex-noms`, non fusionnée. Référence reproductible : `main` `f1eee53`, extraite par
`git archive` dans `artifacts/noms-baseline` ; aucun changement de branche principale, aucune
sauvegarde utilisateur modifiée ; les parties Luna utilisent des copies et bancs. Luna reste
`gpt-6-luna` ; aucun autre modèle.

## Règles et fonctions

- `noms` : noms appris séparés de l'apparence et de la voix, projection publique et décodage
  de références. Désignations visuelles et éléments associés opaques ; liens initiaux en données.
- `voix`, `paroles`, `dialogues`, `commandes`, `Moteur.preparer` : une même désignation peut
  être saisie, proposée et résolue ; perception, portée et propriété restent les règles du moteur.
- `Monde.contexte`, `scene`, `carte`, `rendu` : noms publics cohérents, souvenirs compris ;
  les portraits cités ne deviennent pas des mots entendus.
- `narration.voix_inconnues`, `consigner`, `faits_locaux` : refus déterministe du nom inconnu
  dans le récit ; noms du locuteur dans ses répliques seulement, apprentissage avant affichage.

Voir un corps, reconnaître une voix, connaître un nom et entendre une appellation revendiquée
sont des connaissances distinctes. Une croyance de provenance `dit:*` ne prouve pas que le nom
ait été prononcé. Une voix qui se dit Aubin n'identifie jamais le vrai corps d'Aubin vu ailleurs.
Une voix reconnue jamais vue reste sans portrait. Les producteurs PNJ parlent selon la
connaissance du locuteur, Corvus compris. Les journaux d'action suivent la projection publique.

Le paquet privé d'un locuteur reçoit `nom_du_locuteur`, distinct des noms de tiers prononçables.
Cela permet une présentation sans donner d'identifiant réel ni autoriser le nom dans le récit.
Ce paquet entier est réservé à la narration après parole/action validée : nom propre et listes
de noms de tiers sont absents de l'interprétation mécanique. Les références publiques ne peuvent
ainsi être choisies en croisant des connaissances nominales privées.
L'audit de réplique et le fait persistant `parole` portent `presentation` : le nom littéral dont
la voix se présente, vide sinon. Le moteur exige ce nom dans la citation et consigne ses
auditeurs avant affichage. Une réponse « Gorm. » fonctionne sans reconnaître la question.
Un destinataire nommé d'un appel typé peut être relié ; une mention de tiers reste non attribuée.

L'union typée du contenu de parole refuse les champs inutilisés par son type, avec un
`RefusDeForme` et un `attendu` précis. `propos(sujet=nom)`, autrefois accepté sans réaliser une
question de nom, est ainsi refusé comme toute charge inutile. Aucun traitement de formulation.

Toutes les réponses MJ vérifient les champs de référence avant décodage : les vrais ids
privés devinés sont refusés, les références publiques effectivement fournies sont acceptées.
La prose du joueur et le nom revendiqué typé restent des mots contrôlés par leur contrat.
La contre-revue d'action et l'ancienne voie `proposer` suivent la même frontière. `Plan.resume`
projette aussi opposition, risque et étapes. Le helper visuel exige une vue actuelle ou
antérieure ; aucun texte ne fabrique le portrait d'un corps jamais vu, même à voix reconnue.

## Cas vérifiés

`tests/test_noms.py` : 33 cas après sauvegarde/rechargement, état et terminal/carte/données de
scène web ; trois tests de l'union typée dans `tests/test_contenus_parole.py`.
Le Relais : Gorm vu, sa voix reconnue, aucun nom appris ; question de nom au moteur ; Aubin
l'appelle en le nommant. Même nature : Joss à l'auberge voit Corvus sans son nom puis l'apprend
quand il se présente. Don du briquet par « l'homme trapu ». Voie MJ auditée avec fournisseur
simulé : mention ambiguë de tiers sans lien de corps, identité privée du locuteur, deux
présentations explicites et nominales, contamination privée refusée dans le récit, nom absent
de la citation refusé. Portrait cité et élément `bras_gorm` sans identité divulguée ; référence
opaque devinée hors perception refusée sans mutation ; toute voix jamais vue sans portrait ;
imposture sans oracle du vrai corps ; parole descriptive sans apprentissage ; cache de visibilité
hypothétique sans mutation des souvenirs.

Le garde des citations exige une provenance à portée précise : parole auditée dans son
passage exact, citation entière et unique ; une copie dans un autre segment ne bénéficie
pas de cette autorisation. Les paroles historiques ne sont exemptées que restituées seules
et entières, sans étiquette narrative de corps ni description persistante. Les tests couvrent
Gorm et Ilse cités dans le récit privé malgré un audit sémantique favorable, la duplication
d'une citation autorisée, le fragment de parole, les ajouts persistants et les mots exacts
de Corvus déjà enregistrés. Les voies d'enregistrement et de dernier recours refont le garde.
184 tests ciblés passent en 66,660 s sur ce gel.

Les tests historiques de conversations nommées déclarent maintenant leurs présentations
antérieures (`tests.support.presentes`), au lieu de supposer qu'un regard donne un nom.
Le test de console `test_proto` avait une narration de résultat non simulée après « tenter »,
avec une clé factice : son mock a été complété pour que la suite reste hors réseau.

Le lanceur final interdit les connexions extérieures, possède sa garde `__main__` et conserve
les doublons de discovery. 1 277 tests découverts : 1 276 ordinaires et un recalcul long du
planificateur, manifestes conservés. Le test long final passe en 14,183 s ; les 1 276 ordinaires
passent en 880,346 s, avec quatorze dépendances facultatives ignorées. Au total : 1 263 tests
réussis et quatorze ignorés, aucun échec ni erreur. Les manifestes prouvent zéro omission,
zéro chevauchement et trois doublons de discovery conservés. La partition précédente avant le garde des citations était verte : 1 273 tests
ordinaires en 1 013,482 s, un long en 23,268 s et quatorze dépendances facultatives ignorées.
Une première partition de ce gel (1 276 tests, 769,707 s) a signalé trois `StopIteration`
à la lecture console, sans échec d'assertion, quatorze tests facultatifs ignorés. Les mêmes trois
tests passent isolément et dans 150 répétitions bornées (27,359 s), ce qui n'établit pas la
cause. La passe exhaustive suivante capture la sortie et la dernière commande au point exact
d'épuisement de l'entrée simulée, sans changer le jeu ni ajouter d'entrée. Elle est verte
(1 276 tests, 880,346 s, quatorze ignorés), sans capture d'épuisement. Les trois erreurs
antérieures restent inexpliquées : la validation réussie sur source fonctionnelle inchangée
ne constitue pas une résolution de leur cause. Seule la docstring de `Monde.identifier` a
été actualisée entre les passes ; les erreurs précédentes ne sont pas présentées comme une
suite verte. Traces : `artifacts/noms-suite-court-citations-{finales,capture}.log`.
Une première exécution récursive
du lanceur sans cette garde est intégralement exclue des chiffres ; la partition précédente
(1 258 tests ordinaires, quatre échecs et deux erreurs) a guidé les corrections de fixtures
et n'est pas présentée comme la validation finale.
Une seconde partition intermédiaire de 1 268 tests a duré 858,133 s : un échec de fixture
confondant appellation et corps, deux erreurs de fixtures nommant Mira sans présentation.
Ces fixtures sont corrigées ; 120 tests ciblés passent en 70,702 s, puis 35 tests de noms et
contre-revue en 22,703 s sur un gel intermédiaire. Les tests MiMo facultatifs restent ignorés quand
leurs dépendances sont absentes, sans lancer un autre modèle.
La partition suivante (1 272 tests, 1 118,295 s), chargée avant la séparation de phases,
avait une fixture de contre-revue attendant un nom non présenté et un faux fournisseur donnant
un id privé ; elles ont été corrigées. Un `StopIteration` du test de console hors ligne a été
observé dans cette passe puis n'a pas été reproduit isolément (0,068 s) ; aucune entrée
supplémentaire n'a été ajoutée pour le masquer. Cette passe reste intermédiaire.

### Parties réelles

Les deux replays finaux après le garde des citations donnent « Gorm. » et « Ilse »,
appris avant affichage : Gorm, trois appels/12,0 s sans refus ; Ilse, quatre appels/18,3 s
avec un refus de forme de parole corrigé. Zéro erreur, repli ou mention sans fondement. Après
chaque saisie, le fichier sauvegardé est relu : noms absents des trois vues avant audition,
`noms_connus=[marchand]` ou `[ilse]` et noms présents ensuite. Aubin voisin reste inconnu ;
le don par désignation déplace le briquet du joueur vers Gorm. Quatre/trois saisies, un tour
MJ chacune ; les commandes locales passent par le moteur. La question de Gorm est typée
`qui`, dont le moteur établit la réponse nominale ; celle d'Ilse reste `propos` et sa présentation
nominale est établie par la parole MJ auditée. Le champ superflu du premier `propos` d'Ilse est
refusé, puis corrigé sans règle liée à la question.
Preuves : `artifacts/noms-courtes/etats-{presentation-citations,femme-citations}.json` et fils complets.

La portée du paquet privé est aussi vérifiée dans `Fournisseur.appeler(Demande)` sur les deux
cas : aucun nom inconnu dans les faits d'interprétation, propre nom et noms de tiers disponibles
seulement en narration après validation, puis consigne, sauvegarde, rechargement et trois rendus.

Les replays d'aperçu Gorm/Aubin ont quatre saisies et un tour MJ chacun, deux appels/8,8 s,
aucun refus/repli/erreur/mention. Opposition et risque restent anonymes ; après recharge,
`noms_connus` est vide et l'annulation n'exécute aucune poussée. Preuves :
`etats-apercu-{gorm,aubin}.json`. Les contre-revues ne reçoivent ni nom ni id privé.
Les tests couvrent aussi les textes sur des corps jamais vus, à voix absente, entendue ou reconnue.

### Incidents et replays intermédiaires

Les deux premières parties courtes ont trois/un tours MJ en erreur réseau, sans apprentissage.
Un échange sain a révélé la charge ignorée `propos(sujet=nom)`. Après sa correction, les
locuteurs donnaient encore un nom tiers car leur propre identité était retirée de la projection.
La correction privée a fait produire les vrais noms, mais les réponses nominales ne créaient
aucun lien : le contrat typé de présentation a corrigé cette cause commune.
Les premiers replays avec ce contrat ont trois appels chacun, 16,9/13,2 s, aucun refus/repli/
erreur/mention ; leurs preuves `etats-{presentation-typee,femme-typee}.json` sont conservées,
mais ils précèdent la séparation des phases et ne qualifient pas la version finale.
Les replays suivants après séparation des phases avaient quatre appels/15,0 s/un refus pour
Gorm et trois/11,7 s/zéro refus pour Ilse, sans erreur ni repli. Leurs preuves
`etats-{presentation-phases,femme-phases}.json` restent intermédiaires avant le garde des citations.

La première paire complète branche a ensuite révélé le nom réel dans l'opposition et le risque
de l'aperçu. `Plan.resume`, la validation inverse des références et la contre-revue publique
ont été corrigés ensemble. La lecture du choix d'une cible a ensuite motivé la séparation
du paquet nominal privé entre phases, vérifiée par les replays ci-dessus. La fermeture de portée des citations suit cette correction. Ces
changements concernent seulement le MJ et l'ingestion de faits narratifs ; les campagnes moteur finales sans MJ restent applicables
au moteur inchangé. Aucun échec antérieur n'est compté comme un apprentissage réussi.

## Mesures moteur

Main puis branche, BelowNormal, quatre processus au plus : Relais 8 h, graines
1985, 7, 42, 2024, 3, 11, 99, 500 ; auberge 8 h, graines 1985, 7, 42, 2024.
La première mesure branche (Relais 11,8 s/nuit, auberge 32,6) précède les dernières corrections
et reste intermédiaire. Main : Relais 10,9 s/nuit, auberge 29,5.
La passe finale est complète : les 12 nuits contrôlent `Monde.verifier()` à chaque pas sans
assertion ni échec ; zéro usurpation mesurée sur chaque graine. Le champ `ecarts` du banc compte
les passages consentis, pas les violations.

| Moyenne par nuit | Relais main → branche (8 graines) | Auberge main → branche (4 graines) |
|---|---:|---:|
| Secondes de calcul | 10,90 → 13,17 | 29,49 → 38,56 |
| Gestes | 157,625 → 159,25 | 311,75 → 310,75 |
| Échanges | 15,375 → 15,5 | 37 → 37 |
| Achats | 2,125 → 2,125 | 2,75 → 2,75 |
| Pièces payées pour achats | 3,375 → 3,375 | 2,5 → 2,5 |
| Tâches accomplies | 0,125 → 0,125 | 1 → 1 |
| Noms retenus pendant la nuit | 0 → 0 | 0 → 0,75 |
| Voix appelées enregistrées | 0 → 0 | 0,75 → 0,5 |

La nuit physique n'est donc plus revendiquée identique. Ces durées observées ne constituent
pas une mesure isolant le coût causal : les autres suites de la machine et les trajectoires
sociales peuvent changer. Détail brut : `artifacts/noms-{main,branche-finale}-{relais,auberge}.json`.

Au départ fixe de l'auberge, la connaissance modifie une nuit sociale : vers la minute 405,
Anselme paie quatre pièces à Odile pour entretenir le poêle, qui brûle une charge supplémentaire.
Les pièces passent d'une bourse à l'autre, aucun bois n'est créé. Poêle et fourneau sont éteints
à huit heures, l'âtre tient encore. Le test de rareté vérifie cette échéance plutôt que d'imposer
l'extinction à sept heures. Diagnostic et états aux minutes 150/300/360/420/480 conservés dans
`artifacts/auberge-*`. Les révisions après appels diffèrent ; le détail causal de chaque décision
de prix n'est pas revendiqué comme démontré.

## Mesures Luna

Les mesures et traces complètes sont conservées dans `artifacts/`. Les deux premiers
lancements non élevés n'ont produit aucune partie exploitable : erreurs Windows sur les
dossiers temporaires privés. Tous les lancements mesurés utilisent le même environnement
élevé, `TEMP`/`TMP` locaux et `SEUIL_AUTH` explicitement partagé. Main est joué avant branche,
deux exécutions simultanées au plus. Les incidents du transport sont distingués des refus
de jeu ; aucune conclusion causale de performance ne sera tirée d'une sélection de seuls
tours réussis lorsque les pannes diffèrent.

La main saine utilise `artifacts/noms-baseline/tools/banc_multi.py --variante main=.` puis
le `banc_parties.py` de cette même archive, tous deux identiques aux blobs de `f1eee53`.
La branche utilise ses propres outils avec `--variante branche=.`. Les quatre scripts sont
identiques octet pour octet entre les deux arbres ; chacun contient 23/42/15/10 saisies,
soit 90 par passe et 38 tours MJ. Le chemin `SEUIL_CODE=main` a aussi été vérifié hors réseau
depuis l'outil de branche : quatre parties, 90 saisies, zéro appel, aucun arrêt ni erreur de
rechargement. L'import de `donjon.noms` est conditionné à une préparation `noms_connus` non
vide ; aucun des quatre scripts ne l'active. Ce seul correctif de compatibilité d'outillage,
postérieur au gel moteur, ne change donc pas les requêtes des campagnes mesurées.

La référence saine (`20261022-205142-50436`) est complète : 76 tours MJ, aucun tour en erreur ou
repli, 105/115 appels par passe. La branche finale après garde des citations
(`20261022-224249-36188`) est complète : huit parties, 180 saisies, 76 tours MJ, 235 appels
(r1 : 114 ; r2 : 121), aucun tour en erreur technique ni erreur de rechargement.
Deux tours se replient après contrôle narratif : un texte du moteur et des segments admis,
sans incident de transport. Les 235 appels tracés utilisent `gpt-6-luna` via ChatGPT.
Les secondes incluent tous les tours MJ, sans sélectionner les succès.

| Indicateur par passe (moyenne et étendue) | Main saine | Branche finale |
|---|---:|---:|
| Appels/tour MJ | 2,89 (2,76–3,03) | 3,09 (3,00–3,18) |
| Secondes/tour MJ | 10,8 (10,5–11,2) | 11,9 (11,5–12,4) |
| Tours en repli | 0 | 1 |
| Tours avec refus | 6 | 7 |
| Obstacles narratifs | 2,5 (1–4) | 11 (10–12) |
| Relances narratives | 2 (1–3) | 8 (7–9) |
| Refus moteur/contre-revue | 8 (7–9) | 12,5 (12–13) |

La branche corrige davantage de propositions et relance davantage ; elle n'est pas annoncée
plus rapide sur ces deux échantillons. Les scripts conservent volontairement leurs anciens
noms dans les saisies : certains noms sont désormais inconnus, ce qui change les refus.
Les neuf tours portant un signal lexical ont été relus : mots exacts du joueur (« gardien »),
refus explicites de reconnaître un nom, absence d'un outil ou exigence générique d'échelle ;
aucune de ces mentions n'identifie factuellement un corps inconnu. Dans les deux replis,
le contrôle refuse notamment des phrases qui citent « Ilse » pour expliquer l'absence de
lien nominal ; ce garde conservateur peut donc demander une reformulation même d'un démenti.
Les deux aperçus de poussée restent opaques.
La part de réflexion observée est nulle dans les deux variantes ; ces bancs ChatGPT rapportent
un coût API nul, sans mesurer le coût de l'abonnement.

### Incidents et mesures intermédiaires

Les variables de proxy sont absentes de l'environnement des parties réelles. Une sonde bornée
a constaté un `TimeoutError: timed out` du handshake WebSocket, sans constituer une partie.
Une première paire main dégradée (`20261022-190204-38020`) reste conservée : 38 tours MJ/passe,
2,368/2,342 appels et 66,108/69,893 s/tour ; 12/14 tours en repli et en erreur technique,
cinq tours avec refus par passe, huit/dix refus et deux relances narratives. Soit 26/76 tours
en erreur technique, distincts des refus du jeu ; cette paire ne sert pas de référence saine.

La paire complète branche `20261022-212706-37980` précède la correction de l'aperçu et reste
intermédiaire : 76 tours MJ, 117/120 appels ; 12,57/13,68 s/tour ; un tour en repli par passe,
dont un avec erreur technique dans la première et un repli de contrôle narratif dans la
seconde. Sept/huit tours avec refus, onze/treize refus, dix/dix-huit obstacles, huit/dix
relances. Une trace WebSocket porte `1011 keepalive ping timeout; no close frame received`.
Les mentions de refus explicites ou les mots cités du joueur ne sont pas des identifications ;
en revanche l'aperçu révélait bien Aubin, ce qui a motivé la correction et les nouveaux bancs.

La paire `20261022-215123-36972`, avant séparation du paquet privé par phase, est complète
mais intermédiaire : 76 tours MJ, 109/118 appels, 10,979/12,125 s/tour, zéro tour en erreur,
un/zéro repli, sept/neuf tours avec refus, onze/quatorze refus, sept/onze obstacles et
quatre/huit relances. La lecture du choix d'une cible y a motivé la restriction de la
connaissance nominale privée aux seules narrations après validation.

La paire `20261022-220630-51564`, après séparation des phases mais avant le garde des
citations, reste intermédiaire : 76 tours MJ, 121/104 appels, 11,390/9,884 s/tour,
zéro erreur ni repli ; huit tours avec refus par passe, onze/douze refus, dix/trois obstacles
et huit/deux relances. Elle ne remplace pas la série finale après fermeture de provenance.

Trois séries branche interrompues avant gel ne remplacent pas les passes finales :

| Série | Couverture préservée | Qualification |
|---|---|---|
| `20261022-194914-1640` | 10/23 tours finis, 3/4 tours MJ, 3/4 appels ; tous ces tours MJ en erreur | Aucun script ni passe complet, code antérieur |
| `20261022-201356-47832` | Aucune trace exploitable, journaux vides | Aucune mesure |
| `20261022-204355-40772` | 21/20 tours finis, 9/8 tours MJ, 25/20 appels ; aucun tour en erreur | Aucun script ni passe complet, code antérieur |

Extractions mémoire : `artifacts/luna-intermediaire-*.json`. Les arrêts ont visé seulement
les enfants identifiés et revalidés. Une demande d'arrêt plus large a été refusée par la revue
automatique ; la méthode étroite autorisée a permis de continuer.

## Limites

L'extraction courte d'une apparence est déterministe et bornée ; les portraits dont la
première proposition n'est pas exploitable se replient sur le genre. Des personnes semblables
reçoivent un numéro pour rester ciblables ; aucun système de déguisement n'est introduit.
Les anciens souvenirs visuels ne prouvent pas qu'un nom avait été entendu : ils ne sont pas
convertis en présentations. La contradiction mécanique sans nom reste partiellement sémantique.
Le protocole de réplique auditée n'a pas de destinataire tiers typé : entendre un nom de tiers
ne présente pas son corps. Les appels ciblés du moteur possèdent ce lien. Le classement d'une
présentation reste sémantique ; la citation et son enregistrement sont contrôlés, sans prouver la
sincérité. Les mentions lexicales du banc peuvent aussi relever le nom que le moteur refuse
explicitement de reconnaître : ce compteur ne mesure pas directement les fuites.
Les trois épuisements de saisie simulée dans une passe antérieure restent non expliqués,
même si la passe exhaustive instrumentée suivante est verte sans correction du jeu.
