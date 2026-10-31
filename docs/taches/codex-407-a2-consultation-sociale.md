# Tâche Codex 407 : A2, famille consultation sociale : un sens unique pour moteur, schéma et plan public

Quatrième et dernier lot A2 de la forme A du compilateur (`docs/conception-g1.md`, section A, point 3) après séquence/attente (370), expression/son (379) et passage (381), fusionnés. Reprends la méthode des rapports 379 et 381 (module de contrat commun, tests cas réel/autre cas/faux pendant). Ce lot ne traite que la famille **consultation sociale** : questions d'information (« où est… », « as-tu… », « qui est là »), demande de localisation, de ressource, réclamation sous forme de question, avec leurs raccourcis.

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Une opération de la famille consultation sociale et ses raccourcis ont un sens unique, le même pour le moteur, le schéma du compilateur et le plan public montré au joueur (« Compris : … ») ; aucun champ voisin simplement légal ne remplace la charge requise (interlocuteur, sujet, acte).** Cas réel, autre cas et faux pendant ; mécanique inchangée (réponses selon les croyances du témoin, refus retenus, audience). Pas de changement de revue ni de raccord libre (A4, A6).

Luna : aucune passe dans ce lot.

## Contraintes
**Poste : le laptop.** Fichiers attendus : un module de contrat de la famille, `donjon/operations.py`, `donjon/comprehension.py`, `donjon/commandes.py`, `donjon/paroles.py` seulement pour réemployer leurs tables, tests. Lots en cours : 403 (rouges de la suite c562aa21), 406 (S1j paroles et voix, `social.py`/`voix.py`/`memoire.py`) : signale tout recouvrement ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin est autorisée par l'utilisateur.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-a2-consultation-sociale`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-407-a2-consultation-sociale.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\a2-consultation-sociale-407\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
