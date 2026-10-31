# Tâche Codex 395 : l'avis redit de Brune en crue 2024 après le lot 360

Reste du lot 375 (`docs/taches/rapport-codex-375-suite-e0826ef.md`, fusionné, section « Réserve précise ») :
`tests.test_avis_redits.AvisReditsReelsTests.test_crue_2024_chaque_redite_exige_un_rallumage_appris` est rouge depuis la
fusion du lot 360 (`7708a16d`) : Brune ne transmet plus rien dans la capture crue 2024, à la minute 140. Le lot 360
(`rapport-codex-360-regressions-337.md`) a décidé qu'un PNJ ne confie pas son inventaire de départ, seulement un
changement appris (décision de l'utilisateur, `docs/etat-dev.md`, « Confidences d'inventaire »).

Question du 375 : **quelle prémisse perceptive attestée rend l'extinction nouvelle pour Brune à 140, après le 360 ?**
Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 360, 375 et 108 (avis redits ; cherche « avis redits » dans
`docs/historique-lots.md`). Bruts du 375 : `C:\Users\msics\donjon\artifacts\suite-e0826ef-375\` (laptop).

## Invariant (un seul)
**Un PNJ redit un avertissement seulement quand il a appris un changement depuis sa dernière parole (ici un rallumage
ou une extinction perçus après coup) ; un état connu depuis le début de la partie n'est pas une nouvelle (décision du
360).** Isole d'abord la provenance et l'audience de la croyance de Brune à 140 :
- si Brune a réellement perçu une extinction ou un rallumage nouveau et se tait, c'est un défaut du filtre du 360,
  trop large : corrige-le dans le contrat commun des nouvelles ;
- si l'extinction n'est pas nouvelle pour elle (savoir de départ), la scène doit déclarer la perception qui la rend
  nouvelle, sans retirer l'assertion de transmission ni imposer une confidence.

Preuve citée dans les deux cas ; aucune exception de scénario.

## Vérification
`test_avis_redits` (les deux méthodes, dont celle des lampes homonymes du 375), les fichiers de tests du
360, `test_deja_dit` ; cas réel et autre cas après recharge. Si du code du jeu change : banc rapide 4 h, crue et mine,
quatre graines. Pas de suite complète, ni Luna.

## Contraintes
**Poste : le laptop.** Lots en cours : 374 (position crue), 381 (A2 passage), 392 (scènes connues, laptop), 394 (don
direct) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs
détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin
(https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-avis-redits-crue`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-395-avis-redits-crue.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\avis-redits-395\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
