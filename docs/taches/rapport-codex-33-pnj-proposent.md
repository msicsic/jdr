# Lots 33/36 — Les PNJ proposent, coût du geste (A2b)

**`codex-proposer-cout`, non fusionnée ; lot non validé.** Base `ffcc295`, reprise
de `684ee70`, correctif signé SSH `0da76ef`. Sans Luna, priorité réduite, ≤ 4 travailleurs.

**Invariant.** `pnj_propositions.preparer` calcule candidats et devis avant
l'expansion, sur les moyens et croyances du départ : une offre par auditeur/sorte.
`gestes` rejoue les effets sans double cession ; tenir/trahir restent deux voies.
`_entrees` identifie l'approximation, `VERIFIER` recalcule sa sélection. L'exécution
garde le marché commun, les engagements et la publication atomique du lot 33.

**CPU apparié**, versions lancées ensemble, 4 h, 42/1985, moyenne par nuit :

| Scénario | `ffcc295` / `684ee70` initial | `ffcc295` / final | Surcoût final |
|---|---:|---:|---:|
| Mine | 12,18 / 114,31 s | 11,49 / 72,88 s | +534 % |
| Auberge | 11,25 / 86,16 s | 11,45 / 50,88 s | +344 % |

**Cible +20 % non atteinte**, gain contre `684ee70` : 36 % / 41 %. Profil mine 42 :
Devis dans l'expansion : 1 374 → **0** ; aucune évaluation dans l'expansion.
Restent 682 devis en amont : 55,81/88,80 s CPU ; par recherche, 0,370 devis et
0,0027 évaluation. Offres/développements : 9 831/53 158 → 4 177/33 674.
Les devis serrure/feu dominent encore ; nœuds : porte de réserve 60 168,
garde-manger 25 799. Diagnostics complets par but dans les traces.

**Banc final**, 4 h × quatre graines, référence `ffcc295` réutilisée ; sommes :

| Scénario | Offres / acceptées | Tenues / trahisons | Vols avant → final | Minutes sans recours avant → final |
|---|---:|---:|---:|---:|
| Relais | 5 / 0 | 0 / 0 | 6 → 6 | 180 → 180 |
| Mine | 10 / 2 | 0 / 0 | 2 → 2 | 65 → 50 |
| Auberge | 12 / 1 | 1 / 0 | 0 → 0 | 80 → 30 |
| Crue | 4 / 0 | 0 / 0 | 9 → 9 | 300 → 300 |

Seize nuits sans plantage, usurpation ni écart. Alternance du Relais 7 disparue ;
mine 2024, devoirs satisfaits et attente, pas de plan bloqué. Crue 2024 : mêmes
trois alternances que la référence, bruits distincts.
[Les quinze vols restants, un par ligne, et ces lectures](../plan-relations.md#lecture-des-nuits-du-lot-36).

**Vérifications.** Douze tests A2b verts, état/rendu après recharge compris.
`VERIFIER` + spatial 1, 2 h/42, crue/mine : sans écart. Suite complète :
**1 688 tests, 4 ignorés ; bilan consolidé : 7 échecs, aucune erreur technique**.
Une passe de 156 fichiers (6 023 s, deux travailleurs), puis seules reprises de
six fichiers adaptés (63 tests uniques). Restent quatre échecs de réemploi,
le poêle éteint, les signalements sans appel et l'achat du bois à Mireille plutôt
qu'Odile. Assertions conservées ; scènes isolées par des refus de marché ordinaires.
Créneau de 45 minutes dépassé.

**Limites.** Acquisition, lumière découverte ensuite ou second marché peuvent
rendre meilleure une offre écartée. Promesses sans gain cru exclues. Le bénéfice
intermédiaire du Relais est perdu (4→6 vols, 60→180 min sans recours). **3e non
atteint** : aucune proposition de Brune avant ses vols des sept nuits Relais/crue ;
autres recours non prouvés exhaustivement. Conversion/réparation/intermédiaires hors lot.

Traces non versionnées : `artifacts/36-{temps-avant,temps-apres,profil-avant,rapide,controle,suite-consolidee}`,
diagnostics et `36-lecture.txt`.
