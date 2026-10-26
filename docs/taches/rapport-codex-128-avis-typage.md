# Lot 128 — Analyse des opérations avant le contenu

Branche `codex-avis-typage`, **non fusionnée**, base `20cd5cf` (lot 124).
Ce lot et le lot 124 restent ensemble à relire. Aucun changement de `main`,
d'`integration`, du modèle `gpt-6-luna`, des scénarios, de `tools/` ni des fichiers
réservés aux lots 126 et 127. Aucune clé Git de signature configurée.

**Cause et contrat commun.** Dans le fil du lot 124, les trois interprétations
proposent `propos`, puis déclarent toutes les opérations fausses ; les mots exacts
sont donc dispensés de revue. `avis` figure pourtant dans les variantes du schéma,
dans `SENS_CONTENU` et en tête de la carte des opérations. L'omission précède le
raccourci ; aucune trace ne prouve à elle seule pourquoi Luna omet ce type.
L'ordre du schéma favorise une déclaration après le choix du contenu, tandis que
`propos` signifiait seulement « sans effet mécanique typé », définition circulaire.

`MJ._echanger` présente désormais `operations_demandees` avant les autres champs de
parole ; l'ordre annoncé par `paroles.REGLES` suit le schéma. `SENS_CONTENU.propos`
désigne l'absence de toute opération applicable. La description de
`SCHEMA_OPERATIONS`, commune à l'interprétation et à la revue, demande d'analyser
le sens exprimé, même déclaratif, négatif ou incertain, sans conditionner le type à
la vérité ou à la réussite de ses conséquences. Aucun exemple ni lexique ajouté,
aucune modification particulière de la définition d'`avis`. Le raccourci conserve
son coût nul pour une parole ordinaire déclarée sans opération.

**Preuves console.** 17 tests ciblés : deux erreurs initiales dans les attentes du
nouveau test, corrigées, puis les neuf tests d'avis repris verts ; les huit tests
de parole ordinaire et de paiement étaient verts. Avis positif et négatif d'abord
omis du contenu malgré leur déclaration : refus local privé, correction typée,
une seule parole enregistrée, prévision reçue et rendu contrôlés après recharge.
Les achats de planche et de soupe contrôlent paiement, propriété, réserves et
inventaire rechargé ; les paroles ordinaires gardent zéro revue.
Suite complète unique : **2 066 tests, 223 fichiers, 1 060,85 s**, deux processus
à priorité réduite ; seuls les **deux échecs MiMo historiques**, zéro erreur.

**Luna, une passe sur copies.** Critère demandé **2/3 avis typés**, contre **0/3**
au lot 124 : conduite positive et refuge négatif acceptés dès la première
interprétation, galerie encore omise. Aucun refus affiché ni erreur de recharge.
Mesures par tour MJ (références historiques relues, jamais rejouées) :

| Script | Appels/tour avant → après | s/tour avant → après |
|---|---:|---:|
| avis-joueur (lot 124) | 3,00 → 5,00 | 13,5 → 24,1 |
| noms-dialogue (cache `057766f`, passe 1) | 3,75 → 3,25 | 14,0 → 12,1 |
| soir-appel (même cache) | 5,00 → 6,00 | 20,8 → 22,2 |

Total : **44 → 52 appels / 11 tours**, soit **4,00 → 4,73 appels/tour**.
Sur les avis : 4/3/8 appels ; deux revues typées ajoutées et deux relances
narratives au troisième tour. `soir-appel` conserve un repli narratif, zéro refus
affiché ; les deux autres scripts n'ont aucun repli.
La réclamation est typée `reclamer` et les deux pièces sont rendues ; l'achat
est typé `proposition`, accepté, avec paiement et livraison engagée.
Budgets historiques 200, lot 150, aucun atteint ; charges et commits différents, pas de conclusion de
vitesse. Bruts : `artifacts/avis-typage-128/` et fil du lot 124 dans son worktree.

**MiMo et limites.** Les deux échecs historiques sont reproduits et diagnostiqués :
`jsonschema` **4.26.0** rejette la réponse simulée d'`auditer_narration` de l'atelier
(ancien segment avec `verdict`, sans discriminant `nature`), d'où un appel de
correction supplémentaire, six au lieu de cinq. Les tests sont ignorés sans cette
dépendance facultative ; aucune modification du fournisseur ni de ses tests.
Le seuil Luna du brief est atteint, **l'invariant général n'est pas garanti** :
la galerie reste `propos` et une carte fausse peut encore contourner la revue.
Ce lot renforce le contrat sémantique commun, sans preuve indépendante de son
exhaustivité ; il ne clôt donc pas à lui seul la limite de couverture du lot 124.
