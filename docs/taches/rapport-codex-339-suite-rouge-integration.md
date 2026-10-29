# Lot 339 — incidents préexistants de la suite d’intégration

30 octobre 2026. Branche `codex-suite-rouge`, **non fusionnée**, base
`integration e37d9ee`. Lot terminé, branche poussée, aucun calcul actif.
Bruts :
`C:/Users/msics/donjon/artifacts/suite-rouge-339/`.

**Verdicts sur les parents directs.** Les six premiers incidents sont
un défaut commun du rejeu apparu avec G15 / lot 320 : parent `6037855`
vert (11 tests), fusion `e0be70d` rouge (cinq erreurs, un échec d’audit).
Le code G15 vient de `6f60266`. Pour le septième, la bissection native
établit une attente périmée par le lot 312 : parent `2ddfbe0` vert,
fusion `6be4bac` rouge, code `cf0adfd`.

| Incident | Bascule | Verdict |
|---|---|---|
| Rejeu : lumière dans un autre scénario | `6037855` → `e0be70d` | Défaut de sonde |
| Rejeu : page et filtres | idem | Défaut de sonde |
| Rejeu : témoins des gestes illicites | idem | Défaut de sonde |
| Rejeu : page par graine | idem | Défaut de sonde |
| `RejeuTests.setUpClass` | idem | Défaut de sonde |
| `test_audit_ecrit_une_nuit_mesuree` | idem | Défaut de sonde |
| Auberge : huile après huit heures | `2ddfbe0` → `6be4bac` | Prémisse de stock périmée |

**Correctif commun, `Enregistreur.observer`.** La sonde recopiait la
signature de `ouie.retentir` et rejetait `emission`. Elle lit maintenant
le contrat de l’ouïe pour observer le bruit, puis transmet l’appel entier
sans filtrer ses arguments. L’ouïe conserve l’accès commun au registre
`emissions` ; aucune signature parallèle ni exception de scénario.
Le nouveau test exerce une parole typée du joueur et une dispute PNJ :
paramètres, source, registre, monde complet, scène, écoute et rendu
identiques avec/sans sonde et après vraie sauvegarde/recharge. Les pages
par graine gardent leurs assertions, avec un seul travailleur.

**Huile : preuve et adaptation du test, moteur inchangé.** Le lot 312
permet d’acquérir puis rechercher le destinataire d’une livraison. Dans
la nuit modifiée, Lucien demande l’huile à 469 min, Odile la lui remet
à 470 ; `pot_huile_1` appartient à Lucien, avec sa charge consommée.
Avant l’achat de Corvus, `pot_huile.charges` passe donc de **3 à 2** et
sa masse de **1,5 à 1 kg** ; la réserve d’Odile reste **2**. `garde`
refuse légitimement la vente : bourse **12 → 12**, aucune nouvelle part,
contre **12 → 11**, une part, sur le parent. Les captures des deux parents
et de `9237e14`, rejouées par le moteur courant, conservent état/rendu/scène
après recharge (`analyse.json`). Aucun comportement PNJ discutable
identifié dans ce refus.

Le parcours d’achat/recharge déclare désormais le stock initial de vente,
charges et masse comprises, comme il déclarait déjà la lanterne vide et
l’huile au contact. Il conserve les parts livrées pendant la nuit et cible
la seule part nouvellement achetée. Toutes les assertions historiques de
paiement, livraison, propriété, combustible, charges et lumière restent.
Les autres parcours auberge/mine et les refus sur réserve restent actifs.

**Validation.** Première passe : **68 tests, 67 verts**, le seul échec
étant l’huile encore non adaptée ; zéro erreur ou saut, **1 050,720 s**.
Après adaptation, le fichier huile entier passe (**11/11**). Bilan
consolidé : **68 tests distincts verts / quatre fichiers**, zéro échec,
erreur ou saut, **1 027,263 s** cumulées pour les fichiers verts,
`tests-consolides.json` et **`fin-validation.json ok=true`**. Les trois
autres fichiers et leur code restent inchangés depuis leur passe verte.
Bissection **5 159,478 s**, `fin-bissection.json ok=true`.
Après arrêt du lanceur historique initial, dont les enfants Windows
relançaient les tests, deux travailleurs de calcul au plus, priorité
réduite. Lanceur corrigé et journal conservé ; essais
locaux bloqués par les temporaires du bac également conservés.

**Limites.** Ces preuves portent sur les scènes et nuits mesurées, pas sur
toutes les décisions des PNJ. Les chroniques des captures sont des fenêtres
tronquées : leurs débuts ne localisent pas la première divergence de nuit.
Aucun code de décision, d’émission ou de sauvegarde du moteur ne change :
ni empreintes de nuits, Luna, banc PNJ ni suite complète.
Deux commits séparent le défaut de sonde de la prémisse du test d’huile.
