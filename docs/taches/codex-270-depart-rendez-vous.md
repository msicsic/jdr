# Tâche Codex 270 (diagnostic) : départs juste après « Ici, viens ! » dans la crue

La vérification d'intégration 241 (`docs/taches/rapport-codex-241-verif-integ.md`, l. 61-64 ; bruts
`C:\Users\msics\donjon\artifacts\verif-integ-c870c8b\`) compte, par un repérage textuel, les départs d'un PNJ dans
la minute où il a répondu « Ici, viens ! » : **39 → 24 au total, mais crue 10 → 15**. Ce sont des candidats seulement :
urgence, partenaire et clôture effective du rendez-vous ne sont pas certifiés par ce comptage.

Invariant en jeu (lot 230, fusionné) : **qui répond « Ici, viens ! » reste jusqu'à l'arrivée de l'autre, l'échéance
réglée sur la distance, ou un palier strictement supérieur ; s'il part, la rupture s'annonce par l'ouïe.** Le rendez-vous
se clôt par `appel.retrouves`.

**Diagnostic seul : aucun code du jeu modifié.**

## Ce que le rapport doit établir
1. **Retrouver les quinze cas de la crue** dans les nuits archivées de la vérification 241 (huit graines, 12 h) ; si les
   archives ne suffisent pas, rejouer sur l'intégration actuelle les nuits qui en contiennent (crue, départ tiré, joueur
   et durée de l'audit 241), une à la fois. Si l'intégration actuelle ne les reproduit plus, le dire et instruire
   seulement ceux de `c870c8b` (worktree détaché) sur deux nuits au plus.
2. **Classer chaque départ** : rendez-vous déjà clos (`appel.retrouves`, arrivée, rupture entendue), échéance passée,
   palier strictement supérieur (dire lequel : eau, péril, alarme, désespoir), ou départ sans aucune de ces causes.
   Tableau compact, une ligne par cas. Pour au moins deux cas, capture avant le départ ; monde et rendu identiques
   après rechargement.
3. **Verdict** : départs justifiés (et si le comptage textuel de la 241 devrait les écarter), ou défaut (la règle commune
   en cause en une phrase, sans exception propre à un personnage ou au scénario) et le petit lot de correction proposé.

Lot de 30 à 45 minutes. **Poste : le PC fixe**, un processus à priorité réduite, une nuit à la fois. Pas de Luna, pas de
suite complète, pas de banc comparatif.

## Livraison
- Branche `codex-depart-rendez-vous` : seulement `docs/taches/rapport-codex-270-depart-rendez-vous.md` (une page) et une
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\rendez-vous-270\`.
  Commite ; pousse si tu peux, sinon laisse le commit local et dis-le. Termine ton dernier message par `LOT TERMINÉ`
  (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
