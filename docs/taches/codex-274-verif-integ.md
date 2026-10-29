# Tâche Codex 274 : vérification d'intégration (moteur, sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots fusionnés depuis la vérification `c870c8b`
(lot 241) : 242 (suivi des délégations), 243/244 (bornes de garde, lumière faible), 246 (restitution en route),
247 (oracles), 248 (ascendant neutre), 251 et 259 (présence au service), 252 (filiation de mandat), 253 (restitution
et séjour), 254 (statut sourcé), 256 (jugement de mandat), 258 (devis vu par l'observateur), 260 (A5 : faire ou
confier), et les diagnostics 261–272. La partie Luna est déjà faite (entrée « Vérification Luna c9459ce » de
`docs/etat-dev.md`) : **pas de Luna ici**.

**Aucun changement de code du jeu.** Un défaut trouvé devient un petit lot, décrit avec son cas réel.
**Bruts dans `C:\Users\msics\donjon\artifacts\verif-integ-<commit>\`**, jamais dans le worktree.

**Poste : le PC fixe**, dans ton propre worktree. Note le commit de départ ; le code du jeu doit y rester identique
(`git diff --stat <commit> -- donjon tools` vide), aucun `pull` pendant le lot. D'autres lots calculent sur ce poste :
**un seul processus de calcul à la fois**, priorité réduite, en fond, détaché ; termine alors par
`CALCUL EN COURS : <fichier de fin>` (ne surveille pas en boucle). Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

Modèle : le lot 241 (`docs/taches/codex-241-verif-integ.md`, `docs/taches/rapport-codex-241-verif-integ.md`) ; ses bruts
sont sur ce poste dans `C:\Users\msics\donjon\artifacts\verif-integ-c870c8b\` : **références à relire, jamais à rejouer**.

## Campagnes (une fois, en fond)
Compteurs actifs : classes 219 **dans leur version actuelle** (lots 265 et 271 : changements de moyen, rendez-vous clos,
entrées publiées utilisées ; dis-le en comparant à la 241, qui comptait sans elles), causes 227.
- Audit 12 h, quatre scénarios × graines 1985, 7, 42, 2024, 3, 11, 99, 500.
- `rixe` et `rixe_douce`, 8 h × quatre graines.
- `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, cinq scénarios.
- `crue_hameau`, 12 h × quatre graines.

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches bornées.
- Tableau par scénario `c870c8b` → nouveau commit, mêmes mesures qu'au lot 241, compteurs 219/227 et S/F/D (lot 183).
- Suivis : réserves du lot 260 (crue 7/42, oisiveté urgente 0/0 → 55/195, attente 0/0 → 25/130 PNJ·min) ; mandats
  prononcés naturellement (A5, attendus rares) ; Lucien auberge 42 à 435 (244) ; richesse du hameau ; attente hameau ;
  suspect Aubin Relais 2024 (lot 272, défaut connu, correctif 273 non fusionné) ; coups (Aubin/Gorm hameau 1985 au 241).
- Défauts nouveaux, chacun avec un cas réel et l'invariant en cause ; pour une boucle, dire si elle existait déjà dans la
  même nuit sur `c870c8b`.

## Livraison
- Branche `codex-verif-integ-3` : seulement `docs/taches/rapport-codex-274-verif-integ.md` (une page) et une entrée
  « Vérification d'intégration <commit> » dans `docs/etat-dev.md`. Poussée (pas `main`) ; si la revue bloque la poussée,
  laisse le commit local et dis-le.
