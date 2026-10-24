# Tâche Codex 29 (A2a) : une proposition, évaluée par celui à qui on la fait

Branche `codex-propositions` (elle porte ce fichier, issue de l'intégration **19b0261** : Q, R, A0, A1,
lots 25 à 27), worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des
lots ») : un invariant, vérification minimale, rapport d'une page.

Lis `AGENTS.md`, `docs/etat-dev.md` (« Décisions en attente », agendas), `docs/plan-relations.md` § 7.1
et § 9 « 3e » (contexte seulement : ce lot n'en fait qu'une partie), `docs/plan-agendas.md` (A2), puis
`donjon/echanges.py` (`demander`, `engager`, `differee`, `remettre`), `donjon/agendas.py` (les engagements
y sont portés depuis A1 : seul accès), `donjon/relations.py` (`EPREUVES`, `chance_demande`, `percue`),
`donjon/paroles.py` (`TYPES`, `jet_persuasion`, contenus `reclamer` et `ressource` comme modèles),
`donjon/caractere.py` (`valeur_piece`, `prix_faute`), `donjon/biens.py` (prix propre).

**Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt principal ; copies seulement).

Un autre lot tourne en même temps sur l'autre poste (28, coût des trajets : `planification.py`,
`obstacles.py`, `part_estimee.py`, `pnj._marcher`, `Vue.pression`). **Ne touche ni `planification.py`, ni
`deliberation.py`, ni `obstacles.py`, ni `part_estimee.py`.**

## L'invariant
Une **proposition** — ce que je demande, et ce que tu y gagnes — est évaluée par l'auditeur sur **ses
croyances**, par une seule fonction quel que soit le proposant (§ 7.1) : P, ce qu'il perd (prix propre ;
refus d'office si `necessaire` ou `garde`) ; G, ce qu'il gagne (prix propre de la contrepartie, × confiance
/ 100 si elle est différée, × 1 si elle est donnée d'abord ; un but à lui que la demande sert) ; L, le lien
(altruisme, affection, dette × loyauté, − rancune) ; puis le jet de persuasion existant, avec le DD relevé
d'un mauvais marché selon l'INT de l'auditeur. Acceptée, chaque contrepartie différée devient un
engagement (par `agendas`) du côté de qui la doit ; tenue : `engagement_tenu` ; abandonnée :
`engagement_abandonne` (épreuves existantes). Le refus dit sa cause (une par refus).

Dans ce lot, le proposant est **le joueur** : contenu de parole typé `proposition` (`paroles.TYPES` :
`demande` objet | part | tâche, `contrepartie` objet | part | tâche | pièces | rien), tranché par le moteur,
`attendu` sur toute forme refusée (`donjon/refus.py`). Les constantes nouvelles (pas, poids) : une
méthode, des nombres laissés au banc, dits dans le rapport.

**Une seule règle** : la vente au prix et la demande existantes (`echanges.demander` avec `prix`) sont des
propositions (contrepartie pièces ou rien). Si tu peux les exprimer par la fonction commune **sans changer
une seule nuit des PNJ** (empreintes ci-dessous), fais-le ; sinon garde-les, et dis précisément l'écart
dans le rapport : il sera repris au lot où les PNJ proposent.

Hors de ce lot (lots suivants, ne les anticipe pas) : le geste `proposer` des PNJ dans le planificateur,
`rendre_service`, les intermédiaires (condition « remis »), les avis (3f).

## Vérification (minimale)
- Tests après rechargement (`tests/test_propositions.py`), deux cas au moins par règle : Corvus offre sa
  cloche à Gorm contre une part de vivres (acceptée ; puis refusée par un Gorm méfiant) ; une contrepartie
  différée (une tâche promise par Corvus) pèse selon la confiance, puis engagement inscrit, tenu ou abandonné
  avec son épreuve ; un mauvais marché accepté par un auditeur d'INT basse et refusé à INT haute (même
  graine) ; refus d'office sur ce qui est `necessaire` ou gardé ; forme invalide : refus avec `attendu`. État,
  engagements et ce que lit le joueur après rechargement.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference <19b0261>`), Relais, mine et auberge,
  4 graines : identiques (aucune nuit de PNJ ne doit changer). La référence se range dans le cache.
- Luna, **une passe** : un banc nouveau `tests/data/bancs/propositions.json` (quatre ou cinq saisies :
  « je te donne ma cloche contre une part de vivres », une tâche promise, un mauvais marché, une offre à un
  méfiant, une formulation libre), `tools/banc_parties.py --fil` ; appels par tour, typage du premier coup,
  aucune issue inventée par Luna.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` § 7.1 (ce qui est fait, constantes
retenues), `docs/contrat-mj.md` (le contenu `proposition`), `docs/etat-dev.md` (« Branche
`codex-propositions`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-29-propositions.md` (invariant, fonctions, mesures, limites).
