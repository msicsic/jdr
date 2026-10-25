# Tâche Codex 89 : la revue de fidélité ne refuse pas une parole pour ce qui relève de la décision d'audience

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 3 processus, Luna en 4
exécutions au plus ; les lots 87 (`deliberation.py`, `planification.py`) et 88 (`social.py`, `esprits.py`) tournent en même
temps. Ce lot touche `donjon/mj.py` (contre-revue de fidélité de la parole) et `donjon/couverture_action.py` ; pas ces
fichiers-là. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur** : le temps avant la réponse au joueur. Chaque faux refus coûte un appel de 4 à 6 s. Le critère
de ce lot est le nombre d'appels et de relances par tour, sans perte de contrôle.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-audience` 47 b (une seule décision d'audience, celle de
`paroles.destinataires` ; le dossier de la revue réduit à `replique`, `contenu`, `sens_contenu`), `codex-ressource` 50,
`codex-paiement-effectif` 82, `codex-part-proposee` 84), les rapports des lots 82, 84 et 79
(`docs/taches/rapport-codex-82-paiement-effectif.md`, `rapport-codex-84-part-proposee.md`, `rapport-codex-79-verif-luna.md`),
`docs/contrat-mj.md`, puis `donjon/mj.py` (`_verifier_fidelite_parole`), `donjon/couverture_action.py` (`contenu_conforme`).
Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-882907c\` et les fils des lots 82 et 84
(`tmp-worktrees/codex-paiement-effectif/artifacts/`, `tmp-worktrees/codex-part-proposee/artifacts/`).

## Le constat
Les lots 82 et 84 relèvent des **faux refus de fidélité** : « est-ce que quelqu'un a du bois ? », dite à Aubin (celui d'en
face, règle du lot 47 b), est refusée deux fois parce que la revue oppose « quelqu'un » à l'audience fixée ; la demande
d'une planche est d'abord rejetée avant d'être corrigée en proposition (soir-appel : 4 → 5,6 appels/tour au lot 84).

## D'abord, mesurer
Dans les fils de 882907c et des lots 82 et 84 : chaque refus de la revue de fidélité, son motif, et s'il était justifié
(les mots du joueur contredits) ou non (audience, pronom indéfini, forme du contenu déjà validée par le moteur). Chiffre les
familles.

## L'invariant
**La revue de fidélité juge seulement si les mots et le contenu typé disent ce que le joueur a dit ; l'adresse est décidée par
le moteur (`destinataires`) et n'est jamais un motif de refus**, y compris par les mots qui la portent (« quelqu'un », « vous »,
un vocatif) ; un contenu que le moteur a déjà validé n'est pas rejugé sur sa forme. Corrige la règle commune pour chaque famille
de faux refus mesurée ; les refus justifiés (mots contredits, contenu contraire) restent refusés.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : la question du bois à Aubin acceptée du premier coup ; la
  demande d'une planche acceptée comme proposition sans refus préalable ; une réplique qui contredit les mots du joueur toujours
  refusée.
- Luna, **une passe** : `soir-appel`, `noms-dialogue`, `ressources`, `echanges`, référence 882907c lue du cache ; appels et
  relances par tour, textes affichés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-fidelite-audience`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-89-fidelite-audience.md` (familles mesurées, règle, appels
par tour, limites).
