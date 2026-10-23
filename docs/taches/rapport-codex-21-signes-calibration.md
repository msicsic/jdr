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

Preuve initiale : 20 nuits de 2 h (quatre scénarios et `rixe`, quatre graines),
chronique, mesures et état final complet identiques à `8855312`.
Les mesures définitives et la preuve 8 h seront ajoutées après exécution.

## 2. Relectures

`signes._presence` enregistre les épisodes de perception par observateur dans
`data.suivi_signes` : signes présents, numéro d'épisode, essai, conclusion et
lecture retenue par signe. Une réception partielle de tons ne fait pas disparaître
les autres signes. Une perception complète vide clôt les épisodes, y compris
quand personne n'émet plus rien. Les simples projections restent pures.

`lire` rafraîchit une lecture active équivalente (valeur et cible), sans souvenir
`intention_lue` ni ligne de chronique ; un échec n'écrit pas dans la lecture.
Un épisode nouveau ou une lecture périmée compte de nouveau. La date `apprise`
et l'épisode distinguent une nouvelle impression d'un rafraîchissement ;
`bilan_signes` ne répète que les faits physiques demandés, pas une même impression.
La carte et le contexte conservent l'impression actuelle avec son incertitude.

Tests ciblés : 28 tests des signes et de calibration, dont les guets du Relais et
de l'auberge, retour immédiat d'un signe, péremption, échec préservant la lecture,
deux observations du joueur et 20 minutes d'un bloc ou découpées avec reprise.
Le délai de dix minutes entre essais est conservé, même si le signe disparaît
puis revient ; son retour compte comme nouveau au prochain essai autorisé.
Les mesures de nuits avant/après restent à consigner.

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
