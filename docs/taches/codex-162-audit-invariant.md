# Tâche Codex 162 (plan prompt, L2 b) : un schéma d'audit narratif qui ne dépend pas du texte audité

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Un autre lot tourne sur ce poste (146 e, agendas) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité
réduite. Ce lot touche le schéma de l'audit narratif et sa validation dans `narration.py` (`SCHEMA_AUDIT`, `schema_audit`,
`controler`), avec leurs tests ; **pas** `mj.py`, `consignes.py` (lot 161), `sources.py`, les fournisseurs. **Bruts dans
`C:\Users\msics\donjon\artifacts\audit-162\` (dépôt principal), jamais dans le worktree.** Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (décision 6, L2), les rapports des lots 95 (audit des seuls segments libres, rapport à
variantes), 116 (verdict canonique déduit de la nature), 149 (L0 : audit, indices des segments 47, structure `anyOf` 4, enum des
sources 18 sur 103 changements) et 158 (L2, interprétation : audit encore variable 44/74), puis `narration.schema_audit`.

## L'invariant
**Le schéma de l'outil d'audit narratif est le même à chaque appel d'une partie : les indices de segments et les sources citées
sont des valeurs que le moteur valide (hors bornes, source inconnue : rapport illisible ou refus comme aujourd'hui), pas des
`enum` construits pour le texte du tour ; la structure des variantes ne dépend pas du nombre de segments.** Aucun contrôle
déterministe retiré, aucun verdict relâché ; un rapport qui cite un segment inexistant ou une source absente reste traité comme
aujourd'hui. Contrat propre pour Luna et le fournisseur local.

## Vérification
- Test : sur deux scènes rejouées par MJ simulé, le schéma d'audit sérialisé est identique d'un appel à l'autre ; un rapport
  avec un indice hors bornes ou une source inconnue est traité comme avant (illisible ou refus, avec `attendu` si c'est le cas
  aujourd'hui) ; état et rendu après rechargement inchangés.
- `tools/mesure_prompt.py` : variations du schéma d'audit avant/après (base 44/74), taille après mutualisation.
- Luna, **deux passes** des quatre bancs de référence et de `noms-dialogue`, `soir-noir`, `comptes` ; référence `cdaf371` relue
  du cache ; appels et secondes par tour MJ, secondes de l'audit, jetons cachés par voie, relances, refus, audits illisibles,
  replis ; **rejeu de refus du lot 95** (cinq fois chaque audit refusé de la référence) : pas plus d'un refus juste perdu sur cinq.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-audit-invariant` poussée (pas `main`). `docs/plan-prompt.md`
(L2), `docs/etat-dev.md` (« Branche `codex-audit-invariant`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-162-audit-invariant.md`.
