# Tâche Codex 432 : un refus du rendu porte toujours son `attendu`

Défaut séparé relevé par le diagnostic 430 (`docs/taches/rapport-codex-430-creation-utile-luna.md`, ligne R58 ; bruts
`C:\Users\msics\donjon\artifacts\creation-utile-430\`, `preuves.md` et `refus.json`, PC fixe). Dans le fil du lot 423
(branche, tour 4), un enrichissement des mains de `personne_1` est préparé, puis `narration.attestations` appelle
`rendu.decrire`, qui lève « Cet objet n'est pas visible » **avec un `attendu` vide**. La proposition ne peut pas être
corrigée par le MJ, et ce refus masque la vraie cause (une proposition hors sujet). Le 430 a reproduit cette exception
sur copie.

Lis `AGENTS.md` (« Tout refus `ErreurMonde` qu'une proposition du MJ peut déclencher porte un `attendu` »),
`docs/etat-dev.md` (court), `donjon/refus.py` et le rapport 430.

## Invariant (un seul)
**Tout refus qu'une proposition du MJ peut déclencher, y compris ceux levés pendant les attestations et le rendu
(`narration.attestations`, `rendu.decrire`), porte un `attendu` : champ fautif, valeur reçue et ce qui serait accepté, en
identifiants publics.** Une seule cause par refus. Établis la cause du cas R58 (pourquoi le rendu décrit une entité non
visible : enrichissement d'une partie d'un personnage hors de vue, ou désignation résolue vers une mauvaise entité ?).
Corrige le contrat commun : soit la préparation refuse en amont avec son `attendu`, soit le refus du rendu le porte.
Aucune exception d'objet ni de personnage. Le contrôle de non-fuite reste entier : l'`attendu` ne nomme que ce que
Corvus perçoit ou connaît.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/rendu.py`, `donjon/narration.py`, `donjon/refus.py`, tests. Lots
en cours : 402 (calcul), 419, 429 (K1), 431 (admission préalable, `portee_narrative`, `mj.py`) : évite `mj.py` si
possible. Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite.

## Vérification
Cas réel R58 rejoué sur copie avec MJ simulé (refus avec `attendu` non vide, puis correction acceptée), et un autre cas
de même nature (un autre élément d'un personnage ou d'un objet hors de vue). Contrôle que chaque `ErreurMonde` levée sur
la voie attestations/rendu par une proposition porte un `attendu` (test qui parcourt ces refus). État et vue après
recharge. Tests voisins verts (rendu, narration, refus, audits d'attendu). Pas de suite complète, ni Luna.

## Livraison
Branche `codex-refus-rendu-attendu`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-432-refus-rendu-attendu.md` ;
entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents
graves). Bruts dans `C:\Users\msics\donjon\artifacts\refus-rendu-432\`. Termine par `LOT TERMINÉ`,
`CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
