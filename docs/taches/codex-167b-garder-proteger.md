# Tâche Codex 167 b (A4b) : les sortes d'agenda garder et protéger

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (dis ce qui reste). Pas de Luna. **Poste : le PC fixe**
(`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (169,
audit narratif) et un sur le laptop (166, côté MJ) : au plus 2 processus de calcul, priorité réduite. Ce lot touche `agendas.py`,
`deliberation.py`, `planification.py`, `defense.py`, les données des scénarios (agendas de départ) et leurs tests ; **pas**
`mj.py`, `consignes.py`, `narration.py`, `sources.py`, les fournisseurs. **Bruts dans `C:\Users\msics\donjon\artifacts\garder-167b\`,
jamais dans le worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Déjà livré : le lot 167 (s'interposer : le gardien rejoint le poste d'accès d'un bien gardé quand il voit approcher quelqu'un dont
il se méfie, met en garde par une parole typée, `garde_ignoree` si l'autre persiste). Lis son rapport, `docs/plan-agendas.md`
(§ 4 sortes `garder` et `protéger`, § 6, bilans 144 à 167), les rapports 144, 146 b et 146 e, puis `agendas.py`, la pulsion de
garde et `prix_gardes`, `protege` et l'appel à l'aide.

## Ce qu'il faut faire
Les sortes `garder` (chose ou lieu) et `protéger` (personne) sur le socle des agendas, sans règle propre à un scénario ;
transitions publiées à la sortie du choix (lot 146 b) :
- **garder** reprend ce que font déjà la pulsion de garde et `prix_gardes`, **sans double comptage**, et s'appuie sur
  l'interposition du lot 167 ; fin quand la chose n'est plus à garder (rendue, perdue, détruite, cause retenue).
- **protéger** : rester à portée de voix du protégé, répondre à son appel (existe), s'interposer pour lui (lot 167) ; fin à la
  mort ou au départ du protégé, cause retenue.
- Une épreuve en données (par exemple Gorm protège Ilse dans la crue, ou Anselme garde son ballot à l'auberge) ; si elle change les
  nuits historiques, écarts mesurés et expliqués.

## Vérification
- Tests après rechargement : un gardien qui reste près de son bien et s'interpose, un protecteur qui suit son protégé à portée de
  voix et répond à son appel ; fin d'agenda avec cause ; pas de double comptage avec la pulsion ; même laps d'un bloc ou découpé.
- Empreintes 2 h, quatre scénarios × quatre graines : identiques hors scénario de l'épreuve, sinon écarts expliqués ; banc rapide
  4 h du scénario de l'épreuve × quatre graines (passages par heure, aucune usurpation ni boucle nouvelle) ; `VERIFIER` + spatial
  0,2, 2 h ; `tools/mesure_cout.py` sur ce scénario.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-garder-proteger-b` poussée (pas `main`).
`docs/plan-agendas.md` (A4 : fait et reste), `docs/etat-dev.md` (« Branche `codex-garder-proteger-b`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-167b-garder-proteger.md`.
