# Tâche Codex 392 : ce que les scènes de test déclarent connu depuis le catalogue connu (365)

Question Q2 du lot 390 (`docs/taches/rapport-codex-390-suite-663d1308.md`, fusionné). Le lot 365 (« le catalogue des
choix ne montre que ce que Corvus connaît », `rapport-codex-365-catalogue-connu.md`) a retiré l'admission lexicale de
`_connu_du_joueur` ; le lot 387 a déjà corrigé ainsi cinq tests du terminal d'information. Trois méthodes restent :
- `test_garde_ouidire.GardeOuidireTests.test_preuves_sans_porteur_salle_et_contenant_transmises_et_rechargees` :
  référence de lieu non admise dans le rendu ;
- `test_mandat_joueur.MandatJoueurTests.test_charge_du_banc_apres_information_sans_jet_force` : références du mandat
  refusées comme inconnues ;
- `test_occasions_scenarios.OccasionsScenariosTests.test_inverse_ne_retire_que_les_occasions_du_lot` : savoirs de
  prémisse ajoutés aux données hachées.

Bruts du 390 : `C:\Users\msics\donjon\artifacts\suite-663d1308-390\` (PC fixe). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), les rapports 365, 387 et 390.

## Invariant (un seul)
**Ce que Corvus peut désigner ou voir rendu nommé est ce qu'il connaît (contrat du 365) ; une scène de test qui suppose
une connaissance la déclare explicitement, et une donnée de scénario n'est jamais modifiée pour faire passer un test.**
Pour chaque méthode, établis si la connaissance attendue est légitimement acquise dans la scène (alors défaut réel :
le moteur devrait la rendre connue, à corriger dans le contrat commun) ou supposée à tort (prémisse à déclarer). Pour
`occasions_scenarios`, compare les données historiques en excluant seulement les savoirs de prémisse déclarés par le
test, jamais les savoirs décidés au 365 ; aucun hash réancré sans la liste exacte des champs.

## Vérification
Les trois fichiers, `test_catalogue_connu` (ou le fichier du 365) et `test_information_terminal` ; cas réel et autre
cas après recharge, contre-épreuve (sans la connaissance, le refus ou l'absence de nom tient). Si du code du jeu change :
empreintes 2 h Relais et scénarios touchés, quatre graines. Pas de suite complète, ni Luna.

## Contraintes
**Poste : le laptop.** Lots en cours : 374 (position crue), 380 (U-M social comptes),
381 (A2 passage), 391 (parité acoustique, laptop) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs
longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin
(https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-scenes-connues`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-392-scenes-connues.md` ; entrée « non fusionnée » de 8 lignes
  au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\scenes-connues-392\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
