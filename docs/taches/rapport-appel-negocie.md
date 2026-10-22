# Rapport : l'appel négocié (branche `appel-negocie`)

Tâche : `docs/taches/appel-negocie.md` (décision de l'utilisateur du 2026-10-22). Base : `main` 06602a6.
Détail de la règle, des cas vérifiés, des bancs et des limites : `docs/plan-ouie.md`, « L'appel négocié » ;
règles du joueur : `docs/mecaniques.md`, « Appeler, crier et siffler ».

## Règle

Avant, l'appelé qui saisissait son nom répondait « Ici ! » et attendait cinq minutes (`REJOINT`), quelle
que soit la raison de l'appel. Désormais l'appelé et l'appelant conviennent de qui vient à qui, par des
paroles typées (contenus `appel` et `raison`, des cris de nature `hele`) que le moteur tranche, une seule
règle pour les PNJ et le joueur (`donjon/appel.py`) :

- **« J'arrive ! »** : il vient. Il cherche lui-même l'appelant, on le prie de venir (l'autre ne le peut
  pas), ou la raison dite le fait venir (un avertissement, une aide, ce qu'on lui demande et qu'il a sur lui).
- **« Ici, viens ! »** : il reste. Il ne peut ou ne veut bouger : un geste en cours sur place, une garde, ce
  qu'il fait sur place (assis, au feu, à l'abri), un autre rendez-vous, un chemin qu'il croit fermé, l'eau
  qui le met en péril, un besoin qui le presse ailleurs ; ou la raison ne le fait pas venir.
- **« Qu'est-ce que tu veux ? »** : libre, sans raison de bouger. L'appelant dit ce qu'il veut (tiré de son
  intention : demande, offre, avertissement, tâche, ou « J'ai à te parler. ») et l'appelé décide de nouveau,
  sans redemander.
- **Le silence** : il se méfie de cette voix, ou ne veut pas se signaler (un geste qu'il veut sans témoin,
  ou un geste illicite en cours).

L'appelant qui entend « Ici, viens ! » répond « J'arrive ! » s'il peut venir, sinon « Ici, viens ! » à son
tour, une fois ; prié de venir, celui qui attendait en décide de nouveau.

Ce qui est convenu entre dans l'esprit des deux : qui reste attend (`rejoint` : qui, jusqu'à quand, si
l'autre a promis), qui a dit « J'arrive ! » doit venir (`rejoindre`, une parole due au rang des
engagements). Qui attend quelqu'un qui vient ne va plus le chercher : son plan devient l'attente. L'attente
se règle sur la distance : le plus court chemin en temps, et sa moitié, plus deux minutes. Venu, celui que
l'autre ne voit pas (de dos, dans le noir) dit « Me voici ! ». « J'arrive ! » est une parole donnée :
attendu en vain jusqu'à l'échéance, celui qui l'a dite, joueur compris, perd la confiance de qui
l'attendait (souvenir et cause `parole_rompue`, comme une dette niée).

Le joueur répond sans le MJ : « j'arrive », « je viens » ; « viens », « viens ici », « Ici ! », « je
réponds » ; « qu'est-ce que tu veux ? » (seulement à un appel par son nom ; sinon un refus avec
`attendu`). Ces mots peuvent être entre guillemets, suivre « je réponds » ou « je crie », ou suivre le nom
de l'appelant. Les PNJ y donnent suite par la même règle ; leurs réponses lui parviennent par l'ouïe commune.

## Fonctions

- `appel.py` :
  - `decider` : ce que répond un PNJ, avec `peut_venir`, `retenu`, `presse_ailleurs`, `pressante` et `se_cache` ;
  - `raison_de` : ce que dit vouloir l'appelant ;
  - `repondre` : l'appelé répond ;
  - `dire` : un cri de la négociation, et ce qu'il promet ;
  - `entendre` : la suite donnée par un PNJ ;
  - `reagir` : la suite donnée à une réponse du joueur ;
  - `en_attente` et `dernier_cri` : à qui le joueur peut répondre ;
  - `attendre`, `venir`, `tenir`, `rencontre`, `se_signaler`, `plan_venir` : le rendez-vous ;
  - `venue` et `delai` : le temps de venir ;
  - `verifier` : la forme du rendez-vous dans l'esprit.
- `pnj.appeler` hèle puis passe à `appel.repondre`. `pnj.repondre` et `pnj.repondre_a` sont retirés.
- `pnj._inspecter` appelle seulement qui l'on ne sait pas là (`croit_present`).
- `deliberation` :
  - `attendre` délègue à `appel.tenir` ;
  - `rejoint` clôt les deux côtés ;
  - `_attendre_qui_vient` fait attendre qui doit être rejoint ;
  - le but « venir » est au rang des engagements ;
  - `attendre_l_appelant` et `REJOINT` sont retirés.
- `esprits` : champ `rejoindre` ; `rejoint` porte `vient`.
- `relations.EPREUVES` : cause `parole_rompue`.
- `social.recevoir` : les contenus `appel` et `raison` n'apprennent rien.
- Joueur :
  - `paroles.reponse_a_l_appel` et `paroles._reponse` lisent la sorte de la réponse ; `paroles.repond` est gardé ;
  - `commandes.repondre`, `sons._compiler_repondre` (méthodes `repondre`, `arriver`, `demander_raison`) ;
  - `moteur._appliquer` et `moteur._terminer_etape` (`appel.reagir` le cri fini) ;
  - `ecoute.appels` ; la consigne `emettre_son` du MJ.
- Banc :
  - `reponses_arrive`, `reponses_viens`, `reponses_quoi`, `reponses_raison`, `silences`, `paroles_rompues` ;
  - les textes « … retrouve …, comme convenu. » et « … se tourne vers …, qui arrive comme convenu. ».

## Cas vérifiés (`tests/test_appel_negocie.py`, 22 tests, état après rechargement et ce que lit le joueur)

- **« Ici, viens ! »**
  - Cas réel, Relais : Aubin hèle Gorm, qui croit la porte étanche verrouillée. Gorm ne bouge pas, ils se retrouvent, la part est servie au premier appel.
  - Même nature : Gorm de garde reste à sa garde.
  - L'appelant retenu (cas vu au banc, mine 42) : « Ici, viens ! » croisés, puis l'appelé vient.
- **« Qu'est-ce que tu veux ? »**
  - Cas réel, auberge : Hugues veut prévenir Anselme. L'avertissement le fait venir ; Hugues l'attend et le prévient.
  - Cas réel, mine, graine 2024 (scène enregistrée) : Josse veut les bûches de Gaspard, qui ne les a pas sur lui. « Ici, viens ! », Josse vient, la part est promise.
  - Dans le noir, cas réel de l'auberge (`test_constater_rumeurs`) : Mireille hèle Odile au grenier.
- **« J'arrive ! »**
  - Qui cherche l'appelant vient ; l'autre l'attend le temps de venir.
  - Cas réel, crue, graine 42 (scène enregistrée) : « Me voici ! », sans parole rompue. Sans ce signal, au banc, Brune croyait Gorm parjure.
  - La parole rompue : Aubin empêché ; Gorm cesse d'attendre à l'échéance et s'en méfie.
  - L'échéance suit la distance.
- **Silence** : qui guette un crochetage sans témoin ne répond pas ; qui se méfie se tait.
- **Le joueur hèle** et reçoit chacune des réponses :
  - « Qu'est-ce que tu veux ? » puis « viens » : Gorm vient, sans le rappeler ;
  - « Ici, viens ! » puis « j'arrive » : ils se retrouvent ;
  - « J'arrive ! » de qui le cherche ;
  - le silence.
- **Le joueur hélé** :
  - « j'arrive » sans venir : Gorm s'en méfie à l'échéance ;
  - « viens » : Gorm vient, ou répond « Ici, viens ! » s'il croit la porte fermée ;
  - « qu'est-ce que tu veux ? », puis « Gorm, viens ».
  - Aucun appel au modèle.
- **Le même laps découpé donne le même monde** (Relais, auberge), et les formes de la saisie.
- **Tests changés** : 9 fichiers. Les raisons sont dans le plan ; ce sont surtout les textes « Ici ! » et l'échéance lue du rendez-vous.

Suite complète : 1304 tests (18 sautés), en priorité réduite. `planification.VERIFIER` et
`spatial.VERIFICATION` 0,2 sur une nuit de 8 h de chaque scénario (graine 42) : aucun plantage, aucun écart.

## Mesures

Bancs à départ tiré, graines 1985, 7, 42 et 2024, `--processus 4`. `main` 06602a6 puis la branche, l'un
après l'autre ; chiffres par nuit, de `main` à la branche ; tableau complet dans le plan.

- **Rapide, 4 h, quatre scénarios.** Mesures identiques hors des appels.
  - On y hèle 0 à 0,5 fois par nuit.
  - Crue : une attente vaine devient des retrouvailles (« Me voici ! »).
  - Temps égaux : Relais 3 → 2,8 s, mine 7,2 → 7,2 s, auberge 4,7 → 4,6 s, crue 3,9 → 3,5 s.
- **8 h, mine et auberge**, là où l'on hèle.

  | Mesure | Mine | Auberge |
  |---|---|---|
  | Appels | 3 → 3,5 | 6,75 → 4,75 |
  | « J'arrive ! » | 2 | 3 |
  | « Ici, viens ! » | 2,25 | 2,75 |
  | « Qu'est-ce que tu veux ? » | 1,75 | 3 |
  | Raisons | 1,75 | 3 |
  | Silences | 0,5 | 0 |
  | Retrouvailles | 1,75 → 2 | 3,75 → 3 |
  | Attentes vaines | 0,25 → 0 | 0 → 0 |
  | Minutes sans recours | 36,25 → 36,25 | 138,75 → 137,5 |
  | Échanges | 41,75 → 41,5 | 29,25 → 30,75 |
  | Temps | 28 → 27,7 s | 15,7 → 15,3 s |

  - Auberge, graine 42 : Mireille hélait Odile huit fois en cinq minutes ; désormais une fois.
  - Aucune parole rompue au banc, aucune usurpation ni violation.
- **`tools/comparer_bancs.py`** n'est pas sur `main` (branche Codex `codex-outils`) : les bancs sont
  comparés mesure par mesure.
- **Charge** : une autre session mesurait des temps sur ce poste. Les bancs sont restés à `--processus 4`
  et la suite en priorité réduite. Les temps sont donc indicatifs.

## Luna

Non vérifiée : la connexion n'est pas faite sur ce poste. Il n'y a pas de `.seuil-auth` dans le dépôt
principal, et `python connexion.py connecter` n'a pas été lancé.

À faire sur le portable, sur des copies, une exécution à la fois : « j'appelle Gorm », puis « j'arrive »,
« viens ici », « qu'est-ce que tu veux ? ».

Attendu : 0 appel au modèle pour ces formes typées. Les tests le vérifient avec un MJ simulé.

## Limites

- **La raison du joueur.** Le joueur ne dit pas ce qu'il veut par une parole typée locale. Ce qu'il dirait
  par le MJ n'entre pas dans la décision de l'appelé.
- **Les paroles qui pèsent.** Seul « J'arrive ! » non tenu pèse. « Ici, viens ! » cède à ce qui presse,
  comme l'attente d'avant, sans rancune.
- **Un empêchement compte comme une parole rompue.** Qui est empêché (une porte, l'eau) rompt sa parole aux
  yeux de l'autre. En 3a, une parole rompue ôte la confiance comme une dette niée.
- **Un rendez-vous à la fois.**
- **La rencontre** se juge au choix du but. On se retrouve en se voyant, ou en se sachant là et pouvant se
  parler.
- **Le lieu du rendez-vous** est la salle d'où venait la voix. « Peut-il venir » se juge sur le chemin qu'il
  croit, vers la salle réelle de cette voix.
- **La raison d'un PNJ.** Elle est lue de son intention, en cinq sortes ; « J'ai à te parler. » quand rien ne
  la dit (une garde, une ronde).
- **`MARGE`** est une constante.
- **Les bancs de 4 h** contiennent trop peu d'appels pour mesurer la règle. Seuls ceux de 8 h de la mine et
  de l'auberge le font ; il n'y a pas eu de banc de 8 h au Relais ni à la crue.
