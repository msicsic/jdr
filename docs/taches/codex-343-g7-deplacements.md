# Tâche Codex 343 : G7, les déplacements résolus rendus par le moteur

Lot G7 de la [feuille de route du MJ](../plan-refonte-mj.md). Lis `AGENTS.md`, `docs/etat-dev.md`, la section 9 de
`docs/conception-refonte-mj.md` (ligne G7), puis les rapports 171 (mesures résolues), 292 (G4, résultat public) et
328 (G6, repères).

## Constat
G4 affiche le résultat d'une exécution tel que le moteur le sauvegarde, sans récit ni audit. Ce résultat juxtapose
encore les pas un à un (« Tu avances d'un pas. Tu entends des pas à l'ouest. Tu avances d'un pas… ») : le cumul
qu'un lecteur en tire (« deux pas vers la sortie ») n'est écrit nulle part. Au lot 171, trois audits ont refusé à
tort un tel cumul fait par Luna (`force-4c-fuir` p1/p2) : la voie de narration libre n'a aucune source canonique du
total, de la direction ni de l'acteur.

## L'invariant
**Un déplacement exécuté a un rendu canonique écrit par le moteur, depuis les seuls mouvements réellement accomplis
pendant le geste : acteur, nombre de pas ou distance avec son unité, direction et intervalle de temps.** Concrètement :
- les pas successifs d'un même geste (marche, fuite, approche, traîner, passer un obstacle) sont regroupés en une
  phrase, qui dit le total accompli, la direction publique (repère G6 ou sortie connue) et, si l'arrêt précède la
  fin du plan, ce qui reste non exécuté ;
- un plan non exécuté (refus, interruption, fiche de faisabilité) ne produit aucune phrase de mouvement accompli ;
- les sons entendus pendant la marche restent des lignes distinctes, attribuées comme aujourd'hui, et ne se fondent
  pas dans le cumul ;
- le rendu est sauvegardé avant affichage et identique après recharge, en console, en TUI et dans le web ;
- la même fonction sert aux attestations exactes du lot 95 : une reprise mot pour mot du cumul par une voie encore
  auditée est prouvée sans audit.

Aucune exception pour un scénario, une salle ou une formulation. Les PNJ ne changent pas : le lot ne touche que le
rendu du joueur.

## Contraintes de conception
- Fichiers probables : `moteur.py` (résultat structuré des pas), `narration.py` / `rendu.py` (formulation),
  `localisation.py` (repères publics). Ne modifie ni `jeu.py` (le lot 325 y a une fusion en cours) ni `transactions.py`.
- Le regroupement lit un résultat structuré produit par le moteur, jamais le texte des lignes.
- Direction et lieux : seulement ce que Corvus perçoit ou connaît (repères publics, sorties connues), jamais une
  position cachée.

## Vérification
- Cas réel : `force-4c-fuir` (deux pas vers la sortie, sons à l'ouest). Autre cas de même nature : une marche au clic
  interrompue par une personne qui entre dans le champ, et un traîner. Cas négatifs : refus avant le premier pas,
  question de faisabilité, plan de trois pas arrêté au deuxième. Monde, texte, scène et carte contrôlés après
  rechargement.
- Tests ciblés des fichiers touchés et des voies de résultat (G4, U-D, U-T) ; pas de suite complète.
- Empreintes 2 h, Relais et un autre scénario, quatre graines, références lues du cache : le comportement des PNJ ne
  doit pas changer.
- Luna, **une passe** : `force-4c-fuir` et un autre script qui déplace le joueur. Mesure : zéro second récit ni audit
  du total ; compare aux références relues du cache.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Calcul long détaché, avec un fichier de fin écrit en
dernier. Signale tout fichier commun avec les lots en cours (325 U-C, 338 recours, 341 mandat du joueur, 342
attribution du groupe 1).

## Livraison
- Branche `codex-g7-deplacements`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-343-g7-deplacements.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g7-343\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
