# Lot 49 — devis sans voie d'allumage

Branche `codex-devis-vides`, non fusionnée ; base `3aba83b`, ancien `42bb9c0`.
Aucun Luna, prix, plafond, scénario ni fichier réservé modifié ; `main` inchangée.

**Diagnostic avant modification.** Capture auberge 1985, 480–540 min, pas moteur
de cinq minutes : 4 555 devis calculés, 2 025 vides. Parmi eux, 70 n'ont aucun
allumage ; 1 955 ont un candidat d'allumage sans suite terminale (notamment les
placements qui exigent plusieurs gestes). Cette tranche depuis la capture diffère
de la fin de nuit du brief (3 963 / 2 845). Les sources incompatibles, chargées,
contrariées, inaccessibles ou non obtenables sont déjà écartées avant `_preparer`.

**Condition nécessaire.** Après accès à la source, `part_estimee._allumable`
exige une voie possible : source déjà allumée, autre flamme portée ou accessible
et obtenable, feu demandable au porteur, ou source fixe allumée accessible pour
une source mobile. Permissions, refus, budget, `seul` et routes sont communs.
Toute suite de `_preparer` passe par l'une de ces voies ; leur absence prouve
l'impossibilité. Retour et approches restent optimistes. La passe de découverte
garde ses lectures de lumière. Cache local par état complet et source ; lectures
extérieures déjà dans `_entrees`, aucune lecture nouvelle du monde. Preuve dans
`docs/plan-planificateur.md` ; aucun changement dans `planification.py`.

**Effet sur la capture.** 834 préparations sur 6 182 évitées, 5 348 conservées ;
70 devis vides ne développent plus aucun `_preparer`. Mêmes résultats : 4 555
devis, 2 025 vides. L'accès initial aux sources reste évalué, les comptes de nœuds
ordinaires et de `SuiteDifferee` sont inchangés.

**12 h.** Trois versions lancées ensemble, priorité réduite, file commune de
quatre nuits au maximum, deux par version (même `_lancer` de
`tools/empreintes_nuits.py`). CPU en secondes, triplets **ancien / base / branche** :

| Nuit | Total CPU (s) | 0–4 h | 4–8 h | 8–12 h | Nœuds ancien / base = branche |
|---|---|---|---|---|---:|
| mine 42 | 88.89 / 107.09 / 106.00 | 8.92 / 10.16 / 9.92 | 16.08 / 17.09 / 16.97 | 63.83 / 79.78 / 79.05 | 1086681 / 907820 |
| mine 1985 | 78.23 / 494.97 / 489.36 | 7.91 / 10.73 / 10.64 | 20.12 / 53.19 / 51.98 | 50.12 / 430.98 / 426.67 | 634361 / 2102158 |
| auberge 42 | 69.33 / 203.22 / 193.84 | 5.58 / 9.20 / 8.02 | 10.67 / 59.88 / 54.66 | 53.00 / 134.03 / 131.08 | 606024 / 672447 |
| auberge 1985 | 55.97 / 162.58 / 163.69 | 4.50 / 7.16 / 7.34 | 9.47 / 37.67 / 38.02 | 41.97 / 117.69 / 118.25 | 694868 / 498868 |

CPU moyen mine : 83,56 / 301,03 / 297,68 s (**−1,1 %** contre la base) ; auberge :
62,65 / 182,90 / 178,77 s (**−2,3 %**). Auberge 1985 : **+0,7 %**, sans gain uniforme.
Encore ×3,56 / ×2,85 contre l'ancien moteur, qui précède d'autres mécaniques.
Une seule campagne : aucun facteur constant démontré.

**Validation.** `comparer --calcul` : quatre nuits, zéro différence de monde,
chronique, mesures, récit, souvenirs, repères et résultats de recherche complets.
Empreintes 2 h, quatre scénarios × quatre graines : identiques à `3aba83b`
(16 références en cache, temps non comparés). Trois nouveaux tests : captures
rechargées vécues quinze minutes, toutes les recherches et le rendu ; deux scènes
sans flamme sans aucun préparatif ; deux scènes avec flamme, mêmes suites puis
remise, recharge et lumière réelles après sauvegardes.

`VERIFIER` + spatial 1, mine/auberge 42, 2 h : aucun écart, borne ni usurpation.
Suite complète unique (`tools/tests.py --processus 3`), priorité réduite :
**1 737 tests, quatre ignorés, zéro échec**, 167 fichiers, 781,4 s.
Le lot dépasse 45 minutes avec les vérifications expressément demandées.

**Limites.** Les 1 955 autres devis vides restent développés ; leurs approches et
leur conclusion ne sont pas certifiées par ce filtre. Le but
est une fonction arbitraire : une liste de types de buts ou d'objets ne prouverait
pas leur impossibilité générale. Le devis garde son approximation terminale et
la replanification après remise réelle. Ce lot ne résout pas le coût des bancs.

Bruts : `artifacts/codex-49/` du worktree (diagnostics, nuits, tranches CPU,
empreintes, tests). Les temps instrumentés du diagnostic ne mesurent pas le gain.
