# Lot 101 — Mots courants et emploi technique

Branche `codex-mots-courants`, non fusionnée, base `31e3f9c`. Le constat N2 du lot 99
est relu dans les bruts du dépôt principal, sans modification.

Le garde commun `narration.voix_auteur` distingue désormais la personne du récit des
constructions techniques. Les noms communs ne sont plus interdits seuls : un complément
technique, un emploi comme source informationnelle ou une opération attribuée au moteur
établit le contexte. Les participes de preuve et les unités ordinaires suivent la même
règle ; les réserves ambiguës passent à l'audit sémantique. Les identifiants en snake_case
et les localisations numériques restent refusés avec `attendu`. Aucun ajout au prompt,
aucune exception de scénario, aucun changement de la chaîne de correction ou du repli.
Les anciens tests d'ambiance emploient maintenant une source interne explicite pour
prouver le refus ; les tours de preuve sans cette source ne sont plus censurés lexicalement.

Vérification : 81 tests ciblés verts, puis les quatre tests du nouveau fichier verts
avec le contrôle supplémentaire d'identifiant. Boucle console réelle, MJ simulé : phrase
« Les planches ne t'ont pas encore été données » et actes d'un compagnon admis ; données
du jeu, moteur ayant refusé et identifiant brut corrigés avant affichage. Les sauvegardes
rechargées conservent le récit admis, les objets, le joueur et le temps. Les premiers
lancements sous sandbox ont échoué sur les ACL des dossiers temporaires ; relance autorisée,
sans changement du moteur de sauvegarde.

Une passe Luna ChatGPT medium/libre, séquentielle à priorité réduite, sur copies :
`soir-appel`, 10 saisies, 4 tours MJ, 18 appels (4,5/tour) ; `ressources`, 3 tours MJ,
12 appels (4/tour). Aucun refus, repli, erreur ni défaut de recharge. La phrase initiale
n'a pas été régénérée : sa preuve exacte est apportée par le MJ simulé. La dernière
réponse de `soir-appel` annonce une fourniture future ; cette passe ne prouve pas une
remise matérielle. Bruts : `artifacts/luna-101/`, sorties et tests dans `artifacts/`.

Suite complète unique : **1 979 tests, 16 ignorés, 1 976,44 s**, 208 fichiers, deux
processus à priorité réduite. Deux échecs du même fichier révèlent la forme nominale
« refus du moteur », oubliée par le motif verbal. Le contrat commun reconnaît maintenant
les opérations internes sous leurs formes verbales et nominales ; **reprise ciblée de
21 tests verte** (orientation narrative, mots courants, gardes justes). Aucun autre
échec, aucune erreur ; aucune seconde suite complète. Premier commit signé `2d54461`,
complément nominal et résultats dans le commit final de cette branche.

Limites : ce reconnaisseur n'analyse pas tout le français. Un homonyme dans une
construction informationnelle peut encore être mal classé ; une source implicite ou un
identifiant sans marque distinctive dépend du contrôle sémantique. L'invariant universel
« aucun faux refus » n'est pas garanti : le lot retire les interdictions par forme seule,
sans présenter ses constructions lexicales comme une preuve générale du sens.
