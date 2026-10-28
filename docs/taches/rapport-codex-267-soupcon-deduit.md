# Lot 267 — Soupçon déduit

Branche `codex-soupcon-deduit`, **non fusionnée** ; base `7404d2d`, code
`61a1a67`. Bruts : `C:/Users/msics/donjon/artifacts/soupcon-267/`.

**Changement.** `esprits._constater_bien` compare deux constats propres
datés et les présences perçues dans les quarante souvenirs communs, sans
position cachée ni chronique. Un seul suspect donne l'épreuve relationnelle
`soupcon_deduit` : confiance **−6 à −18 selon PSY**, preuve **0,4**, source
`devine`, sans portage établi ni nom appris. Geste connu/propre et épuisement
exclus ; conséquences concomitantes regroupées. `reviser_soupcons` lève
l'indice au retour, à la réparation ou à l'attribution apprise, compensant
la seule perte appliquée. État enregistré avant récit.

**Tests.** **118 ciblés distincts : 117 verts, un échec préexistant**, onze
fichiers. Onze nouveaux tests, Gorm/réserve et Anselme/coffre avec
contre-épreuves ; monde/rendu/scène conservés après recharge et laps
3 ou 1+1+1. Captures `relais.json`, `auberge.json`, résultats
`tests.json`, `tests-soupcon-final.json`. Ni suite complète ni Luna.

**Preuve de dette.** Le seul test
`tests.test_relations_graduees.TempsEtContratsTests.test_dette_soldee_une_fois_par_demande_acceptee`
rejoué sur **7404d2d** puis **61a1a67** échoue identiquement : **1 test,
1 échec, aucune erreur**, `AssertionError: 40 != 20`, ligne 325. Même
fichier (SHA-256 `ddc685f3…`). Traces complètes `dette-base.json/.log` et
`dette-branche.json/.log` ; copie isolée de base retirée.

**Comparaison à la base exacte : différente, lot non validé.**
`tools/comparer_bancs.py --reference 7404d2d --branche 61a1a67 --heures 4
--depart tire --scenarios relais mine auberge crue crue_hameau --graines
1985 7 42 2024 --processus 2` : **20 nuits de chaque côté lues en cache,
aucune nuit 4 h rejouée**. Le contrôle `comparer_identite` du mode
`--empreintes` est appliqué aux empreintes finales, chroniques et mesures
déjà enregistrées ; les clés distinctes du mode `--empreintes` sont absentes.
**16/20 chroniques, 3/20 mesures identiques ; états bruts 0/20**, les nouveaux
champs `constats_biens`/`soupcons` différant dès la création à la minute 0.
**Zéro plantage/usurpation ; zéro soupçon né**. Suspects 219 **2 → 3**,
seule hausse en **crue 2024 : 0 → 1** (Gorm, devoir/interposition).
À expliquer **55 → 54**, dérives **233 → 234**, cycles **489 → 489**.

Richesse S/F/D moyenne, `cats` du lot 183 : famille × auteur × texte,
D incluant les PNJ inactifs.

| Scénario | Base = branche (S/F/D) |
| --- | --- |
| Relais | 13,25 / 4,25 / 1,563 |
| Mine | 28,5 / 4,75 / 2,036 |
| Auberge | 11 / 4,25 / 1,063 |
| Crue | 18,75 / 6,25 / 2,75 |
| Hameau | 21,75 / 7 / 2,083 |

**Première divergence de chronique : crue 2024, Ilse, 39 min 31 s**
(`instant=23710`) : « Ilse reste dans la lumière » est répété dans la branche.
`esprits._retenir_presence` remplit la mémoire commune ; juste avant cet
instant, **11 des 40 souvenirs sont des présences**. Une parole de Gorm
chasse le souvenir `abrite` de minute 3 ; `pnj._abriter` le recrée et répète
la narration. Rejeu ciblé **40 min**, base/branche puis ablation de la seule
fonction `_retenir_presence` sur une simulation : **chronique et toutes les
mesures retrouvent exactement la base**. Effet hors soupçon causalement
établi sur cet horizon ; les autres différences ne sont pas toutes localisées.
Les quatre chroniques différentes : mine 7/42, crue 7/2024.

L'ancien banc contre `main c870c8b` n'isole pas le lot : ses baisses de
richesse ne lui sont pas attribuables. **Effet hors scènes établi** ; aucun
moteur corrigé dans ce diagnostic. Bruts `comparaison-base-cache.json`,
`bilan-base.json`, `localisation-base/{base,branche,sans-presences}.json`
(mémoires avant/après et pile d'appel). Calculs courts à priorité réduite,
deux processus au plus ; aucun calcul actif.

**Limites.** Soupçon faillible après oubli ; aucune naissance de
`récupérer` sur ce seul indice ni interpellation autonome nouvelle.
Effraction couverte par dégradation constatée, sans crochetage invisible
ni disparition distante déduite du registre. `agendas.py`, `echanges.py`,
choix de délibération, scénarios et MJ inchangés.
