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

- Banc A/B, 4 graines × 8 h, critère fixé avant les mesures : aucune violation (atteint),
  +50 % d'événements distincts hors routine (mesuré : 9 → 10, +11 %), −30 % de minutes de
  besoin urgent sans intention (1170 → 1071, −8 %), au plus 2 appels par heure (2,09 : la
  correction d'une proposition refusée échappait au budget, corrigé depuis). Le stratège
  n'est donc pas activé par défaut : il reste l'option `--stratege` du jeu et du banc.
- Ce qui limite l'apport : le stratège refait surtout ce que le planificateur trouve déjà
  (crocheter la réserve, faire une ronde) ; le Relais offre peu de leviers sociaux (les
  vivres sont sous clé, la clé de Gorm est trop discrète pour qu'on la lui demande) ; la
  sécurité et le repos n'ont aucun geste qui les fasse baisser, si bien que l'oisiveté
  urgente reste hors de portée ; 5 à 7 des 16 appels d'une partie corrigent une proposition
  refusée par le moteur (geste contredit par les croyances, mensonge d'un honnête).
- Un premier essai a montré que Luna refusait de faire voler Brune, même affamée : le
  stratège joue désormais le caractère tel qu'il est écrit, et un besoin à 95 passe outre
  ses scrupules comme la crainte d'être vu.
- Pistes avant de reprendre le stratège : une méthode pour la sécurité et le repos, le
  partage d'une part de nourriture, des évacués qui connaissent Gorm dès le départ ; la
  priorité aux PNJ que le joueur perçoit n'est pas faite (le budget va au premier besoin).

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
| **E. Luna stratège** — *fait, non retenu par défaut* | Brune, peu scrupuleuse, pèse le vol, ment à Gorm (« la réserve est déverrouillée »), qui la croit et va la verrouiller ; Ilse demande à Gorm de garder la réserve fermée et lui dit que Brune n'est pas fiable ; un PNJ demande un objet, confie une tâche, remet ce qu'il porte ; tu entends ces échanges | gestes sociaux `dire`, `demander`, `confier`, `remettre` communs au joueur et aux PNJ, engagements, limite `ne_ment_pas`, stratège consulté sur besoin urgent sans plan, plan illicite ou désœuvrement, plan validé sur les croyances du PNJ, banc A/B | 2 appels par heure de jeu au plus ; option `--stratege` |

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
