# Vérification d’intégration 590653e — lot 114

26 octobre 2026. Vérification seule, sans Luna, code inchangé sur la branche
`codex-verif-integ-590653e` (base documentaire `cec5e3f`). Deux travailleurs au
plus, priorité réduite, campagnes successives. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/verif-integ-590653e/`.
Audits historiques relus sans rejeu, **127 fichiers inchangés** ; CPU ancien
joué depuis une archive isolée de `42bb9c0`.

**Audit : 32 nuits de 12 h**, quatre scénarios × huit graines : aucun plantage,
violation du monde, usurpation, coup ni décès. **Offres identiques à moins d’une
heure : 13 → 0** contre `47d4d25`. **Rixes : huit nuits de 8 h**, aucune
usurpation, aucun coup ni décès. **VERIFIER + spatial 0,2 : cinq nuits de 8 h**,
graine 42, aucun écart ni plantage. Une borne historique inchangée : auberge,
Lucien à 314, lumière, résultat retenu = optimum complet **73,4743**.
**Suite complète unique : 2 020 tests, 16 ignorés, aucun échec ni erreur**,
217 fichiers, deux processus réduits, **1 738,20 s** (`tests.json`).

**Seuil CPU ≤ ×1,5 manqué.** Auberge 1985, 12 h, sans instrumentation ajoutée,
versions lancées ensemble par paire ; départs successifs :

| Départ | CPU 42bb9c0 | CPU 590653e | Rapport |
|---|---|---|---|
| Fixe | 118,50 s | 195,08 s | **×1,65** |
| Tiré | 93,31 s | 246,73 s | **×2,64** |

Une mesure par paire sur poste partagé, sans preuve statistique ni attribution
du surcoût à un lot. Seul le CPU est comparé ici, pas les temps historiques.

Moyennes par nuit ; ordre **42bb9c0 → 47d4d25 → 590653e**. Durées en
PNJ·minutes ; passages = pire PNJ/heure de la cohorte.

| Scénario | Sans recours | Attente | Noir | Eau | Passages |
|---|---|---|---|---|---|
| Relais | 206→92→92 | 131→454→455 | 199→229→232 | 0 | 165→10→10 |
| Mine | 23→21→29 | 1400→1361→1459 | 1413→1287→1394 | 0 | 17→19→16 |
| Auberge | 188→146→154 | 462→490→482 | 1014→958→982 | 0 | 28→42→38 |
| Crue | 141→146→151 | 499→546→551 | 64→108→111 | 229→396→391 | 36→28→24 |

`comparaison-par-nuit.csv` porte les 96 nuits et toutes les mesures demandées,
dont appels, échanges, propositions/acceptées, avis, constats et avertissements ;
`comparaison.txt` donne moyennes/maxima. Les mesures sociales absentes de
`42bb9c0` ne valent pas zéro.
Les temps d’horloge historiques restent indicatifs, sous charges différentes.

| Défaut de 47d4d25 | Verdict sur cette cohorte |
|---|---|
| Boucle de Mathe, mine 3 | Corrigée sur le cas réel : 3/3/3/3 gestes sur le garde-manger contre 328/291/291/328 ; Lucien servi à 9. |
| Propositions redites, mine 7 | Corrigées sur le cas réel : à 244, après la lampe refusée, Josse offre 2 pièces à Lucien ; aucun doublon identique sur la nuit. |
| Contrepartie, mine 1985 | Corrigée sur le cas réel : à 253, Odon demande 1 pièce prise dans la bourse, pas la bourse entière. |
| Avertissements, crue 2024 | Persistants textuellement : six redites, Brune→Gorm 146/242/444. Le lot 108 a établi les rallumages intermédiaires de la référence ; ne pas les assimiler à six défauts. |
| Accords | Corrigés sur les cas réels : « les outils », Odon mine 7 à 0/13 ; « 1 pièce », Lucien auberge 7 à 142. Aucune des deux anciennes formes fautives dans les 32 nuits. |
| Chercher en appelant, Odile auberge 7 | Non observé à 641–644 ; parcours changé, offre à Lucien acceptée à 625. Pas de preuve générale de correction. |

**Alertes et limites.** Aucun nouveau défaut établi par ces seules chroniques.
Mireille auberge 1985, 561–563 : appels dans quatre lieux distincts puis réponse.
Brune crue 7, 226–231 : tournée reprise après nouvelle lecture de Gorm à 228,
à examiner ; invariant à vérifier : un appel sans réponse ne se répète pas au
même lieu sans nouvel indice pertinent. Auberge 7 : Lucien abandonne deux
tâches à 661, dettes de 2 pièces chacune conservées à 720 ; ce n’est pas un
abandon dans la minute (accord d’Odile à 625). L’alerte Ilse crue 2024,
217–686, fusionne huit niveaux d’eau différents. Les attentes de Brune
(Relais 11 à 385, crue 2024 à 400) et Gorm crue 99 restent des observations
anciennes, sans preuve d’un plan admissible ignoré. Aucune garantie générale
sur toutes les boucles, ni vérification sémantique du MJ dans ce lot.
