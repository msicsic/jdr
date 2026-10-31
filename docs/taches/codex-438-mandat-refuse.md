# Tâche Codex 438 : un mandat refusé n'est reproposé que sur une preuve nouvelle

Défaut relevé par la vérification d'intégration 402 (`docs/taches/rapport-codex-402-verif-integ.md`, fusionné, « Petits
lots à ouvrir » ; bruts `C:\Users\msics\donjon\artifacts\verif-integ-4539dd68\`, PC fixe, `cas-a-instruire.json`).
Hameau de la crue 1985, **129–143 min** : Gorm propose **14 fois à Maël et 11 fois à Sève** d'évacuer Ilse, refus
`impossible` à chaque fois. Sur la nuit : 31 activations « mandataire estimé » et 32 sommeils « sans plan admissible au
coût » de l'agenda ; aucune de ces répétitions dans la même nuit sur `0bad227`.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 402, `docs/plan-agendas.md` (A5, mandat ; décision « refus
retenus, réessai lié à l'obstacle, jamais par le seul délai »), les rapports A5 (lots 256 à 260, 338 à 341, 306) et
S1k (409/411 : refus retenus par l'interface), dont le contrat de réouverture est en cause.

## Invariant (un seul)
**Un refus d'un mandat (ou d'une demande d'agenda) est retenu avec sa cause ; le même mandat au même destinataire
n'est reproposé, et l'agenda n'est réveillé pour lui, que sur une croyance ou un moyen nouveaux qui lèvent cette cause,
jamais par le seul délai ni par un réveil d'agenda sans entrée nouvelle.** Établis d'abord sur la capture réelle (129 min,
reconstituée sur copie) pourquoi le refus `impossible` ne tient pas : cause non retenue pour un mandat, clé de refus
différente entre la proposition et le devis du mandataire, ou réveil qui efface le refus. Corrige le contrat commun
(refus retenus de S1k, devis observateur, réveil d'agenda), sans exception de personnage ni de scénario.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/agendas.py`, `donjon/deliberation.py`, `donjon/echanges.py` au
besoin, tests. **Ne pousse pas vers origin** : le PC fixe n'a plus d'identifiants Git en ce moment ; commite dans ta
branche locale et donne le commit final dans ton dernier message, le superviseur la récupère par SSH. Lots en cours :
431, 435 (S1o, mémoire des aides et contrats : touche le moins possible ses vues), 436, 437 (`planification.py`).
Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite.

## Vérification
Capture réelle (hameau 1985, Gorm, Maël, Sève, Ilse) après recharge et laps entier/découpé : une proposition par
destinataire tant que la cause tient, puis reprise si une preuve nouvelle la lève (exerce-la). Autre cas de même nature
(un autre mandat ou une autre demande d'agenda refusée). Banc rapide 4 h, quatre graines, hameau de la crue et Relais,
contre la base (cache) : répétitions de mandats, suspects 219, richesse S. Pas de suite complète, ni Luna.

## Livraison
Branche `codex-mandat-refuse`, base `integration` (locale ; voir contraintes). Rapport d'une page
`docs/taches/rapport-codex-438-mandat-refuse.md` ; entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md`
(puce « - » qui nomme la branche entre accents graves). Bruts dans `C:\Users\msics\donjon\artifacts\mandat-refuse-438\`.
Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
