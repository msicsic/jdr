# Tâche Codex 156 (MJ) : un PNJ peut rappeler ce qu'il a déjà dit (N7)

Petit lot de correction issu de la vérification Luna `cdaf371` (lot 153). Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC
fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste, deux sur le laptop (lots 150 et 151
dans `mj.py`, `sources.py`, fournisseurs) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot
touche `narration.py` (dossier des paroles entendues, rappels, audit) et ses tests ; **pas** `mj.py`, `sources.py`, les
fournisseurs, `consignes.py`, `operations.py` (lot 154). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par
`QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 112 (redire le passé), 135 (rappel exact, N7), 141 et 153
(N7 persistant), puis le fil `soir-noir` p2 n°5 dans `C:\Users\msics\donjon\artifacts\verif-luna-cdaf371\`.

## Le défaut (N7, lot 153)
`soir-noir` p2 : au n°2 Ilse dit « Je suis Ilse » ; au n°5, « je demande à la voix comment elle s'appelle », la réplique
« Je t'ai déjà dit que je suis Ilse » est rejetée par l'audit, qui **inverse les révisions 2 et 5** ; puis le rappel disparaît
(six appels). Une parole entendue n'établit pas son contenu, mais établit qu'elle a été dite : la rappeler est permis.

## L'invariant
**Le dossier des paroles entendues donne un ordre sans ambiguïté (antériorité par rapport au tour courant, explicite) et un
rappel au discours rapporté d'une parole réellement dite par ce locuteur à cet auditeur est admis ; un rappel d'une parole
jamais dite reste refusé.** Établis d'abord dans le fil la cause exacte (numérotation des révisions, ordre du dossier,
projection, extraction des rappels du lot 112). Préfère une preuve déterministe quand la parole rappelée correspond à un
enregistrement (comme le rappel exact du lot 135), sinon un dossier qui rend l'ordre lisible ; aucune règle propre à un nom ni à
« déjà dit ».

## Vérification
- Tests console/MJ simulé après rechargement : le cas réel (rappel admis, parole et état sauvegardés), un autre rappel au
  discours rapporté d'une autre parole d'un autre PNJ, et un faux rappel (jamais dit) refusé.
- Luna, **une passe** de `soir-noir`, `soir-voix`, `noms-dialogue` ; référence `cdaf371` relue du cache ; appels par tour,
  rappel admis au n°5 quand le nom a été dit.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-rappel-ordre` poussée (pas `main`). `docs/contrat-mj.md`
si la règle change, `docs/etat-dev.md` (« Branche `codex-rappel-ordre`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-156-rappel-ordre.md`.
