# Tâche Codex 428 : D0, parole ouverte personnelle

Lot D0 de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne D0 ; `docs/conception-valeur-llm.md`, « Lots de valeur à
ouvrir après décision » et décision sur la conversation ouverte, § 8). Ses préalables G12, G15 et G19 sont fusionnés.
Décision du 2026-10-29 : la conversation ouverte est admise comme parole enregistrée, sans effet caché.

Lis `AGENTS.md` (contrat du MJ, « Mécanique » : une parole établit qu'elle a été prononcée et entendue, pas que son
contenu est vrai), `docs/etat-dev.md` (court), les deux documents ci-dessus, et les rapports de G15 et G19 (cherche-les
dans `docs/historique-lots.md`).

## Invariant (un seul)
**Un contenu de dialogue inédit proposé par Luna pour un PNJ (un souvenir, un avis, une anecdote personnelle) est
admis comme parole enregistrée et entendue, sauvegardée avant affichage, sans aucun effet mécanique non typé : il ne
crée ni dette, ni promesse, ni croyance vraie chez Corvus, ni objet, ni connaissance que le PNJ n'a pas.** Un contenu qui
révèle un secret que le PNJ garde, ou qui contient une promesse ou un accord non typé, est refusé avec un `attendu`
(`donjon/refus.py`). Une réponse ouverte déjà connue (un sujet déjà dit au même interlocuteur) ne relance pas de nouvel
appel de formulation : le moteur restitue la parole enregistrée.

Aucun mot-clé ni exception de PNJ : le refus du secret et de la promesse passe par les données typées existantes
(connaissances privées, contenus typés `promesse`/`accord`), pas par le texte.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/paroles.py`, `donjon/connaissances.py`, `donjon/mj.py`,
`donjon/dialogues.py`, tests. Attention : 426 (K0, laptop) touche aussi `dialogues.py` ; garde tes changements dans ce
fichier petits et localisés. Lots en cours : 402, 419, 426, 427 (G14). Pendant S1, n'ajoute aucun registre d'esprit
(la parole passe par le registre existant des paroles entendues). Deux processus au plus, priorité réduite.

## Vérification
Cas réel (Gorm raconte un souvenir à Corvus au Relais) et autre PNJ (Odile à l'auberge), dans la vraie boucle avec MJ
simulé et recharge : parole enregistrée et visible après recharge, aucun effet mécanique ; secret gardé refusé ;
promesse non typée refusée ; même question reposée : zéro appel de formulation. Tests voisins verts (paroles, G15, G19,
rappels exacts). **Luna : une passe ciblée** sur copies (`noms-dialogue`, `soir-voix` ou un petit script ajouté) ; si la
revue automatique la bloque ou si le coffre est illisible, laisse la commande exacte dans les bruts. Pas de suite complète.

## Livraison
Branche `codex-d0-parole-ouverte`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-428-d0-parole-ouverte.md` ; entrée
« non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
Bruts dans `C:\Users\msics\donjon\artifacts\d0-parole-428\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de
fin>` ou `QUESTION : …`.
