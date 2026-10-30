# Tâche Codex 355 : E4, l'accord initial engage exactement les termes datés acceptés

Quatrième lot de l'échéance négociée, après E1 (348, référence temporelle), E2 (350, réalisation datée) et E3 (352,
délai jugé sur les moyens crus), fusionnés. Conception : `docs/conception-menace-echeance.md`, sections 3, 5 (ligne E4
et preuve commune P) et 6 (arbitrages acceptés le 2026-10-30, à ne pas rouvrir : prestation ponctuelle avant une
limite, paiement présent ; prêt daté, maintien continu et crédit refusés explicitement). Lis `AGENTS.md`,
`docs/etat-dev.md` (court), la conception et les rapports 348, 350 et 352.

## Invariant (un seul)
**Une proposition qui porte un terme daté (une part livrée ou une tâche accomplie avant une limite, contre des pièces
payées maintenant) engage, si elle est acceptée, exactement ces termes : l'obligation enregistrée porte la limite
proposée (E1), le jugement d'acceptation utilise le délai cru du contractant (E3), et le paiement présent est exécuté
une seule fois.** Un refus n'engage rien ; une double soumission ne repaie pas ; aucune clause de paiement futur, de
prêt daté ou de maintien continu n'est acceptée (refus avec `attendu`, une cause par refus) ; un délai indéterminé ne
devient jamais une garantie datée. Les comptes et paroles qui en rendent compte sont formulés par le moteur (contrat du
MJ), complets et publics.

Le chemin du joueur reste celui des propositions typées existantes, sans nouveau schéma de saisie (E5 portera le choix
direct, E6 le libre) : les épreuves passent par le contenu typé déjà accepté par le moteur, étendu du seul champ de
limite si nécessaire, et par les propositions des PNJ si elles existent déjà pour ces termes.

## Épreuves (preuve P en plus)
Termes `part` et `tache` datés, pièces payées maintenant : accepté, refusé, délai impossible, délai indéterminé ;
double soumission ; clause de paiement futur refusée ; réalisation à temps puis en retard jusqu'au remboursement
unique (E2) ; comptes et paroles visibles identiques après recharge et laps découpé. Auberge (cas 1.2 de la
conception) et un autre cas au Relais ou à la mine.

## Vérification
Tests ciblés et voisins (propositions, marchés, comptes parlés, émissions, socle des agendas, tests des lots 348/350/352).
Banc rapide 4 h, quatre graines, Relais, auberge, mine (`tools/comparer_bancs.py --reference main`). Pas de suite
complète, ni Luna, ni banc long.

## Contraintes
**Poste : le PC fixe.** Fichiers prévus : `donjon/propositions.py`, `donjon/echanges.py`, `donjon/agendas.py`,
`donjon/comptes_parles.py`/`comptes_narratifs.py`, `donjon/emissions.py`. Ne touche ni `page.html`, `pont.py`,
`dialogues.py`, `jeu.py`, `tui.py`, ni le transport d'adresse de `paroles.py` (lots 353 et 354 en cours). Priorité
réduite, deux processus au plus.

## Livraison
- Branche `codex-e4-accord-date`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-355-e4-accord-date.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md`, section « Lots non fusionnés ».
- Bruts dans `C:\Users\msics\donjon\artifacts\e4-355\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
