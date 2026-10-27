# Tâche Codex 165 : vérification Luna de l'intégration 227c496 (sans changer le code)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots MJ fusionnés depuis la vérification Luna `cdaf371`
(lot 153) : 150 (L1, préfixe par voie), 151 (L5, refus local hors de portée), 152 (L4, dossiers à portée), 154 (L8, poser au
sol), 156 (ordre des paroles entendues, N7), 157 (restes de force 4f), 158 (L2, schéma d'interprétation invariant), 159 (N11,
source des pièces), 161 (L3, consignes invariantes), 164 (avis du joueur), et des lots moteur 146 à 146 e et 155. **Aucun
changement de code du jeu** ; un défaut trouvé devient un petit lot, décrit avec son cas réel.

**Commit joué : `227c496`.** Chaque partie jouée est rangée dans le cache des références. **Référence : `cdaf371`** (lot 153),
relue du cache, jamais rejouée. **Bruts dans `C:\Users\msics\donjon\artifacts\verif-luna-227c496\`, jamais dans le worktree.**

**Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal du dépôt,
voir `AGENTS.md`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (163) et un sur le
laptop : Luna en **trois exécutions au plus**, priorité réduite. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Modèle : le lot 153 (`docs/taches/codex-153-verif-luna-cdaf371.md`, rapport `rapport-codex-153-verif-luna.md`).

## Campagne
- Deux passes des 32 scripts du lot 153 (vingt historiques, `avis-joueur`, onze bancs de force), plus `poser-sol-*` et
  `sous-obstacle-*` : `tools/banc_multi.py --variante integ=227c496 --variante ref=cdaf371 --repetitions 2` (référence lue du
  cache ; les scripts sans référence en cache sont joués sur `227c496` seulement).
- Appels et secondes par tour MJ (moyenne et médiane), par fonction ; relances, refus, replis, audits illisibles ; jetons cachés
  par voie et `usage.attribution` (outils, consignes, items).

## Ce que le rapport doit dire
- Latence et cache, par fonction et par voie, comparés à `cdaf371` : l'effet cumulé de L1 à L5 et L8.
- Refus hors de portée répondus localement (L5) ; aucune affordance distante proposée (L4) ; poser au sol (L8) sans refus.
- N7, N11, avis du joueur (attendu 6/6), restes de force 4f (traîner, enfermer, geste improvisé) : corrigé, persistant ou non
  exercé, avec la passe et la saisie.
- Les défauts déjà suivis : remboursement de Gorm, achats payés/livrés, fausse absence dans le noir : statut.
- Les défauts nouveaux, chacun avec son cas réel et l'invariant en cause.

## Livraison
Branche `codex-verif-luna-227c496` : seulement `docs/taches/rapport-codex-165-verif-luna.md` (une page) et une entrée
« Vérification Luna 227c496 » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas `main`).
