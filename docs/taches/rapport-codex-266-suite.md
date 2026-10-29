# Lot 266 — reprise des échecs de la fusion d'essai

Branche `codex-rester-pres`, **non fusionnée**. Essai `f637396` (intégration
`0bad227` + branche `184ad5d`) : neuf échecs et deux erreurs. Les **onze tests
passent sur la base `7404d2d` et reproduisent tous leur échec sur `184ad5d`**,
isolés, deux processus à priorité réduite. Les fichiers de tests concernés
étaient identiques sur ces deux arbres. Aucune suite complète relancée.

**Corrections communes.** `condition_valide` admet une dépouille comme cible
d'une condition de proximité déjà enregistrée : sa mort n'invalide ni la
sauvegarde ni la sortie historique de la demande ; son état *perçu* décide de
la fin. `_pulsion(pres)` passe ses moyens par `_couper`, comme les autres
pulsions : retrait des marqueurs de devis et coupure après le geste incertain.
Enfin, `retenir_detresses` renvoie un changement pertinent au lieu de réveiller
directement. La perception applique alors ses règles communes : première
perception et geste propre ne réveillent pas. Une nouvelle détresse réveille
seulement un secours admissible ou sa demande déjà adoptée. Aucun mécanisme
d'agenda ni règle de scénario modifié, aucun délai ajouté au moteur.

**Diagnostic de chaque cas.** La contre-épreuve « sans peur » retire seulement
les naissances de secours peur ; elle conserve leurs observations. Pour les
échecs restants, deux autres contre-épreuves isolent le réveil de rétention et
le maintien du parent sur moyen manqué. La contre-épreuve stricte de rétention
sur `184ad5d` laisse les réveils de relecture existants actifs : les deux tests
de lampe passent (`sans-eveil-retention-seule/`). L'ancien essai `sans-eveil/`,
qui retirait aussi ces réveils de relecture, n'est pas retenu comme preuve isolée.
Les assertions existantes restent
strictement identiques (comparaison AST, `assertions.json`).

| Test signalé | Cause prouvée ; traitement |
|---|---|
| Recherche/appels, mine 7 | Bram adopte `pres Gaspard` ; son plan contient un achat d'huile avec `suppose`/`part_estimee`. Sans naissances peur : vert. **Régression corrigée par `_couper`**, scène et assertions intactes. |
| Tuer, joueur ligoté | Ilse secourt Brune ; après le décès perçu, la sortie du contrat est déjà démentie, mais son ancienne condition échoue à la validation. Sans peur : vert. **Schéma corrigé**, scène intacte. |
| Lumière, lampe gardée | Lucien et Mathe secourent Rémy dès `t=0` : Rémy reste au baraquement obscur, lampe allumée. Retirer seulement les naissances ne suffit pas : les réveils supplémentaires changent encore le parcours. **Cadence corrigée** ; prémisse : Lucien/Mathe sans souci spontané dans ce seul parcours de lampe et d'abri propre. |
| Lumière, huile | Même cause ; secours dès `t=100`. Même correction et même prémisse. Remplissage, extinction au bureau, combustible, état/rendu rechargés toujours exigés. |
| Avis redits, mine 2024 | Mathe puis Rémy, Josse et Gaspard rejoignent Lucien : le circuit d'audience change. Sans peur : vert. Prémisse du seul parcours mine : aucun secours spontané ; les deux identités et leurs preuves d'audience restent exigées. |
| Recours prioritaire, capture | Brune rejoint Ilse, Aubin rejoint Gorm ; Aubin finit sous motif chaleur plutôt que sécurité. Sans peur : vert. Prémisse : abri historique isolé des projets nouveaux **et** du secours spontané. Même monde/vue bloc-découpé et séjour dans la lumière exigés. |
| Garde-manger, crochets absents | **Aucun `pres`**. Gorm conserve son secours alimentaire après moyen manqué et ouvre la réserve. Sans peur : échec ; ancienne clôture sur échec : vert. Trajectoire admissible de secours, pas un crochetage sans outil. Prémisse : aucun secours alimentaire de Gorm dans la scène de recours propre absent. |
| Service non défait, hameau 1985 | Sans peur : échec ; ancienne clôture sur moyen manqué : vert. Le secours alimentaire change l'heure d'allumage et la présence crue d'Ilse ; l'ancrage devient `None`, correctement enregistré comme inconnu. Prémisse du service accepté : Brune et Ilse sans besoins propres pressants avant son exécution. Ancrage, mobilité et non-extinction restent exigés. |
| Pas compagnons, vente | **Aucun `pres`**. Maël garde son secours alimentaire, suit Brune et reçoit l'offre à `802`, avant Aubin (`912`). Base : Aubin `1034`, Maël `1240`, ce dernier encore à l'échoppe. Ancienne clôture : vert. Pour conserver l'ordre commercial exigé, prémisse explicite : Maël encore occupé au départ, disponible à la première minute (`libre=600`, donnée de scène uniquement). Traits, positions, prix et assertions conservés. |
| Pas compagnons, promesse | Même décalage alimentaire que « service non défait » ; même helper de scène désormais apaisée. Promesse prononcée, engagement tenu, ancrage et sauvegarde restent exigés. |
| Pousser, témoin | Aubin adopte `pres Brune` à `t=30`, se retourne et acquiert une source `vu` ; sans peur : vert. Prémisse : Aubin sans souci spontané pendant ce geste, donc reste tourné vers le mur ; l'oracle de transmission par Ilse est conservé. |

**Première validation de branche : 193 tests, dix-neuf fichiers**, les neuf
signalés et les dix ciblés du lot, en 488,127 s. **Les onze échecs signalés sont
résolus**, les quatorze tests de proximité sont verts. Trois échecs restent
sur deux autres méthodes : mémoire de planification sur une heure (garde de
boucle PNJ) et occasion de demande d'Aubin (sous-cas Relais/hameau). Ce dernier
échoue aussi sur `184ad5d`, avant cette reprise. Le diagnostic comparatif de la
mémoire continue ; ces écarts ne sont pas déclarés corrigés.

**Vérification sur la fusion d'essai en cours :** worktree isolé à `f637396`,
avec seulement le correctif de reprise appliqué (`correction.patch`). Les
corrections de présence déjà fusionnées dans l'intégration y restent intactes,
sans les recopier sur la vieille branche. Les mêmes dix-neuf fichiers s'y
jouent après le diagnostic en cours, deux travailleurs réduits au plus.
**Fin attendue : `essai-corrige/fin.json` ; aucun verdict global avant ce bilan.**

Quatre tests ajoutés : cible décédée et préfixe de devis
sur deux scènes (Relais/mine), absence de réveil sans recours, cadence de
première perception/geste propre/événement extérieur. Les cinq cas réels de
continuité restent rechargés, avec une vraie fin par démenti.

Bruts : `C:/Users/msics/donjon/artifacts/rester-266/suite-reprise/`
(`diagnostic/{base,branche,sans-peur,sans-eveil,ancien-echec,corrige,premisse}/`,
`analyse.json`, `assertions.json`, `tests.json`, `tests.log`, `rechute/`,
`essai-corrige/`). Commit local de reprise ; validation de fusion encore en cours.
Le banc vingt nuits **2 → 0** reste celui du code `21d5f5b` et n'est pas une
mesure de cette reprise. Pas de nouveau banc ni de Luna ; la suite complète
de fusion revient au superviseur.
