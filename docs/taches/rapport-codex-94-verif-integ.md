# Vérification d’intégration 47d4d25 — lot 94

26 octobre 2026. Aucun code changé, sans Luna ; deux travailleurs réduits, campagnes
successives. Bruts : `C:/Users/msics/donjon/artifacts/verif-integ-47d4d25/` ;
références relues sans rejeu ni modification.

**Audit : 32 nuits de 12 h**, quatre scénarios × huit graines. Aucun plantage,
violation du monde, usurpation, coup contre une personne ni décès.
**Rixes : huit nuits de 8 h**, `rixe` et `rixe_douce` × 1985/7/42/2024 : mêmes absences.
**VERIFIER + spatial 0,2 : cinq nuits de 8 h**, graine 42 : aucun écart ni plantage.
Une borne ancienne reconnue : auberge, Lucien 314, lumière ; résultat retenu égal au
recalcul complet (73,4743). Auberge : 2 328 s, contre 881 s auparavant, indicatifs.
**Suite complète unique : 1 950 tests, 16 ignorés, aucun échec/erreur**, 203 fichiers,
deux processus, 1 871,95 s (`tests.json`).

Moyennes par nuit ; ordre **42bb9c0 → 5c2ce81 → 47d4d25**. Sans recours/attente/noir/eau
en PNJ·minutes ; passages = pire PNJ/heure de la cohorte.

| Scénario | Sans recours | Attente | Noir | Eau | Passages | Secondes d’horloge |
|---|---|---|---|---|---|---|
| Relais | 206→169→92 | 131→271→454 | 199→204→229 | 0 | 165→10→10 | 45→76→47 |
| Mine | 23→25→21 | 1400→1342→1361 | 1413→1151→1287 | 0 | 17→35→19 | 238→419→179 |
| Auberge | 188→151→146 | 462→376→490 | 1014→864→958 | 0 | 28→42→42 | 206→493→304 |
| Crue | 141→149→146 | 499→513→546 | 64→64→108 | 229→327→396 | 36→49→28 | 56→109→88 |

Temps **indicatifs**, charges différentes, sans conclusion CPU.
`comparaison-par-nuit.csv` juxtapose les 96 nuits et toutes les mesures demandées ;
`comparaison.txt` donne moyennes/maxima. Avis exprimés/adoptés : 0/0 hors crue,
8,4/0,25 en crue ; constats confiés : 7,1/34/50,5/24. Ces mesures sociales
n’étaient pas instrumentées dans les références.

**Les huit défauts de 5c2ce81 :**

| Défaut | Verdict et cas observé |
|---|---|
| Plan/marche sur l’eau | Non observé : crue 2024, Gorm 368–383, plus de refus répété ; crue 1985, Ilse 258–264, passage à 261. |
| Chercher en appelant | Ancienne rafale non observée : mine 7, Odon 470–477. Auberge 7, Odile 641–644 : six appels dans plusieurs lieux, à examiner. |
| Rendez-vous clos d’un seul côté | Non observé sur auberge 42, Anselme/Odile 509–510, une retrouvaille. Réserve : auberge 11, trois retrouvailles 315–318, chacune après un nouvel appel, achat à 318. |
| Propositions redites | Persistant : mine 7, Josse à Lucien deux fois à 244, refus « garde ». |
| Contreparties absurdes | Persistant : mine 1985, Odon à 253, outil contre toute la bourse de la paie. |
| Tâche aussitôt abandonnée | Non observé : crue 7, Ilse 662–664, offres refusées (« cher »), acceptation non exercée. |
| Avertissements redits | Persistant textuellement : crue 2024, Brune à Gorm 146/242/444, torche éteinte ; six redites au total, espacées d’au moins 96 min. |
| Accords grammaticaux | Persistant : mine 7, Odon 0/13, « l’outils » ; auberge 7, Lucien 142, « 1 pièces ». |

**Prochain petit lot :** mine 3, Mathe, dès 9–10 min : déverrouiller/ouvrir/fermer/
verrouiller en boucle, **328/291/291/328** occurrences sur la nuit ; aucune telle rafale
dans les références. Invariant : protection et préconditions du geste doivent rester
compatibles. Relevés : garde à 10–15, service de Lucien à 20–25. Cause à établir ;
aucun correctif ici. Les bascules entre acteurs ne détectent pas cette boucle personnelle.

Limites : aucune garantie générale. Gorm crue 99 (entretien/abri), Brune Relais 11
à 385 et crue 2024 à 400 (attentes) : observations sans preuve d’un plan ignoré.
Détails : `bilan.txt`, `evidence.json`, chroniques et bruts.
