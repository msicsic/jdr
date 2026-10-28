# Lot 273 — demande adoptée et moyen démenti

29 octobre 2026. **Branche `codex-demande-adoptee`, non fusionnée**,
base `c9459ce`, correctif poussé **`3ec23bb`** ; référence de banc demandée
`0e3e626`. **Validation incomplète : non prêt pour fusion.**

**Correctif proposé.** Un échec de geste ne certifie pas la fin d'une
demande adoptée. Dans `deliberation.choisir`, la collision avec `manque`
libère maintenant le plan de cette demande tout en conservant son identité,
son palier et sa provenance. La revalidation existante peut retrouver un
moyen, attendre sans geste, constater une fin par `_fin_demande` ou céder
à une priorité gagnante. Le plan démenti ne fournit plus de suffixe à
recopier, même si la recherche repropose sa tête. Les refus et renoncements
causaux restent contrôlés par les mécanismes existants ; aucun délai ajouté.
Aucun changement dans `planification`, `agendas`, `echanges` ou `signes`.

**Preuves ciblées : 21 tests verts (98,600 s, un processus réduit)** :
13 tests du contrat et huit tests d'empathie, fichiers modifiés entiers.
La capture réelle rechargeable **Relais 2024, 117503** est archivée sous
`tests/data/demande-273-relais-2024-117503.json.gz` : Ilse hors perception,
raison encore valide, appel effectif à `_reprendre_demande`, identité et
palier conservés, phase `continuer`, aucune sortie `dementie`. Le refus
`necessaire` ne tenant déjà plus, le planificateur repropose la demande de
part ; l'exécuteur conserve son interdiction de réessai dans la minute.
Sur les deux minutes suivantes, le retour perceptif d'Ilse est exercé sans
nouvelle naissance de la demande ni sortie.

Deuxième cas, **Mathé/Lucien dans la mine** : demande de secours adoptée,
bénéficiaire hors perception et nourriture constatée épuisée ; attente
persistante sans gestes. Un constat de nourriture disponible permet la
reprise hors perception, puis la part est effectivement servie et la faim
apaisée. Les deux cas contrôlent monde, rendu et scène après sauvegarde et
recharge ; laps entiers et découpés avec recharge donnent le même état.
Un démenti attesté par le corps cru et une vraie préemption demeurent des
sorties justifiées. Un autre test empêche la recopie d'un suffixe périmé.
L'ancien test imposant l'effacement a été conservé pour les intentions sans
demande typée. La scène d'auteur `scene_repas` isole la nourriture portée
pour les tests de repas et de préemption de ronde : leur réussite ne dépend
plus de l'abandon implicite d'une première demande visant une autre
ressource à racheter. La demande conserve sa condition exacte ; changer
d'objet cible n'est pas assimilé à un autre moyen de cette même condition.

**Calcul détaché terminé en échec**, un processus réduit, **398,712 s**.
Tests complémentaires : **28 succès / 29**, aucun échec d'assertion et une
erreur ; avec les fichiers modifiés, **49 succès / 50 tests distincts,
sept fichiers**. Détail : contrats internes **5/5**, dynamique des besoins
**9/10**, échelle du choix **4/4**, réessai obstacle **7/7**, secours acquitté
**3/3**. Les 29 tests complémentaires ont duré **398,297 s**.

L'erreur est dans
`test_dynamique_besoins.TenirTests.test_lucien_attend_une_information_apres_la_reprise_du_ballot`,
ligne 225 : `lire(m, "lucien")["recherches"]["anselme"]` lève
**`KeyError: 'anselme'`**. La recherche attendue par ce test n'est pas
présente au relevé. Sa cause et son attribution au correctif ne sont pas
établies : aucun contrôle de ce test sur la base n'a été exécuté dans cette
relecture. Cet échec reste à instruire avant de conclure le lot technique.

**Banc 4 h non lancé.** Le lanceur s'arrête sur le code de retour des
tests avant d'appeler le comparateur. Aucune des vingt paires prévues
(Relais/mine/auberge/crue/hameau × graines 1985/7/42/2024) n'a donc été
jouée par cette campagne ; `banc.json` et `bilan.json` sont absents. Aucun
compteur 219 par nuit, aucune absence de hausse ni disparition du suspect
Aubin sur une nuit entière ne sont démontrés. La preuve sur sa capture
117503 reste limitée au test ciblé décrit plus haut. La comparaison à
`0e3e626` avec la sonde 265/271 reste à effectuer après traitement du test.
Ni nouveau calcul, ni Luna, ni suite complète lancés lors de cette relecture.

Bruts : `C:/Users/msics/donjon/artifacts/demande-273-sol/`,
`tests-contrat-empathie.json`, `tests-cibles.json`, `tests-cibles.log`,
`fin.json` (**`ok=false`**, trace de l'arrêt avant banc). **Aucun calcul
actif.** La garantie reste limitée aux cas vérifiés du contrat de demande
typée ; aucune validation générale ni aptitude à la fusion n'est revendiquée.
