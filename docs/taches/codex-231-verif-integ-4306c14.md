# Tâche Codex 231 : vérification d'intégration 4306c14 (moteur, sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots moteur fusionnés depuis la vérification `4d4c625`
(lot 212). Lots concernés :
- 205 (péril d'eau), 207 (réclamer), 211 (localisation crue), 213 (contrat d'engagement), 214 (racheter son bien) ;
- 220 (bourse redemandée), 221 (demander où est quelqu'un), 223 (secours acquitté), 224 (service non défait) ;
- 225 (réessai lié à l'obstacle), 226 (contact comme sous-but) ;
- les outils 219 et 227 (compteurs).

**Aucun changement de code du jeu.** Un défaut trouvé devient un petit lot, décrit avec son cas réel. Pas de Luna. **Bruts dans
`C:\Users\msics\donjon\artifacts\verif-integ-4306c14\`, jamais dans le worktree.**

**Poste : le PC fixe**, dans ton propre worktree. Le code du jeu doit être identique à `4306c14` : vérifie que
`git diff --stat 4306c14 -- donjon tools` est vide, et ne fais aucun `pull` pendant le lot. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`. Deux autres lots calculent sur ce poste (228, 230) :
**un seul processus de calcul à la fois**, priorité réduite, en fond. Termine ton dernier message par `LOT TERMINÉ` (résumé
d'une ligne) ou par `QUESTION : …`.

Modèle : le lot 212 (`docs/taches/codex-212-verif-integ.md` et `rapport-codex-212-verif-integ.md`), lanceur et bruts dans
`C:\Users\msics\donjon\artifacts\verif-integ-4d4c625\` sur ce poste.

## Campagnes (une fois, en fond, à priorité réduite)
L'audit tourne avec les compteurs actifs : classes du lot 219 et causes des états payés perdus du lot 227.
- Audit 12 h, quatre scénarios × graines 1985, 7, 42, 2024, 3, 11, 99, 500.
- `rixe` et `rixe_douce`, 8 h × quatre graines.
- `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, cinq scénarios.
- `crue_hameau`, 12 h × quatre graines.

## Références (relire, jamais rejouer)
Bruts du lot 212 dans `artifacts\verif-integ-4d4c625\`, sur ce poste.

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches bornées.
- Tableau par scénario `4d4c625` → `4306c14`, mêmes mesures qu'au lot 212, plus :
  - les classes du compteur 219 (suspects, à expliquer) ;
  - les causes 227 des états payés perdus (un « geste fautif » est une violation du lot 224) ;
  - S/F/D du lot 183.
- Ce que les lots annonçaient à surveiller :
  - attente crue et hameau (205, 211, 226) ;
  - 16 coups crue 2024 (212 → 223) ;
  - boucle de la bourse mine 1985 (220) ;
  - alternances poêle/garde d'Anselme auberge 2024 (222) ;
  - questions « où est » en rafale (221 : refus sociaux réarmés au hameau 42) ;
  - sommeils répétés de l'agenda de Gorm crue 2024 (226) ;
  - renoncements de la mine (225) ;
  - rendez-vous « Ici, viens ! » rompus (cas Mireille/Mathurine, auberge, confié au lot 230 : en compter les occurrences
    naturelles).
- Les défauts nouveaux, chacun avec un cas réel et l'invariant en cause. Pour une boucle, dire si elle existait déjà dans la
  même nuit sur `4d4c625`.

## Livraison
- Branche `codex-verif-integ-4306c14` : seulement `docs/taches/rapport-codex-231-verif-integ.md` (une page) et une entrée
  « Vérification d'intégration 4306c14 » dans `docs/etat-dev.md`.
- Commits signés si une clé est configurée, branche poussée (pas `main`). Si la poussée est bloquée, laisse le commit local et
  dis-le.
