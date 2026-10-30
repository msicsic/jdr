# Tâche Codex 370 : A2, famille séquence et attente : un sens unique pour moteur, schéma et plan public

Premier lot A2 de la forme A du compilateur (`docs/conception-g1.md`, section « A — … », points 3 à 7 ; A0 oracle et A1 provenance publique, lot 346, fusionnés). A2 se porte **une famille à la fois** : ce lot ne traite que la famille **séquence et attente** (enchaîner des gestes, attendre une durée ou un événement).

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Une opération de la famille séquence/attente et ses raccourcis ont un sens unique, le même pour le moteur, le schéma du compilateur et le plan public montré au joueur (« Compris : … ») ; aucun champ voisin simplement légal ne remplace la charge requise.** Cas réel, autre cas et faux pendant (une séquence qui ressemble mais ne l'est pas), mécanique inchangée. Pas de changement de revue ni de raccord libre (A4, A6).

Luna : aucune passe dans ce lot (A6 portera la passe ciblée).

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/compilateur.py` ou le schéma en vigueur, `donjon/comprehension.py`, `donjon/commandes.py` (attente), tests ; lis `docs/conception-g1.md` et le rapport 346. Lots en cours : 365 (catalogue des choix), 369 (U-T social information), 370, 371, 372 ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-a2-sequence-attente`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-370-a2-sequence-attente.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\a2-sequence-attente-370\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
