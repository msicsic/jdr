# S0 — Conception de la mémoire unifiée des PNJ

30 octobre 2026 · lot 373 · branche `codex-s0-conception-memoire` · base d’intégration
`b83f5a59`. **Proposition de conception, sans modification du moteur.** Les décisions du
[plan de l’esprit social](plan-esprit-social.md), § 13, et leur placement validé dans
[etat-dev.md](etat-dev.md) sont acquis. S0 ne rouvre ni le passé exploitable, ni les motivations
noires, ni l’ordre des actes, ni la tranche écrite à la main à l’auberge.

## 1. Conclusion et périmètre mesuré

Unifier **l’accès et l’identité des preuves**, puis le stockage, avant de changer le jugement
social. Une mémoire ne doit pas pouvoir oublier une obligation encore due, réarmer un refus
par une simple nouvelle date, transformer une parole en vérité, ou révéler la position réelle
d’un absent. En revanche, l’oubli d’un épisode racontable peut être normal. Ces deux durées de
vie doivent cesser de dépendre du même tampon de quarante événements.

Le relevé AST de `donjon/`, `tests/`, `tools/`, complété par recherche `rg` et lecture des fonctions,
donne **71 accès à la mémoire des événements, dans 55 fonctions et 17 fichiers du moteur**.
Ce nombre inclut portes d’écriture, migrations, validations et exports ; ce ne sont pas 71
questions de gameplay. Trois accès supplémentaires à la clé homonyme `memoire` dans `banc_pnj`
concernent le cache des recherches. **247 accès explicites dans 106 fichiers de tests** montrent
que le risque dépasse une cinquantaine de tests isolés. Les 26 occurrences dans les outils
comprennent également des diagnostics et des archives.

L’[annexe des accès](conception-memoire-unifiee-annexe-acces.md) livre les fonctions, lignes et
méthodes de tests mesurées ; les annexes A à C ci-dessous donnent leur sens et leur destination.
Le relevé ne prétend pas être une analyse de flux exhaustive des clés calculées. Les alias connus
(`memoire`, `souvenirs`, `_stock`, `entendues`, `_connues`, `preuves`, `registre`) sont traités ici.
Les formats futurs de 372 et 374 ne sont pas inventoriables comme code présent : leurs briefs
sont lus, leur raccord est défini au § 6 et doit être vérifié sur leurs livraisons avant S1.

**S1 conserve les comportements actuels**, y compris leurs limites : fenêtre de quarante,
délais, ordre des événements, effets relationnels additifs, péremption des signes et règles
actuelles de contradiction. Une représentation permettant âge/importance n’autorise pas à
brancher ce nouvel oubli dans un lot à empreintes identiques. L’activation appartient à un
lot de comportement après S1, précisé au § 5. Aucun banc, suite ou appel Luna n’est lancé en S0.

## 2. Trois couches et un registre, avec des propriétaires explicites

### 2.1 Schéma proposé

Le nom proposé du seul accès au stockage subjectif est `donjon/memoire.py`. Les noms d’API
ci-dessous sont des contrats à implémenter, pas des fonctions déjà livrées. Chaque consultation
porte l’observateur ; aucun lecteur ne peut omettre ce paramètre pour prendre le réel par défaut.

| Couche | Enregistrement canonique proposé | Identité et lecture |
|---|---|---|
| Épisode | `id`, `type`, participants connus, contenu typé, preuve, date de l’événement et date d’apprentissage, source, importance, liens vers faits/obligations | Identité stable d’occurrence ; `episodes(qui, requete)` et `dernier_episode(qui, requete)` renvoient des copies ordonnées. Plusieurs conséquences peuvent partager une preuve. |
| Fait cru | `id`, sujet, propriété atomique, valeur, source et chaîne d’origine, date observée, date apprise, confiance initiale, preuve, statut et raison de révision | Identité de propriété séparée de l’identité de version et de la preuve ; `fait(qui, sujet, propriete)` et vues spécialisées. Une absence vaut une information explicite, distincte d’aucune information. |
| Dossier | personne connue, liens vers preuves, compte subjectif, meilleur/pire/dernier/en suspens, valeurs estimées et confiance, traits crus et sources, version du calcul | `dossier(qui, autre)` ; uniquement ce que **qui** connaît. N’inclut pas les vraies valeurs ni le dossier privé d’**autre**. Profil neutre conservé tant que S4 n’est pas branché. |
| Dit/entendu | occurrence de parole, locuteur perçu (corps ou voix anonyme), mots exacts, contenus typés, destinataires, auditeurs connus de l’observateur, date, références de preuve | `paroles(qui, filtre)` et `transmission(qui, a, identite, valeur)`. Une émission, son audition et son adoption sont trois états distincts. |

Le registre des occurrences **existe déjà** : `emissions_parole`, propriétaire `emissions.py`
(G15/320). Il reste l’unique preuve mécanique d’émission et d’audition, avec son identifiant
stable. Le registre subjectif proposé référence ces identifiants et prolonge `faits_dits`
par les audiences connues et le souvenir de contenu ; il ne recopie pas les mots dans un
second flux concurrent. Les anciens `paroles_joueur/paroles_pnj` sont migrés par `emissions`,
avec ordre historique inconnu signalé ; on ne reconstruit pas les témoins d’alors depuis ceux
présents à la recharge. Un événement `parole` dans M40 reste une vue récente durant S1.

Les clés d’entité restent des identifiants moteur internes ; leur exposition emploie les noms
connus et les désignations publiques existantes. Une voix qui prétend être X n’hérite pas du
dossier de X. Une personne morte ou partie peut rester connue ; son absence du registre des
objets manipulables n’efface ni son histoire ni un tort.

Un fait matériel composé reste **une preuve atomique** : lieu et photographie de possession
du 337 voyagent ensemble (`porteur`, `proprietaire`, `permis`, `remis_par`, `remise_autorisee`).
Décomposer l’index des propriétés ne permet pas de recombiner les droits de dates différentes.
L’identité « accusation de portage » reste distincte de « lieu avec droits constatés ».

### 2.2 Âge, importance et mémoire utile

La cible applique une table commune par famille d’événements : importance de départ, durée
de rétention racontable, conditions de clôture et références qui empêchent la suppression.
L’âge se calcule depuis une date sauvegardée, jamais par soustraction répétée à chaque tour.
Une routine ancienne peut perdre son détail ; violence, tort, dette ou secret gardent une
priorité plus forte. **Pas de quota de quarante comme règle cible d’oubli.** Les seuils numériques
restent à arbitrer (§ 8), sans les inventer comme décisions acquises.

Une référence active protège son **résumé nécessaire**, pas nécessairement tout le texte :
engagement ouvert, réparation encore possible, preuve déjà jugée, intervalle de soupçon,
contradiction non résolue ou parole pouvant démentir un mensonge. La purge d’un épisode ne
supprime jamais le fait de contrôle ni le marqueur d’une épreuve déjà appliquée. Un intervalle
de présences tronqué reste marqué incomplet ; il ne peut produire une innocence ou une culpabilité.

En S1, `episodes(..., profil="historique")` désigne conceptuellement le comportement existant,
avec sa même éviction et ses suppressions explicites. Ce profil est interne à la migration,
jamais un mode du jeu ni une exception au contrôle. Les lecteurs n’obtiennent pas les épisodes
supplémentaires avant le lot qui change leur contrat. Aucune récupération de souvenirs déjà perdus.

### 2.3 Faits et contradiction : contrat commun cible

Une table `PROPRIETES` déclare une fois : unité d’identité, valeur admissible, sources admises,
mode de révision, prédicat de validité, échéance éventuelle, projection publique et dépendances
du planificateur. Les familles sont des contrats mécaniques, jamais des cas de scénario.

1. L’admission vérifie la preuve et son accès sensoriel, puis inscrit la parole même si son
   contenu est refusé. Elle sépare événement initial, observation et réception. Un relais ne
   rafraîchit pas la date de l’observation ni ne multiplie les sources indépendantes.
2. Deux versions d’une propriété au même moment peuvent se contredire ; deux versions datées
   différemment d’un état mobile peuvent décrire un changement. Une position ancienne ne prouve
   pas un mensonge actuel. Un fait nouveau ne réécrit pas ce qui a été dit avant lui.
3. Pour des preuves comparables : constat propre admissible prime sur ouï-dire à date égale ;
   un constat propre postérieur révise l’état ; un ouï-dire moins récent ne ressuscite pas une
   ancienne valeur. Hors ce cas, le poids combine qualité de la source, confiance envers le
   locuteur identifié et confiance de transmission. Une égalité sans preuve décisive garde
   l’incertitude, avec raison enregistrée, au lieu de choisir selon l’ordre des dictionnaires.
4. Une décision d’adoption ou de révision est enregistrée une fois ; lire un fait ne relance
   ni persuasion, ni tirage, ni épreuve sociale. La confiance n’est pas la vérité. Les assertions
   fausses restent possibles ; la révision ultérieure conserve la provenance qui les explique.
5. Une invalidation matérielle n’est déclenchée que par un constat autorisé ou une conséquence
   propre. Une réparation dément `fin=detruit` par une valeur négative datée ; l’ancien récit
   de destruction reste historique mais ne peut plus redevenir l’état courant.

**Ce contrat cible n’est pas déjà garanti.** Aujourd’hui `croire` remplace directement une
cellule ; `reviser` sanctionne certaines contradictions récentes ; `_adopter`, les prévisions,
les causes de détresse et les statuts ont leurs filtres. S1 les encapsule à l’identique comme
politiques déclarées, sans les uniformiser silencieusement. Une bascule commune de ces arbitrages
est un lot de comportement distinct avant les consommateurs sociaux qui en ont besoin.

### 2.4 Dossier et compte des échanges : frontière de vérité

Le compte du dossier est **subjectif et explicable**, indexé par contrepartie, preuve, obligation
et version ; chaque ligne porte nature (`pris`, `rendu`, `du`, `prete`, service), objet/quantité,
unité, date et statut connu. La réparation référence le tort qu’elle compense. Une dette morale
et vingt pièces à rembourser restent deux grandeurs ; on ne compense pas automatiquement une
gifle, une lanterne et des pièces dans un solde universel. Le calcul relationnel peut les
évaluer selon le PNJ, sans créer ou solder une créance matérielle.

`biens` garde les biens, permissions, finances et créances réelles ; `agendas` garde l’obligation
exécutoire, ses dates et son issue E1–E4. La mémoire ne garde que **la connaissance** de ces
événements, avec leurs références. Aucun accès au dossier ne termine un prêt ou ne rembourse
un marché. Inversement, une clôture mécanique distante n’inscrit pas d’office un grief chez
un bénéficiaire ignorant cette clôture. Le compte sait « j’ai payé et j’attends », même quand
le moteur sait que le prestataire a échoué : c’est une croyance possible.

Les faits marquants se dérivent des lignes encore pertinentes, avec départage stable
importance/date/identité. Les valeurs estimées et traits restent sourcés ; l’absence de preuve
n’est jamais « voleur ». Les six axes demeurent accessibles par **`relations.py`** : ce module
calcule la projection depuis le dossier en S2, puis applique émotions et bandes. Il ne duplique
pas un deuxième journal de torts. En S1, ses axes, ancrages et trois motifs restent inchangés.

### 2.5 Données persistantes, caches et mutations

Doivent rester dans `data` : preuves et identités stables, dates et précision historique,
faits négatifs, versions démenties encore référencées, audiences connues, suppressions/
clôtures, engagements, états d’hystérésis, ancres d’émotions, progression de compagnie,
compteurs de tirage, indices consommés et marqueurs d’intervalles tronqués. Les dossiers
matérialisés portent leur version de compilation et toutes leurs entrées ; ils sont
reconstructibles à l’identique. Aucune information nécessaire à la reprise n’est seulement
dans un objet Python ou dans la chronique omnisciente.

Restent hors mémoire les états opérationnels du § C : monde réel, besoins, intention et
ordonnanceur. Ils gardent leur validation et leur propriétaire ; leurs événements appris
alimentent la mémoire. Une « vue » n’exige donc pas de transformer un plan actif en souvenir.

Les consultations sont pures, retournent des copies ou objets immuables. Les écritures sont
nommées : `retenir_episode`, `admettre_fait`, `reviser_fait`, `retenir_parole`, `clore_suivi`,
`retenir_preuve`, `publier_choix`. L’acquittement `examine`, `tenu`, `juge`, et le rafraîchissement
d’un examen sonore deviennent ces opérations ; muter une liste rendue par une lecture est interdit.
L’ordre actuel `dit → registre`, copie/datation, identification de preuve, ajout/éviction,
`relations.souvenir`, `defense.retenir` est conservé en S1, y compris les appels réentrants.

Les changements issus d’une évaluation restent privés jusqu’à publication réussie du choix
(`vues_du_choix`, `agendas.evaluation`). Une interruption jette les propositions ; elle n’acquitte
pas un secours, ne consomme pas une recherche et ne publie pas un agenda. Les événements réels
sont enregistrés et sauvegardés avant l’affichage, selon le contrat commun du MJ.

### 2.6 Contrôle AST

Reprendre les contrôles `test_relations_socle.py` et `test_agendas_socle.py`, en les renforçant
sur le périmètre subjectif : indice, `.get`, `.setdefault`, `.pop`, `.update`, affectation,
suppression, alias de stock et retour de référence mutable. L’inventaire des accès non portés
est une liste fermée **fichier/fonction/clé**, qui ne peut que diminuer à chaque lot. Une clé
calculée sur un stock brut n’est pas une échappatoire : pas de stock brut renvoyé aux consommateurs.
Les dictionnaires publics homonymes ont des producteurs séparés et un schéma fermé, pas une
exemption globale pour un fichier. Les tests de corruption emploient des fixtures explicites.

`esprits` garde perception et orchestration ; `signes`, `voix`, `social`, `defense`, `relations`
et `agendas` gardent leurs décisions métier et passent par `memoire` pour leurs preuves
subjectives. `relations` et `agendas` restent seuls propriétaires de leurs stocks mécaniques.
Les migrations et validations subjectives sont dans le module d’accès ; elles ne justifient
pas des accès permanents depuis chaque ancien module. Un AST syntaxique seul ne prouve pas
l’absence d’alias caché : éprouvettes négatives et tests de mutation des retours sont requis.

## 3. Ce que sait réellement le moteur actuel

### 3.1 Croyances : attributs, sources et révision

La cellule de base est `croyances[sujet][attribut] = {valeur, source, minute, confiance, ...}`.
Sources admises : `vu`, `savoir`, `essai`, `entendu`, `se_dit`, `devine`, `dit:<identité>` ou
voix anonyme encodée par `voix.source_dite`. Confiance numérique dans [0,1]. `poids_source`
pondère les sources parlées par la relation à leur auteur ; ce n’est pas une décroissance
générale. `croire` écrit, `reviser` constate et peut découvrir un mensonge dans les 30 minutes ;
la réception sociale peut refuser une nouvelle plus ancienne ou moins solide, et faire un jet.

| Attribut validé dans `esprits._croyance_valide` | Contenu et extensions | Vieillissement/révision actuels et vue cible |
|---|---|---|
| `lieu` | valeur salle/porteur/contenant/None, `salle`, `case`, éventuelle `possession`, `origine` | Pas d’oubli général ; absence constatée explicite ; indice positif réouvre un lieu cherché. `localisation` + preuve de droits ; position d’une personne : **374**. |
| `etat` | booléens visibles ; niveaux lumière/blessure ; corps, départ/mort/conscience ; propriétés partielles fusionnées à réception | Constat ou parole ; pas de péremption commune. Vue d’état atomisée sans perdre les preuves composées. Feux : prévision future distincte, hors 374. |
| `lumiere` | niveau devant un objet et sources `allumees` | Actualisation par constat/apport de sources ; pas de taux d’oubli. Vue `lumiere_connue`. |
| `pieces` | nombre cru de pièces dans une bourse | Appris en la tenant ou savoir ; pas de lecture du contenu caché à distance. Vue `fonds_connus`. |
| `fin` | None/détruit/consommé ; désignation conservée | Survit au retrait matériel ; démenti négatif à la réparation. Vue `fin_connue`, preuve pour garde/capacités/nouvelles (337). |
| `verrouillee` | booléen | Essai/savoir ; ouverture/destruction vue la démentent. Vue `fermeture_connue`. |
| `eau` | cm, niveau, pente, repère précédent | Prévision par mesures, pas oubli. Vue de mesure + modèle d’eau existant. |
| `prevision` | booléen ou triplet minute/niveau/pente, rang | Poids et conviction distincts ; preuve propre postérieure retire l’avis contraire ; pas d’effacement par regard perdu. Vue `avis_eau`. |
| `statuts` | titre, lieux et domaines ; liste vide dément | Savoir sélectif initial ou statut annoncé, source/date/confiance ; `relations.statuts_reconnus` garde l’interprétation. |
| `detresse` | booléen et preuve canal/signe/attribut/minute/valeur | Calme discernable, lecture contradictoire du même signe ou indisponibilité connue ; pas par perte de vue ni temps seul. Vue `detresse_retenue`. |
| `attitude:*`, `emotion`, `intention`, `parole_doutee` | sens lu, signe, cible éventuelle, épisode/date d’apprentissage | `croyance` masque à 30 min pour émotion/intention/doute, 120 min pour autre signe ; `signes.actives` garde son filtre métier. Vue `lecture_active`. |
| `violence` | par victime : minute, menace, opération, clos | `defense` : moins de 30 min, clôture sur neutralisation constatée ; réveil seul ne réouvre pas. Vue `danger_cru`. |
| `passage` | géométrie de franchissement validée par `matiere` | Connue ou admise, peut être fausse ; pas de péremption générique. Vue `passage_connu`. |

`fiable` n’est **plus** un attribut de stockage : `esprits.croyance(..., FIABLE)` délègue à
`relations.croyance`. `confie={valeur,dit_a}` est une ancienne extension validée/migrée, pas une
nouvelle source. La date de réception ne remplace pas l’origine d’une localisation relayée.
Le joueur n’a actuellement qu’un sous-ensemble de ces croyances dans `connaissances_joueur` ;
sa mémoire ne justifie ni un profil autonome, ni des axes de relations subjectifs.

### 3.2 Entrées des recherches : ne pas signer tout le journal

`planification._entrees_communes` inclut valeurs crues (en général **sans leurs dates**),
lectures actives des signes, axes/bandes, salles cherchées en vain, souvenirs de promesses
et leur franchissement de `ATTENTE_PART`, refus avec `tient` et bandes de récence, ordre relatif
des visites, aides, travaux payés, permissions/capacités, restitutions et dangers dérivés.
`_entrees_defense` et `_entrees_proximite` ajoutent leurs données selon le but. La projection
fermée d’un devis observateur signe aussi ses données propres. Les registres absents de la
clé ne sont pas nécessairement oubliés : certains n’agissent que **avant** la recherche.

La nouvelle API `signature_decision(qui, domaine, instant)` doit renvoyer les **mêmes valeurs
normalisées** pendant S1, pas la révision globale de la mémoire. Ajouter une phrase, rafraîchir
un regard ou retenir une routine sans effet ne doit pas invalider toutes les recherches. Une
signature contient un prédicat de franchissement temporel quand il est lu, pas l’horloge entière.
Pour 374, les classes de validité de position deviennent des entrées explicites. Pour S2,
les axes/bandes calculés depuis le dossier remplacent exactement leur projection actuelle.

## 4. Vues de remplacement et invalidations

Les tables B/C sont normatives pour le découpage proposé : **à chaque ligne sa règle déclarée**,
jamais une purge globale « récent ». La colonne entrée indique le code mesuré : D = directement
dans `_entrees_communes`, I = par valeur dérivée, H = hors recherche (choix/exécution/rendu),
C = conditionnel à la défense/proximité/projection. Un H n’autorise pas à l’omettre si un futur
geste de recherche commence à le consulter. Les validateurs actuels sont conservés en S1.

## 5. Plan de migration : lots d’un invariant

Chaque ligne ci-dessous est un lot borné, sans changement de choix, parole, délai, tirage,
classement, valeur de relation ni ordre de sérialisation historique. Les lots de croyances
se suivent : pas de chantier PNJ ajoutant un registre pendant S1. La refonte du MJ continue.
Les tests indiqués sont les **fichiers concernés**, pas une autorisation de lancer la suite.

| Lot | Invariant et frontière | Contrôles ciblés / risque principal |
|---|---|---|
| S1a | Toute insertion/éviction d’épisode passe par la porte commune ; stockage historique inchangé, mêmes crochets/réentrance | `esprits`, `relations_graduees`, `defense`, `temps_etat` ; preuves doublées si l’ordre des crochets change. |
| S1b | Sons et examens ont des requêtes/opérations nommées ; plus de mutation d’un alias de mémoire sonore | `ouie`, `ouie_commune`, `ouie_temoins`, `appels_restes`, `demander_cause` ; couverture sonore et rafraîchissement d’examen. |
| S1c | Approches, avertissements et secours lisent/acquittent la même occurrence | `interposition`, `interposition_lieu`, `protection`, `secours_acquitte` ; `examine/tenu` ne doivent pas muter une copie perdue. |
| S1d | Promesses, prêts et travaux payés gardent leurs requêtes historiques d’épisodes | `promesses`, `taches_payees`, `contrat_engagement`, `echanges_suite`, `reclamations_repetees`, `realisation_datee` ; ordre et fenêtre 40 conservés. |
| S1e | Tous les autres lecteurs d’épisodes (jeu, rendu, banc et outils) passent par des vues pures | A, fichiers concernés ; ordre de `paroles_retenues`, métriques historiques, dernier son et derniers trois souvenirs. |
| S1f | Une seule interface lit/écrit les valeurs de localisation et preuves de possession | `contact_position_inconnue`, `contact_sous_but`, `garde_ouidire`, `agendas_transferts`, tests livrés par 374 ; aucune perte du statut daté ni droits recomposés. |
| S1g | États matériels/capacités sont accessibles seulement par leurs vues crues | `planification`, `lumiere`, `constater_rumeurs`, `agendas_fins`, `service_non_defait` ; distinguer absence, fin négative et valeur inconnue. |
| S1h | Eau/prévisions/statuts ont des preuves accessibles et politiques de révision déclarées | `avis_menace`, `avis_parles`, `disputes`, `relations_statuts` ; garder poids, conviction, dates et jets actuels. |
| S1i | Signes, détresse et dangers ont une invalidation subjective unique par propriété | `signes`, `empathie_peur`, `peur_transmise`, `defense`, `secours_acquitte` ; perdre le regard ne dément rien. |
| S1j | Paroles, audiences, savoir initial et identité vocale passent par des vues sourcées | `deja_dit`, `parole_commune`, `social`, `voix`, `voix_inconnues`, `noms`, `garde_ouidire` ; saturation, imposture et témoin absent. |
| S1k | Les refus et recours ne se réarment que par leurs prédicats historiques | `refus_retenus`, `proposer_recours`, `rendre_service`, `refus_leve_contrepartie`, `offre_sensee` ; baisse de moyens/temps seul sans effet. |
| S1l | La recherche d’une personne conserve ensemble négatifs et indices consommés | `appels_restes`, `appel_negocie`, `contact_sous_but` ; persistance malgré 40 événements et absence répétée. |
| S1m | Renoncements et efforts bornés sont publiés seulement au choix réussi | `reessai_obstacle`, `attente_bornee` ; signatures de recours et frontières de publication. |
| S1n | Les suivis relationnels ont une preuve stable et une seule projection de décision | `relations_graduees`, `agendas_evenement`, `constater_soupcon`, tests de 372 ; mêmes axes, ancrages, effets complémentaires. |
| S1o | Aides, rendez-vous et connaissances de contrat sont des vues référencées, sans déplacer l’autorité d’`agendas` | `gardien_detresse` et familles aide/appel/mandat/date ; clôture mécanique distante sans connaissance automatique. |
| S1p | Nouveau conteneur versionné, trois couches + registre et index reconstruits sans perte de l’état historique | Aller-retour complet de sauvegarde, AST final, absence de stock brut renvoyé ; aucun lecteur nouveau du dossier. |

Les noms de familles ci-dessus sont abrégés ; l’annexe mesurée donne les chemins existants.
Un brief S1 doit résoudre ces chemins et figer sa base. Les grands groupes (notamment S1f–i,
576 accès bruts à `croyances` dans jeu/tests/outils, homonymes compris) se subdivisent encore
par producteur/consommateur si leur diff ne tient pas en 30–45 minutes ; aucun lot de centaines
d’accès n’est présumé petit. L’ordre de mise en œuvre permet un inventaire AST décroissant.

**Vérification de chaque lot S1.** Tests touchés et voisins, cas historique réel de la famille
et autre cas de même nature, état complet + rendu/scène + paroles après recharge, même laps
entier/découpé ; `VERIFIER` court si la signature du plan change. Empreintes 2 h, quatre graines,
scénarios touchés et Relais, référence `main` en cache sans rejeu disponible. À base d’intégration
divergente, comparaison complémentaire à la base exacte pour attribuer les écarts. Pas de Luna
si aucun contrat du MJ n’a changé ; pas de suite complète dans ces lots.

S1a–o gardent les clés sauvegardées actuelles : égalité brute possible. S1p change le schéma :
ne pas annoncer une égalité byte à byte. Comparer **toutes** les données par une transformation
de schéma réversible, versionnée et testée (`export_historique(import_historique(data)) == data`),
ainsi que choix, chroniques, métriques et texte exacts ; toute valeur nouvelle doit être
reconstructible. Aucune exclusion arbitraire de registres ou réancrage de hash pour faire passer
le lot. Si la transformation n’est pas prouvée, garder le stockage historique et déclarer S1p ouvert.

**Frontière avec S2.** S1 fournit des vues et la structure du dossier, pas de compensation de tort,
trahison, repentir, valeurs estimées actives ni nouvel oubli. Après S1, trois bascules sont
des lots de comportement distincts : rétention âge/importance ; révision commune des faits ;
compte subjectif/dossier puis axes qui en dérivent. Elles se placent dans la préparation et les
sous-lots de S2, avant E7 et l’essai E9 autorisés. La séparation colère/grief y a son propre lot.
Chaque bascule demande banc rapide 4 h et oracles lisibles, pas des empreintes identiques promises.
Si le superviseur veut limiter S2 au seul compte, donner des numéros intermédiaires à ces bascules,
sans les glisser dans S1.

**Coût.** Index par observateur/type/entité/obligation ; requêtes spécialisées évitant une copie
du journal entier dans chaque nœud GOAP ; signatures calculées une fois par choix comme les
entrées communes actuelles. Pas de recalcul intégral du dossier à chaque lecture d’axe. Mesurer
nombre d’épisodes/faits/dits, octets sauvegardés, lectures/index touchés par choix, CPU et reprises
de recherche ; comparer le CPU seulement sous même charge, jamais aux secondes du cache. S0
n’a mesuré que les accès de source, aucune accélération ni borne mémoire n’est démontrée.

## 6. Interfaces avec les lots voisins

**374, position comme hypothèse datée.** Elle vit dans le fait `lieu` de l’observateur, avec
date/source/confiance d’observation et indice d’immobilité **cru**. Une vue calcule à la lecture
la validité pour trouver une cible ou éviter son regard. Le seuil déclenche une vérification
existante, pas un oubli de l’identité ni une absence certaine. Départage entre statut « périmé »,
« démenti » et « inconnu » ; revoir, voix reconnue ou ouï-dire réellement daté révisent l’hypothèse
selon le contrat de 374. Relayer la même nouvelle ne rajeunit pas sa preuve. Sa signature intègre
les classes de validité et les croyances qui déterminent la vitesse, sans horloge brute. Les
recherches vaines et indices consommés restent valides tant qu’aucun contenu nouveau ne les lève.
S1 doit porter la forme effectivement livrée, sans coder une seconde formule ni l’appliquer
aux objets/feux. Le brief 374 parle de décroissance de confiance : ce choix reste celui du lot,
distinct de la rétention racontable des épisodes.

**372, soupçon déduit.** Le code de cette base est celui du 267 : indice faillible dans
`indices_soupcon`, perte relationnelle réversible, aucun projet de récupération sur le seul
soupçon. Le brief 372 demande plusieurs suspects pondérés et une ouverture possible du projet.
La vue cible porte observation initiale, constat négatif, intervalle complet/incomplet,
candidats connus, indices, conviction, preuve et cause de révision. Elle ne crée jamais un
`lieu.possession.porteur` à partir d’un suspect. Une preuve plus forte peut requalifier la cause
sans refaire la peine. Après livraison de 372, actualiser l’inventaire du registre et la table
`agendas.NAISSANCES` ; la présente note ne certifie pas son schéma final.

**Colère/grief.** `signes.emotions` garde la colère aiguë (actuellement demi-vie 15 min), avec
ancre/cible/intensité. Le grief cible vit dans le dossier et change par événement seulement
pendant la nuit ; le temps ne le compense pas. `relations.en_veut` devra annoncer quel signal
il projette et garder ses bandes, tandis que la colère module les signes et la réaction immédiate.
Ne pas recopier l’axe `rancune` courant dans deux champs et les sommer : ce serait compter deux
fois le même tort. En S1, conserver le calcul historique ; lors de la bascule, liens initiaux,
preuves de tort et colère connue alimentent séparément les deux états. Sans événements anciens
suffisants, conserver une origine « héritée, détail inconnu », sans inventer un passé.

**A1, projection publique (346).** `projection_publique.projeter` n’est pas encore branché au MJ.
Il exclut les états mentaux/savoirs privés et refuse les nouveaux champs mixtes sans provenance.
Le nouveau stockage ne doit donc pas être passé comme un dictionnaire à Luna. Les producteurs
publics donnent seulement connaissances et paroles de Corvus, dates, preuve et désignation
permise. Les dossiers PNJ restent privés. Un futur paquet de formulation contrôlé peut contenir
une parole que le PNJ a décidé de dire ; il ne rejoint pas l’entrée publique du compilateur.
Le § 9 du plan social envisage des secrets dans une formulation : cela requiert un consommateur
séparé et un contrat propre lors de S7/S8, sans assouplir A1 ni les contrôles actuels du MJ en S1.
Une mention de personne dans une parole n’établit ni présence ni vérité. Pour chaque nouveau
champ public, provenance atomique et validation de couverture A1 sont à porter dans le même lot.

## 7. Origine des contrats et limites à conserver

Les rapports lus en complément des plans sont :
[3b](taches/rapport-codex-6-relations-3b.md) (preuves, portages, suites et compagnie),
[3c](taches/rapport-codex-11-relations-3c.md) (émotions et lectures),
[A1 agendas](taches/rapport-codex-24-a1-socle.md) (accès et AST),
[37](taches/rapport-codex-37-chercher-appeler.md) et [69](taches/rapport-codex-69-appels-restes.md)
(recherches/indices), [43](taches/rapport-codex-43-gardien-detresse.md) (secours/aides),
[55](taches/rapport-codex-55-constats-partages.md) et [191](taches/rapport-codex-191-deja-entendu.md)
(audiences), [64](taches/rapport-codex-64-deja-dit.md) (registre durable des dits),
[57](taches/rapport-codex-57-offre-sensee.md) (refus/offres),
[87](taches/rapport-codex-87-borne-attente.md) (efforts bornés),
[223](taches/rapport-codex-223-secours-acquitte.md),
[225](taches/rapport-codex-225-reessai-obstacle.md) et
[239](taches/rapport-codex-239-renonce-attente.md) (acquittement et renoncements),
[224](taches/rapport-codex-224-service-non-defait.md) et
[232](taches/rapport-codex-232-purete-candidats.md) (services et publication au choix),
[267](taches/rapport-codex-267-soupcon-deduit.md),
[320](taches/rapport-codex-320-g15-emissions.md) et
[345](taches/rapport-codex-345-g16-information-parlee.md) (émissions et contenu moteur),
[337](taches/rapport-codex-337-fin-garde-ouidire.md),
[346](taches/rapport-codex-346-a1-provenance-publique.md),
[348](taches/rapport-codex-348-e1-reference-temporelle.md),
[350](taches/rapport-codex-350-e2-realisation-datee.md),
[352](taches/rapport-codex-352-e3-delai-cru.md),
[355](taches/rapport-codex-355-e4-accord-date.md),
[357](taches/rapport-codex-357-e3-taches-payees.md) et
[appel négocié](taches/rapport-appel-negocie.md). Recherche ciblée seulement dans l’historique.

Limites présentes à ne pas déclarer corrigées par un renommage : fenêtre 40 encore mécanique ;
registre des dits saturé à 512 sans éviction ; `_sait` peut encore consulter le savoir de l’auditeur
(limite du 191) ; observations anciennes sans droits/date/désignation irrécupérables ; joueur
sans adoption subjective générale ni relations ; comportement historique des tâches sans limite
du 357 distinct de la voie datée ; aucune certitude de culpabilité depuis une présence. Le rapport
249 sur les confidences perdues rappelle qu’une information peut être utile **plus tard**, pas
seulement changer le prochain but : ne pas purger les faits selon ce seul critère immédiat.

## 8. Questions restantes, avec recommandation

1. **À la bascule, combien retenir et combien raconter ?** Recommandation : conserver toute la nuit
   les résumés de torts, échanges, secrets et paroles à conséquence, et indexer les routines selon
   âge/importance ; borner séparément le nombre de textes présentés à Luna. Ne pas garder le plafond
   40 comme limite cognitive ni supprimer les preuves actives pour limiter la sauvegarde. Calibrer
   les durées des routines au premier lot de comportement, sur coût et lisibilité mesurés.
2. **Sauvegardes antérieures à la mémoire unifiée : continuité ou parties neuves pour les nouvelles
   attitudes ?** Recommandation : S1 sait relire à l’identique ; S2 conserve un état hérité explicite
   pour les liens/attitudes dont les actes ont disparu. Une partie neuve sert à valider réparation,
   trahison et repentir ; ne pas annoncer une reconstruction du passé d’une vieille sauvegarde.
3. **Compenser un tort : explicitement rattaché ou simplement un service ultérieur ?** Recommandation :
   une restitution/réparation compense le tort identifié ; un service sans lien crée du meilleur et
   une éventuelle dette morale mais n’efface pas automatiquement un vol. Les actes répétés peuvent
   ensuite faire réviser un trait cru. Les créances matérielles suivent toujours leurs propres actes.
4. **Deux ouï-dire de force égale et incompatibles : suspendre ou trancher ?** Recommandation : garder
   une incertitude racontable et chercher une preuve si l’action l’exige. Les tirages actuels restent
   en S1 ; la règle cible de contradiction est branchée dans un lot de comportement explicite.
5. **Lecture d’un grief durable dans les refus existants ?** Recommandation : l’attitude durable
   alimente la bande relationnelle de refus ; la colère aiguë module expression et urgence. Garder
   les signatures et l’hystérésis, puis mesurer cette nouvelle politique dans le lot de séparation.

Ces questions portent sur les paramètres et contrats encore ouverts. Elles ne bloquent pas la
livraison documentaire S0 ; elles doivent figurer dans les briefs de bascule concernés.

## Annexe A — Toutes les questions posées à la mémoire des événements

Convention : **M40** = uniquement les quarante souvenirs survivants, même sans filtre temporel.
Les lignes sont les expressions mesurées ; les alias ensuite parcourus/modifiés sont inclus
dans la description. Les fichiers de tests sont dans `tests/`, préfixe `test_` et suffixe `.py`
omis ici ; l’annexe des accès livre les méthodes exactes qui touchent le stock. Les autres
fichiers cités exercent le contrat indirectement ; aucune exécution n’est revendiquée.

| Fonction et ligne(s), sous `donjon/` | Types / question / fenêtre actuelle | Tests concernés |
|---|---|---|
| `biens.prets_reclames:656` | `pret_reclame` du même objet et de la même date de prêt, échu, non jugé, ≥30 min depuis réclamation ; marque `juge`. M40 | `echanges_suite`, `reclamations_repetees` |
| `causes.connues:36` | `bruit` inconnu non résolu, même salle si proche ; plus récent d’abord, M40 sans délai propre | `demander_cause`, `peur_transmise` |
| `causes.recevoir:98` | `bruit` de cette salle de date ≥ nouvelle reçue : empêche doublon ; M40 | `demander_cause` |
| `defense.approche_vue:109,113` | dernier `approche_charge` pour auteur/objet/lieu/cible puis `mise_en_garde` de sa preuve ; M40, pas de réveil par 30 min | `interposition`, `interposition_lieu` |
| `defense.interposition:169,176` | même approche à la case actuelle et avertissement associé ; M40 | `interposition`, `garde_pret` |
| `defense.avertir_acces:224` | `mise_en_garde` déjà émise pour cette preuve ? M40, inscrit avant mots | `interposition`, `interposition_lieu` |
| `defense.souvenirs:241` | expose la mémoire entière pour PNJ ; joueur : `violences_joueur`, lu par `auteurs`/`constater_fin` (<30 min et non clos) | `defense`, `combat`, `secours_acquitte` |
| `defense.protection:414,423` | joueur : qui a un `secours` ; puis dernier secours de chaque protégé non examiné, <30 min. M40 ; auteurs dangereux lus séparément en croyances | `protection`, `agendas_proteger`, `secours_acquitte` |
| `deliberation.consommer_indices_recherche:621` | `bruit/examen` de salle à consommer lors d’un échec ; M40 sans délai | `appels_restes`, `contact_sous_but` |
| `deliberation.promesse_en_cours:785,795` | dernier `promis` non clos par `promesse_annulee/creance/nourri`, réception `recu` de sa part ; <60 min, ou feu revu vif depuis la promesse. Ordre inverse M40 | `promesses`, `lampes_parts`, `tache_promise_recours` |
| `deliberation.detresses_percues:903` | `detresse` de la minute courante seulement, en complément des signes | `empathie_peur`, `peur_transmise` |
| `deliberation.bruit_a_voir:1081` | `bruit` non résolu ; garde/courage, priorité au lieu déjà visé ; bruit habituel ignoré si visite ≤15 min ; M40 | `ouie`, `ouie_commune`, `securite` |
| `deliberation.alarme:1104` | `bruit` non résolu : appel d’un protégé ou niveau ≥ seuil ; M40, aucun délai propre | `protection`, `ouie_commune`, `agendas_proteger` |
| `deliberation._plan_prevenir:1144` | `a_prevenir` pour victime encore connue, avec contenu restant à dire et route ; M40 | `signalements`, `social` |
| `deliberation._lieux_a_dire:1166` | `vu_agir` de l’auteur ayant déplacé un bien de la victime ; M40 ; localisation actuelle **crue** pour le message | `signalements`, `constater_rumeurs` |
| `deliberation.ouvert_par_soi:1487` | `ouvert_par_soi` même objet depuis ≤ paramètre `depuis` ; M40 | `planification`, `entretenir`, `service_non_defait` |
| `deliberation.tache_payee:1572` | dernier `tache_payee` même condition ; ≤240 min, prestataire non suspect ; aucune `creance` de tâche postérieure envers lui ; ordre relatif dans M40 | `taches_payees`, `tache_promise_recours`, `realisation_datee` |
| `deliberation._candidats:2061` | existe-t-il un `a_prevenir` ? M40 ; ouvre le candidat sans certifier un plan | `echelle_choix`, `signalements` |
| `deliberation.choisir:2396` | `engagement_tenu` même condition depuis l’intention ; M40 ; clôture/restauration de charges suspendues | `installation_gardee`, `contrat_engagement`, `service_non_defait` |
| `deliberation.menager_flamme:2532` | ensemble des objets `flamme_employee` ; M40 sans délai ; protection des services payés lue séparément | `service_non_defait`, `lumiere`, `garde_pret` |
| `echanges.affirmer:645` | `mensonge_decouvert` du sujet dans **les trois derniers** souvenirs après perception ; M40[-3:] | `paroles`, `avis_joueur`, `voix_inconnues` |
| `echanges.tenu:1311` | dernier `suivi_engagement` même condition/depuis ; arrêt à `engagement_pris/tenu/abandonne` correspondant. M40 ; sinon mémorise une nouvelle référence initiale | `contrat_engagement`, `taches_payees`, `engagement_deplacement` |
| `esprits.installer:189,192,202,212` | retire `presence_percue` vers indices ; migre `appel_sans_reponse` seulement sans registre ; dernier `appel` reconstitue secours si absent. M40 déjà disponible, pas de passé reconstruit | `esprits`, `appels_restes`, `constater_soupcon`, `temps_etat` |
| `esprits.verifier:369,486,488` | types/listes/date ; plafond 40, joueur et PNJ ; pas de schéma exhaustif de chaque type d’événement | `esprits`, `temps_etat`, tests de corruption des voisins |
| `esprits.memoriser:722` | écrit tous types, copie/date/preuve, éviction 40 puis crochets ; réentrance possible | `esprits`, `relations_graduees`, `defense` |
| `esprits.dernier_son:843` | dernier `bruit` par ordre dans M40 ; pas de filtre d’âge supplémentaire | `ouie`, `ouie_commune`, `paroles` |
| `esprits.prete:1135` | a-t-il un souvenir `pret` objet/destinataire ? M40 sans délai ; distinct du prêt réel dans permissions | `echanges_argent`, `echanges_suite` |
| `ouie.source:592` | dernier `bruit` non résolu de salle avec case connue ; M40 | `ouie_commune`, `appels_restes` |
| `ouie.parcouru:609` | retire bruits de salle et ancien examen s’il reste des sons attendus ; crée `examen` maximal ; M40 | `ouie_commune`, `ouie_temoins`, `appels_restes` |
| `ouie.couvert:631` | dernier `examen` même salle ≤30 min, son pas plus fort, même voix, pas mieux situé ; M40 ; son couvert rafraîchit sa minute | `ouie_commune`, `appels_restes` |
| `ouie._retenir_seulement:647` | remplace `bruit` de salle par maximum nature/niveau, personnage sans profil ; M40 | `ouie`, `ouie_commune` |
| `ouie._bruit_inconnu:671` | sons de salle encore attendus, maximum/voix/case ; suppression puis nouveau `bruit` ; M40, examen couvert séparé | `ouie_commune`, `appels_restes`, `demander_cause` |
| `paroles.paroles_retenues:458` | **quatre dernières** `parole` dont toutes les références sont connues de Corvus ; voix inconnue conservée anonyme ; M40 | `parole_commune`, `parole_voix`, `audience`, `voix_inconnues` |
| `passage._demande:286` | dernier `passage_demande` à l’autre depuis <120 min ; calcule temps fin écoulé depuis `instant` | `passage`, `temps_etat` |
| `passage.a_pousse:536` | `a_pousse` cette victime depuis <120 min ; M40 | `passage`, `corps`, `combat` |
| `planification.Vue.__init__:494` | `tache_payee` encore valide via `tache_payee`, condition/qui/échéance et dépassement ; M40 | `taches_payees`, `planification`, `tache_promise_recours` |
| `planification._entrees_communes:2256` | `promis/nourri/recu/promesse_annulee/creance` + âge<60 et feu constaté depuis ; signe exactement les lectures du plan | `planification`, `promesses`, `tache_promise_recours` |
| `planification.reagir:3959` | acquitte `secours` non examiné si appelant vu ou état vu strictement après ; aucune confusion vue/cri dans même minute ; M40 | `secours_acquitte`, `defense`, `protection` |
| `pnj._temoins_a_l_oreille:427` | dernier `entendu_agir` même opération/objet/minute ; évite doublon acoustique | `ouie_temoins`, `ouie_commune` |
| `pnj._executer_effet:940` | `secours` non examiné dans salle effectivement inspectée, intention protéger ; marque `examine` | `secours_acquitte`, `protection` |
| `pnj._executer_effet:966` | `compagnie` même cible/portée, minute ≥ début d’intention ; une annonce par intention | `empathie`, `empathie_peur`, `suivi_vocal` |
| `pnj._chauffer:1182` | `se_chauffe` depuis l’intention ; évite annonce répétée ; M40 | `entretenir`, `besoins`, `temps_etat` |
| `pnj._abriter:1205` | `abrite` depuis l’intention ; évite annonce répétée ; M40 | `securite`, `repli_et_appel`, `temps_etat` |
| `relations.chance_demande:299` | `don/engagement_tenu` envers l’autre et `se_sait_vu` par lui, depuis <120 min ; réciprocité/risque | `relations_lectures`, `propositions`, `contreparties` |
| `relations.souvenir:578` | chez bénéficiaire, `nourri/recu` même auteur/objet/minute : conséquence tenue apprise directement, sinon `suites` | `relations_graduees`, `promesses`, `don` |
| `relations.souvenir:590` | `a_prevenir` victime/auteur, pas encore `tenu` ; avertissement identifié acquitte une fois et produit `prevenu` | `relations_graduees`, `signalements` |
| `signes.retenir_detresses:575` | `detresse` de la minute courante fournit preuve d’appel ; révision de la croyance séparée | `empathie_peur`, `peur_transmise` |
| `signes.percevoir_tous:881` | existe-t-il `detresse` de la minute ? déclenche le traitement même sans expression courante | `empathie_peur`, `signes` |
| `social.migrer_dits:274` | `dit` avec valeur, types NOUVELLES et `rumeur`, destinataires survivants ; reprise ancien `confie` des croyances | `deja_dit`, `social`, `garde_ouidire` |
| `social._nouvelles:351` | NOUVELLES ou rumeur rang<2, encore crues ; ordre ancien→récent M40 après constats/avis | `social`, `constater_rumeurs`, `deja_dit`, `garde_ouidire` |
| `social._sait:480` | même identité/valeur dans NOUVELLES ou événement de rumeur ; M40 de l’auditeur ; limite subjective du 191 | `social`, `deja_dit`, `constater_rumeurs` |
| `recit_pnj.Recit._noter:190` | tous sauf `son`, date ≥ dernier relevé et JSON non vu ; fenêtre M40, déduplication de l’observateur à une minute | `recit_pnj`, `banc_pnj` |
| `rejeu.Enregistreur._penser:153` | `bruit` des salles retenues, plus fort niveau, pour la piste d’esprit ; M40 | `rejeu` |
| `banc_pnj.issue:110` | `vu_agir` opération prendre : couples auteur/objet distincts ; M40 final | `banc_pnj` |
| `banc_pnj._executer:254,259,261,370` | compte tous types finaux ; témoins `vu_agir` vue/ouïe et `entendu_agir` ; somme prix `vente` ; M40, pas compte exhaustif de nuit | `banc_pnj`, `recit_pnj` |
| `banc_pnj.nuit:547`, `main:743` | export de tous souvenirs survivants, M40 | `banc_pnj`, lecteurs d’archives listés dans l’annexe |

NOUVELLES vaut exactement : `vu_agir`, `vol_surpris`, `vu_porter`, `mensonge_decouvert`,
`mensonge_dementi`, `absence`, `dette_niee`, `pret_garde`, `mort_vue`, `intention_lue`.
Les crochets `relations.souvenir` et `defense.retenir` reçoivent aussi l’événement neuf en
argument : ce sont des consommateurs de **tous types admissibles**, même lorsqu’ils ne relisent
pas la liste. Leur table d’épreuves et leur routage ne sont pas à remplacer par une liste
fermée d’exemples. Le relevé des types ci-dessus est celui des requêtes, pas un décompte
arbitraire des dictionnaires contenant la clé générique `type` dans le dépôt.

## Annexe B — Registres subjectifs : clés, cycle, validation et vues

Abréviations : E = `esprits.verifier`, R = `relations.verifier`, V = `voix.verifier_entrees`/
`verifier_echange`, A = `agendas.verifier` (avec vérification des références temporelles),
P = `pnj_propositions.verifier`. Ils sont appelés à la validation du monde/rechargement.
Les lecteurs exhaustifs et les lignes exactes sont dans l’annexe des accès ; les principaux
producteurs, effacements et consommateurs sont nommés ici pour rendre la migration praticable.

| Registre et clé/valeur actuelle | Écriture, invalidation/effacement actuels ; validation | Vue cible et dépendance de recherche |
|---|---|---|
| `faits_dits[identite_json]` : valeur, `dit_a[a]=valeur`, `entendu_a[a]=[valeurs]`, valeur inconnue | `social.retenir_dit/_retenir_audience/reviser_dits` ; changement appris rouvre des valeurs, aucune purge à 40 ; maximum 512, nouveaux faits tus à saturation ; E | `transmissions` du registre des paroles, sans confondre audience réelle et audience connue. H, social/signalisations. |
| `faits_initiaux[identite_json]=valeur` | `installer_faits_initiaux`, puis `reviser_dits` retire ce qui change ; pas de réinjection d’inventaire réel à la recharge ; E | `origine_initiale` de faits. Invalidation par changement appris, pas nouvelle date ; H. |
| `derniere_confidence` : minute ou None | `social.bavarder`, une confidence par minute ; valeur remplacée au prochain événement ; E | vue du dernier acte de confidence, invalidation par changement de minute seulement pour le droit de reparler ; H. |
| `refus` : liste de demandes `(de,operation,objet,besoin,mandat)` avec raison, minute, cause/offre/repère/contre-offre | `retenir_refus`, remplacement par `oublier_refus`, levée par accord/service (`services.lever_refus`) ; `tient` : moyens nouveaux, meilleure offre, repère/localisation, ou délai historique 120 min selon cause ; E | `reponses_retenues`, politiques déclarées `tient/refus_tient` conservées. D par `v.refus_tenus`, I par chances/moyens ; contrôle aussi à l’exécution. |
| `recherches[qui][salle]=minute` | `recherche_vaine` ; `contact_recherche/indice_recherche` retire le seul lieu rouvert ; retrouvailles nettoient via appel ; aucune échéance de temps ; migration seulement sans registre ; E | `lieux_ecartes` : invalidation par contenu positif nouveau local, jamais absence/répétition ; D via `appels_vains`. |
| `indices_recherche[qui][salle]=[indice]` | `_retenir_indice`, `consommer_indices_recherche` ; signature présence(force,case)/bruit(intensité,voix,case), sans date/confiance/relais ; conserve les indices consommés ; E | `indices_consommes` ; nouveauté sémantique seule réouvre ; I par recherches et moyens/refus. |
| `presence_recherche[qui]=[salle,case]` | `_situer_recherche` lors d’un positif ; garde dernière présence malgré l’absence, remplace sur nouvelle localisation ; E | `dernier_positif_recherche`, invalidé/remplacé par positif distinct ; I via admission d’indice, pas clé brute. |
| `secours` : `{minute,apaise}` ou None | `appeler_a_l_aide`, migration dernier `appel` si absent ; apaisement réarme l’épisode propre ; E | `appel_personnel` ; validité selon apaisement et seuils, pas taille du récit. H ; ne pas confondre avec épisode `secours` d’un protégé. |
| `detresses_appelees` : liste de besoins | `appeler_a_l_aide` ajoute besoin bloqué, retire ceux apaisés ; E | `episodes_appel_besoin` : réarmement après apaisement, pas délai ni oubli ; H. |
| `aides_attendues[objet]={qui,condition,minute,echeance?}` | `echanges._retenir_aide`, retrait annoncé (`retenir_abandon`) ou constat `agendas.clore_aides_constatees` ; vues filtrent méfiance/refus/240 min et échéance explicite ; E+A pour référence métier | `aide_connue` : réception/constat/abandon entendu ou échéance, aucune lecture de l’engagement privé de l’aidant ; I dans `v.aides`, suivi des délégations. |
| `attentes_bornees[cle_recours]=signature` | `planification.vues_du_choix` publie seulement après choix ; changement d’entrées utiles/paliers réouvre, prix continus seuls non ; E | `effort_sans_plan` ; même signature = attente, pas preuve d’impossibilité. H autour de la recherche, pas réinjecté dans sa propre clé. |
| `renoncements[motif]` : entier ancien ou liste `{instant,but,cause}` | `deliberation.renoncer`, choix/évaluation consultent le juge d’obstacle ; nouvelle cause reste distincte ; témoin/passage/corps/contact levé par constat ou autre moyen, jamais par délai ; E | `obstacles_retenus`, cause et moyen référencés, sans effacer un autre obstacle. H choix et `pnj.refus_etape` ; dépendances du juge à conserver. |
| `donne[objet][attribut]=[valeur,minute]` | `changer_etat` retient geste propre ; purge ≥5 min à l’écriture suivante ; retire état défait vu, crée refus `oppose` ; E | `dernier_geste_propre` ; horizon 5 min et contradiction constatée. H ; refus dérivé D/I. |
| `preuves_relations[autre:preuve]={niveau,effets}` | `relations._appliquer/eprouver_mandat` ; niveau .4/.5/.8/1 ; applique seulement complément, pas de purge courante ; R | `jugements_appliques` : marqueur durable même si épisode oublié, renforcement/compensation explicites ; I par axes et `portage_connu`, pas tout le journal dans la clé. |
| `portages[objet]={auteur,preuve}` | `relations.souvenir`, `oublier_portage` sur constat propre/retour ; distingue nouveau tort d’un regard répété ; R | `possession_illegitime_connue`, invalidation par preuve de retour/changement ; I pour naissance d’agenda, pas registre brut dans `_entrees`. |
| `suites` : conséquences `{type,de,pour,condition,minute,preuve}` | `relations.souvenir` diffère la conséquence ; `annoncer_suites` la dit au contact entendu, retire après annonce ; R | `annonces_dues`, invalidation par annonce effective à celui qui doit l’apprendre ; H, pas savoir à distance. |
| `compagnie[autre]` : minutes 0..59 ; `compagnie_minute` | `relations.partager` une fois par minute perçue ; accumule l’heure commune puis épreuve ; garde le reliquat ; R | `temps_epreuve_partagee`, accumulateur daté sauvegardé ; I par axes et sécurité, jamais nombre de lectures. |
| `visites[salle]=minute` | `depart.installer`, `pnj._inspecter` ; actualisation au parcours effectif, pas purge globale ; E | `dernier_examen_lieu` ; ordre relatif suffit au parcours, horizon de 15 min pour bruit habituel reste séparé ; D `_ordre_visites`, I aide/délégation. |
| `voix` : liste d’identités reconnues | `voix.connaitre`, scénario initial via `esprits.installer` ; ajout durable sans oubli courant ; E | `voix_reconnues`, preuve de reconnaissance/savoir, survit au départ ; C proximité vocale/I par identité, pas export des signatures réelles. |
| `noms` : liste d’identités nommées | `noms.apprendre`, `voix.apprendre_nom/lier` ; durable, pas de purge à 40 ; E | `noms_reconnus` ; un nom prétendu reste séparé, nouveau lien d’identité peut démentir une prétention ; H/C identité. |
| `voix_entendues[signature]={minute,se_dit,mefiance,n,appelee?}` | `voix.retenir/nommer/se_nommer/se_mefier/connaitre` ; max 24, éviction anciennement entendue puis n ; reconnaissance transfère/retire ou dément la prétention ; V+E | `identites_vocales_crues` ; mêmes règles pendant S1, cible distingue trace durable de mensonge et voix oubliable ; I/C via identité/relations/proximité. |
| `echange` : paroles nettes récentes | `voix.retenir_echange/lier` ; garde ≤8 paroles dans les 600 dixièmes (1 minute) précédant la nouvelle parole, pas toute l’histoire ; V+E | `contexte_echange` calculé depuis auditions admises selon cette fenêtre ; H, les mots entendus restent dans le registre séparé. |
| `rejoint` : qui attend, délai, promesse ; `rejoindre` : à qui venir | `appel.attendre/venir/dire`, `tenir/rompre_attente` ; fin sur contact réel/retrouvailles, départ/rupture ou échéance commune ; `appel.verifier` via E | `rendez_vous_connu` à deux engagements subjectifs référencés, sans synchronisation omnisciente. H candidats/attente ; C selon recours/projection. |
| `indices_soupcon.presences/gestes` : listes datées ; `constats[objet][champ]` ; `soupcons[preuve]` ; `oublis[salle]` | `esprits._retenir_presence/_constater_bien/memoriser/_purger_indices_soupcon`, `relations.deduire_soupcon/reviser_soupcons` ; max 40 présences et 40 gestes ; dates à grain minute stockées en dixièmes, ordre canonique ; retour/réparation/auteur appris lèvent l’indice ; E+R | `indices_attribution` et `soupcons_crus` séparés. Marque d’intervalle tronqué interdit attribution, perte effectivement appliquée seule compensée. I via axes, H naissance ; **372 à raccorder**. |
| `demande_refusee` : `{de,besoin,objet}` ou None | `retenir_refus`, `choisir`, `pnj_propositions.executer` ; déclencheur remplacé/effacé quand pris en charge ou plus pertinent ; P | `recours_ouvert`, invalidation par traitement/contexte déclaré ; H après choix, jamais preuve nouvelle de refus. |
| `recours_propositions` : cible/besoin, cause, lien, pièces, biens | `pnj_propositions.executer` remplace tentative même cible/besoin ; `recours/_tient` permet nouveau moyen/relation améliorée/contrepartie ; P | `offres_essayees`, invalidation par amélioration admissible, pas perte de moyens/date seule ; H après recherche. |
| `recours_services` : `(de,besoin,objet,operation,minute)` | `rendre_service` inscrit tentative/remplace selon cible ; `plan_recours` poursuit/restaure ses brouillons ; P | `services_essayes`, identité de demande et raison retenue, pas éviction par mémoire ; H. |
| `service_en_cours` : demande + condition | `rendre_service`, `plan_recours` ; retire quand satisfaite ou raison/plan plus admissible selon contrôle existant ; P | `service_adopte`, obligation opérationnelle référencée au fait de demande ; H ; les faits appris survivent à la fin du plan. |
| `recours_intermediaires` : de/besoin/objet/opération/minute/via/issue/livraison/abouti | `devis_intermediaire/plan_recours`, `executer`, `agendas.affecter_part/tenir` ; échec/nouvelle issue conservés, une tentative identique ne renaît pas ; P | `intermediations_connues` ; clôture par refus/livraison effectivement apprise ; H, métrique de banc distincte. |
| `regards_suivis[signe]=[episode,direction]` | `signes.regard_a_suivre/suivre_regard` ; remplace si épisode physique ou direction perçue change, pas nouvelle minute ; E | `indices_regard_consommes` ; invalidation par nouvel indice physique pertinent ; H. |
| `signes_lus[signe]` : repère du jet déjà tenté | `signes.lire` ; cadence dix minutes et occurrence perçue, échec compris ; défaut dict installé, pas de validation exhaustive de ce dictionnaire trouvée dans `signes.verifier` | `essais_lecture_signe` ; même tirage séparé et sauvegardé, pas de nouveau jet à consultation ; H/C via lectures actives seulement. |

## Annexe C — Registres mécaniques et état courant : ce qui reste hors mémoire

| Registre / clé | Écriture, fin et validation actuelles | Interface mémoire et entrée de recherche |
|---|---|---|
| `relations[autre]`, six axes/bandes/ancrages/motifs | `relations` seul ; estompement affection/rancune/peur/ascendant, confiance/dette durables ; R | S1 projection historique ; S2 projection du dossier, pas second cumul ; D axes/bandes. |
| `emotions[colere]` cible/niveau/depuis | `signes.eprouver`, lecture pure `emotion`, demi-vie 15 min ; `signes.verifier` | Ancre affective courante, épisode causal dans mémoire ; I/C signes. Grief futur dans dossier. |
| `besoins`, `urgences[besoin]={etat,depuis}`, `pulsions` | `deliberation.installer/eveiller/_classer`, corps et constats ; seuils/hystérésis et épisodes pressants ; E | État d’action conservé ; mémoire ne remplace pas faim ou désespoir. I pressions/besoins, H arbitrage/paliers. |
| `intention`, `contrat_intention` facultatif, charges suspendues | choix, `agendas.retenir_intention/clore_intention`, actes PNJ ; changement/fin d’intention, provenance ne vaut que pour but/motif/depuis correspondant ; E+A | Plan et provenance actifs hors dossier ; événements de début/fin appris référencés ; I/C selon gestes, patience/sécurité. |
| `libre`, `veille`, `eveil`, `patience`, `manque`, `en_vue`, `balayage` | ordonnanceur PNJ, corps, perception, `commencer_attente/compter_attente`, `reconsiderer` ; fin de geste/réveil/nouvelle minute/regard ; E et corps | Horloges/état de perception hors mémoire ; `manque` empêche le même échec dans la minute. I patience pour route eau, reste H. Ne pas reconstruire `en_vue` depuis le dernier épisode. |
| `engagements` PNJ, `promesses_joueur` : liste condition/pour/minute/paiement/annulation… | `agendas.prendre/tenir/echoir/retirer_proposition/renouveler/affecter_part/annoncer_abandon` ; réalisation, empêchement, abandon 240 min historique ou limite explicite ; A | Autorité exécutoire conservée dans agendas ; vue mémoire `obligation_connue` par preuve apprise. D/I promesses/aides/travaux, pas lecture brute du registre de l’autre. |
| `reference_temporelle={id,version,creation,limite}`, `sequence_obligations`, `accord_initial` | `agendas.prendre`, E1/E4 ; séquence ne recule pas, pas de date inventée ; A, refus `ErreurMonde.attendu` | Référence stable depuis les faits du dossier ; aucune copie mutable ni recalcul d’une limite. I signatures de contrats actifs/projections. |
| `issues_obligations` : titulaire/engagement/réalisation/verdict/clôture/constatée | `_clore_datee`, expiration à T+1 dixième ; à T réalisation admise, archive non réécrite ; `_constater_issues` apprend selon preuve ; A | Archive **réelle**, vue subjective `issue_connue` seulement sur constat/parole ; H ordonnanceur et I conséquences connues. `journal_promesses` est rendu, jamais preuve autonome. |
| `agendas` facultatif, `agendas_joueur`, `offres_mandat_joueur` | `_stock`, `evaluation`, `actualiser`, `_changer`, plafonnement ; fin irréversible, sommeil sur entrées inchangées, publication après choix ; A | Projet d’action reste dans agendas ; vue `projet_propre` pour soi, `projet_annonce` pour témoin. I/H états/charges sélectionnés. |
| `confies`, `confirme`, `attributions` dans projet ; `mandats_percus` propre à chaque témoin | `confier`, jugements/retraits/comptes perçus, `_actualiser_epreuves` ; retrait annoncé, échéance ou issue apprise ; A | Filiation exécutoire séparée de `mandat_connu` ; D `mandats_percus`, I projets de protection ; ne pas lire le parent secret d’un autre. |
| `engagements[mission]` au niveau **data**, statut/montant/révision de paiement | `agendas.installer_contrats/proposer_contrat/repondre_contrat/payer_contrat` ; A/validation monde | Homonyme des engagements PNJ, contrat de mission réel ; `contrat_mission_connu` par rendu admis, pas source de croyance automatique ; H. |
| `permissions` : objet/a/de/minute | `biens.preter/clore/donner`, remise au propriétaire clôt, don retire prêt ; `biens.verifier` | Droit réel conservé ; mémoire `pret_connu`, photographie de permission du 337 ; I `v.illicite`, capacités, restitution. |
| `finances_pnj[id]`, `joueur.or`, bourses à `pieces` | `biens.payer` transfère, dépense bourse personnelle puis objets portés en ordre stable ; validation du monde et `biens.verifier` pour pièces/prix | Compte matériel autoritaire inchangé ; compte du dossier subjectif, jamais une source de paiement ; I richesse/pièce. |
| `dettes` : liste `{de,a,montant,objet,quoi,minute,a_prevenir?}` | `biens.rembourser` ajoute, `regler/solder/reclamer_dette` diminuent/retirent à zéro ; `a_prevenir` retire la créance des dettes connues jusqu’à réponse locale/remise ; `biens.verifier` | Dette réelle dans biens ; vue `creance_connue` filtre la connaissance actuelle, puis S2 références d’apprentissage explicites ; I `entrees_creance`, refus/réclamations ; aucun registre `creances_connues` séparé inventé. |
| `services_rendus` : liste `{de,pour,condition,lieu_beneficiaire?}` | `biens.retenir_service` inscrit ; `services_proteges` propose une clôture sur état défait ou départ cru selon l’ancrage du bénéficiaire, `clotures_services_du_choix` la publie après choix seulement ; `biens.verifier` | **Fait subjectif de contrôle** actuellement hébergé dans biens, candidat à `resultat_service_connu` dans mémoire. Pas de délai ni maintien continu promis ; D services protégés/I gestes. |
| `restitutions[id][objet]={a,entrees}` | `biens.retenir_restitution`, `restitution_retenue` compare besoins/moyens/pièces/contenu/propriétaire/prix ; remplacement au retour suivant ; `biens.verifier` | Fait de contrôle subjectif `pret_termine`, à terme hébergé dans mémoire ; D via `v.refuse` et I permissions. Délai seul/perte de moyen ne réarme pas. |
| `violences_joueur` | `defense.noter_coup/constater_fin` : par auteur, <30 min ou clos ; aucun validateur structurel spécifique trouvé pour ce stock | Vue de danger joueur, pas relation subjective ni profil autonome ; C `_entrees_defense`. Lacune de validation à fermer au portage. |
| `voix_connues`, `voix_entendues` joueur ; connaissances/noms joueur | `voix`, `noms`, `ecoute` ; mêmes prétentions/24 voix et reconnaissance, validation écoute/voix | Pendant S1 stockage conservé ; vues d’identité communes paramétrées par observateur, exposition publique filtrée ; H/C. |
| `emissions_parole` : flux `id/ordre`, auteur, acte/paramètres/modalité/événement, a/auditeurs, texte/rendu, salle/minute/instant/révision | `emissions.enregistrer/diffuser`, admission avant affichage ; migration `installer` des deux anciens registres, pas de dédoublonnage textuel ni purge courante ; `emissions.verifier` via Monde | Preuve mécanique unique à garder, projections `pnj/joueur/publiques` déjà existantes ; index subjectifs de mémoire référencent cette occurrence. H rendu/compilation, jamais toute l’audience réelle divulguée à un PNJ. `dits` est un paramètre de mots saisis, pas un nouveau stock `data`. |

### Autres suivis de perception à raccorder sans les confondre avec un dossier social

| Registre / clé | Écriture, invalidation et validation mesurées | Destination / lecteurs et entrées |
|---|---|---|
| `occurrences_signes` : actifs, épisodes par signe, paroles et directions | `signes._occurrences` incrémente quand posture réapparaît, regard change ou nouvelle parole ; dates fines physiques conservées ; pas de schéma complet validé dans `signes.verifier` | Source physique d’identité de signe hors mémoire subjective ; `signes.lire/regard_a_suivre` ne donnent que ce qui est perçu. H, I lectures actives. |
| `suivi_signes[observateur]` : version 2, retenus et conclusions par signe | `signes._suivi/lire` ; changement d’épisode permet nouvelle conclusion ; migration ne reconstruit pas histoire physique absente ; validation structurelle incomplète | Vue subjective `conclusions_signes`, invalidée par nouvelle occurrence/conclusion, pas simple lecture ; H/I signes. |
| `signes_lus_joueur`, `lectures[signe]` | `signes.lire`, mêmes essais de dix minutes ; lectures actives 30/120 min selon attribut ; validation actuelle partielle | Vues d’essai et d’interprétation joueur, jamais vérité cachée du signe ; H public. |
| `tirages_lecture`, `tirages_lecture_acteurs[observateur]` | `signes._jet` incrémente, seed indépendante par observateur ; validation du compteur total seulement dans `signes.verifier` | État déterministe des jets conservé hors dossier, aucune remise à zéro à la recharge ; H. |
| `tons_percus` : instant et signe | `signes.entendre_ton` remplace lors d’une parole ; `percus` retient ≤30 dixièmes ; validation générale incomplète | Vue `tons_entendus` depuis auditions, pas humeur secrète ; H. |
| `observations_joueur` (300), `observation_joueur`, `bilan_signes` | `signes.lire` tronque l’historique joueur à 300 ; observation choisie et bilan remplacés à l’action ; pas de validation complète de toutes ces structures | Traces/publication, pas vérité supplémentaire ; conserver leurs filtres et fenêtres dans S1j. H rendu et récit. |
| `mesures_signes` | `signes._compter` cumule les mesures de lecture ; pas de purge comportementale ni lecteur de décision | Instrumentation persistée, ne rentre pas dans les signatures des recherches. H banc. |
| `bruits` (80), `entendus` joueur | `ouie` retient événements acoustiques au dixième, borne 80 ; `ecoute.retenir` ajoute voix nettes durant le geste, moteur réinitialise la fenêtre d’interlocution ; `ecoute.verifier` | Transport sensoriel, pas mémoire de vérités ; `ecoute`, `appel.en_attente`, interlocuteurs ; H. |
| `noms_connus`, `personnes[id]={n,nom}`, `references_personnes[id]=n` | `noms.installer/apprendre` attribuent ordre stable et noms, sans révéler nom réel à la seule vue ; pas d’oubli courant ; `noms.verifier` | Mémoire nominale + tables de désignation publique conservées ; faits d’identité appris dans mémoire, numérotation dans noms. H/C. |
| `personnages_vus`, `souvenirs_personnages[id]`, `souvenirs_visuels[id]` et `souvenirs_portes` | `Monde.identifier/actualiser_souvenirs_personnages`, `spatial.explorer` ; portrait vu proche/éclairé, dernière place vue retirée/revue si champ vide ou objet porté ; validations spatiales/monde existantes | Mémoire perceptive de Corvus, pas dossier privé d’un PNJ. Faits historiques et désignations sourcés pour A1, position actuelle jamais déduite d’un portrait. H ; lectures joueur `scene/tenir/couverture_action`. |
| `faits_vus`, `conversation` | `faits_locaux` inscrit faits admis/perçus, validation dédiée ; `Monde.memoriser` garde 12 échanges, tronque textes selon contrat | Archive d’apprentissage/publication ; conversation sans autorité physique. H contexte, A1 et MJ. |

Les lacunes de validation relevées ne sont pas des garanties fournies par S0. Leur portage
doit introduire un schéma fermé et des sauvegardes corrompues de contre-épreuve, tout en
conservant les états valides. Le resserrement des entrées invalides est annoncé dans le brief.

La table couvre l’état subjectif et les registres sociaux adjacents, pas tous les états physiques
du moteur (combustible réel, eau réelle, corps, géométrie). Ceux-ci restent évidemment dans
`data` et leurs modules. Les fonctions et lignes de chaque clé sont dans l’annexe des accès ;
les signatures internes temporaires des évaluations ne sont pas des registres de sauvegarde.
