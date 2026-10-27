# Tâche Codex 180 (MJ) : les comptes sont écrits par le moteur, hors de l'audit sémantique

Décision de l'utilisateur, 2026-10-27 : **ce que le moteur peut écrire, il l'écrit, et ce texte ne passe plus par l'audit
sémantique.** Premier domaine : les comptes. Les lots 117/117 b/117 c (sens fermé) et 168 (examen obligatoire) sont abandonnés :
le contrôle sémantique des comptes dans la prose de Luna produit soit des inversions admises, soit des faux refus et un audit plus
lourd. Lot de 30 à 45 minutes (`AGENTS.md`) ; livraison partielle permise si elle dit ce qui reste. Pas de Luna dans le lot
(coffre illisible depuis les agents de ce poste) : écris la commande exacte dans
`C:\Users\msics\donjon\artifacts\comptes-180\luna-a-jouer.txt` (deux passes de `comptes`, `soir-appel`, `ressources`, `echanges`,
une passe des quatre bancs de référence, référence `cdaf371`). **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (179 : `echanges.py`, `social.py`, `agendas.py`,
`esprits.py`) : au plus 2 processus de calcul, priorité réduite. Ce lot touche la narration et son audit (`narration.py`), la
préparation du récit (`mj.py`), la règle de narration là où elle est définie, et leurs tests ; il **lit** les comptes du moteur
sans modifier `echanges.py`, `social.py`, `biens.py`, `agendas.py`, `esprits.py`. **Bruts dans
`C:\Users\msics\donjon\artifacts\comptes-180\`, jamais dans le worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé
d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 56, 73, 95 (preuve exacte des segments moteur), 113, 117 b,
117 c (branche `codex-comptes-recit-c`), 168 (branche `codex-relances-168`, `attribution.json` dans
`C:\Users\msics\donjon\artifacts\relances-168\`) et 165, puis le dossier `comptes` transmis au récit et son contrôle dans
`narration.py` (`SCHEMA_COMPTES`, `segments_etablis`, extraction et comparaison des comptes).

## L'invariant
**Tout compte que l'issue établit (paiement, remboursement, dette, refus de rendre, livraison promise ou faite) est affiché au
joueur par une phrase écrite par le moteur, prouvée exactement à l'affichage et à l'enregistrement comme les segments du lot 95 ;
la prose libre de Luna ne restate ni montant, ni sens d'un transfert, ni dette, et une telle restatement est écartée par une garde
déterministe, sans extraction sémantique par l'auditeur.** L'audit narratif perd la rubrique `comptes` ; il n'en gagne aucune
autre. Une phrase du moteur dit seulement ce que l'état établit, avec les références publiques (aucun nom non appris, aucune
entité non perçue). Aucune règle propre à Gorm, Aubin, un objet ou une formulation.

## Vérification
- Rejeu sans Luna (MJ simulé, console, recharge) des cas réels : `comptes` p2 n°1 (« Gorm te rend les deux pièces » refusé à
  tort), `soir-appel` p1 n°5 (repli après trois récits refusés), l'inversion réelle du lot 117 ; plus un autre compte de même
  nature (dette niée, livraison promise). Attendus : phrase du moteur affichée et rechargée identique, prose libre sans montant
  admise sans audit de compte, prose qui restate un compte (même juste) écartée par la garde avec `attendu`, inversion impossible.
- Les contrôles déterministes existants (voix d'auteur, noms, fuite d'entités non perçues) restent identiques sur les rapports
  archivés hors comptes.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-comptes-ecrits-moteur` poussée (pas `main`).
`docs/contrat-mj.md` (la règle change), `docs/etat-dev.md` (« Branche `codex-comptes-ecrits-moteur`, non fusionnée » ; 117 c et
168 abandonnés). Rapport d'une page : `docs/taches/rapport-codex-180-comptes-ecrits-moteur.md`.
