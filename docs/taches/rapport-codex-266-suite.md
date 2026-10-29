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
Les assertions existantes restent strictement identiques (comparaison AST,
`assertions.json`) ; une assertion d'absence de mutation est ajoutée.

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
| Pas compagnons, vente | **Aucun `pres`**. Maël garde son secours alimentaire, achète une part au bon prix (2, avec remise de part), revient vers Brune et reçoit l'offre à `802`, avant Aubin (`912`). L'ancien recours achetait au prix 1, échouait et le laissait à l'échoppe : Aubin `1034`, Maël `1240`. Le nouvel itinéraire est justifié. Prémisse commerciale désormais extraite de la base réelle à `t=656`, juste avant l'offre à Ilse, après ce préambule alimentaire historique. L'admission du service est vérifiée explicitement par la requête commune, sans mutation ; la vente reste choisie par la vie autonome. Ordre, prix 8, propriété et absence de promesse restent exigés. Aucun geste retardé. |
| Pas compagnons, promesse | Même décalage alimentaire que « service non défait » ; même helper de scène désormais apaisée. Promesse prononcée, engagement tenu, ancrage et sauvegarde restent exigés. |
| Pousser, témoin | Aubin adopte `pres Brune` à `t=30`, se retourne et acquiert une source `vu` ; sans peur : vert. Prémisse : Aubin sans souci spontané pendant ce geste, donc reste tourné vers le mur ; l'oracle de transmission par Ilse est conservé. |

**Validation ciblée finale : 193 tests / dix-neuf fichiers verts, consolidés**
sur le worktree isolé `f637396` + correctif de reprise. Les dix-huit fichiers
inchangés étaient déjà verts ; seul le fichier commercial encore en échec
a été repris : **20 tests en 8,437 s**, verts. Aucune assertion existante
modifiée. La capture `tests/data/commerce-266-hameau-1985-avant-offre.json.gz`
remplace le délai de disponibilité `libre=600`, qui ne stabilisait pas l'ordre
sur la fusion. La scène reste rechargée et sa requête d'admission est contrôlée
sans effet sur le monde.

La première passe de branche (488,127 s) avait trois autres échecs sur deux
méthodes : mémoire de planification sur une heure (garde de boucle PNJ) et
occasion de demande d'Aubin (Relais/hameau). **Tous trois reproduits aussi
sur `184ad5d`, avant cette reprise**, et tous verts sur la fusion corrigée.
Les corrections de présence de l'intégration n'ont pas été recopiées sur la
vieille branche ni modifiées. La première passe de fusion (499,194 s) n'avait
plus que l'ordre commercial en échec ; ce dernier est désormais vert.

Les calculs étaient achevés avant le redémarrage Windows signalé à 03:32.
Leurs résultats ont été récupérés, sans relance des dix-huit fichiers verts.
Ce redémarrage n'est pas compté comme un plantage du jeu.

Quatre tests ajoutés : cible décédée et préfixe de devis
sur deux scènes (Relais/mine), absence de réveil sans recours, cadence de
première perception/geste propre/événement extérieur. Les cinq cas réels de
continuité restent rechargés, avec une vraie fin par démenti.

Bruts : `C:/Users/msics/donjon/artifacts/rester-266/suite-reprise/`
(`diagnostic/{base,branche,sans-peur,sans-eveil,ancien-echec,corrige,premisse}/`,
`analyse.json`, `assertions.json`, `tests.json`, `tests.log`, `rechute/`,
`essai-corrige/`, dont `consolides.json`, `pas-compagnons-final.json`,
`fin-cloture.json`). Commits locaux, branche non fusionnée ; validation ciblée
terminée, suite complète à relancer par le superviseur.
Le banc vingt nuits **2 → 0** reste celui du code `21d5f5b` et n'est pas une
mesure de cette reprise. Pas de nouveau banc ni de Luna ; la suite complète
de fusion revient au superviseur.
