# Tâche Codex 173 (MJ) : désigner la surface du sol, c'est poser au sol

Petit lot issu de la vérification Luna `227c496` (lot 165, L8 partiel : `poser-sol-atelier`/`poser-sol-relais` p1, destination
`cour_sol` / `antichambre_sol` refusée puis corrigée en `sol`). Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le laptop**
(`C:\Users\msics\donjon`, Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal,
`AGENTS.md`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (172, contre-revue des
gestes de force) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche la résolution des
destinations de dépôt (`operations.py`, `deplacement_objet.py`) et leurs tests ; **pas** `couverture_action.py`, `tenir.py`,
`consignes.py` au-delà d'une phrase (lot 172), `narration.py`, `mj.py`. **Bruts dans `C:\Users\msics\donjon\artifacts\sol-173\`,
jamais dans le worktree.** Si une revue automatique bloque Luna ou la poussée, termine le reste, commite localement et écris la
commande exacte dans `C:\Users\msics\donjon\artifacts\sol-173\luna-a-jouer.txt`. Termine ton dernier message par `LOT TERMINÉ`
(résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 154 (L8 : `destination: "sol"`, titre « au sol, à tes pieds ») et 165,
puis `operations.compiler` (résolution de `sol`) et les surfaces génériques de salle (objets de type `surface`, nom `sol`).

## L'invariant
**Une destination de dépôt qui désigne la surface du sol de la salle de Corvus (objet `surface` dont le nom est « sol », perçu)
a le même effet que `destination: "sol"` : l'objet est posé sur la case de Corvus ; la surface d'une autre salle, un mur ou un
plafond restent refusés avec `attendu` (« sol » ou un contenant ouvert à portée).** Règle commune fondée sur le type et le nom de
la surface, pas sur un identifiant de salle ; mêmes voies que le lot 154 (`deplacer`, `prelever`, séquences, improvisation).

## Vérification
- Tests MJ simulé/console après rechargement : `antichambre_sol` et `cour_sol` acceptés comme le sol (objet sur la case de Corvus,
  visible au bon endroit après recharge) ; mur et sol d'une autre salle refusés avec `attendu`.
- Luna, **deux passes** de `poser-sol-atelier`, `poser-sol-relais` ; une passe de `atelier` ; critère : aucun refus de destination.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-sol-surface` poussée (pas `main`). `docs/contrat-mj.md` si
la règle change, `docs/etat-dev.md` (« Branche `codex-sol-surface`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-173-sol-surface.md`.
