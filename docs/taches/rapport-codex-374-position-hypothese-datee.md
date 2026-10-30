# Lot 374 — position crue comme hypothèse datée

30 octobre 2026, PC fixe. Branche `codex-position-hypothese`, départ `b83f5a59`
(descendant d'`integration 60f857c5`), non fusionnée. Bruts :
`C:/Users/msics/donjon/artifacts/position-hypothese-374/`.

**Contrat.** La dernière position d'autrui reste un indice, jamais une présence acquise
après expiration. `esprits.confiance_position` applique à la lecture
`confiance_initiale × 2 ** (-âge / demi_vie)`, depuis l'observation d'origine,
sans cumul par tick. `data.positions_hypotheses` sauvegarde seuil **0,5** et demi-vies
**15/60/120 min** : mobile, posée, retenue, selon les seules croyances de l'observateur
(repos assis, garde/guet, entrave, inconscience, issues crues verrouillées).
Un relais conserve l'origine et ne renforce pas le coefficient du témoin. Soi,
objets et feux restent hors vieillissement ; anciens faits sans classe : mobile.

**Réalisation.** `_lieu_cru`, `croit_present`, `_chercher`, `_normaliser_suites` et
`pnj._agir` partagent l'hypothèse ; seuil et règle entrent dans `_entrees`, devis
observateurs compris. Inspection/appel/question précèdent le suffixe incertain.
Les exclusions de recherche ne sont jamais levées par le seul temps.
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

**Tests.** **90 distincts / 13 fichiers** exercés : **44 concernés finaux verts**,
150,032 s (`tests-contrat-final.json`), les 46 autres voisins verts à la passe
précédente (`tests-contact-finaux.json`). L'oracle de déplacements à la mine
comptait toutes les vérifications contre un plafond unique. Attribution réelle :
**11** passages principaux, **21** pour Corvus, **1** pour Bram
(`passages-odon-typage.json`). Plafond **28 inchangé**, désormais contrôlé pour
chaque recherche ; appels, monde et découpage inchangés. Pas de suite complète ni Luna.

**Banc.** Sur `6614e692` : **16 nuits × 4 h**, quatre graines et quatre scénarios,
zéro plantage/usurpation ; `VERIFIER` Relais 7, **1 h vert / 37,982 s**.
Contre la base : appels totaux Relais/auberge/mine/crue **6→5 / 13→45 / 9→29 / 35→36**,
deux retours suspects, et rafale crue 42 corrigée ensuite. Références `origin/main`
(`0bad2272`) et base exacte en cache ; le vieux main local `c870c8b4` était incompatible
avec l'audit (`agendas.enfants`), trace conservée. Nouvelle mesure du contrat final
dans `final/`, mêmes références réutilisées ; deux travailleurs, priorité réduite.
Fin attendue : `C:/Users/msics/donjon/artifacts/position-hypothese-374/fin-final.json`.

**Limites/S0.** Réglage initial non calibré. **Boucles non encore validées sur le
contrat final : pas de fusion avant lecture.** Aucun registre ajouté :
`croyances[sujet].lieu.mobilite`, confiance initiale conservée, confiance dérivée
à la lecture ; l'inspection garde `contenu.verification={type:position, lieu:…}`
dans le plan sauvegardé, validé par `esprits.verifier`. Recouvrement **372** :
`esprits.py` ; revoir la fusion. Pas de fichier commun attendu avec 365/369/370.
