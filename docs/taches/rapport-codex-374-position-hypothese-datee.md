# Lot 374 — position crue comme hypothèse datée

31 octobre 2026, PC fixe. Branche `codex-position-hypothese`, moteur mesuré
**66d3efe8**, intégration **3999bb3a** fusionnée dans `b3233153`. Lot livré,
non fusionné. Bruts : `C:/Users/msics/donjon/artifacts/position-hypothese-374/` ;
bilan consolidé : `contact-consomme/bilan-livraison.json`.

**Invariant commun.** La position d'autrui vieillit à la lecture : confiance initiale
× `2 ** (-âge / demi_vie)` depuis l'observation d'origine, sans cumul par tick.
`data.positions_hypotheses` conserve seuil 0,5 et demi-vies 15/60/120 min selon
mobilité crue (mobile, posée, retenue). Soi, objets et feux exclus ; aucune position
réelle lue pour planifier. `_lieu_cru`, `croit_present`, `_chercher`,
`_normaliser_suites` et `_agir` partagent le contrôle ; règle, expiration et
consommation entrent dans `_entrees` et dans les devis observateurs.

Inspection, appel, question et constat d'absence consomment la piste expirée :
`croyances[sujet].lieu.hypothese_consommee={minute,lieu}` survit à l'absence,
au temps et aux anciens relais. Retrouver la même position clôt aussi le résultat
de sa propre inspection. Le contact requis ne transforme plus cette piste en
recherche des autres salles. Une preuve nouvelle peut rouvrir la piste ; un bruit
attribué conserve date et origine. Le préfixe typé conserve sa progression. Portes et vues mémoire S1a–S1e conservées.

**Attribution demandée, monde/rendu/scène rechargés.**

- Aubin crue 42 : les deux questions sur la voix d'Ilse de minute 3 et la remise
  des préparatifs devant l'inspection causaient les passages ; **24→54→24 en 1 h**.
- Brune crue 1985 : l'inspection de 190 rafraîchissait Aubin vu à 175, puis sa
  propre observation expirait à 205 et réveillait l'agenda. Corrigé ; test 190/205/220/235.
- Lucien mine 1985 : abri→repos à 102→abri à 108, sans quitter le baraquement ;
  repos 90,1→78,1, Mathe revue à 101/107 : retour légitime après satisfaction du besoin.
- Brune crue 2024 : après refus, case d'Ilse inconnue→[0,12], entrée acoustique
  nouvelle qui lève le refus : retour légitime, disparu de l'audit strict final.
- Le seul signal strict final, Lucien auberge 7 à 183 : ancienne question à 142,
  Hugues revu à 168 ; première vérification de cette nouvelle hypothèse expirée,
  sans consommation précédente. Preuve finale rechargée, pas de répétition de la piste de 142.

**Appels, un par un dans le bilan.** Ancienne réserve auberge **46** : 43 contacts
frais ou déjà inconnus, 1 vérification expirée unique, **2 répétitions**. Mine
**38** : 6 contacts hors expiration, 4 vérifications uniques, 4 inspections après
preuve déjà rafraîchie, **24 répétitions**. Inspections/questions répétées comprises :
6 à l'auberge et 63 à la mine. Après correction, les **15+7 appels** sont tous
capturés : **3 vérifications expirées uniques**, **19 contacts frais ou inconnus**,
**zéro répétition expirée**, tous moyens capturés compris. Les douze appels Lucien/Hugues
2024 parcourent des pièces distinctes par observation ; les reprises suivent une
nouvelle vue. Trois signaux de sonde confondaient une preuve déjà rafraîchie en chemin avec
une piste consommée : reclassés par dates, sans modifier l’audit du jeu. **312 captures anciennes et 121 finales** rechargées ;
empreintes des rejeux d'attribution identiques aux bancs correspondants.

**Banc final.** 16 nuits × 4 h, graines 1985/7/42/2024, zéro plantage/usurpation.
Appels base 3999bb3a→branche : **Relais 4→4, auberge 13→15, mine 9→7, crue 35→43**.
Les trois retours initiaux sont corrigés ou attribués ; le seul signal strict
restant est justifié ci-dessus. `VERIFIER` Relais 7 : **1 h vert, 30,378 s**.
16 références et historique b83f5a59 réutilisés ; aucun temps CPU comparé au cache. Les 34 retours « entrée nouvelle à expliquer » restent dans
les bruts : pas de certification globale des autres cycles de besoins.

**Tests et limites.** **119 ciblés, 117 verts, deux échecs de texte hérités** :
`test_contenant_dans_une_autre_salle` et
`test_ilse_capture_141000_pas_de_reprise_par_la_minute`, reproduits sur 3999bb3a
(`reprise/base-3999.stderr.txt`, lot 390), oracles intacts. Les 13 tests position
incluent auberge 371/mine 69, parti/resté, position cachée modifiée sans changer le
plan, sauvegarde/rendu et temps bloc/découpé. Pas de suite complète ni Luna.
Garantie mesurée sur 4 h ; demi-vies initiales non calibrées. Aucun calcul en cours.
