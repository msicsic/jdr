# Tâche Codex 94 : vérification d'intégration de 47d4d25 (sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots fusionnés depuis la dernière vérification
moteur `5c2ce81` : lots 50 à 91 côté moteur (constats partagés 55, offres 57, eau 58, rendez-vous 60, déjà dit 64, appels 69,
coûts 71/72/81/86/87, contre-offre 77, avis 80/88, recours prioritaire 90…). **Aucun changement de code du jeu** ; un défaut
trouvé devient un petit lot, à décrire, pas à corriger ici. Pas de Luna (le lot 93 l'occupe).

Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`. **Un seul poste partagé** avec deux autres lots
Codex (dont un qui mesure du CPU) : priorité réduite, **au plus 2 processus** de calcul, campagnes l'une après l'autre. Bruts dans
`C:\Users\msics\donjon\artifacts\verif-integ-47d4d25\` (dépôt principal, non versionné). Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèle : la vérification `5c2ce81` (`docs/etat-dev.md`, entrée « Vérification d'intégration 5c2ce81 » ; scripts dans
`C:\Users\msics\donjon\artifacts\verif-integ-5c2ce81\`). Référence `42bb9c0` (= `main`) déjà en cache :
`C:\Users\msics\donjon\artifacts\references\42bb9c0\audit-12h\` ; `5c2ce81` dans `artifacts\verif-integ-5c2ce81\audit-12h\`.
Ne rejoue ni l'une ni l'autre.

## Campagnes
1. Audit 12 h (`tools/audit_nuits.py jouer`), quatre scénarios × graines 1985, 7, 42, 2024, 3, 11, 99, 500 ; analyse comparée à
   `42bb9c0` et `5c2ce81` : plantages, violations, usurpations, coups contre une personne ; par nuit sans recours, en attente,
   noir, eau, appels, appels à l'aide, bascules, passages par heure (pire), échanges, propositions/acceptées, avis exprimés/adoptés,
   constats confiés, avertissements redits.
2. `rixe` et `rixe_douce`, 8 h, 1985, 7, 42, 2024 : aucun coup contre une personne, aucun mort ni usurpation.
3. `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, Relais, mine, auberge, crue, `rixe` : aucun écart ; recherches bornées.
4. Suite complète une fois (`tools/tests.py --processus 2`).

## Ce que le rapport doit dire
- Les huit défauts relevés à `5c2ce81` (plan/marche sur l'eau, chercher en appelant, rendez-vous d'un seul côté, propositions
  redites, contreparties absurdes, tâche abandonnée dans la minute, avertissements redits, accords grammaticaux) : corrigé,
  persistant ou non observé, avec la nuit et la minute.
- Les défauts nouveaux, chacun avec un cas réel (scénario, graine, minute, PNJ) et l'invariant en cause : ce sont les prochains
  petits lots.
- Les temps d'horloge par nuit (indicatifs, non lancés ensemble) à côté de ceux de `5c2ce81`.

## Livraison
Branche `codex-verif-integ-47d4d25` : seulement `docs/taches/rapport-codex-94-verif-integ.md` (une page, tableaux compris) et une
entrée « Vérification d'intégration 47d4d25 » dans `docs/etat-dev.md`. Commits signés, branche poussée (pas `main`).
