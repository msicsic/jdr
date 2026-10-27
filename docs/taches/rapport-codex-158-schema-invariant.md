# Rapport 158 — schéma invariant (L2, interprétation)

27 octobre 2026 — `codex-schema-invariant`, **non fusionnée**, base `7adc788`,
code `9a0ea10`, outil de mesure `a2147fd`. **L2 partiel : interprétation traitée, audit narratif encore variable.**

**Invariant.** `MJ._echanger` expose toujours huit modes et toutes les branches,
avec une seule branche de faits à `suite` nullable. `verifier_disponibilite`
refuse les modes sans catalogue/interlocuteur avec `attendu`, avant audit ;
`verifier_forme_reponse` vérifie la famille, `verifier_suite_faits` exige le geste
pour une faisabilité avant tout ajout. `faits` contient des chaînes, y compris
dans les réponses finales ; une source inconnue reste écartée. Ordre des champs,
consignes, modèle Luna et fournisseur local conservés ; voie d'achat du lot 159 intacte.

**Preuves.** **55 ciblés verts**, cinq fichiers. Console au Relais et à l'auberge :
six modes indisponibles, branche incohérente, suite absente/null, source inconnue ;
état complet et rendu rechargés identiques aux témoins. Crypte/atelier : état,
rendu et requêtes hors schéma identiques à la base. Nouveau témoin capturé sur
`7adc788` : le témoin L1 était antérieur aux changements déjà intégrés.
Suite unique : **2 205 tests, 250 fichiers, 16 ignorés, zéro erreur, 3 731,37 s**,
un worker réduit après l'intégration. Un échec de l'outil de mesure : suffixe
de cache L1 absent de sa reconstruction. Corrigé par `sources.voie_cache`,
égalité avec le fournisseur sur quatre voies, **12 ciblés repris verts** ;
mesures recalculées hors réseau, aucune seconde suite ni partie rejouée.
**8/8 empreintes 2 h Relais/auberge × quatre graines identiques** à `7adc788` :
chronique, mesures, état complet. Huit références absentes rangées une fois.

**Schéma après mutualisation**, `tools.mesure_prompt.mesurer` : six captures de
deux scènes, catalogues présents/épuisés, **22 760 → 30 003 caractères (+31,8 %)**,
variations **4/4 → 0/4**, mêmes consignes et entrées. Préfixe Luna simulé
**4 638 → 64 665 caractères**, sans garantie de cache. Sur les bancs réels,
outils moyens **28 657 → 30 003 caractères**, variations hors révisions
**53/90 → 0/86** ; selon les clés réelles de `sources.voie_cache`,
**0/92 variations** d'interprétation, relances comprises. Audit encore **44/74**.
L'agrégat « révision » mélange interprétation et récits.

**Luna**, deux passes × sept scripts distincts : référence `cdaf371`, neuf
parties cachées, cinq manquantes jouées une fois puis rangées. Branche :
**293 appels/88 tours MJ**, un repli, zéro incident technique/recharge.
Première passe commencée avant le garde de famille : aucune sortie archivée
ne déclenche les nouveaux gardes ; seconde passe sur code figé.

| Par passe 1 / 2 | Référence | Branche |
|---|---:|---:|
| Appels/tour, moyenne | 3,43 / 3,45 | 3,41 / 3,25 |
| Appels/tour, médiane | 3,5 / 4 | 3,5 / 3,5 |
| Secondes/tour, moyenne | 10,70 / 11,63 | 12,04 / 11,45 |
| Secondes/tour, médiane | 9,80 / 10,31 | 10,11 / 11,83 |
| Relances / refus / replis | 9/10/2 ; 5/15/1 | 8/15/1 ; 8/10/0 |

Jetons cachés, deux passes référence → branche : interprétation
**646 144 → 982 784**, audit **550 016 → 547 328**, révision
**134 784 → 162 816**, fidélité **0 → 4 096**, autres zéro.
`usage.attribution` : outils **688 612 → 876 819**, consignes
**597 777 → 740 395**, items **44 555 → 79 810**.
**Critère des refus atteint sur 16 audits** : 160 appels, cinq rejeux par côté,
requêtes identiques (auditeur inchangé), zéro erreur/rapport illisible,
perte maximale **1/5**. Faux souvenir de Gorm **5 → 4** ; deux autres refus
mécaniques **5 → 5**. Les faux refus historiques restent présents.

**Limites/livraison.** Aucun gain de secondes démontré : référence partiellement
cachée et poste partagé. Audit variable, consignes conditionnelles (L3), aucune
garantie sémantique nouvelle. Aucun serveur local mesuré, transport simulé couvert.
Vérification prolongée par l'attente du calcul d'intégration, sans seconde suite.
Copies seulement. Aucune clé de signature configurée, commits non signés ; branche seule poussée,
`main` intacte. Bruts : `artifacts/schema-158/` (mesures, SHA-256, scripts, refus),
`artifacts/bancs-multi/20261027-024413-32676/` (parties et résumé).
