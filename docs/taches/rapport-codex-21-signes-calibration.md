# Signes : coût, continuité, calibration et refus local

Branche `codex-signes-calibration`, non fusionnée, base `8855312`, moteur final
`677bfd1`. Rythme **42bb9c0** appliqué : campagnes longues arrêtées, référence
réutilisée, branche seule au banc rapide. `planification.py` et `deliberation.py` intacts.

**Contrats.** `relations._lecture` garde relation brute, minute et paramètres
d'estompement ; `signature_signes` ses seuils. `signes.de` dépend des causes
(relations, intention, émotion, conscience), `_percus_gardes` de l'accès individuel
(lumière, distance, positions, orientations, cibles perçues/crues). Caches dérivés,
reconstruits après recharge, contrôlables par `spatial.VERIFICATION`.
`_occurrences` suit l'émission physique : détourner le regard ne recrée pas Lucien
qui tremble. `lire` rafraîchit sans souvenir/annonce et préserve la lecture sur échec ;
changement, arrêt/retour ou péremption créent une lecture (délai 10 min conservé).
`social._adopter` transmet l'épisode. `commandes.analyser` reconnaît la personne connue
invisible ; `refus.perception` donne une cause moteur, `attendu` réservé au MJ.

**Coût acquis avant la nouvelle consigne**, optimisation seule figée `bbf17cb` :
20 nuits de 2 h puis 20 de 8 h, état complet/chronique/mesures identiques à `8855312`.
CPU simultané, 16 nuits par côté, 2 + 2 processus :

| Scénario | 8855312 → cache (s/nuit) | Écart face à 276524c |
|---|---:|---:|
| Relais | 16,52 → 15,98 | +39,1 % |
| Mine | 45,51 → 44,84 | −8,6 % |
| Auberge | 35,75 → 35,77 | −1,8 % |
| Crue | 24,70 → 24,62 | +17,1 % |

Le seuil mine +15 % est numériquement respecté, mais les nuits face à 276524c
diffèrent : seul **−1,5 % face à 8855312** isole le cache. Profil mine 7 : signes
10,4 % cumulés ; clés et accès sensoriel restent payés.

**Calibration provisoire : 4/3/8** (pénombre/dissimulation/bande rien), règle du jet
conservée. Grille conditionnelle 63 réglages, confirmation 48 nuits avant le dernier
correctif : **24,88 %** de méprises, abstention 42,00 %, Gorm/Hugues PSY 14 :
0,806/0,769. Aucun réglage ne remplit les trois bornes conditionnelles ; compromis
minimax commun. Grille réelle arrêtée : validation finale laissée à l'intégration.

**Vérification finale.** 35 tests ciblés verts ; suite unique : **1 591 tests,
15 ignorés, un échec** (754,45 s), `test_mine.py:84`. À 600 min, Bram conscient
garde ses biens (100) malgré sa sécurité à 100, dans le noir près d'Odon : arbitrage
garde/sécurité non résolu, test intact, à reprendre à l'intégration. Banc rapide : 4 h × 4 graines × 4 scénarios,
référence réutilisée depuis `artifacts/references/8855312/`, zéro usurpation/violation,
27 → 0 alertes de répétition ; **174/816 méprises (21,32 %)**, critère encore ouvert.
Mine, graines 1985/7/42/2024 : intentions
8/11/8/2 → 8/9/7/2 ; confidences 15/13/7/2 → 21/18/8/2. Nouveaux lecteurs/guets
et relais de nouvelles en 1985/7 ; Josse informe Bram à 124 min en 42 ; 2024 inchangée
hors lectures. Constats antérieurs conservés ; +1 alternance de buts crue 42 : bruit à
185 min puis garde à 190, pas de boucle au même bruit établie. Luna, **une passe**
finale des trois scripts : 12 appels, zéro pour « observer Ilse » dans le noir,
zéro erreur/refus de contrôle/fuite détectée, impressions incertaines sans réannonce.

**Vols vus**, ablations déjà acquises sur 8855312 : mine 7, pain d'Odon invisible
à 472,53 min avec signes, vu à 475,72 sans effets physiques ; mine 11, tentative à
98 min vue avec signes, invisible sans. Les tentatives persistent : positions et
orientations expliquent les témoins ; retirer seulement les lectures conserve la
visibilité du vol (mais enlève des témoins en 11). Aucune dissuasion démontrée.

**À l'intégration :** refaire calibration et contrôles longs sur le code final ; le
critère 3c reste ouvert, l'histoire des anciens signes n'est pas reconstructible.
Correctif de trajet isolé **8f60441**, à coordonner avec Q : `_marcher` applique
`Vue.descente` aux salles intermédiaires du détour (Brune crue 500 et Ilse), sans
remplacer le travail de Q sur les trajets. Fils et tableaux complets :
`artifacts/signes-calibration/` (provenance et exclusions dans `LIRE.txt`).
