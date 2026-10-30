# Tâche Codex 368 : Quatre régressions isolées des lots 313, 330, 332 et 333

Quatre méthodes réservées par le 362, chacune d'une fusion différente : `test_echanges_argent.PretTests.test_le_proprietaire_qui_la_redemande_la_recupere_sauf_si_elle_sert` (333 : `absent` au lieu de `necessaire` après trois minutes) ; `test_enfermer.EnfermerTests.test_assommer_trainer_verrouiller_temoin_reveil_et_decoupage` (332 : pas de souvenir `operation=enfermer` chez Gaspard malgré l'événement) ; `test_installation_gardee.InstallationGardeeTests.test_demande_plutot_que_bris_et_laps` (313 : plan de demande valide, mais porte brisée à la fin) ; `test_lumiere.MineTests.test_une_lampe_vide_se_remplit_d_huile_puis_s_allume` (330 : la lampe reste allumée, trajet au bureau et extinction non établis).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 362 et son annexe `docs/taches/attribution-codex-362-rouges-restants.md` (lignes « Réservé » : fusion de bascule, constat, question), et le rapport du lot d'origine. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
Pour chacune, **un invariant distinct** : trouve la cause dans le contrat commun touché par la fusion d'origine et corrige-la si elle est claire et locale (une cause, sans cas particulier) ; sinon décris-la précisément et arrête-toi pour celle-là. Traite-les dans cet ordre et livre ce qui est prouvé.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : selon la cause ; signale tout fichier commun avec les lots en cours. Lots en cours : 364 (E6, `paroles.py`), 365 (catalogue des choix), 366, 367, 368 ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-quatre-regressions`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-368-quatre-regressions.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\quatre-regressions-368\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
