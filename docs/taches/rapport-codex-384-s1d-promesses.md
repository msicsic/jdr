# Lot 384 — S1d, promesses, prêts et travaux payés

30 octobre 2026 · `codex-s1d-promesses` · base exacte `integration 31f80725`.
Code figé pour les mesures : `37069459`. `origin/integration` vérifiée à cette base.

**Invariant et code.** Les consultations des épisodes de parts promises, travaux
payés, suivi d'engagement et prêts passent par les requêtes nommées de
`donjon/memoire.py`. Elles renvoient des copies profondes ou des booléens.
`dernier_travail_paye` départage les accords et créances par l'ordre historique
de la liste, sans trier les dates ; `suivi_engagement` s'arrête à la parole suivante
de même condition. Les politiques de récence, confiance et satisfaction restent
dans leurs consommateurs. La consultation relationnelle d'une remise conserve
l'installation historique de l'esprit du bénéficiaire.

`juger_reclamations_pret` marque chaque occurrence avant d'appeler sa conséquence
métier. L'itérateur parcourt le stock vivant : une insertion réentrante et son
éviction conservent leur effet historique sur les indices suivants. Aucun crochet
supplémentaire, aucune copie perdue lors d'un marquage. Les écrivains continuent
de passer par la façade `esprits.memoriser` et la porte d'insertion S1a. Liste,
plafond 40, clés, preuves, sérialisation et autorité d'`agendas` sont inchangés.

**Contrôle AST et tests.** Neuf expressions retirées de la fixture S1a (**78 → 69**),
sans nouvelle exemption. Le contrôle des mutations couvre les familles portées,
y compris la sélection par indice. Cinq nouveaux tests contrôlent copies imbriquées,
pureté, ordre sans tri chronologique, arrêt du suivi, éviction, remise et réentrance
à quarante occurrences. La première exécution restreinte rencontre la restriction
Windows sur une sauvegarde temporaire ; les calculs suivants sont autorisés hors
de cette restriction.

Quinze fichiers ciblés : les six du brief, `memoire_socle`, `echanges_argent`,
`relations_graduees`, `lampes_parts`, `tache_promise_recours`, `parts_achetees`,
`double_promesse`, `esprits`, `planification`. La capture réelle Relais 42 avant
l'achat à la minute 151 est renforcée en cinq minutes entières ou découpées avec
recharges. Autres chaînes : part livrée par Aubin et tâche ponctuelle datée à
l'auberge. Comparaisons : état complet et ordre JSON, lignes, rendu, scène et
registre des paroles après recharge.

Première passe : **192 tests, trois échecs, aucune erreur** (569,2 s). La fixture
nouvelle remplit à tort le stock d'appels, ce qui déclenche la migration historique
du secours à la recharge : elle utilise maintenant des examens. Deux autres échecs
se reproduisent à l'identique sur la base exacte, modules vérifiés dans la copie
isolée (`attribution-base-exacte.json`, `attribution-synthese.json`) : l'assertion
« Gaspard reste près de Lucien » est déjà suivie par 375 ; les notifications sonores
anonymes du parcours Relais comptent onze lignes de plus en bloc. Cette limite
antérieure n'est pas corrigée en S1d. Le test renforcé garde les égalités intégrales
d'état, ordre JSON, rendu, scène et paroles sauvegardées, sans revendiquer l'égalité
de ces notifications. Les deux fichiers modifiés sont en nouvelle vérification ;
les treize autres ne sont pas relancés.

**Empreintes et livraison provisoire.** Calcul détaché, séquentiel après les tests :
2 h × quatre graines 1985/7/42/2024 × Relais/mine/auberge/crue, référence exacte
`31f80725`, branche `37069459`, cache partagé. Deux processus au plus, priorité
réduite ; pas de suite complète ni Luna. Le lanceur s'arrête avant les empreintes
si les tests corrigés échouent. Aucun résultat d'identité ni conclusion de coût revendiqué
avant lecture du fichier de fin.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1d-384/` : `tests.json`,
`tests.log`, `tests-corriges.json`, `empreintes-base.json`, `empreintes-base.log`,
attributions et `fin-empreintes.json` écrit en dernier. L'ancien `fin.json` relate
l'arrêt initial, avant empreintes. Lanceur local ignoré : `artifacts/s1d-384/run.ps1`.
Recouvrement potentiel 374 : seules les lectures de promesses de `deliberation`,
`planification`, la façade `esprits.prete` et `echanges.tenu` sont modifiées ;
aucune localisation ni recherche changée. Aucun fichier de 380/381 touché.
Le contrôle syntaxique ne prouve pas tous les flux interprocéduraux de Python ;
autres lecteurs, rétention âge/importance et nouveau stockage restent hors lot.
**Lot non clos : résultats ciblés et empreintes à vérifier à la reprise.**
