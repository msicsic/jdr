# Tâche Codex 33 (A2b) : les PNJ proposent

Branche `codex-pnj-proposent` (elle porte ce fichier, issue de l'intégration **ffcc295** : lots 27 à 30 et 29
fusionnés), worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »).
Pas de Luna sur ce poste (aucun changement du MJ dans ce lot).

Lis `AGENTS.md`, `docs/etat-dev.md` (lot 29 `codex-propositions` et sa fusion), le
`docs/taches/rapport-codex-29-propositions.md`, `docs/plan-relations.md` § 7.1, § 7.2 (premier point
seulement) et § 9 « 3e » (critère), puis `donjon/echanges.py` (`evaluer_proposition`, `proposer`,
`demander`), `donjon/propositions.py`, `donjon/agendas.py`, `donjon/relations.py` (`chance_demande`),
`donjon/planification.py` (gestes `demander`, `acheter`, `engager`, `_entrees`, `devis_pulsion`).

## L'invariant
Un PNJ peut **proposer** comme le joueur : même contenu, même évaluation par l'auditeur
(`echanges.evaluer_proposition`), mêmes engagements des deux côtés, même trahison. Dans le planificateur, un
geste `proposer` déclaré une fois, à côté de `demander` : il offre ce qu'il porte ou peut promettre (un objet,
une part, des pièces, une tâche qu'il peut faire selon son devis), et son coût est divisé par la **chance
estimée**, calculée sur ce qu'il croit de l'autre (`relations.chance_demande` et la valeur qu'il croit que
l'autre donne à la contrepartie), jamais sur l'attitude privée de l'autre. Ces lectures entrent dans
`_entrees` ; `planification.VERIFIER` le contrôle. Une promesse qu'il ne compte pas tenir se pèse comme une
faute (`caractere.prix_faute`) à l'abandon.

Hors de ce lot : convertir les demandes et ventes existantes en propositions (lot suivant, dis seulement ce
que la conversion changerait), `rendre_service`, intermédiaires, avis.

## Vérification (minimale)
- Tests après rechargement (`tests/test_pnj_proposent.py`), deux cas au moins : à la crue, Brune affamée,
  dont Gorm se méfie, propose de tenir le brasero contre une part (refusée par méfiance ; acceptée sans
  méfiance, puis tenue) ; à la mine, Odon affamé, que Mathe refuse, propose ses pièces ou une tâche ; le même
  cas avec Brune à honnêteté 90 et à 20 (à 20, la réserve crochetée reste moins chère quand Gorm s'éloigne).
  État, engagements et récit après rechargement.
- Banc rapide (`tools/comparer_bancs.py`, 4 h, 4 graines, quatre scénarios, contre ffcc295) : aucune
  usurpation, violation ni boucle nouvelle (`tools/audit_nuits.py`) ; mesures nouvelles `propositions`,
  `acceptees`, `contreparties_tenues`, `trahisons` ; vols et minutes sans recours, écarts expliqués.
- Temps : ffcc295 et la branche lancés ensemble, 4 h, graines 42 et 1985, mine et auberge (au plus +10 %).
- `VERIFIER` + `spatial.VERIFICATION` 1, 2 h, graine 42, crue et mine : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` § 7.2 (ce qui est fait), `docs/etat-dev.md`
(« Branche `codex-pnj-proposent`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-33-pnj-proposent.md` (invariant, fonctions, mesures, critère de 3e : où on en est).
