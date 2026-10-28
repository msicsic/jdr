# Lot 273 — demande adoptée et moyen démenti

29 octobre 2026. **Branche `codex-demande-adoptee`, non fusionnée**,
base `c9459ce` ; référence de banc demandée `0e3e626`.

**Invariant corrigé.** Un échec de geste ne certifie pas la fin d'une
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

**Vérifications détachées en cours**, PID **31584**, un processus réduit : fichiers
`test_echelle_choix`, `test_dynamique_besoins`, `test_reessai*`,
`test_contrats_internes`, `test_secours_acquitte` ; puis banc 4 h,
Relais/mine/auberge/crue/hameau × graines 1985/7/42/2024. Référence
`0e3e626` réutilisée en cache si disponible, seules nuits manquantes jouées
une fois, puis branche ; sonde actuelle 265/271 identique des deux côtés.
Le bilan comparera les suspects 219 nuit par nuit et le cas Aubin. Aucun
résultat de ce banc n'est encore revendiqué. Ni Luna ni suite complète.

Bruts : `C:/Users/msics/donjon/artifacts/demande-273-sol/`,
`tests-contrat-empathie.json`, `tests-cibles.json`, `banc.json`, `bilan.json` ;
**fichier de fin attendu `fin.json`**, écrit en dernier, avec `ok` et les
éventuelles erreurs. La garantie est celle du contrat de demande typée et
des cas vérifiés, pas une certification générale de stabilité des PNJ.
