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
et arrête la marche. Le rejeu ne montre pas la lumière ; ses croyances sont celles de lieu. Le
rejeu se fait une nuit à la fois (pas avec `--graines`).

## Hors périmètre

Des graphismes élaborés (sprites, animations) ; le jeu à plusieurs ; l'accès depuis une autre
machine.
