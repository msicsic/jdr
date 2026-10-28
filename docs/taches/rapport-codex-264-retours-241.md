# Lot 264 — deux retours du compteur 219

28 octobre 2026, laptop. **Branche `codex-retours-241`, non fusionnée**,
base `8ac7b46` vérifiée, arbre initial propre. Diagnostic seul : aucun code
du jeu modifié. Départs tirés, **12 h**, joueur passif en `galerie` (mine
2024), puis `chambre_cloche` (hameau 7). Un seul calcul à priorité réduite,
nuits successives ; ni Luna, suite complète, ni banc comparatif.

Les archives 241 sont absentes du laptop. Les deux nuits actuelles terminent
sans les retours exacts annoncés à 613/682 ; cela ne démontre pas une correction
générale et n'identifie pas le lot responsable du changement de trajectoire.
Reproduction historique sur **`c870c8b` détaché**, avec les mêmes paramètres.
Bruts, sondes et captures : `C:/Users/msics/donjon/artifacts/retours-264/`.

**Bram : autre moyen, retour justifié.** Sur `c870c8b`, à **367800** (613 min),
le but lumière prévoit l'achat des `chutes_serrurier` à Odon pour alimenter
le poêle. À **367825**, Odon est réellement au bureau, Bram au baraquement ;
`echanges.executer` / `pnj._rate` enregistrent son absence (`lieu=null`,
source `essai`). `manque` porte l'étape `acheter/odon/chutes_serrurier` ;
aucun `renoncer`, `renoncements={}`. `choisir` dément le plan et choisit la
garde du bureau. À **367860**, après le trajet de retour, le but lumière
revient par **`confier/mathe`, chandelle allumée**, sans nouvelle externe
depuis l'abandon : c'est un autre recours, pas la réhabilitation de l'achat.
Mathe refuse aussitôt (`impossible`), cause conservée dans `refus` avant le
retour à la garde. Aucune reprise de cet achat ni boucle durable n'est prouvée.
Le compteur retrouve exactement son alerte `repetition_sans_entree_nouvelle`,
mais n'atteste pas le changement de moyen. Il devrait distinguer les moyens
admissibles d'un même but, conformément à `renoncement_tient`, sans inventer
une nouvelle entrée externe.

**Gorm : rendez-vous accompli, retour justifié.** À **409379** (682 min),
le plan prévoit `engager/seve` pour le brasero. À **409498**, l'échange
« Ici, viens ! » / « J'arrive ! » établit `rejoint={qui:seve, jusqu_a:685,
vient:true}`. À **409723**, `_attendre_qui_vient` substitue l'attente de Sève
au recours ; ni refus de ce service ni obstacle de renoncement n'est alors
retenu. Sève est arrivée à **409678** ; Gorm se tourne vers elle à **409718**,
puis `appel.retrouves` clôt réellement le rendez-vous à **409744**, avant
le retour à `engager/seve`. La chronique dit « retrouve Sève, comme convenu ».
La demande est ensuite effectivement prononcée et refusée (`impossible`,
cause enregistrée). Ce retour ne rompt donc pas une attente encore valide.
L'alerte 219 `non_justifie_retour_etat_initial_exact` est reproduite :
`rejoint` fait **absent → présent → absent**, sans changement des valeurs
de croyance comparées. La sonde `_est_accompli` ne reconnaît pas `attendre` ;
elle devrait reconnaître la clôture attestée du rendez-vous intermédiaire,
plutôt que certifier une répétition par la seule égalité des états extrêmes.

**Preuves et limites.** Quatre nuits achevées, zéro plantage, **336 captures**
avec monde et rendu joueur identiques après sauvegarde/rechargement
(88 actuelles, 248 historiques). Les captures historiques comprennent
l'avant-abandon et l'avant-retour : Bram `087_367825` / `089_367860`,
Gorm `105_409723` / `109_409744` ; chacune possède son rendu avant/après.
Traces des choix/gestes, chroniques, épisodes, alertes et contrôles de recharge
restent dans les bruts. Ces deux alertes sont des **faux positifs du compteur**,
pas une preuve de défaut moteur ; aucun correctif ajouté. Pas de garantie
générale d'absence de boucle, ni d'audit des autres alertes. Aucun calcul actif.
