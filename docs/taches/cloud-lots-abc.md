# Tâche cloud : trois lots en parallèle (chef d'orchestre)

Tâche pour une session cloud qui pilote **trois sous-agents**, un par lot, chacun sur sa branche.
Aucun appel à Luna ni à un modèle de jeu n'est possible ni nécessaire : tout se vérifie par les
tests, le banc sans joueur et `tools/audit_nuits.py`.

## Toi, le chef d'orchestre

1. `git fetch origin`. Prépare l'environnement Linux une fois (voir « Environnement ») et vérifie
   que la suite passe sur `origin/main`.
2. Crée un worktree par lot depuis `origin/main` (`git worktree add ../lot-a -b temps-reel origin/main`,
   `../lot-b -b relations-socle`, `../lot-c -b crochetage-surenchere`) et lance **un sous-agent par
   lot** (outil Agent, modèle Opus) avec, comme consigne, la section « Commun à tous les lots » plus
   la section de son lot, et le chemin de son worktree. Ils travaillent en parallèle.
3. **Charge** : les trois partagent cette machine. Dis à chacun de lancer ses bancs avec
   `--processus` au plus égal au tiers des cœurs (`nproc`), et de jouer `main` puis sa branche l'un
   après l'autre.
4. Quand un sous-agent a fini : vérifie sa suite, puis **pousse sa branche**
   (`git push -u origin <branche>`). Ne fusionne rien dans `main`, ne touche jamais à `main`.
5. À la fin, écris le rapport des trois lots dans `docs/taches/rapport-cloud-lots-abc.md` sur une
   branche `rapport-cloud-lots-abc` que tu pousses aussi (la session qui t'a confié la tâche ne lit
   que les branches poussées).

## Environnement

`CLAUDE.md` décrit le poste Windows. Ici : `python -m venv .venv && . .venv/bin/activate`, installe
`requirements-tui.txt` et `requirements-chatgpt.txt`, puis `pip install pyflakes`. Tests :
`python -m unittest discover -s tests -q` (14 tests sautent sans `jsonschema`, c'est normal ; ceux du
clic demandent Node, dis-le s'il manque). Les tests de scène construisent le monde avec
`depart="fixe"` ; le banc tire le départ par défaut.

## Commun à tous les lots (à donner à chaque sous-agent)

- Lis `AGENTS.md`, `CLAUDE.md`, `docs/etat-dev.md` (dont « Décisions prises le 2026-10-22 »),
  `docs/plan-planificateur.md`, `docs/plan-temps.md` (« Correctif : délibérer à l'événement » et
  son inventaire de ce qui reste à la minute), `docs/audit-nuits.md`. Leurs règles s'imposent :
  corriger l'invariant général, jamais le cas de l'exemple ; vérifier le cas réel et un autre cas de
  même nature après rechargement ; `ErreurMonde` avec `attendu`, une cause par refus ; aucun état
  hors de `data` (`tests/test_temps_etat.py` : même laps découpé = même monde) ;
  `planification.VERIFIER` (toute lecture nouvelle de la recherche entre dans `_entrees` ; `gestes`
  ne lit ni le prix d'une faute ni celui d'abîmer) ; dire les limites ; aucune migration de
  sauvegardes.
- Travaille dans ton worktree, sur ta branche ; commite dessus ; ne pousse pas (le chef d'orchestre
  pousse), ne touche jamais à `main`.
- Vérifications communes : suite complète verte ; `VERIFIER` sur une nuit de chaque scénario ;
  bancs 8 h `main` puis branche (Relais `--graines 1985 7 42 2024 3 11 99 500 --joueur
  chambre_cloche`, mine `--joueur galerie`, auberge `--joueur dortoir`, crue `--joueur
  chambre_cloche`, 4 graines) : usurpations et violations (aucune tolérée), minutes sans recours et
  en attente, événements, échanges, vols vus, temps d'une nuit ; `tools/audit_nuits.py analyser` sur
  4 scénarios × 4 graines × 12 h, avant/après. Docs à jour (`docs/etat-dev.md` : « Branche `<la
  tienne>`, non fusionnée », compte de tests).
- Rapport final : causes, règles changées (fonctions), cas vérifiés, mesures avant → après,
  limites, dernier commit.

## Lot A — `temps-reel` : ce qui reste à la minute

Depuis `deliberation-evenements`, les PNJ délibèrent à l'événement, mais le reste tourne encore à
l'instant pile de chaque minute (`pnj._avancer`, frontière de minute ; inventaire dans
`docs/plan-temps.md`). Traite, dans l'ordre, en gardant le filet de délibération à la minute (décision
de l'utilisateur : ne pas programmer les franchissements de seuil comme événements) :
1. **Les horloges du scénario à leur instant** : `horloges.declencher` n'est appelé qu'à la fin d'une
   action du joueur (`moteur.py`), si bien qu'un geste long retarde l'événement (la rafale qui
   éteint l'âtre) et que les PNJ vivent comme s'il n'avait pas eu lieu. Elles doivent se déclencher
   pendant la simulation des PNJ, à leur instant.
2. **Corps, besoins et sécurité ressentie au temps réellement vécu** : aujourd'hui échantillonnés à
   l'instant de la frontière (`deliberation.deliberer`, `corps.vivre`, `ressentir`) : un PNJ qui
   traverse un couloir noir entre deux minutes n'a pas peur, un autre qui y est une seconde à la
   frontière subit une minute entière ; l'effort ou le repos sont lus du geste en cours au lieu des
   gestes faits. Fais évoluer corps et besoins selon le temps passé dans chaque état (lieu, lumière,
   eau, feu, effort), par exemple en accumulant à chaque geste ce qu'il a vécu ; même chose pour le
   corps du joueur, qui ne change qu'au franchissement d'une minute.
3. **Le froid sec à 4 par heure** (décision du 2026-10-22, aujourd'hui 2).
4. **La patience et le répit en temps** (aujourd'hui `PATIENCE` compte des appels, pas des minutes).
5. Si le temps le permet : combustion et crue à l'instant où le seuil est atteint plutôt qu'à la
   frontière. Sinon, note-le.
Vérifie en particulier « même laps découpé = même monde » et le coût de calcul.

## Lot B — `relations-socle` : sous-étape 3a du plan relations

Lis `docs/plan-relations.md` (en entier, et la section « 3a. Le socle, sans changer le
comportement ») et les décisions du 2026-10-22 dans `docs/etat-dev.md`. Fais **uniquement 3a** : un
module `donjon/relations.py` devient le seul accès à ce qu'un personnage éprouve envers un autre
(aujourd'hui la croyance `fiable`, lue et écrite à une vingtaine d'endroits : jet de persuasion,
refus, confidences, ouïe, appel, passage, sécurité, abri, délégation, humeur, `voix.fiabilite`).
**Aucun changement de comportement** : les empreintes des nuits (chronique, mesures, état final)
doivent rester identiques à `main` sur les 4 scénarios × 4 graines, en départ tiré et fixe. Prépare
l'interface des cinq axes décidés (confiance, affection, rancune, peur, dette) sans encore les faire
vivre. Tous les lecteurs et écrivains de `fiable` passent par le module.

## Lot C — `crochetage-surenchere` : deux réglages décidés

1. **Le bruit du crochetage selon l'adresse** : aujourd'hui `crocheter` est toujours un geste
   bruyant (`ouie.NATURES`). Décision : un crochetage réussi par quelqu'un d'habile (DEX, outil,
   lumière) fait peu de bruit ; un échec, un acharnement ou un forcement font du fracas. Règle
   commune au joueur et aux PNJ ; que le planificateur et le voleur qui veut agir sans être entendu
   (`pnj.oreilles_crues`) en tiennent compte.
2. **La surenchère progressive** : aujourd'hui, après un refus « cher », le payeur repropose au moins
   le double (`planification.SURENCHERE` = 2, branche `refus-retenus`). Décision : hausse par paliers
   (+50 %) tant que l'offre vaut la peine pour lui (`caractere.valeur_pieces`), puis il renonce ;
   pas d'offre par minute en rafale (une hausse à la fois, au plus une par délibération).
Mesure en plus : crochetages (essais, réussites, entendus), témoins par l'ouïe, offres et hausses,
pièces payées.
