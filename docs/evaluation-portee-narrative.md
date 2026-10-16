# Évaluation du contrôle de portée — 15 octobre 2026

## Méthode

Le corpus fixe 16 propositions de description dans
[`tests/data/corpus_portee_narrative.json`](../tests/data/corpus_portee_narrative.json) :
13 détails muraux et 3 portraits. Sept descriptions sont limitées au sujet proposé ; neuf
introduisent aussi un objet, un lieu, un savoir, un événement ou un indice de quête.

[`tools/evaluer_portee_narrative.py`](../tools/evaluer_portee_narrative.py) injecte chaque
première proposition dans la boucle console sur une partie temporaire. La proposition initiale
est fixée par le corpus pour isoler la contre revue. Luna (`gpt-6-luna`) effectue réellement
le contrôle de portée ; pour les portraits, il contrôle aussi la narration finale. Si le
premier ajout est refusé, le harnais fournit une correction locale fixe, que Luna contrôle
à nouveau. Le moteur applique ensuite l'ajout accepté, la console l'affiche et le rapport
vérifie la sauvegarde rechargée. Aucune sauvegarde du joueur n'est ouverte ni modifiée.

Commande :

```powershell
.\.venv\Scripts\python.exe tools\evaluer_portee_narrative.py
```

Le rapport détaillé est écrit dans `artifacts/evaluations/portee_narrative.json` ; le rapport
de cette campagne est conservé localement dans `portee_narrative_16.json` du même dossier.
La commande effectue des appels réels à Luna. Elle peut aussi recevoir `--id IDENTIFIANT` ou
`--limit N`.

## Résultat observé

| Groupe | Attendu | Conforme | Écarts |
| --- | ---: | ---: | ---: |
| Descriptions locales | 7 acceptations | 7 | 0 |
| Faits extérieurs | 9 refus | 7 | 2 acceptations à tort |
| Total | 16 | 14 | 2 |

La campagne a utilisé 26 appels à Luna et environ 136 secondes. Ce petit échantillon sert
à trouver des défauts concrets ; il ne mesure pas un taux de fiabilité général.

Les deux acceptations à tort sont :

1. **`nom_objet_autonome`** : le nom `seconde cloche` est accepté comme simple détail
   attaché aux murs. Le jeu affiche « une seconde cloche sur les murs » et sauvegarde un
   détail, alors que le joueur comprend un objet distinct pouvant compter pour la quête.
2. **`indice_quete`** : `lettres gravées` est accepté comme détail visuel avec la description
   « Ces lettres indiquent que la cloche a été déplacée vers une cave. » Le texte est affiché
   et sauvegardé sans inscription lisible ni événement établi déplaçant la cloche.

Dans les deux cas, le moteur vérifie correctement la couverture du rapport, l'affichage et
la sauvegarde. La faille est le classement sémantique : Luna range toute l'affirmation sous
« propriété du sujet proposé ». La contre revue seule ne peut donc pas garantir que le type
`detail` corresponde à ce que la phrase fait croire au joueur.

Un premier essai du corpus avait aussi refusé à tort un éclat d'enduit ordinaire : Luna
réclamait une preuve de l'existence du sujet que la transaction allait précisément créer.
Le dossier de contre revue indique désormais la mutation autorisée par le moteur. Le cas a
été rejoué et accepté. Le rapport de ce premier essai reste dans
`artifacts/evaluations/portee_pilot_avant.json`.

## Suite proposée

Une première distinction structurelle des ajouts a été ajoutée après cette campagne. La
contre revue classe chaque nom et chaque phrase selon la représentation nécessaire : aspect
local, objet autonome, texte lisible, état du monde, portrait ou portée indéterminée. Le
moteur compare cette classe au type de l'ajout. Le rapport contient toujours une couverture
exacte du texte et une vérification des attestations citées. Cette classification vaut pour
toutes les descriptions, sans règle propre à la cloche ou à la cave.

Une seconde campagne complète, conservée dans
`artifacts/evaluations/portee_narrative_nouveau_contrat.json`, a donné **14 cas conformes sur
16**. Les neuf ajouts attendus comme refusés, dont les deux acceptations à tort ci-dessus,
ont été refusés. Deux ajouts attendus comme acceptés ont aussi été refusés : un éclat
d'enduit, interprété comme objet détachable, et une tache claire sur une surface humide,
dont Luna a exigé une preuve séparée pour l'humidité. Le jeu a poursuivi avec une proposition
corrigée ; les phrases initiales n'ont été ni affichées ni sauvegardées. Les deux cas
historiques ont également été rejoués séparément avec Luna et refusés.

Depuis cette campagne, le moteur accepte également une transaction `objet` pour une chose
autonome et une transaction `evolution` pour un changement déclaré par le scénario. La
contre revue vérifie la mobilité affirmée par une description d'objet. Un essai réel avec
Luna sur une partie temporaire du Relais a créé un bouton de bois posé au sol ; sa position
est restée stable après déplacement du joueur, puis le bouton a été ramassé par la commande
locale et retrouvé dans l'inventaire après rechargement. Une transition conditionnelle du
Relais est couverte par un parcours simulé qui déplace un objet et change l'objectif, avec
vérification après rechargement. Aucun événement de remplacement n'a été ajouté au scénario
jouable sans cause et déclencheur propres. Une sonde réelle sur la proposition d'une seconde
cloche comme `objet` dans le Relais a classé le nom et la description comme liés à l'objectif,
puis refusé l'ajout. Cet essai isolé ne garantit pas que Luna classera toujours correctement
une variante de cette proposition.

La distinction reste **probabiliste** : Luna fournit la classe sémantique, et le moteur ne
peut vérifier que sa cohérence avec la mutation proposée. Un mauvais classement `aspect`
peut encore faire passer une affirmation autonome. À l'inverse, un classement trop strict
peut brider un détail légitime. Depuis cette campagne, la transaction physique déclare
explicitement les capacités de son, de lumière et les usages physiques couper, levier et
allumage ; la contre revue les compare aux implications du nom et de la description.

## Sonde des capacités et de la portée de mission

[`tools/evaluer_capacites_objet.py`](../tools/evaluer_capacites_objet.py) soumet à Luna
trois cas : objets sonores et lumineux ordinaires, outils physiques polyvalents, et seconde
cloche dans le Relais. Le dernier doit être refusé comme modification de l'objectif.
Chaque essai reçoit un monde neuf en mémoire ; le rapport, sans jeton ni sauvegarde du
joueur, est écrit dans `artifacts/evaluations/capacites_objet.json`.

Au départ, un essai sur quatre des objets sonores et lumineux a été refusé parce que Luna
les rangeait parfois comme solution de mission. Après avoir précisé que l'utilité possible
d'un outil ne constitue pas une réussite de quête, un corpus de six décisions (trois cas,
deux répétitions) a encore produit deux faux refus : une source à allumer classée comme
outil d'allumage, et une cible générique d'un usage classée comme objet présent. Le contrat
de contre revue distingue désormais ces relations physiques. Le même corpus rejoué a donné
**six décisions conformes sur six**. Ce petit échantillon ne garantit pas le classement de
toutes les formulations futures ; les échecs restent des refus avant affichage ou mutation.

Le même outil d'évaluation a ensuite contrôlé deux fois un objet physique tranchable
avec Luna réel : les deux propositions ont été acceptées. Le seuil et la ténacité
restent bornés par le moteur ; ce résultat ne démontre pas une compréhension fiable de
toutes les matières par le relecteur.
