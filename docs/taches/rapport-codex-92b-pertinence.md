# Lot 92 b — sous-arbres des préparatifs et relances de faim

Branche `codex-aller-utile`, **non fusionnée**, suite de `dd32414`, moteur
**9810f4a inchangé**. **P2 non implémentée : 135 expansions (0,0128 %) établies
sans rapport par la clôture conservatrice, sous le seuil de ~15 %.**

**Mesure.** Auberge 1985 tirée, **[480, 720[ min**, 1 051 797 expansions
(lot 92 initial : minute 720 incluse). Ascendance = préfixe de moindre coût,
préparatifs comptés une fois par préfixe ; sous-arbres susceptibles de se recouper.
Union `prendre`/`ouvrir`/`alimenter` : **781 841 expansions (74,33 %)**.

| Préparatif | Descendants | Part du total |
|---|---:|---:|
| Prendre la burette | 308 538 | 29,33 % |
| Prendre le pot d'huile | 286 474 | 27,24 % |
| Prendre les fagots de l'étable | 233 332 | 22,18 % |
| Ouvrir la besace d'Anselme | 150 298 | 14,29 % |
| Ouvrir le coffret de Lucien | 89 529 | 8,51 % |
| Alimenter la lanterne du couloir avec `burette_huile_1` | 89 373 | 8,50 % |
| Alimenter le fourneau avec les fagots | 88 693 | 8,43 % |

**Clôture.** Feuilles des prédicats faim/chaleur/lumière : vivres disponibles,
parts, foyers, lumière. Remontée aux contenants/porteurs, serrures, clés, outils,
armes acquérables si la violence est admissible, sources/flammes et combustibles.
Portes conservées pour les routes sous pression, lumière pour noir/crochetage ;
buts opaques et franchissements métriques gardent tout : **ce n'est pas
l'inutilité maximale de toute P2**.

La dépendance est aussi **par fait** : une source utile déjà allumée ne gagne
ni flamme ni lumière avec `charge=True`, sans épuisement simulé. Les **135
descendants** viennent de quinze recharges du fourneau allumé, pour Joss/chaleur ;
**aucun** pour Tilo/faim ou Joss/faim. Faute payée en amont : mêmes frais au
prochain geste utile ; durées/pressions non négatives. Aucun filtre exécuté.

**Pourquoi tant d'états de faim ?**

| Sur la tranche | Tilo | Joss |
|---|---:|---:|
| Appels / recherches avec expansions | 376 / 266 | 165 / 133 |
| Issues de ces recherches : plan / épuisée / bornée | 3 / 258 / 5 | 2 / 124 / 7 |
| Appels sans expansion | 110 | 32 |
| Dont impossibilité certifiée / attente bornée | 90 / 12 | 0 / 26 |
| Expansions totales | 246 327 | 358 430 |
| États distincts développés, min / médiane / max par recherche | 15 / 1 205 / 4 000 | 644 / 2 741 / 4 000 |
| États distincts découverts, min / médiane / max | 15 / 1 205 / 4 727 | 922 / 2 741 / 6 381 |
| Recherches reprenant leur graphe | 129 | 89 |
| Relances par les prix seuls / expansions correspondantes | 170 / 180 129 | 103 / 272 783 |

Tilo : descendants d'inspection/recherche **88,30 %**, prise de burette
**32,31 %**, pot d'huile **32,30 %** ; union **51,14 %**. Lumière dans 187/266 recherches.
Joss : fagots **64,26 %**, burette **43,86 %**, lanterne **30,27 %** ; union
**96,86 %**, lumière dans les 133 recherches. Ces moyens peuvent encore servir.

Les entrées communes changent pour 95 recherches de Tilo et 29 de Joss :
géométrie/positions crues (77/15), croyances (62/11), refus, relations et chances
de demande notamment ; lieu cru d'Odile changé 36/6 fois. Comptes non additifs.
Les relances par les prix seuls sont confirmées contre la clé complète du moteur,
FOR/DEX et paramètres complémentaires inclus : **452 912 expansions**.
Le détail par appel figure dans `bilan.json`.

**Certificats.** Tilo : 18 lacunes et 22 preuves abouties ; Joss : 13 lacunes,
aucune preuve aboutie. Rejeu Joss à 622 : 2 071 nœuds, lacune après 666 états
de preuve ; un état du dortoir développé à **profondeur 8**, sans successeurs,
est rejoint à **6** par la preuve. Tilo à 566 : quinze états certifiés, puis
zéro exploration. Trois rejeux/capture, mêmes résultats, monde et vues.
Piste : compléter à profondeur minimale, sans confondre borne et impossibilité.

**P3 plus tard :** choisir le trajet au prix réel, pression comprise, ne suffit
pas à rendre P3 exacte (effets de portes et admissibilité/retour restent à
dominer) ; cela changerait routes, coûts et possiblement décisions, même hors plafond.

**Contrôles/limites.** Témoin 92 réutilisé ; passes objets/faits/signatures
complètes à priorité réduite, un calcul lourd à la fois. Mine optionnelle omise.
Empreintes, résultats d'appels, diagnostics hors durées, 1 175 083 nœuds et rendu
rechargé conservés ; `comparer --calcul`, compilation et `git diff --check` verts.
Arrêt diagnostique : aucune suite complète ou validation d'implémentation.
Aucun Luna, MJ, scénario, `main` ou moteur modifié. Bruts :
`artifacts/aller-utile-92b/` ; outils `mesurer_sous_arbres.py`,
`bilan_sous_arbres.py`, `diagnostiquer_preuve_faim.py`.

Reproduction : mesure vers `auberge-faits.json`, puis même outil avec
`--causes-seules` vers `causes.json` ; `bilan_sous_arbres.py
artifacts/aller-utile-92b artifacts/aller-utile/temoin.json`. Captures nommées dans
les recherches ; rejeu par `diagnostiquer_preuve_faim.py --sortie <json> <captures>`.
