# Lot 96 — Contenus de parole : schéma et validation communs

26 octobre 2026 — `codex-relances`, **non fusionnée**, base `72ff7ae`, code signé SSH `1c72176`
(code identique à `7b2691f`). **Réserve : conservation des refus sémantiques non validée.**

**Mesure avant code.** Six scripts × deux passes, `gpt-6-luna`, ChatGPT
medium/libre : **78 tours, 257 appels**, aucune erreur. Cache `7b2691f` absent :
export exact, douze parties jouées puis rangées, SHA-256 source/cache identiques.

| Famille | Appels supplémentaires | Secondes | Justification |
|---|---:|---:|---|
| Comptes et issue | 16 | 58,451 | Surtout extractions fausses ; une livraison indûment affirmée (mixte) |
| Portée et observation | 14 | 50,166 | Justes : cible loin, détail non observable |
| Extraction lumineuse | 6 | 23,098 | Faux refus : source extraite sans assertion, direction, citation |
| Référence inconnue | 6 | 22,430 | Justes : cible non identifiée |
| Portée sémantique du récit | 6 | 19,943 | Faux refus : condition, approximation, fin de réponse |
| Rapport illisible | 5 | 19,109 | Redemandes et traitement d'un rapport inexploitable |
| **Champs sans sens** | **2** | **9,262** | **Refus justes ; contrainte absente du schéma** |
| Impossible avant réexamen | 2 | 8,094 | Avis prématurés justement refusés |
| Voix d'auteur | 1 | 4,110 | Refus juste de « moteur » |

**58 appels, 214,663 s** : corrections, leurs audits et rapports redemandés,
hors récits normaux ; attribution exclusive par dernière cause. Détail par
appel (`attendu`, motif, qualification) : `artifacts/lot96/mesure-familles.json`.
Classements sémantiques discutables, cas mixtes signalés.

**Invariant.** Famille retenue : divergence schéma/validateur, pas la plus
coûteuse. Crypte (« Gorm, que sais-tu de cette crypte ? ») et échanges
(« Tu sais où est passé le gardien ? ») remplissaient `propos.sujet`.
`SCHEMA_PAROLE` dérive désormais ses variantes de `CHAMPS_CONTENU`, comme
`verifier_contenus` : champs inutiles vides, description par type, échange
conservé. Aucun mot-clé, nouvelle consigne, charge effacée ou contrôle supprimé.
Regroupement par forme écarté : il détournait les propos vers un échange ;
deux sondes archivées confirment le retour à `propos` par type.

**Deux passes finales**, douze parties exploitables : **257 → 252 appels**,
**3,295 → 3,231/tour** ; **11,874 → 10,784 s/tour (−9,17 %)**, médiane globale
**10,690 → 9,670 s**. Relances narratives **16 → 11**, refus **17 → 18**,
replis **2 → 1**. Corrections ciblées **2 → 0**, aucun nouvel échange de
substitution refusé. Aucun défaut de recharge.

| Fonction | Appels avant → après | s/tour avant → après |
|---|---:|---:|
| Interprétation | 85 → 86 | 4,62 → 4,36 |
| Audit narratif | 85 → 82 | 4,13 → 3,70 |
| Récit | 41 → 41 | 1,52 → 1,38 |
| Fidélité | 14 → 14 | 0,54 → 0,47 |
| Contre-revue | 16 → 18 | 0,42 → 0,44 |
| Révision | 16 → 11 | 0,64 → 0,43 |

Deux exécutions réduites par campagne, quatre Luna au plus, poste partagé.
Coût ciblé **0,119 s/tour** : gain global non attribuable au seul correctif.
Une partie réseau/délai remplacée seule ; un essai antérieur planté dans le
planificateur (`profil` nul), non corrigé. Essais intermédiaires et essais
bloqués par les permissions exclus ; traces conservées.

**Tests.** Suite unique verte : **1 963 tests, 16 ignorés**, deux processus
réduits, **1 910,32 s**. Après affinement : **19 tests ciblés verts, 38,83 s** ;
deux scénarios sans correction, état/rendu après recharge, charge interdite
toujours refusée. Contrôles inchangés, preuve par empreintes/AST.

**Rejeu exact.** Paiement inversé : refus retrouvé des deux côtés. Livraison
indûment affirmée : premiers tirages illisibles, puis cinq chacun, mêmes
entrées/instructions/schéma : **4 refus / 1 illisible → 0 refus /
4 illisibles / 1 admission**. Motifs parfois faux (hochement), comptes par
audit entier : **critère non validé**. Extractions de comptes/lumière et faux
refus de portée restent ouverts.

Bruts : `artifacts/lot96/` (analyse, comparaison, cache, rejeux, tests) et
`artifacts/bancs-multi/20261026-004729-12844/`. Aucun changement de modèle,
scénario, planificateur ou `main`.
