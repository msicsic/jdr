# Tâche : fondre l'ancien son dans l'ouïe commune

Tâche autonome, pensée pour une session cloud. Aucun appel à Luna ni à un modèle n'est possible ni
nécessaire : tout se vérifie par les tests et le banc sans joueur.

## Avant de commencer

- Lis `AGENTS.md`, `CLAUDE.md`, `docs/etat-dev.md`, `docs/plan-ouie.md` (l'ouïe commune, les voix,
  « Nommer, attendre, héler », « Les voix inconnues ») et `docs/plan-planificateur.md`. Leurs règles
  s'imposent : corriger l'invariant général, jamais le cas de l'exemple ; vérifier le cas réel et un
  autre cas de même nature après rechargement ; `ErreurMonde` avec `attendu`, une cause par refus ;
  aucun état hors de `data` (`tests/test_temps_etat.py`) ; `planification.VERIFIER` ; dire les
  limites. Les anciennes sauvegardes n'ont pas à être conservées : aucune migration.
- Environnement Linux : `CLAUDE.md` décrit le poste Windows. Ici : `git fetch origin`, puis
  `python -m venv .venv && . .venv/bin/activate`, installe `requirements-tui.txt` et
  `requirements-chatgpt.txt` (et `pyflakes`). Tests : `python -m unittest discover -s tests -q`
  (ceux du clic demandent Node ; s'il manque, dis-le ; 14 tests sautent sans `jsonschema`, c'est
  normal).
- Crée la branche `ouie-commune` depuis `origin/main` (pas depuis une ancienne branche de cette
  session), commite dessus et pousse-la (`git push -u origin ouie-commune`). Ne touche jamais à
  `main`, ne fusionne rien.
- Les tests de scène construisent le monde avec `depart="fixe"` ; le banc tire le départ par défaut.

## Le problème

Deux systèmes de son coexistent.

- **L'ouïe commune** (`donjon/ouie.py`) : pas, gestes, voix, héler. Distance réelle en cases,
  atténuation par passages et portes, seuil de chacun (aux aguets, au repos, PER), interprétation
  (attribuer, se retourner, retenir un bruit vers un lieu, aller voir selon le devoir de garde et
  le courage).
- **L'ancien système** (`donjon/sons.py`, `appliquer`) : appel à l'aide, cri, sifflement du joueur
  et son d'un objet (la cloche). Portée calculée salle par salle (`portee`, `auditeurs`), sans les
  cases ni la règle commune ; chaque PNJ qui entend passe « inquiet » ou « méfiant » d'office
  (`humeur`) ; `esprits.entendre` range un souvenir de type `son` à part, puis `pnj.reagir`
  applique un réflexe déclaré par le scénario (`reaction_son` : au-delà d'un seuil, aller voir) ou
  fait accourir le protecteur d'un protégé.

Un même cri n'est donc pas entendu de la même façon selon qu'il vient du joueur ou d'un PNJ ; la
cloche ignore les portes comme l'ouïe commune les compte ; le réflexe déclaré court-circuite le
courage et le devoir qui décident ailleurs d'aller voir.

## Ce qu'il faut faire

1. Les sons du joueur et des objets retentissent par l'ouïe commune (`ouie.retentir`), leurs natures
   déclarées une fois (`ouie.NATURES` / `INTENSITES` : appel à l'aide, cri, sifflement, son d'un
   objet selon sa `sonorite`). Plus de portée salle par salle.
2. Le réflexe déclaré (`reaction_son`) devient une donnée de l'ouïe commune (par exemple un seuil
   d'alerte propre, plus bas pour un gardien) ; la décision d'aller voir passe par le même but que
   le reste (`deliberation`, devoir de garde, courage). La protection (le protecteur accourt à
   l'appel de son protégé) est gardée, par la même voie. Migre les données des scénarios.
3. Plus d'humeur forcée : l'inquiétude vient de l'ouïe commune, à la mesure de ce qui est entendu
   (`deliberation.inquieter`).
4. Un seul souvenir de ce qui est entendu : le souvenir `son` à part disparaît au profit de celui de
   l'ouïe commune ; adapte ses lecteurs (`esprits.dernier_son`, ce que reçoit le MJ, le stratège).
5. Celui qu'on hèle se tourne vers la voix (le temps de la rotation, `pnj` / `ouie`), et peut ainsi
   voir l'appelant ; les retrouvailles après un appel en profitent.
6. La réponse au cri du joueur (héler, appel) se décide à la fin de ses 3 secondes de cri, après que
   les PNJ ont vécu ces secondes (aujourd'hui elle est calculée avant).

## Vérifications

- Pour chaque point, un test qui vérifie l'état après rechargement, sur le cas réel et un autre cas
  de même nature : l'appel à l'aide du joueur derrière une porte fermée (proche, puis loin) ; la
  cloche du Relais ; un protégé qui crie ; un gardien au seuil d'alerte bas ; l'appelé qui se tourne
  et voit l'appelant ; la réponse au joueur après ses 3 secondes. « Même laps découpé = même
  monde ».
- Suite complète verte ; `planification.VERIFIER` sur une nuit de chaque scénario.
- Bancs 8 h, `main` puis la branche :
  `python -m donjon.banc_pnj --heures 8 --graines 1985 7 42 2024 3 11 99 500 --joueur chambre_cloche`,
  puis `--scenario mine --joueur galerie`, `--scenario auberge --joueur dortoir`,
  `--scenario crue --joueur chambre_cloche` (4 graines). Rapporte avant → après : appels, réponses,
  retrouvailles, allés voir, bruits inconnus, retournements, inquiétudes, vols vus, minutes sans
  recours et en attente, usurpations et violations (aucune tolérée), temps d'une nuit. Explique les
  écarts.
- Docs : `docs/plan-ouie.md` (section dédiée ; retire la limite « les réflexes déclarés gardent
  l'ancienne portée ») et `docs/etat-dev.md` (« Branche `ouie-commune`, non fusionnée », compte de
  tests, et la ligne des décisions en attente qui parle de fondre les réflexes).

## Rapport final

En français, concis : causes, règles changées (fonctions), données migrées, cas vérifiés, bancs avant
→ après, limites, nom de la branche poussée et dernier commit. La session qui t'a confié la tâche
ne peut pas lire ta réponse : écris le rapport dans le fichier `docs/taches/rapport-ouie-commune.md`
de ta branche, en plus de ta réponse ici.
