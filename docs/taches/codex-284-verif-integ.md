# Tâche Codex 284 : vérification d'intégration (moteur, puis Luna joué par l'orchestrateur)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots fusionnés depuis la vérification `0bad227`
(lot 274, qui a permis d'avancer `main` à ce commit) : 266 (rester près d'un proche en détresse, 3d), 275 (appeler celui
à qui l'on veut demander), 276 (la sonde 219 voit les entrées perceptives), 277 (demander l'allumage d'un foyer fixe),
280 (prêt échu et secours prioritaire), 281 (le but de protection nomme le protégé), et les diagnostics 278, 279, 282.
**Pas de Luna dans ce lot** : l'orchestrateur la joue à part sur le même commit.

**Aucun changement de code du jeu.** Un défaut trouvé devient un petit lot, décrit avec son cas réel.
**Bruts dans `C:\Users\msics\donjon\artifacts\verif-integ-<commit>\`**, jamais dans le worktree.

**Poste : le laptop**, dans ton propre worktree. Note le commit de départ ; le code du jeu doit y rester identique
(`git diff --stat <commit> -- donjon tools` vide), aucun `pull` pendant le lot. **Deux processus de calcul au plus**,
priorité réduite, en fond, détachés ; écris un fichier de fin en dernier même si une campagne échoue (erreur consignée,
campagnes suivantes poursuivies) ; termine alors par `CALCUL EN COURS : <fichier de fin>` sans surveiller en boucle.
Termine par `LOT TERMINÉ` (résumé d'une ligne avec ton verdict : intégration propre ou non pour avancer `main`) ou
`QUESTION : …`.

Modèle : les lots 241 et 274 (`docs/taches/codex-274-verif-integ.md`, `docs/taches/rapport-codex-274-verif-integ.md`).
Leurs bruts sont sur le **PC fixe** (`C:\Users\msics\donjon\artifacts\verif-integ-0bad227\` et `verif-integ-c870c8b\`) ;
copie-les une fois par `scp msics@msi-desktop:...` dans `C:\Users\msics\donjon\artifacts\` du laptop pour les relire :
**références à relire, jamais à rejouer**.

## Campagnes (une fois, en fond)
Compteurs actifs : classes 219 **dans leur version actuelle** (avec la classe `renouvellement_perceptif` du lot 276 ;
dis-le en comparant à la 274, qui comptait sans elle), causes 227.
- Audit 12 h, quatre scénarios (`relais`, `mine`, `auberge`, `crue`) × graines 1985, 7, 42, 2024, 3, 11, 99, 500.
- `rixe` et `rixe_douce`, 8 h × quatre graines. **`audit_nuits.py jouer` n'accepte pas `rixe_douce`** : joue-le par la
  voie qu'a employée le lot 274 (voir son `rixe_douce.py` dans ses bruts).
- `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, cinq scénarios.
- `crue_hameau`, 12 h × quatre graines.

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches bornées.
- Tableau par scénario `0bad227` → nouveau commit, mêmes mesures qu'au lot 274, compteurs 219/227 et S/F/D (lot 183).
- Suivis : demandes d'allumage nées naturellement (277) ; appels à un interlocuteur inaccessible (275) ; « rester près »
  (266) et leurs effets sur l'attente et la richesse ; richesse et attente du hameau (diagnostic 282) ; coups ; suspect
  Aubin Relais 2024 (lot 273 non fusionné) ; mandats prononcés naturellement.
- Défauts nouveaux, chacun avec un cas réel et l'invariant en cause ; pour une boucle, dire si elle existait déjà dans la
  même nuit sur `0bad227`.

## Livraison
- Branche `codex-verif-integ-4` : seulement `docs/taches/rapport-codex-284-verif-integ.md` (une page) et une entrée
  « Vérification d'intégration <commit> » dans `docs/etat-dev.md`. Poussée (pas `main`) ; si la poussée est bloquée,
  laisse le commit local et dis-le, sans passer par l'API GitHub.
