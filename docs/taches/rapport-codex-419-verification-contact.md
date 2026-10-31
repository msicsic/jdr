# Lot 419 — le contact prépare le moyen et son but

31 octobre 2026, laptop · `codex-verification-contact` · intégration **`07e270be`**
fusionnée par `d500fdcb` (G12, G13, S1m, S1n). Moteur final **`cd19880e`**.
**Lot livré dans son périmètre ; cinq rouges hérités restent ouverts.**
Bruts : `C:/Users/msics/donjon/artifacts/verification-contact-419/`.

**Invariant et code.** La vérification est un préfixe du moyen : constat puis
recompilation, sans perdre le but, l'aide ou l'offre. `planification` conserve
la suite conditionnelle ; propositions et parole d'agenda utilisent ce contrat.
`echanges.executer` sépare provenance et termes entendus. Aucun prompt ni registre
d'esprit ajouté ; familles R/E, `memoire.py` et `deliberation.py` inchangés.

**Tilo/Mathurine corrigé sans exception de scénario.** `detacher_part` et
`matiere.prelever_piece` enregistrent `lot_origine`. La reprise de pulsion utilise
une part issue du lot et portée par l'acteur, tout en conservant le but initial.
Les réceptions typées migrent les anciennes parts ; `remettre` fixe aussi cette
filiation au moment d'une livraison ancienne, avant sauvegarde. Elle persiste
après éviction des souvenirs, sans révéler le lot au joueur ou au MJ.

Preuves : capture réelle 289, laps entier/découpé, rechargement et rendu ; autre
cas, bois reçu pour un feu, avec/sans vérification du contact, part consommée et
feu alimenté après recharge. La capture crue 42 sert désormais Brune avec la
part portée dès 18, puis revoit Ilse à 24 : son oracle exige la consommation
réelle de la part et conserve les contrôles de durée, passages, monde et rendu.

**Tests.** 26 fichiers, **242/247 méthodes vertes** après reprise de trois fichiers
directement concernés (32 méthodes, dont deux rouges héritées). Les deux rouges
nouveaux du calcul initial sont résolus : filiation créée tardivement au
rechargement, puis attente devenue fausse de consommation de la piste d'Ilse.
Cinq rouges antérieurs demeurent : lanterne et ballot de Lucien, démenti
empathique, deux égalités rejetant le suffixe descriptif du 417.
Les douze méthodes et adaptations acceptées du brief sont conservées ; le ballot
reste ouvert (piste consommée à 93, vol attendu à 107–110 sans preuve nouvelle).
Aucune suite complète ni Luna.

**Attribution des 42→47 appels historiques, un par un.** Les cinq sont un solde :
25 ajouts bruts, 20 retraits, comptés par auteur/cible et rang, sans prétendre
apparier causalement des trajectoires divergentes. Les 47 appels ont été rejoués
à l'identique : **38 premiers examens de lieux, six retours avec nouveaux indices,
trois vérifications uniques d'hypothèses expirées ; zéro répétition sans preuve**.
Parmi les 25 ajouts : respectivement 19, cinq et un. Détail individuel et indices :
`reprise/attribution-appels.md` et `.json`, mondes avant chaque appel conservés.

Le dernier cas (Brune → Aubin, graine 7, instant 39804) était un faux positif du
classement : plan de vérification adopté à 66, arrivée à 39723, piste consommée
par la perception pendant l'approche, premier cri à 39804 puis réponse entendue.
Il achève la vérification déjà engagée ; il n'en relance pas une autre.

**Banc rapide crue après fusion : 4 h × quatre graines**, référence `07e270be`
puis branche figée `d64f5fe3`, zéro retour suspect et zéro plantage.

| Graine | Référence | Première livraison | Reprise |
|---|---:|---:|---:|
| 1985 | 5 | 6 | 7 |
| 7 | 10 | 7 | 8 |
| 42 | 18 | 16 | 6 |
| 2024 | 9 | 18 | 18 |
| **Total** | **42** | **47** | **39** |

Critère agrégé de non-hausse atteint. Les mesures historiques auberge (13→13)
et mine (5→4, suspects 1→0) restent dans `banc.json`.
`reprise/conclusion.json` consolide les résultats ; `fin-reprise.json` garde
son échec brut antérieur aux deux corrections et à l'attribution vérifiée.
Le dernier correctif de filiation des pièces anciennes a ses tests ciblés ;
le banc n'a pas été relancé. Sans filiation ni réception typée conservée,
une ancienne part ne peut être reliée au lot par son nom. Aucune garantie
supplémentaire sur les boucles hors des cas et graines mesurés.
