# Valeur du LLM dans Le Seuil — conception du lot 288

29 octobre 2026. Branche `codex-valeur-llm`, **non fusionnée**, base
`c90cbea`. Lecture et conception seulement. Ce document révise l'ordre du
[lot 287](conception-refonte-mj.md), avec les décisions transmises dans le
brief 288 puis celle du récapitulatif joueur. Il ne modifie ni le contrat
actuel du MJ ni le jeu. Les interfaces, garanties et nouveaux contenus
décrits ci-dessous sont des travaux proposés, pas des fonctions livrées.

## 1. Direction de game design et décisions acquises

**Rendre les gestes courants directs ; réserver Luna aux intentions dont la
formulation libre ouvre un choix de jeu.** Choisir une cible déjà visible,
ouvrir une porte ou proposer un prix ne demande pas nécessairement un modèle.
Le moteur possède déjà une part importante de la richesse sociale : ressources
rares, croyances, confiance, besoins concurrents, engagements et refus motivés.
Luna apporte surtout une façon d'exprimer et de combiner ces possibilités,
puis d'en proposer de nouvelles dans les limites de leurs règles.

Une interaction n'est pas meilleure parce qu'elle accepte une phrase longue.
Elle l'est si le joueur peut choisir une approche, comprendre l'enjeu et
observer une conséquence persistante. Un menu peut offrir un marché complexe ;
une réplique très naturelle peut ne produire que `propos`. Le coût à comparer
est celui de l'accès à ce choix, avec ou sans langage libre.

Décisions déjà prises, à porter dans G0 sans les remettre au vote :

- L'ambiance est secondaire, correcte et non bloquante ; elle reste différée
  tant que son contrôle n'est pas terminé. Une sortie visant un lieu quitté
  est jetée ; terminal et web indiquent son calcul en cours.
- Les répliques à contenu typé sont formulées par le moteur, option A.
- Une saisie libre nécessite nominalement un appel bloquant, avec corrections
  bornées utiles. Une entrée structurée n'a pas à être recompilée par Luna.
- **Fidélité : option c avec b en filet**, décision transmise pendant le lot.
  Une ligne moteur expose le plan compris. Paiement, offre, avis, enfermement,
  violence et autres actes lourds ou irréversibles issus du texte libre sont
  montrés avant exécution, selon `tenter/annuler`. Pour le reste, exécution
  puis ligne de résultat. Un clic n'ajoute aucun contrôle de fidélité.
  Pendant la transition, contre-revue et fidélité de parole restent seulement
  sur les actes à effets ; leur retrait se décide sur mesure.
- La revue d'une propriété inventée se fait uniquement à son admission quand
  sa compatibilité n'est pas calculable par le moteur.
- `origin/prompt-simplifie` reste la base à porter lot par lot ; la négociation
  de mission reste une épreuve obligatoire. Luna reste `gpt-6-luna`, sans
  comparaison de modèles.

## 2. Inventaire des interactions et interfaces

Sources de l'inventaire : `moteur.ACTIONS`, `operations.OPERATIONS`, le schéma
assemblé par `MJ._echanger`, `paroles.TYPES_JOUEUR`/`SENS_CONTENU`,
`commandes.analyser`, `paroles.analyser`, `dialogues.commande_sociale`, la
boucle de `jeu.py`, `scene.scene_percue`, et [les mécaniques](mecaniques.md).
Certaines sections anciennes des mécaniques parlent encore de comparaison
ou présentent les échanges comme limités aux missions : le code actuel des
propositions et paroles prévaut pour cet inventaire.

| Famille et vocabulaire couvert | Meilleure interface | Limite et rôle du libre |
|---|---|---|
| Lire le jeu : regarder, carte, fiche, inventaire, journal, contexte, lumière, accords ; sauver/quitter/aide | Directe : panneaux, touches, commandes | Aucun appel ; ne pas confondre information publique et debug `etat/esprit` |
| Se situer : aller, marcher, chasser, faufiler, tourner ; attendre/patienter | Directe : carte, touches, durée choisie | Le chemin ne connaît que le sol connu ; aucune garantie d'arrivée ou de tranquillité |
| Percevoir : examiner, toucher, lire, écouter, observer les signes | Directe : cible et modalité | Ne pas transformer « peut-elle attaquer ? » en lecture de son agenda privé ; une propriété réellement absente peut nécessiter admission |
| Manipuler : prendre/poser, deplacer/prelever, détacher, ouvrir/fermer, verrouiller/déverrouiller, crocheter, caler/bloquer/débloquer, copier | Directe : cible, outil et destination ; choix explicites | Libre utile pour désignation inhabituelle ou séquence ; les règles d'accès, propriété et risque restent communes |
| Ressources et sons : allumer/éteindre/alimenter, manger, emettre_son, héler, répondre à un appel | Directe : outil, combustible, quantité ou destinataire public | « Siffler » est borné ; improviser un air particulier peut garder le libre, sans inventer un effet sur l'auditeur |
| Fabriquer et franchir : assembler, decouper ; installer/franchir/désinstaller, franchir_obstacle/passer_obstacle, soulever/appuyer, sauter | Directe pour une recette ou un passage déjà qualifiés ; composée pour une approche originale | Formulaire de dimensions et matériaux pour la recette connue ; le LLM propose l'approche nouvelle, jamais une physique nouvelle |
| Corps et opposition : pousser, ranimer, saisir, ligoter/délier/libérer, traîner, frapper/couper/tuer, fuir/riposter/se_rendre/degager ; méthode assommer | Directe : cible, geste, outil, direction, risque annoncé | « Enfermer » est un objectif composé ; « traîner dans la crypte » contient plusieurs pas. Une improvisation ne doit pas contourner les bornes de violence |
| Économie : acheter/remettre/donner, offre/négocier/accepter/refuser une mission, réclamer un dû | Directe : bien, destinataire, montant, accord visible | « Négocier 25 » est déjà local ; argumenter sur plusieurs contreparties justifie le libre, pas la simple saisie d'un nombre |
| Paroles typées : nom/qui, localisation/ressource, demande/passage, aveu, affirmation, avis, proposition | Dialogue ; raccourci direct pour l'acte et les paramètres usuels | Dire une croyance, demander un objet ou mentir sur un lieu est déjà jugé par le moteur. Le menu ne doit pas révéler les possessions cachées ou les croyances privées |
| composer (1 à 6 étapes), objectif et manière ; improviser | Composée : texte libre, plan visible | LLM utile pour décomposer, conserver les clauses, proposer des effets bornés ; valider puis revalider chaque étape |
| enrichir_joueur, enrichir, enrichir_savoirs, etablir_faits et suite | Libre ciblé ; proposition typée avant affichage | Création persistante, budgets et provenance ; aucun pouvoir de donner un indice ou un outil interdit |
| Conversation ouverte et `propos`, souvenirs, motivation, récit adressé à un PNJ | Dialogue libre | Effet ouvert non automatiquement simulé ; séparer paroles entendues, croyance adoptée et vérité |
| Ambiance : aspect, odeur, bruit de fond, impression | Demande facultative, réponse en fond | Ne crée aucune entité mécanique ; un détail ciblé passe par la matérialisation commune |

`clarifier` et `impossible` sont des issues d'interprétation, pas deux nouveaux
gestes à ajouter à un menu. `compte_rendu` existe dans le transport PNJ ; le
protocole joueur l'exclut encore. De même, A5 a des mandats internes, mais
`mandat` n'est pas un type de `TYPES_JOUEUR` à cette base.

### Le menu actuel et le prix des ajouts

`page.html:gestes/gestesPorte/choixCase` propose examiner ; sur un personnage,
observer et parler ; lire un motif ; allumer/éteindre un luminaire ; manger ;
ouvrir/fermer un contenant ; prendre un objet mobile. Sur une porte : ouvrir,
fermer ou déverrouiller/crocheter selon son état connu. Il propose aussi aller
ici et regarder dans une direction. La marche approche avant un geste de
contact et s'arrête notamment à l'apparition d'une personne. Les boutons
`tenter/annuler`, panneaux et touches complètent ce menu.

**Le menu annonce un verbe, pas une preuve de faisabilité.** Il construit une
commande textuelle ; le moteur tranche ensuite. Crocheter ne choisit pas
encore un outil. « Parler » appelle le MJ en ligne. Examiner un PNJ sans
portrait, ou une action nécessitant une qualification, peut appeler Luna.
Enfin `jeu.py:conclure` peut raconter par Luna un résultat de commande locale :
zéro interprétation n'est donc pas aujourd'hui zéro appel bloquant.

| Ajout proposé | Coût et dépendance, par lot de 30–45 min | Ce qui ne peut être promis au clic |
|---|---|---|
| Poser, toucher, écouter, remettre, actions d'inventaire | Faible : gestes existants, inventaire public, destinataire explicite ; séparer inventaire et carte | Ni don d'un objet absent ni écoute à travers une porte sans portée réelle |
| Outil/destination/combustible pour un geste | Moyen : descripteur d'action public commun, choix parmi ressources connues, validation finale | Ne pas envoyer les préconditions secrètes au navigateur ; un refus public peut rester nécessaire |
| Corps et violence | Moyen par famille : choix de méthode, risque et fiche existante | Ni nouvelle tactique automatique ni effet garanti ; les confirmations de risque existantes restent |
| Recette, passage et dimensions déjà connus | Moyen par famille : formulaire depuis le dossier moteur | Si une propriété manque, une admission reste distincte ; ne pas inventer une mesure pour activer le bouton |
| Demander passage/ressource, identité, localisation, dû, prix | Moyen par famille : entrée sociale structurée commune, émission et réponse sauvegardées | Conserver voix inconnue et auditeurs ; le formulaire ne lit pas l'inventaire caché du PNJ |
| Proposition à deux termes, tâche contre bien/pièces | Plus élevé : éditeur de termes puis raccord à `echanges.proposer` ; plusieurs lots | Un champ « condition libre » n'est pas exécutable ; n'afficher que les conditions admises |
| Toute nouvelle mécanique : menace, échéance choisie, mission générale | Coût moteur distinct, hors extension du menu | Aucune équivalence à un bouton tant que l'effet et son jugement n'existent pas |

Ces coûts sont des estimations de découpage, pas des durées mesurées. Chaque
famille ouvre son lot ; « menu étendu » ne tient pas tout entier dans un lot.
Le terminal dispose déjà de nombreuses commandes : le besoin principal est
leur découverte par une liste numérotée de cibles/gestes publics et des choix
de paramètres, également accessibles au clavier en TUI. Aucun moteur de
menus séparé par interface : le descripteur commun transmet l'intention au
même validateur. Il ne copie ni les objets bruts ni une liste de faits cachés.

## 3. Saisies réelles : 70,1 % de gestes simples, un potentiel social distinct

Classement humain des **68 parties récentes de `c9459ce`**, 34 scripts en deux
passes dans `artifacts/bancs-multi/20261028-235223-6688/integ-r{1,2}` du dépôt
principal. 368 saisies hors `quitter`, soit **184 positions de script** répétées
deux fois, pas 368 intentions indépendantes. Les 68 parties plus anciennes
`d85fb54` ont les mêmes suites de saisies ; elles ne gonflent pas l'échantillon.
Leurs 136 empreintes, récentes et anciennes, sont inchangées après lecture.
Le classement des refus du 287 a aussi été consulté, sans le modifier.

Le classement porte sur l'intention complète et son interface possible, non
sur le mode choisi par Luna. Une demande de faisabilité appelle un **aperçu**,
pas l'exécution. Le même refus de portée peut être une bonne réponse directe.
Une erreur du modèle ne rend pas l'intention impossible à servir autrement.

| Famille exclusive | Positions / saisies | Part des saisies | Tours avec appel / appels historiques |
|---|---:|---:|---:|
| Direct simple : geste, perception publique, contrôle | 129 / 258 | 70,1 % | 91 / 217 |
| Dialogue structurable : mêmes actes et paramètres par formulaire | 22 / 44 | 12,0 % | 40 / 180 |
| Composition, physique ou sociale | 5 / 10 | 2,7 % | 10 / 32 |
| Invention, qualification ou improvisation | 11 / 22 | 6,0 % | 20 / 64 |
| Conversation ouverte ou demande d'interprétation non couverte | 11 / 22 | 6,0 % | 14 / 42 |
| Ambiance | 6 / 12 | 3,3 % | 12 / 26 |
| Total | 184 / 368 | 100 % arrondi | 187 / 561 |

**70,1 %** auraient une voie directe adaptée au sens du geste ; **82,1 %** si
l'on ajoute les actes sociaux rendus accessibles par formulaire. Cette seconde
valeur suppose d'accepter le choix explicite des paramètres à la place des
mots libres. Elle n'affirme ni une expérience identique, ni une disponibilité
de toutes les cibles au moment du clic. Le respect de mots imposés reste
propre à la saisie dialoguée ; on ne remplace pas automatiquement ces mots.

Parmi les 302 entrées candidates à une interface directe : **152** relèvent
de touches, panneaux ou confirmations existants ; **30** d'un verbe du menu
actuel ; **40** d'une commande locale sans ce choix de menu (dont deux offres
de mission) ; **80** demandent une interface structurée supplémentaire. Les
30 ne sont pas un taux de réussite du menu : ciblage, portée et préalables
n'ont pas été rejoués. Les 182 premières entrées représentent 49,5 % du corpus,
mais beaucoup sont de simples pas ou des consultations.

Sur les seuls 187 tours ayant appelé Luna, les gestes simples concernent
91 tours (48,7 %) ; avec les actes sociaux structurables, 131 (70,1 %).
Leurs 397 appels historiques cumulent 755,86 s sur 1 084,78 s. **Ce n'est pas
un gain annoncé** : ils comprennent interprétation, récit, audit et reprises,
et certaines voies directes exigeraient encore une admission. Les secondes
proviennent d'une campagne ancienne, sous une autre charge ; aucun chronomètre
nouveau ni comparaison causale dans ce lot.

Exemples auditables, indices des tours à partir de zéro :

- `crypte` t8, « que représente la gravure ? » : examen/lecture des faits
  disponibles ; t24, offre pour l'anneau : commande sociale déjà présente.
- `ressources` t0–2 : bois, nourriture et dû ; un formulaire suffit aux actes,
  même si leur jugement social reste riche et peut refuser.
- `atelier` t13 : prendre une perche puis franchir avec un appui mobile ;
  composé. `force-4f-enfermer` t0 : objectif à décomposer, pas bouton « fermer ».
- `atelier` t11 : taille de Corvus absente, réellement proposée en profil
  `taille_cm=178` ; classée invention, pas simple consultation de fiche.
  t8 décrit un mur établi ; t9 cherche des outils dans la scène, sans devoir
  en créer. `relais` t21, coup de pied dans la poutre, passe par improvisation,
  pas par une attaque moteur de porte transposée à tout objet.
- `echanges` t3 est une parole composée : annoncer l'eau **et** garder le feu.
  Le `propos` de la seconde clause n'établit pas un engagement. t4–5 se heurtent
  à un nom inconnu ; zéro appel n'est pas un dialogue réussi.
- `signes-ecart` t3–4 demande peur/intention d'attaque ; un bouton d'observation
  donne des signes publics, pas une réponse certaine sur l'esprit privé.

Les scripts présents `propositions`, `assemblage`, `materiaux`, `paroles-brillant`
et `paroles-fruste` complètent la lecture du catalogue, **sans entrer dans ces
pourcentages** : ils ne font pas partie des 34 scripts de cette campagne.
Ce corpus de régression surreprésente marche, confirmations et refus ; il
ne mesure pas le comportement d'une population de joueurs, ni la réussite
future de contrats générés ou d'une conversation ouverte.

Bruts reproductibles : `C:/Users/msics/donjon/artifacts/valeur-llm-288/`,
`compter.py`, `classement-saisies.json` (saisie, source, tour, classe, accès,
sorties et propositions), `mesures.json`, `sources-sha256.json`. Un seul
processus Python léger à la fois, sans import du jeu, rejeu, appel ou banc.

## 4. Ce que Luna ajoute, et quand l'attendre

Un moteur déterministe pourrait presque toujours remplacer une fonction LLM
avec assez de contenu et de grammaire. La question pratique est le coût
raisonnable de ce remplacement et les choix réellement accessibles au joueur.

| Apport et exemple | Moteur actuel | Valeur supplémentaire du LLM / alternative raisonnable | Risque et appel recommandé |
|---|---|---|---|
| Intention libre : « ramasse la bobine » | Prendre/transférer, alias et commandes bornées | Tolérer les façons de dire et référents ; un clic couvre mieux le choix évident | Mauvaise cible ; zéro appel au clic, un bloquant pour le libre |
| Composition : perche puis saut, enfermer quelqu'un | Séquence bornée, géométrie, arrêt au premier échec | Transformer un objectif et ses clauses en plan ; quelques recettes ne couvrent pas les combinaisons | Étape omise, condition transformée en succès ; un nominal et récapitulatif |
| Dialogue ouvert : souvenir de Gorm, raconter une expérience | Paroles retenues, savoirs autorisés, connaissances inventées persistantes | Comprendre le sujet imprévu et produire un contenu personnel cohérent ; coûteux à écrire exhaustivement | Nouveau secret, croyance ou promesse clandestine ; un bloquant uniquement si nouveau contenu utile admis, pas de seconde paraphrase |
| Négociation : pain contre entretien du feu | Jugement du marché, prix, besoins, droits et engagements | Comprendre des termes variés et suggérer une autre contrepartie pertinente ; un éditeur suffit au marché explicitement choisi | Effacer une clause, accepter pour le joueur ; un bloquant sur libre, zéro en formulaire |
| Contrat/mission adaptés : obtenir du bois contre service | Tâches et échanges typés ; missions configurées | Suggérer un lien non préécrit entre un besoin public, des biens connus et les moyens disponibles | Créer dette, argent, autorité ou but privé ; suggestion en fond ou à la demande, validation et accord séparés |
| Détail manquant : pierre, taille, propriété de matière | Enrichissement, invention bornée, qualification avant usage | Proposer un détail adapté à une intention inattendue, puis reprendre cette intention | Fabriquer l'outil qui annule le problème ; bloquant seulement si indispensable, revue ciblée à l'admission |
| Improvisation de geste ou de PNJ | Gestes `improviser` bornés ; décision autonome PNJ et émissions | Geste inédit exprimable, souvenir ou motivation personnelle autorisés ; PNJ autonome déjà riche sans LLM | Raconter un changement de but ou de réaction non jugé ; appel ciblé, jamais délégation générale de la décision PNJ |
| Ambiance : odeur, aspect, fond sonore | Scène, états et perceptions établis | Variété sensorielle à faible coût d'auteur, valeur secondaire | Contradiction immersive ou cible implicite ; fond seulement, aucun appel si rien d'utile à ajouter |

La priorité sociale est donc **comprendre des propositions et autoriser des
choix**, pas reformuler l'acceptation. Générer dix missions sans contraintes
produirait plus de texte, pas nécessairement plus de jeu : les mêmes urgences,
objets disputés et obligations croisées sont des sources de choix déjà présentes.

### Ambiance correcte, avec contrôle différé

Le dossier du narrateur doit être une projection publique complète pour ce
qu'il décrit : éclairage perçu, états connus des portes et sources, présence
actuelle distincte du souvenir, repères, détails déjà établis, sons réellement
perçus et ambiance précédente du lieu. Une omission n'est jamais la preuve
d'une absence. Ne lui transmettre ni secrets ni plans cachés pour faciliter
une phrase. Les références publiques doivent rester opaques aux voix inconnues.

Avant publication : gardes déterministes de références, perception et
provenance, puis contrôle des états explicites contre cette projection.
Renforcer la représentation commune des assertions vérifiables ; allonger une
liste de mots interdits ne prouve pas la cohérence. Une révision de monde
périme le dossier : revérifier les dépendances décrites, jeter le texte si
l'état pertinent a changé ; un départ du lieu le jette toujours.

**Recommandation : une vérification sémantique en fond avant publication** pour
les contradictions restantes, sans relance narrative. Le jeu et sa sauvegarde
avancent pendant ce contrôle ; seule l'ambiance attend. Une sortie incertaine,
contradictoire ou périmée est abandonnée ; aucune phrase provisoire n'est
montrée puis corrigée. L'ambiance admise est enregistrée avec son lieu avant
affichage. Aucun événement social ne peut se cacher dans ce canal.

Cela retire la cible « zéro audit cosmétique total » de G8/G21 du 287 : on vise
**zéro audit cosmétique sur le chemin bloquant**, avec un contrôle de fond
justifié. Ni gardes déterministes ni relecture sémantique ne garantissent
toute contradiction implicite. Si l'exigence est une garantie absolue, proposer
un répertoire de descriptions validées ; ne pas annoncer cette garantie pour
de la prose libre. Le contrat actuel reste en vigueur jusqu'à adoption de son
évolution ; les erreurs flagrantes citées au brief sont des contre-épreuves,
pas des exceptions à coder par torche, porte ou PNJ.

## 5. Contrats et missions : générer des possibilités exécutables

Il existe plusieurs mécanismes, à raccorder sans les confondre :

| Support actuel | Ce qui est utilisable | Ce qui manque pour un contrat libre |
|---|---|---|
| `dialogues` et contrats de mission dans `agendas` | Mission configurée, objet remis, offre/réservation de fonds, négociation bornée, accepter/refuser, paiement unique à remise | Pas d'opération d'invention arbitraire de mission ; le plafond vient du moteur, pas de la force d'un argument |
| `propositions.schema_terme`, `echanges.proposer` | Deux termes indivisibles : objet, part, tâche, pièces ; contrepartie éventuellement rien. Propriété, possession, utilité et confiance jugées, livraison et engagements enregistrés | Pas de langage général de conditions ; pas d'acceptation en deux temps universelle pour toute proposition |
| Tâches/engagements et `agendas` | Conditions exposées : objet allumé, verrouillé, situé dans une salle, service à une personne. Dette/remboursement et limites temporelles existantes | Une durée choisie par le joueur, une sanction ou une clause alternative ne sont pas des champs libres du schéma |
| Mandats A5, jugement et compte rendu PNJ | Délégation interne, filiation et croyance au compte rendu | `mandat` et `compte_rendu` joueur restent à porter (A5/10). Leur existence interne n'autorise pas Luna à les émettre pour Corvus |

Exemple immédiatement exprimable : « une part de vivres contre la promesse
d'entretenir ce brasero ». Les termes désignent la part, la tâche et ses
parties ; `echanges` décide si l'autre accepte. Une acceptation peut produire
le transfert immédiat et les engagements : **ne pas envoyer une proposition
au moteur comme simple brouillon**. L'éditeur affiche d'abord ses termes ;
valider l'offre exprime effectivement l'acte du joueur. La ligne « Compris »
du texte libre doit précéder cet effet.

Exemple plus ambitieux : « ramène Brune avant la crue, je te paierai si elle
arrive indemne ». Il requiert personne bénéficiaire, condition de succès,
échéance, état du corps et règlement conditionnel. Il n'est pas couvert par
la seule chaîne `mission.condition` ni par une tâche allumer/verrouiller/lieu.
La génération doit le déclarer non pris en charge ou proposer un autre contrat
explicite soumis au joueur ; elle ne peut en effacer silencieusement des clauses.

Pipeline proposé, d'abord avec les seuls termes existants :

1. Le moteur fournit des candidats publics : besoins que le PNJ exprime ou
   accepte de discuter, biens connus échangeables et tâches admissibles.
   Un besoin secret ne devient pas une quête parce que Luna le connaît.
2. Luna, si nécessaire, sélectionne/combine et **propose** des termes ; elle
   n'accorde ni fonds, ni connaissance, ni autorité. Un générateur déterministe
   des mêmes termes fournit la référence de valeur avant d'ajouter cet appel.
3. Validation sur copie : forme, droits, moyens, ressources, absence de doublon,
   connaissances et conditions réalisables ; le PNJ garde son jugement du
   marché. Aucun résultat du planificateur ne devient une arrivée fictive.
4. Une proposition d'un PNJ n'engage pas Corvus. Il faut un état d'offre durable
   avec auteur, destinataire, termes, révision/validité et consentement explicite,
   raccordé au registre existant. Les missions ont déjà un cycle d'offre ;
   généraliser ce cycle aux marchés est un lot propre, pas une capacité acquise.
5. À l'accord seulement : opération existante, ressources et engagements,
   sauvegarde, rendu moteur. Suivi, échec, dette et compte rendu restent aux
   mécanismes concernés ; Luna ne certifie jamais leur réalisation.

Liberté du LLM : sujet, combinaison et suggestion parmi les termes admis,
contenu personnel non mécanique autorisé. Aucune liberté sur le verdict du
PNJ, le paiement, la vérité d'une information ou une nouvelle clause juridique.
L'échéance de 240 minutes d'un engagement existant n'est ni une échéance
librement négociable ni une garantie de succès ; ne pas la présenter comme telle.

Recommandation : commencer par un **assistant de négociation à la demande**,
avec une ou deux alternatives valides et un coût d'opportunité lisible ; puis
essayer des offres PNJ opportunes. La suggestion peut arriver en fond si elle
ne crée aucun acte, mais l'émission d'une offre PNJ est un événement sauvegardé,
entendu et soumis à validation. Pas d'offres surgissant automatiquement à
chaque pas, ni de conversation tardive issue du narrateur d'ambiance.

## 6. Dialogues complexes, sans surévaluer les mots

Un menu peut proposer persuader, mentir ou menacer. Ce qu'il couvre mal à coût
raisonnable est le **contenu imprévu** : une raison personnelle, plusieurs
clauses liées, un récit, une référence à un échange passé, un mensonge adapté
à ce que l'autre croit. Le joueur doit pouvoir les dire ; cela ne prouve pas
que le moteur sait aujourd'hui juger leur poids argumentatif.

| Intention | Jugement actuel | Ouverture utile et limite |
|---|---|---|
| Persuader : demander prêt/passage, faire adopter une affirmation ou un avis | Caractéristiques, jets, confiance, perceptions et besoins ; avis d'eau et croyances typés | Luna identifie les actes et leurs objets. Une meilleure tournure n'accorde aucun bonus arbitraire ; des arguments à effets nouveaux exigent un contrat moteur |
| Mentir : « la cloche est au refuge », nom revendiqué | Croyance distincte du réel, démenti par perception/essai, découverte du mensonge ; identité revendiquée distincte de reconnue | Contenu libre précieux, vérité jamais mutée. Les attributs d'affirmation restent bornés (`lieu`, `verrouillee`, `fiable`), pas tout récit pris pour un fait |
| Questionner : qui, où, ressource, dû, passé | Réponses typées et dernières croyances datées ; rappels de paroles ; savoirs configurés | Question non prévue sur un souvenir ou une motivation : ajout personnel admis. « Pourquoi agis-tu ? » n'ouvre pas l'agenda privé par défaut |
| Marchander : 3 pièces contre une planche, service contre pain | Prix, valeur des termes, besoin de garder le bien, droits et acceptation ; missions à plafond | LLM utile pour comprendre/suggérer un assemblage de termes, zéro pour relire un prix déjà fixé |
| Raconter : « autrefois j'ai perdu mon frère dans une crue » | Parole entendue et retenue ; opérations typées si certaines phrases en relèvent | Le récit peut créer un souvenir de parole ; aucune empathie, loyauté ou modification d'agenda générale n'est établie par `propos` |
| Menacer : « laisse-moi passer ou je casse la porte » | Violence et défense effectives modélisées ; pas d'acte joueur général de menace dans `TYPES_JOUEUR` | Ne pas transformer la menace en coup ni inventer un consentement par peur. Il faut une mécanique propre si l'on veut que cette stratégie ait un effet systémique |

L'option A est maintenue : le moteur dit l'acceptation, le refus et leurs termes.
Il ne fait pas relire leur paraphrase par Luna. Pour l'ouvert, recommander une
**proposition de contenu personnel admis**, dans la même compilation nominale,
puis sa publication selon un contrat distinct de parole : auteur, mots,
auditeurs, provenance et éventuelles opérations. L'admission non calculable
peut garder sa revue ciblée ; elle n'autorise pas une seconde génération pour
enjoliver chaque réponse. Si le résultat social doit d'abord être connu, sa
formulation reste celle du moteur, sans seconde improvisation cachée.

Cet ajout exige une décision : les mots libres d'un PNJ ne sont pas une ambiance.
Pour une réponse hors des savoirs/propriétés admis, un refus honnête suffit.
Pour maintenir la conversation sans effets nouveaux, proposer questions de
suivi, contradictions de propos et souvenirs personnels persistants ; ne pas
promettre persuasion par argumentation ou intelligence sociale universelles.

## 7. Révision du plan G0–G21

Les invariants et contre-épreuves du 287 restent la base de chaque lot ; le
tableau donne **leur nouvelle place et leur changement**, sans fusionner les
lots. Un lot tient en 30–45 minutes. Si une famille dépasse ce budget, ouvrir
le lot suivant sur le même contrat, jamais élargir le lot courant.

| Lot 287 | Priorité révisée et delta |
|---|---|
| G0 contrat adopté | D'abord : décisions acquises ci-dessus ; conserver les questions d'ouvert et d'ambiance résiduelle. Le présent document ne modifie pas `AGENTS.md` |
| G1 compilateur public | Haut, **pour saisie libre seulement** ; contexte et actes actuels complets, y compris négociation. Aucun aller-retour de compilation pour clic/formulaire |
| G2 validation/refus découplés | Haut, préalable commun ; provenance d'entrée structurée ou libre, même validation sur copie et `attendu`. Retirer les appels d'explication, pas les raisons moteur |
| G3 transports cloud/local | Descend : ne conditionne pas les menus. Maintenir le portage du contrat Luna ; local plus tard, sans changer de modèle ni comparer les modèles |
| G4 résultat public | Monte juste après le socle : zéro récit après commande/clic ou exécution de plan ; le menu seul ne supprime pas ce coût |
| G5 perception canonique | Haut avec G4 : examine/écoute/observe sans narrateur mécanique ; rendre les seuls faits connus |
| G6 repères | Haut : cible cliquée et texte lu désignent le même lieu public, sans repère inventé |
| G7 déplacements résolus | Haut : marche et plans composés affichent les pas réellement accomplis, sans nouvelle narration |
| G8 producteur d'ambiance | Descend après les interactions et l'invention utile ; un essai, gardes renforcées, éventuel contrôle en fond avant publication ; supprimer les relances, pas affirmer zéro contrôle |
| G9 connexions indépendantes | Préalable technique à l'ambiance active ; aucune attente du compilateur derrière une ambiance ou son contrôle |
| G10 publication persistante | Préalable à l'affichage d'ambiance : lieu, révision, contrôle, sauvegarde puis affichage ; jeter au départ |
| G11 interfaces non bloquantes | Distinguer l'indépendance de saisie/rendu de l'indicateur U-A ci-dessous ; ne pas charger ce lot de tous les menus |
| G12 portée d'une création | Monte après accès aux gestes ; invention utile avant ambiance. Ni indice caché ni perception remplacée par une invention |
| G13 qualification | Même priorité ; ne pas donner une mesure arbitraire pour rendre un clic exécutable ; reprendre la saisie/les paramètres sans répétition |
| G14 ciblage d'ambiance | Après G12/G13 ; nécessaire avant activation d'ambiance ciblable, matérialiser une seule fois avant manipulation |
| G15 émissions uniques | Monte au socle social, avant formulaires de parole et G16–G19 ; traiter la contradiction `avis-joueur` 86/87 du 287 |
| G16 information parlée | Monte : identité, localisation crue, ressource et refus moteur, directement accessibles ; aucune reformulation LLM |
| G17 comptes parlés | Monte : termes et règlement exacts, condition de tout éditeur de marché ; aucune paraphrase ni paiement au stade brouillon |
| G18 avis | Monte avec parole et récapitulatif préalable : l'avis est un acte à effets, même non violent ; aucune transformation en vérité |
| G19 rappels | Avant conversation ouverte : rappeler les mots n'est pas les réémettre ni les réinventer |
| G20 signes | Avec G5, avant promesses de dialogue riche : signes publics et impression restent distincts d'une intention privée |
| G21 fermeture | En dernier : retirer les anciennes voies bloquantes, inventorier les admissions résiduelles ; décider sur mesure le retrait des revues de fidélité. Cible : zéro audit cosmétique **bloquant**, pas zéro contrôle en fond |

### Lots d'interface à ajouter

| Lot ajouté | Un invariant, dépendances et preuve minimale | Coût de jeu et mesure |
|---|---|---|
| U-P récapitulatif sémantique | Une ligne moteur désigne exactement le plan admis, les parties, montant/quantité, conditions, destinataires/portée et étapes ; G2. « Compris : offrir 3 pièces à Aubin contre une planche ». Cas paiement + autre offre/avis, question sans exécution, plan périmé, recharge | Zéro appel de résumé ; lignes lisibles, omissions/erreurs repérées et corrections demandées. Aucun résumé qui cache une clause pour tenir en une ligne |
| U-C consentement du texte libre | Le plan lourd décrit par U-P est celui confirmé par `tenter`, annulé sans effet ; changement pertinent impose nouvel aperçu. Paiement puis enfermement/violence, autre acteur ; état, mots et recharge. Après U-P | Une validation humaine supplémentaire avant effet lourd ; mesurer saisie→aperçu, puis confirmation→effet, temps humain séparé. Aucun appel après confirmation sauf nouvelle admission nécessaire |
| U-D descripteur public | Une intention structurée transmise garde son identité jusqu'au même validateur ; premier geste existant sur deux cibles et voix inconnue. Pas de test de précondition secret envoyé au client | Zéro compilation et zéro contre-revue de fidélité pour le clic ; compter les renvois au MJ dus à un préalable réellement manquant |
| U-M menu contextuel étendu | Choisir un geste et ses paramètres publics conserve le même acte qu'une commande ; après U-D/G4. **Un lot par famille** : inventaire, outil, corps, passage/fabrication, puis social après G15–G18 | Clics/choix nécessaires, erreurs de cible, autonomie sans saisie ; preuve identique commande/menu et après recharge, pas de passe Luna si aucun chemin modèle touché |
| U-T actions directes au terminal | La liste numérotée utilise U-D et les mêmes identifiants publics ; premier geste sur deux cibles, ambiguïté, inconnu. Extensions par famille dans des lots suivants | Touches jusqu'à effet, erreur de nom, parité console/TUI/web ; aucune grammaire naturelle concurrente à entretenir |
| U-A indicateur d'ambiance | Un état de tâche publique distinct de « MJ réfléchit » suit en attente/calcul/contrôle/terminé ou abandon, terminal et web ; après G9–G11. Tester fin tardive, rejet, départ/quitter | « Ambiance en préparation… » non modal ; disparaît aussi en panne. Menu et texte restent actifs ; zéro allongement du délai mécanique par délai artificiel d'ambiance |

Pour un acte libre léger, U-P est la ligne de résultat **après** exécution ;
elle ne permet pas de défaire une action, ni ne constitue une preuve parfaite
de fidélité. Pour un clic, le choix est déjà explicite : pas de ligne « Compris »
à faire valider, ni de revue sémantique. Les fiches de risque existantes ne sont
pas supprimées par cette dispense de contrôle d'interprétation.

U-C doit couvrir les actes lourds ou irréversibles selon leurs **effets typés**,
pas une liste de formulations ou un nom d'objet. La classification de gravité
est commune aux transactions et aux plans composés ; une étape lourde suffit
à imposer l'aperçu de toute la composition. Les revues transitoires ne se
déclenchent plus pour une simple description ou pour la reformulation du
résultat moteur ; elles restent sur les actes à effets issus du libre. Leur
retrait par famille exige d'observer ce que les joueurs repèrent réellement,
et ne se déduit pas d'une baisse de refus dans un banc scripté.

### Lots de valeur à ouvrir après décision

- **K0 candidats de contrat** : une suggestion déterministe ne propose que
  des termes publics admissibles, sans accepter ni payer. Référence pour juger
  ensuite l'apport de Luna ; ressources puis autre famille, recharge.
- **K1 éditeur de marché** : deux termes affichés sont les deux termes soumis
  à l'accord ; après G17/U-D, un seul type d'échange par lot. Le libre converge
  sur le même aperçu, sans perte de clause.
- **K2 suggestion Luna ciblée** : une intention sociale non préécrite devient
  une ou deux alternatives admises, sans changer le verdict du PNJ ; après
  K0/K1/G1. Mesurer les alternatives utiles absentes de la référence, pas leur
  quantité de texte. Une offre PNJ persistante en deux temps est un lot distinct.
- **D0 parole ouverte personnelle** : un contenu inédit autorisé devient une
  parole enregistrée sans effet mécanique clandestin ; après G12/G15/G19.
  Souvenir de Gorm puis autre PNJ, refus d'un secret et d'une promesse non typée.
  Réponse ouverte déjà connue : zéro nouvel appel de formulation.

Échéance libre, menace systémique, génération de mission générale et raccord
A5/10 sont des chantiers de mécanique à décider séparément. Ils ne deviennent
pas quatre sous-tâches cachées du compilateur.

Ordre proposé : **G0 → G2/G4/U-D → G1/U-P/U-C → G5/G6/G7/G20 →
premiers U-M/U-T → G15/G16/G17/G18/G19 et menus sociaux →
G12/G13 puis K0/K1/K2/D0 selon décision → G14 et G8–G11/U-A → G21**.
Les flèches donnent l'ordre des groupes, pas une autorisation de les fusionner.
G3 se porte lorsque nécessaire au compilateur ; sa partie locale peut attendre.
Un système social existant ne doit pas être coupé en attendant son formateur :
les familles non portées gardent leur voie actuelle pendant la migration.

### Mesurer les quatre axes, sans fabriquer un nouveau banc général

| Axe | Observation décisive |
|---|---|
| Interprétation | Réussite fidèle du premier coup, tous paramètres conservés ; clic sans interprétation ; nombre de résumés corrigés et d'intentions abandonnées ; ne pas compter un refus/clarification évitable comme succès |
| Vitesse perçue | Saisie/clic→premier effet ou aperçu utile ; confirmation→effet séparé ; nombre de validations, saisies et choix ; bloquant/fond distincts. Un aperçu rapide sans action ne remplace pas le délai jusqu'à effet |
| Invention à la volée | Détail utile admis puis manipulable et retrouvé après recharge, refus légitimes maintenus ; nombre d'appels jusqu'à manipulation, pas longueur du texte |
| Richesse PNJ | Marchés et stratégies différents réellement jugés, raisons du refus compréhensibles, engagements exécutés ou dus, informations adoptées/contredites. Comparer suggestions utiles au générateur déterministe ; `propos` sans effet n'est pas un marché réussi |

Chaque lot reprend la saisie réelle et un autre cas de même nature, un faux
pendant et le rendu/état après recharge. Tests ciblés seulement ; Luna une
passe ciblée si le chemin MJ change, sur copies. Pour une interface pure,
la preuve de parité déterministe suffit. Référence exacte réutilisée, secondes
comparables seulement sous même charge ; suite et lourd à l'intégration.
Le retrait des revues a aussi besoin d'une observation joueur : les fils de
régression ne montrent pas qu'une personne a vu ou compris son récapitulatif.

## 8. Questions restantes à l'utilisateur

1. **Jusqu'où privilégier le direct ?** Recommandation : gestes courants et
   informations publiques d'abord, puis raccourcis sociaux et éditeur de
   marché ; texte libre toujours disponible. Ne pas exiger d'écrire pour ouvrir
   une porte ou saisir un prix, ni construire un menu exhaustif de phrases.
2. **Contrats générés : assistance à la demande ou offres PNJ spontanées ?**
   Recommandation : K0/K1 puis assistance à la demande avec les termes actuels ;
   offres spontanées ensuite, avec consentement et persistance dédiés. Aucun
   nouveau langage de clauses ni mission générale dans cette première étape.
3. **Conversation ouverte personnelle sous option A ?** Recommandation : oui
   pour sujets/souvenirs autorisés, parole persistée et admission ciblée ; A
   continue de formuler tous les effets typés. Ne pas promettre un effet de
   persuasion à chaque argument ou de peur à toute menace sans mécanique.
4. **Contrôle de l'ambiance restante ?** Recommandation : projection publique
   enrichie, gardes communes et une vérification sémantique en fond avant
   publication, abandon sans relance si doute. Si seule une garantie absolue
   convient, choisir un répertoire validé plutôt que déclarer la prose libre sûre.
5. **Première mécanique sociale nouvelle après ces raccords ?** Recommandation :
   raccorder A5/10 si le besoin prioritaire est de mandater/rendre compte ;
   choisir ensuite menace ou échéance négociée à partir d'un cas de jeu.
   Ne pas ouvrir les trois dans un lot « dialogue complexe ».

Le récapitulatif joueur, son placement avant/après effet et le filet transitoire
de fidélité sont déjà décidés ; ils ne figurent plus parmi ces questions.
