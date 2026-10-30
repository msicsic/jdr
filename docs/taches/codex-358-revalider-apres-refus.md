# Tâche Codex 358 : une action différée est revalidée contre un refus encore valable

Petit lot moteur, révélé par la reprise du lot 306 (A5, agenda du hameau, branche `codex-a5-agenda-hameau` 2d696f65,
non fusionnée pour cette seule raison). Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 306 sur sa branche
(`docs/taches/rapport-codex-306-a5-agenda-hameau.md`, section « Limite bloquante instruite ») et, par mot-clé dans
`docs/historique-lots.md` (sans le lire en entier), les lots qui ont fait le contrat des refus retenus et de la
revalidation des étapes (`refus_retenu`, `refus_etape`, lots 213, 225, 256, 338, 340).

## Le cas
Hameau (`crue_hameau`), graine 1985 : Gorm tente sept fois de confier Sève vers la galerie, minutes 4 à 7, refus
`impossible`. À **t=4200 (minute 7)**, le plan conservé depuis la minute 4 contient encore `confier` à Maël ;
`refus_retenu` retourne le refus de la minute 6 pour exactement ce mandat, **mais l'acte est réexécuté**. Captures,
diagnostics instrumentés et recharges : `C:\Users\msics\donjon\artifacts\agenda-hameau-306\reprise-integration\`
(`diagnostic-1985-4200.json` et voisins, `capture-crue_hameau-1985.json`, `diagnostiquer.py`).

## Invariant
**Toute étape d'un plan conservé est revalidée au moment de son exécution contre les refus retenus encore valables
(même règle que pour l'admission d'un nouveau plan : `refus_etape` commun au choix et à `agir`) ; un refus qui tient
interdit de réexécuter le même acte avec la même cible et les mêmes termes, quel que soit l'âge du plan.** Le refus
cesse seulement selon ses règles existantes (croyance ou moyen nouveau, jamais le délai seul). Pas de cas particulier
du mandat, de Gorm ou du hameau : corriger le chemin commun de la revalidation d'une action différée.

## Vérification
- Le cas réel rejoué depuis la capture (même chronique jusqu'à t=4200, puis plus de réexécution ; monde, rendu, scène
  et écoute identiques après recharge et laps découpé), et un autre cas de même nature (une autre action différée après
  refus, autre scénario : demande ou tâche payée refusée puis restée dans un plan conservé).
- Tests ciblés et voisins (refus retenus, mandats, recours d'agenda, tâches payées, `test_refus_retenus`, protéger).
- Banc rapide 4 h, quatre graines, Relais, mine, crue (`tools/comparer_bancs.py --reference main`, cache) ; pas de
  suite complète, ni Luna.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/pnj.py` (`refus_etape`, `agir`), `donjon/deliberation.py`,
`donjon/agendas.py` si la revalidation du mandat y passe. Le lot 335 (suivi vocal, PC fixe) touche `planification.py`,
`pnj.py`, `trajet_estime.py` : signale tout recouvrement. Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-revalider-apres-refus`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-358-revalider-apres-refus.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\revalider-358\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
