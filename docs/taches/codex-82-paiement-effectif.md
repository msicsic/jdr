# Tâche Codex 82 : une saisie qui paie ou achète ne se réduit pas à des mots

Branche `codex-paiement-effectif` (elle porte ce fichier, issue de l'intégration **3ffd72d** : lots 38 à 80 et les rapports
76 et 79), worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes**. **Luna disponible** (copies seulement ;
`tools/banc_multi.py --connexion chatgpt`). Un seul poste : priorité réduite, au plus 3 processus, Luna en 4 exécutions au
plus ; le lot 81 (`planification.py`) tourne en même temps.

Ce lot touche `donjon/mj.py` (contre-revue de fidélité), `donjon/couverture_action.py`, `donjon/paroles.py` (contenus
d'échange : `proposition`, achat) ; pas `planification.py`.

Lis `AGENTS.md`, le **rapport du lot 79** (`docs/taches/rapport-codex-79-verif-luna.md`, défaut **N1** et le constat 2) et
celui du lot 78 (pièce d'un lot), `docs/etat-dev.md` (entrées `codex-propositions` 29, `codex-comptes-issue` 73,
`codex-piece-de-lot` 78, `codex-contenu-vide` 59), `docs/contrat-mj.md`. Bruts :
`C:\Users\msics\donjon\artifacts\verif-luna-882907c\` (`constats.md`, `soir-appel` passe 2 n° 5).

## Le constat (vérification Luna 882907c)
`soir-appel` p2 n° 5, « je paie Aubin trois pièces pour une de ses planches » : Luna type un contenu `propos` sans
opération ; la contre-revue le déclare **conforme** ; le récit « Il ne confirme pas l'échange ; les planches restent à
lui » est ensuite refusé, la demande abandonnée. Or inchangé (26), aucune planche portée. Ce n'est pas un refus de vente
calculé par le moteur : **l'effet demandé par le joueur s'est perdu entre la saisie et le contenu**. En passe 1, l'achat
passe (or 26 → 23, la planche portée).

## L'invariant
**Une saisie qui demande un échange (payer, acheter, offrir contre) ne peut être couverte que par un contenu qui porte cet
échange** (`proposition` ou l'achat typé, avec ce qui est demandé et la contrepartie) ; un `propos` sans opération ne la
couvre pas, et la contre-revue le refuse avec un `attendu` qui nomme la forme attendue. Le moteur tranche ensuite (vente
acceptée, refusée, contre-offre du lot 77). Une règle commune de couverture (« ce que la saisie demande de faire doit se
retrouver dans le contenu »), pas une liste de verbes : lis-la dans l'analyse commune de la parole, avec un test sur une
autre formulation.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : le cas réel (`propos` refusé, puis l'achat typé exécuté : or et
  planche après recharge) ; une autre formulation (« je t'offre deux pièces pour une part de soupe ») ; une simple parole
  sans échange toujours couverte par `propos`.
- Luna, **une passe** : `soir-appel`, `ressources`, `noms-dialogue`, référence 882907c lue du cache ; achat exécuté dans la
  passe, textes affichés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-paiement-effectif`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-82-paiement-effectif.md`.
