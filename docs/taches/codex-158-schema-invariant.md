# Tâche Codex 158 (plan prompt, L2) : un schéma qui ne dépend pas du tour

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** : la voie d'interprétation d'abord, l'audit narratif
ensuite si le temps le permet ; dis ce qui reste. **Poste : le laptop** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Un autre lot tourne sur ce poste (lot 159, correction d'un achat dans la voie de la parole de `mj.py`) : au plus 2 processus de
calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche l'assemblage du schéma d'interprétation dans `mj.py`
(`_echanger`), le schéma de l'audit narratif (`narration.py`) si le temps le permet, la validation des réponses par le moteur,
`fournisseurs/schema.py` si besoin, et leurs tests ; **pas** la voie de la parole ni la correction des échanges (lot 159), ni
les consignes (L3). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (décision 6, L2), le rapport du lot 149 (L0 : causes de divergence classées,
interprétation : enum `faits` 54, branches `proposition` 28, modes 22 ; audit : indices des segments 47, `anyOf` 4, enum des
sources 18), le rapport du lot 150 (L1, `sources.py`), `docs/contrat-mj.md`, puis l'assemblage du schéma dans `mj._echanger`
(`mode.enum` conditionnel, `faits.items.enum = list(faits)`, `proposition.anyOf` conditionnel, `schema_faits_suite`).

## L'invariant
**Le schéma de l'outil d'une voie est le même à chaque appel d'une partie : tous les modes et toutes les branches de
`proposition` y figurent ; `faits` est une liste de chaînes que le moteur valide (une citation inconnue est écartée ou refusée
comme aujourd'hui) ; un mode ou une branche sans objet ce tour-là est refusé par le moteur avec `attendu`, pas retiré du
schéma.** `SCHEMA_FAITS` et sa variante avec `suite` deviennent une seule branche où `suite` est nullable ; une question de
faisabilité garde son contrat (le geste est exigé : refus avec `attendu` si `suite` manque). Ordre des champs inchangé
(`mode`, `texte`, `faits`, `proposition`). Aucune règle propre à un scénario ; contrat propre pour Luna et le fournisseur local.

## Vérification
- Test : sur deux scènes rejouées par MJ simulé (Relais, auberge), le schéma sérialisé d'interprétation est identique d'un tour
  à l'autre (et de l'audit si traité) ; chaque mode indisponible proposé est refusé avec `attendu` ; une citation de fait
  inconnue suit le contrat existant ; état et rendu après rechargement inchangés.
- `tools/mesure_prompt.py` (lot 149) : taille envoyée après mutualisation, avant/après, et part des appels où le schéma change.
- Luna, **deux passes** des quatre bancs de référence et de `noms-dialogue`, `soir-noir`, `soir-appel`, `atelier` ; référence
  `cdaf371` relue du cache ; appels et secondes par tour MJ (moyenne et médiane), jetons cachés par voie et `usage.attribution`
  (outils, consignes, items), relances, refus, replis ; critère de refus du lot 95.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-schema-invariant` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/plan-prompt.md` (L2), `docs/etat-dev.md` (« Branche `codex-schema-invariant`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-158-schema-invariant.md`.
