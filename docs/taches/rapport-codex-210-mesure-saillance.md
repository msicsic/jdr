# Lot 210 — Mesure de la saillance

2026-10-27, `codex-mesure-saillance`, base **0aa41b3** présente. Aucun `donjon/`,
Luna ou sauvegarde utilisateur modifié ; un calcul réduit à la fois. Bruts :
`C:/Users/msics/donjon/artifacts/saillance-210/nuits-v1/` ; essais exclus :
`fumee/`, `nuits/`. Reproduction : `tools/mesure_saillance_210.py --campagne
--apparier --dossier <bruts>/nuits-v1`, puis outils `bilan`, `scenes`, `verifier`
et `rejouer_choix_saillance_210.py`.

**Règle.** Filtrer `Vue.agissables` par utilité commune (`pertinent`, préparatifs
lumière compris, `besoin` ou cible) **et** rappel : salle crue initiale,
inventaire, cible, croyance vue/entendue/essayée depuis **30 min**, souvenir
structuré associant moyen et motif/cible, ou clé de cette cible. Aucun rayon
PER ni budget expérimental en nœuds. Utilité conservatrice, sans preuve
causale minimale ; navigation, flammes auxiliaires et devis internes restent
courants : **pas encore une saillance uniforme de tous les moyens**.

**Protocole.** C courant, S opt-in, R `emplois=None`/`REFERENCE`, autres
mécanismes inchangés. Même profondeur/prix ; départ fixe, C puis S.
Trois nuits 12 h (1985), vingt nuits 4 h (1985/7/42/2024). Compteurs de
`mesure_cout`, S/F/D de 183, suspects de 199. Premier choix entier/heure/PNJ
rejoué S/R sur copies et caches séparés ; coûts après `endurer`.

**12 h, C → S** ; N = toutes passes, hors certificats ; B/A = minutes·PNJ
urgentes sans recours/en attente ; retours = suspects du compteur 199.

| Nuit | Recherches | N | S/F/D | B/A | Retours |
|---|---:|---:|---:|---:|---:|
| Mine | 4 457 → 4 500 | 1 047 954 → 60 978 | 96/7/3,71 → 60/6/3,14 | 25/960 → 0/1 295 | 4 → 4 |
| Auberge | 8 205 → 8 669 | 942 317 → 198 274 | 83/6/2,50 → 105/6/3,13 | 55/520 → 55/415 | 7 → 1 |
| Hameau | 6 996 → 10 877 | 804 552 → 113 903 | 70/10/4 → 71/7/4,50 | 5/2 675 → 85/665 | 13 → 32 |

**4 h**, sommes des quatre graines sauf S/F/D (moyennes) ; mêmes colonnes.

| Nuit | Recherches | N | S/F/D | B/A | Retours |
|---|---:|---:|---:|---:|---:|
| Relais | 2 540 → 3 411 | 49 963 → 39 859 | 10/4,25/1,44 → 15,25/5/1,81 | 0/0 → 0/480 | 0 → 0 |
| Mine | 4 631 → 2 804 | 58 071 → 65 356 | 38/5,5/2,43 → 29,25/5,25/2,18 | 0/70 → 0/105 | 17 → 7 |
| Auberge | 3 324 → 3 113 | 95 904 → 56 502 | 13/4/1,38 → 18,25/4/1,44 | 0/0 → 30/240 | 1 → 0 |
| Crue | 6 103 → 5 134 | 191 669 → 51 373 | 20/7,5/2,94 → 15,5/6/1,94 | 0/90 → 60/1 285 | 24 → 7 |
| Hameau | 4 083 → 6 470 | 213 951 → 69 963 | 27/7,5/2,13 → 22,75/4,75/1,83 | 0/460 → 60/775 | 16 → 20 |

Total 4 h : **609 558 → 283 053 nœuds (−54 %)**, recherches
20 681 → 20 932 ; certificats 7 889 → 7 670 ; CPU instrumenté hors ombres
440 → 406 s, indicatif, pas un gain causal démontré. Blocage **0 → 150**,
attente **620 → 2 885**, suspects **58 → 34** : pas d'amélioration générale.

**Myopie.** 853 choix entiers S/R appariés : **six premiers gestes changés** ;
482 recherches communes : **sept plans perdus**, aucun surcoût fini des plans
communs, aucune référence bornée observée ; 31 appels non appariables.
Préfixes 4/12 h recoupés : ni indépendance ni taux global. Dix captures
C/S/R à caches froids : choix C = R dans dix, S différent dans huit.
L'échantillon horaire manque des écarts :
**Odile à 75 min**, propre réserve oubliée, feu **1,137 → 4,782** minutes de
coût modèle (**+3,644**) et premier trajet changé ; Brune au hameau perd son
recours faim dès 0 (`bilan.json`, `rejeux-choix.json.gz`).

**Trouvailles, recharge et limites.** La scène lumière/crochetage perd son
plan de huit étapes en S, profondeur inchangée ; le choix entier d'agenda
reste identique : cela ne prouve pas un repas perdu. Capture réelle Gorm
42/151 : C/R vont au bois propre ; S achète les planches d'Aubin, oubliant
ses fagots. L'ancien choix des planches n'est donc pas reproduit en C ; une
contre-épreuve d'auteur sans bois propre conserve cet achat dans C/S/R.
**46 cycles JSON monde/rendu, neuf scènes disque et neuf laps découpés
identiques**, six tests verts ; deux témoins 6 min identiques sans
sonde/appairés (monde, cinq sorties, hors annotations 199). Zéro plantage,
pas de suite complète. Compteur 199 sans certificat général d'absence de boucles.

**Recommandation : ne pas implémenter cette règle en l'état.**
Nœuds −94/79/86 % sur 12 h, mais attente accrue à la mine et suspects/blocage
accrus au hameau ; le préparatif émergent est perdu.

**Avant implémentation.** Unifier tous les moyens et liens aux sous-buts ;
ajouter à `_entrees` règle/ensemble effectif, dates/sources, souvenirs,
motif/cibles et positions crues. La sonde ajoute déjà règle/ensemble ; C garde
ses clés. Mémoire, graphes, impossibilités et attentes doivent partager cette
clé. `VERIFIER` : optimum/recalcul du même ensemble ; déterminisme
recharge/temps découpé ; myopie contre la complète **mesurée**, sans assertion
d'égalité. « Il n'a pas pensé à… » exige un moyen écarté enregistré.
