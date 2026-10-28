# Lot 249 — confidences perdues : utilité différée et portée du critère

**`codex-confidences-perdues`, non fusionnée**, base `integration 59321b9`,
28 octobre 2026. Diagnostic de `adb52c4` contre `942a3c2` ; aucun code du jeu
ni test modifié. **Recommandation : élargir le critère d’utilité par une reprise
ciblée**, pas fusionner 235 en corrigeant seulement ses tests.

## Inventaire et usage

Les huit nuits de 4 h sont appariées par locuteur, destinataire et contenu,
indépendamment de la minute et du verdict crue/doute/connu. L’inventaire donne
**chaque minute, parole, locuteur et auditeur**, les ajouts et les décisions :
`C:/Users/msics/donjon/artifacts/confidences-249/inventaire.md` et `.json`.

| Famille | Relais, référence → 235 | Mine, référence → 235 | Usage décisionnel dans l’heure suivante |
|---|---:|---:|---|
| Source lumineuse éteinte | 13 → 1 | 51 → 0 | Aucun changement de but/motif/plan établi dans l’heure. |
| Contenant fermé à clé | 3 → 0 | 9 → 0 | Aucun changement de but/motif/plan établi dans l’heure. |
| Ressource épuisée | 3 → 0 | 26 → 4 | **Utile perdue : Josse → Mathe, mine 1985, 141**, biscuits épuisés ; évitement à 191–193. |
| Bien disparu | 3 → 2 | 5 → 2 | Les annonces de référence sont toutes reçues « connu » ; aucun apprentissage direct. |
| Guet / intention lue | 0 → 0 | 10 → 4 | Aucun changement de choix établi ; `_utile` accepte cette famille sur les états témoins. |
| Compte rendu de promesse | 3 → 2 | 0 → 0 | Autre circuit : `relations.annoncer_suites`, pas `bavarder`. |
| **Total du compteur historique** | **25 → 5** | **101 → 10** | Ni avis d’eau ni confidence donnant le lieu d’un bien dans ces 126 lignes. |

Hormis la confidence utile ci-dessous, les constats matériels perdus ne
montrent donc aucun usage décisionnel direct dans ces nuits : leur suppression
est légitime selon ce critère mesuré, sans présumer leur inutilité générale.

La baisse nette de 111 cache **122 occurrences absentes, quatre retrouvées et
onze supplémentaires/réattribuées**. Retrouvées : Relais 7,
Brune → Gorm, torche, 74 → 3 ; Relais 42, Brune → Gorm, parole tenue, 2 → 4,
et Brune → Aubin, vivres disparus, 14 → 185 ; mine 7, Josse → Gaspard,
vivres épuisés, 47 → 14. Une différence de trajectoire n’est pas un refus direct
de `_utile`.

**Preuve d’utilité différée.** Mine 1985, Mathe croit à 141 Josse :
`biscuits_1.etat.disponible=False`. À 191–193 elle n’adopte aucun secours
avec ces biscuits. Sur des copies des mêmes états, rétablir la croyance
précédente produit un plan de demande à Josse pour le nourrir avec
`biscuits_1` : six évaluations, 50–52 minutes après l’annonce. Cet évitement
utile échappe au relevé des seuls buts exécutés et au choix immédiat à réception,
qui reste identique.

## Pourquoi le lien manque

`social._utile(Josse, Mathe, noyau)` vaut faux sur l’état témoin de 141 :
aucune faim visible de Mathe, aucun bien, engagement actif ou intention perçue
ne la relie aux biscuits de Josse. Manque l’**usage d’un moyen pour aider un
tiers, hors engagement actif**. Josse a pourtant retenu les paroles où Mathe
nourrit Rémy à 0–1 et perçoit son attachement envers lui à 141. Ces souvenirs
`parole` gardent texte et identifiants cités, pas le lien fonctionnel typé
nécessaire au critère. Lire la faim future ou le plan privé serait interdit.

Invariant proposé : **un moyen concerne aussi les usages que le locuteur
sait que l’auditeur fournit ou recherche, pour lui-même ou pour autrui ; la
pertinence suit cette preuve d’usage retenue, ses moyens équivalents et leurs
supports crus, jusqu’à son démenti.** Il faut conserver cette preuve par le
contrat commun de perception/parole, puis l’exploiter dans `_utile` ; ni
analyse de formulation, ni exception « nourriture », ni lecture d’une pulsion
privée. Schéma et révision de la preuve restent à concevoir.

## Huit assertions rouges et deux nouveaux suspects

Classement de **l’assertion qui échoue**, à partir des captures et des sources,
sans réancrage ni modification d’oracle ; les assertions ultérieures non
atteintes ne sont pas certifiées.

| Cas du 235 | Verdict et famille |
|---|---|
| `bourse_redemandee`, mine | **Attente périmée** de propriétaire final : Josse achète la paie à Rémy à 298 ; les restitutions de Mathe à 290 et Rémy à 298 existent. Échanges / possession. |
| `completion_preuves`, mine-480 | **Attente d’identité historique périmée** : le contrat social change monde et traces ; le hash seul ne démontre aucun défaut matériel. Constat / chronique. |
| `contrat_engagement`, mine-42 | **Prémisse périmée** : Mathe a nourri Lucien à 1 ; l’adoption historique d’un autre secours par Rémy n’est plus nécessaire. Service à autrui. |
| `eau`, Ilse à 80 | **Attente temporelle périmée** : sortie dans les vannes à 77 puis retour ; `trempe=1,025` ne décrit plus un séjour continu à sécher. Déplacements / avertissement. |
| `etapes_chainees`, mine | **Attente d’identité historique périmée** des visites/plans/monde ; ne justifie pas un remplacement aveugle des empreintes. Constat / chronique. |
| `proposer_recours`, Odon | **Attente trop large** : la contre-offre de Mathe est payée et livrée à 0 ; l’offre rouge concerne ensuite la paie de Bram, après l’échec sombre au coffre. Autre projet, pas rachat du repas. |
| `tache_promise_recours`, feu | **Échéance implicite périmée** : Brune a tenu, Gorm voit le feu ; l’annonce reste dans `Brune.suites` à 5, aucune nouvelle conversation ne l’a transmise. Compte rendu différé. |
| `trainer`, Joss | **Prémisse d’identification périmée** : souvenir `subi.auteur=None`, parole d’Odile doutée ; la victime n’a pas identifié son agresseur. Attribution sociale. |
| Aubin / Ilse, Relais 2024, 195–196 | **Faux positif du détecteur** : après l’échec auprès de Gorm à 117165, Aubin demande à Ilse sa localisation à 117635 ; même but, autre moyen. Service à autrui / enquête. |
| Mireille / Mathurine, auberge 2024, 226 | **Défaut réel d’admission/reprise** : `servir` échoue à 135695, Mathurine étant crue et réellement dans la salle commune, Mireille dans la cuisine ; même plan reproposé à 135725 sans retour de Mathurine. Service à autrui. |

Mireille révèle un contrat commun d’admission du service, distinct du rendez-vous
230 ; aucun lien causal avec une confidence précise n’est établi. Les huit
tests restent rouges : conserver leurs contrats dans des scènes aux prémisses
explicites.

## Mesures et limites

Huit rejeux de capture reproduisent exactement chroniques, empreintes, récits
et souvenirs archivés ; **123 transmissions, zéro choix immédiat différent**.
Huit rejeux de choix puis cinq prolongations jusqu’à 300 min couvrent l’heure
après les annonces tardives : **5 472 ablations locales, six écarts, une annonce
utile** ; leurs chroniques sur les quatre premières heures restent identiques
aux bruts. Deux nuits 235 sondées (trois rejeux) reproduisent chroniques,
empreintes, récits et souvenirs. Trois comptes rendus hors ablation. Un processus à priorité réduite,
aucun Luna, suite complète ou banc de comparaison. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/confidences-249/`.

L’ablation compare but/motif/plan au vrai choix, en retirant sur une copie la
croyance encore attribuable à l’annonce et son souvenir. Elle ne mesure ni
une nuit entière sans cette parole ni ses effets sur les témoins auditifs.
Évaluer le critère sur la référence ne reconstitue pas chaque refus de 235.
**Élargissement à concevoir et vérifier ; aucune garantie générale ni
autorisation de fusion de 235.**
