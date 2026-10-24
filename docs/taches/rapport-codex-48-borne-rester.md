# Lot 48 — borne du séjour final

Branche `codex-borne-rester`, non fusionnée ; base **3aba83b**, ancien moteur **42bb9c0**.
Code signé **970d6f5**. Aucun appel au modèle, aucun tarif, prix, scénario ou plafond modifié ; `main` non touchée.

**Borne.** `Vue.borne_rester` : `RESTER × min(gardes laissées ailleurs + eau)` sur les sorties relaxées.
Les autres pressions sont non négatives : admissibilité ; H constant, H+B aux suites différées,
zéro aux résultats : cohérence. `_explorer_etats` conserve g/rang, découverte sans H, graphes et certificat.
Lectures couvertes par `_entrees`. Preuve dans le
[plan](../plan-planificateur.md#borne-du-séjour-final--lot-48-codex-borne-rester-non-fusionnée).

**Contrat précisé par l'utilisateur** : mêmes décisions hors plafond ; sinon, même coût que la complète
(`REFERENCE`, 60 000 états, emplois libres), ou aucun plan si elle n'en trouve pas. `_verifier` contrôle
la référence uniforme sans H, consigne `BORNES/ancienne_borne=True`. Pas de comparaison après bifurcation.

**Premières divergences validées** ; résultats identiques avant chacune. Référence : aucun plan à 4 000 ;
complètes non plafonnées :

| Auberge, Lucien | Résultat optimisé = complet | États optimisés / complets |
|---|---|---:|
| 42, min 559, `garder:grenier` | Recharger puis allumer la lanterne, revenir au grenier ; coût 78,92250378787878 | 78 / 5 759 |
| 1985, min 486, `garder:etable` | Rester, plan vide ; coût 90 | 102 / 4 180 |

Captures : [contrat.json](../../tests/data/borne-rester/contrat.json). Mines entièrement identiques,
recherches comprises ; auberge 1985 : chronique identique, état/recherches différents. Les 16 empreintes de 2 h sont identiques.

**Mesures 12 h, sans cache.** Trois versions lancées ensemble, deux nuits au plus par version,
plafond commun de trois processus plus un contrôle exhaustif, priorité réduite. Dans chaque cellule CPU :
**ancien / base / branche**, secondes ; tranches relevées à 240, 480, 720 minutes.

| Nuit | CPU total | 0–4 h | 4–8 h | 8–12 h | Nœuds base → branche |
|---|---|---|---|---|---:|
| Mine 42 | 73,59 / 90,02 / 89,67 | 6,67 / 7,94 / 7,88 | 13,06 / 14,31 / 14,17 | 53,80 / 67,73 / 67,58 | 907 820 → 907 820 |
| Mine 1985 | 65,44 / 510,52 / 511,84 | 6,14 / 8,94 / 9,16 | 17,20 / 44,84 / 44,98 | 42,05 / 456,66 / 457,64 | 2 102 158 → 2 102 158 |
| Auberge 42 | 60,53 / 213,41 / 296,12 | 4,70 / 8,94 / 8,77 | 9,00 / 58,97 / 48,61 | 46,78 / 145,38 / 238,59 | 672 447 → 881 560 |
| Auberge 1985 | 64,70 / 177,06 / 137,09 | 5,19 / 8,44 / 8,39 | 11,08 / 41,98 / 40,41 | 48,38 / 126,56 / 88,23 | 498 868 → 382 202 |

Après bifurcation : aucune violation/usurpation ni nouvelle boucle persistante. Auberge 42 : gestes 813→845,
attente urgente 555→515, noir 885→605 min ; bascules 1→1, passages/heure maximum 28→28, aides 5→4.
Avertissements 7→8 : mêmes paroles Odile→Tilo à 421/595, seconde crue au lieu de douteuse, sans répétition ajoutée.
Auberge 1985 inchangée : gestes 578, attente 560, noir 760, bascules 0, passages 31, aides 3.

**Vérification.** Huit tests : Lucien à 480 min, 3 688→663 états, même résultat/monde/rendu rechargés ;
lumière mine H=0 ; graphes, égalités, arrondis, découverte, certificat ; cas 559 avec complète et conséquences.
Onze ciblés verts. `VERIFIER` + perception à 1,
2 h, mine/auberge 42 : aucun écart, aucune borne. Suite finale unique : **1 742 tests, 4 ignorés, aucun échec**,
736,2 s, trois processus à priorité réduite.

**Limites.** Pas de gain global : 991,01→1 034,72 s CPU (**+4,4 %**), trajectoires divergentes ;
auberge 1985 −22,6 %, auberge 42 +38,8 %, mine inchangée. Coût des nuits longues toujours ouvert.
H parfois nul ; complète limitée à 60 000 ; décisions après bifurcation non auditées individuellement.
Lot au-delà de 45 min, mesures reprises après clarification.
Bruts, rejeux des premières divergences, chroniques et tranches : `artifacts/codex-48/final/` du worktree.
