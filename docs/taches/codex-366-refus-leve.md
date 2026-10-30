# Tâche Codex 366 : Un refus retenu se lève par une contrepartie ou un accord nouveau

Le lot 358 (revalider une action différée contre un refus encore valable) a fait rougir deux méthodes : `test_contre_offre.ContreOffreTests.test_service_poursuivi_par_pnj_meme_laps_decoupe` (plus de souvenir de prêt de clé après le refus conservé) et `test_verifier_eau.VerifierTests.test_lucien_demande_la_lampe_vue_et_la_reference_le_trouve_aussi` (la vente attendue à Bram pour 17 pièces n'a plus lieu).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 362 et son annexe `docs/taches/attribution-codex-362-rouges-restants.md` (lignes « Réservé » : fusion de bascule, constat, question), et le rapport du lot d'origine. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Un refus retenu cesse de bloquer une demande quand une contrepartie ou un accord nouveau, cru par le demandeur, en lève la cause (règles existantes de levée : croyance ou moyen nouveau, prix supérieur, contre-offre acceptée) ; le lot 358 interdit seulement de réexécuter le même acte avec les mêmes termes tant que le refus tient.** Retrouve où la revalidation du 358 ignore la levée par contrepartie et corrige le contrat commun, sans affaiblir le cas du hameau du 358 (mandat refusé non réexécuté).

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/pnj.py` (`refus_etape`), `donjon/deliberation.py`, `donjon/echanges.py` si la levée y est jugée. Lots en cours : 364 (E6, `paroles.py`), 365 (catalogue des choix), 366, 367, 368 ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-refus-leve-contrepartie`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-366-refus-leve.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\refus-leve-366\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
