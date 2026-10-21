# État du développement

Point de reprise, à tenir à jour à chaque fin de jalon. Mis à jour le 2026-10-21.

## Où on en est

- Branche `refactor/adaptateurs-fournisseurs`, non fusionnée : `MJ` commun et adaptateurs OpenAI,
  Anthropic et MiMo expérimental, contrats de requête/réponse/erreur séparés ; 984 tests passent.
  Voir [la séparation des fournisseurs](adaptateurs-fournisseurs.md) et son compte rendu de vérification.
  Adaptateur MiMo terminé : choix explicite `--connexion mimo`, flux complet, une correction JSON bornée,
  banc migré, 998 tests passent et deux actions réelles réussies en 8 appels. Voir [MiMo](mimo.md).
  [Campagne complète de l'adaptateur final](mimo-campagne-complete.md) : 90 saisies, 38 tours MJ,
  120 requêtes réelles, sept rejets de format corrigés, aucun tour en erreur technique ; TTFT médian
  2,18 s et quatre reprises vérifiées. Défaut restant confirmé : MiMo ajoute des idées à la parole du joueur.
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
  Restent hors périmètre : les messages d'audit (contrôle narratif, contre-revue) ; faits ensuite,
  branche `audits-attendu`.
- Branche `contre-revue` : le raccourci `detacher` libère la fixation sur place (la prendre
  est une étape `deplacer` explicite) ; un rapport de contre-revue mal formé est redemandé
  une fois puis le plan validé passe, au lieu d'être renvoyé au MJ comme un refus. Cas réel
  « fais levier sous l'axe » : 2 appels, conforme du premier coup (contre 4 à 8 avant).
- Branche `banc-haiku` : Claude Haiku 5.5 est une option du jeu (`--connexion anthropic`,
  `donjon/fournisseurs/anthropic.py`, `requirements-claude.txt`) ; Luna reste le MJ par défaut. Correctifs
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
  n'est plus reconnu par son nom (`paroles._connu_du_joueur`). Les deux premiers : branche `mj-restes` ;
  le troisième : branche `parole-voix`.
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
- Branche `echanges-argent`, non fusionnée (manques de l'auberge : un objet prêté restait illicite
  pour l'emprunteur ; l'argent n'existait que pour le joueur ; détail et bancs dans
  `docs/plan-social.md`, « Argent, prêts et garde confiée », règles du joueur dans
  `docs/mecaniques.md`, « Prêter, confier, payer »). **Permissions** (`donjon/biens.py`) : un
  prêt (`data["permissions"]`, clos quand l'objet revient à son propriétaire) ou une garde
  confiée (tâche acceptée sur un bien de qui la confie, pulsion déléguée) font user du bien
  d'autrui sans faute, au plan, à l'exécution, aux yeux des témoins et pour le joueur ; une clé
  prêtée ouvre ce qu'elle ouvre, pas le contenu ; rien ne permet de consommer. Remis par son
  propriétaire, un objet qui dure est prêté, ce qui se consomme donné ; l'emprunteur PNJ le rend
  quand il ne lui sert plus, le propriétaire le récupère en le redemandant ; on ne demande un
  objet qu'à son propriétaire. **Argent** : bourse par PNJ (`finances_pnj`, 5 par défaut),
  objets à pièces, prix d'une part ou d'un objet ; une pièce vaut pour chacun (10 + dette,
  proches, projet pesés par ses valeurs) / (10 + richesse) minutes, au plus 6
  (`caractere.valeur_piece`) ; geste `acheter` du planificateur, vente acceptée au prix sans jet
  sauf ce qu'il garde ou méfiance, don d'autant plus dur que la pièce lui est chère ; dernier but,
  prendre des pièces qui valent plus que le chemin et la faute ; le joueur paie une part, un
  objet ou un passage dans sa parole (`valeur`), au plus son or (`attendu` sinon). Situations,
  bourses et prix déclarés dans les quatre scénarios ; valeurs retouchées à la mine (Odon, Bram,
  Josse, Mathe) et à l'auberge (Anselme, Mireille, Mathurine, Hugues, Lucien, Odile) ; la paie de
  la mine (200) et une bourse d'Anselme (150) ; pas de migration des anciennes sauvegardes.
  Accordée avec `main` après `voix` : une voix inconnue qui offre de payer ou réclame son bien
  s'entend d'abord demander « Qui va là ? » (`echanges.accueil`), puis la vente vaut. Bancs contre
  `main` 1e96cb6 (8 h) : minutes urgentes sans recours Relais 393 → 294, mine 655 → 463, auberge
  670 → 690, crue 301 → 445 ; achats par nuit 1,6 / 1 / 0,75 / 2 ; aucune usurpation ;
  `VERIFIER` sur une nuit de chaque scénario. Au Relais, Ilse et Aubin refusés achètent leur part,
  Brune (honnêteté 20, endettée) vole encore ; à la mine, Odon endetté guette la paie et s'acharne
  sur le coffre dans le noir (mine 15 → 23 s) ; à la crue Brune (50) achète au lieu de voler, d'où
  Gorm au devoir sans rien à faire et Ilse au refuge, dans l'eau, au lieu de la galerie. Limites :
  aucun prêt ni vol de bourse au banc (Odon ne sait pas ouvrir la porte du bureau, personne ne
  connaît la bourse d'Anselme), une part payée non servie n'est pas remboursée, pas de
  marchandage ni de tâche payée entre PNJ.
- Branche `mj-restes`, non fusionnée (`docs/plan-ouie.md`, « Correctif : ce que le MJ ne raconte
  plus sans le moteur ») : les restes des bancs Luna. **Parole** : sans parole de Corvus validée ni
  geste résolu, le récit ne fait pas parler Corvus (« tu demandes à Ilse… », « dis-tu » :
  `narration.parole_racontee`) et, saisie adressée à quelqu'un ou après un refus, personne ne répond
  par une citation nouvelle (`narration.paroles_sans_moteur`, déterministe) ; une interpellation libre
  que son destinataire entendrait, répondue en dialogue, est renvoyée une fois sans contrôle
  (`mj.renvoi`) : parole, geste (« Gorm, je te donne la cloche » → remettre), ou dialogue contrôlé.
  **Détail de loin** : le refus du moteur (détail ou description physique d'un objet hors de portée,
  une cause, `attendu`) passe avant la contre-revue sémantique (`mj.refus_assure`) ; les faits disent
  que de loin les détails d'un objet échappent (un personnage reste décrit de souvenir) ; les
  consignes ne promettent plus la description d'un objet seulement vu. **Faisabilité** : « puis-je… ? »
  (`commandes.faisabilite`) répondu en dialogue est renvoyé une fois ; refusé par le moteur, le joueur
  lit sa raison, pas une explication libre ; un rôle vide d'un assemblage ou d'un franchissement dit
  ce qui manque et s'il y a de quoi le tenir parmi ce que Corvus peut désigner. Le cas « « Gorm, je te
  donne la cloche » » reste une parole (voulu) : « Tu dis à Gorm : « … » », la cloche reste dans la
  besace, Gorm répond sans la prendre. Luna, copies de la sauvegarde réelle : « est-ce que je peux
  fabriquer une échelle ? » (« possible en principe… » → « il te manque un lien… rien de tel n'est à ta
  disposition ici »), perches trop loin (« Oui, une échelle est une possibilité… » → « Approche-toi de
  la perche de bois 1… », 1 appel), mur trop loin (trois refus de la contre-revue, 30 s → refus du
  moteur puis réponse par ce que Corvus voit), « Gorm, je te donne la cloche » sans guillemets
  (« Gorm acquiesce » sans rien changer → la cloche remise). Bancs contre `main` 789be7a, même
  transport (WebSocket), 2 passes, relais + crypte + atelier + échanges (38 tours MJ) : 3,04 → 3,14
  appels et 13,9 → 14,0 s par tour MJ, 0 repli des deux côtés, tours avec refus 6,5 → 6,5, obstacles
  narratifs 2,5 → 5,0 (tous sémantiques, aucun des nouveaux contrôles ; l'étendue des passes couvre
  l'écart) ; l'échelle de l'atelier 3 → 1,5 appel. Trois bancs écartés (coupures réseau, quota).
  Limites : le récit d'une parole est repéré par ses formes (deuxième personne), une réaction sans
  citation (« Gorm acquiesce ») n'est arrêtée que par le renvoi ; la faisabilité ne se juge pas à
  distance (le joueur lit « approche-toi », pas la fiche) ; une règle d'auditeur « personne ne réagit
  sans conversation_validee », essayée, faisait refuser à tort des réponses validées et a été retirée.
- Branche `planif-defauts`, non fusionnée (`docs/plan-planificateur.md`, « Défauts corrigés ») :
  trois défauts du planificateur des PNJ. **Chance crue** : la chance de crocheter est celle du jet
  réel (`pnj.seuil_crochetage`) à la lumière qu'il croit là où il se tient (`lumiere_crue` ; la
  croyance d'une salle porte son niveau, `esprits.constater_lumiere`) ; plus de chance plancher,
  un geste impossible n'est pas envisagé, un essai manqué fait constater la lumière qu'il avait.
  **Portes** : une porte qu'il croit verrouillée se crochète comme un contenant (même chance,
  faute, bruit), puis la route y passe (`pnj.chemin`, `ouvertes`) ; la porte du bureau est à Bram.
  **Pièces crues** : `enrichir` compte la croyance `pieces` (en tenant la bourse, ou savoir : la
  paie de 200 que sait le camp), jamais l'objet. Cas réels et cas de même nature après
  rechargement (`tests/test_planif_defauts.py`), `VERIFIER` sur une nuit de chaque scénario. Bancs
  8 h contre `main` (au même moment) : sans recours Relais 294 → 296, mine 463 → 449, auberge
  690 → 643, crue identique ; essais de crochetage mine 28,5 → 0,75, auberge 31,5 → 0,25 (Odon et
  Lucien s'acharnaient dans le noir), Relais 3,6 → 3,5 ; achats égaux ; vols vus auberge 1 → 0,25
  (plus de fracas à voir) ; aucune usurpation ; temps d'une nuit égal, auberge 28 → 32,5 s. Odon
  envisage la porte du bureau mais le baraquement n'est jamais sans témoin : il renonce (aucune
  porte crochetée au banc). Limites : lumière crue de la case où il se tenait (un essai perdu au
  plus), pas de « forcer » pour les PNJ, contenu d'une bourse appris seulement en la tenant.
- Branche `depart-tire`, non fusionnée (`docs/plan-crue.md`, « Le départ tiré de la graine ») : les
  nuits étaient presque déterministes (au Relais, une seule nuit jusqu'à la minute 5, deux jusqu'à
  120 sur 16 graines ; tout le hasard venait du d20). À la création du monde, le moteur tire le
  départ de la graine par un tirage à part (`donjon/depart.py`, `seed:depart`, les d20 inchangés),
  une fois, gardé dans `data["depart"]` : états du corps (repas, veille, trempé) à 20 % près, besoins
  du profil à 10 points près, périodes de ronde à 20 % près et la prochaine ronde dans la première
  moitié de sa période (au départ déclaré, toutes tombent à la minute 0), échéance des horloges à
  25 % près ; aucun besoin tiré au-delà de 85, sauf déclaré plus haut. Bornes déclarées par les
  quatre scénarios (`depart.bornes`), défauts du moteur sinon ; `depart="fixe"` (constructeurs,
  `banc_pnj --depart fixe`) garde le départ déclaré, et les tests de scène partent de lui. Banc :
  empreintes de l'état aux minutes 5, 60, 120, 240, 480 et issue de la nuit (`divergence`), jets
  par heure ; une pulsion confiée à qui l'on croit fiable compte à part (`minutes_urgentes_confiees`),
  plus « sans recours » ; `echanges` sans les appels ni leurs réponses. Bancs 8 h, fixe → tiré :
  Relais (16 graines) nuits distinctes à 5/60/120/240/480 min 1/2/2/6/10 → 14/16/16/16/16, issues
  4 → 13 ; mine 3/2/2/2/4 → 8 partout ; auberge 1/1/3/8/8 → 8 partout ; crue 2/4/6/7/8 → 8 partout.
  Aucune usurpation ni violation, `VERIFIER` sur une nuit de chaque scénario. Limite relevée : au
  Relais, Gorm n'est plus d'office au refuge à la première minute, et Brune affamée vole dès qu'il
  s'éloigne (minute 3 dans une nuit sur 16, ~30 dans deux) ; jugé dans son caractère, à revoir si
  l'on veut un premier acte plus long.
- Branche `besoins`, non fusionnée (`docs/plan-planificateur.md`, « Dynamique des besoins » ; vu au
  banc : Lucien, à l'auberge, allait et venait entre le grenier noir où il garde ses affaires et le
  couloir éclairé, 19 changements de salle en 4 h). Trois règles communes. **L'effet de seuil**
  (`deliberation.urgents`, `eveiller`, `esprit["urgences"]`) : apaisé, un besoin ne presse de
  nouveau qu'à son seuil + `REPRISE` (15), sauf s'il est d'abord descendu sous seuil − 15 (comblé) ;
  au choix du but, un besoin n'interrompt le plan d'un autre que s'il presse plus que lui
  d'`INERTIE` (5). **Ce qu'un plan laisse monter** (`planification.Vue.pression`, `RESTER` 30,
  `GARDE` 2) : une minute coûte le noir pour qui le craint et chaque lieu gardé dont on est loin ;
  un but qui se tient en restant (lumière, garder, abri, se chauffer) compte 30 minutes de ce que son
  état final laisse monter, et la recherche continue au-delà du premier état qui l'atteint ; pour la
  lumière et la garde, on ne part que si le plan coûte moins que rester (sinon on endure : issue
  « endure » du diagnostic, que `--diagnostic` compte désormais au lieu de planter) ; l'abri compte
  aussi ce qu'il apporte. **L'attente** (`deliberation._classer`, `attentes`) : un besoin dont chaque
  recours a été essayé sans plan attend, sans être oublié ; le banc distingue
  `minutes_urgentes_en_attente` (aucun plan sur ce qu'il croit) de `minutes_urgentes_sans_recours`
  (un plan possible, non entrepris) et des pulsions confiées (`depart-tire`) : chaque PNJ oisif dans
  une seule catégorie. Correctif commun révélé, accordé avec la croyance à niveaux de
  `planif-defauts` en une seule règle (`esprits.constater_lumiere`) : sur place, il juge à la lumière
  de sa case, lueur voisine comprise (`niveau`, chance du crochetage) ; de loin, à ce que la salle
  tient de ses propres sources (`propre`, `eclairee`, `deliberation.lumiere_crue`) : le seuil d'une
  salle obscure ne la fait plus croire éclairée (alternances lumière ↔ abri à l'auberge 15,75 → 0
  par nuit). Cas vérifiés après rechargement (`tests/test_dynamique_besoins.py`) :
  Lucien rapporte la lanterne de l'étable au grenier et y reste (5 changements de salle) ; Bram
  (mine) prend la lampe du filon et revient garder la paie ; sans lumière à emporter, le plus fort
  l'emporte et l'autre besoin attend ; le devoir de Gorm attend puis reprend ; la faim refusée attend
  puis redemande (scènes en départ fixe). Bancs 8 h, départ tiré, contre `main` 87c1ed5 (Relais 8
  graines, autres 4, lancés ensemble) : minutes sans recours Relais 117 → 53, mine 369 → 56, auberge
  665 → 68, crue 81 → 45, le reste passe en attente (oisives totales égales à 2 % près, confiées
  inchangées) ; événements égaux ou en hausse, échanges égaux sauf l'auberge 20,25 → 23,75 ;
  va-et-vient entre deux besoins Relais 8,25 → 8,1, mine 13 → 6, auberge 19,25 → 2,25 (le cas réel de
  Lucien, revenu au banc avec le départ tiré : 70 → 3 en quatre nuits), crue 4,75 → 5,5 (les rondes
  de Gorm) ; vols vus égaux (Relais 0,9 → 1, crue 0,5 → 0,75) ; aucune usurpation ni violation ;
  `VERIFIER` sur une nuit de chaque scénario. Temps d'une nuit (`main` et branche lancés ensemble) :
  Relais 4,8 → 5 s, mine 16,6 → 17,2 s, auberge 18,7 → 21,1 s, crue 6,6 → 6,8 s ; aucun élagage
  exact trouvé pour l'auberge (Lucien refait chaque minute une recherche `garder` que la mémoire ne
  reprend pas, le prix d'une faute variant avec la détresse). Limites : `GARDE` est une constante du
  moteur ; seuls le noir et la garde coûtent par minute ; un besoin apaisé sans être comblé monte
  jusqu'à seuil + 15 (au départ fixe, Ilse hésitait deux fois entre l'abri et le brasero) ; la peur
  du noir ne s'émousse pas ; Odon, qui sait crocheter la porte du bureau, y fait fuir Bram (le test
  de Bram le rend honnête) ; pas de migration, le champ `urgences` vient par défaut. Les échecs de
  `tests/test_tui.py` (« La TUI n'est pas redevenue disponible ») viennent de la charge de la machine
  (attente bornée à 5 s) : les mêmes cinq échouent sur `main` sous charge, tous passent au calme sur
  les deux. Corrigé : branche `parole-voix`.
- Branche `parole-voix`, non fusionnée (`docs/plan-ouie.md`, « Nommer, attendre, héler ») : quatre
  correctifs. **Tests du terminal** : `tests/test_tui.py` attend un état (`attendre`, `pret`) avec un
  délai de 60 s qui tient sous charge, au lieu de 250 tours de 20 ms ; un arrêt du jeu échoue aussitôt
  et l'échec dit l'état observé. Démarrage du jeu ralenti de 20 s : `main` échoue, la branche passe ;
  27 tests sous charge (deux bancs de 8 nuits, 30 processus) et au calme : verts. **Nommer qui l'on
  connaît** : le joueur connaît un personnage vu (`data["personnages_vus"]`, `Monde.identifier`, aussi
  qui n'a été qu'aperçu), dont il connaît la voix ou dont une voix s'est donné le nom
  (`paroles.identites`), jamais d'après une place ; nommer un absent connu donne le refus juste (parole :
  « Tu ne vois pas Ilse d'ici », don : « … n'est pas là pour le recevoir ») ; le MJ reçoit
  `personnages_connus`, sans place. **Qui répond attend** (`deliberation.attendre_l_appelant`, esprit
  `rejoint`) : 5 minutes sur place, sauf un besoin qui presse, la parole due, prévenir, ce qu'il fait sur
  place ; la routine, un bruit à voir, l'argent cèdent aussitôt ; s'il cherche l'appelant et reconnaît sa
  voix, il va vers lui ; fin quand ils se voient ou se parlent, ou à l'échéance. **Le joueur hèle** :
  « j'appelle Gorm », « je hèle Gorm », « je crie le nom de Gorm », « je crie « Gorm ? » »… (analyse locale,
  `paroles.hele`, même en forme de question) sont le geste `emettre_son` méthode `heler`, par la règle
  des PNJ (`pnj.heler` puis `pnj.repondre`) : l'appelé répond « Ici ! » sauf méfiance et l'attend, le
  joueur entend la réponse par l'ouïe commune (« Gorm répond », ou « une voix qui se dit Gorm
  répondre »). Cas réels et cas de même nature après rechargement (`tests/test_parole_voix.py`),
  `VERIFIER` sur une nuit de chaque scénario. Bancs 8 h contre `main` 1ee493b, lancés ensemble : appels
  Relais 1,25 → 1, mine 2,75 → 2,5, auberge 6 → 6, crue 2,75 → 2,25 (12 graines : 2,33 → 1,67 ; graine 3,
  7 → 3) ; 1 à 2 retrouvailles par nuit, attentes vaines 0 à 0,25 ; échanges, minutes sans recours, vols
  vus identiques ; en attente Relais 67,5 → 68,1, crue 105 → 106,25 ; aucune usurpation ; temps égal.
  Luna (copies de la sauvegarde réelle) : « j'appelle Gorm » derrière la porte, 4 appels et « tu ne peux
  pas l'interpeller » → 0 appel et la réponse du moteur ; « j'appelle Ilse » absente, 6 appels → 0 ; « je
  donne la cloche à Ilse » 2 → 0 (refus du moteur). Limites : une interpellation libre d'un absent reste
  au MJ (2 à 10 appels selon les parties) ; l'attente se juge à la minute ; `REJOINT` constant.
  les deux.
- Branche `petits-correctifs-pnj`, non fusionnée (poussée sous `claude/petits-correctifs-pnj-gtlo8g` ;
  `docs/plan-planificateur.md`, « Petits correctifs », et `docs/plan-social.md`, « Une part payée et
  jamais servie »). Quatre règles communes. **Lumière devant la serrure** (`pnj._assez_de_lumiere`) :
  l'étape `crocheter` porte la lumière prévue ; devant, il constate la sienne et la retient de l'objet
  (croyance `lumiere`) ; moindre ou nulle, il renonce sans essai et replanifie (Odon au coffre de la
  paie, Brune à la réserve). **Part payée non servie** : à l'échéance (240 min) ou dès qu'il ne peut
  plus la servir, le vendeur doit le prix (`data["dettes"]`, `biens.rembourser`, `solder`), rendu dès
  qu'ils se savent ensemble ; le joueur le lit ; un PNJ va réclamer son dû (but `reclamer`).
  **Forcer** pour les PNJ (`donjon/force.py`, geste `frapper`) : la règle du joueur partagée, faute
  au prix de l'honnêteté et dégât au prix de la douceur sur le bien d'autrui ; Brune force la porte
  étanche, Gorm sans clé la force pour la cloche. **Gorm et les planches** : diagnostiqué au coût des
  plans ; les vannes, baignées de la lueur diffuse du brasero, étaient crues noires (`propre` compte
  désormais la lueur diffuse, `esprits.lumiere_ici`) et une part demandée comptait comme accordée
  (elle coûte désormais 1 + `DEMANDE` / `PRET`) ; quand ses biens le pressent, `GARDE` le fait encore
  acheter. Bancs 8 h contre `main` (même moment) : sans recours auberge 67,5 → 15, autres égaux ;
  achats en hausse partout (Relais 1,1 → 2, auberge 0,25 → 2,25) ; crochetages à l'auberge 13,5 →
  3,75 essais ; aucun forçage au banc (les PNJ qui prendraient le bien d'autrui ont la douceur à 100) ;
  un remboursement en 8 nuits au Relais ; nuits toutes distinctes ; aucune usurpation ni violation ;
  `VERIFIER` sur une nuit de chaque scénario ; temps mine +20 %. Tests changés et pourquoi :
  `test_entretenir` (Mireille achète au lieu de demander), `test_besoins` (Gorm force la porte, le cas
  sans outil gardé), `test_auberge` (seuil d'événements à 12 : 14 dans cette nuit), `test_mine` (la
  nuit 3, départ fixe : le blessé allume une lampe de rechange à la réserve ouverte au lieu d'appeler
  dans le noir, et Bram est éclairé par celle d'Odon). Limites : la lumière devant une serrure est
  celle qu'il y a vue en dernier (une source posée près d'elle depuis ne compte qu'à son retour ou
  avec la lumière de son plan) ; la chance d'une demande reste une constante (`PRET`) ; forcer ne
  sert qu'à lever une serrure fermée à clé, et abîmer ce qui n'est à personne ou à soi ne coûte que
  le temps et le bruit ; la lueur diffuse est supposée égale dans toute la salle (un recoin qu'elle
  n'atteint pas serait cru en pénombre) ; Gorm achète encore les planches d'Aubin quand ses biens le
  pressent (`GARDE`) ; tout débiteur rembourse, quelle que soit son honnêteté ; le joueur ne réclame
  pas par une parole typée et ne voit la dette qu'au remboursement ; seule une part vendue d'avance
  crée une dette.
- Branche `voix-inconnues`, non fusionnée (`docs/plan-ouie.md`, « Les voix inconnues ») : trois limites de
  la branche `voix`. **Demande d'une voix inconnue** : revue, la part « impossible » de la mine venait de la
  réserve verrouillée (même issue pour une voix connue) ; la règle tenait (étranger, `voix.INCONNU`), vérifiée
  dans le noir comme pour un inconnu vu ; corrigé en route, une part de bois va au feu de la salle d'où vient
  la demande, joueur compris (`echanges.foyer_de`). **Répliques d'une voix inconnue**
  (`narration.voix_inconnues`, `voix.connait_nom`) : le moteur sait qui parle ; la réplique nomme qui son
  locuteur connaît (Corvus seulement s'il lui a donné son nom ou qu'il en a entendu parler), jamais
  elle-même au-delà de ce qui est établi, et ne se dit personne (« je suis… »). **Côté joueur** : voir parler
  quelqu'un fait connaître sa voix (la réponse d'un PNJ à un autre retentit de sa propre voix,
  `social.faire_entendre` ; « Qui va là ? » et « C'est … » chacun de sa voix ; une réplique du MJ d'un
  personnage vu) ; une voix nommée par une autre qui s'adresse à elle dans le même échange est « une voix
  qu'on appelle Gorm » (`ecoute.lier`, `voix.nommer`, ouï-dire), une voix qui dit son nom se dit ainsi ; les
  mots cités d'une parole nette s'entendent tels quels ; juste après un appel de Corvus par son nom, « je
  réponds », « « Ici ! » »… sont le geste de réponse commun (`emettre_son` méthode `repondre`,
  `pnj.repondre_a`), sans le MJ, et l'appelant le croit là. Bancs 8 h contre `main` 888bbc4 (Relais 4 graines
  `--joueur chambre_cloche`, auberge `--joueur dortoir`) : aucune usurpation ni violation, échanges, appels
  et réponses identiques ; trois nuits du Relais et deux de l'auberge identiques, les autres divergent sur
  une réponse qui retentit (auberge : bruits inconnus 117 → 115,75, allés voir 29,75 → 30,5). Luna (copies de
  scènes) : « Qui es-tu ? » à une voix fait nommer Gorm par le moteur, aucun refus du contrôle, Luna ne nomme
  pas de tiers (elle ne sait pas qui la voix connaît) ; « je réponds » 0 appel ; une réponse libre (« je lui
  crie que je suis là ») reste au MJ, qui a fait un cri sans mots ou échoué. Limites : aucun scénario ne fait
  chercher le joueur (cas réel placé d'autorité) ; le nom de Corvus vu se nommer n'est pas retenu ; le MJ
  ignore ce que sait une voix et son genre.
- Branche `audits-attendu`, non fusionnée (`docs/contrat-mj.md`, « Ce que le MJ reçoit d'un refus
  d'audit ») : les refus d'audit suivent le contrat des refus du moteur. Chaque refus du contrôle
  narratif (texte vide, voix d'auteur, nom sans fondement, parole racontée ou citation nouvelle sans
  moteur, voix inconnue, verdicts de l'auditeur), de la portée des ajouts, des capacités et de la
  contre-revue d'action porte un `attendu` (`refus.audit`, `refus.attendu_audit`) : la partie et le
  segment (ou le champ de l'ajout, `proposition.ajouts[0].texte`), la phrase, le nom ou la citation
  reçus tels qu'écrits (`narration.tel_quel`), le verdict et le motif de l'auditeur donnés pour ce
  qu'ils sont, et ce qui serait accepté en identifiants ou citations exactes (destinataires,
  présents, engagements prévus mot pour mot, `parole_prevue.personnage`, clés `objet:<id>` qui
  nomment ce que vise une affirmation sans source, plan reçu de la contre-revue) ; une cause par
  refus (un mot, un nom, une parole racontée, une citation chacun : avant, un refus pour tous). Un
  rapport illisible (`refus.RapportIllisible`, dont `AuditIllisible` et `RapportInvalide`) ne
  reproche rien au texte et le dit ; une proposition mal formée relevée pendant un audit garde
  l'`attendu` du moteur (`refus.depuis_refus`). Le nom d'une entité cachée n'est jamais accompagné de
  son identifiant. `INSTRUCTIONS_REVISION` dit à Luna de suivre `attendu`. Le joueur ne lit jamais
  `attendu` (texte refusé jamais affiché ; repli inchangé). `banc_multi` compte aussi les relances
  narratives et les refus ; `rapport_fil` montre `attendu`. Cas réels et un autre de même nature,
  chaînes complètes après rechargement (`tests/test_audits_attendu.py`) : Ilse et « Pas
  maintenant », « Je vais me pousser », « les faits ne disent… », la voix qui se disait Brune,
  « Prise non demandée » ; invention refusée trois fois (repli), audit illisible, contre-revue non
  conforme puis corrigée. Luna, bancs `main` 4c53791 puis la branche, l'un après l'autre, 2 passes
  chacun, relais + crypte + atelier + échanges (38 tours MJ) : 3,08 → 3,07 appels et 11,3 → 11,5 s
  par tour MJ, 0 repli des deux côtés, relances narratives 4,0 → 3,0 (étendue 2 à 4), tours avec
  refus 6,5 → 7,0, refus du moteur et de la contre-revue 10 → 10,5. Des deux côtés, chaque réponse
  refusée a été corrigée dès la première relance : le banc ne peut pas montrer de gain sur la
  correction, et le nombre de relances dépend surtout des premières réponses, qu'`attendu` ne
  touche pas ; l'écart est dans le bruit. Limites : le verdict de l'auditeur reste sémantique (un
  refus juste ou non reste le sien, cité tel quel) ; les clés proposées pour une affirmation sans
  source sont une indication par le premier mot du nom ; le récit d'une parole de Corvus est cité en
  mots retrouvés dans le texte, sinon sous forme normalisée ; les refus du moteur hors audit sans
  `attendu` (« Réexamine l'intention entière… ») restent tels quels.
- Branche `pnj-lumiere-garde`, non fusionnée (`docs/plan-planificateur.md`, « Lumière et garde ») :
  quatre limites des branches précédentes, diagnostiquées sur les bancs et des copies de leurs états.
  **Lumière dans le noir** : quand le but emploie lui-même un objet (ce qu'il vise, une source ou une
  flamme pour la lumière), on cherche et appelle son porteur perdu de vue, comme pour une part ; et
  l'on **demande du feu** (`demander_feu`, `echanges.demander_feu`) : on tend sa source à qui porte
  une flamme, qui l'y allume sans rien prêter, sauf méfiance (Rémy, le camp éteint, appelle Gaspard
  et allume une lampe de rechange à son briquet ; Joss à l'auberge, au briquet d'Odile). Mine de 11 h :
  appels à l'aide 192 → 96, minutes dans le noir 812 → 696 par nuit. **Lumière devant une serrure** :
  une source qu'il sait allumée ou posée près de l'objet depuis compte de loin (`apport_cru`, la
  croyance `lumiere` retient les sources `allumees`) ; la lueur diffuse par case, le moteur ne la
  connaît que par salle (limite du modèle). **L'échange compte l'éloignement** : Gorm achetait les
  planches d'Aubin parce que le plan d'échange s'arrêtait à l'achat, sans compter l'attente près du
  brasero, loin de ses biens (même sans `GARDE`, 5,66 contre 7) ; une part promise s'attend là où elle
  se sert, ce temps compte avec ce qu'il laisse monter (`Vue.attente_part`), et ne s'explore que si
  elle atteint le but ; Gorm prend ses fagots (Relais 7, 42, 2024). **Un gardien ne laisse pas son
  bien à qui le menace** (`deliberation.menaces`) : un bien dont il a la charge, avec quelqu'un dont il
  se méfie, coûte `GARDE` à tout plan qui s'en éloigne, l'abri n'y gagne pas de quitter cette personne,
  et il appelle à l'aide si sa crainte l'emporte sur son courage (Bram reste, Josse accourt). Cas réels
  et cas de même nature après rechargement (`tests/test_lumiere_garde.py`), `VERIFIER` sur une nuit de
  chaque scénario. Bancs 8 h contre `main` 888bbc4 (lancés ensemble ; mesure `minutes_dans_le_noir`
  ajoutée des deux côtés) : sans recours Relais 53 → 54, mine 59 → 55, auberge 15 → 44 (appels à
  l'aide de Lucien et d'Anselme près de leurs biens menacés, d'où des témoins et des renoncements),
  crue 15 → 15 ; en attente 63 → 66, 290 → 281, 536 → 541, 89 → 108 ; vols vus égaux à 0,25 près ;
  aucune usurpation ni violation ; temps égal à ±14 %. Tests changés : `test_planification` (le plan
  d'une part mène l'attendre près des vivres), `test_constater_rumeurs` (lampe de Josse vide pour
  garder le baraquement noir ; Odon honnête dans la réserve noire, scène partagée avec
  `test_voix_inconnues`, car attendre sa part dans le noir lui coûte un peu plus que forcer le garde-manger). Limites : chercher le porteur
  seulement pour la lumière et ce que le but vise (pas pour un feu : sinon la borne de nœuds) ; pas de
  feu demandé pour une source fixe ; rejoindre qui porte une lampe n'est ni abri ni lumière ; l'apport
  d'une source ignore l'ombre ; l'attente d'une part reste une estimation ; la menace se juge sur où il
  croit les autres.
- Branche `planif-cout`, non fusionnée (`docs/plan-planificateur.md`, « Coût de calcul ») : le temps
  d'une nuit, sans rien changer à ce que décident les PNJ. Points chauds : des recherches refaites à
  chaque minute alors que seul le prix d'une faute ou d'abîmer avait changé avec la détresse (Lucien à
  l'auberge, Odon et Rémy à la mine), la vue du planificateur construite ~10 000 fois par nuit, la
  perception de tous qui relisait l'empreinte de l'état pour chaque PNJ, un trajet qui relisait tous
  les objets à chaque case. **Graphe repris** (`planification._GRAPHES`) : chaque état développé garde
  ses gestes avec les termes de leur coût ; quand seuls ces deux prix ont changé, la recherche se refait
  sur lui, mêmes additions et mêmes égalités, sans recalculer un geste (gardé à la deuxième recherche
  de suite sur les mêmes entrées). Lectures moins chères : la vue (gardes confiées lues une fois par
  propriétaire, aucune vue sans pièces crues ni créance), les gestes (un parcours des salles par départ,
  `pnj.parcours` ; un objet d'une autre salle n'offre qu'une part, `_parts` ; l'état d'un plan comparé
  comme un tuple), la perception de tous dans un seul `etat_fige`, les obstacles d'une salle une fois
  par trajet, le pas sans exception, `monde.copie`. Nuits identiques à `main` 888bbc4 (chronique,
  mesures, état final complet, récit, empreintes, recherches et nœuds) sur 48 nuits (4 scénarios ×
  4 graines, départ tiré et fixe, deux passes tirées) ; `VERIFIER` et `spatial.VERIFICATION` sur 16
  nuits ; `tests/test_planif_cout.py` (Lucien, Odon : même monde avec ou sans graphe après
  rechargement). Temps au processeur, 8 processus, `main` → branche, départ tiré : Relais 14,5 →
  9,2 s, mine 57,3 → 31,7 s, auberge 62 → 26,4 s, crue 15,3 → 10,5 s ; le planificateur passe de 58 %
  à 36 % d'une nuit à l'auberge, de 59 % à 47 % à la mine. Accordée avec `main` 5861f71
  (`pnj-lumiere-garde` : la part promise passe dans `_parts`) : empreintes identiques sur 32 nuits
  (tiré et fixe), `VERIFIER` sur une nuit de chaque scénario ; départ tiré, 4 processus au plus :
  Relais 11,7 → 7,2 s, mine 70 → 39,5 s, auberge 47,3 → 24,2 s, crue 12,6 → 9 s. Limites : une recherche neuve coûte
  toujours ~100 µs par état (mine graine 7 : Josse, deux recherches de 4 000 nœuds par minute en fin de
  nuit) ; une croyance nouvelle refait tout ; pic de mémoire 30 → 59 Mo (mine, graine 7) ; la
  perception reste un tiers d'une nuit.
- La suite de tests passe : 1092 tests (14 sautés sans `jsonschema`, facultatif pour MiMo), sans clé ni connexion (ceux du clic demandent Node).

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
  `lumiere-besoin`) ; prêter, permissions déléguées et l'argent (branche `echanges-argent`) ; un
  besoin que rien n'apaise (le devoir reste urgent une fois franchi son seuil ; il attend désormais
  sans compter comme « sans recours », branche `besoins`). Demander du bois pour un feu et le protégé
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
