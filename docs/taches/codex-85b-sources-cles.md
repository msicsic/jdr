# Tâche Codex 85 b : garder le cache du lot 85 sans perdre la précision des sources

Même branche `codex-cache-prompt` (le lot 85 y est ; ce fichier s'y ajoute), même worktree. **Luna disponible** (copies
seulement ; `tools/banc_multi.py --connexion chatgpt`). Un seul poste : priorité réduite, au plus 3 processus, Luna en 4
exécutions au plus. `git merge origin/integration` au début (lots 83 et 84 fusionnés depuis).

## Le constat (rapport du lot 85)
Le cache passe de 24,6 % à **62,7 %** (`repondre_au_joueur` 71,8 %, `auditer_narration` 36,5 %), mais le MJ se dégrade :
**2,91 → 3,92 appels/tour, relances 5 → 26, replis 0 → 6**. Cause établie par le lot : sans les énumérations, Luna produit
des **sources qui ne sont pas des clés du dossier** (`conversation_validee.faits`, `comptes.issue`, identifiants de signes et
d'impressions) ; le contrôle commun les écarte, l'assertion perd son fondement, elle est redemandée, puis remplacée par un
repli. `auditer_action` est à 0 % de cache.

## L'invariant
**Le schéma reste constant, et une source se résout de façon déterministe vers la clé du dossier qu'elle désigne** : un
chemin vers un sous-champ d'une clé (`conversation_validee.faits` → `conversation_validee`, `comptes.issue` → `comptes`) ou
l'identifiant d'un élément d'une liste du dossier (un signe, une impression, un objet → sa clé `objet:<id>`, `signes`, …)
vaut cette clé, par une seule fonction de résolution des sources (comme `noms.references_fournies` du lot 83 pour les
comptes) ; seule une source qui ne désigne rien du dossier est écartée, avec un `attendu` qui liste les clés valables du
tour (qui sont dans l'entrée, pas dans le schéma). Les clés valables du tour restent données dans l'entrée, en tête de la
partie variable. Et vois pourquoi `auditer_action` n'est jamais servi par le cache (préfixe trop court ? instructions variables ?).

## Vérification
- Tests : chacune des formes de sources relevées au lot 85 résolue vers sa clé ; une source inexistante écartée avec son
  `attendu` ; schémas et instructions toujours constants entre deux scènes et deux tours.
- Luna, **une passe** des onze scripts, comparée à 882907c lu du cache **et** à la passe du lot 85 : appels/tour, relances,
  replis revenus au niveau de 882907c (≈ 2,9 appels/tour, relances ≈ 5, replis 0) **et** part en cache ≥ 60 % (≥ 70 % visé),
  par fonction. Si l'un des deux objectifs n'est pas tenu, dis lequel et pourquoi.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). Une section « 85 b » dans le rapport du lot 85 et dans `docs/etat-dev.md`.
