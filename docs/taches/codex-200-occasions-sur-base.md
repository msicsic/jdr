# Tâche Codex 200 : refaire le lot 186 (occasions asymétriques) sur la base actuelle

Le lot 186 (`docs/taches/rapport-codex-186-occasions-asymetriques.md` sur la branche `origin/codex-occasions-asymetriques`,
`18c52aa`) ajoutait aux scénarios des **données** créant des occasions : bois cessible porté par Brune/Odon/Joss, liens
d'affection en triangle (commissions), observations inégales (avis), sans galettes. Fusionné puis **annulé** sur l'intégration
(`057d151`) : validé sur la base `12a936d`, il rencontrait le projet de pièces du lot 184 fusionné entre-temps (Brune endettée
vend désormais son bois) et faisait échouer **30 tests et 4 erreurs dans 25 fichiers** (suite `C:\Users\msics\donjon\artifacts\suite-c12acd1.txt`),
alors que ces fichiers passent sans lui. Ce comportement nouveau (Brune vend son bois pour payer sa dette) est peut-être
exactement la richesse cherchée : il faut trier.

Lot de 30 à 45 minutes (`AGENTS.md`), livraison partielle permise si elle dit ce qui reste. Pas de Luna. **Poste : le laptop**
(`C:\Users\msics\donjon`, l'utilisateur y travaille ; un autre lot y calcule) : au plus 2 processus, priorité réduite. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`, `PYTHONIOENCODING=utf-8`. Fichiers : données des scénarios (`donjon/scenario_*.json`)
et tests ; **aucun autre fichier de `donjon/`** (si un défaut du moteur apparaît, dis-le, ne le corrige pas ici). **Bruts dans
`C:\Users\msics\donjon\artifacts\occasions-200\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, le rapport 186, `tests/fixtures/README-occasions-186.md` de sa branche, et les rapports 184 et 192.

## Ce qu'il faut faire
1. Porter les données de `18c52aa` (variante sans galettes) sur la base actuelle (`integration`), avec leurs tests propres.
2. **Pour chacun des tests en échec**, établir la cause et la classer : (a) **changement de comportement légitime** dû aux
   nouvelles occasions (un PNJ vend, demande ou sert autrement) : la scène historique garde son intention, soit en posant
   explicitement les données d'avant 186 dans la scène (comme le faisait le lot 186), soit en adaptant l'attendu, **avec la
   justification écrite** ; (b) **régression** (une règle du moteur rendue fausse par la combinaison) : ne pas masquer, la
   documenter avec la capture et la règle en cause. Aucun test affaibli pour passer.
3. Mesure à base identique (`tools/comparer_bancs.py --reference <base>`, quatre scénarios × 1985/7/42/2024, 4 h ; référence
   rangée dans le cache commun) : S/F/D du lot 183 (`C:/Users/msics/donjon/artifacts/dormants-183/analyser.py`), propositions et
   acceptées, ventes, commissions, avis et adoptions, services, projets nés (lots 184/192), alertes de l'audit (dont le compteur
   des changements d'avis s'il est déjà fusionné, lot 199).

## Vérification
Tests ciblés des fichiers touchés ; suite complète une fois à la fin (`tools/tests.py --processus 2`) ; 24 états et rendus
rechargés identiques sur les nuits du banc.

## Livraison
Branche `codex-occasions-sur-base` poussée (si la poussée est bloquée, commit local et dis-le) ; entrée dans
`docs/etat-dev.md` (« Branche `codex-occasions-sur-base`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-200-occasions-sur-base.md` (tableau test → cause → classement → décision).
