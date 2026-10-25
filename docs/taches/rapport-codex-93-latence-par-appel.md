# Lot 93 — Latence par appel

25 octobre 2026 — `codex-latence-appels`, **non fusionnée**, base `258daab`
(code d'intégration `119169c`, lot 91). Code `4883425`, attestation Signed-off-by.

**Mesure d'abord.** Deux passes des six scripts demandés sur `119169c`, puis sur
la branche : **78 tours MJ par variante**, ChatGPT medium/libre, `gpt-6-luna`.
Deux exécutions par variante à priorité réduite, quatre pendant le chevauchement ;
poste partagé. Douze références rangées, relues du cache, SHA-256 vérifiés.
Secondes = attente modèle, hors rendu et calcul local. Le fil conserve début/fin,
premier delta, jetons (entrée/cache/sortie/réflexion), séquence critique par tour ;
HTML et `banc_multi` exposent ces mesures et la médiane. L'affichage attend les contrôles.

| Fonction | Appels avant → après | s/tour avant → après | Part avant → après | Premier delta moyen, s |
|---|---:|---:|---:|---:|
| Interprétation, corrections moteur comprises | 88 → 91 | 5,07 → 4,86 | 36,8 → 36,6 % | 2,03 → 1,75 |
| Récit | 41 → 41 | 1,60 → 1,54 | 11,6 → 11,6 % | 1,28 → 1,20 |
| Audit narratif | 78 → 77 | 5,66 → 5,41 | 41,1 → 40,9 % | 1,34 → 1,24 |
| Fidélité de parole | 14 → 14 | 0,55 → 0,54 | 4,0 → 4,1 % | 1,13 → 1,03 |
| Contre-revue d'action | 16 → 18 | 0,43 → 0,55 | 3,1 → 4,1 % | 1,14 → 1,34 |
| Révision narrative | 9 → 8 | 0,48 → 0,35 | 3,5 → 2,7 % | 2,03 → 1,49 |

Portée/capacités : aucun appel ici. Récit/audit, interprétation/fidélité et refus/révision
sont dépendants. Narration/portée pourraient être parallèles, mais aucun couple ici.
Réflexion déclarée : zéro jeton.

**Levier C, un invariant.** Une répétition du schéma ne change pas le contrat.
`fournisseurs.schema.mutualiser` remplace les sous-schémas identiques par des
`$defs`/`$ref` si cela raccourcit la requête OpenAI ; schémas ayant une identité
ou des références conservés. Expansion identique : champs, descriptions, obligations,
types et bornes inchangés, comme faits, instructions, effort et contrôles.
Seule la représentation du fournisseur change. Références prises en charge selon la
[documentation officielle OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).
Sur la référence, schémas MJ **−30,3 %**, narratifs **−41,4 %** en caractères.

**Résultat observé.** Moyenne **13,794 → 13,249 s/tour (−3,95 %)**, médiane
globale **13,045 → 11,915 s (−8,66 %)** ; **246 → 249 appels**, soit
**3,154 → 3,192/tour**. Jetons d'entrée **3 005 420 → 2 804 658 (−6,68 %)**,
dont cache **908 672 → 793 984** ; sortie **36 148 → 35 604**. Moyennes par passe :
relances **4,5 → 4**, refus **10 → 11**, replis **0,5 → 0**. Aucune erreur
technique, interruption ou erreur de recharge sur les 24 parties. Secondes par
script avant/après : Relais **10,73/11,63**, crypte **12,96/10,34**, atelier
**12,08/12,44**, échanges **14,67/14,57**, soir-appel **20,91/21,82**, noms-dialogue
**18,74/15,70**. Gain global modeste, non uniforme ; chevauchement partiel et
variations sémantiques interdisent une attribution causale précise.
Deux achats de branche exécutés : or **23** dans le dossier après paiement,
`planches_1` portée après recharge. « Pièces rendues » demeure ambigu dans une
réplique, également dans la référence ; le lot ne corrige pas cette lecture.

**Contrôles et limite bloquante.** Console avec fournisseur OpenAI simulé : absence
d'Ilse et orientation de Gorm, mêmes refus/redemandes/relances, correction affichée,
objets et rendu identiques après recharge. Équivalence des schémas, valeurs
littérales, premier delta et appels manqués testés.
Neuf audits narratifs refusés rejoués sur leurs entrées exactes :
six restent refusés, dont écoute non exécutée, comptoir inventé et deux comptes
inversés. Trois refus disparaissent : ambiance, fausse contradiction d'une dette
correcte, hochement classé à tort comme parole sans citation.
**L'unique refus de contre-revue juste n'est pas retrouvé** : écoute demandée à la
porte, plan `ecouter` sans cible, maintenant jugé conforme. Ce schéma de 162
caractères n'est pas mutualisé : entrée, instructions et schéma inchangés.
Instabilité sémantique non corrigée. Critère « aucun refus juste perdu »
**non satisfait**, validation pour fusion non acquise. Dix rejeux hors métriques.

Suite complète unique : **1 947 tests, 16 ignorés, zéro échec/erreur**, 202 fichiers,
**1 349,91 s**, trois processus à priorité réduite. Lot réalisé en environ 42 minutes.

Bruts du worktree : `artifacts/bancs-multi/20261025-224208-29836/` (référence),
`20261025-224813-39728/` (branche), `analyse-93.json`, `comparaison-93.md`,
`preuve-cache-93.json`, `rejeu-refus-93.json`, `rejeu-contre-revue-93.json`,
`tests-cibles-93.json`, `tests-instrumentation-93.json`, `tests-complets-93.{json,log}`.
