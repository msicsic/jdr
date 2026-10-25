# Tâche Codex 77 (3e, suite) : qui refuse dit ce qui le ferait céder

Branche `codex-contre-offre` (elle porte ce fichier, issue de l'intégration **38e5d7e** : lots 38 à 74 compris), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Pas de Luna dans ce lot (côté PNJ ; le
contenu typé du joueur viendra après). **Un seul poste** : priorité réduite, au plus 3 processus ; la bissection du lot 76
tourne en même temps.

Ce lot touche `donjon/echanges.py`, `donjon/deliberation.py` (`retenir_refus`, `tient`), `donjon/pnj_propositions.py`,
l'esprit ; pas `planification.py` (sauf la lecture de la condition retenue si le planificateur doit la voir : dis-le, et
garde-la dans `_entrees`).

Lis `AGENTS.md`, **`docs/plan-relations.md` § 7.2 (décision « faute de mieux ») et le point « Contre-offre » de 3e**,
`docs/etat-dev.md` (entrées `codex-proposer-recours` 45, `codex-offre-sensee` 57, `refus-retenus`, `crochetage-surenchere`),
puis `donjon/echanges.py` (`demander`, `evaluer_proposition`, `proposer`, raisons d'un refus), `donjon/deliberation.py`,
`donjon/pnj_propositions.py`, `donjon/biens.py` (`reticence`).

## Le manque
Un refus (« refus » par réticence, « nécessaire » parce qu'un autre besoin le presse) ferme la porte sans rien dire de ce
qui l'ouvrirait. Le demandeur ne sait lever le refus qu'en payant un prix catalogue, s'il existe, ou en proposant au hasard.

## L'invariant
**Celui qui refuse une demande par réticence ou parce qu'un autre besoin le presse dit, s'il le sait, ce qui le ferait
céder** : un prix (le seuil où sa réticence cède, d'après sa propre valeur des pièces) ou la satisfaction de son besoin du
moment (« apporte-moi de quoi manger et je te prête ma clé »), jamais une condition qu'il ne tiendrait pas. La condition est
une **offre conditionnelle** dans la forme commune du lot 67, retenue avec le refus (`esprit["refus"]`, sauvegardée) ; le
demandeur PNJ la lit comme un moyen nouveau (la règle des refus retenus) et peut la satisfaire, puis redemander ; remplie, la
demande est accordée par le moteur (pas par un second jet). Faute de mieux reste la règle d'A2b : rien n'est comparé dans la
recherche au-delà de ce que la condition retenue apporte comme moyen. Pas de cas propre à une personne ou un objet.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : un refus par réticence avec prix dit, le demandeur paie et reçoit ; un refus
  par besoin (faim) avec la condition « apporte-moi à manger », le demandeur l'apporte et reçoit ; une condition impossible
  pour le demandeur, retenue sans boucle ; aucun refus par méfiance ne donne de condition.
- Banc rapide (`tools/comparer_bancs.py --reference 38e5d7e --processus 3`, 4 h, 4 graines, quatre scénarios) : contre-offres,
  conditions remplies, demandes accordées, vols, aucune usurpation ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` (3e : ce qui est fait), `docs/etat-dev.md` (« Branche
`codex-contre-offre`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-77-contre-offre.md`.
