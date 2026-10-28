# Lot 267 — Soupçon déduit

Branche `codex-soupcon-deduit`, **non fusionnée** ; base `7404d2d`, code
`61a1a67`. Bruts : `C:/Users/msics/donjon/artifacts/soupcon-267/`.

**Changement.** `esprits._constater_bien` compare deux constats propres datés
de présence, intégrité, contenu, disponibilité ou flamme. Chaque propriété
garde sa date ; refermer le coffre ne revoit pas son contenu. L'inférence
utilise les présences perçues dans les quarante souvenirs communs, sans
position cachée ni chronique. Zéro ou plusieurs suspects : aucune attribution.
Geste vu/entendu, geste propre et extinction par épuisement sont exclus.
`relations.EPREUVES.soupcon_deduit` réduit seulement la confiance de **6 à
18 points selon PSY**, contre 20 pour une rumeur ; preuve **0,4**, source
`devine`, sans preuve de portage. Conséquences concomitantes regroupées,
méfiance commune possible. `reviser_soupcons` lève l'indice au retour,
à la réparation ou à l'attribution apprise, compensant la seule perte
appliquée. État enregistré avant récit ; aucun nom inconnu appris.

**Tests.** **118 ciblés distincts : 117 verts, un échec préexistant**, onze
fichiers. Onze nouveaux tests : Gorm/réserve et Anselme/coffre, zéro/deux
passants, oubli, geste vu/entendu, retour/remise, auteur appris, PSY/plancher,
dégradation, extinction, épuisement, ressource reconstituée, ignorance.
Monde/rendu/scène identiques après recharge et laps 3 ou 1+1+1 ; relation
et récit contrôlés. Captures `relais.json`, `auberge.json`, résultats
`tests.json`, `tests-soupcon-final.json`. Ni suite complète ni Luna.

**Preuve de dette.** Le seul test
`tests.test_relations_graduees.TempsEtContratsTests.test_dette_soldee_une_fois_par_demande_acceptee`
rejoué sur **7404d2d** puis **61a1a67** échoue identiquement : **1 test,
1 échec, aucune erreur**, `AssertionError: 40 != 20`, ligne 325. Même
fichier (SHA-256 `ddc685f3…`). Traces complètes `dette-base.json/.log` et
`dette-branche.json/.log` ; copie isolée de base retirée.

**Banc terminé, non validé.** **20 paires de 4 h / 40 nuits achevées**,
cinq scénarios × graines 1985/7/42/2024, départ tiré. Sans lot :
`main c870c8b` ; avec lot : `61a1a67`. **Zéro plantage/usurpation** des
deux côtés. Soupçons nés **0 → 0 dans chaque paire**, chronique et récit
concordants : aucun bénéfice naturel démontré. Suspects 219 **2 → 3** :
auberge **2024 : 0 → 1** (Odile, engagement/rejoindre), crue **7 : 0 → 1**
(Aubin, empathie/attente), auberge **7 : 1 → 0** (Mireille, empathie/attente),
crue **2024 : 1 → 1**, autres **0 → 0**. À expliquer **66 → 54**,
dérives **222 → 234**, cycles **499 → 489**.

Richesse S/F/D moyenne, `cats` du lot 183 : famille × auteur × texte,
D incluant les PNJ inactifs.

| Scénario | Sans lot (`main`) | Avec lot |
| --- | --- | --- |
| Relais | 13 / 4 / 1,563 | 13,25 / 4,25 / 1,563 |
| Mine | 25 / 5 / 1,929 | 28,5 / 4,75 / 2,036 |
| Auberge | 8,75 / 3,75 / 0,938 | 11 / 4,25 / 1,063 |
| Crue | 25,75 / 7,25 / 3,25 | 18,75 / 6,25 / 2,75 |
| Hameau | 25 / 7,5 / 2,208 | 21,75 / 7 / 2,083 |

S baisse en crue (**−27,2 %**) et au hameau (**−13 %**).
**`main` diffère de la base : comparaison non causale du seul lot 267.**
Le critère « aucune hausse 219 » échoue sur ce banc ; aucune régression
causale n'est certifiée. Vingt références absentes cachées une fois, aucune
nuit rejouée à la clôture. Deux travailleurs réduits au plus, **489,338 s**,
`fin.json` code 0 ; aucun calcul actif. Fils `comparaison.json`, bilan
par nuit `bilan-final.json` (source S/F/D identifiée), `banc.log`.

**Limites.** Soupçon faillible après oubli ; aucune naissance de
`récupérer` sur ce seul indice ni interpellation autonome nouvelle.
Effraction couverte par dégradation constatée, sans crochetage invisible
ni disparition distante déduite du registre. `agendas.py`, `echanges.py`,
choix de délibération, scénarios et MJ inchangés.
