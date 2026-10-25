# Lot 89 — Fidélité du contenu et décision d'audience

25 octobre 2026 — `codex-fidelite-audience`, **non fusionnée**, base `96c6396`.
**Validation partielle ; objectif global d'appels non atteint.** Aucun changement
de `main`, des scénarios, de l'audience ou du modèle `gpt-6-luna`.

**Mesure préalable.** Toutes les contre-revues des quarante parties 882907c
(lot 79), trois parties du lot 82 et deux du lot 84 : **16 + 14 + 10 revues de
parole**. Cinq refus, tous injustifiés selon le contrat moteur :

| Lot/script | Nombre | Motif de la revue et erreur |
|---|---|---|
| 82, soir-appel/noms-dialogue | 2/1 | « quelqu'un » porte sur l'ensemble, `ressource` sur l'interlocuteur : rejugement d'audience |
| 84, soir-appel | 1 | `demande` avec valeur 3 ne représente pas explicitement l'échange : forme pourtant exécutable |
| 84, ressources | 1 | La question de dette devient réclamation : conséquence admise par le moteur |

Aucun refus justifié de parole dans ce corpus ; le refus de geste sous obstacle
du lot 79 est exclu. Motifs exacts et sources : `artifacts/refus-historiques.json`.

**Contrat corrigé.** `MJ._auditer_action` sépare parole et gestes. Le rapport
obligatoire porte `perimetre` : seul `sens` peut refuser ; `adresse` et
`validation_moteur` ne relancent pas le MJ. `couverture_action.verifier` exige
toujours les opérations demandées, même hors périmètre. `sens_parole` fournit
les opérations exécutables communes et le prix calculé par `offre` : la revue
compare le sens, sans redécider la représentation. Après le défaut Luna ci-dessous,
`paroles.SENS_CONTENU.reclamer` est aligné sur le contrat existant : interroger
sur son dû ou le réclamer ; le moteur décide du règlement. Cette clarification
finale n'a pas de seconde mesure Luna.

**Tests.** Quatre nouveaux tests de vraie console : bois/Aubin et nourriture/Lucien
au premier contrôle malgré une objection d'adresse ; achats de parts sous demande
chiffrée et proposition, paiement/livraison ; questions de dette à Aubin/Gorm ;
mots contraires et autre ressource refusés, opération manquante toujours bloquée.
État, parole unique, sortie, conversation et inventaire après recharge contrôlés.
**71 tests ciblés consolidés verts**, après correction d'une scène de dette.
Suite complète unique : **1 931 tests, 16 ignorés**, 199 fichiers, trois processus,
**1 444,24 s** ; huit échecs d'attentes de dossier dans deux anciens fichiers et
une erreur Windows de remplacement de sauvegarde temporaire dans le test TUI.
Attentes adaptées ; reprise finale des deux fichiers, du seul test TUI en erreur
(inchangé) et des quatre nouveaux tests : **15 tests verts, 56,40 s**.
**Bilan consolidé sans défaut restant reproduit**, sans seconde suite complète.

**Luna, une passe**, ChatGPT medium/libre, copies, priorité réduite, une exécution ;
quatre références 882907c exclusivement en cache : **53 → 57 appels / 14 tours**,
**3,79 → 4,07 appels/tour** ; relances **4 → 2** (0,29 → 0,14/tour), refus **0 → 2**,
replis du détecteur **0 → 2**, un tour avec erreur réseau, aucun arrêt/défaut de recharge.

| Script | Appels/tour, référence → lot | Relances |
|---|---|---|
| soir-appel | 4,25 → 4,25 | 1 → 2 |
| noms-dialogue | 4,00 → 3,50 | 2 → 0 |
| ressources | 3,67 → 4,33 | 1 → 0 |
| echanges | 3,00 → 4,33 | 0 → 0 |

Le bois passe au premier audit dans les deux scripts et Aubin répond sur ses
planches. L'achat du soir subit un délai de **203,4 s avant proposition** : aucun
achat exécuté. Le remboursement finit sur le rendu moteur après deux relances.
La question de dette reste bloquée : `qui` extrait à tort, correction puis repli
incomplets. Définition commune ensuite clarifiée, sans rejouer Luna. `echanges` :
champ interdit de `propos` refusé avant revue puis corrigé ; trois alertes lexicales
du harnais sont les noms saisis repris par des refus locaux, sans fuite narrative.

**Limites.** Périmètre appliqué déterministement, classement et opérations encore
sémantiques : faux refus classé `sens` et écart classé hors périmètre restent
possibles. L'invariant général n'est pas garanti. Temps historiques sous d'autres
charges, aucun gain causal revendiqué. Bruts du worktree : `artifacts/verification-luna-lot89.json`,
`bancs-multi/20261025-210728-32172/`, `tests-cibles*` et `tests-complets.{log,json}`.
