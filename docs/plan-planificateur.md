# Plan : un planificateur par recherche pour les PNJ

Proposition de jalon, à valider. Première étape de l'ordre retenu dans `docs/plan-crue.md` :
avant d'ajouter des comportements (barrer, fuir, porter le feu, convaincre), remplacer les
méthodes de plan écrites à la main par une recherche sur les actions. Le joueur reste passif ;
tout se mesure au banc sans joueur et à son récit.

## Point de départ

`donjon/deliberation.py` fait choisir à chaque PNJ un but par urgence (`candidats`), puis
cherche un plan avec une méthode écrite pour ce but, dont les recours sont dans un ordre fixe :
- faim : ses vivres, sinon une part demandée, sinon (sans scrupule) le bien d'autrui ;
- froid : un feu vif, sinon ranimer un foyer, sinon une part de bois, sinon le bois d'autrui ;
- pulsions : une branche par forme de condition (ronde, objet à sa place, servir, feu
  entretenu, sous clé) ;
- sous-tâches communes de la classe `Plan` : `aller`, `obtenir`, `acceder`, `rejoindre`,
  `flamme`, `cle`, `outil`, `retablir`.

Environ 480 lignes de méthodes. Chaque capacité nouvelle s'y écrit deux fois (pour le joueur et
pour les PNJ) ; `flamme` sait seulement qu'une torche s'allume à une flamme fixe ;
`assembler`, `decouper` et `prelever` n'existent pas pour les PNJ.

## Ce qui change, ce qui reste

**Remplacé** : les méthodes de plan (`_plan_manger`, `_plan_repas`, `_plan_part`,
`_plan_chauffer`, `_plan_ranimer`, `_plan_part_de_bois`, `_plan_pulsion`, `_plan_garder`, les
sous-tâches de `Plan`), et la complétion des gestes du stratège (`stratege.completer`), qui
passera par le même planificateur.

**Gardé** : le choix du but (urgences, parole donnée, routine), la perception et les croyances,
l'exécution geste par geste revalidée sur l'état réel (`pnj.agir`), les gardes (`sans_temoin`),
les gestes qui durent (se chauffer, se reposer, s'abriter), le stratège Luna en dernier recours.

## Le modèle

**État de recherche** : une projection des croyances du PNJ, jamais la vérité. Où il est, ce
qu'il porte, où il croit chaque objet et chaque personne, ce qu'il croit ouvert, verrouillé,
allumé, chargé ; les promesses qu'on lui a faites ; les refus récents. Le plan simule ce qui
change à mesure (il aura ouvert, pris, allumé).

**Actions** : les opérations existantes des PNJ, chacune déclarée une fois, avec :
- ses **conditions** sur l'état (« dans la salle crue de l'objet », « le contenant cru ouvert »,
  « porte la clé », « capacité crochetage et un outil de crochetage ») ;
- ses **effets** sur l'état (« porte l'objet », « ouvert », « foyer allumé ») ;
- son **coût** en minutes, plus ce que le profil y ajoute ;
- sa **garde** à l'exécution (`sans_temoin` pour le bien d'autrui).

Les opérations : aller, prendre, poser, ouvrir, fermer, déverrouiller, verrouiller,
crocheter, manger, inspecter, alimenter, allumer, éteindre, servir, demander (objet ou part),
attendre une part promise, se chauffer, se reposer, s'abriter. Une action dont l'issue dépend
d'un autre (demander) a un **effet attendu** et une **chance** estimée d'après ce que le PNJ
croit : la confiance que l'autre lui porte, ce qu'il sait du besoin de l'autre, un refus récent.
Son coût est divisé par cette chance. Un geste difficile (crocheter) a une chance qui dépend de
la lumière et des caractéristiques, comme son jet.

**Buts** : des conditions sur l'état, celles qu'on a déjà. Faim : avoir mangé. Froid : se tenir
près d'un feu cru vif. Pulsions : l'objet à sa place, sous clé, le feu entretenu, la salle
inspectée. Le choix du but ne change pas ; seule la façon d'y parvenir est cherchée.

**Le caractère comme coût** : les limites restent des interdits (`ne_vole_pas` exclut toute
action sur le bien d'autrui). Sans limite, un geste illicite coûte cher, et ce coût baisse avec
l'urgence du besoin (au-delà de `DESESPOIR`, il compte peu). Demander coûte un peu, plus après
un refus. Ces coûts reproduisent l'ordre actuel (le sien, puis demander, puis voler) sans
l'écrire ; un profil pourra les nuancer plus tard (un caractère qui préfère prendre que
demander).

**Recherche** : A* en avant depuis l'état projeté, bornée (profondeur 8, quelques milliers de
nœuds), déterministe (départage par identifiants triés). Le meilleur plan sous le coût total ;
aucun plan si rien n'aboutit dans la borne.

**Quand chercher** : aujourd'hui chaque PNJ replanifie à chaque minute, ce que permettent des
méthodes peu coûteuses. Une recherche le sera davantage : on ne replanifie qu'à un changement
de but, un geste manqué, ou un changement de croyance qui touche le plan ; sinon on suit le plan
en cours. Le temps de calcul est mesuré au banc.

## Étapes du jalon

1. **Le planificateur seul** (`donjon/planification.py`) : état projeté, actions déclarées,
   recherche. Tests sur des situations isolées, les mêmes que les méthodes actuelles (vivres
   sous clé, clé dans un contenant, porte verrouillée sur le chemin, part demandée, feu à
   ranimer avec une torche allumée au fanal).
2. **En parallèle, sans effet** : au banc, chaque minute, les deux calculent un plan pour le
   même but ; le récit liste les désaccords. On corrige jusqu'à ce que les différences restantes
   soient voulues ou défendables.
3. **Bascule de la faim et du froid** : le planificateur décide pour ces deux besoins. Critère A
   ci-dessous. Les tests existants des comportements doivent passer, ou leur changement être
   justifié un par un.
4. **Bascule du reste** (pulsions, garder, prévenir, complétion du stratège), puis retrait des
   méthodes remplacées.
5. **Critère B**, puis bilan dans `docs/plan-pnj.md`.

## Critères

**A. Ne rien perdre** (banc, 4 graines × 8 h, récit à l'appui) : autant d'événements distincts
ou plus, aucune violation ni usurpation, pas plus de minutes urgentes sans recours, temps de
calcul du banc au plus doublé.

**B. Retrouver et trouver** :
- retrouver sans méthode écrite les chaînes aujourd'hui codées à la main : la clé d'une porte
  sur le chemin, le crochetage, la part promise attendue près des vivres, la torche allumée au
  fanal pour rallumer le brasero ;
- en trouver qui ne sont écrites nulle part, avec les seules actions existantes. Deux visées :
  prendre de la lumière avant de crocheter dans le noir (la chance le justifie), et demander un
  outil porté par quelqu'un qu'on croit fiable.

**C. Moins de règles** : les méthodes retirées, en lignes ; ce qu'il a fallu ajouter pour
déclarer les actions.

## Risques

- **Comportements déplacés** : un plan « équivalent » mais différent change la suite de la
  nuit. L'étape 2 (en parallèle, sans effet) sert à le voir avant de basculer.
- **Temps de calcul** : borne de la recherche, cache par révision des croyances, replanifier
  moins souvent.
- **Chances mal estimées** : un PNJ qui demande toujours, ou jamais. Elles se lisent dans le
  récit et se règlent par des constantes du moteur, pas par personnage.
- **Tests liés aux méthodes** : certains vérifient un plan exact ; ils passent à l'état du
  monde et au comportement observé.

## Hors périmètre

L'influence (proposition jugée sur les buts, avis, confier un but), les relations graduées, la
crue, la fabrication par les PNJ, l'apprentissage de méthodes. Le planificateur les rend
possibles sans méthode nouvelle ; ils viennent aux jalons suivants.
