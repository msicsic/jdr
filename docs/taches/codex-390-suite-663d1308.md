# Tâche Codex 390 : les rouges nouveaux de la suite 663d1308

La suite complète de l'intégration `663d1308` (après les lots 370 à 386) donne **42 échecs et 7 erreurs sur 42
méthodes** (3 329 tests). Une partie est déjà prise en charge ailleurs :
- **lot 375** (en cours, laptop) : les onze méthodes rouges de la suite `e0826efc` (avis redits, banc sans joueur,
  bourse redemandée, complétion des preuves, prêt réclamé, attente d'une part, rendez-vous, traîner, etc.) ;
- **lot 387** (fusionné après `663d1308`) : les cinq erreurs de `test_information_terminal`.

**Ce lot traite les autres**, nés entre `e0826efc` et `663d1308`. Liste complète des méthodes en échec :
`C:\Users\msics\donjon\artifacts\suite-663d1308-echecs.txt` (laptop et PC fixe), journal entier `suite-663d1308.log` à côté
(sur le PC fixe : `artifacts\suite-integ386-663d1308\suite.log`). Familles visibles :
- appel et voix : `test_appel_negocie` (cinq), `test_voix.HelerTests` (deux), `test_voix_inconnues` (cinq),
  `test_rendez_vous.test_joueur_appelant_et_appele_reprise_sans_luna`,
  `test_question_absent.test_reponses_a_un_appel_gardent_leur_mecanique_distante`,
  `test_constater_rumeurs.ChercherQuelquUnTests` (deux). Le lot 379 les a vues rouges déjà sur sa base `85052cf8` :
  la cause est probablement antérieure (370, 365, 369, 376, 377) ;
- `test_refus.AttenduTests` (deux), `test_passage.DemanderLePassageTests`, `test_luna_noms`, `test_intermediaires`
  (deux), `test_livraison_inconnue`, `test_mandat_joueur`, `test_occasions_scenarios`, `test_garde_ouidire`,
  `test_contact_position_inconnue`, `test_reprise_contact`, `test_etapes_chainees`.

Fusions entre les deux suites (`git log --first-parent e0826efc..663d1308`) : 371, plan esprit social, 370, 372, 369,
365, 373, 377, 376, 379, 378, 382, 383, 384, 385, 386.

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les rapports des lots cités ; pour un lot ancien, cherche dans
`docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Chaque méthode rouge de ce lot est attribuée à la fusion qui l'a fait basculer (bissection `--first-parent` entre
`e0826efc` et `663d1308`, sur ces seuls fichiers de tests), puis corrigée dans le contrat commun si la cause est claire
et locale, ou adaptée seulement si son attente est devenue fausse par un changement voulu et documenté (preuve citée,
assertions de sécurité intactes) ; sinon listée avec la question précise.** Commence par la famille appel/voix (la plus
nombreuse, probablement une seule cause). Si le créneau ne suffit pas, livre les familles corrigées et liste le reste
attribué, sans tout corriger d'un coup. Ne touche pas aux méthodes du 375 ni du 387.

## Vérification
Les fichiers de tests concernés, et pour chaque correctif du moteur un cas réel et un autre cas après recharge ;
empreintes 2 h Relais et scénarios touchés, quatre graines, si du code du jeu change. Pas de suite complète (le
superviseur la relance), ni Luna.

## Contraintes
**Poste : le PC fixe.** Lots en cours : 374 (position crue, repris), 375 (rouges e0826ef, laptop), 380 (U-M social
comptes, web), 381 (A2 passage), 389 (U-T social avis, `jeu.py`/`tui.py`) ; signale tout recouvrement. Pendant S1,
n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés. La poussée de ta
branche vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-suite-663d1308`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-390-suite-663d1308.md` : tableau méthode → fusion fautive → cause →
  correction ou question ; entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme
  la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\suite-663d1308-390\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
