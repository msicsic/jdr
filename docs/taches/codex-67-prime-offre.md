# Tâche Codex 67 : une offre de prime n'est pas une dette, et sa condition se juge sur l'état

Branche `codex-prime-offre` (elle porte ce fichier, issue de l'intégration **d78cfcc**), worktree dans `tmp-worktrees/`.
**Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). **Luna disponible sur ce poste** (copies seulement ;
`tools/banc_multi.py --connexion chatgpt`). Les lots 64 et 65 entrent dans l'intégration pendant ton lot :
`git merge origin/integration` au début si elle a avancé.

Lots en même temps sur l'autre poste : 66 (`planification.py`), 68 (`signes.py`). Ne touche pas à ces fichiers.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-contenu-vide` lot 59 (la prime de l'anneau : 20 pièces du moteur),
`codex-sens-dette` lot 56 (comptes et rôles), `codex-attendu-designable` lot 65 (son rapport : « un repli en crypte sur la
prime : faux refus sémantique de la condition de remise, puis confusion entre offre et dette due »)), `docs/contrat-mj.md`,
puis `donjon/mj.py` (conversation de mission, `conversation_validee`), `donjon/narration.py` (contrôle des comptes du lot
56, `portee_mecanique` du lot 59), `donjon/biens.py` (`compte`), la mission et `prime_base` du scénario de la crypte.
Bruts : le worktree du lot 65 (`tmp-worktrees/codex-attendu-designable/artifacts/bancs-multi/`, banc `crypte`, la prime)
et `C:\Users\msics\donjon\artifacts\verif-luna-f033364\`.

## Le constat
Crypte, « Gorm, combien me donnes-tu pour l'anneau ? » : le lot 59 a rétabli les 20 pièces du moteur, mais la passe Luna
du lot 65 finit en **repli** : la contre-revue refuse à tort la condition de remise (« si tu me rapportes l'anneau »),
puis le contrôle des comptes (lot 56) lit l'offre de prime comme une **dette due**. Deux contrôles se contredisent sur
une promesse conditionnelle.

## L'invariant
**Une offre conditionnelle (une prime promise contre une remise future) n'est ni une dette due ni une invention** : le
moteur la donne au narrateur comme offre, avec sa condition et son montant tirés de l'état (mission, `prime_base`) ; le
contrôle des comptes ne la compte pas comme dette tant que la condition n'est pas remplie ; l'auditeur admet la condition
qui recopie celle de l'état. Une seule représentation de l'offre pour la mission, les propositions (lot 29) et les comptes.
Pas de cas de l'anneau ni de Gorm.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : le cas réel (prime de l'anneau dite avec sa condition, sans
  refus ni repli, aucune dette inscrite) ; la remise de l'anneau (la prime devient due puis payée, dans le bon sens) ; une
  autre offre conditionnelle (une proposition du joueur à contrepartie différée).
- Luna, **une passe** : `crypte`, `ressources`, `comptes` (préparé avec ses noms connus, comme `ressources` au lot 50),
  référence `main` lue du cache ; textes affichés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-prime-offre`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-67-prime-offre.md`.
