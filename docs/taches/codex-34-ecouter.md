# Tâche Codex 34 : une perception proposée par le MJ est un geste, pas une ambiance

Branche `codex-perception-geste` (elle porte ce fichier, issue de l'intégration **ffcc295**), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). **Luna disponible**
(`SEUIL_AUTH` vers le coffre du dépôt principal ; copies seulement).

Lis `AGENTS.md`, `docs/contrat-mj.md`, `docs/etat-dev.md` (`relances-luna` : « la contre-revue admet la
perception qui cherche » ; « À revoir », Luna), puis `donjon/mj.py`, la contre-revue d'action et
`donjon/couverture_action.py`, `donjon/narration.py` (audit, classement ambiance/mécanique), `donjon/consignes.py`.

## Le constat (vérification Luna de l'intégration, 3b6415b)
`crypte`, passe 2, saisie 9 « j'écoute à la porte… » (5 appels ; 0 sur 2 passes de `main`) : Luna propose
`ecouter` ; la contre-revue le refuse (« aucune opération d'écoute »), puis la couverture (« aucun effet de la
manœuvre ») ; Luna répond alors en dialogue « aucun son de l'autre côté ne t'est perceptible », un résultat de
perception que le moteur n'a jamais exécuté, et l'auditeur le classe en ambiance. Fil :
`C:\Users\msics\donjon\artifacts\verif-luna-3b6415b\` (`integration-r2`, `crypte`, et `relecture.txt`). Restes
voisins, une passe sur deux : « je cherche des traces de pas » (7 appels, 2 refus de la contre-revue,
`integration-r1`, `relais` n° 5).

## L'invariant
Une **perception** (écouter, chercher, examiner) dont l'effet est ce que le moteur fait percevoir est un geste
complet : la contre-revue et la couverture l'admettent sans exiger d'effet durable sur le monde, par une règle
commune à toutes les perceptions du moteur (`commandes.PERCEPTIONS` ou la table qui les déclare), jamais par
nom de geste. Et ce qu'une perception **aurait** révélé (« aucun son ne t'est perceptible », « tu ne trouves
rien ») est une affirmation mécanique : sans perception exécutée par le moteur, l'auditeur ne la classe pas en
ambiance. Dis ce qui reste sémantique.

## Vérification (minimale)
- Tests après rechargement (`tests/test_perception_geste.py`), réponses simulées : « j'écoute à la porte » et un
  autre cas de même nature (chercher des traces) passent la contre-revue et la couverture du premier coup, le
  résultat vient du moteur ; un récit « aucun son ne t'est perceptible » sans perception exécutée est refusé
  comme mécanique ; une vraie ambiance reste admise.
- Luna, **une passe** : `crypte`, `relais`, `luna-restes-ambiance` (`tools/banc_parties.py --fil`) ; appels par
  tour, « j'écoute à la porte » en au plus 3 appels, aucune ambiance qui dit le résultat d'une perception.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche
`codex-perception-geste`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-34-perception-geste.md`.
