# Plan — PNJ comportementaux

Objectif : des PNJ qui agissent d'eux-mêmes à partir de ce qu'ils perçoivent, croient,
veulent et ressentent, sans script par scénario. L'auteur déclare des données (besoins,
pulsions, rôle, savoirs initiaux) ; le comportement émerge d'un mécanisme commun.

## Principe : qui décide quoi

| Couche | Décide | Contrôle |
|---|---|---|
| Perception | ce que le PNJ voit et entend, avec les mêmes règles que le joueur (lumière par case, ligne de vue, sons) | moteur |
| Croyances | ce que le PNJ tient pour vrai, avec source, minute et confiance ; elles peuvent être fausses ou périmées | moteur, alimentées par la perception et par les paroles |
| Besoins | jauges qui évoluent avec le temps et les événements (sécurité, devoir, richesse, lien social, repos…) | moteur, déclarées par l'auteur |
| Buts | conditions sur le monde *telles que le PNJ les croit* (« la cloche est au refuge », « le voleur est parti ») | moteur : générés par besoins + croyances |
| Intention | le but retenu et un plan court, choisis par utilité | moteur |
| Actions | pas, portes, prendre, poser, appeler, attendre, suivre, fuir… | moteur, mêmes règles physiques que le joueur |
| Voix | ce que le PNJ dit et comment, à partir de *ses* croyances, buts et humeur | Luna |
| Interprétation | ce que le joueur affirme ou demande au PNJ, en propositions typées | Luna propose, le moteur valide |

Luna ne choisit pas les actions des PNJ : elle les raconte et leur donne une voix. C'est la
suite directe du contrat actuel (présence et position des PNJ sont mécaniques) et de la
règle des paroles : ce que le joueur dit à Gorm établit que Gorm l'a entendu, pas que c'est
vrai ; Gorm en tire une croyance dont la confiance dépend de sa relation au joueur.

## Modèle de données (par PNJ, dans `data["esprits"][id]`)

- `croyances` : `{(sujet, attribut): {valeur, source: vu|entendu|dit:<id>|deduit, minute, confiance}}`.
  Sujets : objets, personnages, lieux. Attributs bornés : `lieu`, `possesseur`, `etat`
  (ouvert, allumé…), `present`, `intention_hostile`, `fiable`.
- `besoins` : `{nom: {valeur 0–100, derive_par_heure, seuil_urgence}}`, déclarés par l'auteur.
- `pulsions` : buts permanents de l'auteur, exprimés avec le même vocabulaire de conditions
  (ex. Gorm : `{"objet": "cloche", "attribut": "lieu", "valeur": "refuge"}` lié au besoin `devoir`).
- `intention` : but courant, plan (liste d'actions typées), minute de décision.
- `memoire_evenements` : événements perçus bornés (sons, vols surpris, paroles), qui
  remplacent `dernier_son_entendu`, `relations_pnj.soupcon` et `humeur`, alors dérivées.

## Boucle (à chaque minute écoulée, dans `Moteur._terminer_etape`)

1. **Percevoir** : champ de vision et audition calculés depuis la case du PNJ.
2. **Réviser les croyances** : ce qui est vu remplace ce qui était cru ; un objet attendu
   mais absent devient « lieu inconnu » ; un vol aperçu crée `intention_hostile` sur le joueur.
3. **Faire évoluer les besoins** (dérive, événements).
4. **Délibérer** si l'intention est accomplie, impossible, ou dépassée par un besoin plus urgent :
   score d'utilité = urgence du besoin × probabilité crue de réussir − coût (minutes, risque).
5. **Planifier** : recherche bornée (profondeur ≤ 4) sur la bibliothèque d'actions, à partir des
   croyances, pas de la vérité : Gorm peut aller chercher la cloche là où il la croit.
6. **Agir** : une action par minute, validée par le moteur comme celle du joueur ; un échec
   (porte verrouillée) révise les croyances et relance la délibération.
7. **Annoncer** ce que le joueur perçoit de ces actions ; le reste reste caché.

Déterminisme : aucune part aléatoire hors des jets du moteur, déjà reproductibles par graine.

## Rôle de Luna

- Contexte des PNJ présents : croyances pertinentes, but courant, besoin dominant, humeur
  dérivée. Jamais la vérité du monde à la place de leurs croyances.
- Nouvelle proposition typée `parole_joueur` : `affirmation` (sujet, attribut, valeur) ou
  `demande` (une condition-but). Le moteur l'enregistre comme croyance ou comme but candidat ;
  il l'adopte si la confiance et les besoins du PNJ le justifient. Mensonge et persuasion
  deviennent des mécaniques : convaincre Gorm que la cloche est déjà au refuge change son plan.
- Le garde-fou existant s'applique : Luna ne nomme que ce que le joueur perçoit ; ce que le
  PNJ dit croire est une parole, pas un fait.

## Stratégies établies par Luna

La délibération a deux étages, interchangeables derrière le même contrat de plan :

- **Planificateur du moteur** (déterministe, gratuit) : routines et buts simples, par chaînage
  arrière sur les préconditions des actions (manger ← avoir de la nourriture ← ouvrir le
  garde-manger ← crocheter ← avoir des crochets ← aller les prendre).
- **Stratège Luna** : appelé seulement quand un besoin devient urgent sans plan évident, ou
  pour un PNJ important proche du joueur. Il reçoit l'esprit du PNJ (croyances, besoins,
  traits, capacités), jamais la vérité du monde, et renvoie un plan typé.

Plan typé : `{pnj, but, etapes: [{operation, cible, outil, destination, methode, condition}],
justification}`. Les opérations sont celles des séquences composées du joueur. `condition`
est un garde évalué par le moteur au moment d'agir : `sans_temoin` (aucun autre personnage
ne perçoit la case du PNJ, joueur compris), `lieu_vide`, `porte_fermee`…

Validation à la proposition : chaque cible figure dans les croyances du PNJ, chaque opération
est dans ses capacités (compétences, outils crus disponibles), les limites dures de l'auteur
sont respectées (traits, ex. « ne blesse personne »). Validation à l'exécution : chaque étape
est revalidée sur l'état réel, comme pour le joueur ; un échec révise les croyances et relance
la délibération. Le plan est sauvegardé ; son exécution est déterministe.

`sans_temoin` est jugé sur ce que le PNJ croit percevoir, mais les témoins réels sont ceux
qui le perçoivent : un joueur tapi dans l'ombre peut surprendre un PNJ éclairé qui se croit seul.

**Répartition retenue.** Le planificateur du moteur fait l'essentiel : les stratégies
pratiques comme le garde-manger sont une recherche sur préconditions qu'il résout de façon
exacte, immédiate et gratuite. Luna intervient là où un moteur demanderait de tout coder à
la main : générer des buts à partir d'une personnalité décrite en prose, choisir et formuler
une stratégie sociale, juger l'usage d'un objet que personne n'avait prévu. Elle décide
rarement du *quoi* et du *pourquoi* ; le moteur décide souvent du *comment*. Son apport est
mesuré par le banc sans joueur, pas supposé.

## Expression et compréhension selon les caractéristiques

Le joueur écrit une intention de parole (« je veux convaincre Gorm de me prêter ses crochets
en promettant de les rendre ce soir ») ; la réplique effectivement prononcée dépend de
l'INT (précision, vocabulaire) et du CHA (tact, aisance) du personnage. Même règle pour la
voix des PNJ et pour ce qu'ils comprennent.

- **Le moteur décide, Luna rédige.** Le moteur fixe une bande d'expression à partir des
  caractéristiques (et d'un jet si la réplique vise à persuader) ; Luna écrit la réplique dans
  cette bande. L'effet mécanique (persuasion, croyance transmise) se calcule sur l'intention
  typée, les caractéristiques et le jet, jamais sur les mots choisis par Luna : le joueur n'est
  pas pénalisé par l'aléa de rédaction.
- **Ce qui est entendu, c'est la réplique rendue.** Elle est enregistrée comme parole avant
  affichage ; une intention complexe portée par une INT faible perd des détails (quantités,
  noms, conditions) dans la croyance transmise.
- **Compréhension par l'auditeur** : un PNJ d'INT faible retient une version simplifiée ; la
  confiance et la relation pèsent ensuite sur l'adoption de la croyance (phase 5).
- **Compréhension de l'environnement** : les déductions offertes par la narration sont des
  indices de l'état avec un seuil (INT ou PER passive), pas une liberté de Luna ; l'ambiance
  adapte seulement son registre.
- **Contrôle du joueur** : la réplique s'affiche comme « Tu dis : « … » ». Pour une réplique
  à enjeu, un aperçu permet de dire, reformuler ou annuler, comme `tenter` pour une action.

## Plusieurs PNJ et émergence

Visée : plusieurs PNJ vivent dans le même monde que le joueur, chacun avec ses besoins et
ses stratégies ; les histoires naissent de leurs interactions, pas d'un script.

Conditions pour que l'émergence soit intéressante plutôt que du bruit :

- **Tensions** : ressources rares et besoins concurrents (nourriture pendant la crue, la cloche,
  l'argent, un abri). Sans conflit, chacun satisfait ses besoins et rien n'arrive.
- **Asymétrie d'information** : chacun agit sur ses croyances ; les erreurs, rumeurs et
  mensonges créent les retournements.
- **Couche sociale** : les PNJ se perçoivent entre eux et ont des croyances les uns sur les
  autres (fiable, voleur, allié). Un échange entre PNJ est une transaction typée du moteur
  (transmettre une croyance, demander, promettre, accuser), avec la même confiance que pour
  le joueur. Luna ne le met en mots que si le joueur l'entend.
- **Mémoire et conséquences** : un vol découvert change durablement les relations ; les
  promesses non tenues aussi.
- **Lisibilité** : une histoire n'existe que si le joueur peut la remarquer : traces (serrure
  forcée, objet déplacé), témoignages, rumeurs, changements de comportement.

Moyens :

- **Niveau de détail** : simulation complète des PNJ proches du joueur ; pour les autres,
  pas de minute à minute mais une résolution par blocs de temps, avec les mêmes règles
  et sans appel au stratège.
- **Budget du stratège** : plafonné par heure de jeu ; priorité aux PNJ que le joueur perçoit
  ou qui agissent sur ce qu'il possède.
- **Banc sans joueur** : faire tourner le monde plusieurs heures de jeu, joueur passif, et
  produire une chronique (actions, croyances changées, conflits). Mesures : événements
  distincts, plans réussis et abandonnés, contradictions, appels. C'est l'outil pour régler
  l'émergence avant d'y jouer.
- **Commande de debug** `esprit <pnj>` et chronique complète en mode `--debug`.

Premier jalon : un bac à sable de trois ou quatre PNJ aux besoins concurrents, sur une durée
de quelques heures de jeu, observé par le banc sans joueur.

## Bac à sable : le Relais des crues

Le Relais réunit déjà ce dont les PNJ ont besoin pour être mis à l'épreuve : mode cases et
lumière par case (perception réaliste), une porte verrouillée et sa clé, des outils
(crochets, pied-de-biche, marteau), un étage, et une situation tendue que l'introduction
annonce : Gorm prépare l'accueil des habitants évacués. Les PNJ suivants seront ces évacués,
ajoutés comme données de scénario. Un autre lieu ne serait envisagé que si le Relais
bloquait une mécanique.

## Profil de Gorm (proposition, à valider)

Données d'auteur ; tout le comportement en découle par le mécanisme commun.

- **Caractéristiques** : FOR 14, DEX 10, INT 11, PER 13, CHA 9. `vigilance` devient dérivée de PER.
- **Traits** (prose pour Luna, bornes pour le moteur) : bourru, honnête, protecteur des
  évacués, méfiant envers qui l'a trompé. Lent à faire confiance, lent à la retirer.
- **Limites dures** : ne vole pas, ne blesse personne hors légitime défense, ne quitte pas
  le relais tant que des évacués y sont attendus.
- **Besoins** :
  | besoin | départ | dérive | sens |
  |---|---|---|---|
  | devoir | 60 | +10/h tant qu'une pulsion n'est pas satisfaite | préparer le refuge |
  | biens | 10 | événementiel (vol, objet disparu) | protéger son matériel et son argent |
  | sécurité | 10 | événementiel (bruit violent, menace) | sa sécurité et celle des évacués |
  | faim | 20 | +4/h | manger |
  | repos | 10 | +3/h | s'asseoir, dormir |
- **Pulsions** : la cloche est au refuge (devoir) ; le brasero est allumé (devoir) ; son
  matériel est dans la conduite ou en sa possession (biens).
- **Croyances initiales** : ce qu'il voit au départ, plus ses savoirs d'auteur : la cloche est
  dans la galerie de ronde, la porte étanche est verrouillée, la clé est au refuge, les
  crochets, le marteau et le pied-de-biche sont à lui et rangés dans la conduite, le joueur
  est fiable a priori (confiance moyenne).
- **Capacités** : marcher, ouvrir et fermer, verrouiller avec la clé, prendre et poser,
  appeler, allumer ; pas de crochetage (DEX moyenne, pas de compétence).

## Écarts retenus au jalon B

- `reaction_son` reste un réflexe déclaré (intention `alerte`) : le remplacer par le besoin
  `securite` n'apportait rien tant qu'aucune méthode ne répond à ce besoin.
- `securite` et `repos` sont déclarés et dérivent, sans méthode pour les satisfaire.
- Les outils de la conduite restent sans propriétaire, pour ne pas changer le jeu du joueur ;
  les biens de Gorm sont la réserve, ses vivres et la clé de la réserve. La pulsion du
  brasero allumé est reportée (pas de source de feu chez Gorm). `vigilance` n'est pas
  encore dérivée de PER.
- Au banc, Gorm reste dans la conduite et ne découvre la réserve forcée que s'il revient
  au refuge : sans routine (ronde, accueil), l'émergence reste mince. C'est la première
  piste pour D.

## Écarts retenus au jalon C

- L'aperçu avant de dire (dire, reformuler, annuler) n'est pas fait : il doublerait les
  échanges pour chaque réplique à enjeu. Le contrôle du joueur passe par les guillemets
  (mot pour mot) ; l'aperçu reste possible si le rendu agace en jeu.
- Les indices d'environnement à seuil d'INT ou de PER sont reportés : aucun scénario n'en
  déclare encore.
- Banc Luna réel (Relais, 7 répliques, Corvus 17/17 puis 6/6, 111 appels sur 150) : les
  répliques diffèrent nettement selon la bande ; le même mensonge est cru à 17 de CHA,
  rejeté à 6, et Gorm répond ensuite d'après ce qu'on lui a dit (« On m'a dit qu'elle était
  au refuge du relais ») ; aucune mention sans fondement dans la voix de Luna.

## Écarts retenus au jalon D

- Pas de niveau de détail hors champ : mesuré à quatre PNJ, le moteur fait 8 h de jeu en
  5,5 s, soit environ 60 ms par tour de 5 minutes ; la simulation complète reste exacte et
  suffit. À reprendre si un scénario multiplie les PNJ ou les longues attentes.
- Pas de demande ni de don entre PNJ (Ilse affamée ne demande pas à Gorm) : les nouvelles
  suffisent aux histoires de D ; les promesses et les accusations directes restent à faire.
- `relations_pnj.soupcon` et `humeur` ne sont pas encore migrés : la méfiance envers le
  joueur en est dérivée (`vol.mefiance`), sans les remplacer.
- Au banc, l'histoire est toujours celle de Brune : sur quatre graines, elle crochète vers
  190 minutes sous les yeux d'Ilse et d'Aubin, et seuls les jets de persuasion varient (Gorm
  croit Aubin, ou doute des deux mais verrouille quand même). La variété viendra du joueur
  et de nouveaux besoins.
- `securite` n'a encore pour méthode que les rondes déclarées ; `repos` aucune.
- Les tests des jalons A à C isolent Gorm et Brune (`tests.support.sans_evacues`) ; le
  Relais à quatre est couvert par `tests/test_social.py` et le banc.

## Écarts retenus au jalon E

Critère fixé avant toute mesure, sur 4 graines (1985, 7, 42, 2024) × 8 h sans joueur : aucune
violation, +50 % d'événements distincts hors routine, −30 % de minutes de besoin urgent sans
intention, au plus 2 appels par heure. Cinq bancs, chaque fois après correction d'un défaut
général trouvé en lisant les chroniques ; le critère n'a pas changé.

| Banc | Ce qui a changé | Événements D → E | Oisiveté urgente D → E | Appels/h |
|---|---|---|---|---|
| e1 | premier stratège | 9 → 10 (+11 %) | 1170 → 1071 (−8 %) | 2,09 |
| e2 | leviers : repos, part de nourriture servie, évacués qui connaissent Gorm | 10 → 12,75 (+28 %) | 1160 → 1084 (−7 %) | 2,0 |
| e3 | refus mémorisé, une autre voie ne bloque plus le moteur | 10 → 11,25 (+13 %) | 1160 → 1064 (−8 %) | 2,0 |
| e4 | le moteur complète chaque geste (ouvrir, aller, outil) | 10 → 13,5 (+35 %) | 1160 → 1011 (−13 %) | 2,0 |
| e5 | une tâche confiée au joueur n'est pas faite à sa place | 10 → 10,75 (+8 %) | 1160 → 1016 (−12 %) | 2,0 |

Le banc e4 est faussé : dans 3 graines sur 8, Gorm allait chercher la cloche confiée au
joueur, ce que la validation du stratège laissait passer et que l'état valide ne trahissait
pas ; le banc compte désormais ces usurpations comme des violations. Sur e5, 4 graines de
robustesse (3, 11, 99, 500) donnent 10 → 11,5 événements et 1125 → 1123 minutes ; les minutes
où un besoin urgent avait quelque chose à faire sans plan, mesure ajoutée après e1 et hors
critère, baissent de 340 à 199 (−41 %). Aucune violation, aucune usurpation.

- Le critère n'est pas atteint : le stratège n'est pas activé par défaut, il reste l'option
  `--stratege` du jeu et du banc. Avec les règles d'e5, il ne dégrade aucune partie.
- Ce qu'il apporte : Brune demande d'abord une part à Gorm, puis vole s'il refuse ; Gorm,
  s'il accepte, ouvre sa réserve, la sert et la referme à clé ; Ilse prévient Gorm et lui
  demande de garder la réserve fermée ; personne ne reste affamé sans rien tenter.
- Ce qui le limite : la plupart de ses décisions sont des rondes que le moteur ferait aussi ;
  le Relais n'a qu'une tension, la faim de Brune ; la sécurité d'Ilse et d'Aubin est urgente
  en permanence par conception (c'est elle qui fait tourner leurs rondes), si bien que
  l'oisiveté urgente compte des minutes où il n'y a rien à faire.
- Essayé et retiré : apaiser un besoin quand sa pulsion est rétablie. Une ronde rassurait
  Ilse et Aubin pour des heures ; leurs rondes cessaient, Brune volait sans témoin dès la
  dixième minute et il ne se passait plus rien : le monde du moteur seul s'appauvrissait,
  ce qui aurait faussé la comparaison.
- Luna refusait d'abord de faire voler Brune, même affamée : le stratège joue le caractère
  tel qu'il est écrit, et un besoin à 95 passe outre ses scrupules.
- Pistes : plus de tensions dans le scénario (besoins concurrents, ressources rares) plutôt
  qu'un stratège plus fin ; une sécurité qui se gagne autrement que par des rondes ; la
  priorité aux PNJ que le joueur perçoit (le budget va aujourd'hui au premier besoin).

## Écarts retenus au jalon F

Tensions ajoutées au Relais, comme données du scénario sur des mécanismes communs :
- tous ont faim avant la fin de la nuit, et la réserve n'a que 4 parts ;
- les évacués trempés ont froid et vont se chauffer au brasero de l'échoppe ;
- le brasero brûle 150 minutes, plus deux charges de fagots que Gorm garde aux vannes.

Banc moteur seul, 4 graines × 8 h, avant → après F (pas de critère fixé d'avance : la mesure
décrit le changement, elle ne tranche rien).

| Graine | Événements distincts | Échanges | Vols vus | Oisiveté urgente | Sans recours |
|---|---|---|---|---|---|
| 1985 | 10 → 17 | 2 → 8 | 14 → 0 | 1125 → 1120 | 305 → 650 |
| 7 | 10 → 24 | 2 → 9 | 16 → 12 | 1125 → 950 | 305 → 340 |
| 42 | 10 → 20 | 2 → 8 | 10 → 0 | 1125 → 1175 | 305 → 530 |
| 2024 | 10 → 19 | 2 → 8 | 16 → 0 | 1265 → 1180 | 445 → 650 |

- Les histoires divergent maintenant d'une graine à l'autre. Avant F, c'était toujours Brune
  qui crochetait vers 190 minutes. Selon les graines :
  - Gorm sert Brune, ou la refuse, et elle crochète ;
  - Ilse refusée attend et redemande ;
  - Gorm garde la dernière part et finit par la manger ;
  - Brune, devenue suspecte, se voit refuser une part par méfiance.
  Le feu tient jusque vers 390 minutes, puis le bois manque.
- Les minutes urgentes sans recours augmentent : c'est la rareté voulue (parts refusées, feu
  mort en fin de nuit), pas une panne du planificateur.
- Défauts généraux trouvés en lisant les chroniques et corrigés :
  - le feu se consumait d'un bloc au début d'une attente, et non minute par minute avec les PNJ ;
  - un PNJ croyait vif un feu vu une heure plus tôt ;
  - qui cherchait quelqu'un ne regardait jamais la salle où il arrivait ;
  - Gorm reverrouillait sa réserve au milieu du service, en boucle ;
  - après avoir mangé, il la laissait ouverte ;
  - un refus sur la nourriture interdisait de demander autre chose ;
  - une ronde, toujours urgente, passait avant la faim et la parole donnée.
- Banc A/B du stratège sur le Relais de F, critère d'E inchangé : 20 → 21 événements
  (+5 %), 1106 → 1100 minutes d'oisiveté urgente (−1 %), 2 appels par heure, aucune
  violation. Sur 4 graines de robustesse : 18,25 → 17,75 événements, 1164 → 991 minutes. Le
  moteur fait désormais seul ce qui était l'apport principal du stratège (demander avant de
  voler) ; il reste optionnel.
- Luna, en vrai, sur la chaîne du joueur :
  - « Je remets du bois dans le brasero » (fagots portés) et « Je prends les fagots puis je
    recharge le brasero avec » (fagots au sol) deviennent `alimenter`, précédé de `deplacer`
    dans le second cas ; l'état rechargé est juste ;
  - « Je ramasse les fagots et j'en mets une brassée dans le feu du brasero » échouait deux
    fois. Deux causes générales, corrigées après le jalon (branche `recharger-foyer`) :
    `deplacer` un combustible vers un foyer était refusé (un foyer n'est pas un contenant), et
    le titre de `deplacer` vers le joueur annonçait un rangement « dans ta besace » que l'état
    ne modélise pas, si bien que la contre-revue refusait « ramasser » comme un changement non
    demandé. Désormais : mettre un combustible dans un foyer, c'est l'alimenter ; le combustible
    est porté ou à portée de main ; le titre dit « Prendre ». Vérifié avec Luna en console
    réelle et après rechargement (`tools/test_brasero_reel.py`) : la phrase d'origine, « je
    jette une brassée de fagots dans le brasero » (fagots au sol) et « je mets du bois dans le
    feu » (fagots portés) rechargent le brasero d'une charge.
- Non fait :
  - les PNJ ne se rallument pas un feu sans outil d'allumage (seul le joueur a un briquet) ;
  - on ne se partage pas le bois, et le froid n'a d'autre recours que le brasero ;
  - la sécurité reste satisfaite par les seules rondes, désormais rangées en routine.

## Jalon G — le feu partagé

**Constat après F.** Seul le briquet du joueur allume une flamme : un feu éteint ne se rallume
que si le joueur l'a laissé à Gorm. Le bois tient en un tas de deux charges (240 minutes) qui
appartient à Gorm ; le brasero en a 150. Au plus tard vers la septième heure, le feu meurt, et
le froid des évacués n'a plus de recours : `_plan_chauffer` ne cherche qu'un foyer cru allumé.
Le Relais contient pourtant d'autres flammes : le fanal du refuge (720 minutes, fixe), la
torche de l'antichambre (30 minutes, mobile), la lanterne du joueur.

### G1. Une flamme en allume une autre

Règle générale, commune au joueur et aux PNJ : pour allumer une source, il faut un outil
d'allumage **ou une autre source allumée et intacte**, portée ou à portée. La source qui
donne la flamme ne se consume pas pour autant ; la cible garde ses conditions (combustible,
intégrité). Une source fixe ne se déplace pas : on lui apporte la cible (la torche au fanal),
jamais l'inverse.

- Joueur : `allumer` dans `operations.py` accepte cette source comme outil, choisie par le
  moteur si l'outil est omis, comme le briquet aujourd'hui.
- PNJ : `pnj.py` accepte la même source ; le planificateur cherche, sur ses croyances, une
  flamme qu'il croit allumée : portée, à prendre (la torche), ou fixe et rejointe avec la
  cible en main. Chaîne attendue de Gorm, brasero éteint, sans briquet : prendre la torche,
  l'allumer au fanal si elle est éteinte, aller à l'échoppe, allumer le brasero.
- Une flamme crue allumée peut s'être éteinte en route (la torche n'a que 30 minutes) : le
  geste échoue, la croyance est révisée, le plan est recalculé, comme pour une porte.

En jeu : Gorm rallume seul ; tu allumes ta lanterne au brasero sans briquet ; porter la flamme
d'une salle à l'autre devient un enjeu.

### G2. Le bois se demande comme une part

La part devient une notion commune à toute ressource à usages comptés qui appartient à un
autre : les `portions` des vivres, les `charges` du bois. On la demande à son propriétaire ;
s'il accepte, il fait lui-même l'usage pour le demandeur, comme il sert une part de vivres :
il recharge le foyer (et le rallume grâce à G1). Mêmes règles que les vivres : il ne donne pas
ce dont il a lui-même besoin, se méfie de qui l'a trompé, et un refus est mémorisé par objet.

Ce qu'il garde pour lui devient une donnée de profil, au lieu de la règle écrite aujourd'hui
dans `echanges.demander` (`portions < 2` : chacun garde exactement une part) :
`reserve`, le nombre de parts que ce personnage garde de toute ressource comptée qu'il
possède, 1 par défaut. La règle des vivres migre vers cette donnée dans le même jalon, sans
changer le comportement des parties existantes : un Gorm prévoyant en garde 2, un généreux
aucune, et le moteur n'a aucune branche propre au bois ou aux vivres.

Le froid gagne le même ordre de recours que la faim, au lieu de se limiter à rejoindre un feu
allumé :
1. un foyer cru allumé : s'y chauffer (inchangé) ;
2. un foyer froid ou qui baisse, avec du combustible à soi ou à personne et une flamme :
   l'alimenter, l'allumer ;
3. du combustible à un autre : lui en demander une part ;
4. sans scrupule (pas de `ne_vole_pas`), le bien d'autrui, sans témoin ; à bout, le besoin
   l'emporte sur la crainte d'être vu, comme pour la faim.

En jeu : quand le feu baisse et que Gorm garde sa dernière brassée, les évacués la lui
demandent ; Brune peut la prendre aux vannes ; tu peux demander du bois à Gorm, ou lui en
apporter.

### Hors périmètre

D'autres remèdes au froid (couvertures, vêtements secs), du bois tiré de la poutre (la coupe
ne crée pas encore de fragments), une sécurité gagnée autrement que par les rondes (piste
d'un jalon H).

### Fin de jalon

Comme les précédents : le cas réel et un autre cas de même nature, état et affichage après
rechargement. Banc moteur seul sur les 8 graines habituelles, sans appel à Luna : nombre de
feux rallumés sans le joueur, minutes de froid urgent sans plan, aucune violation des
limites. Luna en vrai sur les phrases du joueur : « j'allume ma lanterne au brasero »,
« je demande du bois à Gorm ».

### Décisions

1. Ce qu'un propriétaire garde pour lui est la donnée de profil `reserve` (1 par défaut, la
   règle actuelle des vivres y migre). Gorm garde sa dernière charge de bois comme sa dernière
   part de vivres : c'est elle qui crée la tension.
2. Le bois d'autrui suit les règles générales du vol, sans cas propre au bois ; qui vole
   dépend des limites de chaque profil (`ne_vole_pas`), données du scénario.
3. Allumer à une source fixe se fait en lui apportant la cible : règle physique du moteur,
   déduite de `mobile` et de la portée, valable pour toute source de tout scénario.

## Écarts retenus au jalon G

- Données du Relais (A et B), validées en cours de jalon : la torche du refuge attend éteinte
  avec 60 minutes (allumée, elle mourait à la trentième minute) ; les planches de bac d'Aubin,
  au refuge, deux charges de 90 minutes (sans elles, le feu ne meurt que faute de bois et
  aucune flamme n'y peut rien).
- Défauts généraux trouvés en suivant le feu sur 12 heures, corrigés :
  - dans le noir, un PNJ ne voyait pas qu'un feu s'était éteint : une flamme se voit de loin,
    une source crue allumée sous son regard qui ne brille pas est crue éteinte ; un feu vu
    baisser s'est consumé ;
  - un PNJ ignorait l'état qu'il laissait de ses mains dans le noir et rechargeait deux fois ;
  - un besoin à peine urgent interrompait un plan presque fini (Aubin quittait le brasero
    chargé, torche allumée, pour se reposer) : `INERTIE`, 5 points au-delà du seuil ;
  - une flamme employée brûlait pour rien dans la main : elle est éteinte et gardée.
- Banc moteur seul, 8 graines (1985, 7, 42, 2024, 3, 11, 99, 500), 8 heures, `main` → G :
  19,1 → 28,6 événements distincts (+50 %), 7,6 → 9,8 échanges, 1135 → 1063 minutes urgentes
  oisives (−6 %), 530 → 466 sans recours (−12 %), aucune usurpation. Sur 12 heures, le feu
  mort faute de fagots est rallumé dans 8 graines sur 8, deux fois dans 4.
- Luna en vrai : « j'allume ma lanterne au brasero » et « je rallume la lanterne avec le
  feu », briquet laissé au refuge, allument la lanterne (`tools/test_flamme_reel.py`).
- Non fait :
  - le joueur ne demande pas une part (ni de vivres ni de bois) : la part suppose un besoin
    du demandeur, que le joueur n'a pas ; « je demande du bois à Gorm » n'a pas été vérifié ;
  - le feu reste borné par le bois du Relais : il n'en naît pas d'autre (la coupe de la
    poutre ne crée pas de fragments).

## Jalon H — se sentir en sécurité

**Constat après G.** La sécurité est une jauge sans recours : rien ne la fait baisser, et
aucun événement ne la fait monter (`relancer` ne sert qu'aux biens). Ilse (départ 65, +2 par
heure) et Aubin (58, +4 par heure) sont urgents dès la première minute et le restent toute la
nuit ; leurs rondes, rattachées à ce besoin, ne l'apaisent pas. Gorm et Brune se calment
d'eux-mêmes (−5 par heure) et rien ne les inquiète. D'où des rondes perpétuelles, et une
mesure d'oisiveté urgente qui compte des minutes où il n'y a rien à faire.

### H1. Ce qui inquiète, ce qui rassure

La sécurité devient une jauge vivante, mue minute par minute par ce que le PNJ perçoit, comme
la chaleur par le feu. Règles générales, valeurs par défaut du moteur, que chaque profil peut
nuancer par une donnée `securite` (par exemple : Aubin rassuré surtout par sa ronde aux vannes,
Ilse surtout par la compagnie) :

- inquiète :
  - le noir autour de soi (aucune lumière sur sa case) ;
  - un bruit fort entendu sans en voir la cause (`sons`, déjà perçus par les PNJ) ;
  - un geste illicite vu, une atteinte à une de ses pulsions (comme pour les biens) ;
  - la présence de quelqu'un qu'il ne croit pas fiable ;
- rassure :
  - la compagnie, dans sa salle, d'un personnage qu'il perçoit et croit fiable, le joueur compris ;
  - la lumière sur sa case ;
  - une ronde accomplie : inspecter le lieu qu'il surveille l'apaise d'un coup.

La dérive horaire déclarée reste le fond (l'inquiétude d'Ilse pour la crue) ; ces effets
s'y ajoutent.

### H2. Se mettre à l'abri

Un besoin de sécurité urgent gagne une méthode, comme le froid a le feu : rejoindre un lieu
éclairé où se tient quelqu'un qu'il croit fiable, et y rester (geste qui dure, comme se
chauffer) jusqu'à être rassuré. Les rondes restent des pulsions : routine quand le besoin est
calme, recours parmi d'autres quand il presse. Une ronde accomplie compte pour H1.

En jeu : les évacués se regroupent dans la lumière, près de qui ils croient fiable ; le noir
d'un feu mort les inquiète et les pousse vers le fanal ou vers toi ; Ilse, qui a vu Brune
crocheter, s'en écarte au lieu de tourner sans fin ; ta présence rassure qui te croit fiable,
et inquiète qui ne te croit plus.

### Hors périmètre

La crue comme événement de scénario (complémentaire : elle s'appuiera sur H1 pour inquiéter) ;
la sécurité d'autrui (protéger les évacués, que Gorm déclare dans ses traits) ; fuir une menace
qui se déplace.

### Fin de jalon

Le cas réel et un autre cas de même nature, état et affichage après rechargement. Banc moteur
seul, 8 graines, 8 heures, `main` → H : minutes urgentes oisives (attendu en nette baisse,
puisque la sécurité redevient satisfaisable), rondes accomplies, événements distincts,
aucune violation ni usurpation. Pas d'appel à Luna : aucune phrase du joueur ne change.

### Décisions

1. Les quatre sources d'inquiétude et les trois d'apaisement ci-dessus, avec des valeurs par
   défaut du moteur, nuancées par profil (`securite`) plutôt que codées par personnage.
2. Le joueur compte comme compagnie rassurante pour qui le croit fiable, et inquiétante pour
   qui ne le croit plus.
3. Les rondes restent des pulsions ; accomplies, elles apaisent. Une ronde manquée n'inquiète
   pas en soi (seul ce qui est perçu inquiète).

## Jalons

Une branche par jalon, fusionnée avant d'ouvrir la suivante. Aucun nouveau mécanisme en
cours de jalon sans accord. Fin de jalon : le cas réel et un autre cas de même nature,
état et affichage après rechargement, budget Luna consommé, puis décision de poursuivre.

| Jalon | En jeu | Contenu | Luna |
|---|---|---|---|
| **A. Gorm perçoit et se souvient** — *fait* | il ne voit pas dans le noir ni derrière la poutre ; il croit ce qu'il a vu ou su jusqu'à revoir la place ; un témoin est celui qui perçoit le joueur ; il ouvre les portes et apprend une serrure par l'essai ; tout persiste après rechargement | perception par acteur ; ligne de vue symétrique ; croyances `vu`/`savoir`/`essai` et mémoire (sons, absences, vols surpris) ; intention `rejoindre` exécutée geste par geste (`trajet` migré) ; `esprit <pnj>` en `--debug` | aucun appel |
| **B. Gorm veut** — *fait* | Brune, affamée, va chercher les crochets, attend que personne ne la voie, crochète la réserve et mange ; sous les yeux du joueur elle renonce ; sans crochets elle reste sans plan ; surprise depuis l'ombre (joueur ou Gorm) ; Gorm volé garde ses biens, cesse de déléguer la cloche, va chercher la clé, déverrouille et la rapporte ; sans clé, il renonce | profils, besoins, pulsions (dont déléguées), délibération par urgence, planificateur borné sur croyances, gestes prendre/poser/ouvrir/fermer/(dé)verrouiller/crocheter/manger, garde `sans_temoin`, témoins réels, chronique, `banc_pnj` | aucun appel |
| **C. On peut lui parler** — *fait* | ta réplique est rendue selon INT et CHA (« Tu dis : « … » »), mot pour mot entre guillemets ; un mensonge cru change le plan de Gorm et se découvre quand il voit la vérité ; un mensonge démenti par ce qu'il vient de voir est rejeté ; une INT faible transmet moins ; une demande d'objet est refusée s'il en a besoin ou se méfie ; Luna fait parler les PNJ d'après leurs croyances | mode `parole_joueur`, bande d'expression, contenu typé résolu par identifiant ou par nom, jet de CHA et confiance, `mensonge_decouvert`, contrôle des mentions sur la réplique ; objets portés discrets cachés au joueur ; profil des PNJ retiré du contexte de Luna | 3 appels par réplique (interprétation, réponse, audit) |
| **D. Plusieurs PNJ** — *fait* | Ilse et Aubin voient Brune, à bout de faim, crocheter la réserve et le disent à Gorm, qui les croit ou non, referme et verrouille ; ce qu'Ilse voit de toi passe à Gorm puis à Aubin, et Gorm se méfie, reprend la cloche à son compte et te surveille ; Gorm reconnaît son bien entre d'autres mains ; tu entends ce qui se dit dans ta salle | nouvelles et rumeurs typées (jet de CHA du locuteur, confiance décroissante, trois relais au plus), `vu_porter`, rondes `{lieu, periode}` et geste `inspecter`, témoins de toute la minute du geste, besoin extrême plus fort que la crainte d'être vu, Ilse, Aubin et le fanal du refuge, mesures sociales au banc | aucun appel |
| **E. Luna stratège** — *fait, non retenu par défaut* | Brune, peu scrupuleuse, demande une part à Gorm avant de voler, ment à Gorm (« la réserve est déverrouillée »), qui la croit et va la verrouiller ; Gorm qui accepte ouvre sa réserve, sert et referme à clé ; Ilse demande à Gorm de garder la réserve fermée et lui dit que Brune n'est pas fiable ; Aubin se repose ; tu entends ces échanges | gestes sociaux `dire`, `demander` (dont une part de nourriture), `confier`, `remettre`, `servir`, `reposer`, engagements, limite `ne_ment_pas`, stratège consulté sur besoin urgent sans plan, plan illicite ou désœuvrement, plan validé sur les croyances du PNJ et complété par le planificateur, banc A/B | 2 appels par heure de jeu au plus ; option `--stratege` |
| **F. Tensions du Relais** — *fait* | les évacués trempés quittent le refuge pour se chauffer au brasero ; Gorm revoit son feu, va chercher ses fagots aux vannes et le recharge, jusqu'à épuiser le bois ; tous ont faim pour 4 parts : on demande une part à Gorm avant de voler, il sert, refuse ou garde la dernière ; Brune refusée crochète, Ilse refusée redemande deux heures plus tard ; on cherche Gorm quand on l'a perdu de vue ; tu recharges toi-même le brasero | besoin `chaleur`, foyer et combustible (`alimenter`, commun au joueur et aux PNJ, `allumer` pour les PNJ), feu consumé minute par minute avec les PNJ, pulsion de feu entretenu, part demandée par le moteur et attendue près des vivres, refus par objet, recherche d'un personnage, ordre des buts (ce qui presse, parole donnée, ce qu'on finit, routine) | aucun appel ; stratège remesuré |
| **G. Le feu partagé** — *fait* | Gorm, sans briquet, rallume le brasero avec la torche allumée au fanal ; tu allumes ta lanterne au brasero ; quand Gorm garde sa dernière brassée, les évacués demandent une part des planches d'Aubin, qui va lui-même entretenir le feu ; Aubin rallume le brasero mort avec ses planches et la torche allumée au fanal, puis l'éteint et la garde ; tu allumes ta lanterne au feu | une source allumée sert d'outil d'allumage (joueur et PNJ) ; part généralisée aux ressources comptées (`portions`, `charges`), réserve gardée en donnée de profil (`reserve`) ; recours au froid ordonnés comme ceux de la faim ; perception d'une flamme dans le noir, inertie d'un plan en cours, flamme ménagée | aucun appel |
| **H. Se sentir en sécurité** — *proposé* | les évacués se regroupent dans la lumière près de qui ils croient fiable ; le noir d'un feu mort les pousse vers le fanal ou vers toi ; Ilse s'écarte de Brune qu'elle a vue crocheter ; ta présence rassure ou inquiète selon la confiance | sécurité mue par la perception (noir, bruit, geste illicite, méfiance ; compagnie fiable, lumière, ronde accomplie), nuancée par profil (`securite`) ; geste qui dure « se mettre à l'abri » | aucun appel |

Chaque jalon migre ce qu'il remplace (`humeur`, `soupcon`, `vigilance` dérivés) et garde les
parties existantes rechargeables ; le banc des voix (cohérence avec les croyances, aucune
fuite de la vérité) accompagne C et E.

**Mis de côté** jusqu'à ce qu'un jalon en ait besoin : effet « salle inondée / passage
condamné », PNJ sur les échelles, lumière par objet transmise à Luna, cases de pénombre sur
la carte. Les indices d'environnement à seuil (INT, PER) rejoignent C si le mécanisme reste
simple, sinon après.

## Risques

- **Coût de calcul** : perception par PNJ et par minute ; à mettre en cache par révision.
- **Lisibilité** : un comportement émergent doit rester explicable ; une commande de debug
  (`esprit gorm`) montrera croyances, besoins et intention.
- **Un seul PNJ** dans les scénarios actuels : les dynamiques sociales (PNJ entre eux) ne
  seront testables qu'avec un second personnage.
