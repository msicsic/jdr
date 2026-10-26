# Lot 98 — profil comparé de l’auberge (2026-10-26)

Branche `codex-profil-compare`, **non fusionnée**, base **61c854a**.
**Arrêt après diagnostic : aucun moteur, règle, scénario ou prompt modifié.**

**Protocole.** Auberge 1985, fixe puis tirée, mémoires propres à chaque version,
capture à 480, profil jusqu’à 720 avant bilan. `py-spy` absent :
`cProfile(timer=time.process_time)`, puis témoins séparés sans instrumentation.
`42bb9c0`/intégration en paires, deux calculs à priorité réduite, affinité libre,
poste partagé. Aucun cache de temps ni Luna.

**CPU normal**, ancien → intégration, secondes :

| Départ | Nuit 12 h | Rapport | Tranche 8–12 h |
|---|---:|---:|---:|
| Fixe | 127,38 → 244,41 | **×1,92** | 102,11 → 160,13 |
| Tiré | 94,48 → 273,92 | **×2,90** | 70,06 → 230,41 |

**Seuil ×1,5 manqué aux deux départs.** Aucun gain attribuable à ce lot.

**Profil 8–12 h**, temps propres additionnables, ancien → actuel, secondes.
Spatial inclut les cases libres des routes ; JSON/primitives gardent leur module.

| Famille | Fixe | Tiré |
|---|---:|---:|
| Délibération hors recherches + préparation de Vue | 14,67 → 18,09 | 11,19 → 14,98 |
| Recherche hors Vue, signatures et preuves | 253,95 → 343,39 | 199,05 → 635,88 |
| Routes et géométrie | 3,91 → 33,47 | 3,28 → 42,23 |
| Devis des remises | 6,73 → 2,31 | 6,06 → 10,53 |
| Parcours de graphes et certificats | 0,06 → 0,00 | 0,11 → 2,47 |
| Signatures de recherche | 2,38 → 3,72 | 1,13 → 2,81 |
| Perception, esprits, spatial, signes | 62,23 → 111,41 | 52,36 → 104,02 |
| Ouïe et voix | 1,64 → 7,13 | 1,84 → 5,06 |
| Marche/exécution hors appels ci-dessus | 4,84 → 4,25 | 4,30 → 5,09 |
| Banc et empreintes monde, hors JSON | 0,02 → 0,02 | 0,00 → 0,02 |
| JSON, primitives et autres | 147,67 → 228,13 | 121,94 → 287,97 |
| Total mesuré, instrumentation comprise | **499,09 → 752,81** | **402,14 → 1 111,61** |

Sauvegardes hors fenêtre, aux bornes. Repères **inclusifs, non additionnables**
fixe / tiré : `choisir`
423,72→613,98 / 330,34→993,06 ; `chercher` 399,20→586,17 / 310,31→977,34 ;
`_explorer_etats` 367,22→537,97 / 287,86→914,69 ; `gestes`
306,83→374,16 / 237,39→558,69. La reprise de certificats n’est pas le poste dominant.

**Dix plus fortes hausses propres de fonctions nommées**, Δ secondes fixe / tiré
(`p` = `planification`, fonctions anonymes exclues) :

| Fonction | Δ fixe | Δ tiré |
|---|---:|---:|
| `dict.get` | +26,81 | +70,08 |
| `spatial._bloquantes` | +32,03 | +33,20 |
| `p._normaliser_suites` | +16,73 | +41,55 |
| `p.Etat.apres` | +12,97 | +33,47 |
| `p.gestes` | −11,59 | +55,22 |
| `p.Vue.arrivee` | +11,14 | +19,25 |
| `p.Vue.mesure_aller` | +8,95 | +16,89 |
| `p._mesurer` | +8,41 | +16,03 |
| `p.Vue.prix_route` | +5,00 | +12,45 |
| `p._parts_calculer` | +6,88 | +10,23 |

Soit 44 % de la hausse ; générateurs de `planification` regroupés : +73,14 s.
Les fonctions extraites depuis l’ancien code ne sont pas des causes isolées.

**Fréquence**, compte puis appels/minute sur 240 minutes :

| Appels | Fixe ancien → actuel | Tiré ancien → actuel |
|---|---:|---:|
| `choisir` | 3 578→4 840 ; 14,91→20,17 | 3 321→3 964 ; 13,84→16,52 |
| dont hors filet minute | 1 658→2 920 ; 6,91→12,17 | 1 401→2 044 ; 5,84→8,52 |
| `chercher` | 4 020→6 350 ; 16,75→26,46 | 2 517→4 674 ; 10,49→19,48 |

Filet minute : **1 920 choix** partout. Recherches/choix :
1,12→1,31 fixe, 0,76→1,18 tiré. Moyenne instrumentée par recherche :
**99,30→92,31 ms** fixe, **123,29→209,10 ms** tiré ; par choix :
118,42→126,86 / 99,47→250,52 ms. **Plus de décisions et de recours**,
et des recherches plus chères dans le tiré. Décomposition descriptive
`Δ(N×coût moyen) = ΔN×coût ancien + N actuel×Δcoût` sur les deux départs :
environ **497 s (58 %) de fréquence**, **357 s (42 %) de coût moyen** dans
les **854 s** supplémentaires de `chercher`. Mondes et composition différents :
aucune attribution causale aux seuls événements, trajets réels ou recours.

**Arrêt prescrit.** Le levier principal de fréquence, réduire les relances,
peut changer les décisions sans preuve de mêmes entrées/effets : **rien
implémenté**. Piste exacte secondaire : dans `trajet_estime._moyenne`, relever
les obstacles une fois au lieu de rescanner tous les objets par case.
Cet appelant porte 59,31 des 65,00 s de `_bloquantes` en fixe ; son gain CPU
normal et l’atteinte du seuil restent inconnus. Aucun gain moteur livré.

**Contrôles/limites.** Huit recharges vertes (état, `regarder`, `scene_percue`).
Profil/témoin : mêmes compteurs, mesures et états à 480/720 pour les quatre
nuits (SHA-256 canoniques dans le bilan). Syntaxe des outils et analyse finale
validées. Petits appels amplifiés, une graine, une paire
par départ, poste partagé : pas de garantie générale de temps.
Pas de suite complète, empreintes quatre scénarios, `VERIFIER` ou mine
(conditionnés à l’implémentation). Outils `profil_compare_98.py`,
`bilan_profil_98.py` ; bruts et reproduction : `artifacts/profil-98/` du worktree.
Créneau de 45 minutes dépassé par les profils complets et leurs témoins.

**Suite à décider :** accepter un lot modifiant la cadence des relances
(donc potentiellement les réactions), ou conserver l’identité stricte et
mesurer seulement le partage local des obstacles, au gain encore inconnu.
