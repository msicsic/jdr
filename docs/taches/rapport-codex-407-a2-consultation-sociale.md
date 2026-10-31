# Lot 407 — A2, consultation sociale

31 octobre 2026 — `codex-a2-consultation-sociale`, base `integration`
`b4130dc3412e1a3d384978ef9d78474b0074a3ac`, non fusionnée.

**Invariant et changement.** `contrats_consultation.py` réunit sens, champs,
schéma, typage moteur et rendu public de `qui`, `localisation`, `ressource` et
`reclamer`. `paroles` et `comprehension` réemploient ce contrat ;
`commandes.consultation_locale` construit les contenus canoniques des menus
information/comptes, par deux raccords dans `dialogues`. `operations.py` reste
inchangé : ces actes sont des paroles, pas des étapes de manœuvre.
Un champ voisin ne remplace pas le sujet requis d'une recherche ; le sujet
vide reste légal pour réclamer des pièces. Champs supplémentaires, valeurs
non textuelles et sujets manquants portent un refus avec champ/reçu/accepté.
Les champs interdits sont refusés avant les sujets manquants. Le rendu des
besoins suit la normalisation moteur, en conservant la distinction entre
recherche lexicale libre et référence exacte du menu.

**Mécanique.** Croyances du témoin, personne connue, objet réclamé, adresse,
audience, règlement du dû, refus retenus et sauvegardes gardent leurs règles.
Une question sur le dû peut déclencher son règlement ; les mots seuls ne
choisissent aucun acte. Aucune règle de scénario, consigne supplémentaire,
revue ou registre d'esprit ajouté ; pas de changement de `social`/`voix`/`memoire`.

**Preuves.** Neuf nouvelles méthodes : `ressources/0` (bois à Aubin), lampe à
l'auberge, deux localisations crues mais fausses, `ressources/2` et les
règlements/refus du banc comptes. Faux pendants : question au MJ sans parole
de Corvus, mêmes mots sans acte typé. Vraie boucle console/PontWeb, sauvegarde
avant affichage, « Compris », réponses et vues après reprise ; parité des
raccourcis et charges explicites, schéma réellement émis, refus sans mutation.
Deux minutes en bloc ou huit tranches avec recharge donnent le même monde
complet et les mêmes vues. Le montage initial de localisation a été corrigé
pour fixer le lieu et les coordonnées, sans changer les attentes.

**Mesures et raccord du 403.** Passe initiale : **128 tests sur 13 fichiers**,
3 846,59 s, trois échecs et une erreur (`tests.json`). Deux sous-cas imputables
au lot concernaient l'ordre des refus, corrigé sans changer leurs assertions.
Les deux autres anomalies (schéma `rembourser`, don à une voix sans
confirmation) sont reproduites sur la base exacte : **27 tests, un échec et
une erreur**, 69,50 s (`tests-base.json`). Leurs corrections de tests sont
reprises **à l'identique de `fc370ec6`**, déjà fusionné par le 403 : champs
absents explicitement interdits, refus sans mutation, aperçu sans transfert
puis confirmation du don. Les assertions sont conservées et renforcées.
Reprise finale : **14/14** contrat/contenus en **204,65 s** (`tests-finaux.json`)
et **27/27** contenus/corrections de parole en **68,33 s**
(`tests-raccord-403.json`), soit **36 méthodes distinctes**, zéro échec,
erreur ou ignoré. Les autres fichiers verts ne sont pas relancés.

**Empreintes identiques**, chronique, mesures et monde complet : **huit nuits
par version, 2 h × 1985/7/42/2024 × Relais/auberge**, zéro divergence ou
plantage. Base `b4130dc3` puis branche `39ef4ee5`, `PYTHONHASHSEED=0` ; référence
calculée une fois puis cachée, branche non cachée. L'avis Relais 2024 « à
expliquer » existe des deux côtés. La correction ultérieure ordonne seulement
les refus invalides, sans changer les charges admises ni leurs effets : pas
de nouvelle campagne. Deux travailleurs au plus à priorité réduite, calculs
longs détachés ; ni suite complète ni Luna, aucun gain de vitesse revendiqué.
Bruts : `C:/Users/msics/donjon/artifacts/a2-consultation-sociale-407/` ;
`fin.json` conserve le résultat initial, `conclusion.json` consigne la reprise.

**Limites.** La fidélité du choix de Luna reste hors A2 ; les faux pendants
légaux ne déclenchent aucune enquête. Les revues actuelles restent en place,
A4/A6 hors lot ; connaissance et audience dépendent du contrôle moteur.
Seul recouvrement repris : les deux tests du 403 ; `etat-dev.md` reste partagé.
Vérification du lot terminée ; fusion et vérification groupée au superviseur.
