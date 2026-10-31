# Tâche Codex 427 : G14, ciblage d'un élément d'ambiance

Lot G14 de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne G14 ; `docs/conception-refonte-mj.md` § 3, tableau
« Objet, détail, propriété ajoutés » et « Texture, odeur, son de fond », et § 4, paragraphe « Le ciblage d'une ambiance
ne dépend plus d'une extraction oubliée »). Ses préalables G12 (portée d'une création, lot 421) et G13 (qualification,
lot 422) sont fusionnés. Aujourd'hui, l'ambiance persistée (`ambiances[salle]`) porte `entites=[]`, ce qui empêche le
ciblage par `narration.ambiance_ciblee` / `mj.py`.

Lis `AGENTS.md` (contrat du MJ, « Interactif » et « Ambiance »), `docs/etat-dev.md` (court), les deux documents ci-dessus
et les rapports 421 et 422.

## Invariant (un seul)
**Un élément d'ambiance que le joueur cible est matérialisé une seule fois par le contrat commun des faits interactifs
(ancrage public dans le lieu, budget d'invention, validation des usages) avant toute manipulation, ou déclaré non
manipulable (une odeur, un son de fond) ; aucun texte d'ambiance n'applique un effet, et aucun objet n'existe avant la
matérialisation.** Les éléments ciblables d'une ambiance sont enregistrés avec elle (identifiant local, libellé, ancrage),
validés par le moteur avant publication ; la résolution d'une cible passe par la même voie que G12/G13. Pas de mot-clé
ni d'exception de lieu ou de type d'élément ; la détection d'une paraphrase reste une limite sémantique à dire.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/narration.py`, `donjon/faits_locaux.py`, `donjon/mj.py`, la
production d'ambiance, tests. Lots en cours : 402 (vérification d'intégration, calcul seul), 419 (vérification de
contact), 426 (K0, `echanges.py`, `dialogues.py`), 428 (D0, `paroles.py`, `dialogues.py`). Pendant S1, n'ajoute aucun
registre d'esprit. Deux processus au plus, priorité réduite.

## Vérification
Cas réel (un détail d'une ambiance du Relais, ciblé puis manipulé) et autre cas (un autre détail sur un autre support,
une odeur non manipulable, un budget dépassé), dans la vraie boucle avec MJ simulé et recharge : aucun objet avant la
matérialisation, un objet unique après, même cible reprise sans redemander au joueur. Tests voisins verts (G12, G13,
ambiance, faits locaux). **Luna : une passe ciblée** sur copies, scripts qui exercent le ciblage d'une ambiance (ajoute
un petit script si aucun n'existe) ; si la revue automatique la bloque ou si le coffre est illisible, laisse la commande
exacte dans les bruts. Pas de suite complète.

## Livraison
Branche `codex-g14-ciblage-ambiance`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-427-g14-ciblage-ambiance.md` ;
entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents
graves). Bruts dans `C:\Users\msics\donjon\artifacts\g14-ciblage-427\`. Termine par `LOT TERMINÉ`,
`CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
