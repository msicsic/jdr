# Lot 222 — Anselme et les coups de la crue : diagnostic

27 octobre 2026, branche `codex-anselme-coups`, `6b9f42b` présent.
Sources **4d4c625 / fa330e1** archivées ; quatre nuits natives de 12 h,
graine 2024, départ tiré, joueur dortoir / chambre de la cloche.
Un calcul à la fois, **BelowNormal vérifiée (16384)**. Aucun jeu, outil versionné
ou test modifié ; aucun Luna ni suite complète. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/anselme-coups-222/` : scripts, captures,
`inventaire.md`, preuves par occurrence, manifeste. Les deux chroniques et
empreintes historiques retrouvent **exactement 212**.

**Reproduction et classement 219.** Fenêtres Anselme 195–720, crue 665–720
(Brune, Gorm et Aubin). Chaque retour exact et ses captures figurent dans
`retours-cibles.json` ; les relevés de cinq minutes sont séparés des décisions.

| Cas / version | Cycles accomplis | Préemptions | Progrès | Suspects | À expliquer |
|---|---:|---:|---:|---:|---:|
| Anselme, 4d4c625 | 13 | 11 | 0 | 0 | 8 |
| Anselme, fa330e1 | 11 | 3 | 0 | 0 | 7 |
| Crue, 4d4c625 | 12 | 1 | 1 | 2 | 22 |
| Crue, fa330e1 | 2 | 1 | 0 | 0 | 3 |

**Anselme : conserver l'entretien et la garde.** L'indicateur échantillonné
retrouve **11 alternances, dont 10 poêle/garde**, puis **2, dont aucune
poêle/garde**, sur l'intégration. « Dès 200 » est le premier but relevé :
le premier triplet de l'alerte est **315 → 335 → 360**. `satisfaite` expire
l'observation du feu après `REVOIR_FEU=30` ; `_pulsion` fait inspecter un feu
anciennement vif, alimenter un feu faible, chercher du bois s'il manque.
`_candidats` interrompt la garde de routine (13) par l'entretien pressant (4),
puis `_plan_garder` rend un plan vide dans **la même chambre**, après réussite.
Exemples : 360–360,167 et 390–390,408. La ronde de chambre, période 43,
explique le retour 650–650,167. Ce n'est pas une navette de lieux.
Les classes prudentes couvrent rondes, rendez-vous et enquêtes : vers 559–561,
`_attendre_qui_vient` transforme l'entretien en rendez-vous avec Joss ; vers
564–565, demandes manquées/refusées et nouvelles enquêtes. Sur fa330e1, reprise
du ballot à 518 après une localisation apprise d'Hugues, puis remise accomplie.
Les candidats essayés figurent dans `trace-choix-*-auberge.json`.

**Coups historiques : décisions locales justifiées, secours qui se contredit.**
À **672,100**, Brune tente d'assommer Aubin au pied-de-biche pour prendre sa
torche, rallumer le poêle du guet et se chauffer (froid **96,124**). C'est une
prise de moyen, pas une défense ; `gestes` compare ce recours à son prix de
violence (**25,954**). À **672,238**, Gorm frappe Brune à mains nues pour
**protéger Aubin**, dont il a entendu l'agression (`protection`, puis `reagir`).
`but.qui=brune` désigne l'adversaire, malgré le libellé « protéger Brune ».
Les **14 coups suivants**, 672,423–691,412, sont des ripostes de Brune contre
Gorm : danger cru présent, conscient, non rendu ; `pnj._executer` revalide
chaque frappe. **16 coups / 7 touchés**, Gorm finit inconscient ; aucune
frappe contre un adversaire déjà neutralisé.

Le nœud causal est chez **Gorm** : son coup fait crier Brune, qui est aussi sa
protégée. Après sa fuite vers la conduite basse (`echoppe`), `dangers=[]`, mais
`protection` retient ce **même secours non examiné**, avant le cas d'Aubin.
`reagir(aide sans ennemi)` renvoie vers Brune ; à l'arrivée, elle redevient son
danger et il refuit. **Cinq retours 672,598–673,228** ; seule l'étape `inspecter`
acquitte le cri (`pnj._executer`), étape jamais atteinte dans ce cycle.
Captures 022 et 026 : **même décision de retour sur les deux versions**.
La crue native fa330e1 donne **zéro coup** : trajectoire différente, pas preuve
de correction de ce mécanisme. La reprise de l'état historique à 665 sur
fa330e1 diverge aussi : **25 coups à 666**, sans reproduire la série de fuites ;
les décisions de retour sont attestées séparément par les captures 022/026.

**Attribution.** Un petit lot distinct : **un secours doit être réévalué et
acquitté sur ce qui a été constaté, avec le danger connu, sans recréer le même
aller-retour depuis le seul cri ancien** (`protection`, `reagir`, inspection).
Le contrat 213 ne suffit pas : la défense précède `_candidats`, et maintenir
l'intention ne rend pas ce secours pertinent. Préemptions légitimes,
sous-buts de rendez-vous et fins réelles doivent rester permis.
Chez Brune, abri/lumière sont choisis hors du lieu cru de Gorm ; ses retours
rouvrent la riposte. **Aucune auto-annulation chaleur/abri démontrée ici**.
Les deux suspects 219 ne certifient pas deux fautes : à 666, localisation
d'Aubin démentie puis revue (`percevoir`, `_approcher`) ; à 691,662, arrivée
dans le noir et gain de sécurité **39,998 contre 29,384**, supérieur à `INERTIE=5`
(R2/R4 du contrat 213). Aucun nouveau lot sur la chaleur justifié par ces seuls cas.

**Preuves et limites.** **221 captures initiales** : monde complet, `regarder` et
`scene_percue` identiques après recharge, sans mutation par la capture.
Quatre reprises **195→205 / 665→700**, en bloc ou tranches de cinq minutes
rechargées : mondes et rendus identiques. Classement partiel
(`certification_complete=False`), aucun correctif ni date d'apparition attribuée,
aucune garantie générale contre les boucles. Aucune clé Git de signature configurée.
