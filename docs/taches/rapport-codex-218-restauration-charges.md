# Lot 218 — restauration portée par l'engagement

Branche `codex-restauration-charges`, **non fusionnée**. Base finale **`881db69`**,
224/225 conservés par la fusion **`7c46d64`**, sans conflit de code.
Code 218 `2bd1e6f`, validation finale `fa9dbe3` ; commits non signés, aucune clé.
Aucun Luna ; deux travailleurs réduits au plus. Bruts finaux :
`C:/Users/msics/donjon/artifacts/charges-218/881db69/` ; essais antérieurs conservés
dans le dossier parent.

**Contrat.** `agendas` conserve dans l'intention les conditions suspendues et
leur phase de restauration. `choisir` les transmet au même engagement, même
après découpe ou reconstruction forcée ; `retabli_par_son_plan` suspend la
garde correspondante, sans auto-exclure la garde elle-même. Abandon ou
remplacement libère la garde. `planification.suspensions` relève les charges
initialement satisfaites : sous clé, porte ouverte en passant, poste déclaré.
`restaurer_charges` recherche leur rétablissement physique, retour compris,
après le service ; ses moyens passent par le juge commun du 213/225.
Le devis de remise compte la restauration ; la publication ne referme plus
au bout d'un préfixe incertain ni n'y ajoute une remise prématurée. Une parole
due ne s'acquitte pas par la seule satisfaction du bénéficiaire.
`esprits` ne change que le champ facultatif et sa validation ; `null` refusé,
absence ancienne admise. Le delta 218 ne touche ni MJ, ni `social`, ni `pnj`.

**Preuves.** Capture 209 rejouée sur **`881db69`** avant correction : à 5 et
10 min, Gorm reste sur le service à Ilse ; la livraison historique `vivres_6`
interrompue à 6 min **n'est plus reproduite**. Captures et rendus conservés.
**64 ciblés verts, dont 11 nouveaux**, puis onze repris après validation :
Gorm livre depuis sa réserve, Mathe depuis un autre contenant/scénario,
porte franchie, retour au poste, suffixe perdu, reconstruction avant et
pendant restauration, abandon, tête refusée, part promise sans faim.
Monde, rendu et scène perçue contrôlés après recharge, mêmes laps en bloc
ou découpés ; pas de verrouillage intercalé avant les remises testées.

**Banc : 20 paires × 4 h contre `881db69`**, références absentes calculées
une fois puis cachées, classes 219. Suspects **4 → 4**, aucun scénario en
hausse (**0/0/2/2/0**, Relais/Mine/Auberge/Crue/Hameau), zéro plantage/usurpation.
Cycles **523 → 483**, préemptions **67 → 54**, à expliquer **59 → 63**,
autrui **1 → 1**, progression **0 → 0** ; dérives **200 → 178**, états payés
perdus **8 → 6** (durée non spécifiée). **Absence générale de boucle nouvelle
non validée** : nouvelle alerte Brune, hameau 2024, neuf activations et neuf
sommeils d'agenda. Aucune nouvelle répétition de fermeture. Eau crue
**1,25 → 3,75**, hameau **5 → 5 PNJ·min** ; aucun gain uniforme revendiqué.

**Coût mine 1985, 4 h fixe : critère sans hausse notable non atteint.**
Nœuds **9 189 → 11 051 (+20,3 %)**, recherches **601 → 913**, neuves
**315 → 474**. Nouveaux devis de feu de Bram : **0 → 40 / 1 680 nœuds** ;
restauration : **85 nœuds**. Aucun filtre de possibilités ajouté pour réduire
ce coût. CPU non comparés.

**Suite complète finale : 2 497 tests / 289 fichiers, 3 847,957 s**, sur
`fa9dbe3` : **deux échecs, zéro erreur, 16 ignorés ; suite non verte**.
Les deux échecs sont reproduits à l'identique sur la référence exacte
`881db69` : voix inconnues (`test_constater_rumeurs`, trois voix au lieu de
deux) et stabilité de Lucien (`test_dynamique_besoins`, trois lieux au lieu
d'un). Reprises branche/base et mondes/textes conservés ; aucun oracle modifié.
Deux lancements partiels antérieurs interrompus (raccord au juge, puis reprise demandée sur 224/225).
Le banc porte sur `7c46d64` ; seule la validation du champ `null` a ensuite
changé, sans effet sur les états valides.

**Limites et réserve avant fusion.** Pas de gain prouvé sur l'occurrence
historique exacte. Une ancienne sauvegarde ayant déjà perdu suspension et
suffixe ne permet pas d'en reconstruire la cause. Une restauration sans
moyen admissible libère la garde, sans réussite promise. L'identité et la fin
attestée des sources sans demande typée gardent les limites du 213.
Surcoût et alerte d'agenda restent à relire ; aucune garantie universelle.
