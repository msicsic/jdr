# Lot 239 — recours renoncé et attente d'un moyen

28 octobre 2026, laptop. **Branche `codex-renonce-attente`, non fusionnée**,
base intégration **`3c0e1ca`**, incluant 236. Aucun Luna.

**Invariant.** Le choix et son signalement doivent reconnaître la même absence
de moyen admissible. `_classer` traite désormais un résultat `renonce`, déjà
validé par le juge causal commun du choix, comme `rien` : si tous les recours
évalués du besoin sont ainsi bloqués, le besoin est `attente`. Un `plan` garde
la priorité ; un recours non évalué interdit de conclure à l'attente.
`inactivite`, le récit et le banc consomment déjà ce classement : aucune
recherche ni règle supplémentaire n'y est ajoutée. `choisir`, le juge des
obstacles, les propositions, les biens, `pnj.py`, l'ouïe et le MJ sont inchangés.

**Cas réels.** Les archives 237 étant absentes du laptop, replays séquentiels
du départ tiré de la mine, joueur en galerie. La base est reproduite avec
son `_classer` exact extrait par AST de `3c0e1ca` ; c'est le seul code moteur
modifié par ce lot. Les captures versionnées viennent de cette base : Odon
500 à **107**, faim pressante depuis 71, et Odon 7 à **539:599 dixièmes**,
faim pressante depuis 470. En début de 539, l'aide à Gaspard est encore en
cours sur les deux versions ; l'inactivité commence après son renoncement
dans la même minute. Base : `sans_recours` ; correction : `attente`.
À cet instant, seuls l'état et la date de l'urgence faim diffèrent entre
les données complètes des deux versions.
Les chroniques des replays jusqu'à 110/540 sont identiques. Les mesures du
banc sur ces fenêtres passent respectivement de **5 à 0** PNJ·min sans
recours et de **20 à 25 / 450 à 455** PNJ·min en attente. Ces fenêtres ne
constituent pas une nouvelle mesure de nuit entière.

Les tests font passer ces captures par le choix complet, sauvegarde/recharge,
lecture du récit « en attente d'un moyen », deux minutes d'un bloc ou
découpées, comparaison du monde et du rendu, puis constat de témoins
inconscients et réouverture du recours. Autre besoin/scénario : le devoir
de ronde de Gorm au Relais, passage obstrué par le joueur, classement en
attente, mêmes découpages et reprise après dégagement constaté. Les cas
mixtes `rien`/`renonce`/`plan`/non évalué sont aussi contrôlés.

**Mesures.** Huit paires d'empreintes **2 h**, mine/Relais × 1985/7/42/2024,
chronique, mesures et état complet identiques. Quatre paires mine **4 h**,
mêmes graines : zéro plantage, chronique et état final identiques ;
sans recours **0/0/0/0 → 0/0/0/0**, attente **40/0/0/0 → 40/0/0/0**.
Ces quatre nuits n'exercent pas les épisodes tardifs ciblés. Références
réemployées depuis le cache ; aucune comparaison de temps issus du cache.

**Validation.** **22 ciblés verts**. Suite complète unique, deux travailleurs
réduits : **2 531 tests / 293 fichiers, 3 973,916 s, un échec, zéro erreur,
16 ignorés ; suite non verte**. Seul échec :
`test_torche_hameau_1985_service_perdu`, même trace que le lot 236,
réussite à 3188 puis perte à 3615, réserve du lot 238. Aucune nouvelle
contre-épreuve de cette réserve déjà documentée ; aucun oracle affaibli.
Le dernier fichier, `test_vue_action.py`, passe en **854,313 s** (calcul
spatial pur). Aucun nouvel échec identifié. Bruts dans
`C:/Users/msics/donjon/artifacts/renonce-239/`.

**Limites.** Créneau de 30–45 minutes dépassé par la suite complète finale.
Ce classement est aussi consulté pour ouvrir certaines aides :
l'identité des chroniques observées ne garantit pas une absence universelle
de changement de décision. Le lot ne corrige ni la stabilité de l'aide sous
adoption (lot B du diagnostic 237), ni les autres alertes. Un bref chevauchement
des captures et des deux travailleurs d'empreintes a été arrêté après
identification des processus ; reprise à un travailleur, puis deux calculs
réduits au plus. Les premiers lancements de tests ont échoué sur les accès
aux dossiers temporaires du bac à sable ; reprise hors de ce bac.
