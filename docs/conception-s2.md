# S2 — Dossier social : ordre des bascules et preuves attendues

31 octobre 2026 · lot 398 · branche `codex-s2-conception` · base `integration e3adc0f4`.
**Conception documentaire : aucun comportement implémenté ni mesuré ici.** Les sous-lots
ci-dessous sont un découpage proposé au superviseur, qui garde la rédaction des briefs.

## 1. Contrat et décisions acquises

S2 remplace le cumul des épreuves par un jugement explicable depuis le dossier subjectif.
Une preuve apprise peut changer ce jugement ; relire, relayer la même origine ou recharger
une partie ne constitue pas un nouvel acte. Le compte social ne déplace aucun bien et ne
solde aucune créance. `donjon/biens.py` reste l'autorité matérielle ; `donjon/agendas.py`
reste celle des engagements, de leurs références temporelles et de leurs issues réelles.

Sources : [plan social](plan-esprit-social.md) lu en entier, notamment §§ 4, 11–13 ;
[S0](conception-memoire-unifiee.md), notamment §§ 2, 5–8 et annexes ;
[inventaire des accès](conception-memoire-unifiee-annexe-acces.md) ;
[décisions du 30 octobre](etat-dev.md). S2 désigne E2 du plan social. Les cinq arbitrages S0
sont **tranchés**, même si S0 les présente encore comme des questions :

| Décision conservée | Conséquence pour les lots proposés |
|---|---|
| 1. Rétention selon importance et âge. | S2a protège les preuves nécessaires, S2b active l'oubli racontable ; aucun plafond 40 comme règle cible. Les durées chiffrées restent à proposer. |
| 2. Héritage minimal des anciennes sauvegardes. | S1 les relit à l'identique. S2m représente une attitude sans acte comme **« héritée, cause inconnue »**, non compensable par une réparation, estompée par les règles ordinaires. Aucun passé reconstitué ; parties neuves pour réparation, trahison et repentir. |
| 3. Seul un acte rattaché au tort identifié le compense. | S2o : restitution, réparation ou équivalent référencé. Un service sans lien ajoute affection/dette morale sans effacer le tort. Des actes répétés peuvent réviser un trait cru (S2q). Les créances matérielles suivent leurs propres actes. |
| 4. Deux ouï-dire incompatibles de même force gardent l'incertitude. | S2c–j : incertitude enregistrée et racontable ; vérification ou question à un tiers si l'action l'exige. Les jets actuels demeurent jusqu'au portage de chaque voie. |
| 5. Le grief durable alimente la bande de refus. | S2r : colère aiguë pour expression et urgence, jamais seule pour décider un refus ; hystérésis et signatures conservées et mesurées. |

Sur une nuit, le grief, la confiance et la dette ne s'effacent pas avec le temps ; les
émotions retombent en minutes (plan social § 4.1). L'estompement de la composante héritée
reste celui demandé par la décision 2 ; ce n'est ni une preuve de réparation ni un tort
ancien inventé. La position datée du lot 374 et les prévisions physiques gardent leur
contrat : oublier un récit n'est pas rendre un fait mobile actuel, ni le déclarer faux.

L'ordre des actes compte, la tranche est l'auberge et les biographies y seront écrites à
la main : décisions de placement déjà validées. S2 n'active ni attribution de motif S3,
ni valeurs estimées S4, ni sanction attendue S5, ni motivations noires S6. Les contrôles
du MJ restent jusqu'au lot qui leur fournit effectivement une garantie de remplacement.

## 2. État de départ et taille des lots

Sur cette base, `donjon/memoire.py` fournit la porte d'insertion et les vues pures d'épisodes,
encore au format historique et au plafond 40. `donjon/relations.py` possède les six axes,
`EPREUVES`, les bandes, les ancrages et `preuves_relations`. Sa fonction `_appliquer` applique
seulement le complément d'une preuve renforcée, mais cumule encore les épreuves ;
`service_rendu`, `nourri` et `recu` peuvent diminuer la rancune sans rattachement à un tort.
`donjon/signes.py` possède déjà `emotions.colere` et sa décroissance (`emotion`, `eprouver`).
**Ces constats de code ne sont pas des garanties S2.**

Les rapports [373](taches/rapport-codex-373-s0-conception-memoire.md),
[378](taches/rapport-codex-378-s1a-porte-episodes.md),
[379](taches/rapport-codex-379-a2-expression-son.md),
[380](taches/rapport-codex-380-um-social-comptes.md),
[382](taches/rapport-codex-382-s1b-sons-examens.md),
[383](taches/rapport-codex-383-s1c-approches-secours.md),
[384](taches/rapport-codex-384-s1d-promesses.md) et
[385](taches/rapport-codex-385-s1e-vues-episodes.md) ont été relus. Le rapport 381 n'existe
pas dans cette base ; son [brief](taches/codex-381-a2-passage.md) ne prouve pas sa livraison.
S1f est en vérification ([397](taches/codex-397-s1f-localisation.md)), S1g–p restent futurs.
Les noms de champs futurs ci-dessous décrivent des contrats ; ils ne sont pas annoncés comme
des API déjà présentes. Relever les API effectivement livrées avant chaque brief.

Chaque ligne S2a–r est une unité de travail de **30 à 45 minutes** : une règle commune,
un raccord limité, deux parcours ciblés et la mesure courte du § 6. Les activations S2d–i
utilisent le même arbitre S2c ; leurs frontières suivent les propriétés mécaniques déjà
déclarées en S0, jamais un lieu, un PNJ ou une formulation. Aucun nouveau mode de jeu.
Le superviseur vérifie le nombre réel d'appelants sur la base du brief : si une ligne
dépasse le créneau, il la scinde par producteur/consommateur, avec le **même** invariant
et des critères de chaîne complets pour chaque partie ; une voie non portée garde ses contrôles.
La révision de tous les faits, ou la projection des six axes et les trois politiques sociales,
ne doivent pas être réunies dans un seul lot.

Ordre de livraison proposé : **a/b** preuves puis rétention ; **c** arbitre ; **d–i** ses six
raccords de familles ; **j** vérification et parole sur l'incertitude ; **k/l** compte puis
dossier ; **m/n** héritage puis projection des axes ; **o/p/q** réparation, trahison, repentir ;
**r** grief et colère. Les raccords d–i supposent les producteurs et lecteurs déjà fermés
par S1 : ils activent une politique commune sur ces portes, sans reprendre les centaines
d'accès bruts du relevé S0. Si cette fermeture manque, finir le portage S1 avant le raccord.

## 3. Dépendances de S1, champ par champ

Les champs historiques sont nommés ici pour identifier les dépendances ; ils ne sont pas
une autorisation d'accès brut. Toute consommation future passe par la porte livrée par S1.
Les colonnes indiquent le minimum local ; **S1p reste le verrou global d'activation** (§ 3.2).

| Portage | Champs attendus et contrat à vérifier à sa livraison | Sous-lots consommateurs |
|---|---|---|
| S1f (397) | `croyances[*].lieu` : valeur, `salle`, `case`, `origine`, `possession` ; date d'observation/apprentissage, confiance initiale, mobilité et consommation de l'hypothèse 374. `possession` garde ensemble `porteur`, `proprietaire`, `permis`, `remis_par`, `remise_autorisee`. | S2c/d ; S2k/o pour attribution et retour. Aucun droit assemblé depuis deux dates. |
| S1g | `croyances[*].etat` (champs partiels, dont `allume`, états du corps), `lumiere` et `allumees`, `pieces`, `fin`, `verrouillee`, `passage` ; absence, faux explicite et inconnu distincts ; fin négative conservée après réparation. | S2e, puis k/l/o. Une capacité est dérivée des faits connus, pas du réel caché. |
| S1h | `croyances[*].eau` : niveau/pente/repère ; `prevision` : valeur, rang et conviction ; `statuts` : titre, lieux, domaines et liste vide. Sources, dates et filtres actuels conservés. | S2f (eau/prévision), S2g (statuts), S2j. |
| S1i | `attitude:*`, `emotion`, `intention`, `parole_doutee` : signe/cible/occurrence/date ; `detresse` et sa preuve de canal ; `violence` : victime, menace, opération, date, `clos`. | S2h (lectures/détresse), S2i (danger), S2r (signes). Perte de vue distincte d'un démenti. |
| S1j | `faits_dits` : valeur, `dit_a`, `entendu_a` ; `faits_initiaux`, `derniere_confidence` ; `voix`, `noms`, `voix_entendues` (`se_dit`, méfiance, repère), `echange`. Références aux occurrences d'`emissions_parole`, identité perçue et audiences connues. | S2a/b (parole à conséquence), c–j (origine et incertitude racontable), k–q (preuve attribuée). Une voix prétendue ne récupère pas le dossier d'un nommé. |
| S1k | `refus` : demande, raison, date, cause, offre/contre-offre et repère ; `demande_refusee` ; `recours_propositions`, `recours_services`, `service_en_cours`, `recours_intermediaires`. Prédicats de réouverture et publication du choix conservés. | S2j (question/vérification sans boucle), n/r (bandes), interface E9. Temps seul ou moyens perdus ne réarment rien. |
| S1l | `recherches[qui][salle]`, `indices_recherche`, `presence_recherche` : négatifs, dernier positif et contenus consommés. | S2d/j ; identité des alternatives incertaines séparée d'un nouveau signal positif. |
| S1m | `attentes_bornees`, `renoncements` (date, but, cause), `donne` (dernier geste propre), `visites` : signatures utiles et publication après choix réussi. | S2b (ne pas oublier les suivis actifs), j/n/r et E9 (ne pas relancer un échec inchangé). |
| S1n | `preuves_relations` : preuve, niveau, effets ; `portages` : objet, auteur, preuve ; `suites` : conséquence, bénéficiaire, condition, date, preuve ; `compagnie`, `compagnie_minute` ; `indices_soupcon.presences`, `gestes`, `constats`, `soupcons`, `oublis`. | S2a (résumés protégés), k–r. Marque d'intervalle incomplet, perte appliquée et levée du soupçon restent distinctes d'un tort certain et de sa réparation. |
| S1o | `aides_attendues`, `rejoint`, `rejoindre`, `mandats_percus` ; vues connues d'`engagements`, `promesses_joueur`, `reference_temporelle`, `sequence_obligations`, `accord_initial`, `issues_obligations`. Raccorder aussi les connaissances de `dettes`, `permissions`, `services_rendus`, `restitutions`. | S2a/k/l/o, puis E7/E9. Une issue réelle distante n'est pas une issue connue ; une référence de contrat n'est pas une copie mutable de son archive. |
| S1p | Conteneur/version ; identité des épisodes et faits, dates et précision inconnue, source/chaîne d'origine/confiance/preuve ; liens entre couches ; index reconstruits ; migration réversible de tout l'état historique et AST final. | Toutes les activations. La structure du dossier existe sans lecteur social nouveau ; aucune histoire perdue n'est recréée. |

`relations`, ses `bandes/ancrages/motifs`, et `emotions.colere` sont des états dont les
propriétaires restent respectivement `donjon/relations.py` et `donjon/signes.py` ; S1n/i/p
doivent exposer leurs preuves sans transférer leur autorité. Même séparation pour les bourses,
créances et contrats réels dans `donjon/biens.py` et `donjon/agendas.py`.

### 3.1 Données nécessaires au dossier, encore sans schéma S2 imposé

Une ligne d'échange doit pouvoir retrouver observateur, contrepartie connue, nature,
objet/quantité/unité, date d'acte et d'apprentissage, origine/preuve, obligation/version,
statut connu et éventuel lien de compensation. Le tort, sa réparation et le jugement sont
trois identités distinctes. Une preuve renforcée met à jour la connaissance du même acte.
Une précision temporelle inconnue reste inconnue ; aucun ordre ancien fictif pour la trahison.
Le dossier compile meilleur/pire/dernier/en suspens avec un départage stable et une explication.
Les traits crus ont source et confiance ; les valeurs estimées restent sans lecteur jusqu'à S4.
Ce sont des exigences de données, pas de nouveaux registres parallèles à ceux de S1p.

### 3.2 Ce qui peut commencer avant la fin de S1

La préparation documentaire des tables de rétention (S2a/b), des oracles de contradiction
(S2c–j) et des paires de scènes (S2k–r) peut commencer dès maintenant. Après S1g/h, on peut
figer les propriétés des futures activations e/f/g ; après S1n/o, la correspondance des preuves
du compte k/l et des contrats E7. Cela ne requiert pas de nouveau champ de sauvegarde.

**Aucune bascule S2 ne part en production avant S1p** : S0 place ces comportements après S1
et interdit tout autre lot PNJ ajoutant un registre pendant S1. Même S2a/c, préparatoires,
attendent ce verrou pour leur implémentation. Les dépendances locales ne justifient donc pas
de lancer un dossier provisoire à côté du stockage historique. On peut préparer les briefs,
pas annoncer un sous-lot moteur S2 livrable sur la seule livraison de S1f.

## 4. Sous-lots ordonnés

Tous héritent des preuves de chaîne et du banc rapide **4 h, quatre graines** du § 6 ;
les critères ci-dessous s'y ajoutent. Les cas R/A sont définis au § 5 : R est le cas
historique, A l'autre cas de même nature. Les fichiers de tests cités sont existants,
à étendre ; aucun nom de future fonction S2 n'est présenté comme livré.

### S2a — Une preuve encore utile survit à la perte du détail de son épisode

Dépendances : S1j/n/o/p. Entrées : épisodes, références d'obligation, jugements, soupçons,
paroles à conséquence. Fichiers : `donjon/memoire.py`, raccords de validation de
`donjon/esprits.py`, `tests/test_memoire_socle.py`, `tests/test_deja_dit.py`.
Seul changement : définir et conserver le résumé référencé ; pas encore de nouvelle éviction.
Oracles R1/A1 : remplir au-delà de 40, garder la preuve du tort/dit et le suivi actif,
sans nouvelle épreuve à la recharge. Risque : tout protéger sans borne ou perdre une origine.
Fusion : chaque référence active reste résoluble, les copies sont pures ; coût/volume relevés.

### S2b — L'oubli racontable dépend de l'âge et de l'importance

Dépendances : a et toutes les vues d'épisodes S1 ; paramètres du § 8 à valider au brief.
Entrées : date sauvegardée, importance de famille, résumé protégé. Fichiers :
`donjon/memoire.py`, `donjon/recit_pnj.py`, `donjon/paroles.py`,
`tests/test_memoire_socle.py`, `tests/test_deja_dit.py`.
Oracles R1/A1 : plus de 40 routines ne chassent pas un tort ; à seuil d'âge égal, les routines
peu importantes perdent leur détail selon la table, jamais l'obligation ni le fait de contrôle.
Risque : supprimer un indice utile plus tard ou refaire une confidence. Fusion : rétention
identique en temps entier/découpé, pas de fait recréé depuis la chronique, décision 1 mesurée.

### S2c — Une contradiction comparable reçoit une décision commune et traçable

Dépendances : S1f–j/p, a. Entrées : propriété, valeur, dates, origine, source, poids et preuve.
Fichiers : `donjon/memoire.py`, `tests/test_memoire_socle.py`, `tests/test_disputes.py`.
Installer l'arbitre commun et son résultat typé sans brancher les anciennes admissions.
Oracles R2/A2 : même résultat et mêmes alternatives en inversant l'ordre d'arrivée des deux
preuves de même force ; doublon de relais sans renforcement indépendant ; constat admissible
postérieur distinct d'un mensonge. Risque : comparer des moments différents comme contradictoires.
Fusion : résultat reconstructible après recharge et lecture sans jet ; comportement des voies
encore historiques conservé. Le résultat « incertain » n'est pas encore une capacité d'action.

### S2d — Localisation et possession appliquent la révision commune sans inventer de droits

Dépendances : c, S1f/l/j/p. Fichiers : `donjon/memoire.py`, `donjon/esprits.py`,
`donjon/social.py`, `donjon/positions_crues.py`, `tests/test_position_hypothese.py`,
`tests/test_garde_ouidire.py`. Entrées : preuve composée de lieu/droits et dates de 374.
Oracles R3/A3 : relais inchangé sans rajeunissement ; deux droits de dates différentes ne
s'assemblent pas ; nouveau constat révise sans rendre coupable un simple suspect.
Risque : le statut daté ou l'indice consommé disparaît. Fusion : 374 reste vérifié, égalité
de force enregistrée comme incertitude ; pendant l'intervalle avant j, toute action exigeant
la valeur litigieuse conserve un refus ou une vérification sûre, sans choisir un côté.

### S2e — Un état matériel révisé conserve ses preuves atomiques

Dépendances : c, S1g/j/p. Fichiers : `donjon/memoire.py`, `donjon/esprits.py`,
`donjon/social.py`, `donjon/biens.py`, `tests/test_constater_rumeurs.py`,
`tests/test_avis_redits.py`, `tests/test_service_non_defait.py`.
Entrées : `etat/lumiere/pieces/fin/verrouillee/passage`, par propriété déclarée, jamais par objet.
Oracles R4/A4 : extinction, rallumage et nouvel avis ; réparation connue après destruction,
avec `fin` négative ; absence d'information différente d'un faux connu. Risque : fusionner
des états partiels incompatibles ou ressusciter une ancienne destruction.
Fusion : ancienne version historique conservée si référencée, état courant cohérent et
aucune nouvelle capacité depuis une parole non adoptée ; garde d'action comme d avant j.

### S2f — Une mesure ou prévision d'eau se révise sur ses propres preuves

Dépendances : c, S1h/j/p. Fichiers : `donjon/memoire.py`, `donjon/esprits.py`,
`donjon/social.py`, `donjon/eau.py`, `tests/test_disputes.py`, `tests/test_prevision_bornee.py`.
Entrées : repères/niveaux/pentes, rang, conviction et origines. Oracles R2/A2, sur prévisions :
deux ouï-dire égaux restent incertains et un constat propre admissible les départage ;
une date nouvelle seule ne crée pas une nouvelle mesure. Risque : mélanger poids social et
modèle physique, ou prévoir depuis le niveau réel caché. Fusion : modèle d'eau inchangé,
nouvelle règle d'adoption isolée, garde d'action sûre avant j et décision 4 conservée.

### S2g — Un statut connu se révise sans consulter le profil réel du titulaire

Dépendances : c, S1h/j/p. Fichiers : `donjon/memoire.py`, `donjon/relations.py`,
`donjon/social.py`, `tests/test_relations_statuts.py`, `tests/test_agendas_jugement_mandat.py`.
Entrées : titres, portée et démenti vide. Oracles R2/A2, sur statuts : annonce contradictoire
dans une portée puis démenti appris, autre titulaire et domaine ; égalité conservée.
Risque : convertir un titre annoncé en autorité vraie. Fusion : aucune modification du
profil caché n'affecte le jugement sans preuve apprise ; garde d'action sûre avant j.

### S2h — Une lecture sociale se révise par occurrence et canal perçus

Dépendances : c, S1i/j/p. Fichiers : `donjon/memoire.py`, `donjon/signes.py`,
`donjon/causes.py`, `tests/test_empathie_peur.py`, `tests/test_secours_acquitte.py`.
Entrées : lectures d'attitude/émotion/intention/doute et détresse. Oracles R5/A5 : disparition
du champ de vue sans démenti ; calme effectivement discerné, puis nouveau signe contradictoire.
Risque : confondre interprétation et émotion réelle. Fusion : dates/occurrences et horizons
propres aux signes conservés ; aucune nouvelle lecture ou tirage à la recharge.

### S2i — Un danger cru se révise sur sa clôture connue

Dépendances : c, S1i/j/p. Fichiers : `donjon/memoire.py`, `donjon/defense.py`,
`tests/test_defense.py`, `tests/test_secours_acquitte.py`.
Entrées : auteur/victime connus, menace/opération, date et clôture. Oracles R5/A5 : danger
signalé, neutralisation constatée, répétition de l'ancien cri sans réouverture ; deuxième
victime et témoin ignorant la neutralisation. Risque : danger réel lu à distance.
Fusion : clôture réelle et clôture apprise distinguées, urgence vitale toujours accessible ;
la table commune ne change pas les durées physiques ni le contrat de défense.

### S2j — Agir sur un fait incertain déclenche seulement la vérification nécessaire

Dépendances : d–i, S1k/l/m. Fichiers : `donjon/planification.py`, `donjon/deliberation.py`,
`donjon/social.py`, `donjon/paroles.py`, `donjon/emissions.py`,
`tests/test_contact_sous_but.py`, `tests/test_disputes.py`, `tests/test_informations_parlees.py`.
Entrées : alternatives admises, raison d'incertitude et besoin de l'action ; aucun choix privé
de l'arbitre au moment de lire. Oracles R2/A2 : le PNJ peut rapporter les deux avis avec leurs
sources connues ; une action qui a besoin de les départager provoque constat ou question au
tiers accessible ; l'action indépendante se poursuit. Risque : enquête permanente ou attente
en boucle. Fusion : une vérification inchangée ne se réarme pas par le temps/recharge ; mots
moteur enregistrés avant affichage, signatures ne dépendant que des valeurs réellement lues.
Si un recours manque, refuser localement sans traiter l'une des alternatives comme vraie ;
la couverture incomplète doit rester explicite au rapport, sans proclamer la décision 4 entière.

### S2k — Le compte subjectif inscrit un échange une seule fois

Dépendances : a, d/e/j, S1n/o/p. Fichiers : `donjon/memoire.py`, `donjon/relations.py`,
`donjon/echanges.py`, `donjon/biens.py`, `donjon/agendas.py`,
`tests/test_sens_dette.py`, `tests/test_realisation_datee.py`, `tests/test_echanges_suite.py`.
Entrées : pris/rendu/dû/prêté/service, quantité/unité, preuve et obligation connues (§ 3.1).
Oracles R6/A6 : remboursement reçu et restitution volontaire ; livraison distante ignorée
puis apprise. Risque : double ligne réception/engagement ou lecture de la créance vraie.
Fusion : une ligne par acte connu, enrichissement de sa preuve sans double compte ; aucun
paiement, droit ou clôture depuis le dossier. Axes historiques conservés à cette étape.

### S2l — Un dossier compile les faits marquants depuis les seules lignes connues

Dépendances : k et b. Fichiers : `donjon/memoire.py`, `donjon/relations.py`,
`tests/test_relations_lectures.py`, `tests/test_relations_graduees.py`.
Entrées : compte, preuves sociales non matérielles (coup, refus, mensonge, avertissement),
ordre appris et statuts en suspens. Oracles R7/A7 : un meilleur, un pire et un dernier
retrouvables après plus de trois actes ; version alternative restée incertaine ; même dossier
en relisant. Risque : cacher un tort compensable sous un résumé ou perdre un lien de preuve.
Fusion : explication de chaque sélection et départage stable ; aucun trait certain sans preuve,
aucun axe nouveau actif. Pas d'estimation de valeurs ni de schéma de biographies S7 ici.

### S2m — Une attitude sans acte garde son origine héritée inconnue

Dépendances : l, S1p. Fichiers : `donjon/memoire.py`, `donjon/relations.py`,
`donjon/esprits.py`, `tests/test_relations_socle.py`, `tests/test_relations_graduees.py`.
Entrées : axes/ancrages/bandes survivants et preuves réellement présentes ; profils de départ
séparés des actes vécus. Oracles R8/A8 : deux anciennes captures, origine inconnue conservée
sans faux vol, parole ou ordre ; un retour ultérieur ne trouve aucun tort inconnu à compenser.
Risque : recomptage des preuves visibles en plus de l'axe hérité. Fusion : composante héritée
explicite, contribution unique, décision 2 et estompement ordinaire vérifiés après deux recharges.

### S2n — Les axes ont une seule source : la projection du dossier

Dépendances : l/m, b et j. Fichiers : `donjon/relations.py`, `donjon/memoire.py`,
`donjon/planification.py`, `tests/test_relations_socle.py`,
`tests/test_relations_graduees.py`, `tests/test_relations_ascendant.py`.
Entrées : dossier compilé, état hérité, états de bandes et ancres affectives nécessaires.
Oracles R7/A7 : mêmes preuves relues ou renforcées, sans second cumul ; service sans lien
ajoute du crédit en laissant le tort. Fusion : six axes passent par `relations.axes/envers`,
aucun vieux cumul actif en parallèle, bandes et signatures suivent leurs valeurs utiles.
Confiance/dette n'évoluent pas au seul passage du temps. Rancune historique reste transitoire
jusqu'à r ; aucune prétention de grief durable avant cette bascule. Réparation/trahison/
repentir ne sont pas activés ensemble ici. Risque : arrondis, saturation et coût par nœud.

### S2o — Une réparation compense uniquement le tort auquel elle est rattachée

Dépendances : n, k et preuves de retour/réparation de d/e. Fichiers : `donjon/memoire.py`,
`donjon/relations.py`, `donjon/echanges.py`, `tests/test_relations_graduees.py`,
`tests/test_constater_soupcon.py`, `tests/test_restitution_route.py`.
Entrées : tort identifié, acte réparateur connu, lien et portion compensée. Oracles R7/A7 :
vol puis retour de l'objet ; dégradation puis réparation/équivalent ; service sans lien témoin
négatif. Risque : réparer deux torts avec la même portion ou confondre restitution et don.
Fusion : décision 3, compensation unique, grief/rancune réduit plus que confiance restaurée
selon le réglage du brief ; dette matérielle seulement réglée par `biens`. Un soupçon démenti
annule sa perte propre, sans raconter une réparation d'un tort jamais établi.

### S2p — Le poids d'une trahison dépend de la relation crue avant le tort

Dépendances : n/o. Fichiers : `donjon/relations.py`, `donjon/memoire.py`,
`tests/test_relations_graduees.py`, `tests/test_preuve_engagement.py`.
Entrées : affection antérieure justifiée et ordre des actes connus, pas affection recalculée
après le tort. Oracles R7/A7 : service puis vol/parole rompue, contre ordre inversé, sur deux
paires de personnes. Risque : chaque relecture augmente la trahison ou le réel caché la déclenche.
Fusion : sur partie neuve, même tort connu pèse davantage venant d'un apprécié selon le réglage
explicite ; ordre incertain d'une capture ancienne ne produit pas de fausse trahison.

### S2q — Des actes ultérieurs cohérents révisent un trait cru sans solder le tort

Dépendances : n/o/p. Fichiers : `donjon/memoire.py`, `donjon/relations.py`,
`donjon/social.py`, `tests/test_relations_graduees.py`, `tests/test_informations_parlees.py`.
Entrées : trait sourcé, tort connu et plusieurs actes indépendants postérieurs.
Oracles R7/A7 : après vol ou mensonge, plusieurs actes cohérents révisent « voleur » ou
« menteur » ; même service relayé ou même promesse répétée ne fait qu'une preuve.
Risque : service isolé effaçant tout, ou prétention de repentir prise pour acte.
Fusion : trait, confiance et tort restant distingués ; nouvelle formulation seulement après
décision moteur enregistrée, sans créer un fait biographique ni un pardon forcé.

### S2r — Le refus suit le grief durable, l'émotion suit sa cause aiguë

Dépendances : n–q, S1i/k/m/n. Fichiers : `donjon/relations.py`, `donjon/signes.py`,
`donjon/echanges.py`, `donjon/deliberation.py`, `donjon/planification.py`,
`tests/test_refus_retenus.py`, `tests/test_signes.py`, `tests/test_relations_graduees.py`.
Entrées : grief issu des torts non compensés, composante héritée explicitement distinguée,
ancre `emotions.colere`, bandes précédentes. Oracles R9/A9 : sans événement nouveau, la colère
retombe, le grief neuf et la bande de refus demeurent ; réparation liée réduit le grief ;
colère seule sans grief ne décide pas du refus. Risque : compter deux fois le tort ou faire
osciller la bande à chaque lecture. Fusion : décision 5, hystérésis, signes perceptibles et
signature des recherches vérifiés ; `relations.en_veut` et les lecteurs de `rancune` désignent
explicitement le grief. Aucun taux de demi-vie de la rancune historique appliqué au grief neuf.

## 5. Cas historiques, autres cas et captures à constituer

Les chemins ci-dessous existent sur la base ; une **scène construite dans un test** n'est pas
une capture de partie. Les extensions réparation/trahison/repentir ne sont pas aujourd'hui
observées dans une partie réelle. Les lots concernés devront capturer leur chaîne neuve à
l'auberge : ce document ne peut ni inventer un passé aux captures ni annoncer ces preuves vertes.

| Paire | Point réel ou historique R ; autre cas A | Oracle lisible et moments à capturer |
|---|---|---|
| R1/A1, récit/contrôle | Mine 3 dans `tests/test_deja_dit.py` ; Hugues au couloir de l'auberge, chaîne du 378 dans `tests/test_memoire_socle.py`. | Avant saturation, après >40 routines, au seuil d'âge puis après reprise : détail retenu/oublié, preuve et obligation actives, zéro confidence réarmée par oubli. |
| R2/A2, contradiction | Deux avis opposés Aubin/Ilse au Relais, scène historique `tests/test_disputes.py` ; prétention fausse puis démenti dans `tests/test_relations_statuts.py`. | Avant chaque audition, après égalité de force (sources, deux valeurs, raison d'incertitude), après question/constat décisif. Construire la variante de deux statuts incompatibles de même portée depuis cette seconde scène. Ajouter l'autre paire/lieu de `tests/test_disputes.py` pour f et une autre paire de titulaires pour g. Les jets historiques sont des références de départ, pas les résultats cibles de S2. |
| R3/A3, lieu/droits | `tests/captures/position-374-auberge-7-240.json.gz` : Mathurine/Lucien ; Bram/Rémy dans `tests/test_position_hypothese.py`, et preuves composées de `tests/test_garde_ouidire.py`. | Hypothèse ancienne, relayée, consommée, puis revue ; isoler les variantes de contradiction sans antidater de preuve. Le cas de droits complète la localisation, il ne s'en déduit pas. |
| R4/A4, matière | Brune, torche, crue 2024 dans `tests/test_avis_redits.py` (fixtures `tests/fixtures/avis_redits/`) ; deux lampes homonymes de la mine dans ce même fichier. | Extinction/rallumage/nouvelle extinction, audience déjà informée puis réellement nouvelle. Pour `fin`, ajouter deux chaînes de destruction/réparation, sans prétendre qu'elles figurent déjà dans ces captures. |
| R5/A5, détresse/danger | `tests/data/secours-223-22.json.gz` et `tests/data/secours-223-26.json.gz` ; deuxième chaîne Gorm/Ilse de rixe dans `tests/test_secours_acquitte.py`. | Cri, examen, état vu postérieur et neutralisation ; témoins différents, recharge avant chaque apprentissage, mots entendus sans cause cachée révélée. |
| R6/A6, échanges | Achat réel Relais 42 minute 151 dans `tests/test_taches_payees.py` (chaîne 384) ; tâche datée à l'auberge de `tests/test_realisation_datee.py`. | Accord/paiement, réalisation, clôture réelle, apprentissage du bénéficiaire. Ajouter remboursement de `tests/test_sens_dette.py` et prêt rendu de `tests/test_relations_graduees.py` ; ne pas prendre une créance vraie pour connaissance automatique. |
| R7/A7, jugement | Brune donne du bois puis prévient Gorm, et Odon refusé par Mathe puis vu manger le pain de Lucien, scènes de `tests/test_relations_graduees.py` ; Anselme/Lucien et le ballot, scène auberge de `tests/test_constater_soupcon.py`. | Partie neuve : acte illicite réellement perçu, service sans lien, retour/réparation liée, seconde faute ; variantes d'ordre et plusieurs actes indépendants. Pour p : mêmes actes, affection préalable différente et justifiée ; pour q : vol puis actes cohérents, puis mensonge dans l'autre cas. Capturer preuve, trait, solde du tort, axes/bandes et réaction publique. Les scènes existantes servent d'amorces ; chaque prolongement est à produire, pas à injecter comme souvenir. |
| R8/A8, héritage | `tests/captures/position-374-auberge-7-240.json.gz` ; `tests/data/secours-223-22.json.gz`. | Inventorier les attitudes réellement privées de leurs actes à la base de m ; si une capture n'en porte aucune, choisir une autre capture existante et l'indiquer. Avant/après migration, estompement ordinaire puis retour ultérieur : aucune cause ni compensation inventée. |
| R9/A9, grief/colère | Refus Odon/Mathe et Brune/marchand dans `tests/test_relations_graduees.py` ; autre paire Anselme/Lucien construite depuis l'auberge neuve. | Tort neuf, colère forte, colère retombée sans réparation, acte réparateur lié, demande répétée aux frontières de bande ; contrôler aussi colère seule. Capturer avant/après le temps et chaque événement ; le refus ne dépend pas du ton seul. |

Chaque paire est exercée dans la vraie chaîne **saisie ou acte direct → moteur → perception/
audition → mémoire → dossier → décision → enregistrement → rendu → sauvegarde/recharge**.
Les séquences purement injectées servent à éprouver l'arbitre, jamais à remplacer ces parcours.
Les cas qui ont besoin d'un nouveau contenu encore absent restent des captures à produire dans
leur lot ; pas de solution spéciale à l'objet ou au personnage de la table.

## 6. Mesure et critères communs de fusion

**Pas de calcul dans 398.** Pour chaque futur sous-lot, tests du contrat et fichiers directement
touchés, R/A du § 5, sauvegarde à chaque apprentissage significatif. Comparer état du monde
complet, état subjectif, dossier et référence de preuve, axes/bandes, rendu de Corvus,
`donjon/scene.py`, et mots effectivement enregistrés par `donjon/emissions.py` après recharge.
Le diagnostic du dossier est réservé au banc ; le joueur voit seulement ce qu'il perçoit ou
apprend. Les cas où Corvus n'est pas témoin contrôlent aussi l'absence de fuite.

Même laps en bloc et découpé avec recharges, seuils temporels encadrés au dixième si pertinents,
mêmes actes datés et mêmes jets autorisés : résultat identique, aucun tirage à la simple lecture.
Ne pas reprendre comme résultat cible une assertion devenue volontairement différente ;
documenter l'ancien attendu, le nouveau et sa raison. Les limites de messages sonores du 384
et les rouges hérités ne disparaissent pas par retrait d'une comparaison.

**Banc rapide 4 h**, graines **1985, 7, 42, 2024**, scénarios touchés et **Relais**. Pour la
rétention, la révision commune, le compte et les axes transversaux : auberge, mine, crue et
Relais ; aucun scénario écarté parce qu'il dérange. `tools/comparer_bancs.py` porte les options
`--heures`, `--scenarios`, `--graines`, `--reference`, `--processus` et `--sortie` ; ce ne sont
pas des empreintes identiques promises pour les bascules de comportement. Réutiliser le cache
par commit de `main`, ne jouer que la branche et les références manquantes ; si la base exacte
d'intégration diffère, attribuer ses écarts sans les imputer au lot. Deux processus au plus sur
le laptop, priorité réduite ; aucun test complet, banc long ni campagne Luna dans ces lots.
Une passe Luna seulement si un futur brief porte effectivement un contrat du MJ.

Pour chaque nuit, relever nombre d'épisodes/détails/résumés protégés et taille sauvegardée ;
faits adoptés/révisés/incertains et origines distinctes ; vérifications utiles/vaines ; lignes
d'échange/doublons empêchés/compensations ; traits révisés ; axes/bandes/refus et motifs ; actes
illicites/violents, recherches reprises et répétitions sans information nouvelle. Mesurer
lectures de dossier et coût par choix : aucun parcours intégral de l'histoire dans chaque nœud.
Le CPU ne se compare que sous charge comparable, jamais aux secondes tirées du cache.

Fusion : deux chaînes R/A établies et rechargeables, zéro double paiement/compensation/épreuve,
zéro fuite privée, aucune action qui choisit arbitrairement une alternative incertaine ; toutes
les nouvelles boucles/usurpations du rapide expliquées ou corrigées avant livraison. Rapport
d'une page avec mesures, écarts voulus et limites. Les seuils chiffrés non tranchés restent
signalés (§ 8). Le superviseur groupe le lourd à l'intégration selon `AGENTS.md`.

## 7. Après S2 : E7, essai E9 et tranche de l'auberge

### 7.1 Éviter l'homonymie des étapes

Ici **E7/E8/E9 désignent les suites de l'échéance négociée**, définies dans
[conception-menace-echeance.md](conception-menace-echeance.md), § 5. Leur placement validé
est : S2 terminé → E7 → essai borné d'E9 ; **E8, renégociation d'un accord, est reporté**.
L'E7 « passé et lore » du tableau social désigne S7 dans le point de reprise : ce n'est pas
la prochaine offre de contrat. Aucun de ces chantiers n'est autorisé à inventer un passé S2.

| Suite | Ce que S2 doit fournir avant son départ | Ce qui reste dans le lot suivant |
|---|---|---|
| E7, offre PNJ attendant le consentement de Corvus | Compte subjectif fiable (k), obligations/version/issues **connues** (S1o), jugement social unique (n/r), origine des termes expliqués sans dossier secret. Preuves de paiement et d'acceptation distinctes d'une simple parole/offre. | Identité durable d'offre, auteur/destinataire/termes/révision/validité, consentement explicite, revalidation et expiration. S2 ne crée pas ce cycle et ne remplace pas le contrôle de prix/accord des modules existants. |
| Essai E9, délai proposé pour un recours cru utile et réalisable | Devis sur moyens connus, incertitude demandant vérification (j), bandes/refus et causes de réouverture stables (n/r et S1k/m), compte distinguant payé/attendu/reçu. Un nouveau jugement pertinent peut changer le recours ; une nouvelle date de lecture ne le change pas. | Réemploi d'E7 sur une sollicitation ou un refus pertinent, une alternative déterministe ; auberge puis mine. Compter offres, accords utiles et répétitions. Pas de balayage permanent, de besoin secret ni de modification d'un accord conclu. Arrêt et bilan si seule répétition ou aucune décision utile. |

E7 reprend les garanties temporelles E1–E6 et les devis existants de `donjon/echanges.py` et
`donjon/planification.py`. S2 n'apporte ni maintien continu, ni prêt daté, ni paiement différé,
ni sanctions nouvelles au dépassement ; il n'étend pas les formulaires 380/396.

### 7.2 Tranche verticale : protocole proposé, sans écrire les biographies ici

Support existant : `donjon/scenario_auberge.json`, huit PNJ. Biographies **écrites à la main**,
gelées pour la tranche future S7 ; aucune génération de passé pendant une partie ou une recharge.
Un passé partagé peut être connu de certains seulement ; ses versions privées ne sont pas
versées dans la projection publique de `donjon/projection_publique.py`. Les secrets et failles
restent au chantier S7/S8 ; S2 ne les simule pas avec des motifs de relation injectés.

La mesure de S2 utilise des parties neuves à l'auberge pour que l'ordre des actes soit connu.
Les biographies futures devront fournir les mêmes types de preuves que ces actes, sans
politique spéciale de scénario. Préparer les scènes suivantes, chacune avec témoin informé,
témoin ignorant et Corvus présent/absent lorsque c'est pertinent :

1. Ballot déplacé : Anselme constate, reçoit une version contraire et vérifie ; le soupçon
   conserve sa force propre. Captures avant acte, premier constat, contradiction et résolution.
2. Tort suivi d'un retour lié, comparé au même service sans lien : captures de la ligne du tort,
   du lien de réparation, du crédit distinct, des bandes et de la demande suivante.
3. Service puis tort, contre tort puis service, sur deux paires ; captures avant relation,
   après chaque acte et après recharge. Aucun bonus de trahison tiré d'un lien inconnu.
4. Plusieurs actes cohérents après un tort et, séparément, répétition du même ouï-dire :
   captures du trait cru et de ses sources ; repentir distingué d'un tort compensé.
5. Colère retombée, grief restant : captures du signe perceptible et du refus ; le diagnostic
   privé n'est pas montré à Corvus. Autre cas avec colère seule.
6. Paiement et réalisation à distance puis apprentissage tardif : capture avant/après
   apprentissage ; deux offres futures E7, refus/expiration/acceptation, puis alternative E9
   seulement après information pertinente. Les étapes E7/E9 attendent leurs propres lots.

Pour le rapide, enregistrer les quatre nuits auberge de 4 h et les comparer au point de départ
selon § 6. Pour les scènes dirigées, compter les actes utiles jusqu'à la décision, les
vérifications, compensations, refus compréhensibles et différences entre témoins. Publier une
fiche avant/après par scène : acte daté, preuve, connaissance de chacun, jugement privé au banc,
effet réel et texte vu/entendu après recharge. La qualité se juge sur une conséquence mécanique
expliquée et reprise à l'identique, pas sur une prose de repentir. Aucune mesure chiffrée de
cette tranche n'est encore disponible ; aucune biographie nouvelle n'est décidée par 398.

## 8. Questions encore ouvertes et recommandations

Ces propositions ne changent pas les cinq arbitrages acquis. Le superviseur les soumet dans
le brief concerné ; elles ne bloquent pas cette livraison de conception.

| Question | Recommandation à faire valider / lot concerné |
|---|---|
| Durées exactes des routines et échelle d'importance ? | Garder toute la nuit les résumés à conséquence et calibrer quelques durées par familles mécaniques sur le rapide ; borner séparément les textes remis à Luna. S2a/b ; aucun nombre choisi ici. |
| Quand deux preuves sont-elles de « même force » hors du constat comparable déjà défini en S0 ? | Déclarer poids de source, confiance/transmission et comparaison temporelle dans une table commune, sans ordre arbitraire ni tirage à la lecture ; conserver les origines corrélées. Valider les coefficients dans c avant activations. |
| Comment reconnaître et mesurer un équivalent réparateur partiel ? | Lier explicitement acte et tort avec unité/portion ; admission moteur d'une équivalence connue, sans convertir universellement gifles, objets et pièces. Si aucun lien n'est établi, garder le crédit séparé. k/o ; interface libre éventuelle dans un autre brief. |
| Quels coefficients pour réparation, trahison et repentir ? | Mesurer respectivement diminution du grief supérieure au regain de confiance, poids lié à l'affection antérieure, puis actes indépendants assez nombreux pour réviser un trait. Soumettre les valeurs et cas limites au brief o/p/q ; aucune promesse de pardon total. |
| Comment présenter une incertitude et un trait révisé au joueur ? | Mots déterministes bornés aux sources connues et à ce que le PNJ décide de dire ; ne pas exporter le dossier brut. Valider le rendu avec j/q ; Luna seulement dans un portage ultérieur explicite. |

Le découpage ne garantit encore aucun nouveau comportement. Les captures d'extension restent
à produire, les seuils à valider, le rapport 381 et les livraisons S1f–p à relire à leurs
fusions. Si une famille manque à la porte commune ou si un résultat incertain n'est pas traité
jusqu'à l'action et au rendu, la bascule correspondante reste partielle et doit être nommée ainsi.
