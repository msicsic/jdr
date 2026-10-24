# Lot 51 — découvrir le départ feutré

Branche `codex-depart-feutre`, non fusionnée ; base **d60b80a**, ancien moteur **42bb9c0**.
Correctif signé SSH **453a6f3**, signature vérifiée.
Aucun appel au modèle, coût, prix, plafond ou scénario modifié ; `main` non touchée.

**Règle.** `_normaliser_suites` découvre la discrétion sur les gardes communes des gestes
(`sans_temoin`, `dans_le_dos`), après les filtres de tiers et d'effets terminaux utiles.
`_explorer` reprend alors depuis le départ avec les deux allures et la borne entière,
en rejouant aussi la découverte de lumière. `_departs` ne double plus les états sur
la seule permission globale de voler ou de frapper. `_GRAPHES` conserve `discretion`
dès la première recherche par PNJ/but ; les nœuds ne sont gardés qu'à la deuxième.
Changer les seuls prix ne refait pas cette découverte ; changer les entrées la remet
à zéro. Les lectures des gardes sont déjà couvertes par `_entrees` et sa clé complémentaire.
`_sans_plan`/`_parcours` partagent les départs. `VERIFIER` compare au témoin historique
uniforme et à la complète si ce témoin plafonne, conformément au contrat du lot 48.

**Six tests ciblés.** Rémy, capture mine 1985 à 480 min : **4 000 → 2 524 états**,
même absence de plan, même monde et même rendu après cinq minutes par le moteur.
Brune devant la réserve : même plan feutré, crochetage réussi, ouverture et portion
mangée ; allumage illicite au Relais : même plan et flamme allumée ; état complet,
texte et scène perçue identiques après recharge. Marque retenue dès la première
recherche, reprise sans passe de découverte, invalidation lors d'un changement de
permission et redécouverte quand le geste redevient illicite. Certificat contrôlé
avec les mêmes départs. **16 empreintes de 2 h identiques** à `d60b80a`, quatre
scénarios × quatre graines.
`VERIFIER` + `spatial.VERIFICATION=1`, mine/auberge 42, 2 h : aucun écart,
aucune borne ni usurpation. Suite complète finale unique : **1 760 tests,
quatre ignorés, aucun échec**, 170 fichiers, trois processus à priorité réduite,
889,2 s. Les lectures de lumière des filtres de découverte sont aussi contrôlées.

**Mesures 12 h.** Trois versions lancées ensemble, deux processus par version,
priorité réduite, sans cache ; départs tirés et fixes (valeurs par défaut de l'outil).
Les cellules CPU donnent **ancien / base / branche**, en secondes ; tranches à
240, 480 et 720 minutes. Bruts : `artifacts/codex-51/` dans le worktree.
Les nœuds comptent la passe finale ; le CPU inclut les découvertes et reprises.

| Nuit | CPU total | 0–4 h | 4–8 h | 8–12 h | Nœuds base → branche | Bornées |
|---|---|---|---|---|---:|---:|
| Mine 42 tiré | 87,55 / 107,33 / 81,28 | 8,17 / 9,36 / 9,25 | 15,19 / 16,48 / 13,09 | 64,19 / 81,49 / 58,94 | 907 820 → 526 566 | 41 → 0 |
| Mine 1985 tiré | 77,14 / 580,94 / 630,86 | 7,17 / 10,58 / 10,50 | 19,58 / 52,11 / 58,36 | 50,39 / 518,25 / 562,00 | 2 102 158 → 2 128 733 | 343 → 348 |
| Auberge 42 tiré | 77,75 / 331,86 / 322,08 | 6,17 / 9,91 / 10,16 | 11,52 / 55,42 / 55,28 | 60,06 / 266,53 / 256,64 | 881 560 → 825 949 | 4 → 4 |
| Auberge 1985 tiré | 71,66 / 145,39 / 143,80 | 5,77 / 8,91 / 8,91 | 12,19 / 41,72 / 42,30 | 53,71 / 94,76 / 92,60 | 382 202 → 378 578 | 0 → 0 |
| Mine 42 fixe | 88,55 / 277,00 / 238,31 | 8,47 / 14,06 / 13,77 | 16,77 / 70,14 / 67,59 | 63,32 / 192,80 / 156,95 | 1 879 066 → 1 358 537 | 142 → 117 |
| Mine 1985 fixe | 218,02 / 342,95 / 303,38 | 8,44 / 13,48 / 12,89 | 16,70 / 55,97 / 55,41 | 192,88 / 273,50 / 235,08 | 2 466 617 → 2 102 089 | 421 → 195 |
| Auberge 42 fixe | 82,08 / 92,28 / 93,38 | 6,50 / 11,81 / 12,30 | 17,44 / 32,38 / 33,14 | 58,14 / 48,09 / 47,94 | 275 585 → 275 061 | 0 → 0 |
| Auberge 1985 fixe | 88,19 / 352,44 / 357,58 | 8,02 / 12,19 / 12,22 | 10,50 / 20,84 / 22,09 | 69,67 / 319,41 / 323,27 | 1 227 826 → 1 227 583 | 203 → 203 |

**Identité et bilan.** `comparer --calcul` : **huit nuits comparées, zéro différente**,
état complet, chronique, mesures de jeu, récit, souvenirs, empreintes et résultats
de tous les appels logiques compris. Aucune bifurcation, aucun plantage ni usurpation.
CPU total base → branche : **2 230,19 → 2 170,67 s (−2,7 %)** ; mine −4,2 %, auberge −0,6 %.
Nœuds **10 122 834 → 8 823 096 (−12,8 %)** ; recherches bornées **1 154 → 867**.
**Gain modeste, pas uniforme** : mine 1985 tiré **+8,6 %**, dont la tranche 8–12 h
518,25 → 562,00 s ; le prototype local ne se généralise pas à toute la nuit.
Les versions ont partagé la charge de la suite complète pendant une partie des mesures ;
les petits écarts de CPU ne constituent pas une mesure isolée de chaque levier.

**Limites.** La garde découvre un candidat avant la mesure de son approche :
la discrétion peut rester explorée si cette approche échoue ensuite. Une marque
fausse ne vaut pas certificat ; des nœuds encore inexplorés peuvent la faire passer
à vrai. Les bornes de recherche et la complète à 60 000 nœuds restent des limites.
La première découverte demande une reprise ; les entrées qui changent la font
recommencer, tandis que les prix seuls réemploient la marque. Aucun gain universel
ni garantie sur des décisions après une éventuelle bifurcation n'est revendiqué.
Le lot dépasse 45 minutes, mesures longues expressément demandées et reprises avant gel du code.
