# Lot 374 — position crue comme hypothèse datée

31 octobre 2026, PC fixe, branche `codex-position-hypothese`. Reprise demandée
après réserve du premier banc ; **fusion suspendue jusqu'à analyse du nouveau banc**.
`origin/integration 3999bb3a` fusionné sans conflit dans `b3233153` (S1c–S1e, 386–389).
Bruts : `C:/Users/msics/donjon/artifacts/position-hypothese-374/`, reprise dans `reprise/`.

**Contrat commun.** La dernière position d'autrui reste un indice après expiration.
`esprits.confiance_position` lit `confiance_initiale × 2 ** (-âge / demi_vie)` depuis
l'observation d'origine, sans cumul par tick. `data.positions_hypotheses` conserve
seuil **0,5**, demi-vies **15/60/120 min** selon mobilité crue : mobile, posée, retenue.
Soi, objets et feux exclus. Aucune position réelle lue pour planifier.

`_lieu_cru`, `croit_present`, `_chercher`, `_normaliser_suites` et `_agir` partagent
ce contrôle ; règle, seuil franchi et consommation entrent dans `_entrees`.
Le préfixe typé conserve sa progression sous le même but/motif/demande.
Inspection, appel, question et constat d'absence consomment la piste expirée.
Le repère `croyances[sujet].lieu.hypothese_consommee={minute,lieu}` survit à
l'absence et aux anciens relais. Une preuve plus récente peut le lever ; le temps seul non.
Une inspection retrouvant la même position clôt aussi son propre résultat : son
rafraîchissement ne programme pas un autre essai quinze minutes plus tard.
Un bruit simplement attribué conserve date et origine ; il ne vaut pas voix reconnue.
Les témoins consommés cessent de déclencher une recherche furtive. Un contact
requis garde la recherche commune, bornée par ses lieux déjà vérifiés.
Les portes et vues mémoire S1a–S1e sont conservées ; aucun épisode écrit hors porte.

**Attribution sur captures rechargées.** Le rejeu ancien crue 42 reproduit les
empreintes de `7986b7d2`. Aubin : **24→54 passages de salle** dans la première heure
(les autres lignes de déplacement ne sont pas des passages). Deux questions sur
Ilse à **10800/10926** réutilisent sa voix de minute **3**, puis une inspection
à **11733** la retrouve. Le nouveau contrat consomme la première tentative.
Brune crue 1985 : à **190**, inspection d'Aubin vu à **175** ; cette inspection
le revoit au même endroit à 190, puis l'expiration fait renaître l'agenda à **205**.
C'est une répétition corrigée, couverte à 190/205/220/235, sauvegarde et rendu compris.
Brune crue 2024 : à **137384**, contact interrompu, case d'Ilse inconnue ; à
**137391**, nouvelle localisation acoustique **[0,12]**, refus levé et proximité
reprise. Ce retour reçoit une entrée spatiale nouvelle, conservée dans les captures.
Lucien mine 1985 : abri→repos à **102**, repos→abri à **108**, sans quitter le
baraquement ; besoin de repos **90,1→78,1**, Mathe revue à **101/107**.
Ce retour suit un besoin satisfait et une présence fraîche, pas une piste expirée.
La ventilation exhaustive des **13→46 appels d'auberge** et **9→38 de mine**
reste à consolider après les captures détachées.

**Tests et mesures.** Auberge 371/7 à 240 (Lucien cru au couloir depuis 174), mine
69/7 à 470 (Rémy cru au baraquement), variantes parti/resté : exécution réelle,
monde/croyances/rendu/scène après recharge ; pas d'oracle de position cachée.
**31 tests position/mémoire/témoins verts** avant la dernière fusion, dont 12 de
position : consommation, vieux relais, bruits attribués, nouvelle voix, agenda et découpage.
Les **12 tests position passent aussi après la fusion 3999bb3a** (8,600 s).
Première passe de voisins : **64/65**, 262,384 s. L'échec de texte bloc/découpé de
`test_ilse_capture_141000_pas_de_reprise_par_la_minute` est aussi reproduit
sur **a50bbd95 avant ce correctif** ; égalité du monde conservée. Après dernière
fusion, ce test et `test_contenant_dans_une_autre_salle` sont reproduits rouges
sur la base **3999bb3a**, toujours sur le texte (preuve `base-3999.stderr.txt`).
Leurs oracles restent intacts. Nouvelle passe ciblée, puis attribution et mêmes
**16 nuits × 4 h**, deux travailleurs, priorité réduite, contre **3999bb3a**.
La référence historique `b83f5a59` est relue depuis le rapport précédent : ni rejeu,
ni assimilation à un comparatif isolant le lot sur l'intégration actuelle.
Pas de suite complète ni Luna ; pas de comparaison CPU avec des références en cache.

**Relance.** Le lancement du 30 octobre à 22:14 a échoué avant tout calcul : racine
absente de `sys.path` dans `reprendre_position_374.py`. Racine ajoutée avant les
imports métier, démarrage par `-m`, priorité sous le `try/finally`, fin atomique
même sur erreur et traces début/fin avec PID. Un second défaut de contrôle est
corrigé : les échecs hérités déclarés ne bloquent plus l'étape de capture.
Le contrôle du redémarrage a repéré une référence de test inexistante, retirée
de la liste ; son arrêt a bien écrit le fichier de fin d'échec.
Fin de la nouvelle relance : `C:/Users/msics/donjon/artifacts/position-hypothese-374/fin-consommation-relance.json`.
Aucune certification d'absence de boucle ni validation de fusion avant analyse.
Demi-vies non calibrées. Forme S0 : mobilité/consommation dans la croyance,
confiance dérivée, cause de vérification dans le plan sauvegardé.
