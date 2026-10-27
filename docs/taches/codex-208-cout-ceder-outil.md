# Tâche Codex 208 (diagnostic) : d'où vient le surcoût du lot 202 (céder un outil) ?

Le lot 202 (`origin/codex-ceder-outil`, `74a4bc4`, **en attente**, décision de l'utilisateur du 2026-10-27) fait compter à un PNJ
la capacité qu'il perd en cédant un bien (`biens.capacites_crues`, `valeur_bien`, `echanges` : ventes, marchés, contreparties).
Il ne touche ni le planificateur ni la délibération, et pourtant, mine fixe 1985, 4 h : **recherches 698 → 987 (+41 %), neuves
423 → 510, nœuds 6 684 → 10 558 (+58 %)** ; S/F/D en légère baisse au Relais et à la mine ; crue sans recours 15 → 30 ; trois
retours brefs nouveaux en crue 2024 ; deux écarts de parcours propres à la branche dans la suite (lanterne encore là à 480 dans
le test des gestes par nœud ; poêle du guet rallumé). Rapport : `docs/taches/rapport-codex-202-ceder-outil.md` sur la branche ;
bruts `C:\Users\msics\donjon\artifacts\outil-202\` (sur le laptop ; rejoue ici ce qu'il faut).
**Diagnostic seul : aucun fichier du jeu modifié**, pour décider de la reprise du lot.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (205, 195) : **un seul processus**,
priorité réduite. **Bruts dans `C:\Users\msics\donjon\artifacts\cout-208\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## Ce qu'on te demande
1. **Attribuer le surcoût** avec `tools/mesure_cout.py` (compteurs par heure et PNJ × but), base `1a3359a` contre `74a4bc4` :
   quels PNJ et quels buts portent les recherches et nœuds en plus ; est-ce un coût par recherche (l'évaluation d'une cession
   appelée dans la recherche, par un devis ou un graphe) ou des nuits qui divergent (des refus de cession qui laissent des besoins
   ouverts et relancent des recherches) ? Montre l'appel ou la chaîne de décisions qui le produit, avec une capture rechargeable.
2. **Les deux écarts de la suite** : le changement de comportement est-il voulu par l'invariant (un PNJ garde un outil qui lui sert)
   ou un effet de bord ? Même question pour les trois retours brefs de la crue 2024 et la baisse sociale.
3. **Proposition** : la correction générale qui garderait l'invariant du lot 202 sans ce surcoût (par exemple calculer la valeur
   d'une capacité une fois par choix plutôt qu'à chaque évaluation, ou ne l'évaluer qu'au moment d'une cession réelle), avec son
   effet attendu, en un petit lot d'un seul invariant ; et ce qui relève d'une décision de l'utilisateur.

## Livraison
Branche `codex-cout-ceder-outil` (depuis `integration`) : `docs/taches/rapport-codex-208-cout-ceder-outil.md` (une page) et une
ligne dans `docs/etat-dev.md`. Commit et poussée ; si la poussée est bloquée, laisse le commit local et dis-le.
