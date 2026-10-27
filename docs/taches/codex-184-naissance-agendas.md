# Tâche Codex 184 (A6, premier volet) : la table des naissances, et un projet né d'une situation

Priorité de l'utilisateur, 2026-10-27 : la **richesse du comportement des PNJ**. Le diagnostic 183
(`docs/taches/rapport-codex-183-mecanismes-dormants.md`) montre que les PNJ réagissent à leurs besoins mais ne se donnent pas de
projets : A6 manque. Lot de 30 à 45 minutes (`AGENTS.md`) ; livraison partielle permise si elle dit ce qui reste. Pas de Luna.
**Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur
ce poste (185 : `eau.py` et la prévision dans `esprits.py`) : au plus 2 processus de calcul, priorité réduite. Ce lot touche
`agendas.py`, `deliberation.py`, une table de naissances en données (module dédié ou `agendas.py`) et leurs tests ; **pas**
`eau.py` ni les fonctions de prévision d'eau (lot 185), ni `narration.py`, `mj.py`, `consignes.py` (lot 180 en attente de fusion).
**Bruts dans `C:\Users\msics\donjon\artifacts\naissance-184\`, jamais dans le worktree.** Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` (§ 3 table des cas, § 6.1 à 6.5, § 9 A6, § 10 décisions, § 11 « ce qui serait un script »),
les rapports 144, 146 à 146 e, 167 à 167 c, 175, 179, 181 et 183, puis `agendas.py` (activation, sommeil, réveil, fins, trois
actifs au plus, publication à la sortie du choix) et les dettes (`biens.py`, `caractere.valeur_piece`).

## L'invariant
**Un agenda peut naître pendant la nuit, et non seulement des données de départ, par une table commune de naissances qui dit
seulement quelle sorte naît de quelle cause et quelles valeurs en font le poids (plan § 6.5), jamais une personne ni un scénario ;
la naissance passe par la voie commune d'`agendas.py` (registre, trois actifs au plus, sommeil/réveil, fin, publication à la
sortie du choix, sauvegarde), d'après les seules croyances du PNJ.** Premier volet : la table, et **une naissance par situation**,
la dette crue (le PNJ se sait débiteur et sans les pièces) qui fait naître un projet « obtenir des pièces » dont les sous-buts sont
les moyens déjà communs (travail payé, vente, emprunt, et, selon l'honnêteté, le vol au prix de la faute), sans geste nouveau.
Si la sorte d'agenda manque, ajoute-la au vocabulaire commun (plan § 4) plutôt qu'un cas propre.

## Hors lot (à dire dans le rapport)
Occasion (mercenaire), événement (vengeance, punir, rallier) et soupçon déduit : volets suivants.

## Vérification
- Tests après rechargement : Odon (mine) endetté fait naître le projet et agit par un moyen commun ; un autre débiteur (autre
  scénario ou données de tests) ; un PNJ sans dette ou qui croit avoir les pièces : aucune naissance ; une dette soldée termine le
  projet ; registre plein ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, mine et auberge × quatre graines, branche contre les références du cache : aucune usurpation, plantage ni
  boucle nouvelle ; mesure de richesse du lot 183 (`dormants-183/richesse.json`, mêmes définitions) relevée avant/après si l'outil
  le permet sans le modifier, sinon décrite à la main ; coût (`tools/mesure_cout.py` sur la mine) relevé.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-naissance-agendas` poussée (pas `main`).
`docs/plan-agendas.md` (A6 : fait et reste), `docs/etat-dev.md` (« Branche `codex-naissance-agendas`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-184-naissance-agendas.md`.
