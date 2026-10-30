# Lot 384 — S1d, promesses, prêts et travaux payés

30 octobre 2026 · `codex-s1d-promesses` · base exacte `integration 31f80725`.
Code mesuré : `37069459`. À la clôture, `origin/integration dd133ece` est fusionnée :
seule la décision documentaire S0/3 change, aucun recouvrement moteur.

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
sans nouvelle exemption. Le contrôle des mutations couvre les familles portées et
la sélection par indice. Cinq nouveaux tests contrôlent copies imbriquées, pureté,
ordre, arrêt du suivi, éviction, remise et réentrance à quarante occurrences.

Quinze fichiers ciblés : les six du brief, `memoire_socle`, `echanges_argent`,
`relations_graduees`, `lampes_parts`, `tache_promise_recours`, `parts_achetees`,
`double_promesse`, `esprits`, `planification`. La capture réelle Relais 42 avant
l'achat à la minute 151 est renforcée en cinq minutes entières ou découpées avec
recharges. Autres chaînes : part livrée par Aubin et tâche ponctuelle datée à
l'auberge. Comparaisons : état complet et ordre JSON, lignes, rendu, scène et
registre des paroles après recharge.

Bilan : **191/192 verts**, seul rouge hérité de Gaspard, sans erreur ni saut.
Première passe : 192 tests, trois échecs (569,2 s) ; après correction de la fixture
et attribution, les deux fichiers modifiés repassent : **34/34 verts**, 53,2 s.
Les treize autres fichiers ne sont pas relancés. La fixture d'éviction utilise des
examens, car des appels artificiels déclenchaient la migration du secours à la recharge.
Les deux autres assertions échouent à l'identique sur la base exacte, modules
vérifiés dans sa copie isolée (`attribution-base-exacte.json`, `attribution-synthese.json`) :
« Gaspard reste près de Lucien » est déjà suivie par 375 ; onze notifications
sonores anonymes supplémentaires apparaissent dans le parcours Relais en bloc.
Le test renforcé conserve les égalités intégrales d'état, ordre JSON, rendu,
scène et paroles sauvegardées ; l'égalité de ces notifications reste une limite
antérieure explicite, non corrigée en S1d. La restriction Windows sur les sauvegardes
temporaires a nécessité l'exécution autorisée hors restriction, sans changer le moteur.

**Empreintes.** **16/16 nuits identiques** : 2 h × graines 1985/7/42/2024 ×
Relais/mine/auberge/crue, contre la base exacte `31f80725` ; chronique, mesures,
récit et empreinte de l'état final complet, sans exclusion ni plantage.
Les seize références manquantes sont calculées une fois et rangées dans le cache
partagé, comme les nuits de la branche `37069459`. Aucun code moteur modifié depuis.
Avis auxiliaires identiques : neuf « à expliquer », aucun « non justifié » ;
aucune correction revendiquée. Calculs détachés, référence puis branche, deux
processus au plus, priorité réduite. Aucun coût comparé ; ni suite complète ni Luna.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1d-384/` : `tests.json`,
`tests.log`, `tests-corriges.json`, `empreintes-base.json`, `empreintes-base.log`,
attributions, `fin-empreintes.json` et synthèse vérifiée `conclusion.json`.
L'ancien `fin.json` relate l'arrêt initial, avant empreintes. Copie d'attribution
retirée à la clôture ; lanceur local ignoré : `artifacts/s1d-384/run.ps1`.
Recouvrement potentiel 374 : seules les lectures de promesses de `deliberation`,
`planification`, la façade `esprits.prete` et `echanges.tenu` sont modifiées ;
aucune localisation ni recherche changée. Aucun fichier de 380/381 touché.
Le contrôle syntaxique ne prouve pas tous les flux interprocéduraux de Python ;
autres lecteurs, rétention âge/importance et nouveau stockage restent hors lot.
**Lot clos avec les limites héritées ci-dessus ; aucun calcul requis en attente.**
