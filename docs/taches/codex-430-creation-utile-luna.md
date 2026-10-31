# Tâche Codex 430 : pourquoi la création utile n'aboutit jamais avec Luna (diagnostic)

Quatre lots fusionnés ont vérifié leur contrat moteur avec MJ simulé, mais aucun geste utile n'a abouti avec Luna :
- **421 (G12, portée d'une création)** : création utile non démontrée ;
- **422 (G13, qualifier une propriété inconnue)** : longueur de la torche refusée par le garde de portée (« perception
  requise ») ; qualification utile générale non démontrée ;
- **423 (pièce de lot)** : la qualification physique de la planche est écartée par le contrôle de portée, puis un
  enrichissement de personnage est refusé ; aucune pièce prise ;
- **427 (G14, ciblage d'ambiance)** : au Relais, la création proposée avec sa suite est refusée par la revue comme
  « perception active » et pour une « capacité non déclarée » ; Luna substitue alors le toucher du sol. À l'atelier, la
  cible cosmétique directe est bloquée, puis l'admission reste refusée.

Rapports : `docs/taches/rapport-codex-42{1,2,3,7}-*.md`. Fils Luna bruts : `C:\Users\msics\donjon\artifacts\`
`g13-qualification-422\`, `piece-de-lot-423\`, `g14-ciblage-427\` (PC fixe) ; `g12-*-421` (laptop : s'ils manquent ici,
dis-le et travaille sur les trois autres).

Lis `AGENTS.md` (contrat du MJ, « Interactif »), `docs/etat-dev.md` (court), `docs/conception-refonte-mj.md` (§ 3,
« Objet, détail, propriété ajoutés » ; § 4, « Invention sans blocage narratif »).

## Question (un seul invariant à éclairer)
**Une création ou qualification interactive compatible, demandée par le joueur pour un geste, doit pouvoir être admise
puis manipulée sans que le joueur répète sa demande.** Pour chaque refus de ces fils : quel contrôle refuse (garde
déterministe, revue de portée, contre-revue, A4/A5), sur quel champ, avec quel `attendu`, et le refus est-il juste
(invention réelle d'un indice ou d'une capacité) ou faux (le contrôle classe à tort une création interactive comme
perception active ou capacité non déclarée) ? Les consignes données à Luna et le dossier de revue lui permettent-ils
de proposer la forme attendue (détail + geste dans un même paquet ordonné) ?

Rejoue sur copies, sans Luna, les dossiers exacts de revue archivés si utile (MJ simulé, mêmes entrées). Si une passe
Luna est indispensable pour trancher, une seule exécution courte sur copies.

## Contraintes
**Diagnostic seul : aucun code du jeu modifié.** Poste : le PC fixe. Lots en cours : 402 (calcul), 419, 428 (D0),
429 (K1). Deux processus au plus, priorité réduite.

## Livraison
Branche `codex-creation-utile-luna`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-430-creation-utile-luna.md` :
tableau des refus (lot, saisie, contrôle, champ, juste ou faux, preuve) ; cause commune ; **un petit lot de correction
proposé** (invariant, fonctions, vérification), sans le réaliser. Entrée « non fusionnée » de 8 lignes au plus dans
`docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves). Bruts dans
`C:\Users\msics\donjon\artifacts\creation-utile-430\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
