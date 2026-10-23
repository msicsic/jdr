# Rapport Codex 19 — sous un obstacle, ou par-dessus

Branche `codex-sous-obstacle`, non fusionnée, issue de `main` **276524c** ; tâche portée
par **7a38ad6**. Worktree `tmp-worktrees/codex-sous-obstacle`. Premier commit moteur signé
**c5a622c**. Aucun changement de `main`, aucune connexion ni requête à Luna sur ce poste.

## Règle et contrat commun

Le manque était une géométrie de passage, distincte du volume de matière : une poutre,
une table et un bloc ne donnent pas les mêmes vides autour d'eux. `matiere.PASSAGE` et
`valider_passage` décrivent dessous, sommet, largeur, profondeur, prises et charge supportée.
La qualification `etablir_faits` accepte ce fait une fois, même sur un obstacle d'auteur
sans masse renseignée ; contrôle physique sémantique puis validation numérique avant
enregistrement et affichage. Une propriété déjà établie ne se réécrit pas. Le rendu de
l'examen et la fiche lisent la même donnée persistante.

`obstacles.conditions` fixe pour tous la carrure, la charge et l'encombrement acceptés.
Ramper : 12 s, bruit feutré, sans jet ; enjamber jusqu'à 35 % de la stature : 6 s, bruit de
pas, sans jet ; escalader jusqu'à 80 % de la stature sur prises : 18 s, FOR 10, bruit de
mouvement. Un échec d'escalade dépense le temps et l'effort, sans déplacement. Dessus exige
aussi une charge supportée suffisante. Les limites exactes et les conventions de gabarit
figurent dans `docs/mecaniques.md`.

L'opération nouvelle `passer_obstacle` s'insère dans `composer` : méthodes `dessous` et
`dessus`, outil et destination vides, difficulté 0. Cette opération distingue le passage
local d'une échelle installée ou d'un saut à la perche : ces derniers changent de lieu et
gardent leurs règles existantes. Pas d'alias qui transforme aveuglément un ancien `franchir`
mal typé en passage sous un objet. Le catalogue typé et le dossier `passages_obstacles`
exposent la règle au MJ ; aucun objet ni exemple de phrase n'est testé par le moteur.

Les commandes locales « ramper sous », « passer sous », « passer par-dessus », « enjamber »
et « escalader » reconnaissent une cible nommée exactement. La fiche attend toujours
`tenter`. `commandes.faisabilite` conserve la question comme préparation sans action. Tous
les refus propres au passage portent le champ, la valeur reçue et l'acceptation en
identifiants ; ces données ne sont pas affichées au joueur.

## Trajets, croyances, temps et perception

`obstacles.transitions` fournit les arêtes supplémentaires à `spatial.trajet` : deux pas
orthogonaux à travers une case solide, arrivée libre dans la même salle. Aucune arrivée
dans l'obstacle, aucun angle coupé, aucune traversée d'un mur ou d'une seconde obstruction.
`pnj._avancer_de` revalide les conditions réelles, fait le même jet si nécessaire, produit
le bruit commun et marque l'effort pour `vecu`. La marche ordinaire garde ses règles.

La forme perçue devient une croyance `passage`. Sans forme décrite, aucune nouvelle croyance
n'est créée. `obstacles.monde_cru` construit une lecture des obstacles à leur position crue,
avec leur géométrie crue ; `parcours_cru` vérifie aussi les obstacles intérieurs aux salles.
`Vue.route` distingue l'équipement prévu dans chaque état de la recherche. Le coût conserve
la minute abstraite par salle et ajoute le supplément de durée du franchissement ; il ne
remplace pas tous les coûts historiques par des secondes. Le chemin métrique porte aussi sa
durée effective, sans rotation, comme la marche antérieure.

Les croyances et grandeurs stables sont déjà dans `_entrees` ; dès qu'une forme est connue,
les positions crues des obstacles y entrent aussi, et la case de départ lorsque le parcours
métrique est nécessaire. Les caches de route
distinguent tout l'équipement, au lieu des seules clés. Aucune nouvelle lecture de lumière :
les graphes de découverte `sombre` et `lumiere` gardent leur contrat. Le franchissement ne
modifie ni `bloque_vue`, ni le calcul des ombres, ni les entités livrées au récit.

Une preuve évite le parcours métrique lorsqu'il n'apporte rien : chaque salle crue est
connexe par le pas ordinaire, et un détour remplace chaque franchissement en au plus son
temps. La preuve se fait mains vides ; porter ne peut qu'enlever un passage. Elle est propre
à l'allure (le pas feutré peut rendre un raccourci utile), gardée dans une mémoire bornée à
128 géométries et recalculée sans mémoire sous `spatial.VERIFICATION`. Dans ce cas seulement,
la case de départ ne modifie plus la clé de recherche ; les positions crues des obstacles
y restent. Trois situations après recharge contrôlent ce choix : détour dominant, salle
coupée et détour existant mais plus lent. Un simple enjambement qui égale le détour au pas
le bat au pas feutré : cette différence est également vérifiée.

## Données décrites

Valeurs en cm, puis kg ; prises oui/non. Ces données décrivent les obstacles existants sans
changer leur nom, leur texte, leur masse, leur case ou leur opacité.

| Scénario | Obstacle | Dessous | Sommet | Largeur | Profondeur | Charge | Prises |
|---|---|---:|---:|---:|---:|---:|---|
| Relais et crue | `poutre_conduite` | 45 | 100 | 80 | 70 | 180 | Oui |
| Relais et crue | `colonne_vannes` | 0 | 300 | 80 | 100 | 1000 | Non |
| Auberge | `comptoir` | 0 | 110 | 80 | 80 | 180 | Non |
| Auberge | `table_longue` | 60 | 80 | 80 | 100 | 180 | Oui |
| Auberge | `table_cuisine` | 55 | 85 | 80 | 90 | 180 | Oui |
| Auberge | `tonneau` | 10 | 100 | 80 | 80 | 180 | Non |
| Auberge | `stalles` | 0 | 180 | 80 | 100 | 0 | Non |
| Auberge | `lit_chaud` | 20 | 55 | 80 | 100 | 200 | Oui |
| Auberge | `caisses` | 0 | 150 | 80 | 100 | 100 | Oui |
| Mine | `benne` | 0 | 110 | 80 | 100 | 250 | Oui |
| Mine | `bureau_contremaitre` | 55 | 80 | 80 | 80 | 150 | Oui |
| Mine | `eboulis_1`, `eboulis_2`, `eboulis_3` | 0 | 200 | 80 | 100 | 0 | Non |
| Mine | `etai_brise` | 40 | 80 | 80 | 40 | 20 | Non |
| Mine | `rayonnage` | 10 | 200 | 80 | 60 | 100 | Oui |
| Mine | `sacs` | 0 | 120 | 80 | 100 | 150 | Oui |
| Mine | `table` | 60 | 80 | 80 | 100 | 180 | Oui |
| Mine | `treuil` | 0 | 130 | 80 | 100 | 250 | Oui |

21 objets décrits (2 + 2 + 7 + 10). Les stalles occupées et les éboulis n'offrent aucune
réception de charge ; un pilier de maçonnerie ne se franchit pas par cette règle. L'étai
brisé garde une charge faible : son dessous peut se traverser, son dessus ne porte pas un
humain. `margelle`, dont le nom est « ouverture du puits », reste sans `passage` : c'est un
vide, pas un obstacle solide sur lequel inventer un appui. Sa traversée demanderait un saut
avec réception décrite. Les anciennes sauvegardes n'acquièrent pas automatiquement ces
dimensions : leur auteur ou le MJ peut établir les données encore inconnues.

## Vérifications et mesures

Étape 1, aucun scénario changé :

```powershell
$py = 'C:\Users\msics\donjon\.venv\Scripts\python.exe'
& $py tools/comparer_bancs.py --reference 276524c --empreintes --heures 2 --scenarios relais mine auberge crue --graines 1985 7 42 2024 --processus 3 --sortie artifacts/sous-obstacle/etape1-2h.json
& $py tools/comparer_bancs.py --reference 276524c --empreintes --heures 8 --scenarios relais mine auberge crue --graines 1985 7 42 2024 --processus 3 --sortie artifacts/sous-obstacle/etape1-8h.json
```

**32 paires identiques** : chronique, mesures et état final complet, nuit par nuit.
Référence puis branche, l'une après l'autre, trois processus à priorité réduite. Les résultats
bruts restent dans `artifacts/sous-obstacle/` (non versionné). Les 103 tests ciblés de l'étape
moteur sont verts (passage, marche, diagonales, franchissements, matière, faits locaux,
questions et temps réel).

Les tests `test_sous_obstacle` passent par la vraie console avec fournisseur simulé, sauvegarde
avant saisie et recharge après. Ils vérifient la poutre du Relais et la table de l'auberge :
question → fiche sans effet → `tenter` → position et journal → examen après recharge.
Autres cas : dessous trop bas, sommet trop haut, largeur, prises, charge supportée, charge
portée et objet trop long pour joueur et PNJ ; qualification additive ; réception occupée ;
pas diagonal refusé ; enjambement sans jet et escalade ratée ; forme inconnue ; PNJ qui rampe
sur son trajet, même laps d'un bloc ou en rotations rechargées ; forme crue impossible et
équipement prévu qui ferment le plan ; préparation des sept scènes Luna sauvegardées, dont
l'enjambement du lit de l'auberge sur les données réelles.

Deux ruptures de contrat trouvées pendant les bancs et la suite ont été corrigées au point
commun : `prix_tache` arrondit maintenant un temps fractionnaire avec `math.ceil`, pour
produire des pièces entières dans les refus et les engagements ; `_case_interieure` reconnaît
aussi une copie de sortie par ses champs `case`/`vers`/`porte`, même si une route y a ajouté
ses mesures. Avant cette seconde correction, Odile et Mireille s'écartaient en boucle devant
la porte du cellier : la garde de la porte perdait son seuil par comparaison d'identité Python.
La scène réelle aboutit de nouveau ; une autre scène à la mine vérifie la même chaîne avec
une porte fermée, la marche puis la recharge. Le total d'une fiche composée compte les
dixièmes des étapes, y compris les 12 secondes d'un passage, au lieu des seules minutes.
Enfin, les jets génériques du joueur passent par le même `caractere.modificateur` que ceux
des PNJ : la borne de caractéristique à 1 subsiste sous de forts malus. Vérifié après recharge
pour l'escalade composée et une poussée simple à FOR 3 et trois besoins pressants ; la fiche
et le résultat conservent la décomposition de la caractéristique et du corps.

Les premiers calculs avec données (11 nuits interrompues sur 16 par le contrat monétaire)
et la suite intermédiaire (échec de Mireille ; dernier fichier `test_mine` arrêté parce qu'il
avait chargé l'ancienne règle) sont conservés comme diagnostics, **pas comme validation**.
Les lots finaux ci-dessous sont ceux à retenir.

Étape 2, après les 21 descriptions, référence puis branche, trois processus :

```powershell
& $py tools/comparer_bancs.py --reference 276524c --heures 8 --scenarios relais mine auberge crue --graines 1985 7 42 2024 --processus 3 --sortie artifacts/sous-obstacle/etape2-8h.json
& $py tools/audit_nuits.py analyser --dossier artifacts/sous-obstacle/audit-reference --sortie artifacts/sous-obstacle/constats-reference.json
& $py tools/audit_nuits.py analyser --dossier artifacts/sous-obstacle/audit-branche --sortie artifacts/sous-obstacle/constats-branche.json
```

Les champs `reference.nuits` et `branche.nuits` du comparateur ont été exportés, chaque nuit
dans son `.json.gz`, vers les deux dossiers d'audit, sans rejouer les nuits ni changer les
observateurs. Moyennes sur quatre graines et huit heures, **276524c → branche finale** :

| Mesure | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| Gestes | 153,25 → 153,25 | 240,5 → 240,5 | 269,25 → 269,25 | 255,25 → 255,25 |
| Événements distincts | 35,75 → 35,75 | 71 → 71 | 54,25 → 54,25 | 53,25 → 53,25 |
| Échanges | 14 → 14 | 44,25 → 44,25 | 23,5 → 23,5 | 20,75 → 20,75 |
| Minutes urgentes sans recours | 100 → 100 | 13,75 → 13,75 | 125 → 125 | 112,5 → 112,5 |
| Minutes urgentes en attente | 31,25 → 31,25 | 288,75 → 288,75 | 8,75 → 8,75 | 66,25 → 66,25 |
| Minutes dans le noir | 8,75 → 8,75 | 255 → 255 | 138,75 → 138,75 | 67,5 → 67,5 |
| Recherches neuves | 533 → 533 | 614,5 → 614,5 | 584 → 584 | 1 131,75 → 1 131,75 |
| Maximum des passages de salle par heure | 9,25 → 9,25 | 11,5 → 11,5 | 17,75 → 17,75 | 31,25 → 31,25 |
| Usurpations, violations, plantages | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Secondes CPU par nuit, observateurs inclus | 5,52 → 5,81 | 25,77 → 28,37 | 19,45 → 20,58 | 10,58 → 11,59 |

**Toutes les mesures de jeu sont identiques**, nuit par nuit, y compris les comptes de
recherche et de choix. Les chroniques complètes, les relevés toutes les cinq minutes
(positions, besoins, intentions) et les bilans finaux de l'audit sont identiques aussi.
Chaque scénario garde quatre nuits distinctes. Les constats d'audit sont identiques :
15 `fige_presse` expliqués comme observations, 7 `voir_alterne`, 2 `noir_long` ; aucune
rafale nouvelle, aucune bascule ni avertissement redit nouveau. Le hash de l'état complet
diffère nécessairement par les données de forme et les croyances supplémentaires : cette
seconde étape ne prétend pas retrouver le hash de l'ancien schéma.

Sur ces seize nuits, aucun PNJ n'emprunte un nouveau dessous ou dessus : le détour ordinaire
suffit et domine. L'effet mécanique est contrôlé dans les scènes où une cloison coupe la
salle ou impose un détour plus lent, avec passage réel et recharge. Les scénarios offrent
aussi le geste explicite au joueur. Le surcoût CPU final observé est de **5 à 10 %** ; ces
temps CPU incluent les mêmes relevés d'audit, les versions ont tourné l'une après l'autre
sur le poste partagé. Le premier lot vert, avant la preuve de domination, coûtait 3 à 9 fois
la référence sans changer les nuits ; la dépendance inutile à chaque case du PNJ a été
retirée par cette preuve générale, et non par une exception de scénario.

Suite complète : **1 527 tests, quatre ignorés**, verte en **273,79 s**, trois processus,
priorité réduite (`suite-finale.json`). Les **19 tests** de `test_sous_obstacle` sont verts,
dont le vrai planificateur sous `VERIFIER` et perception 1, sur un trajet exigeant le dessous,
sa reprise, puis sa fermeture par l'équipement après recharge.

```powershell
& $py tools/tests.py --processus 3 --sortie artifacts/sous-obstacle/suite-finale.json
& $py tools/empreintes_nuits.py jouer --depot . --sortie artifacts/sous-obstacle/verifier-2h.json --scenarios relais mine auberge crue rixe --graines 42 --departs tire --heures 2 --processus 3 --verifier --verification 1
& $py tools/empreintes_nuits.py jouer --depot . --sortie artifacts/sous-obstacle/verifier-8h.json --scenarios relais mine auberge crue rixe --graines 42 --departs tire --heures 8 --processus 3 --verifier --verification 0.2
```

`VERIFIER` et `VERIFICATION` à 1 sur deux heures : **cinq nuits sans écart**, aucune recherche
neuve bornée. Puis à 0,2 sur huit heures : **cinq nuits sans écart** également. L'outil compte
51 recherches neuves à leur borne à la mine et 18 à l'auberge, zéro ailleurs ; c'est la limite
de recherche déjà signalée sur cette base de `main`, pas un écart de reprise. L'optimalité
des recherches neuves qui atteignent leur borne ne devient pas garantie par ce chantier.

## Limites

- Gabarits par défaut humains (170 cm, 70 kg), carrure déduite par convention, pas du texte
  du portrait. Une silhouette particulière exige les grandeurs d'auteur correspondantes.
- Un objet portable sans dimension compte pour une case (1 m) pour cette règle ; l'escalade
  peut donc demander de poser ou de décrire un petit objet. Aucun encombrement réel n'est
  garanti pour un objet dont la forme n'a pas été établie.
- Franchissement d'une case dans une même salle, sans jeu latéral sous la résolution du
  mètre. Ni obstacles successifs, ni passage rampant à travers un seuil, ni puits ou vide.
- Les rotations ne sont pas dans le coût du chemin ; le coût attendu des jets manqués n'y
  entre pas. Une salle hypothétique de la recherche part d'une case libre représentative,
  pas de la position future précise après chaque geste social.
- La recherche des PNJ conserve sa borne de nœuds ; les contrôles ci-dessus distinguent les
  bornes connues d'une reprise périmée ou d'un écart entre recherches.
- Plausibilité des descriptions et traduction libre de Luna : contrôle encore en partie
  sémantique. Les tests simulés prouvent le contrat du moteur, pas le comportement réel du
  modèle. Les essais ci-dessous restent obligatoires avant de déclarer le défaut Luna clos.

## Vérification Luna à faire

**Aucun essai ni connexion tenté ici**, conformément à la demande. Depuis l'autre poste,
sur copies temporaires, avec `gpt-6-luna` et comparaison désactivée :

```powershell
& $py tools/banc_parties.py tests/data/bancs/sous-obstacle-relais.json tests/data/bancs/sous-obstacle-auberge.json tests/data/bancs/sous-obstacle-enjamber.json tests/data/bancs/sous-obstacle-trop-bas.json tests/data/bancs/sous-obstacle-trop-haut.json tests/data/bancs/sous-obstacle-encombre.json tests/data/bancs/sous-obstacle-inconnu.json --sortie artifacts/sous-obstacle-luna
```

| Script préparé | Saisies exactes, dans l'ordre (puis `quitter`) | Ce que le joueur doit lire et l'état à recharger |
|---|---|---|
| `sous-obstacle-relais` | `est-ce que je pourrais passer sous la poutre effondrée ?` ; `tenter` ; `examiner poutre effondrée` | Fiche ramper, 12 s, bruit feutré, sans jet ; « Rien n'est encore tenté » à la question. Après confirmation, passage sous la poutre, position `[6,3]` dans `echoppe`, temps 12 s ; opacité conservée ; dégagement 45 cm à l'examen. Aucune échelle requise, aucune parole de Corvus inventée. |
| `sous-obstacle-auberge` | `est-ce que je pourrais passer sous la longue table ?` ; `tenter` ; `examiner longue table` | Même fiche et durée ; position `[6,4]` dans `salle_commune`, dégagement 60 cm et sommet 80 cm après recharge. |
| `sous-obstacle-enjamber` | `est-ce que je pourrais enjamber le lit à rideaux ?` ; `tenter` ; `examiner lit à rideaux` | Fiche enjamber, 6 s, sans jet ; position `[2,0]` dans `chambre_chaude`, lit toujours bloquant, sommet 55 cm après recharge. |
| `sous-obstacle-trop-bas` | `est-ce que je pourrais passer sous la poutre effondrée ?` ; `ramper sous la poutre effondrée` | Dégagement trop bas, aucune demande d'échelle ; pas de déplacement ni temps dépensé, aucun `attendu` affiché. |
| `sous-obstacle-trop-haut` | `est-ce que je pourrais passer par-dessus la poutre effondrée ?` ; `passer par-dessus la poutre effondrée` | Obstacle trop haut pour ce passage sans matériel ; aucune réussite racontée. Position `[4,3]` et temps inchangés. |
| `sous-obstacle-encombre` | `est-ce que je pourrais passer sous la poutre effondrée ?` ; `ramper sous la poutre effondrée` | Pied-de-biche décrit à 250 cm et porté : objet trop encombrant ; position et temps inchangés, objet toujours porté. |
| `sous-obstacle-inconnu` | `est-ce que je pourrais passer sous la poutre effondrée ?` ; `tenter` | Soit le MJ qualifie la géométrie plausible avant de préparer la fiche, soit le joueur lit que dégagement/hauteur manquent. Aucune supposition automatique de passage ni exigence d'échelle ; pas de mouvement avant confirmation. Contrôler la qualification et son audit dans le fil. |

Faire au moins deux passes et relire les textes, les appels et les sauvegardes. Le rendu de
Luna peut reformuler le résultat déjà enregistré ; il ne doit pas inventer un passage permanent,
un obstacle devenu transparent, un PNJ déplacé ni la nécessité d'une échelle pour ramper.
