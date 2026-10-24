# Tâche Codex 61 : « devant », « derrière », « à ta gauche » se disent selon où Corvus regarde maintenant

Branche `codex-orientation` (elle porte ce fichier, issue de l'intégration **c592d68**), worktree dans `tmp-worktrees/`.
**Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). **Luna disponible sur ce poste** (copies seulement ;
`tools/banc_multi.py --connexion chatgpt`).

Lots en même temps sur l'autre poste : 58 (`planification.py`), 60 (`appel.py`). Les lots 56, 57 et 59 (comptes,
offres, parole sans contenu : `mj.py`, `narration.py`) arrivent dans l'intégration pendant ton lot : fais
`git merge origin/integration` au début si elle a avancé, et garde tes changements compatibles avec leurs contrôles.

Lis `AGENTS.md`, `docs/etat-dev.md` (**« Vérification Luna de l'intégration f033364 », défauts (3) et (4)** ; entrées
`codex-luna-restes` (positions en mètres), `codex-absence-vue` lot 40, `banc-luna` (souvenirs visuels `vu_a`,
`hors_de_vue`)), `docs/contrat-mj.md`, puis `donjon/narration.py` (l'auditeur, `souvenirs_visuels`), `donjon/mj.py` (ce
que reçoit le narrateur de la position et de l'orientation de Corvus), le contrôle déterministe des unités et repères
en mètres. Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-f033364\relecture.txt` (lignes ~750 et 1052,
`luna-restes-ambiance` n° 3 ; ~586 et 888, `relais` n° 22).

## Le constat (vérification Luna d'intégration f033364)
1. **Orientation fausse admise** : après « tourner ouest », « où est la poutre effondrée ? » reçoit « La poutre effondrée
   se trouve à environ un mètre vers l'est de toi, **devant toi**. » ; l'auditeur l'admet d'après un souvenir visuel
   pris en regardant vers l'est. La passe 1 et `main` disaient bien qu'elle est derrière ou hors de vue.
2. **Méta-langage** (relais n° 22, passe 2) : « Le refus précédent ne signifie pas qu'il y en a un ici : aucun objet de
   ce nom n'est actuellement à ta portée… » : le joueur lit un commentaire sur le fonctionnement du jeu.

## L'invariant (le premier ; le second seulement s'il tient dans la même règle)
**Une direction relative au joueur (devant, derrière, à gauche, à droite, dans ton dos) se juge sur son orientation
actuelle et la position actuelle de la chose**, jamais sur l'orientation qu'il avait quand il l'a vue : le moteur
fournit au narrateur, pour chaque objet ou souvenir, sa direction relative actuelle (ou « hors de vue, derrière »), et
une direction relative contraire est refusée de façon déterministe, avec un `attendu`. Pas de cas de la poutre. Si le
méta-langage (« le refus précédent… ») se règle par la règle existante de voix d'auteur (`REGLE_NARRATION`, contrôle
des mots « refus », « moteur »), étends-la ; sinon, signale-le seulement.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : le cas réel (tourner ouest, poutre à l'est : « derrière
  toi » accepté, « devant toi » refusé) ; un autre de même nature (un personnage vu de face puis dans le dos) ; une
  direction absolue (« vers l'est ») toujours acceptée.
- Luna, **une passe** : `luna-restes-ambiance`, `relais`, `atelier`, référence `main` lue du cache ; textes affichés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche
`codex-orientation`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-61-orientation.md`.
