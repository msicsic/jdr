# Tâche Codex 114 : vérification d'intégration de 590653e (sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots moteur fusionnés depuis la vérification `47d4d25`
(lot 94) : 92 c (preuves d'absence), 97 (aucun devis sans profil), 98 b (obstacles), 103 (garde-manger), 105 (suites par nœud),
106 (accords), 107 (contreparties), 108 (avis redits), 110 (propositions redites). **Aucun changement de code du jeu** ; un défaut
trouvé devient un petit lot, décrit, pas corrigé ici. Pas de Luna.

Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`. **Un seul poste partagé** avec deux lots MJ
(Luna) : priorité réduite, **au plus 2 processus** de calcul, campagnes l'une après l'autre. Bruts dans
`C:\Users\msics\donjon\artifacts\verif-integ-590653e\` (dépôt principal, non versionné). Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèle : le lot 94 (`docs/taches/codex-94-verif-integ.md`, rapport `rapport-codex-94-verif-integ.md`, scripts et bruts dans
`C:\Users\msics\donjon\artifacts\verif-integ-47d4d25\`). Références déjà jouées, à relire sans rejouer : `42bb9c0`
(`artifacts\references\42bb9c0\audit-12h\`) et `47d4d25` (`artifacts\verif-integ-47d4d25\audit-12h\`).

## Campagnes
1. Audit 12 h (`tools/audit_nuits.py jouer`), quatre scénarios × graines 1985, 7, 42, 2024, 3, 11, 99, 500 ; analyse comparée à
   `42bb9c0` et `47d4d25` : plantages, violations, usurpations, coups ; par nuit sans recours, attente, noir, eau, appels, appels à
   l'aide, bascules, passages par heure (pire), échanges, propositions/acceptées, offres identiques en moins d'une heure, avis
   exprimés/adoptés, constats confiés, avertissements redits.
2. `rixe` et `rixe_douce`, 8 h, 1985, 7, 42, 2024.
3. `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, Relais, mine, auberge, crue, `rixe`.
4. Temps CPU de l'auberge 1985 12 h, fixe et tiré, `42bb9c0` et `590653e` **lancés ensemble** (deux processus) : où en est le
   seuil de l'utilisateur (≤ ×1,5).
5. Suite complète une fois (`tools/tests.py --processus 2`).

## Ce que le rapport doit dire
- Les défauts de 47d4d25 : boucle de Mathe (mine 3), propositions redites (mine 7), contreparties absurdes (mine 1985), avertissements
  redits (crue 2024), accords (« l'outils », « 1 pièces »), chercher en appelant (auberge 7, Odile) : corrigé, persistant ou non
  observé, avec la nuit et la minute.
- Les défauts nouveaux, chacun avec un cas réel (scénario, graine, minute, PNJ) et l'invariant en cause.
- Le rapport CPU de l'auberge contre le seuil.

## Livraison
Branche `codex-verif-integ-590653e` : seulement `docs/taches/rapport-codex-114-verif-integ.md` (une page) et une entrée
« Vérification d'intégration 590653e » dans `docs/etat-dev.md`. Commits signés, branche poussée (pas `main`).
