# Tâche Codex 154 (plan prompt, L8) : poser au sol, sans identifiant de salle

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Deux autres lots tournent sur ce poste, deux sur le laptop (lots 150 et 151 dans `mj.py`, `sources.py`, fournisseurs) : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche la validation des opérations de
déplacement (`deplacer`, `prelever` et les effets d'improvisation qui déplacent) dans le moteur, la ligne correspondante de
`consignes.py`, et leurs tests ; **pas** l'assemblage des requêtes de `mj.py`, `sources.py`, les fournisseurs, ni
`agendas.py`/`deliberation.py`/`planification.py`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par
`QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (décision 2, L8), `docs/contrat-mj.md`, puis les règles `deplacer`/`prelever` de
`consignes.INTERPRETATION` (« poser (destination = salle.id) ») et leur validation dans le moteur.

## L'invariant (décision de l'utilisateur, 2026-10-27)
**Poser un objet au sol se dit `destination: "sol"` et le pose sur la case de Corvus (ou la case libre la plus proche selon la
règle existante) ; le MJ n'a plus besoin de l'identifiant de la salle.** Même contrat pour toutes les voies qui posent
(`deplacer`, `prelever`, effets d'improvisation, séquences). Un `destination` égal à l'identifiant de la salle courante reste
accepté pendant ce lot (anciennes réponses, compatibilité), avec le même effet ; une autre salle reste refusée avec `attendu`
(« sol » ou un contenant ouvert à portée). Aucune règle propre à un objet ou un scénario. La consigne dit « sol ».

## Vérification
- Tests MJ simulé/console après rechargement : poser la torche « au sol » (case de Corvus, objet visible au bon endroit dans la
  scène et la carte), prélever une planche puis la poser, une séquence qui pose ; ancienne forme `salle.id` encore acceptée ;
  une autre salle refusée avec `attendu`.
- Luna, **une passe** des bancs qui posent un objet (cherche-les dans `tests/data/bancs/`, au moins `atelier` et `relais`) ;
  référence `cdaf371` relue du cache ; appels par tour, aucun refus de destination.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-poser-au-sol` poussée (pas `main`).
`docs/contrat-mj.md` si la règle y figure, `docs/plan-prompt.md` (L8 fait), `docs/etat-dev.md` (« Branche
`codex-poser-au-sol`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-154-poser-au-sol.md`.
