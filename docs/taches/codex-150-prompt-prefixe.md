# Tâche Codex 150 (plan prompt, L1) : un préfixe ordonné par voie, depuis `cache-kv-local`

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le laptop** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Un autre lot tourne sur ce poste (lot 151, refus local hors de portée, branche de refus de `mj.py`) : au plus 2 processus de
calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche `donjon/sources.py` (nouveau), `donjon/fournisseurs/`
(`openai.py`, `local.py`, `__init__.py`), `config.py`, `jeu.py` et l'assemblage des requêtes dans `mj.py` ; **pas** la branche
de refus `HorsDePortee` de `mj.py` (lot 151), ni le contenu des consignes ou du schéma (lots L2, L3). Termine ton dernier message
par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (décisions 5 et 7, lots), `docs/contrat-mj.md`, puis la branche d'essai d'Argon
**`origin/cache-kv-local`** : `d7913ce` (premier essai) et `9d53229` (relecture intégrée), base `0a53910`. Elle est la source de
ce lot ; elle **n'est pas fusionnée telle quelle** : porte ses changements sur l'intégration actuelle (de nombreux lots MJ ont
touché `mj.py` depuis `0a53910`).

## L'invariant
**Chaque voie (interpréter, raconter, raconter le résultat, chaque audit) compose sa requête dans un ordre stable, du plus
stable au plus variable, avec sa propre clé de cache ; le contenu envoyé est le même qu'avant, à l'ordre près, et la consigne
de révision n'apparaît qu'en relance, en fin d'entrée.** Concrètement, depuis `9d53229` : `sources.ordonner_faits`,
`ordonner_entree`, `voie_cache` ; `prompt_cache_key` par voie dans `fournisseurs/openai.py` ; `INSTRUCTIONS_REVISION` retirée du
premier appel ; fournisseur local OpenAI-compatible (`--connexion local`, `fournisseurs/local.py`, slots par voie). Garde
l'ordre des champs du schéma (`mode`, `texte`, `faits`, `proposition`) et `INSTRUCTIONS_RESULTAT` tels qu'à l'intégration.
Aucun changement de règle, de schéma ni de consigne au-delà du déplacement de la révision.

## Vérification
- Tests de `9d53229` portés (`test_cache_kv_local.py`) et un test qui contrôle qu'à l'ordre près, les requêtes de chaque voie
  sont identiques à celles d'avant le lot, sur deux scènes rejouées par MJ simulé ; état et rendu après rechargement inchangés.
- Luna, **deux passes** des quatre bancs de référence et des bancs `noms-dialogue`, `soir-noir`, `soir-appel` ; référence
  `cdaf371` (dernière fusion MJ) jouée une fois et rangée en cache si absente. Appels et secondes par tour MJ (moyenne et
  médiane), jetons cachés **par voie** (et `usage.attribution` s'il est présent), relances, refus, replis ; critère de refus du
  lot 95. Si un serveur local est disponible sur ce poste, une passe en `--connexion local` ; sinon, dis-le.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-prompt-prefixe` poussée (pas `main`).
`docs/plan-prompt.md` (L1 fait), `docs/etat-dev.md` (« Branche `codex-prompt-prefixe`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-150-prompt-prefixe.md`.
