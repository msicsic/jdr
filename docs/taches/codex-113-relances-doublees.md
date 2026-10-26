# Tâche Codex 113 : les relances du MJ ont doublé entre b0042c9 et 91a4351 — attribuer, puis corriger la première famille

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** :
priorité réduite, au plus 2 processus de calcul, Luna en 4 exécutions au plus ; d'autres lots tournent (lot 110 dans `echanges`/
`propositions`/`deliberation` ; lot 112 dans le dossier du récit, `mj.py`/`narration.py` : coordonne-toi sur des fonctions
distinctes). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur** : le temps avant la réponse au joueur et la qualité du MJ.

## Le constat (vérification Luna du lot 111, deux passes, vingt scripts)
De b0042c9 (lot 99) à 91a4351 (lots MJ 100, 101, 102, 104, 106) : **2,99 → 3,38 appels/tour (+13 %)**, **10,3 → 11,5 s/tour**,
**relances 6,5 → 13,5**, refus 16 → 18 ; par fonction (s/tour) audit narratif 3,10 → 4,05, révision 0,27 → 0,61. Rapport :
`docs/taches/rapport-codex-111-verif-luna.md` ; parties et fils des deux versions **déjà jouées et rangées** :
`C:\Users\msics\donjon\artifacts\verif-luna-b0042c9\` et `…\verif-luna-91a4351\` (et le cache `artifacts/references/`).
Constats liés : N4 (réclamation à Gorm perdue après deux refus de fidélité sur la quantité, puis secours aux mots exacts sans
opération), N5 (méta-preuve affichée), N6 (non-perception refusée comme absence, huit appels).

## D'abord, attribuer (sans rejouer Luna)
Dans les fils des deux versions : chaque relance et chaque appel en plus du minimum d'un tour, par famille (cause exacte,
`attendu`, contrôle qui refuse), **justifiée ou évitable**, et le lot qui l'a introduite (100 forme/repli, 101 garde lexical, 102
couverture de la vue, 104 opérations contestées, 106 accords). Tableau des familles nouvelles ou accrues, en appels et secondes.

## L'invariant
Pour la **première famille évitable introduite** par ces lots (et elle seule ; N4 si c'est elle) : le contrôle qui refuse à tort
juge sur la bonne donnée, ou une opération établie par le moteur (une dette portée par les comptes, sa quantité) n'est pas perdue
parce qu'une revue sémantique conteste sa forme. Corrige le contrat commun, pas un cas ; les refus justes restent refusés.

## Vérification
- Tests après rechargement avec MJ simulé : le cas réel de la famille, un autre de même nature ; un refus juste de même forme
  toujours refusé ; si N4 est traité : « Gorm, rends-moi les deux pièces que tu me dois » rembourse, état et comptes après recharge.
- Rejeu des refus justes de la référence sur leurs entrées exactes (méthode des lots 93/95).
- Luna, **deux passes** des scripts qui exercent la famille (au moins `comptes`, `signes-guet`, `soir-noir`), contre 91a4351 en
  cache : appels, relances, secondes par tour.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-relances-doublees`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-113-relances-doublees.md` (tableau d'attribution, famille traitée,
gain, familles suivantes).
