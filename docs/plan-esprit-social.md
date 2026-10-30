# Plan : l'esprit social des PNJ (mémoire compilée, passé, motifs, normes)

Trace d'une exploration de conception du 2026-10-30 avec l'utilisateur, mise au propre. Ce
document ne décide rien d'autre que ce qui figure en § 13 ; chaque étape demandera un brief et
un accord. Il prolonge `plan-relations.md`, `plan-agendas.md` et `plan-decision.md` sans les
remplacer.

## 1. Direction

- **Un huis clos dense**, sur la temporalité actuelle (une nuit de quelques heures). Le passage
  à plusieurs jours (sommeil, routines, simulation grossière hors du joueur) viendra bien plus
  tard ; rien ici ne doit l'empêcher.
- **Chaque personnage traîne son passé.** Le joueur peut l'apprendre par la conversation, le
  recouper, et **exploiter les failles** qu'il révèle.
- Le monde ne s'organise pas autour du joueur : les PNJ poursuivent leurs propres motifs, et
  ceux-ci peuvent naître de ce qu'ils vivent pendant la nuit.
- **Moins de comportements élémentaires ajoutés au cas par cas** ; plus de motivations qui
  réutilisent les moyens existants.

## 2. Point de départ (code à `0bad227`)

### 2.1 Ce qui est mémorisé

- **Croyances** (`esprits.croyances[sujet][attribut]`) : valeur, source, minute, confiance.
  Révisées seulement quand une observation les contredit. **Aucun vieillissement**, sauf les
  signes et intentions lus (30 ou 120 min) : une personne vue il y a trois heures est encore
  crue là. Le planificateur les tient pour vraies ; la confiance ne pèse que dans la parole.
- **Mémoire des événements** : les 40 derniers souvenirs (`MEMOIRE_MAX`), environ 80 types.
  Elle sert de porte d'écriture aux relations et à la défense, et surtout à une cinquantaine de
  tests ponctuels (« un souvenir de type X depuis telle minute ? »). La fenêtre se compte en
  nombre, pas en temps ni en importance.
- **Registres hors mémoire**, ajoutés lot après lot quand la fenêtre perdait quelque chose :
  `faits_dits`, `refus`, `recherches`, `indices_recherche`, `presence_recherche`, `secours`,
  `detresses_appelees`, `aides_attendues`, `attentes_bornees`, `renoncements`, `donne`,
  `preuves_relations`, `visites`, `voix`, `noms`, `voix_entendues`, `rejoint`, `rejoindre`,
  `urgences`, agendas et engagements. Chacun a sa clé, son effacement, sa validation.
- **Relations** (`relations.py`) : six axes, ancrés, estompés (rancune selon fierté et
  douceur ; peur en 120 min ; affection et ascendant vers le lien de départ). **Confiance et
  dette ne s'estompent pas.** Chaque épreuve **s'additionne** ; seuls les trois derniers motifs
  sont gardés. Exemple : un vol vu puis un service rendu laissent un PNJ méfiant (confiance 20)
  qui **doit quelque chose** à son voleur (dette 20). L'ordre des actes ne compte presque pas ;
  une restitution n'est pas lue comme la réparation du vol.

### 2.2 Motivations et moyens

- **Motivations** : besoins, pulsions, engagements, agendas, réflexes, classés sur l'échelle
  commune des paliers (`deliberation._candidats`) ; l'intention retient `but` et `motif`.
- **Moyens** : le planificateur, recherche exhaustive sur les croyances (proche du GOAP).
- **Valeurs** sur les deux : poids des agendas, prix des moyens (`caractere.prix_faute` selon
  l'honnêteté, `combat.prix_violence` selon la douceur). Un motif n'autorise jamais un moyen.
- **Frapper n'est qu'un moyen**, dans trois cas : se défendre, protéger, assommer pour prendre.
  La rancune module (refus, évitement, signes) ; **aucun but ne vise l'état d'autrui** : ni
  vengeance, ni punition, ni méchanceté.
- **Se tenir à carreaux** passe par une condition binaire `sans_temoin` sur les gestes illicites
  (levée par le désespoir) et par le prix de la faute. Un témoin qui s'en moquerait bloque autant
  qu'un témoin qui dénoncerait.

### 2.3 Comment les autres lisent un acte

- Un coup vu donne `violence_vue` envers l'auteur (confiance −40, peur +20), **quel qu'en soit
  le motif**. La rumeur transmet l'acte sans sa raison.
- Seule exception, partielle : `defense.retenir` ne voit pas une menace dans une riposte si le
  témoin a vu l'agression d'abord (« une intention privée de l'auteur n'est pas une preuve »).
  La relation, elle, prend quand même le coup.
- `agendas.devis_observateur` modélise ce qu'un observateur croit d'un acteur, mais avec un
  profil neutre figé (valeurs 50).

## 3. Principes

1. **Chacun ne raisonne que sur ses propres croyances.** Jamais sur la vraie intention, les vraies
   valeurs ou la vraie mémoire d'autrui.
2. **Déterministe et dans `data`** : même laps découpé, même monde ; sauvegarde complète.
3. **Une règle commune par invariant**, déclarée une fois (tables), jamais un cas propre à un
   personnage, un lieu ou un scénario (`AGENTS.md`).
4. **Second ordre au plus** : « ce que je crois que tu penses ». Pas de « ce que je crois que tu
   crois que je pense ».
5. **Le moteur établit, Luna formule.** Le noyau (passé, secrets, failles, normes, motifs) est en
   données ; ce que Luna improvise de non mécanique est enregistré comme dit, jamais comme vrai.
6. **Un levier exploitable est mécanique** : s'il ne change rien dans le monde, ce n'est pas une
   faille, c'est du décor.

## 4. La mémoire unifiée

Socle de tout le reste. Trois couches et un registre, un seul module d'accès (comme `relations.py`
et `agendas.py`), contrôlé par AST.

1. **Épisodes** : ce qui s'est passé, retenu selon **l'âge et l'importance** (violence, tort,
   dette, secret > routine), pas selon un compte. Le passé d'avant la nuit y entre comme épisodes
   anciens.
2. **Faits** : ce qu'il croit du monde, avec identité, source, date, confiance, et une **règle
   commune de contradiction** (constat propre contre ouï-dire, poids des sources, ancienneté). Les
   croyances actuelles en sont la première forme ; les registres du § 2.1 deviennent des vues de
   ces faits, chacun avec sa règle d'invalidation déclarée.
3. **Dossier de chaque personne connue** : la compilation.
   - un **compte** des échanges (pris, rendu, dû, prêté) où torts et dettes se compensent ;
   - quelques **faits marquants** : le pire, le meilleur, le dernier, ce qui reste en suspens ;
   - les **valeurs estimées** de cette personne (§ 7), avec leur confiance ;
   - les **traits crus** (voleur, secourable, menteur) avec leur source.
   Les axes de relation se calculent à partir du dossier au lieu de s'additionner.
4. **Registre de ce qu'il a dit**, à qui et quand (prolonge `faits_dits`) : condition de la
   cohérence d'une conversation à l'autre, et de la découverte de ses mensonges.

Règles que le dossier rend possibles, toutes générales :
- **réparation** : un acte qui compense un tort connu se lit par rapport à ce tort ; la rancune
  tombe davantage que la confiance ne remonte ;
- **trahison** : un tort venant de quelqu'un d'apprécié pèse à proportion de l'affection ;
- **repentir** : des actes répétés et cohérents après un tort changent le trait cru ;
- **contradiction** : un fait vu et un ouï-dire contraire se tranchent dans le dossier, et le PNJ
  peut dire pourquoi il croit l'un plutôt que l'autre.

### 4.1 Ce qui s'efface avec le temps, et ce qui ne s'efface pas (décision du 2026-10-30)

À l'échelle d'une nuit, trois familles ne vieillissent pas de la même façon :
- **les émotions** (colère, peur aiguë) retombent en quelques minutes quand leur cause disparaît ;
  c'est à peu près le comportement actuel ;
- **les attitudes** (grief, confiance, dette) ne bougent pas avec le temps pendant la nuit, seulement
  par des événements (réparation, excuses, service, nouvelle faute). La rancune actuelle se sépare
  donc en **colère** aiguë et **grief** durable, inscrit dans le dossier ; la demi-vie actuelle de la
  rancune (environ 8 h pour un caractère moyen) disparaît pour le grief. L'oubli lent viendra avec
  plusieurs jours ;
- **les faits sur ce qui change** (position d'une personne, feu qui se consume) relèvent d'une
  prévision ou d'une hypothèse datée, pas d'un taux d'oubli. Ce point est **hors de ce plan** : lot à
  part (voir § 10).

## 5. Le passé

### 5.1 Un épisode ancien

Daté d'avant la nuit, avec : ce qui s'est passé, les personnes concernées (présentes ou absentes),
le lieu, **qui le sait** (mécanisme des statuts du lot 254), sa **charge** (honte, deuil, fierté,
rancune, peur), et ses **effets mécaniques** : une peur et son déclencheur, une valeur décalée,
une dette, une rancune, un agenda en sommeil.

### 5.2 Les failles

| Faille | Levier pour le joueur | Mécanique de rattachement |
|---|---|---|
| secret honteux | chantage, menace de révéler à qui il redoute | peur, ascendant, sanction attendue (§ 7) |
| manque ou désir | offrir ce qu'il veut | valeur des biens, propositions |
| trauma | le mettre en situation, le rassurer | peur avec déclencheur (généralise `peur_du_noir`) |
| croyance fausse | mentir, ou révéler la vérité | avis, poids des sources, mensonge découvert |
| attachement | menacer ou protéger ce qu'il aime | relations, `protege`, loyauté |
| orgueil | flatter, provoquer | fierté, colère, persuasion |

### 5.3 La révélation

Le moteur décide de ce qui est **dicible**, Luna de la façon de le dire :
- **public** : à qui le demande ;
- **confiable** : à qui il fait confiance ;
- **intime** : forte affection, ou sous une émotion (colère, peur, détresse) ;
- **secret** : jamais de son plein gré.

Un secret fuit autrement : par les **signes** (il se tend quand on parle de la mine), par les
**tiers** qui savent, par des **traces matérielles**, par un **mensonge** contredit plus tard. Un
PNJ ment sur son passé selon son honnêteté ; le mensonge est un fait dit, découvrable.

Ce que le joueur apprend entre dans ses connaissances, typé ; il peut ensuite s'en servir par une
parole typée (« je sais ce que tu as fait à la mine »), que le moteur tranche.

### 5.4 Le lore à versions

Un événement réel du lieu (accident, crue, meurtre ancien), dont chacun tient **sa version**,
partielle, déformée ou mensongère selon ce qu'il a vu et ce qu'il veut cacher. Les écarts entre
témoignages sont des indices.

## 6. L'attribution de motif

Valable **pour tous les gestes** (frapper, voler, mentir, refuser, pousser, dénoncer…), pas
seulement la violence.

**Indices, tous tirés des croyances du témoin** : le contexte perçu (B a frappé A avant, B portait
l'objet de A), ce qu'il sait de leur passé (dossier, épisodes), ce que dit l'auteur (parole typée,
crue selon la confiance), ses signes (colère, calme), ce qui suit l'acte (A prend la bourse),
la réputation de A.

**Une table d'hypothèses**, déclarée une fois, chacune avec ses conditions sur ces indices :
défense, protection, vengeance d'un tort connu, punition, intérêt (vol), besoin vital, gratuit.
Le témoin retient la mieux soutenue, ou « je ne sais pas » ; c'est une croyance avec sa confiance.
Elle peut être fausse.

**Le jugement** dépend du couple acte/motif attribué, de ses valeurs (§ 7) et de ses relations
avec l'auteur et la victime ; l'épreuve qu'il reçoit en découle (envers l'auteur, parfois envers
la victime). L'explication **circule** avec la nouvelle (« Gorm a frappé Aubin parce qu'Aubin
l'avait volé ») et peut être contestée (disputes, 3f).

**L'auteur connaît son motif** (intention, épisode) ; il peut le dire ou mentir dessus.

## 7. Les normes perçues

### 7.1 Ce qui retient d'agir

Le prix d'un acte, pour un PNJ, a deux parts :
1. **la conscience** : ses propres valeurs (le `prix_faute` actuel en est la forme) ;
2. **la sanction attendue** : pour chaque personne qui pourrait l'apprendre (témoins crus, chance
   d'une rumeur), sa désapprobation supposée de ce couple acte/motif, multipliée par ce qu'il
   redoute d'elle (peur, dépendance, ascendant, affection qu'il veut garder).

La sanction attendue remplace la condition binaire `sans_temoin` : un témoin indifférent ne
retient plus, un témoin redouté retient même un acte peu grave.

Le psychopathe (conscience nulle) se tient à carreaux tant qu'il croit les autres « normaux » ;
quand il apprend qu'ils ne le sont pas, la sanction s'effondre et il agit.

### 7.2 Ce qu'il croit des autres

- **Par personne** : les valeurs estimées dans le dossier (§ 4), avec leur confiance. Elles
  remplacent le profil neutre figé de `devis_observateur`.
- **Par lieu** : la norme du lieu, **déduite** à chaque lecture des estimations des personnes
  présentes, pondérées par leur influence (ascendant, statut) ; jamais stockée.

### 7.3 L'imprégnation

- **Point de départ** : une culture du lieu déclarée par le scénario, sinon standard ; décalée par
  le caractère (le méfiant suppose les autres pires).
- **Un acte vu et les réactions qu'il provoque** : reproche, refus ultérieur, dénonciation,
  punition, ou silence, tolérance, approbation. Toutes sont des événements perceptibles ; elles
  révisent les valeurs estimées de ceux qui réagissent, et de l'auteur.
- **La parole** : un avis sur la norme (« ici, personne ne te le reprochera »), pesé selon la
  confiance ; le joueur peut mentir.

### 7.4 Jugement privé et réaction publique

- **Le jugement privé** dépend de ses seules valeurs.
- **La réaction publique** dépend du jugement, de la norme qu'il croit en vigueur et de sa peur
  de l'auteur.
- **L'écart possible entre les deux est borné par l'honnêteté** (décision du 2026-10-30) : un
  honnête est peu hypocrite. Proposition : par peur, un honnête peut **se taire** (le courage
  l'aide à parler) mais ne **feint pas** d'approuver ; feindre exige une honnêteté basse. Les
  signes peuvent trahir le jugement privé.

### 7.5 Couples acte/motif

Une petite table croisant les actes (voler, mentir, frapper, trahir une parole, refuser l'aide,
garder une dette, dénoncer…) et les motifs (§ 6). La culture du lieu en remplit les cases ;
les observations les font bouger.

## 8. Les motivations noires

Décidées le 2026-10-30 : **vengeance, punition, humiliation, nuire par jalousie**. Leur but porte
sur l'état d'autrui (« B a payé », « B est déchu aux yeux de C »), atteint par les moyens
existants (frapper, voler, dénoncer, mentir, refuser) ; un motif, plusieurs moyens.

- Elles naissent par la table de naissance commune d'A6 (un tort connu, une rancune vive, une
  jalousie), avec leur poids selon les valeurs et la relation.
- Leur prix suit le § 7.1 : **punir un voleur que la norme condamne rapporte de l'estime** au lieu
  d'en coûter ; d'où une justice spontanée, sans règle écrite.
- Elles se replient en sommeil et cèdent comme tout agenda (ténacité selon la VOL).

## 9. Le joueur et Luna

- **Le joueur** est jugé, attribué et imité par les mêmes règles : s'il frappe impunément, il
  abaisse lui-même la norme de la salle.
- **Ses connaissances** gardent, typés, les épisodes et les faits appris ; ses **leviers** sont des
  paroles typées (révéler, menacer de révéler, invoquer un passé, affirmer une norme).
- **Luna reçoit** : le dossier de l'interlocuteur vu par le PNJ, les épisodes et le lore dicibles
  pertinents pour le sujet abordé, ses secrets (ce qu'il tait, ce sur quoi il ment), sa manière de
  parler. Les questions sur le passé sont typées par sujet (personne, lieu, événement, objet).
- **Noyau fermé, couleur enregistrée** : Luna n'invente ni secret, ni faille, ni lien, ni fait du
  lore ; un détail de couleur improvisé est retenu comme « dit par X », cru par lui, ouï-dire pour
  ceux qui l'entendent.

## 10. Ce qui change dans l'existant

| Aujourd'hui | Devient |
|---|---|
| 40 souvenirs + registres ad hoc | mémoire unifiée, registres comme vues (§ 4) |
| relations additives, trois motifs | axes calculés depuis le dossier (réparation, trahison, repentir) |
| rancune à demi-vie d'environ 8 h | colère aiguë (minutes) et grief durable (événements seulement, § 4.1) |
| croyances sans âge pour ce qui bouge | **hors de ce plan, lot à part** : la position crue d'une personne devient une hypothèse datée, vérifiée (chercher, appeler, demander où il est) avant d'agir dessus ; un feu se prévoit par son combustible connu, comme l'eau |
| `prix_faute` | part « conscience » |
| condition `sans_temoin` | sanction attendue (§ 7.1) |
| `devis_observateur`, valeurs neutres 50 | valeurs estimées du dossier |
| `violence_vue` aveugle au motif | épreuve selon le motif attribué et le jugement |
| rumeur sans raison | rumeur avec son explication |

## 11. Étapes proposées

Une à la fois, chacune avec son invariant, son cas réel et un autre de même nature, vérifiés
après rechargement (`AGENTS.md`).

| Étape | Contenu | Change le comportement ? |
|---|---|---|
| **E0** | Conception de la mémoire : inventaire de toutes les lectures de `memoire` et des registres, schéma des couches, règles d'invalidation, plan de migration. Rapport seulement. | non |
| **E1** | Socle de la mémoire unifiée : seul accès, contrôle AST, registres en vues. | non : empreintes identiques |
| **E2** | Dossier et compte des échanges ; axes calculés depuis le dossier (réparation, trahison, repentir). | oui |
| **E3** | Attribution de motif, pour tous les gestes ; épreuves et rumeurs selon le motif. | oui |
| **E4** | Valeurs estimées d'autrui, culture du lieu, imprégnation ; norme du lieu déduite. Sans lecteur de décision d'abord. | non, puis oui |
| **E5** | Sanction attendue en remplacement de `sans_temoin` ; jugement privé et réaction publique, hypocrisie bornée. | oui, fortement |
| **E6** | Motivations noires par la table de naissance commune. | oui |
| **E7** | Passé et lore à versions : schéma, une tranche verticale sur un scénario, avec Luna. | oui |
| **E8** | Révélation et leviers du joueur (connaissances typées, paroles typées). | oui, côté joueur |
| plus tard | Biographies générées une fois à la création du monde puis gelées ; plusieurs jours. | — |

E4 sans lecteur de décision imite le lot 254 (statuts) : on installe les croyances et leur
apprentissage, on les mesure, puis E5 les branche.

## 12. Mesures et risques

**Mesures** : banc rapide sur les mêmes graines ; récit et chronique lus pour la plausibilité
(chaque choix sous-optimal ou noir porte une raison racontable) ; compteurs des actes illicites
et violents, des motifs attribués (justes et faux), des réactions publiques, des cascades
(un acte impuni suivi d'autres) ; coût de calcul (lectures du dossier dans le planificateur).

**Risques** :
- **la contagion emballée** : une nuit qui bascule dans la violence générale ; bornes à prévoir
  (hystérésis des estimations, poids de la culture de départ) ;
- **le coût** : la sanction attendue lit les estimations de plusieurs personnes dans chaque
  évaluation d'un geste illicite ; elle doit entrer dans les entrées de la mémoire des recherches ;
- **l'inintelligibilité** : un comportement juste mais incompréhensible ; d'où l'exigence d'une
  raison racontable et des signes ;
- **le coût d'auteur** du passé et du lore : schéma fixé à la main sur une tranche avant toute
  génération ;
- **l'interaction avec la feuille de route en cours** (A5, 3d, A6) : E6 recoupe les restes d'A6
  (soupçon, punir) ; l'ordre est à décider.

## 13. Décisions et questions

**Décisions du 2026-10-30** :
1. Huis clos dense sur la temporalité actuelle ; plusieurs jours plus tard.
2. Chaque PNJ a un passé que le joueur peut apprendre et exploiter.
3. Mémoire unifiée, comme socle.
4. Motivations noires (vengeance, punition, humiliation, nuire par jalousie).
5. Attribution de motif pour tous les gestes.
6. « Ce qui est juste » vient des valeurs propres et de ce qu'on croit des autres ; la norme
   s'apprend (imprégnation) ; estimations par personne et norme du lieu déduite.
7. Un honnête est peu hypocrite.
8. Sur une nuit, les émotions retombent en minutes ; les attitudes (grief, confiance, dette) ne
   bougent que par des événements ; la rancune se sépare en colère et grief (§ 4.1).
9. Le vieillissement des faits sur ce qui change (position des personnes d'abord) est un lot à part,
   hors de ce plan (§ 10).
10. Chantage, menaces contre un proche, exploitation d'un traumatisme, manipulation par de fausses
    normes : permis dans toute leur noirceur, au joueur comme aux PNJ, avec leurs conséquences
    mécaniques (peur, haine, vengeance, sanction sociale), sans exclusion de contenu pour le moment.

**Questions ouvertes** :
1. L'ordre des actes compte-t-il (trahison, repentir) ? Recommandé : oui.
2. Biographies écrites à la main pour la tranche verticale, générées ensuite ? Recommandé : oui.
3. Scénario de la tranche : l'auberge (huit PNJ, étrangers à secrets, reliquaire caché) recommandée.
4. Place de ce plan face à A5, 3d et A6 dans la feuille de route : proposition attendue de
   l'orchestrateur.
