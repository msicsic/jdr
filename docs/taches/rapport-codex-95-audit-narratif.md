# Lot 95 — Rapport narratif limité à la décision

25–26 octobre 2026 — `codex-audit-narratif`, **non fusionnée**, base `036d5f2`,
code signé SSH `adb07f7`, correctif `49fa7d6`. **Validation pour fusion bloquée : un refus juste
disparaît au rejeu avec le nouveau rapport.** Aucun changement de modèle,
scénario, planificateur ou `main`.

**Mesure avant changement.** Référence `29ccf1e`, deux passes des six scripts
du lot 93, ChatGPT medium/libre, `gpt-6-luna` : 76 audits, 134 segments,
**16 383 jetons de sortie**, moyenne **215,57**, médiane **208,5** par appel.
Aucun segment n'est exactement un texte moteur ou une citation déjà validée
dans ce corpus. Tous les champs sont lus dans au moins un cas ; certains ne
servent à décider que pour certains verdicts. Fragments JSON tokenisés
séparément avec `o200k_base` : le motif représente **6 206** jetons, dont
**5 780** sans rôle pour le verdict. Détail par champ et par appel conservé ;
ces fragments ne s'additionnent pas exactement au total fournisseur.
Douze références jouées ici, rangées et relues
du cache ; douze SHA-256 identiques.

**Invariant.** `textes_etablis/segments_etablis` prouvent les reprises exactes
du moteur et citations historiques ; `mj._appeler` n'audite que les segments
libres, avec leurs indices. `schema_audit` omet les champs sans objet et le
motif des segments admis ; refus borné à 240 caractères. `controler/consigner`
refont la preuve, les contrôles existants et la perception actuelle.
Seul le rendu complet d'une opération liée aux mêmes comptes prouve leur
couverture globale. `_echanger` corrige le lien résultat/comptes manquant
révélé par la suite. Zéro des 264 requêtes archivées emprunte ce cas : mesures
conservées (`preuve-requetes-inchangees-95.json`).

**Deux passes Luna**, 78 tours par variante : moyenne **13,038 → 11,720 s/tour
(−10,1 %)**, médiane globale **12,41 → 10,24 s** ; appels **251 → 254**,
soit **3,218 → 3,256/tour**. Relances **8 → 11**, refus **23 → 21**, replis
**1 → 1** (totaux). Aucun arrêt, erreur technique ni défaut de recharge sur
les 24 parties. Audit : **76 → 79 appels**, **215,57 → 132,04 jetons/appel**,
sortie totale **16 383 → 10 431 (−36,3 %)** ; entrée **662 887 → 1 173 129
(+77,0 %)** : les variantes du schéma coûtent davantage en entrée malgré la
mutualisation. Premier delta moyen **1,22 → 1,39 s**. Secondes par tour :

| Fonction | Référence → branche |
|---|---:|
| Interprétation | 4,94 → 4,73 |
| Audit narratif | 5,20 → 3,89 |
| Récit | 1,52 → 1,58 |
| Fidélité / contre-revue | 0,52 / 0,53 → 0,58 / 0,48 |
| Révision | 0,33 → 0,46 |

**Rejeu.** Dix audits refusés, entrées exactes : six faux refus/extractions
erronées disparaissent ; deux restent refusés, dont un avec une autre cause.
Deux rapports illisibles sont redemandés une seule fois : géométrie toujours
illisible, mais **second préalable aux crochets accepté**, auparavant refusé
à juste titre. Schéma modifié : l'exception pour appel inchangé ne s'applique
pas. **Critère non satisfait** ; aucun prompt ciblé ni exception ajouté.

**Tests.** Suite complète unique : **1 961 tests, 16 ignorés, 1 858,74 s**, deux
processus réduits ; six échecs et une erreur dans cinq fichiers. Compteurs
adaptés, transport WebSocket toujours exercé par une paraphrase, lien
résultat/comptes corrigé. Reprise des cinq fichiers concernés et des nouveaux
tests (seul test TUI concerné) : **30 tests verts, trois ignorés, 12,64 s**.
État, affichage et recharge contrôlés ; aucun défaut restant reproduit,
sans seconde suite complète. Bilan détaillé dans `bilan-consolide-95.json`.

**Limites.** Preuve exacte déterministe, paraphrases et extractions sémantiques.
Le corpus n'exerce pas l'exemption exacte ; le gain vient du rapport réduit.
Poste partagé, références mesurées auparavant : causalité précise non garantie.

Bruts : `artifacts/mesure-reference-95.json`, `preuve-cache-95.{json,log}`,
`rejeu-refus-95.json`, `rejeu-refus-95-reprises.json`,
`bancs-multi/20261025-232443-15292/` (référence),
`bancs-multi/20261025-233123-39740/` (branche), `tests-complets-95.{json,log}`,
`tests-finaux-95.log`, `analyse-95.json`, `comparaison-95.md`.
