# Tâche Codex 59 : une parole du joueur sans contenu typé ne laisse ni inventer ni refuser à tort

Branche `codex-contenu-vide` (elle porte ce fichier, issue de l'intégration **c592d68** : lots 38 à 55 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). **Luna disponible sur ce
poste** (copies seulement ; `tools/banc_multi.py --connexion chatgpt`).

Lots en même temps sur l'autre poste : 57 (`pnj_propositions.py`, refus retenus), 58 (`planification.py`, eau). Le
lot 56 (comptes : `biens.py`, `mj.py`, `narration.py`, `paroles.py`) sera fusionné avant toi : repars de
l'intégration à jour si elle a avancé (`git merge origin/integration` dans ta branche au début), et garde tes
changements compatibles avec le contrôle des comptes du lot 56.

Lis `AGENTS.md`, `docs/etat-dev.md` (**« Vérification Luna de l'intégration f033364 », défauts (1) et (2)** ; entrées
`codex-audience` 47 b, `codex-ressource` 50, `codex-sens-dette` 56), `docs/contrat-mj.md`, puis `donjon/paroles.py`
(`TYPES`, contenu `propos`, `verifier_contenus`), `donjon/mj.py` (typage `parole_joueur` contre `conversation_pnj`,
la boucle de correction et le message « Précise ce que tu veux dire »), `donjon/narration.py` (l'auditeur : missions,
primes), `donjon/couverture_action.py` (`contenu_conforme`). Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-f033364\relecture.txt`
(lignes ~128/382 pour `main`, 636/938 pour l'intégration : crypte n° 24 ; 706/1008 `echanges` n° 2 ; 784/1086
`soir-noir` n° 1) et les fils dans `onze-20261024-230639-36200\`.

## Le constat (vérification Luna d'intégration f033364, deux passes)
1. **Prime inventée** : crypte n° 24, « Gorm, combien me donnes-tu pour l'anneau ? ». Sur `main`, Luna typait
   `conversation_pnj` / `proposer` / `anneau_veilleur` et Gorm disait « Vingt pièces » (la `prime_base` du scénario)
   2/2. Sur l'intégration, Luna type `parole_joueur` avec un `propos` vide ; Gorm répond « Ça dépendra… » (passe 1)
   puis « Je te donnerai 10 pièces d'or si tu me rapportes l'anneau » (passe 2), et l'auditeur l'admet « même si le
   montant n'est pas établi ». Une mission et sa prime sont mécaniques.
2. **Faux refus affiché** « Précise ce que tu veux dire : les mots ou le contenu proposés ne correspondent pas à ta
   demande. » : `soir-noir` n° 1 « il y a quelqu'un ? » (passe 1 ; passe 2 : 6 appels), `echanges` n° 2 « « Tu sais où
   est passé le gardien ? » » (passe 2). La contre-revue refuse un `propos` vide, puis un `ressource` « présence ».

## L'invariant
**Une parole du joueur dont le contenu ne se type pas reste une parole valable sans contenu mécanique** : elle ne
reçoit aucune réponse mécanique inventée (une prime, une mission, une possession ne s'affirme que depuis l'état ou un
contenu typé que le moteur a tranché, sinon l'auditeur la refuse), et elle n'est jamais refusée au joueur pour son
seul manque de contenu (« Précise ce que tu veux dire » ne s'affiche que si les mots eux-mêmes sont inexploitables).
Trouve pourquoi le typage a basculé de `conversation_pnj` à `parole_joueur` (lots 47 b ou 50 : la décision d'audience
unique, le dossier réduit de la contre-revue) et corrige la règle commune, pas la phrase de l'anneau ni la question du
gardien.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : la prime (Gorm donne la `prime_base`, ou dit ne pas
  pouvoir dire, jamais un autre montant) ; une autre question sur un fait mécanique (une mission ou un prix à
  l'auberge) ; « il y a quelqu'un ? » et la question du gardien sans « Précise… ».
- Luna, **une passe** : `crypte`, `soir-noir`, `echanges`, `noms-dialogue`, référence `main` lue du cache (voir la
  méthode de `verif-luna-f033364` pour le lanceur) ; textes affichés de ces saisies.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche
`codex-contenu-vide`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-59-contenu-vide.md`.
