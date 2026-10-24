# Lot 60 — Clôture commune du rendez-vous

Branche `codex-rendez-vous`, non fusionnée ; base `c592d68`, brief `5e24408`,
mise à jour initiale avec l'intégration **04bca30**. Aucun appel à Luna ; `main` inchangé.

**Cause et changement.** Capture auberge 42 recréée sur `5c2ce81` à 500 minutes
(bruts du brief absents). Odile aperçoit Anselme à travers une porte, lève seule son attente
et repart avant qu'il traite la rencontre ; il conserve la venue vers l'ancienne salle.
`appel.tenir` garde l'attente jusqu'au choix du voyageur après son geste et son arrivée au
lieu convenu ; l'aperçu le réveille. `appel.retrouves` clôt les registres correspondants
des deux, actualise leurs perceptions et réveille leur choix avant d'écrire une seule
retrouvaille. `deliberation.rejoint` y délègue aussi pour les dialogues, joueur compris.
« Me voici ! » passe par l'ouïe commune en cas de perception asymétrique.
`planification.py`, scénarios, consignes et modèles inchangés.

**Tests.** Capture versionnée `tests/data/rendez-vous-auberge-42-500.json.gz` ; rejeu à
510 minutes, branche avant → après : appels **9 → 1**, retrouvailles **5 → 1**, la demande
de bois reprend. Les registres sont vérifiés clos avant l'annonce. Six tests couvrent aussi
le Relais, le joueur appelant/appelé et celui qui vient, l'appelant parti et une autre attente
préservée. Après recharge : égalité du `data` complet, de l'ouïe et de la description du lieu,
temps d'un bloc ou par minutes. Deux anciens attendus sociaux vérifient l'avis reçu et la
baisse de confiance : une rumeur unique ne franchit pas nécessairement l'hystérésis.

**Banc rapide.** Comparateur contre `c592d68`, 4 h × quatre scénarios × graines
1985, 7, 42, 2024, trois processus ; 16 références en cache. Toutes les mesures de jeu
identiques ; aucun plantage, violation ou usurpation. Maximum moyen des passages/PNJ/h :
Relais **6,5**, mine **7,25**, auberge **13,75**, crue **24,75**. La scène est après 4 h.

**Audit 12 h, branche seule.** Auberge 42 et 7, deux processus : aucun plantage,
usurpation ou écart signalé par les mesures ordinaires ; sans `VERIFIER`.

| Graine | Appels | Retrouvailles | Redites à moins de 10 min | Maximum de passages/PNJ/h |
|---|---:|---:|---:|---:|
| 42 | 15 | 7 | **2** | 22 |
| 7 | 8 | 4 | 0 | 31 |

**Réserve :** à 462–463, Odile repart après la clôture avant la demande ; de nouveaux
appels ouvrent d'autres rendez-vous. **L'absence générale de retrouvailles rapprochées n'est
pas acquise**, malgré la clôture bilatérale. Aucun délai anti-appel ni exception de scénario
ne masque ce défaut. Restent aussi du noir prolongé, des buts alternés et un avertissement redit.

**Suite complète unique :** 1 810 tests, un ancien attendu social en échec, quatre sauts,
693,1 s, trois processus à priorité réduite. Après ajustement et reprises ciblées (44 tests),
**bilan consolidé : 1 811 tests, quatre sauts, aucun échec restant** (`bilan-tests.json`).

**Limites.** Clôture au choix après arrivée dans la salle convenue, sauf dialogue échangé ;
l'aperçu au seuil ne termine plus le trajet. Échéance et urgences conservées ; disponibilité
ultérieure non garantie. Bruts dans `artifacts/codex-60/` du worktree ; temps en cache non comparés.
