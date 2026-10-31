# Tâche Codex 415 : A5, la reprise fidèle, construite sur A4

Lot A5 de la forme A du compilateur (`docs/conception-g1.md`, section A, point 6). Il part de la branche
**`codex-a4-dossier-revue`** (lot 412, A4, non fusionné), et non de `integration`. La revue y reçoit le plan développé
et le sens proposé, ce qui détecte l'omission sonore. Mais le rapport 412 relève une régression bloquante : dans le
banc `atelier`, la revue refuse à tort le sifflement canonique (« nuance absente »), puis la correction de Luna le
remplace par `voix_melodique`, et cette substitution est acceptée. Sur la base, aucune substitution en trois parties.
Les deux lots seront fusionnés ensemble.

Lis `AGENTS.md` (contrat du MJ, « Fidélité de la saisie »), `docs/etat-dev.md` (court), `docs/conception-g1.md`
(section A) et les rapports 379, 410 et 412 (`docs/taches/rapport-codex-412-a4-dossier-revue.md` sur la branche,
bruts `C:\Users\msics\donjon\artifacts\a4-dossier-revue-412\`, laptop).

## Invariant
**Une correction après un refus revient à la saisie entière et au refus typé : le candidat précédent reste
explicitement non admis, et ce que le refus n'a pas mis en cause (opération, méthode et manière typées par les
contrats A2) ne peut pas être remplacé par la correction ; une substitution de manière typée qui n'est pas demandée par
l'`attendu` du refus est refusée par le moteur, de façon déterministe, avec son `attendu`.**

Le moteur garde :
- **la borne de corrections**, inchangée ;
- **ses refus réels**, inchangés ;
- **aucun texte proposé ne devient un fait moteur.**

Traite aussi le faux refus de la revue sur le sifflement : ce que les contrats typent (la méthode sonore) se compare au
plan, sans jugement sémantique de « nuance ». La revue reste sémantique pour le reste.

Cas : le sifflement de l'atelier (cas réel), le cri « de colère » (autre cas, refusé à tort au 412), une cible absente
et une autre référence, un refus réel et une fausse impossibilité.

**Luna : une passe ciblée**, sur copies : `atelier` (au moins deux fois), `relais`, `noms-dialogue` et le script du
fredonnement du 412. Critère : aucune substitution acceptée, aucun faux refus de manière typée, appels et secondes par
tour comparables à ceux du 412 (environ 2,4 appels et 9 s). Si la revue automatique bloque la passe, laisse la commande
exacte dans les bruts.

## Contraintes
**Poste : le laptop.** Base : `origin/codex-a4-dossier-revue`. Fusionne aussi `origin/integration` dans ta branche
avant de livrer. Fichiers attendus : `donjon/mj.py`, `donjon/comprehension.py`, les modules de contrat par famille,
tests. Lots en cours : 402 (vérification d'intégration), 413 (S1l), 414 (rouges de la suite 4539dd68). Pendant S1,
n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils
vivent avant de rendre la main. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de
l'utilisateur) est autorisée.

## Livraison
- Branche `codex-a5-reprise-fidele`, base `codex-a4-dossier-revue`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-415-a5-reprise-fidele.md` : ce qui change pour A4 et A5 ensemble, les
  mesures Luna, les limites. Entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme
  la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\a5-reprise-415\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
