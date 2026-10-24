# Lot 34 — Une perception est un geste

Branche `codex-perception-geste`, **non fusionnée**, base d'intégration `ffcc295`,
brief `159faff`. Correctif signé SSH `b0d5f02`, signature vérifiée. 24 octobre 2026.

## Invariant et changement

Une perception produit l'information que le moteur fait percevoir, même sans effet durable
ni information disponible dans son plan préparé. `moteur.PERCEPTIONS` déclare ces gestes ;
`Plan.perception` expose action/cible, `Plan.realise_geste` reconnaît aussi les étapes.
`couverture_action._operations` transmet cette opération à la contre-revue avec les
désignations publiques. `MJ._echanger_prepare` ne refuse plus une perception corrigée comme
un geste vide. La revue conserve le contrôle de fidélité du geste et de sa cible.
`jeu.conclure` sauvegarde puis rend directement le résultat des perceptions : aucune
seconde rédaction ne peut y ajouter un résultat de recherche. Aucun changement du prompt
d'interprétation, des scénarios, de la règle d'exécution des questions ni du modèle Luna.

L'audit narratif commun distingue l'ambiance du résultat positif ou négatif d'une perception
active : seul un résultat exécuté/enregistré le soutient ; demande, proposition et silence
du contexte ne le prouvent pas. Une vraie ambiance reste libre et persistante.

## Vérifications et mesures

- Quatre nouveaux tests (`test_perception_geste`) : boucle console/MJ simulé/recharge,
  écoute derrière une porte avec voix, recherche de traces par observation, écoute corrigée,
  résultats négatifs sans source refusés et ambiance conservée. Déclaration commune et étapes
  contrôlées aussi. Ciblés finaux : **104 tests verts, trois ignorés**, priorité réduite.
- Suite complète unique (`tools/tests.py --processus 3`), **1 775,9 s** : 1 649 tests,
  quatre erreurs d'environnement, 16 ignorés (deux processus TUI bloqués puis arrêtés,
  deux sockets web refusés, `WinError 10013`). Seules reprises hors bac à sable : TUI
  **28 + 5 tests verts**, web/WebSocket **11 verts**. **Bilan consolidé : 1 680 tests,
  16 ignorés, aucun échec ni erreur restant**, 156 fichiers. Sources et consolidation
  gardées séparément ; aucune seconde suite complète.
- Empreintes Relais, **2 h × 4 graines**, contre la base `ffcc295` : chronique, mesures et
  état final complet identiques. Quatre références manquantes calculées une fois et mises
  en cache ; aucune comparaison de temps entre conditions de charge différentes.
- Luna `gpt-6-luna`, forfait ChatGPT, copies temporaires, priorité réduite, **une seule passe**
  des trois scripts prescrits (`--fil`) :

| Script | Tours MJ | Appels | Appels/tour | Secondes/tour |
|---|---:|---:|---:|---:|
| crypte | 9 | 25 | 2,78 | 11,5 |
| relais | 8 | 26 | 3,25 | 12,8 |
| luna-restes-ambiance | 3 | 6 | 2,00 | 10,3 |

Zéro repli, erreur technique ou recharge invalide. Écoute acceptée immédiatement par la revue,
résultat exécuté ; recherche de traces acceptée aussi. L'audit refuse le résultat négatif
ajouté par la narration de cette recherche. Aucune ambiance admise ne conclut au résultat
d'une perception active. Deux alertes lexicales du banc reprennent les mots du joueur
(Gorm et pied-de-biche) dans des refus, sans révéler leur présence.

## Limites

La passe Luna a précédé le rendu direct final : **écoute 4 appels, traces 6**, donc le plafond
de trois appels n'est **pas validé par un nouvel essai Luna sur le code livré**. Pour respecter
l'unique passe, ses réponses archivées ont été rejouées, sans modèle, dans les mêmes scènes
et saisies : **2 appels simulés chacun**, résultat moteur et recharge valides. Le rendu final
dit seulement « Le sol en pierre » ; il ne prouve pas l'absence de traces.
Le classement d'une phrase et la fidélité sémantique de la revue restent probabilistes ;
aucune garantie générale de détection des contradictions n'est revendiquée.

Fils, empreintes, tests et rejeu : `artifacts/codex-34-*` dans le worktree ; détails du rejeu
dans `artifacts/rejouer-codex-34.py`. Aucun banc long ni fusion sur `main`.
