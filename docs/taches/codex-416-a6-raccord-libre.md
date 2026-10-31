# Tâche Codex 416 : A6, le raccord du texte libre au compilateur de la forme A

Dernier lot de la forme A du compilateur (`docs/conception-g1.md`, section A, point 7), après A0 à A5, tous fusionnés (A2 : 370, 379, 381, 407 ; A3 : 410 ; A4 et A5 : 412 et 415). Le compilateur forme A porte maintenant les quatre familles, la liaison du transport, le dossier de revue et la reprise fidèle ; ce lot raccorde la voie du texte libre à ce compilateur.

Lis `AGENTS.md` (contrat du MJ), `docs/etat-dev.md` (court), `docs/conception-g1.md` (section A et le contrat de fusion), les rapports 410 et 415. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**La saisie libre passe par le compilateur forme A sans perdre aucune garantie déjà acquise : contrats A2, liaison A3, dossier A4, reprise A5, consentement U-C et ligne « Compris » U-P, et les voies transitoires (familles non portées) gardent leurs contrôles actuels.** Seul le raccord change ; aucune compaction supplémentaire du schéma ni correction de gameplay mêlée au raccord (une compaction viendra dans un futur lot d'équivalence). Aucun audit retiré.

Cas réels et autres cas après recharge, une saisie par famille, plus une famille non portée qui garde sa voie.

**Luna : une passe ciblée**, sur copies, des bancs `relais`, `crypte`, `atelier`, `echanges`, `noms-dialogue`, `soir-appel`, `sous-obstacle-relais`, `comptes`. Critère : aucun repli ni erreur technique ou de recharge, appels et secondes par tour au plus ceux de la vérification Luna du 2026-10-31 (2,26 appels et 8,5 s par tour sur onze bancs ; 2,08 et 8,05 s au lot 415, corpus différents). Si la revue automatique bloque la passe, laisse la commande exacte dans les bruts.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/mj.py`, `donjon/comprehension.py`, `donjon/fournisseurs/`, tests. Lots en cours : 402 (vérification d'intégration, calcul seul), 414 (rouges de la suite 4539dd68). Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna hors de la passe demandée ci-dessus.

## Livraison
Branche `codex-a6-raccord-libre`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-416-a6-raccord-libre.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\a6-raccord-libre-416\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
