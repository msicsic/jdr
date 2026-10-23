# Tâche 25 — La preuve reste interne au MJ

Branche `codex-ambiance`, **non fusionnée**, base `main` **42bb9c0**. Correctif signé **a223827**.

**Cause lue dans les fils.** Le lot 22 laisse « aucun autre son n'est attesté ici » dans
`luna-restes-ambiance`, passe 1, et une odeur suivie d'une réserve au Relais. L'interprétation
demandait « ce qu'il ignore encore » ; la révision et l'`attendu` d'`invention_protegee` invitaient
à dire l'ignorance après un refus. La référence confirme la chaîne : « révèle les reliefs » est
refusé comme détail non établi, puis le retour invite à dire cette ignorance.

**Invariant et fonctions.** La narration parle des perceptions, savoirs ou suppositions dans la
fiction ; elle ne commente pas la preuve reçue par le MJ. `voix_auteur` et `_reecrire` contrôlent
aussi les termes de preuve et les tours impersonnels d'absence d'indication, sans dépendre du
verdict : un refus par cause, segment et mots reçus dans `attendu`. Le garde existant
est refait par `consigner` avant sauvegarde. `INTERPRETATION`, `INSTRUCTIONS_REVISION`,
`REGLE_NARRATION` et `ACCEPTE_VERDICT` n'invitent plus à ajouter une réserve à l'ambiance.
`INSTRUCTIONS_AUDIT` juge sa compatibilité, sans exiger sa cause, et admet aussi une absence de
sensation. Aucun fichier réservé ni scénario modifié.

**Cas sur la boucle réelle, fournisseur simulé, après rechargement.** `tests/test_ambiance.py` :
calme avec « attesté » et odeur avec réserve sur son origine, même si l'auditeur les admet ; seuls
le texte corrigé et son ambiance liée au lieu persistent, sans création d'objet ni déplacement.
Une inconnue mécanique dite en perception reste admise. Une réponse mêlant odeur et ouverture
inventée conserve l'odeur après refus du détail mécanique, sans invitation à la démentir.
Un audit altéré ne contourne pas le garde à l'écriture ; les répliques gardent leur contrat.

**Vérifications.** Suite complète unique, trois processus à priorité réduite : **1 595 tests,
15 ignorés, verte, 564,4 s** (`artifacts/ambiance/tests-complets.json`) ; 22 tests ciblés verts
après correction du retour d'audit. Premier lancement ciblé bloqué par le sandbox, puis relancé.

Luna `gpt-6-luna`, une passe finale sur `relais`, `crypte`, `luna-restes-ambiance`, référence
42bb9c0 puis branche, coffre principal, copies seules. Référence absente du cache : jouée une
fois et rangée sous `artifacts/references/42bb9c0344f1c943f5b1d9ea40c012810380ee9a/`.
21 tours MJ par variante : **63 → 59 appels**, **3,00 → 2,81 appels/tour**, **12,7 → 11,5 s/tour**,
**4 → 3 relances**, aucun repli, erreur technique ou échec de rechargement. Le nouveau garde
refuse « Aucun autre bruit de fond n'est établi ici » ; la reformulation affichée décrit les
sons, sans preuve du moteur. Aucun vocabulaire de méta-preuve dans les sorties finales relues.
**Critère strict d'absence de faux refus d'ambiance encore partiel** : le silence au Relais est
refusé au motif du bruit courant et des notes précédemment chantées, jugement discutable.
L'odeur reste une absence de sensation, avec une réserve dite en perception.

Fils : `artifacts/bancs-multi/20261023-235020-46808` (référence),
`20261023-235721-59280` (finale) ; `artifacts/ambiance/relecture-finale.txt`.
L'essai de branche `20261023-235533-21628`, interrompu avant la fin du Relais pour corriger
l'`attendu` encore fautif, est exclu des mesures. Aucun banc supplémentaire.

**Limites.** Le garde lexical ne couvre pas toutes les paraphrases et peut refuser un usage
littéraire de ce vocabulaire. Les contradictions et la distinction ambiance/mécanique restent
en partie sémantiques. Une passe ne prouve ni garantie générale ni gain de performance.
