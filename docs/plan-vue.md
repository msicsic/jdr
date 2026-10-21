# Plan : jouer dans le navigateur, avec une carte fidèle

Proposition de jalon, à valider. La carte du terminal, deux caractères par case, perd ce que le
moteur sait : un symbole par type d'objet (le même `!` pour deux plaques différentes), une seule
chose par case, des lettres à relier par la légende, pas de place pour le regard des PNJ. Le
joueur a la vue la plus pauvre de la scène : le moteur et Luna travaillent sur l'information
complète (`Monde.contexte()` : identifiants, positions relatives, portée, souvenirs). Le jalon
donne au joueur une page de jeu complète (saisie, récit, carte fidèle) et, ensuite, un rejeu du
banc pour étudier les PNJ.

## Principes

- **Le moteur reste la seule autorité.** La page affiche ce qu'on lui envoie et envoie des
  commandes : les mêmes que la saisie du terminal (`pas est`, `prendre torche`, texte libre pour
  Luna). Elle ne modifie jamais l'état.
- **Une seule source pour ce que perçoit le joueur.** La scène dessinée vient des mêmes calculs
  que le contexte de Luna et que la carte du terminal : ce que le joueur voit maintenant, ce dont
  il se souvient. Rien de ce qu'il ne perçoit pas n'est envoyé à la page.
- **Fidèle au modèle**, pas plus fin que lui : des cases de 1 m, des instants au dixième de
  seconde ; un personnage est sur une case, pas entre deux.
- **Le terminal reste** (`--tui`, `--console`) : la page est une interface de plus.

## Architecture

```
 jeu.main (boucle de jeu, Luna, sauvegardes)
    │ interface : ecrire, lire, rafraichir, montrer      (comme PontTerminal)
    ▼
 PontWeb ──▶ serveur local (127.0.0.1) ──flux──▶ page : récit, carte, fiche
    ▲                                              │
    └──────────── commande ◀───────────────────────┘
```

- **`jeu.py --web`** lance la partie avec un `PontWeb` (même interface que `PontTerminal`) et un
  serveur local, puis ouvre la page. Python seul, bibliothèque standard : un serveur HTTP, un flux
  d'événements poussés (Server-Sent Events) pour le récit et l'état, une requête POST pour une
  commande. Une commande à la fois ; pendant le travail du MJ, la page indique « en cours ».
- **Écoute sur 127.0.0.1 uniquement** : rien n'est exposé au réseau ; aucune clé n'est envoyée à
  la page.
- **La page** : HTML, CSS et JavaScript sans compilation ni dépendance, dessin sur un canevas 2D.
  Panneau de récit (journal, comme le terminal), saisie avec historique, carte, fiche du
  personnage, aide. Raccourcis : flèches pour marcher, Maj pour le pas chassé, Alt pour le pas
  feutré, et l'équivalent des touches F du terminal.

## La scène perçue (`donjon/scene.py`)

Une structure JSON, produite après chaque action :
- **les salles connues** : géométrie dans le repère commun, cases vues (éclairées, pénombre),
  mémorisées, murs repérés, escaliers ;
- **les portes connues** et leur état tel que le joueur le sait ;
- **les objets perçus** un par un : identifiant, nom, type, case, ancrage au mur, état visible ;
  plusieurs sur une case forment une pile ; ce qu'un personnage porte ou ce qu'un contenant ouvert
  renferme est rattaché à lui ; **les souvenirs** d'objets, marqués comme tels ;
- **les personnages perçus** : identifiant, nom, couleur stable, case, orientation, état ;
- **le joueur** : case, orientation, cône ; **la lumière** des cases vues ; **les sorties connues**.

La carte du terminal devient un rendu de cette scène : le même calcul, deux projections.

**La vérité, pour le banc** : la même structure sans filtre, avec en plus, par PNJ, son intention,
son besoin pressant et ses croyances utiles (où il croit les autres), pour « voir par ses yeux ».

## Étapes

1. **La scène perçue**, testée : elle ne contient que ce que perçoit le joueur (rien de ce qui
   est hors de son champ, hors souvenirs) ; la carte du terminal en est tirée sans changer ce
   qu'elle affiche.
2. **Le client de jeu** : serveur, `PontWeb`, page avec récit, saisie, carte dessinée, fiche.
   Une partie du Relais se joue de bout en bout dans le navigateur, avec Luna, et se recharge.
3. **La carte riche** : icônes par objet et piles, couleurs et étiquettes des personnages, leur
   regard, ton cône, la lumière en dégradé, la fiche d'une case au survol.
4. **Le rejeu du banc** : le banc enregistre chaque événement (positions, orientations,
   intentions) ; une page rejoue la nuit avec une barre de temps ; un clic sur un PNJ montre son
   but, et la vue par ses yeux (son cône, ce qu'il croit).
5. **Agir par clic** : un clic sur une case pour y aller, sur un objet ou un personnage pour un
   geste (examiner, prendre, parler), qui devient la commande correspondante.

## Critères

- Une partie jouée dans la page produit le même récit et le même état qu'au terminal.
- La scène envoyée à la page ne contient rien que le joueur ne perçoive (test sur une scène où
  des objets et des PNJ sont hors de son champ, dans son dos, dans le noir).
- Le rejeu montre, à chaque instant, les positions et orientations enregistrées.

## Bilan

Les cinq étapes sont faites.
- La scène perçue (`donjon/scene.py`) : la carte du terminal en est tirée, comparée sans écart
  à l'ancien rendu ; la page en reçoit le JSON. Chaque case vue porte son degré de lumière
  (pleine, lueur directe, diffuse, noir), sans rien interpoler ; ce qu'un objet bloque ou s'il se
  déplace n'y figure que pour ce que le joueur voit ou a vu.
- Le client : `jeu.py --web [--port]`, serveur local (`donjon/web/serveur.py`), `PontWeb` au même
  contrat que le terminal ; essai réel avec Luna joué de bout en bout et rechargé.
- La carte riche : icônes et piles, couleurs, noms, regards, ce que tient un personnage ; ton
  cône sur les cases que tu vois ; ceux des autres par la règle du moteur, sur les cases connues,
  sans les obstacles (case à cocher) ; fiche de chaque case au survol.
- Le rejeu : `donjon/rejeu.py` observe la nuit sans la changer (même empreinte) ; pistes de
  changements (positions, regards, portes, flammes ; cases vues par chaque PNJ ; but, besoins,
  croyances de lieu) ; ~260 Ko pour 8 h ; page autonome `web/rejeu.html`.
- Agir par clic : marche pas à pas par les commandes « pas » (chemin le plus court sur le sol
  connu, seuils franchis droit comme `spatial.pas_vers`), arrêt si un pas échoue ou si quelqu'un
  entre dans le champ ; menu de gestes devenus commandes ; un geste de contact approche d'abord.
  Test : chaque geste proposé sur une vraie scène est compris et à portée (script de la page sous
  Node).

Limites : le chemin du clic ne connaît que le sol vu ; un obstacle jamais vu fait échouer le pas
et arrête la marche. Les croyances du rejeu sont celles de lieu.

## Rejeu enrichi (branche `rejeu-enrichi`)

Observation seule (`rejeu.py` enveloppe `ouie.retentir`, `ouie.entendre`, `pnj.commencer_geste`,
`pnj._temoins`, `social.retenir_parole` le temps de la nuit ; `tests/test_rejeu.py` vérifie
l'empreinte).
- Lumière : piste `lumiere`, le degré de chaque case (0 noire, 1 diffuse, 2 directe, 3 pleine),
  recalculé quand `spatial.signature_vue` change ; le test la compare à un calcul de zéro, au Relais,
  à l'auberge et à la mine.
- Bruits : liste `bruits` (instant, auteur, nature, case, mots, et pour chaque PNJ qui l'a entendu
  son niveau et ce qu'il en a fait : `vu`, `attribue`, `tourne`, `bruit`, `parole`, combinables) ;
  onde d'une minute sur la carte, panneau « Ce qu'il entend » du personnage choisi (cinq dernières
  minutes, bruits attendus, gestes vus ou commis). Le nombre de retournements enregistrés égale celui
  de la chronique. Limite : un bruit sous le seuil d'un PNJ n'apparaît pas dans ses réactions (le moteur
  n'appelle pas `entendre`).
- Gestes illicites : liste `gestes` (qui, quoi, où, jusqu'à quand, qui était dans la salle, qui
  voyait l'auteur au départ, témoins datés) ; journal filtrable par personnage et par nature.
- Plusieurs nuits : `--rejeu page.html --graines 1985 7` écrit `page_1985.html` et `page_7.html` (un
  dossier donne `rejeu_<graine>.html`), en parallèle. Taille : 420 à 450 Ko pour 8 h au Relais.

Constats au Relais, moteur actuel (`--joueur chambre_cloche`, 8 h) :
- Graine 1985 : aucun geste illicite. Brune obtient sa part de Gorm (« promis ») à la minute 5 et à la
  403 ; personne ne vole, ni n'est méfiant. 8 échanges : 6 parts demandées à Gorm (Brune
  promise deux fois, Ilse refusée deux fois, Aubin refusé puis « nécessaire » à la 473) et 2 dons de Gorm à Brune.
- Graine 7 : Gorm refuse Brune à la minute 5. Elle prend la trousse de crochets (min 6) et guette la
  réserve de l'antichambre de la min 6 à la 36 : Ilse est à côté, Brune lui tourne le dos (« voit » vide
  hors tour d'horizon) ; elle attend, puis son but s'arrête (un renoncement, d'après le compte du banc,
  sans que le rejeu note l'instant ni le tour d'horizon lui-même). Même scène
  de la min 97 à la 127, avec Ilse et Aubin en vue 25 min sur 31. Sa faim atteint 95 (`DESESPOIR`) à 1 h 59 :
  la précaution est levée et elle force la serrure à 2 h 02. Ce geste est bruyant même « sans témoin »
  (`ouie.NATURES`) : le fracas arrive à Ilse au niveau 6, elle (de dos, face au nord) se retourne et
  voit ; Gorm arrive à 2 h 04 m 15 s. Brune s'acharne jusqu'à 2 h 08, devant eux.
- Le chiffre « vols vus » (12) compte un souvenir `vu_agir` par geste d'une minute et par témoin
  (7 gestes, 1 + 1 + 2 + 2 + 2 + 2 + 2) : une seule effraction vue par deux personnes. Les trois
  méfiances et la confidence (Ilse à Aubin, min 258) viennent d'elle, et la rumeur crue.
- Échanges : 8 par nuit sur les deux graines, presque tous de la même sorte (une part demandée à Gorm quand
  la faim atteint ~70 à 80 : 6 demandes dans chaque graine ; en 1985 deux dons de Gorm, en 7 un don et
  la rumeur d'Ilse). Gorm tient l'antichambre (« garder ses biens ») et
  tout le monde y vient ; le rythme est celui de la faim, pas de la perception : cela explique que la
  vue et l'ouïe changent peu leur nombre. Ce qui varie, c'est l'issue du jet de la min 5 (promis ou
  refus), qui décide d'un vol ou non plus tard.
- Hypothèse non vérifiée : « chacune seule multipliait échanges et vols vus » (jalon `integration`)
  tient à la vue d'un témoin pendant un geste d'une minute (comptée à chaque geste) et à la précaution
  « sans témoin » qui ne regarde que ce que le voleur voit ; le rejeu ne rejoue pas les anciennes
  branches, et je n'ai pas mesuré cela.

## Hors périmètre

Des graphismes élaborés (sprites, animations) ; le jeu à plusieurs ; l'accès depuis une autre
machine.
