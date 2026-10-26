# Plan : relations graduées, lire les autres, influencer par la parole

Conception détaillée de l'étape 3 de `docs/plan-social.md` (« Ordre proposé »). Document de
conception, à valider : aucune règle ci-dessous n'est encore dans le moteur. Les nombres sont des
points de départ à régler au banc, sur plusieurs graines et plusieurs scénarios, jamais par
personnage.

Ce que l'étape doit apporter : des relations graduées entre personnages, qui remplacent la
croyance `fiable` vrai ou faux ; des émotions passagères ; leurs **signes**, produits par le
moteur et perçus avec les règles communes de la vue et de l'ouïe ; une **lecture** de ces signes
par la perspicacité ; une influence par la parole qui ne donne plus seulement des faits mais des
**propositions** et des **avis**, et des **disputes** que l'on peut voir. Des relations qu'on ne
perçoit pas ne s'éprouvent ni au banc ni en jeu : chaque sous-étape livre ses signes et sa mesure.

## 1. Point de départ

### 1.1 La relation aujourd'hui : une croyance `fiable`

Une croyance de l'esprit, `croyances[autre]["fiable"]`, booléenne, avec source, minute et
confiance (`esprits._croyance_valide`). Les scénarios la posent en savoir à 0,7 (`fiable` vrai
partout au Relais et à la crue ; à la mine 33 vraies sur 36, à l'auberge 29 sur 32).

**Qui l'écrit à faux** : le témoin d'un geste illicite ou d'une contrainte (`pnj._temoins`) ; le
propriétaire qui voit son bien aux mains d'un autre (`esprits._vu_porter`) ; le mensonge découvert
ou démenti (`esprits.reviser`, `echanges.affirmer`, `social._adopter`) ; la rumeur crue
(`social._adopter`) ; l'aveu (`social.recevoir`) ; la victime d'une poussée (`passage`) ; le vol
surpris du joueur (`vol.appliquer`). **Qui l'écrit à vrai** : le savoir de départ, et la part
servie (`echanges.servir` : « il sait gré »). Rien d'autre ne la fait remonter : une méfiance ne
se lève jamais, sinon par une part reçue.

**Qui la lit** (une vingtaine de sites, tous en tout ou rien) :

| site | règle actuelle |
|---|---|
| `paroles.jet_persuasion` | DD −2 si fiable, +2 sans croyance, +6 si méfiant |
| `echanges.demander`, `confier` | refus d'office « mefiance » |
| `social._auditeur`, `_croit_encore` | on ne confie rien à qui l'on croit peu fiable ; une nouvelle se répète tant que l'accusé n'est pas cru fiable |
| `ouie` (interprétation) | le bruit de qui l'on se méfie se surveille |
| `pnj.appeler` | on ne répond pas à qui l'on se méfie |
| `passage._refus` | méfiance : on ne s'écarte pas |
| `deliberation.autour`, `ressentir` | compagnie fiable rassure, présence méfiante inquiète |
| `deliberation._plan_abri`, `pnj._rejoindre_un_proche` | l'abri est là où se tient quelqu'un de fiable |
| `deliberation._delegue`, `confie_a_autrui` | une pulsion confiée au joueur attend tant qu'on le croit fiable |
| `vol.mefiance`, `moteur` (humeur) | « X semble méfiant » |
| `paroles.esprits_interlocuteurs`, `stratege` | « croit que X est digne de confiance » ; affirmer « fiable oui/non » |
| `recit_pnj`, `banc_pnj` (`mefiances`) | ce qu'ils pensent les uns des autres |

### 1.2 Autour de la relation

- `data["relations_pnj"]` (soupçon 0 à 3, vols surpris, dernier objet) ne vaut qu'envers le
  joueur ; `objet["humeur"]` (« méfiant », « inquiet », « calme ») en dérive et s'annonce au
  joueur (« X semble méfiant. ») : une interprétation donnée pour un fait, et Luna la reçoit
  (`dialogues.interlocuteurs`).
- Les souvenirs nomment déjà presque tout ce qui fait une relation : `vu_agir`, `vol_surpris`,
  `vu_porter`, `mensonge_*`, `rumeur`, `refus`, `nourri`, `recu`, `pret`, `promis`,
  `engagement_pris/tenu/abandonne`, `a_prevenir`, `pousse`, `a_pousse`, `passage_demande`. Mais la
  mémoire est bornée à 40 et les paroles surprises l'encombrent (une soixantaine par nuit à la
  mine, `docs/plan-ouie.md`, « Limites ») : rien de durable ne peut en dépendre.
- **Un premier signe existe** : ce qui presse le corps d'un personnage se voit (`esprits.constater`,
  croyance `etat` : faim, chaleur, repos), joueur compris ; servir un protégé l'emploie.
- **Des comportements relationnels existent** sans être lus : rester près de qui l'on croit fiable
  à l'abri (`pnj._rejoindre_un_proche`, « X reste près de Gorm ») ; se retourner au bruit d'un
  méfiant ; guetter qu'un témoin s'en aille avant un geste illicite (Brune guette 31 minutes,
  `docs/plan-vue.md`). L'auteur d'un geste illicite sait qui l'a vu faire (registre
  `gestes_en_cours`, `se_sait_vu`), sans le retenir dans son esprit.
- PSY existe pour tous (10 par défaut) et ne sert à rien. Empathie, loyauté et fierté sont des
  données presque sans règle (la fierté joue dans `passage`, le courage dans `ouie`).
- La chance qu'un autre prête est une constante (`planification.PRET = 0,5`), pas ce que le PNJ
  croit de lui (`docs/plan-planificateur.md`, « Limites »).
- Aucun avis : tous jugent la crue par la même règle, les avis divergents viennent seulement de ce
  que chacun a vu (`docs/plan-crue.md`, « Étape 3 faite »).

### 1.3 Chantiers en cours dont ce plan dépend

- **`voix`** (non fusionné, `donjon/voix.py`) : connaître de vue et connaître une voix se
  séparent ; une voix inconnue est retenue (`voix_entendues`) avec ce qu'elle a prétendu
  (`se_dit`) et si on la sait menteuse ; se nommer est une affirmation pesée ; la signature d'une
  voix est l'identifiant de son porteur, jamais montré. Surtout, **toute confiance perçue passe
  par `voix.fiabilite(auditeur, locuteur)`** et toute source de ouï-dire par `source_dite`
  (« dit:X » ou « dit:voix:X »). C'est le point où les relations graduées se brancheront : on
  n'éprouve sa relation à quelqu'un que si l'on sait que c'est lui. L'imitation d'une voix et la
  méfiance envers une voix connue viendront plus tard par `voix.reconnaitre`.
- **`echanges-argent`** (non commencé dans son arbre) : prêt, permissions déléguées, prix d'une
  pièce propre à chaque PNJ selon ses besoins hors scène et ses valeurs. Les propositions (§ 7)
  ont besoin d'une mesure commune de ce qu'on perd et de ce qu'on gagne : ce prix propre la
  donne. Le prêt fait une **créance matérielle** (un objet ou une somme à rendre, une échéance),
  distincte de la **dette morale** de la relation ; les deux se répondent (§ 3.7).
- **`besoins`** (non commencé) : hystérésis des besoins (un seuil pour entrer dans l'urgence, un
  autre pour en sortir), coût d'un plan sur les autres besoins. Les seuils de relation et les
  signes ont besoin de la même hystérésis (§ 3.4) ; la gêne d'être près de qui l'on craint est un
  coût sur la sécurité, que la règle générale du coût d'un plan sur les autres besoins doit porter
  plutôt qu'une constante de plus (§ 5.2).
- **`plan-force`** (étapes 4 et 5, en conception à côté) : la peur envers quelqu'un est créée ici
  avec les seules causes qui existent (la poussée) ; la menace, les coups et leurs suites
  l'alimenteront par la même table (§ 3.2).

## 2. Principes

1. **Une relation est dans l'esprit de chacun**, orientée et asymétrique : ce que Gorm éprouve
   envers Brune n'est pas ce qu'elle éprouve envers lui, et aucun des deux ne connaît l'autre
   côté autrement que par des signes.
2. **Une cause par changement.** Toute variation d'une relation vient d'un événement nommé, déclaré
   une fois dans une table commune (comme `ouie.NATURES`), et ses effets sont modulés par les
   valeurs de qui l'éprouve. Rien n'est propre à un personnage, un objet ou un scénario.
3. **Ce qui s'éprouve se perçoit.** Une relation ou une émotion qui pèse sur un choix produit un
   signe. Les signes les plus forts sont des **comportements réels** (où l'on se tient, qui l'on
   regarde, ce qu'on attend), qui ont des conséquences dans le monde (un regard qui surveille
   retient un voleur) ; les expressions (visage, ton) s'y ajoutent. Un signe ne se voit qu'avec
   la perception commune : lumière, ligne de vue, cône, distance ; un ton ne s'entend qu'avec
   l'ouïe commune.
4. **On lit, on ne sait pas.** Ce qu'on tire d'un signe est une croyance de source « deviné »,
   plus fragile que « vu », qui peut être fausse. Le joueur lit par les mêmes signes, avec sa PSY.
5. **Le joueur décide.** Il n'a pas de relations ni d'émotions modélisées : les PNJ en ont envers
   lui, le lisent par ses comportements et ses paroles, comme ils se lisent entre eux.
6. **Sans état caché.** Tout ce dont dépend la suite est dans `data` ; le même laps découpé
   autrement donne le même monde (`tests/test_temps_etat.py`).
7. **Luna ne reçoit que ce que Corvus perçoit** (signes, impressions), plus l'esprit des
   interlocuteurs pour leur donner une voix ; elle n'affirme aucune attitude qui ne soit pas
   dans les faits (§ 8).

## 3. Les relations

### 3.1 Données

Dans l'esprit de chaque PNJ, un champ nouveau `relations` (ajouté à `esprits.CHAMPS`) :

```
"relations": {
  "brune": {"confiance": 20, "affection": 25, "rancune": 45, "peur": 0, "dette": 0,
            "minute": 122,
            "motifs": [{"type": "vu_agir", "minute": 122, "effets": {"confiance": -25, "rancune": 15}}]},
  "joueur": {...}
}
```

- Cinq axes entiers de 0 à 100, comme les valeurs :
  - **confiance** : on le croit, on lui confie, on lui prête, on attend qu'il tienne parole ;
  - **affection** : son bien compte pour soi, sa compagnie rassure ;
  - **rancune** : le tort qu'on lui garde (refus, vol, mensonge, violence) ;
  - **peur** : ce qu'il pourrait vous faire ;
  - **dette** : ce qu'on lui doit (un don, une part, un service, une protection), à ses propres
    yeux. Ce qu'il nous doit se lit dans *son* esprit, pas dans le nôtre : chacun ne connaît que
    ses propres dettes, et ce qu'il a donné (`pret`, `engagement_tenu` pour lui).
- `motifs` : les trois derniers événements qui l'ont changée, avec leurs effets ; ils servent au
  récit, au rejeu et à Luna (« se méfie de toi : vu forcer la réserve, minute 122 »), sans
  dépendre de la mémoire bornée.
- Une entrée n'existe que pour qui l'on connaît (vu, ou voix connue). Sans entrée, c'est un
  **étranger** : confiance 40, le reste à 0 (décision 4).
- Le **lien de départ** est une donnée d'auteur, dans le profil : `profil["liens"]` =
  `{autre: {"confiance", "affection", "dette"}}` (« Aubin doit à Gorm son hébergement » :
  dette 40). Il remplace les croyances `fiable` en savoir des scénarios, et sert d'ancre à
  l'estompement (§ 3.4). Ce n'est pas un script : il dit d'où partent les gens, pas ce qu'ils
  feront.
- Le joueur n'a pas de `relations` ; l'entrée `"joueur"` des PNJ remplace `data["relations_pnj"]`
  (§ 3.6).

### 3.2 Ce qui les fait varier : la table `relations.EPREUVES`

Chaque souvenir d'un type de la table, quand `memoriser` l'inscrit, fait éprouver ses effets à
qui le retient, envers la personne qu'il nomme (`auteur`, `de`, `pour`, `locuteur`…). Un seul
crochet : pas de nouvel appel dispersé dans le moteur, et pas d'effet sans souvenir. Ce qui dure
(une compagnie dans l'épreuve) s'éprouve dans `deliberation.ressentir`, à la minute.

Effets de base (avant modulation) :

| événement (souvenir) | qui l'éprouve, envers qui | conf. | aff. | ranc. | peur | dette |
|---|---|---|---|---|---|---|
| `vu_agir` contre ses biens, `vol_surpris`, `vu_porter` | la victime, l'auteur | −40 | −10 | +40 | | |
| `vu_agir` contre un tiers | le témoin, l'auteur | −25 | | +10 × aff. envers la victime | | |
| `mensonge_decouvert` (il savait le faux) | l'auditeur, le locuteur | −35 | −5 | +15 | | |
| `mensonge_dementi` (le dit est faux, sans savoir s'il le savait) | l'auditeur, le locuteur | −10 | | | | |
| `rumeur` crue qui accuse | l'auditeur, l'accusé | −20 × conf. de la source | | | | |
| `refus` d'une demande | le demandeur, qui refuse | | | +5 (+10 si refusé par méfiance) | | |
| `nourri`, `recu` (don, part) | le receveur, le donneur | +10 | +10 | −10 | | +20 |
| prêt rendu à temps (`echanges-argent`) | le prêteur, l'emprunteur | +15 | +5 | | | |
| `engagement_tenu` pour lui | le bénéficiaire, qui a tenu | +15 | +5 | | | +10 |
| `engagement_abandonne`, promesse non tenue | le bénéficiaire, qui l'a promise | −20 | | +15 | | |
| prévenu d'un tort (`a_prevenir` tenu) | la victime, le protecteur | +15 | +10 | | | +10 |
| `pousse` (subi) | la victime, l'auteur | −30 | −10 | +25 | +20 | |
| `a_pousse` vu | le témoin, l'auteur | −15 | | | +10 | |
| laissé passer à sa demande | le demandeur, qui s'écarte | +3 | +2 | | | +5 |
| une heure ensemble dans l'épreuve (abri, feu partagé, tous deux en besoin pressant) | chacun, l'autre | +3 | +5 | | | |
| dispute perdue devant témoins (§ 7.4) | le perdant, le gagnant | | | +10 | | |

La dette se solde : rendre un service à qui l'on doit (accepter sa demande, lui donner) ôte à la
dette ce que l'acte vaut (même table, signe inverse) ; c'est ainsi qu'une dette « honorée » se lit.

### 3.3 Modulation par les valeurs

Une règle par axe, commune à tous :
- **rancune** gagnée × fierté / 50 ; perdue plus vite avec la douceur (§ 3.4) ;
- **dette** gagnée × loyauté / 50 : un loyal se sent obligé, un ingrat à peine ;
- **affection** gagnée par un don × (50 + empathie) / 100 ;
- **peur** gagnée × (100 − courage) / 50 ;
- **confiance** perdue sur un tort fait à un tiers × (50 + honnêteté) / 100 : un honnête juge
  plus sévèrement le vol d'autrui.

### 3.4 Avec le temps, et l'hystérésis

- **Confiance** : ne s'estompe pas. C'est une preuve accumulée ; elle ne remonte que par des
  événements (« la confiance perdue peut se regagner » : deux ou trois services tenus pour sortir
  de la méfiance).
- **Affection** : revient vers le lien de départ, d'un point par heure.
- **Rancune** : demi-vie de 12 heures × fierté / 50, divisée par (1 + douceur / 100).
- **Peur** : demi-vie de 2 heures, tant que l'autre ne refait rien.
- **Dette** : ne s'estompe pas ; elle se solde.
- Les **seuils** se lisent avec hystérésis (même mécanisme que la branche `besoins`) : on entre en
  méfiance sous 30, on en sort à 40 ; on fait confiance dès 60, on cesse sous 50 ; la rancune
  « en veut à » dès 40, cesse sous 30 ; la peur « craint » dès 40, cesse sous 30. L'état de
  bande (dans ou hors) est gardé dans la relation (`bandes`), pour que le même laps donne le même
  monde.

L'estompement se calcule à la lecture depuis `minute` (dernière mise à jour), pas à chaque minute :
pas de coût par pas de temps, et l'état reste entier dans `data`.

### 3.5 Ce qu'elles font : chaque lecture de `fiable` devient une règle graduée

Un module `donjon/relations.py` est le seul accès : `envers(monde, id, autre)` (la relation,
estompée), `se_mefie`, `se_fie`, `en_veut`, `craint`, `doit`, et `percue(monde, auditeur,
locuteur)` qui passe par l'identification (`voix.identifie`, § 3.7). Les lectures d'une
relation déjà perçue (`mefiance`, `confiance`, `rancune`, `peur`) conservent les mêmes bandes.

| site | règle graduée |
|---|---|
| `jet_persuasion` | DD + (50 − confiance) / 10 − affection / 25 − dette / 20 + rancune / 20 ; VOL inchangée |
| `demander`, `confier` | refus d'office si méfiance ou bande de rancune (entrée ≥ 40, sortie < 30) ; sinon le jet, où la dette pèse |
| `social._auditeur` | on confie à qui l'on fait confiance, le plus aimé d'abord (ordre : affection, puis identifiant) |
| `ouie` | se surveille : le bruit de qui l'on se méfie **ou** craint |
| `appeler` | pas de réponse à qui l'on se méfie, en veut ou craint : bandes communes, entrée rancune/peur ≥ 40, sortie < 30 |
| `passage._refus` | méfiance ou rancune refusent ; l'affection (≥ 50) lève l'orgueil |
| `autour`, `ressentir` | la compagnie rassure × (confiance + affection) / 100 ; la présence de qui l'on craint inquiète × peur / 50 |
| `_plan_abri`, `_rejoindre_un_proche` | rejoindre le plus aimé parmi ceux à qui l'on fait confiance |
| `_delegue`, `confie_a_autrui` | une tâche confiée attend tant qu'on n'est pas en méfiance |
| humeur (`vol.mefiance`, `moteur`) | remplacée par les signes (§ 5) |

Les comparaisons d'axes restent dans `relations.py`, y compris le seuil d'affection qui lève
l'orgueil au passage et la dette morale notable du récit et du banc. Le banc compte méfiances
et rancunes par leurs bandes, donc aussi une bande maintenue entre 30 et 39 par hystérésis.
La remise d'un objet ou d'une part promise inscrit d'abord la réception, puis la parole tenue :
le bénéficiaire qui identifie le donneur l'apprend à cette réception ; une réussite lointaine
reste à annoncer par une parole entendue.

### 3.6 Transition depuis `fiable`, en trois temps

1. **Socle sans changement** (sous-étape 3a) : `relations.py` lit encore la croyance `fiable` et
   la traduit (vrai → 70, absente → 40, faux → 15) ; les règles de lecture sont écrites pour
   redonner exactement les valeurs d'avant (DD −2, +2, +6 ; refus sous 30). Tous les sites
   passent par le module. L'empreinte des bancs doit rester identique : c'est la preuve que plus
   rien ne lit `fiable` en direct.
2. **Bascule** (3b) : les relations sont écrites dans l'esprit ; chaque écriture `croire(...,
   "fiable", ...)` devient un souvenir de la table (le plus souvent déjà là) ; les lectures
   graduées s'appliquent. `fiable` quitte les attributs de croyance (`_croyance_valide`).
3. **Le mot reste dans la parole** : « Brune n'est pas fiable », dit par le joueur ou par un PNJ
   (`paroles.ATTRIBUTS`, `stratege`), devient un **avis sur une personne** : crue, elle fait
   éprouver à l'auditeur `rumeur` (confiance −20 × confiance envers la source) ; elle ne pose plus
   un booléen.

**Migrations au chargement** (comme `caractere.migrer`) :
- scénarios et sauvegardes : une croyance `fiable` vraie en savoir devient le lien de départ
  (confiance 65, affection 20) ; fausse, une relation à confiance 15 avec un motif
  « ancien » ; une croyance `fiable` tirée d'un souvenir encore en mémoire est rejouée par la
  table (vol vu : rancune aussi) ;
- `data["relations_pnj"][id]` : le soupçon 1, 2, 3 donne une confiance envers le joueur de 30,
  20, 10 ; `vols_surpris` reste un compteur (il décide `refuse_ventes_apres_vol`) ;
- `objet["humeur"]` disparaît des données ; `rendu` lit les signes.

### 3.7 Voix, argent, besoins

- **Voix comme signature.** Les relations sont rangées par identifiant réel, mais on n'éprouve
  et ne lit sa relation à quelqu'un que si on l'identifie (`relations.percue`, qui remplace
  `voix.fiabilite`) : une voix reconnue donne la relation de son porteur ; une voix qui « se dit
  X » ne donne jamais plus qu'un étranger, quelle que soit la relation à X (règle de la branche
  `voix`) ; une voix sue menteuse a confiance 0, rangée avec la voix (`voix_entendues`). Le jour
  où l'on identifie la voix menteuse, son porteur éprouve `mensonge_decouvert`. Les souvenirs
  issus d'une voix inconnue (« dit:voix:X ») ne font éprouver aucune relation envers X. Plus tard,
  l'**imitation** : `reconnaitre` rendra X pour la voix d'un imitateur, et c'est la relation à X
  qui sera trompée, sans règle nouvelle ici ; la **méfiance envers une voix connue** sera un doute
  sur l'identification, pas une baisse de la relation.
- **Argent et prêts.** La dette morale (cette étape) et la créance matérielle (`echanges-argent`)
  sont deux choses : prêter fait une créance (l'objet à rendre) et, chez l'emprunteur, une petite
  dette (+10, × loyauté) ; rendre à temps fait gagner la confiance du prêteur ; ne pas rendre à
  l'échéance la fait perdre et donne de la rancune (deux lignes de la table). Les **permissions
  déléguées** ne se donnent qu'à qui l'on fait confiance et se retirent quand la méfiance
  s'installe ; en abuser est une faute et un tort. Le **prix propre** d'une chose pour un PNJ
  mesure ce qu'il perd ou gagne dans une proposition (§ 7.1) ; la relation module le prix (remise
  d'affection, crédit de confiance), elle ne le fixe pas.
- **Besoins.** L'hystérésis des seuils de relation et des signes reprend celle des besoins ; la
  gêne d'être près de qui l'on craint passe par le coût d'un plan sur la sécurité (§ 5.2).

## 4. Émotions

Une émotion est un état passager, avec un objet, qui pousse à agir maintenant ; une relation est
ce qui en reste.
- **L'inquiétude** existe : c'est le besoin de sécurité (`deliberation.SECURITE`). Elle reste ce
  qu'elle est ; ce plan lui donne seulement ses signes.
- **La colère**, nouvelle, dirigée : un tort subi à l'instant (vol découvert, poussée, mensonge
  découvert, refus par méfiance si fierté ≥ 60) donne `emotions["colere"] = {"contre", "niveau",
  "depuis"}` (niveau = rancune gagnée × 2, au plus 100), qui décroît vite (demi-vie 15 minutes).
  Elle se voit et s'entend (§ 5), fait monter la voix d'une dispute (§ 7.4), pousse à demander des
  comptes (dire à l'auteur ce qu'on a vu : un geste `dire` existant, adressé à l'auteur au lieu
  d'un tiers). Elle est la matière de l'étape 5 (contraindre) sans en faire partie.
- La détresse du corps (faim, froid, fatigue) se voit déjà.
- Honte, joie, soulagement : plus tard (décision 5).

Champ nouveau de l'esprit : `emotions` (dict), vide le plus souvent.

## 5. Les signes

### 5.1 Une table, `signes.SIGNES`

Chaque signe est déclaré une fois : l'état qui le produit, sa sorte, ce qu'il faut pour le
percevoir, sa force (qui règle la lecture), et ce qu'il peut vouloir dire (pour les méprises).

| signe | produit par | sorte | se perçoit | peut vouloir dire |
|---|---|---|---|---|
| se tient à l'écart de X | peur ou rancune envers X ≥ 40, X présent | comportement (place) | voir les deux, sur la durée | crainte, hostilité |
| se tient près de X | affection ≥ 60, ou confiance ≥ 60 dans l'inquiétude | comportement (place) | voir les deux | attachement, dépendance |
| ne quitte pas X des yeux | méfiance ou peur envers X, X présent | comportement (regard) | voir son regard (orientation) | méfiance, crainte, attirance |
| lance des regards vers un objet | un geste illicite en attente sur cet objet (`sans_temoin`) | comportement (regard) | voir son regard | convoitise, garde |
| attend que la salle se vide | même attente, prolongée | comportement (durée) | le voir rester sans rien faire | guet, fatigue |
| baisse les yeux devant X | peur envers X ≥ 60 | expression | niveau 2, 4 cases | crainte, honte |
| regard dur, mâchoire serrée | rancune ≥ 60 ou colère | expression | niveau 2, 4 cases | hostilité, inquiétude |
| sourit à X, parle doucement | affection ≥ 60 | expression, ton | niveau 2, ou ses mots saisis | attachement, flatterie |
| voix sèche avec X | rancune ≥ 40 ou méfiance | ton | ses mots saisis | hostilité, fatigue |
| gestes brusques, voix forte | colère | expression, ton | niveau 1, ou l'ouïe | colère, peur |
| tremble, se recroqueville | sécurité au-delà de son seuil | expression | niveau 2 | peur, froid |
| affamé, transi, épuisé | corps (existe) | état visible | `constater` | — |

### 5.2 Les comportements : de vrais choix, avec un coût

Les signes forts sont des décisions du PNJ, prises par les règles communes, qui changent le monde :
- **La place.** Quand un PNJ choisit une case où s'arrêter (attendre, s'abriter, se chauffer, se
  reposer), les cases proches de qui il craint ou à qui il en veut coûtent, celles proches de qui
  il aime rapportent ; dans le planificateur, demeurer dans une salle avec qui l'on craint coûte
  à la sécurité par minute, comme le noir (`planification.NOIR`), par la règle du coût d'un plan
  sur les autres besoins (branche `besoins`). Ilse ne s'assoit plus au feu à côté de Brune.
- **Le regard.** Un PNJ sans geste en cours se tourne vers qui il surveille (méfiance, peur) quand
  il le sait dans sa salle ; cela change son cône, donc qui peut agir sans être vu de lui : Brune
  qui guette la réserve sous le regard de Gorm attend plus longtemps, ou va ailleurs.
- **Le guet.** L'attente d'une occasion (`sans_temoin`, `PATIENCE`) se fait les yeux tournés vers
  l'objet convoité, sauf s'il dissimule (§ 5.4) : il regarde alors ailleurs, et voit moins bien
  quand la salle se vide.

Le moteur sait pourquoi il a choisi : quand un choix de place ou de regard a été décidé par une
relation, il le note dans l'intention (`attitude` : `{"signe", "envers"}`), ce qui fait le signe ;
pas de reconstruction après coup.

### 5.3 Les expressions et le ton

**Détresse perçue (lot 53, `codex-peur-transmise`, non fusionnée).** Dans
`deliberation.autour`, un proche dont on perçoit les tremblements, la fuite ou une
impression de peur/crainte/inquiétude encore appuyée par un signe présent ne compte
plus comme compagnie rassurante. Un appel ou cri effectivement entendu et attribué
par la vue ou une voix reconnue produit le même effet pendant la minute de sa
réception ; une mémoire ancienne ne
vaut pas une détresse actuelle. Les autres compagnons calmes gardent leur effet.
La fuite porte un signe de place seulement après un pas réellement exécuté dans
le plan de fuite, sans révéler l'agresseur ni la destination. Le projet privé seul
ne produit rien. Vue, cône, lumière et portée restent ceux de `signes.percus`.

L'inquiétude transmise vaut **0,5 × (confiance + affection) / 100 point par minute**
pour le proche le plus lié en détresse (maximum, comme la compagnie, sans cumul
des signes). La fraction retenue est la moitié d'une unité de détresse observable
par minute ; aucun niveau privé de sécurité n'est lu pour en estimer l'intensité.
Le profil peut régler `securite.detresse`. `ecart_securite` transmet ce taux au
temps vécu commun, sans saut supplémentaire de besoin. Un signe non perçu ne
change rien à la compagnie ; les appels anonymes gardent seulement l'effet du
bruit déjà prévu par l'ouïe. Questionner l'allié ou suivre son regard reste à faire.

Ils ne changent rien au monde ; ils se calculent à la demande (`signes.de(monde, id)`), à partir de
l'esprit, sans être stockés. Le ton accompagne une parole : `social.faire_entendre` et
`ouie.retentir` portent le signe de ton avec les mots, et qui saisit les mots perçoit le ton.

### 5.4 La dissimulation

On ne cache que ce qu'on a une raison de cacher : une intention illicite ; une rancune ou une peur
envers quelqu'un qu'on a intérêt à ménager (on attend de lui une part, un objet, un passage) ; une
peur, si la fierté passe 60. Qui dissimule :
- n'émet pas les expressions et les tons de ce qu'il cache, pour qui échoue à le lire ;
- garde ses comportements mais les rend plus difficiles à lire (DD relevé) ; le guetteur qui
  dissimule détourne le regard.

La force de la dissimulation est la **VOL** pour les expressions et les intentions, l'**ELO** pour
un mensonge en paroles (décision 7). L'honnêteté ne l'empêche pas : cacher n'est pas mentir.

### 5.5 Perception

Un signe se perçoit avec les règles communes : il faut voir celui qui le porte (`percus`), et,
pour un signe relationnel, savoir qui est X (le voir, ou le croire là) ; les expressions demandent
le niveau 2 de lumière et 4 cases au plus ; un ton, les mots saisis (`ouie.mots_saisis`). Les
signes ont une mémoire distincte de la géométrie (`spatial.etat_vue`) : les causes des émissions
(relations, émotions, attitudes, conscience), puis les personnes réellement perçues, leur lumière,
leur distance et les cibles accessibles à chaque observateur forment les clés de `signes.de` et
`_percus_gardes`. `spatial.VERIFICATION` les recompare au calcul pur. Un esprit éloigné ne force
plus tous les observateurs à recalculer leurs signes.

## 6. Lire les autres

### 6.1 Le jet de lecture

Quand un observateur perçoit un signe nouveau (ou le même signe 10 minutes plus tard), il le lit :

d20 + mod(PSY) + 2 s'il l'observe à dessein (§ 6.5) + 2 s'il le connaît bien (affection ≥ 40 ou
une heure passée ensemble) − 4 en pénombre (niveau 1) − 2 au-delà de 4 cases,
contre DD = 10 + force du signe (comportement 0, expression 2, ton 3) + (mod(VOL ou ELO) + 3 s'il
dissimule).

- réussi : il lit ce que le signe veut dire vraiment ; confiance 0,5 + 0,05 par point de marge, au
  plus 0,8 ;
- manqué de 1 à 8 : il ne tire rien ;
- manqué de plus de 8 : il se **méprend** : il lit l'autre sens que la table donne au signe (un
  timide paraît hostile ; un flatteur paraît attaché) ; s'il dissimule, il ne lit **rien** de ce
  qu'il cache, et la méprise prend le sens le plus banal (« fatigue »).

Les jets de lecture tirent d'un **tirage à part** (comme le niveau d'eau, `eau.py`), compté dans
`data` : ajouter la lecture ne décale pas les autres jets de la nuit, ce qui garde les bancs
comparables avant et après (décision 8).

**Décision du 2026-10-26 (lot 129)** : plafond de justesse basse révisé de
0,6 à **0,7** (PSY ≤ 9) ; justesse haute ≥ 0,8 (PSY ≥ 13) et méprises
strictement < 20 % des lectures conservées. Les abstentions ne sont pas des lectures.
Réglage commun **conservé à 4/3/8** (pénombre/dissimulation/bande « rien ») par décision de
l'utilisateur : le compromis 3/2/7 mesuré par le lot n'est pas appliqué ; aucun réglage par
personne, sorte ou scénario, ni changement du dé ou de la règle du jet.
La grille conditionnelle de 112 combinaisons (pénombre 2 à 5, dissimulation 2 à 5,
bande 5 à 11), sur 48 nuits de 4 h, ne fournit **aucun réglage admissible**.
Le compromis minimax 3/2/7 (justesse basse 0,75, méprises 26,58 % sur la grille) réduit
l'abstention mais augmente les méprises ; à la confirmation (48 nuits libres de 4 h), 4/3/8
donne 21,88 % de méprises et 0,768 de justesse par défaut, 3/2/7 26,00 % et 0,727.
**Calibration close en l'état** : 4/3/8 manque la borne des méprises de 1,9 point et la
justesse basse de quelques centièmes ; pas de nouvelle campagne de réglage des constantes.
Les nuits libres de confirmation et le rapide contre la base sont détaillés dans
[le rapport du lot 129](taches/rapport-codex-129-signes-critere.md).
La grille rejoue les jets à décisions figées ; les échantillons PSY réglés sont petits.
Le critère n'est donc pas atteint et ne le sera pas par les seules constantes ; le revoir
supposerait de changer la règle de lecture elle-même, ce qui n'est pas décidé.

### 6.2 Ce qu'on en retient

Une **lecture** est une croyance de source « devine » (nouvelle source de `esprits.SOURCES`), sur
l'observé, attribut `attitude:<X>` (envers X : crainte, hostilité, méfiance, attachement), `emotion`
(colère, peur) ou `intention` (guette un objet), valeur, confiance, minute, et le signe qui l'a
fondée. Elle cède à tout constat (« vu »), et se périme après `RECENT` minutes pour une émotion,
deux heures pour une attitude. Le joueur a les mêmes lectures dans `data["lectures"]`.

Relire la même valeur envers la même cible pendant la même émission physique
rafraîchit date et confiance, sans souvenir, nouvelle, confidence ni ligne « Lecture »
supplémentaire. Un essai sans impression ne défait pas la lecture active. Un autre sens,
un signe réellement arrêté puis réémis, ou la péremption comptent comme nouveaux ; le
délai de dix minutes demeure dans tous les cas. Détourner le regard, perdre la lumière
ou quitter la salle ne recrée pas le signe qui continue à être émis.
`data.occurrences_signes` conserve l'identité physique commune ; `data.suivi_signes`
retient les conclusions de chaque lecteur. Les paroles reçues portent leur épisode
et sa provenance se transmet dans la nouvelle, sans transmettre sa vérité. Les anciennes
lectures actives sont reprises sans réannonce ; leur histoire physique antérieure,
absente de la sauvegarde, ne peut être reconstituée. Les projections restent pures.

### 6.3 Ce que les PNJ en font

- **Qui croire et à qui demander** : la chance qu'un autre accepte, dans le planificateur, se
  calcule sur ce que le PNJ croit de l'attitude de l'autre envers lui (une lecture, un refus
  récent, ce qu'il sait que l'autre l'a vu faire) ; elle remplace `PRET` (§ 7.2).
  **Socle fait dans `codex-garde-pret`** : une estimation unique
  `relations.chance_demande` utilise le lien propre du demandeur, ses refus retenus,
  services et dettes vécus, et les témoins de faute qu'il a remarqués. Aucune relation
  privée de l'auditeur n'est lue. Les cartes de chances et de prix de garde entrent dans
  `_entrees`. Les signes de 3c affineront cette estimation ; ce n'est pas encore une
  lecture de l'attitude réciproque. Règles et réglages :
  `docs/plan-planificateur.md`, « Garde et chance de demande ».
- **Voir venir** : une intention lue (« guette la réserve ») chez quelqu'un fait surveiller
  l'objet comme un bien à soi s'il est de garde (`de_garde`), et se tourner vers le guetteur ;
  pour un témoin quelconque, c'est une nouvelle qu'il peut confier (`social.NOUVELLES`), mais à
  la confiance d'un « deviné ».
- **Flairer un mensonge** : quand quelqu'un affirme ce qu'il croit faux (le moteur le sait, il
  connaît l'esprit du locuteur), l'auditeur fait une lecture contre son ELO ; réussie, il doute
  (`parole_doutee`) et éprouve un `mensonge_dementi` ; il ne sait pas ce qui est vrai.
- **Éviter, rejoindre** : la place (§ 5.2) se décide aussi sur ce qu'on lit : on évite qui l'on
  croit hostile.

### 6.4 L'empathie

Un besoin d'autrui perçu (son corps, `constater` ; sa peur, une lecture) devient un but de
l'empathique, envers qui il n'est pas hostile, pondéré par empathie × (affection + 20) / 100 :
nourrir (`{"objet", "servir"}`, la condition existe), entretenir un feu pour lui (`{"objet",
"allume"}`), rester près de lui s'il a peur (la compagnie qui rassure). Il passe après ses propres
besoins pressants et avant la routine, comme une parole donnée (`deliberation.candidats`). Cela
lève la limite notée au bilan de l'étape 1 (« l'empathie demande de percevoir le besoin
d'autrui »).

### 6.5 Le joueur lit par les mêmes signes

- **Signes** : les comportements et expressions que Corvus perçoit sont des faits observés,
  rendus par le moteur dans le bilan de fin d'action (`bilan_signes`, sur le modèle de
  `pnj.bilan_presences` : ce qui est apparu, ce qui a cessé), sur la carte (regard, place) et dans
  `rendu`. « Ilse se tient à l'écart de Brune. » remplace « Ilse semble méfiant. ».
- **Impressions** : la lecture de Corvus, faite au bilan pour ceux qu'il a en face (sans bonus), ou
  par la commande `observer <personnage>` (une perception de quelques secondes, bonus +2, répondue
  par le moteur sans le MJ, comme `commandes.PERCEPTIONS`), est dite comme une impression :
  « Elle semble la craindre. » ; une méprise se dit de la même façon, sans que rien ne la
  distingue. Rien n'est affirmé vrai.
- **Relecture** : `observer` redonne les signes physiques et les impressions actuelles de la
  personne demandée, même déjà annoncées, si leur signe d'appui est encore perçu. Le bilan
  spontané n'annonce que les impressions nouvelles. La carte, la description et le contexte
  continuent de présenter l'impression active. Pour un même signe, aucun dé supplémentaire
  avant le délai commun de dix minutes ; une lecture peut rester une méprise. Une personne
  connue peut être nommée hors de vue ; le moteur refuse
  alors selon une seule cause (présence, lumière ou vue), sans appel à Luna, en ligne comme
  hors ligne. Une rotation possible garde sa règle ordinaire.
- **Ce que les PNJ lisent du joueur** : ses comportements (où il se tient, qui il regarde, ce qu'il
  guette), ses tons ne sont pas modélisés (il n'a pas d'état) ; ses mensonges se flairent comme
  ceux d'un PNJ, contre son ELO.

## 7. Influencer par la parole

### 7.1 Les propositions

Une demande devient une **proposition** : ce que je demande, et ce que tu y gagnes.

**A2a, fait sur `codex-propositions`, non fusionnée (2026-10-24).** Le joueur dispose du
contenu indivisible `proposition` : demande objet/part/tâche, contrepartie objet/part/tâche/
pièces/rien. `echanges.evaluer_proposition` calcule P/G/L sur les relations perçues et le devis
cru de l'auditeur ; `proposer` valide les moyens, tire le jet et applique sur copie les remises
et engagements. Les biens sont cédés ; une part est détachée sans céder le lot. Pour une part,
`garde` protège la réserve ; `necessaire` protège la cession de l'objet entier (un devoir portant
sur le lieu du lot ne rend pas chaque part incessible). Les tâches demandées ne peuvent consommer
une réserve gardée. Une tâche déjà promise ne paie pas une deuxième fois.

Constantes de départ : **pas = 5 minutes de valeur propre par point**, **1 pièce** pour un objet
sans prix déclaré ; DD de base **12**, pas de supplément d'INT sous 8. Les poids du lien sont ceux
ci-dessous, sans doubler ceux déjà inclus dans `jet_persuasion`. Un service promis vaut le coût
du devis évité s'il sert une pulsion ou un engagement de l'auditeur, pondéré par confiance/100.
Les promesses du joueur passent par `agendas`, sont visibles dans sa fiche après recharge et
requièrent un effet moteur réalisant la condition puis son observation par le bénéficiaire ;
attendre devant un état déjà vrai ne suffit pas. Échéance **240 min**, abandon éprouvé quand les
deux peuvent se parler. Les engagements PNJ gardent leur cycle existant.

Les demandes historiques restent séparées : une vente au prix est sans jet ; un objet durable
demandé est prêté, tandis qu'une proposition le cède ; la part alimentaire historique est
servie, la proposition peut la remettre. Les fusionner changerait les nuits PNJ. Le geste PNJ,
les services de réparation et les intermédiaires restent aux lots suivants. Le typage spontané
des tâches promises par Luna reste partiel ; voir le [rapport A2a](taches/rapport-codex-29-propositions.md).

**Lot 84, `codex-part-proposee`, non fusionnée (2026-10-25).** La classification
`propositions.prestation` distingue une remise à portée de main d'un travail explicite
ou d'une livraison à aller chercher. La part demandée garde son prix propre et sa réserve
protégée ; elle ne devient pas une demande de cession du lot. L'évaluation, l'exécution
et la contre-offre vérifient la même livraison sur copie (`echanges._livraison_proposition`) :
les biens propres à portée sont constatés, puis une part est détachée par le chemin commun
des demandes et ventes. Tout devis de livraison porte sur cette pièce. Le lot reste au
donneur ; une livraison différée garde l'identité de la part dans l'engagement et les comptes.
Un repas explicitement demandé comme service (`tache`, condition `servir`) reste devisé et
engagé, même si la soupe est portée. Aucun changement des ventes historiques sans jet.
Voir le [rapport du lot 84](taches/rapport-codex-84-part-proposee.md).

- **Contenu typé** (`echanges`, parole du joueur `paroles.TYPES` : `proposition`) :
  `{"demande": <objet | part | tache | passage>, "contrepartie": <objet | part | tache | service
  futur | pieces | rien>, "raison": <avis, § 7.3, optionnel>}`. Les tâches restent le vocabulaire
  commun des buts (`deliberation.condition_valide`), plus une condition nouvelle « remis »
  (`{"objet", "remettre": pour}`), qui sert aussi aux intermédiaires (§ 7.2).
- **L'auditeur juge sur ses croyances** :
  - P, ce qu'il perd : le prix propre de ce qu'on lui demande (`echanges-argent`) ; refus d'office
    si c'est nécessaire à son plan ou ce qu'il garde (`necessaire`, `garde`, inchangés) ;
  - G, ce qu'il gagne : le prix propre de la contrepartie, × la confiance qu'il a que la promesse
    sera tenue (confiance / 100) si elle est différée, × 1 si elle est donnée d'abord ; un but à
    lui servi par la demande (un feu qu'il entretient, l'avis qui le convainc) ;
  - L, le lien : penchant d'altruisme (existe), affection / 25, dette × loyauté / 50 (accepter
    honore la dette), − rancune / 20 ;
  - le jet : d20 + mod(CHA) + mod(ELO) du proposant + (G − P) / pas + L, contre le DD de
    `jet_persuasion` ; un mauvais marché (G < P) relève le DD de (P − G) × (INT − 8) / pas :
    l'intelligence de l'auditeur le protège, un esprit lent se laisse emporter par un beau parleur.
- **Les promesses sont des engagements** (structure existante `{condition, pour, minute}`) : celle
  du proposant s'inscrit dans son esprit quand l'offre est acceptée ; tenue, elle fait éprouver
  `engagement_tenu` ; abandonnée (`ENGAGEMENT_MAX`), elle est une trahison (§ 3.2). Un PNJ peu
  honnête peut promettre ce qu'il ne compte pas tenir : son planificateur pèse la promesse comme
  une faute envers le bénéficiaire (`caractere.prix_faute`), à l'instant où il l'abandonne.

### 7.2 Côté PNJ : proposer, regagner, passer par un autre

**Lot 115, branche `codex-tache-promise`, non fusionnée.** Le recours ajoute
une tâche typée aux contreparties portées, après le choix des moyens ordinaires.
Un refus ancien ne remplace pas un nouveau plan sans faute ; une demande dans
le préfixe d'un plan garde aussi sa chance avant une faute prévue plus loin.
Les conditions proviennent d'un refus entendu ou d'un état connu à réparer :
feu éteint/faible, bien non verrouillé du destinataire ou bien commun dans sa
salle crue. Aucun but privé adverse n'est lu. Un seul candidat est devisé par
recours, même si faute et refus désignent le même interlocuteur ; le devis
autonome et l'évaluation inversée sont partagés entre les contrôles de coût et
de refus. Une demande, un achat ou une délégation futurs dans le devis
interdisent la promesse. Le marché réel réévalue confiance, valeur et relations,
remet la contrepartie et inscrit l'engagement daté par `agendas` ; le moteur
exécute, constate et annonce sa tenue ou son abandon selon le cycle existant.
Les refus de tâche et les tentatives par lésé/besoin survivent à la recharge ;
un ancien plan est revalidé avant parole. Aucune recherche de marché ni Luna.
Ce candidat borné ne parcourt pas toutes les tâches imaginables : un premier
service impossible peut masquer un autre service réalisable. Le verrouillage
est une tâche ponctuelle ; aucune garde permanente nouvelle n'est introduite.
Voir le [rapport du lot 115](taches/rapport-codex-115-tache-promise.md).

**Lot 110, `codex-propositions-redites`, non fusionnée.** Un refus de marché
se compare aux moyens pertinents pour sa cause, au choix et avant exécution
d'un plan sauvegardé, y compris un achat. Une porte voisine devenue ouverte
ne lève ni une garde, ni une nécessité, ni un refus du marché. Pour une
impossibilité matérielle, les contenants de la demande et leurs clés restent
des moyens ; les portes incidentes de la salle ne le sont pas. Un bien
nouvellement porté ne relance que s'il est effectivement offert ; une valeur
plus forte effectivement offerte reste permise. L'inventaire au refus est
retenu parmi les faits de ses moyens. Le temps seul ne lève pas ce refus.
Les anciennes sauvegardes sans cet inventaire restent conservatrices pour
un nouveau bien de valeur égale ; leurs faits matériels et leur force offerte
restent utilisables. La règle sociale de méfiance n'est pas modifiée.

**Décision du 2026-10-24 : un PNJ propose « faute de mieux ».** Proposer n'est pas un geste
envisagé dans chaque état de chaque recherche (lots 33 et 36, non fusionnés : +344 à +534 % de
calcul, et Brune volait toujours sans avoir rien proposé). C'est un **recours de dernier ressort**,
tenté une fois quand ses moyens ordinaires échouent : après une demande refusée, ou quand le plan
retenu contient une faute (voler, forcer) contre quelqu'un, à qui il propose d'abord. Il ne vole
que si l'offre est refusée ou qu'il n'a rien à offrir. Le planificateur ne compare donc jamais une
proposition aux autres moyens : une offre ne passe jamais devant une demande simple ou un plan
sans faute. Contreparties d'abord limitées à ce qu'il porte et à ses pièces ; les tâches promises
(un devis par recours) dans un lot suivant. L'évaluation par l'auditeur (§ 7.1), les engagements,
leur tenue et leur trahison restent ceux du joueur. Ce qui suit décrit le projet initial, que
cette décision remplace pour le geste `proposer`.

**A2b, réalisé sur `codex-proposer-recours`, non fusionnée (lot 45).**
`pnj_propositions.recours`, appelé après le choix du plan ordinaire, remplace celui-ci par
une seule offre avant une faute signalée par le plan, ou après une demande d'objet/part
refusée. Le prochain choix reprend les moyens ordinaires. Les pièces (au plus le prix public
du bien demandé) et les objets/parts possédés et portés sont classés par coût propre divisé
par chance estimée d'accord, puis par chance. L'estimation reprend `chance_demande` et la
valeur publique de la contrepartie, doublée pour un besoin observé ; aucune attitude privée
de l'auditeur n'y entre. Le verdict, les remises et les engagements différés restent ceux
de `echanges.proposer`, commun au joueur.

Le déclencheur de refus et les tentatives sont sauvegardés dans l'esprit. Une tentative
vaut pour un couple lésé/besoin, même après le délai des demandes ordinaires ; seuls un
moyen nouvellement cru, un paiement supplémentaire ou un lien devenu plus favorable
permettent un nouvel essai. Le récit et le journal perçu conservent l'offre et la réponse.
Reprises du lot 36 : chance, contreparties matérielles, validation depuis les connaissances
du proposant et publication atomique conservant les références du moteur. Aucun geste ni
entrée de recherche ajoutés. Les tâches promises, les intermédiaires et la réparation de
confiance restent à faire. Le recours couvre le forcement qui vise un bien mobile à obtenir ;
le passage ou la seule ouverture d'un bien fixe ne sont pas des demandes du contrat A2a.
Vérification et mesures : [rapport du lot 45](taches/rapport-codex-45-proposer-recours.md).

**Lot 57, `codex-offre-sensee`, non fusionnée.** Avant de choisir une contrepartie,
le proposant juge le marché inversé avec `evaluer_proposition` : il ne cède ni ce
qu'il garde, ni ce qui lui est nécessaire, ni une valeur propre supérieure à son
gain. Le même contrôle précède l'exécution. La valeur d'un bien ne se plafonne
plus aux pièces qu'il possède : sans argent, un outil garde son prix.
Un refus de marché ou d'achat retient les moyens de la demande précise et la
valeur effectivement offerte, dans `refus`. Le délai, l'estompement du lien,
une possession sans rapport ou davantage de pièces non offertes ne le lèvent
pas ; un moyen nouvellement cru ou une contrepartie plus forte le permettent.
L'achat refusé remplace la réponse à la demande gratuite du même bien.
Les anciens repères de recours restent lisibles dans les sauvegardes.

**Lot 107, `codex-contreparties`, non fusionnée.** Une demande de recours
porte sur une part utile ou sur le bien indivisible nécessaire. Si le bien visé
est une réserve de pièces, `demande_utile` borne le prélèvement au manque propre
(`besoin_d_argent` moins la richesse), puis `demande_financee` au prix public de
la contrepartie. La source reste explicitement nommée dans le terme
`{type:"pieces", montant, objet}` ; elle n'est pas cédée et aucune autre bourse
ne paie à sa place. Le paiement partiel exige une source possédée et portée,
non gardée, avec les pièces disponibles ; aucune livraison différée de pièces
n'est promise. Le contrat typé, la validation, le transfert et le rendu sont
communs au joueur et aux PNJ.

Le proposant garde le contrôle inversé du lot 57 et anticipe aussi la valeur
pour l'autre : mêmes P/G et même calcul de disproportion que
`evaluer_proposition`. Il n'essaie pas un marché dont le DD de valeur dépasserait
son meilleur jet. Prix publics et contenu monétaire connu sont utilisés ;
situation, richesse liquide, intelligence et lien adverses restent neutres,
sans lecture des dispositions privées. Cette anticipation ne garantit pas
l'accord réel. Le contrôle revient avant exécution, notamment pour un ancien
plan rechargé. Une bourse entière vaut aussi les pièces connues qu'elle contient.
La validation structurelle des termes (`erreur_terme`) est également celle des
audits de narration ; elle accepte le prélèvement partiel sans relâcher les
formes invalides. Aucun changement de recherche ni appel à Luna.

Le devis commun des services (`echanges.devis_service`, tâches payées, confiées,
marchés et empêchement) vérifie aussi les fournitures demandées au bénéficiaire
avec le contrat de livraison. Ilse (crue 7, minute 353) comptait sur une part de
bois que Gorm ne pouvait pas livrer : cette tâche est refusée avant paiement.
Une livraison devenue impossible ou une demande effectivement refusée après
l'accord reste un fait nouveau. La valeur demeure celle du moteur : prix
déclaré ou convention sans prix ; aucun accès aux dispositions privées de
l'autre pour choisir une offre. Détails et limites dans le
[rapport du lot 57](taches/rapport-codex-57-offre-sensee.md).

- **Un geste `proposer`** dans le planificateur, déclaré une fois, à côté de `demander` : il
  offre ce qu'il porte ou ce qu'il peut promettre, et son coût est divisé par la **chance
  estimée**, calculée sur ce qu'il croit de l'autre : ce qu'il lit de son attitude envers lui, un
  refus récent, s'il sait que l'autre l'a vu fauter (le registre `se_sait_vu` est désormais
  retenu dans l'esprit de l'auteur), le besoin qu'il croit à l'autre de la contrepartie. `PRET`
  disparaît. Ces lectures entrent dans `planification._entrees` (la mémoire des recherches) ;
  `planification.VERIFIER` contrôle qu'aucune n'y manque.
  La constante a déjà disparu dans `codex-garde-pret` au profit de cette estimation
  commune aux demandes existantes. Restent ici le geste `proposer`, le prix de la
  contrepartie et le besoin cru de l'auditeur ; le calcul unique pourra les intégrer.
- **Regagner la confiance** (lot 120, décision « faute de mieux » du 2026-10-24) :
  `rendre_service` est un recours après un refus de méfiance ou de rancune, lorsque les moyens
  ordinaires sans faute n'aboutissent pas, avant une faute envers ce même personnage. Il ne
  devient pas un geste comparé dans chaque état de la recherche (précision de la décision 14).
  Une tentative par couple refus/besoin est conservée, même impossible ; une tâche en cours
  reprend son devis existant après sauvegarde. Le proposant agit seul, avec ses propres moyens
  et droits ; aucun mandat du bénéficiaire n'est créé. Le moteur constate le résultat utile,
  perçu avec son auteur identifié, avant l'épreuve commune `service_rendu` : confiance +20,
  affection +10 modulée par l'empathie, rancune −15 et dette +20 modulée par la loyauté.
  Les bandes gardent leur hystérésis ; un lien très dégradé peut demander plusieurs épreuves.
  Le refus social retenu est levé par ce moyen nouveau, sans garantir l'accord suivant.
  Les dons spontanés et repas offerts passent aussi par cette épreuve, joueur compris,
  seulement s'ils comblent un manque cru capturé avant la remise ou la satiété : besoin
  du corps pressant ou condition non satisfaite d'une pulsion ou d'un agenda actif. Sinon,
  ils gardent l'épreuve historique `recu` ou `nourri`, sans recalibrage des simples cadeaux. Les
  livraisons payées, prêts et engagements ont leurs épreuves propres, sans second crédit du
  même geste. Brune peut ainsi recharger un feu commun qui sert Gorm avant de redemander
  une part. Un effet utile effectué hors de son regard ne lui révèle ni l'auteur ni le service.
- **Intermédiaires** : obtenir un objet porté par autrui est une tâche confiable (« remis ») ;
  servir quelqu'un l'est déjà (`{"objet", "servir"}`). L'intermédiaire la planifie avec ses propres
  relations : Ilse, que Gorm croit, lui demande de servir Brune, qu'il refuse en direct. Le récit
  dit la chaîne.

  **Lot 122, branche `codex-intermediaires`, non fusionnée.** Même décision
  « faute de mieux » que les lots 45 et 120 : après un refus retenu de méfiance
  ou de rancune, les moyens ordinaires sans faute gardent la priorité. Le devis
  le moins cher pour le demandeur départage service spontané et commission :
  devis du service existant (ou valeur du don), contre approche de l'intermédiaire
  et peine conventionnelle commune d'une tâche. Aucun recours ajouté aux états
  de la recherche. Une commission acceptée s'attend avant une faute envers la cible.

  Le candidat est connu et joignable ; le demandeur a observé ou entendu une
  attitude d'attachement de la cible envers lui, sans attitude connue de méfiance
  ou d'hostilité du candidat envers le demandeur. Il choisit le moins coûteux
  à rejoindre, sans lire leurs relations privées. Une seule tentative par
  refus/besoin est sauvegardée, même si l'accueil réel dément cette croyance.
  `echanges.confier` conserve le seul jet commun : altruisme, lien du porteur
  envers le demandeur et coût de son propre `devis_service` en fixent le DD.

  Le porteur acquiert lui-même le bien visé, avec ses relations et les refus
  communs, sans déléguer le travail. La demande explicite d'une part à emporter
  vaut aussi pour la nourriture ; elle ne nourrit personne à l'accord. La
  réception affecte l'identité réelle de la part à une seule tâche promise,
  puis `servir` ou `remettre` tient cette parole. Les fournitures accessoires
  restent limitées au commanditaire, comme auparavant ; leur propre livraison
  ne peut pas dépendre d'un accord futur avec un tiers. La demande au cédant
  ne nomme pas le bénéficiaire ; une commission entendue peut le lui révéler.
  Chronique, journal perçu et sauvegarde conservent la chaîne. Le banc compte
  commissions sollicitées, acceptées et abouties. Deux scènes d'auteur et
  limites : [rapport du lot 122](taches/rapport-codex-122-intermediaires.md).

### 7.3 Les avis

**Lot 124, branche `codex-avis-joueur`, non fusionnée.** Le contenu joueur `avis`
porte `sujet` (référence publique d'une salle connue), `attribut: menace`, `valeur: oui|non`.
Sa conviction vient de l'estimation des observations propres de Corvus ; sans estimation,
poids deviné 0,4. Les observations d'eau sont conservées à la mémorisation de sa perception.
La position exprimée reste distincte de ces preuves : une conclusion qualitative n'invente
aucune hauteur ni vitesse. Reçue, elle porte seulement la menace minimale (1 cm dans
`attendue`, jamais une noyade) ; une mesure d'eau présente reste prioritaire.
Auditeurs et témoins passent par `recevoir_prevision` ; la contradiction et les partis pris
utilisent le circuit du lot 121. Le moteur ne fait ni répliquer ni choisir un parti au joueur.
**Limite de bout en bout :** la passe Luna donne trois `propos`, aucun `avis` ; le raccourci
des mots exacts déclarés sans effet évite la revue sémantique. Le typage depuis la saisie libre
n'est pas garanti ; branche non fusionnable comme réalisation achevée de 3f.
[Rapport du lot 124](taches/rapport-codex-124-avis-joueur.md).

Un avis est une croyance sur ce qui va arriver ou ce qu'il vaut mieux faire, avec sa conviction (la
confiance de la croyance). Pour ne rien écrire par scénario, **un avis porte seulement sur un
prédicat que le moteur sait évaluer**, parce qu'une règle commune s'en sert déjà :
- **la menace d'un lieu** (`eau.menacee` : l'eau gagnera telle salle dans l'heure) ;
- **la sûreté d'un lieu** (`_eclairee_crue`, sans menace : un abri) ;
- **la fiabilité d'une personne** (le « fiable » de la parole, § 3.6) ;
- **le besoin d'une personne** (elle a faim, froid, peur), qui nourrit l'empathie.

« La digue tient » n'est pas un avis tant que la digue n'est pas une mécanique : il deviendra un
avis le jour où un barrage (`docs/plan-crue.md`, « Agir ensemble ») aura sa règle (décision 12).

- **Formation** : ce qu'on voit soi-même pèse plus que ce qu'on entend. Poids d'une source : vu ou
  essai 1 ; entendu 0,8 ; dit par X 0,7 × confiance envers X / 100 × (1 + affection / 200) ;
  deviné 0,4. Une croyance nouvelle remplace l'ancienne si son poids × conviction l'emporte ; la
  règle existante `dementi` (ce qu'on vient de voir prime) en est le cas extrême.
- **Exprimer** : un PNJ dit son avis (geste `dire`, contenu typé existant) à qui il croit concerné
  et en danger d'agir contre (un auditeur qui se tient dans un lieu qu'il croit menacé, qui va
  faire confiance à qui il croit menteur), s'il s'en soucie : altruisme + empathie + affection
  envers lui ≥ 100. C'est l'extension de `social.bavarder` (qui confie des nouvelles) aux avis,
  avec la même règle d'auditeur.

### 7.4 Les disputes

**Réalisé entre PNJ, lot 121**, branche `codex-disputes`, non fusionnée : menace d'eau seulement.
`social.faire_entendre` relève les auditeurs par l'ouïe commune, puis ouvre au plus un épisode :
contradiction du premier avis contraire plus étayé, réponse si le locuteur tient encore au sien,
troisième réplique en éclat si fierté > 60 ou colère ≥ 20. L'éclat porte à 6 crans, entre voix (4)
et bruyant (7), et utilise sans modification `bruit_a_voir`. Les témoins ayant saisi les deux
positions les pèsent ensemble ; égalité départagée par d20 + modificateurs CHA/ELO, égalité des jets
conservatrice. Qui n'a entendu qu'une position la reçoit comme un avis ordinaire. Le registre des
faits dits (lots 64/108) borne aussi les répliques et les prises de parti après oubli/recharge.
Un parti pris audible donne +3 d'affection à son auteur ; un désaveu public majoritaire donne
10 de rancune au perdant envers l'autre, modulée par la fierté commune. Un désaccord ne prouve
aucun mensonge et ne baisse pas la confiance. Parole typée `avis` du joueur encore à réaliser.
[Rapport du lot 121](taches/rapport-codex-121-disputes.md).

Quand un auditeur entend un avis contraire au sien, avec une conviction pondérée plus forte, il
**contredit** (geste `contredire`, de la voix : son avis, adressé au locuteur). Le locuteur, s'il
tient encore au sien, répond une fois ; la fierté (> 60) ou la colère le font répéter une
troisième, **la voix monte** (nature d'ouïe nouvelle « éclat », entre voix et bruyant : la dispute
s'entend de la salle voisine, et fait venir voir par la règle commune `bruit_a_voir`). Ce n'est pas
un mensonge : se tromper ne fait éprouver qu'un `mensonge_dementi` faible ; seul un mensonge
flairé (§ 6.3) ou découvert coûte la confiance.

- **Les témoins** (qui saisissent les mots des deux) pèsent chaque côté par la règle des avis (leur
  propre constat, leur confiance et leur affection envers chacun) ; un jet opposé
  (CHA + ELO de chacun) penche à égalité de poids. Chacun adopte, garde ou doute, pour lui.
- **Les suites** : celui que les témoins ont désavoué éprouve « dispute perdue » envers l'autre
  (rancune, × fierté) ; qui a pris son parti gagne un peu de son affection. Un parti pris se voit
  (il se range à côté, il parle à son tour) : c'est le germe de l'étape 6 (suivre), sans la faire.
- **Le joueur** voit et entend la dispute par l'ouïe et la vue communes ; il peut y prendre part
  avec une parole typée (avis), pesée comme celle d'un PNJ.

### 7.5 Le joueur

Le schéma de parole (`paroles.SCHEMA_PAROLE`) gagne deux contenus typés : `proposition`
(demande, contrepartie) et `avis` (un prédicat de § 7.3, une valeur). Le moteur en tire l'issue
comme pour un PNJ ; un refus porte un `attendu` (champ fautif, valeur reçue, ce qui serait
accepté : `donjon/refus.py`), une cause par refus (contrepartie qu'il n'a pas, prédicat inconnu,
destinataire méfiant).

## 8. Le MJ (Luna)

**Ce qu'elle reçoit**, en plus de l'existant :
- `signes_percus` : les signes que Corvus perçoit maintenant, les mêmes que la carte et le
  bilan, chacun avec un identifiant (`{"id", "personnage", "signe", "envers", "texte"}`) ;
- `impressions` : les lectures de Corvus (`{"id", "personnage", "lecture", "envers", "nettete"}`,
  nette au-delà de 0,65 de confiance, vague en deçà) ;
- dans `esprits_interlocuteurs.<id>` : `relations`, envers le joueur et envers les présents, en
  bandes nommées avec un motif (« se méfie de toi : t'a vu forcer la réserve ») ; `dissimule`, ce
  qu'il cache ; `emotion`. Elle s'en sert pour la **voix** du personnage : ton, réticence,
  chaleur. Ce que le personnage dit de ce qu'il ressent est une parole : elle établit qu'il l'a
  dit, pas que c'est vrai ; il ment selon son honnêteté (règle existante), cache selon `dissimule`.
- `humeur` et `relation_joueur` (`dialogues.interlocuteurs`) disparaissent, remplacés par ce qui
  précède.

**Ce qu'elle peut affirmer** (contrat d'`AGENTS.md`) :
- une attitude ou une émotion visible d'un PNJ (où il se tient, qui il regarde, son visage, son
  ton) est **mécanique** : elle ne la raconte que si elle est dans `signes_percus`, et cite son
  identifiant ;
- une interprétation (« elle semble la craindre ») n'est dite que si elle est dans `impressions`,
  au conditionnel de l'impression, et cite son identifiant ;
- l'ambiance reste libre (l'air lourd de la salle), sans attitude prêtée à quelqu'un.

**Contrôle** : le mécanisme commun des citations s'étend. L'audit narratif classe une phrase qui
prête une attitude, une émotion ou une intention à un personnage comme mécanique ; elle doit citer
un signe ou une impression ; le moteur vérifie de façon déterministe que l'identifiant existe et
que personnage et cible concordent ; sinon refus avec un `attendu` qui liste les signes
disponibles. **Limite** : repérer qu'une phrase prête une attitude reste un jugement de
l'auditeur ; seul son appui est vérifié (même limite que les promesses, branche
`don-et-promesses`).

**Consignes** (`donjon/consignes.py`) : une règle à un seul endroit, dans la section des faits qui
font autorité (« Attitudes : signes_percus, impressions »), et une ligne dans la section de la
parole (proposition, avis), sans exemple propre à un scénario.

## 9. Sous-étapes

Chacune est une branche, fusionnée avant la suivante, mesurée au banc sans joueur, sur le Relais
(8 graines : 1985 7 42 2024 3 11 99 500), la mine, l'auberge et la crue (4 graines chacune),
`planification.VERIFIER` et `spatial.VERIFICATION` sur une nuit de chaque scénario. Partout :
aucune usurpation ni violation ; temps d'une nuit mesuré. Les tests vérifient l'état du monde et ce
que lit le joueur **après rechargement**, sur le cas qui a motivé la règle et un autre de même
nature (`AGENTS.md`).

### 3a. Le socle, sans changer le comportement

- `donjon/relations.py` : lecture de `fiable` traduite (§ 3.6), prédicats, `percue` (branchée sur
  `voix.fiabilite`) ; tous les sites de § 1.1 passent par lui ; `recit_pnj` et `banc_pnj` aussi.
- **Mesure** : empreinte des chroniques, des mesures et de l'état final.
- **Critère** : identique sur les quatre scénarios ; suite de tests inchangée.

**Fait** (branche `relations-socle`). `donjon/relations.py` : `FIABLE` (l'attribut qui porte encore
la relation), `AXES`, `ETRANGER`, la traduction (`TRADUCTION` : vrai 70, absente 40, faux 15 ; une voix
sue menteuse 0), les seuils `MEFIANCE` 30 et `CONFIANCE` 60 (`RANCUNE`, `PEUR` 40, sans effet encore) ;
lectures `croyance` (la croyance telle quelle : date et source), `connus`, `envers` (les cinq axes, la
minute et la source), `percue` (remplace `voix.fiabilite`, retirée), prédicats `se_mefie`, `se_fie`,
`mefiance`, `confiance` (sur une relation), `en_veut`, `craint`, `doit` (toujours faux ou 0 en 3a),
`fiable` (ce qu'il en dirait, le mot de la parole) ; écritures `eprouver(monde, id, autre, cause, source,
certitude)` sur une table de causes nommées (`EPREUVES` : `vu_agir`, `agir_entendu`, `vu_porter`,
`mensonge_decouvert`, `mensonge_dementi`, `imposture`, `rumeur`, `aveu`, `pousse`, `vol_surpris`,
`dette_niee`, `pret_garde`, `nourri`), et `avis` (une affirmation « X est / n'est pas fiable » crue,
`echanges.affirmer`). Une cause apprise de seconde main (rumeur, aveu, geste reconnu à l'oreille) ne
remplace pas une méfiance vue : la règle d'avant, gardée cause par cause, telle qu'elle était. Les
lectures génériques d'une croyance par son attribut (`paroles.dementi`, `echanges.affirmer`, le
stratège) passent par `esprits.croyance`, qui renvoie au module pour `FIABLE`. Tous les sites de § 1.1
y passent, avec `recit_pnj`, `banc_pnj` (`mefiances`), `ouie`, `vol.mefiance` (l'humeur) et les gestes
du planificateur (`Vue.se_mefie`, `se_fie`). `tests/test_relations_socle.py` garantit qu'aucun code du
jeu ni de ses outils ne nomme plus l'attribut hors du module, ni ne lit ou écrit la croyance en direct
(indice, `get`, `croire`, `reviser`, `_cru`, `cru` avec `FIABLE`) : le même contrôle relève 42
occurrences sur `main`. Limites : la relation est encore stockée dans la croyance `fiable` (les
scénarios la déclarent en savoir) ; les vidages génériques des croyances (`_entrees`, dossier du
stratège, commande « esprit », rejeu, audit) la voient comme une donnée parmi d'autres, et 3b devra
ajouter les relations à `_entrees` quand elles quitteront les croyances ; les drapeaux « une méfiance
vue tient » reproduisent les écarts d'avant (une imposture reconnue à la voix remplace une méfiance
vue, une rumeur ou un aveu non) ; `data["relations_pnj"]` et l'humeur restent tels quels.

### 3b. Les relations graduées

**Fait**, branche `codex-relations-3b`, non fusionnée ; critère global de banc non atteint
(auberge 1/4, crue 0/4 pour les services levant une méfiance ; temps +15,6 % à l'auberge,
+71,5 % à la crue dans la paire rapprochée, au-delà de la borne +10 %).
Les liens sont des données nouvelles,
sans migration des anciennes sauvegardes (décision de l'utilisateur pour ce chantier).
Les résultats finaux et limites sont consignés dans
[`taches/rapport-codex-6-relations-3b.md`](taches/rapport-codex-6-relations-3b.md).

Précisions du contrat réalisé : ancres exactes par axe pour conserver l'estompement malgré
d'autres événements ; preuve durable commune au constat et à sa rumeur, avec complément
pour une preuve plus forte ; suite d'engagement apprise à réception ou par une annonce
réellement entendue ; achat, don, prêt et restitution distingués. Le registre de preuves
croît avec les incidents ; la compagnie dans l'épreuve compte les minutes perçues du filet.
Le crochet sait compléter une preuve renforcée, mais le circuit social rejette encore une
nouvelle déjà sue : une seconde source ne la fait pas réévaluer tant que le souvenir subsiste.
Les signes et le retrait de l'humeur restent en 3c ; les propositions de réparation en 3e.

- Données : `relations` dans l'esprit, `profil["liens"]`, sans migration des anciennes
  sauvegardes (décision de ce chantier, remplace cette partie du § 3.6) ; table
  `EPREUVES` par le crochet de `memoriser`, modulations, estompement, hystérésis ; lectures
  graduées (§ 3.5) ; `fiable` quitte les croyances ; la crue reçoit ses liens de départ, en
  données (« Gorm se méfie de Brune ; Ilse craint Brune et s'en remet à Gorm ; Aubin doit à Gorm
  son hébergement », `docs/plan-crue.md`).
- Le récit (« Ce qu'ils pensent les uns des autres ») montre chaque relation qui a changé de bande,
  avec ses motifs ; le rejeu la montre dans le temps.
- **Mesures nouvelles** : `mefiances` (bande en fin de nuit, hystérésis comprise), `mefiances_levees`,
  `rancunes` (bande en fin de nuit), `dettes` (≥ 20), `dettes_honorees` (une demande acceptée par qui devait au
  demandeur), `relations_changees` (paires ayant changé de bande) ; et les mesures d'avant :
  échanges, vols vus, rumeurs crues, minutes sans recours.
- **Épreuve** : la crue (liens de départ contrastés). Tests, après rechargement : Brune, dont
  Gorm se méfie, lui remet du bois puis le prévient d'un vol vu : il sort de la méfiance (deux
  motifs) et sa demande suivante va au jet au lieu du refus d'office ; Odon (mine), refusé par
  Mathe, lui en veut (motif `refus`), et Mathe, qui l'a vu manger le pain de Lucien, se méfie de lui ;
  le joueur surpris à voler rend l'objet (don) : le PNJ le croit un peu plus, sans oublier le vol
  (motifs), et ne lui vend toujours rien (`vols_surpris`). En 3b, une méfiance ne se lève que par
  ce qui arrive (dons, paroles tenues, prévenir) ; la chercher est l'affaire de 3e.
- **Critère** : au moins une méfiance levée par un service dans le quart des nuits de la crue et de
  l'auberge, racontée avec sa cause ; minutes sans recours au plus +10 % sur chaque scénario, ou
  chaque écart expliqué par le récit ; temps au plus +10 %.

### 3c. Les signes et leur lecture

**Fait sur `codex-relations-3c`, fusionnée (2026-10-23 ; accords de fusion dans `docs/etat-dev.md`).**
[Rapport, mesures et vérification Luna à faire](taches/rapport-codex-11-relations-3c.md).
Les signes sont des observations ; les impressions restent faillibles, y compris une
impression nette. Colère, décisions de place/regard avec coût réel, source `devine`,
lectures des PNJ/joueur, commande locale `observer` (3 s), rendu/carte, usages de garde,
hostilité et mensonge, retrait de l’humeur et `--regler` sont réalisés. `relations.py`
reste l’unique accès aux axes. Le tirage indépendant est séparé **par observateur** :
observer avec le joueur ne décale ni les dés ordinaires ni ceux d’un PNJ.
Le lot **68**, branche `codex-impressions-observer` non fusionnée, corrige la restitution
des lectures déjà acquises : la déduplication des nouveautés reste celle du bilan spontané,
pas celle d'une demande explicite. La règle commune de lecture, sa mémoire et son appui
perçu sont conservés. Voir le [rapport et les vérifications après recharge](taches/rapport-codex-68-impressions-observer.md).
Les lectures entrent dans les clés du planificateur ; une clé sociale séparée et les
causes des émissions invalident les caches sans rendre une mise à jour d’esprit
incompatible avec le bloc de géométrie figée.

Le cas réel du guet est fourni en capture à 441 min (la minute 122 est historique),
testé après rechargement avec un même dé contrôlé à PSY 14/8, plus un second cas à
l’auberge. Le dé naturel de cette capture peut réussir aux deux PSY : aucune promesse
de séparation de chaque nuit. La qualification quantitative et ses dénominateurs
sont dans le rapport ; ne pas déduire du mot « Fait » que tous les seuils ci-dessous
sont atteints : **critère global non atteint**, justesse haute et méprises à calibrer. Luna est reportée à l’autre poste à la demande de l’utilisateur.
À la fusion : l'humeur de 4b est devenue un signe (l'inconscient n'en montre ni n'en lit, la victime
frappée tremble), les seuils des signes passent par les bandes (`relations.vive`, `familier`), un lieu de
devoir menacé par un guet lu coûte la loyauté du gardien (`prix_gardes`) ; Luna toujours non vérifiée (service
indisponible le jour de la fusion).
Les voix non identifiées ne portent pas encore de lecture de mensonge ; les comportements
du joueur se limitent à son observation explicite, sans état affectif inventé.


- Données : `emotions` (colère) ; source « devine », lectures dans les croyances, `data["lectures"]`
  du joueur ; attitude dans l'intention ; tirage à part pour les lectures.
- Règles : table `SIGNES`, place et regard (§ 5.2), expressions et ton, dissimulation, jet de
  lecture, méprises, usages des PNJ (§ 6.3) ; le joueur : `bilan_signes`, `observer`, la carte et
  `rendu` ; l'humeur retirée.
- Outil : `banc_pnj --regler gorm.PSY=16` (surcharge d'une donnée de profil, sans toucher au
  scénario), pour faire varier la PSY d'une nuit à l'autre.
- **Mesures nouvelles** : `signes` (par sorte), `lectures`, `justesse` (part des lectures vraies,
  par tranche de PSY : ≤ 9, 10 à 12, ≥ 13), `meprises`, `guets_reperes` (une intention illicite
  lue avant le geste), `attentes_sous_regard` (minutes de guet sous le regard d'un surveillant) ;
  vols tentés et vols vus.
- **Épreuve** : le Relais (Brune guette la réserve, Gorm et Ilse), l'auberge (Lucien et le coffre,
  Hugues de garde), avec les PSY réglées par `--regler`. Tests : le cas réel du guet de Brune
  avant qu'elle force la réserve (graine 7, vers la minute 122, `docs/plan-vue.md`) lu par Gorm à
  PSY 14, manqué à PSY 8 ; Ilse à l'écart de Brune,
  vue par le joueur (« Ilse se tient à l'écart de Brune. ») et, après `observer`, l'impression ;
  la même scène dans le noir : ni signe ni impression.
- **Critère** (décision du 2026-10-26) : justesse croissante avec la PSY (au moins 0,8 à PSY ≥ 13, au plus 0,7 à PSY ≤ 9),
  des méprises présentes sans dominer (moins d'une lecture sur cinq) ; aucune lecture sans un signe
  perçu à cet instant (contrôle du rejeu) ; vols vus égaux ou en hausse, ou leur baisse expliquée
  par des guets dissuadés ; temps au plus +20 %.

### 3d. L'empathie

- Règle de § 6.4 ; aucune donnée nouvelle.
- **Mesures** : `secours` (buts d'empathie menés à bien), minutes urgentes d'autrui apaisées par
  un autre, minutes sans recours.
- **Épreuve** : la mine (Odon et Gaspard affamés), la crue (Ilse transie), un cas de contrôle où
  personne n'est empathique. Tests : Mathe sert Lucien qu'elle voit affamé, une fois, puis plus
  (le protégé nourri en boucle de `entretenir-feu` ne revient pas).
- **Critère** : des secours dans la moitié des nuits où un empathique (≥ 70) voit un affamé ou un
  transi ; aucun chez qui n'en a pas ; minutes sans recours en baisse ou expliquées.

### 3e. Les propositions

Après la fusion d'`echanges-argent` (prix propre, prêts, permissions).
- Contenu `proposition`, évaluation (§ 7.1), engagements des deux côtés, trahison ; geste
  `proposer` et chance estimée (fin de `PRET`) ; `rendre_service` ; condition « remis » et
  intermédiaires ; parole du joueur typée.
  Préparé par `codex-garde-pret` : chance estimée centralisée, expériences du demandeur
  et souvenir des témoins remarqués ; `PRET` retiré. Le reste de 3e demeure à réaliser.
- **Contre-offre** (revue externe du 2026-10-24, retenue) : qui refuse une demande par réticence ou parce qu'un
  autre besoin le presse peut dire ce qui le ferait céder : un prix (le seuil où sa réticence cède) ou son propre
  besoin du moment (« apporte-moi de quoi manger et je te prête ma clé »). La condition est retenue avec le refus
  (`esprit["refus"]`) ; le planificateur du demandeur, ou le joueur, y voit un sous-but. Des chaînes de troc à
  trois peuvent en naître sans règle propre. Suite d'A2b « faute de mieux », côté de celui qui refuse.
  **Réalisé côté PNJ, lot 77, `codex-contre-offre`, non fusionnée** : le refus conserve une
  `offre` du contrat commun, annoncée avant affichage ; le prix est le premier montant positif
  où la réticence propre cesse, sans lire la fortune du demandeur. Un besoin de repas peut
  donner un service `servir` si un repas suffit réellement à libérer le bien, vérifié sur copie.
  Ni méfiance, ni garde ou pulsion durable ne produisent de condition inventée. Le recours,
  hors de la recherche ordinaire, rejoint pour payer ou planifie le service existant puis
  redemande ; la prestation accomplie est retenue avec le refus, sans dépendre de la mémoire
  courte. Pas de second jet. Une condition sans moyen reste retenue, sans proposition au
  hasard à sa place. Les moyens ordinaires sans faute gardent la priorité. Aucun changement
  de `planification.py` ni de ses entrées : `tient` conserve la condition, son exécution est
  décidée hors recherche. Limites : les besoins sans service exprimable ne reçoivent pas de
  contre-offre ; les empêchements matériels restent revalidés ; contenu typé du joueur à venir.
  [Rapport du lot 77](taches/rapport-codex-77-contre-offre.md).
- **Mesures** : `propositions`, `acceptees`, `contreparties_tenues`, `trahisons`,
  `intermediaires`, `services_rendus` ; vols et minutes sans recours.
- **Épreuve** : la crue (Brune affamée, dont Gorm se méfie, et les vivres sous clé), la mine (Odon
  affamé, que Mathe refuse), l'auberge (le bois de Joss). Tests : Brune propose à Gorm de tenir le
  brasero contre une part, refusée (méfiance) ; elle le recharge d'abord (`rendre_service`), puis
  sa proposition passe ; ou elle passe par Ilse, qui demande à Gorm de la servir ; le même cas
  avec Brune à honnêteté 90 et à 20 (à 20, la réserve crochetée reste moins chère quand Gorm
  s'éloigne).
- **Critère** : dans la moitié des nuits où un affamé peu honnête a un autre recours, une
  proposition vient avant le vol ; les vols baissent ou chaque vol restant a son explication ;
  temps au plus +20 %.

### 3f. Les avis et les disputes

- **Menace d'un lieu, première partie réalisée, lot 80** (`codex-avis-menace`, non fusionnée) :
  les repères d'eau fondent un avis de menace dans l'heure, confié par les nouvelles communes
  à qui le locuteur croit dans ce lieu ou attendu à un rendez-vous convenu, si altruisme +
  empathie + affection atteint 100. La confiance du locuteur envers l'auditeur n'est pas
  requise pour cet avertissement ; celle de l'auditeur envers la source pondère son adoption.
  Poids des sources × conviction, égalité conservatrice, estimation propre étayée plus récente prioritaire.
  La prévision reçue est une croyance distincte des hauteurs et vitesses observées ;
  `eau.attendue` la départage et la fournit aussi aux routes, avec ses coefficients dans
  les entrées de recherche. Le registre du lot 64 suit la menace et son destinataire,
  sans répétition pour une nouvelle date ou une conviction différente. Témoins auditifs
  soumis à la même réception. Mesures `avis_exprimes`, `changements_d_avis` (adoptions dites).
  Ni dispute, ni autre prédicat dans ce lot ; une destination privée n'est pas devinée.
  [Rapport du lot 80](taches/rapport-codex-80-avis-menace.md).
- **Avis dans les nuits réelles, lot 88** (`codex-avis-reels`, non fusionnée,
  base `c9245dd`) : `_sait` ne confond plus une conclusion de menace avec une
  prévision déjà reçue. Le choix de l'auditeur ne consulte plus sa prévision
  privée ; la réception seule pèse ses preuves. Le seuil de souci reste 100 :
  il ne bloquait aucune paire des deux crues mesurées. Relevé chaque minute,
  500/2024 : **3 327 / 44** occasions bloquées par ce seul filtre ; audits 12 h :
  **16 / 6 avis, aucune adoption**, preuves propres conservées. Les avis dits,
  même déclinés, restent bornés par le registre commun. Trois tests sur captures
  réelles à 72/102 min, monde complet et perception après recharge/découpage.
  Le créneau de confidence et sa limite d'une parole par minute sont inchangés ;
  pas de garantie d'avertissement immédiat pendant un plan actif. Eau longue
  **4 / 1** persistante ; crue 2024 modifiée : rafale de passages après violence
  à 649 min, hors de la correction des avis.
  [Rapport du lot 88](taches/rapport-codex-88-avis-reels.md).
  **Suite, fusion refusée :** les 237 passages/h sont l'alternance lumière/ronde
  d'Aubin, persistante sans danger actif. Défaut latent reproduit sur la base
  depuis une capture commune : même monde et rendu en bloc/découpé/rechargé.
  Audits 2024/500 refaits, identiques ; arrêt au diagnostic (point 3), aucun code
  ajouté, **boucle non corrigée, branche non fusionnable**. Le contrat commun
  choix/prérequis/progression relève d'un lot distinct.
  [Diagnostic de la boucle du lot 88](taches/rapport-codex-88-boucle.md).
- **Disputes entre PNJ, lot 121** (`codex-disputes`, non fusionnée) : épisode fini dans la parole
  commune, `contredire`, nature « éclat », témoins, prises de parti et suites relationnelles (§ 7.4).
  Aucun nouveau prédicat, scénario ou appel Luna ; la parole typée du joueur reste au lot suivant.
  [Rapport](taches/rapport-codex-121-disputes.md).
- **Partager ses constats** (revue externe du 2026-10-24, retenue) : deux personnes qui se font confiance se disent
  aussi leurs constats matériels récents (une réserve vue vide, une porte trouvée fermée à clé, l'eau qui monte,
  un besoin pressant sans recours), par les nouvelles communes ; chacun n'a plus à buter seul sur la même porte,
  et le joueur entend des échanges qui l'informent. Un PNJ désœuvré peut rejoindre, au plus bas rang, un lieu
  éclairé où se trouve quelqu'un qu'il apprécie.
  **Réalisé, lot 55** (`codex-constats-partages`, non fusionnée) : les états matériels récents vus ou
  essayés (ressource épuisée, contenant ouvert vide, verrou, source éteinte, eau observée) passent par
  `social.nouvelles` → `bavarder` → `recevoir`, après les accusations, à un interlocuteur de confiance.
  Croyance en `dit:`, confiance et rang du ouï-dire ; date d'observation conservée, constat propre de
  même date ou postérieur prioritaire. Les destinataires déjà servis sont sauvegardés dans la croyance,
  communs à l'observation et aux relais ; revoir le même état ne relance pas la confidence. Une source
  mobile absente de son ancienne case n'est plus réputée éteinte par cette absence seule.
  Au plus une confidence par minute du jeu, par un repère sauvegardé commun à toutes les nouvelles ;
  la durée ordinaire d'une parole reste inchangée.
  Mesure `constats_confies`, tests d'état et de parole après recharge et même laps découpé ;
  [rapport](taches/rapport-codex-55-constats-partages.md). Restent pour la suite de 3f le besoin sans
  recours, les avis/disputes et rejoindre un lieu pour sa compagnie.
- **Mesures** : `avis_exprimes`, `changements_d_avis` (par source : vu, dit, deviné), `disputes`,
  `disputes_vues` (par un tiers), `partis_pris`, `justesse_avis_fin` (part des PNJ dont l'avis sur
  la menace de leur lieu est vrai en fin de nuit).
- **Épreuve** : la crue, 8 graines (pic haut et pic bas tirés de la graine), et une variante sans
  transmission des avis pour comparer `justesse_avis_fin`. Tests : Aubin, qui a vu l'eau aux
  vannes, dit à Gorm que le refuge sera gagné ; Gorm, qui ne l'a pas vue, doute ; Aubin insiste
  devant Ilse, qui le croit (elle lui fait confiance) et monte.
- **Critère** : des disputes dans la moitié des nuits où les avis divergent ; qui a vu convainc plus
  souvent qu'il n'est convaincu ; `justesse_avis_fin` plus haute qu'avec la variante ; aucune
  dispute hors des prédicats admis.

### 3g. Luna

- Faits (`signes_percus`, `impressions`, `relations` et `emotion` des interlocuteurs), consignes,
  audit par citation (§ 8).
- **Mesure** : les bancs Luna (trois bancs de référence et le banc `echanges`, `--fil`), plus un
  banc `attitudes` (préparé par placement : Ilse à l'écart de Brune, Gorm qui surveille, une
  dispute en cours, une proposition du joueur). Appels et secondes par tour MJ, replis, refus,
  attributions refusées.
- **Critère** : appels par tour au plus +10 % ; dans le banc `attitudes`, aucune attitude affichée
  sans signe ou impression cité ; vérifié aussi sur des copies de la sauvegarde réelle.

## 10. Ce qui serait un script, à éviter

- Une relation écrite pour un couple de personnages ailleurs que dans les liens de départ ; un
  événement qui ne passe pas par la table `EPREUVES`.
- Un signe produit pour qu'une scène soit lisible (« Ilse tremble devant Brune » parce que c'est
  Brune) ; un signe sans état qui le produise.
- Un avis sur un prédicat que le moteur ne sait pas évaluer (« la digue tient ») ; une dispute
  déclenchée par un lieu ou une minute.
- Un ordre des recours par personnage (« Brune propose avant de voler ») : il sort des coûts et des
  chances.
- Une phrase de Luna sur une attitude qui ne s'appuie sur rien du moteur.

## 11. Risques et limites

- **Tout devient réglage.** Cinq axes, des modulations, des demi-vies : les nombres se règlent au
  banc, par scénario contrasté ; le récit doit dire chaque changement de bande avec sa cause, sinon
  on ne réglera rien. Commencer par peu d'événements (ceux de la table) et ne rien ajouter sans
  mesure.
- **Temps de calcul.** Les signes entrent dans l'empreinte de la vue mémorisée ; les relations
  dans les entrées des recherches gardées. Un oubli fait une vue ou un plan périmé : les deux
  vérifications existent et doivent tourner à chaque sous-étape.
- **Mémoire.** Les motifs sont bornés à trois par relation ; le reste du récit vient de la
  chronique.
- **Méprises et lisibilité.** Un joueur qui lit mal (PSY basse) recevra des impressions fausses
  présentées comme les vraies : c'est voulu, mais il doit pouvoir le savoir (sa PSY figure sur sa
  fiche, l'impression vague se dit « peut-être »).
- **Dérive des nuits.** Le tirage à part protège les jets existants, mais les comportements
  nouveaux (place, regard) changent la suite des nuits : les comparaisons se font sur les mesures
  et le récit, pas sur l'empreinte, dès 3b.
- **L'auditeur de Luna reste sémantique** pour repérer qu'une phrase prête une attitude.

## 12. Décisions à trancher

1. **Les axes.** (a) cinq axes de 0 à 100 (confiance, affection, rancune, peur, dette) ; (b) deux
   axes bipolaires (confiance, affection − rancune) plus peur et dette ; (c) la confiance seule,
   graduée. *Recommandé : (a)*, qui permet l'ambivalence (aimer et en vouloir) et reprend
   `docs/plan-social.md`.
2. **Une confiance ou plusieurs.** (a) une seule ; (b) par domaine (dit vrai, respecte mes biens,
   tient parole). *Recommandé : (a)*, avec les motifs pour le récit ; scinder si le banc montre des
   contresens (un menteur honnête avec les biens).
3. **La dette.** (a) un axe moral dans la relation, la créance matérielle restant à
   `echanges-argent` ; (b) un compte typé par service rendu. *Recommandé : (a)*, les deux reliés
   par les lignes de la table (§ 3.7).
4. **L'étranger et l'ancre.** Confiance d'un inconnu : 40 (prudence), 50 (neutre) ou 30 ; retour
   de l'affection vers le lien de départ ou vers 0. *Recommandé : 40, et vers le lien de départ* ;
   la confiance ne s'estompe pas.
5. **Les émotions.** (a) la colère seule maintenant, avec l'inquiétude existante ; (b) aussi honte,
   joie, soulagement ; (c) aucune. *Recommandé : (a)* : la colère sert les signes et les disputes,
   les autres n'ont pas encore de règle qui les emploie.
6. **Les signes.** (a) comportements réels (place, regard, guet) qui changent le monde, plus des
   expressions sans effet ; (b) expressions seules, descriptives. *Recommandé : (a)*, la lecture
   devenant un enjeu (un regard qui surveille retient un voleur).
7. **La dissimulation.** (a) VOL pour les expressions et les intentions, ELO pour les mensonges ;
   (b) une caractéristique nouvelle ; (c) PSY (qui comprend les autres sait se cacher d'eux).
   *Recommandé : (a)*, sans caractéristique nouvelle, et seulement quand on a une raison de cacher.
8. **Les jets de lecture.** (a) un tirage à part, compté dans `data` ; (b) le dé commun.
   *Recommandé : (a)*, pour comparer les bancs avant et après sans décaler les autres jets.
9. **Le joueur lit.** (a) signes au bilan, impressions au bilan pour qui il a en face et par
   `observer` ; (b) impressions seulement par `observer` ; (c) tout au bilan.
   *Recommandé : (a)* : les signes sont des faits, l'interprétation demande un peu d'attention.
10. **Le contrat du MJ.** (a) une attitude visible est mécanique : citée d'un signe, vérifiée par
    le moteur ; (b) elle reste de l'ambiance, contrôlée par l'auditeur seul. *Recommandé : (a)*,
    qui étend le mécanisme commun des citations.
11. **« Fiable » dans la parole.** (a) garder l'attribut, devenu un avis sur une personne ; (b) le
    remplacer par le contenu `avis`. *Recommandé : (a)* puis (b) à la sous-étape 3f, sans changer
    ce que le joueur peut dire.
12. **Le domaine des avis.** (a) les seuls prédicats que le moteur évalue (menace, sûreté,
    fiabilité, besoin) ; (b) des questions déclarées par le scénario (« la digue tient »).
    *Recommandé : (a)* ; une question de scénario n'entre que quand sa mécanique existe.
13. **Dire son avis sans qu'on le demande.** (a) quand l'auditeur est en danger d'agir contre et
    qu'on s'en soucie ; (b) seulement si on le demande ; (c) à tout présent. *Recommandé : (a)*.
14. **Regagner la confiance délibérément.** (a) un geste `rendre_service` dont la recherche projette
    l'effet, dès 3e ; (b) seulement par les événements, plus tard un but. *Recommandé : (a)*, borné
    à ce geste. **Précisé par la décision du 2026-10-24 et le lot 120** : recours de dernier ressort
    hors de la recherche, après refus social et moyens ordinaires, avant la faute envers le même
    personnage ; effet établi par un service réellement constaté, jamais par la projection seule.
15. **L'humeur et `relations_pnj`.** (a) les replier dans les relations et les signes, l'humeur
    disparaît ; (b) garder l'humeur comme résumé dérivé. *Recommandé : (a)*, `vols_surpris` gardé
    pour les ventes.
16. **L'ordre avec les chantiers en cours.** `voix` avant 3a (le point d'accès à la confiance
    perçue) ; `besoins` avant 3b (l'hystérésis, le coût sur la sécurité) ; `echanges-argent` avant
    3e (le prix propre). *Recommandé : oui* ; à défaut, 3a peut se brancher sur `fiable` et suivre
    `voix` à la fusion.
17. **Les seuils** (méfiance sous 30, confiance dès 60, hystérésis de 10, demi-vies) : accepter la
    méthode et laisser les nombres au banc. *Recommandé : oui.*
