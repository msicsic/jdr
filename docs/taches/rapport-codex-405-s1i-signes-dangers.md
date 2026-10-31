# Lot 405 — S1i, signes, détresse et dangers subjectifs

31 octobre 2026 · `codex-s1i-signes-dangers` · base exacte `integration 0643c2ff`.
Code porté : **`15856296`**. **Vérification en cours, lot non clos.**

**Invariant et code.** Les lectures faillibles, leurs essais et conclusions par
observateur, les preuves de détresse et les dangers passent par `memoire`.
`signes.actives/detresse_retenue/retenir_detresses` et `defense.auteurs/constater_fin`
restent des façades. Les vues rendent des copies profondes ; `esprits.croyance`
protège aussi les familles `emotion`, `intention`, `parole_doutee`, `attitude:*`,
`detresse` et `violence`. La relecture compare l'admissibilité de la preuve,
sans dépendre de l'identité Python d'un dictionnaire partagé.

La porte conserve les politiques historiques distinctes : lectures à 30/120 min,
essai toutes les dix minutes, suivi v2 et migration sans réapprentissage ;
détresse sans effacement par perte de vue, démentie par une lecture contraire
du même signe, un calme discernable ou une indisponibilité connue ; dangers à
30 min, clôture sur neutralisation constatée, sans réouverture au seul réveil.
L'admission reste commune (`admettre_fait`/`croire`). Les jets, épisodes physiques,
ordre de sérialisation, épisodes racontables, paroles et délais sont conservés ;
aucun registre ajouté. Les coups perçus de Corvus ont également une vue et des
écritures nommées. Les schémas portés contrôlent essais, lectures joueur, suivi v2
et violences joueur ; les suivis antérieurs à v2 gardent leur migration historique
destructive, sans validation exhaustive d'une histoire absente.

Consommateurs voisins portés : causes de détresse, intermédiaires et occasions
de protection. Aucun changement des fonctions de passage du 381 ni du terminal
de remboursement du 399 ; recouvrement possible avec 403 dans les modules et
oracles communs, sans correction de ses comportements. L'historique des lots
n'est pas modifié.

**Inventaire et tests.** Inventaire AST des croyances **129 → 40 expressions**,
sans addition ; les restantes relèvent des familles ultérieures et homonymes.
Le contrôle étend le suivi des alias aux cinq registres subjectifs de S1i ;
seul reste le compteur homonyme de calibration. Cinq tests nouveaux couvrent
copies imbriquées et pureté, bornes, clôture persistante et nouveau geste,
corruptions et migration sans jet. Captures historiques : Lucien à la mine 7
et guet de Brune au Relais 7, deux minutes entières ou deux fois une minute
avec recharges ; état complet et ordre JSON, lignes, rendu, scène et paroles.
Les tests métier vérifient aussi perte de regard, cadence, secours et dangers.
Passe finale : **161/163 verts**, quinze fichiers, 262,6 s ; aucune erreur ni
test ignoré, cinq nouveaux tests verts (`tests-finaux.json/log`).

La première passe métier donne **76/78 verts**, deux échecs reproduits à
l'identique sur la base exacte (35 tests d'attribution) :
`empathie_peur.test_lecture_retenue_revisee_par_un_dementi_percu_et_non_par_le_regard`
et `test_gorm_attend_un_moyen_sur_pour_le_feu_mais_execute_encore_sa_ronde` à 85 min.
Oracles conservés. Le premier interdit de revendiquer une garantie générale de
démenti sémantique : le portage conserve aussi cette limite héritée.

**Empreintes requises.** Comparaison détachée lancée : 2 h × quatre graines
1985/7/42/2024 × Relais/mine/auberge/crue, référence exacte puis branche,
cache partagé, deux travailleurs réduits au plus ; aucun temps du cache comparé.
L'identité des seize nuits **n'est pas encore acquise**. Ni suite complète ni Luna.
`origin/integration 0643c2ff` n'a pas avancé lors de la vérification finale ;
aucune fusion supplémentaire nécessaire. Le calcul mesure `15856296`.

**Bruts et reprise.** `C:/Users/msics/donjon/artifacts/s1i-405/` :
`tests-metier.json/log`, `attribution-base.json/log`, `tests-porte.json/log`,
`tests-finaux.json/log`, puis `run405.py`, `empreintes-base.json/log` et `fin.json`.
La première porte avait une erreur d'assertion du test de corruption (exception
`ErreurMonde` attendue, corrigée) ; les bruts sont conservés. Le contrôle AST
reste syntaxique/local, sans preuve de tous les flux interprocéduraux Python.
Reprendre au fichier de fin avant de clore le lot ou d'affirmer l'identité.
