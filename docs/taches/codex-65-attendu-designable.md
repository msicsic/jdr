# Tâche Codex 65 : un `attendu` ne cite que ce que Corvus peut désigner

Branche `codex-attendu-designable` (elle porte ce fichier, issue de l'intégration **de3e986**), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). **Luna disponible sur ce poste**
(copies seulement ; `tools/banc_multi.py --connexion chatgpt`). Les lots 60 et 61 entrent dans l'intégration pendant
ton lot : `git merge origin/integration` au début si elle a avancé.

Lots en même temps sur l'autre poste : 63 (`planification.py`), 64 (`social.py`). Ne touche pas à ces fichiers.

Lis `AGENTS.md` (« Contrat du MJ » : absence de fuite d'entités non perçues ; refus et `attendu`), `docs/etat-dev.md`
(« Vérification Luna de l'intégration f033364 », défauts connus : « l'`attendu` d'une cible inconnue liste des
identifiants hors de la salle » ; entrée `banc-luna` : `Monde.designable`), `docs/contrat-mj.md` (« Ce que le MJ reçoit
d'un refus »), puis `donjon/refus.py`, `donjon/monde.py` (`designable`), et les refus d'une cible inconnue dans
`donjon/moteur.py` et `donjon/commandes.py`. Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-f033364\` (fils de
`relais` n° 22, « je prends le pied-de-biche », Corvus dans la conduite ; même chose sur `main`).

## Le constat
Quand le MJ propose un geste sur une cible que Corvus ne connaît pas (« je prends le pied-de-biche » depuis la
conduite), le refus porte un `attendu` qui liste comme cibles valables des **identifiants bruts de personnages et
d'objets hors de la salle** (`brune`, `marchand`, des objets de l'échoppe). L'`attendu` ne va qu'au MJ, mais il donne à
Luna des entités que Corvus ne perçoit pas et ne peut pas désigner : une fuite vers la narration, contraire au contrat.

## L'invariant
**Tout `attendu` qui énumère ce qui serait accepté ne cite que des entités que Corvus peut désigner** (`Monde.designable`
: perçues, ou souvenirs visuels marqués, ou personnes connues au sens des noms), sous la référence que le MJ reçoit
déjà pour elles (projection publique, `personne_<n>`, `objet:<id>` des seules entités désignables) ; rien d'autre, et
quand rien n'est désignable, il le dit (« aucune cible de ce nom n'est désignable ici »). Une seule fonction qui construit
ces listes pour tous les refus de cible. Contrôle : un test qui parcourt les refus de cible possibles et vérifie
qu'aucun identifiant non désignable n'apparaît.

## Vérification (minimale)
- Tests après rechargement : le cas réel (conduite, pied-de-biche absent : `attendu` sans `brune` ni objets de
  l'échoppe) ; un autre de même nature (une personne inconnue nommée dans le noir) ; un cas où des cibles désignables
  existent : elles sont listées sous leur référence publique.
- Luna, **une passe** : `relais`, `crypte`, `echanges`, référence `main` lue du cache ; appels par tour, `attendu`
  relevés dans les fils.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche
`codex-attendu-designable`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-65-attendu-designable.md`.
