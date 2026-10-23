# Audit des nuits sans joueur (2026-10-22)

Audit seul : le moteur n'est pas modifié. Branche `audit-nuits`, partie de `main` 8c108c3 (après la
fusion de `echanges-suite`). Outil : `tools/audit_nuits.py` (`jouer`, puis `analyser`).

## Ce qui a été joué

| Lot | Nuits | Durée | Contrôles | Graines |
|---|---|---|---|---|
| 1 | 64 (4 scénarios × 16) | 12 h, départ tiré | `planification.VERIFIER` (arrêt au premier écart), `spatial.VERIFICATION` 0,2, `Monde.verifier` à chaque pas, rejeu | 1985 7 42 2024 3 11 99 500 1 2 5 13 21 77 123 314 |
| 2 | 64, mêmes graines | 12 h | `VERIFIER` continu (écart noté, classé, la nuit continue), `VERIFICATION` 0,2, rejeu | idem |
| 3 | 64 | 12 h | `VERIFICATION` 0,5 | 4 6 8 9 10 12 14 15 17 18 19 20 22 23 24 25 |

Scénarios et salle du joueur passif : relais et crue `chambre_cloche`, mine `galerie`, auberge
`dortoir`. 192 nuits lancées, 168 jouées jusqu'au bout (les 24 du lot 1 arrêtées par `VERIFIER` sont
rejouées entières au lot 2). Les relevés (toutes les 5 minutes, par PNJ : salle, case, but, besoins
qui pressent, noir craint, eau, croyances fausses sur ce qu'il perçoit) ne changent pas la nuit :
empreintes et mesures identiques à `banc_pnj.nuit` (vérifié sur 5 nuits, dont une en `VERIFIER`
continu). Temps d'une nuit de 12 h avec contrôles, 10 processus : relais 89 s, crue 74 s, auberge
407 s, mine 580 s (`VERIFIER` continu).

Reproduire :

    python tools/audit_nuits.py jouer --graines 1985 7 42 --heures 12 --dossier artifacts/audit-nuits2 \
        --processus 10 --verifier-continu --verification 0.2 --rejeu
    python tools/audit_nuits.py analyser --dossier artifacts/audit-nuits2 --sortie constats.json

Les données (`<scenario>_<graine>.json.gz`, pages `rejeu_<scenario>_<graine>.html`) sont dans
`artifacts/` (non versionné).

## Ce qui va bien

- **Aucun plantage du moteur** sur 192 nuits ; **aucune violation de `Monde.verifier`** (contrôlé à
  chaque pas de 5 minutes) ; **aucun écart de `spatial.VERIFICATION`** (0,2 sur 128 nuits, 0,5 sur 64).
- **Aucune usurpation** ; aucune croyance de lieu ou d'ouverture fausse sur un objet que le PNJ perçoit
  à l'instant du relevé (128 nuits × 144 relevés × tous les PNJ) : la perception révise bien.
- Pas d'agitation (aucun PNJ au-delà de 12 changements de salle par heure), va-et-vient entre deux
  salles rares (4 nuits sur 128, à la mine, voir B2). Les nuits divergent toutes.
- Les remboursements de dettes ont lieu à la crue et à la mine (toute dette née y est rendue).

## Défauts, par gravité

Fréquences sur les 128 nuits complètes des lots 2 et 3 (32 par scénario), sauf mention.

### Violation d'un contrôle

**V1. `planification.VERIFIER` échoue à la mine et à l'auberge.** *Traité (branche `verifier-eau`,
`docs/plan-planificateur.md`, « VERIFIER et l'eau ») : ce que le but demande lui-même se lit du but
(`Vue.eclairer`), plus d'`emplois` ; la référence est la recherche complète du même but, bornée à
60 000 nœuds, comparée par le coût ; une recherche jouée qui atteint sa borne est notée, pas tenue pour
fausse. 32 nuits de 12 h (4 scénarios × 8 graines) : 0 écart ; 161 recherches bornées reconnues
(Lucien et la lumière, auberge 7 ; Josse et le poêle, mine 7 et 11 ; Odon et l'argent, mine 99).
Les deux « vrais manques » ne se rejouent plus (les nuits ont changé depuis) ; le cas de même nature
relevé sur `main` 8589ca2 (auberge 99, minute 374, Lucien, lumière : restreinte sans plan, complète à
98) est une recherche jouée arrêtée à sa borne de 4 000 nœuds : à 12 400 nœuds, la restreinte trouve le
même optimum ; la restriction n'écartait rien.* Lot 1 : 15 nuits de mine sur 16 et
9 d'auberge sur 16 arrêtées (minutes 290 à 710) ; lot 2 (continu) : mine 15/16, auberge 11/16, relais et
crue 0/16 ; 108 écarts, tous sur une recherche à `emplois` (`lumiere` 96, `feu:poele` 10, `abri` 2).
Reproduction : `python tools/audit_nuits.py jouer --scenarios mine --graines 314 --heures 8
--verifier` (Josse, but `feu:poele`, vers la minute 420) ; mine 1, minute 544, Lucien, `lumiere`.
Chaque écart a été rejoué par une recherche complète à 60 000 nœuds (`--verifier-continu`) :

| Classe | Écarts | Cause |
|---|---|---|
| La référence sans `emplois` ne trouve rien, la recherche restreinte trouve un plan qui commence par chercher le porteur d'une lampe (« inspecter … cherche Rémy ») | 41 | `Vue.moyen_du_but` : chercher le porteur d'une source ou d'une flamme n'est offert que si `emplois` contient `lumiere` ; avec `emplois=None` (la référence de `VERIFIER`, « tout »), jamais. `emplois` ajoute donc des gestes au lieu de seulement borner ce qu'on porte. |
| Restreinte moins chère que l'optimum complet | 29 | Même cause (le plan moins cher passe par le porteur cherché). |
| Même coût, étapes différentes | 21 | Égalités départagées autrement : la référence a une étape `aller` de plus au même coût (Odon, mine 11, minute 640). |
| Référence arrêtée par la borne (`NOEUDS` 4 000) | 15 | La recherche restreinte rend l'optimum à 60 000 nœuds : faux écart du contrôle (Josse et `engager`, mine ; `abri` de Lucien, auberge 7). |
| La restreinte ne trouve rien, la complète trouve | 2 | Vrai manque : pour la lumière, Lucien ne pense pas à demander une part des fagots de Joss pour l'âtre (auberge 3 minute 631, auberge 99 minute 650) ; `emplois=("lumiere",)` écarte la part de combustible d'un foyer qui éclaire. |

Invariant suggéré : `emplois` ne fait que retirer ce qu'il ne vaut pas la peine de porter ; tout geste
offert à une recherche restreinte l'est aussi à la recherche complète (`moyen_du_but` traite `None`
comme « tout ») ; `VERIFIER` compare à une référence non bornée par `NOEUDS`, ou ignore une référence
qui atteint sa borne. Le comportement en jeu n'est pas faux pour les 70 premiers écarts (la recherche
restreinte est celle qui joue et fait ce que voulait `pnj-lumiere-garde`) ; c'est le contrôle qui ne
vaut plus sur ces scénarios.

### Boucles

**B1. Appel à l'aide répété toute la nuit.** Un PNJ appelle au moins 15 fois dans 28 nuits de mine sur
32, 6 d'auberge, 4 de crue ; jusqu'à 49 appels. Mine 7 (`--scenario mine --joueur galerie --graine 7
--heures 12 --chronique`) : Lucien, sécurité à 100 dans le noir du couloir d'entrée, appelle à la
minute 463 ; Gaspard le rejoint à 464 (« retrouve Lucien ») ; Lucien appelle encore toutes les 10 minutes
jusqu'à 720 (26 appels), Gaspard à côté. Cause : `deliberation.appeler_a_l_aide` ne regarde que la
sécurité ≥ `DESESPOIR`, l'absence de but d'abri et `APPEL_REPIT` ; ni qui est accouru, ni les appels
restés vains. Invariant : un appel attend une réponse ; quand quelqu'un est venu (ou que personne ne
vient), le même appel ne se répète pas : il faut un autre recours, ou que la présence venue apaise.

**B2. Aller voir, revenir garder, repartir voir.** *Traité (branche `ouie-temoins`, `docs/plan-ouie.md`) : un examen vain règle le bruit ; retours voir le même lieu à moins de 30 min divisés par 3 à 7.* Mine 18 : Mathe garde le baraquement et va voir un
bruit du bureau noir toutes les 10 minutes de la minute 455 à 560 (26 alternances de but) ; au Relais,
Gorm alterne « aller voir : Conduite basse » et « garder ses biens » 4 à 10 fois par nuit (14 nuits sur
32). Cause probable : dans une salle noire, parcourir des yeux ne voit personne, donc le bruit n'est pas
« résolu » (`ouie.resolu` exige d'y avoir vu quelqu'un depuis) ; il reste à voir jusqu'à `RECENT`
(30 min) et le renvoie dès que la garde est rétablie. Invariant : être allé voir un bruit le règle
(vu, ou constaté qu'on n'y voit rien) ; on n'y retourne que pour un bruit nouveau.

**B3. Prévenir la même victime en boucle.** Auberge, 15 nuits sur 32 : Hugues dit à Anselme « Lucien
est peu fiable » 6 à 8 fois (auberge 5 : minutes 243, 450, 455, 458, 464, 475, 479, 619 ; toutes
« crue »). Cause : `pnj._temoins` mémorise un `a_prevenir` par minute de geste vu, et
`deliberation._plan_prevenir` ne tient pour dit que ce qui l'a été après le dernier : chaque minute
d'un crochetage relance l'avertissement. Invariant : on prévient d'un fait que la victime ignore (ce
qu'il lui a déjà dit du même auteur, ce qu'elle croit déjà), pas d'un souvenir.

**B4. Demandes refusées redemandées.** Auberge : Mireille demande et tente d'acheter les fagots de Joss
7 fois chacune dans la nuit (refus « necessaire » à chaque fois), Odile offre une tâche à Tilo ou
Mathurine 7 fois (« cher ») ; Relais et crue : « demande les planches de bac à Aubin (necessaire) » ~3
fois par nuit (97 en 32 nuits). `REDEMANDE` (120 min) espace les demandes, mais un refus « necessaire »
ou « cher » ne change pas d'une heure à l'autre et n'est pas retenu comme tel. Défaut connu, déjà en
correction, cité sans être recompté : les offres de tâche « impossible » de l'auberge, 40 par nuit de
12 h (1 284 sur 2 717 offres en 32 nuits).

**B5. Chercher quelqu'un qui se tait.** Auberge 5 : Odile appelle « Joss ? » 39 fois ; elle traverse
l'étable noire où Joss se tient et l'y appelle (minute 269), il ne répond pas (il se méfie d'elle), elle
refait le tour de toutes les salles à chaque heure (`APPEL_OUBLI`). 16 nuits d'auberge sur 32 ont un PNJ
qui appelle au moins 10 fois. Conforme à la règle (on ne répond pas à qui l'on se méfie), mais la
recherche ne tire rien du silence ni d'une présence toute proche dans le noir.

### Absurdités

**A1. Un bruit de sa propre salle n'est jamais examiné.** *Traité (branche `ouie-temoins`) : le bruit se situe à une case, aller voir mène à portée de vue de sa source.* `deliberation.bruit_a_voir` et `alarme`
écartent tout souvenir de bruit dont la salle est celle où il se tient (`s["salle"] == ici`). Environ
40 % des bruits inconnus retenus viennent de la salle de l'auditeur (lot 2, 16 nuits par scénario, salle
lue au relevé le plus proche : relais 920 sur 1 437, crue 822 sur 1 860, mine 1 321 sur 3 609, auberge
1 594 sur 5 070 ; toutes les nuits). Relais 7 (`--graine 7
--heures 1 --chronique`), minutes 28 à 31 : Gorm, gardien, est dans le refuge à 7 cases de Brune qui
force sa réserve dans la pénombre (on n'y voit qu'à 3 cases, `spatial.PORTEE_VUE`) ; il « entend un
bruit : Refuge du relais » trois fois et reste à garder ; Brune crochète, ouvre et mange. Invariant : un
bruit se situe à une case ; aller voir mène à portée de vue de sa source, y compris dans sa salle.

**A2. Un vol commis à côté de sa victime, dans le noir, n'est jamais découvert.** *Traité en partie (branche `ouie-temoins`) : témoin par l'ouïe, l'auteur reconnu seulement si on le croyait là ; au contact dans le noir, on n'identifie toujours personne.* Sonde
(`artifacts/sonde_illicites.txt`, 16 nuits) : à l'auberge, les 44 présents qui n'ont pas vu un geste illicite
étaient dans le noir complet (39 fois la victime elle-même), à 1 ou 2 cases ; à la mine, Odon force le coffre de la
paie à une case de Bram et Josse (mine 500, minutes 456 à 461). Auberge 1 : Lucien mange les provisions
d'Anselme puis force son coffre (minutes 313 à 429) à une diagonale de lui ; Anselme, qui craint le noir,
n'en saura rien, et le récit le montre partir « voir d'où venait un bruit : Chambre au poêle »… depuis
le couloir où il vient d'aller. 32 nuits d'auberge sur 32 ont un geste illicite resté sans témoin malgré un présent dans la salle. Cause : le témoin est
`esprits.percoit` (la vue seule) ; le fracas tout proche ne donne qu'un « bruit » de salle (A1).
Invariant : ce qui se passe au contact (un fracas à une case, un geste sur ce qu'il garde) se perçoit
sans lumière : quelqu'un est là, il réagit (allumer, « Qui va là ? », appeler).

**A3. Les tâches payées sont acceptées puis presque jamais faites.** Hors auberge, 42 tâches acceptées,
5 faites (Relais 13 → 1, crue 23 → 4, mine 6 → 0) ; dettes qui en naissent : Relais 9 nuits sur 32
finissent avec Brune débitrice de Gorm. Relais 11 : Gorm paie 2 pièces à Brune à la minute 451 pour
entretenir le brasero ; son seul plan est de demander les planches d'Aubin, refusées (« necessaire ») à
453 et 576 ; elle ne fait plus rien pour la tâche, la dette naît à l'échéance (692) et elle refuse de
rendre (695) ; Gorm, qui a des fagots, les garde. Cause : `echanges.engager` accepte sur
`planification.devis_pulsion`, qui compte une part demandée à un tiers comme atteignable (au prix de la
demande), et l'engagement reste ouvert jusqu'à l'échéance même quand son seul plan a échoué.
Invariant (comme pour une part payée non servie) : un engagement payé qu'on sait ne plus pouvoir tenir
se rend ou se dit dès qu'on le sait ; un devis ne compte pas sur ce qu'un tiers garde.

**A4. Piégés par l'eau.** *Traité (branche `verifier-eau`, `docs/plan-crue.md`, « L'eau dans tous les
plans ») : l'eau attendue coûte à tout plan, on ne se tient ni ne se chauffe là où on l'attend, on ne
descend pas où elle va noyer ni ne s'enferme de son côté, piégé on sort d'abord. Crue, 12 h, 8 graines :
se chauffer dans l'eau 7 nuits sur 8 → 0, minutes à 86 cm ou plus 128 → 14 par nuit, appels à l'aide
94 → 2, aucun PNJ une heure à 50 cm ou plus.* 6 nuits de crue sur 32 : des PNJ restent 2 à 9 heures dans l'eau, la sécurité
à 100, sans aucun plan. Crue 500, minutes 165 à 185 : Brune quitte le refuge sec pour se chauffer au
brasero de la Conduite basse sous 88 cm d'eau, 17 minutes avant qu'elle ne soit noyée ; Gorm descend à la
Salle des vannes (71 cm) ; la Conduite noyée et la porte étanche verrouillée (aucun outil pour la
forcer) les enferment ; ils restent 475 minutes sous 86 à 114 cm d'eau et appellent 48 fois à l'aide.
Crue 24 : Brune reste 535 minutes dans le refuge, cul-de-sac derrière la Conduite noyée. Dans 31 nuits
sur 32, quelqu'un (surtout Brune) se chauffe au brasero les pieds dans l'eau (jusqu'à 88 cm), qui le trempe. Cause : seul
l'abri tient compte de l'eau attendue (`eau.menacee` dans `_plan_abri`) ; les plans de chaleur et du
devoir mènent là où l'eau monte et d'où le retour sera coupé. Invariant : tout plan compte l'eau qu'il
attend sur son chemin et à destination pour le temps qu'il y passera, retour compris. Limite du modèle :
rester sous 114 cm d'eau n'a pas d'autre effet que d'être trempé.

**A5. L'auberge finit dans le noir.** Faute de bois (connu), feux éteints vers la 5e heure ; 2 720
minutes·PNJ par nuit dans un noir craint (mine 1 083), dont Mathurine, Tilo et Mireille 4 à 5 heures
sans but dans la cuisine noire (auberge 7, minutes 410 à 725). Conséquence de A3, B4 et du scénario plus
que défaut propre ; à garder en tête pour juger les mesures de l'auberge.

### Curiosités

- Gorm alterne « entretenir le brasero » et « garder ses biens » ~7 fois par nuit : deux devoirs, sans
  dommage.
- Au Relais, Brune affamée reste jusqu'à 4 h 30 sans but (« en attente ») : refusée, sans argent, et la
  réserve n'est jamais sans témoin. Conforme aux règles.
- Crue 8 : réfugiée tôt à la Galerie de ronde, Brune y finit la faim et le froid à 100 sans rien à
  manger ni feu (attente).

## Outil

`tools/audit_nuits.py jouer` : `--verifier` (arrêt au premier écart, comme les tests),
`--verifier-continu` (écart noté avec la borne atteinte ou non et l'optimum d'une recherche complète,
puis la nuit continue à l'identique), `--verification`, `--rejeu`, `--sans-releves`, `--refaire`.
`analyser` : codes `plantage`, `repetition`, `demande_en_boucle`, `appels_nombreux`, `appels_a_l_aide`,
`va_et_vient`, `buts_alternes`, `fige_presse`, `but_hors_besoin`, `noir_long`, `eau_longue`,
`croyance_fausse_vue`, `agitation`, `illicite_sans_temoin_avec_present`, `dette_fin`,
`engagement_ancien`. Les seuils sont des repères de lecture, pas des règles du jeu : chaque constat
retenu ici a été relu dans la chronique ou par une sonde.

## Signalements de `main` 43fa7ac — Codex 14 (2026-10-23)

Branche `codex-signalements`, non fusionnée ; [rapport détaillé, cas et commandes](taches/rapport-codex-14-signalements.md).
32 nuits de 12 h, départ tiré, quatre scénarios × 1985, 7, 42, 2024, 3, 11, 99, 500 ; au plus trois
processus, campagnes successives, aucun appel à Luna. Les seuls observateurs enrichis rejouent
d'abord les 32 nuits à l'identique (chronique, mesures, empreintes, récit et souvenirs).

| Signalement brut | Avant → après | Cause / suite |
|---|---:|---|
| `fige_presse` | 80 → 82 | Attente de moyen, charge confiée ou déjà satisfaite : la lecture commune explique les 80 plages initiales et les 82 finales. |
| `noir_long` | 57 → 67 | Noir réellement subi, ressources et croyances ; conservé comme observation, aucune amélioration uniforme promise. |
| `illicite_entendu` | 81 → 106 | Témoin par l'ouïe correctement enregistré, pas une anomalie en soi. |
| `voir_alterne` | 25 → 19 | Alternance de buts sans identification d'un même bruit : ne prouve pas une boucle. |
| `illicite_sans_temoin_avec_present` | 21 → 22 | Aucun témoin attendu au début : pas de vue ; bruit sous le seuil ou objet non situé. |
| `eau_longue` | 5 → 5 | L'eau change pendant la plage : 1–14, 19–43 ou 21–57 cm sur la référence, sans piège démontré. |
| `appels_nombreux` | 3 → 4 | Boucle d'Anselme 108 → 15 ; pire PNJ-nuit 108 → 16. Restent tournées et demandes distinctes. |
| `appels_a_l_aide` | 1 → 0 | Gorm réarmait l'appel sous `DESESPOIR` sans être rassuré ; correction sur l'épisode d'urgence, conservé en sauvegarde. |
| `repetition` | 6 → 0 | Boucle Anselme/Joss : réponse anonyme, rendez-vous ignoré, résultat infructueux non retenu. |
| `passages_rafale` | 1 → 0 | Même boucle : pire auberge 93 → 38 passages/h. |
| `buts_alternes` | 3 → 3 | Entretien/garde, examen/garde, entretien/abri sur la nuit entière ; conservés comme repères. |
| `dette_fin` | 1 → 0 | Tâche devenue impossible, dette et refus enregistrés ; autre trajectoire après correction, sans abolir les dettes. |

Zéro autre famille, zéro plantage, usurpation ou violation. Les codes bruts n'ont pas été supprimés.
L'analyseur ajoute `niveau` : `observation` indique un fait descriptif ou une cause établie ;
`a_expliquer` garde les alertes sans preuve suffisante, notamment les anciens fichiers non enrichis.
Il conserve aussi les cas de recherche avec réponses que le rapport a expliqués : il ne sait pas
déduire automatiquement de simples textes toutes les raisons d'un changement d'objectif.

Corrections communes : un besoin encore urgent ne réarme pas le même appel ; son suivi survit aux
quarante souvenirs. Un résultat de recherche infructueuse survit lui aussi aux souvenirs, avec
`APPEL_OUBLI` et révision par une croyance de lieu nouvelle ; un plan qui vise l'interlocuteur d'un
rendez-vous emploie le lieu convenu. La clé du planificateur porte ces résultats actifs. Aucune
identité ou présence n'est déduite d'une réponse anonyme. Le banc, le récit et l'audit partagent la
lecture des inactivités, sans modifier les besoins ou inventer des ressources.

Le diagnostic des gestes utilise les règles du moteur au début du geste ; il n'est pas une
reconstitution exhaustive de la perception entre tous les instants. Les recherches restent bornées :
« en attente » signifie qu'aucun plan n'a été trouvé sur les croyances, pas une preuve d'impossibilité
absolue. Résultats de la suite, contrôles et comparaison 8 h dans le rapport.
