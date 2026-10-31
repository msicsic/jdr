# Tâche Codex 429 : K1, éditeur de marché à deux termes

Lot K1 de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne K1 ; `docs/conception-valeur-llm.md`, tableau ligne
« Proposition à deux termes », tableau des contrats `propositions.schema_terme` / `echanges.proposer`, et « Lots de
valeur à ouvrir après décision »). Préalables fusionnés : K0 (lot 426, suggestions déterministes qui préremplissent le
formulaire E5), G17 (comptes parlés), U-D (descripteurs d'actions directes), U-P.

Lis `AGENTS.md` (contrat du MJ), `docs/etat-dev.md` (court), les deux documents ci-dessus et le rapport 426
(`docs/taches/rapport-codex-426-k0-candidats-contrat.md`).

## Invariant (un seul)
**Un marché se compose dans un éditeur à deux termes (ce que Corvus donne, ce qu'il demande : objet, part, tâche,
pièces, ou rien pour une contrepartie), et les deux termes affichés au moment de valider sont exactement ceux soumis à
`echanges.proposer` ; aucune clause n'est perdue, ajoutée ou réécrite entre l'aperçu et l'accord.** Seules les
conditions admises par les termes typés existants sont proposées (aucun champ libre non exécutable). Une saisie libre
de marché converge sur le même aperçu (même descripteur, mêmes termes), sans perte de clause. L'accord, la dette et
l'exécution restent distincts et passent par les voies existantes.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/echanges.py`, `donjon/dialogues.py`, `donjon/accords_publics.py`,
`donjon/web/page.html`, `donjon/tui.py`, tests. Attention : 428 (D0, PC fixe) touche aussi `dialogues.py` ; garde tes
changements dans ce fichier petits et localisés. Lots en cours : 402, 419, 427 (G14), 428 (D0). Pendant S1, n'ajoute
aucun registre d'esprit. Deux processus au plus, priorité réduite. Aucun appel à Luna dans l'éditeur.

## Vérification
Cas réel : Corvus propose à Aubin au Relais ses pièces contre une part de planches, puis un bien contre une tâche ;
autre cas : troc d'un objet contre une part à l'auberge. Dans la vraie boucle (web, console, TUI) avec recharge :
termes affichés = termes soumis, clause inconnue refusée avec `attendu`, refus ou accord du PNJ par la voie existante,
état et vues identiques après recharge. Saisie libre de marché (MJ simulé) qui arrive au même aperçu. Tests voisins
verts (K0, U-D, E5, comptes, propositions). Pas de suite complète, ni Luna.

## Livraison
Branche `codex-k1-editeur-marche`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-429-k1-editeur-marche.md` ; entrée
« non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
Bruts dans `C:\Users\msics\donjon\artifacts\k1-editeur-429\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier
de fin>` ou `QUESTION : …`.
