# Tâche Codex 144 (A4a) : les premiers agendas déclarés, informer et amener

Lot de 45 minutes au plus (`AGENTS.md`) ; **livraison partielle permise** : si le lot déborde, livre le socle d'activation et
une seule sorte, et dis précisément ce qui reste. Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste (MJ : `mj.py`, `paroles.py`,
`narration.py`, `consignes.py`) : au plus 2 processus de calcul, priorité réduite ; ne touche pas ces fichiers.
**Base voulue : la branche du lot 140 (`codex-captivite`, non fusionnée)**, qui touche aussi `deliberation.py`.
Ce lot touche `agendas.py`, `deliberation.py` (candidats, échelle), `planification.py` (sous-but passé à `chercher`), les
données de la crue (agendas de départ de Gorm) et leurs tests. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` en entier (§ 4 vocabulaire, § 5 modèle, § 6.1 à 6.4 choix, sous-but, sommeil, révision ;
§ 9 A4 ; § 10 décisions), `docs/etat-dev.md` (lots A0, A1, 120 à 125, 128), puis `donjon/agendas.py` (socle A1),
`deliberation._candidats` et `Urgence`/`Palier`, `planification.chercher`, `planification._endure`.

## Ce qu'il faut faire (A4 du plan, première partie)
- **Le socle d'activation** : les agendas de départ `profil["agendas"]` (déjà consultables depuis A1) deviennent des agendas de
  l'esprit, d'origine `scenario`, avec `etat` (`actif`, `sommeil`, `atteint`, `abandonne`), `depuis` et `raison`, sauvegardés.
  Au plus trois actifs. Accès seulement par `agendas.py` (le contrôle AST d'A1 reste vert).
- **Le choix** (§ 6.1) : un agenda actif propose un candidat sur l'échelle commune d'A0 ; il passe devant la routine et l'attente,
  derrière le désespoir, l'alarme et le péril de l'eau ; contre un besoin pressant non désespéré, l'urgence décide avec
  l'`INERTIE` commune. Poids calculé à chaque choix (valeurs, situation, relations), jamais stocké.
- **Le sous-but** (§ 6.2) : le premier sous-but de la sorte que le PNJ ne croit pas déjà vrai et dont le planificateur trouve un
  plan, passé comme condition à `chercher` ; l'agenda ne garde jamais de plan.
- **Le sommeil** (§ 6.3) par le coût (la règle de `_endure`), avec sa raison ; réveil sur croyance nouvelle. **Atteint, abandonné**
  (§ 6.4), cause retenue, pas de renaissance de la même cause sans croyance nouvelle. **Hystérésis entre agendas** selon la VOL.
- **Deux sortes** : `informer` (qui, fait ou avis ; sous-buts : être à portée de voix, le dire par la parole commune et les avis
  du lot 121) et `amener` (qui, lieu ; sous-buts : qu'il croie le lieu préférable par un avis, qu'il accepte une proposition du
  lot 3e, l'accompagner ; pas de contrainte : la manière `sans_violence` par défaut).
- **Épreuve en données** : dans la crue, Gorm reçoit l'agenda d'amener les autres à la galerie quand l'eau gagne et celui
  d'informer de la menace (données de scénario seulement, sans règle propre).

## Vérification
- Tests après rechargement : Gorm amène Ilse et Brune à la galerie, une puis l'autre, et s'arrête atteint ; un agenda qui ne
  trouve pas de plan dort avec sa raison et se réveille sur une croyance nouvelle ; la faim désespérée passe devant ; même laps
  d'un bloc ou découpé, même `data`.
- Empreintes 2 h, Relais/mine/auberge × quatre graines contre la base (cache) : identiques (aucun agenda de départ actif ailleurs).
  Banc rapide 4 h crue × quatre graines : PNJ à la galerie quand l'eau gagne, minutes en attente, dans l'eau, passages par heure,
  aucune usurpation ni boucle nouvelle ; `tools/mesure_cout.py` sur la crue pour le coût en recherches.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-agendas-a4a` poussée (pas `main`). `docs/plan-agendas.md`
(A4 : ce qui est fait et ce qui reste : `garder`/`protéger`, s'interposer, hystérésis dans le score), `docs/etat-dev.md`
(« Branche `codex-agendas-a4a`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-144-agendas-a4a.md`.
