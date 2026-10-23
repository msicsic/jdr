# Rapport Codex 20 — temps des trajets et des gestes

Branche `codex-trajets-reels`, non fusionnée, base `main` **aff9626**, tâche **fe77c95**.
Worktree `tmp-worktrees/codex-trajets-reels`. Le dépôt principal reste sur sa branche
initiale ; aucun appel ni connexion à Luna. Premier commit signé **0bd4729**.
Les résultats ci-dessous sont en cours de validation.

## Règle et lecteurs

Le temps prévu dépend de la position de départ et de celle où laisse le geste précédent.
`obstacles.Route` conserve les sorties historiques et la mesure du chemin en cases ;
`cout_route` est l'unique conversion de cette route en minutes. Pas droits et diagonaux
emploient `temps.duree_pas`, portes `pnj.DUREES`, rotations `spatial.QUART` / `quarts`.
Une approche locale est une route, même quand sa liste de sorties est vide.

Lecteurs recensés :

- `Vue.allers`, `route`, `trajet`, `_chercher` ;
- `Vue.attente_part`, `peine_tache` et le choix d'interlocuteur de `s_enquerir` ;
- le devis `part_estimee.suites`, ses préparatifs et ses trajets conclusifs ;
- `pnj.parcours` / `chemin` et leurs tests d'accessibilité (appel, délibération,
  exécution des anciennes parties) ;
- les gestes de défense du planificateur et `defense.chemin_fuite` / la fiche de fuite.

`appel.venue` était déjà exprimé en dixièmes par le trajet spatial, sans minute par salle ;
il ne sert pas de coût au planificateur. Les portées de l'ouïe et de la perception sont des
distances physiques, pas des temps de plan. Les parties sans mode cases conservent
l'exécution à la minute et son coût historique.

Les pressions sont intégrées par salle sur le trajet et avant les effets du geste.
Le noir pendant l'allumage se paie ; la lumière ne vaut qu'ensuite. La combustion
d'une source portée multiplie la durée réelle, jamais une préférence ou un paiement.
Les coups et crochetages gardent leur nombre attendu de tentatives ; l'approche ne
se multiplie pas par ce nombre. Les durées de prise, ouverture, parole, alimentation,
allumage et service proviennent du moteur, au lieu d'une minute forfaitaire.

## État, géométrie et mémoires

`Etat` distingue salle, case, orientation et allure, en plus des possessions et faits.
Les deux allures initiales évitent de découvrir après coup que le trajet précédant un
vol devait être feutré. Les portes ouvertes en chemin et les positions des objets posés
sont des effets projetés. La même forme d'état sert aux graphes `sombre` / `lumiere`,
aux résultats repris et à `_sans_plan` ; la preuve parcourt les deux départs permis.

Le monde de lecture ne garde des obstacles que les positions et formes crues.
Le graphe global relie départ et seuils ; les tables locales gardent leurs distances
aux cases de geste. Mémoire LRU de 2 048 tables, clé par géométrie de salle, obstacles
crus, origine et allure ; corps et équipement lorsqu'un passage spécial sert.
La preuve de domination et sa mémoire du lot O restent contrôlées par
`spatial.VERIFICATION`. Les tables locales reprises le sont aussi. `_entrees` garde
les nouvelles lectures de position et les placements fixes, sans lire la position
réelle d'un objet mobile inconnu. Les clés posées par un plan ne restent pas disponibles
parce qu'elles étaient portées au départ.

La baisse des prix de marche expose un problème de volume : charger ce qui est déjà
assez chargé ne changeait pas l'état physique projeté, mais créait des faits et des
inventaires supplémentaires avant toute demande de feu. Ces préparatifs sans effet
ont été retirés par la règle commune de charge ; aucun prix, borne ni scénario modifié.

## Cas vérifiés

`tests/test_trajets_reels.py` : choix entre deux flammes au Relais et à la mine,
temps prévu comparé aux gestes exécutés, état/perception après recharge ; objet
proche et objet lointain dans une salle, position du geste suivant ; pression avant
allumage ; obstacle cru ou ignoré ; deux portes courtes plutôt qu'un long détour par
une porte ; même laps attendu d'un bloc ou découpé avec rechargement.
L'allure feutrée est vérifiée dès la première approche, durée exécutée comprise ;
la clé posée est retirée des chemins projetés puis de l'inventaire sauvegardé.
La fiche de fuite compte aussi la porte fermée au tarif de l'exécutant : le joueur
emploie encore une manipulation d'une minute, le PNJ une ouverture de deux secondes.
Ces durées existantes ne sont pas modifiées ; elles sont fournies à la même mesure.
Le cas du joueur au seuil vérifie la fiche puis les 61,5 secondes réellement écoulées.

Les attentes anciennes liées à une minute par salle, à l'ignorance de la case et au
premier identifiant de lampe sont adaptées. Les tests de graphe à coûts synthétiques
isolent explicitement leur domaine sans projection géométrique. Les sauvegardes réelles
bornées restent contrôlées par reprise, recharge, rendu et vie identique, sans exiger
qu'un ancien plan soit encore trouvé dans l'espace enrichi.
La crue 7 change également : à 270 minutes Brune n'a plus pris les planches d'Aubin
et arrive après l'extinction du poêle du guet ; les deux charges restent à Aubin et
les trois bûches du guet à Gorm. Le test suit cette nuit, puis vérifie depuis le palier
voisin, avant l'extinction, qu'elle monte effectivement se chauffer au feu haut.
Lucien rencontre Josse et lui demande sa lampe avant de l'appeler ; les contrôles de
recherche restent actifs sur cette scène et sur Rémy, qui cherche et appelle Gaspard.

## Mesures et contrôles

Contrôles exhaustifs terminés : `VERIFIER=True`, `spatial.VERIFICATION=1`,
2 h, graine 42, départ tiré, Relais, mine, auberge, crue et `rixe` : cinq nuits
sans erreur ni recherche bornée. Nœuds joués : 80 482 / 9 995 / 2 254 / 102 694 /
84 064 ; CPU de contrôle 326 / 264 / 104 / 449 / 318 s. Ces durées incluent les
recalculs exhaustifs, elles ne mesurent pas la vitesse normale du jeu.

À compléter après la suite et les campagnes : comparaison finale 8 h contre aff9626,
audit 12 h sur quatre graines, contrôles exhaustifs 2 h puis à 0,2 sur 8 h
(graine 42, quatre scénarios et rixe), CPU et nœuds avec référence et branche ensemble.
Tests et campagnes à priorité réduite, trois processus par campagne ; référence
et branche successives hors mesure simultanée.

## Échelle et limites

Aucune constante de préférence n'est recalibrée : `DEMANDE=3`, `CHERCHER=3`,
`RESTER=30`, `TACHE=5`, `SALAIRE=3`, prix des fautes et valeur des pièces inchangés.
Une marche de dix secondes vaut 1/6 de minute, pas une salle : ces constantes
peuvent désormais dominer la marche. Les réglages éventuels seront proposés avec les
mesures ; aucun ajustement par scénario.

Mesure contrôlée du Relais : allumer la source en main à la flamme proche prend
**11,5 s (0,1917 min)** ; à la flamme éloignée, **21,4 s (0,3567 min)**. Les deux
coûtaient une minute sans approche. À peur du noir 1, la pression de ces gestes vaut
respectivement **0,575** et **1,07** ; elle devient nulle après l'allumage. Une prise
au contact vaut deux secondes, non une minute. À chance neutre 0,5, la préférence
d'une demande vaut toujours six minutes, plus les dix secondes de parole et l'approche.

Réglages à essayer séparément, sans les présenter comme acquis :

| Terme | Valeur conservée | Proposition à mesurer |
|---|---:|---|
| `DEMANDE` | 3 | Essayer 0,25 à 0,5 : 30 à 60 s de réticence à chance 0,5, avant parole et approche. |
| `CHERCHER` | 3 | Essayer 0,5 : distinguer l'incertitude de trouver du trajet désormais très court. |
| `TACHE` | 5 | Essayer 0,5 comme forfait provisoire, puis remplacer ce forfait par un devis des gestes connus de la tâche. |
| `SALAIRE` | 3 | Garder d'abord, puis mesurer avec le nouveau devis ; le prix minimal reste une pièce. |
| `RESTER`, `NOIR`, prix de garde et `FLAMME_EN_MAIN` | inchangés | Garder : ils décrivent une durée de séjour ou un taux par minute physique, pas une distance. |

Exemple de changement d'échelle constaté dans les tests : Odile accepte désormais
une pièce pour un travail proche de quelques secondes là où elle la jugeait trop peu
pour plusieurs minutes abstraites. Le test de refus établit une fortune de 600 pièces
pour éprouver encore une offre réellement insuffisante. Mireille préfère une part
gratuite à un service payé lorsque Joss a du bois disponible ; le test du contrat payé
établit l'offre avant de vérifier le paiement, l'engagement et le foyer entretenu.

La projection n'est pas une simulation de la nuit future : elle ignore les mouvements
futurs des tiers, leurs attentes et leurs refus. Une position inconnue dans une salle
emploie une origine conventionnelle. Le service promis garde une estimation de durée,
sans tous les préparatifs du donneur. Les gestes durables et le devis de part conservent
leurs approximations décrites dans le plan. La borne de 4 000 états peut être atteinte
plus souvent avec les positions et portes projetées ; aucune impossibilité générale
ne sera déduite d'une recherche bornée.
