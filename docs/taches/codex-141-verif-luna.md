# Tâche Codex 141 : vérification Luna de l'intégration 9a39738 (sans changer le code)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots MJ fusionnés depuis la vérification Luna `057766f`
(lot 123) : 124 + 128 (avis du joueur, opérations analysées avant le contenu), 132 (non-perception prouvée par le moteur,
N6), 135 (mots entendus préservés, rappel exact, N7), 138 (réplique au discours direct, N8) ; et les lots moteur 122, 126,
129 (sans changement de constantes), 130 (retrait du stratège), 133, 134, 136, 137 qui peuvent changer ce que Luna reçoit.
**Aucun changement de code du jeu** ; un défaut trouvé devient un petit lot, décrit avec son cas réel.

**Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : Luna en quatre exécutions au plus,
priorité réduite. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèle : le lot 123 (`docs/taches/codex-123-verif-luna.md`, rapport `rapport-codex-123-verif-luna.md`). Référence `057766f`
(quarante parties déjà en cache sur ce poste), et `91a4351` pour l'historique : **relire, jamais rejouer**.

## Campagne
- Deux passes des vingt scripts du lot 123, plus `avis-joueur` (lot 124) : `tools/banc_multi.py --variante integ=9a39738
  --variante ref=057766f --repetitions 2`, la référence lue du cache.
- Appels et secondes par tour MJ (moyenne et médiane), par fonction ; relances, refus, replis, audits illisibles.

## Ce que le rapport doit dire
- N6 (`signes-guet`), N7 (`soir-noir`, rappel du nom), N8 (`ressources`, demande au discours indirect), avis typés
  (`avis-joueur`) : corrigé, persistant ou non exercé, avec la passe et la saisie.
- Les défauts déjà suivis : remboursement de Gorm, achats payés/livrés, fausse absence dans le noir, confusion de récit des
  planches : statut.
- **Coût** : effet des avis désormais relus (lot 128) et de la liste « connu, non vu » (lot 132) sur la taille des entrées et
  les appels par tour ; relever la taille du dossier d'audit sur les scripts longs.
- Les défauts nouveaux, chacun avec son cas réel et l'invariant en cause.

## Livraison
Branche `codex-verif-luna-9a39738` : seulement `docs/taches/rapport-codex-141-verif-luna.md` (une page) et une entrée
« Vérification Luna 9a39738 » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas `main`).
Bruts dans `C:\Users\msics\donjon\artifacts\verif-luna-9a39738\`.
