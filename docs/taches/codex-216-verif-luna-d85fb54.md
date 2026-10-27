# Tâche Codex 216 : vérification Luna de l'intégration d85fb54 (sans changer le code)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots qui touchent le MJ ou ce qu'il voit, fusionnés
depuis la vérification Luna `227c496` (lot 165) : 169 (silence et rappel), 172 et 177 (contre-revue de la force), 173 (sol comme
surface), 178 (retenus après une porte), 180 c (comptes écrits par le moteur), 204 (portée de la main au seuil), 207 (rendu des
refus de réclamation), et les lots moteur depuis (181 à 211). **Aucun changement de code du jeu** ; un défaut trouvé devient un
petit lot, décrit avec son cas réel. La validation Luna de plusieurs de ces lots a été jouée une passe par l'orchestrateur, pas en
campagne.

**Commit joué : `d85fb54`.** Chaque partie jouée est rangée dans le cache des références. **Références : `cdaf371` (lot 153) et
`227c496` (lot 165)**, relues du cache, jamais rejouées. **Bruts dans `C:\Users\msics\donjon\artifacts\verif-luna-d85fb54\`,
jamais dans le worktree.**

**Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal du dépôt,
voir `AGENTS.md`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (212, 213) :
Luna en **trois exécutions au plus**, priorité réduite. Si la revue automatique bloque l'appel à Luna ou la poussée, laisse la
commande exacte dans `C:\Users\msics\donjon\artifacts\verif-luna-d85fb54\luna-a-jouer.txt` et pose une `QUESTION` : l'orchestrateur
la jouera. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèle : le lot 165 (`docs/taches/codex-165-verif-luna-227c496.md`, rapport `rapport-codex-165-verif-luna.md`).

## Campagne
- Deux passes des scripts du lot 165 (vingt historiques, `avis-joueur`, onze bancs de force, `poser-sol-*`, `sous-obstacle-*`), plus
  les bancs des lots suivants s'ils existent (`comptes`, `attitudes` exclu car non fusionné) :
  `tools/banc_multi.py --variante integ=d85fb54 --variante ref=227c496 --repetitions 2` (référence lue du cache).
- Appels et secondes par tour MJ (moyenne et médiane), par fonction ; relances, refus, replis, audits illisibles ; jetons cachés.

## Ce que le rapport doit dire
- Latence, relances et refus comparés à `227c496` et `cdaf371` (le lot 165 avait relevé relances 24 → 41, replis 1 → 2).
- Comptes (180 c) : remboursement de Gorm, achats payés/livrés, phrases du moteur ; force (traîner, enfermer, geste improvisé) ;
  poser au sol ; prise au seuil (204) ; réclamation (207) : corrigé, persistant ou non exercé, avec la passe et la saisie.
- Les défauts nouveaux, chacun avec son cas réel et l'invariant en cause.

## Livraison
Branche `codex-verif-luna-d85fb54` : seulement `docs/taches/rapport-codex-216-verif-luna.md` (une page) et une entrée
« Vérification Luna d85fb54 » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas `main`) ;
si la poussée est bloquée, laisse le commit local et dis-le.
