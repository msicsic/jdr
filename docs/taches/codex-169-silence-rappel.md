# Tâche Codex 169 (MJ) : un silence actuel n'est pas un rappel du passé

Petit lot issu de l'attribution des relances (lot 168, famille « rappels hors avis », 6 relances sur la vérification Luna
`227c496`). Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal du dépôt, voir `AGENTS.md`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (167, agendas) et un sur le laptop (166,
catalogues dans `mj._echanger`) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche
l'extraction et le contrôle des rappels de l'audit narratif (`narration.py`) et leurs tests ; **pas** `mj.py`, `consignes.py`,
`agendas.py`/`deliberation.py`/`planification.py`. **Bruts dans `C:\Users\msics\donjon\artifacts\silence-169\`, jamais dans le
worktree.** Si une revue automatique bloque Luna ou la poussée, termine le reste, commite localement et écris la commande exacte
dans `C:\Users\msics\donjon\artifacts\silence-169\luna-a-jouer.txt`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 112 (redire le passé, extraction des `rappels`), 156 (ordre des
paroles entendues) et 168 (attribution, `C:\Users\msics\donjon\artifacts\relances-168\attribution.json`), puis les fils cités :
`echanges` p1 t2 / p2 t1, `noms-dialogue` p2 t2, `crypte` p2 t41 (`C:\Users\msics\donjon\artifacts\verif-luna-227c496\`).

## L'invariant
**Ce qu'un personnage fait ou ne fait pas maintenant (un témoin qui se tait, qui ne réagit pas, l'issue courante établie par le
moteur) n'est pas un rappel d'une parole passée : l'audit ne le compare pas aux échanges passés.** Seule une affirmation sur ce
qui a été dit auparavant est un rappel, contrôlé comme au lot 112. Établis d'abord dans les fils quel champ ou quelle consigne de
l'audit classe le silence courant comme rappel ; corrige le contrat commun (définition de l'extraction `rappels`, ou preuve
déterministe que le segment décrit l'issue courante), sans mot-clé ni règle propre à une scène. Un faux rappel (« tu m'as dit… »
jamais dit) reste refusé.

## Vérification
- Tests MJ simulé/console après rechargement : les cas réels admis (silence d'un témoin, absence de réponse), un autre de même
  nature ; un faux rappel toujours refusé ; état et rendu inchangés.
- Rejeu des audits concernés (cinq fois chacun, base contre branche, critère du lot 95), puis Luna, **une passe** de `echanges`,
  `noms-dialogue`, `soir-noir` ; référence `cdaf371` relue du cache.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-silence-rappel` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/etat-dev.md` (« Branche `codex-silence-rappel`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-169-silence-rappel.md`.
