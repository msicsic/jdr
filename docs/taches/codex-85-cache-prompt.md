# Tâche Codex 85 : ce qui est fixe dans une requête au MJ ne change pas d'un appel à l'autre (cache ≥ 70 %)

Branche `codex-cache-prompt` (elle porte ce fichier, issue de l'intégration **7cce974**), worktree dans `tmp-worktrees/`.
**Luna disponible** (copies seulement ; `tools/banc_multi.py --connexion chatgpt`). Un seul poste : priorité réduite, au plus
3 processus, Luna en 4 exécutions au plus. **À lancer après le lot 83** (`narration.py`) ; `git merge origin/integration` au
début. Demande de l'utilisateur : « on devrait au moins avoir 70 % en cache ».

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `feat/websocket-persistant` (une WebSocket, contexte complet renvoyé à chaque
demande, `store: false`), `instructions-mj`, et les lots du MJ récents), puis `donjon/fournisseurs/openai.py` (construction
du `payload` : `tools`, `instructions`, `input`, `prompt_cache_key`), `donjon/transport_openai.py`, `donjon/mj.py` (comment
`instructions` et `schema` sont assemblés pour chaque fonction : `repondre_au_joueur`, `auditer_narration`, `auditer_action`,
`auditer_portee`), `donjon/consignes.py`, les schémas de `narration.py`, `couverture_action.py`, `portee_narrative.py`.

## Le constat (mesuré sur les 388 appels de la vérification Luna 882907c, `artifacts/verif-luna-882907c/`)
En moyenne 11 600 tokens d'entrée par appel, dont **~2 700 servis par le cache (≈ 23 %)**. Le cache du fournisseur ne sert
qu'un **préfixe identique** de la requête, dans l'ordre outils → instructions → entrée. Or, sur ces 388 appels :
- `repondre_au_joueur` : **50 schémas d'outil distincts** et **19 instructions distinctes** (224 appels) ;
- `auditer_narration` : **44 schémas distincts** (122 appels), instructions fixes ;
- les schémas portent donc des valeurs propres à la scène (listes d'identifiants, d'opérations ou de sujets admis…), et
  l'outil vient en tête : un schéma qui change invalide tout le reste du préfixe. Les instructions varient aussi selon le
  mode ou la scène (règles d'atelier, de franchissement, de parole ajoutées ou non).

## L'invariant
**Pour chaque fonction, l'outil (nom, description, schéma) et les instructions sont des textes constants de la version du
jeu ; tout ce qui dépend de la scène ou du tour vient après, dans l'entrée.** Les listes admises par la scène (identifiants,
cibles, opérations, sujets) quittent le schéma : le schéma garde des types, et la validation contre la scène reste au moteur
(refus avec `attendu`, inchangé) ; les règles conditionnelles des instructions deviennent un texte fixe unique (toutes les
règles, sans répétition) ou passent dans l'entrée. Le `prompt_cache_key` reste stable par partie et par fonction (vérifie
ce qu'il vaut aujourd'hui). Aucun changement de ce que le moteur accepte ou refuse.

## Vérification
- Un outil de mesure lit le fil des bancs : pour chaque fonction, nombre de préfixes distincts (outil + instructions) et part
  des tokens d'entrée en cache (`usage.input_tokens_details.cached_tokens`).
- Tests : les schémas et instructions de chaque fonction sont identiques entre deux scènes différentes et deux tours ; les
  refus du moteur avec `attendu` inchangés quand une valeur hors scène est proposée.
- Luna, **une passe** des onze scripts de référence (méthode du lot 79), comparée à 882907c lu du cache : appels/tour,
  relances, refus, et **part en cache ≥ 70 %** visée (dis-la par fonction). Si un comportement régresse (plus de refus de
  forme), dis lequel et pourquoi.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` (ce qui est fixe et ce qui vient du tour),
`docs/etat-dev.md` (« Branche `codex-cache-prompt`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-85-cache-prompt.md` (préfixes distincts avant/après, part en cache, mesures Luna, limites).
