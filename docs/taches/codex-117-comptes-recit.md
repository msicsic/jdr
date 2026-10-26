# Tâche Codex 117 : les comptes du récit sont extraits juste du premier coup

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul, Luna en
4 exécutions au plus ; le lot 114 (vérification lourde) et le lot 115 (`pnj_propositions`, `echanges`) tournent. Ce lot touche
le dossier et le contrôle des comptes du récit (`narration.py`, `mj.py`, la projection des comptes), pas `echanges.py`. Termine
ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur** : le temps avant la réponse au joueur.

## Le constat (attribution du lot 113)
Deuxième famille d'appels supplémentaires du MJ : **comptes dans le récit, termes et extraction**, **8 → 16 appels, 32 → 56 s**,
relances **4 → 8** (b0042c9 → 91a4351, vingt scripts, deux passes) ; surtout des **extractions fausses** de l'auditeur (débiteur
et créancier inversés, compte-objet confondu avec une dette, « pièces rendues » lu comme dû), une seule vraie livraison
indûment affirmée. Le lot 116 confirme des « extractions de compte-objet injustifiées » parmi les refus restants. Attribution :
`C:\Users\msics\donjon\artifacts\relances-113\` (`91a4351-attribution.json`, `qualification.json`) ; rapports des lots 56
(sens des dettes), 73 (comptes de l'issue), 83 (verdict cohérent, références des comptes), 113, 116.

## D'abord, établir la cause
Sur les cas archivés : ce que l'auditeur reçoit des comptes de l'issue (forme, références, sens des rôles), ce qu'il extrait,
et pourquoi il se trompe (rôles implicites dans la phrase, pronoms « je/tu » du locuteur, comptes à objet et à pièces mêlés).

## L'invariant
**Le moteur, pas l'auditeur, établit les comptes que le récit doit restituer ; l'auditeur ne fait que relier chaque segment à un
compte fourni** (par sa référence) et dire s'il le restitue ou le contredit, sans réextraire rôles ni quantités depuis la prose.
Un récit qui inverse un compte reste refusé ; une phrase qui restitue un compte fourni n'est plus refusée pour une extraction
fausse. Corrige le contrat du dossier et du schéma, sans consigne de cas.

## Vérification
- Tests après rechargement avec MJ simulé : remboursement de Gorm et d'Aubin, refus de Brune, achat du soir (pièces rendues et
  planche due) restitués sans relance ; un compte inversé toujours refusé.
- Rejeu des refus justes de la référence (méthode des lots 93/95/116 ; cinq rejeux en cas d'écart).
- Luna, **deux passes** de `comptes`, `soir-appel`, `ressources`, `crypte` contre 91a4351 en cache : appels, relances, secondes par
  tour.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-comptes-recit`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-117-comptes-recit.md`.
