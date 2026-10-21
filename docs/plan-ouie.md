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
| bruyant | 7 | crocheter, forcer, frapper, couper, découper, sauter, franchir un obstacle ; tout geste du joueur que l'arbitrage dit fracassant (bruit 3) |
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
  comme une ronde ; oublié après 30 minutes sans nouveau bruit. Le bruit de sa propre salle ne
  l'envoie nulle part.

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

**Règle acceptée.** Le moteur fixe le destinataire (`paroles.analyser`, `paroles.destinataires`) :
celui que le joueur nomme ; sinon celui qui est en face de lui (dans son regard, le plus proche
à portée de voix) ; à égalité, le joueur précise. « à tous » s'adresse à tous les présents qui
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
mains de l'auteur. La nouvelle le dit (« Lucien a posé le ballot de soie dans Étable ») ; qui la
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
en saisit les mots, `ouie.saisissent`) et ne se méfie pas de lui répond de la voix ; s'il entend la
réponse (`ouie.entend`), il le croit là d'où elle vient (`entendu` : sa case dans la même salle,
sinon la salle), et l'ouïe commune attribue ensuite ses bruits. Ils se parlent alors de près même
dans le noir (`pnj.se_parler` : la voix suffit, comme pour le joueur, `passage._peut_prier`). Le
joueur entend l'appel et la réponse par `ecoute` ; appelé, il répond s'il le veut. Cas réel
(auberge, graine 7) : Mireille tournait 70 minutes dans l'auberge sans voir Odile ; au grenier noir,
elle l'appelle, Odile répond, Mireille lui demande sa part sans la voir et l'obtient. Même nature :
Hugues cherche Anselme au dortoir noir pour le prévenir, l'appelle, et le prévient de vive voix.
Odile, qui se méfie de Mireille, ne répond pas.

Vérifié (`tests/test_constater_rumeurs.py`, état après rechargement et ce que lit le joueur) : les
cas ci-dessus ; le joueur lit en clair « Hugues dit à Anselme que le ballot de soie est dans
Étable. » et « Ilse glisse à Gorm que Brune a posé les vivres du refuge dans Conduite basse. »,
et entend au grenier « « Odile ? » » puis « « Ici ! » ».

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
  fait toujours pas appeler, et la voix d'un inconnu ne fait pas reconnaître qui parle. Qui ne veut
  pas être trouvé ne se tait que par méfiance. Le joueur appelé ne répond pas pour le PNJ.
- Les échanges que le joueur ne voit pas, dans sa salle, se lisent comme avant (« X parle à voix
  basse avec Y ») en plus de ce que son ouïe lui en fait entendre ; ne les dire que vus changerait
  le contrat de plusieurs tests du stratège : hors de ce chantier.
- Forcer une serrure dans le noir à 5 % de chance reste un recours que le planificateur prend
  quand il n'en a pas d'autre (mine, Odon) ; la lumière comme but est un autre chantier.

## Limites

- Les réflexes déclarés (`reaction_son`, le protecteur qui accourt) et le souvenir « son » restent
  sur l'ancienne portée (`sons.portee`, échelle 1 à 3) : pour les émissions vocales du joueur, les
  sons d'objets et les appels de PNJ, deux portées coexistent (l'inquiétude, elle, ne vient que de
  l'ouïe commune). À fondre.
- Un geste long (crocheter, une minute) retentit une fois, quand il commence ; le bruit part de la
  case de l'auteur, pas de l'objet.
- Pas d'endormissement : seul le repos assourdit. La voix ne fait pas reconnaître qui parle ; dans
  le noir, un bruit est attribué à qui l'on croit là, même s'il vient d'un autre, et la croyance
  entretenue n'est corrigée que par la vue ou un geste manqué.
- Pas de diffraction, de hauteur ni de bruit de fond (la tempête, la crue) ; l'extérieur ne masque
  rien.
- Le joueur ne fait pas de jet d'ouïe ; ses gestes ont la nature de la table, plus l'arbitrage du
  bruit (3 : fracas).
- Paroles : un destinataire doit être perçu par le joueur ; qui l'entend sans être vu (derrière le
  pilier) n'est que témoin, et le nommer est refusé (« pas ici pour t'entendre »). Les répliques
  que Luna prête aux PNJ (`paroles_pnj`) ne sont pas entendues des autres PNJ. Un PNJ tout près
  d'un chuchotement n'en retient qu'un bruit feutré, pas qu'on chuchote. Sans cases, deux présents
  font toujours une ambiguïté, et l'on chuchote à quiconque est là. « je lui dis » vise le dernier
  à qui Corvus a parlé. Les paroles entendues occupent la mémoire des PNJ (40 souvenirs ; une
  soixantaine de paroles surprises par nuit à la mine).

## Réglages à trancher

- L'échelle (crans, paliers, ouverture 1 / porte 3) ; le crochetage en « bruyant », comme demandé,
  s'entend dans la salle voisine : c'est lui qui multiplie les témoins.
- `PROCHE` (6 cases pour se retourner), `PRES_DE` (1 case pour attribuer un bruit à qui l'on croit
  là), `HABITUDE` (15 min), le courage au-dessus de 50 pour aller voir un fracas.
- L'inquiétude (15 × niveau reçu / 9) ; l'appel qui inquiète à chaque appel.
