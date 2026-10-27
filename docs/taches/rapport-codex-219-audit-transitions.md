# Lot 219 — Audit des transitions de décision

27 octobre 2026 — Branche `codex-audit-transitions`, **non fusionnée**, base
`50de3c2` vérifiée. Outils et tests seulement ; aucun fichier de `donjon/` modifié,
aucun Luna. Au plus deux calculs simultanés, priorité `BelowNormal`.
Bruts : `C:/Users/msics/donjon/artifacts/transitions-219/`.

**Règle commune.** `SondeAvis` observe les candidats réellement essayés, leur
palier, les étapes exécutées et les conditions de fin devenues vraies pendant
l'action d'un tiers. `analyser_episodes` applique une seule règle prioritaire :
cycle accompli, palier strictement supérieur, satisfaction/démenti par autrui,
progression observée du but repris, répétition suspecte, entrée à expliquer.
Une fin intermédiaire seule ne prouve pas un progrès. L'ancienne classe 199 et
les preuves restent dans chaque occurrence. `audit_nuits` expose les compteurs
par classe ; `comparer_bancs` les affiche. Les dérives ouvertes A→B→C sont
séparées des retours et ne sont pas certifiées fautives.

**Les 57 cas de 209**, rejoués sur les sources exactes `78ba505` : **50 répétitions
suspectes, 5 préemptions et 2 à expliquer** (n° 10/28, fin intermédiaire sans
preuve de progrès). Parmi les **21 secours/rondes : 16 suspects,
4 préemptions et 1 à expliquer**, n° 23/27/33 (13→12), n° 24 (12→7). Le n° 38 est une préemption
5→4. Chaque occurrence et sa preuve figurent dans `inventaire-57.md` et
`reclassement-57.json`. Les douze nuits sources retrouvent leurs chroniques,
empreintes et mesures moteur ; les trois anciens compteurs d'audit sont exclus
de cette comparaison, le compteur moteur `avis_exprimes` est conservé.

**Banc courant : vingt nuits de 4 h**, cinq scénarios × graines 1985/7/42/2024,
départ tiré, placements passifs du détecteur. Tableau final dans les bruts.

| Scénario | Cycles | Préempt. | Progrès/autrui | Suspects | À expliquer | Dérives | État payé perdu |
|---|---:|---:|---:|---:|---:|---:|---:|
| Relais | 105 | 6 | 0/0 | 3 | 11 | 23 | 4 |
| Mine | 99 | 8 | 0/0 | 1 | 24 | 44 | 0 |
| Auberge | 137 | 12 | 0/0 | 2 | 9 | 19 | 0 |
| Crue | 65 | 3 | 0/1 | 2 | 15 | 31 | 1 |
| Hameau | 80 | 28 | 0/0 | 5 | 38 | 68 | 2 |
| **Total** | **486** | **57** | **0/1** | **13** | **97** | **185** | **7** |

**20/20 identités finales** : SHA-256 du monde complet, chroniques, empreintes,
mesures moteur ; récit et souvenirs aussi contrôlés lors du calcul des témoins.
Les 185 dérives sont des fenêtres de trois décisions, pas 185 défauts.

**Service payé.** Classe séparée « état payé perdu après réussite, durée non
spécifiée par le contrat », niveau `observation`, jamais violation ni retour
suspect. Le suivi demeure dans la sonde après disparition du souvenir borné.
Le cas exact **217**, `8177959`, joueur à son emplacement initial, retrouve les
**458 événements des dix premières minutes**, allumage à **t=4584** (7 min),
extinction à **t=4824** (8 min). Identité avec/sans sonde ; fixture des deux états,
sauvegarde/recharge, monde, `regarder` et `scene_percue` contrôlés. Un autre
service synthétique porte sur une serrure, avec éviction du souvenir.

**Vérification et limites.** **25 tests ciblés verts**, zéro échec/erreur,
et reprise courte de la règle commune à tous les buts ; aucune suite complète
du jeu nécessaire. Les témoins sans sonde sont
réutilisés pour la dernière vérification après correction du suivi des services,
sans relancer une référence. **Garantie causale générale non établie**
(`certification_complete=False`) : horizon de 60 min, prédicats de fin hérités,
candidats sans palier observable et changements hors des appels sondés restent
des limites. Une étape exécutée n'est pas un certificat de gain durable ; les
services suivent les attributs explicites de leur condition, sans certifier
l'utilité pour le payeur. Les 50 suspects historiques ne deviennent pas
50 défauts établis. Aucun comportement du jeu corrigé. Commits non signés :
aucune clé configurée ; branche seule poussée, sans fusion dans `main`.
