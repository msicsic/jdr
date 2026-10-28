# Lot 266 — rester près d'un proche effrayé

Branche `codex-rester-pres`, **non fusionnée**, base `7404d2d`, moteur `c8e4916`.
Reprise du 28 octobre 2026. Commit local ; push précédemment refusé par la revue
automatique (destination GitHub non vérifiée). Ni Luna, scénario ni suite complète.
`echanges.py` intact ; seule validation `peur` autorisée dans `agendas.py`.

**Invariant.** Signes/lectures communs du 53 via `detresses_percues`/`autour`,
souci et palier du 197 ; `pres` utilise approche, coût, mémoire et séjour communs.
Le contrat cesse sur peur non perçue, détresse propre, péril ou palier supérieur.
`_fin_demande` enregistre le démenti ; `pnj` revalide et enregistre avant affichage.
Seul `vecu` apaise. Aucun besoin/lieu privé d'autrui lu ; aucune exception ajoutée.

**78 tests ciblés distincts verts / huit fichiers** : état entier, rendu/carte,
scène et laps entier/découpé. Reprise : huit tests de proximité en **15,206 s**,
dont deux nouvelles méthodes sur cinq paires réelles et deux états de Gorm.
Sept charges compressées versionnées. Deux anciens oracles de garde restent
isolés du souci spontané dans leurs seules scènes, assertions conservées.

**Banc initial : 20 paires 4 h, zéro plantage/usurpation**, code 0, 544,924 s,
deux travailleurs réduits ; vingt références absentes calculées/rangées une fois.
84 secours de peur, **161,077 min** de sécurité urgente en baisse sous compagnie
(temps vécu, pas gain causal). Suspects 219 **2 → 6**, cycles **489 → 462**,
à expliquer **55 → 66**, dérives **233 → 246** ; bascules **3 → 2**, sans hausse
par nuit. Les cinq surplus étaient tous sur `pres`.

**Les cinq surplus sont légitimes selon le contrat perceptif.** Captures avant
interruption et avant reprise ; temps en dixièmes absolus, directions du regard :

| Cas | Interruption → reprise | Cause de fin ; autorisation de reprise |
|---|---:|---|
| Brune/Ilse, crue 1985, 82 | 49663 → 49763 | Ilse regarde NE puis SO : `surveille` absent puis revu ; lecture de 79 conservée. |
| Brune/Ilse, même nuit, 83 | 49784 → 49900 | Ilse s'écarte puis regarde Brune : NE → SO ; signe revu, même lecture. |
| Aubin/Ilse, hameau 7, 39 | 23408 → 23832 | Signe perdu ; rondes après démenti. Aubin et Ilse se déplacent ; signe revu, préemption de la routine. |
| Maël/Ilse, hameau 7, 61 | 22905 → 36600 | Signe absent à 38 ; Ilse change de place/regard ; lecture à 60, signe revu à 61. |
| Maël/Gorm, hameau 2024, 203 | 121810 → 121820 | Gorm regarde NO puis SO pendant un pas de Brune : signe revu, lecture de 197 conservée. |

Calme et souci tiennent ; démenti **avant** l'intention vide ou la routine,
aucun palier ne chasse un `pres` valide. Relectures seules pures/stables ; mêmes
choix, monde, rendu et scène après recharge. **Aucune correction moteur justifiée**,
aucun délai ajouté. Le compteur brut reste inchangé : il ne représente pas ces
changements physiques du signe. Le suspect faim crue 7 reste celui de la référence ;
celui d'auberge 2024 disparaît. Aucun défaut d'interruption/reprise établi ici.

**Gorm hameau 7 : effet de trajectoire/classement, pas blocage de `pres`.**
Par relevés, sans but pressé **195 → 195 min** : confié **75 → 40**, attente
**120 → 155**. La branche le ramène à l'antichambre dès 55 ; à 85, brasero non
revu depuis 55, séjour humide inaccessible, recherche feu épuisée (24 nœuds),
cloche déléguée au joueur. Il demande du bois à 85/115, offre des travaux à
132–133, fait ses rondes à 106/157/208. La base attend aussi dès 125. L'alerte
ne prouve pas 155 min continues sans agir ; attente globale **400 → 470 min**.
Le diagnostic conserve exactement chronique, souvenirs, récit et empreintes
de la nuit initiale complète du hameau 7.

**Rejeu détaché en cours : branche seule, mêmes vingt nuits.** Vingt références
`7404d2d` vérifiées en cache ; `--reference-cache-seule` interdit leur calcul.
Aucun code du jeu ni sonde 219 modifiés pendant la reprise. Validation finale
réservée au résultat, suivant le critère « surplus restant prouvé légitime ».
Bruts `C:/Users/msics/donjon/artifacts/rester-266/` : `reprise-diagnostic/`
(captures, `preuves.json`, `gorm.json`, tests), `reprise-banc/fin.json` attendu.
