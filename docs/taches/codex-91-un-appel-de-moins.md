# Tâche Codex 91 : retirer l'appel de fidélité systématique ajouté par le lot 82, sans perdre le contrôle des opérations

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 3 processus, Luna en 4
exécutions au plus ; le lot 87 (`deliberation.py`, `planification.py`) tourne en même temps. Ce lot touche `donjon/mj.py`,
`donjon/couverture_action.py`, `donjon/paroles.py` (schéma de l'interprétation) ; pas ces fichiers-là. Termine ton dernier
message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur : le temps avant la réponse au joueur, donc le nombre d'appels par tour.**

Lis `AGENTS.md`, les rapports des lots 82 et 89 (`docs/taches/rapport-codex-82-paiement-effectif.md`,
`rapport-codex-89-fidelite-audience.md`, en particulier la section « Base d'intégration » et sa décomposition par fonction),
`docs/contrat-mj.md`, puis `donjon/mj.py` (`_verifier_fidelite_parole`, l'appel `auditer_action` pour une parole,
l'interprétation `repondre_au_joueur`), `donjon/couverture_action.py` (`operations_demandees`, `verifier`).

## Le constat (lot 89, deux passes, quatre scripts)
La revue de fidélité d'une parole (`auditer_action`) est passée de **0 à environ 1 appel par tour de parole** avec le lot 82
(commit `3510d00`), qui a supprimé ses retours anticipés (adresse explicite, mots exacts) pour toujours relever les opérations
demandées par la saisie : `echanges` 3,00 → 4,33 appels/tour, `ressources` 3,67 → 4,83, sans relance. Le contrôle visé par le
lot 82 est juste (une saisie qui paie ou achète ne doit pas être couverte par une simple parole), mais il coûte un appel de 4
à 6 s à **chaque** parole, y compris « bonsoir » ou « Ilse, tu m'entends ? ».

## L'invariant
**Les opérations qu'une saisie demande sont déclarées par l'interprétation elle-même, dans le même appel**
(`repondre_au_joueur` porte un champ typé des opérations demandées par la saisie, avec la même définition commune que la revue,
`SENS_CONTENU`) ; le moteur vérifie de façon déterministe que le contenu proposé les couvre (règle du lot 82, inchangée) ; **la
revue de fidélité n'est appelée que lorsqu'elle peut changer l'issue** : contenu typé qui dépasse les mots exacts du joueur, ou
désaccord entre les opérations déclarées et le contenu. Une parole aux mots exacts, sans opération déclarée ni contenu typé,
part sans revue. Pas de liste de mots ni de verbes.

## Vérification
- Tests après rechargement, chaîne complète avec MJ simulé : « bonsoir » et « Ilse, tu m'entends ? » sans revue ; « je paie
  Aubin trois pièces pour une planche » : opération déclarée, contenu exigé, achat exécuté ; une interprétation qui déclare
  l'achat mais propose une parole sans opération : refusée sans appel de revue ; un contenu typé qui reformule : revue appelée.
- Luna, **deux passes** des quatre scripts (soir-appel, noms-dialogue, ressources, echanges) et des quatre bancs de référence
  (relais, crypte, atelier, echanges), comparées à l'intégration **ef86ff1** jouée dans les mêmes conditions (deux passes,
  rangée dans le cache) : **appels par tour par fonction**, relances, refus, replis, secondes par tour ; achats exécutés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-un-appel-de-moins`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-91-un-appel-de-moins.md`.
