# Tâche Codex 128 (MJ) : qu'un avis dit librement soit typé `avis`

Suite du lot 124, **sur sa branche** (`codex-avis-joueur`, 20cd5cf) : nouvelle branche `codex-avis-typage` issue d'elle.
Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`,
copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche le MJ (`mj.py`, `consignes.py`,
schémas, `paroles.py` pour le sens partagé) ; **pas** `combat.py`, `defense.py`, `corps.py`, `pnj.py`, `moteur.py` (lot 126),
ni `tools/` (lot 127). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, le **rapport du lot 124** (`docs/taches/rapport-codex-124-avis-joueur.md`, sur la branche de base), les
rapports des lots 82, 91 et 104 (opérations déclarées par l'interprétation, couverture, raccourci des mots exacts), puis
`donjon/mj.py` (`_verifier_fidelite_parole`, déclaration des opérations), `donjon/paroles.py` (`SENS_CONTENU`, carte des
opérations), `donjon/consignes.py`, et le fil Luna du lot 124 (`artifacts/avis-joueur-124/`).

## Le défaut
Le contrat `avis` existe côté moteur (lot 124), mais Luna a typé **0/3** avis du joueur : trois `propos`, déclarés
« sans opération », donc dispensés de revue par le raccourci des mots exacts (lot 91). L'omission d'une opération que
le moteur sait exécuter passe ainsi sans contrôle ; c'est la limite déjà notée au lot 91 (« une omission initiale peut
encore échapper au contrôle local »), révélée ici par un nouveau contenu.

## L'invariant
**Une parole du joueur qui porte une opération que le moteur sait exécuter n'est pas reçue comme simple `propos`.**
Commence par établir la cause dans le fil (description de l'opération `avis` dans le schéma et le sens partagé, ordre
ou formulation des opérations déclarées, consigne d'interprétation, raccourci de revue). Corrige le **contrat commun** :
définitions partagées des opérations et de leur reconnaissance, et/ou condition du raccourci des mots exacts, de sorte
que toute opération exécutable (pas seulement `avis`) soit soit déclarée, soit vérifiée. Aucun mot-clé, aucune règle
propre à l'eau ou aux lieux, aucune consigne qui cite un exemple. Mesure le coût : appels par tour avant/après sur les
scripts touchés.

## Vérification
- Tests MJ simulé/console après rechargement : l'avis dit librement typé `avis` et reçu (lot 124) ; un `propos` sans
  opération reste dispensé de revue ; un autre type d'opération (achat ou réclamation) n'est pas dégradé.
- Luna, **une passe** : `bancs/avis-joueur.json` (trois saisies du lot 124) et deux scripts historiques qui exercent le
  raccourci (`noms-dialogue`, `soir-appel`), référence lue du cache si présente ; typage `avis` attendu au moins 2/3,
  appels par tour, aucun faux refus affiché.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`). Les deux échecs MiMo de comptage d'appels reproduits
  sur la base au lot 124 sont à examiner : s'ils dépendent de `jsonschema` installé sur ce poste, dis-le.

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-avis-typage` poussée (pas `main`).
`docs/contrat-mj.md`, `docs/etat-dev.md` (entrée « Branche `codex-avis-typage`, non fusionnée », lots 124 + 128 ensemble).
Rapport d'une page : `docs/taches/rapport-codex-128-avis-typage.md`.
