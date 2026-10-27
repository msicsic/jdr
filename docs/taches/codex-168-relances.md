# Tâche Codex 168 (MJ) : d'où viennent les relances supplémentaires, et corriger la première cause

Petit lot issu de la vérification Luna `227c496` (lot 165) : relances narratives **24 → 41**, replis **1 → 2** sur les 64 parties
communes avec `cdaf371`. Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal du dépôt, voir `AGENTS.md`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (167, agendas) et un sur le laptop (166,
catalogues et surfaces dans `mj._echanger`) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce
lot touche l'audit narratif et ses contrôles (`narration.py`) et, si la cause l'exige, la voie de la parole de `mj.py` ; **pas**
l'assemblage des `faits` ni les catalogues (lot 166), `consignes.py`, `agendas.py`/`deliberation.py`/`planification.py` (lot 167).
**Bruts dans `C:\Users\msics\donjon\artifacts\relances-168\`, jamais dans le worktree.** Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, le rapport du lot 165 (« Cas à reprendre en petits lots ») et ses bruts
(`C:\Users\msics\donjon\artifacts\verif-luna-227c496\`), les rapports des lots 95, 112, 116 et 156.

## Ce qu'il faut faire
1. **Attribuer** les relances et replis supplémentaires (sans rejouer Luna : les fils sont archivés) : pour chaque relance de
   `227c496` absente ou différente dans `cdaf371`, la cause du refus (motif d'audit, contrôle déterministe), regroupée par famille.
   Familles déjà repérées : mesures résolues refusées (« deux mètres au nord et trois à l'ouest », « deux pas »), silence actuel
   d'un témoin traité comme un rappel absent, comptes (« Gorm te rend les deux pièces » refusé comme compte omis, livraison promise
   malgré l'engagement), avis désormais relus (lot 164). Dis aussi lesquelles viennent de nouveautés légitimes (avis typés).
2. **Corriger la première famille** évitable (la plus fréquente), dans le contrat commun : par exemple, une mesure résolue par
   le moteur citée telle quelle est prouvée de façon déterministe comme les segments exacts (lot 95), ou l'issue courante est
   distinguée de la mémoire des échanges (lot 112). Aucune règle propre à une phrase ; ne relâche aucun refus juste.

## Vérification
- Tests MJ simulé/console après rechargement : le cas réel de la famille corrigée et un autre de même nature, admis ; un faux
  pendant (mesure fausse, rappel inventé) toujours refusé.
- Luna, **une passe** des scripts où la famille apparaît ; rejeu des audits concernés (cinq fois chacun, critère du lot 95).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-relances` poussée (pas `main`). `docs/contrat-mj.md` si la
règle change, `docs/etat-dev.md` (« Branche `codex-relances`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-168-relances.md` (avec le tableau d'attribution).
