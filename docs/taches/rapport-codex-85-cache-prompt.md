# Lot 85 — Préfixes constants des requêtes au MJ

25 octobre 2026 — Branche `codex-cache-prompt`, **non fusionnée**. Reprise
d'`origin/integration` **a2261e6**, puis du préalable 83 **f1d198b** ; fusions
locales signées **589adb4**, **f573250**. **Validation partielle : préfixes
constants, mais cible globale de 70 % manquée et comportement Luna dégradé.**
Code signé **52991b6**, signatures SSH des trois commits vérifiées localement.

**Invariant et fonctions.** `mj.schema_reponse` décrit tous les types de la
version ; `INSTRUCTIONS_REPONSE` réunit les règles conditionnelles et celles
des corrections. Phase, modes autorisés, catalogues, faits et consignes de
narration restent dans l'entrée du tour. `narration.schema_audit` devient un
tableau constant avec indices, comptes et éclairages ; le moteur conserve le
contrôle de couverture et de sources. `couverture_action.schema` enveloppe les
deux jugements dans `rapport` ; `auditer_portee` utilise toujours le schéma
portant `usages`, vide sans proposition de faits. Anciens rapports conservés
en lecture. Les préparateurs, refus et gardes d'enregistrement restent inchangés.
OpenAI reçoit une clé de cache par partie et fonction, mais garde la session
de transport par partie : une WebSocket, contexte complet, `store: false`.

**Mesure.** `tools/mesurer_cache_prompt.py` lit les fils, distingue schémas,
instructions et préfixes complets, respecte l'ordre sérialisé des propriétés,
additionne les tokens et signale les usages absents. Relecture des 388 appels
historiques : **23,45 %** en cache ; **59** préfixes MJ (50 schémas,
19 instructions) et **44** préfixes d'audit narratif, constat reproduit.

Pour les onze scripts communs, historique sur deux passes → nouvelle passe :

| Fonction | Préfixes avant → après | Tokens en cache avant → après |
|---|---:|---:|
| `repondre_au_joueur` | 46 → 1 | 30,51 → **71,81 %** |
| `auditer_narration` | 40 → 1 | 10,30 → **36,45 %** |
| `auditer_action` | 2 → 1 | 1,47 → **0 %** |
| Ensemble | — | 24,61 → **62,70 %** |

Ratios pondérés par les tokens, appels froids compris, aucun usage manquant.
Tokens hors cache par passe : 1 354 247 → 1 047 148 (−22,7 %).
`auditer_portee` non exercé dans ces onze scripts : pas de taux revendiqué ;
constance des deux voies vérifiée hors modèle. Un préfixe constant ne garantit
pas son service par le fournisseur ; l'entrée de scène reste variable. Aucun
remplissage ajouté pour gonfler artificiellement le pourcentage.

**Luna, une passe.** Onze scripts du lot 79, uniquement `gpt-6-luna`, ChatGPT,
medium/libre, quatre exécutions au plus à priorité réduite, copies temporaires.
Les 22 références **882907c** sont exclusivement lues du cache ; leur identité
SHA-256 avec les bruts historiques est vérifiée. Par passe : **154 → 208 appels
/ 53 tours MJ**, **2,91 → 3,92 appels/tour**, **12,82 → 18,68 s/tour** ;
relances **5 → 26**, refus **7,5 → 8**, tours avec refus **6,5 → 8**, replis
**0 → 6**. Aucun arrêt, erreur technique ni recharge invalide. Temps historiques
mesurés sous une autre charge, et lot 83 absent de la référence : pas de
conclusion causale sur la vitesse du transport.

**Régression identifiée.** La disparition des énumérations permet de produire
des sources qui ne sont pas des clés du dossier : `conversation_validee.faits`,
`comptes.issue`, identifiants de signes et d'impressions. Elles sont écartées
par le contrôle commun ; des assertions perdent leur fondement et sont
redemandées, puis parfois remplacées par un repli. Exemples : signes-écart
**6 → 10 appels**, soir-appel **17 → 30**, trois replis ; noms-dialogue
**15 → 19**, source imbriquée sur le déplacement de Brune. D'autres faux rejets
sémantiques d'ambiance et de fidélité persistent. Le texte de noms-dialogue
dit même « Tu passes par l'espace » alors que la position rechargée du joueur
reste `[1, 3]` : aucune nouvelle garantie générale de vérité narrative.
Le résultat ne justifie donc pas une intégration comme amélioration transparente.
Aucune seconde passe Luna ni exception de scénario.

**Tests et empreintes.** Suite complète unique : **1 925 tests, 16 ignorés,
zéro échec/erreur**, 197 fichiers, trois processus à priorité réduite,
**1 806,10 s**. Six tests finaux du lot verts (2,29 s), dont le contrôle des
deux voies de portée ajouté après le passage initial de ce fichier :
**1 926 tests consolidés**, sans seconde suite complète.
Les tests exercent deux scènes et deux tours dans
la console avec le vrai transport simulé, état, texte enregistré et vue après
recharge ; alternance des phases et corrections, types des contre-revues,
sources et cibles hors scène, mêmes refus avec `attendu`, mesure pondérée.
Empreintes 2 h, Relais, graines 1985/7/42/2024, un processus à priorité réduite :
**quatre nuits identiques** à l'intégration **a2261e6**, chronique, mesures et état
final complet. Références manquantes calculées une fois et rangées en cache ;
aucune donnée de scénario touchée, aucun autre scénario rejoué.
Créneau de 45 minutes dépassé, avec une suite complète de trente minutes.

Bruts : `artifacts/lot85/` et quatre dossiers
`artifacts/bancs-multi/20261025-190213-*` du worktree. Aucun scénario, modèle,
planificateur ni `main` modifié par le lot.
