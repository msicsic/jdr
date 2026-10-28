# Tâche Codex 243 : la garde de Lucien sans réponse sous la borne de recherche

La vérification 4306c14 (lot 231, `docs/taches/rapport-codex-231-verif-integ.md`) relève **auberge 42, contrôle `VERIFIER`
+ `spatial.VERIFICATION` 0,2, 8 h : 75 recherches bornées pour Lucien à 435 min**, contre zéro sur `4d4c625`. 73 sont des
`ancienne_borne` dont le résultat égale le recalcul complet ; **deux `garder:grenier` n'ont aucune réponse** sous la borne
alors que la recherche complète trouve un optimum (126,36 et 127,29). Contrat du lot 48 : un autre résultat n'est permis
qu'au coût de la recherche complète ; « aucun plan » n'est permis que si la complète n'en trouve pas.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le PC fixe** ; au plus 2 processus, priorité réduite. Bruts du lot 231 sur ce poste :
`C:\Users\msics\donjon\artifacts\verif-integ-4306c14\`.

**Fichiers** : la recherche de `planification.py` (borne, ordre, borne admissible du séjour du lot 48) et le but
`garder`, leurs tests. **Pas** : `Vue.detresses` (lot 240) sauf lecture, `pnj_propositions`, `biens`, `echanges` (lot
228), `pnj.py` (lot 234), `deliberation.py` (lot 242), le MJ. Si la cause est hors de ces fichiers, pose la `QUESTION`.

**Bruts dans `C:\Users\msics\donjon\artifacts\bornes-243\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## Ce qu'on te demande
1. Capturer l'état à 435 (rejoue sur un worktree détaché de `4306c14`, puis sur l'intégration actuelle) ; dire si les deux
   recherches sans réponse existent encore, combien de nœuds la complète demande, et pourquoi la recherche jouée épuise sa
   borne (états dominés, séjour, garde, combinaisons de lumière…).
2. Si le contrat du lot 48 est violé (aucun plan alors que la complète en trouve un, sans recherche bornée reconnue), le
   corriger par un levier exact (mêmes décisions là où la complète ne plafonne pas). Sinon, dire que c'est une limite de la
   borne et ce qu'elle coûte à Lucien (temps sans plan), sans changer le plafond.

## Vérification
- Tests après rechargement : capture réelle, un autre cas de même nature, monde et rendu rechargés.
- Si du code change : empreintes 2 h (`tools/comparer_bancs.py --empreintes`) auberge/mine/Relais × quatre graines,
  `VERIFIER` + spatial 0,2 auberge 42 sur 8 h, coût mine 1985 4 h (`tools/mesure_cout.py`), suite complète une fois.

## Livraison
- Branche `codex-bornes-garde` poussée (pas `main`). Si la poussée est bloquée, laisse le commit local et dis-le.
- `docs/etat-dev.md` : « Branche `codex-bornes-garde`, non fusionnée ». Rapport d'une page
  `docs/taches/rapport-codex-243-bornes-garde.md`.
