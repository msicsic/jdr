# Lot 374 — position crue comme hypothèse datée

30 octobre 2026, PC fixe. Branche `codex-position-hypothese`, départ `b83f5a59`
(integration ancêtre `60f857c5`), non fusionnée. Bruts :
`C:/Users/msics/donjon/artifacts/position-hypothese-374/`.

**Contrat.** La dernière position d'autrui reste un indice, jamais une présence acquise
après expiration. `esprits.confiance_position` applique à la lecture
`confiance_initiale × 2 ** (-âge / demi_vie)`, depuis l'observation d'origine,
sans cumul par tick. `data.positions_hypotheses` sauvegarde seuil **0,5** et demi-vies
**15/60/120 min** : mobile, posée, retenue, selon les seules croyances de l'observateur
(repos, garde/guet, entrave, inconscience, issues crues verrouillées).
Relais sans rajeunissement ni renforcement. Soi, objets et feux exclus ; anciens faits : mobile.

**Réalisation.** `_lieu_cru`, `croit_present`, `_chercher`, `_normaliser_suites` et
`pnj._agir` partagent l'hypothèse ; seuil et règle entrent dans `_entrees`, devis
observateurs compris. Inspection/appel/question précèdent le suffixe incertain.
Le temps ne lève aucune exclusion de recherche.
Une inspection issue d'une position expirée conserve sa cause typée et progresse
sous le même motif, but et demande ; nouvelle piste, présence apprise, échec
retenu, refus ou préemption la revalident. Les recherches déjà inconnues gardent
leur contrat. Un préfixe ne vaut pas terminal de devis de part.

**Preuves.** Auberge 371/7, à **240**, Mathurine situe Lucien au couloir depuis
**174**, alors qu'il est au grenier. Mine 69/7 à **470**, Bram situe Rémy au
baraquement, alors qu'il est à l'entrée. Positions cachées modifiées sans changer
le plan ; variantes parti/resté exécutées, monde/croyances/rendu/scène rechargés.
La première mesure a révélé **112 passages d'Aubin en une heure**, crue 42 :
recomposition remettant un préparatif devant l'inspection. Capture corrigée :
Ilse revue à **19**, **8 passages en six minutes**, monde et textes identiques
en bloc/découpé. Captures et diagnostics conservés.

**Tests.** **90 distincts / 13 fichiers** : **44 finaux verts**, 150,032 s
(`tests-contrat-final.json`), 46 autres voisins verts à la passe précédente.
L'oracle de déplacements confondait les recherches : **11** passages principaux,
**21** pour Corvus, **1** pour Bram
(`passages-odon-typage.json`). Plafond **28 inchangé**, désormais contrôlé pour
chaque recherche ; appels, monde et découpage inchangés. Pas de suite complète ni Luna.

**Banc final (`7986b7d2`).** **16 nuits × 4 h**, quatre graines, Relais/auberge/mine/crue :
**zéro plantage et usurpation**. `VERIFIER` Relais 7, **1 h vert / 36,882 s**.
Comparaisons `origin/main` (`0bad2272`) et base exacte, **32 références relues du cache** ;
branche jouée une fois, deux travailleurs, priorité réduite ; pas de comparaison CPU au cache.
Main local `c870c8b4` incompatible avec l'audit, trace conservée.
Contre la base, appels totaux **6→5 / 13→46 / 9→38 / 35→47** ; les nouvelles inspections
et questions vérifient notamment les témoins anciens. Aubin crue 42 : **54 passages
sur la première heure**, contre 112 sur le premier correctif et 24 sur la base ;
la répétition des préparatifs devant la même inspection est corrigée.
Mesures et chroniques dans `final/`, lecture consolidée dans `bilan-final.json`.

**Réserve avant fusion.** Le critère « aucune nouvelle boucle » reste **non certifié** :
l'audit strict passe de **0 à 3 retours suspects**, de 11 à 43 entrées à expliquer.
Lucien mine 1985 revient à l'abri après repos (90,1→78,1) ; Brune crue 2024 reprend
la proximité d'Ilse après un contact manqué puis la rejoint effectivement.
Brune crue 1985 réactive son agenda à 190 puis 205 avant de le rendormir : ce
réessai périodique reste insuffisamment attribué. Les alertes de questions répétées
et appels nombreux restent visibles ; **livraison terminée, validation de fusion réservée**.
Pas de nouveau calcul en cours. Demi-vies initiales non calibrées.

**S0.** Aucun registre ajouté :
`croyances[sujet].lieu.mobilite`, confiance initiale conservée, confiance dérivée
à la lecture ; l'inspection garde `contenu.verification={type:position, lieu:…}`
dans le plan sauvegardé, validé par `esprits.verifier`. Recouvrement **372** :
`esprits.py` ; revoir la fusion. Pas de fichier commun attendu avec 365/369/370.
