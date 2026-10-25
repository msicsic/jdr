# Lot 87 — attendre après une recherche bornée

Branche `codex-borne-attente`, **non fusionnée** ; base **020250e**, code signé **a82f469**. Aucun appel à Luna ni changement de `main`.

**Mesurer d'abord.** Auberge 1985, 12 h : appels bornés en fixe, Joss/faim **179**, Lucien/garder:grenier et etable **64 chacun**, Joss/chaleur **18** ; **258/321 paires** successives aux mêmes entrées communes, dont **144** avec prix changés. Tiré : Joss/faim **33**, Tilo/faim **17**, Lucien/placer:ballot **15**, deux gardes **6 chacune** ; **52/66 paires** aux mêmes entrées, dont **38** avec prix changés. Croyances, moyens, lumière, refus, permissions et prix sont conservés dans les relevés. Quatre séries tirées aboutissent : grenier **588**, Joss/faim **622**, chambre chaude **648/706** ; toutes changent une croyance. Aucune en fixe.

**Règle.** `chercher` prépare l'effort borné sans plan ; `vues_du_choix` l'enregistre dans `esprits.attentes_bornees` après l'évaluation des candidats, restés en lecture seule. Requête isolée et choix interrompu ne consomment aucun effort durable. Même graphe admissible et mêmes paliers d'urgence/désespoir : zéro exploration après recharge, sans délai. Les prix continus de faute/casse seuls ne réveillent pas ; leurs interdits restent dans la signature. Une nouvelle lecture ou un palier réveille le recours ; sans motif explicite, les paliers couvrent tous les besoins. Les autres recours sont toujours essayés. Aucune impossibilité affirmée ; algorithme, plafonds et scénarios inchangés. Le banc distingue `attente`.

**Décisions et conservation.** Quatre nuits mine/auberge × fixe/tiré, **12 h** : **tous les résultats d'appels logiques, chroniques, récits et états finaux identiques**, hors registre d'attente ; rendus et scènes identiques après recharge. Aucun geste différent observé : la décision changée est celle de refaire l'effort. Les quatre plans restent trouvés **aux mêmes instants**. Rejeu indépendant : attente antérieure injectée dans chaque capture de référence, recharge, recherche et vues rechargées, **quatre succès**.

**CPU final, secondes**, trois versions lancées ensemble, un processus chacune, priorité réduite :

| Nuit | `42bb9c0` | Base | Branche | Bornées neuves | Attentes |
|---|---:|---:|---:|---:|---:|
| mine fixe | 262,56 | 86,11 | 86,42 | 0 → 0 | 0 |
| mine tirée | 111,64 | 146,69 | 147,92 | 19 → 19 | 207 |
| auberge fixe | 116,38 | 284,16 | 222,80 | 211 → 68 | 257 |
| auberge tirée | 94,44 | 374,94 | 343,12 | 63 → 25 | 52 |

Auberge : **−21,6 % / −8,5 %** CPU ; après 8 h, **233,31 → 172,53 s / 326,08 → 297,30 s**. Nœuds **1 061 077 → 489 077 / 1 327 083 → 1 175 083**. **Cible ×1,5 manquée : ×1,91 / ×3,63** contre l'ancien moteur. Mine tirée : les attentes remplacent des reprises exactes déjà sans exploration ; aucun gain. Les mesures préliminaires sont archivées : cohorte CPU refaite après correction du contrat, pour mesurer le code final sous la même charge.

**Vérifier.** Sept tests nouveaux : frontière du choix, Joss, vivre découvert puis mangé, refus levé, désespoir de Brune, recours sans motif, échec non borné, même laps découpé et rechargé. Suite complète unique : **1 933 tests, 16 ignorés, quatre échecs**, 199 fichiers, **1 245,40 s**. Contrat corrigé, requêtes isolées préservées, deux empreintes historiques normalisent seulement le registre vide. **44 tests ciblés finaux verts**, dont une nouvelle épreuve : **1 934 tests consolidés**, 16 ignorés, sans seconde suite complète. `VERIFIER` + spatial à **1**, auberge 42, **2 h** : **aucun écart ni borne**, **308,14 s CPU**, monde et vues rechargés identiques.

Banc rapide final **4 h × quatre graines × quatre scénarios**, deux processus :
**16 références en cache**, 16 nuits de branche ; chroniques, récits et audits
identiques, zéro plantage, usurpation, violation ou boucle nouvelle. Vols, sans
recours et temps en attente inchangés ; seules les recherches neuves d'auberge 2024
baissent **173 → 167**. Constats préexistants : `fige_presse` **4**,
`voir_alterne` **2**, `noir_long` **1**, `eau_longue` **1**.

**Limites.** La signature commune peut réveiller le but pour un changement finalement inutile. Une variation de prix peut faire trouver un plan sous le plafond : hors des nuits vérifiées, l'attente peut le retarder jusqu'au prochain réveil. Aucune garantie universelle nouvelle. Créneau de 45 minutes dépassé : correction après la suite et reprise des mesures. Bruts, tranches, captures et rejeux : `artifacts/attente-bornee/` ; trois outils livrés (mesure, bilan, rejeu).
