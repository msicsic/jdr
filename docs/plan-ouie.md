# Plan : l'ouïe commune au joueur et aux PNJ

Chantier accepté après les caractères et valeurs (`docs/etat-dev.md`). Branche `ouie`.

## Point de départ

- `pnj.alerter` faisait se retourner tout PNJ de la même salle, à 6 cases au plus (1 pour un pas
  feutré), qui ne voyait pas l'auteur : sans nature du bruit, sans interprétation, sans autre
  salle. Seuls un pas ou un geste illicite d'un PNJ, et le pas du joueur, le déclenchaient.
- `ecoute.py` faisait entendre au joueur les bruits des PNJ, sur une autre échelle (pas et gestes
  1, voix 2, appel 3 ; une ouverture coûte 1, une porte 2), sans distance dans la salle.
- `esprits.entendre` (appels, cris, sons d'objets) inquiétait de 15 qui l'entendait d'une autre
  salle au niveau 2, et déclenchait les réflexes déclarés.

## Règle retenue (`donjon/ouie.py`)

**Tout geste fait un bruit.** Chaque geste a une nature, déclarée une fois (`ouie.NATURES` ; un
geste absent de la table est ordinaire), chaque nature une intensité en crans :

| nature | crans | gestes |
|---|---|---|
| feutré | 1 | pas feutré, toucher ; tout pas ou geste ordinaire fait en douce (joueur `discret`, PNJ `sans_temoin`) |
| pas | 3 | aller, marcher, pas chassé |
| geste ordinaire | 3 | prendre, poser, ouvrir, fermer, manger, servir, alimenter, allumer… |
| voix | 4 | parler, dire, demander, confier, acheter, siffler |
| bruyant | 7 | crocheter manqué (réussi : un geste ordinaire, `nature_crochetage`), forcer, frapper, couper, découper, sauter, franchir un obstacle ; tout geste du joueur que l'arbitrage dit fracassant (bruit 3) |
| appel | 9 | appel à l'aide, cri |

Sans bruit : attendre, patienter, se tourner, observer, examiner, lire, écouter, parcourir des
yeux, se reposer, se chauffer, s'abriter. Le moteur fait retentir le geste là où il l'accomplit
(`ouie.retentir`) : pour un PNJ, la marche (`_avancer_de`, `_pas`), les portes en chemin
(`_annoncer_porte`), tout geste sur un objet, réussi ou non (`_executer`), la parole avec ses mots
(`social.faire_entendre`), l'appel (`ecoute.appel`) ; pour le joueur, chaque étape de son action
(`Moteur._terminer_etape`) et sa parole (`paroles.preparer_parole`).

**La distance atténue.** Dans une salle, un cran par palier de distance dépassé (1, 3, 6, 12, 24
cases : un cran par distance doublée). D'une salle à l'autre, le bruit gagne le seuil (la distance
compte), passe (ouverture 1 cran, porte fermée 3, appui vertical 1), puis repart du seuil d'en face ;
le chemin le plus fort l'emporte, et il s'éteint sous −2. Il en découle : un pas s'entend à 6 cases
(comme avant), un pas feutré à la case voisine (comme avant), une voix à 12 cases, un fracas dans la
salle voisine, un appel à une ou deux salles.

**Seuil.** Ce qui parvient au niveau 1 s'entend sans y prêter l'oreille. Un PNJ aux aguets (une
ronde, une garde, aller voir, accourir) entend un cran plus bas, au repos un cran plus haut ; la PER
modulée ajoute un cran par quatre points au-dessus de 10 (Ilse, PER 14, entend mieux). Le joueur :
un cran plus bas en écoutant, encore un collé à la porte par où le bruit arrive ; sa PER aussi.

**Interprétation (PNJ), selon ce qu'il croit.** Ce qu'il voit faire n'a pas besoin de l'ouïe.
- **Connu** : un bruit ordinaire (feutré, pas, geste, voix) venu de là où il croit quelqu'un depuis
  moins de 30 minutes (dans sa salle : à une case de là où il le croit, s'il le sait ; ailleurs :
  dans cette salle). Il le lui attribue et le croit là où vient le bruit (source `entendu`), sans se
  retourner.
- **Inconnu ou inhabituel** (bruyant, appel) : tout près (même salle, 6 cases) et hors de son
  regard, il se tourne vers le bruit ; la rotation retarde la fin de son geste ; ce qu'il voit
  devient croyance, et l'auteur d'un geste illicite en cours en fait un témoin (registre
  `gestes_en_cours`). Plus loin, ou s'il ne voit rien (le noir), il retient « un bruit vers tel
  lieu » (un souvenir par lieu, le plus fort tant qu'il ne l'a pas vu), qui l'inquiète une fois à
  la mesure de ce qu'il en entend (15 × niveau reçu / 9 : un appel proche, pleinement ; des pas
  lointains, à peine) ; chaque appel à l'aide l'inquiète de nouveau.
- **Méfiance** : le bruit ordinaire de qui il croit là et dont il se méfie se surveille : de près,
  il se retourne comme pour un inconnu ; de loin, il le lui attribue.
- **Aller voir** un autre lieu est un but du planificateur (`planification.voir` : y aller et le
  parcourir des yeux ; but `{"type": "voir", "lieu"}`), après ce qui presse et avant la routine
  (`deliberation.bruit_a_voir`). Son **devoir de garde** l'y envoie (une pulsion du devoir ou des
  biens concerne ce lieu, ou un protégé y est, à ce qu'il croit) ; pour un fracas ou un appel, son
  **courage** aussi, s'il dépasse la moyenne (50). Il poursuit le bruit qu'il est allé voir ; qui
  vient de parcourir un lieu n'y retourne pas pour un bruit ordinaire avant 15 minutes. Le bruit est
  expliqué quand il voit quelqu'un là, ou quand il a parcouru le lieu des yeux, ce qui le rassure
  comme une ronde ; oublié après 30 minutes sans nouveau bruit. Le bruit de sa propre salle se situe
  à une case et s'examine de même (branche `ouie-temoins`, plus bas).

**Le joueur entend par le même calcul.** Ce qui lui parvient d'un geste qu'il ne voit pas faire est
rangé dans `data["bruits"]` (auteur, nature, niveau reçu, d'où il arrive : une sortie, « tout
près », « dans la pièce ») ; un même bruit sans paroles, au même niveau, ne s'y range qu'une fois.
`ecoute` en garde le rendu : « Tu entends un appel à l'aide / un grand bruit / une voix / des pas /
des bruits / un léger bruit… » par direction, et une parole en clair seulement si elle lui parvient
nettement (au seuil commun) et ne nomme que ce qu'il connaît. Il choisit lui-même de se retourner.
Quand un PNJ qu'il voit se tourne vers son bruit, il le lit (« Ilse, meunière évacuée, se retourne
vers toi. »). Les bruits rangés par une ancienne partie ne disaient pas ce qui en parvenait : ils
sont effacés au chargement.

**Sans état caché.** L'instant où chaque PNJ aura fini son geste est dans son esprit (`libre`) ; la
vie des PNJ le lit et l'écrit là, et se retourner le retarde. Le même laps découpé autrement donne
le même monde, rotation et témoignage compris (`test_ouie`, `test_temps_etat`).

## Correctif commun révélé

**Un geste social vers qui n'est pas là corrige la croyance** (`echanges.executer`, `pnj._rate`).
À l'auberge, Lucien, entendant du bruit dans le grenier noir, y croyait Hugues et lui demandait sa
lanterne pendant 90 minutes ; rien ne le détrompait, son inquiétude montait, il appelait à l'aide
et entraînait toute l'auberge. Personne ne lui répondant, il apprend désormais qu'Hugues n'y est
pas, comme pour tout geste manqué.

## Vérifié (`tests/test_ouie.py`, état après rechargement et ce que lit le joueur)

- Cas réel : Brune crochète la réserve à 3 cases dans le dos de Gorm, qui la sait là : il se
  retourne, la voit, en est témoin et se méfie d'elle. Le même laps d'un bloc ou en rotations du
  joueur rechargées en route donne le même monde.
- Cas réel : Brune marche dans le refuge où Gorm la sait : il ne se retourne pas, ne retient aucun
  bruit, et la croit là où elle s'est arrêtée (entendu).
- Le joueur entre à pas normaux derrière Ilse : elle se retourne, le croit au refuge, son geste est
  retardé ; il lit « Ilse, meunière évacuée, se retourne vers toi. » À pas feutrés, à quatre cases,
  elle n'entend rien.
- Un fracas dans une autre salle : Gorm, à l'échoppe, entend crocheter au refuge qu'il garde ; il
  s'inquiète, va voir (but `voir`, motif devoir), voit Brune à l'œuvre ; le bruit est expliqué.
- Ilse, peu courageuse (30), sans garde au refuge : elle retient le bruit, s'inquiète, n'y va pas.
  Aubin (60) dans la même scène y va (motif sécurité) et en est témoin.
- Mine : Odon passe dans le dos de Rémy, qui se méfie de lui : Rémy se retourne ; Josse, qui lui
  fait confiance, non.
- Le joueur, à l'échoppe, entend crocheter au refuge : « Tu entends un grand bruit… à l'est », sans
  que rien ne nomme Brune ; elle compte parmi ceux qu'il a entendus.
- Échelle, atténuation, porte fermée ou ouverte ; un geste social vers qui n'est pas là.
- Joué par `jeu.py --offline` puis rechargé : les deux premiers cas joueur rendent les mêmes lignes
  et le même état.

Tests d'avant l'ouïe dont la scène supposait qu'on n'entend rien : précisés en placement d'auteur
(qui croit qui où ; Gorm au repos dans l'ombre, ou aux vannes, hors de portée d'oreille) ; la
chronique de l'ouïe a sa nature (`ouie`) ; un crochetage sous les yeux d'Ilse vérifie le geste et
que Gorm, à l'échoppe, l'a entendu (il vient ensuite refermer la réserve).

## Bancs (8 h, avant → après ; graines 1985 7 42 2024, plus 3 11 99 500 au Relais)

| | Relais (8) | Mine (4) | Auberge (4) | Crue (4) |
|---|---|---|---|---|
| minutes urgentes sans recours | 438 → 432 | 680 → 604 | 584 → 584 | 362 → 295 |
| échanges | 7,4 → 7,8 | 26,8 → 38,5 | 24 → 22 | 8,5 → 8 |
| vols vus | 1 → 2,9 | 2 → 1,8 | 2,8 → 2,3 | 2 → 2,3 |
| confidences | 0,6 → 0,8 | 3 → 5,3 | 5,8 → 8,5 | 1,8 → 1 |
| méfiances | 1,5 → 1,5 | 4,5 → 5,3 | 8 → 6,5 | 2,8 → 2,3 |
| retournements au bruit | — → 125 | — → 239 | — → 227 | — → 173 |
| bruits inconnus retenus | — → 48 | — → 82 | — → 168 | — → 97 |
| allés voir | — → 7,6 | — → 29,5 | — → 85 | — → 28 |

Aucune usurpation, aucune violation (l'état est vérifié à chaque pas du banc). Au Relais, presque
trois fois plus de vols vus : le crochetage s'entend, Gorm vient voir. À l'auberge, deux fois plus
de jets : Lucien s'acharne plus souvent dans le noir sur le coffre d'Anselme ; les gardes (Odile,
Hugues) vont voir souvent. Temps : une nuit du Relais 5,5 → 5,8 s, quatre en parallèle 8,5 → 9,8 s.

Réglages essayés en route, à l'auberge (8 graines) : une inquiétude fixe pour tout bruit inconnu
(un tiers d'un fracas pour un pas) et un fracas qui inquiète de nouveau toutes les 5 minutes
faisaient basculer la nuit dans une panique générale (minutes sans recours 1 010, sécurité pressante
1 100 min contre 186) ; l'inquiétude à la mesure du niveau reçu et le correctif du geste social l'ont
ramenée au niveau d'avant.

## Paroles : à qui, et qui les entend (branche `parole`)

Avant : une parole du joueur avait un seul destinataire, nommé en tête ou choisi par Luna ; les
autres présents n'en retenaient rien, et une parole entre PNJ ne touchait que son destinataire.
On ne pouvait ni parler à un groupe ni chuchoter.

**Règle acceptée.** Le moteur fixe les contraintes de destinataire (`paroles.analyser`,
`paroles.destinataires`) : celui que le joueur nomme, le groupe ou la suite de l'échange.
Sans adresse ni suite, `audience_libre` laisse Luna distinguer l'assistance de la parole
individuelle ; pour cette dernière, le défaut reste celui d'en face (dans son regard, le plus
proche à portée de voix) ; à égalité, le joueur précise. « à tous » s'adresse aux présents qui
saisiraient ses mots, chacun décidant comme d'une demande individuelle. Une saisie qui commence
par des guillemets vaut « je dis … », ou, quand un ou plusieurs interlocuteurs précédents
saisissent encore ses mots, « je lui/leur dis … » : elle poursuit l'échange avec eux (de même
« je lui dis », un seul, et « je leur dis », plusieurs). Chuchoter ou murmurer : un seul destinataire, au contact,
jamais un groupe ; le chuchotement est feutré (1) et ses mots ne vont qu'à lui.

**Qui l'entend.** La parole retentit avec ses mots (`ouie.retentir`, `parole` : destinataires et
contenu typé). Un PNJ en saisit les mots s'ils lui parviennent au seuil commun, et qu'il les
entend (`ouie.mots_saisis` : niveau ≥ max(1, son seuil) ; au repos il lui faut un cran de plus,
aux aguets il n'entend pas mieux les mots). Qui en saisit les mots sans en être le destinataire
la retient (`social.retenir_parole` : souvenir `parole`, chronique « X surprend les mots de Y à
Z ») et en reçoit le contenu par la règle du destinataire (`social.recevoir`) : affirmation jugée
comme une confidence (`echanges.affirmer`), nouvelle comme une rumeur (`_adopter`, d'une main de
plus), aveu cru (méfiance, rumeur de première main). Rien de ce qu'on dit de lui-même ne
l'atteint ; une demande adressée à un autre ne l'engage pas. Les PNJ entendent les paroles des
autres PNJ par la même règle : confidences (`social.bavarder`), affirmations (`echanges`, dire),
demandes, prières de passage.

Une parole sans conteste (guillemets, à tous, deux-points) que nul présent perçu ne saisirait est
dite à la cantonade (personnage « personne ») : aucun destinataire, qui l'entend la retient. Le MJ
ne peut ni la remplacer par une action ni la raconter lui-même en dialogue : le moteur la lui fait
proposer. Seuls les destinataires répondent (`narration.destinataires_parole`, contrôle
déterministe) ; Luna voit ce que chaque présent a entendu (`a_entendu`).

Correctif commun révélé (banc de la mine) : Mathe, qui venait de voir Odon manger le pain de
Lucien, entendait Rémy le dire et sa méfiance « vu » devenait un ouï-dire « dit:remy ». Une parole
qui confirme ce qu'on vient de voir ou d'essayer ne change plus la croyance (`echanges.affirmer`),
et une rumeur ou un aveu n'abaissent plus une méfiance de première main (`social._adopter`,
`recevoir`).

Vérifié (`tests/test_parole_commune.py`, après rechargement, et ce que lit le joueur) : le cas
réel devant Ilse et Aubin (Ilse en face répond, Aubin retient) ; deux à égalité (le joueur
précise, rien n'est dit) ; Luna qui choisit un autre destinataire (refusé, `attendu`) ; « à
tous : écartez-vous » (Ilse, méfiante, refuse ; Aubin décide pour lui) ; « à tous : il faut
monter » (retenu, personne engagé) ; derrière le pilier, à la cantonade ; « « Gorm, je te donne
la cloche » » (le don proposé par Luna est refusé, la cloche reste au joueur) ; chuchoter à Brune
au contact (Ilse à trois cases ne retient ni les mots ni l'affirmation), à distance et à tous
(refusés) ; un aveu devant Aubin, qui le confie ensuite à Gorm ; une confidence entre PNJ surprise
par Ilse, qui l'adopte de seconde main.

Avec Luna, sur des copies de la sauvegarde réelle (placements d'auteur sur la copie) : à la
cantonade derrière le pilier, Brune, Ilse et Aubin retiennent « pouvez-vous m'aider à faire bouger
Brune ? » ; en face d'Ilse, elle répond, Aubin et Brune retiennent ; l'aveu « c'est moi qui ai
forcé la réserve de vivres » rend les trois méfiants, rumeur de première main ; « « Gorm, je te
donne la cloche » » reste une parole (la cloche reste portée) ; chuchoter à Ilse au contact :
Aubin, à deux cases, ne retient rien ; « à tous : écartez-vous » : Aubin, Ilse et Gorm décident
chacun et s'écartent ; égalité Ilse/Gorm et chuchoter à tous : message du moteur, sans réponse
inventée.

Bancs (8 h, graines 1985 7 42 2024, avant → après) :

| | Relais | Mine | Auberge |
|---|---|---|---|
| paroles surprises | — → 9,75 | — → 62,25 | — → 32,75 |
| confidences | 1,25 → 1,25 | 5,25 → 3,75 | 8,5 → 4,75 |
| rumeurs crues | 1 → 1 | 2,75 → 2,75 | 4 → 4,25 |
| méfiances | 2,25 → 2,25 | 5,25 → 5,25 | 6,5 → 7,75 |
| jets | 8,25 → 8,25 | 11,5 → 12,25 | 161 → 196 |
| minutes sans recours | 394 → 394 | 604 → 678 | 584 → 663 |
| retournements | 129,5 → 129,5 | 239 → 231 | 227 → 188 |

Aucune usurpation. Au Relais, rien ne change hors des paroles surprises (des demandes de part, qui
n'engagent pas le témoin). Ailleurs, les témoins apprennent directement : moins de confidences à
faire, une rumeur qui court plus tôt (auberge : Hugues accuse Lucien à 200 minutes au lieu de
262). Les écarts de minutes sans recours viennent de jets décalés : à la mine, graine 2024, une
part refusée à Gaspard à 221 minutes au lieu d'être promise le laisse affamé (+300 minutes) ; à
l'auberge, graine 7, une nuit de panique (453 retournements) n'a plus lieu (213).

**Correctif : ce qui est une parole sans conteste (branche `repli-et-appel`).** Vu sur `main` :
« Aubin, viens m'aider à porter l'échelle », Aubin derrière le pilier, finissait en dix appels sur
un refus, et « Ilse, tu peux m'aider à déplacer les planches ? » sur un dialogue où Luna racontait
« Tu appelles Ilse et lui demandes… » sans que rien ne soit dit. Règle retenue par l'utilisateur :
une saisie est une parole sans conteste (`paroles.analyser`, `explicite`) seulement si elle
commence par des guillemets, par un verbe de parole (« je dis… », « je dis à Brune… », « je lui
dis… », « je demande à Gorm… », « je chuchote… » ; « lance », qui dit aussi un geste, demande un
destinataire ou un deux-points : `GESTES_HOMONYMES`) ou par « à tous ». Celle-là n'est ni un
dialogue du MJ ni un geste : si le moteur ne peut pas la faire entendre, il le dit sans appel
(« Tu ne vois pas Aubin d'ici : approche-toi pour lui parler », la cantonade proposée) ; si le MJ
s'obstine à la raconter ou à en faire un geste, le moteur prononce les mots du joueur tels quels,
sans contenu typé (`mj.parole_du_moteur`) ; sans mots imposés (« je demande à Ilse de m'aider »),
il demande au joueur de les donner plutôt que de les inventer. Une interpellation sans guillemets
(« Brune, pousse-toi », « Aubin, viens m'aider… ») reste du texte libre : Luna en fait une
question, un geste ou une parole ; si elle en fait une parole, le moteur en fixe le destinataire
(celui qu'elle nomme) et en garde les mots. Avec Luna (copies de la sauvegarde réelle) : en face
d'Aubin, « Aubin, viens m'aider à porter l'échelle » devient une parole (3 appels) ; derrière le
pilier, Luna répond qu'elle ne le voit pas (2 appels), et « je dis à Aubin : viens m'aider » reçoit
le message du moteur sans appel. Une demande d'aide n'a pas de contenu typé : elle reste un propos.

**Correctif : ce que le MJ ne raconte plus sans le moteur (branche `mj-restes`).** Trois restes des
bancs Luna, une même cause : une affirmation mécanique (une parole dite, un détail, une faisabilité)
qui ne passait que par le jugement sémantique de l'auditeur, ou par lui avant le moteur.
- *Une parole n'a lieu que par le moteur.* Sans parole de Corvus validée dans le tour
  (`conversation_validee`) ni geste résolu (`resultat_resolu`), le récit ne fait pas parler Corvus
  (`narration.parole_racontee` : « tu demandes à Ilse… », « tu lui dis », « tu appelles Aubin »,
  « dis-tu » ; une hypothèse, « si tu lui demandes », ou un conseil, « tu peux lui demander », n'en
  sont pas) ; et quand la saisie s'adresse à quelqu'un sans que le moteur ait fait entendre de parole,
  ou après un refus, aucune citation nouvelle (`narration.paroles_sans_moteur`). Contrôle
  déterministe, de toutes les voies. Une interpellation libre (« Gorm, je te donne la cloche ») dont
  le destinataire entendrait la parole, répondue en dialogue, est renvoyée une fois au MJ sans être
  contrôlée (`mj.renvoi`) : « rien n'a encore été dit », avec ce qu'attend le moteur (parole_joueur,
  l'action, ou un dialogue sans réponse de personne). Un dialogue qui revient est contrôlé comme tout
  autre : la règle de l'utilisateur tient (sans guillemets, verbe de parole ni « à tous », pas de
  parole sans conteste). Essayée puis retirée : une règle de l'auditeur « sans conversation_validee,
  personne ne réagit » ; l'auditeur la croyait violée alors que conversation_validee était là (deux
  refus à tort sur « « Gorm, je te donne la cloche » »).
- *De loin, aucun détail.* La règle du moteur existait (un détail ou une description physique ne
  s'établit que sur un support à portée et éclairé, `faits_locaux.supports`, refus d'une seule cause
  avec `attendu`), mais la contre-revue sémantique de l'ajout passait avant elle : trois refus de
  l'auditeur sur « à quoi ressemble le mur de l'atelier ? » (mur à trois cases), puis un repli, ou un
  détail ancré sur un autre support. Désormais le moteur valide d'abord (`mj.refus_assure` : un ajout
  persistant que sa validation écarte, ou un dialogue qu'il remplacera, n'est pas audité). Les faits
  disent ce que le moteur applique : « … trop loin pour être manipulé d'ici ; de là, ses détails
  t'échappent » (`rendu.decrire`, `localisation.REGLES`) ; les consignes ne promettent plus la
  description d'un objet seulement vu, mais d'un objet à portée. Un personnage n'est pas concerné :
  ses traits se décrivent de souvenir (« souvenir d'une rencontre ») ; la phrase des détails qui
  échappent, essayée aussi pour lui, faisait refuser « les yeux de Gorm sont bruns » à deux cases.
- *« Puis-je… ? » : le moteur répond.* Une question sur un geste de Corvus (`commandes.faisabilite`)
  répondue en dialogue est renvoyée une fois pour que le geste soit proposé ; si le moteur le refuse
  (après une correction, ou tout de suite pour la distance), le joueur lit sa raison telle quelle, pas
  une explication libre (« en principe, les perches pourraient servir »). Un rôle laissé vide dit ce
  qui manque et s'il y a ici de quoi le tenir : « Pour une échelle, il te manque un lien pour attacher
  les barreaux : rien de tel n'est à ta disposition ici. » (`artisanat.calculer`, au lieu de « on ne
  peut pas compter deux fois une perche »), « Il te faut un appui long à tenir, une perche par
  exemple : rien de tel n'est à ta disposition ici. » (`franchissement.conditions`). Ce qui est à
  disposition, c'est ce que Corvus peut désigner (`Monde.designable`, ce qu'il verrait en se
  tournant compris) : la ficelle de l'atelier, dans son dos, n'est plus dite absente.
- *Guillemets.* « « Gorm, je te donne la cloche » » reste une parole, voulue : le joueur lit « Tu dis à
  Gorm : « … » », la cloche reste dans la besace, et Gorm répond sans la prendre (avec Luna : « Je t'ai
  entendu. Mais la cloche est encore à toi : il faut me la remettre clairement »).

Luna, copies de la sauvegarde réelle et de l'atelier (avant → après) : « est-ce que je peux fabriquer
une échelle ? » au refuge, une explication devinée (« possible en principe… ») → le refus du moteur
(il manque un lien) ; devant les perches trop loin, « Oui, une échelle est une possibilité, mais… » →
« Approche-toi de la perche de bois 1… » en un appel ; « à quoi ressemble le mur ? », trois refus de la
contre-revue et 30 s → refus du moteur, puis la réponse par ce que Corvus voit (2 appels et un audit) ;
« Gorm, je te donne la cloche », « Gorm acquiesce : la cloche est bien revenue » sans rien changer →
la cloche remise (remettre). Limites : repérer un récit de parole est lexical (formes à la deuxième
personne), une réaction sans citation ni verbe de parole (« Gorm acquiesce ») n'est arrêtée que par le
renvoi, pas par un contrôle ; la faisabilité ne se juge pas à distance (le joueur lit « approche-toi »,
pas la fiche du geste) ; la question de faisabilité est reconnue par ses formes (« puis-je »,
« est-ce que je peux », « est-il possible de »…).

## Constater, raconter où, chercher quelqu'un (branche `constater-et-rumeurs`)

Trois manques relevés en écrivant la mine et l'auberge (`docs/etat-dev.md`).

**On constate ce que la main rencontre** (`pnj._hors_d_atteinte`). Avant, tout geste manqué sur un
objet hors d'atteinte le faisait croire disparu (`pnj._rate`). Désormais, si l'objet est cru dans
un contenant (ou plus loin dans ce qu'il croit le contenir) qui est fermé et à portée de main,
c'est ce contenant que sa main rencontre : il le croit fermé, et verrouillé ou non, par l'essai ;
l'objet reste cru dedans (rien ne lui montre qu'il n'y est plus). Sinon, l'objet n'est pas là où il
le croyait, comme avant. Cas réel (Relais) : Brune croit la réserve ouverte, Gorm l'a refermée à
clé ; dans la pénombre, elle apprend la serrure, va chercher ses crochets et force la réserve, au
lieu de croire les vivres disparues et de rester sans plan. Même nature (auberge) : Lucien, dans
la chambre au poêle éteint, trouve le coffre d'Anselme fermé à clé et s'y acharne. Ouvert et vide :
l'absence, comme avant.

**Le témoin d'un geste qui déplace un objet voit où il va** (`pnj._lieu_vu`, gestes `prendre` et
`poser`, déclarés une fois : `pnj.DEPLACEMENTS`). Son souvenir `vu_agir` porte le lieu, comme une
croyance (valeur, salle, case vue, minute) ; il le croit là (`vu`) ; pris, il le sait dans les
mains de l'auteur. La nouvelle le dit (« Lucien a posé le ballot de soie dans l'étable ») ; qui la
croit en tire une croyance de lieu à la confiance du ouï-dire (`social._apprendre_lieu`), sauf s'il
a lui-même vu, essayé ou entendu l'objet après le geste rapporté ; ne pas l'avoir trouvé là où il
l'attendait n'y fait pas obstacle (et ne dément plus qu'il soit ailleurs : `paroles.dementi`). Qui
a appris depuis l'objet ailleurs dit le geste sans le lieu ; deux témoins du même geste racontent
le même fait (`social._fait`). Le protecteur qui va prévenir la victime d'un geste vu lui dit aussi
où il croit ses biens que l'auteur a déplacés (`deliberation._lieux_a_dire`, une affirmation
`lieu`). La victime les reprend par ses pulsions (un bien à sa place). Cas réel (auberge, graine
42) : Hugues voit Lucien poser le ballot à l'étable, prévient Anselme et lui dit où il est ; Anselme
va le reprendre et le repose dans sa chambre. Même nature (Relais) : Ilse voit Brune poser les
vivres de Gorm dans la conduite basse et le lui glisse aux vannes ; Gorm les rapporte au refuge.

**Chercher quelqu'un, c'est aussi l'appeler** (`pnj.appeler`). Chercher quelqu'un qu'on a perdu de
vue (`planification._chercher` : une part à demander, prévenir un protégé) parcourt une salle des
yeux ; s'il ne l'y voit pas, il l'appelle par son nom (une voix, `ouie`). Qui s'entend appeler (il
en saisit les mots, `ouie.saisit`) répond de la voix, sauf s'il reconnaît l'appelant et se méfie de
lui ; l'appelant qui saisit la réponse et connaît cette voix le croit là d'où elle vient (la
reconnaissance commune, ci-dessous). Le joueur entend l'appel et la réponse par `ecoute` ; appelé,
il répond s'il le veut. Cas réel (auberge, graine 7) : Mireille tournait 70 minutes dans l'auberge
sans voir Odile ; au grenier noir, elle l'appelle, Odile répond, Mireille lui demande sa part sans
la voir et l'obtient. Même nature : Hugues cherche Anselme au dortoir noir pour le prévenir,
l'appelle, et le prévient de vive voix. Odile, qui se méfie de Mireille, ne répond pas.

**Une recherche ne recommence pas sous l'effet du temps** (lot 37, branche
`codex-chercher-appeler`, non fusionnée). Un lieu inspecté sans retrouver la personne, ou appelé
sans réponse, reste écarté pour cette personne dans `esprits.recherches`. Un constat d'absence,
un changement de minute, un trajet rapide ou un rechargement ne l'effacent pas. Un nouvel indice
positif de lieu (`esprits.croire` : vue, voix, bruit attribué, nouvelle) rouvre ce lieu seul ; un
bruit inconnu nouveau (`ouie._bruit_inconnu`, ni déjà attendu ni couvert par un examen) y permet
une nouvelle recherche sans attribuer le bruit à quelqu'un. Une voix reconnue ne rouvre que
la recherche de cette personne. Cela vaut aussi quand le joueur est cherché. Le registre est
persistant ; les souvenirs d'appels ne servent à le reconstituer que pour les anciennes sauvegardes
qui n'en possèdent pas. Le planificateur lit les lieux écartés par son contrat existant
`deliberation.appels_vains`, déjà dans ses clés de reprise ; aucun changement de son graphe.

**Se parler, c'est s'entendre et savoir qui parle** (accepté : deux PNJ peuvent se parler dans le
noir, mais pas par un raccourci de distance ni d'après la place réelle de l'autre).
- *S'entendre* (`ouie.saisit`, `ouie.s_entendent`) : chacun saisit les mots de l'autre par
  l'atténuation commune (distance réelle, ouverture, porte fermée), au seuil des mots (un PNJ par
  `mots_saisis`, le joueur au seuil d'une parole nette). On se parle par une porte ouverte, à
  travers une porte fermée collé contre, pas à l'autre bout d'une grande salle (plus de 12 cases).
  `pnj.de_pres` (même salle, 6 cases) n'en décide plus.
- *Reconnaître une voix* (`ouie.entendre`) : chacun connaît ceux qu'il a vus ou entendus parler
  (`esprits.connait` ; `voix` dans l'esprit d'un PNJ, `data["voix_connues"]` pour le joueur ; on
  connaît qui l'on voit, `esprits.percevoir` et `pnj._observer_presences`). Qui saisit les mots
  d'une voix connue reconnaît qui parle et le croit là d'où elle vient (`entendu`, sa case s'il est
  dans la même salle). Une voix jamais entendue est une voix inconnue : un bruit inconnu, prêté à
  personne. Migration : un PNJ connaît ceux dont il sait quelque chose de première main ou de
  savoir (pas d'un ouï-dire) ; le joueur, ceux dont il garde le portrait ou a appris le nom.
- *On ne parle qu'à qui l'on a identifié* (`pnj.identifie`, `pnj.se_parler`,
  `pnj.pourraient_se_parler`) : celui qui parle s'adresse à qui il croit là (il le voit, ou l'a vu
  ou reconnu à la voix dans sa salle depuis peu : `pnj.croit_present`) ; l'autre sait qui lui parle
  s'il le voit ou reconnaît sa voix, et lui répond ; il faut que chacun s'entende. Sans se voir,
  chacun se tourne vers la voix de l'autre et le croit là. Le PNJ qui prie le joueur de le laisser
  passer (`passage._peut_prier`) suit la même règle.
- *Une seule règle* (accord avec la branche `integration`) : `pnj.peuvent_se_parler` décide de
  toute parole échangée — chacun saisit les mots de l'autre et sait qui lui parle (`identifie` :
  il le voit, reconnaît sa voix, ou le verrait en se tournant vers elle, ce que la lumière permet et
  le noir non). `se_parler` (demander, dire, confier, remettre), `pourraient_se_parler`
  (confidences, prière de passage, qui y ajoutent `croit_present`), servir une part
  (`echanges.servir`, `_servir_joueur` : on appelait qui était dans la salle sans le voir ni le
  reconnaître) et la parole du joueur (`paroles.destinataires` : le destinataire doit saisir ses
  mots, savoir qui lui parle, et Corvus saisir sa réponse ; refus distincts, « trop loin pour
  t'entendre », « ne saurait pas qui lui parle », « tu n'entendrais pas … te répondre »)
  l'emploient tous. Le test de la voix inconnue (Mathe, Odon) échouait après la fusion non par une
  voie détournée, mais parce que le poêle du baraquement, éteint par la scène, est désormais
  rallumé par Gaspard (branche `entretenir-feu`), dont la lampe éclairait Odon : la scène se tient
  maintenant dans la réserve noire.

Bancs contre `integration` (c45dd52, lumière comme besoin comprise ; 8 h, mêmes graines ;
`vols_vus` compte les vols distincts, `temoins_vols` leurs témoins) :

| | Relais (8) | Mine (4) | Auberge (4) | Crue (4) |
|---|---|---|---|---|
| minutes sans recours | 400,6 → 404,4 | 636 → 665 | 581 → 628 | 272,5 → 292,5 |
| appels / réponses | — → 4 / 1,6 | — → 7 / 0,8 | — → 17 / 2,3 | — → 9,8 / 4 |
| échanges hors appels | 9,1 → 9,1 | 28,3 → 34 | 21,8 → 21,5 | 8,5 → 11,3 |
| vols vus / témoins | 1 / 2,1 → 1 / 2 | 0,5 / 1 → 0,5 / 1 | 1 / 1,8 → 1 / 2,3 | 1,5 / 2,8 → 1,3 / 2 |
| rumeurs crues | 0,4 → 0,3 | 2 → 2 | 3,8 → 1 | 1 → 1,5 |
| paroles surprises | 12,8 → 10,6 | 88 → 110 | 39 → 37,8 | 11,3 → 15,3 |

Aucune usurpation ni violation ; `planification.VERIFIER` passe sur une nuit de la mine et une de
l'auberge. Les minutes sans recours montent par des recherches qui aboutissent plus tôt : Mireille
(auberge, graine 2024) appelle Joss et obtient sa réponse en 34 minutes au lieu d'en tourner 50,
puis attend sans rien entreprendre ; les nuits divergent ensuite (moins de rumeurs crues à
l'auberge, Lucien plus longtemps inactif). À l'auberge, Hugues appelle encore Anselme sans fin
quand celui-ci se tient derrière une porte fermée, dans une salle que sa recherche ne visite pas :
la recherche, inchangée, tourne parmi les salles qu'il peut atteindre, et l'appel ne passe pas la
porte fermée.
- *Le joueur* : `ecoute` ne rend en clair qu'une parole nette d'une voix qu'il connaît (et qui ne
  nomme que ce qu'il connaît) ; sinon « une voix ». Seules les voix reconnues le font savoir qui
  est là (`data["entendus"]`, `ecoute.retenir`) : un pas, un fracas, une voix inconnue ne nomment
  personne. Ses interlocuteurs (`dialogues.interlocuteurs`) : qui il voit, ou dont il vient de
  reconnaître la voix, si chacun saisit les mots de l'autre. Un échange entre PNJ dans sa salle
  qu'il ne voit pas ne s'écrit plus « X parle à voix basse avec Y » : il n'en a que ce que son
  ouïe lui en fait entendre (`social.faire_entendre`).
- Correctif révélé : qui a entendu dire où était un objet, puis le voit dans les mains de
  quelqu'un, ne tient plus le locuteur pour menteur (`esprits.reviser`) : l'objet a pu être
  déplacé depuis. À l'auberge, Mireille et Joss accusaient Hugues de mentir après avoir vu Anselme
  reprendre son ballot.
- Les salles se désignent avec leur article (`francais.lieu` ; `genre` déclaré dans les
  scénarios, noms de salle ajoutés à `FEMININS` pour les anciennes parties) : « dans l'étable »,
  « dans la conduite basse ».
- Autres usages de `pnj.de_pres` : `deliberation.autour` (se sentir accompagné ou menacé par ceux
  qu'on entend tout près, même dans son dos) le garde : ce n'est pas une parole, et ce module est
  repris par le chantier de la lumière ; il s'appuie encore sur la place réelle des autres.

Vérifié (`tests/test_constater_rumeurs.py`, état après rechargement et ce que lit le joueur) : les
cas ci-dessus ; le joueur lit en clair « Hugues dit à Anselme que le ballot de soie est dans
l'étable. » et « Ilse glisse à Gorm que Brune a posé les vivres du refuge dans la conduite
basse. », et entend au grenier « Mireille appelle : « Odile ? » » puis « Odile répond : « Ici ! » »
quand il les connaît, « des voix » sans aucun nom sinon (et Odile n'est pas son interlocutrice).
Par la porte du cellier : ouverte, Mireille et Odile se parlent à deux cases ; fermée, plus, sauf
collées contre ; Mireille croit Odile au cellier, à sa case. Cas réel (mine, graine 1985, 420
minutes) : au baraquement noir, Mathe reconnaît la voix d'Odon et lui refuse sa part ; Mathe qui
n'a jamais vu ni entendu Odon ne lui répond pas et ne le croit nulle part. Une partie d'avant les
voix est migrée.

Bancs (8 h, mêmes graines, avant → après ; `appels` et `reponses` sont de nouvelles mesures, et les
appels comptent parmi les échanges) :

| | Relais (8) | Mine (4) | Auberge (4) | Crue (4) |
|---|---|---|---|---|
| appels / réponses | — → 5,1 / 2,3 | — → 0 / 0 | — → 6 / 1,5 | — → 9,5 / 2,5 |
| échanges hors appels | 7,6 → 8,4 | 33,3 → 39 | 21,8 → 25,8 | 7,5 → 7,5 |
| minutes sans recours | 428 → 426 | 668 → 696 | 573 → 634 | 300 → 339 |
| rumeurs crues | 0,5 → 0,4 | 2,5 → 2,5 | 5,5 → 7,3 | 1 → 0,8 |
| vols vus | 8,1 → 9,3 | 0,5 → 0,5 | 2,8 → 2,5 | 7,5 → 8,3 |
| jets | 8,1 → 8,8 | 9,3 → 67 | 159 → 162 | 9,3 → 10,5 |

Aucune usurpation, aucune violation. Le geste manqué sur un contenant fermé ne se produisait dans
aucune nuit d'avant (il venait d'une partie jouée) ; après, une fois : crue, graine 7, Brune, qui a
mangé dans la réserve ouverte, la retrouve refermée, l'apprend verrouillée et s'y remet. Une variante sans la parole
dans le noir isole son effet : la mine retrouve exactement ses mesures d'avant, l'auberge 576
minutes sans recours ; la parole dans le noir fait donc la hausse de ces deux bancs. À la mine,
Odon, affamé, demandait sa part à Mathe dans le noir sans pouvoir lui parler et appelait à l'aide
une heure ; elle l'entend désormais, refuse (méfiance), et il force le garde-manger dans le noir à
5 % de chance, 60 minutes durant (les 58 jets de plus). À l'auberge, qui cherchait sans fin (Hugues
194 minutes après Anselme, graine 42 ; Mireille 70 minutes après Odile, graine 7) trouve et parle,
puis attend la part promise ou n'a plus de recours : ces minutes passent de « en chemin » à « sans
rien entreprendre ». À la crue, la hausse vient de nuits qui divergent (graine 1985 : Ilse bien
moins inquiète, sécurité pressante 102 → 26 minutes, froid 65 → 1, mais refusée et affamée plus
longtemps) ; les minutes dans l'eau baissent (271 → 255).

Bancs après la règle des voix (8 h, mêmes graines ; avant la branche → parole de près → voix) :

| | Relais (8) | Mine (4) | Auberge (4) | Crue (4) |
|---|---|---|---|---|
| minutes sans recours | 428 → 426 → 426 | 668 → 696 → 688 | 573 → 634 → 621 | 300 → 339 → 316 |
| appels / réponses | — → 5,1 / 2,3 → 4,6 / 2 | 0 | — → 6 / 1,5 → 6 / 1,5 | — → 9,5 / 2,5 → 6,5 / 2,3 |
| échanges hors appels | 7,6 → 8,4 → 8,4 | 33,3 → 39 → 36 | 21,8 → 25,8 → 23 | 7,5 → 7,5 → 7 |
| confidences | 0,8 → 0,6 → 0,6 | 2,5 → 2,8 → 1 | 5,5 → 6,8 → 5,8 | 1,3 → 0,5 → 0,3 |
| rumeurs crues | 0,5 → 0,4 → 0,4 | 2,5 → 2,5 → 1,5 | 5,5 → 7,3 → 5,8 | 1 → 0,8 → 0 |
| jets | 8,1 → 8,8 → 8,8 | 9,3 → 67 → 66 | 159 → 162 → 160 | 9,3 → 10,5 → 10,8 |

Aucune usurpation ni violation. Les confidences baissent là où l'on se tient dans le noir (mine) :
on ne se confie plus qu'à qui l'on voit ou vient de reconnaître. À la mine, Mathe connaît Odon :
elle reconnaît sa voix dans le noir et lui refuse sa part, comme avec la parole de près ; Odon
force encore le garde-manger. Plus personne n'est accusé de mentir pour avoir dit où était un objet
qu'on a vu ensuite dans d'autres mains (2 accusations à l'auberge avec la parole de près, 0
maintenant). Auberge, graine 42 : la nuit diverge (Tilo voit Lucien poser le ballot, pas Hugues) ;
la nouvelle, avec le lieu, atteint Anselme à 469 minutes et il reprend son ballot.

Limites :
- On constate le contenant rencontré, pas son contenu : l'objet reste cru dedans même s'il n'y est
  plus. Un contenant cru ouvert mais hors d'atteinte (déplacé) laisse l'objet cru disparu.
- Le lieu d'une nouvelle est celui que le témoin a vu au moment du geste ; une croyance tirée d'un
  ouï-dire n'en garde pas la date : de deux nouvelles entendues sur le même objet, la dernière
  entendue l'emporte, même si elle rapporte un geste plus ancien. Le prévenu qui va reprendre son
  bien et ne le trouve pas dans les 30 minutes tient le témoin pour menteur (`esprits.reviser`).
- Seuls `prendre` et `poser` déplacent un objet aux yeux d'un témoin ; un objet remis ou servi ne
  donne pas de lieu.
- On n'appelle qu'en cherchant quelqu'un pour un plan (une part, prévenir) ; un bruit inconnu ne
  fait toujours pas appeler. Qui ne veut pas être trouvé ne se tait que par méfiance. Le joueur
  appelé ne répond pas pour le PNJ.
- Une voix inconnue reste sans réponse, et rien ne le dit à celui qui parle : il redemande à la
  minute suivante, en silence (sa demande ne retentit que si l'échange a lieu), comme avant quand
  ils ne se voyaient pas. On ne demande pas « qui est là ? » ; une voix ne se fait pas connaître
  en se nommant. *(Levé par la branche `voix`, ci-dessous.)*
- Reconnaître une voix, c'est connaître la personne (l'avoir vue suffit) ; aucune chance de se
  tromper ni de ne pas reconnaître une voix connue, et pas de déguisement de la voix. *(La branche
  `voix` sépare la vue de la voix ; le déguisement reste à faire.)*
- `deliberation.autour` compte encore ceux qu'on entend tout près d'après leur place réelle
  (`pnj.de_pres`), sans les identifier ; `passage.pousser` accepte encore qui le joueur a reconnu
  à la voix (`entendus`), désormais seulement une voix connue.
- Forcer une serrure dans le noir à 5 % de chance reste un recours que le planificateur prend
  quand il n'en a pas d'autre (mine, Odon) ; la lumière comme but est un autre chantier.

## Les voix : héler, parler à une voix inconnue, se nommer (branche `voix`)

Deux manques de la branche précédente. L'appel par le nom (`pnj.appeler`) retentissait comme une
parole (voix, 4 crans) : derrière une porte fermée (3 crans), on ne s'entendait que collé à elle ;
à l'auberge, Hugues appelait Anselme en boucle derrière la porte de sa chambre ; au Relais, Aubin
appelait Gorm à chaque minute derrière la porte étanche. Et se parler exigeait que chacun identifie
l'autre : une voix inconnue dans le noir n'était qu'un bruit, personne ne lui répondait, le joueur
lisait « … ne saurait pas qui lui parle », et voir quelqu'un faisait connaître sa voix.

**Héler** (`ouie.NATURES`, nature `hele`, 9 crans comme l'appel). Héler quelqu'un par son nom est
un cri ; ce sont les mots qui le distinguent d'un appel à l'aide, pas le volume. Qui en saisit les
mots entend qu'on appelle tel nom : pas d'alarme, il reconnaît ou retient la voix (`ouie.entendre`).
Le cri parvenu sans les mots (sous le seuil des mots, qu'une oreille aux aguets perçoit encore) est
un bruit fort inconnu : il le retient, et le courage ou la garde peuvent l'y envoyer. L'appelé qui en
saisit les mots répond « Ici ! », hélé aussi, sauf à une voix dont il se méfie ; répondre à son nom
vaut se nommer : l'appelant qui saisit la réponse croit l'appelé là d'où elle vient, sûr de lui s'il
connaît sa voix, sur sa parole sinon (`voix.se_nommer`), et qui la surprend l'apprend de même. Un
appel resté sans réponse est retenu (`appel_sans_reponse`) : la salle compte pour parcourue dans
cette recherche (`deliberation.appels_vains`, lu par `planification._chercher` et entré dans
`_entrees`) tant qu'il n'a rien appris de neuf sur l'appelé, 60 minutes au plus (`APPEL_OUBLI`).
La réponse est chroniquée en nature `reponse` (une réaction, pas un geste de son but : le récit du
banc ne la range pas dans ses épisodes ; elle compte parmi les échanges).

**Parler à une voix inconnue** (`pnj.peuvent_se_parler`, toujours la règle unique de toute parole
échangée : demander, dire, confier, remettre, servir une part, prière de passage, parole du joueur).
Se parler, c'est que chacun saisisse les mots de l'autre (`ouie.s_entendent`) ; celui qui parle
s'adresse à qui il croit là (`croit_present`, qui admet désormais un lieu appris d'une voix qui s'est
nommée). L'auditeur n'a plus besoin d'identifier : une voix qu'il ne connaît pas est un étranger
(`voix.fiabilite` : aucune confiance connue ; `jet_persuasion` ajoute `voix.INCONNU`, une demande
pèse moins), même si elle s'est nommée. Prudent (`voix.prudent` : sa sécurité qui presse, plus
l'écart de son courage à la moyenne, atteint 50), il répond « Qui va là ? » à une voix qui ne s'est
pas nommée au lieu d'accéder (`echanges.accueil`, issue `qui_va_la` pour demander, confier et le
passage) ; entre PNJ, l'autre se nomme aussitôt et redemande (`qui_va_la` n'est pas un refus pour
`refuse_recemment`). Le joueur suit la même règle : il parle dans le noir à la voix qu'il entend ;
le refus « ne saurait pas qui lui parle » disparaît. Sa méfiance envers qui ment ou avoue une faute
va à cette voix quand il ne sait pas à qui elle est (`voix.se_mefier`) ; son ouï-dire porte la source
`dit:voix:<signature>`, que le MJ lit « une voix inconnue le lui a dit », et un aveu d'une voix
inconnue ne devient pas une nouvelle qui nommerait quelqu'un.

**Les voix comme signatures** (`donjon/voix.py`). Connaître de vue (on sait qui l'on voit) n'est pas
connaître une voix : il faut avoir entendu parler quelqu'un en sachant que c'était lui, c'est-à-dire
en le voyant parler (`ouie.entendre`, `ouie._au_joueur`, et `se_parler` quand on se tourne vers lui
dans la lumière). Plus de `connaitre` à la simple vue (`esprits.percevoir`, `pnj._observer_presences`).
Au début d'une partie, le scénario déclare qui se connaît déjà : un savoir sur quelqu'un donne sa voix
(`esprits.installer`) ; le joueur arrive en étranger. Les anciennes sauvegardes ne sont plus migrées
(décision de l'utilisateur). Le moteur sait à qui est chaque voix : sa signature est l'identifiant de
son porteur, jamais montré au joueur ni au MJ comme une identité. Chacun retient les voix inconnues
qu'il a entendues (`voix_entendues` de l'esprit, `data["voix_entendues"]` du joueur : quand, le nom
qu'elle s'est donné, s'il s'en méfie). Toute reconnaissance passe par `voix.reconnaitre(monde,
auditeur, locuteur) -> (qui il croit entendre, certitude)` : reconnue, prétendue (une voix qui s'est
nommée), suspecte, inconnue.

**Se nommer** (contenu de parole `nom` ; « Ici ! » à son nom ; « C'est Odon » après « Qui va là ? ») :
une affirmation pesée, jamais une identité acquise (`voix.se_nommer`).
1. Il connaît la vraie voix du nommé : ce n'est pas elle, mensonge démasqué ; il se méfie de cette
   voix, et de son porteur s'il sait qui c'est (souvenir `imposture`).
2. Sinon il croit « c'est X » comme un ouï-dire : X est cru là (source `se_dit`, confiance d'un
   ouï-dire), sauf s'il a vu X ailleurs depuis moins de 30 minutes (doute). La confiance accordée
   reste celle d'un inconnu ; un bruit ordinaire de là ne la change pas en constat (`ouie._attribuer`).
3. Il entend plus tard la vraie voix de X (en le voyant parler) : elle devient connue
   (`voix.connaitre`) ; une autre voix s'était dite X, il sait qu'on lui a menti, sans savoir qui
   (cette voix devient suspecte, il ne sait plus où est X) ; le jour où il voit parler le menteur, il
   reconnaît « la voix qui se disait X » et se méfie de lui. Si c'était bien X, la croyance passe du
   ouï-dire au constat et sa confiance envers X s'applique.

**Le joueur et le MJ.** Une voix que le joueur ne sait à qui prêter est un interlocuteur comme un autre
(`ecoute.retenir` retient toute voix nette ; `dialogues.interlocuteurs`), désigné « voix_<n> »
(`voix.designation`, `voix.reel` pour le moteur) et nommé « une voix inconnue », « une voix qui se dit
Brune », « … (ce n'est pas la voix de Brune) » s'il connaît la vraie (`voix.nom_pour_joueur`). Le MJ
ne reçoit ni son identifiant ni ses traits (`esprits_interlocuteurs`, `parole_prevue`, le rapport de la
parole, `paroles_entendues`, les locuteurs proposables) ; on ne peut pas la nommer (« je dis à Brune »
refusé : il ne sait pas Brune là). `ecoute` rend les mots d'une voix inconnue sans son nom (« une voix
inconnue appeler : « Odile ? » »). Contenus de parole `nom` (Corvus se nomme, ou prétend être
quelqu'un) et `qui` (« Qui est là ? » : le personnage se nomme, sauf méfiance). Contrôle déterministe
(`narration.voix_inconnues`) : la réplique d'une voix inconnue ne nomme personne, Corvus compris,
au-delà de ce que le moteur a établi (son nom d'interlocuteur, `conversation_validee`), et le récit
ne lui donne pas le nom qu'elle s'est donné (« la voix qui se dit … »).

Vérifié (`tests/test_voix.py`, `tests/test_constater_rumeurs.py`, état après rechargement et ce que
lit le joueur) :
- cas réel (auberge) : Hugues hèle Anselme à travers la porte fermée de sa chambre ; Anselme répond,
  Hugues le croit là, entre et le prévient ; un seul appel ; le joueur au couloir lit « Hugues appelle :
  « Anselme ? » » (voix connue) et « une voix inconnue appeler : « Ici ! » » ;
- même nature (Relais) : Aubin, au palier, hèle Gorm derrière la porte étanche, qui répond ; Aubin
  obtient sa part (avant : un appel par minute, sans fin) ; le même laps découpé donne le même monde ;
- Anselme enfermé et méfiant ne répond pas : Hugues hèle une fois par salle accessible, puis cesse ;
- le cri sans les mots laisse un bruit inconnu fort ; les mots saisis, aucun ;
- le joueur dans le noir demande sa part à Gorm, qui ne l'a jamais vu : au même jet, refusée à la voix,
  accordée à la lumière ; Gorm retient la voix, sans croyance de confiance ; prudent, « Qui va là ? » ;
  « C'est Corvus » : cru sur parole, situé, sans confiance de plus ;
- une voix inconnue (Brune) se nomme au joueur : « voix_1 » pour le MJ, sans traits ni identifiant,
  puis « une voix qui se dit Brune » ;
- imposteur : démasqué par la vraie voix ; démasqué quand il reconnaît le menteur ; cru sur parole
  sans gain de confiance, démasqué après coup, puis le menteur reconnu ; « c'était bien elle » ; le
  joueur qui se dit Brune devant Gorm qui connaît sa voix ;
- voir Brune sans l'entendre ne fait pas connaître sa voix, l'entendre parler sous ses yeux si ;
- mine (Mathe, Odon), réserve noire : Mathe, inquiète, répond « Qui va là ? » ; Odon se nomme et
  redemande ; elle le croit là sur sa parole, sans confiance gagnée.

Tests d'avant changés par la règle : l'aveu entendu derrière le pilier par Brune (elle se méfie de la
voix, n'en fait pas une rumeur nommant Corvus) ; Brune trouve Gorm au premier appel (`test_caractere`) ;
une voix jamais entendue se fait répondre ; servir une part suit `s_entendent` ; le joueur parle à Odile
qui ne le connaît pas ; « des voix » devient leurs mots sans nom quand il connaît ce qu'ils nomment.

Avec Luna (copies de scènes, placements d'auteur ; 2 parties au plus en même temps) :
- noir, Gorm qui ne connaît pas Corvus : la demande de part est refusée (« Non. Je ne suis pas
  convaincu… »), « c'est Corvus » est cru sans plus de confiance, la redemande refusée ;
- Corvus qui se dit Brune devant Gorm : « Tu n'es pas Brune. Je ne te fais plus confiance. » ;
- une voix inconnue (Brune) : « « Qui est là ? » » → « Tu dis à une voix inconnue… », « La voix répond :
  « Je suis Brune… » », puis « Tu dis à une voix qui se dit Brune… » ; « c'est Brune qui me parle ? »
  (question au MJ) : « Tu ne peux pas savoir si c'est Brune… » ; « je dis à Brune : approche » : refus du
  moteur. Deux défauts vus et corrigés par le contrôle déterministe ci-dessus : la voix répondait « Je
  suis Brune, oui » sans que le moteur l'ait fait se nommer, le récit écrivait « Brune répond », et la
  voix demandait « Tu dis t'appeler Corvus ? » sans qu'il se soit nommé. Après correction : « La voix
  répond tout près de toi : « Je suis Brune. Qui es-tu ? » » (se nommer décidé par le moteur), et le
  récit dit « la voix » ensuite.

Bancs (8 h, graines 1985 7 42 2024, avant = dd6ea75, base de la branche, dont `main` ne diffère depuis que par le transport
du MJ ; les appels comptent parmi les échanges) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| minutes sans recours | 362,5 → 335 | 665 → 655 | 627,5 → 670 | 292,5 → 301,25 |
| appels / réponses | 3,75 / 1,5 → 3 / 3 | 7 / 0,75 → 2,5 / 2,5 | 17 / 2,25 → 3,5 / 2,75 | 4,75 / 1,25 → 7,5 / 5,75 |
| échanges | 15,25 → 16 | 41,75 → 38,25 | 40,75 → 28,25 | 16,75 → 24 |
| vols vus / témoins | 1,5 / 3 → 1,5 / 3,25 | 0,5 / 1 → 0,5 / 1 | 1 / 2,25 → 0,75 / 1,5 | 1,5 / 2,5 → 1,5 / 2,75 |
| rumeurs crues | 0,5 → 0,75 | 2 → 2 | 1 → 3 | 1,25 → 0,75 |
| confidences | 0,75 → 1 | 2 → 2 | 3,25 → 5 | 1,25 → 0,75 |
| méfiances | 2 → 2 | 4,5 → 4,5 | 5 → 6,5 | 2,25 → 2 |
| jets | 8,75 → 9,75 | 23,75 → 24 | 161 → 88 | 11,75 → 11,25 |
| paroles surprises | 11,5 → 19 | 110 → 118,25 | 37,75 → 54,5 | 16,75 → 27,25 |
| bruits inconnus retenus | 59,75 → 53,25 | 62 → 67 | 147,5 → 133,25 | 90 → 99 |
| allés voir | 12,25 → 9,75 | 18,5 → 24,75 | 57,25 → 47,5 | 18,5 → 21,5 |
| minutes dans l'eau | | | | 251,25 → 271,25 |

Aucune usurpation, aucune violation (l'état est vérifié à chaque pas). Les appels baissent là où l'on
tournait en appelant derrière une porte fermée : à l'auberge 17 → 3,5 par nuit, c'est l'essentiel de
la baisse des échanges (40,75 → 28,25) ; à la mine 7 → 2,5 ; les réponses montent partout (le cri
passe les portes). Relais : Brune trouve Gorm au premier appel (graine 42 : 139 → 59 minutes sans
recours), d'où 362,5 → 335. Auberge : des recherches plus courtes laissent ensuite sans recours ;
graine 2024, Mireille trouve Odile au premier appel au lieu de passer par l'étable en la cherchant,
ne voit donc pas les fagots de Joss et reste sans bois (326 → 364 minutes) ; Lucien crochète le coffre
d'Anselme à 406 au lieu de s'y acharner 200 minutes (jets 200 → 53), puis attend (59 → 106) ; la nuit
diverge ensuite (plus de rumeurs crues et de confidences). Crue : Aubin et Gorm se hèlent et se
répondent en se croisant (graine 1985, 11 appels et 11 réponses) ; minutes dans l'eau 251 → 271 par
des nuits qui divergent. Paroles surprises en hausse : la réponse « Ici ! » se nomme à qui l'entend.

Limites :
- Imiter une voix et se méfier d'une voix connue quand un imitateur rôde ne sont pas modélisés : tout
  passe par `voix.reconnaitre`, où ils se brancheront (une certitude moindre, une voix prise pour une
  autre), sans toucher ses appelants.
- Un PNJ ne ment pas sur son nom ; seul le joueur peut se dire un autre. Un PNJ qui démasque un
  imposteur s'en méfie (souvenir `imposture`) mais ne le raconte pas aux autres : ce n'est pas une
  nouvelle de `social`.
- Le cri sans les mots ne survient que sous le seuil des mots (niveau 0, oreille aux aguets ou fine) ;
  l'inquiétude étant à la mesure du niveau reçu, il inquiète peu ; il fait surtout aller voir.
- L'appelé ne s'attend pas : il reprend son but après avoir répondu ; deux PNJ qui se cherchent
  peuvent se croiser (crue, graine 1985 : Aubin et Gorm se hèlent et se répondent six fois en dix
  minutes avant de se trouver). Corrigé ensuite : branche `parole-voix`, « Qui répond attend ».
- Une demande de part à une voix inconnue est « impossible » quand l'auditeur ne sait rien de qui
  la fait (ni où, ni sa faim) : la demande ne dit pas la faim. Une voix inconnue ne peut pas recevoir
  un don du joueur sous son nom ; elle peut être désignée en face. Revu : branche `voix-inconnues`
  (la cause était la porte verrouillée de la réserve, pas la voix).
- La réplique d'une voix inconnue ne peut nommer un tiers que le joueur n'a pas nommé dans ce tour :
  la règle déterministe est plus stricte que nécessaire (elle ne distingue pas « je suis X » de « X est
  aux vannes »). Corrigé : branche `voix-inconnues`.
- Le joueur ne retient le nom d'une voix que par une parole qui le lui donne directement (contenu `qui`) ;
  ce qu'il surprend entre PNJ (« Ici ! » à un appel) ne lui nomme pas la voix, et il ne hèle personne
  par son nom (seul l'appel à l'aide est un cri pour lui). Héler : branche `parole-voix` ; ce qu'il
  surprend : branche `voix-inconnues`.

## Nommer, attendre, héler (branche `parole-voix`)

Trois manques des branches `banc-luna` et `voix`, une même famille : ce que le joueur et les PNJ font
d'un nom et d'un appel.

**Nommer qui l'on connaît** (`paroles.identites`, `paroles._connu_du_joueur`, `Monde.identifier`).
Avant, le joueur ne connaissait un personnage que par une trace fragile : un souvenir de sa place
(`souvenirs_visuels`, effacé quand on regarde la place vide), un portrait vu de près, ou une mention
récente dans ce que le MJ a lu. Vu de loin puis parti, Ilse n'était plus « connue » : « je dis à Ilse :
viens » ne la nommait plus, et la parole partait au MJ ou allait à qui était en face. Règle : le joueur
connaît un personnage d'après ce qu'il sait de lui, jamais d'après une place : il l'a vu (la scène le
nomme ; `data["personnages_vus"]`, tenu à chaque action par `Monde.identifier`, y compris qui n'a été
qu'aperçu pendant l'action), il connaît sa voix, ou une voix s'est donné son nom. Le nommer absent
donne le refus de la parole ou du geste : « Tu ne vois pas Ilse d'ici : approche-toi pour lui
parler », « Ilse, meunière évacuée n'est pas là pour le recevoir » (l'analyse du don nomme aussi
l'absent connu, `commandes._nomme` ; le refus du moteur le nomme même quand personne n'est là,
`dialogues.verifier_don`). Le MJ reçoit `personnages_connus` (identifiant et nom, sans place), ce que
l'auditeur lisait comme « Ilse n'est ni présente ni identifiée dans les faits ». Pas de migration : une
ancienne partie remplit la liste à la première action.

**Qui répond attend** (`deliberation.attendre_l_appelant`, `attendre`, `rejoint`, `_plan_attendre` ;
esprit `rejoint`). Avant, l'appelé répondait « Ici ! » puis poursuivait sa ronde ou allait voir un bruit ;
l'appelant arrivait sur une salle vide et rappelait (crue, graine 3 : Ilse hèle Gorm cinq fois en quatre
minutes pendant qu'il va voir les bruits qu'elle fait). Règle : qui répond à un appel s'attend à être
rejoint. Il attend sur place `REJOINT` (5) minutes, sauf ce qui passe avant (`_passe_avant` : un besoin
qui presse, la parole donnée, prévenir, un réflexe, une stratégie, et ce qu'il fait déjà sur place,
où il attend aussi bien) ; la routine, aller voir un bruit, ce qui ne presse pas et l'argent lui
cèdent, aussitôt (il s'arrête au moment de répondre) puis à chaque délibération (le but vient après la
parole due, avant le bruit et la routine). S'il cherche lui-même l'appelant et reconnaît sa voix, il
sait où il est : sa recherche ailleurs tombe et il va vers lui. L'attente vit dans son esprit et prend
fin quand ils se voient (« Gorm retrouve Aubin, qui l'avait hélé. »), quand ils se parlent (toute
parole échangée, `pnj.se_parler`, et celle du joueur), ou à l'échéance (« … cesse d'attendre … »).
Banc : `retrouvailles`, `attentes_vaines`, `minutes_a_attendre` ; les deux premières, chroniquées en
nature `reponse`, ne comptent pas parmi les échanges mais comptent parmi les événements distincts.

**Le joueur hèle** (`paroles.hele`, `commandes.heler`, `sons._compiler_heler`, `pnj.heler`,
`pnj.repondre`). Héler est un geste du moteur, par la règle des PNJ, factorisée : `pnj.appeler` =
`heler` (le cri, nature `hele`, 9 crans) puis `repondre` (« Ici ! » sauf méfiance, se nommer, attendre
l'appelant). L'analyse locale reconnaît « j'appelle Gorm », « je hèle Gorm », « je crie le nom de
Gorm », « j'appelle Gorm par son nom », « je crie « Gorm ? » », « crier : Gorm ! », suivis au plus de
« fort » ou « à voix haute », avec un personnage que Corvus connaît ; une forme en question n'est pas
une question au MJ (`jeu.py`). Le geste est `emettre_son`, méthode `heler`, cible le personnage (3 s) ;
le MJ peut aussi le proposer (consigne d'une ligne), refusé avec `attendu` s'il ne nomme personne
(« Dis qui tu appelles par son nom ») ou quelqu'un que Corvus ne connaît pas. La réponse vient le cri
fini et s'entend par l'ouïe commune : « Tu entends, à l'ouest : Gorm répond : « Ici ! » » d'une voix
connue, « … une voix qui se dit Gorm répondre : « Ici ! » » sinon (une réponse s'écrit désormais
« répondre », `ecoute._heler`) ; sans réponse parvenue, « Aucune réponse ne te parvient. ».

Vérifié (`tests/test_parole_voix.py`, état après rechargement et ce que lit le joueur) :
- nommer : cas réel (Ilse vue à trois cases, partie, sa place regardée vide, sept actions sans la
  nommer) : « je dis à Ilse : viens m'aider » donne le refus du moteur sans appel ; même nature, le don
  (« je donne la cloche à Ilse » : remettre, refus « n'est pas là pour le recevoir ») ; Brune jamais vue
  mais voix connue, Aubin seulement nommé par une voix : refus justes ; Ilse jamais vue ni nommée :
  inconnue ;
- attendre : cas réel rejoué au Relais (Aubin affamé hèle Gorm, qui part en ronde) : Gorm attend là où
  il a répondu, un seul appel, la part demandée à la minute 4 (sur `main` : deux appels, minute 6) ; le
  même laps découpé donne le même monde ; personne ne vient : il cesse d'attendre à l'échéance puis fait
  sa ronde ; la faim qui presse passe avant, puis il attend ; Aubin, qui cherche Gorm et connaît sa
  voix, va vers lui à son appel, sans rappeler ;
- héler : les formes et ce qui n'en est pas (« j'appelle à l'aide », « je crie », deux noms, une parole
  entre guillemets, un objet) ; cas réel, Gorm derrière la porte étanche : aucun appel au MJ, la réponse
  d'une voix inconnue qui se dit Gorm, retenue ; Gorm attend Corvus jusqu'à ce qu'il ouvre la porte ;
  voix connue et forme en question ; Gorm méfiant ne répond pas ; refus du MJ (cible inconnue, cible
  joueur), chacun sa cause et son `attendu`.

`planification.VERIFIER` sur une nuit de chaque scénario (graine 1985) : aucune reprise périmée.

Bancs 8 h contre `main` 1ee493b, lancés ensemble (Relais 8 graines, les autres 4) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| appels / réponses | 1,25 / 1,25 → 1 / 1 | 2,75 / 2,5 → 2,5 / 2,25 | 6 / 2,5 → 6 / 2,5 | 2,75 / 2,5 → 2,25 / 2 |
| retrouvailles / attentes vaines | — → 1 / 0 | — → 2 / 0 | — → 2 / 0,25 | — → 2 / 0 |
| échanges | 11 → 11 | 28,25 → 28,25 | 23,75 → 23,75 | 10,75 → 10,75 |
| minutes sans recours | 53,1 → 53,1 | 56,25 → 56,25 | 67,5 → 67,5 | 15 → 15 |
| minutes en attente | 67,5 → 68,1 | 303,75 → 303,75 | 622,5 → 622,5 | 105 → 106,25 |
| vols vus / témoins | 1 / 2,4 → 1 / 2,4 | 0,75 / 2,75 → idem | 0,5 / 1 → idem | 0,25 / 0,25 → idem |
| temps d'une nuit | 10,9 → 9,5 s | 24,3 → 24,3 s | 30 → 30 s | 10 → 10,1 s |

Aucune usurpation ni violation. Les nuits ne divergent presque pas : l'attente ne dure que jusqu'à
l'arrivée de l'appelant, qui venait de toute façon. Les appels baissent là où l'appelé s'en allait :
Relais graine 11, 4 → 2 ; crue sur 12 graines 2,33 → 1,67 par nuit (graine 3 : 7 → 3, Ilse obtient sa
part à la minute 333 au lieu de 340 ; graine 2024 : 5 → 3 ; graine 123 : 3 → 1). À l'auberge, les
appels restés sans réponse (méfiance, porte, distance) ne changent pas. Les événements distincts
gagnent une à deux retrouvailles par nuit.

Avec Luna (copies de la sauvegarde réelle, placements d'auteur sur la copie ; 2 parties au plus en même
temps), avant (`main`) → après :
- Corvus au palier, Gorm derrière la porte étanche fermée : « j'appelle Gorm » 4 appels, « Gorm n'est
  pas ici : tu ne peux pas l'interpeller » → 0 appel, « Tu appelles : « Gorm ? » », la réponse d'une voix
  qui se dit Gorm ; « je crie le nom de Gorm » 4 appels, « Tu cries le nom de Gorm à l'aide… » (un cri
  sans nom) → 0 appel ; Gorm, sur `main`, avait quitté la salle des vannes à l'ouverture de la porte ;
  après, il y attendait. « Gorm ? Tu es là ? » (texte libre) reste au MJ : Luna rappelle la réponse
  entendue sans héler de nouveau (2 appels).
- Ilse partie, sa place vide : « je dis à Ilse : viens m'aider » refus du moteur des deux côtés (sur
  `main`, ce que le MJ avait lu la nommait encore) ; « je donne la cloche à Ilse » 2 appels et une explication de Luna
  → 0 appel, refus du moteur ; « j'appelle Ilse » 6 appels, deux plans refusés par la contre-revue (un cri,
  un appel à l'aide) → 0 appel, Ilse répond et attend. « Ilse, viens m'aider à porter la cloche »
  (interpellation libre) : 4 appels sur `main` ; 10 et 9 appels dans les deux premières parties de la
  branche (Luna proposait `heler`, avec la cible « joueur » puis refusé par la contre-revue, qui jugeait
  qu'appeler ne couvre pas « viens m'aider »), 2 appels après le refus séparé « Dis qui tu appelles » et la
  consigne précisée.

Limites :
- Seules les formes reconnues sont des appels du moteur ; une interpellation libre d'un absent
  (« Gorm ? Tu es là ? », « Ilse, viens m'aider ») reste au MJ, qui peut proposer `heler` ou une parole
  (refusée par le moteur), ou répondre en dialogue ; son coût varie.
- Connaître de vue : la scène nomme quiconque est visible, même de loin ou dans la pénombre ; connaître
  quelqu'un, c'est l'avoir vu ainsi. Aucun déguisement n'est modélisé.
- L'attente se juge à la minute (la délibération) ou à la parole : l'appelé qui voit arriver l'appelant
  au milieu d'une minute reste immobile jusqu'à la suivante. Il ne se tourne pas vers la voix.
- `REJOINT` est une constante du moteur ; qui ne cherche pas l'appelant l'attend même si l'appelant n'a
  pas entendu sa réponse (au plus 5 minutes perdues).
- La réponse au joueur vient au terme de son cri (3 s), avant que les PNJ ne vivent ces secondes.
- Le joueur ne répond pas de lui-même à qui le hèle ; « Ici ! » de sa part reste une parole. Corrigé :
  branche `voix-inconnues`.

## Les voix inconnues (branche `voix-inconnues`)

Trois limites de la branche `voix` : une part demandée par une voix inconnue relevée comme
« impossible », un contrôle des répliques d'une voix inconnue trop strict, et un joueur qui n'apprenait
rien des voix qu'il surprend et ne répondait pas à qui le hèle.

**Une demande d'une voix inconnue se juge comme celle d'un étranger.** Revu, le cas relevé (la réserve
noire de la mine, Mathe qui ne connaît pas Odon) n'était pas un défaut de la voix : la réserve est
verrouillée et Mathe ne peut atteindre le garde-manger (`planification` : aucun plan pour servir) ; la
même demande d'une voix connue y est aussi « impossible ». La règle tient déjà : `echanges.demander`
ne lit de celui qui demande que sa confiance perçue (`voix.fiabilite` : un étranger) et le poids de sa
demande (`voix.INCONNU`) ; servir une part se planifie là où sont les vivres, sans savoir où est le
demandeur ni s'il a faim (`echanges.tenu`). Un écart corrigé en route : une part de bois entretient le
feu de la salle d'où l'on entend la demande (`echanges.foyer_de`, par `ouie._place`), le joueur compris
(avant : le premier feu connu du donneur, faute de lire la salle du joueur).

**Une voix inconnue nomme qui son locuteur connaît, jamais elle-même** (`narration.voix_inconnues`,
`voix.connait_nom`). Le moteur sait qui parle derrière « voix_<n> » (`voix.reel`) et ce qu'il sait.
Sa réplique peut nommer un tiers dont il sait le nom : une croyance à son sujet, sa voix, ou le nom
qu'une voix s'est donné ; Corvus, qui arrive en étranger, seulement s'il lui a donné son nom (`se_dit`)
ou qu'il a entendu parler de lui (un ouï-dire `dit:…`). Elle ne nomme jamais son propre locuteur au-delà
de ce que le moteur a établi (son nom d'interlocuteur, `conversation_validee`, la réplique de Corvus),
et ne se dit personne (`SE_NOMMER` : « je suis… », « je m'appelle… », « moi, c'est… » suivis d'un nom).
Une voix que le moteur ne relie à personne garde la règle d'avant. Le récit ne lui donne toujours pas
son nom prétendu ; le MJ ne reçoit toujours ni son identifiant, ni ses traits, ni ce qu'elle sait.

**Ce que le joueur entend des voix** (`ecoute.lier`, `voix.nommer`, `ouie._au_joueur`).
- Voir parler quelqu'un fait connaître sa voix, qu'il s'adresse au joueur ou non : la réponse d'un
  PNJ à un autre retentit désormais de sa propre voix (`social.faire_entendre`, `reponse` : accepter,
  refuser ; remettre l'objet ou s'écarter est un geste, sans voix), et la réplique que le MJ prête à
  un personnage que Corvus voit lui apprend sa voix (`narration.consigner`, `faits_locaux`). Avant, la
  réponse d'un PNJ était fondue dans la phrase de qui demandait, et une réplique du MJ n'apprenait rien.
- « Qui va là ? » puis « C'est Odon » se disent chacun de sa voix (`social.qui_va_la`, pour une demande
  et pour une prière de passage) ; avant, les deux répliques partaient de la voix du demandeur.
- Une parole dont il saisit les mots est rangée avec ses destinataires (`a`), même s'il voit qui
  parle (`vu`, sans être rendue de nouveau). Une voix qui dit son propre nom dans ses mots se dit ainsi
  (`voix.se_nommer`). Une voix à qui une autre s'adresse en la nommant, qu'il entend dans le même
  échange (`ECHANGE`, une minute, avant ou après), est « une voix qu'on appelle Gorm » (`appelee`,
  facultatif dans `voix_entendues`) : un ouï-dire, jamais une identité ; rien s'il connaît la vraie
  voix de Gorm, s'il sait déjà à qui est cette voix ou si elle s'est nommée. C'est le cas de « Gorm ? »
  suivi d'un « Ici ! » d'une autre voix. Les mots cités d'une parole nette se rendent tels qu'ils sont
  dits, même s'ils nomment quelqu'un qu'il ne connaît pas (« une voix inconnue appeler : « Odile ? » ») ;
  le texte entier, lui, reste réservé à une voix reconnue qui ne nomme que ce qu'il connaît. Le nom
  qu'on donne à une voix fait connaître ce nom (`paroles.identites`), comme celui qu'elle se donne.

**Le joueur répond à qui le hèle** (`paroles.repond`, `commandes.repondre`, `sons._compiler_repondre`,
`pnj.repondre_a`). Le geste de réponse des PNJ est factorisé (`pnj.repondre` décide pour un PNJ,
`repondre_a` est l'acte) : « Ici ! », un cri qui vaut se nommer ; l'appelant qui l'entend le croit là
(sûr de lui s'il connaît la voix de Corvus, sur sa parole sinon) ; qui le surprend l'apprend de même.
Juste après un appel de Corvus par son nom (`ecoute.appels` : la dernière parole de l'appelant est cet
appel, entendu pendant son dernier geste ou il y a moins d'une minute), l'analyse locale reconnaît « je
réponds », « je lui réponds », « je réponds à Gorm », « je réponds à l'appel », « je réponds : ici ! »,
« je crie « Ici ! » », ou les seuls mots d'une réponse entre guillemets (« « Ici ! » », « « Oui, je suis
là ! » ») ; c'est le geste `emettre_son` méthode `repondre`, cible l'appelant sous le nom que Corvus lui
connaît (voix_<n>), sans le MJ. Le MJ peut le proposer (une ligne de consigne) ; refus avec `attendu`,
une cause chacun : personne ne vient d'appeler Corvus, la cible n'est pas l'appelant. Le premier geste
d'une manœuvre se juge sur ce qu'il a entendu pendant le geste précédent (`data["entendus"]` est remis
à zéro après lui, `Moteur._executer_operations`).

Vérifié (`tests/test_voix_inconnues.py`, `tests/test_voix.py`, `tests/test_constater_rumeurs.py`, état
après rechargement et ce que lit le joueur) :
- demande : Mathe, qui n'a jamais entendu Odon et ne sait rien de lui, lui promet sa part dans le noir et
  la lui sert, comme à un inconnu qu'elle voit (même jet ; le DD dans le noir est celui de la lumière plus
  `INCONNU`) ; la réserve verrouillée rend la part « impossible » que la voix soit connue ou non ; Gorm,
  qui ne sait rien de Corvus, lui promet sa part dans le noir ; une part de bois demandée par Corvus à la
  cuisine va au fourneau, pas à l'âtre ;
- répliques : la voix de Brune nomme Gorm et Ilse ; « Je suis Brune », « Brune n'a rien vu », « Je
  m'appelle Ilse », « Moi, c'est Gorm », Aubin dont elle ne sait rien, et toute voix que le moteur ne relie
  à personne sont refusés ; « Corvus » seulement après qu'il s'est nommé à elle ; la chaîne
  `consigner` → sauvegarde → rechargement ;
- voix : cas réel (auberge), Corvus au couloir entend Hugues appeler « Anselme ? » puis « une voix qu'on
  appelle Anselme répondre : « Ici ! » » (avant : « une voix inconnue ») ; même nature, au grenier noir,
  « une voix inconnue appeler : « Odile ? » » puis « une voix qu'on appelle Odile » ; Corvus qui voit
  Aubin demander sa part et Gorm lui répondre connaît leurs deux voix ; une réplique du MJ de Gorm qu'il
  voit lui apprend sa voix, reconnue ensuite dans le noir ; dans la réserve noire, « Qui va là ? » de la
  voix de Mathe, « C'est Odon » de celle d'Odon, qui se dit Odon ;
- répondre : les formes et ce qui n'en est pas (une parole qui dit autre chose, un autre nom, « je
  crie », un appel, rien sans appel) ; cas réel, Gorm derrière la porte étanche cherche Corvus et l'appelle
  (intention placée d'autorité, voir les limites) : « je réponds », aucun appel au MJ, « Tu réponds :
  « Ici ! » », Gorm le croit au palier sur sa parole ; même nature, « « Ici ! » » à Gorm qui connaît sa
  voix : il le sait là ; refus du MJ, chacun sa cause et son `attendu`.

Tests d'avant changés par la règle : l'appel d'Hugues et l'appel de Mireille (le joueur nomme désormais la
voix qui répond, « une voix qu'on appelle … »).

Bancs 8 h contre `main` 888bbc4, lancés ensemble (4 graines, Relais `--joueur chambre_cloche`, auberge
`--joueur dortoir`) : aucune usurpation ni violation ; échanges, appels et réponses identiques (Relais
10,5 échanges, 1,75 appel, 1,5 réponse ; auberge 25,75, 3,5, 2,25). Relais : trois nuits identiques, la
quatrième (1985) diverge à la minute 446 sur un retournement (150,5 → 150 en moyenne) ; auberge : deux
nuits identiques, deux divergent sur une réponse qui retentit désormais de la voix de qui répond (Tilo se
retourne au bruit) : bruits inconnus 117 → 115,75, allés voir 29,75 → 30,5, paroles surprises 58 → 58,25,
minutes en attente 536,25 → 537,5.

Avec Luna (copies de scènes, placements d'auteur ; 2 parties au plus en même temps) :
- Corvus dans le noir près de Gorm, qu'il ne connaît que comme une voix (2 parties, 4 tours) : « « Une
  part des vivres… » » refusée par le moteur, la voix demande 2 pièces ; « « Qui es-tu ? » » devient le
  contenu `qui`, le moteur la fait se nommer : « Je suis Gorm, le gardien du relais. », puis « Tu dis à
  une voix qui se dit Gorm » ; aucun refus du contrôle. Luna ne nomme aucun tiers (« Je ne sais pas qui
  d'autre est au relais ») : elle ne sait pas qui la voix connaît. 3 appels par tour.
- Gorm hèle Corvus derrière la porte étanche : « je réponds », 0 appel, « Tu réponds : « Ici ! » », Gorm le
  croit au palier ; « « Gorm ? C'est toi ? » » (parole) se dit à la cantonade : la voix ne passe pas la
  porte. « Je lui crie que je suis là, derrière la porte. » (texte libre, 2 parties) : 9 appels et « Je
  n'ai pas pu déterminer une manœuvre fidèle », puis 4 appels et un cri sans mots (méthode `cri`) qui fait
  venir Gorm voir le bruit ; Luna ne propose pas `repondre`.

Limites :
- Aucun scénario ne fait encore chercher le joueur par un PNJ (`deliberation._plan_prevenir` et
  `planification._rendre` ne visent qu'un personnage ; un objet du joueur n'a pas de propriétaire) : le
  cas réel place l'intention d'autorité, et Gorm, sans motif qui dure, n'en tire qu'une croyance.
- Une réponse libre (« je lui crie que je suis là ») reste au MJ, qui a préféré un cri sans mots ; seules
  les formes reconnues sont la réponse du moteur. Un appelant que Corvus voit compte une minute.
- Le MJ ne sait pas qui une voix inconnue connaît (le lui dire trahirait qui elle est) : la règle évite
  de refuser un nom juste, Luna n'en invente pas. Il ne sait pas non plus si c'est une femme ou un homme
  (« Je ne suis pas convaincue » pour Gorm). Le genre : branche `voix-suite`.
- `voix.connait_nom` : un PNJ qui voit Corvus se nommer ne retient pas son nom au-delà de ce tour
  (rien ne l'enregistre quand il le reconnaît déjà) ; un PNJ connaît le nom de qui il a une croyance.
  Corrigé : branche `voix-suite`.
- Le lien « une voix qu'on appelle … » ne se fait que si la voix nommée est vraiment celle qu'on appelle
  et qu'il l'entend dans le même échange ; une voix qui se tait pendant l'appel ne se nomme pas, une
  autre qui parlerait à sa place non plus (pas de méprise). Seul le joueur l'apprend ainsi ; un PNJ
  n'apprend un nom que d'une voix qui se nomme. Les répliques que Luna prête aux PNJ ne relient pas les
  voix entre elles (elles s'adressent à Corvus). Les PNJ : branche `voix-suite`.

## L'ancien son fondu dans l'ouïe commune (branche `ouie-commune`)

Deux systèmes coexistaient : l'ouïe commune (pas, gestes, voix, héler) et l'ancien son
(`sons.appliquer`, `portee`, `auditeurs`) pour l'appel à l'aide, le cri, le sifflement du joueur et
le son d'un objet, avec sa portée salle par salle (une ouverture 1, une porte 2, sans distance), une
humeur « inquiet » ou « méfiant » forcée à qui l'entendait, un souvenir `son` à part et un réflexe
déclaré (`reaction_son`) qui faisait rejoindre l'origine d'office, ou accourir le protecteur d'un
protégé (connu de façon omnisciente). Un même cri ne s'entendait pas pareil selon qu'il venait du
joueur ou d'un PNJ ; la cloche ignorait la distance ; le réflexe court-circuitait le devoir et le
courage. Règles retenues :

- **Une seule ouïe.** Les sons du joueur et des objets retentissent par `ouie.retentir` (depuis
  `moteur._terminer_etape`, nature donnée par `sons.nature_emise`) : appel à l'aide et cri sont des
  appels (9 crans), un sifflement un fracas (7, inhabituel, sans mots), le son d'un objet selon sa
  sonorité (`ouie.SONS` : 1 un geste, 2 un fracas, 3 un appel ; la cloche d'alarme), un son improvisé
  de même selon son intensité. `sons.portee`, `liens` et `auditeurs` disparaissent ; `data["sons"]`
  garde l'historique de ce qui est émis, avec ceux qui l'entendent par l'ouïe commune
  (`sons.entendants`) ; les paroles que le MJ prête aux PNJ sont entendues de ceux qui en saisissent
  les mots (`ouie.saisissent`, `narration`, `faits_locaux`) ; l'humeur liée au tapage du joueur se
  calcule sur ceux qui entendraient un fracas.
- **Un appel porte la voix.** Sans mots, un appel ou un cri fait savoir qui crie à qui connaît cette
  voix (`voix.reconnaitre`) : il le croit là (`entendu`) et le bruit qu'il retient le nomme (`qui`).
- **Plus de réflexe, une alarme délibérée** (`deliberation.alarme`) : le seuil d'alerte devient une
  donnée du profil (`alerte`, en crans de l'ouïe commune). Un bruit inconnu d'un autre lieu qui lui
  est parvenu à ce niveau, ou l'appel d'un protégé dont il a reconnu la voix, l'envoie voir avant tout
  le reste (le but `voir` du planificateur, motif devoir) ; les autres bruits suivent `bruit_a_voir`
  (devoir de garde, courage). Sans passage cru, aucun plan : il ne part pas. Un personnage sans profil
  (la crypte) ne délibère pas : il retient le bruit inhabituel qu'il entend sans le voir, sans bouger.
  Données migrées : à l'auberge, le `reaction_son` d'Hugues (seuil 2 de l'ancienne échelle : un appel
  d'une salle voisine ouverte) devient `alerte` 3 (le même appel lui parvient à 3 crans depuis la
  cuisine) ; une partie qui porte encore `reaction_son` est refusée au chargement (pas de migration).
- **Plus d'humeur forcée** : l'inquiétude ne vient que de l'ouïe commune, à la mesure de ce qui
  parvient (`deliberation.inquieter`, déjà en place pour les autres bruits).
- **Un seul souvenir** : le souvenir `bruit` de l'ouïe commune (lieu, nature, niveau le plus fort,
  `qui` d'un appel reconnu) ; `esprits.dernier_son`, que le MJ reçoit (`dernier_son_entendu`), le lit.
  `esprits.entendre` et `pnj.reagir` disparaissent. Ce qu'un PNJ voit faire n'a pas besoin de l'ouïe :
  un joueur qui chante sous ses yeux ne laisse aucun bruit retenu.
- **L'appelé se tourne vers la voix** (`ouie._vers_la_voix`) : hélé par son nom, il se tourne vers
  l'appelant dans sa salle, ou vers le seuil par où la voix arrive d'une autre, le temps de la
  rotation, et peut ainsi le voir (« se tourne vers la voix qui l'appelle » ; mesure `vers_la_voix`).
- **La réponse au joueur vient à la fin de son cri** : le moteur décide qui répond après que les PNJ
  ont vécu les 3 secondes du cri (`moteur._terminer_etape`, `pnj.repondre` après `avancer`).

Vérifié après rechargement (`tests/test_ouie_commune.py`, et les tests adaptés de `test_sons`,
`test_reactions`, `test_protection`, `test_improvisation`, `test_narration`, `test_securite`,
`test_eau`, `test_esprits`, `test_rejeu`) : l'appel du joueur derrière la porte étanche fermée
parvient à 6 crans contre la porte et à 3 au fond des vannes (avant : 1 partout) ; au seuil d'alerte
5, le proche accourt, le lointain non ; d'un bloc ou découpé en rotations rechargées, Gorm alerté va
chercher la clé du relais et le monde est le même ; la cloche, sonnée de la galerie, parvient au
refuge comme un appel, et Gorm ira voir (devoir) ; Ilse à bout appelle, Gorm reconnaît sa voix et
accourt, il ne le fait pas s'il ne connaît pas sa voix ; Hugues (alerte 3, cas réel) accourt à l'appel
du couloir, Odile non ; Gorm hélé dans son dos se tourne, voit le joueur et répond, et appelé d'une
autre salle se tourne vers le passage ; la réponse du joueur hélant est datée de la fin de ses 3
secondes. `VERIFIER` sur une nuit de chaque scénario.

Bancs 8 h, `main` cd38352 puis la branche (Relais 8 graines, joueur à la galerie ; mine, auberge et
crue 4 ; moyennes par nuit, `main` → branche) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| appels (héler) / réponses | 1,25 / 1,13 → 1,25 / 1,13 | 2,75 / 2,25 → 2,75 / 2,25 | 6,75 / 2,25 → 5,25 / 1,75 | 2,5 / 2,5 → 2,5 / 2,5 |
| retrouvailles | 1 → 1,13 | 2,25 → 2,25 | 2 → 1,5 | 2,25 → 2,25 |
| appels à l'aide | 0,38 → 0,38 | 3 → 3,25 | 2,25 → 3,25 | 0 → 0 |
| allés voir | 9,25 → 9,25 | 13,75 → 18,25 | 39,25 → 35,25 | 12,75 → 12,75 |
| bruits inconnus | 50,25 → 50,25 | 57,5 → 62 | 134,5 → 126,75 | 75 → 75 |
| retournements | 145,1 → 144,9 | 164,5 → 167,3 | 119 → 113 | 153 → 153 |
| tournés vers la voix (nouveau) | → 0,88 | → 1,5 | → 1,25 | → 0,75 |
| sécurité en fin de nuit (moyenne des PNJ) | 0,1 → 0,1 | 33,3 → 29,9 | 19,3 → 21,9 | 5,4 → 5,4 |
| vols vus | 0,88 → 0,88 | 1 → 1 | 0,5 → 0,75 | 0 → 0 |
| sans recours / en attente | 53,8 / 66,3 → 53,8 / 66,3 | 55 / 281 → 55 / 279 | 43,8 / 541 → 30 / 541 | 15 / 107,5 → 15 / 107,5 |
| nuits distinctes | 8 partout → 8 partout | 4 → 4 | 4 → 4 | 4 → 4 |
| temps d'une nuit | 6,3 → 6,2 s | 23,7 → 22,3 s | 17,9 → 17,8 s | 7,9 → 8,4 s |

Aucune usurpation ni violation (le banc vérifie l'état à chaque pas). Le temps de `main` a été mesuré
pendant que la suite de tests tournait, celui de la branche au calme : écarts de temps non
significatifs. Écarts expliqués :
- Relais et crue : mêmes nuits, à ceci près que l'appelé se tourne vers la voix (une rotation de plus,
  un retournement de moins quand il voyait déjà) ; une retrouvaille de plus au Relais (graine 3 :
  Aubin, hélé par Gorm, se tourne vers sa voix et le retrouve, au lieu de cesser de l'attendre) ;
- mine : Lucien, blessé, appelle à l'aide ; Rémy, son ami qui le protège, et Mathe reconnaissent sa
  voix et accourent par le but « voir » (Rémy 7 → 17 « va voir » sur les quatre nuits) : avant, le
  réflexe faisait rejoindre l'origine sans passer par ce but ni être compté ; la sécurité finit plus
  basse ;
- auberge : Hugues n'accourt plus qu'aux bruits qui lui parviennent à 3 crans (68 → 54 « va voir ») ;
  les nuits se décalent ensuite (moins d'appels par le nom, plus d'appels à l'aide d'Anselme, moins
  de minutes sans recours).

Limites :
- un personnage sans profil ne délibère pas : il retient le bruit, sans y réagir (la crypte) ;
- le seuil d'alerte est une constante par personnage, pas encore un état (fatigue, garde) ; il ne
  vaut que pour un bruit venu d'un autre lieu ;
- un appel fait reconnaître qui crie à qui connaît sa voix, sans retenir une voix inconnue ; un cri du
  joueur n'est reconnu que de qui connaît sa voix ;
- la nature d'un son d'objet tient à sa sonorité en trois paliers (`ouie.SONS`) ;
- l'appelé dans une autre salle se tourne vers le seuil par où la voix arrive, pas vers l'appelant ;
  rien de nouveau s'il regarde déjà par là (corrigé : branche `voix-suite`) ;
- dans la scène de test de la protection (Ilse à bout dans l'échoppe obscure), découper le temps
  change la minute d'une croyance (l'état du brasero éteint revu) sans en changer la valeur : défaut
  déjà présent sur `main`, hors de ce chantier.

## La suite des voix (branche `voix-suite`)

Quatre limites des branches `voix-inconnues` et `ouie-commune`, une même famille : ce que chacun retient
d'un nom entendu, et vers où se tourne qui est appelé.

**Retenir le nom de qui l'on reconnaît** (`voix.apprendre_nom`, `noms` de l'esprit, `voix.connait_nom`).
Avant, un PNJ qui voyait Corvus lui dire « C'est Corvus » le reconnaissait déjà (`se_nommer` : « connu »)
et rien n'enregistrait son nom ; et une voix crue sur parole (« une voix qui se dit Corvus »), une fois
reconnue comme celle de Corvus (`voix.connaitre`), était oubliée avec le nom qu'elle portait : la
croyance passait du ouï-dire au constat, plus rien ne disait qu'il savait son nom. Règle : un PNJ retient
le nom de qui il sait être lui, quand il l'entend se nommer (il le voit ou reconnaît sa voix), quand une
autre voix l'appelle ainsi (`nommer`, voir ci-dessous), ou quand la voix qui s'était dite ou qu'on avait
appelée ainsi se révèle la sienne. `connait_nom` lit ces noms retenus, et aussi le nom qu'une autre voix a
donné à une voix inconnue (`appelee`). Le joueur, lui, connaît le nom de qui il voit
(`paroles.identites`) : rien ne change pour lui.

**Une seule règle pour relier les voix d'un échange** (`voix.lier`, `voix.parole_saisie`, `voix.mots`,
`voix.nom_dit`). La règle du joueur (`ecoute.lier`, branche `voix-inconnues`) devient celle de tous : une
voix à qui une autre s'adresse en la nommant, entendue dans le même échange (`ECHANGE`, une minute, avant ou
après), est « une voix qu'on appelle Gorm » (`nommer`, `appelee`), un ouï-dire, jamais une identité ; rien
s'il connaît la vraie voix de Gorm, si elle s'est nommée ou s'il s'en méfie ; s'il sait déjà à qui est
cette voix (il la voit), un PNJ retient seulement le nom (`apprendre_nom`). Ce que chacun saisit des mots
suit aussi une règle commune (`voix.mots`) : tout le texte d'une voix qu'il voit ou reconnaît et qui ne
nomme que qui il connaît, sinon les mots dits tels qu'ils sont dits (ceux cités entre guillemets d'un
récit, ou la réplique même du joueur, `ouie.retentir(dits=…)`). Le joueur range ce qu'il entend dans
`data["bruits"]` ; un PNJ garde les paroles nettes qu'il vient de saisir le temps d'un échange
(`echange` de son esprit, `voix.retenir_echange`, au plus 8), et relie à chaque parole saisie
(`ouie.retentir`). Un PNJ qui a appris une voix « qu'on appelle Gorm » ne la reconnaît pas pour autant :
aucune croyance de lieu, aucune confiance ; il sait le nom (une réplique de sa voix peut le dire,
`narration.voix_inconnues`).

**L'appelé se tourne vers l'appelant** (`ouie._vers_la_voix`, `ouie._vers_qui_l_a_hele`). Hélé par son
nom, il se tourne vers l'appelant s'il le verrait ainsi (`voix._verrait_en_se_tournant` : la lumière le
montre, le noir non), dans sa salle ou au-delà d'un seuil, par le plan commun des salles ; sinon, comme
avant, vers le seuil par où la voix arrive. Qui attend d'être rejoint (`rejoint`, branche `parole-voix`)
et entend l'appelant approcher se tourne vers lui dès qu'il le verrait (« … se tourne vers Aubin, qui
l'avait hélé. »), au lieu d'attendre qu'il soit sur lui pour se retourner au bruit.

**Le genre d'une voix inconnue** (`voix.genre`). Le MJ reçoit d'une voix inconnue (`interlocuteurs.voix_<n>`
et `esprits_interlocuteurs.voix_<n>`) le genre où elle parle d'elle-même, « masculin » ou « féminin » : ce
que ses mots font entendre (« convaincu », « convaincue ») comme son timbre, sans nom, identifiant ni
traits. Ce n'est pas une fuite : l'auditeur l'entend dans la réplique même. Aucune consigne n'est ajoutée.

Vérifié (`tests/test_voix_suite.py`, état après rechargement et ce que lit le joueur ou reçoit le MJ) :
- noms : cas réel, Gorm voit Corvus dire « C'est Corvus » (parole du joueur, MJ simulé) : il retient son
  nom ; dans le noir, une demi-heure plus tard, la voix de Gorm, que Corvus ne connaît pas, peut dire
  « Corvus, approche. » sans refus du contrôle narratif (sur `main` : refusé) ; Ilse, qui n'a rien
  entendu, ne le sait pas. Même nature, une voix crue sur parole « Corvus » dans le noir, puis vue parler à
  la lumière : la voix devient connue et le nom reste. Ilse voit Corvus répondre « Ici ! » à une voix qui
  l'appelle « Corvus ? » : elle sait son nom ;
- relier : cas réel, Ilse dans le noir entend une voix appeler « Corvus ? » puis une autre voix dire
  « Gorm, je suis là. » : « la voix qu'on appelle Corvus » et « la voix qu'on appelle Gorm », sans les
  reconnaître ; même nature entre PNJ, une voix parle (Gorm à Aubin), puis l'autre la hèle « Gorm ? » :
  Ilse et Corvus, au même endroit, l'apprennent pareillement (« une voix qu'on appelle Gorm ») ; qui
  connaît la vraie voix de Gorm n'apprend rien d'elle ;
- se tourner : cas réel, Gorm dans la conduite, près du passage mais à côté de lui, hélé par Corvus au
  refuge éclairé, hors de l'axe du passage : il se tourne vers lui (sud-est) et le voit, connaît sa voix
  (sur `main` : il avait déjà le seuil sous les yeux, ne se tournait pas et ne le voyait pas) ; un appelant
  qu'il ne verrait pas : rien de plus. Même nature, Gorm attend Aubin qui l'avait hélé et le voit venir
  par le passage : il se tourne vers lui avant qu'Aubin n'entre (sur `main` : il se retournait au bruit
  une fois Aubin dans la conduite) ; le même laps, d'un bloc ou découpé et rechargé, donne le même monde ;
- genre : la voix de Gorm « masculin », celle de Brune « féminin », pour le MJ, sans leur nom ni leur
  identifiant.

`planification.VERIFIER` sur une nuit de chaque scénario (graine 1985, 8 h) : aucune reprise périmée,
aucune usurpation.

Bancs 8 h, `main` 8c108c3 puis la branche, l'un après l'autre, mêmes mesures ajoutées des deux côtés
(Relais 8 graines `--joueur chambre_cloche`, auberge 4 graines `--joueur dortoir`) :

| | Relais | Auberge |
|---|---|---|
| appels / réponses / retrouvailles | 1,25 / 1,13 / 1,13 → idem | 3,25 / 2,75 / 2,25 → idem |
| tournés vers la voix / vers qui l'avait hélé (nouveau) | 0,88 / 0 → 0,88 / 0,25 | 1,5 / 0 → 1,5 / 0,25 |
| voix connues gagnées / voix qui se disent quelqu'un | 0 / 0 → idem | 12,25 / 1,5 → idem |
| voix « qu'on appelle … » (nouveau pour les PNJ) | 0 → 0 | 0 → 1,75 |
| noms retenus (nouveau) | 0 → 0 | 0 → 0 |
| échanges / paroles surprises | 15,75 / 25,5 → idem | 97,75 / 222,75 → idem |
| sans recours / en attente | 53,75 / 58,1 → idem | 60 / 297,5 → idem |
| retournements | 153 → 153 | 127,5 → 127,25 |
| usurpations, violations | 0 → 0 | 0 → 0 |

Toutes les autres mesures sont identiques, graine par graine. Les nuits ne changent que par l'orientation
de qui attend : au Relais (graines 2024 et 3) et à l'auberge (graine 42 : Odile se tourne vers Anselme
qui l'avait hélé, au lieu de se retourner au bruit quand il arrive). À l'auberge, Lucien et Joss
apprennent ainsi des voix (« la voix qu'on appelle Mathurine ») en entendant Odile, qu'ils
reconnaissent, demander du bois à qui ne leur est qu'une voix. Aucun nom retenu au banc : le joueur y
reste muet et les PNJ savent déjà le nom des autres. Temps d'une nuit (4 graines, l'un après l'autre) :
Relais 12,4 → 11,2 s, auberge 36,6 → 37,6 s.

Limites :
- Une réponse à son nom (« Ici ! ») vaut se nommer pour le PNJ qui la surprend (« la voix qui se dit
  Anselme », branche `voix`, qui la situe), alors que le joueur qui la surprend apprend « la voix qu'on
  appelle Anselme » (branche `voix-inconnues` : il ne se dit que si ses mots disent son nom). L'écart
  précède ce chantier ; il est gardé (le PNJ s'en sert pour situer qui il cherche).
- Une voix « qu'on appelle Gorm » ne situe pas Gorm pour un PNJ et ne lui vaut aucune confiance : c'est le
  nom seul. Les répliques que Luna prête aux PNJ (`paroles_pnj`) et la réponse d'un PNJ à une parole du
  joueur ne retentissent pas pour les autres PNJ : elles ne relient pas les voix.
- Un récit d'échange sans guillemets (« Aubin demande une part des vivres à Gorm ») nomme le destinataire
  pour qui sait qui parle et connaît ces noms : la même règle que pour le joueur, qui suppose qu'on
  l'appelle par son nom.
- Se tourner vers l'appelant se décide quand on l'entend (son cri, ses pas) ; qui attend se tourne vers lui
  au bruit de ses pas, pas à chaque pas qu'il fait lui-même. Le passage d'une salle à l'autre est vu par le
  plan commun : par un seuil d'une case, l'appelant visible est presque toujours dans la direction du seuil.
- Le genre de la voix est celui du personnage (`genre`) : ni timbre, ni âge (un enfant parle « au
  masculin » comme un homme). Rien ne vérifie que Luna l'emploie : aucune partie avec Luna n'a été jouée
  (aucune saisie du joueur ne change).

## Témoins par l'ouïe, le bruit de sa salle, l'examen vain (branche `ouie-temoins`)

Trois défauts de l'audit des nuits (`docs/audit-nuits.md`, A1, A2 et B2), une même famille : ce que
l'ouïe fait savoir, et ce qu'on fait d'un bruit quand la vue ne suffit pas.

**Un bruit se situe à une case** (`ouie._bruit_inconnu`, `ouie.source`). Avant, le bruit de sa propre
salle ne l'envoyait nulle part (`deliberation.bruit_a_voir` et `alarme` écartaient la salle où il se
tient) : environ 40 % des bruits inconnus retenus. Gorm, gardien, à sept cases de Brune qui forçait la
réserve dans la pénombre du refuge (on n'y voit qu'à trois cases), l'entendait trois fois et restait
(Relais, graine 7, minutes 28 à 31). Règle : entendu de la salle même, le bruit est retenu avec la case
d'où il vient (le souvenir `bruit` porte `case` ; le MJ n'en reçoit que le lieu, `esprits.dernier_son`).
Il s'examine selon le devoir de garde et le courage, comme celui d'un autre lieu, alarme comprise.
Aller voir (`planification.voir`) mène alors à portée de vue de cette case : l'étape `inspecter` porte
`vers` ; il s'en approche pas à pas jusqu'à la voir en se tournant (la lumière qui l'éclaire, rien qui
s'interpose), ou, si rien ne l'éclaire, jusqu'au contact (`pnj._a_portee_de_vue`, `CONTACT`) ; sans
chemin, il regarde de là où il est. Un bruit d'un autre lieu, qu'il ne situe qu'à la salle, se parcourt
des yeux depuis son centre, comme avant (« va voir de près » dans la chronique pour le premier, mesure
`alles_voir_de_pres`).

**Témoin par l'ouïe** (`pnj._temoins_a_l_oreille`, `ouie.objet_situe`). Avant, le témoin ne comptait
que sur la vue (`esprits.percoit`) : à l'auberge, Lucien mangeait les provisions d'Anselme et forçait son
coffre à une diagonale de lui, dans le noir (graine 1, minutes 313 à 429) ; à la mine, Odon forçait le
coffre de la paie à une case de Bram (graine 500, minutes 456 à 461) ; personne n'en savait rien. Règle :
le registre des gestes en cours porte le bruit de chaque geste (`nature`, celle de `ouie.nature`, feutrée
s'il est fait en douce) ; tant que le geste dure, qui l'entend (`ouie.entend` : distance, passages, son
seuil), sans en voir l'auteur, dans la salle même, et croit tout près de là l'objet en cause ou ce qui le
contient (un bien fixe qu'il connaît est à sa place) sait qu'on y touche. Il n'identifie l'auteur que
s'il le reconnaît : il le croit là d'où vient le bruit (`ouie._crus_la` : vu ou entendu depuis peu, ses
pas ou sa voix). Identifié, il en est témoin comme d'un geste vu (souvenir `vu_agir` marqué `par`
« ouie », sans le lieu où l'objet va) : méfiance de source `entendu` (qui ne remplace pas une méfiance
vue), inquiétude, la victime pressée par ses biens, le protecteur qui ira prévenir ; sa nouvelle se
répète comme de seconde main (rang 1, `social.nouvelles`). Non identifié, il sait seulement que quelqu'un
touche à ce bien (`entendu_agir`, une fois tant que ça dure) : inquiétude, la victime pressée par ses
biens ; personne n'est accusé, rien ne se répète ; le bruit, situé, reste à aller voir. Registre :
`entendus` à côté de `temoins` ; le rejeu les note ; chronique « Bram entend que quelqu'un a tenté de
crocheter la serrure du coffre de la paie. », « Anselme entend que Lucien … ».

**L'auteur compte ceux qu'il croit à portée d'oreille** (`pnj.oreilles_crues`). Corollaire : sans lui,
Lucien forçait plus d'une heure le coffre d'Anselme, à côté de lui dans le noir, qui l'entendait et le
reconnaissait. Un geste qu'il veut sans témoin attend aussi que s'éloignent ceux qu'il croit, depuis peu,
dans sa salle et assez près pour l'entendre (la distance à la case où il les croit ; sans case, la
salle) ; à bout (`pnj.desespere`), il agit quand même, comme sous les yeux d'un témoin.

**Être allé voir règle le bruit** (`ouie.parcouru`, `ouie.couvert`). L'audit supposait que dans le noir,
aller voir ne réglait pas le bruit (`ouie.resolu` exige d'avoir vu quelqu'un) ; relu, `parcouru` effaçait
déjà ce qu'il attendait du lieu. Le va-et-vient venait de ce qu'aucun examen ne valait pour la suite :
l'appel répété de Lucien, dans le bureau noir, renvoyait Mathe à chaque fois (mine, graine 18, minutes 455
à 560 ; l'appel répété lui-même est le défaut B1, hors de ce chantier) ; dans une salle noire où l'on va
et vient, chaque pas d'un inconnu en était un nouveau. Règle : allé voir sans rien trouver, ou sans rien
pouvoir voir, il retient l'examen (souvenir `examen` : le lieu, la case s'il l'a situé, le plus fort de
ce qu'il attendait, qui appelait s'il avait reconnu la voix). Le même bruit, ou un moindre, venu de ce
lieu ne l'y renvoie plus (`couvert` : ni retenu, ni chroniqué ; un appel inquiète encore) tant qu'il se
répète à moins de 30 minutes (`RECENT`) ; seul un bruit nouveau le relance : plus fort, d'une autre voix
reconnue, ou qu'il situe mieux (il avait examiné la salle depuis son centre, il l'entend maintenant d'une
case). Qui a vu quelqu'un là s'explique le bruit : rien à retenir.

**Correctif commun révélé** (`moteur._terminer_etape`) : ce que les PNJ voient du geste du joueur avant
de vivre la période est daté du début du geste. Daté de sa fin, la minute d'une croyance dépendait du
découpage des actions du joueur (la réserve revue par Brune à la minute 4 d'un bloc, 5 en rotations) ;
c'est le défaut « déjà présent sur `main` » noté plus haut (scène de la protection).

Vérifié après rechargement (`tests/test_ouie_temoins.py`, 12 tests) : Gorm, à sept cases dans la
pénombre, situe le fracas, s'approche, voit Brune à l'œuvre et s'en méfie (cas réel) ; Aubin, courageux,
fait de même sans rien à garder ; le souvenir porte la case, que le MJ ne reçoit pas ; dans le bureau noir,
Bram entend forcer le coffre sans savoir qui (aucune accusation, aucune nouvelle), va au contact, n'y voit
rien et le bruit est réglé, puis Odon, qui les sait à portée d'oreille quand Josse arrive, n'insiste pas
(cas réel) ; Bram qui croit Odon là le reconnaît (méfiance `entendu`, nouvelle de rang 1) ; Anselme
entend Lucien forcer son coffre et le reconnaît (cas réel) ; qui voit faire reste témoin par la vue ;
Brune, qui sait Gorm à portée d'oreille, attend, et force sinon ; un examen vain couvre les mêmes bruits
mais pas un appel, ni une voix reconnue ; l'appel répété du bureau ne renvoie plus Mathe, sauf entendu de
la salle même (cas réel). Même laps d'un bloc ou en rotations rechargées : même monde (Relais et mine).

Tests d'autres branches changés, et pourquoi : `test_ouie` (Aubin, courageux, va voir le fracas lui
aussi : ses pas font un autre bruit, d'un autre lieu ; seul le bruit du refuge doit être réglé),
`test_constater_rumeurs` (Odile, au grenier noir, va voir de près les pas de Mireille qu'elle ne sait à qui
prêter ; Mireille finit par la voir ailleurs : on vérifie seulement qu'elle ne la croit pas au grenier
sans réponse), `test_dynamique_besoins` (Anselme entend Lucien forcer son coffre et la nuit tourne
autrement : on vérifie qu'il ne va et ne vient plus, la lanterne n'est plus forcément à lui), `test_besoins`
(deux scènes où Brune force la réserve quand Gorm, ou le joueur, qu'elle a vu, se tient dans l'ombre :
elle les sait à portée d'oreille, il faut qu'elle soit à bout de faim pour forcer).

Bancs : `tools/audit_nuits.py`, 32 nuits de 12 h (4 scénarios × graines 7 1 500 18 1985 42 2024 3,
départ tiré, rejeu), `main` 0489fea puis la branche (moyennes par nuit, `main` → branche) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| alternances « aller voir » / autre but (relevés de 5 min) | 3,1 → 0,9 | 7,8 → 4,4 | 6,5 → 5,0 | 1,9 → 1,0 |
| retours voir le même lieu à moins de 30 min | 7,6 → 1,1 | 63 → 22,4 | 57,6 → 16 | 4,6 → 1,9 |
| allés voir (dont de près) | 25,8 → 16,6 (3,3) | 105,6 → 65,1 (31,4) | 128,9 → 90 (39,1) | 27 → 21,5 (5,5) |
| gestes illicites, un présent, ni vus ni entendus | 1,3 → 0 | 4,4 → 0,1 | 7 → 0,5 | 0,5 → 0,1 |
| gestes entendus sans être vus | 0 → 0 | 0 → 3,8 | 0 → 11,6 | 0 → 0 |
| témoins par l'ouïe, auteur reconnu / inconnu | 1,6 / 0,1 | 1,6 / 1,3 | 7,6 / 2,3 | 0 / 0 |
| vols vus | 1,5 → 1,4 | 0,3 → 0,1 | 0,1 → 0 | 0,4 → 0,5 |
| crochetages manqués / réussis | 6,5 / 1,3 → 13,6 / 1,3 | 3,1 / 0,8 → 3 / 0,6 | 7,9 / 0,8 → 19,9 / 1 | 1,1 / 0,5 → 0,9 / 0,4 |
| méfiances en fin de nuit | 2,8 → 2,6 | 4,5 → 4,5 | 10,6 → 9,9 | 0,6 → 1,4 |
| appels à l'aide | 0,8 → 1,3 | 38,1 → 39,1 | 13,9 → 10,1 | 12 → 12,1 |
| bruits inconnus retenus | 96 → 87 | 225 → 155 | 310 → 249 | 126 → 106 |
| minutes urgentes sans recours / en attente | 119 / 237 → 125 / 201 | 63 / 1264 → 63 / 1304 | 61 / 950 → 154 / 939 | 21 / 506 → 48 / 457 |

Aucun plantage, aucune violation de `Monde.verifier` (contrôlé à chaque pas), aucune usurpation. Cas
réels dans ces nuits : mine 500, Odon force le coffre de la paie de 456 à 466 et Bram et Josse
l'entendent sans le reconnaître ; auberge 1, Anselme entend Lucien forcer son coffre (262 à 265) ; mine 18,
Mathe va voir 5 fois entre 440 et 570 au lieu de 12 (7 changements de but au lieu de 17) ; Relais 7, la
nuit a divergé : Brune, qui sait Gorm à portée d'oreille, ne force la réserve qu'à la minute 93. Écarts
expliqués : les voleurs attendent que s'éloignent ceux qu'ils croient à portée d'oreille, donc forcent
plus souvent dans le noir ou à bout de faim, où le jet est moins bon (crochetages manqués doublés au
Relais et à l'auberge, réussis égaux) ; à l'auberge, Lucien guette son occasion près d'Anselme qui garde
ses biens, renonce au bout de 30 minutes et reste sans rien faire (`REPIT`), d'où des minutes sans
recours ; moins de bruits inconnus retenus (un examen vain les couvre). Le compte « témoins par l'ouïe »
est celui de la chronique (la mémoire de 40 souvenirs n'en garde pas tout en fin de nuit).
## Corrections de la parole (branche `parole-corrections`)

Les défauts de parole du [banc Luna du soir](banc-luna-soir.md), corrigés par des règles communes
(`tests/test_parole_corrections.py`, cas réels des bancs ciblés et un cas de même nature, état après
rechargement et ce que lit le joueur).

- **Un vocatif où qu'il soit** (`paroles._vocatifs`, `_interpeller`) : un nom détaché par une virgule
  désigne le destinataire en tête, au milieu ou en fin de phrase (« as-tu de quoi manger, Ilse ? »,
  « dis-moi, Ilse, … », dans les mots après « je dis : » comme entre guillemets), hors des citations ;
  après « moi, » c'est celui qui parle qui se nomme (« c'est moi, Brune »), pas un vocatif. Cas réel :
  la question allait à Aubin, en face, et la réplique était réécrite « …, Aubin ? ».
- **Un nom que Corvus ne connaît pas** (`analyser` → `inconnu`, `destinataires`) : un vocatif ou un
  « je dis à X » qui nomme un personnage du monde que Corvus ne connaît pas donne « Tu ne connais
  personne du nom de X ici », sans appel au MJ pour une parole sans conteste, jamais un autre
  destinataire. Un absent connu garde « Tu ne vois pas X d'ici ».
- **Nommer la voix par le nom qu'elle porte** (`voix.porteur_du_nom`) : quand Corvus ne sait là
  quelqu'un que par une voix qui s'est dite X (ou qu'on a appelée X devant lui), nommer X, c'est
  s'adresser à cette voix, pour une parole comme pour un don (`dialogues.verifier_don`). Le nom n'est
  pas une identité : la voix reste « une voix qui se dit X » (une imposture comprise), et un don hors
  de portée dit « Approche-toi d'une voix qui se dit Ilse », sans son vrai nom (`proximite.exiger`).
  Un absent qu'il ne perçoit d'aucune façon : « Tu ne vois pas X d'ici : approche-toi pour le lui
  donner » (au lieu de « … n'est pas là pour le recevoir », que Corvus ne peut pas savoir). Cette règle
  remplace celle de la branche `voix` (« il ne peut s'adresser à Brune qu'il ne sait pas là »).
- **Répondre à la cantonade** (`paroles.repondants`, `appelle_reponse`, `entendre_repondant`) : une
  parole qui ne s'adresse à personne en particulier (à la cantonade, ou à tous) et qui appelle une
  réponse (des mots qui portent un « ? », ou un contenu `qui`, `ressource`, `demande`, `reclamer`,
  `passage`) est entendue de qui en saisit les mots sans que Corvus le sache là ; chacun décide de
  répondre par la règle de celui qu'on hèle (`voix.repond` : pas à une voix dont il se méfie, la même
  fonction pour `pnj.repondre`), et ce qu'il répond suit la règle d'un destinataire (accueil d'une voix
  inconnue, « Qui va là ? », valeurs). Corvus entend sa voix (`voix.entendre`, `data["entendus"]`) : il
  devient un interlocuteur, voix inconnue s'il ne la reconnaît pas, et la suite de l'échange va à lui ;
  sa réponse retentit (sans mots pour les autres). Une parole qui n'appelle pas de réponse reste
  seulement retenue. Seul dans le noir, une question (« il y a quelqu'un ? ») offre le mode parole au MJ
  (`paroles.contexte`) ; une parole sans destinataire nommé que nul présent ne saisit est dite à la
  cantonade même sans guillemets ni verbe de parole. Cas réel : « Qui est là ? », Ilse à trois cases
  dans le Palier noir, se nomme ; la question suivante va à « une voix qui se dit Ilse ».
- **Ce que reçoivent le MJ et l'auditeur** : `conversation_validee.repondent` (qui répond : les
  destinataires et ceux qui ont choisi de répondre à la cantonade) et `issue`, la phrase du moteur
  (« Tu as dit à voix haute, à la cantonade : « … ». Une voix inconnue (voix_1) t'a entendu et te
  répond… », ou « Aucune réponse ne te parvient. »), ajoutée aux attestations ; seuls ceux de
  `repondent` peuvent répondre (`narration.destinataires_parole`). Les objets que reçoit le MJ portent
  `a_portee_de_main` (au lieu de `a_portee`, lu comme une portée de voix) et, pour un personnage,
  `a_portee_de_voix` (`pnj.peuvent_se_parler`). Les consignes de l'auditeur disent ce que signifient
  ces champs : la réplique de qui répond est une parole permise ; le dire muet est contradictoire.
- **Un refus de forme n'est pas une impossibilité** (`refus.RefusDeForme`) : un champ, une borne, la
  mauvaise action (l'arbitrage sommaire hors de ses bornes, héler sans nom, « impossible » sans
  réexamen) revient au MJ avec son `attendu`, avec une correction à part de la correction ordinaire
  (trois propositions au plus), et ne s'affiche jamais : à une question de faisabilité, le joueur lit
  la raison du monde, sinon l'explication contrôlée du MJ.
- **Sorties connues** (`rendu.regarder`, `mj._echanger`) : en cases, « Sorties que tu connais : … »,
  « aucune pour l'instant » ; le MJ reçoit `salle.sorties_connues`. N'en connaître aucune n'atteste pas
  qu'il n'y en a pas (« aucun passage directement praticable » reste hors cases, où toutes sont
  listées).
- **Se dire quelqu'un** (`paroles.nom_dans`, `verifier_nom`, `SE_NOMMER` en un seul endroit) : le nom que
  Corvus se donne est celui que disent ses mots (« C'est moi, Brune », « Je suis Corvus ») ; un contenu
  `nom` qui en dit un autre est refusé au MJ (une cause, `attendu`), un nom non typé est ajouté par le
  moteur. Un nom se prononce sans connaître qui le porte (`_nom_dit` cherche tout personnage). Cas
  réel : Ilse, qui connaît la voix de Brune, démasque l'imposture et se méfie de la voix ; le récit
  « Brune ? Je ne te reconnais pas » n'est plus contredit par les faits.
- Faibles : « je réponds » sans mots ni destinataire n'est plus une parole sans conteste ; « je »
  hors des répliques est une voix d'auteur (`narration.AUTEUR`).

Luna (2 passes, `main` 0489fea puis la branche, l'un après l'autre ; relais, crypte, atelier, échanges,
comptes, ressources et les trois bancs du soir ; serveur surchargé pendant le banc de `main` : 9 tours
de référence en panne, écartés des moyennes, aucun pour la branche) :

| | `main` | branche |
|---|---|---|
| 4 bancs de référence, appels / tour MJ | 2,99 (34 tours) | 3,24 (38 tours) |
| secondes / tour MJ | 14,2 | 15,0 |
| replis / relances narratives / tours avec refus / refus | 0 / 3,5 / 6,0 / 8,5 | 1,0 / 6,0 / 7,0 / 11,0 |
| soir-noir, appels / tour | 4,20 | 3,30 |
| soir-voix / soir-appel, appels / tour | 3,50 / 2,92 | 3,00 / 2,83 |

Les refus en plus sont surtout au Relais (3,5 → 8) : la correction à part d'un refus de forme ajoute une
proposition aux questions de faisabilité (la poutre). Un repli de plus vient d'un « Je ne peux pas
dire… » refusé comme voix d'auteur. Saisies du rapport, ce qu'affiche le jeu (avant → après, 2 passes) :
« as-tu de quoi manger, Ilse ? » « Tu dis à Aubin… » 2/2 → « Tu dis à Ilse : « as-tu de quoi manger,
Ilse ? » », Ilse répond, 2/2 ; « « Qui est là ? » » dans le noir, sans réponse 2/2 → la voix d'Ilse se
nomme 2/2, et les questions suivantes vont à « une voix qui se dit Ilse » ; « il y a quelqu'un ? »,
« Dis qui tu appelles par son nom » ou « aucun passage praticable » → Ilse répond 1/2 (l'autre fois
Luna répond en dialogue, sans parole) ; « « C'est moi, Brune. » » typé « Corvus se nomme » et « te
croit sur parole » → imposture démasquée, « Tu n'es pas Brune » 4/4 ; « est-ce que je pourrais passer
sous la poutre effondrée ? » « La difficulté de ce geste sort des limites… » → « Approche-toi de la
poutre effondrée… » ou l'explication du MJ ; « je donne le briquet à Ilse » « Ilse, meunière évacuée
n'est pas là… » → « Tu ne vois pas Ilse d'ici : approche-toi pour le lui donner », et à la voix qui se
dit Ilse « Approche-toi d'une voix qui se dit Ilse… » ; « aucun passage directement praticable » affiché
1 → 0. Le cas réel du nom inconnu (comptes) n'est pas revenu : Brune était connue dans les quatre passes
(test sans Luna). Restent : « je réponds » sans appel, que Luna fait encore parole avec des mots à elle ;
« est-ce que quelqu'un a du bois ? » va à celui d'en face.
Ces deux restes sont repris par `codex-luna-noms` (section « Parole après les noms »).

Limites : le vocatif est reconnu par sa ponctuation (une virgule) ; un nom inconnu n'est refusé que
s'il est celui d'un personnage du monde (un nom qui ne nomme personne, « Bertrand, … », va au MJ comme
avant), ce qui laisse deviner qu'un tel personnage existe ; un nom dit qui ne nomme personne du monde
n'est pas enregistré comme imposture ; répondre à la cantonade se décide sur la seule méfiance (pas de
voleur qui se tait pour rester caché) ; « appelle une réponse » se lit à la ponctuation et au contenu
typé ; le silence d'un destinataire n'est arrêté que par l'auditeur, que les champs explicites
guident (pas de contrôle déterministe) ; la réponse d'un PNJ à la cantonade retentit sans ses mots
pour les autres PNJ.

## Ce qu'on a déjà dit (branche `boucles-pnj`)

Boucle N4 de la [revérification](reverification.md) : à l'auberge (graines 3, 500, 123), Hugues redisait
jusqu'à 26 fois à Anselme que son ballot de soie était dans la chambre au poêle, où Anselme l'avait
posé lui-même et se tenait. Variante de lieu de la boucle B3 de l'audit (« Lucien est peu fiable »
redit), corrigée par `deliberation-evenements` pour l'auteur seulement : `_a_dire` tenait un lieu pour
dit s'il l'avait été depuis la minute de sa croyance de lieu, et cette minute se renouvelle à chaque
regard sur le ballot. Règle (`deliberation._a_dire`, `_deja_dit`) : on ne dit à quelqu'un que ce qu'on
croit qu'il ignore. Un fait dit l'est jusqu'à ce que sa valeur change : la dernière fois qu'il lui a
dit où est ce bien, c'était ce lieu-là (le souvenir `dit` porte désormais la valeur, `echanges`), quelle
que soit la date de ce qu'il en croit. Et il ne lui apprend pas où est un bien qu'il croit sous ses
yeux : il le croit dans la même salle que lui (il l'y a posé, ou l'y voit). Qu'il n'est pas fiable reste
dit une fois pour toutes.

Cas vérifiés après rechargement (`tests/test_boucles_pnj.py`) : le cas réel (Anselme dans la chambre au
poêle avec son ballot, Hugues qui les voit chaque minute : « Lucien est peu fiable » une fois, le lieu
jamais ; sur `main`, six fois en vingt minutes) ; même nature (Anselme au dortoir, le ballot à l'étable :
dit une fois ; revu à l'étable, rien ; vu au grenier, dit de nouveau).

Limites : le souvenir `dit` peut sortir de la mémoire bornée (`MEMOIRE_MAX`) : le lieu se redit alors
une fois ; « sous ses yeux » se juge à la salle où il croit l'un et l'autre, pas à ce que la victime
voit vraiment (dans le noir, ou le bien dans un contenant fermé, elle peut l'ignorer).

## Le bruit du crochetage selon l'adresse (branche `crochetage-surenchere`)

Décision du 2026-10-22 : un crochetage réussi par quelqu'un d'habile fait peu de bruit ; un échec, un
acharnement ou un forcement font du fracas. Avant, `crocheter` était toujours bruyant (`ouie.NATURES`) :
au Relais, la réserve forcée s'entendait de l'échoppe même quand la serrure cédait du premier coup, et
le fracas « même sans témoin » faisait se retourner Ilse, de dos (branche `rejeu-enrichi`).

**Règle commune au joueur et aux PNJ** (`ouie.nature_crochetage`) : le bruit d'un crochetage tient à son
jet (d20 + DEX contre `pnj.seuil_crochetage`, 14 en pleine lumière, 4 de plus par niveau qui manque ;
le joueur a désormais le même seuil). Réussi, la serrure cède sous la main : un geste ordinaire (3 crans),
feutré s'il est fait en douce (PNJ `sans_temoin`, joueur `discret`). Manqué, il s'acharne sur la serrure :
un fracas (7 crans), comme forcer (`frapper`), qui le reste. L'adresse (la DEX modulée par le corps, la
lumière qu'il a sur sa case) fait la chance de réussir, donc la part des essais discrets. Le jet se fait
avant que le geste retentisse (`pnj._executer`, `pnj._crocheter` rend la marge), et le registre des gestes
en cours porte ce bruit tant qu'il dure (témoins par l'ouïe). Le joueur : la marge de son jet
(`Plan.marge`) fait la nature de son geste (`Moteur._terminer_etape`). Un crochetage dont on ne connaît
pas le jet (la simulation d'une manœuvre avant de la tenter) reste un fracas. La chronique dit « crochète
la serrure de … sans forcer. » pour un crochetage réussi, « s'acharne sur la serrure de … » sinon.
`AISANCE` (0) est la marge qu'il faut au jet pour que la serrure cède sans fracas : toute réussite.

**Le voleur qui veut agir sans être entendu** (`pnj.agir`, `pnj.oreilles_crues`) attend que s'éloignent
ceux qu'il croit à portée d'oreille du bruit qu'il attend de son geste : pour un crochetage, celui que lui
promet son adresse à la lumière qu'il a devant la serrure (`planification.bruit_crochetage`, par la même
chance que le planificateur, `chance_crochetage`) : un geste feutré s'il a au moins une chance sur deux
(`HABILE`) de réussir, sinon un fracas. Brune (DEX 15, diminuée par la faim) attend encore un fracas ;
plus adroite, elle se saurait capable d'un crochetage feutré qu'on n'entend qu'au contact.

Vérifié après rechargement (`tests/test_crochetage_surenchere.py`) : Brune réussit en douce dans le dos de
Gorm (cas réel) : il n'entend rien, ne se retourne pas, n'en est pas témoin ; manqué, un fracas qui le
fait se retourner et le rend témoin ; réussi sans se cacher, Gorm qui la sait là lui prête un geste
ordinaire sans se retourner, mais en est témoin par l'oreille (peu de bruit n'est pas aucun) ; le joueur
à l'échoppe n'entend pas un crochetage réussi, entend le grand bruit d'un échec ; Corvus qui crochète la
réserve : réussi, Gorm reste à l'échoppe, manqué, il vient voir ; Brune maladroite guette tant qu'elle
croit Ilse à trois cases, habile (DEX 20), elle agit et la serrure cède sans bruit. Tests changés :
`test_social` (Brune, à bout de faim, réussit en douce sous les yeux d'Ilse : Gorm, à l'échoppe, ne
l'entend plus) ; les textes de `test_besoins`, `test_social`, `test_planif_defauts` (« sans forcer »).

Bancs 8 h, départ tiré, `main` d5d4bee puis la branche, l'un après l'autre, sous un verrou commun (Relais
8 graines, mine, auberge, crue 4), par nuit, `main` → branche : crochetages (essais / réussis / réussis
sans forcer) Relais 3,4 / 0,5 / 0 → 3,4 / 0,5 / 0,5, mine 24,8 / 6,5 / 0 → 25,3 / 7 / 7, auberge
13,3 / 0,25 / 0 → 6,5 / 0,75 / 0,75, crue 0,75 / 0,5 / 0 → 0,75 / 0,5 / 0,5 ; crochetages entendus sans
être vus (témoin par l'ouïe) 0,5 → 0,5, 0,75 → 0,75, 0,75 → 1, 0,5 → 0 ; témoins par l'ouïe de tout geste
(auteur reconnu + bien touché) Relais 0,6 → 0,6, mine 0,75 → 0,75, auberge 1 → 1,75, crue 0,5 → 0 ; vols
vus égaux à 0,25 près ; aucune usurpation ni violation. Au Relais, les mesures sont les mêmes (seule
l'offre de tâche la plus haute d'une nuit change, par la surenchère) : quatre crochetages réussis en huit
nuits, sans personne à portée d'oreille. Les
voleurs des scénarios (DEX 15, et la faim qui la diminue) ne se savent jamais habiles : ils attendent
toujours un fracas, et guettent comme avant ; seul le bruit d'une réussite change. Audit de 12 h
(`tools/audit_nuits.py`, 4 scénarios × 4 graines, `main` → branche) : réussis sans forcer 0 → 1,25 / 7,25
/ 1 / 1 par nuit, entendus 0,75 / 0,75 / 0,75 / 1 → 0,75 / 0,5 / 1 / 0,25 ; aucun plantage ni usurpation.

## Les noms entendus et les apparences (branche `codex-noms`)

La décision du 22 octobre remplace les anciennes équivalences « vu = nom connu » et
« voix connue = nom connu » décrites dans les jalons historiques ci-dessus. Trois mémoires
restent distinctes : apparence reconnue (`personnages_vus`, portraits), voix reconnue
(`voix_connues` / `voix`), noms entendus et reliés (`noms_connus` du joueur, `noms` des PNJ).
Une croyance issue de la vue ne donne aucun nom. Un savoir déclaré par le scénario ou une
parole effectivement saisie qui permet de relier le nom à la personne le donne.

`donjon/noms.py` centralise cet apprentissage et la projection publique. Une personne visible
sans nom porte une désignation courte issue de son portrait, ou du genre si aucun trait ne
peut être extrait, conservée dans `personnes`. Les doublons reçoivent un numéro stable. Le MJ
la vise par `personne_<n>`, ses éléments rattachés par `element_<n>` : aucune identité interne
n'est livrée par le portrait, les pièces du corps ou les souvenirs. Le moteur décode ces
références puis applique ses contrôles ordinaires de perception et de portée. Un pseudonyme
deviné ne donne aucun accès. La saisie accepte la désignation (« je dis à l'homme trapu… »,
« je donne le briquet à l'homme trapu »). Carte, terminal et page partagent cette projection.

Le contrôle déterministe de `narration.voix_inconnues` refuse un nom inconnu dans le récit,
y compris si un autre fait ou le joueur l'a mentionné. Une réplique ne nomme que qui son
locuteur connaît. Les `noms_pour_repliques` du contexte sont des noms que ce locuteur peut
prononcer, sans identifiants ni position ; ils ne fondent aucune affirmation du narrateur.
Le paquet privé de chaque locuteur distingue `nom_du_locuteur`, ajouté par le MJ après
la projection publique : connaître des noms de tiers ne permettait pas au personnage de
savoir lequel était le sien. Ce nom privé ne fonde toujours aucun nom dans le récit.
Le paquet nominal privé entier (nom propre et noms de tiers prononçables) ne figure que dans
la narration après validation du moteur. L'interprétation mécanique ne reçoit que les noms
publics du joueur, sans pouvoir reconstruire les identités par différence entre listes privées.
Une présentation explicite du locuteur, ou le nom d'un destinataire appelé et identifié,
relie le nom avant la sauvegarde et l'affichage. Une simple mention de tiers ne désigne pas
lequel des corps visibles porte ce nom. Les mots enregistrés restent cités ; les guillemets d'un portrait ou d'une
description ne bénéficient pas de cette provenance. Se donner le nom d'un tiers ne présente
pas le corps de ce tiers.

Le contrôle des citations garde leur portée : la citation entière d'une parole auditée est
exemptée dans son passage exact seulement, et doit y être unique. Une copie dans un autre
segment ne transporte pas cette autorisation. Une parole historique effectivement entendue
peut être restituée seule, entière, mais n'autorise aucune nouvelle étiquette narrative de
personne ni description persistante. Les mots exacts de Corvus restent ainsi disponibles,
sans faire de tout guillemet une parole ni d'un fragment une preuve de provenance. Les voies
de consigne et de dernier recours appliquent le même garde avant affichage.

L'audit d'une réplique porte `presentation` : le nom littéral par lequel le locuteur se
présente, y compris dans une réponse comme « Gorm. », ou une chaîne vide. Le moteur vérifie
sa présence dans la citation et l'attache à la signature de cette voix avant l'affichage.
Les faits persistants de type `parole` utilisent le même contrat. Le classement d'une
présentation reste sémantique ; le lien de voix et l'absence d'identification du corps d'un
tiers sont déterministes. Un nom seulement revendiqué ou appelé reste une appellation de
voix, distincte du nom connu d'un corps. Une voix reconnue dont le corps n'a jamais été vu
reste « une voix reconnue », sans portrait.

Les scénarios déclarent `connait_noms` pour les liens antérieurs des PNJ et
`scenario.noms_connus` pour ce que l'introduction a effectivement donné au joueur. Le Relais
commence avec un homme trapu, sans nom préchargé. À l'auberge, l'introduction nomme Odile.
Les scènes de banc peuvent déclarer leurs présentations antérieures par `noms_connus`,
séparément des objets simplement `connus`.

Les tests de `tests/test_noms.py` suivent le cas du Relais (voir Gorm ; le questionner ou
entendre Aubin le nommer) et celui de l'auberge (Joss voit Corvus puis entend son nom),
avec sauvegarde/rechargement et les trois rendus. Ils couvrent aussi une mention ambiguë dans
une vraie réponse MJ auditée (fournisseur simulé), qui reste sans lien avec un corps,
deux présentations à partir de l'identité privée du locuteur, la voix reconnue sans nom, les détails aux
identifiants composés et une référence devinée hors perception. Mesures et limites dans
[le rapport](taches/rapport-codex-2-noms.md).

Le protocole de réplique MJ fournit son locuteur et sa citation, sans destinataire tiers
validé. Il peut faire entendre un nom de tiers connu du locuteur ; cela ne présente pas son
corps. L'appel ciblé du moteur possède ce destinataire et peut établir le lien. Les étiquettes
du récit (« Aubin dit à Gorm… ») ne comptent jamais comme des noms prononcés.

## L'appel négocié (branche `appel-negocie`)

Décision de l'utilisateur (2026-10-22). Avant, héler était un cri (`pnj.heler`) auquel l'appelé qui
saisissait son nom répondait toujours « Ici ! » (sauf méfiance) puis attendait d'être rejoint `REJOINT`
(5) minutes : rien ne décidait qui se déplaçait, quelle que soit la raison de l'appel ; l'appelant
cherchait, l'appelé attendait, même quand l'appelé avait ce qu'on venait lui demander sur lui, ou ne
pouvait de toute façon pas bouger.

**Une règle commune** (`donjon/appel.py`), au même endroit pour les PNJ et le joueur. L'appelé et
l'appelant conviennent de qui vient à qui par des paroles typées (contenu `appel`, sorte `arrive`,
`viens`, `quoi` ; contenu `raison`), des cris (nature `hele`) que chacun saisit par l'ouïe commune :
- « J'arrive ! » : celui qui le dit vient à l'autre, qui l'attend ;
- « Ici, viens ! » : celui qui le dit reste où il est, l'autre vient ;
- « Qu'est-ce que tu veux ? » : l'appelé ne sait pourquoi on l'appelle et n'a pas de raison de bouger ;
  l'appelant dit ce qu'il veut (`raison_de` : le geste de son plan qui vise l'appelé, sinon son but ou
  le besoin qui le lui fait chercher : une demande, une offre, un avertissement, une tâche, ou lui
  parler), et l'appelé décide de nouveau, sans redemander ;
- le silence : il se méfie de cette voix (`voix.repond`), ou ne veut pas se signaler (`se_cache` : un
  geste de son plan qu'il veut sans témoin, ou un geste illicite en cours).

Ce que dit l'appelé, `decider`, dans l'ordre : le silence ; « Ici, viens ! » s'il attend déjà celui qui
l'appelle, s'il ne croit pas pouvoir venir (`peut_venir` : aucun chemin qu'il croie ouvert, l'eau qui le
met en péril), s'il est retenu (`retenu` : un geste en cours sur place, `passage.raison_de_rester` ; une
garde ; ce qu'il fait sur place, assis, au feu, à l'abri ; un autre rendez-vous) ou si un besoin qui
presse l'occupe ailleurs (`presse_ailleurs`) ; « J'arrive ! » s'il cherche lui-même l'appelant ou si on le
prie de venir ; avec une raison, « J'arrive ! » si elle le fait venir (`pressante` : un avertissement, une
aide, la demande d'un objet qu'il a sur lui), « Ici, viens ! » sinon ; libre et sans raison, « Qu'est-ce
que tu veux ? ». L'appelant qui entend « Ici, viens ! » répond « J'arrive ! » s'il peut venir (sinon,
une fois, « Ici, viens ! » à son tour : qui l'entend vient, ou se tait).

**Ce qui est convenu entre dans l'esprit des deux.** Qui reste attend (`rejoint` : qui, depuis, jusqu'à
quand, et si l'autre a promis de venir) ; il s'arrête aussitôt, sauf pour ce qui passe avant l'attente
(`deliberation._passe_avant`). Qui a dit « J'arrive ! » doit venir (`rejoindre` : qui, la salle d'où venait
sa voix, jusqu'à quand) : une parole due (`plan_venir`, rang `engagement` : après ce qui presse, avant le
bruit et la routine), aller là et y parcourir la salle des yeux. Qui attend quelqu'un qui a promis de
venir ne le cherche plus : un plan qui commence par aller à lui ou le chercher devient l'attendre là où
il est (`deliberation._attendre_qui_vient`), son but reprend quand ils se sont retrouvés. **L'attente se
règle sur la distance** (`delai`) : le temps que met celui qui vient, par le plus court chemin en temps
(`spatial.trajet`, portes ouvertes en passant), et sa moitié, plus `MARGE` (2) minutes ; plus de
constante `REJOINT`. Le rendez-vous est tenu quand ils se retrouvent (`tenir`, `rencontre` : il voit
l'autre, ou le sait là et ils peuvent se parler) ; celui qui est venu et trouve l'autre qui, lui, ne le
voit pas (de dos, dans le noir) le lui dit : « Me voici ! » (`se_signaler`). **« J'arrive ! » est une
parole donnée** : qui attend jusqu'à l'échéance celui qui l'avait dite le voit, cesse d'attendre et n'a
plus confiance en lui (« … cesse d'attendre Gorm, qui avait promis de venir. » ; souvenir
`parole_rompue`, cause `parole_rompue` de `relations.EPREUVES`, comme une dette niée ou un prêt gardé),
joueur compris. Un seul rendez-vous à la fois : qui attend déjà quelqu'un garde cette attente.

**Le joueur** répond ou demande sans le MJ (`paroles.reponse_a_l_appel`, `commandes.repondre`,
`sons._compiler_repondre`, méthodes `repondre`, `arriver`, `demander_raison` d'`emettre_son`) : « j'arrive »,
« je viens » ; « viens », « viens ici », « Ici ! », « je réponds » ; « qu'est-ce que tu veux ? », « que
veux-tu ? » ; entre guillemets, après « je réponds » ou « je crie », ou précédés du nom de l'appelant
(« Gorm, j'arrive ! ») ; « ici » ou « oui » seuls ne répondent pas. Il peut répondre à qui vient de le
héler, de lui demander ce qu'il veut, de lui dire ce qu'il veut ou de lui dire « Ici, viens ! »
(`appel.en_attente`, `ecoute.appels`) ; « Qu'est-ce que tu veux ? » seulement à un appel par son nom (refus
« Tu sais déjà ce qu'on te veut… » avec `attendu` sinon). Le PNJ y donne suite par la même règle
(`appel.reagir`, le cri fini) : il attend Corvus qui arrive, vient s'il le peut quand Corvus le prie de
venir, ou dit ce qu'il veut ; ses réponses parviennent au joueur par l'ouïe commune. Ce que le joueur
promet pèse comme ce que promet un PNJ.

Vérifié (`tests/test_appel_negocie.py`, état après rechargement et ce que lit le joueur) :
- « Ici, viens ! » : cas réel du Relais, Aubin affamé hèle Gorm derrière la porte étanche, que Gorm croit
  verrouillée : « Ici, viens ! », « J'arrive ! », Gorm ne bouge pas, ils se retrouvent, la part au premier
  appel ; même nature, Gorm qui garde (le but `garder`) ne quitte pas sa garde ;
- « Qu'est-ce que tu veux ? » : cas réel de l'auberge, Hugues veut prévenir Anselme : la raison
  (avertissement) le fait venir, Hugues l'attend sans bouger et le prévient ; cas réel de la mine (graine
  2024, scène enregistrée à la minute 340), Josse veut une part des bûches de Gaspard, qui ne les a pas
  sur lui : « Ici, viens ! », Josse vient, la part est promise ; et, dans le grenier noir de l'auberge,
  Mireille et Odile (`test_constater_rumeurs`) ;
- « J'arrive ! » : Aubin qui cherche Gorm vient à son appel, Gorm l'attend le temps de venir ; cas réel
  de la crue (graine 42, scène enregistrée à la minute 215), Gorm vient au refuge où Brune ne le voit
  pas : « Me voici ! », retrouvés, sans parole rompue (sans ce signal, au banc, elle l'aurait cru parjure) ;
  la parole rompue : Aubin empêché, Gorm cesse d'attendre à l'échéance et s'en méfie ; l'échéance suit la
  distance ;
- le silence : Brune qui guette un crochetage sans témoin ne répond pas à Gorm ; qui se méfie se tait ;
- le joueur qui hèle : « Qu'est-ce que tu veux ? » puis « viens » (Gorm « J'arrive ! », ouvre la porte et
  le rejoint, sans le rappeler), « Ici, viens ! » puis « j'arrive » (retrouvés), « J'arrive ! » de qui le
  cherche, le silence ;
- le joueur hélé : « j'arrive » sans venir (Gorm cesse d'attendre et s'en méfie), « viens » (Gorm vient,
  ou répond « Ici, viens ! » s'il croit la porte fermée), « qu'est-ce que tu veux ? » (« J'ai à te
  parler. », puis « Gorm, viens ») ; aucun appel au MJ ;
- le même laps découpé donne le même monde (Relais, auberge) ; les formes de la saisie.

Correctif commun révélé : celui qui cherche quelqu'un ne l'appelle pas s'il le sait là après avoir
parcouru la salle des yeux (`pnj._inspecter` : `croit_present` au lieu de `percoit`) ; Gorm, venu au palier,
hélait Corvus qu'il venait de voir pendant son tour d'horizon.

Tests changés et pourquoi : « Ici ! » devient « Ici, viens ! », « J'arrive ! » ou « Qu'est-ce que tu
veux ? » selon la scène (`test_voix`, `test_parole_voix`, `test_voix_inconnues`, `test_voix_suite`,
`test_constater_rumeurs`, `test_ouie`, `test_ouie_commune`) ; « … retrouve …, qui l'avait hélé. » devient
« … retrouve …, comme convenu. » et « … se tourne vers …, qui arrive comme convenu. » (celui qui attend
n'est plus toujours l'appelé) ; l'échéance de `test_parole_voix` se lit du rendez-vous (la distance) au
lieu de `REJOINT`, et Aubin y sait la porte fermée pour que personne ne vienne ; `test_entretenir`, à la
nuit décalée par l'appel, Mireille achète la part que Joss garde au lieu de la demander (même refus).

Corrigé en route, vu au banc (mine, graine 42) : Mathe, de garde, hèle Gaspard, qui lui dit de venir ;
retenue, elle répond « Ici, viens ! » à son tour, et chacun attendait l'autre jusqu'à l'échéance. Prié de
venir, celui qui attend en décide de nouveau (il vient, et n'attend plus).

`planification.VERIFIER` et `spatial.VERIFICATION` 0,2 sur une nuit de 8 h de chaque scénario (graine 42,
`tools/audit_nuits.py`) : aucun plantage, aucun écart. Bancs (départ tiré, graines 1985, 7, 42, 2024,
`--processus 4`, `main` 06602a6 puis la branche, l'un après l'autre ; moyenne par nuit, `main` → branche) :

| | Relais 4 h | Mine 4 h | Auberge 4 h | Crue 4 h | Mine 8 h | Auberge 8 h |
|---|---|---|---|---|---|---|
| appels | 0,25 → 0,25 | 0 → 0 | 0 → 0 | 0,5 → 0,5 | 3 → 3,5 | 6,75 → 4,75 |
| réponses (toutes) | 0,25 → 1 | 0 → 0 | 0 → 0 | 0,5 → 1,5 | 2 → 8,25 | 4 → 11,75 |
| « J'arrive ! » / « Ici, viens ! » / « Qu'est-ce que tu veux ? » / raisons | — → 0,25 / 0,25 / 0,25 / 0,25 | — | — | — → 0,5 / 0,25 / 0,25 / 0,25 | — → 2 / 2,25 / 1,75 / 1,75 | — → 3 / 2,75 / 3 / 3 |
| silences | — → 0 | — → 0 | — → 0 | — → 0 | — → 0,5 | — → 0 |
| retrouvailles / attentes vaines | 0,25 / 0 → 0,25 / 0 | 0 / 0 | 0 / 0 | 0,25 / 0,25 → 0,5 / 0 | 1,75 / 0,25 → 2 / 0 | 3,75 / 0 → 3 / 0 |
| paroles rompues | — → 0 | — → 0 | — → 0 | — → 0 | — → 0 | — → 0 |
| minutes à attendre (relevé aux 5 min) | 0 → 0 | 0 → 0 | 0 → 0 | 1,25 → 0 | 1,25 → 0 | 2,5 → 0 |
| minutes sans recours | 45 → 45 | 26,25 → 26,25 | 20 → 20 | 0 → 0 | 36,25 → 36,25 | 138,75 → 137,5 |
| minutes en attente | 1,25 → 1,25 | 0 → 0 | 1,25 → 1,25 | 10 → 10 | 290 → 291,25 | 1,25 → 1,25 |
| échanges | 6,5 → 6,5 | 13,25 → 13,25 | 7,75 → 7,75 | 6 → 6 | 41,75 → 41,5 | 29,25 → 30,75 |
| temps d'une nuit | 3 → 2,8 s | 7,2 → 7,2 s | 4,7 → 4,6 s | 3,9 → 3,5 s | 28 → 27,7 s | 15,7 → 15,3 s |

Aucune usurpation ni violation, aucun écart. En quatre heures, on ne hèle presque pas (les quatre
scénarios en ont 0 à 0,5 par nuit) : les bancs de 8 h de la mine et de l'auberge, où l'on hèle, montrent
l'effet. Les appels en boucle baissent à l'auberge (graine 42 : Mireille hélait Odile huit fois en cinq
minutes ; désormais une fois, puis « J'arrive ! ») ; l'attente vaine de la crue (graine 42) devient des
retrouvailles par « Me voici ! », celle de la mine (graine 7, Gaspard attendant Lucien) aussi. Les
réponses comptent chaque cri de la négociation (deux à quatre par appel). Le reste des nuits est égal :
les rendez-vous ne changent ni les besoins ni les échanges, seulement qui marche vers qui. Les minutes à
attendre, relevées toutes les cinq minutes, ne saisissent plus d'attente : elles durent désormais le temps
de venir (une à trois minutes) au lieu de cinq.

Limites de l'appel négocié :
- Le joueur ne dit pas ce qu'il veut par une parole typée locale : à « Qu'est-ce que tu veux ? », il
  répond « j'arrive » ou « viens » ; ce qu'il dirait par le MJ n'entre pas dans la décision de l'appelé.
- Seul « J'arrive ! » pèse s'il n'est pas tenu ; « Ici, viens ! » cède à ce qui presse comme l'attente
  d'avant, sans que l'autre lui en tienne rigueur. Qui avait promis et en a été empêché (une porte, l'eau)
  rompt sa parole aux yeux de l'autre, qui n'en sait pas la cause. En 3a, une parole rompue ôte la
  confiance comme une dette niée (la croyance `fiable`) ; les relations graduées la pèseront.
- Un rendez-vous à la fois : qui attend déjà quelqu'un garde cette attente, sans tenir compte d'un autre
  qui lui promet de venir.
- Le rendez-vous se juge au choix du but (événements, minute) ; on se retrouve en se voyant, ou en se
  sachant là et pouvant se parler. Le lieu du rendez-vous est la salle d'où venait la voix ; peut-il venir
  se juge sur le chemin qu'il croit, vers la salle réelle de la voix.
- La raison d'un appel se lit de l'intention de l'appelant, en cinq sortes ; « J'ai à te parler. » quand
  rien ne la dit (une garde, une ronde). `MARGE` est une constante.
- `tools/comparer_bancs.py` n'est pas sur `main` : les bancs sont comparés mesure par mesure.

## Limites

- Un geste long (crocheter, une minute) retentit une fois, quand il commence ; le bruit part de la
  case de l'auteur, pas de l'objet. Un geste illicite s'entend, lui, tant qu'il dure (registre).
- Témoins par l'ouïe (branche `ouie-temoins`) : dans le noir, au contact, on n'identifie personne (ni
  toucher, ni « Qui va là ? » pour un geste) ; l'auteur ne se reconnaît qu'à ce qu'on croyait de sa
  place ; une case seulement d'écart entre le bruit et l'objet cru (`PRES_DE`) ; seule la salle même fait
  savoir sur quoi porte un bruit. Un examen vain couvre la salle entière pour un bruit pareil ou moindre :
  un autre inconnu qui y entre à pas ordinaires ne l'y renvoie pas avant 30 minutes de silence. L'auteur
  qui croit quelqu'un à portée d'oreille l'y croit tant que sa croyance a moins de 30 minutes, même s'il
  est parti sans bruit.
- Pas d'endormissement : seul le repos assourdit. Une voix dont on saisit les mots fait reconnaître
  qui l'on connaît (branche `constater-et-rumeurs`) ; un autre bruit, ou une voix trop faible pour
  en saisir les mots, est attribué dans le noir à qui l'on croit là, même s'il vient d'un autre, et
  la croyance entretenue n'est corrigée que par la vue, une voix reconnue ou un geste manqué.
- Pas de diffraction, de hauteur ni de bruit de fond (la tempête, la crue) ; l'extérieur ne masque
  rien.
- Le joueur ne fait pas de jet d'ouïe ; ses gestes ont la nature de la table, plus l'arbitrage du
  bruit (3 : fracas).
- Paroles : un destinataire doit être perçu par le joueur ; qui l'entend sans être vu (derrière le
  pilier) n'est que témoin, sauf à répondre à une question dite à la cantonade (`parole-corrections`) ; le nommer dans une parole sans conteste est refusé par le moteur, sans
  appel au MJ (« Tu ne vois pas Aubin d'ici : approche-toi… », la cantonade proposée). Les répliques
  que Luna prête aux PNJ (`paroles_pnj`) sont enregistrées pour les auditeurs qui en saisissent
  réellement les mots ; une présentation leur apprend le nom selon le même contrat. Un PNJ tout près
  d'un chuchotement n'en retient qu'un bruit feutré, pas qu'on chuchote. Sans cases, deux présents
  font toujours une ambiguïté, et l'on chuchote à quiconque est là. « je lui dis » vise le dernier
  à qui Corvus a parlé. Les paroles entendues occupent la mémoire des PNJ (40 souvenirs ; une
  soixantaine de paroles surprises par nuit à la mine).

## Parole après les noms (`codex-luna-noms`)

Sans adresse imposée, `parole_prevue.audience_libre` laisse Luna distinguer la parole
individuelle, le groupe (`tous`) et la cantonade sans destinataire particulier (`personne`),
même si des personnes sont visibles. La contre-revue de fidélité contrôle ce choix sur la
copie préparée avant tout enregistrement ; après deux propositions refusées, le joueur doit
préciser son adresse et ses mots. Le secours local ne contourne pas ce refus. Les
destinataires explicites, les chuchotements et les suites d'échange restent contraints par
la saisie. Une question directe devenue parole conserve ses mots. Un verbe sans propos et
sans réponse locale d'appel demande les mots du joueur sans les inventer.

Chaque répondant est entendu avant le récit, même si sa réponse mécanique l'a fait s'écarter
hors du champ visuel. Une voix qui répond d'une autre salle devient aussi un interlocuteur
tant que chacun saisit les mots de l'autre ; elle ne révèle que son identité perçue. Les
répliques auditées et les faits typés `parole` utilisent les mêmes auditeurs acoustiques,
joueur compris, et retiennent le lieu réel de leur source. Les PNJ autonomes gardent leurs
règles de décision ; les empreintes moteur sont comparées dans le rapport de la tâche 8.

Les formes locales de l'appel négocié sont rejouées avec la connexion Luna, sur des copies,
avec et sans guillemets : l'appel, l'arrivée promise, l'invitation à venir et la question de
raison ne font aucun appel au modèle. Les rendez-vous et les réponses entendues appartiennent
au moteur. Voir `docs/taches/rapport-codex-8-luna-noms.md` pour les scènes et les limites.

## Réglages à trancher

- L'échelle (crans, paliers, ouverture 1 / porte 3). Le crochetage sonne selon l'adresse (branche
  `crochetage-surenchere`) : `ouie.AISANCE` (0 : toute réussite cède sans fracas ; une marge de 5
  ferait d'une réussite de justesse un acharnement bruyant) et `planification.HABILE` (0,5 : la chance
  à partir de laquelle un voleur attend un crochetage feutré ; aux DEX des scénarios, personne ne s'y
  sait habile) sont à régler au banc ; l'outil ne compte que par sa nature (des crochets, pas un levier).
- `PROCHE` (6 cases pour se retourner), `PRES_DE` (1 case pour attribuer un bruit à qui l'on croit
  là), `HABITUDE` (15 min), le courage au-dessus de 50 pour aller voir un fracas.
- L'inquiétude (15 × niveau reçu / 9) ; l'appel qui inquiète à chaque appel.
- Les voix (branche `voix`) : `voix.INCONNU` (+2 au DD d'une demande d'une voix inconnue), la prudence
  (sécurité + 50 − courage ≥ 50), `APPEL_OUBLI` (60 min où une salle hélée en vain compte pour
  parcourue), `VU_AILLEURS` (30 min : « c'est X » de qui a vu X ailleurs est douteux) ; `REJOINT`
  (5 min où qui a répondu à un appel attend d'être rejoint, branche `parole-voix`).

## Suite prévue : imiter une voix (non faite)

L'utilisateur veut plus tard une imitation de voix plus ou moins réussie (un changelin qui dupe les
PNJ), puis des PNJ qui, sachant qu'un imitateur rôde, se méfient même d'une voix connue. Tout passe
déjà par `voix.reconnaitre(monde, auditeur, locuteur) -> (qui il croit entendre, certitude)` :
l'imitation y rendra (X, une certitude moindre) pour la voix d'un autre, selon un jet de l'imitateur
contre l'oreille de l'auditeur ; la méfiance, une certitude « douteuse » pour une voix connue. Les
appelants (`ouie.entendre`, `voix.identifie`, `voix.fiabilite`, `voix.se_nommer`, `ecoute`) lisent
déjà la certitude ; `voix.connaitre` compare déjà la voix entendue à ce qu'elle a prétendu.
