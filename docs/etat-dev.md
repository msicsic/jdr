# État du développement

Point de reprise, à tenir à jour à chaque fin de jalon. Mis à jour le 2026-10-21.

## Où on en est

- `main` contient les jalons PNJ A à I (`docs/plan-pnj.md`, tableau « Jalons » et sections
  « Écarts retenus »). Le dernier fusionné est **I. Demander, écouter, protéger** :
  - le corps commun (faim, froid, fatigue) pour tous, joueur compris (`donjon/corps.py`) ;
    malus aux jets, PV à l'extrême, manger ; le scénario déclare des états ;
  - le joueur demande une part de vivres ou de bois ;
  - les PNJ font du bruit ; action `ecouter`, mieux contre une porte ;
  - protéger : donnée `protege`, appel à l'aide, protecteur qui accourt, victime prévenue.
  - avant I : H (sécurité perçue, abri, rondes en routine), G (le feu partagé).
- Luna (`gpt-6-luna`) reste le MJ. Le stratège Luna des PNJ (jalon E) est optionnel
  (`--stratege`), désactivé par défaut. Remesuré sur le Relais de F, il n'apporte presque
  plus rien : +5 % d'événements, −1 % d'oisiveté urgente. Le moteur fait désormais seul
  ce qui était son apport principal.
- Après F, branche `recharger-foyer` : mettre un combustible dans un foyer, c'est le recharger
  (`deplacer` vers un foyer devient `alimenter`) ; le combustible peut être porté ou à portée
  de main ; le titre de `deplacer` vers le joueur dit « Prendre », sans rangement que l'état
  ne modélise pas. Détail et vérification réelle dans `docs/plan-pnj.md` (écarts du jalon F).
- Branche `messages-refus` : les refus du moteur guident la correction du MJ. Chaque
  `ErreurMonde` porte `attendu` (champ fautif, valeur reçue, identifiants valables), transmis
  dans `retour_moteur` et jamais au joueur ; les causes fusionnées sont séparées ; l'étape,
  l'effet ou l'ajout fautif est numéroté. Mesure Haiku A/B sur les trois bancs : les refus
  corrigeables passent de 4 répétés et jamais corrigés à 2 corrigés dès la première relance.
  Restent hors périmètre : les messages d'audit (contrôle narratif, contre-revue).
- Branche `contre-revue` : le raccourci `detacher` libère la fixation sur place (la prendre
  est une étape `deplacer` explicite) ; un rapport de contre-revue mal formé est redemandé
  une fois puis le plan validé passe, au lieu d'être renvoyé au MJ comme un refus. Cas réel
  « fais levier sous l'axe » : 2 appels, conforme du premier coup (contre 4 à 8 avant).
- Branche `banc-haiku` : Claude Haiku 5.5 est une option du jeu (`--connexion anthropic`,
  `donjon/claude.py`, `requirements-claude.txt`) ; Luna reste le MJ par défaut. Correctifs
  communs révélés par le fil complet des appels (`tools/banc_parties.py --fil`) : citation de
  fait inconnue écartée au lieu d'invalider la réponse ; audit narratif à une entrée
  obligatoire par segment, audit illisible redemandé ; texte vide signalé sans audit ;
  apparence d'un personnage acceptée en aspect ou portrait ; rappel d'une parole déjà
  entendue classé mécanique. Comparatif final sur les trois bancs (31 tours MJ) : Luna
  3,55 appels et 20 s par tour MJ, Haiku 3,68 appels et 12 s, 1 repli chacun (celui de
  Haiku corrigé ensuite), Haiku 0,17 $ les trois parties. Ni l'un ni l'autre ne réfléchit
  dans le jeu : Haiku ne le peut pas sous outil imposé, Luna en medium ne produit aucun jeton
  de réflexion. `tools/sonde_reflexion.py` vérifie hors jeu qu'une réflexion se constate.
- Branches `haiku-reflexion` et `narration-fidele` : Haiku joue par défaut avec réflexion
  adaptative (`--reflexion libre` ; `imposee` reste plus rapide, sans réflexion). Une réponse
  rendue en texte au lieu de l'appel est retranscrite en appel imposé. Banc (31 tours MJ) :
  0 repli, 1 tour refusé (contre 8 sans réflexion, 5 pour Luna), 22 s par tour MJ, 0,18 $
  les trois parties. Narration fidèle, quatre défauts communs corrigés : message technique
  affiché au joueur (consigner sans les croyances du locuteur), réplique du joueur réécrite
  (le personnage interpellé en tête est le destinataire, ses mots sont la réplique), geste
  refusé raconté comme tenté (audit), voix d'auteur dans le texte affiché (contrôle
  déterministe). Comparaison des textes : Luna ~190 caractères, sobre ; Haiku ~340, plus
  descriptif, et plus de dérives que les corrections encadrent.
- Branche `instructions-mj` : consignes du MJ réécrites (`donjon/consignes.py`), dans l'ordre de
  la décision (ton, autorité, mode, puis une section par mode), une règle à un seul endroit,
  sans anciens raccourcis ni rustines d'exemples ; ~15 000 caractères au lieu de ~24 000.
  Bancs multiples (même code, consignes seules) : Haiku 3 passes, 3,06 appels et 22 s par tour
  MJ contre 3,20 et 23,7, refus 1,3 contre 2,0, coût −8 % ; Luna 2 passes, 3,24 appels et 17 s
  contre 3,50 et 20,2, 0 repli contre 1, refus 4,5 contre 6.
- Outillage : `tools/banc_multi.py` joue des variantes (références git) en plusieurs passes et
  en parallèle, et résume moyenne et étendue ; le forfait ChatGPT a tenu 4 passes simultanées.
- Branche `fabrication-generale`, étapes 1 et 2 : tout objet peut recevoir une description
  physique (`donjon/matiere.py` : forme, dimensions, matière, pièces) établie par le MJ
  (`etablir_faits`, qualification) ; le moteur vérifie l'accord avec la masse et en déduit
  longueur et charge ; l'atelier y est migré. Ce qu'un objet contient ou consomme (la lanterne
  brûle de l'huile). Lots : un nom de pièce, un seul compte (pièces = utilisations), opération
  `prelever` qui réutilise les règles de `deplacer`. Correctifs trouvés en route : boucle de
  correction pour conversation, savoirs et description de personnage ; `enrichir` (personnage)
  et `etablir_faits` (objet) distingués ; l'audit physique juge un contenu sur sa plausibilité ;
  messages du moteur au tutoiement, sans rangement prétendu. Vérifié en bancs : Haiku et Luna
  décrivent planches, torche et lanterne, et prélèvent une planche (vol discret).
- Lisibilité : carte avec la pénombre (vert sombre dans l'interface), une lettre par personnage,
  méta-langage refusé dans le texte affiché.
- Branche `don-et-refus` (vu en partie : la cloche ne pouvait pas être donnée à Gorm, et Luna
  lui prêtait un motif inventé) : `remettre` est le geste de donner, avec récompense si un accord
  est accepté, sinon un don (l'objet passe au personnage, qui s'en souvient) ; une explication de
  refus ne fait parler aucun personnage ; un déplacement vers un personnage oriente vers
  remettre ; la contre-revue voit « nom (identifiant) » au lieu d'identifiants nus (« marchand »
  lu comme un marchand). Bancs : don de la cloche 3/3 avec Haiku et avec Luna.
- Branche `fabrication-generale`, étape 3 : action `assembler` (usage, pièces par rôle, lien,
  outil) avec n'importe quelle pièce décrite ; `fabriquer` en reste un alias ; l'échelle prend
  le nom « échelle » et sa matière de ses pièces. Action `decouper` : une barre ou un lien
  coupé à longueur donne un morceau, le reste garde la masse complémentaire ; l'outil doit
  pouvoir couper cette matière. Un lot se prélève d'abord pièce par pièce (prélever sur place
  ne déplace rien) ; la dernière pièce garde le nom de pièce. Bancs : échelle de perches et
  ficelle coupée d'un mètre, 3/3 avec Luna et avec Haiku.
- Branche `recit-pnj` : le banc sans joueur imprime un récit (`donjon/recit_pnj.py`) : buts et
  gestes de chaque PNJ, rondes résumées, besoins pressants et minutes sans rien entreprendre,
  échanges et témoins, méfiances à la fin ; `--chronique` ajoute chaque pas. Il montre un Relais
  surtout fait de rondes, une vie sociale réduite aux parts demandées, Gorm au devoir urgent en
  permanence sans rien à faire, un affamé honnête refusé sans autre idée.
- Branche `planificateur` : les plans des PNJ viennent d'une recherche sur des gestes déclarés
  une fois (`donjon/planification.py` : conditions sur ce que le PNJ croit, effets, coût ; faute
  comptée par personne lésée, chance de crocheter selon la lumière, flamme qui se consume).
  Faim, froid, pulsions, paroles données, garder, prévenir, s'abriter et la complétion du stratège
  y passent ; les méthodes écrites sont retirées. Comparées avant retrait : 6 800 plans
  identiques, deux ordres différents gardés. Banc identique à `main`, +33 % de temps. Trouvé sans
  être écrit : de la lumière avant de crocheter dans le noir ; demander un objet que porte un
  autre (Gorm demande ses planches à Aubin pour le feu). Bilan dans `docs/plan-planificateur.md`.
- Branche `vitesse-banc` : la vision des PNJ (lumière par case, champs de vue) est gardée
  pendant leur vie minute par minute, tant que portes, sources allumées et objets opaques n'ont
  pas changé ; `--graines` joue plusieurs nuits en parallèle. Résultats identiques (empreinte de
  la chronique, des mesures et de l'état final sur 4 graines). Une nuit : 9,2 s → 6,4 s en
  moyenne ; 4 nuits : 57 s → 11 s ; la suite de tests : 236 s → 135 s.
- Jalon `temps-fin` (`docs/plan-temps.md`) : l'horloge compte à la seconde (minutes et dixièmes) ;
  les PNJ vivent par événements, geste après geste avec leur durée, et marchent case par case
  par la règle du pas du joueur ; orientation en huit directions, cône de 120° et côtés
  immédiats, rotation 0,5 s par huitième de tour ; un pas s'entend à 6 cases et fait se retourner,
  un pas feutré (3 s) seulement de la case voisine ; tour d'horizon avant un geste sans témoin ;
  témoins pendant toute la durée d'un geste illicite. Le joueur est sur la même horloge : pas
  1,5 s, pas chassé (Maj), pas feutré (Alt), « tourner », regard sur la carte ; un geste sur ce
  qu'il a dans le dos le tourne d'abord ; les sorties connues restent listées. Les scènes de test
  posent l'orientation avec la position. Banc 4 graines : une nuit ~6 s, aucune violation.
- Jalon `vue-web` (`docs/plan-vue.md`) : `jeu.py --web` joue dans une page locale (127.0.0.1,
  commandes refusées d'un autre hôte) avec le même contrat que le terminal. Une scène perçue
  (`donjon/scene.py`) est la source unique de la carte du terminal et de la page : rien de ce que
  le joueur ne perçoit pas. La carte dessine chaque objet et personnage (icône, couleur, nom,
  regard, ce qu'il tient), le degré de lumière de chaque case tel que le moteur le calcule et le
  cône réel du joueur ; un clic mène à une case (commandes « pas », arrêt si quelqu'un entre dans
  le champ) ou propose les gestes possibles sur ce qui s'y trouve, en s'approchant d'abord.
  `banc_pnj --rejeu page.html` enregistre une nuit sans la changer et la rejoue : barre de temps,
  but, besoins, regard réel et croyances de chaque PNJ (fausses en rouge).
- Branche `annonces-presence` (vu en partie : « Aubin, Gorm et Brune arrivent puis s'éloignent »
  pendant qu'on allume une torche) : les présences se disent en bilan, à la fin de l'action du
  joueur (une manœuvre entière comprise) : qui il voit désormais, qui il ne voit plus, qui il n'a
  fait qu'apercevoir (`pnj.bilan_presences`). « Entre dans la pièce » ou « quitte la pièce »
  seulement s'il a vu le passage ; sinon « Tu aperçois… » ou « Tu ne vois plus… », ce qui couvre
  aussi son propre regard. L'humeur remarquée suit ce bilan. Banc identique à `main`.
- Branche `temps-fin-marche` (relecture du jalon temps fin) : aucun geste ne s'achève sur une
  case occupée (le pas qui mène sur quelqu'un se poursuit jusqu'à la case libre suivante ; le
  joueur ne marche pas sur un PNJ ; contrôlé par `Monde.verifier`, anciennes parties écartées au
  chargement) ; tout ce qu'un geste touche (cible, outil fixe) se rejoint par la marche, sans
  bond (`_a_toucher`, `_approcher`) ; le trajet en cases est le seul juge du passage : sans
  chemin, geste manqué, obstacle appris, et le chemin par salles évite un seuil qu'on croit
  barré ; on marche vers la case crue, puis on constate. Détail dans `docs/plan-temps.md`.
- Branche `temps-fin-etat` (relecture du jalon temps fin, `docs/plan-temps.md`, dernière
  section) : tout ce dont dépend la suite est dans `data` ; le même laps, attendu d'un bloc ou
  découpé en rotations et rechargé en route, donne le même monde (`tests/test_temps_etat.py`).
  Tour d'horizon dans l'esprit du PNJ ; un registre des gestes en cours, joueur compris, jusqu'à
  leur fin (témoin : quiconque voit l'auteur pendant le geste) ; bruits datés à l'instant ;
  interlocuteur = personnage perçu (vu, ou entendu pendant le dernier geste) ; perception des
  PNJ après chaque événement. Banc : aucune usurpation, plus d'échanges et de confidences.
- Branche `planif-rapide` : le planificateur des PNJ ne pèse plus que 7 % d'une nuit (41 %
  avant). Diagnostics des recherches au banc (`--diagnostic`) ; le dernier résultat de chaque PNJ
  pour chaque but est repris tant que rien de ce que lit la recherche n'a changé ; chaque but dit
  ce qu'il peut employer (repas, feu) et l'on ne porte que ce qui peut le servir. Empreinte des
  4 nuits identique ; nœuds examinés 185 000 → 11 700 ; une nuit 10,1 s → 5,6 s (processeur).
  `planification.VERIFIER` refait chaque résultat repris ou borné par une recherche complète :
  toute lecture nouvelle de la recherche (un coût, une croyance) doit entrer dans `_entrees`.
- Branche `perception-rapide` : ce que perçoit un acteur, les places des objets et les champs
  sont gardés tant que l'empreinte complète de l'état ne change pas (`spatial.etat_vue` : chaque
  clé que lit la perception) ; une consultation qui ne révise que des esprits la calcule une fois
  (`etat_fige`). Lignes de vue, vue autour d'une case et champs ne dépendent que des salles et de
  la signature d'une salle (seules les sources qui peuvent l'éclairer) : gardés d'une étape à
  l'autre, clé le texte des salles. `spatial.VERIFICATION` recompare les lectures mémorisées à un
  calcul de zéro. Empreintes des 4 nuits identiques, aussi en vérification complète. Perception :
  2,7 s → 1,0 s par nuit (30 % → 13 %), au profil 33 % → 11 % ; une nuit 9,1 s → 7,4 s ; 4 nuits
  12,2 s → 10,1 s.
- Branche `scenario-auberge` : second scénario, l'auberge du Col-Pendu (`donjon/scenario_auberge.json`,
  `donjon/auberge.py`, `banc_pnj --scenario auberge --joueur dortoir`, `jeu.py --auberge`). Une nuit de
  tempête, huit salles sur trois niveaux, huit PNJ aux buts concurrents (aubergiste, cuisinière,
  enfant, palefrenier, marchand et son ballot, ancien soldat, pèlerine, voyageur au crochet qui cache
  un reliquaire), bois et vivres comptés, trois foyers, une rafale qui éteint l'âtre (horloge). Écrit
  seulement avec des données ; un seul correctif de moteur, `social.GESTES` (une rumeur sur un feu
  allumé, éteint ou rechargé par un autre faisait planter le banc). Mécaniques qui manquent, relevées
  en l'écrivant : demander du combustible pour une pulsion de feu (aujourd'hui seulement pour le
  froid de soi), un objet prêté encore illicite pour l'emprunteur s'il a un propriétaire déclaré, une
  nouvelle sans lieu (le marchand ne retrouve pas son ballot), aucun recours au bruit pour retrouver
  quelqu'un dans le noir, le froid sec trop lent (2 par heure) pour menacer qui est au sec.
- Branche `caracteres-valeurs` (étape 1 de `docs/plan-social.md`, `donjon/caractere.py`) : VOL,
  ELO et PSY pour tous ; les états modulent les caractéristiques par une règle commune (la
  fatigue touche aussi INT et PER ; volonté brisée prévue en donnée) ; persuasion d20 + CHA + ELO
  contre la VOL de l'auditeur. Huit valeurs de 0 à 100 dans le profil ; les limites deviennent
  honnêteté ou douceur 100 (profils et sauvegardes migrés au chargement). Une faute a un prix
  en minutes selon l'honnêteté, usé par la détresse, moins vite avec de la volonté ; l'altruisme
  de qui donne facilite une demande. Banc : même ordre, plus d'échanges, moins de vols dans
  certaines nuits ; bilan et limites dans `docs/plan-social.md`.
- Branche `crue-eau` (étape 3 de `docs/plan-crue.md`) : un niveau d'eau tiré de la
  graine par un tirage à part (`donjon/eau.py`) ; salles mouillées puis noyées (100 cm) selon
  leur altitude ; l'eau trempe, éteint un feu posé, barre le passage, pour le joueur comme pour
  les PNJ. Les PNJ voient l'eau, en jugent la vitesse, l'attendent dans l'heure ; l'eau inquiète,
  un lieu menacé n'est pas un abri, et tant qu'elle monte l'abri est le plus haut lieu éclairé.
  Scénario dérivé `crue` (`donjon/scenario_crue.json`, `jeu.py --crue`, `banc_pnj --scenario
  crue`) ; le Relais et son banc sont inchangés. Banc 16 graines : feu noyé 5 fois, quelqu'un
  monte à la galerie 14 fois. Corrigés en route : un réflexe d'alerte sans passage tombe ; un PNJ
  ne prend rien dans la main d'autrui ; pas de bois demandé pour un feu cru sous l'eau.
- Intégration du 2026-10-20 (branche `integration`, une fusion par branche, suite et banc après
  chacune) : chronique du banc, vue web, présences, marche, temps fin sans état caché,
  planificateur et perception rapides, mine, auberge, caractères et valeurs, crue. Correctifs de
  fusion : les témoins reçoivent le geste en cours ; la mémoire du planificateur lit aussi le prix
  d'une faute et l'adresse modulée (contrôle `VERIFIER` sur 4 nuits). Défaut d'origine corrigé :
  l'étage d'une salle est celui du plan (`niveau`), pas l'altitude de son sol ; deux salles d'un
  même étage à des hauteurs différentes se voient et s'éclairent, un escalier change d'étage.
  Relais : empreinte des 4 nuits inchangée par les optimisations et par la crue ; une nuit ~13,7 s
  → ~4,7 s (4 nuits en parallèle). Constat : combinées, la marche et la perception par événement
  redonnent au Relais une nuit proche de celle d'avant (mêmes mesures), alors que chacune seule
  multipliait échanges et vols vus ; à examiner avec le rejeu.
- Branche `laisser-passer` (vu en partie : Brune, désœuvrée sur le seuil du refuge, barrait la
  sortie ; Luna lui faisait promettre de se pousser sans que rien ne la déplace, et « je la
  pousse » était refusé) : trois règles communes, joueur compris (`donjon/passage.py`). Un PNJ
  sur la case où l'on doit s'arrêter s'écarte d'une case hors du chemin, sauf geste en cours
  (dont la porte qu'il va ouvrir), méfiance ou fierté qui l'emporte de 30 sur l'altruisme ;
  sinon le pas du joueur est refusé avec un `attendu`. Demander le passage est un contenu de
  parole typé (`passage`) que le moteur tranche ; acceptée, le PNJ bouge vraiment. Pousser :
  action et commande, jet de FOR opposé, la victime recule d'une case ; victime et témoins
  cessent de croire l'auteur fiable ; douceur 100 l'interdit, sinon faute au prix de la
  douceur. Un PNJ bloqué attend, demande, pousse si ses valeurs le permettent, sinon patiente et
  renonce ; il prie le joueur de le laisser passer. Bancs Relais (8 graines), mine et auberge :
  identiques à `main` (personne n'y bloque quelqu'un d'immobile). Joueur posté sur une porte
  (`--joueur crypte` au Relais, `--joueur cuisine` à l'auberge) : les PNJ le prient de les
  laisser passer (1,25 et 6,25 demandes par nuit), puis renoncent au bout de 30 min au lieu
  d'attendre sans fin (renoncements 1 → 1,25 et 1 → 7) ; aucune poussée, tous ces PNJ ayant la
  douceur entière. Luna (3 parties courtes) type la demande `passage` et l'action `pousser`.
  Détail, cas vérifiés et limites dans `docs/plan-temps.md`, « Correctif : laisser passer ».
- Branche `don-et-promesses` (vu en partie : « je donne la cloche a Gorm » partait au MJ ; Brune
  répondait « Je vais me pousser » sans que rien ne la fasse bouger, puis le MJ le rappelait
  comme acquis) : l'analyse locale reconnaît donner et remettre à la première personne et à
  l'impératif, avec « à », « au » ou « a », le destinataire avant ou après l'objet, chaque nom
  désignant exactement un objet et un personnage ; le moteur refuse ce qui manque. Après un
  refus, quelle que soit la voie, la réponse ne cite aucune parole nouvelle (contrôle
  déterministe, sans dépendre du verdict de l'auditeur). Une promesse d'agir d'un PNJ (verdict
  d'audit `engagement`) doit recopier ce que le moteur a enregistré : engagements pris, intention
  en cours, accords (`esprits_interlocuteurs.<id>.engagements`) ou l'issue qu'il vient de valider
  (`conversation_validee`) ; sinon elle est reformulée sans promesse. Luna sur la sauvegarde
  réelle : « Je vais me pousser » (Brune) et « je peux garder un œil sur la réserve » (Ilse)
  refusés puis reformulés. Limite : repérer une promesse reste un jugement de l'auditeur ; seul
  son appui est vérifié de façon déterministe.
- Branche `ouie` (`docs/plan-ouie.md`, `donjon/ouie.py`) : une règle d'ouïe commune
  au joueur et aux PNJ remplace `pnj.alerter`. Tout geste retentit selon sa nature, déclarée une
  fois (pas feutré < pas, geste ordinaire < voix < bruyant < appel) ; la distance et les passages
  l'atténuent ; seuil mieux aux aguets, moins bien au repos, modulé par la PER. Un bruit ordinaire
  de qui l'on croit là est attribué ; inconnu ou inhabituel, on se retourne de près (témoin par le
  registre), sinon on retient un bruit vers ce lieu, qui inquiète à la mesure de ce qu'on entend ;
  aller voir est un but du planificateur que décident le devoir de garde et, pour un fracas ou un
  appel, le courage ; le bruit de qui l'on se méfie se surveille. Le joueur entend par le même
  calcul et lit qui se retourne vers lui. Correctif révélé : un geste social vers qui n'est pas là
  corrige la croyance. Bancs : aucune usurpation ; vols vus au Relais 1 → 2,9 ; minutes sans
  recours égales ou moindres (auberge 584 → 584, mine 680 → 604). Limite : les réflexes déclarés
  gardent l'ancienne portée des sons.
- Branche `diagonales` : un pas en diagonale dure √2 fois un pas droit, à toute
  allure, pour le joueur et les PNJ (`temps.duree_pas`, 15 → 21 dixièmes) ; les chemins
  (`spatial.trajet`, le clic de la page) sont les plus courts en temps ; lumière, vue, ouïe et voix
  se mesurent en distance réelle arrondie à la case (`geometrie.distance`) : halos ronds, une
  diagonale voisine reste au contact. Bancs sans usurpation ni violation, même temps de calcul ;
  Brune, arrivée face aux témoins, attend avant de crocheter (plus de vols aboutis et vus). Détail
  et limites dans `docs/plan-temps.md` (« Correctif : les diagonales »).
- Branche `parole` (`docs/plan-ouie.md`, section Paroles) : le moteur fixe à qui
  parle le joueur (`paroles.analyser`, `paroles.destinataires`), celui qu'il nomme, sinon celui
  qui est en face de lui ; à égalité, le joueur précise. « à tous » vise tous les présents qui
  l'entendent, chacun décidant pour lui ; des guillemets en tête valent « je dis » ; chuchoter ou
  murmurer, à un seul, au contact. Toute parole à voix haute, du joueur ou d'un PNJ, est retenue
  de tous ceux qui en saisissent les mots (`ouie.mots_saisis`, `social.retenir_parole`) : une
  affirmation se juge comme une confidence, une nouvelle comme une rumeur, un aveu (nouveau
  contenu typé) se croit ; seuls les destinataires répondent (contrôle narratif déterministe).
  Sans personne en vue, une parole sans conteste est dite à la cantonade ; le MJ ne peut plus la
  raconter lui-même ni la changer en geste. Vérifié avec Luna sur des copies de la sauvegarde
  réelle (cas réel, aveu, guillemets, chuchotement, à tous). Correctif révélé : une parole qui confirme ce qu'on vient de voir ne le change plus en ouï-dire.
  Bancs : Relais identique (9,75 paroles surprises par nuit) ; mine et auberge, moins de
  confidences (les témoins savent déjà), plus de rumeurs crues et de méfiances à l'auberge ;
  minutes sans recours en hausse par des jets décalés (une part refusée à Gaspard, mine 2024).
- Branche `constater-et-rumeurs`, non fusionnée (`docs/plan-ouie.md`, « Constater, raconter où,
  chercher quelqu'un ») : trois manques de la mine et de l'auberge. **On constate ce que la main
  rencontre** : un geste manqué sur un objet cru dans un contenant ouvert, alors fermé, apprend le
  contenant fermé (verrouillé ou non, par l'essai) et garde l'objet cru dedans (`pnj._hors_d_atteinte`) ;
  Brune force de nouveau la réserve au lieu de croire les vivres disparues. **Le témoin d'un geste
  qui déplace un objet voit où il va** (`pnj._lieu_vu`, `prendre` et `poser`) : il le croit là, sa
  nouvelle porte le lieu (« … a posé le ballot de soie dans l'étable »), qui la croit en tire une
  croyance de lieu à confiance de ouï-dire, sauf constat propre postérieur (`social._apprendre_lieu`) ;
  qui sait depuis l'objet ailleurs tait le lieu ; le protecteur qui prévient la victime lui dit
  aussi où sont ses biens. Anselme reprend son ballot (graine 42). Ne pas avoir trouvé un objet ne
  dément plus qu'il soit ailleurs (`paroles.dementi`), le voir dans d'autres mains non plus
  (`esprits.reviser`). **Chercher quelqu'un** : en parcourant une salle où on le cherche sans le
  voir, on l'appelle (`pnj.appeler`) ; il répond, sauf à qui il reconnaît et dont il se méfie.
  Mireille trouve Odile au grenier noir au lieu de tourner une heure. **Se parler, c'est
  s'entendre et savoir qui parle** (accepté) : chacun saisit les mots de l'autre par l'ouïe commune
  (`ouie.s_entendent` : distance réelle, ouverture, porte fermée ; plus de `de_pres`) et le voit ou
  reconnaît sa voix ; on ne s'adresse qu'à qui l'on a vu ou reconnu (`pnj.identifie`,
  `croit_present`), jamais d'après sa place réelle. Chacun connaît ceux qu'il a vus ou entendus
  parler (`voix` de l'esprit, `data["voix_connues"]` du joueur, migrées) ; une voix connue dont on
  saisit les mots situe qui parle (`entendu`), une voix jamais entendue est un bruit inconnu. Le
  joueur : `ecoute` ne nomme qu'une voix connue, seules elles font savoir qui est là ; un échange
  qu'il ne voit pas ne s'écrit plus « X parle avec Y ». Salles désignées avec leur article
  (`francais.lieu`). Accordée avec `integration` (jusqu'à la lumière comme besoin) : une seule
  règle, `pnj.peuvent_se_parler`, pour toute parole échangée, y compris servir une part et la
  parole du joueur (refus distincts) ; on identifie aussi qui l'on verrait en se tournant vers sa
  voix (la lumière, pas le noir). Bancs contre `integration` (8 h) : aucune usurpation ni
  violation ; par nuit 4 appels au Relais, 7 à la mine, 17 à l'auberge, 9,8 à la crue ; minutes
  sans recours Relais 401 → 404, mine 636 → 665, auberge 581 → 628, crue 273 → 293 (des
  recherches qui aboutissent plus tôt laissent attendre une part promise ou refusée) ; vols vus
  inchangés hors la crue (1,5 → 1,3) ; minutes dans l'eau 318 → 259. Détail et limites dans
  `docs/plan-ouie.md`.
- Branche `rejeu-enrichi` (observation seule : `rejeu.py`, `web/rejeu.html`, option du banc) : le rejeu
  note la lumière de chaque case (même degrés que la page de jeu, recalculés quand sources, portes ou
  obstacles changent), chaque bruit émis avec ce que chacun qui l'a entendu en a fait (vu, attribué,
  retourné, bruit retenu, parole saisie, avec le niveau parvenu), les gestes illicites (qui était là, qui
  les voyait, qui en a été témoin et quand) et les « aller voir ». La page colore le sol, dessine une onde
  par bruit, montre ce que le personnage choisi entend et filtre le journal par personnage et par nature.
  `--rejeu` avec `--graines` écrit une page par graine. Une nuit de 8 h pèse 420 à 450 Ko (bruits 77 Ko,
  esprits 134 Ko, vues 73 Ko, lumière 4 Ko) ; la nuit reste identique (empreinte). Constats sur le Relais
  (graines 7 et 1985) : un « vol vu » compte un souvenir par geste d'une minute et par témoin, d'où 12 pour un
  seul cambriolage vu par deux personnes (graine 7, min 122 à 128, Brune forçant la réserve de l'antichambre) ;
  Brune guette 31 min sans rien tenter tant qu'un témoin est en vue, jusqu'à la faim à 95 (`DESESPOIR`),
  qui lève la précaution ; le fracas du crochetage (geste bruyant, même « sans témoin ») fait se retourner
  Ilse, de dos, qui devient témoin. Les 8 échanges de chaque nuit sont 6 demandes de part à Gorm, plus des
  dons ou la rumeur d'Ilse, au rythme de la faim, pas de la perception. Détail dans
  `docs/plan-vue.md`.
- Branche `banc-luna`, non fusionnée : Luna remesurée sur le moteur actuel (2 passes, `--fil`) et
  un banc `echanges` (parler sans nommer, guillemets, à tous, chuchoter, passage, pousser, donner,
  interpeller dans son dos ; la préparation d'un banc place des personnages et leur regard).
  Défauts communs corrigés : ce que Corvus a dans son dos (vu plus tôt, hors du cône) se nomme et
  se vise comme tout geste (`Monde.designable` : analyse du don, noms, liste d'un refus ; chaque
  souvenir visuel porte son identifiant et `vu_a`) ; une parole se tourne vers celui qu'on nomme
  dans son dos, et à même distance celui qui est droit devant est « en face » ; le récit d'un
  résultat reçoit les gestes exécutés (`gestes_accomplis`), que l'auditeur admet comme le
  narrateur ; écouter dit « contre la porte » ; un support trop loin se dit sans en détailler un
  autre ; patienter a la cible vide ; une citation recopiée avec ses guillemets reste la parole ;
  un refus d'improvisation nomme son seul champ fautif. Trois bancs (31 tours MJ), avant → après :
  3,50 → 3,26 appels et 16,7 → 15,3 s par tour MJ, replis 1 → 0,5, obstacles 14 → 9,5 ; tours
  avec refus 2 → 4, des « approche-toi » justes là où Luna supposait l'objet absent. Banc
  échanges : 2,75 → 3,0 appels, 13,5 → 12,5 s, obstacles 3 → 0,5, et les huit saisies traitées
  (avant : deux « précise à qui tu parles », deux « Ilse n'est pas ici » faux). Reste : la
  faisabilité d'une échelle (« est-ce que je peux… ») sans fait qui l'établisse, décrire un objet
  trop loin passe encore parfois par etablir_faits, un personnage dont la place connue s'est vidée
  n'est plus reconnu par son nom (`paroles._connu_du_joueur`).
- Branche `repli-et-appel`, non fusionnée (vu en partie : « pousse toi ca prend trop de temps »
  finissait sur « Je ne peux pas encore répondre avec certitude. » ; « Aubin, viens m'aider à
  porter l'échelle », Aubin derrière le pilier, finissait en dix appels ; « est-ce que je peux
  fabriquer une échelle ? » partait en conversation où Luna devinait). Trois règles communes.
  **Parole sans conteste** (décidé par l'utilisateur) : une saisie qui commence par des guillemets,
  un verbe de parole (« je dis… », « je lui dis… », « je demande à Gorm… », « je chuchote… ») ou « à
  tous » (`paroles.analyser`, `explicite`) n'est ni un dialogue du MJ ni un geste ; destinataire
  hors de vue : message du moteur sans appel ; MJ obstiné : le moteur prononce les mots du joueur
  (`mj.parole_du_moteur`). Une interpellation sans guillemets (« Brune, pousse-toi ») reste du
  texte libre ; si Luna en fait une parole, le moteur en fixe le destinataire. **Repli du contrôle
  narratif** (trois réponses refusées) : chaque relance reçoit tous les refus du tour ; le joueur
  lit ce que le moteur a établi (résultat, issue d'une parole), sinon les phrases admises de la
  meilleure réponse (`narration.rescape`), sinon ce que Corvus perçoit de ce qu'il vise et ce qui
  manque (`narration.repli`) ; un souvenir visuel est marqué `hors_de_vue` (l'auditeur refusait
  « tu ne la vois pas d'ici »). **Question de faisabilité** (« puis-je… ? ») : Luna propose le
  geste comme s'il était demandé, le moteur le prépare ou le refuse avec sa raison, et le joueur
  voit la même fiche sans rien exécuter (« Rien n'est encore tenté », puis tenter ou annuler) ;
  seules les perceptions répondent tout de suite (`commandes.PERCEPTIONS`). Luna, copies de la
  sauvegarde réelle et bancs ciblés : Aubin en face, « Aubin, viens m'aider… » devient une parole
  (3 appels) ; derrière le pilier, Luna répond qu'elle ne le voit pas (2 appels), « je dis à Aubin :
  … » reçoit le message du moteur (0 appel) ; devant les perches, « est-ce que je peux fabriquer
  une échelle ? » montre la fiche (52 min, sans jet) en 2 appels, « tenter » la fabrique ; trop
  loin, le moteur dit « Approche-toi de la perche… » ; « qu'est-ce que je vois au nord ? » reste
  une conversation (2 appels). Bancs de référence (1 passe, 31 tours MJ) : avant 3 replis, 9
  relances narratives, 3,32 appels par tour ; après 0 repli, 5 relances, 3,35 appels par tour
  (refus du moteur 3 → 7 : les questions de faisabilité passent désormais par lui). Limites :
  l'auditeur reste sémantique ; une interpellation libre peut encore être racontée par Luna sans
  rien faire dire ; « Gorm, je te donne la cloche » entre guillemets reste une parole. Détail dans
  `docs/plan-ouie.md` (« Correctif : ce qui est une parole sans conteste »).
- Branche `entretenir-feu`, non fusionnée (manques de la mine et de l'auberge : Odile et Mireille
  devant un foyer mort sans demander le bois de Joss ; le poêle de Josse tenu seulement par la
  dérive de son devoir ; Mathe servant Lucien en boucle). Trois règles communes. Une pulsion qui
  cesse d'être satisfaite est **rompue** (`esprit["pulsions"]` : True, False rompue, None désir
  jamais satisfait) : il la rétablit sans attendre que son besoin presse, quelle qu'en soit la
  cause (un feu qui baisse, un protégé qui a faim, ce qu'il a ouvert ou emporté lui-même) ; les
  rondes gardent leur routine, un désir attend son besoin. Un feu à entretenir peut employer le
  bois d'un autre : la part de combustible va au feu que le but entretient (le donneur le
  recharge et le rallume), on ne demande pas ce qu'on a sur soi, on ne prête pas ce qu'on garde
  (`echanges.garde`), une parole n'est tenue que sur ce qu'on a constaté depuis (un feu vu vif
  avant la demande se revoit), une part de bois est servie quand on a revu le feu rechargé.
  Servir un protégé : seulement s'il est cru affamé (la faim qui presse se voit, `etat` d'un
  personnage), et il le voit manger ; la pulsion de Mathe est remise. Cas vérifiés après
  rechargement (`tests/test_entretenir.py`) : Mireille demande les fagots de Joss, qui recharge
  le fourneau puis garde sa dernière charge ; Josse, devoir à 10 sans dérive, recharge son poêle
  de ses étais, puis sans étais obtient une part des bûches de Gaspard ; Mathe sert Lucien une
  fois ; Gorm, bois en main et sans flamme, va allumer la torche au lieu de demander des planches.
  Bancs (8 h ; `VERIFIER` sur 5 nuits) : Relais 8 graines, sans recours 428 → 401, événements
  23,3 → 26,5 ; crue 300 → 281 ; mine 668 → 670, poêle allumé 385 → 448 min (Josse obtient le
  bois de Gaspard), Odon, privé d'une part que Mathe a servie à Lucien, force le garde-manger ;
  auberge 573 → 673 : les demandes ont lieu (Joss donne une charge par nuit, Anselme garde les
  deux siennes), les trois foyers brûlent 622 → 710 min, mais le bois manque avant la fin de la
  nuit et le devoir, que rien n'apaise, reste urgent (Odile et Mireille inchangées) ; Anselme
  recharge son poêle à temps, ce qui déplace le crochetage de Lucien. Aucune usurpation. Limites :
  on ne demande que le bois qu'on connaît ; une part de bois promise s'attend 60 minutes si l'on
  n'a pas revu le feu ; une ancienne sauvegarde lit False comme rompue.
- Branche `lumiere-besoin`, non fusionnée, accordée avec `integration` (manque relevé par la mine :
  dans le noir, personne ne cherchait de lumière ; détail dans `docs/plan-planificateur.md`,
  « Lumière ») : une source qui consomme se recharge de ce qu'elle brûle (`perception.recharge` :
  son contenu déclaré, un foyer brûle du bois ; une torche, sans contenu déclaré, ne se recharge
  pas) ; `alimenter` vaut pour le joueur, le MJ, le stratège et les PNJ, verser de l'huile dans la
  lampe aussi. La mine déclare l'huile de ses lampes et un bidon d'huile à la réserve. Dans le noir,
  qui le craint (`peur_du_noir`) cherche à avoir de la lumière (recours de la sécurité, avant
  l'abri) ; le planificateur trouve les moyens par ses gestes : allumer une source à une flamme
  portée ou fixe, la recharger, prendre une lampe, la demander, rejoindre un lieu éclairé. Toute
  minute dans un lieu qu'il croit obscur lui coûte (`NOIR` × sa peur) : il allume sa lampe avant
  une ronde dans le noir ; la lampe qui l'éclaire ne se ménage ni ne se prête. Une salle se croit
  éclairée par ce qui y est posé, pas par ce qu'on y porte (lui ou un autre) : la lampe d'un
  passant ne fait pas éteindre la sienne. Accord avec `entretenir-feu` : la pulsion rompue du
  poêle fait rallumer le feu (part de bois demandée) ; celui qui avait allumé sa lampe la ménage
  alors. Bancs contre `integration` (8 h, `VERIFIER` sur une nuit de chaque scénario, aucune
  usurpation) : Relais 7 graines sur 8 identiques ; sans recours mine 670 → 636, auberge 673 →
  581, crue 281 → 273. Auberge : aux rondes, Odile allume la lampe du comptoir, Hugues sa
  lanterne ; Lucien quitte le grenier noir pour le couloir éclairé, puis va et vient entre sa
  garde et la lumière. Mine : la dernière flamme est le briquet de Gaspard, que personne ne
  retrouve dans le noir ; ceux qui craignent le noir vont vers la lumière dont ils se souviennent
  (le bureau) et Bram n'y est plus seul.
- Branche `feat/websocket-persistant` (Codex, `docs/integration-websocket.md`) : en mode forfait
  ChatGPT, le MJ parle à Luna par une WebSocket Responses persistante (`donjon/transport_openai.py`),
  ouverte au premier appel et partagée par l'interprétation, les audits et la narration. Chaque
  demande renvoie instructions, outils et contexte complets (`store: false`, aucun historique
  serveur) ; seul `response.completed` est validé. Jeton renouvelé, socket fermée ou âgée de
  55 min : nouvelle ouverture ; coupure pendant une demande : une reconnexion et une reprise du
  même appel dans le même délai (45 s pour l'échange entier, et non plus par lecture). Le mode
  API garde HTTP. Microbanc (`tmp-worktrees/ttft-luna-medium`) : premier jeton −32 %, durée d'un
  appel −17,5 % contre HTTP. Vérifié après fusion : deux parties réelles avec une coupure
  simulée chacune (4 ouvertures, 4 fermetures, une seule exécution de l'action).
  Dépendance `websockets` (`requirements-chatgpt.txt`).
- Branche `voix` (`docs/plan-ouie.md`, « Les voix » ; `donjon/voix.py`). Deux manques :
  l'appel par le nom ne passait pas une porte fermée (Hugues appelait Anselme en boucle, Aubin Gorm
  à chaque minute) ; une voix inconnue n'était qu'un bruit, et voir quelqu'un faisait connaître sa
  voix. **Héler** est un cri (nature `hele`, 9 crans) : les mots saisis disent qu'on appelle tel nom,
  sans alarme ; le cri seul est un bruit fort inconnu ; « Ici ! » répond, hélé, et vaut se nommer ; un
  appel sans réponse compte la salle pour parcourue dans la recherche (`deliberation.appels_vains`,
  60 min). **Se parler** = s'entendre (`pnj.peuvent_se_parler`, règle unique) : une voix qu'on ne sait
  à qui prêter est un étranger (`voix.fiabilite`, `voix.INCONNU`), à qui le prudent répond « Qui va
  là ? » (`echanges.accueil`) ; le joueur parle dans le noir, le refus « ne saurait pas qui lui parle »
  disparaît. **Voix** : on connaît la voix de qui l'on a entendu parler en le voyant, ou que le
  scénario fait connaître (un savoir) ; plus à la simple vue ; chacun retient les voix inconnues et ce
  qu'elles prétendent ; toute reconnaissance passe par `voix.reconnaitre` (où se brancheront
  l'imitation et la méfiance). **Se nommer** (contenu `nom`, et `qui` pour « Qui est là ? ») : démasqué
  par la vraie voix, sinon cru sur parole (lieu `se_dit`) sans jamais plus de confiance qu'un inconnu,
  démasqué après coup quand on entend la vraie voix, puis le menteur reconnu. Le MJ ne connaît une voix
  inconnue que comme « voix_<n> » (« une voix qui se dit Brune »), sans identifiant ni traits ; contrôle
  déterministe : sa réplique ne nomme personne au-delà de ce que le moteur a établi, le récit ne lui
  donne pas son nom prétendu (`narration.voix_inconnues`). Plus de migration des anciennes sauvegardes
  (décision de l'utilisateur). Bancs (8 h, 4 graines, avant → après) : sans recours Relais 362,5 → 335,
  mine 665 → 655, auberge 627,5 → 670, crue 292,5 → 301 ; appels / réponses auberge 17 / 2,25 → 3,5 /
  2,75, mine 7 / 0,75 → 2,5 / 2,5 ; aucune usurpation. Luna (copies de scènes) : demande refusée à la
  voix dans le noir, « c'est Corvus » cru sans confiance, « c'est moi, Brune » démasqué, une voix
  inconnue nommée par le moteur puis « la voix » dans le récit ; deux défauts de Luna vus et corrigés
  par le contrôle (voix qui se disait Brune d'elle-même, « Brune répond » dans le récit). Limites dans
  `docs/plan-ouie.md`.
- La suite de tests passe : 920 tests, sans clé ni connexion (ceux du clic demandent Node).

## Décisions en attente

- **Fabrication générale** (`docs/plan-fabrication.md`) : étapes 1 à 3 fusionnées ; l'étape 4
  (d'autres usages : passerelle, cale…) attend un accord. Limite : les planches du Relais ne
  suffisent pas à une échelle (deux pièces, à Aubin) ; l'assemblage de planches est vérifié en
  test sur l'atelier, pas en partie au Relais.
- **PNJ d'abord, joueur passif** : la crue du Relais comme scénario d'étude (`docs/plan-crue.md`,
  étape 3, le niveau d'eau, faite ; suite : influence et relations) ;
  caractères, valeurs, relations, lire les autres, contrainte et groupes (`docs/plan-social.md`).
  Faits : temps fin et orientation, jeu dans le navigateur, caractères et valeurs (sans
  l'empathie), niveau d'eau, l'ouïe et la parole (`docs/plan-ouie.md`) ; réglages de l'ouïe à trancher : l'échelle, le crochetage en geste bruyant,
  l'inquiétude d'un bruit inconnu, le courage qui fait aller voir ; à fondre ensuite : les réflexes
  déclarés et le souvenir « son » dans l'ouïe commune.
- **Manques relevés par la mine et l'auberge** : avoir de la lumière comme but (branche
  `lumiere-besoin`) ; prêter et permissions déléguées ; l'argent ; un besoin que rien n'apaise (le
  devoir reste urgent une fois franchi son seuil). Demander du bois pour un feu et le protégé
  nourri en boucle : branche `entretenir-feu`. Chercher quelqu'un dans le noir, le lieu dans une
  rumeur et le contenant fermé cru ouvert : branche `constater-et-rumeurs`.
- **Voix** (branche `voix`) : imiter une voix, plus ou moins bien (un changelin qui dupe les PNJ),
  puis des PNJ qui, sachant qu'un imitateur rôde, se méfient même d'une voix connue. Préparé : toute
  reconnaissance passe par `voix.reconnaitre` (`docs/plan-ouie.md`, « Suite prévue »).
- **Instructions conditionnées à l'état du monde** : plus tard ; critère retenu, inclure une
  règle quand le moteur pourrait valider ce type de proposition dans l'état actuel, jamais
  selon un lieu ou un scénario.
- **Suite du plan PNJ**, au choix (la crue est reprise dans `docs/plan-crue.md`) :
  - un événement qui éteint le feu en laissant du bois (les `horloges` existent, aucun
    scénario n'en déclare encore) ;
  - la voix des PNJ : Luna donne voix aux échanges entre PNJ dont le joueur est témoin, et
    les répliques ne contredisent plus l'issue décidée par le moteur ;
  - une protection plus riche ; d'autres remèdes au froid ;
  - la priorité du stratège aux PNJ que le joueur perçoit.
- **Branches d'essai**, poussées sur `origin` et non fusionnées :
  - `essai-code` : le MJ écrit un script Python borné au lieu du JSON ;
  - `essai-haiku` : premier adaptateur Anthropic, remplacé par celui de `banc-haiku`.
  Les mesures sont rapportées dans leurs commits.

## Reprendre sur un autre poste

1. `git clone https://github.com/msicsic/jdr.git`, puis l'installation du README (`.venv`,
   `requirements-tui.txt`, `requirements-chatgpt.txt`).
2. Connexion de Luna : `python connexion.py connecter` (forfait ChatGPT, voir
   `docs/connexion.md`). L'autorisation (`.seuil-auth/`) n'est pas versionnée et se refait
   sur chaque poste.
3. Clés éventuelles dans `.env`, non versionné : `OPENAI_API_KEY` pour `--connexion api`.
   `ANTHROPIC_API_KEY` pour `--connexion anthropic` (Haiku, `requirements-claude.txt`).
4. Vérifier : `python -m unittest discover -s tests -q`.

Non versionnés, donc absents d'un nouveau poste :
- `sauvegardes/` ;
- `artifacts/` (chroniques et verdicts des bancs, traces du MJ). Les bilans chiffrés des bancs
  sont recopiés dans `docs/plan-pnj.md`.

## Outils de mesure

- Banc moteur seul, sans appel à Luna, avec son récit (`--chronique` pour chaque pas) :
  `python -m donjon.banc_pnj --heures 8 --graine 1985 --joueur chambre_cloche` ; plusieurs nuits
  en parallèle, avec le tableau des mesures et leur moyenne : `--graines 1985 7 42 2024`.
  `--diagnostic` ajoute les recherches du planificateur par PNJ et par but (issue, reprises de
  la mémoire, nœuds, durée), aussi dans `--sortie`.
  `--scenario crue` joue la crue : récit de l'eau (tirage, salles gagnées, feux noyés, où chacun
  finit) et mesures `minutes_dans_l_eau`, `feux_noyes`, `trempes_fin`, `au_sec_fin`.
- Banc A/B du stratège, avec Luna, environ 15 minutes pour 8 graines :
  `python tools/banc_stratege.py --graines 1985 7 42 2024 --graines-sup 3 11 99 500`
  Plusieurs exécutions Luna peuvent tourner en même temps (le coffre sérialise le renouvellement
  du jeton ; 4 vérifiées) : en rester à quelques-unes, et mesurer les temps au calme.

## Règles de travail

- `AGENTS.md` : corriger l'invariant général, jamais le cas de l'exemple ; vérifier le cas réel
  et un autre cas de même nature après rechargement ; dire les limites.
- Une branche par jalon, fusionnée avant d'ouvrir la suivante ; pas de nouveau mécanisme en
  cours de jalon sans accord.
- Les phrases des docs tirées d'un test ou d'un scénario décrivent ce scénario, pas une règle
  de conception du jeu.
