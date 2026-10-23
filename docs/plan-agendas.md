# Plan : les agendas des PNJ, le mandat et les groupes

Rédigé le 2026-10-23 à la suite d'une discussion de conception. Rien n'est implémenté ; les
décisions de l'utilisateur, prises le même jour, sont à la fin (§ 10) et reportées dans le texte.

## 1. Point de départ

Les PNJ ont des **besoins** qui montent et qu'on fait retomber (faim, chaleur, repos, sécurité,
devoir, biens), et la délibération choisit un but à la fois parmi leurs recours
(`deliberation._candidats`, `choisir`). Le planificateur trouve la suite de gestes la moins chère
vers ce but (`planification.chercher`), sur ce que le PNJ croit. Il ne choisit jamais le but.

Ce qui va déjà au-delà d'un besoin, sans en être un étage :

- **Les pulsions** du profil (« le feu allumé », « le ballot à sa place ») sont des conditions sur
  le monde, mais chacune est attachée à un besoin et ne sert qu'à le faire retomber.
- **Les engagements** (`esprit["engagements"]` : `condition`, `pour`, `minute`, `paye`,
  `annule`) : une parole donnée ou une tâche payée persiste, oblige, s'abandonne après
  `echanges.ENGAGEMENT_MAX` ou quand elle devient impossible (`echanges.empeche`), et cet abandon
  s'annonce. C'est la structure la plus proche d'une intention.
- **Confier et engager** (`echanges.confier`, `echanges.engager`) : un PNJ fait faire une condition à
  un autre ; l'autre juge sur son devis (`planification.devis_pulsion`), la persuasion ou le prix.
- **`protege`** du profil : le protecteur accourt à l'appel, prévient, ranime, défend (4c).
- **La situation** (`profil["situation"]` : dette, proches, projet) ne pèse que sur la valeur d'une
  pièce (`caractere.valeur_piece`) ; le projet de Gorm, d'Anselme ou de Lucien n'engendre aucun geste.
- **Les relations** (cinq axes, 3b) et **les signes** (3c) modulent les décisions ; une rancune ne
  donne jamais envie de se venger.

Ce qui manque : un état du monde voulu, poursuivi sur des heures, qui donne un sens aux choix et
occupe le temps que les besoins laissent libre. Le banc le montre : un Relais « surtout fait de
rondes », des minutes « en attente » et « sans recours » par centaines.

Ce que les plans existants prévoient déjà, et sur quoi ce plan s'appuie :

- **Influencer** : `docs/plan-relations.md`, **A2 = 3e** (propositions, `rendre_service`,
  intermédiaires) et **A3 = 3f** (avis sur des prédicats que le moteur sait évaluer, disputes). L'épreuve de
  3f (Aubin, qui a vu l'eau, convainc Ilse de monter) est déjà presque une évacuation.
- **Contraindre** : `docs/plan-force.md`, 4d (retenir, ligoter, enfermer) et 4e (tuer).
- **Statut et groupes** : `docs/plan-social.md`, « Statut et groupes ».

Les agendas ne remplacent aucun de ces plans : ils se posent au-dessus. Un agenda dit quoi viser
sur des heures ; ces plans fournissent les gestes pour agir sur les autres.

## 2. Principes

- **Un étage au-dessus de la délibération, la recherche en dessous.** L'agenda choisit le prochain
  sous-but (une condition) ; le planificateur actuel trouve les gestes, comme pour un besoin. Les
  méthodes écrites retirées par la branche `planificateur` disaient *comment* se nourrir : rien ici
  ne dit comment, seulement *quoi viser ensuite*.
- **Révocable, jamais irrévocable.** Un agenda est réévalué quand ce que le PNJ croit change ; il
  tient avec une hystérésis (comme `REPRISE`, `INERTIE` et le recours en cours), il s'endort, se
  réveille, s'abandonne pour une raison qu'on peut raconter.
- **Sur ce qu'il croit.** Le choix des sous-buts, des mandataires, du risque : jamais d'après la
  vérité. Le banc continue de compter les usurpations.
- **Une même règle pour tous.** Aucune règle propre à un personnage ni à un scénario. Le scénario ne
  fournit que des données : des agendas de départ, des liens, une autorité.
- **Le groupe de départ est un état initial** (décision du 2026-10-23). Un scénario peut commencer
  avec un groupe et un chef établis ; rien n'est gravé : le groupe ne tient ensuite que par les
  mécaniques communes. Chacun peut cesser de suivre, le chef perdre son autorité, un autre la prendre.
  Cela précise « un groupe n'est pas déclaré » de `docs/plan-social.md` : il ne l'est que comme point
  de départ.
- **Le joueur reste libre.** Le moteur ne lui donne aucun agenda ; il peut recevoir ou donner des
  mandats par la parole typée, et les PNJ le jugent par les mêmes règles.

## 3. Table des cas

Pour chaque cas : l'origine, la décomposition en sous-buts, ce qui existe, ce qui manque, ce que le
joueur peut y faire. Ces cas sont des épreuves du vocabulaire, pas des règles.

| # | Cas | Origine | Décomposition | Existe | Manque | Joueur |
|---|-----|---------|---------------|--------|--------|--------|
| 1 | Gorm évacue et prévient le village | scénario | amener chacun à la galerie ; informer le village (la cloche) ; garder le relais tant que c'est tenable | eau prévue, `prevenir`, appel négocié, persuasion | but sur l'état d'autrui ; convaincre de bouger (3e, 3f) | aider, refuser de monter, retenir quelqu'un |
| 2 | Gorm confie à Aubin d'aller chercher Brune | sous-but du cas 1, mandaté | Aubin rejoint Brune, la convainc, la ramène, rend compte | `confier`, `engager`, `chance_demande` | mandat sur un sous-but ; compte rendu ; réaffectation | être le mandaté |
| 3 | Un combattant cupide devient mercenaire | occasion | proposer ses services ; contrat ; protéger l'employeur | tâche payée, `protege`, défense (4c) | repérer l'occasion ; contrat qui dure ; garder une personne | l'embaucher, le débaucher |
| 4 | Le mercenaire payé par deux camps | deux contrats incompatibles | arbitrer selon loyauté, honnêteté, gain | prix d'une faute, relations | voir que deux agendas s'excluent ; trahison pesée | surenchérir |
| 5 | L'assassin | scénario | écarter X, à la manière discrète ; dissimuler son rôle | guet, sans témoin, oreilles crues, coups | tuer (4e) ; anticiper le soupçon | cible, enquêteur, suspect |
| 6 | Anselme, le marchand | scénario | obtenir des pièces en vendant ; garder son ballot ; partir à l'aube | vente, garde, argent | proposer une vente de soi-même ; échéance | acheter, voler |
| 7 | Lucien et le reliquaire | scénario | que personne ne sache où il est ; partir sans être vu | croyances de lieu d'autrui, rumeurs | dissimuler : un but sur les croyances d'autrui | découvrir, faire chanter |
| 8 | Odon et sa dette | situation | obtenir des pièces : travail, emprunt, vol | presque tout | faire de la dette un agenda, pas un poids | prêter, employer |
| 9 | Brune pendant la crue (témoin) | besoins | survivre | tout | rien : ce n'est pas un agenda | — |
| 10 | La vengeance après un vol | événement, rancune | récupérer ; dénoncer ; nuire | rancune, rumeurs, `reclamer` | naissance d'un agenda ; nuire | voleur, allié |
| 11 | Le ralliement contre un menaçant | événement, peur partagée | rallier X et Y ; écarter le menaçant | peur, méfiance, appel à l'aide | rallier ; un chef qui émerge et mandate | menaçant, coalisé |
| 12 | Le joueur donne un faux ordre | autorité usurpée | le mandaté juge la source | `voix.reconnaitre`, méfiance d'une voix inconnue | vérifier l'autorité de qui mandate ; imitation de voix | l'imposteur |
| 13 | Le chef du groupe de départ perd son autorité | scénario, puis événements | les suivants réévaluent ; un autre prend la tête | relations graduées, hystérésis | l'autorité comme lien ; désobéir | prendre la tête, saper le chef |
| 14 | Ilse obéit par peur et veut partir | scénario ou événement | partir (en sommeil) ; dissimuler ; obéir aux mandats tant que refuser coûte plus | peur, guet, mensonge (3c), signes | agenda en sommeil ; réputation de qui punit | rassurer, terroriser |
| 15 | Gorm tyrannique punit un refus | caractère et événement | être obéi ; punir le désobéissant (enfermer, frapper) | coups (4b), défense (4c) | naissance d'un agenda « punir » ; enfermer (4d) ; dissuasion par la réputation | être puni, témoin, protecteur |

## 4. Vocabulaire

Sept sortes d'agenda, déclarées une fois par le moteur, paramétrées par le scénario ou par la
naissance de l'agenda. Chaque sorte se décompose en **sous-buts**, des conditions que le
planificateur sait viser ; jamais en gestes.

| Sorte | À atteindre ou à tenir | Paramètres | Sous-buts (dans l'ordre où ils sont envisagés) |
|-------|------------------------|------------|-----------------------------------------------|
| **protéger** | à tenir | qui | être à portée de voix de lui ; répondre à son appel (existe) ; s'interposer, défendre (4c) |
| **garder** | à tenir | chose ou lieu | ce que fait déjà « garder » (pulsion, `prix_gardes`) |
| **amener** | à atteindre | qui (un ou plusieurs), lieu | qu'il croie le lieu préférable (avis, 3f) ; qu'il accepte (proposition, 3e) ; l'accompagner ; le contraindre si la manière le permet (4d) |
| **informer** | à atteindre | qui, fait ou avis | être à portée de voix ; le dire (`dire`, `prevenir`) ; le faire dire par un autre (mandat) |
| **obtenir** | à atteindre | bien, pièces | le planificateur actuel (demander, acheter, travailler, prendre), étendu à ce qui n'est pas un besoin |
| **écarter** | à atteindre | qui | qu'il parte (proposition, menace) ; l'enfermer (4d) ; l'assommer (4b) ; le tuer (4e) ; selon la manière et la douceur |
| **rallier** | à atteindre | qui | lui rendre service (3e) ; partager un avis contre un tiers (3f) ; lui proposer |
| **dissimuler** | à tenir | fait, objet, rôle | qu'aucun témoin ne le voie ; ne pas être vu près de ; taire ou mentir quand on l'interroge (3c) ; cacher l'objet |

Les **manières** contraignent les gestes admis pour tout l'agenda : `discret` (sans témoin, et un
agenda `dissimuler` attaché), `sans_violence`, une `echeance`. « Sans soupçon » n'est pas une règle
à part : c'est un agenda `dissimuler` attaché au premier. Lucien, l'assassin et Ilse en sont trois
usages.

Diriger n'est pas une sorte : **le mandat** est une manière d'atteindre n'importe quel sous-but.

## 5. Modèle de données

Tout est dans `data`, sauvegardé ; même laps découpé, même monde. Pas de migration des anciennes
sauvegardes.

**Un agenda** (`esprit["agendas"]`, au plus trois actifs ; d'autres peuvent dormir ; au-delà, le
plus faible au poids du moment, puis le plus ancien, est abandonné avec sa raison) :

```
{
  "id": "a3",                       # unique dans l'esprit
  "sorte": "amener",
  "parametres": {"qui": ["ilse", "brune"], "lieu": "galerie"},
  "maniere": {"sans_violence": true},
  "origine": {"type": "scenario" | "parole" | "contrat" | "mandat" | "occasion" | "evenement",
              "de": "gorm", "minute": 120, "cause": "refus_obeir"},
  "parent": {"de": "gorm", "agenda": "a1"},   # mandat : l'agenda du mandant
  "echeance": 300,                  # ou absent
  "etat": "actif" | "sommeil" | "atteint" | "abandonne",
  "depuis": 140, "raison": "risque",          # dernier changement d'état, racontable
  "confies": {"brune": {"a": "aubin", "minute": 142, "compte_rendu": null}},
  "secret": true                    # il ne le dit pas
}
```

Le **poids** ne se stocke pas : il se calcule à chaque choix des valeurs (ambition, loyauté,
altruisme, honnêteté, douceur, courage), de la situation et des relations envers les personnes
visées, pour suivre ce qui a changé (un prix de faute qui remonte fait céder un agenda illicite).

**Les engagements deviennent des agendas** d'origine `parole` ou `contrat` (sorte la plus proche :
`obtenir` pour une remise, une condition de pulsion sinon). Le socle les porte sans changer leur
comportement (étape A1).

**Agendas de départ** : `profil["agendas"]` dans le scénario, mêmes champs moins l'état.

**L'autorité** que B reconnaît à A se lit de trois sources (décision 1) :
- **le statut** de A, une donnée du scénario (grade, responsable des lieux, employeur), que B
  connaît comme une croyance (un savoir, ou dit par A ou par un autre) ; un statut prétendu peut
  être une imposture, comme un nom prétendu ;
- **l'ascendant**, un sixième axe des relations de B envers A, gradué, avec ses épreuves : il monte
  quand les ordres de A sont suivis et aboutissent, baisse avec ses échecs et ses abus ; les liens
  de départ peuvent le fixer ;
- **la lecture dérivée** de la confiance, de la dette et de la peur de B envers A.

Un statut sans ascendant s'use ; un ascendant sans statut fait un chef de fait. Comme les autres
axes, l'ascendant ne se lit et ne s'écrit que par `relations.py`.

**La réputation** : des croyances sur une personne, portant seulement sur des réactions que le moteur
sait reconnaître (§ 6.7).

## 6. Les règles

### 6.1 Le choix, sur une échelle commune

Aujourd'hui `_candidats` produit une liste ordonnée par catégories, avec des insertions placées à la
main (l'alarme et l'eau en tête, la routine ensuite, l'argent en dernier) et l'hystérésis entre
recours dans `choisir`. Y ajouter les agendas de la même façon rendrait l'ensemble ingérable.

Préalable (étape A0) : chaque candidat porte une **urgence** comparable (un besoin, sa valeur
au-dessus du seuil ; une parole due, son échéance ; une alarme, son rang), et l'ordre actuel en
découle, **sans rien changer aux nuits** (empreintes). Les agendas s'y ajoutent ensuite avec leur
urgence : poids × proximité de l'échéance, ou poids seul s'il n'y en a pas.

Règles (décision 2) :
- un besoin au-delà de `DESESPOIR`, une alarme et le péril de l'eau passent devant tout agenda ;
- un agenda passe devant la routine et l'attente ;
- entre agendas et besoins pressants non désespérés, l'urgence décide, avec la même `INERTIE`
  qu'entre besoins : Gorm évacue malgré la faim si l'eau presse davantage.

### 6.2 Du projet au sous-but

À chaque choix, un agenda actif propose **son prochain sous-but** : le premier de sa sorte (§ 4) que
le PNJ ne croit pas déjà vrai et dont le planificateur trouve un plan. Le sous-but est une condition
passée à `chercher`, avec la manière de l'agenda (gestes admis). Le plan est exécuté en préfixe et
refait, comme aujourd'hui ; l'agenda ne garde que son état, jamais un plan.

Un agenda à plusieurs personnes (amener Ilse et Brune) choisit la plus proche d'abord, à égalité par
identifiant.

### 6.3 Le sommeil : le risque dans le coût

Un agenda n'a pas besoin d'un mécanisme d'obéissance : son prochain pas ne se fait que s'il coûte
moins que d'attendre, la même règle que `planification._endure`. Le risque entre dans ce coût : le
prix d'une faute (honnêteté), les témoins et les oreilles crues, la sanction attendue (réputation,
§ 6.7). Tant qu'aucun plan ne passe, l'agenda est **en sommeil**, avec sa raison ; il se réveille quand
une croyance change (l'opposant s'éloigne ou dort, un allié se déclare). C'est la règle du guet de
Brune, étendue aux agendas.

### 6.4 Révision, fin, hystérésis

- **Atteint** : sa condition est crue vraie. Un agenda à tenir ne s'atteint pas ; il est tenu tant
  qu'il dure.
- **Abandonné** : impossible sur ce qu'il croit (comme `echanges.empeche`), échu, ou supplanté par un
  agenda incompatible de poids plus fort de plus que la marge d'hystérésis ; la cause est retenue,
  et un agenda reçu s'annonce abandonné à qui l'a confié (comme `retenir_abandon`).
- **Hystérésis** : un agenda actif garde la main sur un autre de même rang tant que son poids ne passe
  pas sous l'autre d'une marge, qui croît avec la volonté (VOL) : un PNJ volontaire tient son agenda,
  un faible en change plus vite (décision 4).
- Un même agenda ne renaît pas de la même cause tant qu'aucune croyance nouvelle ne l'y autorise
  (la règle des refus retenus, `deliberation.tient`, `moyens_crus`).

### 6.5 La naissance d'un agenda

Un agenda naît de quatre façons, toutes par des règles communes :
- **le scénario** (données de départ) ;
- **une parole ou un contrat** : ce que font déjà `engager` et `confier`, étendu à un agenda durable
  (protéger quelqu'un contre une paie, pendant une durée) ;
- **une occasion** : un PNJ voit qu'un autre a besoin de ce qu'il peut offrir et que cela vaut pour lui
  (le combattant cupide et le marchand qui a peur ; l'employé qui cherche du travail) ;
- **un événement**, par une table de causes comme `relations.EPREUVES` : un vol subi et la rancune font
  naître « récupérer » ou « nuire », un refus d'obéir chez qui veut être obéi fait naître « punir »
  (une forme d'écarter), une peur partagée fait naître « rallier ».

La table des naissances dit seulement *quelle sorte* naît de *quelle cause* et *quelles valeurs* en
font le poids ; jamais une personne ni un scénario.

### 6.6 Le mandat

**Mandater** confie un sous-but d'un de ses agendas à un autre. C'est `confier` généralisé.

- **Le mandant** choisit, pour un sous-but, entre le faire lui-même et le confier, sur ce qu'il croit :
  où est chacun, ce qu'il sait faire, sa fiabilité (`chance_demande`), ce que la mission lui coûtera
  (`devis_pulsion` vu du mandant). L'attribution est gloutonne : le meilleur candidat estimé, à
  égalité par identifiant, avec une hystérésis contre les réaffectations.
- **Le mandaté** juge comme une tâche aujourd'hui, avec en plus ce qu'il doit au mandant : autorité,
  loyauté, dette, peur, paie. Il accepte par adhésion ou par crainte (une même règle, des raisons
  différentes que le récit dit). Accepté, le mandat devient un agenda d'origine `mandat`, en
  concurrence avec ses besoins et ses propres agendas ; il peut le négliger, l'abandonner, le trahir.
- **Le suivi** passe par les croyances du mandant : il voit le résultat, ou il reçoit un **compte
  rendu** (une parole typée nouvelle, `compte_rendu`), ou il reste sans nouvelles. Sans nouvelles
  au-delà d'un délai réglé sur la distance (comme l'appel négocié), il réaffecte ou s'en charge.
- **La parole** porte le mandat : il faut pouvoir se parler (`pnj.peuvent_se_parler`). Un mandat
  passe par la voix : un ordre venu d'une voix inconnue ou imitée se juge par `voix.reconnaitre`.
- **La récursion** est bornée : un mandaté peut déléguer à son tour, jusqu'à une profondeur fixée.

### 6.7 La réputation

Ilse ne craint pas seulement d'être vue maintenant : elle craint ce que Gorm fera s'il l'apprend. Le
moteur ne simule pas l'esprit de Gorm : Ilse retient une **réputation**, une croyance sur une personne
qui associe une cause à une réaction (« Gorm frappe qui lui désobéit »), apprise en le voyant faire ou
par une rumeur, avec la confiance d'un ouï-dire. Comme les avis de 3f, elle ne porte que sur des
couples que le moteur sait reconnaître : un refus d'obéir, un vol, un coup, une parole rompue, d'un
côté ; punir, dénoncer, se venger, pardonner, de l'autre.

La sanction attendue entre dans le coût du risque (§ 6.3). La dissuasion naît du jeu : une punition
vue rend la suivante crédible. La même forme sert à l'assassin, sur les gens en général : « qui est vu
près d'un corps est soupçonné ».

### 6.8 Dissimuler

Un agenda `dissimuler` est tenu tant qu'aucun autre ne croit le fait caché. Ses sous-buts agissent
sur ce que les autres percevront : agir sans témoin ni oreille crue, ne pas être vu près du lieu,
cacher l'objet, et, interrogé, taire ou mentir selon l'honnêteté (le mensonge de 3c). Les signes de
3c continuent de fuir : un agenda caché peut se lire (« semble avoir peur de Gorm »). Le PNJ ne sait
pas ce que les autres ont lu de lui ; il sait seulement ce qu'il croit avoir montré.

### 6.9 Le joueur et le MJ

- Le joueur peut recevoir un mandat (« Gorm te demande d'aller chercher Brune ») : c'est un engagement
  lisible sur sa fiche, que le moteur ne lui fait pas tenir ; ne pas le tenir est une parole rompue
  pour le mandant. Il peut mandater par une parole typée (`mandat`), jugée par le mandaté comme celle
  d'un PNJ, et donner un faux ordre.
- **Ce que reçoit Luna** (décision 3). Luna interprète les saisies et met en mots ce que le moteur a
  décidé, dont les répliques des PNJ. Pour chaque interlocuteur, elle reçoit **ce que ce PNJ est prêt
  à dire à Corvus maintenant**, décidé par le moteur, plus ce que Corvus a déjà entendu. Quatre cas :
  - un PNJ dont un agenda concerne Corvus (Gorm veut que tout le monde monte) : ce qu'il attend de
    Corvus, pour que sa réplique aille dans le sens de ce qu'il fait ;
  - un mandat adressé à Corvus : son contenu (qui, quoi, où), pour le formuler ;
  - « pourquoi tu fais ça ? » : le moteur décide si le PNJ répond vrai, ment ou se tait (honnêteté,
    secret) ; Luna reçoit la réponse décidée, pour un mensonge son contenu, jamais la vérité ;
  - le contrôle : une réplique qui annonce ou promet un agenda doit recopier ce que le moteur a
    enregistré (comme les promesses, `don-et-promesses`).
  Un agenda secret n'est jamais dans le contexte du MJ, ni un agenda annoncé à d'autres hors de
  portée de Corvus.

## 7. Contrôles, mesures, récit

- **Usurpations** : un mandant qui choisit son mandataire d'après sa vraie place, un agenda qui se
  réveille sur un fait non cru, sont des usurpations comptées par le banc.
- **`VERIFIER`** : inchangé pour les recherches ; chaque sous-but est un but de recherche ordinaire, et
  toute lecture nouvelle (poids, réputation, autorité) entre dans `_entrees`.
- **Même laps découpé, même monde** : obligatoire pour chaque étape ; aucun tirage d'agenda ne dépend
  de l'ordre des appels (tirages indexés sur l'identifiant, l'instant et un compteur de l'esprit).
- **Mesures du banc** : agendas nés (par origine), actifs, en sommeil, atteints, abandonnés (par cause) ;
  minutes passées sur un agenda ; minutes en attente et sans recours ; mandats donnés, acceptés,
  refusés, menés, trahis, réaffectés ; comptes rendus ; réputations apprises ; punitions et leur effet.
- **Audit des boucles** (`tools/audit_nuits.py`) : bascules entre agendas, mandats réaffectés en boucle,
  agenda qui renaît de la même cause.
- **Récit** (`recit_pnj`) : chaque agenda né, endormi, réveillé, abandonné, avec sa raison ; qui a
  confié quoi à qui et ce qu'il en est advenu. C'est le premier juge de la plausibilité.
- **Temps de calcul** : mesuré à chaque étape ; un agenda ajoute au plus une recherche par choix.

## 8. Préalables

1. **Les intégrations en cours** (menées dans une autre session) et le lot **trajets réels**
   (`codex-trajets-reels`, en cours) : un agenda compare des coûts sur des heures, et des trajets
   comptés en minutes abstraites par salle faussent ces comparaisons.
2. **Le choix du but sur une échelle commune** (étape A0), sans changement de comportement.
3. **Le coût de calcul** : une mesure de référence ; l'invalidation incrémentale des signes (mine +35 %,
   « À revoir ») ; les recherches bornées de Josse, Rémy et Lucien. La rationalité limitée
   (habitudes, réflexion bornée) peut attendre que la mesure l'exige (§ 9, après A4).
4. **La calibration des lectures de 3c** (41,3 % de méprises) : nécessaire aux agendas cachés
   (étapes A7 et A8), pas avant.

## 9. Étapes

Chaque étape est une branche, mesurée au banc rapide sur les scénarios qu'elle touche, avec le cas
réel et un autre de même nature vérifiés après rechargement.

**A0. Le choix sur une échelle commune.** Urgence de chaque candidat, ordre actuel retrouvé.
Critère : empreintes identiques à `main` sur 2 h puis 8 h, quatre scénarios × quatre graines.

**A1. Le socle des agendas.** `donjon/agendas.py`, seul accès aux agendas (comme `relations.py` en 3a) ;
les engagements y sont portés ; données de départ lues ; sauvegarde. Aucun agenda nouveau ne s'active.
Critère : empreintes identiques ; contrôle AST qu'aucun code ne lit plus `esprit["engagements"]` hors
du module.

**A2. Les propositions (3e de `docs/plan-relations.md`).** Telles que planifiées, avec la condition
« remis » et les intermédiaires, qui serviront au mandat.

**A3. Les avis et les disputes (3f).** Telles que planifiés ; l'avis « la menace d'un lieu » est la
brique de l'évacuation.

**A4. Les premiers agendas déclarés.** Sortes `amener`, `informer`, `garder`, `protéger` ; sous-buts,
sommeil par le risque, révision, fin. Épreuve : la crue, Gorm doté de l'agenda d'évacuer et de prévenir
(données). Mesures : PNJ à la galerie quand l'eau gagne, minutes en attente, temps de calcul.
Vérification Luna (bancs de référence et une scène d'évacuation). **Point de décision** : reprendre ici
le plan de décision (habitudes, réflexion limitée), sur la mesure du coût et de la plausibilité
(décision 7).

**A5. Le mandat et l'autorité.** Mandater, juger un mandat, compte rendu, réaffectation, profondeur ;
l'autorité (statut, ascendant, lecture dérivée) ; parole typée du joueur (`mandat`, `compte_rendu`).
Épreuve : la crue étendue aux évacués du hameau, six à huit PNJ (décision 5) ; Gorm, responsable des
lieux, confie Brune à Aubin.

**A6. La naissance des agendas.** Table des naissances ; occasion (le mercenaire), situation (la dette
d'Odon), événement (la vengeance), rallier. Épreuve : l'auberge (Anselme, Lucien, Hugues) et la mine
(Odon).

**A7. La réputation, enfermer (4d), punir.** Le tyran et l'obéissance contrainte (cas 14 et 15), sans
règle propre ; ils doivent venir des pièces précédentes. S'ils ne viennent pas, une pièce manque : la
trouver, ne pas écrire le cas.

**A8. Tuer (4e) et dissimuler.** L'assassin (cas 5) et Lucien (cas 7). Vérification Luna (agendas
secrets jamais dits, signes qui fuient, mensonges).

## 10. Décisions (2026-10-23)

1. **L'autorité** se lit de trois sources : un statut social prédéfini par le scénario (grade,
   responsable des lieux, employeur), connu comme une croyance ; un sixième axe des relations,
   l'ascendant reconnu ; la lecture dérivée de la confiance, de la dette et de la peur (§ 5).
2. **Agendas et besoins** : un agenda peut passer devant un besoin pressant non désespéré si son
   urgence l'emporte ; le désespoir, une alarme et le péril de l'eau passent toujours devant (§ 6.1).
3. **Luna** reçoit, pour chaque interlocuteur, ce que ce PNJ est prêt à dire à Corvus, décidé par le
   moteur, plus ce que Corvus a déjà entendu ; jamais un agenda secret ni un agenda annoncé hors de
   portée de Corvus (§ 6.9).
4. **La ténacité** : la marge d'hystérésis croît avec la volonté (VOL) (§ 6.4).
5. **Le banc des groupes** : la crue étendue aux évacués du hameau, six à huit PNJ (A5).
6. **Combien d'agendas** : au plus trois actifs, d'autres en sommeil ; au-delà, le plus faible au poids
   du moment, puis le plus ancien, est abandonné avec sa raison (§ 5).
7. **Le plan de décision** (habitudes, réflexion limitée) : repris après A4, sur la mesure du coût et de
   la plausibilité.

Ordre des lots convenu : le lot trajets réels (Q) d'abord, puis A0, puis A2 (3e) et A3 (3f), l'un après
l'autre, car tous touchent `planification.py`.

## 11. Ce qui serait un script, à éviter

- Un agenda dont les sous-buts sont écrits pour un personnage ou un scénario.
- Une obéissance automatique à un chef déclaré.
- Un « tyran » ou un « traître » codé : ils doivent sortir des valeurs, des relations et de la
  réputation.
- Une réputation sur un prédicat que le moteur ne sait pas reconnaître.
- Un mandant qui sait où sont les autres sans le croire.

## 12. Risques

- **La complexité de la combinaison** : chaque pièce est petite, leur combinaison ne l'est pas. Ordre
  strict des étapes, chacune vérifiée au banc avant la suivante.
- **Le coût** : un agenda ajoute une recherche par choix ; le mandat en ajoute chez le mandant (devis
  des candidats). À mesurer dès A4.
- **Des boucles nouvelles** : réaffectations, agendas qui s'endorment et se réveillent, punitions en
  chaîne. L'audit des nuits les compte dès A4.
- **Luna** : ordres, comptes rendus et mensonges passent par la parole ; de nouveaux faux refus
  sémantiques sont probables. Vérification à A4, A5 et A8.
- **Des PNJ trop actifs** : des agendas qui occupent tout le temps libre peuvent rendre la nuit
  agitée et illisible. Le poids et l'urgence se règlent au banc, jamais par personnage.
