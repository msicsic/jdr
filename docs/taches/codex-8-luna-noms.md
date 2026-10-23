# Tâche Codex 8 : Luna sur les noms et l'appel négocié, et les restes des bancs Luna

Branche `codex-luna-noms` (elle porte ce fichier, issue de `main` 9075aea), worktree dans
`tmp-worktrees/`. Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-noms`, `appel-negocie`,
`relances-luna`, `parole-corrections`, `banc-luna-soir`, `reverification`), `docs/contrat-mj.md`,
`docs/taches/rapport-codex-2-noms.md`, `docs/taches/rapport-appel-negocie.md`, `docs/banc-luna-soir.md`
et `docs/reverification.md` (N5).

## Luna en parallèle
La consommation de Luna est négligeable (décision de l'utilisateur, 2026-10-23) : tu peux lancer
plusieurs exécutions Luna en même temps (`tools/banc_multi.py` en parallèle, 4 à 8 exécutions). Toujours
sur des copies, jamais sur `sauvegardes/` ; `SEUIL_AUTH` désigne le coffre du dépôt principal
(`C:\Users\msics\donjon\.seuil-auth`). Les temps de réponse comparés (`main` contre branche) se mesurent
dans les mêmes conditions de charge : lance les deux variantes ensemble ou l'une après l'autre au calme.

## 1. Vérifier ce qui ne l'a jamais été
- **Appel négocié** (fusionné sans Luna) : sur des copies de scènes (`tests/data/bancs/soir-appel.json`
  ou un banc nouveau qui place un PNJ hors de vue), « j'appelle Gorm », puis « j'arrive », « viens ici »,
  « qu'est-ce que tu veux ? », entre guillemets ou non. Attendu : formes typées sans appel au modèle, la
  réponse du PNJ entendue par l'ouïe commune, aucune promesse ou venue racontée par Luna sans le moteur.
- **Noms** : après `codex-noms`, les relances narratives des quatre bancs de référence sont passées de
  2 à 8 par passe (rapport Codex 2). Le rapport note que les scripts des bancs gardent les anciens noms,
  désormais inconnus du joueur. Sépare les deux causes : (a) relances légitimes (le joueur nomme qui il
  ne connaît pas) ; (b) défauts (Luna nomme un inconnu, le contrôle refuse un démenti qui cite un nom,
  « Ilse » refusé pour expliquer l'absence d'un lien nominal…). Pour (a), fais une variante des bancs où
  le joueur a d'abord entendu les noms (présentation dans le scénario du banc ou saisie préalable), en
  gardant l'ancienne pour comparer ; pour (b), corrige le contrat commun (règle d'`AGENTS.md`).

## 2. Les restes des bancs Luna (non corrigés, `docs/reverification.md` N5 et son tableau)
- « est-ce que quelqu'un a du bois ? » : va au seul PNJ d'en face, réécrit ; « quelqu'un » s'adresse à
  tous ceux qui entendent (règle de `paroles.repondants`, répondre à la cantonade).
- « je réponds » sans appel en cours : Luna invente qu'on l'a appelé (« Oui, Aubin ? »).
- Silences et précautions absurdes imposés par l'auditeur : « décris l'ambiance » (le crépitement d'un
  brasero allumé refusé), « Brune, laisse-moi passer » (7 appels, un repli), « Ilse, tu m'entends ? ».
  Première source de relances : voir ce que reçoit l'auditeur et ce qu'il refuse, renforcer le mécanisme
  commun (données reçues, règles déterministes), pas une consigne propre à l'exemple.
- « Tu demandes à passer sous la poutre » pris pour une parole racontée (`narration.parole_racontee`).
- « Passer sous la poutre » répondu par « Il faut une échelle » (`franchir`, dont la seule méthode est
  l'échelle) : la question doit recevoir une réponse juste sur passer dessous.
- Le refus du monde montré à la place d'une explication porte ses coordonnées (« case 5, 11 du plan »).
- « je m'étire » → « en réalisant un geste d'effort » (texte technique affiché).

## Vérifications
- Tests après rechargement (`tests/test_luna_noms.py` ou à ton choix) : chaque défaut corrigé, cas réel
  et un autre de même nature, ce que voit le joueur.
- Suite complète verte (`tools/tests.py`). Aucun changement de ce que décident les PNJ : banc rapide par
  `tools/comparer_bancs.py --empreintes` (2 h, Relais et auberge), identique.
- Luna : `main` 9075aea contre la branche, au moins 3 passes des quatre bancs de référence (relais,
  crypte, atelier, echanges), plus `soir-appel`, `soir-noir`, `soir-voix`, `ressources`, `comptes` et
  les bancs nouveaux ; appels et secondes par tour MJ, replis, relances, refus, tours avec refus ; textes
  affichés relus pour chaque saisie citée ci-dessus.
- Docs : `docs/contrat-mj.md`, `docs/plan-ouie.md` si la parole change, `docs/etat-dev.md` (« Branche
  `codex-luna-noms`, non fusionnée », compte de tests).

## Livraison
Commits signés comme d'habitude ; pousse la branche `codex-luna-noms` sur `origin` (pas `main`). Rapport
dans `docs/taches/rapport-codex-8-luna-noms.md` : causes des relances (légitimes / défauts), corrections,
mesures avant → après, limites.
