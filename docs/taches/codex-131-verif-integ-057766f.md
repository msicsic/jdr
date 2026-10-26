# Tâche Codex 131 : analyse de la vérification d'intégration 057766f (sans Luna, sans rejeu)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots moteur fusionnés depuis la vérification `590653e`
(lot 114) : 115 (tâche promise en contrepartie), 116 (rapports illisibles), 120 (rendre service), 121 (disputes). Les campagnes
sont **déjà jouées** sur `057766f` ; ce lot les **analyse**, sans rejouer une nuit. **Aucun changement de code du jeu** ; un défaut
trouvé devient un petit lot, décrit avec son cas réel, pas corrigé ici. Pas de Luna (la vérification Luna de 057766f est le lot 123).

**Poste : le portable** (les bruts n'existent que là). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ;
`PYTHONIOENCODING=utf-8`. Poste partagé : priorité réduite, au plus 2 processus. Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèle : le lot 114 (`docs/taches/codex-114-verif-integ.md`, rapport `rapport-codex-114-verif-integ.md`).

## Bruts (dépôt principal, non versionnés)
- `C:\Users\msics\donjon\artifacts\verif-integ-057766f\` : `audit-12h\` (quatre scénarios × 1985, 7, 42, 2024, 3, 11, 99, 500,
  12 h), `rixe\rixe.json` et `rixe\rixe_douce.json` (8 h × 1985, 7, 42, 2024), `verifier-8h\` (`VERIFIER` +
  `spatial.VERIFICATION` 0,2, 8 h, graine 42, Relais, mine, auberge, crue, `rixe`), `campagnes.ps1` (commandes exactes) et
  leurs `.log`/`.err`.
- Références à relire, jamais à rejouer : `590653e` (`artifacts\verif-integ-590653e\`, lot 114) et `42bb9c0`
  (`artifacts\references\42bb9c0\audit-12h\`).

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups contre une personne, décès, écarts `VERIFIER`/`VERIFICATION` et recherches bornées.
- Tableau par scénario, `42bb9c0` → `590653e` → `057766f` : sans recours, attente, noir, eau, appels, appels à l'aide, bascules,
  passages par heure (pire), échanges, propositions/acceptées, offres identiques en moins d'une heure, avis exprimés/adoptés,
  constats confiés, avertissements redits ; et pour les lots nouveaux : services spontanés rendus (`service_rendu`), tâches
  promises en contrepartie offertes/acceptées/tenues/rompues, disputes et éclats (lot 121). Les lots 120 et 121 n'avaient
  aucun cas naturel dans leurs bancs de 4 h : dire s'il y en a sur 12 h, avec scénario, graine, minute et PNJ.
- Les défauts de 590653e : la borne historique de Lucien (auberge 42, 314), les avertissements redits (crue 2024), les appels
  d'Odile (auberge 7), la contrepartie mine 1985 à 253 : corrigé, persistant ou non observé, avec la nuit et la minute.
- Les défauts nouveaux, chacun avec un cas réel (scénario, graine, minute, PNJ) et l'invariant en cause ; pour une boucle,
  dire si elle existait déjà sur `590653e` dans la même nuit.
- Pas de mesure CPU (le lot 127 a livré `tools/mesure_cout.py`) ; pas de suite complète (aucun code changé).

## Livraison
Branche `codex-verif-integ-057766f` : seulement `docs/taches/rapport-codex-131-verif-integ.md` (une page) et une entrée
« Vérification d'intégration 057766f » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas `main`).
Un éventuel outil d'analyse va dans `artifacts/verif-integ-057766f/` (non versionné), sauf s'il sert au-delà de ce lot.
