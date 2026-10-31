# Tâche Codex 412 : A4, le dossier de revue reçoit le plan développé et le sens proposé

Lot A4 de la forme A du compilateur (`docs/conception-g1.md`, section A, point 5), après A0, A1, A2 (370, 379, 381, 407) et A3 (410, liaison du transport, fusionné). Le rapport 410 relève une limite : Luna peut encore compiler « je fredonne doucement » en un geste sans effet sonore, que la revue de fidélité ne voit pas.

Lis `AGENTS.md` (contrat du MJ, « Fidélité de la saisie »), `docs/etat-dev.md` (court), `docs/conception-g1.md` (section A), les rapports 379 et 410. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**La revue de fidélité d'une saisie libre à effets reçoit le plan développé par le moteur et le sens proposé par les contrats (opérations, paramètres, effets typés, clauses transitoires, manière demandée), indépendamment de l'admission ; une omission réelle (le son demandé absent du plan) y est visible et refusable, un plan fidèle passe.** Aucun retrait d'audit dans ce lot. Contre-épreuves opposées : un refus fidèle (la saisie demande un son et le plan le porte : admis) et une omission réelle (le fredonnement compilé sans effet sonore : refusé avec un `attendu` qui nomme l'effet manquant).

**Luna : une passe ciblée**, sur copies, de bancs qui exercent l'expression sonore et deux autres familles (`relais`, `atelier`, `noms-dialogue`, plus un script qui contient « je fredonne doucement »). Si la revue automatique la bloque, laisse la commande exacte dans les bruts. Mesure les appels et secondes par tour.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/mj.py` (dossier de la revue), `donjon/comprehension.py`, les modules de contrat par famille, tests. Lots en cours : 402 (vérification d'intégration, calcul seul), 411 (S1k recours, `memoire.py`) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna hors de la passe demandée ci-dessus.

## Livraison
Branche `codex-a4-dossier-revue`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-412-a4-dossier-revue.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\a4-dossier-revue-412\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
