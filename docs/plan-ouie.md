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

## Réglages à trancher

- L'échelle (crans, paliers, ouverture 1 / porte 3) ; le crochetage en « bruyant », comme demandé,
  s'entend dans la salle voisine : c'est lui qui multiplie les témoins.
- `PROCHE` (6 cases pour se retourner), `PRES_DE` (1 case pour attribuer un bruit à qui l'on croit
  là), `HABITUDE` (15 min), le courage au-dessus de 50 pour aller voir un fracas.
- L'inquiétude (15 × niveau reçu / 9) ; l'appel qui inquiète à chaque appel.
