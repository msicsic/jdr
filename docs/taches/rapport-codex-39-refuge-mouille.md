# Lot 39 — refuge mouillé : diagnostic du contrat des trajets

24 octobre 2026. Branche `codex-refuge-mouille`, **non fusionnée**, base `63a717c`.
**Arrêt au diagnostic prescrit par le brief** : la cause implique `planification.py`,
réservé au lot 38. Aucun code du jeu ni fichier réservé modifié ; aucune correction annoncée.

**Cause et chronologie.** Rejeu de la crue 500 sur la base, départ tiré, joueur passif
à `chambre_cloche`, comme `audit_nuits.py`. Aubin choisit la galerie à **156 min + 13,1 s**
(`aller`, coût total pondéré 4,233), Brune le poêle à **160 min** (`chaleur`, 5,291).
Leur route estimée dure **0,789 minute**. `Vue.allers` contrôle `descente` seulement pour
la destination ; `Vue.route` / `trajet_estime.parcours` laissent passer les salles
intermédiaires tant que leur eau n'est pas déjà crue noyée. `pnj._marcher`, renforcé par
`8f60441` pour empêcher un vrai piège, leur applique aussi la descente prévue : il rend
`None`, sans mouvement. À 160, conduite : **84 cm réels/crus, 124 attendus** ; vannes :
64 réels, 104 attendus ; galerie sèche. La prévision utilise **60 minutes**, même pour
ce passage bref. Le plan vise la galerie mais son exécution refuse le détour.

À **182**, conduite réellement à **100 cm** : les recherches rendent désormais `None`
(Brune : quatre nœuds ; Aubin : deux, sans atteindre leur borne). Brune passe de son
plan de chauffage à une enquête puis à l'attente à **182 + 3 s** ; Aubin, après sa ronde
locale, à l'attente de sécurité à **182 + 10 s**. Ilse ne cherche le chauffage qu'à **360**,
après la priorité de la faim ; la porte est en outre crue verrouillée depuis la minute 1.
Aubin ne cherche le chauffage qu'à **404**, après ses autres besoins. Aucun renoncement
au froid ou à la sécurité n'interdit le départ ; le répit de faim de Brune date de 34.
Les réponses « rien » aux enquêtes arrivent après l'échec du trajet, elles ne le causent pas.

**Invariant et correctif proposé.** La recherche et l'exécution doivent employer une seule
admissibilité de route, chaque salle et chaque porte comprises, sur les croyances du PNJ.
Évaluer le risque pendant les séjours et passages prévus, et traiter distinctement le séjour
au but, la possibilité de retour et l'évacuation ; conserver le refus d'un enfermement réel,
y compris quand ouvrir une porte exige une attente ou un crochetage incertain. Propager
la cause jusqu'au récit d'absence de recours. Fonctions à reprendre ensemble : `Vue.descente`,
`Vue.route` / `allers`, `trajet_estime.parcours`, `pnj._marcher`, puis leurs entrées de cache.
Aligner seulement les filtres en rejetant davantage de plans ne garantit pas l'invariant ;
retirer le contrôle de la marche réintroduirait le piège historique. Rien ne justifie de
modifier les personnages, les ressources, `REPIT` ou le prompt de Luna.

**Preuves et mesures.** `tools/diagnostic_refuge_mouille.py` recharge deux captures livrées :
`tests/data/scenes/refuge-mouille-crue500-160.json.gz` (base rejouée jusqu'à 160) et
`refuge-mouille-auteur-100.json.gz` (scène fixe de `test_verifier_eau.EauTests.scene`, Ilse
transie à 90). Sur la seconde : conduite 70 cm réels / 130 attendus, même route de
0,789 min, chauffage trouvé et marche refusée. Pour chacune : absence de mutation à l'échec,
sauvegarde/recharge, puis vingt minutes en bloc et par minutes ; **monde complet et rendu
joueur identiques**, personnage toujours au refuge. Le test historique
`tests.test_signes_calibration.TrajetsRevelesTests` passe pour Brune et Ilse (un test,
deux sous-cas) : la protection contre le détour dangereux doit être conservée.

Le rejeu **12 h de la seule crue 500** conserve toutes les empreintes de la nuit `ffcc295`
archivée et ses mesures de jeu : **865 minutes·PNJ dans l'eau, 495 sans recours, 1 100 en
attente, neuf renoncements, zéro usurpation ou écart**, aucun plantage. Seul le compteur
instrumental de recherches neuves diffère de un (2 205 → 2 204). Bruts, captures intermédiaires,
traces de choix et résultats : `artifacts/codex-39/` du worktree.

**Limites.** Invariant non garanti ; le récit n'explique pas encore le refus du trajet.
Livraison de diagnostic selon le point d'arrêt du brief : ni banc comparatif de comportement,
ni seconde nuit longue, ni suite complète relancés ; aucune modification du moteur à qualifier.
Aucun appel Luna. Les durées ci-dessus sont des coûts du jeu, pas des mesures CPU comparées.
