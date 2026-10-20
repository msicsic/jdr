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
- Branche `ouie` (`docs/plan-ouie.md`, `donjon/ouie.py`), non fusionnée : une règle d'ouïe commune
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
- La suite de tests passe : (à recompter), sans clé ni connexion.

## Décisions en attente

- **Fabrication générale** (`docs/plan-fabrication.md`) : étapes 1 à 3 fusionnées ; l'étape 4
  (d'autres usages : passerelle, cale…) attend un accord. Limite : les planches du Relais ne
  suffisent pas à une échelle (deux pièces, à Aubin) ; l'assemblage de planches est vérifié en
  test sur l'atelier, pas en partie au Relais.
- **PNJ d'abord, joueur passif** : la crue du Relais comme scénario d'étude (`docs/plan-crue.md`,
  étape 3, le niveau d'eau, faite ; suite : influence et relations) ;
  caractères, valeurs, relations, lire les autres, contrainte et groupes (`docs/plan-social.md`).
  Faits : temps fin et orientation, jeu dans le navigateur, caractères et valeurs (sans
  l'empathie), niveau d'eau. **L'ouïe** est faite sur la branche `ouie` (`docs/plan-ouie.md`), à
  relire avant fusion ; réglages à trancher : l'échelle, le crochetage en geste bruyant,
  l'inquiétude d'un bruit inconnu, le courage qui fait aller voir ; à fondre ensuite : les réflexes
  déclarés et le souvenir « son » dans l'ouïe commune.
- **Manques relevés par la mine et l'auberge** : avoir de la lumière comme but ; demander du bois
  pour entretenir un feu ; chercher quelqu'un dans le noir ; le lieu dans une rumeur ; prêter et
  permissions déléguées ; l'argent ; un protégé nourri en boucle ; `pnj._rate` croit disparu un
  objet caché dans un contenant fermé.
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
