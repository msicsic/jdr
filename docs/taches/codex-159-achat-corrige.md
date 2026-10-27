# Tâche Codex 159 (MJ) : la correction d'un achat ne perd pas l'intention (N11)

Petit lot de correction issu de la vérification Luna `cdaf371` (lot 153). Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le
laptop** (`C:\Users\msics\donjon`, Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (lot 158, assemblage du schéma
d'interprétation dans `mj._echanger`) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot
touche la voie de la parole de `mj.py` (préparation et correction des échanges), `paroles.py`/`echanges.py` (validation des
contreparties) et leurs tests ; **pas** l'assemblage du schéma ni des requêtes (lot 158), ni `sources.py`, les fournisseurs,
`consignes.py`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 78 (pièce de lot), 82 (paiement effectif), 142 (N9) et 153 (N11),
puis le fil `soir-appel` p1 n°5 dans `C:\Users\msics\donjon\artifacts\verif-luna-cdaf371\` (copié du PC fixe si absent :
demande-le par `QUESTION` plutôt que de rejouer).

## Le défaut (N11, lot 153)
`soir-appel` p1 n°5, « je paie Aubin trois pièces pour une de ses planches » : la contrepartie `pieces` porte
`objet=planches` ; refus précis demandant un objet à pièces ; la correction `objet=planches de bac` est encore invalide, puis
« Corvus cherche ses mots… ». Aucune parole d'achat, aucune planche. P2 retire ce champ et réussit.

## L'invariant
**La correction d'un échange respecte le contrat typé que le refus lui a donné (`attendu` exact et exploitable : quel champ,
quelle valeur reçue, ce qui serait accepté) ; une intention exprimable (payer N pièces pour une part d'un lot à portée) n'est
pas perdue faute d'une correction réussie.** Établis d'abord dans le fil la cause : `attendu` ambigu, champ mal défini dans le
schéma ou le sens commun, validation trop stricte pour une contrepartie en pièces. Corrige le contrat commun (définition du
champ, `attendu`, validation), sans mot-clé ni règle propre aux planches ou à Aubin.

## Vérification
- Tests MJ simulé/console après rechargement : le cas réel (achat exécuté, pièces payées, part portée), un autre achat de même
  nature (autre bien, autre vendeur), et une contrepartie réellement invalide toujours refusée avec `attendu`.
- Luna, **une passe** de `soir-appel`, `ressources`, `noms-dialogue` ; référence `cdaf371` relue du cache ; appels par tour,
  achat exécuté.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-achat-corrige` poussée (pas `main`). `docs/contrat-mj.md`
si la règle change, `docs/etat-dev.md` (« Branche `codex-achat-corrige`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-159-achat-corrige.md`.
