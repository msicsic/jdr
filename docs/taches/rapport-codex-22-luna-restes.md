# Rapport Codex 22 — les restes de Luna

Branche `codex-luna-restes`, **non fusionnée**, issue de `main` **8855312** ; tâche portée par
`ac32a29`. Worktree `tmp-worktrees/codex-luna-restes`. Commits de code signés SSH : **8a93408**,
puis **768bae6** et **24324f7** (code mesuré à la livraison). Signatures SSH vérifiées avec la
clé publique locale (`G`).
`main` n'a ni été changé de branche ni reçu de commit de ce lot.

Luna reste **gpt-6-luna**, connexion ChatGPT, effort medium. `SEUIL_AUTH` pointe vers
`C:\Users\msics\donjon\.seuil-auth`. Toutes les parties utilisent des copies temporaires ;
aucune sauvegarde de `sauvegardes/` n'est utilisée. Deux passes Luna simultanées par campagne.
Tests et empreintes à priorité réduite, trois processus au plus. Aucun banc moteur autre que
les empreintes de 2 h. Aucun changement de `planification.py`, `deliberation.py`, `signes.py`,
de la commande `observer`, des données des scénarios ni du coût des routes.

## 1. Forme d'un obstacle et descriptions physiques

**Cause lue dans les fils.** Référence 8855312, `sous-obstacle-inconnu`, passe 2 : refus de
revue « aucune description de la poutre effondrée n'établit qu'elle forme ce passage » ;
quatre appels avant le manque du moteur. La passe 1 révèle aussi un défaut distinct :
`degagement_cm=35`, `hauteur_cm=35`, puis 36/35 ; deux propositions incohérentes, sans forme
enregistrée, et « Le dessous ne peut pas être au-dessus du sommet » comme réponse.

L'ancienne revue autorisait explicitement une information nouvelle pour le contenu mais
exigeait encore une description préalable pour la géométrie. Elle ne recevait pas la
description `physique` déjà connue. Les valeurs numériques pouvaient être soumises à une
revue avant leur validation par le moteur. Enfin, même une qualification juste impliquait une
nouvelle interprétation du geste : quatre appels au minimum avec les deux revues.

**Invariant et décision.** Une description physique inconnue peut être établie par le MJ,
si elle est plausible pour l'objet et compatible avec ses propriétés connues. Son absence
n'est pas une contradiction. Le résultat souhaité ne prouve pas cette description. Le moteur
valide les bornes, la masse quand elle est déterminée, l'ancrage et l'absence de réécriture ;
la plausibilité par rapport au nom et au texte reste sémantique. Aucune forme favorable n'est
déduite automatiquement du nom d'un obstacle.

Une précondition physique inconnue est typée `refus.ProprieteInconnue` ; les qualifications
automatiques existantes (`moteur.QualificationRequise` : coupe, son, lumière) en dérivent.
Une question explicite de faisabilité reçoit immédiatement ce manque si Luna propose le
geste ; les autres refus restent corrigeables. Ainsi un lien disponible mais omis pour une
échelle peut toujours être ajouté à la proposition corrigée.

Luna peut aussi proposer `etablir_faits` avec `ajouts` et une `suite`, le geste demandé.
Les deux propositions restent validées séparément : faits sur copie, revue physique, préparation
et revue de fidélité du geste sur cette copie. Les faits sont enregistrés avant la fiche.
Pour une question de faisabilité, ce format évite une deuxième interprétation ; il ne crée
pas de nouveau mode et n'escamote aucun contrôle. Il vaut pour tous les faits. Une question
n'exécute toujours rien. Les anciennes propositions sans suite gardent leur réexamen existant.

**Fonctions.** `coherence_physique.propositions` transmet les propriétés physiques connues
et les `champs_a_etablir` ; sa revue juge la compatibilité d'une information nouvelle.
`mj._appeler` valide d'abord les faits sur copie ; `mj.sans_suite`, `_echanger`,
`_echanger_prepare` composent les deux validations. `matiere.SCHEMA_PASSAGE` précise le même
repère de sol pour le dégagement et le sommet. `obstacles.conditions` type le manque ; aucune
fonction de parcours ni de coût n'est modifiée.

**Cas après rechargement.** Poutre effondrée du Relais et longue table de l'auberge sans
forme : manque en un appel, sans temps ni déplacement. Qualification proposée avec sa suite :
trois appels exactement (interprétation, physique, fidélité), dimensions sauvegardées avant
la fiche, puis passage et examen après recharge ; obstacle toujours bloquant. Dimensions
impossibles refusées avant revue physique, sans ajout. Même contrat pour le son et la lumière
inconnus de la ficelle ; qualification sonore d'une hache et geste suivant, sans réinterprétation.

## 2. Fidélité de la parole

**Causes lues dans les fils.** Les deux passes nouvelles de référence acceptent la question
à la cantonade de `noms-dialogue` ; le faux refus historique n'y est pas reproduit. Les fils
conservés de `codex-luna-noms`, campagne `20261023-114652-16580`, le montrent précisément :
`apres-r1/…-echanges-presentes.json`, « bonsoir, vous tenez le coup ? », seconde revue :
« le plan l'adresse à “tous” individuellement ». Dans `apres-r2/…-soir-appel.json`, l'achat
d'une planche est refusé parce que le plan « ne transfère ni les trois pièces ni une planche » ;
la passe 3 répète ce jugement. La revue recevait les mots et le contenu typé d'une parole,
mais pas les conséquences calculées par le moteur ; un booléen et un motif libre pouvaient
requalifier une référence dont le sens était pourtant déterministe.

**Invariant.** Le moteur décide ce que signifient `tous` et `personne`, qui entend, qui répond
et ce que produit une demande. La revue compare la demande et les propositions sémantiques,
sans refaire ces calculs. Elle renvoie désormais les `audiences_fideles` à la demande et un
`contenu_conforme` séparé. Le moteur compare lui-même l'adresse proposée à ces audiences ;
un motif libre ne peut pas transformer `tous` en individu. Chaque refus a sa propre cause
et son `attendu` : audience, ou mots/contenu.

La première campagne sur 768bae6 a révélé un autre faux refus de ce même contrat : le code
`chaleur`, pour une question sur du bois, a été lu comme un changement de sujet. Le sens de tous
les contenus et des codes de ressource est désormais une donnée commune du schéma et de la revue
(`SENS_CONTENU`, `RESSOURCES_DEMANDEES`, `sens_contenu`), sans supposer que le destinataire possède
la ressource. Cette campagne a aussi fait inventer deux fois par l'auditeur une présentation
« Gorm » absente de la citation : le moteur écarte maintenant la seule métadonnée non fondée,
sans apprendre ce nom ni faire réécrire une réplique contrôlée. Une présentation explicitement
proposée comme fait typé sans les mots correspondants reste refusée. Ces correctifs sont vérifiés
sur la faim et le combustible, et sur Gorm et Aubin inconnus après rechargement.

**Fonctions.** `mj._verifier_fidelite_parole` joint destinataires, répondants et
`consequences_moteur` calculées sur copie. `couverture_action.schema`, `entree`, `verifier`
séparent les deux jugements ; les références reçoivent leurs noms publics et les mots libres
restent littéraux. Une demande payée n'a pas à contenir une opération de transfert faite par
Corvus : les conséquences du moteur disent la vente, la remise, le service différé ou le refus.

**Cas après rechargement.** « est-ce que quelqu'un a du bois ? » et « qui peut nous aider ? »,
à `personne` et à `tous` : une seule revue, mots exacts, auditeurs et destinataire enregistrés.
Achat d'une part de planches et de vivres à Aubin : conséquences réellement transmises à la
revue, trois pièces payées ; la planche prélevée est portée, les vivres promis ne sont pas
fictivement consommés ni remis.

## 3. Localisations en cases ou coordonnées

**Causes lues dans les fils.** Référence : atelier, « plusieurs cases » ; crypte, trousse de
crochets « trois cases au sud et une à l'est » ; échanges, vieil homme « à une case vers le
sud ». `localisation.relatif` fabriquait ces phrases pour les objets et les souvenirs.
Les sorties connues conservaient leur tableau `case` alors que les positions des objets et
du joueur étaient retirées du paquet MJ. La consigne disait encore « case par case ».

Le refus de proximité « case 5, 11 du plan » était déjà corrigé dans la base 8855312 : le
message public invite à s'approcher, les coordonnées restent dans `attendu`. Il ne fallait
pas le réintroduire via un contexte relatif ni dans un repli. Le refus d'un franchissement
sans sol décrit ne parle plus de « sol décrit en cases ».

**Invariant.** Le quadrillage est une représentation interne. La fiction donne des repères,
directions et distances physiques. `localisation.relatif` produit des mètres (le plan a une
unité par mètre) ; `_echanger` remplace aussi la position brute d'une sortie par ce repère.
Le contrôle déterministe existant de la voix d'auteur est étendu au vocabulaire du quadrillage
et aux écritures de coordonnées : récit, répliques, justifications et ajouts persistants.
La carte technique garde ses axes et sa légende ; elle n'est pas le récit.

**Fonctions.** `narration.unites_moteur`, `voix_auteur`, `mentions_proposees`, `consigner` ;
`verifier_unites` est également appelé à l'écriture par `faits_locaux.preparer_faits`,
`enrichissement.preparer_complements`, `connaissances.preparer_savoirs`. Le nom d'une pièce
physique est contrôlé aussi. Le même contrôle à la proposition et à l'enregistrement empêche
qu'un texte refusé devienne visible après recharge.

**Cas après rechargement.** Planches et briquet hors de vue, positions mémorisées réelles,
repères différents : le texte sauvegardé reste en mètres et l'objet ne bouge pas. Texte en
cases, paire `(5, 11)`, tableau `[2, 4]`, axes `x=3, y=7` : refus, reformulation, seul le texte
admis persiste. Audit altéré et ajouts directs (détail, parole, portrait, savoir) : refus à
l'écriture, aucun changement et aucune description contaminée après recharge.

## 4. Ambiance et précaution qui la dément

**Cause lue dans les fils.** Référence, Relais, passe 1 : les bruits de mouvements sont refusés
faute d'attestation ; la révision donne « Tu ne perçois pas d'autre ambiance sonore particulière ».
Passe 2 : refus pour un son non établi et pour une absence exclusive d'autres sons. La règle de
révision demandait indistinctement de dire que Corvus ignore un ajout non établi, sans réserver
cette inconnue à l'état mécanique. Une contradiction pouvait être déclarée sans source.

**Invariant.** Une absence dans le contexte ne prouve pas le contraire. Une ambiance compatible
avec l'état est libre, perçue et enregistrée avec son lieu. Une réserve qui affirme qu'elle est
imperceptible la contredit. La révision distingue cette liberté sensorielle de l'inconnue
mécanique. Le rapport de l'auditeur doit citer un fait fourni pour un verdict `contradictoire` ;
sans source il est redemandé à l'auditeur, sans demander au MJ de réécrire une ambiance admise.

**Fonctions.** `narration.controler`, `INSTRUCTIONS_AUDIT`, `INSTRUCTIONS_REVISION`,
`REGLE_NARRATION` ; boucle de rapport illisible existante dans `mj._appeler`.

**Cas après rechargement.** Bruits lointains et odeur de terre : une contradiction sans preuve
retourne à l'auditeur, le texte initial reste inchangé, l'ambiance est enregistrée avec le lieu,
aucun objet mécanique n'est créé. Le script supplémentaire `luna-restes-ambiance` examine deux
descriptions sensorielles puis la localisation d'un obstacle après s'être tourné.

**Résultat partiel sur ce quatrième constat.** Le complément final, passe 1, garde exactement
« aucun autre son n'est attesté ici » après une description de calme. Au Relais, une odeur est
aussi suivie d'une réserve sur son origine ; l'autre passe refuse de préciser une odeur faute
d'indication. Le contrôle est renforcé, mais **l'absence générale de précaution d'ambiance n'est
pas garantie et ce critère n'est pas entièrement atteint**. Le classement sémantique laisse
encore passer une réserve de preuve comme une phrase sensorielle. Ce résidu reste dans « À revoir ».

## Vérifications et mesures

### Suite et empreintes

- `tools/tests.py --processus 3` sur **24324f7** : **1 591 tests, 15 ignorés, aucun échec**, 648,777 s.
  Quatorze méthodes nouvelles dans `tests/test_luna_restes.py`, avec plusieurs cas par méthode ;
  fixtures existantes accordées au nouveau rapport de fidélité et aux repères en mètres.
  Résultat : `artifacts/luna-restes/tests-complets-livraison.json`.
- `tools/comparer_bancs.py --reference 8855312 --empreintes --heures 2 --scenarios relais mine
  auberge crue --graines 1985 7 42 2024 --processus 3` : **16 nuits par version, chronique,
  mesures et état final complet identiques nuit par nuit**. Référence puis branche, priorité
  réduite. Résultat : `artifacts/luna-restes/empreintes-2h-livraison.json`. Même identité sur
  768bae6 avant les derniers correctifs de lecture. Aucune donnée de forme de scénario n'a changé.

### Luna avant → livraison

Deux passes simultanées de chaque variante, référence puis branche, `banc_multi --connexion chatgpt
--repetitions 2 --paralleles 2 --max-appels 650`, `--fil` dans chaque partie. Référence **8855312**,
livraison **24324f7**. Pour la référence, `preparer_variante` du lanceur était redirigé vers son
worktree détaché local sous `tmp-worktrees` ; `SEUIL_CODE` pointait bien vers 8855312. Le résumé
de cette campagne affiche donc `avant=.` sans désigner le code de la branche. La livraison utilise
le lanceur standard et `livraison=HEAD`, résolu et figé avant les passes.

Moyennes par passe. Appels et secondes par tour MJ ; replis, relances et refus par passe. Les
15 scripts communs sont comparés ensemble ; le complément est séparé pour garder le même périmètre.

| Banc | Tours MJ avant → après | Appels / tour | s / tour | Replis | Relances | Refus moteur/revue |
|---|---:|---:|---:|---:|---:|---:|
| **15 scripts communs** | 60 → 59 | **3,06 → 3,04** | **12,46 → 12,09** | 0 → 0,5 | 7 → 6 | 21,5 → 23 |
| 4 références | 34 → 33 | 3,13 → 3,15 | 12,58 → 12,80 | 0 → 0 | 5 → 3 | 12,5 → 15,5 |
| noms-dialogue | 4 → 4 | 3,50 → 3,00 | 16,15 → 12,67 | 0 → 0 | 1 → 0 | 0 → 0 |
| soir-appel | 5 → 5 | 3,90 → 3,40 | 14,34 → 12,14 | 0 → 0 | 0 → 0 | 2 → 0,5 |
| soir-noir | 5 → 5 | 3,50 → 4,30 | 13,24 → 14,76 | 0 → 0,5 | 0 → 2 | 0,5 → 0,5 |
| 7 sous-obstacle | 10 → 10 | 2,10 → 1,90 | 9,44 → 8,11 | 0 → 0 | 0,5 → 0 | 6,5 → 6,5 |
| dont forme inconnue | 1 → 1 | 3,00 → 1,00 | 15,38 → 5,89 | 0 → 0 | 0,5 → 0 | 0,5 → 1 |
| force-4c-fuir | 2 → 2 | 2,50 → 3,00 | 11,38 → 12,26 | 0 → 0 | 0,5 → 1 | 0 → 0 |
| complément ambiance | 3 → 3 | 2,33 → 2,67 | 13,18 → 11,28 | 0 → 0 | 0,5 → 1 | 0 → 0 |

Le coût global est **stable**, sans gain général démontré sur deux passes. Le manque physique
immédiat est maintenant tracé comme refus du monde ; la référence avait notamment deux
qualifications numériques invalides sans trace de validation dans sa passe 1. Les refus ne
mesurent donc pas, à eux seuls, une régression de la jouabilité. Les temps restent indicatifs
sur le poste partagé ; même concurrence Luna (deux passes), autres travaux à priorité réduite.

### Textes et états relus

- **Aucune unité du quadrillage ni coordonnée dans les sorties finales**, contrôle déterministe
  et relecture des textes. Aucun `attendu` affiché, aucune erreur technique, aucun budget épuisé,
  aucune erreur de rechargement dans les 32 parties finales.
- `sous-obstacle-inconnu` : **1 appel dans chacune des deux passes**, 5,79 et 6,00 s, réponse exacte
  du moteur sur le dégagement et la hauteur inconnus. Position `[4, 3]`, temps inchangé, aucune
  forme enregistrée ; « tenter » n'a aucune proposition à exécuter. Le chemin d'établissement
  avec suite en trois appels est prouvé en chaîne simulée, pour deux obstacles et une autre
  propriété physique ; la campagne finale n'a pas choisi ce chemin sur la forme inconnue.
- Passages connus : fiches en deux appels, 12 s sous la poutre et la table, 6 s pour enjamber le
  lit ; après « tenter », respectivement `[6, 3]`, `[6, 4]`, `[2, 0]`, 120 ou 60 dixièmes. L'obstacle
  reste bloquant et les dimensions sont encore lisibles après recharge. Trop bas, trop haut,
  encombrant : raisons du moteur, sans mouvement ni nouvelle forme.
- `noms-dialogue`, question sur le bois : **4 appels, aucun refus ni relance, deux fois sur deux** ;
  l'une des passes choisit le groupe, l'autre la cantonade, tous les répondants sont enregistrés.
  Dans `soir-appel`, une des deux passes corrige encore une audience individuelle avant de parler :
  la bonne interprétation de toute question collective n'est pas garantie.
- Achat de planche : accepté en quatre appels, deux fois sur deux, trois pièces prises et remise
  annoncée par l'engagement réel. Au pas suivant, « Aubin te remet les planches de bac : tu l'avais
  payé », et la planche apparaît dans les affaires portées de l'état rechargé. Aucun faux refus
  « le plan ne produit pas le transfert » dans ces deux passes.
- Les descriptions d'ambiance de la conduite passent en deux appels, deux fois sur deux. Le
  complément conserve cependant la réserve de preuve citée au constat 4 : critère partiel.
- Le seul repli final est `soir-noir`, « C'est moi, Brune », passe 1 : sept appels. L'auditeur
  classe d'abord contradictoire l'obscurité qu'il reconnaît compatible dans son propre motif ;
  le garde nominal refuse ensuite « la voix toute proche qui se dit Ilse » comme désignation
  d'une voix inconnue. Le joueur reçoit le fait sûr du moteur : « Une voix qui se dit Ilse sait
  que tu n'es pas “Brune”. » La passe 2 réussit en trois appels. Ce problème de désignation modulée
  demeure ; aucune exception de formulation n'est ajoutée.
- Autres faux refus encore vus : caractère joyeux d'un sifflement ; « bobine de ficelle solide »
  jugée différente de « bobine de ficelle » ; confusion entre un nom saisi non relié et le corps
  visible dans « je pousse Aubin » (6 et 11 appels). Ils expliquent une part des relances des
  références et ne sont pas présentés comme résolus.

Campagnes brutes, non versionnées :

- Référence 8855312, 15 scripts × deux passes : `artifacts/bancs-multi/20261023-211130-21668`.
- Complément de référence : `artifacts/bancs-multi/20261023-212802-14360`.
- Correction intermédiaire 768bae6 : `artifacts/bancs-multi/20261023-214401-20356`.
- Livraison **24324f7**, 16 scripts × deux passes : `artifacts/bancs-multi/20261023-220538-8360`.
- Mesures détaillées et relecture : `artifacts/luna-restes/mesures-completes.json`,
  `relecture-finale.txt` ; chaque partie garde aussi son fil JSON/HTML intégral.

Les 15 scripts prescrits sont les quatre références, `noms-dialogue`, `soir-appel`, `soir-noir`,
les sept `sous-obstacle-*` et `force-4c-fuir`. Toutes les passes gardent `--fil`.
Les deux passes de chaque variante sont lancées ensemble ; référence puis correction.
Une première campagne de correction intermédiaire a été interrompue après la découverte d'une
distinction nécessaire entre propriété inconnue et outil disponible omis ; elle est exclue des
chiffres finaux. La première suite sous sandbox a également été interrompue : tests web bloqués
par les sockets locaux et attentes anciennes de distances en cases ; la suite finale est relancée
avec les sockets autorisés et les mêmes trois processus à priorité réduite.
La campagne intermédiaire complète a eu un incident réseau de 226 s pendant une narration de
`noms-dialogue`, en plus des défauts de métadonnées traités ensuite. Elle est conservée mais
n'entre pas dans le tableau de livraison. Aucun incident technique dans la dernière campagne.

## Limites

- La plausibilité d'une description physique et la compatibilité avec le texte existant restent
  sémantiques ; le moteur ne déduit pas la géométrie du nom, et ne garantit pas la justesse de toute
  invention de Luna. Les dimensions incohérentes et une propriété déjà établie sont refusées.
- Le choix des audiences fidèles et le sens du contenu restent des jugements sémantiques.
  Leur comparaison avec l'adresse calculée est déterministe ; citer une conséquence du moteur
  n'empêche pas toute mauvaise lecture de l'auditeur.
- Exiger une source d'une contradiction empêche le rapport vide de preuve de faire réécrire le MJ.
  Une source citée à tort ou une invention mécanique classée comme ambiance reste possible.
- Le contrôle des unités couvre le vocabulaire technique et les écritures usuelles de coordonnées ;
  il peut aussi refuser une occurrence littéraire de ce vocabulaire. Il ne prouve pas la vérité
  sémantique de toutes les distances formulées en mots ou en mètres.
- Trois appels est le chemin d'une qualification physique valable avec sa suite, pas une borne
  absolue en présence d'erreurs du MJ, d'un rapport illisible ou de faits nécessitant d'autres revues.
  Les résultats Luna ci-dessus doivent être lus avec les cas effectivement observés.
