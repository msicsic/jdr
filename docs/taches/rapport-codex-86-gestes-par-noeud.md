# Lot 86 — préparation des gestes (2026-10-25)

Branche `codex-gestes-par-noeud`, **non fusionnée**, base **02c8e8b** ;
`origin/integration` déjà ancêtre. Code signé **9f344cd**. Aucun appel à Luna,
changement de scénario, coût, plafond ou choix ; `main` inchangé.

**Invariant.** `Vue.situations_gestes` partage lieux/portée par salle,
possessions, agissables et faits `lieu`/`ouvert`/`assomme` ; `droits_gestes`
partage les droits par `permis`/`achete`/`acquis`/`faute`. Préconditions des
parts (`lot_partageable`) et compatibilités de combustible préparées une fois.
Les lectures variables et `Etat.apres` restent propres au nœud ; les parts
gardent l'état complet pour le but arbitraire. Aucune lecture de lumière
déplacée, aucune table sauvegardée ; contrat dans `docs/plan-planificateur.md`.

**Profils.** Capture à 600 min obtenue en continuant celle à 480 avec la base.
Vingt recherches neuves par processus, CPU sans profileur :

| Joss/faim | Nœuds/recherche | Base → branche, µs/nœud | Gain |
|---|---:|---:|---:|
| 480 min | 149 = 149 | 335,6 → 288,4 | 14,1 % |
| 600 min | 2 065 = 2 065 | 554,3 → 425,6 | 23,2 % |

Familles, temps inclusifs par ligne dans une passe distincte (5/2 recherches),
**µs/nœud base → branche**, surcoût d'instrumentation inclus :

| Famille | 480 min | 600 min |
|---|---:|---:|
| Aller | 142,0 → 139,7 | 62,3 → 52,9 |
| Objets, portée, droits | 321,4 → 229,5 | 351,6 → 185,1 |
| Prendre | 21,8 → 24,1 | 171,7 → 84,6 |
| Demander/acheter | 25,7 → 28,3 | 75,5 → 67,6 |
| Parts/attentes | 134,5 → 98,5 | 230,8 → 142,8 |
| Recharges/allumages/chaleur | 15,0 → 16,3 | 29,8 → 28,0 |
| Portes | 15,9 → 18,5 | 20,5 → 18,8 |
| Poser/fermer/servir | 27,8 → 30,1 | 36,1 → 30,3 |
| Violence/défense | 7,0 → 7,3 | 38,8 → 32,0 |
| Manger/terminaux/engager | 7,3 → 8,2 | 8,6 → 8,5 |

Sous-calculs `cProfile`, cumuls emboîtés **non additifs** : `gestes`
553,7 → 454,3 / 802,3 → 535,9 ; lecture `salle` 52,3 → 35,4 / 62,8 → 33,6 ;
`lieu` 17,5 → 15,2 / 33,2 → 27,1 ; droits préparés 3,3 / 3,6 ;
`Etat.apres` 43,3 → 41,0 / 66,2 → 68,0. Les refus sont déjà mémorisés
(≈ 2 / 4,5 µs) ; le prix `depense` pèse 0 / 0,1 µs.
Compatibilités `recharge` à 600 : **91,4 → 2,0 µs**.

**Nuits 12 h.** Trois versions ensemble, un processus chacune, priorité réduite,
graine 1985. Base/branche strictes et `--calcul` : **quatre nuits identiques**,
état, récit, souvenirs, traces, recherches et nœuds compris.

| Nuit | `42bb9c0` CPU | Base CPU | Branche CPU | Gain | Nœuds identiques |
|---|---:|---:|---:|---:|---:|
| Mine fixe | 405,34 s | 146,66 s | 140,28 s | 4,35 % | 353 096 |
| Auberge fixe | 166,94 s | 452,77 s | 407,61 s | 9,97 % | 1 061 032 |
| Mine tiré | 145,03 s | 200,80 s | 191,72 s | 4,52 % | 476 548 |
| Auberge tiré | 128,56 s | 526,08 s | 482,44 s | 8,30 % | 1 326 957 |

Auberge, CPU entre 8 et 12 h : **371,92 → 328,75 s** fixe,
**457,25 → 422,39 s** tiré. Pics mémoire base → branche : mine
**76,8 → 78,3 / 98,3 → 102,2 Mo**, auberge **199,1 → 197,6 / 206,0 → 205,0 Mo**.

**Validation.** Trois nouveaux tests : 2 138 états développés,
14 661 successeurs ordonnés contre la base (coûts hexadécimaux, suites
différées, découvertes), variations de localisation/droits contre lecture
directe, mine/auberge jouées puis rechargées (monde, lignes joueur, `regarder`,
`scene_percue`, diagnostics). **21 tests ciblés verts.** Empreintes 2 h, quatre
scénarios × quatre graines : **16 nuits identiques**, référence calculée une
fois et rangée en cache. `VERIFIER` + `spatial.VERIFICATION=1`, auberge 42,
2 h : **sans écart ni entrée dans `BORNES`**, **427,77 s CPU**, 1 219 nœuds.
Suite complète unique : **1 916 tests, 16 ignorés, zéro échec/erreur**,
196 fichiers, trois processus à priorité réduite, **1 365,9 s écoulées**.

**Limites.** Une mesure, affinité libre, autres tâches Python : petits gains
sans portée statistique. Profils instrumentés distincts du temps normal.
Auberge encore **×2,44 / ×3,75** contre l'ancien modèle. Affichage CP1252
repris en UTF-8 après le constat d'identité, sans rejouer de nuit.
Créneau de 45 min dépassé. Bruts, conditions et commandes
dans `artifacts/gestes-par-noeud/` du worktree de livraison.
