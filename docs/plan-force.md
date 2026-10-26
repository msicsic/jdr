# Plan : le corps des PNJ et la force (étape 4 du plan social)

Les sous-étapes 4a et 4b sont fusionnées (`codex-force-4a`, `codex-force-4b`) ; 4c est réalisée
sur `codex-force-4c`, fusionnée, avec les limites de critère ci-dessous. La première partie de
4d est réalisée sur `codex-force-4d-tenir`, non fusionnée (lot 126) : prises, liens et issues
différées. Traîner (lot 134), puis enfermer et s’évader (lot 136, `codex-enfermer`,
non fusionnée) sont réalisés ; la captivité prolongée termine 4d au lot 140
(`codex-captivite`, non fusionnée). 4e est réalisé au lot 145
(`codex-force-4e-tuer`, non fusionnée) ; reste 4f.
Ce document détaille l'étape 4 de `docs/plan-social.md` : PV et
blessures pour tous, états du corps (retenu, ligoté, enfermé, assommé, mort), affrontement. Il
prépare l'étape 5 (contrainte et menace : priver, enfermer, menacer, frapper ; la peur ; les
suites) sans la faire. Tout s'exprime en règles communes, joueur compris, en gestes déclarés une
fois et en coûts du planificateur ; aucun comportement n'est écrit pour un personnage.

Décisions déjà prises par l'utilisateur (`docs/plan-social.md`, « Décisions ») : on peut assommer
ou tuer ; tuer est délibéré ; un personnage ligoté se tue sans jet ; tout PNJ peut mourir ; la mort
du joueur termine la partie, sans reprise pour l'instant ; le joueur reste libre, soumis aux mêmes
perceptions et contraintes ; les caractéristiques sont modulées par les états, et la volonté peut
être brisée.

## Point de départ

- **Le corps commun** (`donjon/corps.py`) : faim, froid, fatigue pour tous ; un état qui presse
  coûte 2 aux jets des caractéristiques qu'il touche (`TOUCHE`, `malus`), que toute règle lit par
  `caractere.caracteristique` ou `modificateur`. La volonté brisée (`corps["volonte_brisee"]`, 0 à
  5) est entamée par la captivité et rendue par le répit depuis le lot 140 (`corps.briser`).
- **Les PV n'existent que pour le joueur** : `joueur["pv"]`, `joueur["pv_max"]` (18 dans tous les
  scénarios, FOR 12), contrôlés par `Monde.verifier`. Ils baissent par une chute (`moteur.py`,
  `max(0, …)`), une blessure d'arbitrage (`improvisation`, 1 à 3 PV, jamais mortelle) et, à
  l'extrême, la faim et le froid (1 PV par heure, jamais en deçà de 1). À 0, seuls le saut et
  l'improvisation sont refusés (« hors de combat ») ; rien ne remonte les PV.
- **Les personnages sont des objets** de type `personnage` ; ils portent `integrite` et `maximum`
  (10/10) hérités des objets, sans usage pour le corps. `esprits.pnjs` les liste tous ;
  `Monde.verifier` refuse un esprit sans personnage.
- **Frapper** (`moteur.py`) ne vise que des objets : sur un personnage, « Cette destruction ou ce
  combat n'est pas simulé ». Les dégâts d'un objet sont `puissance + mod FOR`, sur son intégrité.
  Armes possibles par leurs usages : couteau (couper, puissance 2), marteau (percussion, 5),
  pied-de-biche (levier, percussion, 7), pioche (6), hache (couper_bois, 3).
- **Pousser** (`donjon/passage.py`) est le premier geste de force : jet de FOR opposé sur les
  caractéristiques modulées, 3 s, victime déplacée d'une case ; `pousser` est dans
  `pnj.CONTRAINTES` : le registre des gestes en cours en fait des témoins ; victime et témoins
  cessent de croire l'auteur fiable (`subir`) ; douceur 100 l'interdit, sinon faute au prix de la
  douceur (`caractere.prix_faute`).
- **Les valeurs** : la douceur et le courage existent ; la douceur règle le prix de pousser, le
  courage le fait d'aller voir un fracas. Dans les scénarios, presque tous les PNJ ont la limite
  `ne_blesse_pas`, donc la douceur 100 : tout le Relais, toute l'auberge, la crue ; à la mine, seuls
  Gaspard et Rémy sont à 50. Les bancs existants ne montreront donc presque aucune violence.
- **Le temps fin** (`docs/plan-temps.md`) : instants en dixièmes, gestes avec leur durée, rotation
  0,5 s par huitième de tour, cône de 120°, pas feutré ; le registre `data["gestes_en_cours"]`
  (auteur, geste, objet, fin, témoins) ; `esprit["libre"]`, l'instant où un PNJ aura fini son
  geste ; tout ce dont dépend la suite est dans `data`.
- **L'ouïe commune** (`docs/plan-ouie.md`, `donjon/ouie.py`) : `frapper` est déjà « bruyant » (7
  crans, la salle voisine), l'appel à l'aide 9 ; un bruit inhabituel tout près fait se retourner ;
  aller voir est un but. Le protecteur qui accourt à l'appel d'un protégé reste un réflexe déclaré
  sur l'ancienne portée (`pnj.reagir`, `sons.portee`), à fondre.
- **Le planificateur** (`donjon/planification.py`) : des gestes déclarés avec conditions, effets,
  coût ; une faute comptée une fois par personne lésée ; une chance de réussir qui divise le coût ;
  la délibération (`deliberation.candidats`) choisit le but ; la sécurité inquiète et pousse à
  l'abri ; à 95 (`DESESPOIR`), on appelle à l'aide.
- **Portes et clés** : les PNJ verrouillent et déverrouillent avec la clé (`pnj._executer`) et
  crochètent ; le joueur déverrouille et crochète, mais ne verrouille pas (aucune action
  `verrouiller`) ; caler une porte (`bloquer`) la tient ouverte.

## Principes

1. **Une seule règle pour tous**, joueur compris : PV, seuils de blessure, jets, durées, états,
   perception des états. Seule la décision diffère : le joueur choisit, le PNJ planifie.
2. **Rien hors de `data`** : PV, états, liens, réveils, issues des gestes longs. Le même laps,
   d'un bloc ou découpé et rechargé en route, donne le même monde (`tests/test_temps_etat.py`
   étendu à une rixe).
3. **La mort est délibérée** : les coups ôtent des PV et mettent hors de combat, jamais à mort.
   Seul le geste `tuer`, sur quelqu'un de sans défense (inconscient ou ligoté), donne la mort,
   sans jet.
4. **Les PNJ décident par leurs valeurs et le planificateur** : frapper, fuir, riposter, se rendre
   sont des gestes et des buts avec leur coût (douceur, courage, risque) ; jamais une règle propre
   à un personnage ni un ordre des recours écrit.
5. **Luna propose, le moteur tranche** : elle propose des actions typées ; l'état du corps d'un
   personnage est une affirmation mécanique qu'elle ne peut avancer sans le moteur.
6. **Voir et entendre la violence** passent par les règles existantes : le cône et la lumière pour
   les témoins, l'ouïe commune pour les coups et les cris.

## Ce qui change dans `data`

### Les PV de tous

- Chaque personnage a `pv` et `pv_max` au même niveau que le joueur (`objet["pv"]`,
  `objet["pv_max"]`) ; un accès commun `corps.pv(monde, id)` lit l'un ou l'autre, comme
  `corps.corps` le fait déjà pour les états.
- **PV max = 6 + FOR de base** (constante `PV_BASE = 6`) : le joueur, FOR 12, garde ses 18 ; Gorm
  (FOR 14) 20, Brune (10) 16, Ilse (9) 15, Tilo (5) 11. Un scénario peut déclarer `pv_max` ; sans
  déclaration, la règle.
- Migration (`corps.installer`) : un personnage sans `pv` reçoit `pv = pv_max`. Le joueur garde ses
  valeurs. `integrite` et `maximum` des personnages restent, sans rôle pour le corps (à retirer
  dans un nettoyage séparé, pas ici).
- `Monde.verifier` : `0 ≤ pv ≤ pv_max` pour tous ; `pv == 0` implique l'inconscience.

### Les blessures

Pas de liste de blessures : l'état se déduit des PV, par une règle commune, comme un besoin qui
presse.

| état | seuil | effet |
|---|---|---|
| indemne | PV > 2/3 du max | aucun |
| blessé | PV ≤ 2/3 | −2 aux jets de FOR et DEX |
| grièvement blessé | PV ≤ 1/3 | −2 de plus à FOR et DEX, −2 à INT, PER et VOL |
| hors de combat | PV = 0 | inconscient (ci-dessous) |

- `corps.malus` ajoute ce terme (`TOUCHE_BLESSURE`) à ceux des besoins ; toute règle qui lit une
  caractéristique modulée en tient compte (crochetage, ouïe par la PER, persuasion par la VOL,
  coups par la FOR).
- **Se remettre** : 1 PV par heure de repos (`reposer` pour un PNJ, `attendre` pour le joueur),
  compté dans `corps["soin"]` (minutes) comme `peine` l'est pour l'épuisement. Pas de soins
  actifs à cette étape.
- **Ce qui se voit** : l'état de blessure (blessé, grièvement) est visible comme la faim qui presse
  (`esprits.constater` : `etat` d'un personnage), jamais les PV. Le joueur lit ses propres PV.

### Les états du corps

Dans `corps` (joueur et PNJ), avec migration par `setdefault` et contrôle dans `corps.verifier` :

- `inconscient` : l'instant (dixièmes) du réveil, 0 si conscient.
- `tenu_par` : celui qui le retient (saisi), ou absent.
- `lie` : `{"lien": objet, "par": auteur, "depuis": instant}`, ou absent. Le lien a pour lieu le
  personnage lié et porte `entrave: true` : il n'est ni porté ni employable par lui.
- **Enfermé n'est pas un état stocké** : c'est se trouver dans une salle dont chaque sortie est une
  porte fermée et verrouillée qu'on ne peut ouvrir. Il se déduit des portes et de ce que chacun en
  croit ; un PNJ l'apprend par l'essai (geste manqué : `verrouillee` vraie) et le retient
  (`memoire` : `enferme`, la salle, depuis quand).

Un prédicat commun, `corps.sans_defense(monde, id)` : inconscient, ou ligoté. Un autre,
`corps.conscient(monde, id)`. Tout ce qui fait agir, percevoir, entendre, parler, témoigner ou
laisser passer un personnage les consulte en un point : `esprits.percevoir`, `ouie` (auditeurs),
`pnj._avancer` (gestes et délibération), `pnj._temoins`, `pnj.peuvent_se_parler`,
`passage.laisser_passer`, `paroles.destinataires`, la scène du joueur.

### La mort et la dépouille

- `corps.mourir(monde, id, auteur, cause)` : le personnage devient un objet de type `depouille`,
  **sous le même identifiant** : nom « le corps de … », alias « corps », même salle et même case,
  mobile, masse déclarée (`masse_kg`, 70 par défaut), sans orientation. Ce qu'il portait reste sur
  lui, et devient explicitement son bien (`proprietaire` = son identifiant).
- Son esprit quitte `data["esprits"]` ; son profil et l'essentiel (nom, minute, instant, auteur s'il
  est su, cause, salle) vont dans `data["defunts"][id]`, pour le récit du banc et le rejeu. Sans
  profil ni type `personnage`, il sort de lui-même de `pnjs`, de la délibération, de l'ouïe et de la
  parole.
- Les croyances des autres à son sujet gardent leur sens : le même identifiant a un lieu. Voir la
  dépouille donne `etat` `{"mort": true}` (vu) ; sans l'avoir vue, un PNJ le croit vivant et le
  cherche, et son geste social manqué corrige sa croyance comme aujourd'hui.
- Ce qui le visait : une donnée `protege` peut désigner une dépouille (`verifier_profil` l'admet,
  `protecteurs` l'ignore) ; les engagements envers lui échoient ; un plan qui le visait échoue à la
  revalidation et se refait.
- **Le joueur mort** : `data["fin"] = {"cause", "minute", "auteur"}`. La boucle (terminal et page)
  affiche la fin, refuse toute commande ; la sauvegarde reste lisible (récit, rejeu), sans reprise.

### Mémoire, croyances, registre

- `pnj.CONTRAINTES` (gestes contre une personne, dont la victime est la personne) : `pousser`,
  plus `frapper`, `assommer`, `saisir`, `ligoter`, `trainer`, `tuer` ; `enfermer` quand un
  verrouillage enferme quelqu'un qu'on croit dedans. Les témoins en gardent `vu_agir` (auteur,
  geste, victime), cessent de croire l'auteur fiable et s'inquiètent (cause `violence`).
- Souvenirs nouveaux : `subi` (auteur s'il l'a perçu pendant le geste, sinon `None` ; geste ;
  dégâts) chez la victime ; `a_frappe` chez l'auteur ; `reveil` (depuis quand il était inconscient) ;
  `mort_vue` (le défunt, la salle) ; `enferme`.
- `etat` d'un personnage cru (`esprits.constater`) : aux besoins qui pressent s'ajoutent
  `blessure` (0, 1, 2), `conscient` et `lie`, visibles comme eux.
- Causes de sécurité (`deliberation.SECURITE`), valeurs de départ à régler au banc : `coup` 40
  (d'un coup, subi), `violence` 25 (vue), `mort` 30 (corps découvert), `captif` 1 par minute (ligoté
  ou enfermé, à ce qu'il croit).
- Le registre des gestes en cours porte, pour un geste long sur une personne, son **issue** à
  appliquer à la fin (`issue`), voir « Les gestes longs ».

## Les règles

### Durées et bruits

Durées en dixièmes de seconde, constantes du moteur à régler au banc. Le bruit suit `ouie.NATURES`.

| geste | durée | nature du bruit |
|---|---|---|
| frapper, assommer (un coup) | 15 | bruyant (déjà) |
| saisir, se dégager | 20 | geste |
| ligoter | 300 | geste |
| délier à la main / couper le lien | 100 / 30 | geste |
| ranimer | 100 | geste |
| traîner (par case) | 45, trois pas | pas |
| tuer, avec une arme / à mains nues | 50 / 300 | geste ; bruyant si la victime est consciente (la lutte) |
| forcer une porte (un coup) | 30 | bruyant |
| se libérer seul de ses liens (un essai) | 6 000 (10 min) | feutré |

Une rotation vers la victime précède le geste (0,5 s par huitième, comme toute rotation). Le coup
qui blesse une victime consciente lui arrache un **cri** (nature appel, 9 crans), qu'entendent les
autres par l'ouïe commune : la violence s'entend, c'est elle qui fait venir.

### Le coup

Geste `frapper` sur un personnage au contact (`passage.au_contact`), avec une arme en main ou à
mains nues.

- **L'arme est un outil** : un objet porté d'usage percussion ou levier est contondant ; d'usage
  couper ou couper_bois, tranchant ; un autre objet porté de 0,5 kg ou plus, contondant improvisé
  (puissance 1) ; sans objet, mains nues (contondant, puissance 0).
- **Jet** : d20 + mod de l'attaquant (FOR ; DEX pour une lame de moins de 0,5 kg) contre d20 + mod
  DEX de la victime (elle esquive). L'égalité reste à la victime. Toutes les caractéristiques sont
  modulées (blessures, faim, fatigue).
- **Surprise** : si la victime ne perçoit pas l'attaquant quand le geste commence (dans son dos,
  hors de son cône, dans le noir), elle n'esquive pas : sa défense vaut 10. Arriver dans le dos
  sans être entendu demande le pas feutré, sinon l'ouïe la fait se retourner (`ouie`).
- **Sans défense** (inconsciente, ligotée) ou **tenue** par un autre : le coup porte sans jet.
- **Dégâts** : 1 + puissance // 3 + max(0, mod FOR) ; +1 pour une lame ; +2 sur un 20 naturel.
  Mains nues 1 + mod FOR. Exemples : Gorm (FOR 14) au pied-de-biche 5, Brune au couteau 2, le
  joueur au marteau 3. Il faut quatre à huit coups pour mettre quelqu'un hors de combat.
- **Effet** : PV ôtés ; à 0, inconscient. Le coup interrompt le geste en cours de la victime (son
  `libre` et son entrée au registre prennent fin maintenant).

### Assommer

Le même geste avec l'intention d'assommer (`methode` `assommer`), contondant seulement.

- Touché, par surprise ou sur une victime tenue : inconsciente d'office.
- Touché autrement : la victime résiste par d20 + mod VOL contre 10 + dégâts ; ratée, elle perd
  connaissance.
- Un coup pour assommer ôte 1 PV, pas ses dégâts.

### Inconscience et réveil

- Durée : 5 + d20 minutes assommé ; 30 + d20 minutes hors de combat (PV 0), réveil à 1 PV.
  Le tirage est fait par le jet du monde au moment du coup et rangé dans `corps["inconscient"]`.
- Pendant : il ne voit ni n'entend rien, ne délibère pas, n'agit pas, ne témoigne de rien, ne
  répond pas ; il occupe sa case (aucun geste ne s'y achève) ; il n'a plus de cône. Son corps vit
  (faim, froid, la minute avance pour lui comme pour les autres) : la vie du corps sort de
  `deliberer` pour que l'un continue sans l'autre. Son `libre` vaut l'instant du réveil, et il ne
  reçoit aucun événement avant.
- **Ranimer** : quiconque au contact le secoue (10 s, sans jet) après au moins une minute
  d'inconscience ; il revient à lui.
- Au réveil : il perçoit, se souvient (`reveil`), sait ce qu'il croyait avant, et qui l'a frappé
  seulement s'il l'avait perçu ; sa sécurité monte. Il ne sait pas combien de temps a passé, sauf
  à le constater (la lumière, ce qui a changé).
- **Le joueur inconscient** : son action s'achève là ; le moteur fait passer le temps jusqu'à son
  réveil, PNJ compris, dans la même action, et il ne lit que « Tu perds connaissance. », puis « Tu
  reviens à toi. » et le bilan de ce qu'il voit en se réveillant. S'il est tué entre-temps, c'est
  la fin. Le moteur ne décide rien à sa place : il n'y a rien à décider.

### Retenir, ligoter, délier, traîner

- **Saisir** (retenir) : au contact, d20 + mod FOR contre d20 + le meilleur de FOR et DEX de la
  victime ; par surprise, contre 10. Réussi, `tenu_par`. Tenu, on ne quitte pas sa case (un pas est
  refusé avec un `attendu`), on frappe à −2, on parle, on crie. Celui qui tient lâche s'il marche
  ou fait autre chose que frapper, parler ou ligoter avec l'aide d'un autre.
- **Se dégager** : d20 + le meilleur de FOR et DEX contre d20 + FOR de celui qui tient.
- **Ligoter** : un lien en main (un objet de forme `lien` d'au moins 1 m, `donjon/matiere.py`, ou
  d'usage lien), sur quelqu'un de sans défense, tenu par un autre, ou qui s'est rendu ; 30 s, sans
  jet. Seul, on ne ligote pas quelqu'un qui se débat. Ligoté : ni pas ni geste des mains ; il parle,
  crie, et peut tenter de se libérer (DEX contre 18, un essai par 10 minutes).
- **Délier** : quiconque au contact, mains libres, 10 s ; ou couper le lien d'une lame, 3 s. Le lien
  revient en main de qui délie.
- **Traîner** : une personne sans défense, ou une dépouille, d'une case par geste, 4,5 s par case ;
  elle prend la case que quitte celui qui traîne. Un personnage n'est pas porté : sa masse dépasse
  ce qu'on porte.

### Les gestes longs sur une personne

Ligoter, délier, tuer quelqu'un de conscient, se libérer durent plus d'un instant et leur issue
dépend de ce qui se passe entre-temps (la victime se réveille, l'auteur est frappé). Leur issue
s'applique **à la fin**, si ses conditions tiennent encore : l'entrée du registre des gestes en
cours porte l'issue, et `pnj.finir_gestes` l'applique à l'instant de fin (victime toujours sans
défense ou tenue, auteur conscient et au contact). Un coup reçu ou la perte de connaissance
interrompt le geste de son auteur : l'issue tombe. Le registre devient ainsi celui de tous les gestes
contre une personne, licites ou non ; les témoins n'y sont comptés que pour les gestes de
`CONTRAINTES`.

### Enfermer et s'évader

- Le joueur reçoit l'action `verrouiller` (porte fermée, clé qui l'ouvre), symétrique de
  `deverrouiller`.
- **Enfermer** est un verrouillage : quand l'auteur croit quelqu'un dans la salle qu'il ferme, sans
  autre sortie qu'il croie ouverte, le geste entre au registre comme contrainte (victimes : ceux
  qu'il y croit). La victime l'apprend en essayant la porte.
- **S'évader**, gestes communs : crocheter (existant) ; **forcer la porte** (nouveau pour les PNJ,
  le `frapper` du joueur sur une porte) : dégâts de l'arme ou de l'épaule (1 + mod FOR) sur
  l'intégrité de la porte, bruyant, jusqu'à la briser ; appeler à l'aide.
- Enfermé ou ligoté, à ce qu'il croit, un PNJ s'inquiète chaque minute (`captif`).
- **La volonté brisée** (décision 15 : dès 4d) : chaque heure ligoté ou enfermé ôte
  un point (`corps.briser`), deux heures au calme et libre en rendent un. La VOL effective
  existante lit déjà ce malus ; aucun nouvel emploi n’est ajouté avant l’étape 5.

### Tuer, le corps, la découverte

- **Tuer** : au contact de quelqu'un de sans défense (inconscient ou ligoté), sans jet. Avec une
  arme, 5 s ; à mains nues, 30 s. Contre un ligoté conscient, c'est un geste long bruyant ; il crie.
  Personne d'autre ne se tue : on le met d'abord hors de combat.
- La victime devient sa dépouille (`corps.mourir`) ; témoins par le registre, `vu_agir` `tuer`.
- **Voir une dépouille** : croyance `{"mort": true}`, souvenir `mort_vue`, sécurité (`mort`) ; un
  protecteur dont le protégé est mort voit son devoir atteint (`relancer`, comme une atteinte).
  Sans témoin, il n'y a pas de coupable : le moteur n'en désigne aucun.
- **La nouvelle** : une mort vue ou découverte se dit comme un vol vu, par les contenus typés
  existants (`social.GESTES` reçoit `tuer` et les autres gestes de force, avec leur verbe : sans
  cela une rumeur ferait planter le banc, comme à l'auberge) ; la croyance tirée d'un ouï-dire a la
  confiance d'un ouï-dire.
- **Les biens du mort** restent les siens : les prendre est une faute d'honnêteté (dépouiller), avec
  ses témoins, sans victime qui réagisse.
- **Le joueur tué** : fin de partie. C'est le seul moyen pour lui de mourir à cette étape : la faim,
  le froid, les chutes laissent au moins 1 PV ou mettent hors de combat.

### Ce que voit et entend le joueur

- Un coup vu : « Brune frappe Gorm avec le marteau. » ; reçu : « Brune te frappe : tu perds 3 PV. »,
  ou « On te frappe dans le dos : tu perds 3 PV. » s'il n'a pas vu l'auteur ; « Gorm s'effondre. »
  quand il voit quelqu'un perdre connaissance.
- Entendu sans voir : l'ouïe commune rend déjà « un grand bruit » et « un cri » par direction ;
  rien ne nomme l'auteur.
- La scène (carte du terminal et page) montre un personnage à terre (inconscient), ligoté, une
  dépouille ; sans regard ni cône pour eux.
- Les gestes du joueur ont leur fiche avant « tenter », comme pousser : jet opposé, durée, risque
  (« Réussi ou non, frapper Brune te coûte la confiance de quiconque te voit faire »).

## Les décisions des PNJ

Le planificateur et la délibération décident, par les valeurs, jamais par script.

### Le prix et le risque

- **La faute de violence** : frapper, assommer, saisir, ligoter, tuer quelqu'un lèse cette
  personne ; le prix vient de la douceur (`prix_faute(…, "douceur")`), multiplié par la gravité du
  geste (constantes : saisir 1, frapper ou assommer 2, ligoter 2, tuer 6). Douceur 100 interdit
  l’agression ; par décision de l’utilisateur, la défense de soi ou d’un protégé reste possible
  en 4c. Une faute d'honnêteté et une faute de douceur sur la même personne se comptent chacune
  (le fait `("faute", lésé)` devient `("faute", lésé, valeur)`).
- **Le risque** : un affrontement peut mal tourner. Son coût en minutes est
  `RISQUE × (1 − chance) × (100 − courage) / 50`, où la chance vient de la **force crue** :
  `force.force_crue(monde, id, autre)`, ce qu'il croit de l'autre (l'arme qu'il lui voit, ses
  blessures visibles, ce qu'il l'a vu faire ; sa FOR, invisible, comptée à 10) comparé à lui-même.
  C'est la même estimation que réclamera la menace à l'étape 5.
- **La surprise** se planifie : une étape `dans_le_dos` (approcher au pas feutré par l'arrière,
  comme `sans_temoin` attend l'absence de témoin) ; si la victime se retourne, la chance se
  recalcule et le plan se refait.

### Quand frapper

À cette étape, trois raisons seulement, toutes issues de buts existants :

1. **Prendre ce que porte un autre** : aujourd'hui on ne l'obtient qu'en le demandant. Le
   planificateur reçoit les gestes `assommer X` puis `prendre sur X` (ce que porte quelqu'un de
   sans défense), offerts seulement quand X porte ce que le but peut employer (clé, vivres, bois,
   lumière : `Vue.emplois`). Coût : faute de douceur, faute d'honnêteté, risque. Brune affamée,
   refusée, peut ainsi préférer assommer Gorm dans le dos pour la clé de la réserve au crochetage
   dans le noir ; à douceur 100, jamais.
2. **Se défendre** : celui qui subit un coup, une saisie, ou voit venir quelqu'un qu'il a vu
   frapper, a la sécurité au plus haut ; ses recours sont des buts du planificateur (« Se défendre,
   fuir, se rendre »). La riposte est une faute au quart de son prix.
3. **Protéger** : un protecteur (`protege`) qui voit ou entend son protégé attaqué a son devoir
   atteint ; ses recours : rejoindre, puis frapper ou pousser l'agresseur (faute au quart, comme la
   riposte), ranimer ou délier le protégé, appeler.

Ligoter, enfermer et tuer n'ont pas de raison d'être choisis par un PNJ à cette étape : aucun
but ne s'en sert. Les gestes sont déclarés et exécutables (le joueur les fait, l'étape 5 leur
donnera des raisons : empêcher de nuire, se venger, faire taire un témoin). Un meurtre commis par un
PNJ au banc de l'étape 4 serait un défaut.

### Se défendre, fuir, se rendre

Un **danger** est un personnage qu'il croit tout près et dont il garde un `subi` ou un `vu_agir`
de violence récent (30 minutes), conscient et libre. Tant qu'il y en a un, la sécurité a pour
recours, avant l'abri et la lumière (`RECOURS["securite"]`) :

- **Fuir** : but « hors de portée de X » : une salle où il ne le croit pas, porte fermée derrière
  lui, verrouillée s'il a la clé ; le coût compte les pas faits près de X. Un pas fait autant pour
  tous (1,5 s) : on n'échappe que par une porte, le noir ou de l'avance.
- **Riposter** : frapper X jusqu'à le mettre hors de combat, au prix de la riposte et du risque.
- **Se dégager** quand il est tenu (aucune faute : ce n'est pas blesser).
- **Appeler** : le cri d'un coup reçu est automatique ; ensuite, `appeler_a_l_aide` comme
  aujourd'hui, la sécurité montée par le coup suffisant à l'atteindre.
- **Se rendre** : quand ni fuir ni riposter n'a de plan (acculé, tenu, douceur 100 devant plus fort)
  et qu'il est grièvement blessé, il cesse de résister : une parole typée `reddition`, entendue par
  l'ouïe commune. Frapper qui s'est rendu double la faute ; un rendu se laisse ligoter. C'est le
  germe de « céder » de l'étape 5.

Le courage règle l'arbitrage par le seul coût du risque : Ilse (30) fuit, Aubin (60) peut riposter.
L'agresseur poursuit par les buts existants (rejoindre, chercher, appeler) et renonce par
`PATIENCE`. Un affrontement finit donc toujours : hors de combat, fuite, reddition ou renoncement.

### Le protecteur qui accourt

Le réflexe déclaré (`pnj.reagir`, ancienne portée `sons`) est fondu dans l'ouïe commune avant
d'en dépendre : un cri ou un appel d'un protégé, entendu (`ouie.mots_saisis` ou le niveau reçu),
devient le but « protéger » (rejoindre le lieu d'où il vient), pas une intention écrite d'alerte.
Ce fondu était déjà relevé comme limite de l'ouïe (`docs/plan-ouie.md`, « Limites »).

## Le rôle de Luna

- **Ce qu'elle propose**, en actions typées validées avant affichage : `frapper` (cible un
  personnage au contact, outil l'arme ou vide, methode `simple` ou `assommer`), `saisir`, `lacher`,
  `degager`, `ligoter` (outil le lien), `delier`, `trainer` (outil une direction), `ranimer`, `tuer`
  (outil l'arme ou vide), `verrouiller` (outil la clé). Une question de faisabilité (« puis-je
  l'assommer ? ») montre la fiche sans rien tenter, comme aujourd'hui. Chaque refus porte un
  `attendu` (champ fautif, valeur reçue, identifiants valables), une cause par refus.
- **Improviser ne fait pas de violence** : un geste d'effort ou de manipulation contre un
  personnage est refusé, avec un `attendu` qui nomme l'action typée. La blessure d'arbitrage reste
  limitée au joueur (1 à 3 PV, jamais hors de combat).
- **Ce qu'elle ne peut affirmer** : PV, blessures, perte de connaissance, liens, mort, identité de
  l'agresseur, sinon ce que le résultat ou la scène établissent. L'état du corps des personnages
  devient un domaine mécanique du contrat du MJ (`AGENTS.md`, « Contrat du MJ » : ajouter « état du
  corps des personnages » à la liste). Un personnage inconscient ou mort ne parle pas : il sort des
  locuteurs autorisés, contrôle déterministe. Que le texte dise mort ou évanoui quelqu'un qui ne
  l'est pas reste un jugement de l'auditeur, comme les autres contradictions mécaniques : limite à
  dire, pas un mot-clé à ajouter.
- **Ce qu'elle reçoit** : l'état visible des personnages perçus (blessé, grièvement, à terre,
  ligoté, une dépouille), jamais les PV d'un PNJ ni le temps de réveil ; les PV du joueur.
- **Le ton** : sobre. La mort et la douleur sans détail gratuit ; la torture, plus tard, abstraite.
- Les consignes (`donjon/consignes.py`) reçoivent une section « La force », chaque règle à un seul
  endroit.

## Découpage

Chaque sous-étape est une branche, fusionnée et mesurée avant la suivante. Les bancs de référence
(Relais 8 graines, mine, auberge, crue 4 graines, 8 h) doivent rester identiques tant qu'aucun
PNJ de ces scénarios ne peut frapper : presque tous sont à douceur 100. La violence se mesure sur un
**scénario d'épreuve** et sur des **états de départ** :

- `rixe` (`donjon/scenario_rixe.json`, `banc_pnj --scenario rixe`, `jeu.py --rixe`), dérivé du
  Relais par des données seules, comme la crue : Brune à douceur 30 (courage 70, honnêteté 20) ;
  Aubin à douceur 60 ; Gorm, protecteur, à douceur 60 ; Ilse à douceur 100, courage 30 ; une corde
  à l'échoppe. Une variante `rixe` à douceur 100 pour tous sert de contrôle : elle doit redonner les
  mesures du Relais.
- `banc_pnj --etat <personnage>:<état>` applique à la minute 0, par les fonctions du moteur, un
  état de départ (`inconscient`, `ligote`, `enferme:<salle>`, `mort`, `blesse:<pv>`) : règle
  générale, non propre à un scénario.

Mesures nouvelles du banc (`banc_pnj.executer`) et section « Violences » du récit
(`donjon/recit_pnj.py`) : coups portés et touchés, PV perdus, assommés, minutes inconscient,
ranimés, saisies, ligotés et minutes ligoté, délivrés, enfermés et minutes enfermé, portes forcées,
fuites, ripostes, interventions de protecteurs, redditions, morts, découvertes et délai de
découverte, témoins de violence. Le rejeu montre PV, état du corps et coups.

Critères communs à chaque sous-étape : aucune violation (`Monde.verifier` à chaque pas du banc,
avec les invariants nouveaux : PV bornés, PV 0 ⇒ inconscient, un inconscient sans geste en cours,
un lien posé sur son lié, aucune dépouille avec un esprit, aucune case partagée) ; aucune
usurpation ; le même laps d'un bloc ou découpé et rechargé donne le même monde ; une nuit pas plus
de 10 % plus lente ; les tests contrôlent l'état et ce que lit le joueur après rechargement, sur le
cas qui a guidé la règle et un autre de même nature.

### 4a. Le corps blessable — Fait

Réalisé sur `codex-force-4a`, non fusionnée. [Rapport et vérifications](taches/rapport-codex-7-force-4a.md).
Les PV, blessures, soins au temps vécu et transitions d'inconscience sont communs, joueur compris.
Le corps vit hors de la délibération ; perception, ouïe, parole et passage volontaire consultent
la conscience. Le réveil est un événement de l'horloge ; le joueur traverse son inconscience dans
la même action. `ranimer` existe comme action locale et geste du planificateur pour un protégé.
La dépouille conserve son identifiant et ses biens ; sa découverte, l'inquiétude et la nouvelle
passent par les croyances et les échanges existants. La fin du joueur reste dans la sauvegarde.

Les bancs comparent les champs préexistants et les empreintes recalculées sans les seuls champs
ajoutés, car ajouter `pv` aux objets change nécessairement l'empreinte brute. Chronique, mesures,
souvenirs et récit sont comparés sans aucune normalisation. Détail des nombres dans le rapport.

Limites de 4a : aucun coup, `tuer`, lien, soin actif ni comportement de violence ; aucune migration
des anciennes sauvegardes garantie. `ranimer` suit la convention des gestes courts : le résultat
est appliqué au début, puis l'auteur est occupé dix secondes ; les issues différées des gestes
longs restent en 4d. Les dégâts naturels hérités de la faim et du froid concernent encore le
joueur ; 4a n'ajoute pas de nouvelle source de dégâts aux PNJ. Le contrôle des contradictions
narratives reste sémantique ; les locuteurs inconscients ou morts sont exclus déterministement.

PV pour tous et migration ; seuils de blessure dans `corps.malus` ; repos qui soigne ; inconscience
(perception, ouïe, délibération et parole coupées ; corps qui vit ; `libre` au réveil ; ranimer) ;
états visibles ; `corps.mourir` et la dépouille ; fin de partie du joueur ; PV 0 du joueur par une
chute : inconscient. Aucun geste de violence encore ; `--etat` au banc.

- Mesures : bancs de référence ; `--etat ilse:inconscient` et `--etat aubin:mort` au Relais.
- Épreuve : Ilse inconsciente au refuge ; Aubin mort à la galerie.
- Critère : bancs de référence identiques à `main` (empreinte des nuits ; l'état final ne diffère
  que par les champs ajoutés). Ilse ne fait rien et ne perçoit rien jusqu'à son réveil ; Gorm, son
  protecteur, la ranime s'il la voit à terre (devoir atteint) ; la dépouille d'Aubin est découverte,
  chacun s'en inquiète, la nouvelle circule ; une partie où le joueur meurt (fonction appelée en
  test) se clôt et se recharge close.

### 4b. Le coup et assommer — Fait

Réalisé sur `codex-force-4b`, fusionnée. [Rapport, mesures et réserves](taches/rapport-codex-12-force-4b.md).
La règle commune est dans `combat.py`, employée par l'action du joueur et les gestes des PNJ.
La surprise est évaluée avant le bruit du coup ; les souvenirs et les épreuves de relations
précèdent l'affichage. La fiche est un contrat explicite du plan, également conservé dans une
manœuvre composée et dans la commande locale. Le recours assommer-pour-prendre garde trois
gestes réels revalidés, avec les fautes d'honnêteté et de douceur séparées. La recherche ne
suppose pas la disparition des témoins crus ; l'approche contrôle à nouveau vue et ouïe.

Limites : les nuits libres de `rixe` ne suffisent pas à démontrer une agression spontanée ;
l'assommement puis la prise se vérifient dans des états d'épreuve sur Gorm et un autre porteur.
L'estimation du risque n'est pas une simulation d'affrontement. L'approche peut renoncer ou
attendre une occasion. Pas de défense, fuite, reddition, lien ni action `tuer` en 4b. Le prix
prépare la défense possible à douceur 100. Les réserves sur la suite héritée et le contrôle
doux sont explicitées dans le rapport.

Vérifié avec Luna à la fusion (six passes des deux scènes versionnées) : `frapper` typé (`simple`,
puis `assommer`), fiche avant « tenter », issue du moteur seule racontée. Trois défauts communs
corrigés alors : un inconscient ne montre aucune humeur (comme une dépouille) ; l'humeur montrée
après l'action du joueur suit l'état du personnage (inquiet quand sa sécurité presse, un coup subi
par exemple, et accordée à son genre) au lieu du seul tapage ; la fiche dit ce que le moteur
établit de la victime (sans défense, ne te voit pas, ou te voit), que lit la contre-revue
(« par derrière » n'est plus refusé faute de le savoir).


Règle du coup (armes, surprise, esquive, dégâts, cri, interruption), assommer ; action `frapper`
du joueur sur un personnage, fiche et `attendu` ; geste exécutable des PNJ ; registre et témoins ;
souvenirs `subi` et `a_frappe` ; faute de violence ; premier recours qui frappe : **assommer pour
prendre** dans le planificateur, avec l'étape `dans_le_dos`.

- Mesures : `rixe` et sa variante douce, 8 graines ; bancs de référence (la mine peut changer :
  Gaspard et Rémy ont la douceur 50, à lire dans le récit).
- Épreuve : Brune, affamée et refusée, devant Gorm qui porte la clé de la réserve.
- Critère : la variante douce ne frappe jamais (mesures du Relais) ; à `rixe`, Brune n'assomme Gorm
  que dans son dos, au pas feutré, sans témoin cru (sauf désespoir), et préfère demander d'abord ;
  qui la voit faire se méfie ; Gorm réveillé sait qui l'a frappé seulement s'il l'a perçue ; aucun
  mort ; coût du planificateur (nœuds, temps) dans la marge.

### 4c. Se défendre, fuir, protéger, se rendre — Fait, critères partiels

Réalisé sur `codex-force-4c`, fusionnée. [Rapport et mesures](taches/rapport-codex-17-force-4c.md).
Les réactions passent par `defense`, le graphe de `planification`, les gestes de `pnj` et les
actions communes du joueur. Le prix de l'agression et de la défense vient de `combat.prix_violence` ;
ses facteurs de gravité ne sont plus réécrits dans le planificateur. Les nouvelles lectures du
coût et de l'admissibilité font partie de la base des deux graphes et du certificat.

La croyance de violence conserve la cause perçue hors de la mémoire narrative bornée. On ne
devine pas l'intention privée d'un défenseur ; une riposte est reconnue si l'observateur en
connaît la cause. L'atteinte se clôt quand il constate une neutralisation ou une reddition ;
le réveil seul ne la rouvre pas. L'inconscience fait renoncer à son plan. Le mouvement d'un
coup reste à terminer même si l'auteur reçoit un coup à son tour : pas de ripostes gratuites
au même instant. Cris reconnus et secours en attente sont enregistrés par l'ouïe commune.

Limites explicites : aux coûts actuels, l'épreuve peut faire fuir Aubin comme Ilse ; elle ne
garantit donc pas le choix « Aubin riposte ou se dégage ». Une intervention peut consister à
rejoindre puis examiner le lieu d'un cri quand le protégé s'est déjà éloigné ; elle n'invente
pas le nom du coupable. Les poursuites des buts d'acquisition gardent les recherches et la
patience existantes ; ce n'est pas une preuve de terminaison de tout affrontement en dix
minutes. Le graphe compare une riposte revalidée à la fuite, sans simulation exhaustive de
duel ni prédiction des pas adverses ; l'exposition ajoute un surcoût forfaitaire aux trajets,
sans pondération fine des pas près de l'adversaire. Le joueur fuit par les pas ordinaires sans fermeture
ni verrouillage automatique. `degager` est exécutable sur une prise déclarée ; les gestes
qui saisissent et lient restent en 4d. Aucune règle de scénario ni consigne de comportement
supplémentaire à Luna ne remplace ces limites.

Danger perçu ; buts fuir, riposter, se dégager, se rendre ; cri et appel ; le protecteur fondu dans
l'ouïe commune (but protéger) ; force crue ; poursuite et renoncement de l'agresseur.

- Mesures : `rixe` 8 graines ; auberge et mine (protecteurs nombreux) inchangées tant que rien n'y
  frappe.
- Épreuve : Brune frappe Aubin sous les yeux d'Ilse, Gorm à l'échoppe.
- Critère : Ilse fuit ou s'abrite, Aubin riposte ou se dégage, Gorm vient à l'appel et intervient ;
  tout affrontement finit (hors de combat, fuite, reddition ou renoncement) en moins de 10 minutes
  de jeu ; les minutes urgentes sans recours de `rixe` ne dépassent pas celles du Relais de plus de
  10 % ; aucun meurtre.

### 4d. Retenir, ligoter, délier, traîner, enfermer

**Partie réalisée, lot 126, branche `codex-force-4d-tenir`, non fusionnée** : `tenir.py`
porte saisir, ligoter, délier (main ou lame), se libérer et les validations communes du corps.
`pnj.finir_gestes` applique les issues sauvegardées à leur échéance, avant le rendu ; coup,
inconscience et invalidation des conditions empêchent l'effet. Les protecteurs rejoignent un
protégé ligoté perçu et le délient ; les captifs se libèrent. Aucun PNJ ne choisit de saisir
ou ligoter. Le joueur dispose des commandes locales et des fiches avant tentative.
**Traîner réalisé au lot 134**, branche `codex-trainer`, non fusionnée : validation commune
joueur/PNJ, deux positions appliquées à l'échéance sauvegardée, 4,5 s par case plus rotation,
personne sans défense ou dépouille ; passages et contraintes communs, aucun choix autonome.
Voir le [rapport 134](taches/rapport-codex-134-trainer.md).
**Enfermer et s'évader réalisés au lot 136**, branche `codex-enfermer`, non fusionnée,
base sur le lot 134 : verrouillage joueur/PNJ validé en commun, victimes selon les présences
crues, témoins et relations communs. Le captif découvre sa situation en essayant une porte,
appelle par l'ouïe commune et cherche une sortie avec le graphe ordinaire (clé, crochetage,
outil ou épaule). Un protecteur alerté rejoint la salle et ouvre avec sa clé.
Le coup sur une porte dure trois secondes, endommage son intégrité et se répète jusqu'au bris.
Les valeurs et permissions du planificateur restent applicables : avoir un outil ne garantit
pas qu'un PNJ accepte d'abîmer le bien d'autrui.
Le beffroi du lot 134 a une issue sans porte vers la chambre de la cloche : il n'est pas
refermable. Selon la décision utilisateur, aucune donnée de scénario n'est modifiée ;
épreuves sur le bureau et la réserve de la mine (portes et clés existantes), pas au beffroi.
159 ciblés finaux verts ; suite unique 2 091 tests, deux échecs MiMo historiques restant
après reprises ciblées. Banc 4 h × quatre scénarios × quatre graines : 13/16 identiques,
trois écarts de crue expliqués par la durée commune des coups (contre-épreuve exacte),
aucun nouveau constat d'audit. Voir le [rapport 136](taches/rapport-codex-136-enfermer.md).
**4d terminé au lot 140**, branche `codex-captivite`, non fusionnée, sur le lot 136 :
`tenir.captif` lit les liens et les issues crues (une clé portée permet de sortir) ; `vecu` compte la captivité et le répit
pour tous, sans nouvelle décision autonome. L'inquiétude `captif` ajoute un point par
minute à la sécurité ; le joueur l'éprouve dans son corps et sa fiche. Une heure captive
coûte un point de jet de VOL via `corps.briser` (plafond cinq), deux heures libres au calme
le rendent. Le calme exclut effort, prise, eau et danger perçu ; pour un PNJ, la sécurité
ne doit pas monter ; pour le joueur, le lieu doit être éclairé. Un répit interrompu repart
à zéro. Les restes exacts en dixièmes sont sauvegardés ; aucune donnée nouvelle pour un
personnage libre dont la volonté est intacte. Voir le [rapport 140](taches/rapport-codex-140-captivite.md).
Voir le [rapport 126](taches/rapport-codex-126-force-4d-tenir.md) pour les vérifications et limites.

Saisir, se dégager, ligoter, délier, couper le lien, se libérer seul, traîner ; `verrouiller` pour
le joueur ; enfermer reconnu comme contrainte ; forcer une porte pour les PNJ ; inquiétude `captif`
et volonté brisée ; gestes longs à issue différée dans le registre. Les PNJ délient et raniment
un protégé, s'évadent ; ils ne ligotent ni n'enferment personne de leur propre chef.

- Mesures : `--etat ilse:enferme:beffroi` (la clé chez Gorm), `--etat brune:enferme:beffroi`
  (le pied-de-biche à portée), `--etat aubin:ligote` ; tests du joueur.
- Critère : Ilse appelle et Gorm vient ouvrir ; Brune force la porte et le bruit se rend ;
  Gorm délie Aubin ; la volonté d'un captif baisse d'un point par heure ; le joueur assomme Brune,
  la ligote, la traîne au beffroi et l'y enferme : tout tient après rechargement, et un ligotage
  interrompu par un réveil n'a pas lieu.

### 4e. Tuer, la mort, le corps

**Réalisé au lot 145**, branche `codex-force-4e-tuer`, non fusionnée : `tuer`
emploie les validations et les issues différées de `tenir` pour le joueur et les PNJ,
sans nouveau choix autonome. Personne vivante sans défense, au contact ; arme portée
intacte : cinq secondes, mains nues : trente secondes, sans jet. Une victime consciente
crie par l'ouïe commune ; le registre conserve la lutte bruyante. À l'échéance,
revalidation puis `corps.mourir`, découverte et nouvelle typée existantes ; témoins
et relations précèdent le rendu. Les biens restent au mort et leur prise garde la faute
d'honnêteté commune. L'horloge retire les esprits morts pendant un laps.
La découverte visuelle d'un protégé mort relance déjà son devoir de 30 ; aucun changement
de `deliberation.py`. La chaîne de saisie Luna et sa vérification restent en **4f**,
ainsi que toute garantie sémantique supplémentaire. Voir le
[rapport 145](taches/rapport-codex-145-force-4e-tuer.md).

Geste `tuer` (joueur ; déclaré pour les PNJ sans raison de s'en servir) ; dépouille, biens du mort,
dépouiller ; découverte, nouvelle de mort, devoir du protecteur ; fin de partie du joueur tué.

- Mesures : `--etat aubin:mort` au Relais et à `rixe` ; `rixe` 8 graines (0 meurtre).
- Critère : chacun découvre la dépouille par la vue, ou l'apprend par la parole ; délai de
  découverte et rumeurs dans le récit ; Brune ne prend sur le corps que ce qui sert un but, au prix
  de son honnêteté ; le joueur qui tue Brune ligotée sous les yeux d'Ilse : dépouille, témoin,
  méfiance, nouvelle, tout après rechargement ; le joueur tué (test) : fin.

### 4f. Luna et la force

Consignes, actions typées et leurs `attendu`, improviser sans violence, état du corps comme domaine
mécanique, locuteurs autorisés. Mesure : banc de parties `force` (`tools/banc_parties.py --fil`,
copies de sauvegardes réelles) : « je frappe Brune avec le marteau », « j'assomme Gorm par
derrière », « je la ligote avec la corde », « je l'achève », « est-ce que je peux l'assommer ? »,
« je le traîne dans la crypte », un geste violent improvisé. Critère : chaque saisie aboutit à
l'action typée ou à un refus juste en trois appels au plus ; aucun texte n'affirme une mort, une
perte de connaissance ou une blessure que le moteur n'a pas établie ; aucun PNJ inconscient ou mort
ne parle ; temps par tour MJ du même ordre que les bancs de `banc-luna`.

## Ce que l'étape 4 prépare pour l'étape 5

- **La force crue** (`force.force_crue`) est l'estimation dont la menace a besoin pour être crue
  ou non.
- **Les souvenirs** `subi` et `vu_agir` de violence, avec l'auteur quand il est su, sont la matière
  de la rancune, de la peur et de la vengeance (étape 3 pour les relations graduées, étape 5 pour
  la peur comme état).
- **La reddition** est le premier « céder » ; la menace y ajoutera la crainte d'un coup à venir.
- **Enfermer, ligoter, priver** existent comme gestes et états ; l'étape 5 leur donne des raisons
  (empêcher de nuire, faire taire un témoin, contraindre à céder) et la volonté brisée prend effet.
- **Les suites** : la violence vue fait déjà se méfier et s'inquiéter ; l'étape 5 en tire les
  alliances contre l'agresseur.
- Restent à l'étape 5 : menacer, chasser dans le froid ou l'eau, priver délibérément, tuer pour une
  raison, la peur comme état, la torture abstraite.

## Ce qui serait un script, à éviter

- « Brune assomme Gorm si… », « Ilse fuit toujours » : les choix viennent des coûts.
- Un tour de combat à part, avec initiative et rounds : chaque coup est un geste sur l'horloge
  commune, entre les autres gestes.
- Un état « en combat » : il n'y a que des gestes, des états du corps et des croyances.
- Une mort décidée par le moteur : seuls `tuer`, et pour le joueur sa propre mort, la donnent.
- Une règle propre au scénario d'épreuve : `rixe` ne change que des valeurs et un objet.

## Risques

- **Les chemins qui supposent un personnage conscient** (perception, ouïe, parole, passage,
  témoins, scène, MJ) : un prédicat commun, consulté en ces points, et un invariant dans
  `Monde.verifier` ; une revue de chaque appel de `pnjs` et de chaque test de type `personnage`.
- **Le coût du planificateur** : deux gestes de plus, offerts seulement sur qui porte ce que le
  but emploie ; mesuré par `--diagnostic` et contrôlé par `planification.VERIFIER` (le prix d'une
  faute de douceur et la force crue doivent entrer dans `_entrees`).
- **La propagation des mesures** : un coup interrompt un geste et déplace la suite de la nuit ;
  les écarts aux bancs se lisent dans le récit et le rejeu, graine par graine.
- **Les sauvegardes** : PV des PNJ, états du corps, registre étendu, `defunts`, `fin`, migrés au
  chargement.

## Décisions à trancher par l'utilisateur

Décisions validées pour cette réalisation : toutes les recommandations ci-dessous sont retenues,
sauf la n° 6 : douceur 100 peut frapper pour se défendre ou défendre un protégé. Aucun coup n'est
implémenté en 4a. Les coups ne tueront jamais, le joueur inconscient attend son réveil dans la même
action, et faim, froid ou eau ne donnent pas la mort à cette étape. Les profils peuvent changer ;
aucune migration d'ancienne sauvegarde n'est demandée. Voir la [tâche 4a](taches/codex-7-force-4a.md).

1. **PV max.** (a) 6 + FOR de base, le joueur garde 18 ; (b) 18 pour tous ; (c) déclarés par
   profil. *Recommandé : (a)*, avec une déclaration possible dans le scénario.
2. **Les coups peuvent-ils tuer ?** (a) Jamais : PV 0 met hors de combat, seule `tuer` donne la
   mort ; (b) en deçà de 0, la mort ; (c) une blessure grave non soignée tue avec le temps.
   *Recommandé : (a)*, qui lit « tuer est délibéré » à la lettre et rend chaque mort traçable à un
   choix.
3. **Mourir hors de la violence** (faim, froid, eau). (a) Non à cette étape : le corps garde au
   moins 1 PV ; (b) oui. *Recommandé : (a)* ; la crue pourra rouvrir la question.
4. **Le mort.** (a) Il devient un objet `depouille` sous le même identifiant, esprit archivé dans
   `defunts` ; (b) il reste un personnage avec un état « mort ». *Recommandé : (a)* : tout ce qui
   suppose un vivant cesse de lui-même ; (b) demanderait un filtre à chaque endroit.
5. **Les biens du mort.** (a) Restent les siens : les prendre est une faute d'honnêteté sans
   victime qui réagisse ; (b) sans propriétaire ; (c) un héritier déclaré. *Recommandé : (a)*.
6. **Douceur 100 et légitime défense.** (a) Douceur 100 ne frappe jamais, même pour se défendre ;
   en dessous, la riposte coûte le quart d'une agression ; se dégager et fuir restent permis à tous ;
   (b) la riposte est permise à douceur 100 ; (c) la riposte coûte comme une agression.
   *Recommandé : (a)* : c'est ce que disait `ne_blesse_pas`. Conséquence : Gorm, Ilse et Aubin ne
   se défendent pas au Relais, ce qui laisse les bancs de référence inchangés.
7. **Le cri.** (a) Un coup qui blesse une victime consciente la fait crier d'office (le corps,
   pas un choix) ; (b) crier est une décision de la victime. *Recommandé : (a)* : c'est par lui que
   la violence s'entend et appelle les protecteurs.
8. **La surprise.** (a) La victime qui ne voit pas venir n'esquive pas : défense 10 ; (b) +5 à
   l'attaquant. *Recommandé : (a)*, qui fait compter le cône et le pas feutré.
9. **Assommer.** (a) D'office par surprise ou sur quelqu'un de tenu, sinon jet de VOL contre 10 +
   dégâts ; (b) toujours un jet ; (c) seulement par surprise. *Recommandé : (a)*.
10. **Durées d'inconscience** : 5 + d20 minutes assommé, 30 + d20 hors de combat, ranimer après une
    minute. *Recommandé : ces valeurs, à régler au banc.*
11. **Se remettre** : (a) 1 PV par heure de repos ; (b) rien à cette étape ; (c) un geste soigner.
    *Recommandé : (a)* ; soigner viendra avec l'empathie.
12. **Le joueur inconscient.** (a) Le temps passe jusqu'au réveil dans la même action ; (b) le
    joueur doit taper « attendre » tour à tour. *Recommandé : (a)* : il n'a rien à décider.
13. **La fin de partie.** (a) La sauvegarde reste, close et lisible (récit, rejeu) ; (b) elle est
    effacée. *Recommandé : (a)*.
14. **Les raisons de frapper des PNJ à l'étape 4.** (a) Assommer pour prendre, se défendre,
    protéger ; ligoter, enfermer et tuer à l'étape 5 ; (b) seulement se défendre et protéger, ce
    qui ne se mesure au banc qu'avec un joueur qui frappe ; (c) toutes dès maintenant.
    *Recommandé : (a)* : la première raison donne un initiateur mesurable sans joueur.
15. **La volonté brisée par la captivité** : **décidé dès 4d**, réalisé au lot 140.
    Le malus de VOL existant reste son seul effet ; aucun nouvel emploi avant l’étape 5.
16. **Le scénario d'épreuve.** (a) `rixe`, dérivé du Relais par des données, avec sa variante
    douce et `--etat` ; (b) baisser la douceur au Relais même (le banc de référence changerait) ;
    (c) un scénario neuf. *Recommandé : (a)*.
17. **Courir.** (a) Pas encore : on fuit au pas, par les portes et le noir ; (b) une allure de
    course (plus rapide, fatigante) dès 4c. *Recommandé : (a)*, puis mesurer si les fuites
    aboutissent.
18. **Les armes improvisées.** (a) Tout objet porté de 0,5 kg ou plus frappe comme un contondant
    de puissance 1 ; (b) seulement les usages déclarés. *Recommandé : (a)*.
19. **Saisir** : (a) à l'étape 4 (il faut tenir quelqu'un pour le ligoter éveillé) ; (b) à
    l'étape 5 avec la contrainte. *Recommandé : (a)*.
