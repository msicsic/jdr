# Rapport Codex 8 — Luna, noms et appel négocié

Branche `codex-luna-noms`, non fusionnée, issue de `main` **9075aea**. Worktree :
`tmp-worktrees/codex-luna-noms`. Luna reste `gpt-6-luna`, connexion ChatGPT, effort medium.
Toutes les parties utilisent des sauvegardes temporaires ; aucune sauvegarde utilisateur
n'est modifiée. Le coffre du dépôt principal est partagé par `SEUIL_AUTH`.

## Causes et corrections

Les noms inconnus des scripts historiques ne sont pas des noms connus du personnage.
Refuser de choisir ce corps par ce nom est légitime. Ce refus ne justifie toutefois ni
trois réécritures d'un démenti nominal, ni l'invention d'un interlocuteur de remplacement.
Les quatre scripts `*-presentes.json` ajoutent les présentations comme données d'auteur,
sans changer leurs saisies. L'atelier, sans PNJ, reste le contrôle de cette variante.

| Cause commune | Correction |
|---|---|
| Une adresse inconnue sans guillemets passait au MJ ; son démenti citait un nom que le garde refusait | Même refus local que pour l'adresse entre guillemets. Pour les autres questions, si le récit reprend le nom saisi non résolu, clarification du moteur par une désignation publique, sans autoriser ce nom ni révéler un corps |
| Sans adresse imposée, le moteur exigeait la personne d'en face ; autoriser le groupe laissait encore Luna choisir cette personne | `audience_libre` expose trois adresses : individuelle, groupe (`tous`), cantonade (`personne`), même avec des personnes visibles. La contre-revue de fidélité contrôle l'audience, les mots et le contenu sur la copie préparée avant enregistrement. Après deux propositions refusées, précision demandée sans secours qui contourne le refus. Les questions directes choisies comme paroles gardent leurs mots exacts |
| Un verbe de parole sans propos laissait inventer appel et réplique | Demande locale des mots du joueur ; les réponses à un appel en cours restent résolues avant cela |
| Un destinataire qui s'écarte sort du champ, donc disparaît du dossier de l'auditeur | Tous les répondants sont entendus avant le récit, comme l'étaient déjà ceux découverts à la cantonade |
| Une réponse traverse une ouverture mais les interlocuteurs et l'enregistrement exigeaient la même salle | Interlocuteur perçu par la vue ou par sa voix audible ; mêmes auditeurs acoustiques dans l'audit et les faits typés ; lieu réel du locuteur enregistré |
| Plusieurs répliques successives formaient un segment à locuteur unique | La fin d'une phrase citée sépare la phrase suivante ; les incises restent avec leur réplique |
| L'auditeur ajoutait une `presentation` absente de la citation | Rapport illisible redemandé une fois à l'auditeur. Le nom n'est jamais appris à partir de ce champ invalide ; le fait typé forgé reste refusé |
| Le refus de `franchir(poutre)` prétendait manquer d'une échelle | Cible du mauvais type : `RefusDeForme`, qui ne prouve aucune impossibilité du mouvement demandé |
| Une question de faisabilité devenait une parole à un PNJ, notamment après correction d'une action refusée | Même frontière avant et après les corrections : préparer le geste ou préciser ce qui manque ; ne pas faire parler le joueur |
| Le refus public de proximité portait les coordonnées | Coordonnées dans `attendu`, invitation à s'approcher dans le message public |
| Le libellé interne d'approche colorait le récit (« geste d'effort ») | L'approche reste structurée ; libellé public et secours sans cette catégorie technique |

« Tu demandes à passer… » était déjà distingué d'une parole accomplie sur cette base.
Le crépitement d'un objet perçu allumé était déjà autorisé comme ambiance. Ces deux contrats
sont revérifiés, sans ajouter de reconnaissance de formulation ni de consigne d'exemple.

Le contrôle nominal n'est pas assoupli : aucun démenti libre, fragment de citation ou nom
fourni par la question ne permet de nommer un corps inconnu. La clarification du moteur
remplace une réponse qui ne peut résoudre cette référence ; elle n'autorise pas sa prose.

## Vérifications sans modèle

`tests/test_luna_noms.py` couvre les défauts, le cas réel et un autre cas de même nature,
par la boucle console avec fournisseur simulé, sauvegarde puis rechargement : mots exacts,
audience, voix et noms retenus, déplacements, absence de geste exécuté, ambiances et répliques
enregistrées, lieu du locuteur et rendu. La voie de réplique auditée et la voie `parole`
des faits typés sont vérifiées depuis une autre salle. Les questions de faisabilité sont
contrôlées au premier choix, après correction, et face à une question explicitement dite.

Les attentes historiques modifiées portent sur les mots publics sans catégorie d'approche,
la conservation littérale de la casse saisie, l'absence d'appel MJ pour une adresse inconnue,
et le renvoi d'un rapport invalide à l'auditeur. `test_voix_suite` tient compte de la voix
désormais entendue dans la réponse du destinataire : elle reste reconnue dans le noir,
sans perdre le nom que le PNJ a appris du joueur.

Suite complète du gel final : **1 391 tests, 14 ignorés, aucun échec ni erreur**, en
**390,059 s** avec quatre processus à priorité réduite (`artifacts/tests-suite-fidelite.json`).
Les sauts sont ceux des dépendances facultatives. Les suites vertes antérieures restent
intermédiaires ; seule cette passe qualifie la version finale.

Commande : `.venv/Scripts/python.exe tools/tests.py --processus 4` depuis le worktree,
avec l'interpréteur du dépôt principal. Sous Windows, les accès ordinaires hors sandbox sont
nécessaires aux sockets locales des tests web ; `TEMP` et `TMP` sont locaux au worktree.

`tools/comparer_bancs.py --reference 9075aea --empreintes --scenarios relais auberge
--heures 2 --processus 2` : **huit nuits par variante**, graines 1985, 7, 42 et 2024,
départ tiré. Le gel est **identique nuit par nuit** : chronique, mesures et état final complet
(`artifacts/empreintes-fidelite-2h.json`). Les deux variantes sont jouées successivement par l'outil.
Cette identité porte sur les nuits sans saisies ; en interaction, une audience correctement
élargie et une réponse désormais entendue changent les conséquences de la parole du joueur.

## Campagne Luna

Gel fonctionnel **5a04b33**, avec contre-revue des paroles, empreintes des 82 sources dans
`artifacts/gel-final.json`. Campagne finale :
`artifacts/bancs-multi/20261023-114652-16580`, trois passes par variante, lancées ensemble
avec six processus (`avant=9075aea`, `apres=.`). Les 21 scripts représentent 230 saisies
par passe, soit 126 parties et 1 380 saisies pour les deux variantes réunies.

Reproduction depuis ce worktree (interpréteur et `SEUIL_AUTH` du dépôt principal) :
`tools/banc_multi.py --variante avant=9075aea --variante apres=5a04b33 --repetitions 3
--paralleles 6 --connexion chatgpt --max-appels 1000`, suivi des 21 chemins
`tests/data/bancs/<script>.json` énumérés ci-dessous. Le code des deux variantes est
joué par le même lanceur, avec les mêmes préparations d'auteur.

- Quatre références historiques : `relais`, `crypte`, `atelier`, `echanges`.
- Leurs quatre variantes avec présentations préalables.
- `soir-appel`, `soir-noir`, `soir-voix`, `ressources`, `comptes`.
- `noms-dialogue` : répondre sans appel, question collective, passage, écoute et ambiance.
- Six scripts d'appel négocié, avec et sans guillemets : appel puis arrivée ou invitation,
  ou appel initial d'auteur puis question sur la raison.
- `noms-faisabilite` : deux gestes sur des cibles différentes, avec annulation entre les questions.

Les secondes et appels par tour MJ ne comptent que les tours qui font appel au modèle.
Les refus locaux à zéro appel ne sont donc pas dans ce dénominateur. Les relances sont les
réponses refusées puis redemandées par le contrôle narratif ; les refus et tours avec refus
comptent la validation du moteur et la contre-revue, pas le refus social d'un PNJ.
Précisément, les refus sont les événements `validation` du fil, pas chaque verdict négatif
émis par un auditeur. La clarification après deux refus de fidélité d'une parole n'est pas
un repli narratif dans l'outil ; ses quatre occurrences sont donc aussi dénombrées séparément.
Les replis comprennent la clarification de dernier recours d'une faisabilité non préparée.
Une explication de limite admise par l'auditeur n'est pas un repli de contrôle : un compte
nul de replis ne suffit donc pas à prouver qu'un mouvement a été compris ou préparé.

Les **126 parties et 1 380 saisies** sont complètes, sans erreur technique, arrêt de budget
ni échec de rechargement. Les six passes ont abouti. Le gel des sources reste inchangé.
Sur l'ensemble des scripts, la moyenne passe de 100 à 91,33 tours MJ et de 297 à 291,67
appels : les appels/tour passent de 2,97 à 3,19 et les secondes/tour de 11,9 à 13,1.
Les relances narratives passent de 13,33 à 10,33, les refus tracés de 24,33 à 29 et les
tours avec refus de 16,33 à 19,33. Un repli narratif au total de chaque côté. Les quatre
clarifications après refus de fidélité côté branche sont détaillées séparément ci-dessous.
Ces chiffres ne prouvent ni une amélioration générale de la latence ni la disparition des
refus sémantiques erronés.

### Quatre références historiques

Moyenne par passe ; étendue entre crochets.

| Mesure | `main` 9075aea | Branche 5a04b33 |
|---|---:|---:|
| Tours MJ | 38,00 | 33,33 [33,00–34,00] |
| Appels totaux | 117,00 [109,00–123,00] | 93,67 [89,00–98,00] |
| Appels / tour MJ | 3,08 [2,87–3,24] | 2,81 [2,62–2,97] |
| Secondes / tour MJ | 12,60 [12,33–12,94] | 12,06 [10,60–13,72] |
| Tours en repli | 0,33 [0,00–1,00] | 0,00 |
| Relances narratives | 8,33 [6,00–10,00] | 2,00 [0,00–4,00] |
| Refus moteur / contre-revue | 10,33 [9,00–11,00] | 9,67 [9,00–11,00] |
| Tours avec refus | 6,67 [6,00–7,00] | 6,00 |

### Quatre références avec présentations

Moyenne par passe ; étendue entre crochets.

| Mesure | `main` 9075aea | Branche 5a04b33 |
|---|---:|---:|
| Tours MJ | 38,00 | 38,00 |
| Appels totaux | 109,33 [104,00–118,00] | 117,67 [111,00–122,00] |
| Appels / tour MJ | 2,88 [2,74–3,11] | 3,10 [2,92–3,21] |
| Secondes / tour MJ | 11,53 [10,61–12,71] | 12,90 [12,18–14,02] |
| Tours en repli | 0,00 | 0,00 |
| Relances narratives | 2,67 [1,00–5,00] | 4,00 [2,00–5,00] |
| Refus moteur / contre-revue | 8,33 [7,00–9,00] | 11,00 [9,00–13,00] |
| Tours avec refus | 6,00 [5,00–7,00] | 7,67 [7,00–8,00] |

### Autres scripts

Moyenne par passe ; cellules « avant → après ».

| Banc | Tours MJ | Appels / tour | s / tour | Replis | Relances | Refus | Tours avec refus |
|---|---:|---:|---:|---:|---:|---:|---:|
| soir-appel | 5,00 → 5,00 | 2,73 [2,60–3,00] → 3,80 [3,60–4,00] | 10,41 [9,65–11,33] → 14,45 [13,25–15,61] | 0,00 → 0,00 | 0,33 [0,00–1,00] → 0,33 [0,00–1,00] | 0,00 → 1,67 [1,00–2,00] | 0,00 → 1,67 [1,00–2,00] |
| soir-noir | 5,00 → 5,00 | 3,33 [3,20–3,60] → 3,53 [3,40–3,60] | 11,67 [10,74–12,84] → 12,08 [10,84–13,36] | 0,00 → 0,00 | 0,00 → 0,00 | 1,67 [1,00–3,00] → 0,67 [0,00–1,00] | 1,33 [1,00–2,00] → 0,67 [0,00–1,00] |
| soir-voix | 4,00 → 4,00 | 3,25 [3,00–3,75] → 4,75 [3,75–5,75] | 11,91 [10,91–13,52] → 17,55 [13,54–21,20] | 0,00 → 0,00 | 0,33 [0,00–1,00] → 2,33 [1,00–4,00] | 0,33 [0,00–1,00] → 1,00 | 0,33 [0,00–1,00] → 1,00 |
| ressources | 2,00 → 0,00 | 1,00 → 0,00 | 5,06 [4,71–5,47] → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 |
| comptes | 1,00 → 0,00 | 1,00 → 0,00 | 6,02 [5,67–6,28] → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 |
| dialogue | 5,00 → 4,00 | 3,40 [3,00–3,60] → 3,92 [3,50–4,50] | 13,27 [11,07–14,82] → 16,18 [13,21–17,68] | 0,00 → 0,33 [0,00–1,00] | 1,67 [1,00–2,00] → 1,33 [1,00–2,00] | 0,00 → 0,67 [0,00–1,00] | 0,00 → 0,67 [0,00–1,00] |
| faisabilite | 2,00 → 2,00 | 3,67 [3,00–4,00] → 4,50 [3,50–6,00] | 15,53 [13,32–17,75] → 18,15 [14,18–23,45] | 0,00 → 0,00 | 0,00 → 0,33 [0,00–1,00] | 3,67 [3,00–4,00] → 4,33 [3,00–6,00] | 2,00 → 1,67 [1,00–2,00] |
| appels | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 |


Sur les références historiques, le garde nominal relève **18 obstacles dans les récits
de `main`, contre un dans la branche**, sur les trois passes. Ce ne sont pas 18 refus
injustifiés de noms : le refus initial d'une référence inconnue reste légitime. Les
18 obstacles viennent des démentis ou explications qui reprennent les noms des saisies
(trois sur les yeux de Gorm, neuf sur la remise à Ilse, trois sur la question à Ilse,
deux sur Aubin poussé, un sur le passage demandé à Brune). Les redemander ou décrire un
corps en expliquant ce lien manquant ne résout pas la référence. Le repli de `main`
porte sur la remise du bloc de cire à Ilse. Dans la branche, l'obstacle restant est
une vraie faute de narration : « Plus loin, Ilse ajoute… » alors que le nom n'est pas
appris ; le garde la refuse avant affichage, puis la voix est désignée publiquement.
Le contrôle reste donc actif, et le nombre de relances ne se confond pas avec celui
des noms inconnus employés par le joueur.

Avec les présentations, les quatre références ont chacune 38 tours MJ par passe :
**109,33 → 117,67 appels** (+7,6 %), **2,88 → 3,10 appels/tour**, **11,53 → 12,90 s/tour**,
**2,67 → 4 relances narratives** ; aucun repli des deux côtés. Le gain sur les anciens
scripts vient donc largement des références nominales résolues localement ; il ne prouve
pas une baisse générale du coût ni des relances. La revue supplémentaire des paroles a un
coût et les autres jugements sémantiques fluctuent. Les étendues se recouvrent.

### Relecture des saisies demandées

Toutes les occurrences des saisies de la tâche sont relues dans les deux variantes,
avec les propositions et les obstacles du fil, pas seulement le résumé chiffré.

| Saisie / voie | Observation finale côté branche |
|---|---|
| Appel puis « j'arrive », « viens ici », question de raison ; avec et sans guillemets | 18 parties, 36 tours, **zéro appel modèle**, comme sur `main`. Les réponses entendues annoncent l'accord du moteur ; aucune venue n'est inventée par Luna. Les engagements et l'ouïe après recharge sont également couverts par `test_appel_negocie` |
| « je réponds » sans appel | Trois demandes locales de mots, zéro appel ; aucune parole inventée. Avec l'appel en cours, les trois réponses de `soir-appel` restent locales et font entendre « J'arrive ! » |
| « est-ce que quelqu'un a du bois ? » | **Six sur six à la cantonade**, mots exacts ; plusieurs répondants, dont la voix distante. 4 à 7 appels ; `main` garde Aubin seul et réécrit la phrase dans les six cas |
| « Brune, laisse-moi passer » avec nom connu | `echanges-presentes` : 3/5/3 appels, aucun repli ; `noms-dialogue` : **7/5/3 appels, un repli**. Le déplacement est enregistré et rendu. Le premier récit la tait encore, puis prétend ses mots indistincts : la boucle persiste malgré la réponse audible établie |
| « Ilse, tu m'entends ? » | `noms-dialogue` : réponses entendues en 3/3/4 appels. Après les déplacements de `soir-appel`, le refus de perception reste affiché en un appel ; aucune audition n'est inventée |
| Ambiance | `noms-dialogue` : 2/2/4 appels ; la troisième passe relance l'attribution de voix au-delà d'une cloison, puis impose encore une précaution. Les descriptions du brasero dans les références ne sont pas systématiquement interdites. Les deux cas sensoriels après recharge vérifient lumière/allumage et ambiance enregistrée, sans créer d'entité |
| « Tu demandes à passer… » | Le contrôle déterministe ne confond plus intention décrite et parole accomplie ; une contre-revue sémantique refuse pourtant encore « Tu demandes si… » dans `relais-presentes`. La variante avec présentations l'affiche dans une autre passe |
| Passer sous la poutre | Le banc dédié ne répond plus « Il faut une échelle » et ne fait pas parler le joueur. Il explique que le mauvais type de proposition ne tranche pas le passage, ou demande de repérer l'obstacle. **Il ne fournit pas une solution générale de passage dessous**. Le brasero reçoit deux propositions de geste et une réponse de perception |
| Refus public et coordonnées | Aucun « case … du plan » du refus de proximité côté branche ; les coordonnées absolues restent dans `attendu`. Des directions et distances relatives demeurent des informations de perception/mémoire |
| « je m'étire » | Les six sorties d'atelier, référence et variante nominale, décrivent l'étirement sans « geste d'effort » ; l'approche reste enregistrée en données |

La revue de fidélité ajoute **quatre clarifications** après deux propositions refusées :
deux sur « bonsoir, vous tenez le coup ? » et deux sur l'achat d'une planche à Aubin.
L'un des verdicts rejette même `tous` en prétendant que ce serait une adresse individuelle,
après avoir demandé le groupe : c'est un faux refus sémantique. Les achats sont refusés car
la proposition ne fait que parler et ne réalise pas le transfert demandé. Rien de ces
propositions n'est appliqué ; ces interactions n'aboutissent cependant pas au résultat voulu.
Le choix d'audience est mieux contrôlé, **pas garanti pour toute formulation**.

Les données locales de cette campagne sont dans `mesures-detaillees.json`,
`completude.json`, `refus-narratifs.json`, `textes-cibles.txt` et `relecture-finale.txt`
du dossier de campagne ; chaque partie possède aussi son fil JSON/HTML intégral.

## Incidents intermédiaires

La première passe sous sandbox échoue immédiatement sur l'accès réseau et n'est pas une
référence Luna. Les trois passes saines initiales de neuf scripts sur une archive de `main`
(`artifacts/luna-noms-reference/artifacts/bancs-multi/20261023-093415-52100`) servent au
diagnostic, pas aux mesures avant/après finales.

La première suite complète sous sandbox bloque les sockets locales des tests web
(`WinError 10013`) ; les deux travailleurs TUI non terminés sont arrêtés précisément,
sans toucher aux autres processus. Cette passe signale aussi les anciennes attentes de
libellé et de reconnaissance de voix, corrigées. Elle n'est pas comptée comme verte.
La suite est relancée avec les accès Windows normaux et la priorité réduite.

Le lot `20261023-101233-49060` s'interrompt côté référence après les quatre scripts historiques :
les scripts nouveaux étaient cherchés relativement à l'ancienne copie de `main`.
`banc_multi` résout maintenant les chemins dans le dépôt du lanceur avant de changer de copie.
La reprise `20261023-102240-14368`, puis le lot `20261023-102925-26140`, restent intermédiaires :
la relecture révèle la question de faisabilité transformée en parole, puis le même détour
après correction d'une action. Les seuls enfants Luna de ces lots sont arrêtés et leurs
traces conservées. Ils ne remplacent aucune passe du gel final.

Le lot `20261023-103711-55244` est également intermédiaire : les quatre références avec
présentations donnaient 113,67 → 120,33 appels par passe (+5,9 %). La relecture établit que
des questions descriptives au MJ étaient plus souvent prononcées à un PNJ. Les mots de
toutes les questions avaient été exposés comme paroles annoncées dans `parole_prevue`.
Le gel `db778aa` retire cette donnée de l’interprétation : seuls les mots explicitement
annoncés y figurent ; la formulation directe est encore imposée au moment de valider une
parole effectivement choisie. Les passes encore actives de ce lot sont arrêtées et le
comparatif final reprend les deux variantes ensemble, sans réutiliser ces mesures.

Le lot complet `20261023-110117-50428` (126 parties) révèle encore six questions collectives
sur six adressées à Aubin seul. Autoriser `tous` ne garantissait pas la fidélité du choix.
Cette campagne n'est donc pas la qualification finale. La contre-revue commune est étendue
aux paroles sans adresse imposée ; le contrat distingue aussi le groupe de la cantonade
sans destinataire particulier. Le pilote `20261023-114032-18116` donne six questions sur six
prononcées à la cantonade, avec leurs mots exacts et plusieurs répondants audibles ; quatre
premiers choix de groupe sont corrigés avant affichage. Le comparatif complet repart sur
les deux variantes ensemble après ce pilote.

## Limites

Le choix sémantique d'une audience implicite et le classement des affirmations restent
ceux de Luna. Le moteur valide les destinataires et ce qui est effectivement audible ;
il ne dispose pas d'un analyseur sémantique déterministe de toute phrase française.
La contre-revue peut se tromper ; comme pour les actions, deux rapports de revue illisibles
laissent passer un plan déjà validé mécaniquement. Un verdict négatif, lui, ne peut être
contourné par le secours local.
Les noms saisis sans lien nominal restent inutilisables pour cibler un corps.

Des refus sémantiques erronés restent observés dans les variantes avec présentations :
une fois « Tu demandes si tu peux passer… » est compris comme une parole prononcée,
alors que `parole_racontee` ne le classe pas ainsi ; deux répliques autorisées d'Ilse sont
jugées impossibles faute d'`objet:ilse` perceptible, malgré sa présence dans les répondants
audibles. Une demande de Brune (« Alors qu'on le garde allumé ») est aussi prise pour un
engagement personnel. Les données communes et les contrôles déterministes sont renforcés,
mais **l'absence de ces faux refus n'est pas garantie**. Aucun contournement par une
formulation, un personnage ou une classe de fait n'est ajouté. Les deux premières passes
de description d'ambiance historiques relancent encore des bruits de mouvements ou une
affirmation exclusive de silence ; cela ne prouve pas une interdiction générale de l'ambiance.

Corriger une erreur de type de proposition ne fournit pas une mécanique générale de tout
mouvement physique. Le moteur ne prétend plus qu'une échelle est nécessaire pour un autre
geste, et ne transforme plus la question en parole. Si Luna ne prépare aucun geste fidèle,
il demande une précision au lieu de prétendre avoir démontré une impossibilité physique.
Ce dernier recours reste une limite de compréhension, comptée dans les replis.

Une même question collective peut obtenir plusieurs réponses, dont une voix distante non
identifiée. Ce n'est ni une présentation ni une localisation visuelle de cette personne.
Les mentions lexicales du banc comprennent des mots du joueur dans les refus et ne mesurent
pas directement les fuites ; les garde-fous déterministes et les textes sont contrôlés séparément.
Trois passes décrivent cet échantillon, sans garantir l'absence future de refus sémantiques erronés.
