# Reprise du chantier `besoins` (en cours)

Branche `besoins`, ouverte depuis `main` (dd6ea75). `main` fusionné deux fois : 1e96cb6 (WebSocket
du MJ, voix) puis **789be7a** (prêter, garde confiée, l'argent) : fusion faite (commit 0deeab5),
conflits résolus dans `esprits.py` (champs `voix_entendues` + `urgences`), `planification.py`
(imports `appels_vains`, `gardes`, `PRIX_PART` ; `_entrees` garde `v.gardes` et les entrées de
l'argent), `deliberation.py` (`APPEL_OUBLI` + `REPRISE`/`INERTIE`).

## Les trois volets : faits

1. **Effet de seuil** (`deliberation.urgents`, `eveiller`, `_etat_urgence`, état
   `esprit["urgences"]` = {besoin: {"etat": "presse"|"apaise"|"attente", "depuis": minute}}).
   Apaisé (repassé sous son seuil), un besoin ne presse de nouveau qu'à seuil + `REPRISE` (15),
   sauf s'il est d'abord redescendu sous seuil − `REPRISE` (besoin comblé : seuil ordinaire). Au
   choix du but (`urgents(..., inertie=True)`), un besoin n'interrompt le plan en cours d'un autre
   que s'il presse plus que lui d'`INERTIE` (5) : l'ancienne `INERTIE` en est le cas « le besoin
   servi ne presse plus ». `urgents()` sans inertie garde l'ancien sens pour les autres modules.
   Pas de migration (consigne : anciennes sauvegardes écartées) ; le champ vient par `CHAMPS`.
2. **Ce qu'un plan laisse monter** (`planification.Vue.pression`, `GARDE` = 2, `RESTER` = 30,
   `deliberation.gardes`, `_explorer(tenir)`, `chercher(tenir, endurer)`, `_endure`,
   `planification.garder`, `planification.abri`). Coût par minute : noir (`NOIR` × peur) + `GARDE`
   par lieu gardé dont il est loin (quand `biens` presse). Buts qui se tiennent (lumière, garder,
   abri, chaleur) : + `RESTER` × pression de l'état final ; la recherche continue après le premier
   état qui atteint le but. Lumière et garde « endurent » (`endurer=0`) : pas de départ si le plan
   coûte plus que rester ; l'abri ajoute son gain (noir+lumière si dans le noir, méfiance, compagnie,
   taux du profil × `NOIR` × `RESTER`). `_plan_lumiere` poursuit un plan de lumière restant fait
   d'« aller » si le PNJ porte une source allumée (sinon, une demande refusée se répétait à chaque
   minute : piège rencontré, corrigé).
3. **Attente** (`deliberation._classer`, `attentes`). Un besoin qui presse, dont chaque recours a été
   essayé sans plan (ou sans recours du tout), passe « attente » ; un recours qui aboutit le remet
   « presse ». Recours retentés à chaque minute (mémoire du planificateur). Banc :
   `minutes_urgentes_sans_recours` (plan possible non entrepris : au banc, des renoncements) et
   nouvelle `minutes_urgentes_en_attente` (`banc_pnj._oisifs_urgents` renvoie 3 valeurs) ; récit :
   « Pressé, en attente d'un moyen ».

Correctif commun ajouté (dernier commit avant celui-ci, 8b34c18) : `esprits._percevoir` ne compte
plus la lueur d'une salle voisine (`source` None) dans la croyance « salle éclairée ». Sans lui, au
seuil de la cuisine (auberge) Joss, Tilo, Mathurine croyaient la cuisine éclairée et faisaient
lumière ↔ abri à chaque minute (15,75 alternances par nuit sur la branche avant ce correctif, 0
après ; `main` 0,5).

## Tests

- `tests/test_dynamique_besoins.py` (9 tests) : seuil, besoin comblé, interruption ; Lucien
  (auberge, grenier noir) rapporte la lanterne de l'étable au grenier ; Bram (mine) prend la lampe
  du filon et revient au bureau ; sans lumière à emporter, le plus fort l'emporte (Lucien peur 0,5 :
  retourne au grenier, sécurité en attente ; peur 0,8 : reste au couloir, biens en attente) ;
  devoir de Gorm en attente puis repris ; faim refusée en attente puis redemandée.
- Adaptés : `test_securite.test_rassuree_elle_quitte_l_abri` (abri après 2 min, sur place) ;
  `test_mine.test_le_noir_gagne_le_camp…` (le payeur rejoint peut recevoir de la lumière).
- Suite complète : **951 tests verts** après la fusion de 789be7a (suite4), puis après 8b34c18
  tout vert sauf `test_tui` (4-5 échecs « La TUI n'est pas redevenue disponible ») : ils échouent
  **aussi sur `main` 789be7a** au même moment (machine chargée) ; à relancer seuls au calme.
- `planification.VERIFIER` sur une nuit (graine 42) de chaque scénario : OK après 8b34c18.

## Bancs (8 h ; Relais 8 graines `--joueur chambre_cloche`, mine/auberge/crue 4 graines 1985 7 42 2024)

Derniers chiffres, `main` 789be7a → `besoins` 8b34c18 :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| sans recours | 293,75 → 71,25 | 462,5 → 83,75 | 690 → 126,25 | 445 → 32,5 |
| en attente (nouvelle) | → 225 | → 372,5 | → 583,75 | → 396,25 |
| oisives (total) | 296,25 → 296,25 | 792,5 → 786,25 | 1016,25 → 1026,25 | 445 → 428,75 |
| événements | 31,9 → 32,9 | 43,5 → 42,75 | 47,75 → 49,25 | 32,75 → 34 |
| échanges | 16,1 → 17,9 | 34 → 35 | 31,75 → 35 | 18,25 → 21,75 |
| vols vus | 1 → 1 | 0,75 → 0,75 | 1 → 1 | 0 → 0,5 |
| usurpations | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |

Va-et-vient entre deux besoins (épisodes A, B, A de motifs différents, même but, < 30 min, moyenne
par nuit) : Relais 6,6 → 5,5 ; mine 8,25 → 3,5 (Lucien de la mine, abri ↔ repos, 6 → 0,75) ;
auberge 4,5 → 2,25 (Anselme) ; crue 4 → 0,5. Alternances lumière ↔ abri : auberge 0,5 → 0.
Allers-retours A-B-A de Lucien à l'auberge : déjà bas sur `main` (4/1/2/2 → 4/1/1/3) ; le cas réel
des 39 allers-retours ne se reproduit plus sur `main` (Lucien force le coffre d'Anselme) : il est
rejoué en placement d'auteur (test) : `main` 19 changements de salle en 4 h, `besoins` 5.

Temps de calcul : **à refaire au calme**. Mesures parasitées par la charge de la machine
(dernière passe : Relais 13 → 11 s, mine 29 → 46 s, auberge 35 → 48 s, crue 14 → 15 s ; une passe
plus calme avant 8b34c18 : 9 → 8, 20 → 21, 18 → 25, 9 → 8). L'auberge semble plus lente (recherches
`tenir` qui explorent au-delà du but, garder par la recherche) : à mesurer avec `--diagnostic`.

Sensibilité (avant 8b34c18) : `REPRISE` 10/15/20 quasi identiques (Relais : va-et-vient 12,75 à
10 et 15, 9 à 20) ; `GARDE` 1 → 2 : auberge événements 50 → 54, sans recours 104 → 90 ; 3 ≈ 2.

Scripts de mesure utilisés (dans le bloc-notes de session, non versionnés) : comparer les moyennes
des `--sortie` ; compter les A, B, A dans `recit.episodes` ; compter les A-B-A de salles dans les
`deplacement` de la chronique.

## À faire

1. Relancer `test_tui` seul au calme (et sur `main` pour comparer) ; suite complète.
2. Bancs finaux au calme contre `main` actuel (temps compris) ; `--diagnostic` à l'auberge.
3. Mettre à jour `docs/plan-planificateur.md`, section « Dynamique des besoins » (déjà écrite avec
   des chiffres antérieurs à la fusion de 789be7a et au correctif 8b34c18 : remplacer les chiffres
   par ceux d'ici, ajouter le correctif de la lueur voisine et ses limites) ; ajouter à
   `docs/etat-dev.md` « Branche `besoins`, non fusionnée » et le compte de tests (951).
4. Rapport final : règles (fonctions ci-dessus), cas vérifiés, bancs, limites, dernier commit.

## Limites et pièges connus

- `GARDE` est une constante du moteur ; un méfiant près de ses biens ne pèse pas sur la garde : à la
  mine, Bram revenu avec la lampe part s'abriter quand Odon (méfiant) entre au bureau (gain de
  l'abri : méfiance + compagnie > `GARDE`).
- Seuls noir et garde ont un coût par minute ; froid, compagnie, méfiance n'entrent que dans le gain
  de l'abri ; se chauffer compte le séjour sans endurer.
- La croyance « salle éclairée » reste formée à la case où il se tient (sans la lueur voisine).
- La peur du noir ne s'émousse pas avec le temps.
- Au Relais, Gorm demande les planches d'Aubin plutôt que d'aller chercher son bois à la crypte
  (s'éloigner du refuge coûte `GARDE`) : cohérent, à signaler.
- Ilse (Relais, graine 7) : le froid interrompt encore une fois l'abri (une fois au lieu de cinq).
