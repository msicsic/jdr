# Tâche Codex 115 (3e) : un PNJ peut offrir une tâche en contrepartie, faute de mieux

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna (le contenu joueur des tâches promises existe déjà).
Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul ;
le lot 113 (MJ) et le lot 114 (vérification lourde, 2 processus) tournent en même temps. Ce lot touche `pnj_propositions.py`,
`propositions.py`, `echanges.py` (devis de service existants), pas la recherche (`planification.py` : seulement appeler les devis
existants) ni `deliberation.py` hors du point d'appel du recours. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` § 7.2 (décision du 2026-10-24 « faute de mieux » ; A2b lot 45 ; lots 57, 77, 107, 110),
`docs/plan-agendas.md` (engagements, A1), les rapports des lots 45, 77, 107, 110, puis `donjon/pnj_propositions.py` (`recours`),
`donjon/propositions.py`, `donjon/echanges.py` (`devis_service`, `evaluer_proposition`, `proposer`), `donjon/agendas.py`.

## Ce qui manque
Le recours « faute de mieux » (lot 45) n'offre aujourd'hui que des pièces et des biens portés. Le plan prévoit ensuite **les tâches
promises** : « je recharge ton brasero / je garde ta réserve / je t'apporte du bois si tu me donnes une part ». Le joueur peut déjà
promettre une tâche (lot 29, contenu typé, engagement tenu par l'effet réel et la perception du bénéficiaire).

## L'invariant
**Une tâche promise est une contrepartie comme une autre, pour les PNJ comme pour le joueur** : le recours peut l'offrir quand
elle sert un besoin cru de l'autre et que le proposant peut la faire **par ses propres moyens** (`devis_service`, sans compter sur
un tiers), à un coût propre qu'il juge acceptable (même évaluation inversée que les lots 57/107) ; l'auditeur l'évalue par
`evaluer_proposition` (valeur de la tâche pour lui, confiance dans la promesse, relations) ; acceptée, c'est un engagement
(`agendas`) daté, tenu par le planificateur du proposant comme les autres engagements, dû ou rompu (parole rompue, relations)
sinon. Toujours après les moyens ordinaires, jamais un geste comparé dans la recherche ; une tentative par couple lésé/besoin
(règle des lots 45/110).

## Vérification
- Tests après rechargement, même laps découpé : Brune refusée par Gorm (crue ou Relais) offre de recharger le brasero contre une
  part, Gorm accepte, la part est remise, Brune tient la tâche (le brasero est rechargé, Gorm le voit) ; un autre cas (auberge :
  garder une réserve contre un repas) ; une tâche promise non tenue devient une parole rompue ; une tâche impossible n'est pas
  offerte.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache, sinon calculée une fois) : propositions / acceptées,
  tâches promises / tenues / rompues, aucune usurpation ni boucle nouvelle ; temps CPU au bruit près.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` § 7.2, `docs/etat-dev.md` (« Branche `codex-tache-promise`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-115-tache-promise.md`.
