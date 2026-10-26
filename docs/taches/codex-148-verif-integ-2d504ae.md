# Tâche Codex 148 : vérification d'intégration 2d504ae (moteur, sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots moteur fusionnés depuis la vérification `057766f`
(lot 131) : 122 (intermédiaires), 126 et 134 (prises, liens, traîner), 129 (outil seul, signes inchangés), 130 (retrait du
stratège), 133 (promesse tenable), 136 (enfermer), 137 (lieu des ouvertures), 139 (crue du hameau), 140 (captivité), 144
(agendas, informer), 145 (tuer). **Aucun changement de code du jeu** ; un défaut trouvé devient un petit lot, décrit avec son
cas réel, pas corrigé ici. Pas de Luna (la vérification Luna suivra les lots 142, 143 et 147).

**Poste : le PC fixe**, dans ton propre worktree (code du jeu identique à `2d504ae` ; seuls des briefs s'y ajoutent ; vérifie
`git diff --stat 2d504ae -- donjon tools` vide et n'y fais aucun `pull` pendant le lot). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`. Deux
autres lots tournent sur ce poste : **au plus 2 processus de calcul**, priorité réduite. Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèles : les lots 114 et 131 (`docs/taches/codex-131-verif-integ-057766f.md`, rapport `rapport-codex-131-verif-integ.md`).

## Campagnes (les jouer une fois, à priorité réduite)
Reprends `C:\Users\msics\donjon\artifacts\verif-integ-057766f\campagnes.ps1` (copié sur ce poste ; `Set-Location` vers ton worktree) avec
`$d='C:\Users\msics\donjon\artifacts\verif-integ-2d504ae'` : audit 12 h quatre scénarios × 1985, 7, 42, 2024, 3, 11, 99, 500 ;
`rixe` et `rixe_douce` 8 h × quatre graines ; `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, cinq scénarios. Ajoute
une campagne **`crue_hameau`** 12 h × quatre graines (nouveau scénario du lot 139). Les nuits durent : lance-les en fond et
analyse au fur et à mesure.

## Références (relire, jamais rejouer)
`C:\Users\msics\donjon\artifacts\verif-integ-057766f\` (bruts du lot 131, copiés sur ce poste) et, si présents,
`artifacts\verif-integ-590653e\`, `artifacts\references\42bb9c0\audit-12h\`.

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups contre une personne, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches
  bornées (la borne historique de Lucien, auberge 42 à 314 : inchangée ou non).
- Tableau par scénario `057766f` → `2d504ae` : sans recours, attente, noir, eau, appels, appels à l'aide, bascules, passages
  par heure (pire), échanges, propositions/acceptées, offres identiques en moins d'une heure, avis exprimés/adoptés, disputes,
  services rendus, tâches promises offertes/acceptées/tenues/rompues, constats confiés, avertissements redits.
- Lots nouveaux : agendas de Gorm dans la crue (informé à qui, quand ; sommeil, réveils répétés), commissions d'intermédiaire
  (lot 122), tâche promise de la crue 11 à 210 (lot 133) ; prises, liens, enfermements ou meurtres spontanés (attendu : aucun).
- Les défauts déjà suivis (crue 2024 avertissements redits, Odon mine 2024 appels, contrepartie mine 1985 à 253) : corrigé,
  persistant ou non observé, avec la nuit et la minute.
- Les défauts nouveaux, chacun avec un cas réel (scénario, graine, minute, PNJ) et l'invariant en cause ; pour une boucle,
  dire si elle existait déjà sur `057766f` dans la même nuit.
- Pas de mesure CPU comparative (temps d'horloge indicatifs seulement) ; pas de suite complète (aucun code changé).

## Livraison
Branche `codex-verif-integ-2d504ae` : seulement `docs/taches/rapport-codex-148-verif-integ.md` (une page) et une entrée
« Vérification d'intégration 2d504ae » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas
`main`). Bruts dans `C:\Users\msics\donjon\artifacts\verif-integ-2d504ae\` (non versionnés).
