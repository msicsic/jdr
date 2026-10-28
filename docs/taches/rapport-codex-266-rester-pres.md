# Lot 266 — rester près d'un proche effrayé

Branche `codex-rester-pres`, **non fusionnée**, base `7404d2d`, moteur `c8e4916`,
preuves/rejeu `8e1cb2d`. Commit local ; push précédemment refusé par revue
automatique (GitHub non vérifié). Ni Luna, scénario ni suite complète.

**Contrat.** Peur perçue via `detresses_percues`/`autour`, souci et palier du 197,
terminal `pres`, approche/coûts/mémoire communs, apaisement par `vecu`.
`_fin_demande` constate le démenti avant changement d'intention. Aucun besoin
privé lu. Reprise : moteur et sonde inchangés, aucune correction justifiée.
`echanges.py` intact ; seule validation `peur` autorisée dans `agendas.py`.

**78 tests ciblés distincts verts / huit fichiers**, dont huit de proximité
(15,206 s) : cinq paires réelles et deux états de Gorm, rechargés avec mêmes
choix, monde entier, rendu et scène. Sept charges compressées versionnées.
Laps entier/découpé vérifié ; oracles de garde isolés, assertions conservées.

**Rejeu terminé : vingt nuits de branche 4 h, code 0, 386,007 s**, deux
travailleurs réduits, zéro plantage/usurpation. Vingt références en cache,
aucune rejouée. Vingt hashes d'état final complet, chroniques, avis, boucles
et compteurs identiques au premier banc. **84 secours, 161,077 min** de sécurité
urgente en baisse sous compagnie (temps vécu, pas gain causal). Cycles 219
489 → 462, à expliquer 55 → 66, dérives 233 → 246 ; bascules 3 → 2, sans hausse
par nuit.

**Sonde utilisée : celle de cette branche, issue de `0ff727d`, antérieure aux
lots 265/271**, blob `4e2c68d073fcdf71d4996da93527bf3cdd02267b`, instrumentation
cache `1f6b05da83`. Même sonde pour référence/rejeu ; nouvelle sonde d'intégration
non utilisée. Compteur 219 **brut**, graines **1985 / 7 / 42 / 2024** :

| Scénario | Référence `7404d2d` | Branche `8e1cb2d` |
|---|---:|---:|
| Relais | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Mine | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Auberge | 0 / 0 / 0 / 1 | 0 / 0 / 0 / 0 |
| Crue | 0 / 1 / 0 / 0 | 2 / 1 / 0 / 0 |
| Hameau | 0 / 0 / 0 / 0 | 0 / 2 / 0 / 1 |
| **Total** | **2** | **6** |

**Cinq surplus légitimes au contrat perceptif.** Captures avant interruption
et reprise ; temps en dixièmes absolus, directions du regard :

| Cas | Interruption → reprise | Cause de fin ; autorisation de reprise |
|---|---:|---|
| Brune/Ilse, crue 1985, 82 | 49663 → 49763 | Ilse regarde NE puis SO : `surveille` perdu/revu ; lecture de 79 conservée. |
| Brune/Ilse, même nuit, 83 | 49784 → 49900 | Ilse s'écarte, puis regarde Brune : NE → SO ; signe revu, même lecture. |
| Aubin/Ilse, hameau 7, 39 | 23408 → 23832 | Signe perdu ; rondes après démenti. Tous deux se déplacent ; signe revu, routine préemptée. |
| Maël/Ilse, hameau 7, 61 | 22905 → 36600 | Signe absent à 38 ; déplacement/regard d'Ilse, nouvelle lecture à 60, signe revu à 61. |
| Maël/Gorm, hameau 2024, 203 | 121810 → 121820 | Gorm regarde NO puis SO pendant un pas de Brune : signe revu, lecture de 197 conservée. |

Calme/souci maintenus, démenti **avant** intention vide/routine ; relectures
seules pures et stables. Aucun `pres` valide évincé sans cause, aucun délai
ajouté, aucun compteur reclassé. Suspect faim crue 7 identique à la référence ;
celui d'auberge 2024 disparaît.

**Gorm hameau 7 : effet de trajectoire/classement, pas blocage de `pres`.**
Sans but pressé aux relevés : **195 → 195 min**, confié **75 → 40**, attente
**120 → 155**. Retour à l'antichambre dès 55 ; à 85, brasero non revu depuis
55, séjour humide inaccessible, recherche feu épuisée (24 nœuds), cloche
déléguée au joueur. Enquêtes à 85/115, offres à 132–133, rondes à 106/157/208.
La base attend dès 125 : pas 155 min continues sans agir. Attente globale
400 → 470 min. Rejeu diagnostic : chronique/souvenirs/récit/empreintes conservés.

**Critère de reprise satisfait par preuve des cinq surplus**, sans validation
générale de l'intégration 265/271. Aucun calcul actif ni vérification relancée
à cette clôture. Bruts `C:/Users/msics/donjon/artifacts/rester-266/` :
`reprise-diagnostic/` (captures, preuves, Gorm, tests), `reprise-banc/`
(`fin.json`, `bilan.json`, `validation.json`, comparaison exacte des vingt nuits).
