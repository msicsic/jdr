# Lot 273 — demande adoptée et moyen démenti

29 octobre 2026. **`codex-demande-adoptee`, non fusionnée**, base `c9459ce`,
moteur `3ec23bb`, banc sur `527b505`.

**Verdict avant fusion : correctif incomplet, défaut commun établi.**
Conserver la demande après échec d'un moyen est nécessaire, mais sa reprise
reste liée au lot source après réception d'une portion concrète. La baisse
de richesse ne peut pas être déclarée légitime. **Fusion à différer ;
correction proposée, non implémentée dans ce diagnostic.**

**Richesse mine**, mêmes signatures `(famille, auteur, texte exact)` du
lot 183 sur les huit nuits archivées ; aucune simulation supplémentaire
pour ce tableau :

| Graine | S référence → branche | Perdues | Gagnées |
|---|---:|---:|---:|
| 1985 | 32 → 12 | 24 | 4 |
| 7 | 19 → 18 | 6 | 5 |
| 42 | 24 → 13 | 18 | 7 |
| 2024 | 28 → 18 | 16 | 6 |

**64 pertes, 22 gains, solde −42** (−10,5 par nuit). Pertes/gains :
demandes **29/7**, offres **17/4**, appels **7/5**, services **8/4**,
interpositions **3/1**, promesses **0/1**. Les 27 couples famille/PNJ perdus
et 13 nouveaux expliquent exactement D −0,5. Les crédits de service
passent de **8 à 4**, sans être un décompte des repas : en mine 42,
Gaspard est nourri dans les deux versions, avec crédit spontané seulement
en référence ; en branche c'est une prestation promise. Une partie du
recul est légitime ; le défaut ci-dessous interdit de l'excuser globalement.
Les familles et auteurs par nuit, toutes les signatures et les limites
causales figurent dans le [diagnostic détaillé](diagnostic-codex-273-richesse-alertes.md).

**Rejeu mine 1985 borné à la première divergence**, sur référence isolée
et branche : mondes avant choix **strictement identiques à `268` (26,8 s)**.
La référence abandonne le secours et achète une part à servir à Josse pour
1 pièce ; la branche conserve le secours à Odon et achète une part à
remettre pour 3 pièces. Les effets diffèrent : ce seul prix ne suffit pas
à conclure à un surcoût injustifié.

**Défaut prouvé à `373` (37,3 s)** : Josse possède `biscuits_1`, reçu avec
provenance `lot=biscuits`. Le planificateur produit `servir biscuits_1 pour
odon`, Odon étant perçu et affamé. Pourtant l'arbitrage le traite comme
une autre demande ; à urgence égale **12 / 20**, il redemande le lot.
Sur copie, ce service réussit et fait passer la faim **85,077→35,077**.
**21 égalités monde/rendu/scène après recharge** sur ces captures et la
contre-épreuve. L'archive garde le but source jusqu'à `18000`, puis ne
sert la portion à Odon qu'à `18627`. Toutes les pertes des quatre nuits
ne sont pas attribuées individuellement à ce défaut.

**Correction proposée.** Séparer identité du but et liaisons de ses moyens ;
revalider la continuation sur les reçus/provenances publiés (`lot→part`,
remise ou transformation), sans renaissance ni perte de palier. Ne pas
assimiler arbitrairement « même raison » à « même demande » ; une mission
peut exiger un objet précis. Aucun cas par objet, PNJ, scénario ou prompt.

**Bilan antérieur conservé.** 21 tests contrat/empathie verts, 28 autres
compléments verts, puis test Lucien vert avec **30 assertions inchangées**
après explicitation de ses prémisses. Capture Aubin `117503`, autre cas
Mathé/Lucien, vraies fins/préemptions et laps découpés vérifiés. Banc 4 h :
**aucune hausse de suspects sur 20/20 paires**, référence `0e3e626`, sonde
265/271, **1→0**, Aubin Relais 2024 `117518` absent. S/F/D mine
**25,75/5/1,964→15,25/5/1,464**. Ce critère numérique tenu ne valide pas
la continuation des moyens. Quarante nuits calculées une fois, **2 515,732 s**,
un processus réduit ; zéro plantage, usurpation ou violation d'audit.

**Alertes.** Crue 7 : nouveau rendez-vous après clôture attestée, puis
retour au brasero après évacuation et moyens changés. Crue 2024 : deux
retours de garde après abri/appels et enquête/entretien. Hameau 2024 :
retour au froid après sommeil de l'agenda. Hameau 42 : les deux abris
étaient déjà en référence ; les ajouts sont l'agenda et l'interposition.
Rejeu ciblé (**34,031 s**, dix captures, **30 égalités de recharge**) :
perception changée et préemption **13→5** pour Gorm ; devis de Brune
`None→offre à Aubin`, cause précise encore ouverte. Ancien/nouveau moteur
produisent les mêmes états sur les trois captures de choix : divergence
de trajectoire, sans nouvelle différence locale du 273 démontrée.

Bruts : `C:/Users/msics/donjon/artifacts/demande-273-sol/`, notamment
`diagnostic-richesse-alertes.json`, `preuve-part-recue.json`,
`alertes-hameau42/`. **Aucun banc relancé, ni Luna ni suite complète ;
aucun calcul actif.** `fin-banc.json` (`ok=true`) reste le résultat du
banc antérieur, pas un certificat de correction générale.
