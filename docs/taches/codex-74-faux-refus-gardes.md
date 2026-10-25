# Tâche Codex 74 : les gardes déterministes du récit ne refusent pas une phrase juste

Branche `codex-gardes-justes` (elle porte ce fichier, issue de l'intégration **fbcf0ff**), worktree dans `tmp-worktrees/`.
**Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). **Luna disponible sur ce poste** (copies seulement ;
`tools/banc_multi.py --connexion chatgpt`). Un seul poste : priorité réduite, au plus 3 processus ; Luna en 4 exécutions
au plus. **À lancer après le lot 73** (mêmes fichiers du récit) ou en parallèle d'un lot de coût seulement ;
`git merge origin/integration` au début.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-orientation` 61 (locatifs relatifs, mot « refus » ajouté à la voix
d'auteur), `codex-absence-vue` 40, `relances-luna` (voix d'auteur), et la **vérification Luna fbcf0ff** :
`docs/taches/rapport-codex-70-verif-luna.md`, constats 5, 6, 7 et le méta-langage restant), `docs/contrat-mj.md`, puis
`donjon/narration.py` (`orientations`, voix d'auteur, contrôle des sources de lumière), `donjon/localisation.py`.
Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-fbcf0ff\` (`constats.md` points 2, 3, 4 ; `relecture.txt`).

## Le constat (vérification Luna fbcf0ff)
Les gardes déterministes ajoutées récemment refusent des phrases justes :
- **Mot ordinaire censuré** (`comptes` p2 n° 2) : « Elle maintient son refus des deux pièces qu'elle te doit » est refusé
  pour le seul mot « refus » (voix d'auteur, lot 61) : la phrase raconte une décision de Brune, pas une procédure.
- **Faux refus spatial** (`crypte` n° 26, deux passes) : « derrière toi », « à ta gauche » rejetés alors que l'`attendu`
  même cite `orientation_relative = ['derriere', 'gauche']` ; en passe 2, le locatif est rattaché à Gorm au lieu des
  crochets : liaison cible/segment ambiguë.
- **Lumière rejetée** (`crypte` p2 n° 25) : le brasero jugé non établi parce que hors de vue, alors que
  `perception.contributions` le donne à niveau 2 : la source visible et l'effet perçu sont confondus.
- **Méta-langage restant** (`relais` p2 n° 21) : « Le geste envisagé dépasse aussi ce que tu peux trancher sans examen plus
  précis ».

## L'invariant
**Une garde déterministe du récit ne refuse que ce qu'elle établit faux** : la voix d'auteur vise le vocabulaire du
fonctionnement du jeu (moteur, refus d'une proposition, audit, procédure), pas le même mot dans le monde raconté (un
personnage qui refuse) ; un locatif relatif n'est refusé que s'il porte sans ambiguïté sur une cible dont le repère
contredit le mot, et un repère cité comme admis dans l'`attendu` est toujours accepté ; une lumière perçue par sa
contribution (`perception.contributions`) est un fait établi même si sa source est hors de vue. Une règle par garde, pas de
liste de phrases. Si le méta-langage restant relève de la même garde de voix d'auteur, traite-le ; sinon, signale-le.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : chacun des trois cas réels accepté ; un vrai méta-langage
  (« le moteur refuse… ») toujours refusé ; un locatif relatif réellement faux toujours refusé ; une lumière sans
  contribution perçue toujours refusée.
- Luna, **une passe** : `crypte`, `comptes`, `relais`, `luna-restes-ambiance`, référence fbcf0ff lue du cache ; appels et
  relances par tour.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-gardes-justes`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-74-gardes-justes.md`.
