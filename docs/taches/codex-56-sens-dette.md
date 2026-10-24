# Tâche Codex 56 : qui doit à qui, dit tel que le moteur l'établit

Branche `codex-sens-dette` (elle porte ce fichier, issue de l'intégration **f033364** : lots 38 à 54 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant,
vérification minimale, rapport d'une page. **Luna disponible sur ce poste** (copies seulement ;
`tools/banc_multi.py --connexion chatgpt`).

Lots en même temps sur l'autre poste : 52 (`planification.py`), 55 (`social.py` : `bavarder`, `recevoir`). Ne touche
ni `planification.py` ni ces fonctions de `social.py`.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `echanges-suite` (le joueur réclame, comptes sur sa fiche),
`codex-ressource` lot 50, `codex-audience` lot 47 b), `docs/contrat-mj.md`, puis `donjon/biens.py` (`comptes_joueur`,
`regler`, dettes), `donjon/echanges.py` (traitement de `reclamer`), `donjon/paroles.py` (le contenu `reclamer`,
`SENS_CONTENU`), `donjon/mj.py` (ce que reçoit le narrateur de l'issue : `conversation_validee`). Bruts :
`C:\Users\msics\donjon\tmp-worktrees\codex-ressource\artifacts\luna50-relecture.txt` (banc `ressources`, fin).

## Le constat (passe Luna du lot 50, banc `ressources`)
« Aubin, tu me dois quelque chose ? » est typé `reclamer` sans sujet ; Aubin répond « Non, **tu ne me dois rien**. » :
la réponse dit l'inverse de la question (si Corvus doit à Aubin, et non si Aubin doit à Corvus). Le joueur lit une
affirmation sur les comptes dont le sens n'est pas celui que le moteur a tranché.

## L'invariant
**Une affirmation sur une dette, un prêt ou une créance dite au joueur porte le sens établi par le moteur : qui doit,
à qui, quoi.** Le moteur donne au narrateur l'issue avec ses rôles explicites (débiteur, créancier, objet ou pièces,
ou « rien dans ce sens »), et la réponse qui en inverse le sens est refusée avant affichage, avec un `attendu` qui
cite l'issue. Trouve d'abord si la cause est le typage (une question de comptes typée comme une réclamation), l'issue
transmise (sans direction), ou le récit ; corrige la règle commune, pas la phrase d'Aubin. La même règle vaut pour un
prêt échu, une part payée due, une créance réclamée par un PNJ au joueur.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : le cas réel (Aubin ne doit rien à Corvus : réponse dans le
  bon sens) ; un cas où Aubin doit deux pièces (il les rend, ou refuse, dit dans le bon sens) ; un cas où c'est Corvus
  qui doit (un prêt échu) ; une réponse inversée refusée avec `attendu`.
- Luna, **une passe** : `ressources`, `comptes` (`tests/data/bancs/comptes.json`), référence `main` lue du cache ;
  appels par tour, textes affichés pour chaque question de comptes.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` (comptes et sens), `docs/etat-dev.md` (« Branche
`codex-sens-dette`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-56-sens-dette.md`.
