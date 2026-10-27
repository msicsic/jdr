# Tâche Codex 167 c (A4b, fin) : l'agenda protéger et les fins de garder

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (dis ce qui reste). Pas de Luna. **Poste : le PC fixe**
(`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (171,
audit narratif) et un sur le laptop (166, côté MJ) : au plus 2 processus de calcul, priorité réduite. Ce lot touche `agendas.py`,
`deliberation.py`, `planification.py`, `defense.py`, les données des scénarios (agendas de départ) et leurs tests ; **pas**
`mj.py`, `consignes.py`, `narration.py`, `sources.py`, les fournisseurs. **Bruts dans `C:\Users\msics\donjon\artifacts\garder-167c\`,
jamais dans le worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Déjà livré : le lot 167 b (l'agenda `garder` sur le plan commun, sans double comptage avec la pulsion, `deliberation.charges_gardees` ; interposition comme premier sous-but) et le lot 167 (s'interposer : le gardien rejoint le poste d'accès d'un bien gardé quand il voit approcher quelqu'un dont
il se méfie, met en garde par une parole typée, `garde_ignoree` si l'autre persiste). Lis son rapport, `docs/plan-agendas.md`
(§ 4 sortes `garder` et `protéger`, § 6, bilans 144 à 167), les rapports 144, 146 b et 146 e, puis `agendas.py`, la pulsion de
garde et `prix_gardes`, `protege` et l'appel à l'aide.

## Ce qu'il faut faire
Ce qui reste d'A4b, sans règle propre à un scénario ; transitions publiées à la sortie du choix (lot 146 b) :
- **protéger** (personne) : rester à portée de voix du protégé, répondre à son appel (existe), s'interposer pour lui (lot 167) ;
  fin à la mort ou au départ cru du protégé, cause retenue.
- **fins de `garder`** : rendu, perdu (cru), détruit, avec cause, sans renaissance ; une position inconnue ne prouve pas une perte.
- **interposition d'un lieu sans objet** (garder un lieu) si le contrat commun le permet ; sinon dis-le.
- Une épreuve en données de tests (par exemple Gorm protège Ilse dans la crue) ; aucun agenda historique nouveau sans le dire.

## Vérification
- Tests après rechargement : un gardien qui reste près de son bien et s'interpose, un protecteur qui suit son protégé à portée de
  voix et répond à son appel ; fin d'agenda avec cause ; pas de double comptage avec la pulsion ; même laps d'un bloc ou découpé.
- Empreintes 2 h, quatre scénarios × quatre graines : identiques hors scénario de l'épreuve, sinon écarts expliqués ; banc rapide
  4 h du scénario de l'épreuve × quatre graines (passages par heure, aucune usurpation ni boucle nouvelle) ; `VERIFIER` + spatial
  0,2, 2 h ; `tools/mesure_cout.py` sur ce scénario.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-garder-proteger-c` poussée (pas `main`).
`docs/plan-agendas.md` (A4 : fait et reste), `docs/etat-dev.md` (« Branche `codex-garder-proteger-c`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-167c-garder-proteger.md`.
