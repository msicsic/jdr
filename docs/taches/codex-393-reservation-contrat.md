# Tâche Codex 393 : une réservation de part ne bloque pas la livraison de son propre contrat (377)

Question Q3 du lot 390 (`docs/taches/rapport-codex-390-suite-663d1308.md`, fusionné). Le lot 377 (« une même part n'est
pas promise deux fois », `rapport-codex-377-double-promesse.md`) a fait basculer deux méthodes :
- `test_intermediaires.IntermediairesTests.test_bien_durable_livre_par_le_meme_contrat` : le bien durable n'est plus
  livré après sa réservation ;
- `test_livraison_inconnue.LivraisonInconnueTests.test_devis_plan_et_empeche_purs_independants_du_lieu_cache` : une
  nouvelle copie validée par le 377 rejette un placement artificiel hors du sol posé par le test.

Question du 390 : la commission réserve-t-elle deux fois son propre moyen, et quelles cases d'auteur valides permettent
de continuer le contrôle de pureté du devis ? Bruts du 390 : `C:\Users\msics\donjon\artifacts\suite-663d1308-390\`
(PC fixe). Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 377 et 390.

## Invariant (un seul)
**Une part ou un bien réservé à un engagement reste réservé contre une seconde promesse, mais il reste livrable par cet
engagement même et par ses étapes (commission, remise, intermédiaire) : la réservation ne se compte jamais deux fois
contre son propre contrat.** Pour `intermediaires`, trouve où la réservation du 377 compte le moyen du même contrat
comme déjà pris ; corrige-le dans le contrat commun (`echanges`/`agendas`), sans rouvrir la double promesse. Pour
`livraison_inconnue`, remplace le placement hors du sol par une case d'auteur valide qui garde l'intention du test
(pureté du devis indépendante du lieu caché), preuve citée ; l'assertion de pureté reste intacte.

## Vérification
Les deux fichiers, `test_double_promesse` (ou le fichier du 377), `test_promesses`, `test_taches_payees`,
`test_echanges_suite` ; cas réel et autre cas après recharge, contre-épreuve : la double promesse reste refusée. Si du
code du jeu change, banc rapide 4 h Relais et crue, quatre graines. Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Lots en cours : 374 (position crue), 380 (U-M social comptes),
381 (A2 passage), 391 (parité acoustique, laptop), 392 (scènes connues, laptop) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs
longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin
(https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-reservation-contrat`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-393-reservation-contrat.md` ; entrée « non fusionnée » de 8 lignes
  au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\reservation-contrat-393\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
