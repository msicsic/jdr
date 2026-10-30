# Tâche Codex 367 : Un service payé reste dû quand l'évacuation déplace la lumière

Le lot 306 (agenda d'évacuation du hameau) a fait rougir deux méthodes : `test_pas_compagnons.PasCompagnonsTests.test_promesse_hameau_1985_annoncee_retrouvee_apres_recharge` (service de torche absent du registre final, autre service d'évacuation présent) et `test_service_non_defait.ServiceNonDefaitTests.test_hameau_1985_prestataire_mobile_bloc_decoupe` (service payé réalisé puis état perdu).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 362 et son annexe `docs/taches/attribution-codex-362-rouges-restants.md` (lignes « Réservé » : fusion de bascule, constat, question), et le rapport du lot d'origine. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Un service payé et son état obtenu restent protégés selon le contrat des services (« ne pas défaire ce qu'on a été payé pour faire », trace des services rendus, lots 224/238) quand un agenda d'évacuation déplace le prestataire ou sa source de lumière ; l'évacuation n'efface pas la trace d'un autre service.** Corrige l'interaction dans le contrat commun, sans cas propre au hameau.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/biens.py` (services rendus), `donjon/agendas.py`, `donjon/deliberation.py`. Lots en cours : 364 (E6, `paroles.py`), 365 (catalogue des choix), 366, 367, 368 ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-service-evacuation`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-367-service-evacuation.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\service-evacuation-367\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
