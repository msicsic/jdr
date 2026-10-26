# Tâche Codex 142 (MJ) : une déclaration erronée non confirmée ne bloque pas la parole corrigée (N9)

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`,
copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche la voie de la parole dans `mj.py`
(`proposer`, `_verifier_fidelite_parole`, obligations d'opérations) et `paroles.py` si besoin ; **pas** `narration.py` ni
`consignes.py` (lot 143), ni `corps.py`, `vecu.py`, `deliberation.py`, `tenir.py` (lot 140). Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 100 et 104 (N3 : opérations du contenu rejeté et omissions
reconnues), 128 et 138, puis le rapport du lot 141 (N9) et son fil dans `C:\Users\msics\donjon\artifacts\verif-luna-9a39738\`.

## Le défaut (N9, vérification Luna 9a39738, lot 141)
`soir-noir` p1 n°2, « Qui est là ? » : la première proposition déclare `nom=true` avec une réplique inventée (« Corvus. Qui
es-tu ? »), refusée ; la seconde déclare `qui=true` avec les mots exacts, correcte. Le joueur lit pourtant « Tu n'as encore
rien dit : précise ce que tu veux demander… » et rien n'est prononcé. Cause probable : l'opération `nom` de la proposition
refusée est mémorisée comme obligation et imposée à la correction et au secours. La passe 2 exécute la même saisie sans cette
première erreur.

## L'invariant
**Une opération déclarée seulement par une proposition refusée, et non confirmée par la revue ni par la saisie, n'est pas une
obligation pour la correction.** Le lot 104 avait posé ce contrat pour le contenu rejeté ; établis d'abord dans le fil quelle
voie le contourne ici (déclaration `operations_demandees` du lot 128, préparation échouée, secours). Corrige le contrat commun :
les obligations ne naissent que d'une analyse confirmée (revue, saisie sans ambiguïté), et une correction qui déclare
d'autres opérations est jugée sur elles. Ne relâche pas la conservation d'une opération réellement reconnue (lots 82, 91, 104).
Aucun mot-clé, aucune règle propre à « Qui est là ? ».

## Vérification
- Tests MJ simulé/console après rechargement : le cas réel (correction `qui` exécutée), un autre cas de même nature (première
  proposition avec une opération fausse, correction juste, autre script), et une opération réellement reconnue qui reste exigée
  (achat omis dans la correction : toujours refusé).
- Luna, **une passe** : `soir-noir`, `soir-voix`, `noms-dialogue`, référence `9a39738` lue du cache (lot 141) ; appels par tour,
  plus de « Tu n'as encore rien dit » après une correction juste.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-correction-parole` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/etat-dev.md` (« Branche `codex-correction-parole`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-142-correction-parole.md`.
