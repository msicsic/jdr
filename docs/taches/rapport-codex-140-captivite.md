# Rapport Codex 140 — captivité vécue, fin de 4d

Branche `codex-captivite`, **non fusionnée**, base voulue `9aab62a` (lot 136,
`codex-enfermer`, non fusionné). Aucun Luna, scénario modifié, nouveau choix autonome,
ni modification de `main`, du worktree d’intégration ou des fichiers réservés aux lots 138/139.
Python du dépôt principal, deux calculs au plus à priorité réduite. Aucune clé de signature
Git configurée : commit non signé.

**Invariant** : `tenir.captif` qualifie les liens ou l’absence d’issue crue praticable.
Les verrous réellement invisibles ne sont jamais consultés : croyances pour les PNJ,
verrous visibles (déjà montrés au rendu) ou mémoire pour le joueur. Une clé portée permet
de sortir ; les liens empêchent d’en profiter. `deliberation.ecart_securite` ajoute la cause
`captif`, un point par minute, avec les autres causes ordinaires. `vecu` enregistre les
conditions et solde les durées exactes ; la fin des liens actualise le vécu de la victime à
l’échéance du geste. `corps.vivre_captivite` appelle `briser` : un point de jet de VOL perdu
par heure captive, cinq au plus, un rendu par deux heures libres au calme. Les restes en
dixièmes sont sauvegardés. Le joueur éprouve l’inquiétude dans son corps et sa fiche ;
la fiche montre aussi sa volonté éprouvée, après rechargement. Aucun nouvel usage de VOL.

**Épreuves** : bureau et réserve de la mine du lot 136, sécurité croissante à la minute,
heure captive puis deux heures de répit ; même `data` complet et rendu après laps continus
ou découpés et recharges. Aubin ligoté au Relais ; joueur captif puis libre, même état et
fiche après recharges et découpage ; malus de jet VOL existant ; saturation et interruption
du répit ; croyance fausse d’un verrou malgré la porte ouverte et enfermement ignoré ;
clé portée par PNJ/joueur, neutralisée par les liens. Les choix et bavardages sont suspendus
pendant les épreuves de durée pour ne pas terminer la captivité avant une heure ; les corps,
perceptions, sécurité, horloge, validations et sauvegardes sont réels. Les épreuves d’évasion
et de secours du lot 136 restent vertes.

**Mesures** : 56 tests ciblés verts sur cinq fichiers (49 existants et sept nouveaux),
après reprises des fixtures des nouveaux tests. Suite complète unique : **2 101 tests**, 230 fichiers, **1 126,77 s**, deux échecs
MiMo historiques `6 != 5` (`test_fournisseurs_jeu`, `test_restes_fusions`), zéro erreur
et zéro test ignoré. Ces échecs sont déjà documentés sur la base du lot 136 ; aucune
seconde suite complète ni nouveau rejeu de base. La dernière correction de l’horloge
de l’épreuve de croyance a été vérifiée par la reprise des sept nouveaux tests (5,90 s).
Banc rapide 4 h × Relais/crue/mine/auberge × quatre graines : **16/16 identiques**,
état final complet (empreinte), relevés, récit, souvenirs, chronique, mesures, boucles et
constats ; seules les durées de calcul sont écartées de la comparaison. Zéro plantage,
usurpation ou violation. Les seize références manquantes ont été calculées une fois puis
cachées ; aucun rejeu de référence. Le premier banc a révélé le détenteur d’une clé compté
captif ; correction commune de l’issue praticable, contre-épreuve des quatre mines sur la
branche seulement. Aucune conclusion de performance sur ce poste partagé.
Bruts : `artifacts/captivite-140/`, notamment `identites.json`, `banc-final.json`,
`banc-mine-final.json`, `cibles-valides.json` (consolidation des reprises) et `suite.json`.

**Limites** : le calme reprend les conditions ordinaires : pas d’effort, de prise, d’eau
ni de danger perçu ; sécurité non croissante pour les PNJ, lumière pour le joueur. Un répit
interrompu repart à zéro. Les conditions sont relues par les gestes et les minutes comme
le reste du temps vécu ; un changement extérieur sans geste peut donc attendre la frontière
de minute. La récupération est éprouvée avec un foyer alimenté et sans appels de détresse.
L’inquiétude corporelle du joueur n’ajoute aucun malus autonome. Aucune garantie narrative
Luna supplémentaire ; les limites des lots 126/134/136 restent applicables. 4e et 4f restent
à faire. Livraison : branche `codex-captivite` poussée, commit non signé, sans fusion.
