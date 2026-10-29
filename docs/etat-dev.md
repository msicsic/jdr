# État du développement

Point de reprise, à tenir à jour à chaque fin de jalon. Mis à jour le 2026-10-29.

- **Branche `ds-demande-adoptee`, non fusionnée**, lot **273**, base `0e3e626`,
  moteur : `deliberation.py` seulement. Un geste manqué dément le moyen, pas la
  demande adoptée : le plan périmé est écarté, l'intention tenue, et la
  revalidation existante retrouve un autre moyen ou met en attente ; la sortie
  `dementie` sur `manque` disparaît. `_meme_demande_tenue` identifie une demande
  par sa raison commune (changer d'objet servi est un nouveau moyen), employée
  par `_meme_demande_adoptee`, `correspondants` et la boucle d'arbitrage — un
  autre moyen n'est pas une préemption. Capture **117503** : la demande d'Aubin
  n'est plus close, passe à `attendre` puis sollicite Gorm ; seconde nature mine
  1985 (pain refusé → `vivres`, même raison) ; vraie fin (`dementie`) et vraie
  préemption (`palier`) toujours des sorties.
  **Reprise : deux causes du recul de la mine.** (1) Une demande sociale sans
  moyen admissible s'endort au lieu d'attendre sans borne : même règle que les
  agendas (sommeil, palier libéré, réveil sur croyance ou moyen nouveaux, jamais
  par délai). Capture **mine 1985 minute 200** (code 20b7601) : Remy tenait
  `pulsion {objet: biscuits, servir: josse}`, plan `[]`, phase `attendre`,
  `_reprendre_demande` `None`, inchangé après 6 choix et 60 min. Après : record
  `demandes_sommeil`, palier 12, une autre intention prend le palier sans
  clôturer la demande ; 6 choix à la même minute ne changent pas l'empreinte ;
  un biscuits en sa possession la réveille avec `depuis` 190, même palier,
  `servir biscuits pour josse`, sans sortie. (2) Une demande conservée
  reconnaît comme sien un moyen reçu dont la provenance publiée la satisfait
  (`lot → part`, promesse, engagement), sans assimiler « même raison » à
  « même demande » quand la mission exige un objet précis. Capture réelle
  **mine 1985 minute 373** de l'analyse indépendante : Josse tient `biscuits`
  et possède `biscuits_1` reçu du lot ; les candidats ne redemandent plus le
  lot, `choisir` sert `biscuits_1` à Odon, palier 12 et `depuis` 0 conservés,
  sans sortie. Sur notre propre rejeu, Josse sert la part dès la minute 10.
  **47 tests ciblés verts** (90 s : demande/sommeil, contrat, empathie, besoins,
  pas-compagnons, étapes) et **106 tests d'agendas/reprise verts** (169 s) ;
  l'oracle des étapes est réécrit pour mine et auberge (visites/plans/monde),
  la scène de Lucien passe par une capture à 95 min, les attentes de
  `vivres_1` et du secours endormi sont explicites. Monde/rendu/scène
  identiques après recharge. **Banc de reprise en cours** : cinq scénarios
  (Relais, mine, auberge, crue, hameau) × 1985/7/42/2024, 4 h, départ tiré,
  référence `0e3e626`, **deux processus**, sortie `banc2-fin.json` ; le banc
  précédent (20 paires, `rixe` au lieu du hameau, quatre processus) donnait
  **20/20 identités**, suspects **1 → 0**, mais une mine à **25,75 → 17,25**.
  Bruts `C:/Users/msics/donjon/artifacts/demande-273-ds/`.
  [Rapport 273](taches/rapport-codex-273-demande-adoptee.md).

- **Branche `codex-retour-aubin`, fusionnée**, lot **272**, diagnostic
  seul, base `aaaf4cf` : Aubin Relais 2024, départ tiré, joueur passif,
  **retour 117518 reproduit** ; sortie 117503 après naissance 117488.
  **Défaut de continuité** : un `manque` ancien du même geste efface
  l’intention avant la reprise de sa demande adoptée, sans fin attestée ni
  palier supérieur. Ilse reste crue affamée ; hors perception à 117503,
  elle redevient perçue à 117518, recréant le candidat de secours. La sonde
  ignore cette entrée perceptive : son « strict complet » est trop fort.
  Refus `necessaire` retenu mais déjà non tenant aux trois relevés,
  aucun renoncement 225 ; aucun réessai par le seul délai démontré.
  Contre-épreuves sur copies : retirer, déplacer ou vieillir seulement le
  marqueur conserve la demande hors perception. **Une nuit 4 h, 15,999 s**,
  un processus réduit, classements identiques à l’archive 271 ; huit contrôles
  de captures et quatre de contre-épreuves, **36 égalités monde/rendu/scène**
  après recharge. Aucun code du jeu modifié, ni Luna, suite complète ou
  banc comparatif. Bruts `C:/Users/msics/donjon/artifacts/retour-272/`,
  `fin.json` (`ok=true`) ; aucun calcul actif. Suite proposée : préserver
  la demande adoptée lors du démenti d’un moyen, revalider les moyens et
  exiger une fin ou une préemption attestée ; aucune correction livrée.
  [Rapport 272](taches/rapport-codex-272-retour-aubin.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement (Sol medium). Défaut réel : à 117503, choisir lit un ancien échec (manque, demande d'une part refusée « necessaire ») et clôt en « dementie » la demande d'Aubin pour nourrir Ilse, alors que sa raison tient (Ilse crue affamée) ; Ilse sortie du champ de vision, rien ne la reprend, puis à 117518 sa perception renouvelée fait renaître le même plan (1,5 s d'interruption). Preuve : retirer seulement manque conserve la demande. Petit lot proposé : le démenti d'un moyen ne clôt pas une demande adoptée dont la raison tient ; moyens revalidés, fin ou préemption attestée. La sonde 219 ne relève pas les entrées perceptives.

- **Branche `codex-reveils-agenda-sonde`, fusionnée**, lot **271**,
  base `de74ff2`, moteur `1355f7a`, outils seulement : reprise justifiée par
  possession/propriété nouvelle, lieu cru changé ou engagement accompli publié,
  reliés aux références du plan admissible repris (offres imbriquées comprises).
  Brune hameau 2024 **591/929** reconnus ; captures 268 sous `881db69`
  **495/1393/59658** reconnus, **738 reste à expliquer**. Mireille auberge 1985
  **36720** reste suspecte. **30 tests ciblés distincts verts**, scènes avec/sans
  sonde et recharges monde/rendu/scène, 18 recharges des captures historiques.
  Aucun moteur modifié, ni Luna ni suite complète. **Vingt paires 4 h terminées :
  20/20 identités, 180 contrôles verts**, zéro plantage, un processus réduit
  détaché, **2 466,737 s**. Sur les mêmes nuits : à expliquer **41 → 15**,
  **26 entrées publiées utilisées**, suspects **1 → 1** (Aubin Relais 2024
  `117518`), cycles **495 → 495**, préemptions **48 → 48**, changements de moyen
  **14 → 14**, progressions **1 → 1**, dérives **212 → 212**, pertes d'état payé
  **4 → 4**, aucune violation de service. Référence 265 : à expliquer **47**,
  suspects **1**, cycles **489**, préemptions **46**, changements de moyen **9**,
  pertes **5** ; écarts intercampagnes non attribués au lot. Aucun retour ajouté
  ou retiré ; aucune référence rejouée, aucun temps comparé entre campagnes.
  Bruts `C:/Users/msics/donjon/artifacts/reveils-271/`, `bilan.json`,
  `fin.json` (`ok=true`). Correctif `3b1ccdc` poussé ; **aucun calcul actif**.
  Horizon 60 min et reçus bornés ; lien structurel, sans preuve de nécessité
  contrefactuelle ni garantie universelle.
  [Rapport 271](taches/rapport-codex-271-reveils-agenda-sonde.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Outils seulement. Classe entree_publiee_utilisee : une reprise du même but est justifiée si une entrée publiée depuis la sortie (bien acquis ou possédé, lieu cru changé, reçu engagement_tenu) est référencée par le plan repris et que ce plan respecte les renoncements. Brune 591/929 (hameau 2024) et trois réveils historiques du 268 reconnus ; 738 reste à expliquer ; suspect Mireille 36720 conservé. 20 nuits 4 h identiques avec et sans sonde : à expliquer 41 → 15, 26 reclassements, suspects 1 → 1 (Aubin, Relais 2024, 117518).

- **Branche `codex-depart-rendez-vous`, fusionnée**, lot **270**,
  diagnostic seul, base `4d2881f` : les **15 départs** comptés par la 241 dans
  la crue (huit graines `audit-12h` et `verifier-8h`) sont **11 cas distincts
  = 4 venues, 1 clôture, 6 ruptures**. Les venues sont des `J'arrive !` suivis
  du départ vers l'appelant ; la clôture est Ilse 42 à 282, dont l'attente est
  déjà rompue à 281 ; les six ruptures ont toutes un **palier strictement
  supérieur** (eau 0, besoin pressant 4, parole due 5), sont annoncées et
  **entendues** par le partenaire. Les quatre lignes `verifier-8h/42` répètent
  `audit-12h/42` (665 lignes et cinq empreintes identiques jusqu'à 480 min,
  seule `issue` diffère). **Aucun défaut du moteur** : la hausse 10 → 15 est
  un artefact du compteur, qui ne suit ni l'état réel de l'attente, ni le
  `J'arrive !` du même PNJ, ni la rupture entendue, et ne déduplique pas les
  nuits rejouées dans deux groupes. Aucun code du jeu modifié, ni Luna, suite
  complète ou banc comparatif. **Quatre captures** monde/empreinte/rendu
  identiques après recharge, dont les départs de 281 sur `c870c8b` (worktree
  détaché, graine 42, cinq empreintes exactes). Bruts
  `C:/Users/msics/donjon/artifacts/rendez-vous-270/` ;
  [rapport 270](taches/rapport-codex-270-depart-rendez-vous.md). Aucun calcul
  actif.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rapport seulement, premier essai de DeepSeek V4.1 Flash Free (OpenCode) : livré complet. Les 15 départs comptés par la 241 sont 11 cas distincts : 4 venues promises (J'arrive ! puis départ vers l'appelant), 1 après clôture, 6 ruptures à palier strictement supérieur (eau, besoin pressant, parole due), toutes annoncées et entendues ; 4 doublons (verifier-8h/42 rejoue audit-12h/42). Aucun défaut du moteur ; la hausse 10 → 15 vient du comptage textuel de la 241, qui ne suit ni l'attente réelle, ni le J'arrive !, ni la rupture entendue, ni les nuits rejouées.

- **Branche `codex-coup-torche`, fusionnée**, lot **269**, diagnostic
  seul, base `integration 47fd0a2` : coup absent de la nuit actuelle,
  reproduit sur `c870c8b` détaché, hameau 1985, départ tiré, joueur passif
  chambre de la cloche, 12 h. Aubin frappe à **391220 (652 min)** et prend
  la torche à 391235 ; Gorm inconscient au relevé 655. Chaleur 100,
  palier besoin pressant ; désespoir corporel autorisant les témoins.
  Coûts refaits **25,415 à 615**, **32,321 à 652** ; recherche pacifique
  épuisée à 185/66 nœuds, refus de combustible encore valides, aucun
  service de rechange/aide attendue. Torche de Maël portée par Gorm :
  prêt/achat à ce tiers exclus par le contrat de transfert existant.
  Verdict conforme aux recours modélisés, sans garantie sur toutes les
  négociations imaginables. Premier écart actuel/historique dès 600,
  offres de Brune différentes à la première minute ; cause non isolée.
  **169 captures monde/rendu/scène identiques après recharge**, deux nuits
  successives à priorité réduite, aucun code du jeu modifié, Luna, suite
  complète ou banc comparatif ; aucun calcul actif.
  Bruts `C:/Users/msics/donjon/artifacts/coup-269/` ;
  [rapport 269](taches/rapport-codex-269-coup-torche.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rapport seulement (Sol medium). Absent de l'intégration actuelle (hameau 1985, 12 h, aucun coup), reproduit sur c870c8b à 652. Aubin, chaleur à 100 (seuil corporel 95 qui autorise l'embuscade malgré les témoins), sans aucun plan pacifique admissible : part de bois refusée (necessaire, impossible), torche de Maël portée par Gorm avec permission, ni prêt au détenteur permis ni achat possibles. Coût brasero 25,4 et poêle 32,3 ; recherche sans assommer épuisée. Manques relevés, non corrigés : demander un prêt au détenteur permis du bien d'un tiers, demander qu'on allume un feu pour soi.

- **Branche `codex-compteurs-faux-positifs`, fusionnée**, lot **265**,
  base `integration c32cc7d`, outils seulement : clôtures publiées des services
  suivies avec leur preuve et l'ancrage 238 ; autre moyen admis seulement si le
  plan évite le geste manqué et respecte les renoncements ; rendez-vous
  intermédiaire clos par `appel.retrouves` relié au partenaire du plan repris.
  Trois faux positifs exacts reconnus sur copies des sources `c870c8b` : Bram
  `367860`, Gorm `409744`, torche `24600` close à `24090`. Identité avec/sans
  sonde et recharges des deux reprises ; **26 tests ciblés verts**, scènes
  fautives toujours signalées. Aucun moteur modifié, Luna ni suite complète.
  **Vingt nuits 4 h terminées : 20/20 identités, 180 contrôles verts**, zéro
  plantage, un processus réduit détaché via WMI, 2 338,585 s. Suspects **2 → 1**,
  à expliquer **55 → 47**, changements de moyen admis **0 → 9** ; cycles
  **489 → 489**, préemptions **46 → 46**, pertes d'état payé **5 → 5** (quatre
  cessations physiques, un bénéficiaire parti). Suspect historique Mireille
  auberge 1985 `36720` toujours signalé. Bruts et `fin.json` (`ok=true`) :
  `C:/Users/msics/donjon/artifacts/compteurs-265/`. Aucun calcul actif.
  Correctif `91377b1` poussé. Suite 268 non couverte : les réveils d'agenda de
  Brune `591`/`929` restent à expliquer ; reconnaître acquisitions, positions
  apprises et engagements accomplis dans un lot suivant. Certification générale
  fausse ; aucune garantie universelle de stabilité du jeu.
  [Rapport 265](taches/rapport-codex-265-compteurs-faux-positifs.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Outils seulement. La sonde garde l'historique des clôtures publiées (service clos avant perte, ancrage 238), reconnaît un changement de moyen qui évite le geste manqué et un rendez-vous intermédiaire clos par appel.retrouves. Cas exacts 263/264 reclassés ; suspect historique Mireille auberge 1985 toujours signalé. 20 nuits 4 h identiques avec et sans sonde : suspects 2 → 1, à expliquer 55 → 47, neuf changements de moyen reconnus (crue). Suite : réveils d'agenda sur moyen acquis, position apprise ou engagement accompli (lot 268) encore à expliquer.

- **Branche `codex-agenda-brune`, fusionnée**, lot **268**, diagnostic
  seul sur `a6ecefd` (moteur `1355f7a`) : hameau 2024, départ tiré, joueur
  passif, 4 h ; alerte huit/neuf absente. **Deux réveils effectifs** actuels
  (crochets acquis, puis pied-de-biche/position de Gorm), trois sommeils ;
  quatre lignes actif car naissance et changement de raison se cumulent.
  Rejeu demandé de `881db69` détachée : **six réveils**, sept sommeils,
  huit lignes actif ; chaque réveil a une empreinte changée et un recours
  admissible. Aucun délai seul observé, aucun suspect 219 certifié ; deux
  retours actuels restent « entrée nouvelle à expliquer ». **20 captures**
  monde/rendu/scène identiques après recharge, deux nuits successives à
  priorité réduite, zéro plantage. Premier commit de disparition non établi ;
  neuf cycles exacts du moteur corrigé 218 non diagnostiqués. Aucun code
  du jeu modifié, ni Luna, suite complète ou banc comparatif ; aucun calcul
  actif. Bruts `C:/Users/msics/donjon/artifacts/agenda-268/` ;
  [rapport 268](taches/rapport-codex-268-agenda-brune.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement (Sol medium). Alerte 205/218 (huit à neuf activations/sommeils de l'agenda a1 de Brune, hameau 2024) non reproduite sur l'intégration : deux réveils seulement, chacun après une entrée nouvelle (crochets pris, Gorm cru en antichambre). Sur 881db69, six réveils, tous sur une croyance ou un moyen nouveaux (positions apprises, travail accompli, bien racheté), jamais par le délai. Le compteur 219 les laisse « à expliquer » : il devrait reconnaître les moyens acquis, les positions apprises et l'engagement accompli (avec le lot 265).

- **Branche `codex-torche-eteinte`, fusionnée**, lot **263**, diagnostic
  seul, base `integration 769c7f1` : épisode absent de la nuit actuelle 12 h ;
  reproduit sur `c870c8b`, hameau 1985, départ tiré, joueur chambre de la
  cloche. Service payé à `686`, allumé à `2436`, ancré en `antichambre`
  à `2536`, clôturé à **`24090`** sur départ vu d’Ilse en crypte pendant que
  Brune et la torche sont encore dans l’échoppe. Brune rejoint ensuite Ilse
  puis éteint à `24600` par `menager_flamme` : **extinction légitime**, faux
  positif de la sonde 227 sans historique des clôtures. Ancrage 238 respecté.
  Captures création/clôture/avant-après extinction et fins 12 h : monde,
  rendu et scène identiques après recharge. Aucun code du jeu changé,
  Luna, suite complète ni banc comparatif.
  Bruts `C:/Users/msics/donjon/artifacts/torche-263/` ;
  [rapport 263](taches/rapport-codex-263-torche-eteinte.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement (Sol medium). Hameau 1985 sur c870c8b, 1 233 entrées de chronique identiques à l'archive 241 ; absent de l'intégration actuelle. Le service d'allumage payé par Ilse était clos à 24090 sur son départ observé (crue en crypte, ancrage 238 appliqué : ni au lieu de réussite ni à celui du résultat) avant que Brune n'éteigne la torche à 24600 pour la ménager : extinction légitime selon le contrat ; faux positif de la sonde 227, qui ignore l'historique des clôtures. Limite du contrat relevée : Brune rejoint ensuite Ilse dans la crypte et la protection close ne renaît pas.

- **Branche `codex-ilse-poele`, fusionnée**, lot **261**, diagnostic seul,
  base `integration 2365125` : Ilse entretient le poêle du guet 450 min dès 165
  malgré la faim (crue, graine 7). Reproduit sur l'intégration actuelle ;
  captures rechargées 160/165/270/275/400/600/720 min (monde/rendu identiques).
  À 270 min+, faim pressante (71→100, seuil 70) mais les deux recours faim
  évaluent à `RIEN` (`planification.planifier` retourne `None`, issue `epuise`,
  1 nœud) : aucun vivre qu'Ilse croit pouvoir prendre (réserve gardée par le
  marchand). Verdict : comportement juste, routine de garde pendant l'attente.
  Aucun code modifié. Bruts `C:/Users/msics/donjon/artifacts/ilse-261/`.
  [Rapport 261](taches/rapport-codex-261-ilse-poele.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement, premier essai d'OpenCode Beam Free : livré complet. Épisode reproduit (165-720) ; la faim est seule urgence mais sans recours admissible d'après les croyances d'Ilse (vivres à la réserve gardée par Gorm), recherche faim épuisée à 1 nœud ; le poêle est une routine exécutée pendant l'attente. Verdict : comportement juste. Réserve du superviseur : un épuisement à 1 nœud ne montre pas pourquoi la demande d'une part à Gorm n'est pas envisagée (refus retenu ou autre) ; non vérifié.

- **Branche `codex-ilse-demande`, fusionnée**, lot **262**, diagnostic seul (Beam Free),
  base `integration 769c7f1` : pourquoi Ilse ne demande pas une part à Gorm (crue 7).
  Sur les captures 270/400/600 rechargées, `planification.gestes` depuis l'état initial
  propose seulement `aller beffroi` (et `chauffer poele_guet` à 600) ; aucun `demander`
  de part de vivres. Exclusion : Gorm (`marchand`) est cru en `antichambre`, salle connue
  et différente de `chambre_cloche`, tandis que l'antichambre est inaccessible (`porte`
  crue verrouillée, sans clé ni crochetage) ; `_parts_calculer` n'offre `demander` que si
  le donneur est co-présent, ni `_chercher` si son lieu est connu. Aucun refus retenu
  (`refus_retenu` `None`), ni méfiance/rancune, ni vivre cru épuisé.
  Verdict : exclusion juste selon ses croyances (passage verrouillé, co-présence requise).
  Aucun code modifié. Bruts `C:/Users/msics/donjon/artifacts/ilse-262/` ;
  [rapport 262](taches/rapport-codex-262-ilse-demande.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rapport seulement (Beam Free). Réserve du superviseur : l'appel à travers la porte (héler, appel négocié « Ici, viens ! ») pour faire venir le donneur n'est pas envisagé par le recours de faim ; piste à instruire.

## Où on en est

- **Branche `codex-faire-ou-confier-b`, fusionnée, prête pour une nouvelle
  suite complète du superviseur**, lot **260**, correctif **`323a0af`**.
  Régression de la suite `d0f9f7a` (2 671 tests, une erreur propre au lot) :
  crue/Brune devenue dépouille rejetée par le devis de mandat. Contrat commun
  corrigé : identité persistante (`noms.PERSONNES`) distincte de disponibilité
  mort/parti crue ; lecteurs communs au cycle, sous-but, choix et devis.
  Tous indisponibles : fin/sommeil ; groupes partiels conservés. Projection
  neutre depuis les croyances : une mort cachée ne change pas à elle seule
  le type/nom/profil du modèle estimé ; cible hors modèle = devis impossible.
  Jugements et filiation restent rechargeables après décès de la cible.
  Aucun masquage d'exception ni cas de scénario. Coûts, paroles et jugement
  réel du mandat conservés ; intégration 259 déjà fusionnée sans rebase.
  **796/796 tests verts / 92 fichiers**, dont **17/17 corps blessable entier**
  inchangé et six nouveaux tests de cycle de vie, monde/rendu/scène rechargés,
  deux PNJ / deux sortes, mort cachée, croyances fausses, groupe et historique.
  **812,656 s**, deux travailleurs réduits au plus. **Huit paires 4 h
  crue/Relais identiques** contre `ab21fb3` : monde final, chronique, mesures,
  empreintes, récit et souvenirs ; huit références intégralement en cache,
  aucune rejouée. Zéro plantage. **Réserves antérieures maintenues** : crue
  7/42 oisiveté 0/0 → 55/195, attente 0/0 → 25/130 PNJ·min ; crue 2024
  250/185 → 215/160 (oisiveté/attente). Aucun recours possible non entrepris
  certifié. Brune crue 42 : 10 lignes actif / 9 sommeil, huit réveils avec
  empreintes différentes, huit captures rechargées ; à 2441, provenance
  seule vu → entendu, nécessité individuelle non démontrée. Cas distinct du
  268 (hameau 2024). Ni boucle sans entrée établie ni non-régression globale
  revendiquée. Ni Luna ni suite complète lancée ici ; aucun calcul actif.
  Bruts `C:/Users/msics/donjon/artifacts/confier-260/destinataires-*` et
  `apres-259/`. Aucun compte rendu ni réaffectation sur retard.
  [Rapport 260](taches/rapport-codex-260-faire-ou-confier.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Le mandant choisit entre faire lui-même et confier d'après le devis de l'acteur vu par lui (agendas.devis_observateur, lot 258) ; identité d'un destinataire persistante (survit au décès), disponibilité crue séparée : un destinataire cru mort ou parti termine l'agenda ou le met en sommeil, n'est pas devisé. Correction après la première suite (Brune dépouille en crue : ValueError). Suite complète sur la branche (c590aad) : 2 677 tests, verte. Réserves conservées pour la prochaine vérification d'intégration : crue 7/42, oisiveté urgente 0/0 → 55/195 et attente 0/0 → 25/130 PNJ·min après 259, sans recours possible non entrepris certifié ; aucun mandat prononcé naturellement dans les nuits.

- **Branche `codex-presences-regression`, fusionnée**, lot **259**, base
  `integration 7e69227`, moteur `15d18c1` : admission d'une part demandée
  avec sa venue convenue ; localisation inconnue distincte d'absence crue,
  présence réelle et parole toujours contrôlées avant consommation.
  Service spontané de Mireille à Mathurine absente toujours refusé ; approche
  et observation ordinaires des cibles disparues restaurées. Aucun nouveau
  champ, scénario, MJ, social/esprits/agendas/relations modifié.
  **310/310 tests ciblés verts**, 18 fichiers du journal + six voisins,
  assertions intactes, monde/rendu rechargés, joueur/Ilse et scènes 251.
  Suite complète du superviseur sur PC fixe, `dc326ad` : **2 655 tests,
  un échec AST préexistant**, les 25 échecs/erreurs de 251 disparus.
  Test isolé reproduit sur **7e69227 et dc326ad**, même
  `agendas.py:1054`, fichier et contrôle AST inchangés par le lot.
  **Banc achevé, code 0 : vingt nuits 4 h par version**, cinq scénarios ×
  quatre graines, `39db079` / `e875877` / branche. Suspects **4/2/3**,
  sans hausse par nuit contre l'avant-251 ; deux alertes anciennes d'Aubin
  reviennent contre 251 (Relais/crue 2024), Odile auberge 2024 disparaît.
  Cycles **498/489/495**, à expliquer **51/55/53**, dérives **216/233/212** ;
  attente urgente **565/400/565**, sans recours **0/0/0 PNJ·min**.
  S/F/D détaillés au rapport : S mine **24,25/28,50/25,75**, auberge
  **9,50/11/9,25** ; aucune amélioration générale revendiquée.
  Zéro plantage/usurpation/violation. Quarante références exactes absentes
  calculées une fois, vingt nuits de branche calculées une fois puis relues
  pour la seconde comparaison ; aucun temps comparé avec le cache.
  **1 513,801 s**, deux travailleurs réduits au plus, aucun calcul actif.
  Ni Luna ni suite complète relancée par l'agent. Limites : venue future non
  garantie, trois suspects non certifiés bénins, pas d'identité universelle.
  Bruts `C:/Users/msics/donjon/artifacts/regression-259/`, `bilan-final.json`,
  `banc.termine.json`, preuves `ast-base.log` et `ast-branche.log`.
  [Rapport 259](taches/rapport-codex-259-presences-regression.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `planification.py`, fusionnés sans conflit textuel. Corrige la régression du lot 251 : la présence nécessaire se juge au moment du geste, une venue convenue compte, une localisation inconnue n'est pas une absence. Suite sur la branche (dc326ad) : 2 655 tests, les 25 échecs hérités de 251 disparus ; seul échec, le contrôle AST de l'ascendant, déjà corrigé sur l'intégration par 57d70d4 (vert ici). 20 paires 4 h : richesse revenue à l'avant-251, suspects 4/2/3 (avant 251 / 251 / 259), attente urgente 565/400/565.

- **Branche `codex-retours-241`, fusionnée**, lot **264**, diagnostic seul,
  base `integration 8ac7b46` : retours Bram mine 2024 à 613 et Gorm hameau 7
  à 682 absents des deux nuits actuelles de 12 h, reproduits sur `c870c8b`
  détaché. **Deux faux positifs 219** : Bram change de moyen après l'absence
  constatée d'Odon (achat de combustible → tâche d'allumage à Mathe) ; Gorm
  reprend après l'arrivée de Sève et la clôture réelle du rendez-vous, que
  `_est_accompli` ne reconnaît pas pour `attendre`. Refus suivants enregistrés,
  aucun renoncement causal effacé ni attente encore valide rompue sur ces
  retours. Quatre nuits achevées sans plantage, **336 captures monde/rendu
  identiques après recharge** ; un calcul réduit à la fois, aucun code du jeu
  modifié, ni Luna, suite complète ou banc comparatif. Aucun calcul actif.
  Bruts `C:/Users/msics/donjon/artifacts/retours-264/`.
  [Rapport 264](taches/rapport-codex-264-retours-241.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement (Sol medium). Reproduits sur c870c8b, absents de l'intégration actuelle. Bram (mine 2024, 613) : achat raté car Odon absent, puis le but lumière revient par un autre moyen (confier la chandelle à Mathe), refusé et retenu : changement de moyen légitime. Gorm (hameau 7, 682) : le recours cède à l'attente de Sève convenue (« J'arrive ! »), rendez-vous réellement clos par appel.retrouves avant la reprise : légitime. Deux faux positifs du compteur 219 : il devrait distinguer les moyens d'un même but et reconnaître la clôture d'un rendez-vous intermédiaire.

- **Branche `codex-devis-observateur`, fusionnée**, lot **258**, base
  `integration e9a8dfe` : `agendas.devis_observateur` et contexte explicite
  observateur/acteur sur modèle fermé ; départ et possessions crus, savoirs
  partagés/transmis explicites, profil neutre, relations/refus de l'observateur,
  autorité estimée sans lire ni inverser la reconnaissance privée du tiers.
  Toutes les données projetées dans les entrées, caches réel/estimé séparés ;
  devis réel 256 intact, aucun appelant autonome. **75 tests ciblés distincts
  verts / onze fichiers**, dont huit nouveaux : deux charges du 257,
  variations privées sans effet sur projection/devis, départ et clé crus avec
  effet, pureté et monde/rendu/scène conservés après recharge. Ni suite
  complète ni Luna. **Empreintes validées : 20/20 paires 2 h identiques**,
  cinq scénarios × quatre graines, référence `e9a8dfe`, branche `9149386` :
  chroniques, mesures, empreintes et hash de l'état final complet identiques.
  Zéro plantage, avis non justifiés **1 → 1** (crue 7), à expliquer
  **41 → 41**. Vingt références absentes calculées et mises en cache une
  fois, aucune rejouée. Calcul détaché terminé en **226,699 s**, deux
  processus réduits au plus, `fin.json` code 0 ; aucun calcul actif.
  Bruts `C:/Users/msics/donjon/artifacts/observateur-258/`.
  Limite : catalogue structurel/carte communs au planificateur, sans nouvelle
  mémoire des transformations cachées ; coût du prochain sous-but seulement.
  [Rapport 258](taches/rapport-codex-258-devis-observateur.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. agendas.devis_observateur et planification.ContexteDevis : départ, possessions et connaissances partagées crus par l'observateur, ses relations et refus ; profil inconnu estimé neutre (caractéristiques 10, valeurs 50) ; relations.autorite_estimee (statut propre cru, ascendant et dette réciproques inconnus à zéro), distincte du jugement réel ; mémoires et graphes séparés par observateur et acteur, lectures dans _entrees. Déplacer Aubin ou changer son savoir privé ne change pas le devis de Gorm ; ses croyances le changent. 20/20 nuits 2 h identiques ; suite complète sur la branche : aucun échec nouveau par rapport à la régression connue du 251, hors un contrôle AST venu du 256.

- **Branche `codex-faire-ou-confier`, fusionnée**, lot **257**, base
  `integration 5e08b76` : arrêt au constat explicitement prévu au brief.
  Le devis réel du titulaire (`agendas.devis_mandat`, 256) ne peut servir
  de classement vu du mandant : deux preuves amener Brune / informer Ilse,
  esprit de Gorm et objets inchangés, retrait d'un savoir privé d'Aubin,
  coût **0,225 / 0,166667 → impossible**. Monde, rendu, scène et devis
  conservés après recharge pour chaque variante ; devis initiaux purs.
  Proposition d'un lot neutre de projection observateur/acteur avant le
  choix autonome. Aucun moteur modifié, suite complète, Luna ou banc lancé ;
  aucun calcul actif. Bruts `C:/Users/msics/donjon/artifacts/confier-257/`.
  [Rapport 257](taches/rapport-codex-257-faire-ou-confier.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement, arrêt prévu par le brief. agendas.devis_mandat (256) planifie comme le titulaire sur une copie qui garde ses connaissances privées : bon pour le jugement réel du mandaté, pas pour le classement du mandant. Preuve rechargée : retirer seulement la croyance privée d'Aubin sur le lieu de Brune fait passer le devis de 0,225 à impossible (et 0,167 à impossible pour l'information à Ilse) sans changer l'esprit de Gorm. Lot neutre préalable proposé : le devis d'un acteur vu par un observateur ne dépend que des données de l'observateur.

- **Branche `codex-jugement-mandat`, fusionnée**, lot **256**, base
  `integration 4318a5b` : jugement explicite de mandat par `echanges.confier`,
  devis social commun sur copie, statut cru dans sa portée et ascendant :
  bonus plafonné à 5 points de DD ; dette du jet inchangée, comptée une fois.
  Accueil prioritaire, aucune obéissance forcée ; raison et bilan enregistrés
  sur le parent avant publication et chronique, filiation par `agendas.confier`,
  confirmation sans nouveau jet. **68 tests verts / neuf fichiers, 32,616 s**,
  deux processus réduits ; Gorm/Aubin/Brune et information à Ilse, refus et
  acceptations rechargés, monde/rendu/scène/paroles, laps entier/découpé.
  Aucun scénario, MJ, social/esprits/planification modifié ; ni Luna ni suite
  complète. **Banc terminé : 20/20 paires 4 h identiques**, cinq scénarios ×
  quatre graines, référence `4318a5b`, branche `a4443eb` : chroniques, mesures
  et empreintes de l'état final complet. Zéro plantage/usurpation/violation ;
  compteur 219 suspects **2 → 2**, sans hausse par nuit (Relais/mine/auberge/
  crue/hameau **0/0/1/1/0**), préemptions **46 → 46**, cycles **489 → 489**,
  à expliquer **55 → 55**, dérives **233 → 233**. Vingt références exactes
  absentes calculées une fois et mises en cache, aucune rejouée. Deux processus
  réduits au plus, **551,850 s**, `fin.json` code 0 ; aucun calcul actif.
  Bruts `C:/Users/msics/donjon/artifacts/mandat-256/`.
  Limite : coût du prochain sous-but social, pas garantie de réussite complète ;
  aucun choix autonome de mandataire ajouté.
  [Rapport 256](taches/rapport-codex-256-jugement-mandat.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. echanges.confier(mandat=...) juge un mandat explicite par le jet commun (_juger_tache : faisabilité, coût, altruisme, liens, volonté, un d20) plus relations.autorite_mandat : statut cru dans son lieu et son domaine 3 points de DD, ascendant 0 à 3, somme plafonnée à 5, dette comptée une seule fois ; refus d'accueil avant tout jet, jamais d'acceptation forcée ; raison (adhésion, dette, autorité, refus et cause) enregistrée avant la chronique ; acceptation par agendas.confier. Demandes ordinaires inchangées ; aucun appelant autonome : 20/20 nuits 4 h identiques, suspects 2 → 2. 68 tests ciblés verts.

- **Vérification d'intégration c870c8b**, lot **241**, branche
  `codex-verif-integ-2` : **49/49 nuits achevées, zéro plantage**,
  cinq contrôles 8 h VERIFIER/spatial 0,2 terminés, dont mine/rixe 42 ;
  zéro écart consigné et aucune mutation candidate détectée. Aucun code
  du jeu changé, Luna, pull, suite complète ni référence rejouée ; un seul
  travailleur détaché à priorité réduite. **Intégration non déclarée verte** :
  Lucien auberge 42, 435–480, **75 → 74 bornes**, mais plans manqués
  **2 → 73** (une seule ancienne borne exacte). Une alerte 227 nouvelle,
  Brune/Ilse hameau 1985 : torche payée allumée à 2436, éteinte à 24600
  (41 min), bénéficiaire cru présent ; violation moteur non certifiée sans
  historique de clôture, sonde non raccordée à l'ancrage 238. Pertes 227 :
  21 physiques et cette alerte, aucune autre cause. Suspects 219 **31 → 23**,
  à expliquer **390 → 376** (47 → 49 nuits achevées). Anselme auberge 7,
  420–479 : **246 → 4 passages** ; onze suspects chaleur/devoir de Gorm
  hameau 1985, 541–545 : **→ zéro**. Sans recours mine **58,12 → 0** ;
  attente hameau **1 761,25 → 931,25**, S **80,25 → 64,50 (−19,6 %)**,
  perte de richesse acceptée après 233, avis adoptés toujours zéro.
  Départs candidats dans la minute d'un « Ici, viens ! » **39 → 24**,
  crue **10 → 15** : aucune garantie générale. Zéro usurpation/mort,
  un coup nouveau Aubin→Gorm à 652 (hameau 1985), suivi d'inconscience ;
  aucune volonté brisée relevée, captivité non certifiée. À instruire :
  recherche bornée, clôture/service payé et sonde, réessai de Bram mine
  2024 à 613 et attente de Gorm hameau 7 à 682 (alertes, pas boucles
  certifiées). Monde/rendu rechargé non couverts par les archives.
  Bruts `C:/Users/msics/donjon/artifacts/verif-integ-c870c8b/` ;
  [rapport 241](taches/rapport-codex-241-verif-integ.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rapport seulement. 49/49 nuits achevées, zéro plantage, usurpation ou mort ; mine 42 et rixe 42 sous VERIFIER et spatial 0,2 terminent (pureté corrigée par 232). Suspects 219 31 → 23, sans recours mine 58 → 0, Anselme auberge 7 246 → 4 passages/h, Gorm hameau 1985 11 suspects → 0, attente hameau 1 761 → 931 PNJ·min ; S hameau −19,6 % (perte acceptée après 233). Non déclarée verte : Lucien auberge 42 à 435, 73 plans manqués sous la borne (corrigé depuis par le lot 244). Un coup réel (Aubin assomme Gorm, hameau 1985 à 652, pour la torche). Petits suivis : service payé de Brune éteint à 41 (hameau 1985), retours de Bram (mine 2024, 613) et de Gorm (hameau 7, 682), Ilse crue 7 au poêle 450 min malgré la faim.

- **Branche `codex-suite-bf99943`, fusionnée**, lot **253**, départ
  `39db079` : frontières reproduites sur parents directs, Lucien **246 /
  f46a0b5**, captures mine/auberge **248 / bf99943**. La restitution
  projetée protège le plan actif et son séjour, même avec un plan vide ;
  garde éclairée de Lucien et visite de galerie de Rémy vérifiées après
  recharge, remplacement puis restitution couverts. Projection des seuls
  champs d'ascendant neutre et des relations JSON : égalité structurelle
  et deux hashes historiques retrouvés, aucun hash attendu remplacé.
  **62 ciblés verts / sept fichiers, 191,559 s** ; nouvelle scène de mine
  rouge sur `bf99943` inchangé. **Banc validé : 20/20 paires 4 h**, cinq
  scénarios × quatre graines contre `bf99943`, branche `74eb299` : états
  complets, empreintes, chroniques, mesures, récits, souvenirs et audits
  identiques. Zéro plantage/usurpation signalée ; suspects **4 → 4**, aucune
  hausse par nuit (Relais/mine/auberge/crue/hameau **1/0/1/2/0**), cycles
  **498 → 498**, dérives **216 → 216**, à expliquer **51 → 51**. Vingt
  références absentes calculées et rangées une fois, aucune rejouée.
  Banc détaché terminé, deux processus réduits au plus ; aucun calcul actif
  pour ce lot. Aucune suite complète ni Luna.
  Bruts `C:/Users/msics/donjon/artifacts/suite-253/` ;
  [rapport 253](taches/rapport-codex-253-suite-bf99943.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `deliberation.py`, fusionnés sans conflit textuel. Lucien (lot 246) : une restitution ne retire plus un moyen encore employé par le plan actif ou le séjour qu'il tient (echanges.necessaire protège les emplois explicites, deliberation.lumiere_utile juge la projection après remise sur les étapes restantes et le séjour) ; oracle de garde intact, autre cas Rémy/lampe de Gaspard. Empreintes mine et auberge (lot 248) : retrait prouvé du seul axe neutre, hashes historiques retrouvés et conservés. 62 tests verts ; 20/20 nuits 4 h identiques, suspects 4 → 4.

- **Branche `codex-statut-source`, fusionnée**, lot **254**, base
  `integration e65fd54`, code `3f4a951` : statut déclaré au profil, croyance
  sourcée réservée aux connaisseurs initiaux, portée explicite lieux/domaines,
  lecture copiée `relations.statuts_reconnus`, aucun lecteur de décision.
  Affirmations et nouvelles par la parole commune ; source connue/inconnue,
  date, poids sans privilège du titre, retrait persistant, déclarations réelles
  intactes ; ni `_utile` ni `bavarder` modifiées. **63 tests / six fichiers :
  62 verts, un échec préexistant** de dette (40 au lieu de 20), reproduit seul
  sur `e65fd54` :
  `tests.test_relations_graduees.TempsEtContratsTests.test_dette_soldee_une_fois_par_demande_acceptee`.
  Six nouveaux tests verts, Relais et mine, monde/rendu rechargés, contrôle AST.
  **Empreintes 20/20 paires 2 h identiques**, chronique, mesures et état final
  complet sans retrait de champs ; Relais, mine, auberge, crue, `crue_hameau`,
  graines 1985/7/42/2024. Zéro plantage, divergence nulle ; vingt références
  exactes manquantes calculées une fois et mises en cache, puis branche.
  Un travailleur réduit, calcul détaché terminé en 731,228 s, `fin.json` code 0.
  Aucun calcul actif ; bruts `C:/Users/msics/donjon/artifacts/statut-254/`.
  Pas de scénario historique, décision, MJ, Luna ou suite complète changé/lancé.
  Limites : aucun démenti omniscient, protocole joueur/MJ et émission autonome
  hors lot ; identité limitée aux vingt paires vérifiées sans statut déclaré.
  [Rapport 254](taches/rapport-codex-254-statut-source.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. profil.statuts (titre, lieux, domaines, connus) reste une donnée d'auteur ; esprits.installer_statuts n'en donne le savoir qu'aux connaisseurs déclarés ; relations.statuts_reconnus lit la seule croyance sourcée, filtrée par lieu et domaine, sans lire le profil réel ; transmission par la parole commune (social.recevoir_statuts, fonction distincte), poids de la source, prétention fausse possible et retrait. Aucun consommateur de décision : 20/20 nuits 2 h identiques. Un test de dette (test_relations_graduees, 40 au lieu de 20) échoue déjà sur la base e65fd54, à examiner.

- **Branche `codex-filiation-mandat`, fusionnée**, lot **252**, base
  `integration 59cb572` : API `agendas.confier`, lectures copiées `filiation`
  et `enfants`, origine `mandat`, liens réciproques, unicité par parent /
  titulaire / condition, deux arêtes au plus, aucun titulaire répété.
  Refus sans effet, relance avec confirmation datée sans ressusciter un
  résultat terminal ; validation à la recharge et contrôle AST renforcés.
  Anciens contrats inchangés ; aucun lecteur de décision ni appel automatique.
  **25 ciblés distincts verts / cinq fichiers**, parole et déplacement réels,
  monde/rendu/scène rechargés. **Empreintes 20/20 paires 2 h identiques** :
  chronique, mesures et état final complet sans retrait de champs ; référence
  figée `59cb572`, branche `28983ff`, cinq scénarios, quatre graines.
  Zéro plantage ; avis inchangés, non justifiés **2 → 2**, à expliquer
  **39 → 39**. Vingt références exactes manquantes calculées une fois et
  rangées dans le cache commun ; un travailleur réduit, calcul terminé,
  `fin.json` code 0. Aucun calcul actif, pas de suite complète ni Luna.
  Bruts `C:/Users/msics/donjon/artifacts/filiation-252/`.
  Limite : identité vérifiée sur ces vingt paires, sans garantie universelle.
  [Rapport 252](taches/rapport-codex-252-filiation-mandat.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. agendas.confier publie un mandat déjà accepté (amener, informer) : origine mandat reliée au parent, références confies réciproques, profondeur dérivée des liens ; troisième arête et cycle refusés avant publication (causes distinctes, attendu), relance idempotente, refus sans écriture, publication interdite pendant une évaluation ; agendas.verifier contrôle les liens à la recharge. Aucun appelant en jeu : 20/20 nuits 2 h identiques, état complet compris. 25 tests ciblés verts.

- **Branche `codex-service-repropose`, fusionnée**, lot **251**, base
  `integration 854bb10` : présences requises d'un geste partagées entre
  mesure du plan et `pnj.refus_etape` (admission/revalidation/exécution).
  Le bénéficiaire d'un service doit être cru présent, sans exiger le contact.
  Auberge 2024 : absent de l'intégration, défaut reproduit sur `942a3c2`
  à 135695 puis reproposition à 135725 ; capture conservée. Aucun délai ni
  nouvelle mémoire d'échec. **28 tests ciblés distincts verts / cinq fichiers**,
  deux contre-épreuves rouges ; capture réelle et mine, monde/rendu rechargés,
  laps en bloc/découpés, reprise sur croyance de retour. Placement du test de
  garde explicité près du repas, assertions conservées. **Banc achevé : 20/20
  paires 4 h**, cinq scénarios × quatre graines, un travailleur réduit,
  référence 854bb10 (remplissage unique du cache absent). Compteur 219 :
  suspects **4 → 2**, préemptions **46 → 46**, « à expliquer » **51 → 55**,
  cycles **498 → 489**, dérives ouvertes **216 → 233** ; zéro plantage,
  usurpation ou violation. **Réserve : hausse locale auberge 2024, 0 → 1**,
  Odile 135912–136430, service → rejoindre Mathurine → service, trajets vers
  le cellier ; nouvelle alerte non certifiée faux positif, à diagnostiquer.
  Le critère sans hausse par nuit n'est pas garanti malgré la baisse globale.
  Aucune suite complète ni Luna. Limites : présence crue, pas garantie de
  l'ouïe ni mémoire universelle d'échecs ou nouvelle recherche de bénéficiaire.
  Bruts `C:/Users/msics/donjon/artifacts/service-251/`, fin `banc.termine.json`.
  [Rapport 251](taches/rapport-codex-251-service-repropose.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Défaut révélé par le diagnostic 249 (Mireille sert Mathurine absente de sa salle, auberge 2024 sur la branche 235) : pnj._a_reunir étend aux participants d'un service le contrôle des cibles touchées, lu par planification._mesurer_direct et pnj.refus_etape (admission, revalidation, agir). Capture rejouée et scène de la mine ; test de garde de la mine réancré près du repas, assertions conservées. 20 paires 4 h : suspects 4 → 2 (Relais, auberge 7, crue 2024 disparus), mais une alerte nouvelle à diagnostiquer : Odile auberge 2024 (135912-136430, service à Mathurine, rejoindre au cellier puis retour) ; à expliquer 51 → 55, dérives 216 → 233.

- **Branche `codex-ascendant-neutre`, fusionnée**, lot **248**, base
  `f46a0b5` (référence remplacée sur instruction du superviseur) : sixième
  axe orienté neutre dans `relations.py`, lecture pure `autorite_reconnue`,
  liens initiaux, bande 60/50, estompement vers le lien déclaré à 1 point/h,
  signatures et validation. Anciennes relations sans champ lues à zéro sans
  migration ; contrats partiels rejetés. Aucun lecteur de décision ni épreuve,
  aucun scénario/MJ changé. **81 tests distincts verts / six fichiers**,
  contrôle AST renforcé ; monde et rendu rechargés, deux couples orientés,
  ancien format et laps découpés. **Banc validé : 20/20 paires 2 h**,
  cinq scénarios, quatre graines : mêmes textes de chronique, mesures,
  récits, souvenirs, empreintes physiques ; zéro plantage. États complets
  identiques après retrait de l'axe neutre et recalcul sourcé des hashes
  dérivés. Le diagnostic intermédiaire restait à 12/20 ; **rejeu unique de
  huit références expressément autorisé**, captures à part, cache inchangé,
  hashes de référence reproduits 8/8. Quinze champs restants localisés :
  douze signatures de recours négatifs dans `attentes_bornees`
  (`pnj_propositions._entrees_negatives`), deux JSON de relations dans les
  causes de refus (`deliberation.moyens_crus`) et un hash d'agenda qui les
  inclut. Projections et formats conservés ; états/données bruts de branche
  identiques aux passes initiales ; **aucun écart réel de comportement**.
  Aucun moteur modifié pendant la reprise. Limite : pas identité binaire
  des sauvegardes, ni garantie universelle hors des vingt nuits vérifiées.
  Aucune suite complète ni Luna ; deux processus réduits au plus,
  aucun calcul actif. Bruts `C:/Users/msics/donjon/artifacts/ascendant-248/`,
  bilan consolidé `validation-finale.json`, chemins `diagnostic-champs.json`.
  [Rapport 248](taches/rapport-codex-248-ascendant-neutre.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Sixième axe des relations (ce que B reconnaît d'autorité à A), lu et écrit par relations.py seul (autorite_reconnue), neutre à zéro, liens de départ possibles, bande 60/50 et estompement vers le lien initial ; anciennes sauvegardes chargées neutres sans migration ; aucun lecteur de décision. 20/20 nuits 2 h : jeu identique ; état complet identique après retrait du champ neutre et recalcul des empreintes qui en dérivent (attentes bornées, causes de refus sérialisées, croyances d'agenda), rejeu unique des huit références autorisé pour le prouver. 81 tests ciblés verts.

- **Branche `codex-confidences-perdues`, fusionnée**, lot **249**, base
  `integration 59321b9` : diagnostic documentaire de `adb52c4` contre 235
  (`942a3c2`), aucun code du jeu ni test modifié. Inventaire exhaustif des
  126 paroles Relais/mine, quatre graines × 4 h : 122 occurrences absentes,
  quatre retrouvées à un autre instant, onze ajouts/réattributions ; compteur
  25/101 → 5/10, comprenant aussi les comptes rendus de promesse.
  Huit captures identiques aux bruts (chroniques/empreintes/récits/souvenirs),
  123 transmissions sans effet sur le choix immédiat ; huit rejeux de choix
  et cinq prolongations pour couvrir l'heure après les annonces tardives :
  **5 472 ablations locales, six écarts issus d'une confidence utile perdue**,
  Josse → Mathe, biscuits épuisés à 141, évitement d'un secours impossible
  à 191–193, mine 1985. `_utile` ignore l'usage connu d'un moyen pour aider
  autrui hors engagement actif ; recommandation d'élargir par une preuve
  d'usage perçue, typée et révisable, sans lecture privée. Schéma non conçu.
  Huit assertions rouges reclassées sur captures, aucun oracle modifié ni
  test déclaré vert. Deux nuits 235 sondées, identiques aux bruts : Aubin/Ilse est un
  faux positif (enquête de localisation, autre moyen) ; Mireille/Mathurine,
  un défaut réel d'admission du service envers une personne crue ailleurs.
  Effets des témoins auditifs et nuit entière
  sans parole non mesurés ; aucune autorisation de fusion de 235. Un processus
  réduit, aucun Luna, suite complète ou banc de comparaison. Bruts
  `C:/Users/msics/donjon/artifacts/confidences-249/`.
  [Rapport 249](taches/rapport-codex-249-confidences-perdues.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rapport seulement. Mine et Relais : 122 confidences absentes sous 235, presque toutes sans usage décisionnel (sources éteintes, contenants fermés, biens disparus) ; une seule utile perdue démontrée (Josse → Mathe, biscuits épuisés, mine 1985 à 141 : évitement à 191-193). Manque : l'usage d'un moyen pour aider un tiers hors engagement actif, à retenir comme preuve d'usage par le contrat commun perception/parole. Huit assertions rouges du 235 classées en attentes périmées ; suspect Aubin/Ilse faux positif ; Mireille/Mathurine (auberge 2024, 226) défaut réel d'admission du service. Premier diagnostic Sol medium sur nuits rejouées.

- **Branche `codex-suite-bf4cede`, fusionnée**, lot **247**, base
  `f46a0b5` : quatre oracles corrigés, aucun code moteur ni MJ modifié.
  Bissection `4306c14`–`bf4cede`, frontières confirmées vert/rouge sur
  parents directs : deux ancrages de service introduits par **234 / bf4cede**
  (Ilse crue à l'antichambre au constat), exploration d'auberge par
  **244 / b744265** (20 632 → 8 573 visites, mêmes plans/monde/lignes/vues),
  prémisse de crue par **242 / d606305** (Gorm ne transmet plus sa vitesse
  à Ilse ; échéance de `confier` isolée par contre-épreuves).
  Connaissance de montée désormais explicite dans la scène d'auteur,
  assertions de sécurité conservées, exécution et deux vues rechargées
  vérifiées. **39/39 tests verts sur quatre fichiers, 118,060 s** ; fichier
  d'eau final renforcé **7/7, 67,695 s**. Pas de suite complète, banc ni Luna.
  Bruts `C:/Users/msics/donjon/artifacts/suite-247/` ;
  [rapport 247](taches/rapport-codex-247-suite-bf4cede.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Tests seulement, moteur inchangé. Bissection : deux oracles de lieu du bénéficiaire périmés par le placement du lot 234 (Ilse reste crue à l'antichambre), empreinte de visites de l'auberge périmée par le lot 244 (20 632 → 8 573 visites, mêmes plans et monde), scène d'eau dont la prémisse venait d'une mesure transmise par Gorm que l'échéance du lot 242 supprime (connaissance déclarée explicitement, contrôles d'exécution et de recharge ajoutés). 39 tests verts.

- **Branche `codex-restitution-route`, fusionnée**, lot **246**, base
  `2b15134` : transport avec le bien jusqu'à la destination crue, puis
  nécessité dans l'état de remise ; même admission et revalidation via
  `_rendre`, recherche commune d'`aller` et `echanges.necessaire(apres=...)`.
  Cession compensée 228 conservée, aucun cas de scénario. Capture historique
  `4306c14`, hameau 42 à 421, reproduite ; contre-épreuve rouge sur la base
  pour Maël et pour une lampe de la mine. Restitution, refus sans autre
  lumière, remplacement, monde/rendu/scène rechargés et laps découpés couverts.
  **47 ciblés distincts verts / cinq fichiers, passe 452,688 s** ; trois premiers
  fichiers repris sur le raccord final : **31/31 verts, 63,743 s**.
  **20/20 paires 4 h identiques** : monde complet,
  chroniques/récits/souvenirs, empreintes, mesures et audits. Zéro plantage/
  usurpation ; suspects 219 **4 → 4**, aucune hausse par nuit, répartition
  Relais/mine/auberge/crue/hameau **1/0/1/2/0**. Cycles **498 → 498**,
  préemptions **46 → 46**, à expliquer **51 → 51**, dérives **216 → 216**.
  Un travailleur réduit ; vingt références exactes absentes calculées et
  rangées une seule fois. Aucune nouvelle garantie d'autonomie des sources
  sur un long trajet. Aucun Luna ni suite complète ; bruts
  `C:/Users/msics/donjon/artifacts/restitution-246/`.
  [Rapport 246](taches/rapport-codex-246-restitution-route.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Lot C du diagnostic 237. _rendre juge la remise sur l'état projeté après le trajet (recherche commune d'aller, puis echanges.necessaire(apres=...)) : le bien reste un moyen pendant le transport, la restitution n'est écartée que s'il reste nécessaire après la remise. Capture historique de Maël (hameau 42, 421) et lampe de Gaspard (mine) ; refus si l'arrivée est sombre sans autre source. 20/20 nuits 4 h identiques, suspects 4 → 4.

- **Branche `codex-conception-a5`, fusionnée**, lot **245**, base
  `integration 9b69785` : inventaire d'A5 et onze lots proposés, sans code
  du jeu ni calcul. `confier`, agendas sociaux et contrat 213 réutilisables ;
  filiation de mandat, autorité et compte rendu général manquants.
  Lot 242 lu sur `origin/codex-suivi-delegation` (`0b37f44`), absent de cette
  base : à intégrer avant A5, limites des anciennes charges non datées
  conservées. Six PNJ déjà présents dans la crue étendue ; statut de Gorm,
  réglages d'autorité, profondeur et réaffectation proposés en options.
  Aucun test, banc ou Luna ; vérification documentaire uniquement.
  [Rapport 245](taches/rapport-codex-245-conception-a5.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rapport seulement. Inventaire d'A5 : briques existantes (confier, amener, devis d'intermédiaire, aides acceptées, voix), origine mandat, compte rendu, réaffectation, récursion, statut et ascendant absents ; onze lots proposés (ascendant neutre, statut sourcé, filiation bornée, jugement selon l'autorité perçue, faire ou confier, compte rendu, réaffectation, évolution de l'ascendant, joueur mandant et mandaté, données du hameau). Quatre arbitrages à l'utilisateur. Premier essai Sol medium.

- **Branche `codex-place-perimee`, fusionnée**, lot **234**, ciblés et banc validés.
  Merge demandé de `origin/integration` **`d9e5166`** (233/236/238/239/240)
  dans **`860fa0b`**, sans rebase, seul conflit documentaire. Moteur 234
  inchangé depuis `5f73166` : jugement commun placement/rapprochement, cible
  crue, trajet possible et progression sans dégradation ; posture effective
  sans réservation de geste, détour à distance égale permis. Aucun cas d’acteur.
  **46/46 ciblés initiaux verts**, puis **31/31 verts** (Lucien, 225, place,
  sécurité). Aubin **8 passages/30 min** contre 188, garde livrée/verrouillée.
  **Ilse rejoint Brune éclairée**, jamais Aubin localisé : chronique complète,
  adaptation conditionnelle autorisée `89fdfb8`, croyance/lumière contrôlées.
  **La nuit historique de Lucien change : vol réussi à la place de la garde
  éclairée.** Contrôle 229 à 95 conservé ; reprises seulement après entrée
  nouvelle levant l’obstacle, aucun témoin cru présent/vu/à portée d’oreille
  au vol 107–109. Anselme reprend le ballot, huit pièces cherchées à 114,
  contrat de tâche palier 4 en attente ; garde palier 13 non prioritaire.
  Zéro aller-retour injustifié 219, aucune navette après la recherche.
  **Séparation autorisée `ffd814f`** : test de cette trajectoire et scène de
  lanterne explicitement sans pulsion sur le ballot ; assertions de garde,
  possession/lumière/changements de lieu/recharge conservées.
  **Suite complète laissée au superviseur**, nouvelle règle **`4422f13`**. Passe arrêtée sur instruction après **1545 tests / 166 fichiers achevés**, zéro échec, une erreur Windows `os.replace` à la sauvegarde initiale du test TUI de coffre vide, avant l’application. Ce seul test, inchangé, repris **vert en 3,602 s** ; cause système non identifiée. Résultats partiels archivés ; cette passe n’a été ni achevée ni relancée.
  Banc : **20 paires de 4 h**, quatre références du cache `d9e5166`, seize
  manquantes rangées une fois. Suspects **2 → 2, épisodes identiques**, aucune
  hausse par nuit ni nouvelle alerte, aucun plantage/usurpation ; maxima PNJ/h
  **9/10/15/24/22 inchangés**. Cycles **499 → 499**, préemptions **49 → 49**,
  à expliquer **66 → 65**, dérives **222 → 218**. Mireille auberge 2024 et
  demandes promises de Maël hameau 7 : anciens écarts absents après fusion.
  Fonctions exclues intactes, aucun Luna, deux travailleurs réduits au plus ;
  créneau dépassé. Bruts `C:/Users/msics/donjon/artifacts/place-234/reprise/` ;
  [rapport 234](taches/rapport-codex-234-place-perimee.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. pnj._jugement_placement et _pas_placement communs à signes.place et _rejoindre_un_proche : cible crue localisable, objectif atteignable, trajet qui améliore ; une posture périmée cède et ne réserve plus le geste. Ilse rejoint la lumière et une compagnie (Brune, Aubin jamais localisé : assertion adaptée avec preuve). La nuit historique de Lucien change : vol réussi à 107-109 min sans témoin cru (légitime selon 225), puis attente d'information ; le retour de lanterne est vérifié dans une scène dédiée, assertions conservées. Aubin 188 → 8 passages/30 min. 20 paires 4 h : suspects 2 → 2, maxima inchangés. Suite complète laissée au superviseur.

- **Branche `codex-suivi-delegation`, fusionnée**, lot **242**, base
  `c870c8b` : suivi des charges confiées sur échéance explicitement connue.
  `confier` conserve une durée physique mesurable du plan accepté, distincte
  du coût pondéré ; contrôle du résultat cru par le mandant, arrêt sur
  réalisation apprise, revalidation de l'attente dans `Vue.aides` et
  `agendas._amener`. Échéance facultative des délégations initiales validée
  avec `attendu` ; aucune migration ni donnée de scénario modifiée.
  **Limite : Gorm au Relais n'a aucun accord daté ni échéance dans la donnée
  actuelle ; son immobilité historique ne reçoit pas un délai fabriqué.**
  Scène d'auteur avec accord explicite et autre charge à la mine (Bram/Josse),
  sauvegardes/rendus rechargés, réalisation en route et laps découpés.
  Relance d'abord rouge (deux obligations au lieu d'une), puis raccord
  supplémentaire expressément autorisé :
  `confier` réutilise l'obligation active du même mandant et de même condition,
  renouvelle devis/date/échéance par `agendas.renouveler` ; autres conditions,
  contreparties et ordre conservés. Paroles closes/annulées/rompues exclues.
  **54 tests directement concernés verts / six fichiers**, dont 17 nouveaux
  tests, la relance après recharge, deux conditions distinctes, paroles
  closes/annulées et le contrôle AST A1. **Banc final : vingt paires 4 h**,
  zéro plantage/usurpation, suspects **0/0/1/1/0 inchangés** (Relais/mine/
  auberge/crue/hameau), aucune hausse par nuit ; S/F/D et minutes d'attente
  inchangés, chroniques/récits/souvenirs identiques 20/20. Références toutes
  relues ; aucune référence rejouée. Une première suite
  interrompue à 45 fichiers / 784 tests pour clôture durable et prémisse
  explicite du test d'abri (eau crue en hausse +8, et non baisse mesurée).
  Assertions historiques intactes, fichier des boucles repris vert.
  **Suite complète laissée au superviseur**, nouvelle consigne du 2026-10-28
  (`4422f13`) : passe finale arrêtée à **18 fichiers / 323 tests, aucun échec** ;
  aucune suite complète achevée ni revendiquée. Créneau dépassé par les reprises
  et vérifications ; aucun calcul laissé actif. Bruts
  `C:/Users/msics/donjon/artifacts/delegation-242/`.
  [Rapport 242](taches/rapport-codex-242-suivi-delegation.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `echanges.py`, `planification.py`, fusionnés sans conflit textuel. Le mandant juge une charge confiée sur une échéance connue (planification.duree_devis : durée physique du plan retenu, conservée par echanges.confier) et ses croyances ; échéance passée sans constat : il va voir, reprend ou réaffecte ; réalisation constatée ou apprise : clôture. Relance du même mandant pour la même condition : l'obligation active est réutilisée (agendas.renouveler). Pas de délai inventé : la délégation initiale de Gorm au Relais, sans échéance déclarée, reste sans suivi temporel. 20/20 nuits 4 h identiques. Suite complète laissée au superviseur.

- **Branche `codex-ceder-outil-b`, fusionnée**, lot **228**, reprise du
  **202**, base intégrée **`d9e5166`** (233/238/239/240), fusion `e938352`.
  Compensation `e8feb8f`, six premiers oracles `537a352`, seconde extension
  autorisée **`d3a4d67`**. Aucun nouveau code moteur pendant les arbitrages.
  Capacité marginale protégée sauf doublon, remplacement ou gain suffisant ;
  achat **8,4 contre 0,909 refusé**. Cache négatif à dépendances crues égales
  conservé, anciens verdicts rejugés. Fonctions réservées des autres lots intactes.
  **Torche 1985 : service non bloqué**, douze jugements admissibles avant 2 min ;
  vente de crochets compensée à huit pièces (P=G=33,899), classée 6,20, qui
  devance le service choisi sur intégration (55,43). Parcours naturel original
  testé séparément. Reconstruction déclarée : torche d'Ilse remise à Brune,
  offre typée réellement payée, puis autonomie intacte ; annonce sauvegardée,
  engagement tenu, service protégé, état/rendus et bloc/découpe contrôlés.
  Rémy : extinction juste au bureau éclairé (niveau 2, `lumiere_utile=False`).
  Tilo : achat réel 1, remboursement 19, dette 1 persistante, conservation d'or
  et absence de double versement ; apport réel puis solde complet vérifiés.
  **48 ciblés distincts verts** pour les quatre fichiers de la seconde extension.
  `securite` intact : distance 4 déjà rouge sur `d9e5166`, confiée au lot 234.
  **Suite complète laissée au superviseur** (consigne/AGENTS `4422f13`) :
  passe en cours arrêtée, aucun verdict final revendiqué ; ciblés du lot verts.
  Suite antérieure : 2 590 tests, six échecs/zéro erreur, attribution archivée.
  Seul réancrage de capture : hash monde auberge du premier arbitrage (crochets
  14,4 contre huile 6 ; pièce proposée, autres empreintes gardées).
  Mesures antérieures contre `3c0e1ca` : S hameau **35→35,75**, nuits dans
  **[26 ; 44]**, suspects **2→2** sans hausse par nuit ; mine **910→887 recherches,
  10 925→9 959 nœuds**. Aucun nouveau banc revendiqué sur `d9e5166`.
  Aucun Luna ; deux travailleurs réduits au plus ; aucune clé de signature.
  Bruts `C:/Users/msics/donjon/artifacts/ceder-228/reprise/` ;
  [rapport 228](taches/rapport-codex-228-ceder-outil-reprise.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Un PNJ ne cède pas une capacité qu'il perdrait sans compensation (202) ; une offre reste possible quand la contrepartie compense réellement la capacité perdue (biens.valeur_capacites, echanges.necessaire, evaluer_proposition) ; recours négatif retenu tant que ses dépendances crues ne changent pas. 20 paires 4 h : S hameau 35 → 35,75 (toutes les nuits dans l'étendue de référence), suspects 2 → 2, coût mine −8,8 % nœuds. Promesse de torche du hameau 1985 : Brune préfère désormais la vente compensée de ses crochets (autre choix, service non interdit). Oracles de trajectoire arbitrés avec preuve dans dix fichiers de tests ; hash monde auberge réancré explicitement. Suite complète laissée au superviseur.

- **Branche `codex-lumiere-faible`, fusionnée**, lot **244**, base
  intégration **707e7ac**. `Vue.recharge_utile` distingue capacité de
  lumière et réserve faible : une source encore allumée ne rend plus
  pertinent du combustible sans gain dans la projection, sauf entretien
  explicite. Même critère pour acquisition, parts et alimentation ; aucun
  plafond ni autre mécanisme changé. Les trois recherches réelles de 435
  retrouvent le résultat de l'ancienne complète sous plafond ; grenier
  **7 091 → 336 nœuds**, coût **125,64**, chambre **11 139 / 11 898 →
  656 / 663**. Monde/rendu/scène rechargés, **zéro seconde sans intention
  entre 435 et 480** sur le rejeu ciblé (44 min 17,8 s au 243),
  laps découpé à l'auberge et à la mine,
  entretien réellement exécuté et sauvegardé. **12/12 paires 2 h
  identiques** (auberge/mine/Relais). Coût mine 1985 4 h : **10 119 →
  10 100 nœuds**, mêmes choix, chroniques et état final complet.
  **20/20 paires 4 h identiques** (états, récits, souvenirs, empreintes,
  mesures, audits), cinq scénarios × quatre graines ; zéro plantage,
  deux suspects inchangés. **5 tests finaux verts, 18,244 s**.
  **Contrôle 8 h auberge 42 vert, 2 528,217 s**, `VERIFIER` et spatial 0,2 ;
  une ancienne borne à 312, même coût complet (73,498790), aucune absence
  à 435, 143 choix de Lucien avec intention entre 435 et 480.
  **Suite complète laissée au superviseur** : passe en cours arrêtée à
  réception de la règle `integration` 4422f13, sans bilan global.
  Créneau dépassé par ces validations.
  Limite : pas de
  décompte de l'autonomie dans la projection, donc aucune garantie ajoutée
  de couvrir physiquement un long plan. Aucun Luna, bruts
  `C:/Users/msics/donjon/artifacts/lumiere-244/` ;
  [rapport 244](taches/rapport-codex-244-lumiere-faible.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Vue.recharge_utile : une recharge n'est utile que pour allumer une source éteinte sans charge ou restaurer une réserve visée par un entretien ; la réserve faible ne rend plus l'huile pertinente (729 acquisitions, 1 052 devis envisagés pour rien). Lucien auberge 42 à 435 : 7 091 → 336 nœuds, même résultat que la complète, zéro seconde sans intention (44 min au lot 243). 12/12 empreintes 2 h et 20/20 nuits 4 h identiques ; VERIFIER + spatial 0,2 auberge 42 8 h vert. Suite complète laissée au superviseur (nouvelle règle).

- **Branche `codex-bornes-garde`, fusionnée**, lot **243**, base
  intégration **c870c8b**, diagnostic seul. Les deux absences historiques
  `4306c14`, auberge 42 à 435, sont reproduites : 4 000 nœuds contre
  **7 071 / 6 574** pour les complètes, coûts **126,36 / 127,289407**.
  Elles sont reconnues dans `BORNES`, même résultat sans optimisation :
  aucune violation silencieuse du contrat 48, aucun plafond ni code changé.
  Lecture de lanterne devenue faible, combinatoire des états, séjour H trop
  bas pour conclure sous plafond ; contre-épreuve forte à 336 nœuds.
  Intégration : première absence au grenier maintenue (7 091 nœuds),
  deux absences à la chambre (11 139 / 11 898), ronde de sécurité choisie.
  Historiquement, aucun temps sans but : la garde de la chambre coûte moins.
  Sur l’intégration, **44 min 17,8 s sans intention entre 435 et 480**,
  hors deux courtes rondes ; besoin de biens en attente confirmé à la recharge.
  Cinq couples état/but réétudiés sur captures rechargées, conséquences
  moteur/monde/rendu/scène rechargés identiques ; autre recours de Joss.
  **15 ciblés verts, 163,033 s** ; aucune suite complète ni campagne globale
  supplémentaire (diagnostic seul), aucun Luna. Bruts
  `C:/Users/msics/donjon/artifacts/bornes-243/` ;
  [rapport 243](taches/rapport-codex-243-bornes-garde.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement. Limite reconnue, pas de violation du contrat 48 : les recherches jouées plafonnent à 4 000 et sont consignées. Cause : la lanterne d'Hugues lue faible à 435 déclenche la découverte des moyens de lumière, qui multiplie les états (336 nœuds sans cette lecture contre plus de 4 000). Sur l'intégration, Lucien reste 44 min 17,8 s sans intention entre 435 et 480. Suite possible : borner la découverte de lumière quand une source faiblit (piste C1/saillance), à mesurer.

- **Branche `codex-aide-stable`, fusionnée**, lot **240**, base
  intégration `1c71666`. `Vue.detresses` conserve l'ouverture de l'aide pour
  une intention sans geste tant qu'une promesse connue reste valide, dès
  le retrait de la demande exécutée. La phase `attendre` seule n'ouvre pas
  l'aide d'une garde tenue. Moyens,
  refus et confiance restent revalidés ; aucun ancien plan réinstallé,
  aucun champ ajouté, aucun changement de `_classer`, des échanges, de
  `pnj.py`, des biens, de l'ouïe ou du MJ. Captures historiques `4306c14`
  hameau 1985 à 541 et 544:156 reproduites ; deux régressions échouent sur
  le constructeur exact de la base et passent avec le raccord. Autre besoin
  à la mine (lumière de Bram, aide de Josse), annulation reçue et réalisation.
  Monde/rendu rechargés et laps découpés couverts ; deux contre-épreuves
  rouges sur la base. Suite complète unique : **2 534 tests / 293 fichiers,
  3 409,760 s, trois échecs, zéro erreur, 16 ignorés ; suite non verte**.
  Deux écarts d'empreintes corrigés par le raccord à la seule promesse connue,
  sans modifier les oracles : tous les champs mine/auberge retrouvent la base.
  Torche hameau 1985 reproduite sur la base, mêmes 3188/3615 (réserve 238).
  **24 ciblés finaux verts**, dont les deux oracles historiques intacts ;
  même échec de torche sur le raccord final. **20 paires 4 h finales**,
  zéro plantage, suspects 219 **0/0/2/0/0 inchangés** ; cycles 507,
  préemptions 58, à expliquer 87 inchangés. **20/20** états finaux,
  chroniques/récits/souvenirs/empreintes identiques ; recherches neuves
  **15 017 → 15 024 (+0,05 %)**. Vingt références réemployées, aucune
  rejouée ; aucune seconde suite complète. Créneau dépassé par les validations.
  Bruts `C:/Users/msics/donjon/artifacts/aide-240/` ;
  [rapport 240](taches/rapport-codex-240-aide-stable.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Vue.detresses garde l'ouverture de l'aide tant qu'une aide acceptée reste connue et valide, sans dépendre du classement du besoin (Gorm hameau 1985, 544 : son choix effaçait son propre recours). Autre cas : Bram attend que Josse allume la chandelle. 20/20 nuits 4 h identiques, suspects inchangés. Suite : un échec préexistant (torche, corrigé depuis par 238).

- **Branche `codex-pas-compagnons-c`, fusionnée**, lot **233** :
  livraison `f34e6c2`, reprise après merge de `origin/integration` **`01ce467`
  dans `7d68a8f`**, sans rebase, seul conflit documentaire. Le bruit attribué
  réveille le choix sans rotation ni position inventée ; aucun nouveau moteur
  ni MJ dans la reprise, `tenu` 195 conservé. **Décision utilisateur : baisse
  de richesse du hameau acceptée**, les rencontres nées des rotations fortuites
  n'étant pas légitimes : banc initial S **35 → 27,75**, acceptées **13 → 9**.
  **Cinq écarts arbitrés**, placement d'Ilse laissé au **234** : six champs
  d'empreintes migrés sur preuves, lignes et deux vues historiques inchangées ;
  secours de Rémy repris au checkpoint réel d'adoption **725** de `01ce467` ;
  lampe effectivement vue et Josse occupé au poste ; trajet du témoin déclaré
  comme réflexe prioritaire au lieu d'un devoir injecté sans charge.
  **31 ciblés + 19 tests de pas verts**, mêmes monde/rendu rechargés et laps
  découpés ; **152/153 anciennes assertions identiques**, une expression
  d'empreintes migrée, quatre assertions de provenance/schéma ajoutées.
  **Aubin crue 2024 à 23576** : trajectoire issue indirectement du réveil 233
  (absente sans ces seules lignes), mais retour après fin de surveillance,
  `eveil=None`, vers **ouvrir/servir**, sans répéter la demande refusée à 23551.
  Refus conservé, réserve toujours fermée et pas de nouveau don pendant le
  contrôle rechargé/découpé. Retour **justifié comme changement de moyen** ;
  alerte brute 219 conservée, aucune garantie générale des boucles.
  **Suite de reprise unique : 2 549 tests / 294 fichiers, 2 430,801 s,
  quatre échecs, zéro erreur, zéro ignoré**. Aucun des cinq écarts repris ne
  revient ; le fichier de stabilité de Lucien du 229 passe (neuf tests).
  Restants : **trois préexistants** (torche hameau 1985, deux MiMo `6 != 5`,
  reproduits sur `adb52c4` à la livraison initiale) et **placement d'Ilse du
  195 réservé au 234**. Suite non verte, aucun nouvel échec identifié.
  Créneau dépassé par la suite unique. Aucun Luna, deux travailleurs réduits ;
  pas de nouveau banc global, mesures initiales et leur référence conservées.
  Bruts `C:/Users/msics/donjon/artifacts/pas-233/reprise/` ;
  [rapport 233](taches/rapport-codex-233-pas-compagnons-c.md).
  Fusionné sur l'intégration : conflits de documentation et de `tests/test_signalements.py` (test de classement du lot 239 et préparation de scène du lot 233, réunis) ; fichiers de code touchés aussi depuis la base : aucun commun. Décision du 2026-10-28 : perte de richesse au hameau acceptée (S 35 → 27,75). Un pas compatible avec un compagnon cru proche s'explique sans retournement et réveille le choix (esprits.reconsiderer) sans position inventée ; preuve d'accomplissement des engagements dans echanges.tenu (195). Retournements divisés par deux à quatre. Cinq oracles caducs arbitrés avec preuve ; retour d'Aubin crue 2024 justifié (autre moyen). Placement d'Ilse laissé rouge, réservé au lot 234.

- **Branche `codex-suite-verte`, fusionnée**, lot **238**, base `e84d5a7` :
  faux audit MiMo remis au schéma actuel (`nature`, sans `verdict`/`comptes`),
  comptes d'appels et assertions conservés ; deux fichiers entiers verts,
  **13 tests, 7,627 s**. Passe initiale : **36 tests, trois échecs**.
  Reprise moteur autorisée après l'arrêt initial : trace créée à 3288 puis
  clôturée dans le même choix, déplacement de Brune avec la torche pris
  pour un départ d'Ilse, encore crue dans l'échoppe ; extinction à 3615,
  combustible 59. `biens.py` retient le lieu cru du bénéficiaire à la
  réussite ; une ancienne trace mobile sans ancrage ne prouve pas un départ.
  Raccords de création/validation explicitement autorisés après clarification.
  **50 ciblés verts / cinq fichiers, 34,530 s**, trois nouveaux tests,
  monde/rendu/scène rechargés, laps en bloc/découpé ; assertions historiques
  intactes. Banc final vingt paires 4 h, cinq scénarios × quatre graines :
  fautifs **1 → 0**, physiques **5 → 6**, suspects **2 → 2** sans hausse par
  nuit/scénario, zéro plantage. Vingt références `e84d5a7` rangées une fois,
  toutes relues au banc final après renforcement des anciennes traces mobiles.
  Suite commencée puis interrompue pour ce renforcement ; seule passe complète
  finale achevée : **2 529 tests / 292 fichiers, 2 518,071 s, zéro échec,
  une erreur Windows TUI**, zéro ignoré. `os.replace` refuse le temporaire de
  `test_sortie_galerie_vers_palier_noir_garde_joueur_sur_la_carte` ; test inchangé
  repris seul vert en **1,020 s**, verrou non identifié. **Suite brute non verte**,
  aucune seconde suite complète. Les trois échecs initiaux sont corrigés.
  Anciennes traces mobiles sans ancrage : protection conservée faute de preuve
  de départ, aucune reconstruction historique ni entretien ajouté. Créneau
  dépassé par les validations, deux calculs réduits au plus, aucun Luna.
  Aucun MJ, adaptateur, capture ou fonction des lots voisins modifié.
  Bruts `artifacts/suite-238/` du dépôt principal ;
  [rapport 238](taches/rapport-codex-238-suite-verte.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Torche du hameau 1985 : la trace du service payé était close par une fausse déduction de départ d'Ilse (Brune emportait la torche) ; le lieu cru du bénéficiaire au constat de réussite est sauvegardé (services_rendus.lieu_beneficiaire) et clore pour départ exige de le croire ailleurs que ce lieu et que le résultat. Faux audit MiMo remis au schéma actuel. 20 paires 4 h : pertes fautives 227 1 → 0, suspects 2 → 2. Suite : zéro échec, une erreur Windows TUI passagère (verrou de fichier temporaire), test repris vert.

- **Branche `codex-renonce-attente`, fusionnée**, lot **239**, base
  intégration `3c0e1ca` (236 inclus). `_classer` compte `renonce`, dont
  l'obstacle cru tient encore, comme un recours sans moyen admissible :
  attente si tous les recours sont bloqués, priorité à tout plan possible,
  aucun classement déduit d'un recours non évalué. Aucun changement du
  choix, du juge des obstacles, des propositions, des biens, de `pnj.py`,
  de l'ouïe ni du MJ. Captures mine 500/107 et 7/539:599 reproduites sur
  la base : `sans_recours` devient `attente`. Choix, récit, sauvegarde/rendu,
  laps découpés et reprise après constat couverts, autre besoin au Relais.
  **8/8 paires 2 h identiques** mine/Relais ; **4/4 paires mine 4 h
  identiques**, zéro plantage, sans recours 0/0/0/0 et attente 40/0/0/0
  inchangés. Replays ciblés jusqu'à 110/540 : chroniques identiques,
  5 → 0 PNJ·min sans recours dans chacune des deux fenêtres. **22 ciblés
  verts**. Suite complète unique : **2 531 tests / 293 fichiers,
  3 973,916 s, un échec, zéro erreur, 16 ignorés ; suite non verte**.
  Même échec de torche hameau 1985 que le lot 236, réussite à 3188 puis
  perte à 3615 ; aucun oracle affaibli. Comparaison spatiale pure verte
  (854,313 s). Aucun nouvel échec identifié, deux travailleurs réduits ;
  aucun Luna. Créneau dépassé par la suite finale.
  Bruts `C:/Users/msics/donjon/artifacts/renonce-239/` ;
  [rapport 239](taches/rapport-codex-239-renonce-attente.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. _classer traite un recours renoncé dont l'obstacle cru tient encore comme un essai sans moyen : besoin en attente, plus « sans recours ». Odon mine 500 à 107 et mine 7 à 539 : sans recours → attente, reprise après constat qui lève l'obstacle ; Gorm (Relais, passage obstrué) comme autre cas. Huit empreintes 2 h et quatre nuits mine 4 h identiques. Suite : un échec préexistant (torche, lot 238).

- **Branche `codex-navettes-garde`, fusionnée**, lot **236**, base
  `ecbf1a1`, diagnostic `6bed2a0`, correctif `3f217d0`. Extension autorisée à
  `pnj_propositions.plan_recours` et son raccord dans `deliberation.choisir` ;
  `recours`, registres négatifs, services protégés et MJ intacts. Un résultat
  ordinaire vide (but tenu) n'est plus confondu avec l'absence de solution
  (`None`) : pas de greffe commerciale par le seul besoin partagé. Auberge 7
  sur `4306c14` : sept passages/minute à 430–434 ; garde stable, ancienne
  contre-offre d'huile réinjectée au poste puis retirée en route. Nouvelle
  nuit `ecbf1a1` : pas de rafale de 426 à 435, mais greffe encore reproductible
  sur capture historique avant correction. **35 ciblés verts**, capture et
  Brune au Relais, monde/rendu rechargés, laps découpés, contre-offre utile
  conservée. **20 paires 4 h contre `ecbf1a1`**, références manquantes rangées
  une fois : suspects 219 **0/0/2/0/0 inchangés**, maxima de passages/heure
  **9/11/17/62/22 inchangés** (Relais/mine/auberge/crue/hameau), zéro plantage.
  Cycles 507, préemptions 58, à expliquer 87 inchangés. Réserve auberge 7 :
  dérives ouvertes **8 → 9**, pas de hausse de suspects. **Suite complète
  unique : 2 524 tests / 292 fichiers, 3 643,527 s**, un échec, zéro erreur,
  16 ignorés ; **suite non verte**. Échec de torche hameau 1985 reproduit seul
  sur `ecbf1a1` (16,293 s), mêmes réussite à 3188 et perte fautive à 3615 ;
  aucun oracle affaibli. Deux travailleurs réduits au plus, créneau dépassé
  par les vérifications. Aucune garantie
  universelle des navettes, heure historique entière non rejouée. Bruts
  `C:/Users/msics/donjon/artifacts/navettes-236/` ;
  [rapport 236](taches/rapport-codex-236-navettes-garde.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Un but tenu sans geste ([]) se distingue d'un recours sans moyen ordinaire (None) : plan_recours ne remplace plus le plan vide d'une garde par une ancienne contre-offre du même besoin (Anselme, auberge 7, 429-435 : achat d'huile injecté puis retiré à chaque reconstruction). Capture historique corrigée, aucun nouveau départ sur six minutes. 20 paires 4 h contre ecbf1a1 : suspects et maxima de passages inchangés, 18/20 états identiques. Suite : un échec préexistant (torche du hameau, lot 238).

- **Branche `codex-alertes-231`, fusionnée**, lot **237**, diagnostic seul,
  base/intégration **`e84d5a7`** (218/229/230/232 inclus), aucun code du jeu
  modifié. **Dix nuits × 12 h**, cinq cas sur `4306c14` détaché puis intégration,
  séquentielles, priorité réduite, aucun Luna ni suite complète. Les cinq
  replays historiques retrouvent chronique/récit/souvenirs/empreintes et
  mesures communes ; **228 captures**, monde et rendu rechargés identiques.
  Mine : les 465 PNJ·min historiques « sans recours » viennent d'Odon 500/7 ;
  renoncement retenu laissé « pressant » par `_classer`, premières inactivités
  107/539. Intégration **305 → 275**, **160 → 145**, même défaut initial.
  Gorm hameau 1985 : onze suspects chaleur ; revalidation dépendant du classement
  attente/presse, abandon isolé à 544 (326556). Maël hameau 42 : quatre suspects,
  restitution choisie à 419 puis annulée au lieu sombre intermédiaire par
  `necessaire`. Les deux occurrences disparaissent des nuits actuelles
  (zéro retour chaleur de Gorm, zéro suspect de Maël), mais les deux juges
  reproduisent encore leurs limites sur les captures historiques.
  Appels Odon/mine 1985 **19 → 0** ; historiquement sept lieux puis douze
  réouvertures par indices nouveaux, aucun rappel sans réouverture observée.
  Trois petits lots distincts proposés : qualification des recours bloqués,
  stabilité de l'aide sous adoption, cohérence transport/remise ; aucune
  nouvelle moyenne sur huit graines ni garantie générale des boucles.
  Bruts `C:/Users/msics/donjon/artifacts/alertes-237/` ;
  [rapport 237](taches/rapport-codex-237-alertes-231.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement. Mine : « sans recours » mal qualifié après un renoncement (Odon, 107 et 539 ; toujours présent sur l'intégration), petit lot A (classement commun des recours renoncés). Appels : aucune faute établie. Gorm hameau 1985 : l'aide ouverte après attente est effacée par sa propre adoption (lot B, mécanisme latent). Maël hameau 42 : restitution rejetée en route par la nécessité immédiate du bien (lot C, latent).

- **Branche `codex-purete-candidats`, fusionnée**, lot **232**, base
  `integration adb52c4` : `biens.services_proteges` ne supprime plus les
  traces pendant une lecture. Clôtures retenues hors `data`, publiées après
  un choix complet réussi ; devis isolé et choix interrompu sans écriture,
  imbrications transmises au parent. Arrêts historiques `4306c14` reproduits :
  mine 42 à 415 (copie 418, Gaspard, poêle/Josse), rixe 42 à 350 (copie 351,
  Aubin, brasero/marchand) ; `_entrees_communes → services_proteges`, seul
  champ modifié `services_rendus`. Sur la base actuelle enrichie de 218/230,
  ces deux nuits passent déjà, mais la lecture écrit encore hors choix.
  **22 ciblés verts**, cinq nouveaux tests, captures versionnées, monde/
  rendu/scène rechargés et laps découpés identiques. **12/12 empreintes
  2 h identiques** à `adb52c4` (Relais/mine/rixe × quatre graines), zéro
  plantage ; douze références manquantes rangées une fois. Mine et rixe
  corrigées 8 h `VERIFIER` + spatial 0,2 achevées sans arrêt, mesures et
  mondes finaux complets identiques à la base actuelle. **Suite complète
  unique : 2 526 tests / 292 fichiers, 2 366,049 s, quatre échecs, zéro
  erreur**, suite non verte : Lucien et deux MiMo identiques aux traces
  préexistantes 230 ; compteur torche hameau 1985 reproduit exactement
  sur `adb52c4` (un ciblé, 9,414 s), laissé intact. Aucun nouvel échec
  identifié, aucun oracle modifié. Créneau dépassé par les validations.
  Aucun Luna, deux calculs réduits au plus ; bruts
  `C:/Users/msics/donjon/artifacts/purete-232/` ;
  [rapport 232](taches/rapport-codex-232-purete-candidats.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. biens.services_proteges ne supprime plus les traces finies pendant la lecture : clôtures retenues hors de data et publiées par planification.vues_du_choix après un choix complet réussi, abandonnées sinon. Corrige les deux arrêts du lot 231 (Gaspard mine 42 à 415, Aubin rixe 42 à 350) : huit heures achevées sous VERIFIER et spatial 0,2. 12/12 empreintes 2 h identiques. Suite : quatre échecs préexistants.

- **Branche `codex-reessai-regressions`, fusionnée**, lot **229**,
  départ `1e09926`, première livraison `ad785cf`, puis merge demandé de
  `origin/integration` **`c9d8c05`** (230/231), sans rebase. Aucun moteur/MJ
  modifié par 229. Lucien : divergence à 95 min, ancienne reprise par délai
  contre témoin encore cru présent ; reprises à 107 et 167 sur localisation
  entendue d'Anselme. Fenêtre de garde explicitement réancrée 150 → 165 min,
  but, bougeoir porté/allumé, lumière effective et état/rendu rechargés exigés.
  Huile `881db69` : refus reproduit, deux parts pour une réserve de deux
  après part préparée pour Lucien à 464 min ; refus juste. Promesse annulée
  à 466, part séparée chez Odile (échanges réservés au 228).
  **Après 230, test d'huile vert sans adaptation 229** : fichier strictement
  identique à `origin/integration`, lanterne à sec et au contact de 230 conservée,
  réserve d'Odile inchangée. **35 ciblés verts après merge** : 34 tests de
  quatre fichiers en 225,369 s et test exact d'huile en 194,531 s.
  Suite complète unique **avant 230** : **2 498 tests / 289 fichiers,
  3 637,727 s**, un échec de voix préexistant (Mathurine entendue, relevé 225),
  zéro erreur, 16 ignorés ; **suite non verte avant 230**. Pas de seconde
  suite ni banc moteur : aucun fichier moteur commun entre 229 et 230.
  Deux travailleurs à priorité réduite, aucun Luna ; créneau dépassé par
  les vérifications. [Rapport 229](taches/rapport-codex-229-reessai-regressions.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Tests et documentation seulement. Lucien : comportement juste (reprise du vol seulement après avoir entendu Anselme ailleurs, jamais par le délai), oracle de garde réancré 150 → 165 min avec exigences de lumière ramenée et de cause opposable. Huile : refus d'Odile pour cause necessaire juste sur 881db69 (réserve gardée = parts restantes) ; le test adapté par 230 passe inchangé. À voir avec 228 : une part détachée reste séparée chez Odile après l'annulation d'une promesse.

- **Branche `codex-restauration-charges`, fusionnée**, lot **218** :
  code `2bd1e6f`, reprise demandée sur **`881db69`** (224/225), fusion
  `7c46d64` sans conflit de code, validation finale `fa9dbe3`. Charge suspendue
  dans l'intention via `agendas`, conservée après découpe et reconstruction ;
  restauration physique et retour au poste par le planificateur, juge commun
  du 213/225, garde libérée après abandon. Parole due distincte de satisfaction
  du bénéficiaire ; remise et restauration au devis commun. Seul champ et
  validation dans `esprits`, aucun MJ/`social`/`pnj` modifié par le delta 218.
  **64 ciblés verts, 11 nouveaux**, onze repris après rejet du champ `null` ;
  Gorm/Mathe, autre contenant/scénario, porte/poste, suffixe perdu,
  reconstruction avant/pendant restauration, abandon, monde/rendu rechargés
  et laps découpés. Capture 209 rejouée sur la base : service à Ilse à 5/10 min,
  livraison historique `vivres_6` à 6 min non reproduite ; aucune amélioration
  de cette occurrence revendiquée. **20 paires 4 h**, classes 219 : suspects
  **4 → 4** (0/0/2/2/0 inchangé), zéro plantage/usurpation ; cycles **523 → 483**,
  préemptions **67 → 54**, à expliquer **59 → 63**, dérives **200 → 178**,
  états payés perdus **8 → 6** (durée non spécifiée). **Réserves avant fusion** :
  nouvelle alerte Brune hameau 2024 (neuf états actif/neuf sommeil), absence
  générale de boucle nouvelle non validée ; **coût mine +20,3 % en nœuds**
  (**9 189 → 11 051**, recherches **601 → 913**), critère non atteint.
  Nouveaux devis de feu de Bram : **1 680 nœuds**, restauration **85** ;
  aucune possibilité retirée pour réduire le compteur. Eau crue **1,25 → 3,75**,
  hameau **5 → 5 PNJ·min**, aucun gain uniforme d'attente/richesse.
  **Suite complète finale unique achevée : 2 497 tests / 289 fichiers,
  3 847,957 s**, deux échecs, zéro erreur, 16 ignorés ; les deux échecs
  (voix inconnues et stabilité de Lucien) sont reproduits sur **`881db69`**,
  aucun oracle modifié. Deux passes partielles antérieures interrompues,
  dont la reprise demandée sur 224/225 ; créneau dépassé par les vérifications.
  Anciennes suspensions déjà perdues et identité des sources non typées :
  limites explicites, aucune garantie universelle. Aucun Luna, deux travailleurs
  réduits au plus, commits non signés (aucune clé). Bruts finaux
  `C:/Users/msics/donjon/artifacts/charges-218/881db69/`, archives dans le parent ;
  [rapport 218](taches/rapport-codex-218-restauration-charges.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `deliberation.py`, `planification.py`, fusionnés sans conflit textuel. Conditions suspendues et phase de restauration conservées dans l'intention, transmises au même engagement après découpe ou reconstruction ; restaurer_charges recherche le rétablissement physique après le service (juge commun 213/225). 20 paires 4 h contre 881db69 : suspects 4 → 4, préemptions 67 → 54, états payés perdus 8 → 6 ; nouvelle alerte d'agenda de Brune (hameau 2024, neuf activations/sommeils) à relire à la prochaine vérification. Coût mine 1985 4 h : nœuds 9 189 → 11 051 (+20 %), recherches 601 → 913 (devis de feu de Bram). Occurrence historique 209 non reproduite sur la base. Fichiers de code communs avec 226/230 : suite complète relancée. Suite complète sur la fusion (`2844ef7`, `tools/tests.py --processus 3`, PC fixe) : **2 521 tests, quatre échecs**, zéro erreur (2 024,6 s) : la stabilité de Lucien, corrigée ensuite par le test du lot 229 (vert sur `bee69b4`), et trois préexistants (torche du hameau 1985 depuis 221/224, deux MiMo `6 != 5`). La troisième voix de Mathurine ne revient plus depuis 230.

- **Branche `codex-rendez-vous-tenu`, fusionnée**, lot **230**, base
  `1e09926` de l'intégration : une invitation à venir suppose de rester ;
  les plans de départ sans rapport avec l'interlocuteur cèdent aussi au
  rendez-vous. Seul un palier strictement supérieur autorise la rupture,
  annoncée par l'ouïe et retenue si entendue. Défense immédiate et alerte
  raccordées ; voyageur attaché au lieu convenu jusqu'au contact, au constat
  vide ou à la rupture entendue, sans rappel par simple délai/chemin coupé.
  Scène historique : six invitations de Mireille dont cinq à Mathurine
  **→ une**, trois voix **→ deux**, oracle historique inchangé.
  Défaut déjà visible sur `bd45f65` : Gorm invite Maël à 35, part à 292
  (hameau 7/42/2024, chroniques en cache). **105 ciblés consolidés verts**,
  neuf fichiers dont douze nouveaux cas : monde/ouïe/rendu rechargés et laps découpés.
  **20 paires de 4 h contre `1e09926`**, références manquantes rangées une
  fois : zéro plantage/usurpation, deux suspects 219 intégralement identiques ;
  préemptions **87 → 70**, à expliquer **85 → 70**, dérives **241 → 216**.
  Passe finale : vingt références relues du cache ; état final, chronique et
  avis identiques à la première mesure de branche, moteur figé par empreintes.
  Appels **11 → 12**, réponses **37 → 39**, retrouvailles **8 → 5** ; aucune
  nouvelle alerte de répétition/alternance par nuit/PNJ. Nouvelle alerte
  d'attente de devoir de Gorm en crue 7 (**fige_presse 3 → 4**), sans attente
  de rendez-vous active au relevé final ; limite conservée, pas de garantie
  générale des boucles ni des repas de Mathurine. Rupture non entendue ou
  départ muet du joueur : lieu vide à constater, aucun savoir distant.
  Suite complète unique : **2 508 tests / 290 fichiers, 2 530,264 s**, sept
  échecs et une erreur bruts ; cinq prémisses/oracles repris verts, **trois
  préexistants reproduits sur `1e09926`** (Lucien, deux MiMo), suite non verte.
  Derniers ajustements pendant la passe, puis neuf fichiers repris ; aucune
  seconde suite complète. Créneau dépassé par les validations. Aucun Luna ; bruts
  `C:/Users/msics/donjon/artifacts/rendez-vous-230/` ;
  [rapport 230](taches/rapport-codex-230-rendez-vous-tenu.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Qui répond « Ici, viens ! » reste jusqu'à l'arrivée, l'échéance réglée sur la distance ou un palier strictement supérieur ; s'il part, la rupture s'annonce par l'ouïe ; « J'arrive ! » va au lieu convenu sans rappeler. Mireille/Mathurine : six invitations → une. 20 paires 4 h contre 1e09926 : suspects 219 identiques, préemptions 87 → 70, à expliquer 85 → 70 ; une alerte fige_presse nouvelle (Gorm, crue 7). Test de l'huile (lot 229) adapté : lanterne déclarée à sec et au contact. Suite : trois échecs préexistants (Lucien, deux MiMo).

- **Vérification d'intégration 4306c14**, lot **231**, branche
  `codex-verif-integ-4306c14`, fusionnée : code `donjon/ tools/` identique
  à `4306c14`, aucun correctif, Luna, pull ni référence rejouée. **49 nuits
  lancées une fois, 47 achevées, intégration non verte** : contrôles mine 42
  à 415 et rixe 42 à 350 interrompus par la mutation d'état pendant
  `planification.vues_du_choix` ; mêmes contrôles achevés sur `4d4c625`.
  Auberge 42/Lucien à 435 : **75 bornes**, dont 73 `ancienne_borne` à
  résultat exact et deux plans de garde manqués ; aucun autre écart consigné.
  **31 suspects 219, 390 à expliquer ; zéro geste fautif 227**, 22 pertes
  physiques et une après départ cru ; zéro usurpation/coup/mort relevé.
  Attente crue **905 → 1 162,50**, hameau **1 021,25 → 1 761,25 PNJ·min**.
  Bourse mine 1985 **228 → 0 demandes**, crue 2024 **16 → 0 coups**.
  Nouveaux cas à instruire : Anselme auberge 7 **246 passages/h** sous garde,
  Gorm hameau 1985 **onze retours chaleur/devoir** à 541–545, Maël hameau 42
  **quatre suspects restitution/inspection** ; correspondances anciennes
  archivées. Gorm crue 2024 : **5 → 12 sommeils** avant évacuation.
  Rendez-vous : **28 → 39 départs candidats** après « Ici, viens ! », aucun
  de Mireille ; urgences/échéances non certifiées. Un travailleur de calcul
  en fond à priorité réduite. Ni captivité exhaustive ni monde/rendu rechargé
  certifiés ; deux nuits sans mesures finales. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/verif-integ-4306c14/` ;
  [rapport 231](taches/rapport-codex-231-verif-integ.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement. 47/49 nuits : deux plantages de pureté des candidats (planification.vues_du_choix, mine 42 à 415, rixe 42 à 350) ; bourse 228 → 0, coups crue 2024 16 → 0, renoncements mine 1,75 → 0,25 ; suspects 219 : 31. Petits lots désignés : pureté des candidats, bornes de Lucien (auberge 42, 435), passages d'Anselme (auberge 7, 420-479), retours chaleur/devoir de Gorm (hameau 1985), suspects de Maël (hameau 42), sommeils de l'agenda de Gorm (crue 2024).

- **Branche `codex-compteur-services`, fusionnée**, lot **227**, départ
  `b8e433d` vérifié, moteur identique à `881db69` : outils seulement, aucun
  `donjon/` ni Luna modifié. Les pertes d'états payés distinguent le geste du
  prestataire sans départ cru (seul fautif), son geste après départ cru,
  le bénéficiaire/tiers et la cessation physique ; une cause non observée
  reste inconnue. Croyances prises avant le geste, observation de `agir`
  (marche comprise), exécution et horloges physiques, sans mutation du monde.
  Six cas 224 rejoués sur `bd45f65`/`e4ba54e` : **4 fautifs → 0**, **2 permis
  → 2**, **0 physiques → 4**, total brut **6 → 6**. Cas 217 historique
  retrouvé à **4584/4824**, corrigé sans perte dans la fenêtre reprise.
  Banc courant **20 nuits × 4 h**, cinq scénarios × quatre graines :
  **8 cessations physiques**, aucune autre classe ; monde complet,
  empreintes, chronique, récit, souvenirs et mesures identiques avec/sans
  sonde. **43 tests verts / trois fichiers, 104,740 s**, monde et rendus
  rechargés sur torche, serrure et marche. Pas de suite complète du jeu.
  Un seul calcul à la fois, priorité réduite ; aucune clé de signature.
  Limites : paiements/réussites non observés non reconstruits, première
  perte et conditions d'état déjà reconnues ; pas de causalité distante
  certifiée ni de garantie générale sur les boucles. Bruts
  `C:/Users/msics/donjon/artifacts/compteur-227/` ;
  [rapport 227](taches/rapport-codex-227-compteur-services.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Outils seulement. Quatre causes : geste fautif du prestataire (seule violation), geste après départ cru du bénéficiaire, bénéficiaire ou tiers, cessation physique. Six cas du banc 224 : 4 gestes fautifs → 0 (devenus cessations physiques), 2 permis. Intégration 881db69 : zéro perte fautive ; 20/20 nuits identiques avec et sans sonde.

- **Branche `codex-reessai-obstacle`, fusionnée**, lot **225**, départ
  `e4d8655` vérifié : patience 30 min conservée, répit 60 min retiré ; chaque
  renoncement retient son obstacle cru par but/moyen, sans effacement par
  délai, nouveau regard ou essai d'un autre moyen. Raccords minimaux
  `pnj._patienter`/`agir`/`_impasse` et `passage.faire_place`/`_patienter`
  expressément autorisés ; fonctions des lots voisins et MJ intacts.
  Mine 1985, même départ au puits : renoncements **31/122/213 → 31/147**,
  reprise **114** sur constat sans témoin, monde/rendu rechargés identiques.
  **51 ciblés verts**, autre cause/PNJ/scénario, ronde autonome et laps
  découpé contrôlés. **20 paires 4 h**, 20 références `bd45f65` en cache :
  suspects 219 **5→4**, cycles **468→498**, préemptions **53→53**, à expliquer
  **61→52** ; zéro plantage/usurpation, aucune nouvelle alerte de boucle
  par nuit/PNJ parmi les codes contrôlés. Mine : renoncements **3→1,5** ;
  auberge : sans recours **20→0 PNJ·min**, attente urgente inchangée ailleurs.
  Suite finale unique achevée : **2 462 tests / 286 fichiers, 2 014,763 s**,
  zéro erreur, trois échecs bruts ; oracle de rendu des rondes corrigé et
  repassé vert, **deux MiMo `6 != 5` historiques restent** (213/223), suite
  non verte. Tentative antérieure interrompue après découverte de la perte
  de mémoire lors d'un autre moyen, corrigée et testée. Créneau dépassé par
  les vérifications ; aucun code moteur changé après le banc final.
  **Limite : les anciens entiers n'ont aucune cause récupérable** ; le
  prochain renoncement l'enregistrera. Vérifications soumises aux urgences
  et trajets admissibles, pas de garantie universelle des boucles.
  Deux travailleurs réduits au plus ; aucun Luna, aucune clé de signature.
  Bruts `C:/Users/msics/donjon/artifacts/reessai-225/` ;
  [rapport 225](taches/rapport-codex-225-reessai-obstacle.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `deliberation.py`, `esprits.py`, fusionnés sans conflit textuel. Décision du 2026-10-27 (3 B) : patience 30 min gardée, REPIT retiré ; renoncer retient l'obstacle cru (étape, lieu, témoins, passage), levé par un constat ou un autre moyen, jamais par le temps ; inspections ordinaires en rondes de contrôle. Odon (mine 1985) : renoncements 31/122/213 → 31/147, reprise à 114 après constat sans témoin. Répétitions suspectes 5 → 4, à expliquer 61 → 52. Fichiers de code communs depuis la base (deliberation, esprits) : suite complète relancée.

- **Branche `codex-contact-sous-but`, fusionnée**, lot **226**, départ
  `e5afca8` vérifié, puis intégration 225 (`881db69`, pointe documentaire `b8e433d`)
  en avance rapide, seul conflit documentaire. Contact perdu de vue recherché
  sous son parent abri/enquête par `rejoindre` (inspection/appel/question 221),
  sans localisation réelle ni abri supposé. Seuls `_plan_abri`, `s_enquerir`
  et le raccord commun changent ; périmètre des lots voisins conservé.
  Captures 215 : Ilse cherche/appelle Aubin, Brune cherche Ilse pour sa chaleur ;
  Aubin reste justement sans recours sur ses ressources déjà connues.
  **Huit nouveaux tests verts**, auberge autonome, parent apaisé/démenti,
  refus/indices, monde/rendu/scène rechargés et laps découpés.
  **20 paires finales 4 h contre `881db69`**, références complétées une fois en cache :
  attente crue **218,75 → 108,75**, hameau **92,5 → 76,25 PNJ·min** ;
  suspects **4 → 2**, sans hausse par scénario, deux restants intégralement
  identiques ; zéro plantage/usurpation. S crue **16,5 → 24,5** ; appels **5 → 11**.
  Préemptions **67 → 87**, à expliquer **59 → 85**, dérives **200 → 241**,
  états payés perdus **8 → 9**. **Absence de toute boucle nouvelle non certifiée** :
  nouvelle alerte textuelle d'agenda en crue 2024 ; limites du service 224 conservées.
  **35 ciblés verts après 225** ; première mesure sur `346c1aa` archivée séparément.
  Suite initiale interrompue sur demande d'intégration (10 fichiers / 100 tests verts),
  seule passe complète finale achevée : **2 494 tests / 289 fichiers, 2 558,203 s,
  15 échecs bruts, zéro erreur**. Cinq échecs reproduits sur `881db69` (voix,
  compteur de service, lanterne Lucien, deux MiMo), laissés intacts ; dix écarts
  d'oracles/prémisses propres au contact résolus en reprises ciblées, monde/rendus
  et contrats conservés. **17 ciblés finaux + deux reprises verts** ; bilan
  consolidé : **cinq préexistants, suite non verte**, pas de seconde suite complète.
  AST : seules les deux fonctions et le raccord autorisés ; moteur inchangé depuis
  le banc. Créneau dépassé par validations et reprise 225. Aucun Luna, deux travailleurs réduits au plus,
  aucune clé de signature Git. Bruts `C:/Users/msics/donjon/artifacts/contact-226/` ;
  [rapport 226](taches/rapport-codex-226-contact-sous-but.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base 881db69 (227 : outils seulement). Contact sans lieu connu repris par rejoindre (inspection, appel, question 221) sous le but parent abri ou enquête. 20 paires 4 h contre 881db69 : attente crue 218,75 → 108,75, hameau 92,5 → 76,25 PNJ·min, S crue 16,5 → 24,5, suspects 4 → 2 ; préemptions 67 → 87 et à expliquer 59 → 85 en hausse, huit sommeils de l'agenda de Gorm en crue 2024 à surveiller. Cinq échecs de sa suite préexistants (voix du joueur, compteur torche corrigé par 227, lanterne de Lucien, deux MiMo).
- **Branche `codex-pas-compagnons`, non fusionnée**, lot **195** :
  **346c1aa fusionné par 11f728a**, extension autorisée à **`echanges.tenu`**.
  Point de comparaison après parole, preuve nouvelle propre `vu`/`essai`, bornes
  entre promesses identiques d'une même minute ; souvenir neutre sauvegardé.
  Aucun constat, position, émotion ou retour au choix ajouté. Seul `tenu` change
  dans `echanges.py` ; bloc `retenir_service` du 224 intact. Tilo allume et solde
  à minute 0 ; notification sur la chronique entière, clôture et protection
  vérifiées en plus, sans réancrer. **41 ciblés verts**, dont quatre nouveaux
  tests de preuve, monde/rendu/scène rechargés. Clé prêtée toujours à rendre.
  Prêts, contrat 213, tests 224 et palier passent.
  **Banc 20 paires 4 h contre 346c1aa : suspects 5→1**, aucune hausse par
  scénario ; préemptions 67→65, cycles 494→462, à expliquer 67→77,
  dérives 202→210, états payés perdus 8→7, figés pressés 3→4 (observations).
  Zéro plantage/usurpation. Après borne : 20 références relues du cache,
  20 états/chroniques/mesures/épisodes identiques au premier banc.
  Gorm Relais 2024 et hausse hameau absents ; Brune 2024 : zéro alerte.
  Après arbitrage : **huit échecs et l'erreur corrigés par des prémisses
  explicites**, **273 assertions identiques par AST**, huit fichiers et
  **67 tests ciblés verts**. Aucun changement du moteur depuis `e7aab68`,
  aucun banc relancé. Quatre préexistants laissés rouges : MiMo ×2 ; voix
  apparue à la fusion 221 (`d7dbf1a`) ; attente historique de perte de torche
  apparue à la fusion 224 (`346c1aa`), interaction avec 221 (224 seul vert).
  Vérification sur cinq sources exactes avec les deux tests originaux.
  **Suite après arbitrage : 2 497 tests / 289 fichiers, 2 091,515 s, cinq
  échecs, zéro erreur, zéro ignoré**, une passe finale après les prémisses,
  deux travailleurs réduits : quatre préexistants et défaut de placement.
  **Richesse hameau : S 40,5→27 correspond à des interactions réelles perdues**,
  ni bruits ni retournements ne comptent dans S ; acceptées 16→9, tâches
  faites 4→2, prêts/rendus 1/1→0/0 ; occurrences de travail payé 20→26.
  Placement hors périmètre : attitude périmée et recours d'abri. Proposition
  non appliquée dans `signes.place` : 21 tests de signes verts, Ilse rejoint
  Brune, assertion spécifique Aubin toujours rouge. **Lot séparé à créer**,
  contrat d'invalidation des attitudes périmées décrit sans l'appliquer ;
  défaut laissé rouge pour décision d'intégration. Aucun Luna, deux calculs
  réduits au plus, aucune clé Git.
  Limite : checkpoint oublié ou croyance inchangée, jugement conservateur.
  Rondes et registre visuel joueur hors lot. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/pas-195/extension-346/` et `arbitrage/` ;
  [rapport 195](taches/rapport-codex-195-pas-compagnons.md),
  [classement exhaustif et richesse](taches/rapport-codex-195-arbitrage.md).

- **Branche `codex-service-non-defait`, fusionnée**, lot **224**, base `a22f92e`
  vérifiée, puis 213 intégré (`bd45f65`, fusion `0192bb3`) : résultat promis
  conservé après clôture dans `biens`, filtre commun
  des gestes qui le défont (trajets compris) et économie de flamme, engagements
  ouverts compris. Besoin approché par le lieu cru du bénéficiaire, sans délai
  ni lecture de ses buts privés, sans obligation d'entretien. Cas réel 217
  repris à l'instant 4584, monde/rendu rechargés et laps découpé contrôlés.
  **20 paires 4 h contre `bd45f65` : critère du compteur brut non atteint,
  états payés perdus 6 → 6** ; quatre extinctions précoces évitées au Relais,
  pertes ensuite relevées à l'épuisement naturel ; les deux du hameau restent
  permises selon le lieu cru. Autres classes globalement stables/en baisse :
  suspects 5 → 5, à expliquer 61 → 56, dérives 196 → 193 ; zéro plantage/usurpation.
  Coût mine inchangé : 567 recherches / 8 383 nœuds. **Six nouveaux tests verts ;
  suite unique achevée après fusion : 2 459 tests / 285 fichiers, 2 314,709 s,
  deux MiMo préexistants reproduits sur `bd45f65`, zéro erreur**. Passe avant 213
  interrompue sur instruction ; aucune seconde suite achevée. Aucun Luna,
  deux travailleurs réduits au plus, aucune clé de signature. Limites : présence
  crue comme approximation du besoin, anciennes clôtures sans trace non reconstruites.
  Bruts `C:/Users/msics/donjon/artifacts/service-224/` ;
  [rapport 224](taches/rapport-codex-224-service-non-defait.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `deliberation.py`, `echanges.py`, `planification.py`, fusionnés sans conflit textuel. Trace durable du service rendu (biens.services_rendus), filtre des gestes qui défont l'état et menager_flamme ; protection tant que le bénéficiaire est cru présent ou porteur, sans délai ni entretien. Cas réel : torche de Brune conservée. Compteur brut des états payés perdus 6 → 6 (il compte aussi l'épuisement naturel du combustible) ; retours suspects 5 → 5. Fichiers de code communs depuis la base (planification, echanges, deliberation) : suite complète relancée sur la fusion.

- Branche `codex-ou-est-il`, fusionnée, lot **221**, départ `4fe33ef` :
  question commune de localisation à un tiers cru présent, réponse fondée sur
  les seules croyances datées du témoin ; même contenu typé pour le joueur.
  Réponses positives/négatives retenues hors des quarante souvenirs, selon les
  indices persistants 37/69, sans réessai par délai. Extension du mécanisme des
  refus et de la validation des sauvegardes autorisée par le superviseur ;
  fonctions des lots voisins intactes. Registre suivi par `esprits.croire` :
  seuls de vrais changements de lieu perçus renouvellent le contexte, pas
  les cases, délais, confirmations ou bruits non attribués. Origine conservée
  dans les relais ; une indication plus ancienne qu'une recherche infructueuse
  ne rouvre pas le lieu. Capture auberge 42 à 500 : **11 → 3 questions**,
  aucune réponse encore tenue réexécutée, mêmes monde/rendu et laps rechargés.
  **38 reprises finales vertes, 18 nouveaux tests**.
  Intégration `bd45f65` (213/219) fusionnée dans `813d45b` : seul conflit
  documentaire, aucun conflit de code ; **38/38 ciblés verts en 49,729 s**.
  Banc final cinq scénarios × quatre graines × 4 h, classes **219** :
  suspects **0/1/2/2/0 → 0/1/2/2/0** (Relais/Mine/Auberge/Crue/Hameau),
  **critère satisfait partout** ; cinq épisodes intégralement identiques à la
  référence, aucune nouvelle répétition suspecte issue des questions.
  **22 questions**, zéro plantage/usurpation. Un trio répété au hameau 42 :
  Gorm → Maël sur Aubin, refus sociaux réarmés par rancune perçue **0 → 14**,
  sans délai ; limite : un changement défavorable des axes permet aussi le réessai.
  Préemptions **53 → 67**,
  entrées à expliquer **61 → 69**, cycles accomplis **468 → 501**.
  Attente urgente crue **196,25 → 218,75**, hameau **97,50 → 87,50** ;
  S Relais **9,50 → 12**, hameau **31 → 40,50**, auberge en baisse.
  La réserve historique 199 sur la base antérieure est remplacée par ce contrôle
  classé 219 ; aucune amélioration uniforme d'attente ou de richesse garantie.
  Capture 215 testée par `rejoindre` ; ses dix minutes inchangées ne déclenchent
  pas la question (P1 reste distinct).
  Suite unique **2 444 tests / 283 fichiers**, sept échecs bruts, zéro erreur,
  16 ignorés, **3 166,835 s** ; cinq fichiers verts sur la base (20 tests),
  puis 38 reprises vertes après correctif, migration N3/N9 et oracles explicités.
  Aucune seconde suite complète ; aucun Luna, commits non signés. Bruts
  `C:/Users/msics/donjon/artifacts/ou-est-221/` ;
  [rapport 221](taches/rapport-codex-221-ou-est-il.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `planification.py`, fusionnés sans conflit textuel. Question commune au tiers présent, réponse d'après ses seules croyances (ouï-dire daté), indication démentie retenue selon sa cause ; même question pour le joueur. Sur bd45f65 : répétitions suspectes inchangées partout, préemptions 53 → 67, à expliquer 61 → 69 ; 17 questions sur 20 nuits. Fichiers de code communs depuis la base (deliberation, planification, echanges) : suite complète relancée sur la fusion.

- **Branche `codex-secours-acquitte`, fusionnée**, lot **223** : départ
  `395834b`, puis intégration 213 `bd45f65` fusionnée sans conflit. Lecture
  `protection` pure ; acquittement sur constat dans `reagir`, appel non élucidé
  sans trajet vers un danger connu. Captures 022/026 : retours effectifs **1→0**
  chacune sur une minute ; coups **24→24 / 15→20**, combat toujours possible.
  Autre protecteur/scénario, monde/rendus et laps découpés rechargés identiques.
  **63 ciblés finaux verts** ; **24 paires 4 h** contre `bd45f65`, chroniques,
  mesures, états et audits **24/24 identiques**, classes 219 **5 suspects,
  58 préemptions, 566 cycles, 68 à expliquer** inchangées, zéro plantage/usurpation,
  coups **0→0**, appels **9→9**. Références manquantes cachées une fois.
  Suite unique initiale **2 446 tests / 284 fichiers, 2 239,365 s** : deux MiMo
  historiques, une erreur Windows TUI repassée verte ; suite lancée avant fusion
  et dernière correction de publication, ciblés/banc sur l'arbre final, pas de
  seconde suite (code disjoint de 213). **Limite : raccord automatique des appels
  joueur non établi dans ce périmètre** ; aucune garantie universelle des boucles
  ni baisse de violence. Deux travailleurs réduits au plus, créneau dépassé,
  aucun Luna, pas de clé Git de signature. Bruts
  `C:/Users/msics/donjon/artifacts/secours-223/` ;
  [rapport 223](taches/rapport-codex-223-secours-acquitte.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Captures 022/026 du lot 222 : retour de Gorm vers le danger connu 1 → 0, acquittement sur constat ; un appel non élucidé ne mène plus vers un lieu connu dangereux. 24 paires 4 h (avec rixe) identiques à bd45f65, aucune alerte nouvelle. Le joueur garde le choix de ses gestes.

- **Branche `codex-contrat-engagement`, fusionnée**, lot **213 / 196 c** :
  **lot terminé, limites explicites**. `cca5f50` vérifié ; 211 puis
  `3aa16f7` (219) intégrés ; moteur final **`5016c87`**. Raccord `pnj.py` autorisé :
  `refus_etape` commun au choix et à `agir`, sans lecture réelle supplémentaire ;
  seuls ces deux noms changent dans pnj, `_abriter`/témoins et localisation crue intacts.
  Plan vide/hors de vue, attente sans geste périmé, délégation payée, tête de moyens
  revalidée, palier absolu `PERIL_EAU` et marge `INERTIE + VOL/4` ; aucun coût passé.
  Sept écarts initiaux corrigés, assertions gardées, prémisses listées au rapport.
  **Suite finale : 2 448 tests / 283 fichiers, deux Mimo préexistants, zéro erreur**,
  après 48 ciblés verts ; recharges monde/rendu/scène et laps découpés contrôlés.
  **20 paires 4 h, vingt références en cache : suspects 13 → 5**, aucun scénario
  en hausse ; cycles 486 → 468, préemptions légitimes 57 → 53, autrui 1 → 0,
  progrès 0 → 0, à expliquer 97 → 61 ; dérives 185 → 196, états payés perdus 7 → 6.
  Zéro plantage/usurpation. Hameau 42 après raccord : eau totale 120 → 5 PNJ·min,
  ancien séjour de Brune 110 min supprimé. Eau moyenne crue 2,5 → 1,25, hameau
  10 → 6,25 ; attente crue 178,75 → 196,25, hameau 128,75 → 97,5.
  Restent cinq suspects, des alertes d'agenda distribuées en crue 1985 et une
  attente confiée de Gorm au Relais 42 ; aucune garantie générale d'absence de boucle.
  **Arbitrage utilisateur validé (version testée)** : un agenda sans plan admissible
  au coût passe en sommeil et libère son palier (A4) ; reprise sur croyance ou moyen
  nouveau, jamais par le délai seul. Aucun code changé depuis les vérifications.
  Sources anciennes sans demande persistante : garantie générale encore limitée.
  **218 non couvert entièrement** : une reconstruction forcée peut perdre la
  suspension temporaire de charge ; le cas Gorm qui reverrouille sa réserve reste
  au 218. Conserver les étapes du plan ne porte pas cette suspension indépendamment.
  Aucun Luna, deux travailleurs réduits au plus, aucune clé de signature.
  Bruts `C:/Users/msics/donjon/artifacts/engagement-213/` ;
  [rapport 213](taches/rapport-codex-213-contrat-engagement.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Répétitions suspectes 13 → 5 (Relais 3 → 0, hameau 5 → 0), à expliquer 97 → 61, préemptions légitimes conservées ; inertie INERTIE + VOL/4 sans coût passé (revue 217) ; agenda sans plan admissible en sommeil, palier libéré ; refus_etape commun au choix et à l'exécution, PERIL_EAU absolu (hameau 42 : eau 120 → 5 PNJ·min). Attente crue 178,75 → 196,25. Suspension temporaire d'une charge laissée au lot 218.

- **Branche `codex-anselme-coups`, fusionnée**, lot **222**, diagnostic seul : quatre nuits natives 2024 sur `4d4c625` / `fa330e1`, historiques identiques à 212 ; Anselme **11→2 alternances**, poêle/garde **10→0**, aucun suspect 219 ; crue **16 coups / 7 touchés → 0**, mais cycle fuite/secours de Gorm encore reproduit sur captures dans les deux versions (cri de Brune non acquitté, cinq retours). Petit lot distinct sur revalidation/acquittement du secours ; pas de défaut chaleur/abri établi ni de correction générale attribuée au 213. **221 captures** monde/rendus rechargés identiques, quatre reprises bloc/découpées identiques ; un seul calcul BelowNormal, aucun jeu ni Luna modifié. Bruts `C:/Users/msics/donjon/artifacts/anselme-coups-222/` ; [rapport 222](taches/rapport-codex-222-anselme-coups.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement. Anselme : entretien du poêle et garde légitimes (préemption, plan vide après réussite), 10 → 0 alternance poêle/garde sur l'intégration. Coups : décisions locales justifiées (prise de moyen de Brune, protection de Gorm, ripostes), mais Gorm refait cinq fois l'aller-retour vers un ancien cri de secours non acquitté : petit lot distinct (secours réévalué et acquitté sur constat).

- **Branche `codex-bourse-redemandee`, fusionnée**, lot **220**, base
  `fb2dd65` vérifiée : restitution retenue durablement par `biens`, possession
  constatée à la clôture du prêt, même garde dans le graphe et l'échange,
  joueur compris ; aucun délai ni cas de scénario. La capture historique
  mine 1985 sur `4d4c625` reproduit les demandes dès 288 ; reprise de la boucle
  engagée à 290 avec la branche : retour à 290, puis aucune demande Mathe/Rémy
  jusqu'à 305, bourse chez Rémy ; temps en bloc/découpé et monde/rendu rechargés
  identiques. La base actuelle ne reproduit déjà plus cette naissance : Odon
  prend la bourse à 287 et refuse sa restitution. **20 paires 4 h : chroniques
  20/20 identiques**, audits 20/20 identiques, états 19/20 : hameau 7 ne diffère
  que par la mémoire du retour de la torche Brune/Sève (empreinte sans ce champ
  exactement égale à la référence). Zéro plantage/usurpation,
  alertes et S/F/D inchangés, 199 **16/144/494**. Mine 1985 branche **12 h** :
  138 échanges, 47 demandes, aucune demande de bourse Mathe/Rémy, zéro
  plantage/usurpation, 199 **0/21/63**, trois `fige_presse`, cinq `noir_long`.
  **35 ciblés distincts verts**, dont cinq nouveaux ; suite unique **2 437 tests /
  283 fichiers, 1 980,589 s**, zéro erreur, deux MiMo `6 != 5` reproduits sur
  `fb2dd65`, aucune seconde suite. Deux travailleurs réduits au plus ; vérification
  au-delà du créneau. Borne du prix nul admise dans le nouveau schéma après la
  suite ; cinq ciblés repassés verts, décisions mesurées inchangées.
  Aucun Luna ni fichier interdit modifié, aucune clé de signature Git.
  Bruts `C:/Users/msics/donjon/artifacts/bourse-220/` ;
  [rapport 220](taches/rapport-codex-220-bourse-redemandee.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Restitution retenue avec les entrées du prêt (biens.clore, Vue.refuse, echanges.demander), levée par un besoin, un moyen, des fonds ou un prix nouveaux, jamais par le temps. Capture historique 290→305 : plus de redemande de Mathe/Rémy ; sur la base actuelle la boucle ne naissait déjà plus. 20/20 chroniques identiques, 19/20 empreintes (nouveau champ), suite 2 437 tests verte hors MiMo.

- **Branche `codex-audit-transitions`, fusionnée**, lot **219**, base
  `50de3c2` vérifiée : outils seulement, aucun `donjon/` ni Luna modifié.
  Retours classés par preuve ordonnée, paliers effectivement essayés, étapes
  exécutées et fin survenue pendant l'action d'autrui ; dérives et pertes
  d'état payé séparées. Suivi des services conservé après éviction du souvenir,
  aucune durée convenue inventée ni violation imputée. **25 ciblés verts** et
  deux reprises courtes vertes ; **20/20 nuits 4 h identiques** aux témoins sans
  sonde (monde complet, chroniques, empreintes, mesures), témoins réutilisés.
  Courant : **486 cycles, 57 préemptions, 0 progrès, 1 autrui, 13 suspects,
  97 à expliquer**, 185 fenêtres de dérive et 7 états payés perdus.
  **57 historiques 209 : 50 suspects / 5 préemptions / 2 à expliquer** ; les
  21 secours/rondes donnent **16/4/1**. Cas exact 217 torche **7–8 min** reproduit
  sur `8177959`, 458 événements identiques, monde et rendu rechargés.
  **Garantie causale générale non établie**, prédicats hérités et observation
  partielle ; aucun comportement moteur corrigé. Pas de clé de signature
  configurée. Bruts `C:/Users/msics/donjon/artifacts/transitions-219/` ;
  [rapport 219](taches/rapport-codex-219-audit-transitions.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Outils seulement. Une règle classe chaque retour : cycle accompli, palier supérieur, satisfaction par autrui, progression observée, répétition suspecte, à expliquer ; dérives ouvertes et états payés perdus à part. Les 57 cas de 209 : 50 suspects, 5 préemptions, 2 à expliquer. Intégration actuelle, 20 nuits 4 h : 13 suspects, 57 préemptions, 7 états payés perdus ; 20/20 nuits identiques avec et sans sonde.

- Branche `codex-sait-observations`, **non fusionnée, en attente**, lot **206** (`820762d`) : `social.bavarder` ne lit plus le savoir réel de l'auditeur, seulement les paroles, audiences et observations communes du locuteur. Juste, mais **les PNJ se redisent tout** : confidences crue 56 → 334, hameau 74 → 385, répétitions 2 → 23, demandes en boucle 0 → 26 (Brune → Gorm, crue 1985 : 54 confirmations, souvent des hauteurs d'eau successives) ; suite 14 échecs. Reprise à concevoir : ne dire que ce qui est nouveau **et pertinent** pour l'auditeur, et tenir pour commune une observation de l'environnement partagé (une eau vue ensemble), sans lecture privée. [Rapport 206](taches/rapport-codex-206-sait-observations.md) sur la branche ; bruts `artifacts/sait-206/`.
  **Reprise 206 b (`0ba27d3`), toujours en attente** : `social._auditeur` décide avec les seules croyances du locuteur. Confidences 27/104/48/49/92 → 6/12/6/6/27 (Relais/mine/auberge/crue/hameau) et avertissements redits 6 → 0, mais 13 échecs et une erreur introduits, suspects 4 → 5, deux boucles nouvelles (Mireille/Mathurine auberge 2024, agenda de Brune au hameau 2024) : non fusionnable en l'état ; la baisse des confidences appauvrit aussi les échanges. Décision à l'utilisateur.
  **Reprise 235 (`codex-sait-observations-c`, `942a3c2`), en attente** : `social._utile` relie la nouvelle aux biens, portages, intentions perçues, engagements et supports crus de l'auditeur. Confidences Relais/mine/auberge/crue/hameau 25/101/47/65/62 → 5/10/7/50/47 (mine et Relais non restaurées), S mine 26,75 → 23, suspects 2 → 4 (Aubin/Ilse Relais 2024, Mireille/Mathurine auberge 2024), suite : 13 échecs (huit écarts non résolus). Non fusionnable en l'état.

- **Vérification d’intégration 4d4c625**, lot **212**, branche `codex-verif-integ-4d4c625`, base documentaire `a49c31e` : **49/49 nuits achevées**, code `donjon/`/`tools/` identique à `4d4c625`, aucun Luna, référence rejouée ou suite complète ; deux calculs au plus, en fond à priorité réduite. Zéro plantage, violation d’état, usurpation, mort relevée ou écart VERIFIER/spatial 0,2 ; cinq contrôles complets de 8 h, zéro borne (Lucien auberge 42/314 non reproduit). **16 coups, sept touchés**, crue 2024 à 672–691, Gorm finit inconscient. Hameau : attente **750 → 1 021,25**, noir **268,75 → 575**, pire passage **40 → 39/h** (1985 : **40 → 28**). Compteur 199 actif : **338 suspects**, garantie générale non établie ; boucle de prêts de la bourse mine 1985 (Mathe 97 demandes, Rémy 100) absente de ses suspects, et alternance poêle/garde d’Anselme auberge 2024 à instruire par les contrats communs, ancienneté même nuit indéterminable avec le seul rapport 174. **117 repas d’empathie**, 40 projets de pièces (un marqué atteint), 12 récupérations nées (huit fins sur retour cru, reprises autonomes non certifiées) ; aucun départ définitif relevé. Pas de monde/rendu certifié après recharge ; aucun correctif. Bruts, scripts, lecture de pile et manifeste des 49 archives exclusivement `C:/Users/msics/donjon/artifacts/verif-integ-4d4c625/` ; [rapport 212](taches/rapport-codex-212-verif-integ.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rapport seulement. 49 nuits, zéro plantage, violation, usurpation, mort ou écart VERIFIER/spatial ; richesse S/F/D en hausse dans les quatre scénarios, sans recours en forte baisse ; attente crue et noir Relais/crue en hausse. Petits lots désignés : boucle de la bourse Mathe/Rémy (mine 1985 dès 288, 97 et 100 demandes), alternances poêle/garde d'Anselme (auberge 2024 dès 200), 16 coups en crue 2024 672-691.

- **Branche `codex-racheter-bien`, fusionnée**, lot **214**, base `cca5f50`,
  code `2b47bd9` : le geste d'achat commun permet au propriétaire de racheter
  son bien au détenteur. Rétention et vente jugées au prix de faute d'honnêteté
  existant ; accueil, utilité, budget, paiement, remise et refus communs.
  La réclamation passe avant le rachat ; le prix et le poids du projet bornent
  ce recours, aucun plafond d'agenda changé. **29 ciblés finaux verts**, dont
  sept nouveaux ; ballot et marteau rachetés autonomement en scènes d'auteur
  (estimation initiale 70, revente 7), monde/rendu et temps découpé identiques.
  Joueur acheteur par sa parole existante ; joueur vendeur hors lot selon
  l'instruction de repli du superviseur, car son acceptation actuelle ne couvre
  que les missions déclarées. Aucun nouveau parcours ni raccord moteur/dialogue.
  Suite unique **2 429 tests / 281 fichiers verte**, zéro échec/erreur,
  16 ignorés, 3 580,295 s ; banc exact `cca5f50` / `2b47bd9` : **20 paires 4 h,
  20 chroniques et états complets identiques**, zéro plantage/usurpation,
  compteur 199 **24/204/510** inchangé, aucune nouvelle alerte. Aucune naissance
  de récupération naturelle ; réclamations de biens/rachats/reprises **0 → 0**,
  S/F/D inchangés. Coût mine 4 h identique : **870 recherches, 10 624 nœuds**.
  Bois du guet en scène équivalente : refus raisonné (**5,944 > 1,857432**),
  reste à Brune, projet en sommeil ; monde/rendu et laps découpés vérifiés.
  Capture historique 207 rejouée 151→240 : mêmes recharges/laps, pas de naissance
  sur cette base, bois au guet. Vérification au-delà du créneau. Aucun Luna,
  aucun fichier des lots voisins modifié, commits non signés (aucune clé).
  Bruts `C:/Users/msics/donjon/artifacts/racheter-214/` ;
  [rapport 214](taches/rapport-codex-214-racheter-bien.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rachat par le geste d'achat commun, borné par le prix et le poids du projet (bois du guet : coût 5,944 > poids 1,86, pas de rachat, refus raisonné). Preuve par scènes (ballot, marteau) ; aucun rachat naturel dans les 20 nuits, 20/20 états identiques, coût mine identique. Joueur vendeur hors lot.

- **Vérification Luna d85fb54**, lot **216**, jouée par l'orchestrateur sur le laptop (le coffre ChatGPT était illisible depuis l'agent du PC fixe) : deux passes des 34 scripts du lot 165, intégration `d85fb54` contre `cdaf371` (cache, scripts absents joués et rangés). Aucun code du jeu changé. **Appels/tour 3,21 → 2,98, s/tour 11,5 → 10,5 (médiane 9,3 → 9,0), replis 2 → 0,5, obstacles narratifs 31 → 19,5, relances 18 → 16,5, refus 25,5 → 22** ; aucune erreur technique ni de recharge. Force : traîner 2 appels/tour, enfermer 2,5 avec un refus sur quatre tours, geste improvisé encore refusé (3 refus/2 tours) ; poser au sol 4 appels/tour sans refus de destination ; comptes 4,75 appels/tour. Lecture qualitative des textes non faite saisie par saisie. [Rapport 216](taches/rapport-codex-216-verif-luna.md), bruts `C:/Users/msics/donjon/artifacts/verif-luna-d85fb54/`.
- **Revue vierge 217, lecture seule** : cinq nuits 4 h sur `8177959`, regard influencé par la lecture préalable de ce point de reprise (limite autorisée) ; continuité d'intention, contact et service utile à distinguer des seuls retours. [Rapport 217](taches/rapport-codex-217-revue-vierge-decisions.md), bruts `C:/Users/msics/donjon/artifacts/revue-217/` ; aucun jeu, outil ou test modifié.
  Fusionné sur l'intégration (rapport seulement). Retenu : engagement minimal porté par l'intention, sans majorer l'inertie du trajet déjà parcouru (transmis au lot 213) ; contact comme sous-but commun (P1 du 215) ; services payés qui portent leur durée (Brune éteint la torche payée une minute après, hameau 1985) ; réessai lié à l'obstacle plutôt qu'au délai 30/60.

- **Lot 215, diagnostic seul**, `codex-richesse-crue`, départ `3e86d1f` vérifié : huit nuits crue/hameau 4 h identiques à `d2243c2`, références `ef86cab`/`aadab7c` réemployées ; contre avant 211, signatures perdues/gagnées crue **55/19**, hameau **71/77**, S **23→14 / 29,5→31** ; attentes attribuées aux besoins, **36 captures** monde/rendu rechargées. Manque commun de contact/recherche proposé en priorité ; routes dangereuses, cloche déléguée et rondes satisfaites à conserver ; causalité distante de chaque texte non isolée, aucun gain garanti. Aucun jeu/Luna modifié, un calcul réduit à la fois ; bruts `C:/Users/msics/donjon/artifacts/richesse-215/`, [rapport 215](taches/rapport-codex-215-richesse-crue.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement. Baisse S de la crue surtout juste (contacts obtenus par position réelle inconnue). Manques : P1 un contact nécessaire (abri en compagnie, enquête de ressource) sans localisation passe par la recherche/l'appel commun ; P2 demander à un tiers où est quelqu'un. Attentes restantes surtout Gorm/devoir et Brune/chaleur, contraintes justes.

- **Branche `codex-localisation-crue`, fusionnée**, lot **211**, départ
  `0b95f33` vérifié puis **reprise demandée sur `aadab7c`** (205/207), fusion
  `5a97ab3`, seul conflit documentaire. `monde.mobile_par_nature` et `_lieu_cru`
  retirent le repli réel des personnages ; aucun savoir implicite ajouté au jeu,
  aucun autre changement de production contre `aadab7c`. Trois graines 209,
  t=753/1034, douze variantes monde/rendu rechargées ; cas Ilse/Aubin et autre
  PNJ/auberge, savoir déclaré, fixe/mobile, porteur inconnu, temps découpé.
  **15 ciblés verts** sur la fusion ; vérification de l'intention persistée et
  de la non-perception renforcée avant exécution dans la suite finale.
  **20 paires × 4 h**, référence exacte en cache : **24 → 16 retours**
  (Relais 0→4, mine 1→1, auberge 5→2, crue 9→2, hameau 9→7), zéro
  plantage/usurpation. Aucune nouvelle alerte de répétition/alternance, mais
  **absence de boucle nouvelle non validée** : quatre retours de secours/ronde
  au Relais, causalité détaillée non établie ; deux observations d'attente.
  Attente urgente crue 102,5→178,75, hameau 111,25→128,75 PNJ·min ; sans recours
  crue 27,5→0. **Réserve avant intégration**, aucun élargissement à 196 c.
  Suite finale unique sur `aadab7c` : **2 425 tests / 281 fichiers, 2 128 s,
  quatre échecs et une erreur bruts** ; six reprises vertes après observation
  du test d'abri, contre-épreuve sur une case valide et oracle du rejeu.
  **Deux MiMo préexistants restent, zéro erreur consolidée** ; aucune seconde
  suite sur cette base. Première base archivée (2 404/13, 15 reprises vertes).
  Le test d'eau passe après 205 ; Aubin nourri à 4 min, rotations reconnues
  et état réel remplacent les anciens oracles textuels de part/rejeu.
  Aucun Luna, deux travailleurs réduits au plus. Bruts
  `C:/Users/msics/donjon/artifacts/localisation-211/`, finaux dans `aadab7c/` ;
  [rapport 211](taches/rapport-codex-211-localisation-crue.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Retours suspects 24 → 16 (crue 9 → 2, auberge 5 → 2, hameau 9 → 7) mais Relais 0 → 4 (secours interrompus, transmis au lot 213) ; crue S 23 → 14 (proches retrouvés par une connaissance indue), attente crue 102,5 → 178,75, sans recours crue 27,5 → 0. Suite de la branche sur aadab7c : deux MiMo seulement.

- **Branche `codex-evacuation-juge`, fusionnée**, lot **205 / 196 b**,
  départ `71bb01d`, reprise demandée sur **`ef86cab` (204 intégré)** : péril
  indépendant du plan, certificat de transit, repli vers moins d’eau, abri commun
  au choix et au séjour, cible tenue jusqu’à l’accomplissement. Seul raccord
  autorisé : `pnj._abriter` ; `_lieu_cru`/`salle_crue` intacts (autre lot).
  Quatre états réels issus de **209** en fixtures (Aubin/Ilse/Gorm et cible d’Ilse),
  monde/rendu rechargés et laps découpés ; **157 ciblés consolidés verts**.
  Suite finale : **2 410 tests / 279 fichiers, 9 échecs bruts, zéro erreur** ;
  après scènes explicitées et ciblés, restent les **deux MiMo préexistants**
  reproduits sur la base exacte. Une seule passe par base, seconde demandée après 204.
  Contrôle crue 1985 2 h `VERIFIER` et spatial 0,2 vert. **20 paires finales 4 h** :
  suspects Relais **0 → 0**, mine **1 → 1**, auberge **5 → 5**, crue **27 → 9**,
  hameau **24 → 9**, total **57 → 24**, zéro plantage/usurpation. Eau en crue
  **13,75 → 7,5**, hameau **13,75 → 2,5 PNJ·min** en moyenne.
  **Critères non validés** : seulement **7/12 empreintes 2 h identiques** ;
  agenda a1 de Brune hameau 2024 réactivé/endormi huit fois, nouvelles répétitions,
  attente urgente **27,5 → 111,25 PNJ·min** au hameau. Aucune garantie générale
  contre les boucles ; contrat complet 196 c distinct, localisation crue non traitée.
  Aucun Luna, deux calculs réduits au plus, commit non signé ; bruts exclusivement
  `C:/Users/msics/donjon/artifacts/evacuation-205/` ;
  [rapport 205](taches/rapport-codex-205-evacuation-juge.md). **À revoir avant fusion.**
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Retours suspects 57 → 24 (crue 27 → 9, hameau 24 → 9), eau crue 13,75 → 7,5 et hameau 13,75 → 2,5 PNJ·min ; en contrepartie attente urgente crue 77,5 → 102,5 et hameau 27,5 → 111,25, sans recours crue 15 → 27,5, Brune hameau 2024 active/endort son agenda huit fois, Gorm 125 min sans but : à reprendre dans 196 c. Abris hors crue aussi changés (7/12 empreintes 2 h identiques). Suite complète sur les fusions 207 et 205 (`tools/tests.py --processus 2`, `aadab7c`) : **2 422 tests, 16 ignorés**, verte (3 287,6 s).

- **Branche `codex-reclamer-vol`, fusionnée**, lot **207**, base `c6c2de6` :
  recours typé `reclamer` avant la recherche de reprise, porteur/danger/présence
  crus, pas de peur ni d'inconscience crue ; demande au joueur sans remise imposée.
  Décision commune de rétention illégitime : honnêteté, relation, valeur et utilité,
  permission du prêt conservée ; rendu ciblé de `paroles._reclamer` **autorisé**.
  Dix tests nouveaux verts : deux restitutions autonomes, refus puis reprise,
  violence contrôlée, joueur libre, exclusions, temps découpé, monde/rendu rechargés.
  Cas historique 200 reproduit sur 9904574 : naissance 152, atteint 228 ;
  sa capture à 151 rejouée : Gorm réclame à 213, Brune refuse par rancune,
  projet en sommeil faute de moyen admissible ; 89 min entières/découpées,
  monde/rendu et recharges identiques. Base actuelle : aucune naissance.
  Banc 20 paires 4 h, références a488f1f en cache (code identique) : zéro
  plantage/usurpation, 20 chroniques identiques, avis **57/272/563** inchangés,
  S/F/D inchangés ; aucune récupération naturelle, aucun gain de richesse démontré.
  Suite unique : **2 411 tests / 279 fichiers, 3 117,025 s**, sept assertions en
  échec, zéro erreur, 16 ignorés. Dix reprises finales vertes après adaptation
  des oracles (portage suivi du refus ; réception d'accusation isolée du recours
  prioritaire) ; **seul `test_rondes_resumees` reste en échec, reproduit sur c6c2de6**.
  Aucune seconde suite ; clé de signature absente, livraison non signée sur la branche ;
  [rapport 207](taches/rapport-codex-207-reclamer-vol.md).
  Bruts `C:/Users/msics/donjon/artifacts/reclamer-207/`, aucun Luna, deux travailleurs réduits au plus.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Réclamation par la parole commune reclamer, recours hors recherche avant la reprise ; rendu des refus de reclamer par cause (paroles.py, autorisé). Aucune réclamation naturelle dans les 20 nuits 4 h (aucune naissance de récupération sur cette base) : preuve par scènes et capture historique ; compteur 199 identique (57).

- **Lot 210, mesure seule**, `codex-mesure-saillance`, base `0aa41b3`, fusionnée : filtre expérimental des moyens agissables dans `tools/` ; 46 nuits séquentielles à priorité réduite, aucun `donjon/`/Luna modifié. Nœuds 12 h −94/79/86 % (mine/auberge/hameau), mais plan lumière avant crochetage perdu ; 4 h × cinq scénarios × quatre graines : nœuds −54 %, blocage 0 → 150, attente 620 → 2 885 min·PNJ ; hameau 12 h, suspects 13 → 32. 853 choix entiers S/REFERENCE échantillonnés, sept plans perdus sur 482 recherches communes ; Odile 75 min, surcoût +3,644 minutes modèle au rejeu. Six tests courts, deux témoins strictement identiques, 46 recharges JSON et neuf scènes disque/laps découpés verts. **Ne pas implémenter cette règle en l'état** ; filtre encore borné aux agissables, pas de garantie uniforme sur les flammes auxiliaires/devis. Bruts `C:/Users/msics/donjon/artifacts/saillance-210/` ; [rapport 210](taches/rapport-codex-210-mesure-saillance.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Sonde et rapport seulement. Nœuds −54 % sur 4 h (−79 à −94 % sur 12 h), mais attente 620 → 2 885 min·PNJ, blocage 0 → 150, hameau plus de retours, préparatif émergent (lumière avant crochetage) perdu, Odile oublie sa réserve : règle déconseillée en l'état ; préalables d'implémentation dans le rapport.

- **Lot 209, diagnostic seul**, `codex-retours-restants`, base `78ba505` : 57 retours reproduits (Relais 0, mine 1, auberge 5, crue 27, hameau 24), inventaire exhaustif attribué ; 25 évacuations à 205, 7 arbitrages d'abri à 205/196 c, 21 secours/rondes à examiner par le contrat complet de 196 c ; hors des deux : 3 localisations réelles lues sans croyance et une livraison interrompue par sa propre remise sous clé, deux petits lots proposés. Cas 208 rejoués : Ilse conserve la faim connue de Brune, Aubin perd le péril dès l'adoption du plan. Douze nuits réinstrumentées identiques, 35 captures monde/rendu rechargées ; aucun jeu modifié, aucun Luna, un calcul réduit à la fois ; bruts `C:/Users/msics/donjon/artifacts/retours-209/`, [rapport 209](taches/rapport-codex-209-retours-restants.md). Aucune garantie générale ni baisse future certifiée.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Rapport seulement. 57 retours attribués : eau 25 et cibles d'abri 7 (lot 205, abri aussi 196 c), secours/rondes 21 (196 c), localisation crue d'un personnage lue sur sa position réelle 3 (lot à créer), restauration d'une charge suspendue 1 (lot à créer).

- Branche `codex-pas-compagnons`, **non fusionnée, en attente de 196 c et du diagnostic 209**, lot **195** (`4968e54`, reprise sur `ef86cab`) : dans `ouie.py`, un pas compatible avec la marche possible d'un compagnon cru là s'explique sans retournement ni bruit inconnu, sans confirmer sa position. Retournements Relais 100 → 28,75, hameau 134,5 → 78,5 ; retours suspects 57 → 54 au total mais hameau **24 → 35** et un retour nouveau au Relais 2024 (Gorm sert Ilse, abandonne, reprend, sans entrée nouvelle) ; trois tests rouges (abri d'Ilse, deux prêts). Arbitrage commun du contrat d'engagement (196 c) attendu avant reprise. [Rapport 195](taches/rapport-codex-195-pas-compagnons.md) sur la branche ; bruts `artifacts/pas-195/`.
  **Reprise finale (`cf777e7`, sur 346c1aa), toujours en attente** : ouïe des compagnons plus preuve d'accomplissement dans `echanges.tenu` (souvenir `suivi_engagement`). 20 paires 4 h : suspects 5 → 1, retournements divisés par deux à quatre ; mais hameau S 40,5 → 27 (échanges acceptés 16 → 9, demandes −28, offres −10, promesses −10 : interactions nées de perceptions fortuites), mine S 26,25 → 24, auberge 10,25 → 8,25 ; à expliquer 67 → 77. Suite 2 497 tests, cinq échecs : quatre préexistants et un défaut de placement révélé (`signes.place` : attitude périmée qui bloque l'abri d'Ilse), lot séparé proposé. Décision à l'utilisateur : moins de retournements contre moins d'interactions au hameau.
  **Reprise 233 (`codex-pas-compagnons-c`), non fusionnée** : baisse de richesse acceptée par décision du 2026-10-28 ; rencontres fortuites non légitimes. Après merge de l'intégration `01ce467`, cinq écarts d'oracles/prémisses repris sur preuves, placement conservé pour 234. Retour d'Aubin crue 2024 justifié comme autre moyen après refus, sans nouveau réveil au retour. Suite de reprise et détails : voir l'entrée 233 et son rapport actualisés en tête de ce document.

- **Lot 208, diagnostic seul**, `codex-cout-ceder-outil`, `1a3359a` contre `74a4bc4` : surcoût mine reproduit, recherches 698 → 987, nœuds 6 684 → 10 558 ; 89,4 % des nœuds en plus dans les devis de fermeture d'Odon/Rémy, recours négatifs répétés après auto-refus d'outils. Poêle et trois retours de crue reproduits, ancien écart de lanterne non reproduit (fichier ciblé vert sur les deux commits). Réutilisation des recours négatifs proposée, gain non garanti ; 202 reste en attente. Aucun jeu modifié/Luna, un calcul réduit à la fois, captures monde/rendu rechargés ; bruts `C:/Users/msics/donjon/artifacts/cout-208/`, [rapport 208](taches/rapport-codex-208-cout-ceder-outil.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement. 89 % des nœuds en plus viennent de recours négatifs redemandés (Odon, Rémy : devis de fermeture) après que les PNJ ne proposent plus leurs outils ; aucun calcul de valeur dans la recherche. Petit lot proposé pour la reprise de 202 : retenir un recours sans offre acceptable tant que ses dépendances crues ne changent pas.

- **Branche `codex-portee-sans-salle`, fusionnée**, lot **204**, base
  `51c1e0b` : P1 implémenté en mode cases ; contact par pas commun au joueur,
  aux accès PNJ et à leur approche, indépendamment du secteur de la cible ;
  contenants/portes fermés et coins bloqués préservés, positions crues conservées.
  Les deux côtés d'une diagonale doivent être libres, comme pour la marche ;
  le volume de la cible ou de son support ne bloque pas son propre contact.
  État et rendu rechargés, saisie réelle torche/crochets, autre seuil/verbe,
  PNJ et temps découpé vérifiés. **88 ciblés puis 18 finaux verts** ; suite unique
  **2 385 tests / 276 fichiers, 29 échecs et six erreurs**, ramenés après
  corrections et adaptations vérifiées à **trois échecs préexistants reproduits
  sur la base** (deux MiMo, AST du compteur 199), zéro erreur ; pas de seconde
  suite complète. Empreintes 2 h : **6/16 identiques**, dix écarts de comportement,
  zéro plantage ; références exactes en cache, ancien `main` incompatible avec
  la sonde actuelle. **VERIFIER + spatial.VERIFICATION 0,2**, Relais 1985 2 h : vert.
  Banc final 4 h, 16 paires : zéro plantage/constat d'usurpation, pics de passages/h
  inchangés **10/9/18/38** ; retours suspects **275 → 380** (Relais 1→1, mine 1→2,
  auberge 2→5, crue 271→372), à expliquer **313 → 292**, cycles **469 → 463**.
  **Critère « aucune boucle nouvelle » non validé** : nouvelle alerte d'alternance
  entretien du brasero/garde de Gorm, Relais 1985 min 5 ; réserve avant intégration
  avec 201. Aucune alerte masquée ni correctif dans les fichiers de cet autre lot.
  P2/P3 et M1–M3 restent ouverts ; aucun code de 201/202 ni du MJ modifié,
  aucun Luna, deux travailleurs réduits au plus. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/portee-204/` ;
  [rapport 204](taches/rapport-codex-204-portee-sans-salle.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Banc 4 h cinq scénarios × quatre graines sur la fusion contre f746c30 : retours non justifiés 82 → 57 (hameau 48 → 24, crue 28 → 27, auberge 2 → 5, mine 3 → 1, Relais 1 → 0), aucune alternance nouvelle de Gorm ni usurpation ; la hausse du rapport venait de sa base antérieure au lot 201.

- Branche `codex-ceder-outil`, **non fusionnée**, lot **202** (`74a4bc4`) : céder un bien compte la capacité perdue (`biens.capacites_crues`, `valeur_bien`, ventes, marchés, contreparties ; prêt distinct). Lucien garde ses crochets (auberge 1, 239) ; Gaspard offre encore son briquet (sa lampe allumée compte comme autre flamme). Offres d'outils 36 → 19, acceptées 3 → 0, mais S/F/D en légère baisse (Relais, mine), crue sans recours 15 → 30, trois retours brefs nouveaux en crue 2024 ; **coût mine 4 h : nœuds +58 %, recherches +41 %** ; deux écarts de parcours propres à la branche dans la suite. **Mis en attente**, décision à l'utilisateur. [Rapport 202](taches/rapport-codex-202-ceder-outil.md) sur la branche ; bruts `artifacts/outil-202/`.

- **Branche `codex-occasions-sur-base`, fusionnée**, lot **200**, base
  `23aba63` : reprise du lot 186 sans galettes sur les projets 184/192 actuels.
  Sept scénarios, données et tests seulement, aucun moteur/Luna. Les 30 échecs
  et quatre erreurs historiques sont retrouvés ; 32 méthodes classées comme
  changements légitimes, leurs ressources/rencontres d'auteur explicitées sans
  relâcher les assertions. Les 54 inverses conservent exactement les données
  de la base actuelle, projets compris (sept empreintes indépendantes).
  **16 paires de 4 h**, référence exacte calculée une fois en cache commun :
  S/F/D Relais **6,75/4,25/1,188 → 7,75/4/1,188**, mine
  **13,25/4,75/1,214 → 15/5,25/1,321**, auberge inchangée
  **6,5/2,75/0,625**, crue **17,25/6,25/1,938 → 16,75/5/1,563**.
  Propositions/acceptées **58/15 → 71/18**, ventes **25/8 → 50/13**,
  commissions **0/0/0 → 4/0/0**, avis/adoptions **0/0 → 4/1**, services
  **3 → 3** ; projets de dette **12 → 12**, récupération naturelle **0 → 1**
  (Gorm, bois du guet pris par Brune en crue 7, projet né à 152 min et atteint
  à 228). Zéro plantage/usurpation, **24 recharges monde/rendu identiques**
  sur la branche. Alertes : `fige_presse` **4 → 3**, répétitions **2 → 0**,
  alternances **3 → 0**, appels nombreux **1 → 0**, noir long **1 → 1** ;
  bascules **3 → 1**, pire passage **46 → 50/h**. Gain non uniforme, aucune
  garantie générale contre les boucles ; compteur d'audit 199 non fusionné.
  Suite complète unique : 2 360 tests, un seul échec (contrôle AST des agendas par le détecteur 199, corrigé sur l'intégration). Bruts
  exclusivement `C:/Users/msics/donjon/artifacts/occasions-200/` ;
  [rapport 200](taches/rapport-codex-200-occasions-sur-base.md).
  Fusionné sur l'intégration : conflits de documentation et de `tests/test_ressources.py` (scène sans souci du lot 197 et stock contractuel du lot 200, réunis) ; base antérieure aux lots 197, 199 et 201 : suite complète relancée sur la fusion (`tools/tests.py --processus 2`) : **2 389 tests, 16 ignorés, deux échecs**, deux nuits réelles changées par les nouvelles données : `test_battants_brises` (crue 2024, Brune vend son bois au lieu de briser la réserve ; reprend le stock contractuel d'avant 186) et `test_banc_sans_joueur` (Gorm sert Brune par empathie avant sa demande) ; adaptés, 9 tests repris verts. Remplace le lot 186 annulé.

- **Branche `codex-reserve-brisee`, fusionnée**, lot **201 / 196 a**,
  base exacte `fffa3a2` : capacité commune de fermeture sur fin crue/constatée/
  simulée, constats vue/essai cohérents, verrou démenti aussi pour le joueur
  (schéma sauvegardé inclus), garde du plan sans auto-exclusion de sa pulsion.
  **22 ciblés verts**, cas réel crue 2024 et contenant de la mine, monde/rendu
  rechargés, laps entier/découpé. **20 paires de 4 h** : suspects Relais
  **1 → 1**, mine **1 → 1**, auberge **2 → 2**, crue **271 → 19**, hameau
  **16 → 17** ; crue 2024 **253 → 1**, boucle réserve/garde supprimée.
  La base actuelle ne reproduit plus l'effraction des graines 7/42 ; en 2024,
  elle survient à 45 min. **Critère aucun scénario en hausse non atteint** :
  hameau 7, retours d'abri **5 → 6** ; attribution unique non établie par trois
  contre-épreuves. Nouvelle observation `fige_presse` de Gorm sur devoir confié.
  Aucune garantie générale sur les avis/abris. Crue 7, 2 h, `VERIFIER` et
  `spatial.VERIFICATION=0,2` : zéro écart, borne, plantage. Suite unique :
  **2 385 tests / 276 fichiers, 1 803,701 s, trois échecs, zéro erreur** ; les
  deux MiMo `6 != 5` et le contrôle AST des accès aux agendas du détecteur 199
  sont reproduits sur la base exacte. Huit nouveaux tests repris verts avec
  le texte public ; reprise de la capture de base à 45 min et six recharges
  identiques (monde/rendu), sans retour à la fermeture. Aucune clé de signature
  configurée, commit non signé.
  Aucun Luna, deux travailleurs réduits au plus ; bruts exclusivement
  `C:/Users/msics/donjon/artifacts/reserve-201/` ;
  [rapport 201](taches/rapport-codex-201-reserve-brisee.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Compteur 199, 20 paires 4 h contre la base exacte : crue 271 → 19 retours non justifiés (crue 2024 253 → 1, boucle réserve/garde de Gorm disparue), total 291 → 40 ; hameau 16 → 17 sans attribution causale établie. VERIFIER + spatial 0,2 crue 7 2 h sans écart. Le troisième échec de sa suite (contrôle AST des agendas par le détecteur 199) est corrigé sur l'intégration.

- **Lot 203, diagnostic seul**, `codex-capacites-salle`, base `2fe05b9` : portée manuelle encore bornée au secteur (deux cas au seuil ouvert, état et rendu rechargés), contexte social PNJ et projections MJ recensés ; lots P1–P3 proposés, MJ gelé séparé, aucune garantie générale ni modification du jeu, aucun Luna ; un processus réduit, bruts `C:/Users/msics/donjon/artifacts/capacites-203/`, [rapport 203](taches/rapport-codex-203-capacites-salle.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Rapport seulement. P1 : la portée manuelle (spatial.proche, monde.present_physique/accessible, pnj._accessible) reste bornée à la salle de l'acteur, contrairement au contact entre personnages (refus « Approche-toi » au seuil ouvert, reproduit). P2 : contexte social des PNJ (de_pres, autour) borné à la salle. P3 : zone de calme de l'atelier. M1 à M3 côté MJ, en veille.

- **Branche `codex-garantie-avis`, fusionnée**, lot **199 / 196d**,
  base `0fb5a07` : mesure déterministe des retours de décision dans l'audit
  des nuits et le comparateur, mode empreintes compris ; comptes par PNJ,
  décisions/minutes/classes et alertes dès un retour suspect. Les entrées
  changées restent **à expliquer**, les archives sans sonde **non mesurées**.
  **Garantie générale non établie** (`certification_complete=False`) : aucun
  certificat moteur de démenti/palier/marge, moyens sous un même but et retours
  > 60 min hors observation. **20 nuits de 4 h**, cinq scénarios × quatre
  graines : **385 suspects, 315 à expliquer, 530 accomplis** ; Relais/mine/
  auberge zéro suspect, crue **367**, hameau **18**. **20/20 identités** avec/
  sans sonde (état complet, chronique, mesures, empreintes, récit, souvenirs),
  vingt états/empreintes identiques aux bruts 196 malgré ses classes différentes.
  Temps appariés **590,37 / 590,15 s** : surcoût non distinguable du bruit.
  Trois cas 196 relus et six captures en fixtures ; aucun fichier de `donjon/`,
  aucun Luna. **33 ciblés finaux verts**, écriture de l'audit, modes du comparateur,
  sauvegarde/recharge et rendu compris. Suite unique : **2 343 tests, 271 fichiers,
  31 échecs, quatre erreurs, 16 ignorés** ; deux fragments (41 + 230), sans rejouer
  les fichiers terminés. Les **35 incidents sont reproduits sur la base exacte**
  (33 méthodes, 26 fichiers, mêmes identifiants et catégories) ; suite générale
  non verte, outils modifiés verts. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/garantie-199/` ;
  [rapport 199](taches/rapport-codex-199-garantie-avis.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Outils seulement. Départ, cinq scénarios × quatre graines × 4 h : 385 retours non justifiés (crue 367, hameau 18 ; Relais, mine, auberge 0), 315 à expliquer, 530 cycles accomplis ; 20/20 nuits identiques avec et sans sonde. Les 35 échecs de sa suite venaient du lot 186 présent dans sa base (annulé depuis). Garantie générale non établie : lots 196 a à c.

- **Lot 197 b, branche `codex-empathie`, fusionnée**, reprise de `47ac3f1`
  sur base `116294e` : triage des **34 constats** de 197 a, tableau complet dans
  le rapport. Scènes historiques précisées unitairement par des données de souci
  absent, contrats conservés ; le test de repas après appel vérifie désormais
  une demande, un repas effectivement reçu et la satiété, plutôt qu'une formulation.
  `services.conditions_manquantes` inclut le froid éprouvé du bénéficiaire dans la
  salle du foyer, avant geste ; effet réel, perception, preuve unique, charge et
  prestation convenue passent par les mêmes contrôles. Tests PNJ/joueur, doubles
  crédits et recharges verts ; peur hors lot.
  **313 ciblés dans 26 fichiers, 278,440 s : quatre échecs, zéro erreur** :
  deux MiMo historiques, plus deux régressions de références internes exposées
  par les portions créées par les secours (`test_avis_redits`, `test_combat`).
  État mécanique/chronique identiques ; références 67/68 permutées ou référence 48
  absente avant sauvegarde. **Raccord autorisé de trois lignes appliqué** dans
  `echanges.detacher_part` : installateur commun des références appelé dès la
  création, dans les deux chemins physique/compté. **Attention à la fusion avec
  le lot 198 : même fichier, seuls ces trois ajouts pour 197 b.** Aucun champ
  exclu ni secours neutralisé dans ces régressions ; comparaisons complètes vertes.
  Le test des lampes prouve aussi les deux identités/audiences : Rémy peut annoncer
  une lampe devant Lucien, que Josse n'a alors plus à répéter. **33 ciblés consolidés
  verts** sur références, combat, portions et crédit. **Suite complète unique :
  2 364 tests / 274 fichiers, 1 982,678 s : deux MiMo historiques et une erreur
  de croyance `allume` autonome après allumage utile.** Corrigée dans
  `services.constater`, qui conserve les états visibles du constat commun ;
  cas réel inchangé et allumage complémentaire après recharge : **24 ciblés verts
  / 3 fichiers, 19,304 s**. Bilan consolidé : deux MiMo historiques, zéro erreur ;
  pas de seconde suite complète ni de nouveau banc.
  Bruts `C:/Users/msics/donjon/artifacts/empathie-197/b/`, sans Luna, deux
  travailleurs réduits au plus ; [rapport et tableau](taches/rapport-codex-197-empathie.md).

- **Historique 197 a** (complété par 197 b ci-dessus), **3d partiel** :
  faim/froid perçus deviennent des conditions communes `servir`/`allume`, après
  les besoins propres et avant la routine. Seuil du souci du lot 80, rancune
  exclue ; poids empathie × (affection + 20) / 100. Peur différée, crédit du froid
  corporel sans charge encore absent du contrat commun de service.
  **Base reprise : `integration 116294e`**, après annulation des données 186 et
  fusion des lots 194/180. Le banc initial de 20 paires et la suite interrompue
  sur `9c1897f` sont obsolètes, archivés sous `empathie-197/avant-integration-9c1897f/`.
  **26 ciblés consolidés verts** : Mathe/Lucien sans charge, transi PNJ/joueur,
  exclusions, priorité propre, temps entier/découpé et monde/rendu/journal
  rechargés. **20 paires finales de 4 h**, cinq scénarios × quatre graines :
  **21 repas d'empathie dans 13 nuits**, aucun entretien spontané sous ce
  motif ; froid prouvé seulement en scènes ciblées. Sans recours **635 → 140 min**
  (auberge 65 → 80, biens de Lucien) ; zéro plantage/usurpation. Vingt
  sauvegardes/rendus stables après préparation de sauvegarde ; en crue 2024,
  `sauver` complète seulement la référence interne `planches_1` avant écriture,
  puis la recharge est identique (rejeu et chronique identiques également).
  Pics de passages/h : 9/10/15/46/52 → 10/9/18/38/27 ; nouvelles alertes de
  dette, froid, eau et noir : aucune garantie générale d'absence de boucle.
  Aucun profil initial ≥ 70 : le seuil commun du souci permet pourtant des
  secours, donc le critère historique n'est pas satisfait. Restent aussi la
  mesure causale des minutes apaisées et la validation générale des anciens
  parcours. **L'invariant complet 3d reste ouvert.** Suite finale unique sur
  116294e : **2 361 tests, 274 fichiers, 1 887,048 s, 30 échecs et 4 erreurs**
  dans 24 fichiers, dont les deux MiMo historiques. Épreuves du secours,
  entretien isolé, échelle et vue pure/mémo vertes. Anciens parcours de demande,
  appel, vol et déplacements encore en échec, sans attribution exhaustive ni
  adaptation générale : **ne pas intégrer comme validation générale de 3d**.
  Sans Luna, deux travailleurs réduits au plus. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/empathie-197/` ;
  [rapport 197](taches/rapport-codex-197-empathie.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Livraison partielle (3d) : secours sur faim et froid perçus, souci commun du lot 80, crédit service_rendu du froid, ordre déterministe des références des portions. Banc 20 paires 4 h : 21 repas d'empathie dans 13 nuits, sans recours 635 → 140 min, S mine 13 → 23, auberge 6,5 → 11. Peur (rester près) hors lot. Aucun profil d'empathie ≥ 70 dans les scénarios.

- **Diagnostic changements d'avis des PNJ**, lot **196**, branche `codex-changements-avis`, base `56ae922` : diagnostic et conception seuls (aucun fichier de `donjon/`, scénario ou test modifié, aucun Luna), détecteur générique sans effet de bord `tools/detecter_changements_avis.py` joué sur 20 nuits de 4 h (`relais`, `mine`, `auberge`, `crue`, `crue_hameau` × 1985/7/42/2024 ; 594 cycles accomplis, 272 allers-retours justifiés, **364 allers-retours non justifiés** tous prouvés boucles réelles sur `crue` 359 et `crue_hameau` 5 : 358 oscillations de Gorm sur la réserve brisée combinant `fin == "detruit"` ignorée par `gestes`/`satisfaite`, croyance `verrouillee` et bascule `"essai"`/`"vu"` dans `constater`, et auto-annulation par `retabli_par_son_plan` ; évacuations `PERIL_EAU` auto-annulées de Brune en `crue 1985` min 42 et `crue_hameau 1985` min 204 ; changements d'abri d'Ilse en `crue_hameau 2024` min 42–97), contrat d'engagement commun et découpage en lots 196a–196d dans [rapport 196](taches/rapport-codex-196-changements-avis.md), bruts dans `C:/Users/msics/donjon/artifacts/avis-196/detection-4h.json`.

- **Branche `codex-occasions-asymetriques`, fusionnée**, lot **186**,
  base `integration 12a936d`, **variante finale sans galettes** : les nouveaux
  lots alimentaires de Gorm/Mathe/Odile et leurs connaissances sont retirés
  des sept scénarios. Bois propre de Brune/Odon/Joss, triangles d'affection
  via Aubin/Josse/Mireille et observations inégales de la crue conservés.
  Aucun `donjon/*.py`, trait, valeur, garde ou stock alimentaire historique modifié.
  **16 paires de 4 h**, quatre scénarios × 1985/7/42/2024 ; références exactes
  `12a936d` toutes relues en cache, seule la branche rejouée, moteur/outils
  identiques. S/F/D moyens : Relais **3/2/0,625 → 3/2/0,625** ; mine
  **13,5/4,5/1,286 → 13,5/4,5/1,250** ; auberge
  **6,5/2,75/0,625 → 6,5/2,75/0,625** ; crue **10,75/5,5/1,75 → 11/5,75/2**.
  Propositions/acceptées **18/2 → 21/2** (avec galettes : 11/0). Marchés retrouvés :
  Odon/Mathe à 13 min, une part de bois contre le repas, outils conservés ;
  Lucien/Anselme à 212, crochets contre besace. À 4 h : promesses **1/0 → 0/0**,
  tâches payées **3/0/0 → 10/0/0**, commissions **0/0/0 → 1/1/1**,
  avis/adoptions **11/2 → 3/2**, services crédités **3 → 3**, aucune dispute.
  Zéro plantage/usurpation/violation ; `fige_presse` **5 → 4**, `noir_long`
  **1 → 1**, deux répétitions de lectures (Josse/Rémy, mine 2024) et une
  alternance de Gorm (crue 7). Quatre bascules isolées de chaque côté,
  pire passage **30 → 42/h** ; aucune boucle motrice nouvelle établie.
  Gain non uniforme : mine 1985 S **17 → 14**, compensé par les autres graines ;
  crue 7 **13 → 8**, notamment huit avis absents. Les anciennes nuits de 12 h
  avec galettes restent archivées, sans attribution à la variante finale.
  **Tests ciblés : 299 dans 25 fichiers**, puis **68** dans cinq fichiers ;
  dépendances déjà reprises : **25 méthodes**, puis **42 tests** dans quatre
  fichiers. **Bilan consolidé vert**. Les assertions liées aux galettes sont
  restaurées ; seules les scènes concernant bois, liens et positions gardent
  leurs contraintes d'auteur. Sept variantes jouées cinq minutes puis rechargées
  (état, description, besace, sons), rareté alimentaire vérifiée contre une
  référence déclarée de 12a936d ; 54 inverses contractuels restituant la base.
  Pas de nouvelle suite complète : aucun fichier modifié hors de ceux déjà
  repris, conformément à la consigne. Aucun Luna ni nouveau banc de 12 h ;
  deux travailleurs réduits au plus, `main` intacte, aucun temps comparé.
  Complément commité localement pour la poussée du superviseur ; pas de clé
  de signature configurée. Bruts finaux exclusivement
  `C:/Users/msics/donjon/artifacts/occasions-186/sans-galettes/` ;
  [rapport 186](taches/rapport-codex-186-occasions-asymetriques.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Données seulement : bois cessible, liens d'affection en triangle, observations inégales ; galettes retirées après comparaison à base identique (elles supprimaient la rareté). Base 12a936d, 16 nuits 4 h : propositions 18/2 → 21/2, une commission aboutie, avis 11/2 → 3/2 (crue 7 divergente), pire passage 30 → 42/h. Empreintes de référence modifiées.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Neuf familles de parades locales inventoriées ; 364 allers-retours sans entrée nouvelle sur 20 nuits de 4 h, dont 358 boucles de Gorm en crue après le bris de la réserve, invisibles à l'audit échantillonné. Contrat d'engagement proposé et lots 196 a à d. Suite complète sur 116294e (194 et 180 fusionnés) : 2 356 tests, 16 ignorés, verte.

- Branche `codex-comptes-ecrits-moteur`, fusionnée, lots **180 / b / c**,
  base initiale `integration e61cf08`, correction c sur `a0fcdb5`.
  Le narrateur raconte le geste et le ton sans affirmer de compte : garde
  stricte, seules les répliques citées des PNJ sont comparées aux comptes
  issue/état/offres typés. Quantités présentées sans transfert inventé,
  compléments de lieu « pièce » exclus du domaine monétaire.
  Le moteur écrit une phrase naturelle par compte, à la deuxième personne,
  avec accords communs et désignations publiques sans apposition ; paiement
  et livraison réciproque réunis, solde nul et offre conclue non répétés.
  Provenance typée des textes d'opérations dans `paroles` : les anciens textes
  comptables sont remplacés sans retirer les autres faits de la même parole.
  Parts/services et offres préparées utilisent les mêmes noms grammaticaux
  publics. Preuve exacte, sauvegarde avant affichage, repli et montants conservés.
  **Grammaire bornée : invariant exhaustif en français libre non garanti.**
  Aucune exception de scénario ; essais 117/117 b/117 c et 168 abandonnés.
  Suite c unique : **2 289 tests, 264 fichiers, 1 382,257 s**, uniquement
  les deux échecs MiMo historiques `6 != 5`, zéro erreur/ignoré. Tests du lot
  verts, dont six nouveaux tests de rendu naturel ; aucune reprise nécessaire.
  Console/MJ simulé et recharge : Gorm, Brune, Aubin, achats de deux biens,
  prime vingt et montant inventé, pied-de-biche « dans cette pièce »,
  réplique présentative, phrases moteur contrôlées mot pour mot.
  Validation externe de b (`a0fcdb5` contre `cdaf371`) : comptes deux passes,
  5,08 → 4,58 appels/tour, 19,5 → 17,6 s/tour, comptes justes mais replis
  1 → 2 ; références une passe, relances 3 → 6 et refus 8 → 13.
  Ces mesures motivent c et ne le valident pas. Aucun Luna joué par cet agent ;
  commandes exactes pour c, mêmes groupes et référence, dans
  `C:/Users/msics/donjon/artifacts/comptes-180/luna-a-jouer.txt`.
  Bruts exclusivement dans ce dossier ; au plus deux travailleurs réduits.
  Aucun fichier réservé au lot 179 ni `main` modifié. Pas de clé de signature
  configurée : commit non signé sur cette branche.
  [Rapport 180](taches/rapport-codex-180-comptes-ecrits-moteur.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Décision du 2026-10-27. La prose du narrateur ne dit plus aucun compte (garde stricte) ; seules les répliques des PNJ sont comparées aux comptes (issue et offre) ; une phrase naturelle du moteur par compte. Validation Luna de l'orchestrateur contre cdaf371, comptes deux passes : appels/tour 5,08 → 4,42, obstacles narratifs 11 → 5,5, replis 1 → 0,5, refus 1 → 0, prime de Gorm à 20 ; références une passe : relances 3 → 7 (familles connues de l'audit, pas les comptes). Remplace les lots 117 c et 168, abandonnés.

- **Branche `codex-porte-lieu-garde`, fusionnée**, lot **194**, base
  `integration de18162` : responsabilité crue des installations sans
  propriétaire déclaré dans `biens`, coût commun du bris (honnêteté/douceur),
  identité de la personne lésée dans la clé du plan. Porteur cru de clé,
  garde lue et charge propre ; aucun agenda privé d'autrui consulté.
  Témoins par leurs propres croyances ; raccords `pnj.py` et `moteur.py`
  autorisés, coups du joueur désormais au registre commun. Aubin ayant froid
  devant la porte du beffroi demande la clé ; autre contenant, témoin du
  joueur et d'un PNJ, détresse, ignorance, expiration, recharges et laps
  découpé : **105 ciblés finaux verts**. La nuit hameau 1 de la base actuelle
  ne reproduit plus le bris historique ; scène équivalente autorisée, avec
  bris retrouvé en neutralisant seulement la nouvelle lecture.
  Suite unique **2 323 tests, 268 fichiers, 1 868,206 s**, quatre échecs et
  quatre erreurs bruts ; défauts du raccord et des nouvelles épreuves repris
  verts, restent les deux MiMo historiques `6 != 5`, sans seconde suite.
  **21 nuits 4 h**, zéro plantage/usurpation, 21 mondes/rendus rechargés
  identiques ; deux bris au hameau, cinq crochetages, aucune demande de clé
  dans ces nuits. Quatre répétitions : trois contrôles neutralisant la seule
  nouvelle lecture ont états complets/chroniques/alertes identiques ; aucune
  nouvelle boucle attribuée au lot. **VERIFIER + spatial 0,2**, hameau 1985,
  2 h, vert et recharge identique. Seize références anciennes relues, aucun
  cache hameau disponible ; aucune référence existante rejouée, aucun temps
  de cache comparé. Pas de nouveau moyen social ; une victime par bien,
  priorité propriété, clés puis gardes ; garde d'autrui connue par lecture.
  Aucun Luna ni scénario modifié, deux travailleurs réduits au plus. Bruts
  exclusivement `C:/Users/msics/donjon/artifacts/porte-194/` ;
  [rapport 194](taches/rapport-codex-194-porte-lieu-garde.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Briser l'installation d'un lieu dont quelqu'un a la responsabilité crue (clé, garde, charge) est une faute envers lui ; témoins et joueur par la même règle (raccords minimaux pnj.py, moteur.py autorisés). Aucune demande de clé dans les nuits libres : choix prouvé par scènes ciblées.

- **Lot 186 (occasions asymétriques, `codex-occasions-asymetriques`), fusion annulée le 2026-10-27** (`057d151`) : ses données
  (bois cessible de Brune/Odon/Joss, liens d'affection en triangle, observations inégales), validées sur la base `12a936d`,
  rencontrent le projet de pièces du lot 184 fusionné entre-temps (Brune endettée vend désormais son bois) : 30 échecs et
  4 erreurs dans 25 fichiers de tests sur `c12acd1`, alors que ces fichiers passent sur `7f4445f` (261 tests). Gain du lot
  modeste à base identique (propositions 18/2 → 21/2, une commission aboutie, avis 11/2 → 3/2). À refaire sur la base actuelle
  (branche conservée sur `origin` jusqu'à décision, bruts `artifacts/occasions-186/`).

- **Branche `codex-deja-entendu`, fusionnée**, lot **191**, base
  `integration 8a10a16` : livraison **partielle, à ne pas intégrer comme garantie
  de l'invariant subjectif complet**. Le registre commun suit les paroles
  entendues par les témoins connus, y compris les avis refusés ; plusieurs
  positions entendues coexistent sans devenir des croyances. Les nouvelles,
  `_a_dire` et les preuves de transmission consultent ce registre sauvegardé.
  Un changement appris rouvre les anciennes valeurs ; une première conclusion
  personnelle ne se confond plus avec le contenu d'une parole entendue.
  **Limite ouverte** : le contrôle historique `_sait` de `bavarder` lit encore
  l'esprit de l'auditeur pour les connaissances antérieures. Sa suppression et
  un essai de vue commune ont révélé des régressions de défense et de trajets ;
  cet essai est retiré. Il faut étendre le contrat des observations communes,
  au-delà des seules fonctions de registre autorisées dans `esprits.py`.
  Suite unique intermédiaire : **2 299 tests, 265 fichiers, 1 572,001 s,
  15 échecs et une erreur**, dont les deux MiMo historiques ; elle ne valide
  pas à elle seule la version réduite finale. **135 ciblés finaux verts,
  17 fichiers** ; les échecs intermédiaires hors les deux MiMo historiques
  sont repris verts, deux empreintes réancrées (plans et vues inchangés).
  **16 nuits retenues 4 h** : zéro plantage/usurpation, aucune nouvelle alerte
  de boucle. Confidences totales Relais/mine/auberge/crue :
  **9/127/37/48 → 9/81/30/37** ; avis crue **15 → 5**, deux adoptions,
  aucune dispute naturelle. Seize références `4c57020` relues, antérieures
  à la base : écarts non attribuables au seul lot. Mine 1 rejouée dès le début :
  guet **15 → 3** ; ancienne capture avant 40 garde encore les annonces 40/41,
  sans reconstitution rétroactive des audiences. Reprises 10 min / 5 + 5,
  mondes et rendus rechargés identiques. Aucun Luna,
  deux calculs réduits au plus ; tous les bruts conservés dans
  `C:/Users/msics/donjon/artifacts/deja-entendu-191/`.
  [Rapport 191](taches/rapport-codex-191-deja-entendu.md).
  Fusionné sur l'intégration : conflits de documentation et de `tests/test_etapes_chainees.py` (patch des naissances A6 du lot 184 et paroles attendues du lot 191, réunis) ; aucun fichier de code du jeu commun depuis la base. Livraison partielle : annonces du guet de la mine 15 → 3. Reste un lot séparé : `_sait` dans `bavarder` lit encore le savoir réel de l'auditeur.

- **Branche `codex-naissance-evenement`, fusionnée**, lot **192 / A6
  deuxième volet partiel**, base `integration 3668061` : un portage illégitime
  constaté et son épreuve persistante font naître `récupérer {objet, qui}` par
  la table et la création communes aux dettes personnelles. Poids selon valeur
  matérielle, ambition, honnêteté, douceur, fierté et rancune ; terminal du
  graphe existant « porter le bien », refus et prix de violence communs.
  Sommeil/réveil, publication différée, plafond et sauvegarde conservés ; fin
  sur retour, destruction ou consommation crus. Pas de lecture de position
  cachée ni de fin inventée pour une suppression distante.
  **28 ciblés distincts verts** consolidés, dont dix d'événement repris ;
  suite unique **2 318 tests, 267 fichiers, 1 713,848 s**, deux MiMo historiques
  `6 != 5`, aucune erreur/ignoré. Derniers ajustements repris en ciblés.
  **16/16 nuits 4 h** (Relais/mine/auberge/crue × quatre graines) : états et
  chroniques identiques au témoin exact, mondes/rendus rechargés identiques,
  zéro plantage/usurpation ; alertes de base inchangées. **Zéro récupération
  née naturellement**, richesse S/F/D inchangée. Mine fixe 1985, 4 h :
  793 recherches, 342 neuves, 10 979 nœuds ; CPU indicatif 13,14 s.
  Anselme/ballot et Gorm/marteau : six captures ciblées conservées, prise
  autonome et deux projets atteints, trois minutes d'un bloc ou 1 + 1 + 1,
  monde/rendu rechargés identiques. Capture historique de vol en nuit libre
  non acquise ; les scènes d'auteur isolent les pulsions concurrentes.
  Restent : disparition attribuée sans portage constaté, réclamation du vol,
  dénonciation autonome, restitution de tout stock porté par autrui et abandon
  selon la VOL ; nuire sans bien, punir, rallier, occasion et soupçon déduit
  hors lot. Aucun Luna ni fichier réservé aux lots voisins modifié ; deux
  travailleurs réduits au plus. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/naissance-192/` ;
  [rapport 192](taches/rapport-codex-192-naissance-evenement.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Livraison partielle (A6) : naissance et moyens communs prouvés par scènes d'auteur ; aucune récupération née naturellement dans les 16 nuits (aucun vol vu par sa victime), richesse inchangée.

- **Branche `codex-sortie-exterieure`, fusionnée**, lot **189**, base
  `60617f9` : une sortie terminale est exclue du graphe des déplacements
  internes, des estimations et des candidats de `Vue`, avec sa carte dans
  `_entrees` ; la marche PNJ revalide la transition courante dans les deux
  modes. Départ volontaire du joueur conservé. Les **439 événements** du
  hameau 1 (revue 187) sont reproduits à l'identique sur la base ; captures
  Brune 120 / Ilse 177 reprises sans départ, état complet et rendu identiques
  après recharge et temps entier/découpé. Gorm 352 min 54,7 s / Aubin
  380 min 39,7 s (hameau 2024, cas 188) également repris, recharges et laps
  découpés identiques. **34 ciblés finaux verts** ; suite unique **2 297 tests,
  265 fichiers, 2 304,410 s**, aucun échec/erreur, 16 ignorés (15 dépendances
  MiMo facultatives, un `jsonschema`). Deux compléments après le passage du
  fichier sont vérifiés en ciblés. **16/16 empreintes 2 h** Relais/mine/auberge/
  crue × quatre graines identiques à la base exacte, état complet, repères,
  récits et 32 recharges compris ; références manquantes constituées une fois.
  **5/5 nuits hameau 4 h**, graines 1/1985/7/42/2024 : zéro PNJ parti,
  usurpation ou plantage, cinq recharges état/rendu identiques, aucune boucle
  « à expliquer ». Deux bascules isolées ; passages horaires max 24/40/22/19/28.
  Contrôle exact 1985 : Sève quitte les lieux à 192 sur la base ; Gorm
  20 → 40 passages/h sur le lot, achats, inspections de deux bruits distincts
  et ronde ; hausse signalée, pas de boucle sans nouvel événement identifiée.
  Pas de garantie générale sur les autres boucles ni but autonome de départ.
  Deux travailleurs réduits au plus, sans Luna, aucun fichier réservé modifié,
  aucune clé Git configurée (commit non signé). Poussée rejetée par la revue
  automatique (export privé, propriété/destination GitHub non établies) ;
  commit conservé localement selon le brief. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/sortie-189/` ;
  [rapport 189](taches/rapport-codex-189-sortie-exterieure.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `planification.py`, fusionnés sans conflit textuel. Corrige la régression du lot 181 trouvée par la revue 187 et le diagnostic 188 (Brune 120, Ilse 177 hameau 1 ; Gorm 352, Aubin 380 hameau 2024). À surveiller : pic de passages hameau 1985 20 → 40/h, sans boucle identifiée.

- **Branche `codex-naissance-agendas`, fusionnée**, lots **184 a/b / A6
  partiel**, base `integration 4efb277`, suite de `ae9504a` : table commune de
  naissances et projet de pièces sur dette personnelle ; **184 b** compare
  travail payé, vente de biens propres portés cessibles, prêt d'une bourse,
  prise permise et vol au prix commun de la faute. Marches/paroles cherchées,
  marchés par `proposer`, tâche contre numéraire par `engager` : avance,
  engagement et remboursement éventuel communs. Pas d'accord ni fonds privés
  supposés. Coût en minutes attendues par fraction du manque ; borne optimiste
  sur le tarif du travail, sans supprimer un meilleur recours. Sommeil sans
  nouvel essai identique, refus causaux, routine d'argent dédupliquée.
  Odon et Rémy : ventes réelles, travail payé/accompli, prêt et vol, refus,
  laps découpé, monde/rendu rechargés. **273 ciblés/repris distincts verts**,
  31 fichiers ; suite unique **2 306 tests, 1 594,589 s**, 28 échecs/trois erreurs
  bruts : cas repris verts hors deux MiMo historiques `6 != 5`. Frontière moteur
  corrigée : coupe des annotations de devis avant publication du plan monétaire.
  Capture de recherche : 31 passages, 17 monétaires/14 des recours de recherche ;
  plafond de recherche précisé, monde/ouïe découpés conservés, A6 actif.
  Répétition 42 de 184 a **causée par sa trajectoire de projet** : capture à 5,
  reprise jusqu'à 240 strictement identique à l'archive, huit lectures de Mathe ;
  même capture avec le seul projet abandonné, dette conservée : trois lectures.
  Lecture des signes inchangée depuis la base ; aucun cas propre ajouté.
  Banc final 184 b, 8/8 nuits sans plantage/usurpation, zéro bascule ;
  `repetition` et `voir_alterne` disparus. Attente sous regard 164 → 74 min.
  S/F/D, même `cats` du lot 183, mine 4 h : base **13,5/4,5/1,286**, 184 a
  **12,25/4,75/1,143**, final 184 b **12,75/5/1,179** ; auberge inchangée.
  Gain général non acquis ; noir mine base/184 b **31,25/90 PNJ·min**.
  Coût fixe mine 1985/4 h base/184 a/184 b : neuves **264/401/342**, nœuds
  **7 564/13 202/10 979**. Premier devis exhaustif 184 b : 187 362 nœuds ;
  borne sans changement de monde/chronique/récit/souvenirs du relevé fixe ni
  états/chroniques des huit nuits tirées. CPU final 14,52 s, indicatif ; aucun
  temps du cache comparé. Vérifications au-delà du créneau, pas de seconde suite.
  Aucune référence rejouée, aucun Luna ni fichier réservé
  aux lots 180/185 modifié ; deux calculs réduits au plus, `main` intacte.
  **Restent A6** : créances locales subjectives et identité d'une nouvelle dette,
  occasion, événement, soupçon déduit ; pas de crédit numéraire nouveau ni de
  remboursement extérieur simulé. Aucune clé de signature Git configurée. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/naissance-184/` ;
  [rapport 184](taches/rapport-codex-184-naissance-agendas.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Livraison partielle (A6) : la dette crue fait naître un projet de pièces qui compare vente, travail payé, prêt, prise permise et vol au prix de la faute. Mine 4 h contre la base : nœuds 7 564 → 10 979, noir 31 → 90 PNJ·min, S 13,5 → 12,75, F 4,5 → 5 ; alertes de 184 a disparues. Suite décidée le 2026-10-27 : projets hors détresse (placer l'agenda selon son poids).

- **Mesure de réflexion limitée**, lot **190**, branche
  `codex-mesure-reflexion`, base `integration e62c5bf` : sondes et documentation
  seules, aucun fichier de `donjon/` modifié, aucun Luna. Deux variantes de
  profondeur (INT modulée ; même limite sauf sécurité/devoir/désespoir),
  neuf nuits libres 12 h, mine/auberge/hameau 1985 fixes. Mine : monde et récit
  identiques ; auberge INT : premier écart de chronique à 658 min, attente
  435 → 440 ; variante enjeu identique. Hameau : six départs avant 155 min
  contre quatre au témoin, défaut des issues du lot 189 encore présent dans
  cette base ; baisse de CPU non interprétable comme amélioration.
  Le plan lumière avant crochetage est perdu par les deux variantes ; la
  capture historique Gorm 42/151 choisit désormais ses fagots, pas les planches.
  701 explorations échantillonnées × deux variantes : mine/hameau sans écart,
  auberge deux plans changés en INT, un en enjeu ; surcoûts maximaux 8,085 et
  2,167 minutes modèle. Aucun plan perdu dans cet échantillon ; il manque la
  première divergence du hameau. Trois témoins appariés strictement identiques
  aux témoins simples ; douze mondes/rendus finaux rechargés stables.
  Six reprises de scènes : monde/rendu rechargés et dix minutes d'un bloc ou
  5 + 5 identiques. Livraison **partielle** : saillance non filtrée, appariement
  échantillonné des recherches avant `endurer`, sans référence élargie ni taux
  exact de choix de but changés. Ne pas avancer l'implémentation avant A5 sur
  ces seules mesures. Deux calculs réduits au plus ; bruts exclusivement
  `C:/Users/msics/donjon/artifacts/reflexion-190/` ;
  [rapport 190](taches/rapport-codex-190-mesure-reflexion-limitee.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Profondeur selon l'INT, entière en urgence (variante E) : mine et auberge identiques en comportement, nœuds −44 % / −43 %, CPU indicatif −18 % / −27 % ; perd un plan émergent de huit étapes (allumer avant de crocheter). Saillance non mesurée, hameau faussé par les départs (lot 189). Décision à l'utilisateur.

- **Diagnostic appels/alternances**, lot **188**, branche
  `codex-appels-alternances`, base `integration 31f7a0d` : aucun code ni Luna,
  un seul calcul à priorité réduite. Crue 1985, 12 h : les **douze appels de
  Brune, 495–518**, sont reproduits ; cinq premiers lieux et sept rappels
  après des pas anonymes situés différemment, une seule voie d'appel,
  aucune présence de Gorm inventée. Hameau 2024, 12 h, confirmé avec récit
  et relevés : **quatre** alternances, une entretien/garde ; inspections
  après 30 min et faits nouveaux avant les retours à la garde. **L'alerte
  historique est interrompue par un défaut distinct du contrat des routes** :
  Gorm sort définitivement à **352 min + 54,7 s** en cherchant Aubin pour
  entretenir le feu ; Aubin à **380 min + 39,7 s** en cherchant Brune pour
  la prévenir. Issue terminale introduite au lot 181, traitée comme salle
  d'inspection ordinaire par le planificateur. À reprendre : même conséquence
  terminale dans recherche/devis/route/exécution, aucun plan ne promettant
  d'agir dans les lieux après départ. **153 recharges** état/rendu identiques,
  dix choix de Gorm identiques après recharge ; reprises des deux départs
  confirmées, limite de cadence des captures intermédiaires documentée.
  Archives 174 absentes, onze alternances anciennes non expliquées une à une ;
  archive 160 seulement relue. Aucun correctif ni suite complète.
  Bruts exclusivement `C:/Users/msics/donjon/artifacts/appels-188/` ;
  [rapport 188](taches/rapport-codex-188-appels-alternances.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Appels de Brune légitimes (indice perceptif nouveau à chaque rappel). Alternances de Gorm non reproduites : la nuit s'interrompt par le départ définitif de Gorm (352) puis d'Aubin (380) par la digue en cherchant quelqu'un, même défaut que la revue 187 ; cas transmis au lot 189.

- **Revue vierge 187, lecture seule**, branche `codex-revue-vierge-pnj` : six nuits 4 h observées avant lecture des plans (`C:/Users/msics/donjon/artifacts/revue-187/`), [rapport 187](taches/rapport-codex-187-revue-vierge-pnj.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Deux défauts confirmés par l'orchestrateur dans les bruts : hameau graine 1, Brune (120) et Ilse (177) quittent les lieux par la sortie extérieure en cherchant Gorm (régression du lot 181) ; Aubin force la porte du beffroi au pied-de-biche à côté de Gorm qui tient la clé (79).

- **Branche `codex-prevision-bornee`, fusionnée**, lot **185**, base
  `integration 4efb277` : observation sèche ou mesurée postérieure bornant
  la droite de montée incompatible, sans changer la pente ni lire l'eau
  cachée. Contrat commun `eau.borner` / estimation propre / avis quantitatif,
  routes et clé existante, sauvegarde sans migration. Captures 182 de Sève
  345, Ilse 420 et Maël 450 : recours retrouvés, dix minutes d'un bloc ou
  découpées, monde et rendu rechargés identiques ; trois entrées exactes
  également relues. **38 ciblés finaux verts**, **12/12 empreintes 2 h** hors eau
  active identiques aux archives 181, état complet compris. **Huit nuits
  rapides 4 h**, aucun plantage/usurpation/nouvelle alerte de boucle ; hameau
  identique aux quatre archives 181. Crue comparée au cache de `main 812ebe5`,
  antérieur à la base : écarts non attribués au seul lot 185. Suite unique :
  **2 293 tests, 264 fichiers, 1 464,334 s**, trois échecs bruts : deux MiMo
  historiques `6 != 5`, ancienne attente de plan absent corrigée puis ciblée
  verte. Aucune erreur ni test ignoré. `VERIFIER` + spatial 0,2, crue 2024 et
  hameau 42, 2 h : zéro écart/plantage, reprise finale après réancrage comprise.
  Aucun Luna ni fichier réservé
  au lot 184 modifié, deux calculs réduits au plus ; aucune clé de signature.
  Bruts exclusivement `C:/Users/msics/donjon/artifacts/prevision-185/` ;
  [rapport 185](taches/rapport-codex-185-prevision-bornee.md).
  La borne ne prouve pas la décrue ni la fin de toute attente ou navette.
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Corrige le défaut diagnostiqué au lot 182 (Sève, Ilse et Maël, hameau 42 : routes et abri rétablis). Crue 4 h contre une référence antérieure à la base : eau 128,75 → 17,5, passages horaires max 13,25 → 20, à surveiller à la prochaine vérification d'intégration (Maël galerie puis retour à Gorm en deux minutes dans une capture).

- **Branche `codex-depart-definitif`, fusionnée**, lot **181 / A4b
  partiel**, base `integration 8c0cecd` : sortie `exterieur: true`, état
  `parti` sauvegardé par la marche commune joueur/PNJ avec ou sans cases ;
  personne et biens conservés, sans présence, occupation, perception, lumière
  ni ouïe dans les lieux. Retrait immédiat de l'ordonnanceur pendant son laps,
  invalidation des caches perceptifs. Digue déclarée dans `crue_hameau` seul.
  Preuve `etat.parti` aux témoins, constats et nouvelles datées des PNJ ;
  `protéger` finit avec cause publiée à la sortie du choix, sans renaissance.
  Lieu inconnu non terminal ; retour par placement d'auteur à l'issue,
  croyance démentie par la vue, reprise corporelle sans temps rétroactif.
  Départ du joueur : fin `depart`, journal et rendu de fin sauvegardés.
  **16/16 empreintes historiques 2 h identiques**, Relais/mine/auberge/crue
  × quatre graines, état complet et monde/rendu rechargés compris ; références
  finales du lot 179 exclusivement relues. Aucun temps du cache comparé.
  **55 ciblés validés au terme des reprises**, dont huit départs/retours et
  conversations ; suite unique : **2 287 tests, 263 fichiers, 1 334,188 s**,
  deux échecs MiMo historiques `6 != 5`, aucune erreur. Les deux compléments
  de tests ajoutés après le passage du fichier et les reprises finales du
  retour/nouvelle sont validés en ciblés, sans seconde suite complète.
  **4/4 nuits hameau, 4 h**, zéro usurpation/plantage, aucune boucle signalée,
  trois bascules isolées ; une observation `fige_presse` de devoir (1985).
  Quatre mondes/rendus identiques après recharge ; aucun PNJ parti dans ces
  nuits passives, les franchissements sont exercés dans les scènes ciblées.
  **Limite** : l'adoption subjective des nouvelles par le joueur reste
  absente ; paroles entendues seulement, sans modèle de confiance inventé.
  Aucun choix autonome nouveau de départ, geste de retour du MJ ni simulation
  hors des lieux. Restent suivi vocal, interposition d'un lieu et ouï-dire
  des droits de garde. Aucun Luna ni fichier réservé au lot 180 modifié.
  Deux travailleurs réduits au plus, `main` intacte, aucune clé de signature.
  Bruts exclusivement `C:/Users/msics/donjon/artifacts/depart-181/` ;
  [rapport 181](taches/rapport-codex-181-depart-definitif.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Décision du 2026-10-27 appliquée. Livraison partielle autorisée : adoption subjective par le joueur des nouvelles d'un départ ouverte ; aucun choix autonome de partir (lot ultérieur).

- **Diagnostic attente/noir du hameau**, lot **182**, branche
  `codex-attente-hameau`, base `integration 1598b57` : aucun code modifié,
  aucun Luna. **Neuf nuits historiques 12 h**, deux calculs réduits au plus.
  146 e inchangé sur 42/7 ; **163** : attente **0 → 1 435** en 42 et
  **15 → 495** en 7 ; **167** : **495 → 720** en 7, noir **580 → 715**.
  167 b/c : mêmes chroniques/relevés ; deux nuits expliquent **96 %** de la
  hausse d'attente. En 42, anciennes pentes positives malgré des lieux revus
  secs : routes alimentaires et abri interdits par les croyances, recherches
  épuisées sans plafond. Neutraliser ces pentes sur copies rend les recours
  possibles ; aucun correctif livré. Invariant à reprendre : l'observation
  sèche récente contraint l'extrapolation, sans inventer de pente ni lire
  l'eau cachée. En 7 : froid sans moyens, lumière possible mais sécurité non
  urgente ; interposition de Gorm dès 347, puis attente alimentaire de Sève
  **10 → 285 min**, porte crue verrouillée par ouï-dire, réellement ouverte
  mais non vue de près. Aucun passage connu ignoré. **48 recharges** de
  captures et **quatre entrées exactes** : état/rendu identiques ; rejeu
  110–450 identique au témoin. Auberge sans eau active : cause du noir non
  attribuée ; 1985/2024 seulement relues, aucune garantie générale.
  Pas de suite complète ni clé de signature ; `main` intacte. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/attente-182/` ;
  [rapport 182](taches/rapport-codex-182-attente-hameau.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Petit lot désigné : une observation sèche récente borne une prévision d'eau ancienne qui la contredit (contrat observation/prévision/routes/clé de recherche/sauvegarde), cas réels Sève et Maël hameau 42 ; après le lot 181 (`esprits.py`).

- **Diagnostic des mécanismes dormants**, lot **183**, branche
  `codex-mecanismes-dormants`, base `integration 1b0a778` : les **49 archives**
  du lot 174 relues, aucune modification du jeu, des scénarios ou de Luna.
  **174 propositions, 14 acceptées** ; **18 promesses en contrepartie**,
  17 refus `garde`, un `epuise`, aucune acceptation ; une commission naturelle
  dans le hameau 1985, Brune → Maël à 659 min, refus `mefiance` ; aucune dispute.
  Sept crédits de service dans les huit mines, sans preuve de réparation
  intentionnelle. Le compteur des travaux payés ne mesure pas les promesses.
  Mesure documentaire S/F/D (signatures sociales, familles, diversité par PNJ,
  inactifs compris) sur les 49 nuits ; durées et groupes séparés. Priorités
  proposées : situations négociables et asymétrie des preuves comme données,
  empathie générale 3d, mandat A5 et naissances d'agendas A6 comme pièces moteur.
  Reconstitutions ciblées sur copie de `ee835d2`, un seul processus de nuits à
  priorité réduite : **mine 1985, crue 7, hameau 1985, 12 h**, chroniques,
  mesures, empreintes, récits et souvenirs identiques aux archives. Captures
  rechargeables, dix suites de décisions vérifiées deux fois, états/rendus
  stables après recharge ; détails dans les bruts,
  exclusivement `C:/Users/msics/donjon/artifacts/dormants-183/`.
  Pas de suite complète ni de banc nouveau sur la branche documentaire.
  [Rapport 183](taches/rapport-codex-183-mecanismes-dormants.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Priorité du 2026-10-27 (richesse des PNJ) : suites désignées A6 (naissance des agendas) après le lot 181, 3d (empathie), et données de scénario créant des occasions asymétriques (biens cessibles, travail utile, observations inégales), sans affaiblir les gardes.

- **Vérification d'intégration ee835d2**, lot **174**, laptop, branche
  `codex-verif-integ-ee835d2`, base documentaire `a96a495` : code `donjon/` et
  `tools/` identique à `ee835d2`, aucun changement du jeu ni Luna. **49/49 nuits
  achevées une fois**, deux travailleurs au plus à priorité réduite : 32 × 12 h,
  huit rixes × 8 h, cinq VERIFIER/spatial 0,2 × 8 h, quatre hameaux × 12 h.
  Zéro plantage, violation, usurpation, mort, coup contre personne ou écart de
  contrôle ; seule borne Lucien auberge **42/314**, retenu = optimum **73,4743**.
  Archives 160/148 absentes : rapports seuls relus, aucune référence rejouée.
  Crue, moyenne huit graines : eau **344,38 → 44,38 PNJ·min**, attente
  **511,25 → 393,75** ; pire passage **30 → 36/h**. Crue 2024 : eau **30**,
  attente **145**, pire **24/h** (lot 163 : 34), Brune faim finale **100**,
  Ilse **73** ; quatre parts épuisées à **431**, ancienne alerte continue de
  Brune 305 min non retrouvée sous cette forme. Josse : mine 1985, 125 min dès
  80 et 135 dès 210, devoir satisfait ; 2024, 165 dès 560, faim/devoir en attente.
  **56 interpositions** principales sans violence ; sept hameau, cinq renforcées.
  Galerie à 4 h sur quatre graines **3/8**, à 12 h sur huit graines **3/16**.
  Gorm `amener` atteint **7/8**, aucun abandon ; graine 11 encore active.
  `informer` absent du scénario courant, hameau sans agenda déclaré.
  À instruire : Brune crue 1985, douze appels 495–518 ; Gorm hameau 2024,
  onze alternances dont sept entretien/garde. Aucun défaut nouveau établi ;
  absence d'archives empêchant de certifier leur ancienneté dans la même nuit.
  Hameau : eau **280 → 40**, attente **192,50 → 750**. Monde et rendu après
  recharge non certifiés par ces archives d'observation ; captivité non recensée
  exhaustivement. Aucune suite complète, aucun correctif, `main` intacte.
  Pas de clé de signature configurée ; livraison documentaire sur la branche seule.
  [Rapport 174](taches/rapport-codex-174-verif-integ.md) ; bruts exclusivement
  `C:/Users/msics/donjon/artifacts/verif-integ-ee835d2/` (49 archives et manifeste).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Petits lots désignés : diagnostic de la hausse d'attente du hameau (192,5 → 750 PNJ·min) et du noir (hameau, auberge), à relier aux lots 163/146 e/167 ; appels répétés de Brune à Gorm (crue 1985, 495-518, paires dans la même minute) ; alternances de Gorm dans le hameau 2024.

- **Branche `codex-garde-rendue-perdue`, fusionnée**, lot **179 / A4b
  partiel**, base `integration dd815f4` : preuve de possession et de droits
  enregistrée avec le lieu cru par `esprits.constater_possession`, vue et
  `echanges.remettre` (les deux participants, joueur compris). Fin de `garder`
  sur remise propre autorisée, retour vu au propriétaire autre que le gardien,
  perte vue aux mains d'un tiers sans permission ; cause sauvegardée,
  publication différée du choix et aucun réveil d'un agenda terminal.
  Prêt, garde confiée et position inconnue conservés ; aucune relecture des
  droits réels à la décision. Anselme/ballot et clé, deux biens par cause,
  laps entier/découpé, mémoire et monde/rendu rechargés éprouvés.
  **91 ciblés verts au terme des reprises**, besace et cause affichée incluses.
  Suite complète unique : **2 280 tests, 262 fichiers, 1 242,806 s**, quatre
  échecs et une erreur bruts : projection des preuves nouvelles corrigée,
  `tenir` repris vert après retrait de l'ouï-dire ; restent deux MiMo
  historiques `6 != 5`, aucune seconde suite. **16/16 nuits 2 h** finales,
  quatre scénarios × quatre graines : chroniques, mesures, récits, souvenirs
  et empreintes physiques identiques à la référence du lot 175 exclusivement
  relue, monde/rendu rechargés identiques. États hors nouvelles preuves et
  empreintes internes des croyances d'agendas identiques ; aucun temps du
  cache comparé. Code `7c52c26`, puis `70bf000` ; deux travailleurs réduits.
  **Ouï-dire non livré**, livraison partielle autorisée : l'ébauche des
  constats pouvait être masquée par l'identité d'une ancienne accusation ;
  il faut unifier les propriétés transmises dans la voie commune. Pas de
  modèle subjectif de confiance du joueur inventé ; `social.py` inchangé.
  Transfert hors `echanges.remettre` dans le noir non couvert comme remise
  propre. L'invariant intégral reste ouvert sur ces voies. Aucun Luna,
  scénario historique ni fichier réservé au lot 178 modifié. Aucune clé
  de signature configurée ; `main` intacte. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/garde-179/` ;
  [rapport 179](taches/rapport-codex-179-garde-rendue-perdue.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Livraison partielle autorisée : la fin apprise par ouï-dire reste à faire (contrat commun des propriétés transmises par les nouvelles à reprendre), ainsi que les remises dans le noir hors `echanges.remettre`.

- Branche `codex-retenus-apres`, fusionnée, lot **178**, base
  `integration dd815f4` : projection pure commune `tenir.retenus_apres`,
  employée par `enfermer` et le dossier de contre-revue. Chaque opération de
  porte indique les personnes retenues après elle ; fermeture seule ou autre
  issue libre/inconnue : aucune retenue. Présences et verrous selon l'auteur,
  vue du joueur actualisée sur une copie ; aucun effet physique ni prompt changé.
  **29 ciblés verts**, trois fichiers, 44,046 s : Bram/bureau, Rémy/réserve,
  console et MJ simulé, dossier sans mutation, refus de l'enfermement non établi,
  événements et monde/rendu rechargés.
  **8/8 exécutions identiques à `dd815f4`**, événements et recharges compris.
  **12/12 empreintes 2 h identiques**, Relais/mine/rixe × quatre graines,
  état complet et monde/rendu rechargés ; références du lot 175 et cache
  `79594e4` exclusivement relues. Suite unique : **2 271 tests, 261 fichiers,
  1 254,899 s**, deux échecs MiMo historiques `6 != 5`, zéro erreur/ignoré.
  Aucune seconde suite. **Luna non jouée sur instruction** ;
  commande exacte dans
  `C:/Users/msics/donjon/artifacts/retenus-178/luna-a-jouer.txt` : deux passes
  enfermer/traîner, une passe des neuf autres bancs de force contre `cdaf371`.
  Amélioration sémantique et critère des trois appels non certifiés.
  Deux travailleurs réduits au plus ; `main` intacte, aucune clé de signature.
  Commit local uniquement : poussée refusée par la revue automatique
  (confiance/destination d'`origin` non établies, risque d'exfiltration).
  Bruts exclusivement `C:/Users/msics/donjon/artifacts/retenus-178/` ;
  [rapport 178](taches/rapport-codex-178-retenus-apres.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Commit et poussée repris par l'orchestrateur (saturation du modèle de l'agent). Validation Luna jouée par l'orchestrateur contre cdaf371 (cache) : enfermer/traîner deux passes **5,25 → 1,83 appels/tour**, 23,8 → 9,0 s/tour, refus 3,5 → 0,5, relances 1 → 0 ; **enfermer réussi p1** (fiche puis fermer et verrouiller exécutés, deux appels chacun), **p2 Luna vise encore Bram** au lieu de la porte (refus local « Approche-toi », un appel) : écart d'interprétation restant 1/2 ; traîner 2/2. Neuf autres bancs de force, une passe : 2,53 → 2,18 appels/tour, relances 3 → 1.

- **Branche `codex-fins-agendas`, fusionnée**, lot **175 / A4b partiel**,
  base `integration 7eb1ac9`, code `0544be1` puis `101f770` : croyance `fin` après
  destruction/consommation constatée, joueur et PNJ ; date conservée hors
  mémoire bornée et après retrait des restes, pas de preuve par suppression
  distante. La disponibilité garde sa lecture historique. `garder` abandonne
  sur cette preuve, cause sauvegardée et publication différée du choix ;
  aucun devis ne réveille un agenda terminal. Réparation observée démentant
  la croyance, sans renaissance de la garde. **157 ciblés finaux verts** : deux biens,
  deux réserves, gestes propres dont outil brisé sur échec, ignorance à
  distance, choix interrompu, laps entier/découpé, monde/rendu rechargés.
  Suite unique : **2 264 tests, 261 fichiers, 1 352,153 s**, sept échecs et
  une erreur bruts ; régressions reprises vertes, deux MiMo historiques
  `6 != 5` laissés, aucune seconde suite complète. Un test de clé ajouté
  après la suite, dans les ciblés. Cadence historique conservée ; preuve
  exclue des moyens du plan, effets sur les responsabilités dans sa clé.
  **16/16 nuits 2 h**, quatre scénarios × quatre graines : chroniques,
  mesures, récits, souvenirs et empreintes physiques identiques, monde/rendu
  rechargés identiques. **8/16 états complets identiques**, cinq autres avec
  seules preuves nouvelles, trois crues aussi avec empreinte des croyances
  de l'agenda d'évacuation ; états, causes et dates inchangés. Référence
  `5f69840` (code identique à la base) exclusivement relue ; trois contrôles
  de branche sans écriture de preuve expliquent les écarts crue. Pas de gain
  de vitesse revendiqué. Placement d'auteur `sans_evacues` nettoyant désormais
  ses connaissances initiales, sans purge omnisciente en partie.
  **À sa livraison, restaient rendu/remis et perte vue sans permission ;
  suite partielle au lot 179 ci-dessus.** Départ définitif du protégé expressément
  retiré du lot par l'orchestrateur, notion absente du monde et à décider.
  Restent aussi suivi à portée de voix et interposition d'un lieu.
  Aucun Luna, scénario historique ni fichier réservé aux lots 172/173
  modifié. Au plus deux travailleurs réduits ; aucun changement de `main`.
  Pas de clé Git de signature configurée. Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/fins-175/` ;
  [rapport 175](taches/rapport-codex-175-fins-agendas.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Livraison partielle autorisée : rendu/remis et perte vue sans permission restent pour garder ; départ définitif d'un protégé hors lot (notion absente du monde, à décider). La croyance `fin` est exclue des entrées de la recherche (lue seulement via gardes/prix_gardes) : à contrôler par VERIFIER à la prochaine vérification d'intégration.

- Branche `codex-contre-revue-etat-final`, fusionnée, lot **177**,
  base `integration` `4cb4361` : règle commune de contre-revue fondée sur
  l'état final établi par le moteur. Déplacements inhérents au geste admis,
  état déjà vrai selon le dossier sans opération supplémentaire ; changements
  étrangers et états demandés manquants toujours refusés. Instructions seules,
  aucun effet moteur ni dossier perceptif changé. **16 ciblés verts**, console
  avec MJ simulé, deux seuils, Bram/bureau et Rémy/réserve, refus d'un déplacement
  de tiers et d'une ouverture contraire à l'enfermement, monde/rendu rechargés.
  Suite complète unique : **2 260 tests, 260 fichiers, 1 283,253 s**, zéro erreur
  ou ignoré ; deux échecs MiMo historiques `6 != 5` et un échec de saisie du
  test négatif, corrigé puis repris dans les **16 ciblés finaux verts, 40,771 s**.
  Aucune seconde suite, deux travailleurs réduits au plus.
  **Luna non jouée sur instruction** ; commande exacte dans
  `C:/Users/msics/donjon/artifacts/contre-revue-177/luna-a-jouer.txt` : deux
  passes traîner/enfermer, une passe neuf autres force et atelier/relais contre
  `cdaf371`. Amélioration sémantique et critère des trois appels non certifiés.
  Bruts exclusivement dans ce dossier ; aucune clé de signature configurée,
  `main` intacte. [Rapport 177](taches/rapport-codex-177-contre-revue-etat-final.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Validation Luna jouée par l'orchestrateur contre cdaf371 (cache) : traîner/enfermer deux passes 5,25 → 3,50 appels/tour, refus 3,5 → 2 ; **traîner corrigé 2/2** (deux appels, fiche puis geste exécuté, récit juste) ; **enfermer toujours refusé 2/2** : la contre-revue lit « enfermer dans » comme « y faire entrer » (« Bram est déjà dans le bureau et l'action ne le met pas à l'intérieur »), p2 10 appels. Neuf autres bancs de force, atelier et Relais, une passe : 2,72 → 2,61 appels/tour, refus 9 → 11, dans le bruit d'une passe. Suite : le dossier dira qui sera retenu après l'opération, selon la captivité du lot 140 et les issues connues (lot 178).

- Branche `codex-banc-attitudes`, **non fusionnée**, lot **176** (relations 3g), `7fb17a4` : banc `attitudes` et extraction typée
  des attitudes dans chaque segment d'audit narratif, comparée par le moteur aux `signes_percus`/`impressions` fournis (id,
  personnage, cible), contrôle refait à l'enregistrement. 40 ciblés verts, 4/4 empreintes identiques, suite verte hors MiMo.
  Luna jouée par l'orchestrateur, deux passes relais/crypte/atelier/echanges contre `cdaf371` (cache) : appels/tour
  **2,94 → 3,19**, obstacles narratifs **4,5 → 12**, relances **3 → 7**, refus 10 → 14, replis 0 → 0,5. Seuls 2 obstacles sur 24
  sont des refus d'attitude (un hochement de tête sans signe perçu, plutôt juste) ; les autres sont les familles connues (vue
  partielle, ambiance jugée mécanique, orientation), plus fréquentes : élargir le schéma et la consigne de l'audit narratif rend
  l'auditeur plus sévère sur tout, comme au lot 162. Banc `attitudes` seul : 2,75 appels/tour, 2 refus. Secondes non comparables
  (référence du cache, laptop chargé). **Mis en attente** : décision à l'utilisateur (contrôle des attitudes hors de l'audit
  narratif commun, ou abandon). Bruts `artifacts/attitudes-176/` (PC fixe) et bancs-multi 20261027-084505 / 085427 (laptop).

- Branche `codex-force-contre-revue`, fusionnée, lot **172**, base
  `79594e4` : dossier de traînage avec les deux déplacements du trajet validé,
  titre/information communs, positions des lieux non visités masquées ; dossier
  de porte avec lieu de Corvus et état après opération, consigne d'enfermer sans
  déplacer la personne déjà derrière. Aucun effet moteur ni instruction d'audit
  changé. Deux scènes de chaque nature, console et monde/rendu rechargés ;
  **29 ciblés finaux verts**. Suite unique : **2 249 tests, 259 fichiers,
  1 279,825 s**, aucune erreur/ignoré, deux échecs MiMo historiques `6 != 5`.
  **16/16 empreintes 2 h identiques** à `79594e4`, Relais/mine/auberge/rixe ×
  quatre graines ; références manquantes rangées une fois, aucun temps comparé.
  Vérifications détaillées au [rapport 172](taches/rapport-codex-172-force-contre-revue.md).
  **Luna non validée** : deux exécutions en erreur « Coffre ChatGPT illisible »
  avant tout appel modèle ; critère des trois appels non certifié. Commande
  exacte dans `C:/Users/msics/donjon/artifacts/force-172/luna-a-jouer.txt`.
  PC fixe partagé, deux travailleurs réduits au plus, bruts exclusivement
  `C:/Users/msics/donjon/artifacts/force-172/`. Aucune clé de signature configurée ;
  commit non signé, branche seule poussée ; `main` intacte.
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `tenir.py`, fusionnés sans conflit textuel. Validation Luna jouée par l'orchestrateur (coffre illisible pour l'agent), contre cdaf371 : traîner/enfermer deux passes 5,25 → 2,75 appels/tour, 23,8 → 12,3 s/tour, relances 1 → 0 ; neuf autres bancs de force une passe 2,53 → 2,29 appels/tour, aucun repli. **Critère non atteint** : la contre-revue rejette encore 2/2 le pas inhérent de traîner (« fait aussi avancer le joueur ») et 1/2 un plan d'enfermement correct (« ne déplace pas Bram ») ; p2 enfermer propose d'emblée de déplacer Bram ; les quatre saisies finissent sur le refus de portée d'une proposition de repli, dans les deux variantes. Petit lot de suite : la contre-revue tient les déplacements établis par le moteur pour un geste comme partie de ce geste (lot 177). Suite complète sur la fusion (`tools/tests.py --processus 2`, `f415db4`) : **2 258 tests, 16 ignorés**, verte (2 283,7 s), `tenir.py` ayant été touché aussi par le lot 167 c.

- Branche `codex-sol-surface`, fusionnée, lot **173**, base `79594e4` :
  `operations.compiler` résout via `deplacement_objet.destination_depot` une
  surface nommée `sol`, perçue dans la salle courante, comme `destination: sol`.
  Dépôt sur la case de Corvus pour déplacement, prélèvement, séquences et
  improvisation ; murs/plafonds/sols distants ou non perçus refusés avec `attendu`.
  Neuf ciblés verts, console/MJ simulé, antichambre/cour, monde et rendu rechargés.
  Suite unique : **2 251 tests, 259 fichiers, 1 295,595 s**, zéro erreur/ignoré,
  deux échecs MiMo historiques `6 != 5`. Relais 4 h × quatre graines : états
  finaux/relevés/bilans/alertes identiques à `main` `812ebe5`, trois `fige_presse`
  par côté ; références relues, aucune comparaison de temps. PC fixe partagé,
  au plus deux travailleurs réduits. **Luna non validée : coffre illisible**,
  première exécution en erreur avant réponse modèle ; commandes des deux passes
  à reprendre dans `artifacts/sol-173/luna-a-jouer.txt`. Aucun fichier réservé
  du lot 172 modifié ; aucune clé de signature configurée ; `main` intacte.
  [Rapport 173](taches/rapport-codex-173-sol-surface.md) ; bruts exclusivement
  `C:/Users/msics/donjon/artifacts/sol-173/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Validation Luna jouée par l'orchestrateur (coffre illisible pour l'agent) : deux passes poser-sol-atelier/poser-sol-relais contre cdaf371, 4 → 4 appels/tour, aucun refus de destination ni repli des deux côtés ; atelier une passe 3,00 → 3,18 appels/tour, refus 3 → 5, aucun sur une destination (vue partielle, sens d'un compte, pierre distincte : familles connues). Bruts artifacts/sol-173/ et bancs-multi 20261027-081013 / 081145.

- **Branche `codex-garder-proteger-c`, fusionnée**, lot **167 c / A4b
  partiel**, base `1aba0df`, code `13fde5f` et `5f69840` : responsabilités
  communes profil/agendas `protéger`, sans doublon ; appels, cris, défense,
  interposition, perception, témoins, réanimation et secours aux liens.
  Mort crue : fin avec cause publiée après choix, sans renaissance ; position
  inconnue non terminale. Épreuves en données de tests, aucun agenda historique
  ajouté. Gorm/Ilse appelle et accourt ; deux protecteurs de Brune rejoignent
  leur poste et avertissent ; monde/rendu rechargés, laps entier/découpé.
  Sélections finales **36 puis 38 tests verts** (avec recouvrement).
  **16/16 empreintes 2 h identiques** à la base, quatre scénarios × quatre
  graines ; Relais 4 h × quatre graines, mesures identiques, passages horaires
  max moyens **6,25 → 6,25**, zéro usurpation/violation/bascule/plantage,
  trois `fige_presse` historiques de chaque côté. VERIFIER/spatial 0,2,
  Relais fixe 1985, 2 h : monde et rendu rechargés identiques.
  Coût Relais 4 h : **265 recherches / 3 058 nœuds** inchangés ; CPU
  indicatif 3,42/3,28 s, sans conclusion de vitesse. Suite unique : **2 255
  tests, 260 fichiers, 1 302,232 s**, deux échecs MiMo historiques `6 != 5`,
  zéro erreur/ignoré ; aucune seconde suite. Deux travailleurs réduits au plus.
  **Restent suivi vocal, fin sur départ cru, fins garder rendu/perdu/détruit,
  interposition d'un lieu.** Sans poste, `protéger` dort explicitement pour
  suivi vocal non pris en charge ; les secours restent actifs. Coût avec
  nouvel agenda actif non isolé. Pas de Luna ni fichier MJ réservé ; `main`
  intacte, aucune clé de signature configurée, branche seule poussée.
  Jonction temporaire des traces automatiques retirée ; aucun brut local.
  Bruts exclusivement
  `C:/Users/msics/donjon/artifacts/garder-167c/` ;
  [rapport 167 c](taches/rapport-codex-167c-garder-proteger.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Restent : suivi à portée de voix, départ cru du protégé, fins de garder, interposition devant un lieu ; aucun agenda historique ajouté.

- Branche `codex-consignes-degraissees`, **non fusionnée**, lot **170** (L6), `b503242` : doublons retirés des consignes
  d'interprétation, **−2,7 %** (39 910 → 38 828 caractères), suite verte, empreintes identiques. Luna deux passes contre
  `cdaf371` : appels/tour 3,24 → 3,30, **s/tour 10,51 → 11,42**, **relances 14 → 19**, refus 21 → 25, replis 3 → 1 ;
  faisabilité de l'atelier manquée dans une passe, avec une réponse qui parle du « dossier ». Rejeu des refus non joué.
  **Mis en attente** (gain faible, signes de régression ; l'agent ne le propose pas à la fusion) : décision à l'utilisateur.

- Branche `codex-mesures-resolues`, **diagnostic, fusionnée**, lot **171**,
  base `06cfe9e` : les trois refus de mesures (`force-4c-fuir` p1/p2 t1,
  `atelier` p2 t8) sont faux ; aucune source nécessaire absente. Cumul de deux
  pas mal lu, destination pourtant fournie par le geste résolu, coordonnées
  équivalentes rejetées avec citation altérée. L’hypothèse d’une autre
  affirmation sans fondement expliquant ces refus est retirée. Une preuve de
  valeurs ne suffit pas à exempter les phrases entières ; décomposition typée
  à décider, attestations canoniques à évaluer comme piste limitée aux reprises
  exactes. **Aucun code, appel Luna ni test**, sur instruction de l’orchestrateur ;
  aucune correction ou garantie après recharge revendiquée. Extraits et empreintes
  des trois fils dans `C:/Users/msics/donjon/artifacts/mesures-171/diagnostic-audits.json`.
  Pas de clé de signature configurée ; `main` intacte.
  [Rapport 171](taches/rapport-codex-171-mesures-resolues.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Trois faux refus sémantiques, aucune source manquante. Décision de conception à l'utilisateur : décomposition typée des affirmations de l'audit, ou attestations canoniques de positions et de totaux de déplacement réutilisables par la preuve exacte.

- **Branche `codex-garder-proteger-b`, fusionnée**, lot **167 b / A4b
  partiel**, base `f5eb72b`, code `57cf8fe` puis `70717fb` : sorte `garder`
  objet/lieu sur le plan commun, interposition prioritaire pour sa charge,
  responsabilités partagées avec les pulsions et `prix_gardes` sans somme,
  publication différée, sommeil/réveil et fin à l'échéance. Épreuves en données
  de tests : Anselme/ballot et autres gardiens, monde/rendu rechargés,
  découpage ; aucun agenda historique ajouté. **Restent `protéger`, fins de
  garde pour bien rendu/perdu/détruit, interposition d'un lieu sans objet.**
  29 ciblés distincts verts, réveil compris. Suite unique : **2 246 tests,
  258 fichiers, 2 209,27 s**, zéro erreur/ignoré, deux échecs MiMo historiques
  `6 != 5` laissés ; aucune seconde suite.
  **16/16 empreintes 2 h identiques** à l'intégration `6d87361`, quatre
  scénarios × quatre graines. Auberge 4 h × quatre graines : mesures identiques,
  passages horaires max moyens **13,75 → 13,75**, seul noir long historique,
  aucune boucle nouvelle détectée. VERIFIER/spatial 0,2, auberge fixe 1985,
  2 h : monde/rendu rechargés identiques. Coût 4 h : **201 recherches /
  4 220 nœuds** inchangés, CPU indicatif 9,88/9,91 s, poste partagé.
  Un travailleur réduit ; aucun Luna, fichier MJ réservé ni `main` modifiés.
  Vérification au-delà du créneau pour cohabiter ; aucune clé de signature
  configurée, commits non signés, branche seule poussée.
  [Rapport 167 b](taches/rapport-codex-167b-garder-proteger.md) ;
  bruts exclusivement `C:/Users/msics/donjon/artifacts/garder-167b/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Restent : protéger, fins rendu/perdu/détruit, interposition d'un lieu sans objet ; aucun agenda de garde historique déclaré, coût d'un agenda actif non isolé.

- Branche `codex-silence-rappel`, fusionnée, lot **169**, base `27b5268` :
  définition temporelle commune de l'extraction `rappels` dans `narration.py`.
  L'issue courante reste contrôlée par ses faits, sans comparaison au passé.
  Quatre audits de silence concernés ; les deux rappels de la crypte ne sont
  pas des silences, contrôle maintenu. Silence de Brune encore contestable
  au regard de « te répond ». **17 ciblés verts**, console et MJ simulé,
  deux scènes de témoins, absence de réponse, faux rappels refusés ; état complet
  et rendu identiques après recharge. Suite complète unique : **2 235 tests,
  257 fichiers, 1 957,560 s, zéro erreur/ignoré**, deux échecs MiMo historiques
  `6 != 5` ; trois nouveaux tests verts dans leur version finale. Deux travailleurs
  réduits, l'un suspendu pendant les calculs du lot voisin.
  **Aucun appel Luna** : revue automatique bloquante sur les 60 appels de rejeu
  demandés, interprétés comme dépassant deux exécutions et une passe.
  Commandes dans `luna-a-jouer.txt` ; références `cdaf371` exclusivement relues.
  **Critère 95 non mesuré, amélioration sémantique non certifiée**.
  Pas de fichier réservé ni de moteur autonome modifié ; `main` intacte.
  Aucune clé Git de signature configurée. [Rapport 169](taches/rapport-codex-169-silence-rappel.md) ;
  bruts exclusivement `C:/Users/msics/donjon/artifacts/silence-169/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Validation Luna jouée par l'orchestrateur (revue automatique de l'agent bloquante) : rejeu de six audits, cinq essais par côté, refus base → lot 0→0, 5→5, 5→5, 1→0, 0→1, 0→0 (vrais rappels de Gorm toujours refusés 5/5, critère du lot 95 tenu) ; passe Luna echanges 4,67, noms-dialogue 3,25, soir-noir 4,6 appels/tour, aucun repli ni incident. Bruts artifacts/silence-169/ (PC fixe).

- Branche `codex-faits-a-la-demande`, **non fusionnée**, lot **166** (L7 partiel), `0ea6047` : surfaces génériques omises
  quand elles sont intactes, vides et sans usage (identifiants vus conservés) ; autres catalogues inchangés faute de critère sûr.
  `faits` d'interprétation **−3,9 %**, fiches de surfaces 927 → 501 caractères ; mais **préfixe d'entrée commun 10 959 → 8 113**
  caractères (les surfaces envoyées varient d'un tour à l'autre), contraire à l'objectif du fournisseur local. Validation Luna
  du code final et rejeu des refus non faits. **Mis en attente par l'orchestrateur** : gain faible, risque sur le préfixe local ;
  décision à l'utilisateur. Bruts `artifacts/faits-166/`.

- **Branche `codex-garder-proteger`, fusionnée**, lot **167 / A4b partiel**,
  base `45d07fb`, code `d230e4a` puis `0bdfee4` : interposition sur approche
  observée d'une charge ou d'un protégé du profil, marche réelle vers le poste,
  avertissement typé enregistré avant affichage, épreuve relationnelle commune
  en cas de persistance. Joueur compris parmi les approchants ; aucune violence
  ajoutée ni information privée de charge dans la parole. Huit ciblés verts,
  dont Anselme/ballot et autre gardien, recharge et découpage ; présence immobile
  31 minutes sans répétition. **Sortes d'agenda `garder`/`protéger` non livrées**,
  suivi vocal/appel sur ce socle et hystérésis générale restent à faire.
  Suite unique : **2 240 tests, 257 fichiers, 1 309,96 s**, zéro erreur/ignoré,
  25 échecs bruts : 23 assertions historiques adaptées, **24 repris verts**,
  deux MiMo historiques `6 != 5` laissés. **8/8 empreintes Relais/auberge
  identiques**, mine/crue différentes (approches mémorisées, postes et paroles).
  Banc rapide 4 h × quatre graines × auberge/mine/crue : zéro arrêt, usurpation,
  violation, poussée ou boucle nouvelle détectée ; passages **13,75/8/21,5 →
  13,75/8,25/20**, vols vus **0/0,5/1,5 → 0/0,25/1,5**, eau crue
  **21,25 → 17,5 PNJ·min**. Josse sous devoir déjà satisfait : observation
  déplacée de 2024/130 min à 1985/125 min, à surveiller. VERIFIER + spatial 0,2,
  auberge fixe 1985, 2 h : monde et rendu rechargés identiques. Coût auberge
  4 h : **201 recherches / 4 220 nœuds** inchangés ; CPU indicatif 8,17/10,19 s,
  charges différentes, aucun surcoût isolé conclu. Références réutilisées,
  seuls manques calculés ; deux travailleurs réduits au plus pour ce lot.
  Pas de Luna ni fichier MJ réservé modifié ; `main` intacte. Pas de clé de
  signature configurée, commits non signés ; branche seule poussée.
  [Rapport 167](taches/rapport-codex-167-garder-proteger.md) ; bruts exclusivement
  `C:/Users/msics/donjon/artifacts/garder-167/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Les sortes d'agenda garder et protéger restent à faire. À surveiller : Josse fige_presse déplacé de mine 2024 à mine 1985 (devoir déjà satisfait).

- Branche `codex-relances-168`, **non fusionnée**, lot **168**, `841f5d1` : attribution des relances de la vérification
  Luna 227c496 (lot 165), **24 → 41** sur 64 parties communes : comptes omis ou engagement mal lu **10**, rappels hors avis
  (silences actuels pris pour des rappels absents) **6**, avis désormais typés et relus **4** (légitime, lot 164), mesures
  résolues **3**, gestes **2**, lumière **2**, perception/savoir/sources/voix d'auteur **14**. Correction partielle de la
  famille des comptes (examen obligatoire de chaque compte dû/rendu) : refus de comptes **42/55 → 20/55** au rejeu, mais
  huit audits perdent plus d'un refus sur cinq : **critère du lot 95 non atteint, non fusionnée**. Même famille que les
  lots 117 b/117 c (`codex-comptes-recit-c`, en attente) : **décision du 2026-10-27 : abandonnée**, comme 117 c, au profit des comptes
  écrits par le moteur (lot 180). [Rapport 168](taches/rapport-codex-168-relances.md) sur la branche ; bruts `artifacts/relances-168/` (`attribution.json`).

- **Vérification Luna 227c496**, lot **165**, branche
  `codex-verif-luna-227c496` : aucun code changé, deux passes des 34 scripts,
  **68 parties / 184 tours MJ / 590 appels**, trois processus réduits au plus,
  copies seulement. **68/68 parties identiques au cache**, référence `cdaf371`
  exclusivement relue, 114 fichiers contrôlés inchangés. Sur les 64 communs :
  **542 → 572 appels**, **3,01 → 3,18 appels/tour**, **10,03 → 10,72 s/tour**,
  médiane **9,16 → 8,59 s** ; relances **24 → 41**, refus **48 → 52**,
  replis **1 → 2**, cache **2 301 312 → 4 262 016** jetons. Aucun gain causal
  de vitesse établi. **Avis 6/6**, achats payés/livrés 2/2, Gorm remboursé 2/2,
  fausse absence dans le noir non reproduite. L5 : refus locaux en un appel ;
  L4 : propositions distantes persistantes. L8 : quatre poses abouties, deux
  après refus de destination du sol. Traîner/enfermer toujours refusés à tort ;
  improvisé typé tuer et refusé justement, geste improvisé non exercé.
  N7 historique non réexercé (aucun rappel du nom proposé). Faux refus de
  coordonnées, pas résolus, témoins actuels et comptes/engagements documentés
  comme petits lots à reprendre ; aucune correction ni garantie générale.
  Zéro incident technique, budget épuisé, audit illisible ou erreur de recharge.
  Monde complet et panneaux après recharge non conservés : certification limitée
  aux projections/textes/traces disponibles. Aucune suite moteur relancée,
  aucune clé de signature configurée, branche seule poussée, `main` intacte.
  [Rapport 165](taches/rapport-codex-165-verif-luna.md) ; bruts exclusivement
  `C:/Users/msics/donjon/artifacts/verif-luna-227c496/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Relances 24 → 41, replis 1 → 2, s/tour moyenne 10,03 → 10,72 (médiane 9,16 → 8,59), cache 2,3 → 4,3 M jetons : main non avancée, décision à l'utilisateur. Petits lots désignés : cause des relances supplémentaires (lot 168), repères publics du sol, restes de force (traîner, enfermer).

- **Branche `codex-survie-en-route`, fusionnée**, lot **163**, base `ab7a2e2` :
  sortie des séjours humides sans attendre l'inquiétude ou 100 cm prévus ;
  traversées admissibles et gestes finis conservés, attente/répit/réflexe
  réévalués. Préfixe accompli commun à la lecture et à l'exécution ; attente
  dans `_entrees` seulement lorsque l'eau est active. Captures historiques
  reconstituées exactement : Brune 135/355 rejoint le sec, la seule ancienne
  fonction la laisse dans l'eau ; Ilse 490 sans recours cru, réserve vue ouverte
  relance sa demande, dernière part prise par Brune. Monde complet/rendu après
  recharge et découpage identiques, autre scène à deux personnes.
  **86 ciblés distincts verts après reprises** ; suite unique **2 226 tests,
  255 fichiers, 2 109,456 s, zéro ignoré**, cinq échecs/une erreur bruts :
  quatre hypothèses de scènes adaptées et reprises vertes, deux MiMo historiques
  `6 != 5` laissés. **12/12 empreintes** Relais/mine/auberge 2 h identiques,
  références relues ; VERIFIER/spatial 0,2 crue 2024 2 h sans écart/borne/plantage.
  Crue 4 h × quatre graines : eau **92,5 → 21,25**, attente **13,75 → 21,25**,
  passages **15,5 → 21,5** ; aucune nouvelle alerte/plantage/usurpation.
  Crue native 2024 12 h : eau **210 → 30**, Brune mouillée 135–360 **13 → 1**
  relevés (16 historiquement), Ilse faim 100 en attente **0 → 0** (47 historiquement).
  Attente **120 → 370**, passages **14 → 34** ; nouvelle alerte Brune sans but
  305 min conservée, vivres crus épuisés à 435, faim 100 finale sans nourriture
  garantie. Monde et rendu à 720 stables après recharge. **Pas de garantie
  générale d'absence de navettes/attentes.** Pas de Luna ni fichier MJ réservé
  modifié ; `main` intacte. Suite à deux travailleurs réduits, un suspendu pour
  cohabiter ; vérification au-delà du créneau. Aucune clé de signature : commit
  non signé, branche seule poussée. [Rapport 163](taches/rapport-codex-163-survie-en-route.md) ;
  bruts exclusivement `C:/Users/msics/donjon/artifacts/survie-163/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Eau 92,5 → 21,25 PNJ·min (crue 4 h) et 210 → 30 (crue 2024, 12 h) ; en contrepartie attente urgente 13,75 → 21,25 et passages max 15,5 → 21,5 (34 en crue 2024), sans boucle courte relevée : à surveiller à la prochaine vérification d'intégration. Attente d'Ilse justifiée par ses croyances (réserve verrouillée, aucun plan).

- **Branche `codex-avis-saisie`, fusionnée**, lot **164**, base `5bf8840` :
  définition commune d'`avis` clarifiée : annonce d'une menace future, même
  certaine et sans échéance ; horizon de calcul distinct du sens de la parole.
  Aucun effet moteur ni fichier réservé aux lots 161/163 modifié. Douze tests
  d'avis et neuf voisins verts ; trois saisies réelles, réception/faits dits,
  parole ordinaire et refus de lieu inconnu, monde et rendu rechargés.
  Luna : **6/6 avis**, référence `cdaf371` **3/6** exclusivement relue ;
  quatre parties, **54 → 65 appels / 14 tours MJ**, un repli narratif sur
  l'achat accepté de `soir-appel`, zéro erreur technique ou de recharge.
  Suite complète unique : **2 224 tests, 254 fichiers, 2 270,737 s**, zéro
  erreur/ignoré, deux échecs MiMo historiques `6 != 5` ; aucune seconde suite.
  Un worker réduit pour cohabiter avec 163 ; vérification au-delà du créneau.
  Le typage libre reste sémantique : carte entièrement fausse et raccourci
  des mots exacts encore possibles ; aucune garantie exhaustive annoncée.
  Aucune clé de signature configurée ; livraison non signée, branche seule
  poussée, `main` intacte.
  [Rapport 164](taches/rapport-codex-164-avis-saisie.md) ; bruts exclusivement
  `C:/Users/msics/donjon/artifacts/avis-164/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Avis typés 6/6 contre 3/6 ; appels/tour 3,86 → 4,64 sur les quatre parties (avis désormais relus, comme au lot 128).

- **Branche `codex-consignes-invariantes`, fusionnée**, lot **161 / L3**,
  base `c22541b` : consignes d'interprétation permanentes, quatre règles techniques
  et parole présentes à chaque tour ; indications du refus courant en entrée.
  **7/7 → 0/7 variations** sur huit captures Relais/atelier, consignes moyennes
  **34 259,75 → 39 910 caractères**. Quatre parcours console identiques à la base,
  état complet et rendu rechargés. Première passe **27 ciblés verts** ; suite
  complète unique **2 214 tests, 253 fichiers, 16 ignorés, zéro échec/erreur,
  2 060,44 s**, deux travailleurs réduits après la fin du calcul d’intégration.
  Deux nouveaux tests L3 et neuf tests cache/local verts dans cette suite. **Validation Luna** :
  « passe Luna faite par l'orchestrateur, à compléter » (rubrique réservée ; aucune
  passe exécutée ici). Commande déposée dans `luna-a-jouer.txt`. Mesures Luna et
  critère des refus à compléter par l'orchestrateur, qui poussera la branche.
  Commits locaux non signés ; aucune poussée par cet agent. `main` intacte.
  [Rapport 161](taches/rapport-codex-161-consignes-invariantes.md), bruts exclusivement
  `C:/Users/msics/donjon/artifacts/consignes-161/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Passe Luna jouée par l'orchestrateur (revue automatique de l'agent bloquante), deux passes, sept scripts contre cdaf371 : appels/tour 3,24 → 3,07, s/tour 10,5 → 9,9 (médiane 9,6 → 9,4), replis 1,5 → 1,0, obstacles 16 → 12, relances 7 → 6,5, refus 10,5 → 11 ; jetons cachés d'interprétation 567 808 → 1 141 120. Rejeu des refus du lot 95 non fait. Bruts artifacts/consignes-161/.

- Branche `codex-audit-invariant`, **non fusionnée**, lot **162** (L2 b, schéma d'audit narratif invariant), `fd90d59` :
  schéma invariant atteint (**50/72 → 0/76** variations), contrôles déterministes identiques sur les 86 audits archivés,
  suite verte hors MiMo. **Refusée à la relecture** : critère de conservation des refus du lot 95 non atteint (trois audits
  perdent plus d'un refus sur cinq : pierre non perçue 3→1, approbation accompagnant une parole 3→0, conduite/éclairage 4→2),
  relances **13 → 22**, audits refusés **14 → 23**, replis **0 → 2**, un illisible ; **11,13 → 11,49 s/tour**. La forme du
  rapport (liste indexée au lieu de clés) change le comportement de Luna. À reprendre autrement ou abandonner : décision à
  l'utilisateur. [Rapport 162](taches/rapport-codex-162-audit-invariant.md) sur la branche ; bruts `artifacts/audit-162/`.

- **Branche `codex-amener-social-e`, fusionnée**, lot **146 e**, base `116be91` :
  sous-buts sociaux d'amener livrés : parole dans le graphe, avis de menace,
  demande `confier`, refus motivé, sommeil/réessai sur croyance nouvelle,
  accompagnement propre et attente sans navettes. Abandon reçu : aide attendue
  correspondante invalidée ; régression prouvée sur deux scènes avec la base.
  Gorm reçoit l'évacuation d'Ilse et Brune à la galerie. Scènes collectives
  2024/42 éclairées, route ouverte : Ilse puis Brune, atteint, état et rendu
  rechargés, laps continu/découpé identiques. Suite unique : **2 212 tests,
  252 fichiers, 1 084,053 s**, zéro erreur/ignoré, sept échecs : deux MiMo
  historiques et cinq assertions de scènes eau/services/marchés désormais
  perturbées par l'évacuation ; scènes isolées, assertions conservées,
  **49 tests repris verts**, aucune seconde suite. VERIFIER + spatial
  0,2 : crue fixe 42/2024 × 2 h sans arrêt, monde et rendu rechargés identiques.
  Douze empreintes Relais/mine/auberge identiques ; quatre crues sans arrêt
  ni usurpation, atteint sur 7/42 ; galerie finale **3/8 → 2/8**, eau
  **128,75 → 92,5 min**, passages horaires **13,25 → 15,5**. Reprise avant
  fusion : crue 1985 `116be91`/`eef4925`, torche **1/1 → 10/9** allumages/
  extinctions, captures avant premier allumage sauvegardées puis rechargées.
  Boucle introduite dans cette nuit par le lot : économie selon lumière de
  salle, plan selon lumière devant cible. `lumiere_devant_crue` partage
  désormais cette lecture, sans source portée ; capture réelle et autre cas
  Gorm/lanterne échouent avec la seule ancienne fonction, passent corrigés.
  **51 ciblés/voisins verts**, aucune nouvelle suite complète (correction locale).
  Quatre crues rejouées : aucun arrêt/usurpation/répétition de torche,
  **4/3** sur 1985, plus de rafale 213–218. Trois autres états complets et
  mesures identiques ; sur 1985, crochetage poursuivi, jets **19 → 25**,
  gestes **164 → 148**, recherches **1 203 → 1 177**. Galerie/eau/passages
  inchangés ; eau longue 2024 seule alerte conservée. Refus sociaux
  1985/2024 respectés, aucune évacuation universelle revendiquée. Préférence
  générale, seule portée vocale, réveil relationnel et coopération aux portes
  restent limités. Pas de Luna, fichier MJ réservé ni `main` modifiés.
  Deux calculs réduits au plus ; aucune clé de signature Git configurée,
  livraison non signée, branche seule poussée.
  [Rapport 146 e](taches/rapport-codex-146e-amener-social.md) ; bruts exclusivement
  `C:\Users\msics\donjon\artifacts\amener-146e\`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Reprise après relecture : la boucle de torche de Brune (crue 1985), introduite par le lot, venait d'une lecture de lumière différente entre planificateur (devant la cible) et décision de garder la source (salle) ; lecture commune lumiere_devant_crue, quatre crues sans répétition. Restent : maintien à la galerie (3/8 → 2/8), parole exigeant le contact, préférence générale entre lieux.

- **Branche `codex-schema-invariant`, fusionnée**, lot **158 / L2**, base
  `7adc788`, code `9a0ea10`, mesure `a2147fd` : huit modes et toutes les branches
  d'interprétation toujours présents, sources en chaînes, faits à `suite` nullable.
  Disponibilités refusées avec `attendu` avant audit, famille vérifiée, faisabilité
  sans geste refusée avant préparation. Consignes et voie d'achat du lot 159 intactes.
  **55 ciblés verts** : six modes indisponibles, branche incohérente, suite absente/null
  et source inconnue, Relais/auberge, état complet et rendu rechargés identiques aux
  témoins ; crypte/atelier, requêtes hors schéma, état et rendu identiques à la base.
  Suite unique : **2 205 tests, 250 fichiers, 16 ignorés, zéro erreur, 3 731,37 s**,
  un worker réduit après l'intégration. Un échec de mesure (suffixe de cache L1
  non reconstruit), corrigé par `sources.voie_cache`, **12 ciblés repris verts**
  sur quatre voies ; mesures recalculées hors réseau, aucune seconde suite.
  **8/8 empreintes 2 h Relais/auberge identiques** à la base, quatre graines ;
  huit références absentes rangées une fois. Six captures : outils moyens
  **22 760 → 30 003 caractères**, variations **4/4 → 0/4** ; bancs Luna
  **0/92 variations** d'interprétation, relances comprises. Deux passes, sept
  scripts distincts, **293 appels/88 tours MJ**, un repli, zéro incident/recharge.
  Référence `cdaf371` : neuf parties cachées, cinq absentes jouées une fois et rangées.
  Cache d'interprétation **646 144 → 982 784 jetons** ; aucun gain de secondes démontré.
  **Critère des refus atteint sur 16 audits/160 appels**, cinq rejeux par côté,
  perte maximale **1/5**, aucune erreur/rapport illisible. Faux souvenir de Gorm 5→4.
  **L2 partiel : audit narratif encore variable**, L3 intact, pas de serveur local
  mesuré ni garantie sémantique nouvelle. Vérification hors créneau après attente
  du calcul d'intégration. Copies seulement ; aucune clé de signature, commits
  non signés, branche seule poussée ; `main` intacte.
  [Rapport 158](taches/rapport-codex-158-schema-invariant.md), bruts `artifacts/schema-158/`.
  Fusionné sur l'intégration : conflits de documentation, de `tools/mesure_prompt.py` (même correction de la clé par voie des deux côtés, version de la branche gardée) et de `tests/test_cache_kv_local.py` (comparaison avec et sans l'ordre des sources sur le code courant gardée, sans nouvelle empreinte figée) ; `mj.py` touché aussi par les lots 150, 151 et 159, fusionné sans conflit textuel ; suite complète relancée. L'audit narratif reste variable (44/74) : suite de L2 à faire. Suite complète sur la fusion (`tools/tests.py --processus 2`) : **2 212 tests, 16 ignorés, une erreur** : `test_scenarios_libres.test_resultat_local_attend_une_sauvegarde_reussie_avant_affichage`, `StopIteration` des saisies simulées, intermittente déjà vue aux lots 54 et 83 ; fichier repris seul deux fois, vert (6 tests).

- **Vérification d'intégration 7adc788**, lot **160**, branche
  `codex-verif-integ-7adc788` : aucun code du jeu changé, aucun Luna, aucune
  suite complète ni référence rejouée ; `main` intacte. **49/49 nuits achevées**,
  deux calculs réduits au plus, en fond : 32 × 12 h, huit rixes × 8 h, cinq
  contrôles renforcés × 8 h, quatre hameaux × 12 h. Zéro plantage, violation,
  usurpation, mort ou écart de contrôle ; borne Lucien auberge 42/314 inchangée,
  retenu = optimum 73,4743. Crue 42 renforcée atteint **480 min**, ancien arrêt
  d'évaluation d'agenda absent. Brune crue 2024 : **68 → 8 passages** dans la
  dernière heure, fin des navettes à 688 ; pire passage global crue **68 → 30**.
  Aucune nouvelle alerte sur les 32 nuits principales ; deux anciennes alertes
  de la boucle supprimées. Brune dans l'eau et Ilse affamée en attente persistent,
  mêmes relevés qu'en `2d504ae` ; pas de preuve ici d'un recours disponible.
  Gorm : mêmes sommeils/réveils, trois agendas d'information atteints, cinq non
  atteints, aucun abandon ; aucun `amener` déclaré. Hameau 4/4 chroniques,
  mesures, récits et alertes identiques ; huit rixes aux mesures identiques.
  Cinq coups crue 2024 identiques, aucun captif attesté, captivité non recensée
  exhaustivement. Archives sans sauvegarde complète : rendu après recharge non
  certifié. 32 références `057766f` conformes au manifeste ; temps non comparés.
  Aucune clé de signature, commit non signé, branche seule poussée sans fusion.
  [Rapport 160](taches/rapport-codex-160-verif-integ.md), bruts et analyses
  `C:/Users/msics/donjon/artifacts/verif-integ-7adc788/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Défauts du lot 148 corrigés (crue 42 sous VERIFIER au bout, Brune 68 → 8 passages). Petit lot désigné : recours de survie réévalués pendant le trajet et l'attente (Brune dans l'eau 135-360, Ilse faim 100 en attente 490-720, crue 2024), après 146 e.

- **Branche `codex-amener-social-d`, fusionnée**, lot **146 d**, base `bd11a3d` :
  livraison partielle, correctif moteur préalable. Une fermeture de PNJ préparée
  avant la destruction ou le dégondage du battant pouvait refermer le passage,
  puis faire échouer la copie d'un devis sur `Passage incohérent`.
  `portes.valider_fermeture` partage les préconditions matérielles du joueur et
  des PNJ ; geste périmé refusé, état touché constaté, aucune fausse fermeture
  publiée. Deux scènes crue 2024/42 reproduisent l'erreur avec la fonction de la
  base, puis vérifient devis, monde complet et rendu après recharge ; **25 ciblés
  verts**. Suite unique : **2 204 tests, 251 fichiers, 1 250,899 s**, deux échecs
  MiMo historiques, zéro erreur/ignoré. **12/12 empreintes 2 h identiques** à
  `main` `812ebe5`, Relais/mine/auberge ; références relues sans rejeu.
  Crue 4 h × quatre graines : **4/4 états complets identiques** à `ef65e55`,
  galerie **3/8**, eau **128,75 min**, attente urgente **60 min**, passages
  horaires **13,25**, aucune boucle nouvelle/usurpation ni arrêt.
  `VERIFIER` + spatial 0,2 crue fixe 42 et 2024 × 2 h : sans arrêt.
  Deux calculs réduits au plus ; aucune clé Git de signature configurée,
  commit non signé, branche seule poussée.
  Le fil exact 2024/120 n'est pas reconstitué : cause capable de reproduire
  l'erreur prouvée, unicité historique non prouvée. Sous-buts sociaux et données
  d'évacuation non livrés, répétitions de plans non garanties. Aucun Luna ni
  fichier MJ réservé modifié ; `main` intacte.
  [Rapport 146 d](taches/rapport-codex-146d-amener-social.md), bruts exclusivement
  dans `C:\Users\msics\donjon\artifacts\amener-146d\`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Correctif du défaut révélé par le lot 146 c ; sous-buts sociaux d'amener toujours à faire (lot 146 e).

- **Branche `codex-achat-corrige`, fusionnée**, lot **159**, base `7adc788` :
  contrat commun de `pieces.objet` précisé dans `propositions.py` : source
  facultative des pièces, jamais bien acheté ; refus inchangé avec champ,
  valeur et correction exacte conservant le montant. Aucun retrait automatique,
  aucune consigne ni assemblage de requête changé. **Cinq ciblés verts**,
  achats planche/Aubin et bûche/Joss corrigés, payés, livrés puis état et fiche
  vérifiés après recharge ; source invalide refusée sans mutation.
  Luna une passe soir-appel/ressources/noms-dialogue : **43 → 45 appels / 11 tours**,
  **3,91 → 4,09 appels/tour**, achat exécuté et `planches_1` portée après recharge,
  aucun refus moteur/contre-revue, repli, arrêt technique ou défaut de recharge.
  Référence p1 `cdaf371` relue dans les archives copiées, empreintes du manifeste
  conformes ; cache d'origine absent. Premier lanceur de référence interrompu
  sans partie achevée ; branche jouée une seule fois. Correction historique
  prouvée par simulation, pas réémise naturellement par Luna ; aucune garantie
  de toute saisie libre ni gain de vitesse. Suite complète unique : **2 199 tests,
  249 fichiers, 16 ignorés, zéro erreur, 3 844,17 s**, un travailleur réduit,
  vérification au-delà du créneau. Trois échecs bruts : deux sous-tests de
  référence figée actualisés après comparaison des scènes à la base intacte,
  **neuf tests repris verts** ; un échec de `test_mesure_prompt` (clé de cache
  sans `:interpreter`) reproduit sur `7adc788`, laissé hors périmètre.
  Pas de clé de signature Git ; commit non signé, branche seule poussée.
  [Rapport 159](taches/rapport-codex-159-achat-corrige.md).
  Fusionné sur l'intégration : conflits de documentation et de la référence figée `prompt-prefixe-avant.json`, supprimée par l'intégration (le test du lot 150 compare désormais le code courant avec et sans l'ordre des sources ; `tools/mesure_prompt.py` porte déjà la clé par voie) ; aucun fichier de code commun depuis la base.

- **Branche `codex-amener-social`, fusionnée**, lot **146 c**, base `ef65e55` :
  livraison partielle, abandon d'`amener` pour coupure prouvée par les positions
  et hauteurs d'eau crues, même avec toutes les portes ouvertes. Cause conservée,
  aucun refus de route déduit d'une recherche bornée ou d'une serrure.
  **Sous-buts sociaux non livrés** : tentative retirée après répétitions et arrêt
  « Passage incohérent », crue 2024/120. Données de la crue inchangées.
  **25 ciblés verts**, deux personnes/deux destinations coupées et une route
  ouverte, état/rendu rechargés. **2 188 tests, 249 fichiers, 1 293,96 s**, deux
  échecs MiMo historiques, zéro erreur/ignoré ; suite unique à deux processus réduits.
  **12/12 empreintes 2 h identiques** à `ef65e55` (Relais/mine/auberge).
  Crue 4 h : **4/4 états complets identiques** à la base ; galerie **3/8**,
  eau **128,75 min**, attente urgente **60 min**, passages horaires **13,25**,
  inchangés. VERIFIER/spatial 0,2 sur crue 42 fixe × 2 h sans arrêt ; coût
  crue 1985 fixe × 4 h inchangé : **1 430 recherches, 83 066 nœuds**.
  [Rapport 146 c](taches/rapport-codex-146c-amener-social.md), bruts dans `artifacts/`.
  Aucun Luna ni fichier réservé modifié ; `main` intacte.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Sous-buts sociaux retirés : leur tentative a révélé un défaut moteur (crue 2024 à 120 min, « Passage incohérent » dans la copie d'un devis, porte détruite/détachée non ouverte) ; lot 146 d pour l'isoler.

- **Branche `codex-force-restes`, fusionnée**, lot **157**, base `af1b8f3` :
  destination du corps dans le titre et repère public/identifiant dans le dossier ;
  salles nommées dans les effets et faits des désignations, portes avec type,
  lieux et personnes perçues ou mémorisées, contact de la porte explicité.
  Tests force et console/recharge verts (deux seuils, deux portes/personnes),
  38 voisins verts, reprise finale 27 tests verte ; **2 185 tests, 247 fichiers, 1 310,441 s**, deux échecs MiMo historiques
  `6 != 5`, zéro erreur/ignoré, suite complète unique. Resserrement final des
  références de lieu et des issues avant action après son démarrage : 27 ciblés
  finaux verts en 30,972 s, deux calculs au plus.
  Luna deux passes des trois restes et une des huit autres scripts, référence
  `cdaf371` relue sans rejeu : **60 → 60 appels / 22 tours MJ**, zéro repli,
  incident technique ou erreur de recharge. Traîner **6/4**, enfermer **3/7**,
  improvisé **3/3** ; **critère non atteint**, faux refus persistants.
  Projection `ouverture=False` clarifiée en `fermer` après la passe, tests finaux
  verts, pas de troisième passe Luna. Aucun nouvel état corporel inventé relevé,
  monde complet/corps non archivés par le harnais Luna : garantie limitée aux
  fils. Aucun effet moteur, règle lexicale, instruction de contre-revue ou
  module réservé aux autres lots changé. Deux calculs réduits au plus ; aucune
  clé de signature Git, commit non signé, branche seule poussée, `main` intact.
  [Rapport 157](taches/rapport-codex-157-force-restes.md),
  bruts `artifacts/force-157/` de ce worktree.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Critère 4f toujours non atteint (traîner, enfermer : faux refus sémantiques de la contre-revue) ; projection ouverture=False → fermer non revalidée par Luna.

- **Branche `codex-rappel-ordre`, fusionnée**, lot **156**, base `7cc0d16` :
  dossier `narration.echanges_passes` trié, ordre chronologique et antériorité
  explicites par rapport à la réponse non encore prononcée, révision courante.
  Cause N7 confirmée dans le fil `cdaf371` p2 : extraction établie mais portée
  contradictoire par inversion 2/5. **14 ciblés verts**, deux rappels rapportés,
  faux rappels refusés, état et texte rechargés. Luna une passe des trois scripts :
  **55 appels / 13 tours MJ**, aucun repli/erreur technique/recharge. `soir-noir`
  **4,80 appels/tour**, `soir-voix` **4,50**, `noms-dialogue` **3,25** ; références
  `cdaf371` relues sans rejeu, `soir-voix` absent du cache.
  **N7 reste ouvert** : au n°5, le rappel du nom n'est plus rejeté pour l'ordre,
  mais une décision actuelle est extraite à tort comme un passé jamais dit ;
  sept appels et rappel retiré. Pas de garantie sémantique générale.
  **4/4 empreintes Relais 2 h identiques** à `7cc0d16`, état complet, chronique,
  mesures ; références absentes calculées une fois, rangées sans rejeu.
  Suite complète unique : **2 179 tests, 246 fichiers, 1 273,205 s**, deux échecs
  MiMo historiques `6 != 5`, zéro erreur/ignoré. Aucun fichier réservé ni `main`
  modifié. Aucune clé de signature configurée : commit non signé, branche poussée.
  [Rapport 156](taches/rapport-codex-156-rappel-ordre.md), bruts
  `artifacts/rappel-156/`. Deux calculs réduits au plus, Luna avant la suite.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. N7 non clos : l'audit ne rejette plus le rappel pour sa chronologie mais extrait le refus actuel de se nommer comme un passé jamais dit ; jugement sémantique.

- **Branche `codex-portee-locale`, fusionnée**, lot **151**, base `4641dc3` :
  `HorsDePortee` rendu directement par `reponse_du_moteur`, sans explication
  ni audit, sans déplacement ni effet mécanique. Autres refus et paroles
  attendues sur leurs voies ordinaires ; aucun assemblage, consigne, schéma
  ou fournisseur modifié. **28 ciblés verts puis cinq tests de portée verts**,
  barricade à six mètres, prise éloignée, fiche au contact et cible inconnue
  corrigée ; état et rendu après recharges. Suite complète unique : **2 162 tests,
  242 fichiers, 16 ignorés, 3 514,6 s, zéro échec d’assertion, une erreur TUI
  Windows** de remplacement temporaire ; seul test repris vert, sans changement
  ni seconde suite. Un worker réduit pour cohabiter, vérification au-delà du créneau.
  Luna une passe, neuf scripts : **72 → 80 appels / 29 tours MJ**, 2,48 → 2,76
  appels/tour, 7,96 → 8,68 s/tour ; coup de pied Relais et saut avec perche
  **3 → 1 appel** chacun. Aucun repli, incident technique ou défaut de recharge.
  Neuf références `cdaf371` manquantes jouées une fois et cachées.
  **L5 partiel** : premier refus seulement, recensement de toutes les cibles
  éloignées et validité du reste de la proposition non garantis ; un essai de
  collecte retiré a révélé les contrôles de distance répartis dans les préparateurs.
  Une reprise coordonnée du moteur dépasse les fichiers autorisés dans ce lot.
  Code `3805393`. Aucune clé de signature configurée ; commits non signés, branche seule poussée.
  [Rapport 151](taches/rapport-codex-151-portee-locale.md).
  Fusionné sur l'intégration après le lot 150 : conflits de documentation seulement ; `mj.py` touché aussi par le lot 150 (ordre des requêtes), fusionné sans conflit textuel ; suite complète relancée. Question de l'agent (recenser toutes les cibles éloignées en reprenant les préparateurs) non retenue : le joueur lit le premier refus puis s'approche. Suite complète sur les fusions 150 et 151 (`tools/tests.py --processus 2`) : **2 198 tests, 16 ignorés, trois échecs de tests**, aucun du jeu : l'empreinte figée des requêtes du lot 150 (prise avant les lots 151, 152, 154) remplacée par une comparaison avec et sans l'ordre des sources sur le code courant ; `tools/mesure_prompt.py` reproduit la clé de cache par voie du lot 150. Les deux fichiers repris : 12 tests verts.

- **Branche `codex-prompt-prefixe`, fusionnée**, lot **150**, base `4641dc3`,
  code `9a55cc1` : portage ciblé de `9d53229`, ordre commun des faits et entrées,
  contexte avant propositions d’audit, révision en fin de relance, clés par voie,
  fournisseur local et quatre slots. Consignes conditionnelles, résultat et schéma
  conservés ; aucun refus du lot 151 modifié. **Neuf ciblés verts**, requêtes,
  état complet et rendu rechargé identiques à la base sur deux scènes console.
  Suite unique : **2 169 tests, 243 fichiers, 16 ignorés, zéro erreur, 3 530,46 s**,
  un travailleur réduit ; seul échec d’une ancienne assertion d’ordre entrée/enum,
  adaptée à l’égalité des clés avec multiplicité et reprise verte, sans seconde suite.
  **4/4 empreintes Relais 2 h identiques** à la base : chronique, mesures,
  état complet ; quatre références absentes rangées une fois, aucun rejeu.
  Luna : sept références absentes cachées une fois, branche deux passes,
  **21 parties, 132 tours, 454 appels**, aucun incident technique/recharge.
  Branche **3,52 / 3,36 appels par tour**, référence **3,43** ; secondes moyennes
  **12,29 / 11,67**, référence **10,70** ; replis **1 / 0**, référence **2**.
  **Aucun gain de vitesse démontré. Réserve de validation : critère brut du lot 95
  non atteint sur trois des huit audits rejoués cinq fois par côté (80 appels)** ;
  faux refus de comptes/parole mêlés aux motifs, aucune garantie par cause.
  Faux souvenir de Gorm refusé 5/5 des deux côtés. Serveur local absent,
  tests réseau simulé seulement ; L2/L3 et les limites sémantiques restent.
  Aucune clé de signature configurée ; commits non signés, branche poussée seule.
  [Rapport 150](taches/rapport-codex-150-prompt-prefixe.md), bruts `artifacts/prompt-150/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Réserve du rapport jugée non bloquante : les trois audits où la branche refuse moins sont des faux refus de comptes (remboursements d'Aubin conformes à l'issue) ; le refus juste (faux souvenir de Gorm) reste 5/5 des deux côtés. Aucun gain de vitesse démontré, attendu de L2/L3. Fournisseur local non mesuré (aucun serveur sur le laptop).

- **Branche `codex-fuite-lumiere`, fusionnée**, lot **155**, base `3b284b6` :
  fuite, abri et lumière partagent les auteurs de violence encore actifs selon
  les croyances. Leur lieu cru est exclu des recours de sécurité et coûte comme
  une présence crainte dans le parcours ; lectures couvertes par `_entrees`.
  Capture réelle crue 2024/680 rechargée : **68 → 8 passages de Brune en 40 min**,
  fin des navettes après 688 ; mêmes `data` et rendu en laps continu/découpé.
  Autre scène d'Ilse et réouverture des abris après fin du danger vérifiées.
  **16/16 empreintes 2 h identiques** ; audit 12 h crue 2024 : maximum
  **68 → 15 passages/heure**, aucune boucle nouvelle, usurpation ou mort.
  Banc rapide 4 h crue/rixe : **8/8 identiques**, mêmes alertes historiques ;
  VERIFIER + spatial 0,2 sur 2 h crue 2024 : zéro écart/borne/plantage.
  Suite complète unique : **2 180 tests, 247 fichiers, 1 230,13 s**, deux
  échecs MiMo historiques `6 != 5`, zéro erreur/ignoré, deux processus réduits.
  Audit final sur le dernier code : mêmes chroniques, mesures et relevés, hors
  temps de calcul. Aucun Luna ni fichier MJ réservé modifié ; aucune clé Git
  de signature, commit non signé, branche seule poussée sans fusion ; `main` intacte.
  [Rapport 155](taches/rapport-codex-155-fuite-lumiere.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Corrige la boucle fuite/lumière de la vérification 148 (crue 2024, Brune) ; reste à voir : Brune longtemps dans l'eau et Ilse affamée en attente dans la même nuit.

- **Branche `codex-poser-au-sol`, fusionnée**, lot **154 / L8**, base
  `0352f29`, moteur `8697169`, présentation corrigée `040a9a1` : `destination: "sol"` résolu dans le compilateur
  commun de `deplacer`/`prelever`, séquences et effets d'improvisation compris.
  Ancienne salle courante compatible, autre salle refusée avec `attendu` ;
  prélèvement direct déposé aux pieds de Corvus, état sauvegardé en lieux réels.
  Cinq nouveaux tests console/MJ simulé verts, torche et planche, scène et carte
  après recharge ; reprise ciblée finale 5/5. **2 174 tests, 245 fichiers,
  1 285,395 s**, suite complète unique à deux processus réduits, deux échecs
  MiMo historiques `6 != 5`, zéro erreur/ignoré. Banc rapide Relais quatre graines
  × 4 h : états complets, relevés, chroniques, récits, souvenirs et mesures
  **4/4 identiques** à `main` `812ebe5`, aucun plantage, trois `fige_presse`
  identiques par côté ; quatre références absentes rangées une fois.
  Luna une passe, atelier/Relais et deux dépôts ciblés : **72 appels/21 tours MJ**,
  commun **64 → 62 appels/19 tours**, référence `cdaf371` relue sans rejeu.
  Relecture : le faux refus atelier était une lacune du lot, corrigée dans le
  titre, l'information et la projection des effets du dossier de contre-revue :
  « au sol, à tes pieds », destination publique `sol`, salle interne préservée
  dans les seuls effets exécutables. Même source pour les prélèvements, séquences
  et branches d'improvisation ; aucune consigne d'audit ajoutée. **55 tests ciblés
  verts**, dont dossier sans mutation ; pas de nouvelle suite complète pour cette
  reprise de présentation. Nouvelle passe demandée des deux dépôts et d'atelier :
  **40 appels/13 tours MJ**, couteau et torche posés sans refus, quatre appels chacun,
  atelier **32/11**, contre 39/11 en référence. Aucun refus de destination,
  repli/incident technique/erreur de recharge/mention sans fondement détectée.
  Deux tours avec refus de matériau/portée à l'atelier. Les surfaces génériques
  proposées lors de la première passe sont signalées pour L7, sans traitement ici.
  Aucun repli/incident technique du jeu/erreur de recharge. Export HTML initial
  interrompu puis régénéré hors ligne, aucun script rejoué. Pas de clé de
  signature : commits non signés, branche poussée seule ; `main` intact.
  [Rapport 154](taches/rapport-codex-154-poser-au-sol.md), bruts dans
  `artifacts/poser-sol-154/` de ce worktree.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Reprise après relecture : le titre, l'information et le dossier de contre-revue disent « au sol, à tes pieds » (faux refus de l'atelier levé, deux dépôts Luna sans refus). Confusion avec les surfaces génériques signalée pour L7.

- **Branche `codex-agendas-amener-b`, fusionnée**, lot **146 b**, base
  `b5a23bb`, code `36e1b33` puis `268e190` : complément prioritaire du lot 148,
  pureté de l'évaluation des candidats. Registre temporaire, transitions et
  chronique publiées après un choix complet ; rien pour un devis isolé ou un
  choix interrompu, comme les efforts bornés du lot 87. Le sommeil d'un agenda
  essayé sans plan reste enregistré même si un autre candidat fournit le plan
  (précision demandée et confirmée). Test neuf échouant sur la base intacte,
  crue 42 fixe/tirée 2 h avec `VERIFIER` et `spatial.VERIFICATION` 0,2 sans arrêt :
  état complet, chronique, mesures, récit et souvenirs identiques à la base
  non vérifiée. **12/12 empreintes 2 h identiques** (Relais/mine/auberge).
  **4/4 crues 4 h identiques** en état complet ; aucune boucle nouvelle,
  plantage/usurpation/violation ; mêmes constats historiques. Attente urgente
  20 min, eau 128,75 min, passages horaires maximum 13,25, Ilse/Brune à la
  galerie en fin de nuit 3/8, inchangés. Références manquantes cachées sans rejeu.
  Coût crue 1985 fixe 4 h inchangé : 1 430 recherches, 1 092 neuves, 83 066 nœuds.
  Suite complète finale : **2 168 tests, 244 fichiers, 1 192,24 s, deux échecs
  MiMo historiques `6 != 5`, zéro erreur/ignoré** ; deux échecs reproduits seuls
  sur `b5a23bb`. Première suite interrompue au complément prioritaire, une seule
  suite achevée sur le code final.
  Livraison partielle du cycle de fin d'`amener` :
  Toutes les personnes crues au lieu donnent `atteint` ; destination crue ou
  attendue noyée : `abandonne`, cause sauvegardée. Aucune lecture des positions
  distantes, aucune renaissance terminale. Sinon sommeil explicite, sans demande
  ni transport ; données de la crue inchangées. **31 ciblés verts**, six fichiers,
  dont huit nouveaux tests : deux personnes/deux lieux, état et rendu rechargés,
  trois minutes entières/découpées identiques. **Amener reste incomplet** :
  préférence générale et avis, plus proche, portée vocale, demande autonome et
  refus durable/réveil, accompagnement, abandon pour route coupée et épreuve
  d'évacuation avec faim désespérée restent à faire. Aucun Luna ni fichier MJ
  réservé modifié. Deux calculs réduits au plus ; aucune clé de signature Git,
  commits non signés, branche seule poussée sans fusion.
  [Rapport 146 b](taches/rapport-codex-146b-agendas-amener.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Corrige l'arrêt VERIFIER de la vérification 148 (crue 42, minute 0). Restent d'amener : préférence et avis, portée vocale, demande autonome, refus durable, accompagnement, données de la crue (lot 146 c).

- **Branche `codex-dossiers-proches`, fusionnée**, lot **152 / L4**, base
  `45e9f95` : les dossiers atelier, franchissement, obstacles et espace prennent
  leurs sources dans `espace.objets_proches` (vue et `spatial.proche`), outils et
  installations compris. Les repères éloignés restent dans la vue ; les biens
  portés restent à portée. Sans coordonnées anciennes, aucune portée au sol
  supposée. Aucun changement de consignes, d'actions, de trajets ou de PNJ.
  Six nouveaux tests verts, console/MJ simulé, Relais/auberge/atelier, état et
  rendu après recharge ; 63 ciblés existants verts. Dix projections identiques
  hors dossiers : `faits` **136 247 → 129 655 caractères (−4,8 %)**,
  franchissements **6/10 → 2/10**, obstacles **4/10 → 2/10**.
  **8/8 empreintes 2 h identiques**, Relais/auberge × quatre graines ; référence
  absente cachée une fois, aucun rejeu. Luna une passe de neuf scripts, référence
  `cdaf371` cachée une fois : **84 → 77 appels / 29 tours MJ**, **2,90 → 2,66**
  appels et **9,3 → 8,1 s/tour** ; dix tours avec refus de chaque côté, aucun
  repli/erreur technique/recharge. Aucun dossier classé « aucun proche » après.
  **Critère des propositions distantes Luna non atteint** : encore deux actions
  et un détail bruts sur des cibles éloignées, refusés par le moteur ; réponses
  finales bornées à l'approche ou à la vue. Suite complète unique : **2 169 tests,
  244 fichiers, 1 242,46 s**, deux processus réduits ; deux échecs MiMo historiques
  `6 != 5`, zéro erreur/ignoré. Aucun rejeu de référence pour ces échecs déjà
  documentés. Pas de clé Git de signature ; commit non signé, branche poussée
  seule ; `main` intact.
  [Rapport 152](taches/rapport-codex-152-dossiers-proches.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Luna propose encore des gestes sur des cibles éloignées : refusés par le moteur, rendus locaux par L5 (lot 151).

- **Vérification Luna cdaf371**, lot **153**, branche
  `codex-verif-luna-cdaf371` : aucun code du jeu changé, `main` intact.
  Deux passes des 32 scripts, **64 parties, 352 saisies, 180 tours MJ,
  542 appels**, trois exécutions réduites au plus, copie exacte supprimée.
  64 parties rangées sous `cdaf371`, SHA-256 source/cache identiques ; référence
  `9a39738` relue sans rejeu, 63 fichiers inchangés. Commun : **445 → 448 appels**,
  **3,13 → 3,15 appels/tour**, **11,76 → 10,64 s/tour**, charges différentes.
  Ensemble : 3,01 appels/tour, 10,03 s/tour, médianes 2 / 9,16 ; 24 relances,
  48 refus/32 tours, un repli par segments, zéro audit illisible ou incident
  technique/recharge. **N9 corrigé sur le parcours réel p2** (`nom` refusé puis
  `qui` exécuté) ; N10 non reproduit ; **N7 persiste**, audit inversant les
  révisions du nom entendu. Avis **3/6**, toujours incomplets. Gorm rembourse
  2/2 ; achat payé/livré p2, **N11 p1** contrepartie mal formée et correction
  invalide, achat abandonné. Fausse absence et confusion comptable non réémises.
  Force : huit saisies sur onze en deux appels 2/2 ; restes traîner **5/4**,
  enfermer **2/3** (faux refus), improvisé **6/4** : critère non atteint.
  Aucun résultat corporel inventé ni mort/inconscient parlant relevé ; monde
  complet et corps après recharge non archivés, garantie limitée aux projections,
  issues et fils conservés. 2 301 312 jetons cachés, dont 94 171 sur les items.
  Aucune suite moteur ; aucune clé de signature, commit non signé, branche poussée.
  [Rapport 153](taches/rapport-codex-153-verif-luna.md), bruts
  `C:/Users/msics/donjon/artifacts/verif-luna-cdaf371/`.
  Fusionné sur l'intégration (rapport seulement). Petits lots désignés : N11 (correction d'un achat qui perd l'intention, `soir-appel`), restes de force 4f (traîner, enfermer, geste improvisé), N7 et avis du joueur encore partiels. Aucune régression grave : `main` avancée ensuite (décision du 2026-10-27).

- **Branche `codex-prompt-mesure`, fusionnée**, lot **149 / L0**, base
  `3f16fe9` : mesure seule, aucun code du jeu changé ni appel à Luna/local.
  **123 parties archivées, 1 354 appels**, dont 42/445 du lot 141, 80/896 de
  références et 1/13 d’Argon `9d53229` lu sans fusion. Trois tests courts verts,
  comparaison du message fournisseur simulé ; sources contrôlées par SHA-256.
  Interprétation 141 : consignes changées 42/113 paires, schéma 60/113 ; audit
  69/103. Ordre Luna outils → consignes → entrée distinct de l’ordre JSON réseau.
  Entrée effectivement cachée : 47 429 jetons sur neuf appels, contrairement à
  « jamais items.msg ». Trace Argon : sept jetons d’outils retirés, cache à zéro,
  retrait réel `objet:brune`, pas `parole_prevue`. Ordre des faits testé isolément
  en simulation locale ; pas de gain de temps ni serveur local mesuré.
  Dix tours de portée, 24 appels dont 12 après refus ; atelier sans référence
  proche 69/103, franchissements 8/103, obstacles 6/59, inconnus séparés.
  Un processus réduit, aucun banc moteur ni suite complète pour cette mesure.
  [Rapport 149](taches/rapport-codex-149-prompt-mesure.md), bruts
  `C:/Users/msics/donjon/artifacts/prompt-149/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Priorité confirmée : L2 (schéma invariant) est le premier levier pour Luna ; L4 retire ~31 000 caractères éloignés, L5 jusqu'à 12 appels après refus sur ce corpus.

- **Vérification d'intégration 2d504ae**, lot **148**, branche
  `codex-verif-integ-2d504ae` : aucun code du jeu ou outil changé, aucun Luna,
  aucune suite complète ni rejeu de référence. **49 nuits jouées une fois,
  48 achevées** : 32 × 12 h quatre scénarios/huit graines, huit rixes × 8 h,
  cinq contrôles `VERIFIER` + `spatial.VERIFICATION` 0,2 × 8 h, quatre hameaux
  × 12 h. Deux calculs réduits au plus, fond ; temps non comparés.
  **Défaut nouveau : crue 42, Gorm/0**, agenda actif → sommeil et chronique
  pendant l'évaluation en lecture seule, arrêt du contrôle. Reproduction courte
  instrumentée, pas de correctif ici. **Crue 2024, Brune/687–715** : boucle
  fuite/lumière palier/galerie, 68 passages/heure, absente de la même nuit
  `057766f` ; contrat danger/abri à reprendre. Cinq coups contre personnes
  crue 2024 à 633/686 ; aucune mort, usurpation ni prise/lien/enfermement/meurtre
  spontané relevé, captivité non recensée exhaustivement. Autres contrôles sans
  écart ; borne de Lucien auberge 42/314 identique, retenu = optimum 73,4743.
  Gorm informe en crue 1985/144, 500/155, 99/176, pas de rafale de réveils ;
  cinq agendas non atteints. Un intermédiaire sollicité, Odon → Rémy mine 7/472,
  refus par méfiance, zéro accepté/abouti. Promesse fautive crue 11/210 non
  observée ; pièce mine 1985/253 correcte ; quinze appels Odon mine 2024
  571–696 persistants. Hameau : aucun agenda déclaré dans le dérivé, diffusion
  par agenda non exercée ; alerte entretien/garde Gorm 42/25 sans défaut prouvé.
  32 empreintes de référence conformes au manifeste 131 ; archives sans
  sauvegarde complète, rendu après recharge non certifié. Bruts et analyse
  `C:/Users/msics/donjon/artifacts/verif-integ-2d504ae/`. Pas de clé Git de
  signature ; commit non signé, branche poussée, `main` intact.
  [Rapport 148](taches/rapport-codex-148-verif-integ.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Petits lots désignés : évaluation d'un candidat d'agenda sans écriture (confié au lot 146 b, même module) ; boucle fuite/lumière de Brune, crue 2024 687-715 (famille fuite ↔ sécurité, après 146 b).

- **Branche `codex-agendas-amener`, fusionnée**, lot **146**, base `cee0201` :
  livraison partielle autorisée, prérequis de l'accord de déplacement. La condition
  `{objet: auteur, lieu: destination}` utilise une marche dans le devis et dans
  l'engagement commun, au lieu de prendre/poser le personnage. Arrivée reconnue
  par sa position propre, même dans la minute ; le demandeur reste limité à ses
  croyances sur autrui. Gorm confie deux marches (Ilse/galerie, Brune/échoppe),
  accord sans déplacement instantané, engagement exécuté par le destinataire ;
  mêmes `data` et rendus après recharges et laps entier/découpé. Méfiance et lieu
  cru noyé refusés avant engagement. **28 ciblés verts puis 5 nouveaux ciblés verts**.
  **12/12 empreintes 2 h identiques** (Relais/mine/auberge × quatre graines),
  **4/4 crues 4 h identiques**, état complet, relevés, récits et mesures ; aucun
  plantage/usurpation/violation ni boucle nouvelle. Attente urgente 20 min,
  eau 128,75 min, passages horaires maximum 13,25, Ilse/Brune à la galerie 3/8,
  inchangés. Crue 1985 fixe 4 h : 1 430 recherches, 1 092 neuves, 83 066 nœuds
  inchangés. Seize références manquantes cachées, aucun rejeu. Suite complète unique :
  **2 154 tests, 241 fichiers, 2 170,72 s**, deux échecs MiMo historiques `6 != 5`,
  zéro erreur ; reproduits sur la base intacte (13 tests, 10,99 s). Contrôle de la
  réponse entendue enrichi pendant la suite, cinq ciblés repris verts, moteur figé.
  Aucun Luna, deux calculs réduits au plus ; suite à un processus pour cohabiter.
  Code `b70e530`, aucune clé de signature configurée : commits non signés,
  branche poussée seule, sans fusion.
  **`amener` reste non réalisé**, données de la crue inchangées : préférence/avis,
  demande autonome/refus durable, accompagnement, fin/abandon et épreuves restent.
  [Rapport 146](taches/rapport-codex-146-agendas-amener.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Livraison partielle permise par le brief : la sorte amener reste entièrement à faire (lot 146 b).

- Branche `codex-force-4f-luna`, fusionnée, lot **147**, base `cee0201` :
  gestes 4d/4e exposés dans les consignes communes, état du corps explicitement
  mécanique dans l'audit ; filtre existant des locuteurs conscients vérifié après
  recharge jusque devant l'écriture. Fiche de `trainer` : destination du corps
  ajoutée au dossier de contre-revue après un faux refus Luna, sans changer le pas.
  Six tests nouveaux verts (console et recharge, deux personnes, deux seuils,
  bureau/réserve), 70 ciblés existants verts ; reprise finale 16 tests verte.
  Suite complète unique : **2 154 tests, 241 fichiers, 1 205,71 s, deux échecs
  MiMo historiques `6 != 5`, zéro erreur/ignoré**. Complément de destination
  postérieur au lancement de la suite, couvert par les ciblés finaux.
  **16/16 empreintes de 2 h identiques** à `2d504ae` (code de jeu identique à
  `cee0201`), Relais/rixe/mine/auberge × quatre graines : chronique, mesures,
  état complet ; seize références manquantes cachées une fois, aucun rejeu.
  Luna une passe : six nouveaux scripts et les cinq 4b/4c, **49 appels / 19 tours MJ,
  2,58 appels/tour, 9,13 s/tour**, aucune erreur technique/recharge ni repli.
  Huit saisies typées en deux appels ; refus juste du geste improvisé en quatre,
  faux refus de traîner et d'enfermer en cinq et quatre. **Trois appels non garantis,
  4f non entièrement satisfait** ; preuve de destination reprise en tests seulement,
  contradictions corporelles toujours en partie sémantiques. Aucun fichier réservé
  au lot 146, aucun modèle ni comportement autonome changé. Pas de clé de signature :
  commit non signé, branche poussée sans fusion. Bruts `artifacts/force-147/`.
  [Rapport 147](taches/rapport-codex-147-force-4f-luna.md).
  Fusionné sur l'intégration : aucun conflit ; aucun fichier de code commun depuis la base. Critère des trois appels non atteint sur trois saisies (traîner : contre-revue qui rejette une action correcte ; enfermer : porte confondue avec un meuble ; geste improvisé typé `tuer`) : petit lot de reprise ou vérification Luna suivante. Destination du corps traîné ajoutée après la passe Luna, non revalidée par Luna.

- Branche `codex-force-4e-tuer`, fusionnée, lot **145**, base `4c57020` :
  geste `tuer` commun au joueur et aux PNJ, sans choix autonome ; cible vivante sans
  défense au contact, sans jet, cinq secondes avec arme portée ou trente à mains nues.
  Issue revalidée à l'échéance sauvegardée, cri d'une victime consciente, témoins,
  relations, dépouille via `corps.mourir`, découverte et nouvelle typée existantes.
  Les biens restent au mort ; prise par Brune avec faute et témoin vérifiée.
  L'horloge retire les esprits morts pendant le laps ; argument de rendu manquant
  dans l'approche de secours rétabli. État et rendu rechargés, cas Brune et Joss,
  laps continus/découpés, joueur tué puis commande refusée. La parole du témoin dit
  « a tenté de tuer » ; la mort découverte est une nouvelle distincte.
  **62 ciblés verts**, puis huit repris verts ; suite complète unique **2 132 tests,
  1 774,48 s, deux échecs MiMo historiques `6 != 5`, zéro erreur**, 237 fichiers.
  Les deux échecs sont reproduits sur la base intacte (13 tests, 10,23 s).
  Banc 4 h × cinq scénarios × quatre graines : **20/20 états complets, récits,
  chroniques, souvenirs et mesures identiques** à la base ; zéro mort, plantage,
  usurpation ou violation. Vingt références manquantes cachées sans rejeu.
  Aubin mort au Relais et à rixe : trois découvertes chacun, aucun plantage.
  Aucun Luna, deux calculs réduits au plus ; suite à un processus pour cohabiter
  avec le banc. Derniers compléments de rendu/refus/tests vérifiés par ciblés.
  4e moteur réalisé ; saisie/narration Luna et leur vérification restent en 4f.
  Pas de clé de signature Git configurée : commit non signé, branche poussée.
  [Rapport 145](taches/rapport-codex-145-force-4e-tuer.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `social.py`, fusionnés sans conflit textuel.

- Branche `codex-agendas-a4a`, fusionnée, lot **144**, base `8ec3ace`
  (lot 140 `codex-captivite`, non fusionné : dépendance voulue) : livraison partielle
  permise, **activation + informer**. Déclarations du profil activées une fois dans
  l'esprit, état/cause/origine sauvegardés, trois actifs au plus ; poids et plan
  transitoires. Candidat sur l'échelle commune, désespoir devant, continuité selon VOL.
  Destinataire suivant les routes crues, trajet par `chercher` et `_endure`, parole
  typée commune avec avis et dispute ; Gorm doit prévenir Ilse et Brune en crue.
  Sommeil sans plan/contenu cru et réveil sur croyance nouvelle. Aucun Luna,
  deux calculs réduits au plus ; fichiers MJ et worktree d'intégration intacts.
  **40 ciblés consolidés verts**, dont six d'activation (Gorm prévient deux personnes,
  même état et rendu rechargés après laps découpé ; autre parole et registre plein).
  Suite complète unique : **2 105 tests, 231 fichiers, 1 169,75 s**, deux échecs
  MiMo historiques `6 != 5`, zéro erreur ; deux nouveaux tests repris hors de la suite.
  **12/12 empreintes de 2 h identiques** à la base, Relais/mine/auberge × quatre
  graines : chronique, mesures et état complet. Références calculées une fois et
  cachées, aucun rejeu. Premier banc crue : neuf alertes de réveil répété ; correction
  commune (nouvelle croyance autorise un essai, réveil seulement avec plan admissible),
  **11 puis 10 ciblés verts**, sans seconde suite. Reprise branche seule 4 h × quatre
  graines, quatre références cachées : aucune répétition nouvelle, zéro plantage,
  usurpation/violation, mêmes deux observations historiques. Attente urgente moyenne
  **22,5 → 20 min**, eau **123,75 → 128,75 min**, maximum de passages horaires
  **17,5 → 13,25**. Ilse/Brune à la galerie à 4 h **1/8 → 3/8** ; arrivée avant
  l'eau non prouvée. Information atteinte seulement sur 1985 (144 min), sommeil sans
  menace crue sur les trois autres graines. Coût crue 1985 fixe, 4 h : recherches
  **1 475 → 1 459**, nœuds **101 145 → 89 838** ; nuits différentes, aucun surcoût
  isolé ni gain CPU garanti sur ce poste partagé. Code `36d2b82`, aucune clé de
  signature configurée ; commits non signés, branche poussée sans fusion.
  **A4 non achevé** : `amener`, impossibilité crue, manières générales, portée vocale
  dans le graphe et borne d'une recherche supplémentaire par choix restent à faire ;
  puis `garder`/`protéger`, s'interposer et hystérésis générale dans le score.
  [Rapport 144](taches/rapport-codex-144-agendas-a4a.md).

- Branche `codex-captivite`, **non fusionnée**, lot **140**, base `9aab62a`
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `scenario_crue.json`, fusionnés sans conflit textuel. Livraison partielle permise par le brief : amener reste à faire. Limite transitoire : le palier désespoir et l'inertie entre besoins ne valent que pour les porteurs d'agenda (nuits historiques identiques), à généraliser avec l'hystérésis dans le score (A4c).

- **Branche `codex-contrats-internes`, fusionnée**, lot **143**, base
  `4725388` : N10 venait du lexique de `narration.voix_auteur`, déjà appelé
  sur les deux voies : justification d'un avis `impossible` après contre-revue
  et dialogue après refus du monde. Opérations du contrat reconnues avec
  négation, pronoms et subjonctif ; noms de contrats explicitement techniques
  contrôlés, emplois ordinaires et répliques conservés. Aucun prompt ni fichier
  réservé aux lots 140/142 modifié. Deux textes réels corrigés en console,
  état et rendu contrôlés après recharge ; garde refait à l'enregistrement
  malgré un audit favorable. **33 ciblés verts**, puis garde d'écriture ajouté
  et suite complète unique : **2 119 tests, 235 fichiers, 1 241,41 s, deux
  échecs MiMo historiques `6 != 5`, zéro erreur/ignoré**. Luna une passe sur
  copies, atelier/Relais/ambiance : **22 tours MJ, 59 appels, 2,68 appels/tour**
  (références 9a39738 p1/p2 : 61/63, 2,77/2,86), une relance contre 1/4,
  aucun repli, incident technique ou défaut de recharge ; aucune explication
  technique affichée, cas pierre et pied-de-biche en fiction. Six références
  cachées lues, empreintes inchangées, aucun rejeu. N10 non réémis naturellement,
  rejet exercé en simulation. Deux calculs au plus, priorité réduite, Luna une
  exécution. Aucune clé de signature Git configurée ; commit non signé.
  Limite : contrôle lexical, paraphrases et polysémie en partie sémantiques.
  [Rapport du lot 143](taches/rapport-codex-143-contrats-internes.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base.

- Branche `codex-correction-parole`, fusionnée, lot **142**, base `4725388` :
  N9 confirmé dans le fil 141 : `nom` ajouté aux obligations après préparation
  refusée, correction `qui` et secours bloqués sans revue. La déclaration contrôle
  sa propre proposition ; seuls les types reconnus par revue lisible obligent
  les corrections. Préparation refusée, omission locale et revue illisible ne
  confirment plus les déclarations candidates. **Relecture de `e55e252`** :
  régression d'abandon silencieux d'une omission reconnue ; `operations_a_examiner`
  bloque désormais le raccourci aux mots exacts jusqu'à revue lisible, sans
  imposer automatiquement le type. Revue illisible : attente conservée ; type
  présent refusé par préparation : aucune attente (N9). Trois anciens tests
  rétablis dans leur intention, achat déclaré/omis puis abandonné contrôlé.
  Aucun prompt ni scénario modifié. **22 ciblés verts après relecture**,
  cinq fichiers, 24,80 s, deux processus réduits ;
  rejeu des propositions historiques et autre script,
  achat reconnu toujours exigé ; état et rendu contrôlés après recharge.
  Luna, une passe sur copies, trois scripts : **50 appels / 13 tours MJ**,
  aucun repli, incident technique ou défaut de recharge ; `soir-noir` **4,20**,
  `soir-voix` **4,00**, `noms-dialogue` **3,25 appels/tour**. Un refus d'omission
  corrigé ; aucun « Tu n'as encore rien dit ». Références `9a39738` relues sans
  rejeu (`soir-voix` absent du lot 141). Suite complète unique : **2 118 tests,
  235 fichiers, 1 247,64 s**, deux échecs MiMo et une erreur dans le test
  d'audience, dont la première adaptation masquait la régression ci-dessus.
  Les deux échecs MiMo historiques `6 != 5` reproduits sur l'archive intacte
  de la base (13 tests, 11,39 s). Aucune seconde suite complète ni nouvelle
  passe Luna après relecture ; commit non signé et branche poussée.
  Deux calculs réduits au plus, Luna une exécution ; aucune clé Git de signature.
  Reconnaissance du sens encore sémantique ; raccourci aux mots exacts conservé
  sans obligation confirmée ni analyse en attente ; pas de garantie d'exhaustivité
  du typage libre.
  [Rapport du lot 142](taches/rapport-codex-142-correction-parole.md) ;
  bruts `artifacts/correction-142/`.
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base. Version révisée à la relecture : une opération déclarée mais omise exige une revue lisible avant les mots exacts, les trois anciens tests gardent leur protection.

- Branche `codex-crue-hameau`, fusionnée, lot **139**, base `3df20ff` :
  nouveau dérivé de données, six PNJ (Maël au refuge, Sève à la galerie), sans
  mesure initiale des salles basses chez ces évacués ; sept parts, quatre charges
  de bois du guet. Moteur et scénarios existants intacts ; option `--crue-hameau`.
  Banc 4 h × quatre graines : **32 avis, deux adoptions** (Aubin et Sève, 1985,
  193 min), zéro dispute, plantage, écart ou usurpation, aucune boucle signalée.
  **Limite : une seule adoption par un évacué, déjà exposé à l'eau du palier**,
  mesures des salles basses encore issues de paroles ; aucune preuve d'alerte
  précoce ni d'avantage tactique. Ressources restantes mais distribution imparfaite.
  Témoin 4 h lu du cache `97e7198` (code du jeu identique à la base), quatre
  empreintes 2 h de la crue strictement identiques ; **quatre ciblés verts**,
  deux scènes bloc/découpées et deux adoptions capturées, état/rendu rechargés.
  Suite complète unique : **2 076 tests, 228 fichiers, deux échecs MiMo `6 != 5`,
  zéro erreur ni ignoré**, 2 061,03 s ; ces deux échecs reproduits seuls sur la
  base intacte (deux tests, 1,57 s). Un processus réduit, aucun Luna.
  Aucune clé Git de signature configurée : commit non signé, branche poussée.
  [Rapport du lot 139](taches/rapport-codex-139-crue-hameau.md).
  Fusionné sur l'intégration après les lots 132 à 138 et 140 : seul conflit de documentation ; `banc_pnj.py` touché aussi par le lot 136 (épreuves `enferme`), fusionné sans conflit textuel. Accord de fusion : la porte du scénario dérivé recopiait `lieu: antichambre`, refusé depuis le lot 137 ; ramenée à `crypte` comme dans les autres scénarios. Suite complète relancée une fois sur l'ensemble des fusions 139, 140 et 142 à 145 (`tools/tests.py --processus 2`, `2d504ae`) : **2 149 tests, 16 ignorés**, verte (2 316,8 s).

- Branche `codex-captivite`, fusionnée, lot **140**, base `9aab62a`
  (lot 136 `codex-enfermer`, non fusionné : dépendance voulue) : captivité selon les
  liens et les issues crues, inquiétude `captif` par le temps vécu, corps du joueur
  et fiche communs. Une heure captive coûte un point de jet de VOL (plafond cinq),
  deux heures libres au calme en rendent un ; restes exacts sauvegardés en dixièmes.
  Le répit exclut effort, prise, eau et danger perçu ; sécurité non croissante pour
  le PNJ, lumière pour le joueur. Aucun choix autonome nouveau ni appel à Luna.
  Bureau et réserve de la mine, Aubin ligoté au Relais, joueur captif puis libre :
  même `data` et rendu après recharges et laps découpés ; croyances fausses et serrure
  ignorée, détenteur de clé, bornes et répit interrompu vérifiés. **56 ciblés verts**
  après reprises ; suite complète unique **2 101 tests, 1 126,77 s, deux échecs MiMo
  historiques `6 != 5`, zéro erreur**, 230 fichiers. **16/16 nuits de 4 h identiques**
  à la base (quatre scénarios × quatre graines), état, récit, souvenirs et mesures ;
  références calculées une fois puis cachées, aucun rejeu de référence, zéro plantage,
  usurpation ou violation. La contre-épreuve mine corrige l’invariant « verrou ne retient
  pas le porteur d’une clé », sans exception de personnage. Deux calculs réduits au plus.
  Aucune clé de signature Git configurée : commit non signé, branche poussée, sans fusion.
  4d terminé ; 4e et 4f restent à faire.
  [Rapport 140](taches/rapport-codex-140-captivite.md).
  Fusionné sur l'intégration (base voulue : la branche du lot 136, fusionnée juste avant) : seul conflit de documentation ; aucun fichier de code commun depuis la base.

- **Vérification Luna 9a39738**, lot **141**, branche `codex-verif-luna-9a39738` :
  aucun code du jeu changé ; deux passes, vingt scripts historiques + avis,
  **42 parties, 308 saisies, 142 tours MJ, 445 appels**, quatre processus réduits
  au plus, copies ; 42 parties cachées, 120 fichiers de référence inchangés,
  `057766f` et `91a4351` relus sans rejeu. Vingt communs : **437→416 appels**,
  **3,21→3,06 appels/tour**, **12,15→11,38 s/tour**, médiane 10,91→10,36 s ;
  zéro audit illisible, un repli, aucun incident technique/recharge.
  N6/N8 non reproduits 2/2 ; N7 partiel (refus sémantique du nom persistant,
  rappel exact non exercé) ; avis **2/3 puis 1/3**. Gorm remboursé et achats
  payés/livrés 2/2 ; confusion comptable narrative p1. N9 : typage `nom`
  erroné encore imposé après correction `qui`, parole abandonnée ; N10 :
  explications « moteur/identifiant » affichées. Aucun correctif dans ce lot.
  Dossier d’audit moyen **12 885→13 807 caractères**, liste non vue seule
  153 en moyenne/341 au plus (avis 1 327) ; aucune borne en partie longue.
  Quatorze projections sous obstacle rechargées identiques ; soldes complets
  non capturés. Pas de conclusion de vitesse sur poste partagé ni de garantie
  sémantique universelle ; aucune suite moteur. Pas de clé Git de signature.
  Bruts `C:/Users/msics/donjon/artifacts/verif-luna-9a39738/` ;
  [rapport du lot 141](taches/rapport-codex-141-verif-luna.md).
  Fusionné sur l'intégration (rapport seulement). Petits lots désignés : N9 (déclaration erronée non confirmée qui rend une correction de parole irrécupérable) et N10 (contrats internes du moteur exposés au joueur dans une explication). Avis du joueur : typage encore partiel (2/3 puis 1/3), à reprendre.

- Branche `codex-discours-indirect`, fusionnée, lot **138**, base `e48c2cc` :
  définition de la réplique directe partagée entre interprétation, schéma et fidélité ;
  les cadres introducteurs reconnus ne passent plus par le raccourci de copie littérale.
  Secours local sans transposition inventée, guillemets conservés. N8 vient de la première
  interprétation, admise par la revue pour son contenu `ressource=faim`, sans correction.
  Console et recharge : cas Brune, autre affirmation, citation, secours sans parole ;
  ciblés verts après correction d'un nouveau test grammatical. Luna, une passe sur copies,
  trois scripts : **46 appels / 11 tours**, aucun refus moteur/fidélité, repli ou défaut
  de recharge ; N8 donne « Tu as de quoi manger ? », opération conservée, quatre appels.
  Appels/tour ressources **4,00**, soir-appel **4,75**, noms-dialogue **3,75** ; références
  `057766f` relues sans rejeu. Suite complète unique : **2 077 tests, 228 fichiers,
  1 107,42 s, deux échecs MiMo `6 != 5`, zéro erreur/ignoré**, deux processus réduits.
  Les deux échecs sont reproduits sur la base intacte : 13 tests, 11,15 s ; aucun autre
  défaut restant. Deux calculs au plus, Luna une exécution ; branche poussée.
  **Limite : transposition et revue sémantiques, invariant universel non garanti** ;
  garde grammaticale locale limitée aux introducteurs reconnus. Aucune clé de signature
  Git configurée. [Rapport du lot 138](taches/rapport-codex-138-discours-indirect.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `mj.py`, fusionnés sans conflit textuel.

- Branche `codex-lieu-ouvertures`, fusionnée, lot **137**, base `97e7198` :
  `porte.lieu = crypte` dans Relais/crue/rixe/rixe douce, cohérent avec les
  deux sorties crypte est/beffroi ouest. Validation commune de toute donnée
  initiale à `relie` dans `depuis_scenario`, refus avec objet/champ/salles admises
  et `attendu`. Huit scénarios, dix ouvertures contrôlés ; aucune croyance initiale
  de localisation à modifier, savoir des objets fixes corrigé par la donnée.
  Trois ciblés verts : capture crue 11 à 210 et Relais, présence/perception,
  ouverture PNJ des deux côtés, état complet et rendu rechargés. Banc 4 h
  Relais/crue/rixe × quatre graines : douze chroniques/récits/souvenirs/relevés/
  projections finales/boucles/constats identiques, zéro plantage/usurpation ;
  seul compteur crue 7, recherches neuves 629→624. Empreintes complètes différentes
  avec le champ modifié ; attribution exhaustive des états non conservés non prouvée.
  Suite complète unique : **2 076 tests, 228 fichiers, deux échecs MiMo historiques
  `6 != 5`, zéro erreur, 1 073,32 s**. Sans Luna, deux processus réduits au plus.
  Anciennes sauvegardes et croyances historiques sans migration ; manipulation
  de la capture remise en état et à portée, sans rejeu de sa promesse autonome.
  Aucune clé Git de signature configurée. Bruts `artifacts/ouvertures-137/` ;
  [rapport du lot 137](taches/rapport-codex-137-lieu-ouvertures.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base.

- Branche `codex-promesse-tenable`, fusionnée, lot **133**, base `3cdcab3` :
  crue 11 rejouée 12 h sur copie, capture avant offre à **126226**, abandon
  reproduit à **126336**. Cause : présence physique de la cible incompatible
  avec son `lieu` déclaré, et non intégrité de la porte. `_mesurer_direct` contrôle
  toutes les cibles touchées par `Monde.present_physique` sur l'état cru/projeté,
  devis et échéance communs, aussi sans cases ; aucun cas propre au scénario.
  **42 ciblés existants et quatre nouveaux tests verts** : cas réel et objet
  incorporé, refus avant accord/transfert, état/mémoire/rendu rechargés et même
  laps découpé ; service tenable encore accepté et tenu. Rapide final **16 nuits
  de 4 h** : **16/16 états finaux complets identiques** à la base, mêmes
  chroniques, mesures métier, boucles et alertes ; zéro plantage/violation/
  usurpation, aucune répétition supplémentaire. Zéro tâche promise naturelle
  sur ces nuits dans les deux versions ; tenue prouvée en scènes ciblées.
  Seul écart : recherches neuves crue 7 **629 → 624**.
  Suite complète unique : **2 077 tests, 11 échecs, zéro erreur, 1 276,59 s** ;
  contrôle déplacé hors des estimations de fourniture, puis **139 repris,
  deux seuls échecs MiMo historiques**, reproduits sur l'archive intacte de
  `3cdcab3` (13 tests). Aucune garantie ajoutée sur les autres
  préconditions des gestes, les objets brisés accessibles ou les approches
  locales estimées. Sans Luna ; aucune clé Git de signature configurée.
  [Rapport du lot 133](taches/rapport-codex-133-promesse-tenable.md).
  Fusionné sur l'intégration : seul conflit de documentation ; fichiers de code touchés aussi depuis la base : `planification.py`, fusionnés sans conflit textuel.

- Branche `codex-enfermer`, fusionnée, lot **136**, base `bce47d8`
  (lot 134 `codex-trainer`, non fusionné : dépendance voulue) : verrouiller joueur/PNJ,
  victimes selon les présences crues, contrainte et témoins communs ; constat par essai,
  appel et but de sortie dans le planificateur, clé/crochetage/outil/épaule. Trois secondes
  par coup de porte, bris ouvert et déverrouillé. Le protecteur alerté rejoint avec sa clé.
  Aucun choix autonome supplémentaire d'enfermer, ni inquiétude captive/volonté brisée.
  Beffroi non refermable (autre issue sans porte) : sur décision utilisateur, aucune donnée
  de scénario modifiée ; bureau et réserve de la mine employés pour les épreuves.
  Lucien/Josse au passe ; Bram à la pioche ; joueur assomme et traîne Bram puis l'enferme
  devant Gaspard ; état complet et rendu identiques après rechargement et laps découpé.
  **159 ciblés finaux verts**, douze fichiers. Suite complète unique : **2 091 tests,
  1 094,80 s, huit échecs et une erreur** ; reprises des défauts nouveaux vertes,
  deux échecs MiMo historiques non corrigés, aucune seconde suite.
  Banc 4 h × quatre scénarios × quatre graines : **13/16 strictement identiques** ;
  crue 1985/7/2024 divergent par une étape `frapper` devenue inutile après ouverture
  par un tiers, désormais 3 s au lieu d'une minute. Rétablir cette durée seule rend
  les trois états et chroniques identiques à la base (contre-épreuves branche seule).
  Aucun plantage/usurpation/violation ni nouveau constat ; l'identité des seize nuits
  n'est pas acquise. Seize références calculées une fois et cachées, sans rejeu.
  Aucun Luna, au plus deux calculs réduits ; aucune clé de signature Git configurée.
  [Rapport du lot 136](taches/rapport-codex-136-enfermer.md).
  Fusionné sur l'intégration après le lot 134 (base voulue) : seul conflit de documentation ; `planification.py` touché aussi par le lot 133, fusionné ensuite sans conflit textuel ; suite complète sur l'ensemble des fusions 132 à 138 (`tools/tests.py --processus 2`) : **2 114 tests, 16 ignorés**, verte (2 328,5 s).

- Branche `codex-trainer`, fusionnée, lot **134**, base `bb31eb5` :
  traîner une personne inconsciente, ligotée ou rendue, ou une dépouille ; même
  validation joueur/PNJ, deux positions appliquées à l'échéance sauvegardée,
  pas commun, arrivée libre, mains libres et interruptions. Allure 4,5 s
  (diagonale 6,4 s), plus rotation. Témoins, souvenirs, relations et rendu communs ;
  aucune contrainte pour les dépouilles, aucun choix autonome. Le contact accepte
  les dépouilles et l'éveil d'un témoin occupé reste stable au découpage du laps.
  Banc 4 h × Relais/rixe × quatre graines : **8/8 identiques** à la base, état final,
  empreintes, chroniques, mesures et boucles ; six observations historiques
  `fige_presse` inchangées, zéro plantage/usurpation/violation. Référence calculée
  une fois puis cachée ; aucune conclusion CPU sur ce poste partagé.
  **37 ciblés verts** (7,11 s) ; suite complète unique : **2 082 tests, deux échecs
  MiMo `6 != 5`, zéro erreur**, 228 fichiers, **1 101,90 s**. Les deux échecs
  reproduits sur l'archive intacte de la base (13 tests, 10,05 s) ; aucune seconde suite.
  Aucun Luna, deux calculs réduits au plus ; aucune clé Git de signature configurée,
  commit non signé, branche poussée. Mains libres = aucun objet mobile directement porté ;
  pas de nouveau système d'équipement. Enfermer et le reste de 4d restent à faire.
  [Rapport du lot 134](taches/rapport-codex-134-trainer.md).
  Fusionné sur l'intégration : seul conflit de documentation ; aucun fichier de code commun depuis la base.

- Branche `codex-rappel-exact`, fusionnée, lot **135**, base `d509da1`
  (lot 132 volontairement non fusionné) : cause N7 confirmée dans les bruts 057766f,
  `paroles_entendues.texte` projetait « Je m’appelle une voix qui se dit Ilse »
  tandis que `echanges_passes` gardait les mots exacts. Projection des événements
  entendus et du dossier corrigée ; références publiques conservées, paroles privées
  encore projetées. `rappel_exact` historique et phrases entières du découpage commun
  prouvés sans audit, sans nouvelle parole ni vérité de leur contenu ; preuve refaite
  avant sauvegarde. **15 ciblés verts**, cas réel et autre scène en console rechargée,
  faux rappels refusés, nom inconnu projeté, preuve périmée refusée.
  Luna finale : **52 appels / 13 tours**, soir-noir **5,40 / 4,60 → 4,20 appels/tour**,
  soir-voix **4,00** (référence absente), noms-dialogue **3,75 / 3,75 → 3,75**.
  Zéro repli, erreur de recharge ou fuite de nom observée. Tour 5 sans N7 mais sans
  rappel, refus actuel de se nommer : jugement libre **non garanti**. Autre faux rappel
  d’une phrase entière au tour 2 désormais prouvé localement depuis le fil, sans nouvel
  appel Luna. Premier lancement prématuré interrompu après deux scripts, puis une seule
  passe finale : écart à la passe unique du brief déclaré dans le rapport.
  Suite complète unique : **2 081 tests, deux échecs MiMo historiques `6 != 5`,
  zéro erreur**, **1 101,71 s**, deux processus réduits ; aucune seconde suite.
  Extension aux phrases vérifiée par les 15 ciblés finaux après son ajout pendant
  la suite (cinq nouveaux tests déjà exécutés par celle-ci). Bref chevauchement
  du ciblé final et de la suite déclaré dans le rapport.
  Aucune clé Git de signature configurée : commit non signé.
  [Rapport du lot 135](taches/rapport-codex-135-rappel-exact.md).
  Fusionné sur l'intégration juste après le lot 132 (base voulue) : aucun conflit ; aucun fichier de code commun depuis la base.


- Branche `codex-non-perception`, fusionnée, lot **132** : dossier commun
  `perception.non_vus_connus`, références et désignations déjà connues sans position
  actuelle ; attestations exactes de non-perception prouvées par le mécanisme du
  lot 95 et recalculées avant sauvegarde. La couverture borne les absences,
  indépendamment de la non-perception visuelle. Aucun changement du garde de fuite.
  Cas réel Gorm sous couverture partielle et objet connu ailleurs, console/rendu
  rechargés ; fausses absences du lot 102 toujours refusées. **18 ciblés verts**,
  puis **trois tests finaux verts**, dont attestation périmée refusée à la sauvegarde.
  Luna sur copies, une passe, une exécution réduite : **27 appels / huit tours**,
  signes-guet **4,50 → 2,00 appels/tour**, signes-noir **2,00 → 2,00**,
  soir-noir **5,00 → 4,20** ; tour Gorm **6 / 4 → 2 appels**.
  Aucun refus N6 ni fausse absence affichée, repli ou défaut de recharge.
  Références `057766f` exclusivement relues ; identité finale soir-noir encore
  incohérente, hors périmètre. Paraphrases et ignorance de position restent
  sémantiques ; seule la preuve visuelle et sa reprise exacte sont déterministes.
  Suite complète unique : **2 076 tests, deux échecs MiMo historiques `6 != 5`,
  zéro erreur**, **1 110,50 s**, deux processus réduits ; pas de seconde suite.
  Aucune clé Git de signature configurée, commit non signé, branche poussée. [Rapport du lot 132](taches/rapport-codex-132-non-perception.md).
  Fusionné sur l'intégration après les lots 130, 124+128 et 129 : aucun conflit ; aucun fichier de code commun depuis la base. Réserve : la liste « connu, non vu » grossit avec la partie (dossier de chaque appel), à surveiller à la vérification Luna groupée.


- Branche `codex-signes-critere`, fusionnée **sans son réglage**, lot **129**, base `56afc2e` :
  critère du 2026-10-26 (PSY basse ≤ 0,7, haute ≥ 0,8, méprises globales <20 %).
  Grille commune de **112 réglages**, corpus de 48 nuits de 4 h, aucun admissible ;
  compromis minimax **3/2/7** dans les seules constantes de `signes.py`, sans
  réglage individuel, par sorte ou scénario, ni changement du jet. Confirmation
  en 48 nuits libres : basse **9/12 = 0,75**, haute **26/26 = 1,00**, méprises
  globales **144/658 (21,88 %) → 188/723 (26,00 %)**, abstention **40,93 → 36,91 %**.
  **Critère non atteint** (+0,05 en bas, +6,00 points de méprises), petits échantillons.
  Rapide 4 h × quatre scénarios × quatre graines : références manquantes calculées
  une fois et cachées, zéro plantage/usurpation ; nouvelle alerte de répétition
  mine 2024 (Mathe lit huit fois peur contre six, après méprises froid supplémentaires),
  avertissements redits 5→8, alternances aller voir/autre but 1→2 (crue 7 ajoutée).
  **Absence de répétition nouvelle non acquise** ; aucun contournement ajouté.
  39 ciblés verts (guet réel et autre guet, état/rendu rechargés), seuls dés contrôlés
  adaptés aux seuils. Suite complète unique : **2 075 tests, deux échecs MiMo `6 != 5`, zéro erreur**,
  **995,11 s** ; les deux échecs reproduits seuls sur la base intacte `56afc2e`
  (2 tests, 1,34 s). Quatre tests finaux de classement verts (0,17 s).
  Deux calculs réduits au plus, sans Luna ; aucune clé Git de signature configurée,
  commit non signé. Bruts `artifacts/signes-129/` ;
  [rapport du lot 129](taches/rapport-codex-129-signes-critere.md).
  **Décision de l'utilisateur (2026-10-26) : garder 4/3/8.** Fusionnés : l'outil de calibration (`tools/calibrer_signes.py`, `--heures`, `classer`), ses tests et le critère révisé du plan ; `signes.py` et `test_signes.py` restent ceux de la base. Calibration close en l'état (méprises 21,9 %, justesse basse 0,77) : les seules constantes ne peuvent tenir le critère.

- Branche `codex-avis-typage`, fusionnée, lots **124 + 128**, base du
  lot 128 `20cd5cf` : contrat d'opérations commun analysé avant le contenu,
  `propos` réservé à l'absence d'opération applicable, sans lexique ni règle
  particulière au scénario. Console/MJ simulé : avis positif et négatif omis
  puis corrigés, réception et rendu rechargés ; parole ordinaire sans revue,
  achats et paiements conservés. **17 ciblés**, deux erreurs d'attente du nouveau
  test corrigées, puis **neuf tests d'avis verts** (les huit autres étaient verts).
  Suite complète unique : **2 066 tests, 223 fichiers, 1 060,85 s**, deux processus
  réduits ; **deux échecs MiMo historiques**, zéro erreur.
  Luna sur copies, une passe : **2/3 avis typés contre 0/3**, galerie encore
  `propos` ; avis **3,00 → 5,00 appels/tour**, noms-dialogue **3,75 → 3,25**,
  soir-appel **5,00 → 6,00**, références historiques lues sans rejeu ; total
  **44 → 52 appels / 11 tours**. Aucun refus affiché ni défaut de recharge,
  un repli narratif à soir-appel. Les deux échecs MiMo préexistants sont liés
  à la validation `jsonschema` 4.26.0 d'un ancien segment d'audit simulé,
  rejeté avant reprise (six appels au lieu de cinq), sans modification fournisseur.
  **L'invariant depuis toute saisie libre reste non garanti**, malgré le seuil
  Luna du brief atteint ; ce lot ne clôt pas la limite du lot 124.
  Aucune clé de signature Git configurée.
  [Rapport du lot 128](taches/rapport-codex-128-avis-typage.md).
  Lots 124 et 128 fusionnés ensemble sur l'intégration après les lots 122, 123, 125 à 127, 130 et 131 : seul conflit de documentation ; `esprits.py` et `spatial.py` touchés aussi depuis la base, fusionnés sans conflit textuel ; suite complète sur l'ensemble des fusions 130, 124+128 et 129 (`tools/tests.py --processus 2`) : **2 073 tests, 16 ignorés**, verte (2 319,9 s). Surcoût d'appels surtout dû aux avis désormais typés et relus (avant : sans revue) ; à revoir à la prochaine vérification Luna groupée.

- Branche `codex-avis-joueur`, fusionnée (avec le lot 128), lot **124**, base `85b9204` :
  contenu joueur `avis` (lieu public connu, menace oui/non), validation avec `attendu`,
  conviction sur les observations propres de Corvus mémorisées avec sa perception,
  réception commune et dispute du lot 121 avec témoins/partis pris/dispute perdue.
  Le moteur ne fait pas répliquer Corvus à sa place. Prévisions qualitatives sans
  mesure inventée ; faits dits et paroles rechargés. **37 ciblés verts**, puis le
  huitième nouveau parcours, décrue réelle, vert. Suite complète unique : **2 064 tests,
  223 fichiers, 1 009,24 s, cinq échecs**, zéro erreur/ignoré, deux processus réduits.
  N3 adapté au nouveau champ `avis:false`, sans changer les réponses ; reprise de
  24 tests : deux échecs MiMo restants, reproduits identiquement sur l'archive de base
  `85b9204` (13 tests, deux échecs, atelier : six appels au lieu de cinq). Bilan non
  entièrement vert ; aucune seconde suite. Banc 4 h crue/Relais × quatre graines :
  huit nuits terminées, aucun signalement dans les seules chroniques, 36 avis/zéro adoption.
  **Limite bloquante : Luna 0/3 avis typés**, trois `propos`, 9 appels (3/tour),
  13,5 s/tour, aucun faux refus affiché ni erreur de recharge. Le raccourci des mots
  exacts déclarés sans effet évite la revue sémantique. **Non fusionnable comme 3f achevé** ;
  pas de seconde passe Luna ni de contournement lexical. Aucune clé de signature Git
  configurée. [Rapport du lot 124](taches/rapport-codex-124-avis-joueur.md).

- Branche `codex-retrait-stratege`, fusionnée, lot **130**, base `56afc2e` :
  retrait du stratège Luna des PNJ, de ses options, outil, tests propres et mesures ;
  délibération ordinaire inchangée. Ancien champ `stratege` ignoré, conservé inerte,
  sans migration ; deux scènes rechargées et jouées (Relais/mine), même récit et état.
  **16/16 nuits de 2 h strictement identiques** (Relais/crue/mine/auberge × quatre
  graines), chronique, mesures et état complet sans exclusion. Référence calculée une
  fois et cachée. **11 ciblés verts** ; suite complète unique : **2 052 tests, deux
  échecs MiMo `6 != 5`, zéro erreur**, 1 047,51 s ; deux échecs reproduits sur la base
  intacte (13 tests). Pyflakes sans nom indéfini, trois avertissements préexistants.
  Aucun Luna, deux calculs réduits au plus ; fichiers réservés aux lots 128/129 intacts.
  Aucune clé Git de signature configurée : commit non signé, branche poussée.
  [Rapport du lot 130](taches/rapport-codex-130-retrait-stratege.md).
  Fusionné sur l'intégration après les lots 122 à 127 et 131 : seul conflit de documentation ; aucun fichier de code commun depuis la base (lot 122 : `echanges`, `planification`, `pnj_propositions`), pas de suite complète relancée.

- **Vérification d'intégration 057766f**, lot **131**, branche
  `codex-verif-integ-057766f` : analyse des bruts seuls, aucun rejeu, Luna,
  code du jeu, suite complète ni mesure CPU. **32 nuits de 12 h, huit rixes
  de 8 h, cinq nuits VERIFIER + spatial 0,2 de 8 h** : aucun plantage,
  violation signalée, usurpation, coup contre une personne ni décès observé ;
  aucun écart des contrôles. Borne historique Lucien, auberge 42 à 314,
  retenu = optimum **73,4743**, inchangée. **Sept services Mathe → Lucien**
  dans la mine, **deux disputes naturelles** crue 99 (Aubin/Brune à 544,
  Aubin/Ilse à 557), aucun éclat ; Gorm révise sa prévision à 557.
  **18 tâches promises offertes, une acceptée, zéro tenue, une rompue** :
  nouveau défaut crue 11, Ilse à 210, promesse de verrouiller la porte contre
  le pied-de-biche, annulée pour impossibilité **11 secondes après accord**.
  À isoler : préconditions communes au devis autonome et à l'engagement,
  aucune correction ici. Contrepartie d'Odon mine 1985 à 253 toujours correcte ;
  six avertissements redits crue 2024 persistants avec rallumages, anciens
  appels d'Odile auberge 7 à 641–644 non observés. Odon mine 2024, 15 appels
  de 571 à 696 avec nouveaux bruits : alerte nouvelle, pas une boucle prouvée.
  Comparaison des 96 nuits archivées, références inchangées, un processus réduit.
  Pas de sauvegarde complète dans les bruts pour vérifier le rendu rechargé.
  Bruts `C:/Users/msics/donjon/artifacts/verif-integ-057766f/`, analyse `analyse-131/`.
  Aucune clé Git de signature configurée, commit non signé, branche poussée.
  [Rapport du lot 131](taches/rapport-codex-131-verif-integ.md).

- Branche `codex-intermediaires`, fusionnée, lot **122**, base **219bc8d** :
  code signé SSH **fc5f62a**, puis **76c071a**, signatures vérifiées. Commission
  « faute de mieux » après méfiance/rancune : un candidat choisi sur les seules
  attitudes crues, une tentative sauvegardée par refus/besoin ; ordre avec le
  service spontané au devis le moins cher pour le demandeur. `confier` utilise
  altruisme, lien et coût de son devis, avec son unique jet. Le porteur demande
  avec ses propres relations, reçoit une part réelle puis la sert ou la remet
  au bénéficiaire ; aucun transfert à l'acceptation. Acquisition du bien visé
  permise dans le devis commun, travail délégué exclu ; nourriture à emporter,
  affectation de la part reçue à une seule tâche et coût des remises communs.
  Deux scènes après recharge et même laps découpé : Brune/Ilse/Gorm et
  Joss/Mireille/Odile ; **39 ciblés verts**, un processus à priorité réduite.
  Banc **4 h × quatre scénarios × quatre graines** : **16/16 chroniques,
  mesures métier, audits et boucles identiques**, aucune violation/usurpation
  ni aucun plantage ; **zéro commission naturelle**, preuve par scènes d'auteur.
  Référence calculée une fois puis cachée, aucune comparaison CPU.
  Suite complète unique : **2 065 tests, 16 ignorés, 223 fichiers,
  3 634,73 s**, un processus réduit. Un échec de fourniture : le devis commun
  vérifie aussi la livraison autonome des fournitures du commanditaire,
  sans accord futur d'un tiers ; cas réel crue 7 à 353 min et autre lot.
  Une erreur Windows TUI avant action, sans changement de son code.
  Reprises finales : **55 verts en 104,54 s**, puis **un TUI vert en 8,42 s** ;
  **bilan consolidé vert**, aucune seconde suite. Le banc concerne `fc5f62a`,
  avant le resserrement des fournitures contrôlé par les reprises ciblées,
  sans second banc. Créneau dépassé par la vérification séquentielle.
  Aucun Luna. Les permissions d'usage d'un bien durable ne sont pas étendues
  par sa transmission ; signes interprétés faillibles, fournitures accessoires
  de tiers exclues. [Rapport du lot 122](taches/rapport-codex-122-intermediaires.md).
  Fusionné sur l'intégration après les lots 123, 125, 126 et 127 : seul conflit de documentation ; aucun fichier de code commun avec le lot 126 (`pnj.py`, `tenir.py`). Suite complète sur la fusion (`tools/tests.py --processus 2`) : **2 079 tests, 16 ignorés**, verte (2 081,4 s).
- Branche `codex-mesure-cout`, fusionnée, lot **127**, base **62429a8** :
  `tools/mesure_cout.py`, compteurs déterministes par heure et PNJ × but,
  recherches neuves/reprises, toutes les passes, nœuds de certificats et gestes
  réellement générés ; aucun fichier de `donjon/` modifié, aucun Luna.
  Auberge 1985 12 h fixe/tiré et mine 1985 12 h fixe, `42bb9c0` contre `62429a8` :
  **6/6 nuits**, deux mesures identiques et identité des empreintes au témoin sans
  sonde ; quatre tests ciblés verts, aucune suite complète. Deux calculs réduits
  au plus, worktrees détachés nettoyés, résultats dans le cache commun des références.
  Aucun compteur unique ne suit tous les CPU : recherches en fixe, générations/gestes
  en tiré ; nœuds examinés (terminaux compris), expansions strictes non exposées.
  CPU indicatif uniquement ; aucune clé Git de signature configurée, commit non signé.
  Bruts `artifacts/cout-127.json` ;
  [rapport du lot 127](taches/rapport-codex-127-mesure-cout.md).
- Branche `codex-force-4d-tenir`, fusionnée, lot **126**, base `28fa4b2` :
  prises et liens communs joueur/PNJ (`tenir.py`) ; saisir, se dégager, ligoter, délier,
  couper le lien et se libérer. Issues longues sérialisées, appliquées à l'échéance
  exacte par `pnj.finir_gestes` après revalidation ; coup et inconscience interrompent.
  Contraintes du corps partagées avec les pas, opérations et objets ; états visibles
  après recharge. Protecteurs déliant un protégé perçu, captifs se libérant, aucune
  saisie ni aucun ligotage autonome. **Traîner reporté à ce lot** (réalisé depuis au lot 134), selon la clause de livraison
  partielle du brief ; enfermer et le reste de 4d restent à faire.
  Suite complète unique : **2 063 tests, deux échecs MiMo `6 != 5`, zéro erreur**,
  **1 072,38 s** ; les deux échecs reproduits sur la base intacte (13 tests).
  Derniers ciblés : **63 verts**, 26,14 s. Banc 4 h Relais/rixe × quatre graines :
  **8/8 états complets et chroniques identiques**, aucune usurpation/violation,
  aucun ligotage spontané, six alertes `fige_presse` inchangées. Sans Luna,
  deux processus réduits au plus ; références calculées une fois puis cachées.
  Danger durable 4c non élargi (`esprits.py` réservé) ; souvenirs `subi`/témoins
  et réactions corporelles pour les nouvelles contraintes.
  Aucune clé Git de signature configurée : commits non signés.
  [Rapport du lot 126](taches/rapport-codex-126-force-4d-tenir.md).

- Branche `codex-adoption-avis`, **diagnostic, fusionné (docs et outil)**, lot **125**, base
  `85b9204` : six nuits crue (4 h × 1985/7/42/2024, 12 h × 500/2024),
  **40 avis, 70 réceptions, zéro adoption/dispute**. Tous les auditeurs tiennent
  déjà la même menace sur une preuve propre `vu` de poids 1 ; poids reçus 0 à
  0,6825, convictions dites 1, dates de preuve égales, aucun contradicteur entendu.
  Formule du § 7.3 respectée ; aucun défaut du contrat établi, asymétrie des
  preuves à prévoir dans les données pour rendre un avis utile. État final complet,
  chronique, empreintes et mesures identiques avec/sans sonde sur les six nuits ;
  deux captures nouvelles rechargées et trois tests historiques verts (monde,
  parole, perception et temps découpé). Aucun code du jeu modifié, sans Luna ni
  suite complète ; au plus deux processus réduits. Aucune clé Git de signature
  configurée, commit non signé. Bruts `artifacts/adoption-125/` ;
  [rapport du lot 125](taches/rapport-codex-125-adoption-avis.md).
- **Vérification Luna 057766f**, lot **123**, branche `codex-verif-luna-057766f` :
  aucun code changé, mêmes vingt scripts et deux passes que les lots 99/111.
  **40 parties, 302 saisies, 136 tours MJ, 437 appels** contre 459 ;
  **3,38→3,21 appels/tour**, **11,54→12,15 s/tour**, médiane 9,57→10,91 s.
  **156→135 audits, 35→0 illisibles, trois replis→zéro** ; aucun plantage,
  erreur réseau, arrêt ni défaut de recharge. Quatre Luna au plus, copies,
  priorité réduite ; quarante parties cachées sous 057766f, 95 fichiers des
  références main/91a4351 inchangés, aucun rejeu des références.
  Gorm remboursé 2/2 sans faux refus de quantité ; achats payés/livrés 2/2,
  confusion de récit persistante p2. N1/N3 et fausse absence non reproduits,
  N2 exact non exercé, réserve sur « les faits » non reproduite ; N6 persiste.
  Nouveau faux refus d'un rappel exact d'Ilse (N7), discours indirect devenu
  réplique descriptive (N8). Identité seulement partielle, aucune garantie
  sémantique générale ; quatorze projections sous obstacle rechargées conformes.
  Temps historiques sur poste partagé : aucune attribution causale de latence.
  Un refus auxiliaire d'écriture avant Luna, repris ; trace conservée.
  Aucune clé de signature Git configurée : commit non signé.
  Bruts `C:\Users\msics\donjon\artifacts\verif-luna-057766f\`.
  [Rapport du lot 123](taches/rapport-codex-123-verif-luna.md).

- Branche `codex-rendre-service`, fusionnée, lot **120**, base `0a53910`,
  code signé SSH **`7ec9fbc`**, signature vérifiée : recours de service spontané
  après méfiance ou rancune, hors de la recherche, après les moyens ordinaires
  et avant une faute envers le même personnage. Devis autonome existant,
  tentative sauvegardée par refus/besoin, aucun mandat ou droit inventé.
  L'effet utile constaté avec son auteur identifié produit l'épreuve commune
  `service_rendu` (confiance +20, affection +10, rancune −15, dette +20,
  modulations et hystérésis conservées), dons et joueur compris ; prestations
  convenues sans double crédit. Brune/Gorm et réserve commune d'auberge :
  service, méfiance levée, redemande et journal rechargés, même laps découpé.
  Suite complète unique : **2 048 tests, 16 ignorés, 221 fichiers, 1 860,72 s**,
  deux processus réduits ; sept anciennes attentes/empreintes adaptées et
  une erreur Windows TUI, reprises **28 + 1 tests verts**, bilan consolidé vert.
  Oracles historiques conservés, seuls registres nouveaux vides exclus des
  projections. Banc 4 h × quatre scénarios × quatre graines : **16/16 audits,
  boucles et chroniques hors relations identiques**, aucun plantage/usurpation.
  Trois repas spontanés constatés dans la mine, aucune demande accordée ensuite
  ni réparation délibérée naturelle ; deux parcours ciblés positifs. CPU des
  versions lancées ensemble, un processus réduit chacune, sans cache :
  **213,250 → 213,688 s (+0,21 %)**, mesure ponctuelle sur poste partagé.
  Bruts `artifacts/service-120/`, cache de base conservé.
  **Révision d'utilité avant fusion** : un don/repas ne devient `service_rendu`
  que s'il comble un manque cru avant le geste (besoin du corps pressant,
  pulsion ou agenda actif non satisfait), auteur identifié. Sinon `recu`/`nourri`
  historiques ; aucun recalibrage des cadeaux sans usage. Critère partagé avec
  `services.preparer`, capturé avant transfert/satiété. Les deux fichiers
  historiques `relations_graduees` et `constater_rumeurs` reviennent exactement
  à `0a53910` : leurs dons/repas ne comblaient aucun manque cru.
  Même don utile/inutile/vide, repas avant satiété, pulsion et agenda contrôlés
  après rechargement. **71 ciblés verts (un ignoré), puis 11 finaux verts** ;
  aucune seconde suite ni nouveau banc, selon la demande de relecture.
  Les mesures précédentes concernent `7ec9fbc`, avant cette révision.
  Aucun Luna, scénario, `social.py`, `ouie.py` ou algorithme de recherche modifié.
  [Rapport et limites du lot 120](taches/rapport-codex-120-rendre-service.md).
  Fusionné sur l'intégration après le lot 121 : seul conflit de documentation ; `relations.py`, `esprits.py` et `pnj.py` touchés aussi par le lot 121, fusionnés sans conflit textuel ; suite complète sur la fusion (`tools/tests.py --processus 2`) : **2 057 tests, 16 ignorés**, verte (1 615,6 s).

- Branche `codex-disputes`, fusionnée, lot **121**, base **0a53910** :
  avis de menace contradictoires entre PNJ par la parole commune ; une contradiction,
  une réponse et un éclat seulement par fierté/colère. Témoins auditifs, poids des sources,
  départage CHA/ELO, partis pris audibles et épreuves relationnelles ; registre des faits
  dits durable après oubli/recharge. Aucun Luna, scénario ou changement du planificateur.
  Deux scènes d'auteur (Aubin/Ilse au refuge, Ilse/Aubin au palier), ouïe voisine et
  `bruit_a_voir`, sauvegarde et même laps découpé vérifiés. Banc 4 h crue/Relais × quatre
  graines : **8/8 états finaux et chroniques identiques**, 18 avis en crue, zéro adoption,
  aucune dispute naturelle, aucun plantage/usurpation, mêmes alertes historiques.
  Suite complète unique : **2 045 tests, 16 ignorés, zéro échec/erreur**, 221 fichiers,
  deux processus réduits, **1 919,09 s** ; après les derniers resserrements de réception,
  **53 tests ciblés verts en 68,01 s**, sept fichiers, un processus. Aucune seconde suite.
  Menace d'eau seulement ; parole typée du joueur et fréquence naturelle non garanties.
  [Rapport du lot 121](taches/rapport-codex-121-disputes.md).
  Fusionné sur l'intégration (`main` 0a53910 + ce lot) : aucun conflit, aucun autre lot fusionné depuis la base. Aucune dispute naturelle dans les nuits : preuve seulement par scènes d'auteur ; à surveiller à la prochaine vérification d'intégration.

- **Revue Argon du coût et lots 118–119, non fusionnés** (branches poussées `codex-reprises-exactes` `bb02f3a`,
  `codex-perception-exacte` `bd6d1eb`). Revue : `docs/taches/rapport-revue-argon-cout.md` (pistes A1 à A5 exactes, B1 à B3
  qui changent des décisions). Mesures (paires lancées ensemble, auberge 1985 12 h) : A3 tables partagées +2,6 %, A2 clé sans
  lectures mortes −0,2 %, A1 graphe gardé dès la première recherche **+15 %** (preuves précoces 60 → 365, mémoire ×2), A4 réfuté
  (les gestes dépendent de l'allure par les trajets) ; lot 118 entier +15,5 % fixe / +17,4 % tiré : non fusionné. A5 perception :
  −1 %, sous la variation entre répétitions (3 à 5 %) : non fusionné (principe : pas de cache sans gain). Le rapport à `42bb9c0`
  varie selon la cohorte (tiré ×2,64 à ×3,81) : la mesure du seuil elle-même est bruitée sur ce poste.

- **Vérification d'intégration 590653e**, lot **114**, branche
  `codex-verif-integ-590653e` : aucun code du jeu changé, sans Luna.
  **32 nuits de 12 h**, **huit rixes de 8 h**, puis **cinq nuits de 8 h
  VERIFIER + spatial 0,2** : aucun plantage, violation, usurpation, coup ni
  décès ; aucun écart de contrôle. Seule borne historique inchangée :
  auberge 42, Lucien à 314, résultat retenu égal à l'optimum **73,4743**.
  Mathe mine 3 : **3/3/3/3** gestes au lieu de **328/291/291/328** ;
  offres identiques à moins d'une heure **13 → 0** contre `47d4d25`.
  Contrepartie mine 1985 à 253 et accords corrigés sur les cas réels ;
  appels d'Odile auberge 7 à 641–644 non observés, parcours changé.
  Six avertissements textuellement redits en crue 2024 conservés ;
  aucune nouvelle anomalie établie par les seules chroniques, alertes et
  limites détaillées dans le rapport.
  **Seuil CPU ×1,5 toujours manqué**, auberge 1985 12 h, versions appariées
  lancées ensemble : fixe **118,50 → 195,08 s (×1,65)**, tiré
  **93,31 → 246,73 s (×2,64)**. Une mesure par paire sur poste partagé.
  Suite complète unique : **2 020 tests, 16 ignorés, aucun échec ni erreur**,
  217 fichiers, deux processus réduits, **1 738,20 s**. Audits historiques
  relus sans rejeu, **127 fichiers inchangés** ; CPU ancien sur archive isolée.
  Bruts `artifacts/verif-integ-590653e/`.
  [Rapport du lot 114](taches/rapport-codex-114-verif-integ.md).

- Branche `codex-comptes-recit`, **non fusionnée**, lots **117** et **117 b** (poussée, `94a0782`) : les comptes du récit
  viennent du moteur ; l'auditeur relie chaque segment à un compte fourni et choisit un sens fermé et une quantité, que le
  moteur compare. Rejeu : inversion réelle refusée 5/5, trois faux refus 5/5 → 0/5. **Non fusionnée** : une passe Luna (quatre
  scripts) donne 3,94 → 3,83 appels/tour mais **14,0 → 20,5 s/tour** et obstacles narratifs 11 → 60 ; le lot 117 seul (sans sens
  fermé) gagnait 13 % d'appels mais laissait passer l'inversion 2 fois sur 5. **Décision du 2026-10-27 : remesurer** en deux passes Luna sur la base actuelle avant de décider ; branche non fusionnée d'ici là. **Remesure faite (lot 117 c, branche `codex-comptes-recit-c` `5be5581`, portée sur l'intégration, suite verte hors MiMo)** : deux passes, sept scripts contre `cdaf371` en cache ; **11,23 → 14,78 s/tour** (+32 %), audit narratif **3,64 → 8,71 s/tour** sur les quatre scripts 117 b, obstacles narratifs **19 → 68** ; aucune inversion naturelle dans la référence, douze tentatives de faux refus comptables sur sept tours (zéro en référence) ; rejeu : inversion réelle refusée 5/5. [Rapport 117 c](taches/rapport-codex-117c-comptes-recit-mesure.md) sur la branche. **Décision du 2026-10-27 : abandonnée** au profit des comptes écrits par le moteur, hors de l'audit sémantique (lot 180).

- Branche `codex-tache-promise`, fusionnée, lot **115**, base **6910d8e** :
  une tâche typée peut payer une part dans le recours après les moyens ordinaires.
  Conditions connues, un candidat et un devis par recours, propres moyens sans
  demande ni délégation futures ; jugement inversé, marché et agendas communs.
  Aucun Luna ni changement de recherche/scénario. Brune recharge le brasero de
  Gorm ; Joss verrouille la réserve d'Odile contre un repas : état, perception,
  journal rechargé et même laps découpé contrôlés. Rupture annoncée et confiance
  diminuée, impossibilité et refus sauvegardés vérifiés. Neuf tests fonctionnels nouveaux ;
  un ancien refus ne remplace plus un nouveau plan ordinaire ni sa demande.
  Banc 4 h × quatre scénarios × quatre graines : aucun plantage/usurpation,
  aucun nouveau code d'audit, 10/16 états identiques ; aucune tâche naturelle
  offerte/acceptée/tenue/rompue dans les 16 nuits finales. Propositions/acceptées
  Relais 0/0 → 0/0, mine 13/1 → 10/1, auberge 3/1 → 3/1, crue 9/0 → 5/0.
  Mine : une observation supplémentaire de devoir satisfait chez Rémy (230 min),
  répétition et avertissement redit disparus ; pas de boucle active nouvelle.
  **Réserve CPU levée sur les huit nuits demandées** : base et branche lancées
  ensemble, un processus réduit chacune, sans cache, 4 h. Première mesure
  crue +15,66 %, auberge −1,40 % ; profil crue 2024 : recours 7,206 s (12,4 %)
  sur 58,197 s, dont devis 6,770 s (11,6 %), 32 devis avec échecs répétés.
  Levier exact `_charge_irrealisable` : sans réservoir rechargeable, une charge
  initialement fausse/inconnue ne peut devenir vraie dans le devis autonome.
  Projection datée commune, aucune décision changée ni cache persistant.
  CPU par nuit, secondes : base `6910d8e` dans les deux mesures ;
  (1) avant levier, branche `5261663` ; (2) après levier, branche `4167150` :

  | Scénario | Graine | Base (1) | Branche (1) | Base (2) | Branche (2) |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | Crue | 1985 | 17,062 | 19,516 | 16,250 | 16,141 |
  | Crue | 7 | 19,922 | 21,234 | 18,688 | 17,656 |
  | Crue | 42 | 17,344 | 22,438 | 16,828 | 17,562 |
  | Crue | 2024 | 21,625 | 24,656 | 21,156 | 21,281 |
  | **Crue total** | | **75,953** | **87,844 (+15,66 %)** | **72,922** | **72,641 (−0,39 %)** |
  | Auberge | 1985 | 15,094 | 14,969 | 14,594 | 14,750 |
  | Auberge | 7 | 16,609 | 16,703 | 16,500 | 16,641 |
  | Auberge | 42 | 16,469 | 16,062 | 16,312 | 16,094 |
  | Auberge | 2024 | 14,453 | 14,016 | 14,000 | 14,094 |
  | **Auberge total** | | **62,625** | **61,750 (−1,40 %)** | **61,406** | **61,578 (+0,28 %)** |
  | **Ensemble** | | **138,578** | **149,594 (+7,95 %)** | **134,328** | **134,219 (−0,08 %)** |

  33 tests ciblés verts (un ignoré), 36,95 s ; cas réel crue à 17 min et autre
  source d'auberge, recherche ancienne/nouvelle et rendu rechargé comparés.
  16/16 états finaux, chroniques, audits et mesures hors compteurs de recherche
  identiques avant/après optimisation sur les quatre scénarios (4 h, quatre
  graines) ; 127 recherches neuves évitées en crue. Mesure ponctuelle : le seuil
  historique ×1,5 contre `42bb9c0` n'est pas remesuré.
  Un seul candidat peut masquer un autre service possible ; verrouillage ponctuel,
  pas de garde permanente nouvelle ni de tarif de service en pièces.
  Suite complète unique : 2 033 tests, 16 ignorés, 219 fichiers, 2 266,85 s ;
  trois échecs et deux erreurs de parcours, corrigés dans leurs scènes de test.
  Reprises 101 tests (une attente de première offre), puis 13 verts en 20,04 s ;
  bilan consolidé vert, un ignoré, aucune seconde suite. Code signé SSH
  `d3567d8` / `ee0ab0c` / `4167150`, signatures vérifiées. Créneau initial dépassé
  par la vérification ; pas de seconde suite complète pendant le suivi CPU.
  Bruts `artifacts/tache-115/`.
  [Rapport et limites du lot 115](taches/rapport-codex-115-tache-promise.md).

- Branche `codex-rapports-illisibles`, fusionnée, lot **116**, base
  `5ff7ce5`, code signé SSH **6949ca6**, signature vérifiée : le schéma extrait
  nature et fondement ; le moteur déduit le
  verdict canonique d'une nature mécanique, sans jugement indépendant.
  Douze variantes, 24 qualifications ; refus sous parole/ambiance conservés,
  aucun prompt narratif ni contrôle retiré. Un premier filtrage des paires,
  abandonné, admettait des absences non prouvées. Cause établie avant changement :
  7 → 45 segments incompatibles, tous `mecanique` + portée négative,
  dans 7 → 35 audits. Schéma identique entre 95/b0042c9/91a4351 ; hausse
  antérieure à 112, pas de causalité sémantique isolée au lot 102.
  Rejeu exact Luna final : **42/42 illisibles devenus lisibles**, 10 admissions,
  32 refus ; quinze refus narratifs rejoués, quatre écarts examinés par
  cinq appels de chaque schéma, aucun recul de refus juste dépassant un
  sur cinq. Détail des écarts conservé au rapport.
  Contrôles des **68 rapports archivés identiques** à 91a4351, sources
  inchangées ; paires forgées refusées, console et recharge vérifiées.
  Deux passes Luna des six scripts du lot 93 : **18→0 audits illisibles**,
  265/78→266/80 appels/tours MJ, **3,397→3,325 appels/tour** ; moyenne
  **11,437→11,661 s/tour**, médiane **9,570→10,755 s**. Relances 17→17,
  replis 2→1, aucun arrêt ni défaut de recharge ; douze références cachées
  inchangées. **Aucun gain global de délai observé**, comparaison historique
  incluant aussi les lots 112/113. Suite complète unique : **2 029 tests,
  16 ignorés, 219 fichiers, 2 270,43 s**, deux processus réduits, aucun
  échec ni erreur. Lancée avant le dernier format ; **71 tests finaux verts,
  sept fichiers, 23,98 s**, aucune seconde suite complète. Cohérence typée
  garantie, fondement et extractions toujours sémantiques.
  Bruts `artifacts/illisibles-116/`.
  [Rapport et limites du lot 116](taches/rapport-codex-116-rapports-illisibles.md).

- Branche `codex-relances-doublees`, fusionnée, lot **113**, code signé
  `4fc1719`, base `2ef7a07` : le dossier commun de fidélité reçoit les comptes
  connus avant règlement de la copie, références nommées ; aucun prompt ni
  garde de décision changé. Attribution sans Luna des 80 parties archivées :
  406→459 appels, supplémentaires structurels 56→102 ; rapports illisibles
  9→44 (contrôle ancien lot 83), quantité implicite N4 0→4. Le dossier incomplet
  est ancien ; la perte du typage contesté passe par les lots 100/104, sans preuve
  causale de l'apparition du faux verdict. Gorm et autre dette payés une fois
  après recharge, montant divergent refusé, comptes privés exclus. Deux passes
  Luna ciblées : Gorm remboursé 2/2, 6/10→4/4 appels sur son tour ; ensemble
  comptes/guet/soir-noir 95→94 appels, 17,8→18,5 s/tour, relances 7→10,
  replis 1→2. Aucun arrêt ni défaut de recharge ; pas de gain global de latence.
  Rejeu local de 275 audits exacts identique à 91a4351 ; rejeu Luna de 21 refus :
  cinq fidélités toujours refusées, narration huit refus/six admissions/deux
  illisibles, réserves explicitées au rapport. Suite complète unique : **2 018
  tests, 16 ignorés, aucune erreur, 217 fichiers, 1 925,76 s**, deux processus
  réduits ; sept assertions d'anciens champs adaptées, **23 tests repris verts,
  54,01 s**, aucun échec de test restant reproduit, aucune seconde suite.
  Les faux refus sémantiques et rapports illisibles
  restent ouverts. [Rapport du lot 113](taches/rapport-codex-113-relances-doublees.md).
  Fusionné sur l'intégration après les lots 110 et 112 : seul conflit de documentation ; `mj.py` touché aussi par le lot 112 (rappels du passé), fusionné sans conflit textuel ; suite complète relancée. Famille suivante désignée : **rapports d'audit illisibles** (verdict/portée incompatibles, contrôle du lot 83), 9 → 44 appels supplémentaires.

- Branche `codex-redire-passe`, fusionnée, lot **112**, base `8613fc9` :
  dossier des paroles entendues par interlocuteur sous ses références publiques,
  sans fenêtre globale ; extraction des rappels du passé dans tous les verdicts,
  refus accompagné des mots enregistrés, relecture avant enregistrement.
  Aucun mot-clé ni exception de scénario ; simulation inchangée.
  Audit archivé du tour 5 rejoué avant modification : zéro obstacle ; cas réel
  reconstitué jusqu'à l'imposture puis refus corrigé, autre cas après vrai service
  de Gorm et rappel conforme admis, console et sauvegarde rechargée vérifiées.
  Luna une passe soir-noir/soir-voix : **39 appels, 14,4 s/tour MJ**, aucun
  repli ni erreur de rechargement ; aucun faux rappel observé. Reconnaissance
  et compatibilité sémantiques, anciens rapports lisibles, pas de registre
  universel des actes anciens. Suite complète unique : **2 021 tests, 16 ignorés,
  aucun échec ni erreur, 1 932,23 s**, 217 fichiers, deux processus réduits ;
  reprise finale **6 tests verts en 4,37 s**, aucune seconde suite.
  Bruts `artifacts/redire-112/`,
  `artifacts/bancs-multi/20261026-054955-38148/`.
  [Rapport du lot 112](taches/rapport-codex-112-redire-passe.md).
  Fusionné sur l'intégration après les lots 110, 111 et 114 (brief) : seul conflit de documentation ; aucun fichier de code commun. À surveiller : l'extraction `rappels` ajoutée à chaque rapport d'audit narratif allonge la sortie que le lot 95 avait réduite (latence à mesurer à la prochaine vérification Luna).

- Branche `codex-propositions-redites`, fusionnée, lot **110**, base
  `61a4406` : le refus d'un marché se lève seulement pour un moyen pertinent
  à sa cause ; une ouverture incidente ne change pas une garde, une nécessité
  ou une réticence. Inventaire au refus retenu ; nouveau bien effectivement
  offert ou force offerte supérieure permis. Propositions et achats d'un
  plan rechargé revalidés avant parole, jet ou transfert. Mine 7 à 244 et crue
  11 à 347 reproduites : portes crues ouvertes indûment comptées comme moyens.
  **34 tests ciblés verts**, dont les deux captures, monde et rendu rechargés,
  laps découpé, plan refusé sans publication, offre plus forte et nouveau bien.
  Banc 4 h × quatre scénarios × quatre graines : propositions/acceptées
  Relais **0/0 → 0/0**, mine **11/1 → 13/1**, auberge **3/1 → 3/1**, crue
  **9/0 → 9/0** ; offres identiques à moins d'une heure **1 → 0**, aucun
  plantage, violation, usurpation ou nouveau code de boucle. Les offres en
  plus portent une lampe nouvellement ramassée ; la redite est remplacée
  par un prix réellement supérieur. 16 références en cache réutilisées.
  Suite complète unique : **2 013 tests, 16 ignorés, 216 fichiers, 1 870,76 s**,
  deux processus réduits ; une erreur Windows de remplacement de fichier TUI,
  reprise du seul test verte en **6,13 s**, sans changement de code. Aucun autre
  échec ni erreur, aucune seconde suite. Aucun Luna ni changement des buts.
  Anciennes sauvegardes sans inventaire conservatrices sur un nouveau bien
  de valeur égale ; évolution sociale de la méfiance inchangée. Bruts
  `artifacts/redites-110/`.
  Code signé SSH **91f618f**, signature vérifiée.
  [Rapport et limites](taches/rapport-codex-110-propositions-redites.md).
  Fusionné sur l'intégration après les lots 108, 109 et 111 : seul conflit de documentation ; aucun fichier de code commun.

- Branche `codex-verif-luna-91a4351`, lot **111**, code **91a4351** : vérification seule, aucun code modifié. Deux passes des vingt scripts du lot 99 : **40 parties, 302 saisies, 136 tours MJ, 459 appels**, **3,38 appels/tour, 11,54 s/tour**, médiane **9,57 s**. Références 42bb9c0/882907c/b0042c9 relues, **177 fichiers inchangés**, quarante parties cachées identiques ; aucun plantage, erreur technique, arrêt ou défaut de recharge, quatorze parcours sous obstacle cohérents. **Validation partielle** : N1/N3 et fausse absence non reproduits ; N2 non reproduit mais phrase exacte non générée. Achats exécutés 2/2, confusion comptable et identité refusée après nom donné toujours présentes. Nouveau faux refus de quantité : remboursement à Gorm perdu 2/2 ; réserve sur « les faits » affichée en ambiance, surcontrôle de la non-perception. Trois replis, charges historiques différentes, aucune conclusion causale de latence ni garantie sémantique générale. Bruts `artifacts/verif-luna-91a4351/`. [Rapport et limites du lot 111](taches/rapport-codex-111-verif-luna.md).

- Branche `codex-avis-redits`, fusionnée, lot **108**, base `a73a35d` :
  le registre social conserve la dernière valeur dite par destinataire.
  Un changement connu du seul locuteur ne réinitialise plus tous les auditeurs ;
  un changement appris du destinataire rouvre ses suivis, une réaffirmation
  inchangée les conserve. Menaces dérivées, confidences et `_a_dire` partagent
  le registre ; anciennes listes migrées à la recharge. Aucun Luna ; moteur
  limité à `social.py`/`esprits.py`. Diagnostic exact `47d4d25` : les six
  répétitions crue 2024 suivent des rallumages connus des destinataires ;
  mine 2024 76/79 et mine 7 76/78 portent sur deux lampes homonymes.
  Ces annonces justifiées restent admises. Captures crue 140/mine 70 : même
  monde, chronique et rendu rechargés, laps d'un bloc ou découpé.
  Banc final 4 h × quatre scénarios × quatre graines, base mise en cache
  une fois puis réutilisée : aucun plantage ni usurpation ; répétitions
  textuelles **0/7/0/1 → 0/8/0/1**, constats confiés
  **9/83/37/22 → 9/84/37/22** (Relais/mine/auberge/crue).
  Suite complète unique : **2 007 tests, 16 ignorés, 1 915,93 s**, 214 fichiers,
  deux processus réduits ; six seules attentes d'empreinte corrigées après
  restitution exacte des six SHA-256 historiques par conversion inverse
  du seul registre ; **11 tests repris verts en 14,23 s**, deux fichiers.
  Les valeurs intermédiaires déjà effacées
  dans une ancienne sauvegarde restent irrécupérables. Bruts `artifacts/avis-108/`.
  [Rapport du lot 108](taches/rapport-codex-108-avis-redits.md).
  Fusionné sur l'intégration après les lots 105, 107 et 109 : seul conflit de documentation ; aucun fichier de code commun.

- Branche `codex-recherche-tiree`, fusionnée (diagnostic), lot **109**, base
  **70f4fae** : diagnostic seul, arrêt prescrit avant implémentation ; aucun
  moteur, scénario, cadence ou Luna modifié. Auberge 1985, ancien `42bb9c0`
  contre base actuelle, 480–720, profils puis témoins appariés, deux calculs
  réduits. Tiré/fixe actuel : **×2,67 nœuds réellement développés/recherche**,
  **392,9 contre 418,5 µs/nœud** ; **×3,42 générations de gestes/recherche**.
  Les passes offrant les deux allures portent **380 850 nœuds, 124,28 s CPU**
  dans le tiré, dont **58,86 s Tilo/faim** ; gardes et placement de Lucien
  dominent aussi. Réduire cet espace peut supprimer des plans admissibles :
  aucun levier principal exact établi, décision demandée avant changement.
  CPU témoins 12 h, compteurs actifs, ancien→actuel :
  **121,47→218,84 s fixe (×1,80)**, **102,53→277,31 s tiré (×2,70)** ;
  aucune nouvelle mesure CPU nue ni gain levant le seuil ×1,5 manqué au lot 105.
  Quatre nuits profil/témoin identiques (mondes 480/720, recherches, gestes),
  huit recharges monde/rendus vertes, SHA-256 moteur inchangés. Vérifications
  conditionnées à l'implémentation non lancées. Bruts `artifacts/recherche-109/`.
  [Rapport et décision du lot 109](taches/rapport-codex-109-recherche-tiree.md).
  **Décision du 2026-10-27 : pas maintenant** (réduire l'exploration des deux allures, 58 % du CPU de recherche en départ tiré, peut changer des plans) ; le coût revient après A4.

- Branche `codex-contreparties`, fusionnée, lot **107**, base `303d38c` :
  le recours demande une part utile ou les pièces manquantes, au plus au prix
  offert, avec une source monétaire explicite conservée. Contrôle inversé du
  lot 57 conservé ; anticipation de valeur par les P/G et le DD communs, sans
  dispositions privées adverses. Plans rechargés revalidés ; paiement partiel
  atomique, sans céder le contenant. Validation structurelle des termes commune
  aux propositions et audits. Aucun Luna, délibération/planification inchangées.
  Mine 1985 à 253 reproduite puis capture/recharge vérifiées ; auberge, paiement
  partiel et scènes raisonnables du lot 45 couverts. Banc 4 h × quatre scénarios
  × quatre graines : **16 états, chroniques et mesures identiques**, aucune
  usurpation ni boucle nouvelle ; propositions/acceptées Relais **0/0**, mine
  **12/1**, auberge **3/1**, crue **9/0**. Suite complète unique : **2 001 tests,
  16 ignorés, 213 fichiers, 1 870,08 s**, deux processus réduits ; une erreur
  temporaire Windows TUI, reprise isolée verte en **2,66 s** ; reprises finales
  **34 tests verts, un ignoré, cinq fichiers, 31,34 s**, aucun défaut restant
  reproduit, aucune seconde suite. Anticipation neutre sans garantie d'accord ;
  source portée exigée, pas de livraison différée de pièces. Bruts
  `artifacts/contreparties-107/`.
  [Rapport et limites](taches/rapport-codex-107-contreparties.md).
  Fusionné sur l'intégration après les lots 103 et 105 : seul conflit de documentation ; aucun fichier de code commun.

- Branche `codex-suites-par-noeud`, fusionnée, lot **105**, base **dcd7b31**,
  code signé **0aa644a** : `_mesurer` compose les seuls changements de portes
  et reprend le successeur sans reconstruction quand rien ne change. Aucun
  changement de coûts, d'ordre, de nœuds, de relances ou de scénario ; aucun Luna.
  Trois tests ciblés verts, composition, captures ordonnées/coûts hexadécimaux,
  tour moteur et rendu rechargé mine/auberge. Vingt répétitions par capture :
  génération **196,67→177,68 µs/nœud mine 480**, **209,73→199,24 auberge 480**,
  **284,13→249,70 auberge 600**, six recherches identiques à la base.
  CPU 12 h apparié, deux processus réduits : base→branche **227,64→217,42 s
  fixe (−4,49 %)**, **280,42→260,81 s tiré (−6,99 %)**, **90,41→86,88 s mine
  (−3,90 %)**. Contre `42bb9c0`, auberge **×1,75 fixe / ×2,67 tiré** : seuil
  ×1,5 non atteint, pas suffisant pour avancer `main`. Trois nuits base/branche
  et trois répétitions branche identiques avec `comparer --calcul`, douze
  recharges vertes. Empreintes 2 h, quatre scénarios × quatre graines :
  **16 identiques**, huit références relues, huit manquantes calculées une fois.
  `VERIFIER` + spatial 1, auberge 42 tirée, 2 h : aucun écart ni borne,
  **1 221 nœuds, 350,44 s CPU**, recharge correcte. Suite complète unique :
  **1 994 tests, 16 ignorés, aucun échec ni erreur**, 212 fichiers, deux processus
  réduits, **1 806,26 s**. Même SHA-256 moteur qu'aux mesures.
  Un seul levier ouvert ; gains observés, pas de preuve statistique sur ce poste
  partagé. Bruts `artifacts/suites-105/`.
  [Rapport du lot 105](taches/rapport-codex-105-suites-par-noeud.md).
  Fusionné sur l'intégration après les lots 106 et 103 : seul conflit de documentation ; aucun fichier de code commun (`planification.py` seul). Seuil ×1,5 toujours manqué (auberge ×1,75 fixe / ×2,67 tiré dans cette cohorte).

- Branche `codex-boucle-garde-manger`, fusionnée, lot **103**, base
  `811ae4b`, code signé SSH `ddfbc36` : la garde laisse finir la remise sous clé
  prévue par le plan d'un autre but, même sans motif urgent. Mine 3, capture
  à 8 min : service de Lucien contre garde, avant le premier service ; défaut
  ancien révélé par la fusion des contre-offres `1e7b4d9` (parent : 14 gestes
  sur le garde-manger en 30 min ; fusion : 353). Aucune route ni MJ modifié.
  Mathe et Gorm servant depuis leur réserve gardée : même monde, croyances,
  chronique et rendu après recharge, laps d'un bloc ou découpé. Garde après
  un tiers conservée. Suite complète unique : **1 988 tests, 16 ignorés,
  2 092,61 s**, deux processus réduits ; deux erreurs du nouveau placement
  de rendu et une régression intermédiaire de l'arbitrage de la garde elle-même
  corrigées, sans modifier les tests historiques ; **33 tests repris verts en
  135,02 s**. Banc 4 h × quatre scénarios × quatre graines : aucun plantage
  ni usurpation, mêmes catégories et nombres de constats ; avis redits en mine
  **3 → 7**, limite sociale conservée. Audit mine 3, 12 h : gestes sur la
  réserve **328/291/291/328 → 3/3/3/3**, Lucien servi à 9 min ; aucune rafale,
  ni usurpation. **VERIFIER + spatial.VERIFICATION=1, mine 3, 2 h : aucun écart, borne reconnue, plantage ni usurpation**, 4 532 s à priorité réduite. Limite : les plans portant une
  restauration sous clé ; aucune preuve générale sur toutes les boucles.
  [Rapport du lot 103](taches/rapport-codex-103-boucle-garde-manger.md).
  Fusionné sur l'intégration après les lots 104, 98 b et 106 : seul conflit de documentation ; aucun fichier de code commun (`deliberation.py` seul).

- Branche `codex-accords`, fusionnée, lot **106**, base `dcd7b31` :
  nombre déclaré prioritaire, sinon tête du nom, commun aux désignations,
  accords sociaux et quantités ; pièces des échanges, missions, fiches, TUI
  et compteur web centralisées dans `francais`. Aucun Luna ni changement de
  scénario, planification ou délibération. Odon mine 7 reproduit ; échange
  Lucien–Anselme reconstitué ; état, chronique, récit et vue après recharge.
  Empreintes 2 h Relais/mine × quatre graines : **mesures et empreintes de jeu
  identiques**. État final : seulement **28 chaînes accordées**, 19 désignations
  d'outils et neuf contre-offres à une pièce ; huit SHA-256 complets identiques
  après restauration de ces seules chaînes, huit recharges et rendus verts.
  Suite complète unique : **1 995 tests, 16 ignorés, 1 822,58 s**, 212 fichiers,
  deux processus réduits ; cinq échecs/deux erreurs corrigés, reprises finales
  **158 tests, un ignoré, aucun défaut restant**, onze fichiers ; aucune seconde
  suite. Les noms invariants ambigus demandent toujours `pluriel` explicite ;
  les anciennes phrases sauvées restent historiques. Bruts `artifacts/accords-106/`.
  [Rapport et limites](taches/rapport-codex-106-accords.md).

- Branche `codex-profil-compare`, fusionnée, lot **98 b**, base **677f4c1** :
  `_moyenne` relève les obstacles une fois par calcul, sans cache supplémentaire,
  au lieu de rescanner tous les objets par case. Même sol, même projection crue ;
  chemin `pur` case par case conservé pour `spatial.VERIFICATION`, clé existante
  inchangée. Aucun changement de relances, coût, décision ou scénario ; aucun Luna.
  Onze tests ciblés verts, dont captures auberge/mine, tour moteur, monde et rendu
  rechargés contre oracle direct. CPU 12 h apparié, deux processus réduits :
  base→branche **250,27→240,92 s fixe (−3,74 %)**, **292,23→286,16 s tiré
  (−2,08 %)**, **91,72→89,97 s mine fixe (−1,91 %)**. Contre `42bb9c0`,
  auberge **×1,93 fixe / ×2,85 tiré** : seuil ×1,5 non atteint.
  `comparer --calcul` : trois nuits base/branche et trois répétitions branche
  identiques, mêmes choix, recherches et nœuds ; douze recharges vertes.
  Empreintes 2 h, quatre scénarios × quatre graines : 16 identiques, référence
  677f4c1 manquante calculée une fois puis rangée en cache depuis l’archive locale.
  `VERIFIER` + spatial 1, auberge 42 tirée, 2 h : aucun écart ni borne,
  1 221 nœuds, 392,25 s CPU, recharge correcte. Suite complète unique : **1 972
  tests, 16 ignorés, aucun échec ni erreur**, 207 fichiers, deux processus réduits,
  **2 079,91 s**. Même SHA-256 moteur qu’aux mesures ; variations de répétitions
  branche 1,6–6,0 %, gains non établis statistiquement.
  Pas de deuxième levier ouvert ; créneau dépassé par les vérifications prescrites.
  Bruts `artifacts/obstacles-98b/`.
  [Rapport et limites](taches/rapport-codex-98b-obstacles.md).

- Branche `codex-profil-compare`, fusionnée, lot **98**, base **61c854a** :
  diagnostic seul, aucun moteur/scénario/MJ modifié, aucun Luna. Auberge 1985,
  fixe puis tirée, `cProfile` CPU sur 480–720 et témoins sans instrumentation,
  ancien/intégration appariés, deux calculs à priorité réduite. Choix/minute
  **14,91→20,17 / 13,84→16,52**, recherches/minute **16,75→26,46 / 10,49→19,48** ;
  filet minute inchangé (1 920), hausse hors minute **+76 % / +46 %**.
  Recherche moyenne instrumentée **99,30→92,31 / 123,29→209,10 ms** : fréquence
  et coût unitaire comptent ; décomposition descriptive des recherches :
  **58 % fréquence / 42 % coût moyen**, sans causalité établie entre mondes différents.
  **Arrêt prescrit avant implémentation** : réduire les relances peut changer
  les décisions. Piste exacte secondaire non codée : relever les obstacles une
  fois dans `_moyenne`, au lieu d'un balayage d'objets par case ; gain inconnu.
  CPU normal 12 h : **127,38→244,41 s (×1,92) fixe**, **94,48→273,92 s (×2,90)
  tiré** ; seuil ×1,5 manqué. Huit recharges vertes ; mêmes compteurs, mesures
  et états à 480/720 entre profils et témoins, quatre nuits.
  Pas de suite complète ni de vérification conditionnée à une implémentation.
  Outils et bruts `artifacts/profil-98/`, créneau dépassé par les profils complets.
  [Rapport et décision demandée](taches/rapport-codex-98-profil-compare.md).
  Lots 98 et 98 b fusionnés ensemble sur l'intégration après les lots 97 et 100 à 104 : seul conflit de documentation ; aucun fichier de code commun (`trajet_estime.py` seul). 58 % du surcoût de l'auberge vient de la fréquence des choix et recherches (délibération à l'événement, recours) ; la réduire peut changer le moment de certaines réactions des PNJ. **Décision du 2026-10-27 : pas maintenant**, le coût revient après A4.

- Branche `codex-n3-reformule`, fusionnée, lot **104**, base `e4dbc6a` :
  le rejeu exact du fil lot 102 reproduit N3 avant correction (trois appels,
  aucune parole sauvée). La revue refusait le contenu `qui` tout en cochant
  cette opération ; elle devenait une obligation indue pour la correction et
  le secours. Le contrat commun distingue les opérations présentes dans le
  contenu rejeté des omissions reconnues ; les obligations déjà confirmées
  ou non examinées restent conservées. Le secours aux mots exacts, sans
  contenu typé ni obligation, ne relance plus une revue redondante.
  **21 tests ciblés verts**, cinq fichiers (48,05 s puis 37,68 s), console,
  état et rendu après recharge,
  cas réel, salle éclairée, correction refusée aussi et saisie inintelligible.
  Passe Luna unique : **9 tours MJ, 38 appels, 13,40 s/tour**, `soir-noir` et
  `noms-dialogue`, N3 absent, aucun arrêt, repli ni défaut de recharge.
  Suite complète unique : **1 990 tests, 16 ignorés, 210 fichiers, 2 133,20 s**,
  deux processus réduits ; quatre attentes obsolètes corrigées (libellés et
  comptes d'appels), puis **9 tests verts** dans les deux fichiers repris,
  aucune seconde suite. Aucun défaut restant reproduit.
  Le jugement de sens reste sémantique et
  un contenu non exécutable reste refusé ; la réplique refusant le nom déjà
  donné subsiste hors invariant. Aucun prompt ni modèle changé.
  [Rapport du lot 104](taches/rapport-codex-104-n3-reformule.md).

- Branche `codex-absence-noir`, fusionnée, lot **102**, base `e218907` :
  le dossier d'audit porte la couverture réelle de la vue (`aucune`, `partielle`,
  `salle`), calculée sans les entités cachées. Une absence est mécanique,
  distincte d'une non-perception ; les refus de portée restituent la perception
  courante dans leur `attendu`. Cas réel reproduit : Ilse et Brune présentes
  dans l'antichambre noire, fausse absence affichée et sauvegardée. Neuf tests
  ciblés verts : deux personnes, objet, vue éclairée et fouille exécutée,
  état et rendu après recharge. Passe Luna unique : trois scripts, **17 tours MJ,
  58 appels, 10,6 s/tour**, fausse absence non reproduite, aucun défaut de recharge.
  `soir-noir` conserve un abandon de parole avec « Reformule-la » et une réplique
  incohérente avec les paroles précédentes, hors de l'invariant de ce lot.
  Suite complète unique : **1 982 tests, 16 ignorés, 208 fichiers, 1 907,24 s**,
  deux processus réduits ; une erreur Windows TUI de remplacement temporaire
  avant action (`WinError 5`), **rejeu du seul test vert en 3,05 s**, sans
  changement de code ni seconde suite complète. La couverture est déterministe ; la reconnaissance
  d'une absence dans une phrase reste sémantique. Le verdict historique erroné
  rejoué tel quel passe encore : aucune garantie générale sur les paraphrases.
  [Rapport du lot 102](taches/rapport-codex-102-absence-noir.md).
  Fusionné sur l'intégration après le lot 101 : seul conflit de documentation ; `narration.py` touché aussi par le lot 101 (garde lexical), fusionné sans conflit textuel ; suite complète relancée. **À reprendre** : `soir-noir` montre encore « Ta demande n'a pas été exécutée. Reformule-la. » sur une base qui contient le lot 100 (N3 non clos), et une voix qui dit avoir refusé son nom après l'avoir donné.

- Branche `codex-mots-courants`, fusionnée, lot **101**, base `31e3f9c`.
  Révision après `2d54461`/`4920a9e` : les réserves sur la preuve restent refusées
  lexicalement **sans source interne nommée** ; les tests historiques d'ambiance sont
  rétablis à l'identique de la base, avec leur `attendu`. Le garde commun distingue
  passif de preuve, négation impersonnelle et absence d'information d'un acte accompli
  ou d'un support concret ; aucun sujet du monde sélectionné. Les mots courants,
  unités ordinaires et phrase réelle de `soir-appel` restent admis. Aucun prompt,
  chaîne de correction ni repli modifié. **25 tests ciblés verts**, puis **92 tests verts en 36,28 s**,
  huit fichiers repris à deux processus de priorité réduite ;
  narration, monde, regard et carte contrôlés après recharge par MJ simulé.
  Suite complète initiale unique : **1 979 tests, 16 ignorés, 1 976,44 s**, deux
  échecs nominaux corrigés puis 21 tests verts ; aucune nouvelle suite complète.
  Luna initiale conservée, sans nouvelle passe : `soir-appel` **18 appels / 4 tours MJ
  (4,5)**, `ressources` **12 / 3 (4)**, aucun refus, repli ou défaut de recharge.
  Limite : constructions polysémiques et paraphrases restent en partie sémantiques,
  sans relâcher les refus historiques de preuve. Aucune garantie universelle
  d'absence de faux refus.
  [Rapport du lot 101](taches/rapport-codex-101-mots-courants.md).
  Fusionné sur l'intégration après le lot 100 : seul conflit de documentation ; aucun fichier de code commun. Première version renvoyée : elle relâchait les réserves de preuve du lot 25 et réécrivait leurs tests ; la révision `abaf283` les rétablit à l'identique (refus lexical) et n'admet que les emplois concrets.

- Branche `codex-sans-message-technique`, fusionnée, lot **100**, base
  `a86fdd7` : enveloppe des réponses contrôlée avant les audits, correction
  `RefusDeForme` distincte, puis repli de perception si la forme reste invalide.
  Les déclarations candidates de parole ne sont plus confondues avec les
  opérations reconnues par la revue ; un typage contesté ne condamne plus les
  mots exacts. Omission locale, préparation refusée et revue illisible conservent
  les obligations non examinées. N1 préexistait aux lots suspects (`723d7d6`) ;
  N3 venait du cumul introduit par le lot 91 (`031a86e`).
  Reproductions console avec recharge avant correction ; passe Luna unique sur
  atelier, soir-noir, noms-dialogue, échanges : **23 tours, 81 appels, 10,88 s/tour**,
  aucun arrêt, erreur technique, repli ni défaut de recharge ; N1/N3 absents.
  Reprises finales : **96 tests verts, 10 fichiers, 133,73 s**, un processus réduit ;
  suite complète unique : **1 975 tests, 16 ignorés, 207 fichiers, 2 046,41 s**,
  deux processus réduits ; quatre erreurs et deux échecs corrigés, aucun défaut
  restant reproduit, sans seconde suite complète. Les contrôles de sens restent sémantiques et
  une opération exigée sans contenu exécutable reste inexécutée : pas de garantie
  générale sur toutes les voies historiques de refus.
  [Rapport du lot 100](taches/rapport-codex-100-sans-message-technique.md).
  Fusionné sur l'intégration après le lot 97 : seul conflit de documentation ; aucun fichier de code commun. Une passe Luna seulement : appels par tour en hausse sur `soir-noir` et `atelier`, en baisse sur `echanges`, à revoir à la vérification Luna groupée.

- Branche `codex-promesse-joueur`, fusionnée, lot **97**, base `be5fe50`,
  code signé SSH `886eae5` : les devis autonomes et les fournitures futures
  exigent un profil avant toute recherche. Les remises déjà en main restent
  possibles ; aucune prise future jouée pour le joueur ou un PNJ sans profil.
  Gardes explicites dans `chercher` et `devis_pulsion`, sans modification des
  graphes ni des certificats. Plantage reproduit avant correction par MJ simulé
  dans la console, crypte et Relais : ici l'acteur sans profil est Gorm,
  pas le joueur (acteur de la trace initiale inconnu). **17 tests ciblés verts,
  un ignoré**, état et rendu persistés après recharge ; empreintes Relais
  **2 h × quatre graines identiques** à la base. Une passe Luna : crypte
  **42 tours / 22 appels**, ressources **3 tours / 12 appels**, aucun arrêt,
  erreur technique, repli ou défaut de recharge. Suite complète unique :
  **1 967 tests, 16 ignorés, 1 912,52 s**, deux processus réduits ; une erreur
  TUI de remplacement temporaire Windows (`WinError 5`, avant action),
  **rejeu du seul test vert en 1,73 s**, sans changement de code ni seconde
  suite complète. Aucun défaut restant reproduit ; pas d'autre calcul
  simultané pendant la suite de ce lot.
  Limite : aucun trajet ni service autonome nouveau pour un personnage sans
  profil ; le jugement sémantique de Luna n'est pas renforcé.
  [Rapport du lot 97](taches/rapport-codex-97-promesse-joueur.md).
  Fusionné sur l'intégration après le lot 92 c : seul conflit de documentation ; `planification.py` touché aussi par le lot 92 c (certificats), fusionné sans conflit textuel ; suite complète relancée sur la fusion.

- Branche `codex-verif-luna-b0042c9`, lot **99**, code d’intégration **b0042c9**
  inchangé : deux passes des vingt scripts du lot 79, **40 parties, 302 saisies,
  136 tours MJ, 406 appels**, Luna ChatGPT medium/libre, quatre exécutions au plus
  à priorité réduite sur copies. Références 42bb9c0/f033364/fbcf0ff/882907c
  exclusivement relues ; 257 fichiers de cache inchangés, quarante nouvelles
  parties rangées avec SHA-256 identiques. Face à 882907c : **12,747 → 10,335 s/tour
  (−18,9 %)**, médiane **11,725 → 9,585 s** ; appels **388 → 406 (+4,6 %)**.
  Charges différentes : aucune attribution causale. Achat du soir plus lent
  (**16,5 → 20,4 s/tour**) mais paiement/remise exécutés **2/2**, or 26→23,
  `planches_1` portée après recharge. **Validation partielle** : fausse absence
  d’Ilse encore affichée en p1 ; orientation de Gorm et faux compte nominatif
  non reproduits, sans garantie sémantique générale. Nouveaux constats : description
  du mur remplacée par « Faits narratifs invalides » aux deux passes ; « données »
  censuré dans une remise, puis repli ; appel de présence abandonné aux deux passes.
  Trois replis détectés, aucun plantage du jeu, erreur réseau ni défaut de recharge ;
  `profil` nul non reproduit. Erreur de rangement du lanceur auxiliaire reprise
  sans rejouer Luna, trace conservée. Quatorze parcours sous-obstacle cohérents
  après recharge ; limites du rendu des panneaux inchangées. Aucun code ni test
  moteur modifié ; aucune suite complète relancée pour ce lot de vérification.
  [Rapport et limites](taches/rapport-codex-99-verif-luna.md).

- **Vérification d'intégration 47d4d25**, lot **94**, sans Luna ni changement de code.
  Branche `codex-verif-integ-47d4d25`, base documentaire `a5cb018` ; références
  `42bb9c0` et `5c2ce81` relues sans rejeu. Audit 12 h × quatre scénarios × huit graines,
  rixe/rixe_douce 8 h × quatre graines : aucun plantage, violation, usurpation,
  coup contre une personne ni décès. `VERIFIER` + spatial 0,2, 8 h, graine 42,
  cinq scénarios : aucun écart ; une ancienne borne reconnue (auberge, Lucien 314,
  lumière), résultat retenu égal au recalcul complet, 73,4743. Auberge contrôlée :
  2 328 s contre 881 s auparavant, charges différentes, sans conclusion CPU.
  Suite complète unique : **1 950 tests, 16 ignorés, aucun échec/erreur**, 203 fichiers,
  deux processus à priorité réduite, **1 871,95 s** ; aucune seconde suite.
  Contre `5c2ce81`, sans recours par nuit Relais/mine/auberge/crue :
  **169/25/151/149 → 92/21/146/146** ; attente **271/1342/376/513 → 454/1361/490/546** ;
  pire passages/PNJ/h **10/35/42/49 → 10/19/42/28**. Noir et eau ne baissent pas
  généralement ; les moyennes ne garantissent pas l'absence de boucle.
  **Nouveau petit lot : mine 3, Mathe dès 9–10 min**, protection sous clé contre
  service de Lucien : **328 déverrouillages, 291 ouvertures et fermetures,
  328 verrouillages**, sans telle rafale dans les références. Un acteur défait ses propres progrès,
  ce que les bascules entre acteurs ne comptent pas ; cause précise à établir.
  Persistent : offres identiques (mine 7, Josse 244), outil contre toute la paie
  (mine 1985, Odon 253), avertissements textuels espacés (crue 2024), accords.
  Anciens refus de marche sur l'eau et clôture unilatérale non observés ; appels
  dans plusieurs lieux et nouveaux rendez-vous rapprochés restent possibles.
  Ancienne tâche aussitôt abandonnée non exercée, offres refusées en crue 7.
  Aucun correctif ni intervention sur `main`. Bruts et tableau des 96 nuits dans
  `artifacts/verif-integ-47d4d25/` du dépôt principal ;
  [rapport du lot 94](taches/rapport-codex-94-verif-integ.md).

- Branche `codex-aller-utile`, fusionnée, lot **92 c**,
  suite de `7598fc4`, base moteur **9810f4a** : une preuve d'absence complète
  les seuls nœuds manquants à leur profondeur minimale, avec les gestes communs.
  Mesure auberge 1985 tirée : 31 lacunes de faim certifiables ; borne prudente
  **358 057 expansions évitables − 10 353 états enrichis = 347 704, 33,06 %**
  de `[480, 720[`. Pas de nouveau cache ou champ sauvé ; permissions et profondeur
  restent dans la signature, borne de recherche et attente bornée restent distinctes.
  Vues de preuve et devis privés, lumière couverte dans les deux graphes ;
  discrétion nouvelle et budget de preuve ne certifient rien. `VERIFIER` refait
  toute reprise de certificat avec la complète à `REFERENCE`.
  Captures Joss 622, Tilo 566, mine 480 et plan positif : mêmes coûts/plans,
  monde et rendus après recharge ; Joss et mine à zéro nœud au troisième appel.
  **32 tests ciblés existants + huit nouveaux verts**, 16 empreintes de 2 h
  identiques contre la base ; `VERIFIER` + spatial 1 auberge 42, 2 h : aucun
  écart ni borne, **354,34 s CPU**. Suite complète unique : **1 947 tests,
  16 ignorés, 201 fichiers**, deux processus, **1 828,67 s** ; une empreinte
  historique de calcul adaptée sans changement du contrat joueur, une erreur
  Windows TUI de remplacement temporaire non reproduite. **Deux reprises
  ciblées vertes**, aucun défaut restant consolidé, sans seconde suite complète.
  CPU 12 h, deux cohortes appariées ancien/branche et base/branche, deux processus :
  gains contre base **auberge fixe 0,1 %, tirée 5,1 % ; mine fixe 3,0 %, tirée 2,6 %**.
  Auberge tirée : **335,31 → 318,27 s**, **1 175 083 → 706 709 nœuds**.
  `comparer --calcul` : quatre nuits identiques contre base et entre répétitions
  branche ; monde et rendus rechargés identiques. Contre `42bb9c0`, auberge
  **×1,96 fixe / ×3,22 tirée** : seuil **≤ ×1,5 non atteint**, `main` reste en attente.
  Mesures 8–12 h, preuve, limites et reproduction dans le rapport ; lot livré
  par commit signé sur la branche, sans fusion.
  [Rapport et mesures](taches/rapport-codex-92c-preuves.md).

- Branche `codex-aller-utile`, fusionnée, lot **92 b**, suite de `dd32414` :
  P2 mesurée en **sous-arbres**, moteur **9810f4a inchangé**. Auberge 1985 tirée,
  `[480, 720[` : **1 051 797 expansions** ; **781 841 (74,33 %)** descendent
  d'au moins un `prendre`/`ouvrir`/`alimenter`, avec recoupements entre préparatifs.
  Clôture transitive des moyens des buts faim/chaleur/lumière, faits de charge
  distingués de la source elle-même ; buts opaques et géométrie métrique gardés.
  **135 expansions (0,0128 %)** seulement établies sans rapport : recharger un
  fourneau déjà allumé, pour Joss/chaleur. **P2 non implémentée**, seuil de ~15 %
  manqué par cette clôture conservatrice ; une analyse plus fine pourrait encore aider.
  Tilo/faim : **376 appels, 266 recherches, 246 327 expansions**, médiane
  **1 205 états distincts développés** ; Joss/faim : **165 / 133 / 358 430**,
  médiane **2 741**. L'ampleur vient des combinaisons de moyens de lumière
  susceptibles de servir et des recherches recommencées, pas du seul nombre de successeurs.
  Clé complète contrôlée, FOR/DEX compris : **170 relances par les prix seuls**
  pour Tilo et **103 pour Joss**, soit **180 129 + 272 783 expansions**.
  Rejeu Joss à 622 : un état développé à profondeur **8**, sans successeurs,
  est retrouvé à **6** par la preuve : lacune, aucune impossibilité certifiée.
  Tilo à 566 : quinze états certifiés, puis zéro exploration. Trois outils de
  diagnostic livrés, mêmes résultats, empreintes, diagnostics hors durées et
  rendus après recharge ; aucune suite complète ni campagne CPU d'implémentation.
  Piste proposée : mesurer la complétion de la preuve aux profondeurs minimales.
  P3 : tarifer directement les routes avec la pression ne suffirait pas à sa preuve
  (portes et admissibilité/retour) et pourrait déjà changer les décisions hors plafond.
  [Rapport et limites du lot 92 b](taches/rapport-codex-92b-pertinence.md).

- Branche `codex-aller-utile`, fusionnée, lot **92**, base **56581f1**,
  moteur identique à **9810f4a** : **arrêt après mesure, P3 non implémentée**.
  Auberge 1985 tirée, 8–12 h : `aller` **88,78 %** des successeurs parcourus ;
  **33,80 %** des expansions sans autre successeur ni but immédiat. Ce compte
  ne prouve pas qu'un arrêt soit supprimable : objets/PNJ connus, pression
  sur les routes et effets des portes doivent être conservés sans domination
  prouvée. Majorant d'un filtre conservateur sans pression variable, eau ni
  effet de porte connue : **5 237 / 1 055 783 expansions, 0,496 %**, sous ~15 %.
  CPU témoin : **324,52 s** sur la tranche, recherches **301,16 s**,
  **285,24 µs/expansion**. Tilo/faim **65,13 s**, Lucien/ballot **47,39 s**,
  Joss/faim **43,02 s** ; préparatifs `ouvrir`, `alimenter`, `prendre` dominent
  hors trajets. Deux outils de diagnostic livrés ; témoin et relevés conservent
  empreintes, résultats de tous les appels, monde, regard et scène après recharge.
  `comparer --calcul` : **une nuit identique**, 1 175 083 nœuds sur 12 h.
  Aucun moteur, MJ, scénario ou `main` modifié ; aucune suite complète lancée
  après l'arrêt prescrit. Piste à mesurer : P2, pertinence des préparatifs ;
  une domination locale des routes sous pression pourrait encore aider P3,
  sans preuve ni gain général établis ici.
  [Rapport et limites](taches/rapport-codex-92-aller-utile.md).
  Lots 92, 92 b et 92 c fusionnés ensemble sur l'intégration après les lots 90, 88, 93, 95 et 96 : seul conflit de documentation ; `planification.py` touché aussi par le lot 90 (séjour du recours), fusionné sans conflit textuel ; suite complète relancée sur la fusion. Coût : nœuds auberge tirée 1 175 083 → 706 709, mais CPU −5 % seulement ; seuil ×1,5 non atteint (×1,96 fixe / ×3,22 tiré).

- Branche `codex-relances`, fusionnée, lot **96**, base `72ff7ae`
  (code `7b2691f`), code signé SSH `1c72176` : `SCHEMA_PAROLE` dérive les champs vides obligatoires
  de `CHAMPS_CONTENU`, comme le validateur, avec une variante et description
  par type. Aucun effacement de charge ni contrôle supprimé ; l'essai de
  regroupement par forme, qui détournait les propos vers des échanges, est écarté.
  Mesure avant code : **78 tours, 257 appels, 11,874 s/tour**, médiane **10,690 s** ;
  douze références absentes du cache jouées puis rangées, SHA-256 vérifiés.
  Deux passes finales : **252 appels, 10,784 s/tour (−9,17 %)**, médiane **9,670 s** ;
  relances narratives **16 → 11**, refus **17 → 18**, replis **2 → 1**.
  Champs sans sens : **2 corrections / 9,262 s → zéro correction** ; ce faible
  coût (**0,119 s/tour**) ne permet pas d'attribuer le gain global au correctif.
  Une partie finale réseau/délai remplacée seule ; un essai antérieur arrêté
  sur un `profil` nul dans le planificateur, hors périmètre. Aucun défaut de
  recharge sur les douze parties finales retenues. Deux exécutions réduites
  par campagne, quatre Luna au plus avec les rejeux, poste partagé.
  **Réserve de validation : conservation des refus sémantiques non validée.**
  Paiement inversé refusé des deux côtés ; livraison indûment affirmée,
  cinq rejeux exacts après deux rapports illisibles initiaux : **4 refus /
  1 illisible → 0 refus / 4 illisibles / 1 admission**. Les instructions,
  schémas et contrôles de cet audit sont identiques ; motifs parfois faux,
  critère non clos. Aucune garantie sémantique générale ; comptes, lumière
  et portée restent ouverts. Suite complète unique verte : **1 963 tests,
  16 ignorés**, 205 fichiers, deux processus réduits, **1 910,32 s**.
  Après affinement de la représentation : **19 tests ciblés finaux verts,
  38,83 s**, deux scénarios sans correction et même état/rendu après recharge ;
  les charges interdites restent refusées. Aucune seconde suite complète.
  [Rapport du lot 96](taches/rapport-codex-96-relances.md).
  Fusionné sur l'intégration après le lot 95 : aucun conflit. Réserve jugée non attribuable au lot : l'audit rejoué (livraison indûment affirmée) a les mêmes entrées, instructions et schéma des deux côtés, le correctif ne touche que le schéma des paroles de l'interprétation. **À revoir** : cette instabilité de l'audit narratif sur un même dossier (4 refus sur 5 puis 0 sur 5) et les familles évitables restantes (extractions de comptes, extraction lumineuse, portée sémantique du récit, rapports illisibles).

- Branche `codex-audit-narratif`, fusionnée, lot **95**, base `036d5f2`,
  code signé SSH `adb07f7`, correctif `49fa7d6` : preuve exacte des segments moteur, audit des seuls
  segments libres avec indices conservés ; rapport variant selon verdict/portée,
  extractions sans objet omises et motif de refus borné à 240 caractères.
  Preuve refaite à l'enregistrement, attestations courantes revalidées,
  couverture des comptes par le rendu complet de l'opération typée ; aucun
  crédit global pour un rendu partiel, contrôles déterministes conservés.
  Mesure initiale `29ccf1e` : **76 audits, 134 segments, zéro segment exact**,
  **215,57 jetons de sortie/appel**, dont beaucoup de motifs non utilisés.
  Deux passes des six scripts, **78 tours par variante** : **13,038 → 11,720
  s/tour (−10,1 %)**, médiane **12,41 → 10,24 s** ; **251 → 254 appels**,
  relances **8 → 11**, refus **23 → 21**, replis **1 → 1**. Audits : **76 → 79**,
  **5,20 → 3,89 s/tour**, sortie **16 383 → 10 431**, entrée **662 887 →
  1 173 129** (schéma à variantes plus gros). Aucun arrêt, erreur technique
  ni défaut de recharge sur les 24 parties. Douze références jouées une fois,
  relues du cache, SHA-256 identiques ; deux exécutions par variante,
  quatre au chevauchement, priorité réduite, poste partagé.
  Suite complète unique : **1 961 tests, 16 ignorés, 1 858,74 s**, deux
  processus réduits ; six échecs et une erreur dans cinq fichiers : attentes
  d'appels adaptées et lien résultat/comptes corrigé. **30 tests ciblés finaux
  verts, trois ignorés, 12,64 s**, couvrant les cinq fichiers et les nouveaux
  tests ; aucun défaut restant reproduit, sans seconde suite complète.
  Correctif final sans effet sur les 264 requêtes archivées de branche/rejeu
  (22 résultats résolus, aucun compte d'issue) : mesures Luna conservées.
  **Réserve levée selon le seuil demandé le 26 octobre : fusionnable.**
  Le rejeu initial avait perdu un refus juste. Sans changer le code, trente
  appels supplémentaires, trois audits × deux rapports × cinq répétitions,
  entrées exactes, deux exécutions au plus à priorité réduite : refus référence
  → nouveau **1/5 → 0/5** (second préalable aux crochets), **1/5 → 4/5**
  (premier préalable), **4/5 → 3/5** (ambiance, voix/lueur). Un rapport illisible
  de chaque côté pour le premier préalable, compté à part ; aucune erreur
  technique. Les trois cas passent la tolérance d'un refus de moins sur cinq :
  perte initiale traitée comme variance selon cette règle. Les motifs d'ambiance
  varient et incluent des faux refus ; aucune garantie sémantique générale.
  Entrée +77 % : surtout 14 variantes du schéma, **2 245 → 5 999 jetons estimés**
  sur les mêmes entrées ; cache **25,2 → 28,8 %**, donc pas de perte globale
  observée. Non-caché/appel **+62 %**, premier delta **+0,174 s** : surcoût
  compatible, causalité non isolée. Bruts : `variance-refus-95.json`,
  `variance-refus-95-resume.json`, `analyse-entree-95.json` dans `artifacts/`.
  [Rapport du lot 95](taches/rapport-codex-95-audit-narratif.md).
  Fusionné sur l'intégration après le lot 93 : aucun conflit. Règle de décision de l'orchestrateur appliquée au rejeu répété (cinq fois chaque schéma) : refus aussi fréquents à un près, perte observée = variance de Luna.

- Branche `codex-latence-appels`, fusionnée, lot **93**, base `258daab`
  (code d'intégration `119169c`, lot 91), code `4883425` avec Signed-off-by :
  mesure par appel du premier delta et des jetons, chemin critique dans le fil,
  médiane et ventilation par fonction dans `banc_multi` ; fournisseur OpenAI :
  sous-schémas identiques mutualisés par `$defs`/`$ref`, expansion identique,
  aucun champ, instruction, effort ou contrôle supprimé. Schémas MJ **−30,3 %**,
  narratifs **−41,4 %** ; entrées Luna **3 005 420 → 2 804 658 jetons (−6,68 %)**.
  Deux passes des six scripts, **78 tours par variante** : **246 → 249 appels**,
  **13,794 → 13,249 s/tour (−3,95 %)**, médiane globale **13,045 → 11,915 s**.
  Relances moyennes **4,5 → 4**, refus **10 → 11**, replis **0,5 → 0** ;
  aucune erreur technique, interruption ou défaut de recharge sur 24 parties.
  Douze références jouées une fois ici, rangées et relues du cache, SHA-256 vérifiés.
  Deux exécutions par variante, quatre pendant le chevauchement, priorité réduite ;
  poste partagé, gain non uniforme et causalité précise non démontrée.
  Tests ciblés : équivalence des schémas et console réelle simulée, absence d'Ilse
  et orientation de Gorm, mêmes refus/relances, état et rendu après recharge.
  Suite complète unique verte : **1 947 tests, 16 ignorés**, 202 fichiers,
  **1 349,91 s**, trois processus à priorité réduite.
  **Validation incomplète** : six des neuf audits narratifs refusés restent
  refusés au rejeu exact, dont écoute non exécutée, comptoir inventé et comptes
  inversés ; trois faux refus ou défauts d'extraction disparaissent. L'unique refus
  juste de contre-revue (écoute à la porte, cible vide) est accepté au rejeu,
  malgré un schéma strictement inchangé et non mutualisé. Instabilité sémantique
  non corrigée : critère « aucun refus juste perdu » non satisfait, fusion non validée.
  Deux achats exécutés, or 23 dans le dossier après paiement et `planches_1`
  portée après recharge ; récit « pièces rendues » encore ambigu à une passe,
  comme dans la référence. Aucun changement du planificateur, du modèle ou de `main`.
  [Rapport du lot 93](taches/rapport-codex-93-latence-par-appel.md).
  Fusionné sur l'intégration après les lots 90 et 88 : seul conflit de documentation ; aucun fichier de code commun. Réserve du rapport jugée non bloquante : le refus juste de contre-revue qui disparaît au rejeu porte sur un appel dont l'entrée, les instructions et le schéma sont inchangés par le lot (variance de Luna, pas un effet de la mutualisation) ; les trois refus d'audit disparus étaient faux. Mesure par fonction : l'audit narratif (41 % de l'attente) et l'interprétation (37 %) sont les leviers suivants.

- Branche `codex-recours-prioritaire`, fusionnée, lot **90**, base
  `9810f4a` (lot 87 inclus), code signé SSH `e5c71f9`, `0144f92`, `8a6c1b6` :
  le séjour terminal tarifé par `eclairer(tenir=True)` est exporté comme geste
  durable `abriter` sans lumière portée ; `_plan_lumiere` le revalide et
  `_continuer_progres` retrouve le recours qui porte ce progrès, avec ses replis.
  L'inertie commune entre besoins continue après l'arrivée, jusqu'au seuil
  d'apaisement du geste ; une ronde reste possible avec une lumière portée.
  Aucun délai, registre supplémentaire, coût ou plafond nouveau ; aucune lecture
  du graphe ajoutée à couvrir par `_entrees`.
  Capture réelle crue 2024 à 645 min : **128 → 8 passages d'Aubin / 30 min**,
  même monde complet et même vue description/sons d'un bloc ou par quinze
  secondes sauvegardées/rechargées ; autre cas de mine, reprise de ronde après
  apaisement et lumière portable ordinaire contrôlés. Aubin reste inquiet à 675 :
  aucune inspection sans moyen n'est prétendue dans cet état.
  Le terminal reste soumis à la coupure des gestes supposés/livraisons ; une
  attente vide ne devient un séjour qu'après constat de la lumière. Frontière
  de fin de plan sauvegardée couverte par un cinquième test du lot.
  Lot 88 `9193904` fusionné **localement** par `3665e94` pour les audits.
  Rapide final `735165d`, 4 h × quatre scénarios × quatre graines, contre `9810f4a` :
  seize références relues du cache, mêmes constats d'audit, aucun plantage,
  violation ou usurpation ; pire heure par PNJ inchangée **8 / 10 / 15 / 24**
  (Relais/mine/auberge/crue). En crue, bascules **4 → 5**, répétition brute
  d'avis **0 → 1**, sans alternance durable nouvelle signalée ; la mesure
  inclut le lot 88, sans attribution de ces écarts au seul lot 90.
  Suite complète unique : **1 946 tests, 16 ignorés, 1 286,32 s**, 202 fichiers,
  15 échecs dans cinq fichiers ; erreur de coupure corrigée et quatre attentes
  historiques adaptées (rang, poussée, annonce et conservation du bois à chaque
  geste). **68 tests ciblés finaux verts**, bilan consolidé **1 947 tests,
  16 ignorés, sans échec/erreur restant**, sans seconde suite complète.
  `VERIFIER`, capture 30 min et mine 3 min : **aucun écart ni borne**.
  Audits 12 h : crue 2024 **237 → 24 passages/h**, **292 → 30 glissantes** ;
  crue 500 **22 → 22 / 32 → 32**, chronique et récit identiques, aucun plantage.
  Bascules inchangées **3 / 2**. Plus de rafale ni va-et-vient signalés ; restent
  en 2024 45 min de faim sans recours pour Brune puis attente, et **3 → 6 avis
  textuels redits**, espacés d'au moins 96 min ; causes hors de cette correction,
  aucune garantie générale d'absence d'autres défauts. Le choix garde ses priorités et `INERTIE`, sans nouveau
  comparateur universel de tous les plans entre besoins ; un séjour peut
  durer tant que la sécurité ne s'apaise pas. Aucun appel à Luna ni modification
  de scénario ou de `main`. [Rapport du lot 90](taches/rapport-codex-90-recours-prioritaire.md).
  Fusionné sur l'intégration après les lots 87 et 91, avec le lot 88 (`codex-avis-reels`, avis de menace exprimés dans les nuits réelles, réunis par `3665e94`) : seul conflit de documentation ; `planification.py` touché aussi par le lot 87 (attente bornée), fusionné sans conflit. `test_ressources` (auberge) ne fige plus la vente précise d'Odile à 300 : il contrôle chaque transfert de bois ; vérifié à part, mêmes foyers allumés à 120/200/300/420 min sur la branche et l'intégration.

- Branche `codex-un-appel-de-moins`, fusionnée, lot **91**, base
  `123cc0c` issue d'intégration : l'interprétation d'une parole déclare ses
  opérations dans le même appel, avec les définitions communes de `SENS_CONTENU`.
  Le moteur vérifie localement leur couverture avant revue ; les corrections et
  le repli ne peuvent effacer une opération reconnue. Mots exacts sans opération
  ni contenu typé opérant : aucune revue de fidélité. Reformulation, contenu typé
  et secours local non classé : revue conservée. Déclaration retirée avant la
  transaction sauvegardée, conséquences moteur inchangées.
  Code signé **031a86e**. Suite complète unique : **1 935 tests, 16 ignorés**,
  200 fichiers, trois processus réduits, **1 396,20 s** ; trois échecs et une
  erreur dans trois anciennes simulations/attentes adaptées. Reprise finale
  des douze fichiers modifiés : **128 tests verts, un ignoré, 107,86 s**, deux
  processus réduits ; bilan consolidé sans défaut restant reproduit, aucune
  seconde suite complète. Luna deux passes des sept scripts distincts, contre
  `ef86ff1` joué ici et rangé en cache : **280 → 278 appels / 84 tours MJ**,
  **3,333 → 3,310 appels/tour**, fidélité **50 → 37 appels** ; mais
  **13,76 → 14,43 s/tour**, objectif de temps non atteint. Relances narratives
  moyennes **3,5 → 5,5**, refus **11 → 10**, replis **0 → 0,5** ; aucune erreur,
  arrêt ou défaut de recharge sur 28 parties. Achats du lot exécutés aux deux
  passes : or **26 → 23**, `planches_1` portée après recharge. Quatre scripts
  ciblés seuls : **118 → 109 appels / 28 tours**. Vérifications finales dans le
  [rapport du lot 91](taches/rapport-codex-91-un-appel-de-moins.md).
  La reconnaissance des opérations et la fidélité des contenus typés demeurent
  sémantiques : une omission initiale peut encore échapper au contrôle local.
  Fusionné sur l'intégration après le lot 87 : seul conflit de documentation ; aucun fichier de code commun (lot 87 : `planification`, `esprits`, `banc_pnj`). Fusion décidée sur la baisse des appels de fidélité (F 50 → 37) ; la hausse R/N et le temps par tour viennent surtout de scripts que le lot ne touche pas (relais, crypte), deux passes : à revoir à la vérification Luna groupée.

- Branche `codex-borne-attente`, fusionnée, lot **87**, base **020250e**,
  code signé **a82f469** (première version **a181ada**) :
  un recours borné sans plan retient son effort dans `esprits.attentes_bornees`.
  Lectures communes et admissibilité inchangées, mêmes paliers d'urgence et de
  désespoir : il attend, sans délai et après recharge ; la baisse continue des
  prix ne relance pas seule la recherche. Les recours sans motif explicite
  suivent les paliers de tous les besoins. Aucun certificat d'impossibilité
  nouveau ; autres recours, plans, épuisements et endurance inchangés.
  Quatre nuits mine/auberge × fixe/tiré, 1985, 12 h : **mêmes actions,
  chroniques, récits, résultats de tous les appels logiques et monde final hors
  registre d'attente**, mêmes vues après recharge. Quatre plans après borne
  conservés à **588/622/648/706**, aussi par réinjection de l'attente dans les
  captures rechargées. Auberge fixe : **211 → 68 bornées neuves**, **257 attentes**,
  **1 061 077 → 489 077 nœuds**, **284,16 → 222,80 s CPU** ; tirée **63 → 25**,
  **52 attentes**, **374,94 → 343,12 s**. **Cible ×1,5 manquée : ×1,91 / ×3,63**
  contre `42bb9c0`. Mine fixe **86,11 → 86,42 s**, tirée **146,69 → 147,92 s**,
  mêmes nœuds : 207 attentes remplacent des reprises exactes déjà sans exploration.
  Première simulation de branche rejetée au regroupement (`attente` manquait au
  consommateur) ; mesures préliminaires archivées, cohorte CPU des trois versions
  reprise ensemble après correction du contrat pour mesurer le code final.
  Suite complète unique : **1 933 tests, 16 ignorés, quatre échecs**, 199 fichiers,
  **1 245,40 s**. Contrat corrigé : candidats en lecture seule, efforts enregistrés
  à la sortie du choix, aucun effort pour une requête isolée ou un choix interrompu.
  Deux empreintes historiques normalisent seulement le nouveau registre vide.
  **44 tests ciblés finaux verts** (dont une nouvelle épreuve de frontière) ;
  bilan consolidé **1 934 tests, 16 ignorés**, sans seconde suite complète.
  Vérification finale `VERIFIER` + spatial à 1, auberge 42,
  2 h : **aucun écart ni borne**, **308,14 s CPU**, monde et vues rechargés.
  Banc rapide 4 h, quatre scénarios × quatre graines : **chroniques, récits et
  audits identiques**, aucun plantage, usurpation, violation ou boucle nouvelle ;
  vols, sans recours et attente inchangés. Auberge 2024 : seules les recherches
  neuves baissent **173 → 167**. Référence 020250e rangée une fois en cache.
  Banc rapide final : seize références relues du cache, seize nuits de branche,
  mêmes chroniques, récits et constats ; même baisse de six recherches neuves.
  Signature volontairement large : des faits finalement inutiles réveillent
  encore le but ; un prix seul peut révéler un plan borné et l'attente le retarder
  hors des nuits vérifiées. Aucun appel à Luna, changement de scénario ou modification
  de `main`. [Rapport du lot 87](taches/rapport-codex-87-borne-attente.md).
  Fusionné sur l'intégration après le lot 89 : seul conflit de documentation ; aucun fichier de code commun (lot 89 : `mj`, `couverture_action`, `paroles`).

- Branche `codex-fidelite-audience`, fusionnée, lot **89**, base
  `96c6396` : contrat de revue de parole séparé des gestes ; `perimetre`
  obligatoire (`sens`, `adresse`, `validation_moteur`), seul `sens` peut refuser.
  La couverture des opérations reste obligatoire quel que soit ce périmètre.
  Sens public enrichi des opérations exécutables et du prix offert ; définition
  commune de `reclamer` alignée sur les questions de dû admises par le moteur.
  Relecture des lots 79/82/84 : **40 revues de parole, cinq faux refus**,
  trois d'audience, un de forme d'achat, un de règlement d'une question de dette.
  Quatre tests nouveaux console, état, paroles, paiement, livraison et rendu après
  recharge ; **71 tests ciblés consolidés verts**. Suite complète unique :
  **1 931 tests, 16 ignorés**, 199 fichiers, trois processus à priorité réduite,
  **1 444,24 s** ; huit échecs d'attentes de dossier dans deux anciens fichiers,
  adaptées aux champs ajoutés, et une erreur Windows de remplacement du fichier
  temporaire du test TUI. Reprise finale : **15 tests verts, 56,40 s**, incluant
  les deux fichiers adaptés, le seul test TUI en erreur (inchangé) et les quatre
  nouveaux tests ; bilan consolidé sans défaut restant reproduit, sans seconde suite.
  Luna une passe, quatre scripts, 882907c uniquement en cache : **53 → 57 appels
  sur 14 tours MJ**, **3,79 → 4,07 appels/tour**, relances **4 → 2**, refus **0 → 2**,
  replis du détecteur **0 → 2** ; un tour avec erreur réseau, aucun arrêt ni
  défaut de recharge. Bois à Aubin accepté au premier audit dans les deux scripts ;
  achat interrompu par un délai de 203,4 s avant proposition. Question de dette
  encore bloquée par une mauvaise analyse (`qui`), puis définition partagée
  clarifiée avant la seconde mesure. **Objectif global d'appels non atteint** ;
  périmètre et opérations restent classés sémantiquement, pas de garantie générale
  contre les faux refus ou les écarts mal classés. Aucun changement d'audience,
  de scénario, du modèle ou de `main`.
  **Seconde mesure demandée avant fusion**, sur `8c47cc7` : deux passes des quatre
  scripts, huit références 882907c exclusivement en cache, deux exécutions à
  priorité réduite ; **104 → 125 appels / 28 tours**, **3,71 → 4,46 appels/tour**,
  relances moyennes **3,5 → 3,5**, refus **0 → 1**, replis du harnais **0 → 0**,
  aucun arrêt, erreur technique ou défaut de recharge. Achats exécutés aux deux
  passes, or **26 → 23**, `planches_1` portée après recharge ; question de dette
  correctement typée `reclamer` aux deux passes. Champ interdit de `propos` non
  reproduit ; cinq refus locaux d'identité inconnue dans `echanges` identiques
  aux références. **Régression trouvée et corrigée** : « Ilse, tu m'entends ? »
  bloquée aux deux passes par `qui` extrait à tort, sans être comptée en repli
  par le harnais. Le schéma analyse désormais chaque opération séparément avec
  son booléen obligatoire et sa définition commune ; contrôle structurel avant
  accumulation, conservation des opérations reconnues inchangée. Un nouveau
  test réel/autre question ordinaire, sortie et état après recharge ; **77 tests
  ciblés verts, six fichiers, 53,93 s**, sans seconde suite complète. Reprise
  `noms-dialogue` corrigée, deux passes : **3,50 appels/tour**, aucun refus,
  repli, relance, erreur ou défaut de recharge ; question prononcée au premier
  contrôle et Ilse répond aux deux passes. Lors de cette reprise, les trois
  autres scripts ne sont pas rejoués ; leur mesure reste celle de `8c47cc7`.
  **Comparaison à la base d'intégration**, `96c6396 → c57b1d3`, deux passes des
  quatre scripts sur chaque commit, seize parties jouées et rangées en cache,
  quatre exécutions au plus à priorité réduite ; huit références 882907c relues,
  24 empreintes vérifiées. **122 → 120 appels / 28 tours**, **4,36 → 4,29/tour** ;
  moyennes par passe : refus **4,5 → 0,5**, relances narratives **1 → 2,5**,
  replis **0 → 0,5**, sans erreur technique, arrêt ou défaut de recharge.
  **Aucun appel systématique ajouté par le lot 89** : l'appel de fidélité des
  paroles explicites et des mots exacts sans effet typé vient du **lot 82,
  `3510d00`**. Par fonction, totaux base → final : MJ **60 → 60**, narration
  **25 → 33**, fidélité **37 → 27**, portée **0 → 0**. La base abandonne cinq tours
  MJ, le final aucun ; un repli final restitue l'issue moteur après trois
  récits de compte inverse. Le défaut `qui` était aussi présent sur `96c6396` :
  son attribution antérieure au seul lot 89 n'était pas établie. Pas de code
  modifié ni de nouvelle suite de tests dans ce complément ; aucun gain général
  de latence démontré (secondes observées **16,7 → 17,6/tour**).
  **Limites nouvelles consignées sans correction** : au second achat final,
  la correction omet la part et fait acquérir le lot entier `planches` ; le récit
  dit rembourser trois pièces alors que les comptes indiquent un paiement et
  l'or vaut 23. Fidélité des quantités et audit sémantique toujours incomplets.
  Décomposition par script/fonction et preuve d'attribution dans « Base d'intégration ».
  [Rapport et limites du lot 89](taches/rapport-codex-89-fidelite-audience.md).
- Branche `codex-avis-reels`, fusionnée (avec le lot 90), lot **88**, base **c9245dd**,
  code signé SSH **1dffefd** : le locuteur ne consulte plus la prévision privée
  de l'auditeur pour décider de l'avertir. Une conclusion de menace commune
  ne vaut pas identité des preuves ; la réception conserve sa comparaison des
  sources et convictions. Aucun seuil de souci modifié : il ne bloquait aucune
  paire réelle. Relevés à chaque minute, crues 500/2024 sur 12 h : **3 327 / 44**
  occasions bloquées par le seul ancien `_sait`. Trois tests nouveaux sur captures
  réelles juste avant les paroles à 72/102 min, monde complet, sons et rendu
  identiques après recharge pour dix minutes d'un bloc ou découpées ; **24 tests
  ciblés verts**. Rapide 4 h, crue/Relais × quatre graines : **0 → 18 avis**,
  zéro adoption, aucun plantage/violation/usurpation, mêmes constats d'audit et
  compteurs de boucles ; eau crue **133,75 → 133,75 min·PNJ**. Relais : quatre
  mondes finaux et chroniques identiques. Huit références calculées une fois
  et mises en cache. Audits 12 h branche seule : **16 / 6 avis, zéro adoption**,
  eau **1 095 → 1 085 / 275 → 325 min·PNJ**, `eau_longue` **4 / 1** ; 500 :
  Gorm refuge, Brune galerie, Ilse conduite, Aubin vannes ; 2024 : tous au refuge.
  **Limites** : plan actif non interrompu pour prévenir ; crue 2024 modifiée,
  violence à 649 min puis **237 passages en une heure** et va-et-vient signalés,
  absence de boucle nouvelle non garantie. Suite complète unique : **1 930 tests,
  16 ignorés, zéro échec/erreur**, 199 fichiers, deux processus à priorité réduite,
  **2 231,5 s** ; créneau de 45 minutes dépassé sous charge partagée.
  Aucun appel à Luna, changement de scénario ou de `main`, ni modification de
  `planification.py`/`deliberation.py`. [Rapport du lot 88](taches/rapport-codex-88-avis-reels.md).
  **Suite du lot 88, diagnostic seul après refus de fusion : non fusionnable.**
  Les 237 passages sont ceux d'Aubin, heure 660–719 ; **292** sur 60 min glissantes.
  Alternance principale **lumière galerie ↔ inspection refuge**, relayée au palier
  noir par une sécurité toujours urgente ; persiste après extinction du danger.
  `eclairer` termine sur l'arrivée éclairée, sans progression de sécurité ;
  `_plan_lumiere` s'efface, `_plan_abri` n'y prend pas le relais, puis `_candidats`
  et `_pulsion` relancent la ronde dont le parcours sera interrompu. Inertie entre
  recours d'un même besoin seulement. Base normale : aucun coup à 649 min,
  pire heure 24 ; mêmes captures à 645 min sur les deux moteurs : **128 passages
  d'Aubin / 30 min**, monde complet et rendu identiques en bloc/découpé/rechargé,
  **249 événements** identiques à la vraie nuit. Défaut latent du contrat commun
  choix/prérequis/progression, pas une boucle causée par les seules violences.
  Arrêt au diagnostic autorisé au point 3 ; aucun code modifié, aucune suite
  complète supplémentaire. Audits 12 h refaits, chroniques identiques :
  2024 **237 passages/h, 6 avis/0 adoption** ; 500 **22 passages/h, 16/0**.
  [Diagnostic, fonctions et preuves](taches/rapport-codex-88-boucle.md).

- Branche `codex-gestes-par-noeud`, fusionnée, lot **86**, base
  **02c8e8b**, code signé **9f344cd** : lieux et portée partagés par salle,
  possessions, agissables et faits `lieu`/`ouvert`/`assomme` ; droits et fautes
  par `permis`/`achete`/`acquis`/`faute`. Préconditions fixes des parts et
  compatibilités de combustible préparées une fois par `Vue`. Chaque geste
  compose encore ses effets sur son propre nœud ; aucune lecture de lumière
  déplacée, aucune modification des coûts, ordres, plafonds ou décisions.
  Joss/faim, vingt recherches : à 480 min, **149 nœuds**, **335,6 → 288,4 µs
  CPU/nœud (−14,1 %)** ; à 600 min, **2 065 nœuds**, **554,3 → 425,6 µs
  (−23,2 %)**. Trois tests nouveaux, **2 138 états / 14 661 successeurs**
  ordonnés contre la base, coûts hexadécimaux ; clés contre lectures directes,
  monde, lignes joueur et rendu mine/auberge identiques après recharge.
  **21 tests ciblés verts**. Douze heures, mine/auberge × fixe/tiré, 1985,
  trois versions ensemble : **quatre nuits strictement identiques** à la base,
  traces et nœuds compris. Gains CPU **4,35 à 9,97 %** ; auberge encore
  **×2,44 / ×3,75** contre `42bb9c0`. Empreintes 2 h, quatre scénarios × quatre
  graines : **16 nuits identiques**, référence calculée une fois et mise en cache.
  `VERIFIER` + spatial à 1, auberge 42, 2 h : **sans écart ni borne**, 427,77 s CPU.
  Suite complète unique : **1 916 tests, 16 ignorés, zéro échec/erreur**,
  196 fichiers, trois processus à priorité réduite, **1 365,9 s écoulées**.
  Créneau de 45 min dépassé ; aucun appel à Luna ni modification de `main`.
  [Rapport du lot 86](taches/rapport-codex-86-gestes-par-noeud.md).
  Fusionné sur l'intégration après les lots 83 et 84 : seul conflit de documentation ; aucun fichier de code commun.

- Branche `codex-part-proposee`, fusionnée, lot **84**, base d'intégration
  **7cce974**, brief **3dbd225** : une part demandée dans une proposition conserve
  sa valeur propre et la garde de la réserve. Classification commune de la remise
  et du travail ; évaluation, exécution et contre-offre vérifient la livraison
  sur copie par le chemin des demandes/ventes, sur la pièce détachée au lieu du
  lot entier. Les propres biens à portée sont constatés avant l'accord. Le service
  explicite `servir` reste une tâche avec devis et engagement. Quatre tests nouveaux
  console/MJ simulé, paiement, réserve, autre ressource, soupe et livraison depuis
  une autre salle, état et inventaire après recharge. Suite complète unique verte :
  **1 912 tests, 16 ignorés**, trois processus à priorité réduite, **1 763,95 s** ;
  code final repris sur six fichiers : **39 tests, un ignoré**, **64,47 s**, verts.
  Banc rapide Relais **4 h × 4 graines**, contre 7cce974 : aucun plantage, violation
  ni usurpation, mêmes constats d'audit ; autres scénarios non mesurés dans ce lot.
  Luna une passe soir-appel/ressources, référence **882907c** relue du cache (7cce974
  absente) : **28 → 39 appels / 7 tours MJ**, relances **2 → 4**, refus **0 → 2**,
  aucun arrêt, repli ou défaut technique/recharge. **Achat exécuté** : or **26 → 23**,
  puis `planches_1` remise au déplacement suivant et portée après recharge.
  Faux refus de fidélité et relances narratives conservés ; aucune garantie générale
  nouvelle sur les audits sémantiques. `main`, `narration.py`, `mj.py`, planificateur,
  scénarios et modèle inchangés. [Rapport du lot 84](taches/rapport-codex-84-part-proposee.md).
  Fusionné sur l'intégration après le lot 81 ; aucun fichier de code commun avec lui.

- Branche `codex-verdict-coherent`, fusionnée, lot **83**, brief
  `13ae231`, intégration du lot 82 `7cce974` reprise par fusion signée `b1dbf65`.
  Correctifs signés `b2be935`, `be8e175`.
  `narration.controler` rend illisible un désaccord entre verdict mécanique
  favorable et portée négative, ou verdict négatif et portée établie ; audit
  redemandé une fois, garde refait par `consigner`. Les références des comptes
  extraits passent par la résolution exacte commune, uniquement dans le dossier
  public conservé : noms, identifiants, alias, personnes connues, souvenirs visuels,
  nom du joueur et termes imbriqués
  des offres. Ambiguïté : audit illisible ; aucune identité privée devinée.
  Sept tests nouveaux de console/recharge, remboursements Gorm/Corvus et
  Aubin/Corvus, rendus et état vérifiés. Suite complète unique : **1 914 tests,
  16 ignorés, une erreur**, 195 fichiers, trois processus à priorité réduite,
  **1 755,2 s**. `test_scenarios_libres.test_empreinte_crypte_visible_apres_rechargement` :
  saisies simulées épuisées en mode hors ligne (`StopIteration`), hors du nouvel
  audit ; cause non établie, aucune correction de contournement. Reprise finale :
  **63 tests verts**, six fichiers, **82,75 s**, dont ce fichier inchangé et les
  sept tests finaux. Six tests du lot dans la suite, sept après les compléments
  de références hors de vue : **1 915 tests consolidés, 16 ignorés, aucun défaut
  restant reproduit** ; aucune seconde suite complète.
  Luna une passe signes-noir/crypte/comptes, référence `882907c` exclusivement
  relue du cache : 31 → 38 appels sur 12 tours MJ, 2,58 → 3,17 appels/tour,
  une relance narrative dans chaque variante, aucun arrêt, erreur/recharge ou
  repli du harnais. Remboursement de Gorm affiché sans relance, or 24 → 26 ;
  Brune conserve sa dette. N4 historique exact admis après résolution des noms.
  **N2/N3 non clos** : leurs rapports exacts restent admis, car seul le motif
  libre contredit leurs champs typés favorables. Non-reproduits dans cette
  passe, sans garantie générale nouvelle. Demande de prime en crypte non
  exécutée après des refus de fidélité, hors lot. Aucun prompt, modèle,
  scénario, planification ni `main` modifiés. [Rapport et limites du lot 83](taches/rapport-codex-83-verdict-coherent.md).
  Fusionné sur l'intégration après le lot 81 ; aucun fichier de code commun avec lui.

- Branche `codex-cout-par-noeud`, fusionnée, lot **81**, base **cf08508**,
  brief **f7a558a**, correctif signé **0270367** : géométrie et tarifs partagés
  par les nœuds d'une `Vue` et les références de `VERIFIER`. Clés de route par
  salle, allure, clés/équipement métrique et faits de portes ; pression fixe
  par salle quand ni lumière ni compagnie ne la changent, sinon possessions,
  lieux et lumières dans la clé. Durées sommées une fois, admission et causes
  gardées, effets de portes composés avec l'état suivant original. Aucun coût,
  ordre d'addition, modèle de trajet, nœud ou choix changé. Témoin spatial du
  dernier état complet, indépendant des clés projetées, partagé entre ses
  destinations ; une clé omise et une corruption restent détectées.
  Capture Joss/faim, vingt recherches : **149 nœuds chacune**, même coût et
  résultat, **367,0 → 262,2 µs CPU/nœud (−28,6 %)** ; ancien moteur : 73 nœuds,
  149,8 µs/nœud, autre modèle. Douze heures, mine/auberge × fixe/tiré, 1985,
  trois versions ensemble, un processus chacune : **quatre nuits strictement
  identiques** à la base, traces et nœuds compris. Gain CPU observé **2,10 à
  8,93 %** ; **cible sous ×2 non atteinte**, auberge fixe ×2,66, tiré ×4,46.
  Cinq tests nouveaux : tarifs directs, portes, eau attendue, obstacle, lumière,
  allures et captures réelles mine/auberge vécues puis rechargées, même monde,
  texte joueur et rendu. Empreintes 2 h, quatre scénarios × quatre graines :
  **16 nuits identiques**, référence calculée une fois et mise en cache.
  `VERIFIER` + spatial à 1, auberge 42 tiré, 2 h : **sans écart ni borne**,
  413,98 s CPU. Suite complète unique : **1 908 tests, 16 ignorés, zéro échec/erreur**,
  194 fichiers, trois processus à priorité réduite, **1 829,4 s écoulées**.
  Premier contrôle spatial interrompu pour supprimer ses
  recalculs par destination ; seul ce contrôle est ajusté après les mesures CPU.
  Créneau de 45 minutes dépassé ; aucun appel à Luna, aucune modification de
  `main`. [Mesures et limites du lot 81](taches/rapport-codex-81-cout-par-noeud.md).
  Fusionné sur l'intégration après les lots 79, 80 et 82 : `planification.py` touché aussi par le lot 80 (lecture de la prévision d'eau), fusionné sans conflit ; suite complète relancée.

- Branche `codex-paiement-effectif`, fusionnée, lot **82**, base `a6f9368`
  (brief sur l'intégration `3ffd72d`) : analyse des opérations demandées séparée du
  verdict de fidélité, avec les sens communs de `paroles`. Le moteur compare cette
  analyse aux opérations du contenu ; `propos` ne couvre pas un échange, même avec
  un verdict favorable. Les offres historiques utilisent le montant exécutable
  de `offre`. Contrôle aussi sur adresse explicite, mots exacts et repli littéral ;
  les opérations reconnues restent exigées pendant les corrections de la saisie.
  Une revue illisible ne valide plus une parole. Cinq nouveaux tests console/MJ
  simulé, monde, texte et inventaire après recharge. Suite complète unique :
  **1 908 tests, 16 ignorés**, 194 fichiers, trois processus à priorité réduite,
  **1 683,2 s** ; trois échecs et quatre erreurs d'anciennes attentes et d'une nouvelle
  scène simulée. Ces scènes corrigées et le code final repris sur huit fichiers :
  **102 tests verts**, deux processus, **98,0 s**. Bilan consolidé vert, sans seconde suite.
  Luna une passe soir-appel/ressources/noms-dialogue, référence **882907c** en cache :
  **44 → 44 appels / 11 tours MJ**, relances **4 → 0**, refus **0 → 2**, aucun arrêt
  ou erreur technique/recharge. **Validation partielle : achat effectivement typé
  et arbitré, mais non exécuté.** Deux faux rejets de la question sur le bois
  confondent contenu et audience ; le repli sans opération reste bloqué, Aubin ne
  constate pas sa réserve, puis refuse le marché. Même question bloquée dans
  noms-dialogue ; demande nominative exécutée dans ressources. L'omission initiale
  d'une opération et la comparaison des biens/montants restent sémantiques ; pas
  de garantie générale ni de seconde passe. `main`, `planification.py`, scénarios,
  modèle et prompts d'interprétation/narration inchangés ; protocole de revue étendu.
  [Rapport du lot 82](taches/rapport-codex-82-paiement-effectif.md) ; bruts dans
  `artifacts/` du worktree de livraison.

- **Vérification Luna de l'intégration 882907c**, lot **79**, branche
  `codex-verif-luna-882907c`, sans changement de code : deux passes des vingt scripts
  du lot 70, **40 parties, 302 saisies, 388 appels**, uniquement `gpt-6-luna`/ChatGPT,
  medium/libre, quatre exécutions au plus à priorité réduite, copies temporaires.
  Aucun arrêt, erreur technique/recharge, tour écarté ou repli détecté. Quarante parties
  rangées en cache, SHA-256 identiques aux bruts ; **42bb9c0, f033364 et fbcf0ff
  exclusivement relus**, 102 références inchangées et mesures historiques reproduites.
  Onze scripts, main → f033364 → fbcf0ff → 882907c : **3,15 → 2,96 → 3,21 → 2,91
  appels/tour**, **12,7 → 11,1 → 14,4 → 12,8 s/tour** ; relances **8 → 2,5 → 9 → 5**,
  refus **16 → 10,5 → 13,5 → 7,5**, tours avec refus **10,5 → 8,5 → 9,5 → 6,5**,
  replis **0,5 → 0 → 1 → 0**. Vingt : f033364 → fbcf0ff → 882907c **2,80 → 3,06 → 2,85
  appels/tour**, 66 → 68 → 68 tours MJ. Temps historiques sous des charges différentes,
  sans conclusion causale de performance. **Validation partielle** : Aubin et Gorm
  remboursent, Brune reste débitrice ; brasero hors de vue admis, faux rejet spatial
  et présentation d'Ilse rejetée non reproduits. Mot « refus » non exercé lexicalement.
  Achat du soir exécuté **une passe sur deux** : paiement 26 → 23 puis `planches_1`
  portée après recharge ; autre passe réduite à `propos`, couverture déclarée conforme,
  aucun paiement ni remise. Faux rejet de compte sur propriété des planches persistant.
  Nouveaux défauts : absence d'Ilse affirmée dans le noir malgré sa présence rechargée,
  Gorm dit « face à toi » malgré son orientation, motifs d'audit contradictoires avec
  leurs verdicts ; compte de Gorm extrait avec noms publics au lieu des identifiants.
  Quatorze passages/refus sous-obstacle cohérents après recharge. Aucun correctif ni
  suite moteur supplémentaire ; panneaux non capturés par le harnais, aucune garantie
  générale nouvelle du rendu ou de l'absence de contradictions. Bruts et preuves dans
  `artifacts/verif-luna-882907c/` du dépôt principal ;
  [rapport du lot 79](taches/rapport-codex-79-verif-luna.md). Branche livrée sans fusion dans `main`.
  Fusionné sur l'intégration (rapport seulement).

- Branche `codex-bissection-auberge`, fusionnée, lot **76**, moteur **1171fc3**,
  brief **bf4bf71** : diagnostic seul, **22 révisions**, **32 nuits de 12 h**,
  auberge 1985 fixe, joueur au dortoir. Quatre marches retenues : trajets réels Q
  (`1f21384`, 144,44 → 624,03 s CPU dans le sondage, presque autant de nœuds),
  calibration des signes (`3792eb7`, **+51,3 %** au contrôle), propositions faute
  de mieux (45, `3aba83b`, **+51,5 %**) et constats partagés (55, `c592d68`,
  **+66,8 %**, 760 632 → 1 712 879 nœuds). Ces trois derniers changent la nuit,
  les recherches neuves et les échecs bornés ; Tilo/faim domine la hausse du lot 55.
  Dix contre-mesures, deux cœurs distincts de même classe (`--affinite 0x11`),
  deux nuits au plus : le **faux saut du lot 61** tombe de +40,6 % apparent à
  **+0,55 %** à monde/trace/nœuds identiques ; lot 60 **+4,7 %**, sous le seuil.
  Les CPU ne se comparent que dans un couple. Bornes de la série libre :
  `42bb9c0` → `1171fc3`, **144,44 → 511,14 s**, ×3,54 ; référence 12 h calculée
  une fois. Toutes les nuits contrôlent monde, `regarder` et `scene_percue` après
  recharge ; chaque contre-mesure retrouve aussi l'état, le rendu et les compteurs
  de son sondage. Harnais vérifié sur auberge ancienne et mine actuelle.
  Suite complète unique : **1 874 tests, 16 ignorés, zéro échec/erreur**,
  188 fichiers, un processus, 3 836,85 s. Aucun changement du moteur, de `main`
  ou du modèle ; aucun appel à Luna, aucun gain revendiqué. Contrats proposés :
  génération/tarification par état fixé, puis absence certifiée distincte d'un
  échec borné, avec dépendances complètes du graphe et des prix. Une seule
  graine/départ ; une hausse compensée entre points non testés reste possible.
  Format de 45 minutes dépassé (nuits et contrôle du faux saut CPU).
  [Rapport du lot 76](taches/rapport-codex-76-bissection-auberge.md) ; bruts dans
  `artifacts/bissection-auberge/` du worktree de livraison.
  Fusionné sur l'intégration (rapport et outil, sans moteur).

- Branche `codex-avis-menace`, fusionnée, lot **80** (A3, menace d'un lieu),
  base d'intégration **882907c**, brief **5fd85a1**, code signé **a2bb274** : les nouvelles communes
  transmettent la prévision d'eau à un auditeur cru concerné, selon le souci
  (altruisme + empathie + affection ≥ 100). La réception pèse source × conviction ;
  une estimation propre étayée plus récente dément durablement l'avis. Croyance `prevision`
  séparée des mesures du lot 58, lue par `eau.attendue` ; raccord des routes et
  coefficients dans `_entrees`. Algorithmes de recherche et règles de choix des buts inchangés.
  Le registre du lot 64 suit la valeur « menace » et les destinataires, hors dates
  et conviction. Une destination n'est connue que par rendez-vous convenu ; aucun
  accès au plan privé d'autrui. Huit tests nouveaux, dont la crue 500, un autre
  lieu/locuteur, le doute, le souci, la non-répétition et la reprise découpée.
  Suite complète unique : **1 903 tests, 16 ignorés**, 193 fichiers, trois processus
  à priorité réduite, **1 477,7 s** ; seul échec de la nouvelle scène d'écoute sans mode
  spatial. Scène corrigée puis code final repris : **18 tests verts**, dont les dix
  tests inchangés des lots 41/58 ; bilan consolidé vert, sans seconde suite complète.
  Empreintes sans avis 2 h, crue/Relais × quatre graines : identiques à la base.
  Rapide 4 h, mêmes scénarios/graines : états et chroniques identiques, zéro avis/adoption,
  aucune usurpation ou plantage ; eau crue **133,75 → 133,75 min·PNJ**, `eau_longue` **1 → 1**.
  Audits 12 h branche seule, crue 500/2024 : **1 095/275 min·PNJ** dans l'eau,
  **4/1** constats `eau_longue`, aucun plantage/usurpation, zéro avis/adoption.
  À 12 h, 500 : Gorm au refuge, Brune à la galerie, Ilse dans la conduite, Aubin aux
  vannes ; 2024 : tous au refuge. Sept constats d'eau différents d'Ilse expliquent
  l'alerte de répétition. L'émission est prouvée par les parcours ciblés, pas ces nuits.
  Contrôle 2 h crue 42, `VERIFIER` + `spatial.VERIFICATION=1` : aucun écart, borne
  atteinte ou plantage, **586,7 s**. Créneau du lot dépassé ; chiffres et limites dans le rapport.
  Aucun appel à Luna, changement de scénario ou modification de `main`.
  [Rapport du lot 80](taches/rapport-codex-80-avis-menace.md).

- Branche `codex-piece-de-lot`, fusionnée, lot **78**, base **6a49036**,
  intégration de départ **38e5d7e** ; correctif signé **69f04db**. Le sens du contenu
  porte référence, noms connus, quantité et unité (`part`/`objet`), pour les demandes
  simples et les termes de marché. Nom, alias et `nom_piece` déclaré sont partagés
  entre saisie, résolution, lexique et repères de désignation ; aucun singulier deviné.
  Quatre tests nouveaux console/MJ simulé, transaction, remise et rendu après recharge ;
  parcours fonctionnels et complément ciblé verts. Suite complète unique : **1 887 tests,
  16 ignorés, aucun échec ni erreur**, 191 fichiers, trois processus à priorité réduite,
  **1 576,9 s**. Quatrième test ajouté après chargement du fichier par la suite,
  repris isolément vert ; **bilan consolidé 1 888 tests, 16 ignorés**, sans seconde suite.
  Luna une passe soir-appel/ressources/noms-dialogue, référence **fbcf0ff** en cache :
  **42 → 40 appels / 11 tours MJ**, **3 → 2 relances**, **1 → 0 repli**, aucun arrêt
  ou erreur de recharge. Achat réel déclaré conforme et exécuté, puis `planches_1`
  remise et portée après recharge. Fidélité encore sémantique ; formulation finale
  évoquant une dette antérieure non attestée, limite de portée/extraction consignée.
  `main`, scénarios, modèle, instructions de Luna, échanges et délibération inchangés.
  [Rapport du lot 78](taches/rapport-codex-78-piece-de-lot.md).
  Fusionné sur l'intégration après les lots 73 et 74 ; fichiers de code distincts de l'autre lot du jour ; suite complète relancée.

- Branche `codex-contre-offre`, fusionnée, lot **77**, base d'intégration
  **38e5d7e**, brief **c1cb020** : un refus PNJ peut annoncer le prix propre où sa
  réticence cesse, ou le repas servi qui libérerait réellement le bien nécessaire
  à son plan. Offre commune et preuve du service conservées avec le refus avant
  affichage ; ni méfiance, ni garde durable ne donnent de condition inventée.
  Recours « faute de mieux », hors recherche : payer ou planifier le service puis
  redemander, sans second jet ; moyens ordinaires sans faute prioritaires,
  condition impossible retenue sans offre au hasard. `planification.py` inchangé.
  Sept tests nouveaux, état/rendu après recharge, autre bien et même laps découpé
  pour paiement et service ; cinq fichiers d'anciennes scènes adaptés à la condition dite.
  Banc **4 h × quatre scénarios × quatre graines**, trois processus à priorité
  réduite : **17 contre-offres, 12 conditions remplies**, demandes accordées
  **21 → 32**, vols tentés **12 → 11** (mine **1 → 2**), aucun plantage,
  violation ou usurpation. Aucun nouveau code d'audit ; quelques avertissements
  redits et un appel à l'aide supplémentaires, pas de cycle de contre-offre.
  Réserve : auberge 2024 **26,89 → 100,95 s CPU**, noir **160 → 170 min·PNJ** ;
  moyenne auberge **24,05 → 41,48 s**. Suite complète unique : **1 891 tests,
  16 ignorés, 1 479,1 s**, trois processus à priorité réduite. Sept échecs et une
  erreur d'anciennes attentes dans cinq fichiers ; ces cinq fichiers repris verts
  (**72 tests**, dernier fichier **25/25** après correction d'attente de prix),
  bilan consolidé vert, sans seconde suite complète. Vérification au-delà du
  créneau initial ; aucun code moteur changé pendant les reprises.
  Limites : satisfaction corporelle exprimable aujourd'hui par le repas servi
  seulement ; contrôles matériels de remise maintenus ; contenu joueur à venir.
  Aucun appel à Luna, ni modification de `main`.
  [Rapport du lot 77](taches/rapport-codex-77-contre-offre.md).

- Branche `codex-gardes-justes`, fusionnée, lot **74**, brief
  **0a1eda2**, intégration **fe85a44** reprise au départ ; correctifs signés
  **2549160**, **c65d421**. À la demande de l'utilisateur, lot 73 **29c9ae4** intégré
  par fusion signée **c84dcf9** ; seul conflit dans `consigner`, deux validations
  conservées. « Refus » n'est plus interdit comme nom commun ; vocabulaire technique
  existant conservé. Les locatifs ne sont refusés que sur attribution directe à une
  cible publique univoque et repère incompatible ; aucune cible héritée entre
  propositions/segments, direction admise acceptée malgré une négation distincte.
  Effet lumineux perçu séparé de la vue de sa source, extraction typée `eclairages`,
  comparaison aux contributions positives et nouveau contrôle avant enregistrement.
  Sept tests nouveaux console/MJ simulé, état et lecture après recharge ; **66 tests
  ciblés verts**, puis seconde source revalidée ; **20 tests des deux lots verts après
  fusion**. Première suite 74 interrompue sans bilan après la demande d'attendre le
  lot 73. Suite complète finale sur branche réunie : **1 875 tests, 16 ignorés**,
  188 fichiers, **1 809,8 s**, trois processus à priorité réduite ; une `PermissionError`
  sur le verrou temporaire de `test_connexion` (deux fichiers inchangés depuis la base).
  Reprise du fichier : **21 tests verts**, 1,7 s ; incident non reproduit, non corrigé
  dans ce lot, aucune seconde suite complète. Attente et validation réunie prolongent
  le créneau initial.
  Luna une passe avant fusion, crypte/comptes/relais/luna-restes-ambiance, référence
  **fbcf0ff** exclusivement relue du cache : **55 → 60 appels / 22 tours MJ**,
  **1 → 4 relances**, aucun arrêt, erreur technique/recharge ou repli historique.
  Brasero admis, aucun faux rejet spatial déterministe, refus de Brune restitué ;
  faux audit d'approche des crochets persistant. Resserrements finaux validés ensuite
  par tests, sans seconde passe Luna. Extraction lumineuse et contradictions encore
  sémantiques, méta-langage implicite non clos ; aucune garantie générale d'absence
  de faux refus. `main`, modèle, scénarios et planification inchangés par ce lot.
  [Rapport du lot 74](taches/rapport-codex-74-gardes-justes.md).
  Fusionné sur l'intégration après le lot 73 (déjà réuni dans la branche) : seul conflit de documentation.

- Branche `codex-comptes-issue`, fusionnée, lot **73**, brief **6a18952**,
  mise à jour initiale sur l'intégration **fe85a44** : paiements et remises alimentent
  les comptes depuis leurs opérations, dans la copie transactionnelle de la parole ;
  journal retiré avant sauvegarde, essais abandonnés sans effet publié. Les biens à
  livrer sont lus dans les engagements et reviennent dans les comptes publics et leur
  rendu après recharge. Le contrôle exige la restitution des comptes rendus ou dus
  de l'issue, même pour une réplique à portée aucune ; inversion toujours refusée,
  garde refait à l'enregistrement. Trois tests nouveaux sur cinq parcours, **19 tests
  ciblés verts**. Suite complète unique : **1 868 tests, 16 ignorés**, 187 fichiers,
  **2 152,2 s**, trois processus à priorité réduite ; un échec et trois erreurs dans
  deux anciens récits simulés, complétés et repris verts sur leurs quatre parcours.
  Bilan consolidé sans défaut restant connu, sans seconde suite complète. Correctif
  signé **e219008**.
  Luna une passe soir-appel/ressources/comptes, référence **fbcf0ff** lue du cache :
  **36 → 30 appels**, neuf tours MJ, **4,00 → 3,33 appels/tour**, trois → zéro
  relance, un → zéro repli, aucune erreur technique/recharge. Remboursements d'Aubin
  et de Gorm racontés ; Brune garde les pièces. **Limite : l'achat du soir n'est pas
  exécuté**, contre-revue du contenu puis précision demandée ; achat payé validé
  avec MJ simulé sur planches et fagots. Extraction/portée encore sémantiques,
  aucune garantie de toute paraphrase. Ni `main`, ni `planification.py`/`obstacles.py`,
  ni modèle ou prompt du MJ modifiés. [Rapport du lot 73](taches/rapport-codex-73-comptes-issue.md).
  Fusionné sur l'intégration après les lots 71 et 72 : seul conflit de documentation ; aucun fichier de code commun.

- Branche `codex-etapes-chainees`, fusionnée, lot **72**, base **fbcf0ff**,
  brief **f5fec82** : `_explorer_etats` chaîne les ajouts sans copier les préfixes.
  Le seul chemin retenu est reconstruit et gelé ; `_MEMOIRE` le garde directement,
  `chercher` rend une liste publique indépendante jusque dans ses contenus imbriqués.
  Coûts, rangs, états et décisions inchangés ; `_couper` garde ses frontières.
  Captures mine/auberge : mêmes plans, retraits du tas, diagnostics, monde complet
  et rendu après recharge. 28 tests existants ciblés et trois nouveaux verts.
  Empreintes 2 h × quatre scénarios × quatre graines contre la base : identiques.
  `VERIFIER` + `spatial.VERIFICATION=1`, mine 42, 2 h : aucun écart ni borne.
  Profil 480–505 : signes sous 1 % du temps cumulé de `percevoir_tous`, laissés
  inchangés ; les allocations de chemin supprimées pèsent peu dans ce coût.
  Banc simultané 12 h, mine/auberge 1985, tiré/fixe, un calcul par version :
  états, récits, chaque plan et nœuds identiques à la base (4,06 millions de nœuds).
  CPU total 1 604,58 → 1 595,12 s (−0,59 %, une passe), pics mémoire voisins ;
  `42bb9c0` 699,72 s. La cible générale ×1,3 reste non atteinte (×2,28 agrégé,
  décisions différentes sur l'ancien main). Suite complète unique : **1 861 tests,
  16 ignorés, aucun échec ni erreur**, 186 fichiers, 1 144,39 s,
  trois processus à priorité réduite.
  Aucun appel à Luna ni changement de `main` ;
  [rapport du lot 72](taches/rapport-codex-72-etapes-chainees.md).
  Fusionné sur l'intégration après les lots 69 et 70 ; `planification.py` fusionné sans conflit avec les lots 71/72 voisins ; suite complète relancée.

- Branche `codex-cout-fixe`, fusionnée, lot **71**, base **fbcf0ff**,
  brief **5ea04cf** : préparation paresseuse de `Vue` et relevé commun des entrées
  partagés dans la seule sélection en lecture seule de `choisir`. Chaque recherche
  garde ses paramètres, découvertes et dictionnaires ; aucune vue ne survit au
  choix. Violence et défense restent dans les entrées propres au candidat.
  Les trois clés géométriques d'`obstacles` utilisent le texte immuable d'une
  carte comparée à une copie témoin ; éditions en place et ordre des salles/sorties
  pris en compte. Mêmes lectures, tarifs, recherches et plafonds. Code signé **63ae2b3**.
  Douze heures, mine/auberge × départ tiré/fixe, graine 1985 : quatre nuits
  strictement identiques à la base, résultats et nœuds compris ; trois versions
  mesurées ensemble, un processus chacune. Gain CPU **1,91 à 2,53 %**,
  surcoût des longues nuits toujours ouvert. Six tests nouveaux ; empreintes 2 h,
  quatre scénarios × quatre graines : identiques à la base (référence en cache).
  `VERIFIER` et spatial à 1, auberge 42 tiré, 2 h : sans écart ni entrée dans `BORNES`.
  Suite complète unique, trois processus à priorité réduite : **1 864 tests,
  16 ignorés, aucun échec ni erreur**, 186 fichiers, **1 260,4 s écoulées**. Mesures et
  limites : [rapport du lot 71](taches/rapport-codex-71-cout-fixe.md).
  Fusionné sur l'intégration après les lots 69 et 70 ; `planification.py` fusionné sans conflit avec les lots 71/72 voisins ; suite complète relancée.

- **Vérification Luna de l'intégration fbcf0ff**, lot **70**, branche
  `codex-verif-luna-fbcf0ff`, sans modification de code : deux passes des onze scripts
  historiques, de `ressources`, de `comptes` avec noms préparés et des sept
  `sous-obstacle-*`. **40 parties, 302 saisies, 416 appels**, uniquement `gpt-6-luna`
  via ChatGPT ; aucun arrêt ni erreur technique/recharge. Copies temporaires,
  quatre exécutions au plus, priorité réduite. Les quarante parties sont rangées
  dans le cache de **fbcf0ff**, identiques aux bruts par SHA-256 ; **main 42bb9c0
  et f033364 uniquement relus du cache**, jamais rejoués.
  Onze scripts, main → f033364 → fbcf0ff : **3,15 → 2,96 → 3,21 appels/tour**,
  **12,7 → 11,1 → 14,4 s/tour**, relances **8 → 2,5 → 9**, refus
  **16 → 10,5 → 13,5**, tours avec refus **10,5 → 8,5 → 9,5**, replis **0,5 → 0 → 1**.
  Temps historiques sous des charges différentes, sans conclusion causale.
  Vingt scripts : f033364 → fbcf0ff **2,80 → 3,06 appels/tour**, 66 → 68 tours MJ ;
  `comptes` passe de zéro à deux tours, préparation différente.
  Prime de vingt pièces, questions sans faux « Précise… », poutre derrière après
  rotation, impressions d'`observer` et attendu public tiennent aux deux passes.
  `comptes` rembourse Gorm et maintient Brune débitrice dans le bon sens, or 24 → 26.
  **Validation des comptes partielle** : `soir-appel` passe 1 n° 4 affiche le démenti
  d'Aubin sans narrer le remboursement effectué ; passe 2 n° 4 rejette des récits
  exacts et finit en repli. Autre repli sur le marché payé (passe 1 n° 5), faute
  de comptes structurés correspondant à l'issue. Nouveaux constats : cible couteau
  substituée au pied-de-biche, faux refus de directions pourtant conformes, lumière
  d'un brasero hors de vue pourtant perçue, mot ordinaire « refus » censuré,
  présentation d'une voix inconnue rejetée. Méta-langage seulement partiellement résolu.
  Relecture saisie par saisie et limites dans le
  [rapport du lot 70](taches/rapport-codex-70-verif-luna.md) ; bruts dans
  `artifacts/verif-luna-fbcf0ff/` du dépôt principal. Aucun correctif ni intervention
  sur `main` ; le harnais ne capture pas le rendu des panneaux après recharge,
  seulement l'état résumé et les marqueurs d'affichage : aucune garantie générale nouvelle.
  Fusionné sur l'intégration après le lot 69 (rapport seulement).

- Branche `codex-appels-restes`, fusionnée, lot **69**, base `be90377`
  (intégration **4acc36c**, déjà à jour au départ) : les indices d'une recherche gardent
  leur contenu hors des quarante souvenirs (`esprit.indices_recherche`), par personne et
  lieu. Voix réentendue, bruit réexpliqué, date, confiance et relais ne réarment plus une
  recherche sans information supplémentaire. Un examen consomme son point de départ avant
  de réviser la croyance ; le silence consomme son lieu ; réponse saisie ou réapparition vue
  permettent un nouveau contact local. Captures originales de `5c2ce81`, mine 7 à 470 et
  auberge 7 à 625 : état complet et rendu après recharge, temps groupé ou découpé ; Gorm et
  le joueur servent d'autres cas. Dernière présence positive conservée malgré une absence :
  un vrai retour appris reste nouveau sans effacer les anciens sons. Sept tests nouveaux.
  La rafale d'Odile contient huit premiers lieux puis deux indices nouveaux, pas dix reprises
  sans information ; aucune promesse de supprimer ces appels légitimes. Rapide 4 h × quatre scénarios × quatre
  graines contre `4acc36c` : chroniques et mesures de jeu identiques, aucun plantage,
  violation ou usurpation ; référence calculée une fois et rangée dans le cache.
  Suite complète unique : **1 855 tests, 16 ignorés**, verte, 2 280,9 s à deux processus.
  Deux cas ajoutés ensuite ; sept tests finaux et reprise des 28 tests existants verts :
  **bilan consolidé 1 857 tests, 16 ignorés**, sans seconde suite complète.
  Rapide final sur `1d763cc` : seize références relues du cache, mêmes chroniques et
  mesures de jeu. Audits 12 h, mine 7/1985 et auberge 7/2024 : **9/2/7/14 appels**,
  pics par même cible sur quinze minutes **3/1/1/4**, donc aucune rafale ≥ 5 ; maximum
  de passages/PNJ/h **14/16/20/38**, aucun plantage ni usurpation. Les différences contre
  l'audit ancien `5c2ce81` incluent les autres lots intégrés, sans attribution au seul lot 69.
  Aucun appel à Luna ; ni `main`, ni `planification.py`, ni `signes.py` ou scénario modifiés.
  Les rafales de premiers passages restent possibles ; les indices anciens déjà évincés
  ne se reconstruisent pas dans une ancienne sauvegarde. La consommation illicite de la
  croûte après refus suit la voie du vol, distincte d'une demande : pas de correctif hors lot.
  Budget de 45 min dépassé (compléments du contrat et reprises ciblées, suite de 38 min) ;
  calculs finaux à priorité réduite, trois simultanés au plus.
  [Règle](plan-ouie.md) et [rapport du lot 69](taches/rapport-codex-69-appels-restes.md).
  Fusionné sur l'intégration après les lots 67 et 68 : seul conflit de documentation ; `deliberation.py`/`esprits.py` fusionnés sans conflit avec les lots 64 et 60 ; suite complète relancée.

- Branche `codex-impressions-observer`, fusionnée, lot **68**, base **d78cfcc**,
  brief **764e040** : `signes._bilan_signes` restitue les impressions actuelles de la
  cible d'une observation explicite, même déjà annoncées. Le filtre des nouveautés
  introduit par la calibration **0f16152** reste réservé au bilan spontané ; le lot
  53 n'avait pas retiré les lectures. Règle commune de lecture, jets mémorisés et
  exigence du signe encore perçu conservés. Trois tests nouveaux, chacun sur la
  scène réelle d'Ilse et sur Brune : saisie/moteur/journal, deux observations sans
  nouveau dé, disparition sélective d'un signe, perte/retour de vue, état complet et
  rendu après recharge. **49 tests ciblés verts**. Empreintes Relais/crue 2 h ×
  quatre graines contre **d78cfcc** : chronique, mesures et état final complet
  identiques ; référence rangée dans le cache. Suite complète unique : **1 837 tests,
  16 ignorés, aucun échec ni erreur**, 182 fichiers, **1 484,1 s**, trois processus
  à priorité réduite. Aucun appel à Luna ni changement de
  `planification.py`, de `deliberation.py` ou de `main`. Une lecture reste faillible,
  son délai de dix minutes et sa validité inchangés ; calibration hors lot.
  [Rapport du lot 68](taches/rapport-codex-68-impressions-observer.md).
  Fusionné sur l'intégration après les lots 62 à 67 : seul conflit de documentation ; `signes.py` intouché depuis la base.

- Branche `codex-prime-offre`, fusionnée, lot **67**, base **cd25fcd** :
  les offres de mission et les propositions utilisent les mêmes termes typés
  (prestation conditionnelle, contrepartie, débiteur et créancier). Le dossier de
  comptes distingue `offre`, `du`, `rendu`, `absent` ; les rôles et les deux termes
  d'une offre sont comparés à l'état fourni, puis contrôlés à l'enregistrement.
  Le devis de mission vient de `prime_base` ou de l'accord ; le lieu actuel du
  donneur accompagne sa condition. Remise et paiement restent atomiques, avec
  compte `rendu` fourni au récit. Cinq tests nouveaux console/MJ simulé/recharge,
  dont offre réelle sans dette ni repli, remise payée dans le bon sens et récit
  rechargé, autre échange contre tâche différée, termes faux et garde persistant.
  44 tests ciblés des contrats existants verts (un ignoré). La suite unique relève
  deux tests de noms inconnus (préparation `comptes` désormais avec noms appris)
  et deux lectures directes du stockage ; préparation inconnue explicite et
  lectures par `agendas.contrats`, puis 22 tests de parole et 28 tests finaux
  offres/dialogues/socle verts, avec le récit payé rechargé.
  Suite unique à trois processus, priorité réduite : **1 839 tests, 16 ignorés**,
  1 973,6 s ; un échec et deux erreurs initiaux, corrigés et rejoués dans les
  fichiers concernés. Bilan consolidé sans défaut restant connu, sans seconde suite.
  Luna, une passe : crypte 25 appels / neuf tours, ressources 11 / trois, sans
  repli ; prime « Vingt pièces, quand tu me remettras l'anneau du veilleur ici »
  en quatre appels sans refus ni relance. `comptes` préparé avec noms : délai
  réseau sur Gorm avant opération, puis refus de Brune dans le bon sens ; aucune
  erreur de recharge. Référence main 42bb9c0 relue en cache (crypte : 24 / neuf) ;
  lanceur récent incompatible avec ce vieux commit pour les scripts manquants.
  Comparaison intégrée f033364 également relue, périmètre différent, sans
  comparaison de latence. Limites : extraction et reformulation encore sémantiques,
  remboursement de Gorm non validé en ligne par cette passe. Ni `main`, ni les
  fichiers réservés aux lots 66 et 68 ne sont modifiés.
  [Rapport du lot 67](taches/rapport-codex-67-prime-offre.md).
  Fusionné sur l'intégration après les lots 61, 64 et 65 : `mj.py`, `narration.py` et `paroles.py` touchés aussi par les lots 61 et 65, fusionnés sans conflit ; suite complète relancée.

- Branche `codex-attendu-designable`, fusionnée, lot **65**, base **de3e986** :
  les listes d'entités dans les refus passent par `refus.cibles` : candidats du geste,
  `Monde.designable`, références publiques, tri et plafond commun. Le champ technique
  `attendu` conserve `personne_<n>`/`element_<n>` au lieu de les convertir en portraits.
  Même contrat pour actions, opérations, improvisations, outils, dons, paroles, combat,
  défense et ajouts. Les souvenirs visuels marqués, corps reconnus, voix récemment
  entendues et noms appris se désignent sans donner d'accès matériel ; registres existants
  rechargés, aucune migration. Le cas réel est reproduit en console/MJ simulé et en Luna :
  plus de `brune`, `marchand`, `barbe_gorm`, `mains_gorm` dans les candidats transmis.
  Nuance du constat : dans le Relais, `echoppe` est la Conduite basse, dont les surfaces et
  Gorm sont perçus ici ; leurs références publiques restent légitimes, comme les souvenirs
  marqués d'ailleurs. Cinq nouveaux tests, état et rendu après recharge ; parcours de toutes
  les actions et opérations sur deux mondes. Suite complète unique, trois processus :
  **1 823 tests, 16 ignorés**, 1 092,75 s ; neuf assertions initiales (deux régressions
  corrigées, sept attentes connaissance/accès adaptées). **103 tests de reprise verts**,
  plus 24 tests de défense/sauvegarde ; bilan consolidé sans échec restant.
  Empreintes Relais, 2 h × quatre graines contre de3e986 : chroniques, mesures et états
  complets identiques. Luna une passe relais/crypte/echanges : cache main 42bb9c0 relu,
  scripts identiques mais ancien harnais ; 62 → 54 appels, 22 → 20 tours MJ,
  **2,82 → 2,70 appels/tour**, 12,03 → 11,32 s/tour (temps indicatifs). Aucune erreur
  technique ni de recharge ; un repli en crypte sur les conditions de prime et le sens
  d'une offre/dette, hors lot, reste consigné. Candidats bornés déterministement ; aucune
  garantie nouvelle sur les contradictions sémantiques ou faux refus d'audit. Ni main,
  ni `planification.py`, ni `social.py`, ni scénarios, ni consignes ou modèle modifiés.
  [Contrat, mesures et limites](taches/rapport-codex-65-attendu-designable.md).
  Fusionné sur l'intégration après les lots 60, 61 et 64 : `monde.py` et `narration`/`mj` touchés aussi par le lot 61, fusionnés sans conflit ; suite complète relancée.

- Branche `codex-deja-dit`, fusionnée, lot **64**, base `de3e986` : le registre sauvegardé
  `esprit.faits_dits` suit les identités, valeurs et destinataires hors des quarante souvenirs.
  Contrat commun de `social.faits_dits`, `nouvelles`, `bavarder`, `_a_dire` et `dire` : dates,
  preuves, confiance et épisodes ne créent pas une nouvelle valeur ; objets homonymes distincts.
  Les relais conservent la date d'observation : une propriété ancienne ne remplace plus une
  connaissance plus récente et ne rajeunit plus un guet. Migration des anciennes traces encore
  disponibles ; 512 identités par PNJ sans éviction, nouvelles identités tues à saturation.
  Capture mine 3 reproduite sur `5c2ce81` (archives absentes) : à 14, Lucien sait déjà le guet depuis
  Rémy à 4 et figure dans l'ancien suivi ; aucune répétition de Josse jusqu'à 247. Onze tests nouveaux,
  dont deux comparaisons du monde complet et des paroles, même laps découpé et rechargé.
  Banc final 4 h × quatre graines × quatre scénarios contre `de3e986` (référence en cache) : aucun
  plantage, violation ou usurpation, aucune boucle nouvelle signalée ; avertissements redits mot pour
  mot Relais 0 → 0, mine 2,5 → 0,5, auberge 0,25 → 0,25, crue 0 → 0 ; constats confiés 2,5 → 2,5,
  22,5 → 18,5, 12,5 → 10,25, 5 → 5. Les doublons restants du rapide sont des homonymes ou suivent
  un changement appris (guet → fatigue → guet). Audits 12 h mine 3 et auberge 7 : aucun plantage,
  violation ou usurpation ; Josse ne répète plus le guet à Lucien ; doublons textuels 2 / 3.
  Suite complète unique : 1 829 tests, quatre ignorés, deux échecs et une erreur ; reprise finale
  de 69 tests sociaux verte. Les 17 tests des deux parcours sont revalidés après ajustement des scènes
  (huile reprise seule sur l'assertion finale : 140 s) : **bilan consolidé 1 829 tests, quatre ignorés,
  aucun échec ni erreur restant** ; aucune seconde suite complète. Ancien souvenir `dit` de test complété par sa valeur ; scènes de vente
  d'huile et de bois rendues explicites (les deux tests passaient sur la base). **Limite révélée hors
  lot** : un feu rechargé dans la minute même de l'accord peut laisser l'engagement non soldé,
  faute d'observation datée après l'accord ; la scène de bois sépare ces deux minutes, sans corriger
  ce contrat ici. Aucun appel à Luna, changement de `planification.py` ni de `main`.
  Voir [la règle](plan-ouie.md) et le [rapport](taches/rapport-codex-64-deja-dit.md).
  Fusionné sur l'intégration après les lots 60 et 61 : `deliberation.py` touché aussi par le lot 60, fusionné sans conflit.

- Branche `codex-orientation`, fusionnée, lot **61**, brief **1008f21**, après
  intégration de `origin/integration` **04bca30** : objets perçus et dernières positions
  mémorisées portent leurs demi-plans dans le regard actuel de Corvus (`orientation_relative`).
  Le contrôle commun compare les locatifs explicites aux repères publics, même si l'auditeur
  les admet ; chaque refus a son `attendu`, et le garde est refait avant enregistrement avec
  l'état courant. Aucune position cachée n'est lue pour reprojeter un souvenir. « refus » rejoint
  le garde existant de voix d'auteur. Dix tests nouveaux, dont console/MJ simulé et recharge :
  poutre à l'est après rotation ouest, Ilse vue de face puis dans le dos, gauche/droite,
  absolu admis, huit regards, absence de fuite et regard modifié avant enregistrement. Une réponse
  pronominale se relie à la cible publique unique de la demande, sans deviner une cible ambiguë.
  Empreintes Relais 2 h × quatre graines contre **04bca30** : chronique, mesures et état final
  complet identiques. Suite complète unique à trois processus : **1 815 tests, 16 ignorés**,
  aucun échec ni erreur, 1 304,7 s ; 109 tests ciblés et dix tests finaux verts. Résultats dans le
  [rapport du lot 61](taches/rapport-codex-61-orientation.md).
  Luna, une passe des trois scripts prescrits : aucun repli ni erreur de recharge ; un faux refus
  pronominal, corrigé ensuite et rejoué avec MJ simulé ; pas de deuxième passe Luna.
  **Limite explicite** : le garde lexical ne garantit pas l'invariant pour toute paraphrase
  française ; les directions implicites et la portée temporelle restent sémantiques. Une
  ambiguïté ou une négation demande une reformulation, sans direction devinée. Ni `main`,
  ni les fichiers des lots planification/appel, ni le modèle `gpt-6-luna` ne sont modifiés.
  Fusionné sur l'intégration après les lots 56 à 60 : `narration.py` et `mj.py` touchés aussi par les lots 56 et 59, fusionnés sans conflit ; suite complète relancée.

- Branche `codex-rendez-vous`, fusionnée, lot **60**, base **c592d68**, accordée au début
  avec l'intégration **04bca30** : une clôture commune (`appel.retrouves`, reprise par
  `deliberation.rejoint` pour les dialogues) efface l'attente et la venue des deux avant
  d'écrire une seule retrouvaille ; perception actualisée et choix réveillé. Celui qui attend
  ne repart pas avant le traitement de l'arrivée par le voyageur après son geste ; l'aperçu
  au seuil le réveille, la venue se termine au lieu convenu ou à une parole réellement échangée.
  Capture recréée sur `5c2ce81` (bruts du brief absents) : auberge 42 à 500–510 minutes,
  appels **9 → 1**, retrouvailles **5 → 1**, la demande reprend. Six tests de recharge,
  découpage, état complet, rendu, Relais, joueur et rendez-vous manqué. Banc 4 h × quatre
  scénarios × quatre graines contre `c592d68` : mesures de jeu identiques, zéro plantage,
  violation ou usurpation ; références en cache. Audit auberge 12 h, graines 42/7 : appels
  **15/8**, retrouvailles **7/4**, redites à moins de dix minutes **2/0**, passages/PNJ/h
  maximum **22/31**, aucun plantage ou usurpation. **Réserve : l'absence générale de
  retrouvailles rapprochées n'est pas acquise** ; à 462–463, Odile repart après la clôture,
  avant la demande, et les nouveaux appels ouvrent d'autres rendez-vous. Suite complète unique :
  **1 810 tests**, un ancien attendu social en échec, quatre sauts, **693,1 s**, trois processus
  à priorité réduite. Après ajustement de cet attendu et reprises ciblées (44 tests), bilan
  consolidé **1 811 tests, quatre sauts, aucun échec restant** ; aucune seconde suite complète.
  Limites : clôture au choix après arrivée dans la salle convenue, sauf dialogue ; échéance
  et urgences conservées, disponibilité ultérieure non garantie. Aucun appel au modèle,
  `planification.py` et `main` inchangés. [Rapport du lot 60](taches/rapport-codex-60-rendez-vous.md).
  Fusionné sur l'intégration après les lots 56 à 59 : `deliberation.py` touché aussi par le lot 57 (refus retenus), fusionné sans conflit ; suite complète relancée.

- Branche `codex-eau-plan-marche`, fusionnée, lot **58**, base **c592d68** :
  le désaccord plan/marche de la crue venait de `eau.estimation`, qui rajeunissait
  une ancienne vitesse à chaque vue du niveau dans sa salle. Les deux pentes
  opposées de Gorm à 368 min se remplaçaient à chaque passage, sans mesure nouvelle.
  La dernière vue ancre désormais le niveau, le dernier repère mesuré choisit la
  vitesse ; une première mesure ou un sol sec efface la pente sans ses deux repères.
  Les croyances sauvegardées suffisent, les entrées de recherche couvrent déjà la
  prévision ; aucun registre de refus, changement des routes, du MJ ou des scénarios.
  L'eau inconnue découverte au seuil reste apprise et datée avant la prochaine route.
  Captures originales de `5c2ce81` rejouée (archives absentes) : Gorm crue 2024 à 368,
  Ilse crue 1985 à 247, même boucle reproduite avant les minutes citées de l'audit.
  Sur vingt minutes, refus 9 → 2 / 5 → 1, passages 44 → 14 / 40 → 12 ; monde complet
  et rendu identiques après recharge, d'un bloc ou par minutes. Le premier refus
  peut viser le plan ancien déjà inscrit dans la capture ; une mesure nouvelle peut
  encore interdire une route. Les deux captures du lot 39 gagnent le sec, le détour
  dangereux reste refusé. Rapide 4 h × quatre graines contre `c592d68` (référence
  en cache), crue/Relais : aucun plantage, violation ou usurpation ; empreintes du
  Relais identiques. Crue, maximum horaire moyen 24,75 → 17,75 (pire 46 → 30),
  eau 83,75 → 87,5 min·PNJ, sans recours 60 → 60. Audit 12 h, 2024/1985/500 :
  passages/h, pire 20/22/34, eau 220/345/1 090, sans recours 245/230/60,
  « eau longue » 0/0/4 ; aucun plantage ni écart. Les 49 tests ciblés passent.
  Suite finale une fois, trois processus, priorité réduite : 1 800 tests, quatre
  ignorés, un échec (750,9 s), déjà présent avec `eau.py` exact de `c592d68` :
  `test_appel_negocie.QuoiTests.test_cas_reel_mine_josse_dit_ce_qu_il_veut_gaspard_le_fait_venir`
  attend une part promise alors que Gaspard refuse puis échange. `VERIFIER` et
  `spatial.VERIFICATION=1`, 2 h, crue 42/2024 : aucun plantage, écart ni borne.
  Voir la
  [règle](plan-crue.md) et le [rapport](taches/rapport-codex-58-eau-plan-marche.md).
  Fusionné sur l'intégration après les lots 55 à 57 et 59 : seul conflit de documentation ; `eau.py` seul fichier de code, intouché depuis. L'échec de `test_appel_negocie` cité plus haut était déjà adapté dans l'intégration.

- Branche `codex-contenu-vide`, fusionnée, lot **59**, base `18abb2c` (intégration
  `c592d68`, à jour sur `origin` au départ ; lot 56 encore absent) : mots exacts sans contenu
  mécanique acceptés sans revue ; après deux typages refusés, reprise des mots fournis sur
  l'état original, sans effet typé ni effet des copies refusées. Les mots non fournis restent
  à préciser. La portée mécanique est un champ obligatoire de chaque segment d'audit,
  indépendant du verdict : une citation `parole` ne peut plus contourner un refus de portée
  sans fondement ; source exigée pour la portée établie, contrôle refait à l'enregistrement.
  Quatre tests nouveaux : console/MJ simulé, parole entendue, contrats, missions, or et texte
  après recharge ; prime inventée et prix à l'auberge, deux questions réelles et secours.
  Suite complète unique, trois processus à priorité réduite : **1 800 tests, 16 ignorés,
  un échec préexistant**, 1 088,45 s. `test_appel_negocie.QuoiTests.test_cas_reel_mine_josse_dit_ce_qu_il_veut_gaspard_le_fait_venir`
  attend une demande promise ; le PNJ refuse puis accepte un échange. Rejoué seul sur une
  copie de la base 18abb2c : même assertion et chronique identique (encodage normalisé).
  Aucun correctif PNJ hors lot. Les quatre tests du lot repris sur leurs assertions finales
  sont verts (8,92 s).
  Luna une passe, crypte/soir-noir/echanges/noms-dialogue : Gorm offre 20 pièces du moteur,
  les deux questions sont dites et répondues sans « Précise… », Aubin seul répond au bois.
  Référence `main` 42bb9c0 relue dans le cache : 69 → 70 appels, 22 → 21 tours MJ,
  3,14 → 3,33 appels/tour, 12,6 → 13,2 s/tour ; aucun repli ni erreur technique/recharge.
  Faux positif d'audit sur « ici » dans la condition de remise, corrigé avant affichage.
  Reconnaissance des effets/conditions et pertinence de leurs sources toujours sémantiques,
  sans garantie absolue contre les inventions. Aucun changement de `main`, des scénarios,
  du modèle ou de `paroles.py`/`biens.py` ; pas de fusion. Bruts dans `artifacts/` du worktree.
  [Cause, contrat, mesures et limites](taches/rapport-codex-59-contenu-vide.md).
  Fusionné sur l'intégration après les lots 56 et 57 : `mj.py` et `narration.py` fusionnés sans conflit avec les comptes du lot 56 ; les faux rapports d'audit des tests portent désormais `comptes` (lot 56) et `portee_mecanique` (lot 59) ; suite complète relancée.

- Branche `codex-offre-sensee`, fusionnée, lot **57**, base **c592d68** : le
  proposant juge sa contrepartie avec `evaluer_proposition` inversée, au choix
  et avant exécution : ni ce qu'il garde, ni ce qui lui est nécessaire, ni une
  perte supérieure au gain. Un bien ne vaut plus zéro faute de pièces en poche.
  Le refus d'un marché ou d'un achat garde les moyens de cette demande et la
  force effectivement offerte ; délai, lien qui s'estompe et richesse non
  offerte ne relancent plus. Nouveau moyen cru ou offre plus forte seulement.
  **Ilse, crue 7, minute 353**, reproduite sur **5c2ce81** : le devis comptait
  sur du bois demandé à Gorm, qui ne pouvait pas le livrer. `devis_service`
  valide les fournitures par les livraisons communes, avant accord et paiement,
  pour tâche payée, confiée, marché et empêchement ; aucun changement du
  planificateur. Fixture réelle sauvegardée, second lot de bois vérifié.
  Banc rapide **4 h × 4 graines × 4 scénarios** contre **c592d68** : aucun
  plantage, violation ni usurpation ; propositions moyennes Relais **0,75 → 0,5**,
  mine **5,25 → 5,25**, auberge **2 → 1,5**, crue **5 → 2,75**. Audit **12 h** des
  seules crue 11/7 et mine 42/1985 : aucun plantage ni usurpation, aucune tâche
  due aussitôt. Deux paires textuelles : Odon apprend le coffre ouvert (125 → 139),
  Lucien demande deux lots homonymes distincts (646), pas la même offre répétée.
  Suite complète unique : **1 800 tests, 4 sauts** ; trois attentes de scénario
  ajustées et fichiers repris. Avec le cinquième test ciblé ajouté, bilan consolidé
  **1 801 tests, 4 sauts, aucun échec ni erreur**.
  Vérification complète et limites dans le
  [rapport du lot 57](taches/rapport-codex-57-offre-sensee.md).
  Code **e65310c**, signature SSH vérifiée. Aucun appel à Luna ; `main` non touchée.
  Fusionné sur l'intégration après les lots 55 et 56 : conflits de documentation et de `test_appel_negocie` (même adaptation des deux côtés, réunie) ; fichiers de code communs `echanges.py` (lot 56 : comptes) fusionnés sans conflit, suite complète relancée.

- Branche `codex-sens-dette`, fusionnée, lot **56**, base **f033364**, brief
  **0b2ea87** : les comptes transmis au MJ portent débiteur, créancier, objet ou
  pièces, quantité et état dû/rendu/absent ; les réclamations donnent leur solde
  et leurs remises effectives. L'auditeur extrait les rôles de chaque segment,
  même une réplique ; le moteur les compare à l'issue et refait le contrôle à
  l'enregistrement. Un rapport incomplet est illisible, chaque compte contraire
  reçoit un `attendu` citant l'issue. L'absence monétaire dit « aucune pièce ».
  Neuf tests nouveaux : console, MJ simulé, état/fiche/textes après recharge,
  deux absences et leurs inversions, remboursement, refus, prêt échu au joueur,
  restitution d'objet, prose ordinaire, garde persistant et comptes privés exclus.
  **50 tests ciblés finaux verts**. Suite complète unique : 1 793 tests, 16 ignorés,
  1 302,4 s, trois processus à priorité réduite ; ancien placement de prêt et
  liste de faits du harnais artisanat corrigés, trois fichiers rejoués verts.
  Bilan consolidé : **175 fichiers, 1 793 tests, 16 ignorés**, aucun défaut restant ;
  aucune seconde suite complète.
  Empreintes Relais, 2 h × quatre graines : chronique, mesures et état final
  complet identiques à f033364. Luna une passe : `ressources`, 9 → 13 appels
  contre le cache intégré f033364, 3 → 4,33 par tour ; inversion refusée trois
  fois, repli moteur dans le bon sens. `comptes` : zéro appel des deux côtés,
  noms non appris ; aucun test en ligne du règlement dans ce script. Extraction
  sémantique encore faillible (un faux refus observé), aucune garantie absolue
  d'absence d'inversions ; précision finale « aucune pièce » vérifiée sans modèle
  après cette passe. Pas de changement de `main`, de `planification.py` ou des
  fonctions sociales réservées au lot 55. [Rapport et limites](taches/rapport-codex-56-sens-dette.md).
  Fusionné sur l'intégration après le lot 55 : seul conflit de documentation ; aucun fichier de code commun.

- Branche `codex-constats-partages`, fusionnée, lot **55**, base **5b174ad** : les constats matériels
  récents vus ou essayés se confient par les nouvelles communes, après les accusations : ressource
  épuisée, contenant ouvert vide, verrou, source éteinte, eau d'un lieu. `recevoir` en fait du ouï-dire
  (`dit:`, confiance/rang communs), daté de l'observation ; un constat propre de même minute ou
  postérieur prime. `croire` conserve les destinataires du même état, y compris entre observation et
  relais, après sauvegarde. `moyens_crus`/`tient` et `planification.py` inchangés. Prérequis révélé au banc :
  une source mobile qu'on ne voit plus à son ancienne case peut avoir bougé ; cette absence seule ne
  constate plus son extinction. `constater` relève aussi le vide d'un contenant ouvert vu.
  Au plus une confidence par minute du jeu : repère sauvegardé `derniere_confidence`, commun à toutes
  les nouvelles ; la durée ordinaire de la parole reste inchangée.
  Tests de paroles, d'état, de reprise et de découpage ; banc quatre scénarios × quatre graines × 4 h :
  aucun plantage, violation ni usurpation ; constats confiés moyens Relais **3,5**, mine **22,25**,
  auberge **12,5**, crue **7**. Pas d'alternance répétée d'états (bascules maximales : 1) ; deux objets
  homonymes peuvent produire le même texte. **Réserve d'audit** : mine 2024, cinq avertissements redits
  sur le guet d'Odon et deux lampes homonymes ; un ancien épisode de guet se retransmet. L'absence de
  toute répétition nouvelle n'est pas acquise ; le partage matériel ne corrige pas ce défaut des rumeurs
  d'intention préexistantes. Détails dans le rapport.
  Suite complète unique (3 processus), puis reprise finale de 26 fichiers (294 tests) : bilan consolidé
  **1 790 tests, 4 sauts, aucun échec ni erreur**. Détails et limites dans le
  [rapport du lot 55](taches/rapport-codex-55-constats-partages.md).
  Ni Luna ni comparaison de modèles ; ni fusion ni modification de `main`.
  Fusionné sur l'intégration après le lot 54 : conflit d'imports dans `social.py` (accord commun du lot 54 et `RECENT`/`esprit` du lot 55), le reste sans conflit ; tests ciblés et suite complète relancés.

- **Vérification d'intégration 5c2ce81** (lots 31, 32, 34, 35, 37 à 49 ; sans Luna ; bruts
  `artifacts/verif-integ-5c2ce81/` du dépôt principal). Audit 12 h, quatre scénarios × 1985, 7, 42, 2024, 3, 11, 99, 500,
  contre 42bb9c0 (cache) et ffcc295 : aucun plantage, violation, usurpation ni coup contre une personne. Par nuit,
  42bb9c0 → ffcc295 → 5c2ce81 : sans recours Relais 206 → 193 → 169, mine 23 → 44 → 25, auberge 188 → 183 → 151, crue
  141 → 217 → 149 ; noir mine 1 413 → 1 310 → 1 151 ; bascules en baisse (mine 0) ; passages par heure, pire, mine
  17 → 24 → 35, auberge 28 → 30 → 42, crue 36 → 32 → 49 ; échanges mine 88 → 106, auberge 77 → 117 ; propositions /
  acceptées par nuit Relais 6,9/1, mine 23,3/1,4, auberge 22/3,6, crue 9,9/0,5. Se dénoncer soi-même : 0 (corrigé).
  `rixe`/`rixe_douce` 8 h : aucun coup contre une personne. `VERIFIER` + `VERIFICATION` 0,2, 8 h, graine 42, cinq
  scénarios : aucun écart, aucune recherche bornée. Temps d'horloge 12 h (indicatif, non lancés ensemble) : Relais
  44,5 → 118 → 76 s, mine 238 → 711 → 419 s, auberge 206 → 739 → 493 s, crue 56 → 100 → 109 s. **Défauts** : (1) **plan
  et marche en désaccord sur l'eau** : crue 2024 368-383, Gorm monte dix fois galerie → vannes, la marche refuse
  (« séjour ou retour menacé par l'eau »), il remonte, recommence (49 passages/h) ; crue 1985 258-264, Ilse ; le refus
  de la marche n'est pas retenu ; (2) chercher en appelant, restes : Odon mine 7 (« Lucien ? » ×10 puis mange la croûte
  que Lucien lui refusait), Odile auberge 7 et 2024 (« Joss ? » ×9-10) ; (3) **rendez-vous clos d'un seul côté** :
  auberge 42 501-506, Anselme hèle Odile ×10, « J'arrive ! » ×5, Odile « retrouve Anselme, comme convenu » ×5 ; (4)
  **propositions du lot 45 redites sans fait nouveau** (Brune à Gorm ×6, crue 11 ; offres identiques en moins d'une
  heure : 6 / 14 / 16 / 14 sur 8 nuits ; achats refusés repris au même prix) ; (5) **contreparties absurdes** (Bram
  offre la clé de la paie qu'il garde ; Odon un outil contre toute la paie) ; (6) tâche acceptée puis abandonnée dans
  la minute (crue 7, Ilse, après une surenchère de Gorm) ; (7) avertissements redits (mine 3, Josse ×5 ; auberge
  0,6 → 2,9) ; (8) accord : « l'outils de serrurier », « 1 pièces ». Connus : crue 500 en partie (Brune et Aubin au
  sec ; Gorm et Ilse 235 min au refuge mouillé dès 215) ; Bram agit (appels, achat, hèle) ; Brune crue 3 corrigé.

- **Vérification Luna de l'intégration f033364** (lots 40, 42, 44, 47 b, 50, 54 ; deux passes contre `main` 42bb9c0 en
  cache ; bruts `artifacts/verif-luna-f033364/` du dépôt principal). Onze scripts : 3,15 → 2,96 appels et 12,7 → 11,1 s
  par tour MJ, relances 8 → 2,5, refus 16 → 10,5, replis 0,5 → 0 ; 57 → 53 tours MJ. Les lots 40, 42, 44, 47 b et 50
  tiennent dans les deux passes ; 54 en partie (le chuchotement n'est pas joué). `ressources` et `comptes` 3,0 appels,
  `sous-obstacle-*` 1,9 (intégration seule, pas de référence). **Défauts nouveaux** : (1) **prime inventée** : crypte
  n° 24, « Gorm, combien me donnes-tu pour l'anneau ? » typé `parole_joueur` à `propos` vide (sur `main` :
  `conversation_pnj`/`proposer`), Gorm offre 10 pièces (passe 2) au lieu des 20 de `prime_base`, l'auditeur l'admet ;
  (2) faux refus affiché « Précise ce que tu veux dire… » sur un `propos` vide ou un `ressource` « présence »
  (`soir-noir` n° 1, `echanges` n° 2) ; (3) méta-langage « Le refus précédent ne signifie pas… » (relais n° 22) ; (4)
  orientation fausse admise d'après un souvenir (poutre « devant toi » après « tourner ouest ») ; (5) `signes-ecart` :
  « observer Ilse » ne donne plus « semble craindre Brune » (deux passes ; `main` oui), à relier aux lots 53 ou de
  calibration ; (6) le banc `comptes` n'a pas de `noms_connus` (paroles refusées localement, sans MJ). Persistent : la
  dette inversée (lot 56 en cours), l'ambiance « aucun autre bruit… », l'`attendu` d'une cible inconnue qui liste des
  identifiants hors de la salle, « je réponds » sans appel.

- Branche `codex-elision`, fusionnée, lot **54**, base **5125d06** :
  `francais.groupe_nominal` accorde les désignations avec de/à et leur capitale ;
  `inserer_designation` reprend la liaison du texte lors de la projection d'un nom
  ou d'une référence opaque dans la prose. Citations et références typées conservées.
  Même accord dans les rendus sociaux, dons, promesses, réponses et noms d'objets ;
  aucune donnée de scénario, règle mécanique, consigne ni modèle changé. Le cas réel
  donne au MJ « Je me méfie du vieil homme voûté. », en gardant la parole prononcée.
  Six tests nouveaux : formes françaises, console/MJ et recharge, nouvelle entendue,
  don et promesse à deux corps désignés. **127 + 106 tests ciblés verts**, puis les
  six cas finaux rejoués verts. Suite unique : **1 776 tests, 16 ignorés**, 1 556 s,
  trois processus à priorité réduite ; un ancien attendu grammatical corrigé
  (19 tests rejoués verts), une `StopIteration` de console non reproduite
  (six tests rejoués verts, cause non établie). Bilan consolidé avec les contrôles
  finaux : **173 fichiers, 1 777 tests validés, 16 ignorés** ; aucune seconde suite.
  Empreintes 2 h, Relais/auberge × quatre graines : mesures identiques ; six états
  entièrement identiques et cinq chaînes seules changées dans les deux autres
  (déterminants en milieu de phrase, « près de l'âtre »). États complets diagnostiqués.
  Luna une passe `echanges`/`noms-dialogue` : 22 appels, sept tours MJ, aucun repli
  ni erreur technique/recharge ; le chuchotement inaccessible à Brune inconnue est
  joué seul sur copie préparée, quatre appels, sujet corrigé et citation originale
  affichée. Refus sémantiques hors lot consignés. Correctif signé SSH **8a9ed47**,
  signature vérifiée ; aucun changement de `main`, `planification`, `deliberation`
  ou `signes`. [Rapport, mesures et limites](taches/rapport-codex-54-elision.md).
  Fusionné sur l'intégration après le lot 53 : seul conflit de documentation ; aucun fichier de code commun.

- Branche `codex-peur-transmise`, fusionnée, lot **53**, base **5125d06** :
  un proche dont la détresse est perçue ne rassure plus ; `autour` le retire de
  la compagnie et `ecart_securite` ajoute 0,5 × (confiance + affection) / 100
  point/minute, maximum des proches concernés, via le temps vécu existant.
  Signes perçus et impressions encore appuyées par un signe présent seulement ;
  appel entendu attribué par la vue ou une voix reconnue jusqu'à la prochaine
  minute. L'appel éveille l'auditeur ; un vrai pas de fuite produit un signe de
  place sans révéler l'agresseur ni la destination. Le projet privé ne suffit pas.
  Sept tests nouveaux : épreuve Brune/Aubin/Ilse, appel à l'auberge, compagnie
  calme, dos/noir, fuite exécutée, lien, impression et voix inconnue ; état et
  rendu après recharge, même laps découpé. Banc rapide cinq scénarios × quatre
  graines × 4 h contre `5125d06` : aucun plantage, violation, usurpation ni nouveau
  signalement de boucle ; référence en cache pour la reprise finale de branche.
  Relais/mine/rixe inchangés ; appels conservés à l'auberge, plus d'inquiétude et
  quelques réactions différentes en crue. Correctif **9b8a590**, signature SSH
  vérifiée. Suite complète unique : **1 776 tests, quatre ignorés**, verte,
  173 fichiers, trois processus à priorité réduite, 707,2 s ; reprises ciblées
  sur le dernier raccord de perception, dont les sept nouveaux tests finaux, vertes.
  Aucun appel à Luna, aucun fichier du MJ ni de `planification.py`
  modifié, `main` non touchée. Questionner l'allié et attention conjointe reportés.
  [Réglage, vérification et limites](taches/rapport-codex-53-peur-transmise.md).

- Branche `codex-depart-feutre`, fusionnée, lot **51**, base **d60b80a** :
  les gardes des suites admissibles découvrent le besoin de discrétion ; sans
  cette découverte, un seul départ ordinaire. Si elle a lieu, reprise depuis
  le départ avec les deux allures ; marque `discretion` retenue par PNJ/but
  dès la première recherche, nœuds conservés seulement à la deuxième.
  Invalidation par les entrées communes ; graphes de lumière et certificat
  partagent les départs. `VERIFIER` garde le témoin historique et le contrat
  hors plafond / recherche complète du lot 48. Aucun coût, prix, plafond,
  scénario, fonction réservée au lot 46 ni appel au modèle modifié.
  Rémy à 480 min : 4 000 → 2 524 états, même absence de plan ; Brune devant
  la réserve et un allumage illicite : mêmes plans, conséquences, état et
  rendu après recharge. Marque conservée puis invalidée avec les permissions.
  Empreintes 2 h, quatre scénarios × quatre graines : identiques à la base.
  `VERIFIER` et `spatial.VERIFICATION=1`, mine/auberge 42, 2 h : sans écart,
  borne ni usurpation. Suite complète unique : **1 760 tests, quatre ignorés**,
  verte, 170 fichiers, trois processus à priorité réduite, 889,2 s.
  Correctif signé SSH **453a6f3**, signature vérifiée ; `main` non touchée.
  Huit nuits de 12 h, mine/auberge × 42/1985 × départ tiré/fixe : `comparer --calcul`
  entièrement identique, résultats de tous les appels logiques compris ; aucune
  bifurcation, aucun plantage ni usurpation. Trois versions lancées ensemble,
  deux processus chacune : CPU global base → branche **2 230,19 → 2 170,67 s
  (−2,7 %)**, mine −4,2 %, auberge −0,6 % ; nœuds **10 122 834 → 8 823 096**,
  bornées **1 154 → 867**. Gain limité : mine 1985 tiré **+8,6 %** ; la découverte
  coûte encore et le prototype local ne se généralise pas à toute la nuit.
  Mesures et limites dans le [rapport du lot 51](taches/rapport-codex-51-depart-feutre.md).
  Fusionné sur l'intégration après les lots 46 à 50 : `planification.py` fusionné sans conflit avec les lots 46 et 48 (fonctions distinctes) ; suite complète relancée sur la fusion.
  Accord : `test_une_source` (Rémy, mine 1985 à 480) supposait la base sans la règle du lot 46 plafonnée ; avec le
  départ feutré découvert au besoin elle peut aboutir sous la borne, et le test exige alors le résultat complet.

- Branche `codex-ressource`, fusionnée, lot 50, base d'intégration `d60b80a`,
  brief `d24e7d5` : `ressource.sujet` conserve le bien nommé (nom, alias, matière,
  catégorie), même inconnu de Corvus ; `faim`/`chaleur` restent les besoins généraux.
  Même sens dans le schéma, `SENS_CONTENU` et le dossier de contre-revue ; les sujets
  restent littéraux dans la projection publique. `echanges.enqueter` cherche dans
  les seules possessions connues de l'interlocuteur, sans transfert ni capacité déduite.
  Six tests nouveaux après recharge : bois/Aubin au Relais, lampe/Lucien et huile
  absente dans l'auberge, correction d'un besoin trop large et refus d'un contenu
  contraire, possession ignorée non révélée et sujet vide avec `attendu`.
  Banc rapide 4 h × quatre graines, Relais/auberge contre `d60b80a` : chroniques,
  empreintes aux relevés, récits et souvenirs identiques, mêmes mesures et audits,
  aucune usurpation ou violation ; référence calculée une fois puis mise en cache.
  Suite complète unique, trois processus à priorité réduite : **1 760 tests, 16 ignorés**, 170 fichiers verts, 1 929,2 s. Le temps de cette suite fait dépasser les 45 minutes du lot.
  Luna une passe : bois dit à Aubin, réponse par ses planches dans `noms-dialogue`
  et `soir-appel` (quatre appels chacun) ; `ressources`, préparation des noms connus
  rétablie après un lancement sans appel, bois et nourriture en trois appels chacun.
  Aucun faux refus sur ces demandes, aucun repli ni erreur technique/recharge.
  Trois scripts comparables à `main` `42bb9c0` lu du cache : 41 → 40 appels,
  13 → 11 tours MJ, 3,15 → 3,64 appels/tour ; référence `ressources` absente du cache.
  Faux refus sémantique sur la question du gardien et dette inversée restent hors lot,
  comme l'élision d'un nom public. Aucun changement de `planification.py` ni de `main`.
  [Cause, fonctions, mesures et limites](taches/rapport-codex-50-ressource.md).
  Fusionné sur l'intégration après les lots 46 à 49 : seul conflit `docs/etat-dev.md` ; aucun fichier de code commun.

- Branche `codex-une-source`, fusionnée, lot 46, base d'intégration `bafb9b9` (lot de coût) :
  une source de lumière portable de plus, qui n'apporte aucune capacité absente des sources déjà
  portées, n'ouvre aucun geste de la recherche (prendre, demander, acheter, saisir sur un porteur, faire
  remettre par une aide sur place), sauf si le but la vise. Capacité définie une fois sur ce que lisent
  les gestes de lumière (`Vue.capacite` : allumée, chargée, rechargeable de quelle substance, sans
  faute ; `Vue.couvre`, `Vue.doublon`) ; règle commune de `gestes` et `_aide_sur_place`, indépendante
  d'`emplois`, donc appliquée aussi par la référence de `VERIFIER` ; aucune lecture nouvelle hors de
  `_entrees`, aucun coût, prix, borne ni scénario changé. Recherches de la mine 1985 rejouées de 480 à
  570 : 180 recherches, 0 écart, nœuds −71 %. Empreintes 2 h contre `bafb9b9`, quatre scénarios ×
  quatre graines : identiques. 12 h, mine et auberge × 42/1985, tiré et fixe, `42bb9c0`, `bafb9b9` et
  la branche lancés ensemble : mine 2 462,6 → 1 625,1 s CPU (−34 %, encore ×1,55 contre `42bb9c0`),
  auberge 1 679,2 → 1 708,5 s (bruit) ; cinq nuits sur huit identiques recherches comprises, les trois
  autres divergent sur une recherche bornée de la base dont la branche rend exactement le résultat de
  la recherche complète (`REFERENCE`). `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine et auberge
  42 : sans écart ni borne. Cinq tests après rechargement (`test_une_source`). Suite complète unique,
  trois processus à priorité réduite : **1 730 tests, 16 ignorés**, verte, 1 192,7 s. Commits non
  signés (aucune clé configurée sur ce poste). Aucun appel à Luna.
  [Règle](plan-planificateur.md), [rapport, temps par tranche et limites](taches/rapport-codex-46-une-source.md).
  Fusionné sur l'intégration après les lots 47 à 49 : `planification.py` fusionné sans conflit avec la borne du lot 48
  (fonctions distinctes) ; conflits seulement dans la documentation.
  Accord : `test_borne_rester` (auberge 42 à 559) supposait la recherche sans borne plafonnée ; depuis le
  lot 46 elle trouve le plan de la recherche complète sous le plafond (la seconde lanterne doublait les états) :
  le test vérifie désormais que la borne rend ce même plan en moins d'états et que les deux mondes sont identiques.

- Branche `codex-audience`, fusionnée, lot **47 b**, base `e28df5c`, brief `d33e492` :
  décision de l'utilisateur du 24 octobre appliquée : nom/vocatif, groupe explicite,
  échange poursuivi, sinon celui d'en face ; égalité, le joueur précise ; sans
  interlocuteur perçu à portée de voix, cantonade et répondants acoustiques.
  Une seule décision dans `paroles.destinataires`, utilisée par la prévision et la
  préparation ; refus d'une proposition contraire avec `attendu` avant la revue.
  La contre-revue reste limitée aux mots et au contenu, sans « Précise à qui… »
  quand le moteur a fixé l'adresse. Aucun mot-clé de question collective ni nouvelle
  forme de groupe. Les anciennes scènes individuelles retrouvent leur saisie d'origine.
  Neuf tests `test_audience` couvrent le Relais réel (Aubin seul répond, les autres
  retiennent), l'auberge, la cantonade sans interlocuteur perçu, « à tous », vocatif,
  échange poursuivi, refus de contenu et intentions nominales, après rechargement.
  Ciblés : 234 tests, deux doubles de `test_luna_restes` adaptés puis 14 tests rejoués verts.
  Correctif signé SSH `f10f9d3`, signature vérifiée. La passe Luna révèle encore un refus
  d'audience déguisé en contenu : le dossier de revue est ensuite limité à `replique`,
  `contenu`, `sens_contenu`, sans adresse, auditeur ni effet ; sens typés indépendants
  de l'audience. **70 tests ciblés verts** sur ce contrat final ; « lui » et chuchotement
  sans personne perçue gardent leur refus, neuf tests d'audience verts.
  Luna, une passe, `main` `42bb9c0` lu du cache : 68 → 64 appels, 22 → 19 tours MJ,
  3,09 → 3,37 appels/tour ; aucun repli ni erreur technique/de recharge. `noms-dialogue` :
  question dite à Aubin, Aubin seul répond, six appels (faux refus de contenu puis correction).
  `soir-appel` : quatre appels puis « Précise ce que tu veux dire… », aucune parole enregistrée.
  Aucun « Précise à qui… ». Ces mesures précèdent le dossier final, sans seconde passe Luna ;
  absence de faux refus sémantiques non garantie.
  Campagne complète interrompue par le plantage du PC : 71 fichiers et 892 tests verts
  récupérés. Reprise des seuls 95 fichiers sans résultat : 845 tests verts, 79,8 s,
  trois processus à priorité réduite. Bilan consolidé : **166 fichiers validés,
  1 737 tests, 16 ignorés**, aucun échec ni erreur ; aucune seconde suite complète.
  [Rapport, section 47 b](taches/rapport-codex-47-audience.md#47-b--celui-den-face-redevient-le-défaut).
  Passe Luna sur le code final (15c85da, une passe, `artifacts/luna-47b-final/` du dépôt principal) :
  3,37 → 3,05 appels/tour, aucun repli ni « Précise à qui… » ; paroles sans nom à celui d'en face.
  Reste un faux refus affiché, hors audience : « est-ce que quelqu'un a du bois ? » finit sur « Précise ce
  que tu veux dire… » (le moteur n'accepte que `faim`/`chaleur` comme sujet de `ressource`, la contre-revue
  refuse `chaleur` pour « bois »). Fusionné sur l'intégration après les lots 45, 48 et 49 : seul conflit
  `docs/etat-dev.md` ; aucun fichier de code commun.

- Branche `codex-audience`, remplacé par 47 b, lot 47, base d'intégration `60da18c`
  (brief `d22190d`, **règle d’adresse remplacée par le lot 47 b ci-dessus**) : `destinataires` fixe une seule adresse, partagée par la prévision et la
  validation sur copie. Sans nom, groupe ou échange à poursuivre, la parole à voix haute
  va à la cantonade même avec quelqu'un en face. Un pronom individuel sans antécédent
  et le chuchotement gardent le regard ; une cible nominale d'intention racontée est
  conservée sans forcer le mode parole. Aucun choix d'audience libre de Luna ; revue des
  mots et du contenu seule, refus d'adresse déterministe avec `attendu` avant elle.
  Correctif signé SSH `2100c41`, signature vérifiée. Six tests nouveaux : Relais réel,
  auberge, voix audible, adresse individuelle refusée puis corrigée, contenu contraire,
  formes sans question et restitution/achat nommés ; sauvegarde et rendu contrôlés.
  Luna, une passe des quatre scripts prescrits, référence `main` `42bb9c0` en cache :
  68 → 63 appels, 22 → 19 tours MJ, 3,09 → 3,32 appels/tour ; aucun repli ou défaut
  technique/de recharge. La question du bois est dite telle quelle à la cantonade,
  quatre répondants, quatre appels dans les deux scripts, sans clarification d'audience.
  Cette passe précède le dernier correctif d'analyse des intentions nominales : les
  propositions initiales de restitution et d'achat qui y furent refusées sont rejouées
  avec MJ simulé sur le code final, restitution et refus individuel d’achat vérifiés après recharge.
  Suite complète unique, trois processus à priorité réduite : 1 733 tests, 16 ignorés,
  1 488,9 s ; six échecs et douze erreurs initiaux (anciennes adresses implicites,
  désignations tronquées). Après corrections et reprises ciblées : **166 fichiers validés,
  1 734 tests couverts, 16 ignorés**, aucun défaut restant ; pas de seconde suite complète.
  Reconnaissance syntaxique bornée, contenu encore sémantique ; aucune seconde passe Luna.
  Aucun changement de scénario, de `deliberation.py` ou `echanges.py` ni de `planification.py` ;
  `main` non touchée. [Rapport du lot 47](taches/rapport-codex-47-audience.md).
- Branche `codex-borne-rester`, fusionnée, lot 48, base **3aba83b**, code signé **970d6f5** :
  borne admissible et cohérente du séjour final (`Vue.borne_rester`, `_explorer_etats`) :
  `RESTER × min(gardes laissées ailleurs + eau)` sur les sorties relaxées, sans noir ni compagnie ;
  constante pendant la recherche, nulle pendant la découverte de lumière. Coûts et rang historique
  conservés, même lors d'arrondis ; graphes et certificat restent indépendants de ce tri.
  **Contrat précisé par l'utilisateur le 2026-10-24** : mêmes décisions quand la référence uniforme
  ne plafonne pas ; si elle plafonne, autre résultat permis seulement au coût de la complète
  (`REFERENCE`, 60 000 nœuds), ou aucun plan si elle n'en trouve pas. `VERIFIER` le contrôle et
  relève ces cas dans `BORNES` (`ancienne_borne=True`). Premières divergences des nuits longues :
  Lucien, auberge 42 min 559, `garder:grenier`, aucun plan à 4 000 avant, plan à 78 avec H,
  complète identique à 5 759 (coût 78,92250378787878) ; auberge 1985 min 486, `garder:etable`,
  aucun plan à 4 000 avant, rester à 102 avec H, complète identique à 4 180 (coût 90).
  Les deux mines sont entièrement identiques sur 12 h ; 16 empreintes de 2 h identiques.
  Contrôles `VERIFIER` + perception à 1, mine/auberge 42, 2 h : sans écart ni borne.
  Huit tests nouveaux, état et rendu après recharge ; onze ciblés verts ; suite finale unique :
  **1 742 tests, quatre ignorés, aucun échec**, 736,2 s, trois processus à priorité réduite.
  Sur la capture de Lucien à 480 min : 3 688→663 états, même résultat et monde.
  Trois versions lancées ensemble, priorité réduite : CPU moyen ancien/base/branche sur 12 h,
  mine **69,52 / 300,27 / 300,76 s**, auberge **62,62 / 195,24 / 216,61 s**.
  **Pas de gain global** (991,01→1 034,72 s, +4,4 %) : auberge 1985 −22,6 %, auberge 42 +38,8 %,
  après bifurcation autorisée ; le coût de la mine reste ouvert. Aucune violation, usurpation ni
  nouvelle boucle persistante relevée ; les nuits divergentes ne sont plus comparées pas à pas.
  Preuve, deux captures, résultats complets, tranches et limites dans le
  [rapport du lot 48](taches/rapport-codex-48-borne-rester.md). Aucun appel au modèle, `main` non touchée.
  Fusionné sur l'intégration après le lot 49 : seul conflit `docs/etat-dev.md` ; aucun fichier de code commun.

- Branche `codex-devis-vides`, fusionnée, lot 49, base moteur `3aba83b` :
  un certificat nécessaire d'allumage dans `part_estimee` écarte les sources sans
  voie de flamme, après leur accès et avant `_preparer`. Croyances, permissions,
  refus, budget et routes communs ; cache local par état complet et source,
  lectures déjà dans `_entrees`, découverte de lumière conservée. Capture auberge
  1985, 480–540 : 834 préparations sur 6 182 évitées ; 70 devis entièrement sans
  préparatif sur 2 025 vides. Les 1 955 autres devis vides restent calculés :
  aucune prétention à les éliminer tous ni à résoudre le coût des bancs.
  Empreintes 2 h, quatre scénarios × quatre graines : identiques ; quatre nuits
  de 12 h, `comparer --calcul` : mêmes mondes et résultats de recherche, mêmes
  nœuds. CPU moyen base → branche : mine 301,03 → 297,68 s (−1,1 %), auberge
  182,90 → 178,77 s (−2,3 %), auberge 1985 +0,7 %. Ancien/base/branche mesurés
  ensemble, quatre nuits au plus. `VERIFIER` et spatial 1, mine/auberge 42, 2 h :
  aucun écart ni borne, aucune usurpation.
  Suite complète unique : **1 737 tests, quatre ignorés**, verte, 167 fichiers,
  trois processus à priorité réduite, 781,4 s. Trois nouveaux tests contrôlent les
  captures, l'absence de flamme et les suites valables après recharge et rendu.
  Aucun prix, plafond, scénario, fichier réservé ou appel au modèle modifié.
  Bilan de validation dans le [rapport du lot 49](taches/rapport-codex-49-devis-vides.md).

- Branche `codex-proposer-recours`, fusionnée, lot 45, base **bafb9b9**, code signé
  **2cb8220** : les PNJ proposent « faute de mieux », après une demande d'objet/part refusée
  ou avant la faute du plan retenu, sans geste nouveau dans la recherche. Pièces et biens/parts
  possédés et portés ; chance estimée depuis les croyances du proposant, évaluation réelle
  commune au joueur. Déclencheur et tentatives sauvegardés par lésé/besoin ; pas de réessai par
  le simple délai. Validation depuis les connaissances du proposant, publication atomique
  préservant les références moteur. Les parts remises sont attendues auprès du demandeur,
  distinctement des parts servies au lot ; la réception garde l'identité du lot. Six tests ciblés
  après recharge, dont Brune/Gorm en crue et Odon/Mathe dans la mine, même laps découpé.
  Banc rapide quatre scénarios × quatre graines × 4 h : aucun plantage, violation ou usurpation ;
  propositions/acceptées 1,25/1,25, 4,25/1,75, 2/0,75, 3,25/0 (Relais/mine/auberge/crue), vols
  tentés 1,5 → 0, 0,5 → 0,25, 0 → 0, 2,25 → 2. CPU sans cache, versions ensemble, 42/1985 :
  mine −2,0 %, auberge +7,0 %, ensemble +2,1 % : plafond +5 % par scénario non atteint à l'auberge.
  Tâches promises en contrepartie, réparation, intermédiaires et passage restent à faire ; le
  forcement se négocie pour le bien mobile visé, pas pour la seule ouverture d'un bien fixe.
  Suite complète finale : 1 731 tests, 4 ignorés, 614,3 s ; deux scènes de test corrigées puis
  leurs fichiers repris en entier (30 tests verts), bilan consolidé vert. Une première suite
  a précédé le correctif d'attente des parts ; le lot dépasse 45 min, vérification comprise.
  Voir le [rapport du lot 45](taches/rapport-codex-45-proposer-recours.md).
  Fusionné sur l'intégration après le lot 44 : seul conflit `docs/etat-dev.md` ; aucun fichier de code commun.

- Branche `codex-geste-hors-portee`, fusionnée, base d'intégration `cd7195d`, lot 44 :
  une approche d'improvisation n'accorde plus de portée physique ; toutes ses cibles passent
  par `proximite.exiger`, comme le passage d'un obstacle. Le dossier des passages prépare
  les cibles désignables par le moteur, rotation simulée comprise. L'opération reste connue
  hors de vue et en souvenir ; le refus de type d'échelle oriente vers `passer_obstacle`,
  la contre-revue exige l'effet d'un déplacement. Le joueur se rapproche par ses pas :
  à distance, refus commun « Approche-toi… » avec `attendu`, aucune fiche de jet abstraite.
  Trois nouveaux tests, console/MJ simulé/recharge, Relais et auberge, cinq approches,
  contexte du cas historique, puis fiche et passage après rapprochement ; ciblés verts.
  Correctif signé SSH `b758341`, signature vérifiée. Banc rapide Relais/auberge, 4 h × quatre
  graines contre `cd7195d` : chroniques, mesures, récits, souvenirs et empreintes identiques,
  aucun plantage, violation ou usurpation, constats inchangés. Luna, une passe, neuf scripts :
  71 appels / 29 tours MJ, aucun repli, obstacle narratif, défaut technique ou de recharge.
  Référence `main` en cache : Relais 3,00 → 2,63 appels/tour, atelier 3,91 → 2,82 ; obstacles
  absents du cache, aucun rejeu de référence. Relais n° 20 : `passer_obstacle` du premier coup,
  refus « Approche-toi… » en un appel ; n° 21 : refus de portée en quatre appels, état inchangé.
  Campagne complète appelée une fois, trois processus à priorité réduite : **164 fichiers validés,
  1 723 tests couverts, 16 ignorés** après reprises ciblées. Exécution initiale : 1 692 décomptés,
  1 833,6 s ; une ancienne attente de fiche à distance corrigée (19 tests rejoués verts), deux
  erreurs web de sockets interdites (huit tests hors restriction verts), deux workers TUI bloqués
  sans calcul dans le bac à sable, arrêtés seuls puis rejoués hors restriction (33 tests verts,
  186,2 s). Les deux interruptions sont chacune comptées pour un test dans les 1 692 ; aucune
  seconde suite complète. [Rapport du lot 44](taches/rapport-codex-44-geste-hors-portee.md).
  Aucun scénario ni fichier réservé au lot 43 modifié ; `main` inchangée.
  Fusionné sur l'intégration après le lot 43 : seul conflit `docs/etat-dev.md` ; aucun fichier de code commun.

- Branche `codex-gardien-detresse`, fusionnée, lot 43, base `dd36155` :
  un besoin sans recours ouvre l'aide auprès de sa charge : demander l'allumage
  d'une source locale ou la remise d'un moyen utile, avec les tâches communes et
  leur réalisation réelle ; aucun effet à l'acceptation. Promesse attendue dans
  l'esprit du demandeur, sans lecture de l'agenda privé de l'autre ; entrées de
  recherche complètes. Les autres besoins bloqués peuvent aussi appeler une fois
  par épisode, sans modifier garde, seuils ni `REPIT`. Sur la base mine 42, Bram
  appelait déjà à 462, révisait le lieu d'Odon et savait les biscuits épuisés à 139.
  La branche ajoute sa demande d'allumage à Gaspard à 500 (impossible), puis son
  appel pour la faim à 638, au bureau ; sécurité 100 et faim 78 encore à la fin.
  Cinq tests nouveaux, monde complet et rendu utile après recharge et laps découpé,
  dont allumage, nourriture remise puis mangée, autre gardien et promesse sans
  effet anticipé ni lecture privée. Rapide 4 h, mine/auberge × quatre graines :
  aucun plantage, violation ou usurpation ; un appel de plus en auberge 2024,
  noir 165 → 170, aucune nouvelle bascule ni alerte d'audit. Audit mine 42 de 12 h :
  attente 1 250 → 1 245 min·PNJ ; les excursions antérieures restent possibles.
  `VERIFIER` et `spatial.VERIFICATION=1`, mine 42, 2 h : sans écart ni borne.
  Suite complète unique : **1 720 tests, quatre ignorés**, verte, trois processus
  à priorité réduite, 636,9 s ; cinq tests du lot et douze tests d'échanges revérifiés.
  Aucun appel au MJ ni changement de ses fichiers réservés au lot 42.
  [Règle](plan-planificateur.md), [rapport et limites](taches/rapport-codex-43-gardien-detresse.md).
  Fusionné sur l'intégration après le lot 42 : seul conflit `docs/etat-dev.md` ; aucun fichier de code commun.

- Branche `codex-fouille-faits`, fusionnée, base d'intégration `de74ec1`, lot 42 :
  correctif signé SSH `5502858`, signature vérifiée ;
  la revue de portée reçoit demande et transaction entière ; chaque ajout, avec ou sans
  prose, est jugé sur la perception qu'il remplace et l'indice qu'il crée, même sans quête.
  Refus séparés avec `attendu` vers les perceptions du moteur ; rapport incomplet bloquant.
  Le rendu d'un détail ne juxtapose plus son nom et son support. Cinq nouveaux tests
  console/MJ simulé/recharge, Relais et atelier, avec et sans suite, qualification sans prose,
  indice hors quête et ambiance légitime. Suite complète unique, trois processus à priorité
  réduite : **1 714 tests, 16 ignorés, 1 313,6 s** ; deux erreurs d'un ancien double de parole
  omettant le nouveau jugement, corrigé puis ses 19 tests rejoués seuls, verts (54,9 s).
  **162 fichiers validés après correction**, pas de seconde suite complète.
  Luna, une passe relais/crypte/atelier/luna-restes-ambiance, `main` `42bb9c0` lu du cache :
  106 → 86 appels, 3,31 → 2,77 appels/tour, replis 1 → 0, aucune erreur technique ou recharge.
  Relais n° 5 : `examiner antichambre_sol`, deux appels, « Le sol en pierre. », aucun détail
  inventé. **Limites** : détection sémantique ; pas de mécanique dédiée aux empreintes ;
  cause du premier choix probabiliste non isolée, dérive de correction démontrée par les fils.
  Aucun fichier réservé au lot 41 ni scénario modifié ; `main` inchangée.
  [Rapport du lot 42](taches/rapport-codex-42-fouille-faits.md).
  Fusionné sur l'intégration après le lot 41 : seul conflit `docs/etat-dev.md` ; aucun fichier de code commun.

- Branche `codex-route-admissible`, fusionnée, lot 41, base `750837a` :
  `route_admissible.refus` juge la route crue salle par salle et porte par porte ;
  recherche et marche l'emploient. Traversée au temps cumulé, séjour à son horizon,
  retour ou évacuation par le même parcours projeté, portes certaines et durées comprises.
  Une porte incertaine exige un repli immédiat possible ; clés et ouvertures acquises comptent.
  `eau.en_peril` conserve une traversée en cours si la même règle prouve sa sortie avant
  la noyade : la minute ronde ne la change pas en séjour. Prévision affine et durées dans
  `_entrees` ; borne terminale du lot 38 toujours admissible (aucun coût minoré réduit).
  Six tests : captures du lot 39 arrivées au sec, traversée en cours, passage trop long,
  porte incertaine/repli, état et rendu identiques après recharge et découpage ; test
  historique du détour adapté à une coupure pendant le passage. Le test des ressources
  suit Brune, qui consomme une planche pour rallumer le poêle, sans bois créé.
  Banc rapide 4 h, crue/Relais × quatre graines, contre `750837a` : zéro plantage,
  violation ou usurpation ; Relais identique ; crue sans recours 75 → 60, eau 110 → 98,75,
  maximum horaire moyen des passages 17 → 12,75 (pire 32 → 14). Une fermeture de réserve
  et une enquête isolée de plus en crue 7, aucune nouvelle boucle observée. CPU final,
  paire sans cache crue 1985, 4 h, un processus : 10,31 → 12,06 s (+17 %, nuits divergentes).
  Audit 12 h, crue 500/42 : eau 815/285, sans recours 60/185, « eau longue » 3/0,
  aucun plantage ou usurpation. Archives `verif-integ-ffcc295` absentes de ce poste :
  comparaison aux chiffres historiques de 500 seulement, pas aux deux nuits complètes.
  `VERIFIER` + `spatial.VERIFICATION=1`, 2 h, crue 42/500 : aucun écart ni borne.
  Suite finale : **1 713 tests, quatre ignorés**, verte (3 processus, priorité réduite,
  563,8 s) ; les six tests du lot repassent après le dernier contrôle du départ du retour,
  sans changement des chroniques ni mesures du rapide.
  Ni baisse uniforme de l'eau ni fin générale des boucles garantie. Aucun appel au MJ.
  [Règle](plan-crue.md), [rapport du lot 41](taches/rapport-codex-41-route-admissible.md).
  Fusionné sur l'intégration après le lot 40 : seul conflit `docs/etat-dev.md` ; aucun fichier de code commun.

- Branche `codex-absence-vue`, fusionnée, base `8443458`, lot 40 : la vue courante
  donne `perception.objets_visibles`, limitée aux objets `visible=true`, en références publiques.
  L'audit admet une absence dans cette vue avec la source `perception` ; un résultat de fouille,
  d'écoute derrière une porte ou d'examen caché exige toujours une perception exécutée. Aucun
  changement du prompt d'interprétation ni des fichiers réservés au lot 38. Correctif signé
  `c5f0b77`, signature SSH vérifiée. Console/MJ simulé/recharge : atelier 9 et 12, antichambre,
  porte, coffre fermé, noir ; état et texte sauvegardé contrôlés, tests du lot 34 conservés.
  Ciblés **55 tests verts** ; suite complète unique (`tools/tests.py --processus 3`) :
  **1 704 tests, 16 ignorés, aucun échec ni erreur**, 1 291,2 s à priorité réduite.
  Empreintes Relais 2 h × 4 graines identiques à la base (référence manquante calculée et cachée).
  Luna, une seule passe atelier/crypte/luna-restes-ambiance/signes-noir, `main` lu du cache :
  86 → 66 appels, 3,44 → 2,75 appels/tour, replis 1 → 0, aucun défaut technique ou de recharge.
  Zéro refus d'absence visible comme `invention_protegee` ; écoute exécutée en deux appels,
  trois minutes enregistrées. **Limite** : atelier 9 et 12 restent à six et quatre appels
  (voix d'auteur et contradictions sémantiques, dont pierre/sol) ; pas de garantie générale du
  classement. Un commentaire de preuve subsiste dans l'ambiance. Pas de conclusion de vitesse
  depuis le cache. [Rapport du lot 40](taches/rapport-codex-40-absence-vue.md).

- Branche `codex-refuge-mouille`, **fusionnée**, base `63a717c`, lot 39 :
  Fusionné sur l'intégration après les lots 38 et 39 : seul conflit `docs/etat-dev.md` ; aucun fichier de code
  commun (`mj`, `narration` contre `planification`, `part_estimee`, `perception`, `obstacles`, `trajet_estime`).

- Branche `codex-cout-12h`, fusionnée, base moteur `63a717c` (brief `17164f8`), lot 38 :
  mêmes décisions sur les nuits contrôlées, trois leviers de calcul. Une borne admissible sur les
  suites terminales diffère leur devis ; rang historique des égalités réservé, normalisation commune
  des gestes, découverte de lumière au même point, certificat d'absence conservateur devant une suite
  inconnue. La borne reste nulle sur les états ordinaires : ce n'est pas une heuristique positive
  générale sur tous les buts. Parts par état complet, besoin de combustible et attente du donneur par
  leurs entrées exactes, devis partagé entre lots de même compatibilité ; imports chauds au module ou
  par référence gardée. Aucun coût, prix, plafond de nœuds, scénario ni consigne du MJ modifié.
  Cinq tests nouveaux (mine et auberge : moins d'états internes de devis, même plan, monde et rendu
  après recharge ; égalités et plafond ; filtres des devis ; cache exact ; certificat réel).
  Suite complète unique : **1 707 tests, quatre ignorés**, verte, trois processus à priorité réduite,
  688,6 s ; les cinq tests du lot repassent après ajout du compte des états de devis.
  Empreintes 2 h, quatre scénarios × quatre graines, contre `63a717c` : identiques.
  `VERIFIER` + `spatial.VERIFICATION=1`, 2 h, mine/auberge 42 : sans écart ni borne.
  Quatre nuits de 12 h, mine/auberge × 42/1985 : état complet, chronique, mesures, récit, souvenirs
  et tous les résultats des recherches strictement identiques à la base (`--calcul`), nœuds et
  recherches bornées également identiques. Trois versions lancées ensemble, deux processus chacune :
  CPU moyen ancien/base/branche, mine **82,7 / 311,6 / 248,7 s**, auberge **75,0 / 274,9 / 232,1 s** ;
  **−20,2 % / −15,6 %** contre la base, encore **×3,01 / ×3,09** contre `42bb9c0`.
  Leviers isolés, 12 h, 1985, mine/auberge : borne **3,88 % / −0,04 %**, puis cache **1,89 % / 2,14 %**,
  puis imports **15,63 % / 12,07 %** ; mêmes résultats des recherches à chaque étape.
  **Visée ×1,5 non atteinte** : la recherche reste dominante en fin de nuit, sans retrait d'états
  ordinaires ni modification de leur borne. Mesures par levier, tranches et profil dans le
  [rapport du lot 38](taches/rapport-codex-38-cout-12h.md), bruts `artifacts/codex-38/` du worktree.
  Aucun appel au modèle.
  Fusionné sur l'intégration après le lot 39 (diagnostic sans code du jeu) : seul conflit `docs/etat-dev.md`,
  aucun fichier de code commun depuis 63a717c.

- Branche `codex-refuge-mouille`, fusionnée (diagnostic seul), base `63a717c`, lot 39 :
  **diagnostic seul, conformément au point d'arrêt du brief** (cause dans les trajets réservés
  au lot 38). Crue 500, même joueur passif que l'audit : Aubin choisit la galerie à 156 min,
  Brune le poêle à 160, mais la marche refuse leurs salles intermédiaires attendues noyées ;
  le planificateur ne contrôle que la destination. À 182, la conduite réellement noyée coupe
  aussi la recherche ; Ilse ne tente son recours au froid qu'à 360, Aubin à 404. Aucun répit
  de chaleur ou de sécurité ni refus social n'explique le premier blocage. Route estimée
  0,789 min, eau attendue avec un horizon de 60 min : contrat de traversée/séjour à reprendre
  ensemble dans `Vue.descente`, `Vue.route`, `trajet_estime.parcours` et `pnj._marcher`.
  Rejeu de 12 h : empreintes identiques à la nuit `ffcc295` conservée, mesures de jeu identiques
  (865 minutes·PNJ dans l'eau, 495 sans recours, 1 100 en attente, zéro usurpation/écart).
  Deux captures livrées (crue 500 à 160 ; scène d'auteur à 100), diagnostic reproductible par
  `tools/diagnostic_refuge_mouille.py` : plans trouvés, marche impossible, monde et rendu identiques
  après sauvegarde/recharge et vingt minutes en un bloc ou par minutes. Test historique du détour
  dangereux vert (deux personnes). Aucun code du jeu ni fichier réservé modifié ; invariant
  **non garanti**, pas de correctif revendiqué. Pas de banc comparatif ni suite complète relancés
  pour cette livraison de diagnostic. [Rapport du lot 39](taches/rapport-codex-39-refuge-mouille.md).
  Bruts : `artifacts/codex-39/` du worktree.

- Branche `codex-chercher-appeler`, fusionnée, base `da13f9d`, lot 37 : les lieux
  cherchés en vain restent écartés jusqu'à un nouvel indice local ; ni une absence, ni le
  temps, ni une recharge ne réactivent la tournée. Réouverture commune par la croyance de
  lieu ou un bruit nouveau, joueur cherché compris ; migration des souvenirs réservée aux
  sauvegardes sans registre. `planification.py` et Luna inchangés. Code signé SSH `222f3cf`.
  Six tests nouveaux : scènes crue 3 à 120 et mine 7 à 469, même état et même rendu après
  recharge et laps découpé ; autres cas : voix, bruit, absence et délai, joueur, retrouvailles.
  Banc 4 h contre `da13f9d`, quatre scénarios × quatre graines : mesures identiques pour
  les seize nuits, zéro violation, usurpation ou plantage. Audit 12 h, crue 3 et mine 7, contre
  les nuits `ffcc295` conservées : appels 11 → 9 et 23 → 19 ; passages/h 21,5 → 19,5 et
  20,33 → 18,25 ; aucune nouvelle alerte de boucle. Brune appelle trois fois au lieu de dix
  avant de retrouver Gorm ; Odon rappelle seulement après les nouveaux bruits des lieux.
  **Limites** : « appels nombreux » d'Odon subsiste (20 → 15) ; dans la crue, sans recours
  60 → 240 minutes cumulées, deux observations d'eau longue nouvelles. Aucun gain uniforme
  des besoins promis. Bilan consolidé : **1 694 tests, 16 ignorés**, zéro échec restant.
  Suite lancée une fois, trois processus, 1 743,6 s ; deux erreurs Web et deux fichiers TUI
  bloqués dans le bac à sable, seules reprises des trois fichiers hors bac à sable : 41 tests verts.
  [Rapport du lot 37](taches/rapport-codex-37-chercher-appeler.md), bruts `artifacts/codex-37/`
  du worktree ; priorité réduite, quatre processus de calcul au plus, aucun appel au modèle.
  Fusionné sur l'intégration après les lots 34 et 35 : seul conflit `docs/etat-dev.md` ; aucun fichier de code
  commun (`deliberation`, `esprits`, `ouie` contre `moteur`, `mj`, `narration`, `signes`, `social`).

- **Fusions des lots 34 et 35 sur l'intégration** (77473f9, base 1f1ea43 ; sans Luna) : `codex-perception-geste`
  (ccc517a) puis `codex-soi-meme` (77473f9), seul conflit `docs/etat-dev.md`. Fichier de code commun : `moteur.py`
  seul (lot 34 contre la vue mémorisée de la transaction), hunks disjoints qui s'accordent ; le lot 35 (`signes`,
  `social`) ne croise rien. Tests des lots et `test_question_absent`, `test_nom_non_relie`, `test_signes` : 45 tests,
  verts. `comparer_bancs --empreintes` contre 1f1ea43, 2 h, Relais et crue × 1985, 7, 42, 2024 : Relais identique ;
  crue 1985, 7 et 42 : empreintes d'état, chronique et mesures identiques, récit et souvenirs différents par le
  seul champ `aveu: false` des rumeurs reçues par `social.bavarder` (désormais via `social.recevoir`) et leur
  `preuve` qui en dépend (première divergence de l'état final, crue 1985, minute 25) ; aucun écart de jeu à 2 h
  (le jet de moins du rapport est à 203 min). Suite complète une fois (`tools/tests.py --processus 4`) :
  **1 696 tests, 16 sautés**, verte (1 015,5 s), sans reprise hors bac à sable.

- **Fusions des lots 31 et 32 sur l'intégration** (da13f9d, base 41c1c7c ; sans Luna) : `codex-cout-exact` (f4e95fd)
  puis `codex-question-absent` (da13f9d), seul conflit `docs/etat-dev.md`. `comparer_bancs --empreintes` contre
  41c1c7c, 2 h, quatre scénarios × 1985, 7, 42, 2024 : chronique, mesures et état final complet identiques nuit par
  nuit. Tests des lots (`test_trajet_estime`, `test_vue_action`, `test_question_absent`, `test_repli_et_appel`,
  `test_propositions`) : 37 tests, un saut, verts. Suite complète une fois (`tools/tests.py --processus 4`) :
  **1 688 tests, 16 sautés**, verte (981,5 s). **Coût sur 12 h**, `main` 42bb9c0 et l'intégration da13f9d lancés
  ensemble (deux nuits à la fois par version, priorité réduite, `banc_pnj.nuit` avec diagnostic, temps processeur
  relevé à chaque heure), joueur passif comme `empreintes_nuits.py` : par nuit, mine 42 184,5 → 655,5 s (×3,55),
  mine 1985 163,9 → 718,2 s (×4,38), auberge 42 157,5 → 617,2 s (×3,92), auberge 1985 143,5 → 477,8 s (×3,33).
  Par tranche de 4 h (0-4 / 4-8 / 8-12 h) : mine 42 ×1,26 / ×3,3 / ×3,9 ; mine 1985 ×1,32 / ×5,7 / ×4,3 ; auberge 42
  ×1,47 / ×2,3 / ×4,5 ; auberge 1985 ×1,30 / ×2,6 / ×3,7 : le surcoût **croît avec la durée de la nuit**, ce que
  les mesures de 4 h des lots (×1,28 / ×1,55) ne voyaient pas. Presque tout est dans les recherches du
  planificateur : en fin de nuit, mine Rémy `faim` (42 : 40 → 379 s, 0,68 → 1,12 M nœuds ; 1985 : 32 → 262 s,
  0,27 → 1,27 M nœuds, bornées 0 → 319) et Josse `feu:poele` ; auberge Tilo et Joss `faim` (42 : 11 → 234 s et
  20 → 212 s), Mireille `feu:fourneau` (1985 : 9 → 154 s pour 3 167 nœuds), Lucien `garder` et `placer:ballot`.
  Deux causes cumulées : plus d'états développés par recherche et chaque état plus cher. Profil (cProfile, auberge
  1985, 8 h-9 h, même fenêtre des deux côtés ; nuits différentes) : 117 → 328 explorations, 4 443 → 110 303 états
  développés (38 → 336 par exploration), 1,2 → 4 ms par état ; `gestes` → `_parts` → `_parts_remises` 52 % du
  temps, dont le devis `part_estimee.suites` / `_preparer` 31 % ; `_plan_garder` 44 %. Mine 1985, 7 h-7 h 30 :
  `_parts_remises` 27 %, devis 12 %, `route`/`prix_route` 11 %, et 7 % dans des `from . import` locaux de
  fonctions chaudes (`_mesurer`, `obstacles.sejours_route`, `perception.substance`, `Vue.arrivee`, `prix_route`,
  `route` : 6,3 M appels d'`importlib._bootstrap.parent`). Bruts : `artifacts/cout-12h/` du worktree d'intégration (nuits et profils).

- Branche `codex-soi-meme`, fusionnée, base `41c1c7c` (brief `2a96b84`),
  correctif signé SSH `8fa071f` : les accusations directes de `social.bavarder` passent par
  `social.recevoir`, comme celles entendues par un tiers. L'accusé ne reçoit plus une rumeur sur
  lui qu'il pourrait répéter ; les anciennes nouvelles contre soi sont écartées, le contenu
  `aveu` reste la voie explicite pour accuser son locuteur. Aucun choix autonome d'aveu ajouté
  aux PNJ. La perception et la lecture des signes excluent l'observateur lui-même.
  Cause reproduite en crue 2024 (421) et 7 (373 puis 391), avec le placement de l'audit : Aubin
  accuse Brune, qui répète vraiment ; aucun défaut d'attribution du récit ni lecture de ses
  propres signes à l'origine. Quatre tests nouveaux après recharge, quatorze sous-cas ;
  58 tests ciblés verts, puis le fichier enrichi revérifié. Deux captures réelles reprises sur
  quinze minutes et rechargées sans auto-accusation retransmise. Banc rapide 4 h, crue/Relais,
  quatre graines, contre `41c1c7c` : aucun plantage ni usurpation, constats d'audit inchangés ;
  seul écart de jeu : un jet de persuasion et une rumeur doutée en moins (crue 1985, Gorm accuse
  Brune à 203). Suite complète unique, trois processus à priorité réduite, 2 207,3 s :
  deux erreurs de socket Web et deux fichiers TUI bloqués dans le bac à sable ; seules reprises
  hors bac à sable, Web 8 tests et TUI 33 tests, vertes. **Bilan consolidé : 1 680 tests,
  16 ignorés, aucun échec restant**, 156 fichiers. Aucun Luna.
  Anciennes traces et effets historiques conservés ; pas de garantie sémantique sur toute prose.
  [Rapport du lot 35](taches/rapport-codex-35-soi-meme.md), bruts `artifacts/codex-35/` du worktree.
  Fusionné sur l'intégration après le lot 34 : seul conflit `docs/etat-dev.md` ; aucun fichier de code
  commun avec l'intégration depuis 41c1c7c (`signes.py`, `social.py` intouchés de ce côté).

- **Vérification d'intégration ffcc295** (lots Q, R, A0, A1, cache, 25 à 30 ; sans Luna ; bruts dans
  `artifacts/verif-integ-ffcc295/` du dépôt principal). Audit 12 h (`tools/audit_nuits.py`), quatre
  scénarios × 1985, 7, 42, 2024, 3, 11, 99, 500, contre `main` 42bb9c0 (référence complétée dans
  `artifacts/references/42bb9c0/audit-12h/`) : aucun plantage, violation ni usurpation, dans les deux.
  Par nuit, 42bb9c0 → ffcc295 : sans recours Relais 206 → 193, mine 23 → 44, auberge 188 → 183, crue 141 → 217 ;
  en attente 131 → 250, 1 400 → 1 350, 462 → 382, 499 → 473 ; noir 199 → 194, 1 413 → 1 310, 1 014 → 849,
  64 → 98 ; dans l'eau (crue) 229 → 348, constats « eau longue » 2 → 4 ; appels à l'aide 2 → 0,5, 2 → 2,25,
  1,25 → 1,4, 0,75 → 1 ; appels (héler) 0,5 → 1, 5,3 → 10,5, 17,5 → 16,8, 2,4 → 4,8 ; bascules ≤ 3 partout ;
  passages par heure, pire : Relais **165 → 10**, mine 17 → 24, auberge 28 → 30, crue 36 → 32. **Fuite ↔ sécurité**
  (Relais 2024, Ilse) : absente, mais la violence qui la déclenchait (Aubin assomme Brune) n'a plus lieu
  dans cette nuit : non prouvée corrigée. **Faim ↔ eau** (crue 2024, Brune) : absente sur 42bb9c0 comme sur
  ffcc295 (Brune mange par une part de Gorm à 365) ; non prouvée corrigée non plus. `rixe` et `rixe_douce`,
  8 h, 1985, 7, 42, 2024 : aucun coup contre une personne, aucun mort ni usurpation (Aubin force la réserve,
  rixe 1985 à 422). `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, Relais, mine, auberge, crue,
  `rixe` : sans écart ; recherches bornées : mine 4 (Josse `feu:poele`), autres 0. Bram (mine 42, 12 h) :
  quand biens et sécurité pressent ensemble, il garde ses biens au bureau dans le noir (58 relevés de
  5 min, sécurité 100 et faim 78 à 710-720), comme sur 42bb9c0 (50) ; l'arbitrage n'est pas tranché.
  Temps par nuit (horloge, quatre nuits ensemble, non lancés ensemble ; indicatif) : Relais 44,5 → 118,4 s,
  mine 238 → 711 s, auberge 206 → 739 s, crue 56 → 100 s (×1,8 à ×3,6 sur 12 h) ; `rixe` 8 h 98 s,
  `rixe_douce` 49 s. Défauts relevés, à prendre en petits lots : (1) **chercher en appelant** : Brune
  (crue 3, 121-128) hèle « Gorm ? » dix fois en courant refuge ↔ conduite ↔ vannes ↔ galerie, puis crochète
  la réserve ; Odon (mine 7, 470-474) « Mathe ? » huit fois en repassant quatre fois par le baraquement ;
  appels doublés à la mine et à la crue ; (2) **crue 500** : Brune, Ilse et Aubin restent 235 min au refuge
  mouillé (1 à 14 cm), chaleur 73 à 100 sans recours, la faim renoncée entre eux, alors que sur 42bb9c0
  Brune et Ilse gagnent la galerie vers 300 ; d'où l'eau et le « sans recours » de la crue ; (3) un PNJ se
  dénonce lui-même : « Brune dit à Gorm que Brune porte les planches de bac, qui n'est pas à elle » (crue
  2024, 421 ; aussi sur 42bb9c0, Relais 3 et crue 2024), « Brune dit à Ilse que Brune semble guetter la
  réserve » (crue 7, 391) ; (4) le temps de calcul sur 12 h (mine et auberge ×3 à ×3,6).
- Branche `codex-perception-geste`, fusionnée, base d'intégration `ffcc295`
  (brief `159faff`, correctif signé SSH `b0d5f02`, signature vérifiée) : perceptions déclarées
  par le moteur, opération/cible dans la contre-revue ; un geste corrigé peut produire
  seulement une perception. Rendu direct du résultat moteur après sauvegarde. L'audit distingue
  résultat positif/négatif de perception active et ambiance libre ; classement et fidélité
  restent sémantiques. Quatre tests nouveaux après recharge ; 104 tests ciblés finaux verts,
  trois ignorés.
  Suite complète unique, trois processus à priorité réduite, 1 775,9 s : quatre erreurs
  d'environnement (deux processus TUI bloqués puis arrêtés, deux sockets web refusés).
  Reprises des seuls fichiers d'interface hors bac à sable vertes (33 TUI, 11 web/WebSocket) ;
  **bilan consolidé : 1 680 tests, 16 ignorés, aucun échec ni erreur restant**. Empreintes Relais
  2 h × quatre graines identiques à la base (référence calculée une fois et rangée).
  Luna, une seule passe des trois scripts prescrits : 57 appels, aucun repli ni erreur de
  recharge ; résultat de recherche inventé refusé par l'audit, vraies ambiances admises.
  **Plafond de trois appels non revérifié avec Luna après le rendu direct final** : écoute
  4 appels, traces 6 dans cette passe ; leurs réponses archivées rejouées sur le code final
  donnent 2 appels simulés chacune, résultat moteur et recharge valides.
  [Rapport et limites du lot 34](taches/rapport-codex-34-perception-geste.md).
  Fusionné sur l'intégration après les lots 31 et 32 (base 1f1ea43) : seul conflit `docs/etat-dev.md` ;
  seul fichier de code commun depuis ffcc295, `moteur.py` (lot 34 : `PERCEPTIONS` et `Plan.perception`/
  `realise_geste` ; intégration : `vue_memorisee` autour de `_executer_simple`/`_executer_sequence`), hunks
  disjoints qui s'accordent.

- Branche `codex-propositions`, fusionnée, base `450cebb` (intégration `19b0261`),
  lot 29 A2a : contenu de parole indivisible demande/contrepartie, évaluation P/G/L et INT
  dans `echanges`, remises atomiques et engagements par `agendas`. Les promesses du joueur
  exigent un effet réel puis la perception du bénéficiaire ; fiche et contexte les conservent
  après recharge. Pas de double paiement d'une même promesse, pas de lot cédé pour une part.
  Les anciennes demandes restent séparées (vente sans jet, prêt, part servie) afin de préserver
  les nuits ; aucun fichier réservé au lot 28 touché. Empreintes de 2 h, Relais/mine/auberge,
  quatre graines : douze nuits identiques à `19b0261`, référence entièrement en cache.
  Luna, une seule passe de cinq saisies sur copies : 17 appels, aucun repli ni erreur de
  recharge ; cloche et méfiance typées dès le premier appel, **tâches promises et formulation
  libre encore mal typées**, mauvais marché corrigé par la revue. Pas de garantie générale
  du typage ni de toute issue narrative. Suite complète unique à priorité réduite, trois
  processus : **1 672 tests, 16 ignorés, bilan consolidé vert**, 2 534,6 s. Lancement trop tôt :
  deux fichiers ont chargé un import transitoire manquant (12 erreurs) ; leurs seules reprises
  sur le moteur final sont vertes (32 tests), aucun échec restant. Derniers ciblés consolidés :
  39 tests, un saut facultatif. Code signé et vérifié : `65032f5`, `7595dc7`, `a880ca8`.
  [Invariant, constantes, tests et limites](taches/rapport-codex-29-propositions.md).
  Fusionné sur l'intégration 2590c4a (depuis la base 19b0261 : lots 28 et 30) : seul conflit
  `docs/etat-dev.md`, aucun fichier de code commun depuis la base (lot 29 : `agendas`, `echanges`, `monde`,
  `moteur`, `paroles`, `pnj`, `propositions`, `rendu` ; lots 28 et 30 : `obstacles`, `planification`,
  `trajet_estime`) ; pas de suite complète. Tests du lot (`test_propositions`, `test_luna_restes`) et
  `test_agendas_socle`, `test_trajets_reels` (`tools/tests.py --processus 3`) : 43 tests, un saut, verts.

- Branche `codex-cout-exact`, fusionnée, base **2590c4a** (brief `d4c8b66`) :
  mêmes décisions et même monde, deux leviers exacts, commits signés SSH `3b3b895` et `4773611`.
  `trajet_estime.moyenne` garde son résultat dans la `Vue` figée : salle, cibles, sortie,
  allure et possessions si métriques ; corps, géométrie et obstacles crus sont propres à cette vue.
  Chaque reprise contrôlée recalcule la moyenne et ses tables locales. La copie de transaction du
  moteur garde la perception jusqu'aux souvenirs, au bilan et au rendu, pour les actions simples
  et composées ; clés physiques et sociales existantes, aucune mémoire dans la sauvegarde.
  Empreintes 2 h, quatre scénarios × quatre graines : chronique, mesures et état final identiques.
  Traces de recherches et nœuds strictement identiques sur ces 16 nuits, durées exclues.
  `VERIFIER` + `spatial.VERIFICATION=1`, mine/auberge 42, 2 h : aucun écart ni borne.
  Suite complète unique : **1 668 tests, quatre ignorés**, verte, 707,9 s, trois travailleurs.
  CPU moyen, trois versions lancées ensemble, 4 h, graines 42/1985 : ancien/base/branche,
  mine **7,102 / 11,492 / 9,125 s**, auberge **5,609 / 10,547 / 8,695 s** :
  **−20,6 % / −17,6 %** contre la base, encore **×1,28 / ×1,55** contre `42bb9c0`.
  Même état, mesures et recherches sur ces quatre nuits de 4 h ; aucun appel Luna,
  priorité réduite, quatre travailleurs au plus. [Rapport du lot 31](taches/rapport-codex-31-cout-exact.md).
  Fusionné sur l'intégration après le lot 29 (41c1c7c) : seul conflit `docs/etat-dev.md` ; `moteur` touché
  des deux côtés, sans conflit textuel : les engagements du joueur du lot 29 (`agendas.etat_promis`,
  `constater_geste_joueur`, autour de `_appliquer`) lisent les objets bruts de la copie de transaction,
  aucune lecture gardée par `vue_memorisee` ; rien de lu hors clé.

- Branche `codex-question-absent`, fusionnée, base d'intégration **2590c4a**
  (brief `894187d`, correctif signé SSH **b8a1f84**) : `noms.verifier_saisie` réemploie
  `est_question` hors parole et hors faisabilité ; `verifier_nom` exige le lien nominal
  sans imposer la présence pour une demande d'information. Geste et faisabilité gardent
  leur accès, perception nommée son refus moteur ; adresse nommée validée localement par
  `paroles.destinataires` (regard et voix distantes conservés). Aucun prompt ajouté.
  Sept tests nouveaux, **104 ciblés validés** : cas réels Brune/Gorm et peur d'Ilse,
  autres cas analogues ; état, texte sauvegardé et rendu après recharge, refus à zéro
  appel en ligne et hors ligne. Suite complète unique, trois processus à priorité réduite
  (1 522,8 s), puis seules reprises ciblées : **1 670 tests, 15 ignorés**, sans échec
  restant, bilan consolidé sur 155 fichiers. Régression d'appel distant corrigée par
  la priorité de `cri` ; attente historique d'adresse à un absent adaptée au refus local ;
  38 tests puis 10 tests rejoués, tous verts, traces initiales et consolidation conservées.
  Luna, une passe des quatre scripts prescrits : **32 appels**, aucun repli, arrêt ni
  recharge invalide ; les trois questions ciblées, une interprétation et un audit chacune,
  rappellent les pas sans les attribuer ou l'ignorance de la peur, sans révéler le guet.
  « observer Ilse » et « je pousse Aubin » : zéro appel ; Brune reliée s'écarte, Ilse répond.
  Deux autres tours corrigent leur audience collective. Appels et réponses négociées
  passent d'abord par `commandes.cri`, sans contrôle d'adresse de dialogue prématuré.
  Banc rapide Relais, 4 h × quatre
  graines, base puis branche : mêmes états finaux, mesures, boucles et constats d'audit ;
  aucun plantage, usurpation ni violation. Référence rangée dans le cache partagé.
  Limites : reconnaissance syntaxique des questions, noms absents du lexique et
  compatibilité mécanique de la prose encore en partie sémantique.
  [Rapport d'une page](taches/rapport-codex-32-question-absent.md), traces `artifacts/question-absent/`.
  Fusionné sur l'intégration après le lot 31 (f4e95fd) : seul conflit `docs/etat-dev.md` ; aucun fichier de
  code commun avec les lots 29 et 31 (`noms` seul côté moteur).

- Branche `codex-trajet-estime`, fusionnée (intégration 2590c4a), base d'intégration `ecbbed7`
  (brief `e282120`, code signé SSH `9f4bf2f`, `500d917`) : la recherche estime les trajets par salle,
  l'exécution garde le parcours réel. `Etat` ne distingue plus case ni orientation ; allure
  conservée pour les gestes sans témoin. Moyenne des trajets depuis les entrées, propre à la
  géométrie, obstacles/franchissements crus et portes comptés, pression par salle ; coût unique
  `obstacles.cout_route`. `Vue` et `part_estimee` partagent ce modèle, `_entrees` l'identifie.
  74 tests ciblés verts ; suite complète unique : **1 663 tests, quatre ignorés**, 729 s ;
  cinq échecs initiaux résolus, 96 tests en seules reprises ciblées, tous verts. Relais et mine :
  même plan depuis deux positions après recharge, durée exécutée et perception persistée ; grande salle plus chère.
  Erreur locale, 1 898 trajets : médiane 3,20 s, pire 14,05 s ; ce n'est pas une borne globale.
  CPU, trois versions ensemble, 4 h, 42/1985 : mine 7,102 → 12,484 → 11,648 s,
  auberge 5,992 → 12,508 → 11,109 s (`42bb9c0` → base → branche) ; nœuds environ divisés
  par deux contre la base, aucune borne sur ces douze nuits. **Cible ×1,3 non atteinte**
  (×1,64 / ×1,85 contre l'ancien). Banc rapide quatre scénarios × quatre graines, 4 h :
  aucun plantage/usurpation/violation ; pas de rafale, mais répétition sociale nouvelle mine 7
  et alternance supplémentaire mine 7 ; crue : passages maximaux 36 → 32.
  `VERIFIER` + contrôle spatial 1, 2 h, mine/auberge 42 : aucun écart. Aucun appel Luna ; priorité réduite, quatre travailleurs au plus.
  Limites : composantes d'une salle coupée, contacts sans entrée accessible, occupation mobile,
  détours locaux et absence stricte de toute répétition nouvelle. [Rapport du lot 30](taches/rapport-codex-30-trajet-estime.md).


- Branche `codex-cout-trajets`, fusionnée, base **0ac6b15** (brief **ff33ef0**) :
  invariant de Q conservé, décisions/coûts/ordre/recherches/nœuds identiques. Deux leviers exacts,
  commits signés : partage LRU des parcours crus sous géométrie, obstacles, portes, clés, origine,
  allure, eau et équipement utile ; cases de contact partagées par salle/cibles dans une vue figée,
  sans changer le départage des approches. Recalcul des reprises par `spatial.VERIFICATION`.
  50 tests ciblés verts ; 16 nuits de 2 h (quatre scénarios × quatre graines), puis quatre nuits
  CPU de 4 h : empreintes strictes identiques à Q, recherches et nœuds compris. CPU, trois versions
  lancées ensemble, graines 42/1985, mine : 6,745 → 14,045 → 11,485 s ; auberge :
  4,840 → 13,290 → 11,255 s (`42bb9c0` → Q → branche). Gains 18,2 % / 15,3 % contre Q ;
  **cible ×1,5 non atteinte**, reste ×1,70 / ×2,33 contre l'ancien moteur. Aucune réduction
  approchée d'`Etat`, aucune correction des recherches bornées. Contrôles `VERIFIER` +
  `spatial.VERIFICATION=1` sur mine/auberge, 2 h, graine 42 : aucun écart ni borne.
  Suite complète lancée une fois, trois processus : **1 603 tests, quatre ignorés**, verte,
  999,7 s (inclut le test existant de nuit de 10 h à la mine).
  Aucun appel à Luna, priorité réduite, quatre travailleurs au plus, aucune fusion ni banc long.
  Références réutilisables dans `artifacts/references/{0ac6b15,42bb9c0}/codex-28-*.json`
  du dépôt principal ; [rapport d'une page](taches/rapport-codex-28-cout-trajets.md).
  Fusionné sur l'intégration 19b0261 (depuis la base 0ac6b15 : R, A0, A1, cache, lots 25 à 27) : seul
  conflit `docs/etat-dev.md` ; `planification.py` fusionné sans conflit (l'intégration n'y change que l'accès
  aux engagements par `agendas.en_cours` ; A0 est dans `deliberation.py`) et `obstacles.py` intact depuis la
  base côté intégration. Aucune lecture hors clé : `_parcours_cru` ne lit que `obstacles`, `spatial`, `eau`,
  `geometrie` et `temps`, inchangés depuis la base ; le `_marcher` de R (`Vue.descente` sur les salles du
  détour) est l'exécution, pas le parcours partagé ; `Vue.contacts` ne lit que la vue crue figée et
  `pnj._a_portee_de`, inchangé. `comparer_bancs --empreintes` contre 19b0261, 2 h, quatre scénarios ×
  4 graines : chronique, mesures et état final complet identiques nuit par nuit. `VERIFIER` +
  `spatial.VERIFICATION` 1 sur 2 h, graine 42, mine et auberge : sans écart, aucune borne. Tests
  `test_trajets_reels`, `test_echelle_choix`, `test_agendas_socle`, `test_planif_cout` : 23 tests, verts. Suite complète
  une fois sur la fusion (ecbbed7, `tools/tests.py --processus 4`) : **1 661 tests, 15 sautés**, verte (1 678 s).

- Branche `codex-nom-non-relie`, fusionnée, base `ea4d562` (lot 26 `64351b2`) :
  résolution nominale commune dans `noms.personnage`, contrôle lexical avant saisie locale,
  conversation et MJ (`verifier_saisie`, `verifier_nom`). Un nom sans lien ou relié à un absent
  donne un refus local, sans modèle ni apprentissage ; paroles, noms hélés et voix gardent leur
  contrat. Aucun nouveau prompt ni fichier réservé touché. Correctif signé **736c043**.
  Neuf tests nouveaux : état complet et rendu après recharge, zéro appel dans les refus en ligne
  et hors ligne ; geste permis quand le lien existe. Suite unique, trois processus ; bilan
  consolidé après seules reprises ciblées : **1 607 tests, 15 ignorés, tous validés**.
  Reprises : attentes anciennes adaptées au refus plus précoce, diagnostics placés avant la saisie,
  HTTP local hors bac à sable (82 tests, 63,8 s) ; deux workers TUI initialement bloqués arrêtés,
  puis les seuls deux fichiers rejoués hors bac à sable (33 tests, 161,2 s), tous verts.
  Les traces brutes de la première passe et le rapprochement sont conservés dans `artifacts/`.
  Luna, une passe `echanges` et `noms-dialogue` : 10 et 12 appels, aucun repli ni recharge invalide ;
  « je pousse Aubin » : zéro appel (10 dans le fil du lot 26 réutilisé), aucun déplacement ni jet.
  Noms reliés : Brune s'écarte, Ilse répond. Limite : noms absents du lexique non reconnus comme
  noms propres, interprétation et gardes encore nécessaires. [Rapport du lot 27](taches/rapport-codex-27-nom-non-relie.md).
  Fusionné sur l'intégration b3c4bea (depuis la base : R signes, A0, A1, cache, lots 25 et 26) : seul
  conflit `docs/etat-dev.md` ; `commandes` et `paroles` fusionnés sans conflit (la résolution de
  `paroles._personnage` passe par `noms.personnage`, les engagements par `agendas`). Accord de fusion :
  le contrôle du lexique (`verifier_saisie`, appelé en tête d'`analyser` et dans `jeu.py`) devançait le
  refus du moteur d'« observer » une personne connue hors de vue (lot R : « cette personne », avec sa cause
  lumière, présence ou regard) par « Tu ne vois pas Ilse d'ici » (`test_signes_calibration`, six cas) ;
  une perception locale dont le complément entier nomme une personne reliée (`commandes.perception_nommee`)
  laisse désormais le moteur trancher (correctif à part, après la fusion), un nom non relié reste refusé par le lexique (« observer Aubin »).
  Les deux refus restent locaux, zéro appel, un `attendu` et une cause chacun. Tests ciblés (noms non
  reliés, signes, calibration, noms, parole-voix, relances, prises locales) : 114 verts. Suite complète
  une fois sur le correctif (2917a62, `tools/tests.py --processus 4`) : **1 659 tests, 15 sautés**, verte (1 905 s).

- Branche `codex-designations`, fusionnée, base `main` **42bb9c0** : noyaux nominaux
  reconnus par `noms`, qualificatifs conservés et contrôlés séparément. Même mécanisme dans
  le garde des voix, la projection et les liens publics transmis aux deux revues. Aucun nom
  appris par la description ; aucune donnée de scénario ni fichier des lots réservés modifié.
  Sept tests nouveaux en chaîne avec réponses simulées, sauvegarde/recharge et rendu : voix
  d'Ilse toute proche et de Gorm basse et lointaine, ficelle et couteau qualifiés ; identités
  ajoutées, négation de revendication et matières contraires refusées avec `attendu` ;
  appellation rapportée conservée avec apostrophe typographique. Tests nominaux finaux :
  **88 verts**, complément typographique compris ; suite complète unique : **1 597 tests,
  15 ignorés**, verte en 560,1 s, trois processus à priorité réduite. Luna, une passe
  (`soir-noir`, `atelier`, `echanges`) : aucun repli ni recharge
  invalide, bobine prise et portée, aucun refus nominal dans le noir ; sifflement joyeux
  (8 appels) et nom saisi non relié (10) restaient ouverts dans ce lot ; ce dernier est traité
  par le lot 27 ci-dessus, sans gain de temps général établi.
  Livraison et mesures dans le [rapport du lot 26](taches/rapport-codex-26-designations.md).
  Fusionné après `codex-ambiance` (intégration 121afb1) : seul conflit textuel `docs/etat-dev.md` (entrée et
  « À revoir », les réserves d'ambiance et de désignations gardées côte à côte) ; `narration.py` fusionné sans
  conflit : la voix d'auteur d'ambiance (lot 25) et `hors_designations` dans `_noms_voix_recit` (lot 26)
  touchent des fonctions distinctes ; `contrat-mj.md` sans conflit. Tests `test_designations`, `test_ambiance`,
  `test_narration`, `test_noms`, `test_luna_noms`, `test_voix_inconnues`, `test_relances_luna` : 138 tests, verts.
  L'écart d'appels Luna sur `echanges` du rapport n'est pas relancé (vérification groupée).
  Suite complète une fois sur la dernière fusion (227d20c, six branches réunies, `tools/tests.py --processus 3`) :
  **1 650 tests, 15 sautés**, verte (2 202 s) ; `test_mine.py:84` y passe.

- Branche `codex-ambiance`, fusionnée, issue de `main` **42bb9c0** : le contrôle commun de
  la voix d'auteur s'étend aux réserves sur la preuve reçue par le MJ. Il refuse le
  vocabulaire de preuve, avec segment, mots reçus et `attendu`, même si l'auditeur l'appelle
  ambiance ; il est refait à l'enregistrement. Interprétation sans ignorance systématique
  ajoutée ; révision centrée sur la rupture désignée ; audit de compatibilité sans exiger la
  cause d'une sensation. Cas réel du calme « aucun autre son n'est attesté ici » et odeur avec
  réserve de preuve : réponse corrigée, lieu, absence d'entité créée et texte persisté contrôlés
  après rechargement. Une inconnue mécanique dite en perception reste admise.
  Correctif signé **a223827** ; suite complète unique verte, **1 595 tests, 15 ignorés**, trois
  processus à priorité réduite, 564,4 s. Luna une passe finale, Relais, crypte, complément ambiance :
  63 → 59 appels, 3,00 → 2,81 appels/tour MJ, 12,7 → 11,5 s/tour, aucun repli ni erreur de recharge.
  « Aucun autre bruit de fond n'est établi ici » refusé par le nouveau garde et reformulé avant
  affichage. Méta-preuve absente des sorties finales relues ; critère d'absence de tout faux refus
  d'ambiance encore partiel (silence refusé au Relais au motif du bruit et des notes précédentes).
  [Cause, vérifications et limites](taches/rapport-codex-25-ambiance.md).
  Fusionné après `cache-references` (intégration 8047294 ; depuis la base : Q, correctif `defense`, R, A0, A1,
  cache) : seul conflit textuel `docs/etat-dev.md` ; `narration.py` et `consignes.py` fusionnés sans conflit
  (A1 n'y change que l'accès aux engagements, `agendas`). Tests `test_ambiance`, `test_narration`,
  `test_relances_luna`, `test_luna_restes` : 69 tests, verts. Luna non relancée (vérification groupée).

- Branche `cache-references`, fusionnée, base `main` **42bb9c0** (outillage seul, **ffbe799**) : les résultats
  d'une référence se calculent une fois par commit et se réemploient (`tools/references.py`, dossier
  `artifacts/references/<commit>/` du dépôt principal) ; `comparer_bancs` et `banc_multi` lisent les nuits et
  parties déjà jouées, ne jouent que celles qui manquent, jamais le worktree courant ; `--sans-cache` pour
  comparer des temps ; une phrase d'`AGENTS.md` (« Pas de référence relancée »). Détail dans « Outils de mesure ».
  Fusionné après `codex-a1-socle` (intégration ba3f7da) : aucun conflit (`AGENTS.md`, `docs/etat-dev.md`,
  `tools/` seulement ; `audit_nuits.py` d'A1 entre dans l'empreinte d'observation du cache). Tests
  `test_references`, `test_comparer_bancs`, `test_banc_multi` : 23 tests, verts.
- Branche `codex-a1-socle`, fusionnée, base A0 **2ddebe4**, brief **ccd8751** :
  `donjon/agendas.py` est le seul accès aux engagements PNJ, aux accords de mission et aux
  agendas de départ. Lectures copiées et filtrables ; écritures par opérations nommées ;
  cycle des échéances et validation déplacés sans changement d'ordre ni de stockage.
  Aucun agenda activé ni nouveau champ dans `data` ; la conversion en agendas d'origine
  `parole`/`contrat` attend le premier lot qui en a besoin. Contrôle AST : 46 accès directs
  sur 42bb9c0, aucun hors du socle désormais. Cinq nouveaux tests : garde AST, copies et
  déclaration sans effet, part promise puis remise au Relais, tâche payée puis abandonnée
  à l'auberge ; sauvegarde/rechargement, état et textes visibles contrôlés. Implémentation
  **162986d**, signée SSH. Suite complète une fois, `tools/tests.py --processus 3` :
  **1 600 tests, 4 ignorés, verte (349,6 s)**. Empreintes de 2 h contre 2ddebe4 :
  chronique, mesures et état final complet identiques, quatre scénarios × quatre graines.
  Référence calculée une fois et conservée dans `artifacts/references/2ddebe4017cfeec2d4fcd17d9fe923176f4112bb/`
  du dépôt principal. Aucun appel Luna ni banc de 8 h. `planification.py` : une lecture
  et l'import ; `pnj.py` et `signes.py` sans changement.
  [API, sites, mesures et limites](taches/rapport-codex-24-a1-socle.md).
  Fusionné après `codex-a0-echelle` (intégration 7526ff4 ; depuis la base 2ddebe4 : Q, correctif `defense`, R) :
  conflits `docs/etat-dev.md` et `tools/audit_nuits.py` (chargement du socle `agendas` d'A1 et entrée `rixe` de R
  côte à côte) ; `planification.py` fusionné sans conflit (la lecture de `_vu_avant_la_tache` passe par
  `agendas.en_cours`). Ni Q ni R n'ajoutaient d'accès aux engagements : le contrôle AST
  (`test_agendas_socle`, 5 tests) reste vert sur la fusion ; les seules clés `engagements` hors du module sont
  des dictionnaires publics produits pour le MJ ou l'audit. `comparer_bancs --empreintes` contre 7526ff4, 2 h,
  Relais et mine × 1985 et 42 : chronique, mesures et état final complet identiques nuit par nuit.

- Branche `codex-a0-echelle`, fusionnée, base `main` **42bb9c0**, brief **6772f31** :
  chaque candidat de `deliberation._candidats` porte une urgence explicite (palier, valeur,
  départage), seul critère du tri. Treize paliers historiques ; valeur des besoins pressants =
  écart au seuil, égalités et routines préservées. `choisir` ne change que le déballage du candidat ;
  hystérésis et sauvegardes inchangées. Quatre nouveaux tests : ancienne fonction copiée comme
  oracle à chaque choix de dix nuits de 2 h (quatre scénarios et `rixe`, deux graines), tous les
  paliers et égalités en scène, même ordre après rechargement, mêmes états et textes après les
  actions dans deux parcours Relais/auberge. Ciblés verts, 64,4 s. Suite complète une fois,
  `tools/tests.py --processus 3` : **1 595 tests, 15 ignorés, verte (864,7 s)**. Empreintes de 2 h contre 42bb9c0 : chronique,
  mesures et état final complet identiques, quatre scénarios × quatre graines. Référence conservée
  dans `artifacts/references/42bb9c0344f1c943f5b1d9ea40c012810380ee9a/` du dépôt principal.
  Aucun appel Luna ni banc de 8 h. Surcoût CPU observé, non attribué dans ce lot ; aucune garantie
  de stabilité du coût. [Échelle, mesures et limites](taches/rapport-codex-23-a0-echelle.md).
  Fusionné après `codex-signes-calibration` (intégration 3792eb7 ; depuis la base 42bb9c0 : Q, correctif
  `defense`, R) : seul conflit textuel `docs/etat-dev.md` ; `deliberation.py` fusionné sans conflit (ni Q ni R
  n'y touchent). `test_echelle_choix` (oracle de l'ancien tri à chaque choix, sur les nuits de Q) : 4 tests, verts.
  `comparer_bancs --empreintes` contre 3792eb7, 2 h, Relais et mine × 1985 et 42 : chronique, mesures et état
  final complet identiques nuit par nuit.

- Branche `codex-signes-calibration`, fusionnée, base moteur `8855312` :
  caches des causes d'émission, de perception par observateur et des relations ;
  continuité **physique** des signes sauvegardée (`677bfd1`) : détourner le regard
  ne recrée ni lecture, ni souvenir, ni annonce. Échec préservant la lecture active,
  retour réel/péremption nouveaux, même délai de dix minutes, provenance transmise
  avec les nouvelles. Refus moteur local d'une personne connue invisible : une cause,
  présence/lumière/vue, « cette personne », zéro appel au MJ en ligne et hors ligne.
  **35 tests ciblés**, dont captures réelles Relais 7 à 441 min et Lucien/Rémy mine 7,
  second guet à l'auberge, joueur et reprises ; suite finale : **1 591 tests, 15 ignorés, un échec**, 754,45 s.
  Échec historique `test_mine.py:84` (mine 3, 600 min) : Bram conscient, sécurité
  100 et biens 100, garde dans le noir près d’Odon sans secours. Arbitrage
  garde/sécurité à reprendre à l’intégration ; test intact, aucun contournement.
  Nouveau « Rythme des lots » de `main` **42bb9c0** appliqué : campagnes longues
  arrêtées. Banc final branche seule, référence 8855312 réutilisée : 4 h × quatre
  graines × quatre scénarios, zéro usurpation/violation, répétitions **27 → 0** ;
  constats antérieurs conservés, +1 alternance de buts crue 42 (bruit à 185 min,
  garde à 190 ; pas de boucle au même bruit établie). Luna finale : **une passe**,
  trois scripts, 12 appels, zéro pour observer Ilse dans le noir, aucune fuite détectée.
  Réglage commun **provisoire 4/3/8**, aucune exception individuelle : 174/816 méprises
  au banc rapide final (21,32 %), critère <20 % non atteint. Grille conditionnelle 63
  réglages et confirmation acquises avant le dernier correctif ; grille libre arrêtée,
  justesses haute/basse et abstention par sorte à revérifier à l'intégration.
  Preuves de coût seules, figées `bbf17cb`, acquises avant la consigne : état identique
  à 8855312 sur 2 h puis 8 h × quatre graines × cinq scénarios ; mine CPU 45,51 → 44,84 s
  (−1,5 %). Face à 276524c : −8,6 %, **nuits différentes**, pas le gain isolé des signes.
  Aucun changement de `planification.py` ni `deliberation.py`. Correctif de trajet
  isolé **8f60441**, à coordonner avec Q : `_marcher` applique `Vue.descente` aux salles
  du détour (Brune crue 500 et second cas Ilse ; test historique inchangé).
  [Rapport d'une page, mesures et limites](taches/rapport-codex-21-signes-calibration.md).
  Fusionné après `codex-trajets-reels` (intégration 0ac6b15 ; depuis la base 8855312 : S, Q, correctif `defense`,
  plans et « Rythme des lots ») : seul conflit textuel `docs/etat-dev.md` ; `pnj.py`, `moteur.py`, `refus.py`,
  `tools/empreintes_nuits.py` fusionnés sans conflit. **Trajet de R gardé** : Q ne le couvre pas (son `_marcher`
  n'écarte que les salles crues noyées) ; le correctif ne crée pas de seconde mesure de route (`obstacles.cout_route`
  reste la seule, pour le plan) : il réutilise la règle du plan `Vue.descente` pour exclure, dans la marche case par
  case (`spatial.trajet`, avec le `cout_porte` de Q), les salles du détour où le PNJ attend un piège
  (`TrajetsRevelesTests`, Brune et Ilse, vert sur la fusion). **`test_mine.py:84` passe sur la fusion** (mine 3,
  600 min, départ fixe) : la nuit n'est plus celle de R une fois les trajets réels de Q en place ; aucun test adapté.
  L'arbitrage garde/sécurité de Bram que R avait relevé n'est pas prouvé corrigé, seulement absent de cette nuit
  (voir « À revoir »). Tests ciblés (`test_mine`, `test_signes`, `test_signes_calibration`) : 40 tests, verts.
- Branche `codex-trajets-reels`, fusionnée, base `main` **aff9626** :
  coût unique `obstacles.cout_route` en temps réel cru (case réelle puis projetée,
  allure, diagonales, approches, rotations, portes et gestes). Pression par salle
  avant les effets ; état de recherche, graphes et certificats distinguent positions,
  portes et objets posés. Distances locales mémorisées et reprises vérifiées.
  Neuf tests de trajets suivent exécution, état, rendu et rechargement : Relais/mine,
  portes, approches, noir, obstacles crus ou ignorés, allure et clé posée, fuite, laps découpé.
  Suite complète verte : **1 585 tests, quatre ignorés**, trois processus, 1 161,92 s ;
  neuvième test ajouté ensuite et passé séparément (**1 586 tests couverts**).
  Contrôles 2 h, graine 42, quatre scénarios et `rixe` : sans erreur ni borne ;
  empreintes aux repères de 2 h conservées sur quatre graines, référence réutilisable
  dans `artifacts/references/aff9626af03c810f5881bae33301254d84bd9940/` du dépôt principal.
  Nouvelle règle « Rythme des lots » de **42bb9c0** appliquée : dernière campagne CPU
  8 h arrêtée, aucun calcul restant, aucune suite ni campagne longue relancée.
  Limites révélées avant l'arrêt : Bram lumière à 463 min atteint la borne de 4 000
  états ; nouvelle rafale au Relais 1985 (197 passages par PNJ dans une heure),
  allers-retours faim/abri dans crue 2024. L'absence de boucle nouvelle n'est pas acquise.
  Préférences inchangées, aucun appel à Luna. Bruts dans `artifacts/` ;
  [rapport d'une page et réserves pour l'intégration](taches/rapport-codex-20-trajets-reels.md).
  Fusionné après `codex-luna-restes` (`main` 42bb9c0 ; depuis la base : S, `plan-agendas`, `plan-decision`,
  « Rythme des lots ») : seul conflit textuel `docs/etat-dev.md`. Un seul fichier de code commun,
  `obstacles.py`, fusionné sans conflit : la forme inconnue d'un passage lève `ProprieteInconnue` (S,
  sous-classe d'`ErreurMonde`, donc toujours attrapée par `transitions`, `compiler` et la fuite de Q) et
  `cout_route` reste la seule mesure de route (Q). Suite (`tools/tests.py --processus 2`, poste chargé)
  **1600 tests, 15 sautés**, verte (3 449 s). Vérification d'intégration : `VERIFIER` + `VERIFICATION` 1 sur
  2 h, graine 42, Relais, mine, auberge, crue et `rixe` : sans écart ni borne. Audit 8 h (`tools/audit_nuits.py`,
  quatre scénarios × 1985, 7, 42, 2024 ; référence 42bb9c0 rangée dans `artifacts/references/42bb9c0/`) :
  aucun plantage, usurpation ni violation, aucune rafale (passages par heure au pire Relais 9 → 9, mine 17 → 21,
  auberge 23 → 21, crue 30 → 26), bascules ≤ 1 ; sans recours Relais 100 → 101, mine 14 → 15, auberge 134 → 128,
  crue 90 → 75 ; en attente 78 → 84, 289 → 299, 9 → 9, 119 → 178 (crue 1985 et 42) ; noir 93 → 93, 253 → 221,
  140 → 143, 36 → 30 ; eau 114 → 111. **Temps de calcul ×3,7 à ×4,8** au processeur, `main` et la fusion lancés
  ensemble (mine 42, 8 h : 43,9 → 210,4 s ; auberge 42 : 31,2 → 115,6 s) : plus d'états (case, orientation,
  allure dans `Etat`) et chaque état plus cher (routes, approches, pression par salle) ; recherches bornées à la
  mine 42 : 8 → 91 (Rémy `faim` 49, Josse `feu:poele` 39, Bram `lumiere` 3 à 463-465, aucune pour Bram sur
  `main`). **Rafale du Relais 1985 (12 h)** : Aubin force la réserve de Gorm à 690 ; `defense.retenir` lisait ce
  `frapper` sur une chose comme une violence contre son propriétaire : Brune, Ilse et Gorm le fuyaient vers la
  conduite noire puis revenaient à la lumière ou à l'abri (197 passages en une heure), et sur `main` Gorm
  ripostait (« frappe Aubin avec les fagots », Relais 1985 et crue 2024 à 12 h). Corrigé (commit séparé :
  seule une contrainte, `pnj.est_contrainte`, est une violence ; `test_defense.ForcerNEstPasAgresserTests`,
  Ilse et Gorm après rechargement, échoue sans) : Relais 1985 12 h, pire 197 → 9 passages par heure.
- Branche `codex-luna-restes`, fusionnée, issue de `main` **8855312** : validation physique
  déterministe avant revue de plausibilité ; propriétés connues et champs inconnus distingués ;
  fidélité de parole séparée en audiences admissibles et contenu, comparée par le moteur, avec
  les conséquences calculées sur copie et les noms publics. Repères du MJ en mètres (objets,
  souvenirs, sorties), unités du quadrillage et coordonnées refusées avant affichage et à
  l'enregistrement. Une contradiction narrative sans source retourne à l'auditeur ; la révision
  ne confond plus l'ambiance libre et une inconnue mécanique. Une question explicite de
  faisabilité reçoit immédiatement la propriété physique qui manque (`ProprieteInconnue`) ;
  les autres refus restent corrigeables. Gardes refaits à l'écriture de toute prose persistante.
  `etablir_faits` peut proposer les faits et la `suite` du geste dans le même appel, validés
  séparément sur copie ; une question n'exécute toujours rien.
  Sens des contenus typés partagé entre interprétation et revue ; une présentation extraite
  sans nom dans la citation est écartée sans réécrire la réplique ni faire apprendre ce nom.
  Quatorze nouveaux tests après rechargement. Livraison **24324f7**, commits signés : suite complète
  verte, **1 591 tests, 15 ignorés**, 648,8 s, trois processus à priorité réduite ; empreintes de 2 h
  identiques contre 8855312, quatre scénarios × quatre graines. Luna, deux passes ensemble par
  variante, 15 scripts prescrits et un complément : périmètre commun 3,06 → 3,04 appels et
  12,46 → 12,09 s par tour MJ, relances 7 → 6, replis 0 → 0,5 ; coût global stable. Forme inconnue :
  un appel dans les deux passes, manque du moteur, aucun déplacement ni forme inventée.
  `noms-dialogue` : question collective en quatre appels sans relance, 2/2 ; achat de planche accepté,
  puis remise réelle, 2/2. Aucune case ni coordonnée dans les textes, aucune erreur technique ou
  recharge invalide. **Ambiance : critère partiel**, « aucun autre son n'est attesté ici » subsiste ;
  autres faux refus et un repli nominal dans le noir restent décrits dans le
  [rapport de la tâche 22](taches/rapport-codex-22-luna-restes.md). Aucun changement des fichiers
  réservés aux lots trajets/signes ni des données de scénario.
  Fusionné sur `main` df81dc4 (depuis la base : `plan-agendas` et `plan-decision`, documentation seule) :
  aucun conflit, aucun fichier de code commun. Suite sur la fusion (`tools/tests.py --processus 4`) : 1 591 tests,
  15 sautés, verte (536,7 s).
- Branche `codex-sous-obstacle`, fusionnée, base `main` **276524c** :
  géométrie `passage` qualifiable et persistante, action composée `passer_obstacle` (dessous,
  dessus), même règle de gabarit/charge/encombrement et même durée pour le joueur et les PNJ.
  Ramper et enjamber sans jet ; escalader sur prises : FOR 10, échec sans déplacement. Le trajet
  rejoint une case libre de l'autre côté sans rendre l'obstacle transparent. Forme crue dans
  le parcours et les entrées de reprise du planificateur ; supplément de temps réel au coût
  historique par salle. Preuve de connexité et de détour au plus aussi rapide, à l'allure choisie,
  pour garder le parcours léger quand la marche suffit. Dix-neuf tests nouveaux : console/MJ
  simulé/recharge, jet commun, coût des séquences, temps découpé, planificateur et son contrôle.
  Prix des tâches fractionnaires arrondis en pièces entières ; une copie de sortie mesurée garde
  son seuil (fin de la boucle d'écartements révélée devant le cellier). Sans données nouvelles :
  quatre scénarios × quatre graines, 2 h puis 8 h contre 276524c, chronique, mesures et état final
  complet identiques. Puis 21 obstacles décrits dans les quatre scénarios ; l'ouverture du puits
  reste un vide, sans appui inventé. Banc 8 h × quatre graines × quatre scénarios : toutes les
  mesures, chroniques, positions et besoins relevés et constats d'audit identiques ; aucun PNJ
  n'a besoin du nouveau passage dans ces nuits (les scènes le vérifient quand le détour manque
  ou prend plus de temps). Surcoût CPU observé 5 à 10 %. Suite complète verte : **1 527 tests,
  quatre ignorés**, trois processus, 273,79 s. `VERIFIER` et perception 1 sur 2 h, graine 42,
  quatre scénarios et `rixe`, puis 0,2 sur 8 h : sans écart (recherches neuves bornées à 8 h :
  mine 51, auberge 18, limites déjà connues). Aucun appel ni connexion à
  Luna sur ce poste ; sept scènes préparées pour l'autre poste, essais requis avant de clore N5.
  [Règle, données, mesures, limites et vérification Luna à faire](taches/rapport-codex-19-sous-obstacle.md).
  Fusionné après `codex-force-4c` (`main` 663b664 ; depuis la base de O : H relations 3c, N part estimée,
  M noms lisibles, P force 4c) : conflits `esprits._croyance_valide` (croyances `passage` de O, lectures et
  `violence` de H et P côte à côte) et `planification._entrees` (lectures de H, du devis de N, de la défense
  de P, puis le parcours métrique de O : positions crues des obstacles, case de départ quand la preuve de
  domination ne l'écarte pas ; toutes dans la clé de la mémoire, la base des deux graphes `sombre`/`lumiere`
  et du certificat `_sans_plan`), docs. **Une seule règle de trajet** : la fuite du joueur de P
  (`defense.chemin_fuite`) avait son propre `spatial.trajet` sans les arêtes de O ; elle passe désormais par
  `obstacles.transitions` (obstacles que le joueur peut désigner, forme établie, carrure, charge et
  encombrement), la fiche nomme le passage avec sa durée (« … en rampant sous la poutre effondrée », 16,5 s
  au lieu des pas seuls) et, pour une escalade, son jet ; chaque passage est revalidé par
  `obstacles.compiler`, tourné vers l'obstacle s'il le faut, jet commun, échec qui arrête la fuite de ce côté.
  La fuite des PNJ suivait déjà les mêmes routes (`Vue.route`, `_marcher`). **Une seule mesure de route** :
  le devis de N (`part_estimee.aller`) et `planification._chercher` comptaient `len(route)` ; ils comptent
  `obstacles.cout_route`, comme `Vue.allers` et `Vue.trajet` (identique sans passage). Coût : la clé des
  routes de `Vue.route` ne distingue l'équipement entier que pour le parcours métrique (sinon les clés,
  comme avant O : 2 206 parcours → 788 sur trois heures de mine), mêmes nuits. Défaut commun révélé par Luna
  (`sous-obstacle-inconnu`, 1 passe sur 4) : **« La correction des faits narratifs n'a pas abouti. »
  affiché au joueur** quand la qualification corrigée revenait en geste ; le joueur lit désormais le refus
  du monde déjà opposé, sinon le geste revenu suit le chemin de son mode une fois, sinon « rien n'est
  tenté » (`mj._echanger_prepare`). Tests (après rechargement, `test_sous_obstacle`) : `FuiteTests` (le
  joueur fuit sous la poutre ou par-dessus en escaladant, escalade manquée ; sans forme ou avec une perche de
  3 m : refus avec `attendu` ; Gorm fuit sous la poutre, sans forme crue il reste coupé ; échouent sans le
  correctif pour le joueur), `_chercher` au coût de la recherche, qualification ratée puis geste (trois
  chaînes simulées, échouent sans le correctif). Suite (`tools/tests.py --processus 4`) **1577 tests, 15 sautés**, verte (459,8 s).
  `VERIFIER` + `VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h, graine 42, Relais, mine, auberge, crue, `rixe` :
  sans écart (recherches bornées à 8 h : mine 6, autres 0, comme après P), avant et après l'optimisation de
  la clé. `comparer_bancs` contre 663b664, 8 h, 4 scénarios × 4 graines : chroniques, mesures, récits,
  souvenirs, relevés, bilans et constats d'audit identiques nuit par nuit ; seules les empreintes d'état
  diffèrent, par les données `passage` des obstacles et les croyances `passage` (état identique ces champs
  retirés, vérifié sur 2 h, 4 scénarios × 2 graines) ; aucun PNJ n'emprunte de dessous ni de dessus. Temps
  au processeur, `main` et la fusion lancés ensemble (`empreintes_nuits.py`, 8 h, 4 graines, deux processus
  chacun), mêmes nuits et mêmes nœuds : avant l'optimisation Relais 17,1 → 18,4 s (+7,9 %), mine 50,7 →
  55,8 s (+10,1 %), auberge 41,2 → 42,7 s (+3,6 %), crue 27,7 → 29,7 s (+7,1 %) ; après, 17,1 → 18,0 s
  (+5,3 %), 51,0 → 53,6 s (+5,1 %), 39,0 → 40,7 s (+4,5 %), 27,5 → 28,5 s (+3,7 %). Ce qui reste : la preuve
  de domination (`metrique_necessaire`, 1 183 appels sur trois heures de mine, dont 13 calculs réels, ~3 %
  au profileur ; sa clé relit salles et obstacles à chaque appel) et `_marcher`. Luna (`banc_parties --fil`,
  quatre passes en parallèle des sept bancs `sous-obstacle-*` et de `force-4c-fuir`, puis quatre passes de
  `sous-obstacle-inconnu` après le correctif) : la question donne la fiche (ramper 12 s, bruit feutré, sans
  jet ; enjamber 6 s) en 2 appels 12 fois sur 12, jamais « il faut une échelle » ; `tenter` : Corvus de
  l'autre côté (Relais [6, 3], auberge [6, 4], lit [2, 0]), 12 s ou 6 s, obstacle toujours bloquant et
  opaque, aucun PNJ déplacé, récit fidèle (« Tu rampes sous la poutre effondrée et rejoins le sol de l'autre
  côté. ») ; examen après rechargement : les dimensions. Trop bas, trop haut, encombré (pied-de-biche) : la
  raison du moteur, 2 appels, position et temps inchangés, 4 sur 4. Forme inconnue : avant le correctif,
  le refus du moteur (1), un dialogue audité « tu n'en sais pas assez sur sa forme… examine-la de près »
  (2) et le message technique (1) ; après, « Le dégagement sous l'obstacle et sa hauteur ne sont pas encore
  décrits. » 4 sur 4, aucune forme enregistrée, mais 5 à 7 appels (Luna tente des qualifications, parfois
  incohérentes, que la contre-revue physique refuse toutes). `force-4c-fuir` : `fuir` typé du premier
  coup, 2 appels, fuite par la porte ; le récit relancé une fois sur deux (« deux pas »), comme à la fusion
  de P. `banc_parties` note l'état rechargé après chaque tour (`etat` : place, temps, ce que porte Corvus,
  personnages, formes et obstacles de la salle).
- Branche `codex-force-4c`, fusionnée, base `main` 9520f77 : danger attribué par la
  perception, croyance datée de violence hors du récit borné, comparaison fuite/riposte par
  le graphe commun, protection par cri reconnu et examen du lieu, reddition sauvegardée,
  dégagement d'une prise déclarée. Le joueur dispose de `fuir`, `riposter`, `se_rendre`,
  `degager`, avec fiche et `attendu`. Le prix de violence est centralisé ; les lectures
  nouvelles font partie de la base des graphes repris et du certificat. Un mouvement de
  coup garde sa durée même interrompu ; une neutralisation vue clôt l'atteinte et
  l'inconscience fait abandonner le plan : pas de coups gratuits au même instant ni de
  reprise au seul réveil. Le danger identifié est dans la fiche et le contexte du MJ,
  sans attribution devinée d'un coup non vu. Seize tests 4c vérifient deux cas par règle, état et rendu
  après rechargement, et même laps découpé. Suite complète : **1 482 tests, 14 sautés**,
  aucun échec ni erreur, quatre processus à priorité réduite (483,7 s) ; les seize cas 4c
  sont aussi rejoués sur le dernier code. Empreintes 2 h et 8 h : seize paires identiques
  aux quatre scénarios ; huit nuits de `rixe` identiques à 9520f77, sans coup ni mort.
  À placement identique du joueur, sans recours : `rixe` 68,75 contre Relais 64,375 (+6,8 %).
  CPU final au plus +2,5 % en moyenne par scénario. `VERIFIER` et spatial 1 sur 2 h,
  puis 0,2 sur 8 h, cinq scénarios : sans écart (les 66 recherches bornées connues de
  l'auberge). Luna non validée : catalogue disponible, ouverture WebSocket en délai dépassé.
  Dans l'épreuve, Aubin peut fuir comme Ilse :
  le choix demandé « riposte ou se dégage » et une borne universelle de dix minutes ne
  sont pas garantis ; les poursuites d'acquisition gardent la patience existante.
  Aucun lien ni `tuer`, aucun changement du modèle Luna. Mesures et réserves dans le
  [rapport 4c](taches/rapport-codex-17-force-4c.md).
  Fusionné après `codex-noms-lisibles` (`main` 7533778 ; depuis la base de P : E, L, K, H relations 3c, N et
  M) : conflits `deliberation.appeler_a_l_aide` (le suivi `secours` de K gardé ; un agresseur perçu,
  `defense.dangers`, garde le désarroi ouvert et empêche de le dire apaisé, donc un seul appel par épisode),
  `esprits` (croyances `violence` et lectures de H côte à côte), `planification._entrees` (lectures du devis de
  N et de H, puis admissibilité et prix des réactions de P : clé de la mémoire, deux graphes, certificat),
  `rendu.decrire` (sans humeur ; dépouille de L), `banc_parties` (états, noms et appels de main, puis coups de
  P), docs. Une seule `combat.prix_violence` (aucune copie revenue). Aucune humeur ressuscitée : la reddition
  est une posture du corps (`corps.visible`, `etat`), dite en phrase à part (« Aubin a cessé de résister » ;
  « Aubin est a cessé… » avant) ; la peur de la victime reste le signe « tremble » de 3c. Trois défauts communs
  corrigés : **un cri reconnu d'un protégé se retenait deux fois** (le souvenir de P, puis la voie commune de
  l'ouïe : deux inquiétudes pour un cri, 20 au lieu de 15 dans le test) ; **le MJ recevait le danger sans son
  fait** (`dangers_percus: ["brune"]`) et Luna concluait « personne ne t'agresse », proposait `impossible` ou
  répondait en dialogue : `defense.dangers_vus` donne l'auteur (projeté, `personne_<n>` pour un inconnu), le
  geste contre Corvus et depuis quand, décrit dans les consignes ; **la contre-revue lisait une réaction comme
  une agression** (« le plan frappe Brune, alors que la demande est de se défendre », « le plan fait se rendre
  Brune ») : le titre des réactions dit contre qui et pourquoi (« Te défendre : riposter contre Brune, …, qui
  t'a agressé, en frappant. », « Te rendre à …, qui t'a agressé : c'est toi qui cesses de résister. », « Fuir
  … ») et la contre-revue a une règle commune pour toute réaction à un agresseur nommé par le plan (la cible
  que le moteur fixe seul n'est pas un ajout). Tests (`test_defense`, après rechargement, deux cas chacun) :
  `CriUniqueTests` (Aubin et Ilse, échoue sans le correctif), `DangerDitAuMjTests` (Brune et Gorm, nom connu
  ou non) ; deux tests de P lisent la reddition sur le texte sans retour à la ligne. Suite (`tools/tests.py
  --processus 4`) **1553 tests, 15 sautés**, verte. `VERIFIER` + `VERIFICATION` 1 sur 2 h (tiré et fixe), puis 0,2 sur 8 h, graine
  42, Relais, mine, auberge, crue et `rixe` : sans écart ni usurpation ; recherches bornées à 8 h : mine 6
  (comme après N), autres 0. `comparer_bancs --empreintes` contre 7533778, 2 h puis 8 h, quatre scénarios ×
  4 graines : chronique, mesures et état final complet identiques nuit par nuit (personne n'y frappe).
  `rixe` et `rixe_douce` 8 h, graines 1985, 7, 42, 2024 : identiques à `main`, aucun coup, aucune fuite,
  aucun mort ni usurpation. Épreuve rejouée (`VERIFIER`, spatial 1, dix minutes rechargées minute par
  minute) : Brune frappe Aubin (3 PV) ; Aubin fuit à 8,3 s, Ilse à 9,7 s, Gorm vient et examine le lieu à
  22,2 s ; Ilse frappée : fuite à 9,7 s, Gorm à 23,7 s ; aucun autre coup, aucun mort ; le joueur lit
  « Aubin tremble et se recroqueville », puis la salle sans les fuyards. Temps au processeur, `main` et la
  fusion lancés ensemble (`empreintes_nuits.py`, 8 h, 4 graines, deux processus chacun), 24 nuits
  identiques : Relais 18,6 → 18,7 s, mine 53,6 → 54,2 s, auberge 41,6 → 42,2 s, crue 29,5 → 29,9 s,
  `rixe` 25,4 → 25,7 s, `rixe_douce` 19,9 → 20,1 s (+0,5 à +1,4 %). Luna (`banc_parties --fil`, deux passes,
  en parallèle) : avant les correctifs, « je m'enfuis » `impossible` puis `fuir` (une relance, 3 à 5 appels),
  « je me défends » et « je me rends » 0 sur 4 (contre-revue ou « personne ne t'agresse » affiché) ; après,
  `force-4c-fuir`, `-riposter`, `-reddition` typés `fuir`, `riposter`, `se_rendre` du premier coup (2 appels
  chacun), fiche puis « tenter », issue du moteur seule (« Tu dis : « Je me rends ! » et cesses de résister à
  Brune », « Tu ripostes à mains nues contre Brune : ton coup porte »), aucun PV, mort, nom ou parole
  inventés ; le récit de la fuite est relancé une fois sur deux (« deux pas » contre deux pas d'un pas).
  `force-4b-frapper` et `-assommer` : 2 + 2 appels, aucun refus, comme avant.
- Branche `codex-noms-lisibles`, fusionnée, base `main` **276524c**, worktree
  `tmp-worktrees/codex-noms-lisibles` : réécriture de lisibilité de `noms.py` et des seuls
  blocs nominaux de `voix`, `paroles`, `narration`, `mj`, sans changement de contrat ni de
  consigne au MJ. Variantes/motifs et numéros communs, projection séparée des règles de
  citation, contrôles nominaux décomposés et contre-revue de parole extraite.
  Aucun appel à Luna. Bancs d'empreintes 2 h puis 8 h, quatre scénarios × quatre graines,
  trois processus, contre 276524c : chronique, mesures et état final complet identiques.
  Corpus de 53 mondes avant/après recharge : 212 requêtes MJ, références, refus, rendus et
  état complet identiques octet pour octet (18 376 770 octets). Suite finale : **1 508 tests,
  quatre ignorés**, verte en 257,451 s ; aucun nom indéfini à pyflakes. Coût CPU médian sur
  neuf lots : `public` −62,32 %, `texte` −1,69 %.
  [Rapport, fonctions et preuves hors modèle](taches/rapport-codex-18-noms-lisibles.md).
  Fusionné après `codex-part-estimee` (intégration 1269064) : seul conflit `docs/etat-dev.md` ; ni H, ni N,
  ni rien d'autre depuis 276524c n'avait touché `noms`, `voix`, `paroles`, `narration` ou `mj` : ces cinq
  fichiers sont ceux de M octet pour octet, et les appels des signes (`noms.nom`, `noms.connait`) gardent
  leur contrat. Identité : `tools/comparer_noms.py --reference` (worktree détaché sur 1269064) sur
  **60 mondes**, dont les bancs `signes-ecart`, `signes-noir`, `signes-guet` et les scènes
  `tests/data/scenes` (`signes_ecart_relais`, `…_noir`, `guet_relais7`), prises d'office par l'outil
  depuis que ce dossier existe : corpus identique octet pour octet (20 391 535 octets, SHA-256
  `ca10fc25…`) ; l'outil rend le code 1 pour son seul critère de temps (`texte` +6,2 %, `public` −50 %,
  médianes de neuf lots sur un poste chargé ; le rapport mesurait −1,7 %). `comparer_bancs --empreintes`
  2 h, quatre scénarios × 4 graines, contre 1269064 : chronique, mesures et état final complet
  identiques nuit par nuit. Suite (`tools/tests.py --processus 4`) **1535 tests, 15 sautés**, verte.
- Branche `codex-part-estimee`, fusionnée, base intégrée `4fc5212`
  (`main` avec `GARDE`/`PRET` et force 4b) : une remise de combustible termine
  la recherche par un devis depuis le lieu de remise, au lieu d'y développer
  réception, recharge, allumage et suites. Demande et achat gardent trajet,
  chances, prix et attente ; livraison réelle et replanification gardent leurs
  frontières. Le devis commun compte source, flamme, pressions et un trajet avec
  au plus un geste conclusif ; la scène reste celle du départ, avec les moyens,
  droits et budget acquis par le préfixe, y compris une source empruntée.
  C'est une approximation, qui peut aussi écarter une voie à plusieurs préparatifs,
  pas une garantie générale de faisabilité future. Les lectures et la règle sont
  dans `_entrees` ; découverte de lumière, graphes et certificat suivent le même
  modèle. Auberge, 12 h, huit graines, référence et branche ensemble, quatre
  calculs au plus : CPU 108,71 → 68,28 s (×1,59), nœuds 1 521 695 → 614 622
  (×2,48), noir 1 050,625 → 989,375 min·PNJ, sans recours 174,375 → 176,25.
  Le dernier critère strict reste donc manqué de 1,875 min·PNJ ; le facteur deux
  visé n'est pas atteint sur le CPU. Demandes de
  combustible 11,5 → 11,625, achats 1,5 → 1,75, parts livrées 4,25 → 4,625,
  recharges de lampes 0,375 → 1,125 ; foyers allumés et rechargés stables.
  Justesse : 24 178 recherches rejouées avec l'ancienne chaîne, 95,86 % de mêmes
  premiers gestes et effets terminaux, 99,82 % quand les deux trouvent un plan ;
  écart médian de coût nul, pire fini 1,741 minute, un recours ponctuel de lumière
  perdu par pessimisme. Bancs 8 h, 4 × 4 graines, comparés à `4fc5212` puis à
  `origin/main` 5594028 : aucun plantage, violation ni usurpation. Contre la base,
  Relais 7 : noir +30 min·PNJ et une livraison de moins ; les autres nuits ne
  dégradent pas noir/sans recours. `VERIFIER` + spatial 1 sur 2 h, puis 0,2 sur
  8 h, graine 42 des quatre scénarios : aucun écart ni borne. Suite finale :
  1 469 tests, six échecs MiMo reproduits sur la référence, quatre sautés,
  aucun nouvel échec ; la suite n'est pas entièrement verte.
  Les critères d'acceptation ne sont donc pas tous atteints. Voir le
  [rapport Codex 16](taches/rapport-codex-16-part-estimee.md). Aucun appel à Luna.
  Fusionné après `codex-relations-3c` (`main` 6aaf0fb ; depuis la base de N : 4b corrigée, E, L, K et H) :
  seul conflit textuel `docs/etat-dev.md` ; `planification` fusionné sans conflit. Accords relus : `_entrees`
  garde les lectures de H (`actives`), de K (`recherches` par `appels_vains`) et de garde-pret
  (`prix_gardes`, dont le lieu de devoir menacé par un guet lu, `chances_demandes`), plus celles du devis
  (`v.eau`, `peurs_sociales`, `taux_mefiance`) ; le devis (`part_estimee.suites`) ne lit que la vue, dont la
  pression, et passe par les lectures communes de lumière (`feu`, `flamme`, `pression`), donc par la
  découverte et les deux graphes ; son cache est clé par l'état normalisé, le lot et l'emploi de lumière. Un
  candidat estimé n'entre jamais dans un graphe (poussé terminal, fait `estimation`) : `_parcours` le
  rencontre comme une lacune, jamais comme une preuve d'absence. `VERIFIER` refait la recherche neuve avec
  la même règle. Test adapté : `test_attente.test_un_appel_entendu` (la nuit libre du Relais n'a plus
  d'appel en 12 h : à 362, Gorm achète une part des planches d'Aubin, la reçoit et recharge lui-même le
  brasero, au lieu d'attendre le service puis de chercher Aubin en le hélant à 422, l'écart « remise ou
  service » du rapport ; placement d'auteur : Aubin ne sait plus où est Gorm, faim 60, il le hèle d'en
  dessous à 99 min, après des pas qui n'ont pas interrompu l'attente). Les six échecs MiMo ne reviennent
  pas (`test_mimo`, `test_fournisseurs_jeu` avec `jsonschema`, `.venv-mimo` : 16 tests, un saut, verts).
  Suite (`tools/tests.py --processus 4`) **1535 tests, 15 sautés**, le seul échec étant ce test, adapté.
  `VERIFIER` + `VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h, graine 42, Relais, mine, auberge, crue et `rixe` :
  sans écart ni plantage ; recherches jouées bornées à 8 h : mine 6, auberge 0 (les 66 de Lucien depuis
  garde-pret ont disparu). Banc rapide (`comparer_bancs`, 4 h, 4 graines, quatre scénarios, contre
  6aaf0fb) : toutes les mesures identiques, mêmes constats d'audit ; aucun plantage, usurpation ni
  violation ; seul le temps change. Temps (`tools/mesurer_part_estimee.py`, 6aaf0fb et la fusion lancés
  ensemble, quatre calculs au plus, poste partagé avec un Codex), au processeur par nuit et nœuds :
  auberge 12 h (4 graines) 202,8 → 140,5 s (×1,44), 1 446 295 → 661 857 nœuds (×2,19), recherches bornées
  398 → 65 ; 8 h : Relais 19,5 → 19,5 s (×1,00), mine 59,1 → 57,0 s (×1,04, nœuds ×1,59 ; 1985 +9 %),
  auberge 46,7 → 44,9 s (×1,04, nœuds ×1,15), crue 36,1 → 31,4 s (×1,15, nœuds ×2,47). Comportement à
  12 h : noir 1 046,25 → 1 046,25 min·PNJ, sans recours 180 → 180, en attente égales, parts livrées
  4,5 → 4,25, demandes de combustible 11 → 10,5 ; à 8 h, mesures égales sauf mine en attente
  283,75 → 288,75. Le gain du rapport tient à 12 h (×1,59 CPU et ×2,48 nœuds contre 4fc5212, ici ×1,44 et
  ×2,19 contre une base où K et H pèsent) ; la mine ne coûte plus davantage (rapport +6,8 %).
- Branche `codex-relations-3c`, fusionnée : signes physiques et impressions
  faillibles, colère, décisions de place/regard, lectures `devine`, flux de dés séparés
  par observateur, garde et doute d’un mensonge. `observer <personnage>` est local,
  consomme trois secondes ; rendu, carte et rejeu montrent leurs projections respectives.
  Humeur retirée ; `banc_pnj --regler gorm.PSY=16` disponible. Pas de 3d–3g.
  Référence mesurée `origin/main` récupéré à `a7ecb50` (le `main` local est antérieur).
  Suite complète : **1 437 tests, 4 ignorés**, sans échec ni erreur ; huit contrôles
  `VERIFIER`/`VERIFICATION` 2 h puis 8 h sans écart ni borne. Banc complet 20 nuits
  de référence puis 20 de branche, plus 24 nuits PSY, lots successifs à trois processus.
  Nouveau compteur `vols_vus_nuit` au registre, indépendant des souvenirs finaux ;
  les 40 états finaux restent identiques avec cette instrumentation.
  **Critère global non atteint** : justesse haute insuffisante, 41,3 % de méprises par
  défaut, coût CPU au-delà de +20 % hors auberge, baisse des vols vus non entièrement
  expliquée par dissuasion. Limites de la dissimulation, du joueur et des nuits libres
  détaillées dans le rapport ; calibration à reprendre, aucune exception de scénario.
  Luna **non vérifiée sur instruction de l’utilisateur** ; scènes versionnées et saisies,
  formes typées, appels nominaux et affichages attendus dans le
  [rapport de la tâche 11](taches/rapport-codex-11-relations-3c.md).
  Fusionné après `codex-luna-noms`, `codex-restes-fusions` et `codex-signalements` (`main` 276524c ; base de la
  branche a7ecb50, d'où lampes-suite, cout-suite, garde-pret et force 4b aussi absents de sa base) :
  conflits `moteur` (le bilan d'humeur de 4b retiré : seuls les signes disent ce que montre un personnage),
  `rendu.decrire` (sans humeur ; la blessure de la dépouille de L gardée), `vol` (plus d'humeur),
  `pnj.NATURES` (`lecture` et `violence`), `relations` (`chance_demande` et `signature`),
  `deliberation.menaces` (bandes de rancune et de peur de garde-pret, plus les guets lus), `banc_pnj`
  (`rixe` et `--regler`), tests MiMo (version de K), docs. **L'humeur de 4b sous forme de signes** : un
  inconscient n'émet ni ne lit aucun signe (`signes._de`, `_percus`), comme une dépouille, au joueur comme
  au MJ ; la victime frappée par surprise « tremble et se recroqueville » (sa sécurité presse) et Corvus
  peut lire « semble avoir peur » ; au réveil, le signe revient si sa cause demeure ; la fiche du coup est
  inchangée. `test_combat` adapté sans affaiblir ce qu'il vérifie (inconscient : aucun signe ni impression,
  ni au MJ, ni lu par lui ; frappé : un signe de peur dans le texte et après rechargement ; réveil : retour).
  Humeurs retirées du scénario `rixe` (`humeur` n'existe plus nulle part). Accords de fusion : les seuils des
  signes passent par les bandes et des lectures nommées de `relations` (`vive` à 60, `familier` à 40 ; le
  contrôle AST de L l'exigeait : « sec », dissimulation et place suivent l'hystérésis des bandes) ; un lieu de
  devoir ou de protégé que rend menacé un guet lu coûtait 0 avec `prix_gardes` (garde-pret ne pesait que les
  biens) : il coûte désormais sa loyauté, 2 à valeurs neutres, comme une charge (cas réel Gorm à la crypte,
  2,7 ; Odile à l'étable, 2) ; la conscience entre dans la clé sociale des signes (`spatial.etat_signes`,
  défensif : aucun écart observé sans elle) ; `vols_tentes`/`vols_vus_nuit` comptent par
  `pnj.est_contrainte` (4b) ; une impression ne se répète pas dans `regarder` ; `banc_parties` joue une
  scène enregistrée, avec noms connus déclarés (bancs `signes-ecart`, `signes-noir`, `signes-guet`). Trois
  tests de fusion (`test_signes.FusionTests`) : guet sur lieu de devoir (relais et auberge, échoue sans
  l'accord), signes et impressions d'inconnus par leur désignation et `personne_<n>` pour le MJ, cible
  comprise, inconscient sous `VERIFICATION` 1. Lectures du planificateur : `actives` (valeur et cible) entre
  dans `_entrees`, donc dans la clé de la mémoire, des deux graphes repris et la base du certificat ; les
  signes ne lisent pas la lumière dans la recherche (`menaces` lit les lectures retenues, pas les signes).
  Suite (`tools/tests.py --processus 4`) **1530 tests, 15 sautés**. `VERIFIER` + `VERIFICATION` 1 sur 2 h,
  puis 0,2 sur 8 h, graine 42, Relais, mine, auberge, crue et `rixe` : sans écart, usurpation ni borne notée.
  Banc rapide (`comparer_bancs`, 4 h, 4 graines, contre 276524c) : aucun plantage, usurpation ni violation ;
  auberge identique hors des mesures de signes (9,25 lectures par nuit) ; Relais lectures 44,5, méprises
  17,2, vols vus 1,25 → 1,5, retournements 99 → 112, noir 5 → 37,5 (Brune 95 min dans l'échoppe, graine
  2024) ; mine lectures 162, guets repérés 7,25, attentes sous regard 102 min, confidences 0,75 → 9,25 (les
  guets lus se répètent en nouvelles `intention_lue`), échanges 13 → 22,5, jets 5,75 → 19,8 ; crue lectures
  49, méprises 20, noir 42,5 → 20, crochetages 7,5 → 9,5 ; les alertes `repetition` de l'audit (mine 26,
  Relais 1) sont les lignes « Lecture de … » relues toutes les dix minutes. Temps au processeur, `main` et
  fusion lancés ensemble (`tools/empreintes_nuits.py`, 4 h, 4 graines, 2 processus chacun) : Relais 7,2 →
  8,1 s (+13 %), mine 12,7 → 17,1 s (+35 %), auberge 12,8 → 14,7 s (+15 %), crue 8,9 → 9,8 s (+10 %) ; à la
  mine (profil, graine 1985), `signes.percevoir_tous` (émissions de tous puis lecture par chaque PNJ, aux
  minutes et aux événements) et les lectures d'axes (`relations._lecture`) font l'essentiel du surcoût.
  Luna **non vérifiée** : le service a répondu en 88 s à un appel trivial et a laissé passer le délai de 45 s
  (une reprise comprise, 90 s) à chacun des appels du jeu, sur deux passes des bancs `signes-*`, des scènes
  de force et de `depouille` (16 h 02 à 16 h 10) ; `banc_multi` arrêté pour la même cause. Sans appel : sur
  copie de `signes_ecart_relais`, « observer Brune » et « observer Ilse » donnent 0 appel, les signes d'Ilse
  (« se tient à l'écart de Brune », « baisse les yeux », « tremble ») et « semble craindre Brune » / « semble
  avoir peur », rien pour Brune ; observer de nouveau après rechargement ne relance aucun dé (tirages 3 → 3) ;
  dans le noir, « observer Ilse » est refusé localement (« Tu ne vois pas cet objet ici »).
  Luna vérifiée après les fusions de N et M (intégration 59016d6), le service répondant de nouveau à
  17 h 08 (deux sondes à 16 h 21 et 16 h 44 encore en délai dépassé, 90 s par appel). Bancs `signes-*`, 2 passes
  en parallèle : `signes-ecart` 2 appels par tour MJ (interprétation et audit), aucun refus ni repli ; « Que
  remarques-tu… », « Ilse a-t-elle peur de Brune ? », « Veut-elle attaquer Brune ? » ne disent que les signes
  reçus et l'impression de crainte, toujours avec son incertitude (« tu ne peux pas savoir avec certitude »),
  aucune attitude prêtée à Brune, aucun projet d'attaque ; observer avant et après rechargement : 0 appel,
  mêmes signes. `signes-guet` 2 à 3 appels par tour, aucune fuite du guet caché (« rien ne te permet de
  savoir s'ils viennent de Brune »). `signes-noir` : « Ilse a-t-elle peur de Brune ? » 2 appels, rien
  d'invisible (« dans le noir, tu ne peux pas les observer ») ; mais « observer Ilse » coûte 4 à 5 appels et
  1 à 2 refus (Luna propose d'observer la lumière, puis Ilse ; refus du moteur et de la contre-revue) avant
  une réponse juste : en ligne, le refus local de la désignation (« cet objet ») part au MJ (`jeu.py`, une
  intention libre peut dépasser la syntaxe locale) ; hors ligne, 0 appel. `banc_multi`, `main` 276524c (avant
  H) contre 59016d6, 2 passes chacun lancées ensemble, huit scripts (quatre références, `force-4b-frapper`,
  `force-4b-assommer`, `depouille`, `noms-dialogue`) : 3,07 → 3,06 appels et 12,8 → 12,5 s par tour MJ,
  replis 0,5 → 0,5, relances 5 → 4,5, obstacles 8 → 5, refus 13 → 12, tours avec refus 8 → 9,5 ; force et
  dépouille 2 appels par tour des deux côtés, aucun refus. Textes relus : la victime frappée « tremble, se
  recroqueville et semble avoir peur » (`main` : « Brune semble inquiète »), Gorm assommé « s'effondre, sans
  connaissance », sans signe ni humeur, aucune humeur inventée ; la dépouille sans nom, portrait ni parole.
  Restes vus des deux côtés, sans lien avec H : la contre-revue juge individuelle une question « à
  quelqu'un » adressée à tous (relance) ; une ambiance rescapée par segments ; un récit qui situe un objet
  hors de vue « à deux cases vers le sud et deux vers l'est ».
- Branche `codex-signalements`, fusionnée, base `main` 43fa7ac : audit 32 nuits de 12 h,
  quatre scénarios × huit graines, sans Luna. Le même désarroi ne réarme plus l'appel sous le seul
  seuil de désespoir : le suivi de secours survit à la mémoire bornée. Une recherche retient aussi
  son échec après une réponse anonyme et suit le lieu d'un rendez-vous convenu ; résultats actifs
  dans la clé du planificateur. Lecture commune de l'inactivité pour le banc, le récit et l'audit
  (attente de moyen, charge confiée, charge satisfaite), sans changement des besoins. Les codes
  bruts restent visibles avec leur niveau d'explication. Appels d'Anselme, auberge 3 : 108 → 15 ;
  répétitions 6 → 0, rafales de passages 1 → 0. Noir long 57 → 67 : pas d'amélioration uniforme
  promise. Les observateurs seuls ont rejoué les 32 références à l'identique. Quatorze tests
  nouveaux avec quatre scènes enregistrées, laps découpés et rendu après rechargement. `VERIFIER`
  et perception 1 sur 2 h, puis 0,2 sur 8 h, graine 42, quatre scénarios : sans écart ni borne.
  Suite complète verte : **1 438 tests, quatre sautés**, trois processus, 241,3 s. Six échecs
  MiMo simulés également présents sur la référence avec `jsonschema` sont corrigés dans leurs
  fixtures (champ `presentation`, initialisation de la perception), sans appel au modèle.
  [Rapport, causes de chaque famille, commandes et limites](taches/rapport-codex-14-signalements.md).
  Fusionné en dernier, après `codex-luna-noms` et `codex-restes-fusions` (intégration e813865) :
  conflits `test_mimo` et `test_fournisseurs_jeu` (L et K corrigeaient les mêmes six sous-tests pour les
  mêmes causes ; gardée une seule version, celle de K : la capture est initialisée par
  `spatial.installer`, comme à l'ouverture du jeu, plutôt que par `memoriser` seul ; faux audit avec
  `presentation`), `test_ressources` (même assertion, commentaire réunissant la chance de demande de
  `codex-garde-pret` et le lieu du rendez-vous), `plan-planificateur` (deux sections gardées), docs.
  `recherches` entre dans `_entrees` par `appels_vains` (salles écartées encore actives) : clé de la
  mémoire, des deux graphes repris (`sombre`, `lumiere`) et base du certificat `_sans_plan`, qui ne lit
  que les arêtes ; aucune autre lecture nouvelle dans la recherche (`_attendre_qui_vient`, `appel.tenir`
  sont hors recherche). Suite (`tools/tests.py --processus 4`) **1508 tests, 15 sautés** ; MiMo, restes et
  signalements avec `jsonschema` (`.venv-mimo` du worktree de L) : 38 tests, un saut, verts. `VERIFIER` +
  `VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h, graine 42, Relais, mine, auberge, crue et `rixe` : sans
  écart ni usurpation (recherches jouées bornées à 8 h : mine 51, auberge 18, contre 46 et 6 avant K).
  Banc rapide (`comparer_bancs`, 4 h, 4 graines, contre e813865) : toutes les mesures identiques dans les
  quatre scénarios (les effets de K viennent après la 4e heure ou dans des nuits rares : auberge 3,
  Relais 42) ; `--empreintes` : l'état diffère dès la minute 0 par les champs nouveaux de l'esprit
  (`secours`, `recherches`). Mine 8 h, 4 graines, `tools/empreintes_nuits.py`, avant puis après K, l'un
  après l'autre : 28,7 → 39 s au processeur par nuit (planificateur 15,5 → 25,8 s) ; 1985 et 42 égales ou
  moindres, 7 39,7 → 47,4 s, 2024 22,1 → 56 s. Le surcoût n'est pas un coût par recherche (recherches
  neuves 616 → 662 en 2024) : les nuits divergent et des recherches atteignent leur borne de nœuds
  (bornées 2 → 73 en 2024 : Josse `faim` et `feu:poele` entre 330 et 480, après avoir cherché Gaspard en
  vain à la réserve et au filon à 345, puis Rémy `faim` à 450 ; nœuds 128 550 → 491 439 ; 7 : 67 → 87).
- Branche `codex-restes-fusions`, fusionnée, base `main` **5594028**, worktree
  `tmp-worktrees/codex-restes-fusions` : la réception précède la parole tenue dans la remise
  d'un objet ou d'une part promise ; accueil et réponses aux appels lisent les bandes communes
  de rancune/peur, hystérésis comprise. Seuils d'affection du passage et de dette du banc
  centralisés sans changement ; méfiances/rancunes comptées par bandes. Refus d'action clos et
  inconscient en champs et identifiants. La dépouille perd portrait libre, voix et tempérament
  du vivant, conserve apparence structurée, blessures et biens ; désignation du défunt d'après
  l'observateur PNJ. Le décodeur retrouve aussi les personnes mortes sous leur référence opaque,
  ce qui débloque les attestations et les actions du MJ. Les six sous-échecs MiMo étaient des
  attentes anciennes (symboles de vue, champ `presentation` absent du faux audit) : adaptateur
  intact, cinq transports attendus conservés. `.venv-mimo` isolé, `.venv` partagé inchangé.
  Cas réels et seconds cas après recharge dans `test_restes_fusions`, revue des seuils dans
  `test_relations_socle`. Suite complète : **1448 tests, 15 sautés**, verte en 566,25 s avec
  quatre processus ; tests MiMo et restes dans l'environnement isolé : 24 tests, un saut
  (SDK Anthropic absent). Luna : deux tours sur copie, huit appels, aucun refus, repli, incident
  ou mention sans fondement détectée. Banc rapide 4 h × quatre graines × quatre scénarios
  contre 5594028 : zéro plantage, usurpation ou violation, 16 empreintes physiques identiques.
  Relais 7 : annonce de parole tenue devenue inutile à la remise, échanges 9 → 8 ; auberge :
  désignations de souvenirs selon le PNJ observateur ; crue 42 : une rancune maintenue enfin
  comptée (mesure, état inchangé). Appels/réponses et refus d'accueil égaux sur ces 4 h.
  `VERIFIER` et `VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h, graine 42, chaque scénario :
  sans écart ; quatre recherches neuves bornées à la mine à 8 h, limite de recherche conservée.
  Résultats de suite, mesures et limites dans
  [le rapport](taches/rapport-codex-15-restes-fusions.md).
  Fusionné après `codex-luna-noms` (intégration 650b965), avant `codex-signalements` : conflits
  `rendu.decrire` (l'humeur de 4b, aucune chez l'inconscient, gardée ; blessure de la dépouille de L
  ajoutée), `tools/banc_parties` (préparation : états du corps de L d'abord, puis noms connus et appels
  d'E), docs. Aucune comparaison numérique d'axe ne restait hors de `relations` dans le code de 4b ni de
  `codex-garde-pret` (contrôle AST de `test_relations_socle` vert sans retouche). Suite **1494 tests,
  15 sautés**. `VERIFIER` + `VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h, graine 42, quatre scénarios et
  `rixe` : sans écart ni usurpation. Banc rapide contre 650b965 (4 h, 4 graines) : écarts du rapport
  seulement (Relais confidences 0,5 → 0,25, la parole tenue apprise à la remise, première divergence
  Relais 7 minute 162 ; crue rancunes 0,5 → 0,75, mesure par bande) ; aucun plantage, usurpation ni
  violation. Luna, scène `depouille` (2 passes par variante) : `main` 9520f77 répond « Cet objet n'est
  pas visible » sans appel (décodeur limité aux vivants) ; après L, 4 appels par tour, aucun refus ni
  repli, « le corps du vieil homme voûté … grièvement blessé ; les planches du bac sont accessibles »,
  sans nom, portrait ni parole ; « je fouille le corps » rend le même examen.
- Branche `codex-luna-noms`, fusionnée, base `main` 9075aea, worktree
  `tmp-worktrees/codex-luna-noms` : les contraintes d'adresse sont séparées du choix d'audience
  (individuelle, groupe, cantonade même avec des personnes visibles), contrôlé par la contre-revue
  de fidélité avant enregistrement, sans secours qui contourne un verdict négatif ;
  question directe conservée mot pour mot, verbe sans propos précisé sans appel au MJ, nom non relié
  traité sans démentis narratifs répétés. Tous les répondants sont entendus ; une voix audible
  d'une autre salle reste interlocutrice, et ses répliques sont enregistrées à leur source réelle
  par les deux voies (audit et fait typé). Citations successives segmentées ; présentation inventée
  par l'auditeur redemandée à l'auditeur. Mauvais type d'assemblage : refus de forme, pas besoin
  d'échelle déduit ; une question de faisabilité ne devient pas une parole, y compris après une
  correction. Coordonnées de proximité réservées à `attendu`, approches d'improvisation conservées
  en données sans libellé technique dans le récit. Suite du gel : **1 391 tests, 14 ignorés**,
  aucun échec ; huit nuits de 2 h, Relais et auberge, graines 1985/7/42/2024 : chronique, mesures
  et état final complet identiques à 9075aea. Campagne finale Luna : 21 scripts × 3 passes par
  variante, 126 parties/1 380 saisies, aucune erreur technique ni recharge invalide. Appel négocié :
  36 tours par variante à zéro appel modèle ; question collective à la cantonade 6/6. Relances
  historiques : 8,33 → 2 par passe, mais avec noms appris 2,67 → 4 (appels +7,6 %). Un repli
  Brune persiste et quatre clarifications de fidélité s'ajoutent : l'absence de faux refus
  sémantiques n'est pas garantie. Le passage sous la poutre ne demande plus une échelle par
  erreur de type, mais aucune solution générale de passage n'est fournie. Voir le
  [rapport de la tâche 8](taches/rapport-codex-8-luna-noms.md), mesures et limites explicites.
  Fusionné en premier (sur `main` 9520f77, après relations 3b, corps 4a, lampes-suite, coût suite,
  `GARDE`/`PRET` et force 4b) : conflits `dialogues.interlocuteurs` (la présence physique d'E retirée
  pour qu'une voix audible d'une autre salle reste interlocutrice, la conscience de 4a gardée : un
  inconscient ne parle ni ne répond, le joueur inconscient n'a pas d'interlocuteur) et docs. Accord
  ajouté : `narration.clarification_nominale` compte une dépouille comme personne (`noms.PERSONNES`).
  `auditeurs_parole` passe par `saisissent`/`saisit`, qui excluent déjà l'inconscient ; la contre-revue
  de fidélité ne porte que sur une parole à audience libre (`parole_joueur`) : un geste typé
  (`frapper`, `remettre`) n'y passe pas. Suite **1485 tests, 14 sautés**. `VERIFIER` + `VERIFICATION`
  1 sur 2 h, puis 0,2 sur 8 h, graine 42, Relais, mine, auberge, crue et `rixe` : sans écart.
  `comparer_bancs --empreintes` contre 9520f77, 2 h et 4 h, 4 scénarios × 4 graines : chronique,
  mesures et état final identiques ; mine et auberge 8 h graine 42 identiques aussi. Luna
  (`banc_multi`, `main` 9520f77 contre 650b965, 2 passes chacun lancées ensemble, 21 scripts : quatre
  références, leurs variantes `*-presentes`, `soir-*`, `noms-*`, six `appel-negocie-*`,
  `force-4b-frapper`, `force-4b-assommer`) : ensemble 3,07 → 2,99 appels et 12,1 → 12,1 s par tour MJ,
  replis 1 → 0,5 (le seul, `soir-voix`, une panne réseau de 52 s), relances 16 → 5,5, obstacles
  21 → 7,5, refus 31 → 31, tours avec refus 18 → 21. Quatre références : 38 → 33 tours MJ (refus locaux
  d'un nom inconnu, sans appel), 3,24 → 2,85 appels, 13,1 → 11,4 s, relances 10 → 1,5 (rapport :
  8,33 → 2). Avec présentations : 2,91 → 2,83 appels, 11,3 → 11,3 s, relances 3,5 → 1,5, refus
  9,5 → 12,5 (rapport : 2,88 → 3,10 appels, relances 2,67 → 4). `soir-appel` 2,6 → 3,9 appels et
  `noms-dialogue` 3,2 → 4,1 (la question à la cantonade fait répondre plusieurs voix : 3 → 6 ou 7
  appels) ; `noms-faisabilite` 4,75 → 3,5 ; appel négocié 0 appel des deux côtés ; `force-4b` 2 appels
  par tour des deux côtés, fiche du moteur, aucun refus. Textes relus : « est-ce que quelqu'un a du
  bois ? » dit tel quel à la cantonade 4/4, Aubin, Brune, Ilse et la voix de l'ouest répondent (`main` :
  à Aubin seul, phrase réécrite 4/4) ; « je réponds » sans appel demande les mots, sans appel au modèle,
  et avec un appel en cours fait entendre « Ici, viens ! » puis « J'arrive ! » ; « Brune, laisse-moi
  passer » nom connu : 3 appels, Brune s'écarte, nom inconnu : refus local ; « Ilse, tu m'entends ? »
  répondu, ou « tu ne vois pas Ilse d'ici » après les déplacements ; « passer sous la poutre » : plus
  d'« échelle », « Approche-toi … » sans coordonnées ; « je m'étire » sans « geste d'effort » ; ambiance
  décrite, encore avec une précaution sur les bruits (« rien de tel ne t'est perceptible »).
- Branche `codex-force-4b`, fusionnée : coups et assommement par la même règle pour le
  joueur et les PNJ, fiche avant tentative, armes et surprise, cris, interruptions, souvenirs
  et relations, registre et prise sur un porteur inconscient. Le recours assommer-pour-prendre
  compare les coûts, passe par `dans_le_dos` au pas feutré et ne suppose pas la disparition des
  témoins crus. `rixe` et son contrôle doux sont des données, sans branche de comportement
  propre au scénario. Empreintes de référence et contrôles croisés documentés dans le
  [rapport 4b](taches/rapport-codex-12-force-4b.md), avec leurs limites. Les scènes Luna sont
  versionnées ; vérification différée à la fusion sur un autre poste à la demande de l’utilisateur.
  Pas de 4c à 4f ni de modification du modèle Luna. Quatorze tests 4b verts ; suite complète
  1 432 tests, six échecs MiMo reproduits sur la référence, quatre ignorés. Quarante paires de
  nuits de référence (2 h et 8 h) identiques, dix contrôles croisés sans écart ; rixe, huit graines,
  nœuds +0,21 %, temps des recherches +2,88 %. Les nuits libres ne frappent pas ; l’agression
  puis la prise sont démontrées par les états d’épreuve, sans règle propre à leurs personnes.
  Fusionné après `codex-garde-pret` (intégration bcd6a83) : conflits `pnj._temoins` (l'événement
  `violence_vue` gardé ; l'auteur qui se sait vu passe par la boucle de `codex-garde-pret`, témoins
  remarqués en cours de geste compris) et `docs/etat-dev.md`. Aucune constante `PRET` ni `GARDE` ne
  survit ; l'agression ne compare aucune demande par une constante (les demandes ont la chance de
  `relations.chance_demande`). Courage, plafond d'enjeu et désespoir sont dans la base des deux graphes
  repris et du certificat ; `force_crue` et `embuscade_possible` lisent croyances, objets et ce qu'il
  porte, tous dans `_entrees`, sans lumière. Luna (connexion de ce poste, `banc_parties --fil`, scènes
  `force-4b-frapper` et `force-4b-assommer`, six passes) : `frapper` typé (`simple`, `assommer`), fiche
  puis issue du moteur, 2 appels pour typer et 2 pour raconter, aucun repli, aucun PV, mort, identité ni
  parole inventés ; Luna proposa deux fois un couteau pour assommer (refus avec `attendu`, corrigé en
  mains nues : 3 appels). Trois défauts communs vus et corrigés : « Gorm … à terre, sans connaissance
  et préoccupé » (un inconscient ne montre aucune humeur, `rendu` et `moteur`, comme une dépouille) ;
  « Tu frappes Brune… Brune semble calme » (l'humeur montrée suit l'état : inquiet si sa sécurité presse,
  accordée au genre, `moteur.HUMEURS_FEMININES`, `vol`) ; « j'assomme Gorm par derrière » refusé par la
  contre-revue qui ignorait que Gorm tourne le dos, puis Luna affirmant « il n'est pas derrière toi »
  (la fiche dit ce que le moteur établit de la victime : sans défense, ne te voit pas, te voit). Après
  correction, deux passes : 2 + 2 appels par scène, aucun refus. Tests ajoutés (`test_combat`, Gorm et
  Brune après rechargement) : aucune humeur sans connaissance, puis retour au réveil ; victime frappée
  par surprise « inquiet » / « inquiète » ; la fiche selon le regard et sans défense. Suite
  (`tools/tests.py --processus 4`) **1466 tests, 14 sautés**. `VERIFIER` + `VERIFICATION` 1 sur 2 h, puis
  0,2 sur 8 h, graine 42, Relais, mine, auberge, crue et `rixe` : sans écart ni usurpation (auberge 8 h :
  les mêmes 66 recherches bornées de Lucien qu'après `codex-garde-pret`). `comparer_bancs --empreintes`
  contre bcd6a83 (2 h, 4 scénarios × 4 graines) : chroniques, mesures, récits et souvenirs identiques
  sur les 16 nuits ; l'état final diffère dans 9 nuits par le seul champ `humeur` des PNJ et les lignes
  « … semble … » du journal du joueur passif (le correctif de l'humeur ; états identiques sans ce
  champ, vérifié nuit par nuit). `banc_pnj --scenario rixe` et `rixe_douce`, 8 h, graines 1985, 7, 42,
  2024 : aucun coup, aucun PV perdu, aucun mort, aucune usurpation ni écart ; la variante douce ne frappe
  jamais (aucun coup non plus dans `rixe` libre, comme le rapport) ; 12,9 s par nuit.

- Branche `codex-garde-pret`, fusionnée : `GARDE` et `PRET` retirés.
  `planification.prix_gardes` pèse l'ambition pour ses biens, la loyauté pour une charge
  confiée et la méfiance, rancune ou peur envers les présences crues ; à valeurs neutres,
  un lieu coûte toujours 2 par minute d'éloignement. `relations.chance_demande` centralise
  l'estimation du demandeur : son lien, ses refus, dettes et services vécus, ses témoins
  de faute remarqués et conservés après le geste ; jamais l'attitude privée de l'autre.
  Objets, parts et tâches y passent ; les deux cartes entrent dans `_entrees`.
  Dix tests ajoutés, état et rendu après rechargement (Gorm/Bram, Ilse/Joss, charge confiée,
  positions crues, cache, témoins remarqués ou non). Suite complète : **1428 tests, 14 sautés**.
  `VERIFIER` actif, `spatial.VERIFICATION` à 1 sur 2 h puis à 0,2 sur 8 h, graine 42 de chaque
  scénario : aucun écart signalé, aucune usurpation ni plantage.
  Bancs 4 h puis 8 h, quatre scénarios × quatre graines, `main` a7ecb50 puis branche,
  séquentiellement, quatre processus au plus : aucune usurpation ni violation. À 8 h,
  départs loin des biens Relais 6,5 → 4,25, auberge 5,75 → 5,25, crue 4,25 → 5,25 ;
  sans recours Relais 102,5 → 100, auberge 131,25 → 125, autres égaux ; temps processeur
  mine +12,1 %, auberge +11,2 %. Les alertes d'audit restantes et les limites de cette
  estimation avant 3c/3e sont détaillées dans le
  [rapport](taches/rapport-codex-13-garde-pret.md). Aucun scénario ni prompt modifié.
  Fusionné après `codex-lampes-suite` et `codex-cout-suite` (`main` 5594028) : conflits seulement dans
  `docs/etat-dev.md` et `docs/plan-planificateur.md` ; `prix_gardes` et `chances_demandes` sont dans
  `_entrees`, donc dans la base des deux graphes repris (`sombre`, `lumiere`) et du certificat
  d'impossibilité, qui ne lit que les arêtes (la chance ne change que des coûts) ; aucune lecture de
  lumière. Docstrings de `deliberation.menaces`/`gardes` accordées. Test adapté : `test_cout_suite` (la
  garde de Lucien, ambition 70, coûte 2,4 par minute : l'abri de la graine 7 trouve son plan à 3 855
  nœuds au lieu de la borne ; la graine 42 reste bornée). Suite (`tools/tests.py --processus 4`)
  **1449 tests, 14 sautés**. `VERIFIER` + `VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h, graine 42, quatre
  scénarios : sans écart ni usurpation ; à l'auberge 8 h, 66 recherches bornées notées (`BORNES`,
  Lucien `garder:grenier` et `garder:etable`, 33 chacune), les mêmes sur la branche seule (c9e0cb3),
  aucune sur `main` 5594028 : la garde plus chère à l'ambition 70 rend ces recherches plus longues que
  la borne de 4 000 nœuds (limite de la recherche jouée, pas un écart). Banc rapide (`comparer_bancs`,
  4 h, 4 graines, contre 5594028) : aucun plantage, usurpation ni violation ; écarts comme le rapport
  (Relais départs loin des biens 3,75 → 3, minutes-lieux 20,5 → 17,5, achats 1 → 0,75, tâches proposées
  0,5 → 1, appels à l'aide 0,75 → 0,25, noir 20 → 5 ; mine demandes 6,75 → 7,25, refus 5 → 5,25, achats
  1,5 → 1,25 ; auberge départs 2,5 → 2 ; crue demandes 3 → 2,75, refus 2,5 → 2,25) ; temps par nuit
  Relais 9,1 → 8,2 s, mine 14,8 → 13,7 s, auberge 14,7 → 15,7 s, crue 9,7 → 10,5 s.
- Branche `codex-cout-suite`, fusionnée, base initiale `main` 9075aea, puis fusion de
  `origin/main` **a7ecb50** par **1efbb12** : certificats d'absence
  sur les graphes déjà développés, indépendants des prix mais conservant permissions et
  profondeur ; chaque reprise contrôlée par `VERIFIER`. Une recherche pondérée épuisée ou
  bornée ne suffit pas à prouver cette absence (contre-exemple de profondeur testé).
  Ordre des visites avec égalités dans la clé ; empreintes visuelles partagées par objet et
  entre lectures sans changement, mutations ordinaires conservées, contrôle complet par
  `spatial.VERIFICATION`. Axes des relations 3b conservés dans les entrées des recherches.
  Sur a7ecb50 : **32 nuits de 8 h identiques** (4 scénarios × 4 graines, tiré/fixe), puis
  **4 nuits de 12 h de l'auberge identiques**, y compris tous les résultats des recherches via
  `empreintes_nuits.py --calcul`. Main et branche lancés ensemble, quatre calculs lourds au plus :
  CPU total 453,03 → 439,51 s (−3,0 %) sur les 32 nuits ; auberge 12 h 86,85 → 84,66 s/nuit.
  Les grandes recherches restent coûteuses. La dominance de dépense essayée hors du moteur
  change les résultats bornés de Lucien à l'auberge (7 à 644, 42 à 627), donc elle n'est pas
  livrée ; `_parts_remises` reste intact. Un contre-exemple général de borne et deux sauvegardes
  réelles protègent ce contrat. Les captures de preuve sont régénérées avec les relations 3b
  (Rémy mine 7 à 365, Aubin crue 7 à 443) : état complet et rendu après rechargement contrôlés.
  Suite après fusion : 1 431 tests, 4 sautés, six échecs MiMo préexistants ; la suite entière
  n'est pas verte (mêmes six échecs reproduits sur a7ecb50) ; 39 tests ciblés passent.
  `VERIFIER` et `VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h de chaque scénario, graine 42 :
  sans écart, nuits identiques. [Rapport, profils et limites](taches/rapport-codex-10-cout-suite.md).
  Fusionné après `codex-lampes-suite` et son correctif (`main` 43fa7ac) : seul conflit textuel
  `docs/etat-dev.md`, mais le certificat lisait un graphe à plat alors que le graphe repris en garde
  désormais deux (`sombre`, `lumiere`) : tel quel, il ne voyait que des lacunes. Règle accordée
  (`planification._sans_plan`, `_parcours` ; `docs/plan-planificateur.md`) : qui emploie la lumière dès
  le départ se prouve sur `lumiere` ; sinon le parcours de `sombre` ne suit pas un état dont le but ou
  les gestes ont lu la lumière, et l'absence n'est prouvée que si `lumiere` la prouve aussi (lacune
  s'il manque). Sans elle, une recherche épuisée dans le noir passait pour impossible alors qu'à faute
  bon marché la reprise avec lumière trouve un plan (`VERIFIER` l'arrête ; deux tests ajoutés, dont la
  chaîne réelle de `chercher`). `_entrees` garde les axes des relations 3b, `peur`/`eclairer` et l'ordre
  des visites. Suite (`tools/tests.py --processus 4`) **1439 tests, 14 sautés** (MiMo sans
  `jsonschema` : les six échecs du PC fixe sont ici sautés), verte. `VERIFIER` + `VERIFICATION` 1 sur
  2 h, puis 0,2 sur 8 h, graine 42, quatre scénarios : sans écart (78 reprises par certificat contrôlées
  à 8 h, mine et crue). `comparer_bancs --empreintes` contre 43fa7ac (2 h, 4 graines) : chroniques,
  empreintes et état identiques, seule la mesure `recherches_neuves` baisse (mine de 2 à 4, auberge 7 et
  42 de 1 : l'économie visée). `empreintes_nuits.py comparer --calcul`, 8 h, 4 × 4 graines, tiré et
  fixe : 32 nuits identiques, résultats des recherches compris ; reprises par certificat 139 / 779 /
  44 / 2 967 (Relais / mine / auberge / crue), les mêmes que contre a7ecb50. Temps au processeur,
  43fa7ac puis la fusion, l'un après l'autre, poste partagé avec deux Codex : 1 089,6 → 1 053,1 s
  (−3,3 %), × 0,99 à × 1,09 selon le scénario, dans le bruit.
- Branche `codex-lampes-suite`, fusionnée, base `main` 9075aea : la lumière employée par
  le but et ses gestes remplace la capacité de crocheter dans la pertinence des sources et des
  remises de combustible. Découverte par les lectures communes de lumière, reprise depuis le
  départ avec sa borne entière, marqueur conservé dans le graphe et mémoire contrôlée.
  La découverte s'arrête dès sa première dépendance ; identité chronique/mesures/état complet
  contre la première correction sur 16 nuits de 2 h. Cinq tests nouveaux : demande et livraison
  réelles, recharge, allumage, crochetage ou inspection, état et rendu après rechargement ;
  dont deux scénarios sans peur ni crochetage et un geste de fixture qui lit la lumière sans
  que son but la lise. La crue historique augmente surtout après la disparition d'un faux
  raccourci de chaleur (recevoir du bois ne réchauffe pas) ; trajets et priorités changent,
  sans promesse d'amélioration uniforme du noir. Coût de fin de nuit encore dominé par les
  grandes recherches. Suite finale : **1 377 tests, 14 sautés**, verte avec quatre processus.
  `VERIFIER` + vérification spatiale exhaustive sur 2 h, puis à 0,2 sur 8 h, graine 42, les
  quatre scénarios : sans erreur, code final. Banc rapide 4 h × quatre graines × quatre scénarios :
  chroniques, mesures et états finaux complets identiques. Audits 12 h auberge/crue × quatre
  graines : mêmes chroniques, mesures et événements de ressources ; zéro usurpation, violation
  ou plantage. Mesures actuelles, contre-épreuve et limites dans
  [le rapport](taches/rapport-codex-9-lampes-suite.md).
  Fusionné après les relations graduées (3b) et le corps blessable (4a), `main` a7ecb50 : aucun conflit
  textuel ; `_entrees` garde les axes et bandes des relations et ajoute le coût du noir et le but de
  lumière ; peurs sociales, présences craintes et `ranimer` ne lisent pas la lumière et passent par
  `_explorer_etats` comme les autres gestes. Correctif de fusion (relecture) : la découverte suit l'ordre
  d'exploration, donc le prix d'une faute, absent de la clé du graphe repris ; le marqueur
  `emploie_lumiere` du graphe faisait ensuite chercher avec les moyens d'éclairer à un prix où une
  recherche neuve ne les découvre pas (borne au lieu du plan, arrêté par `VERIFIER`). Le graphe en garde
  deux (`sombre`, `lumiere`), chaque nœud du premier retient si son but ou ses gestes ont lu la lumière
  et la relit, rejoué (`docs/plan-planificateur.md`, « Lumière employée ») ; test ajouté
  (`test_le_graphe_repris_redecouvre_la_lumiere_selon_le_prix_d_une_faute`, échoue sans le correctif),
  test du graphe repris adapté (deux graphes au lieu du marqueur). Suite 1424 tests, 14 sautés.
  `VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis `VERIFIER` et 0,2 sur 8 h, graine 42, quatre
  scénarios : sans écart. `comparer_bancs --empreintes` contre a7ecb50 (2 h, 4 graines, quatre
  scénarios) : 16 nuits identiques. 12 h, 4 graines, `tools/empreintes_nuits.py` : auberge identique
  jusqu'aux nœuds, temps égal (deux passes en ordre inverse : 180,9 → 210,2 s puis 195,9 → 193,6 s,
  l'écart suit la charge du poste) ; mine mêmes nuits, quelques centaines de nœuds de moins par nuit
  sur 1,3 à 1,9 million (les crocheteurs n'emportent plus de quoi éclairer sans en lire le besoin),
  184,9 → 160,4 s en une passe. Le surcoût de l'auberge depuis les lampes (~2× contre f1eee53) ne
  bouge pas : il vient des parts envisagées pour qui craint le noir, pas de la capacité.
- Branche `codex-noms`, fusionnée : nom entendu et relié séparé de l'apparence, de la voix
  et de l'appellation revendiquée ; personnes et éléments opaques, ciblage par désignation,
  mêmes règles pour les PNJ. Présentation typée auditée, identité privée propre au locuteur,
  contrôle inverse des références MJ et projection des rendus/contre-revues. Les corps jamais
  vus ne livrent aucun portrait. Les paquets nominaux privés servent seulement à la narration
  après validation, jamais au choix d'une cible mécanique. Citations auditées à portée précise, sans exemption d’une citation privée du narrateur.
  Discovery : 1 277 tests (1 long + 1 276 autres), suite verte, quatorze dépendances
  facultatives ignorées. Trois erreurs de console de la passe antérieure restent inexpliquées,
  non reproduites dans la passe exhaustive instrumentée verte, sans correction fonctionnelle. Douze nuits moteur 8 h sans violation de `Monde.verifier` ni usurpation ;
  replays Luna de présentation et d'aperçu vérifiés après recharge.
  Quatre références Luna × deux passes, main puis branche : 76 tours MJ par variante,
  2,89 → 3,09 appels/tour, 10,8 → 11,9 s/tour ; deux replis narratifs branche, aucun incident technique final,
  davantage de refus et relances (noms autrefois connus dans les saisies désormais inconnus).
  Voir [le rapport et ses mesures/limites](taches/rapport-codex-2-noms.md).
  Fusionné après `codex-profils` et `codex-lampes` : conflits `voix.se_nommer` (le bloc des noms gardé, la
  méfiance par la cause `imposture` des relations), `test_proto` (garde réseau de profils), `test_ressources`
  (la version des lampes, qui passe après les noms), `plan-ouie` (deux sections gardées) ; aucun accès direct
  à `fiable` (`test_relations_socle`). Suite 1329 tests. Banc rapide 4 h, 4 graines, Relais et auberge :
  identiques avant → après (le banc sans joueur ne voit presque rien des noms : 0 nom retenu en 4 h).
  Relecture : contrat du MJ renforcé (projection `personne_<n>`, contrôle déterministe des noms) ; code
  dense (`noms.py`) ; relances Luna 2 → 8 par passe selon le rapport, à surveiller ; Luna non revérifiée ici.
- Branche `codex-outils`, fusionnée : comparateur de bancs livré en premier,
  `tools/comparer_bancs.py` (référence puis branche, temps CPU par nuit, audit et identité
  chronique/mesures/état complet). Relais, 4 graines, 2 h : `main` contre `main` identique ;
  `main` contre `codex-profils` divergent dès la minute 0. Premier commit `4b8c4db` poussé avant
  le second outil. `tools/tests.py` isole les fichiers unittest dans des processus à priorité réduite,
  les plus longs d'abord (durées non versionnées) ; priorité Windows 64 bits effective par
  `tools/priorite.py`, sans modifier le moteur. Suite entière verte en série et en parallèle :
  **1 293 tests, 14 sautés**, même compte ; **24 min 18 s → 5 min 38 s** avec huit processus
  (×4,31, une passe de chaque, successives). Aucun regroupement des fichiers terminal/web requis.
  [Rapport, commandes et limites](taches/rapport-codex-4-outils.md).
  Fusionné après `codex-profils`, `codex-lampes` et `codex-noms` : seul conflit `docs/etat-dev.md`. Tests
  des outils verts (11). `tools/tests.py --processus 4` sur la suite entière : 1340 tests, 14 sautés, en
  8 min 32 s, même compte que la découverte `unittest` (1340). `comparer_bancs.py --empreintes`, `main`
  contre `main`, Relais, 2 h, graines 1985 et 7 : « identique ». Lancé depuis un worktree, l'outil crée
  ses worktrees temporaires sous le `.worktrees/` de ce worktree (ignoré par git), pas sous celui du dépôt.
- Branche `codex-taches-payees`, fusionnée, base `main` 06602a6, worktree
  `tmp-worktrees/codex-taches-payees` : parts, objets livrés et tâches se promettent, se font et
  s'abandonnent sur le même devis autonome (`planification.devis_pulsion`, `planifier_engagement`,
  `echanges.empeche`). Recevoir un bien du commanditaire reste possible ; lui faire servir une part
  ou allumer le feu à sa place ne l'est plus. Une vente devenue impossible est due sans attendre
  l'échéance ; une promesse gratuite garde un abandon sauvegardé à annoncer au destinataire. Le
  remboursement retient aussi la cause du refus, pour ne pas racheter en boucle le même service
  impossible. La réserve d'Odile est rétablie dans la scène de Tilo de `test_crochetage_surenchere`.
  Dix nouveaux tests après rechargement (`tests/test_taches_payees.py`), dont la sauvegarde réelle
  du Relais 42 à la minute 151 ; suite complète : 1292 tests, 14 sautés, aucun échec. `VERIFIER`
  et `spatial.VERIFICATION` 0,2 : une nuit de 8 h de chaque
  scénario, aucun écart ni borne atteinte. Banc rapide 4 h, quatre graines, Relais / auberge / crue,
  base puis branche, au plus quatre processus : aucun plantage, usurpation ou violation ; attente
  au Relais 8,75 → 0 min, parts devenues dues 0,25 → 0,5 (elles sont réglées plus tôt). Relais 42,
  8 h : dette de la part à 153 au lieu de 211, pièce rendue à 154 ; tâches proposées / acceptées /
  faites 19 / 4 / 0 → 2 / 1 / 1, dues aussitôt 3 → 0, dettes 5 → 1, attente 80 → 0 min. À 350,
  Aubin accepte pour deux pièces et fait le travail, tenu à 351. Le devis reste fondé sur les
  croyances : un prêt espéré peut être refusé ; le vendeur ne propose pas spontanément de changer
  le service en livraison de bois. [Rapport et limites](taches/rapport-codex-5-taches-payees.md).
  Fusionné après les tâches Codex 1 à 4 : conflits avec `codex-lampes` sur `echanges._remettre_part`
  (structure des lampes, faisabilité par `devis_pulsion` au lieu de `_plan_pulsion`), `_parts` (la part remise
  au commanditaire reste possible dans un devis, la part servie non), `esprits.verifier` (champs `lot`,
  `objet`, `annule`), `_entrees` (souvenirs `recu`, `promesse_annulee`, `creance`), `test_entretenir`, docs.
  Accord ajouté : une part à remettre promise sous le nom de son lot cesse d'être attendue quand elle est
  annulée ou remboursée (`promesse_en_cours`, `retenir_abandon` lit `lot`). Test adapté : Joss se présente
  au joueur avant la scène (`presentes`, branche des noms). Suite (`tools/tests.py`) 1350 tests. Banc rapide
  (`comparer_bancs`, 4 h, 4 graines, contre l'intégration d'avant) : auberge identique ; Relais en attente
  8,75 → 0, noir 48,8 → 5, dettes et remboursements 0 → 0,5 ; crue appels 0,25 → 0,75, une attente vaine ;
  aucun plantage, usurpation ni violation. Relais 42, 8 h : part vendue à 151, due à 153, rendue à 154 (avant :
  achats répétés « promis » à 211, 271, 332, dette à 392) ; à 350 Aubin accepte la tâche et la fait à 351.
- Branche `codex-relations-3b`, fusionnée : relations graduées à cinq axes dans l'esprit,
  liens de départ en données, épreuves par les souvenirs, estompement et hystérésis ; lectures
  graduées dans la parole, l'ouïe, les échanges, les passages, la compagnie et le planificateur.
  `fiable` quitte les croyances ; récit, rejeu et six mesures nouvelles. Aucun changement de MJ,
  aucune sous-étape 3c à 3f. Suite complète verte : 1311 tests, aucun échec ni erreur,
  14 ignorés (1297 réussis), en priorité réduite. Le texte d'abri vérifie la proximité réelle,
  même si le PNJ croit encore son compagnon sur une ancienne case.
  Bancs complets avant/après et quatre nuits de contrôle : critère des services atteint à
  l'auberge (1/4), pas à la crue (0/4). La paire rapprochée dépasse la borne de temps à
  l'auberge (+15,6 %) et à la crue (+71,5 %) : critère global non atteint ; limites et attentes
  de la crue documentées.
  Voir [le rapport 3b](taches/rapport-codex-6-relations-3b.md), notamment les limites de
  corroboration sociale, le registre de preuves durable et les réglages proposés.
  Fusionné après les sept branches de la nuit (`main` 9075aea) : conflits `relations.EPREUVES` (table graduée ;
  `parole_rompue` de l'appel négocié y entre comme une promesse non tenue, confiance −20 et rancune +15, réservée
  à qui identifie l'auteur ; d'une voix non identifiée, méfiance envers cette voix par `voix.se_mefier`),
  `echanges.remettre` (champs de 3b et `lot` des lampes ; une part détachée remise aussitôt est demandée, et
  payée n'est pas un don), `paroles._se_nommer` (noms entre guillemets, sans « ne te fait plus confiance »),
  `planification.Vue` (peurs sociales et lieux crus), scénario de la crue (valeurs des profils et liens),
  `tests/support` (`presentes`, `lier`, `relation`). États archivés de l'appel négocié et des tâches payées
  convertis comme 3b l'a fait (croyances `fiable` en relations, lien d'auteur contradictoire retiré).
  Tests adaptés : `test_appel_negocie` (parole rompue : Gorm, lié à 65, ne fait plus confiance à Aubin sans s'en
  méfier ; une voix inconnue devient suspecte), `test_lampes_parts`, `test_noms`, `test_relations_lectures`
  (réponse par `appel.repondre`), `test_ressources` (auberge 1985 : Odile refuse de donner puis vend une charge,
  trois foyers à 300 et 420), `test_attente` (premier fracas à 11 h 14, plus d'appel avant 8 h),
  `test_verifier_eau` (crue 500 : personne n'appelle à l'aide depuis l'eau ; au refuge, au sec, Gorm, Aubin et
  Ilse appellent à l'aide contre Brune qui vole). Suite 1401 tests. `VERIFIER` et `spatial.VERIFICATION` 1 sur
  2 h, puis 0,2 sur 8 h, graine 42, chaque scénario : sans écart. Banc rapide (`comparer_bancs`, 4 h, 4 graines,
  contre 9075aea) : aucun plantage, usurpation ni violation ; Relais échanges 5 → 6,5, appels à l'aide
  0,25 → 0,75 (Gorm trois fois en 70 min, graine 42), noir 5 → 20 ; mine sans recours 26 → 6 ; auberge égale
  hors relations ; crue méfiances 0 → 2,5, vols vus 0 → 1,25, crochetages 1,75 → 7,5, sans recours 0 → 60 (Brune
  refusée par Gorm dès la première minute, comme le rapport), dans l'eau 195 → 65 ; bascules crue 0 → 0,5 (une
  par nuit, pas une boucle). Temps au processeur : Relais 5,4 → 6,1 s, mine 10,1 → 12 s, auberge 10,8 → 13,7 s,
  crue 5,8 → 8,7 s (+15 à +50 %, comme le rapport : à réduire). Restes repris par
  `codex-restes-fusions` (fusionnée) : réception avant `engagement_tenu`, seuils en dur de
  l'accueil et des appels remplacés par les bandes. Les appels à l'aide répétés après un vol vu
  (désarroi renouvelé) : corrigés par `codex-signalements` (fusionnée).
- Branche `codex-force-4a`, fusionnée : sous-étape 4a du [plan force](plan-force.md),
  PV pour tous, blessures et malus, repos qui soigne au temps vécu, inconscience et réveil,
  réanimation au contact et par le planificateur du protecteur. Le corps vit hors de la
  délibération ; l'inconscient ne perçoit, n'entend, ne parle ni n'agit. Une chute à 0 PV du
  joueur traverse l'inconscience dans la même action. `corps.mourir` conserve l'identifiant
  et les biens dans une dépouille, archive le profil, retire l'esprit ; découverte, inquiétude
  et nouvelle de mort passent par les voies communes. La fin du joueur est sauvegardée close.
  Pas de coup ni d'action `tuer`. `banc_pnj --etat` prépare les épreuves ; états qualitatifs
  visibles, PV des PNJ cachés, rejeu omniscient avec PV/conscience. 16 tests spécifiques avec
  cas de même nature après recharge, sauts réels, laps découpés et décès de tous les PNJ des
  quatre scénarios. Les 20 nuits de 8 h restent identiques à `main` `06602a6` sur chronique,
  mesures, souvenirs, récit, état préexistant et empreintes normalisées sans les seuls champs
  ajoutés ; quatre nuits `VERIFIER`/spatial 0,2 et les épreuves passent, zéro usurpation.
  Surcoût CPU moyen apparié : Relais +4,27 %, mine +2,01 %, auberge +3,33 %, crue +7,67 %
  (une graine, deux à trois paires, variabilité entre passes). Suite finale : 1298 tests,
  quatre sautés faute du SDK Anthropic facultatif ; 16 tests propres à 4a.
  [Rapport, mesures et limites](taches/rapport-codex-7-force-4a.md).
  Fusionné après `codex-relations-3b` : conflits `deliberation` (devis des tâches payées gardé, réanimation
  ajoutée ; le corps vit dans `pnj._avancer`, la compagnie dans l'épreuve reste à la délibération), `esprits`
  (l'inconscient ne perçoit pas, avant toute mémoire de la vue), `pnj` (répondre vit dans `appel` ; la garde de
  conscience reste à appeler et héler, l'appelé inconscient ne saisit rien), `social._qui` (désignation des noms,
  puis nom du défunt), `faire_entendre` (l'inconscient ne parle ni n'annonce ses suites), `vol` (sans soupçon),
  `monde.contexte`, `moteur`, docs. Défauts de la fusion corrigés : un lien de profil survit à la mort de l'autre
  (`relations.verifier`) ; `scene_percue` masquait son champ visible par `corps.visible` importé sous le même nom
  (plantage dès qu'un personnage précédait une autre salle) ; le nom d'un défunt jamais entendu passait au joueur
  et au MJ (« corps de Aubin », portrait, identifiant) : une dépouille est une personne pour les noms
  (`noms.PERSONNES`), « le corps d'un vieil homme voûté », `personne_<n>` pour le MJ. Tests : `test_corps_blessable`
  (scène sous désignation puis présentée ; nouveau test du défunt jamais nommé, Aubin et Brune, connu ou non).
  Suite 1418 tests. `comparer_bancs --empreintes` (2 h, 4 scénarios × 4 graines) contre l'intégration d'après
  3b : chronique, mesures, récit et souvenirs identiques ; seules les empreintes d'état diffèrent, par les champs
  ajoutés (PV, inconscience, soin, `blessure`/`conscient` des croyances) : l'état final complet, ces seuls champs
  retirés, est identique sur les 16 nuits. `VERIFIER` et `VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42,
  chaque scénario, et épreuves (`--etat` inconscient, mort, blessé) sous `VERIFIER` et `VERIFICATION` 1 : sans écart.
  Restes repris par `codex-restes-fusions` (fusionnée) : refus du moteur en identifiants,
  description actuelle de la dépouille sans portrait vivant ni manière de parler ; `noms.nom`
  juge pour le PNJ locuteur d'après sa propre vue.
- Branche `refactor/adaptateurs-fournisseurs`, non fusionnée : `MJ` commun et adaptateurs OpenAI,
  Anthropic et MiMo expérimental, contrats de requête/réponse/erreur séparés ; 984 tests passent.
  Voir [la séparation des fournisseurs](adaptateurs-fournisseurs.md) et son compte rendu de vérification.
  Adaptateur MiMo terminé : choix explicite `--connexion mimo`, flux complet, une correction JSON bornée,
  banc migré, 998 tests passent et deux actions réelles réussies en 8 appels. Voir [MiMo](mimo.md).
  [Campagne complète de l'adaptateur final](mimo-campagne-complete.md) : 90 saisies, 38 tours MJ,
  120 requêtes réelles, sept rejets de format corrigés, aucun tour en erreur technique ; TTFT médian
  2,18 s et quatre reprises vérifiées. Défaut restant confirmé : MiMo ajoute des idées à la parole du joueur.
- `main` contient les jalons PNJ A à I (`docs/plan-pnj.md`, tableau « Jalons » et sections
  « Écarts retenus »). Le dernier fusionné est **I. Demander, écouter, protéger** :
  - le corps commun (faim, froid, fatigue) pour tous, joueur compris (`donjon/corps.py`) ;
    malus aux jets, PV à l'extrême, manger ; le scénario déclare des états ;
  - le joueur demande une part de vivres ou de bois ;
  - les PNJ font du bruit ; action `ecouter`, mieux contre une porte ;
  - protéger : donnée `protege`, appel à l'aide, protecteur qui accourt, victime prévenue.
  - avant I : H (sécurité perçue, abri, rondes en routine), G (le feu partagé).
- Luna (`gpt-6-luna`) reste le MJ. Le stratège Luna des PNJ (jalon E), anciennement
  optionnel et désactivé par défaut, est retiré au lot 130. Remesuré sur le Relais de F, il n'apporte presque
  plus rien : +5 % d'événements, −1 % d'oisiveté urgente. Le moteur fait désormais seul
  ce qui était son apport principal.
- Après F, branche `recharger-foyer` : mettre un combustible dans un foyer, c'est le recharger
  (`deplacer` vers un foyer devient `alimenter`) ; le combustible peut être porté ou à portée
  de main ; le titre de `deplacer` vers le joueur dit « Prendre », sans rangement que l'état
  ne modélise pas. Détail et vérification réelle dans `docs/plan-pnj.md` (écarts du jalon F).
- Branche `messages-refus` : les refus du moteur guident la correction du MJ. Chaque
  `ErreurMonde` porte `attendu` (champ fautif, valeur reçue, identifiants valables), transmis
  dans `retour_moteur` et jamais au joueur ; les causes fusionnées sont séparées ; l'étape,
  l'effet ou l'ajout fautif est numéroté. Mesure Haiku A/B sur les trois bancs : les refus
  corrigeables passent de 4 répétés et jamais corrigés à 2 corrigés dès la première relance.
  Restent hors périmètre : les messages d'audit (contrôle narratif, contre-revue) ; faits ensuite,
  branche `audits-attendu`.
- Branche `contre-revue` : le raccourci `detacher` libère la fixation sur place (la prendre
  est une étape `deplacer` explicite) ; un rapport de contre-revue mal formé est redemandé
  une fois puis le plan validé passe, au lieu d'être renvoyé au MJ comme un refus. Cas réel
  « fais levier sous l'axe » : 2 appels, conforme du premier coup (contre 4 à 8 avant).
- Branche `banc-haiku` : Claude Haiku 5.5 est une option du jeu (`--connexion anthropic`,
  `donjon/fournisseurs/anthropic.py`, `requirements-claude.txt`) ; Luna reste le MJ par défaut. Correctifs
  communs révélés par le fil complet des appels (`tools/banc_parties.py --fil`) : citation de
  fait inconnue écartée au lieu d'invalider la réponse ; audit narratif à une entrée
  obligatoire par segment, audit illisible redemandé ; texte vide signalé sans audit ;
  apparence d'un personnage acceptée en aspect ou portrait ; rappel d'une parole déjà
  entendue classé mécanique. Comparatif final sur les trois bancs (31 tours MJ) : Luna
  3,55 appels et 20 s par tour MJ, Haiku 3,68 appels et 12 s, 1 repli chacun (celui de
  Haiku corrigé ensuite), Haiku 0,17 $ les trois parties. Ni l'un ni l'autre ne réfléchit
  dans le jeu : Haiku ne le peut pas sous outil imposé, Luna en medium ne produit aucun jeton
  de réflexion. `tools/sonde_reflexion.py` vérifie hors jeu qu'une réflexion se constate.
- Branches `haiku-reflexion` et `narration-fidele` : Haiku joue par défaut avec réflexion
  adaptative (`--reflexion libre` ; `imposee` reste plus rapide, sans réflexion). Une réponse
  rendue en texte au lieu de l'appel est retranscrite en appel imposé. Banc (31 tours MJ) :
  0 repli, 1 tour refusé (contre 8 sans réflexion, 5 pour Luna), 22 s par tour MJ, 0,18 $
  les trois parties. Narration fidèle, quatre défauts communs corrigés : message technique
  affiché au joueur (consigner sans les croyances du locuteur), réplique du joueur réécrite
  (le personnage interpellé en tête est le destinataire, ses mots sont la réplique), geste
  refusé raconté comme tenté (audit), voix d'auteur dans le texte affiché (contrôle
  déterministe). Comparaison des textes : Luna ~190 caractères, sobre ; Haiku ~340, plus
  descriptif, et plus de dérives que les corrections encadrent.
- Branche `instructions-mj` : consignes du MJ réécrites (`donjon/consignes.py`), dans l'ordre de
  la décision (ton, autorité, mode, puis une section par mode), une règle à un seul endroit,
  sans anciens raccourcis ni rustines d'exemples ; ~15 000 caractères au lieu de ~24 000.
  Bancs multiples (même code, consignes seules) : Haiku 3 passes, 3,06 appels et 22 s par tour
  MJ contre 3,20 et 23,7, refus 1,3 contre 2,0, coût −8 % ; Luna 2 passes, 3,24 appels et 17 s
  contre 3,50 et 20,2, 0 repli contre 1, refus 4,5 contre 6.
- Outillage : `tools/banc_multi.py` joue des variantes (références git) en plusieurs passes et
  en parallèle, et résume moyenne et étendue ; le forfait ChatGPT a tenu 4 passes simultanées.
- Branche `fabrication-generale`, étapes 1 et 2 : tout objet peut recevoir une description
  physique (`donjon/matiere.py` : forme, dimensions, matière, pièces) établie par le MJ
  (`etablir_faits`, qualification) ; le moteur vérifie l'accord avec la masse et en déduit
  longueur et charge ; l'atelier y est migré. Ce qu'un objet contient ou consomme (la lanterne
  brûle de l'huile). Lots : un nom de pièce, un seul compte (pièces = utilisations), opération
  `prelever` qui réutilise les règles de `deplacer`. Correctifs trouvés en route : boucle de
  correction pour conversation, savoirs et description de personnage ; `enrichir` (personnage)
  et `etablir_faits` (objet) distingués ; l'audit physique juge un contenu sur sa plausibilité ;
  messages du moteur au tutoiement, sans rangement prétendu. Vérifié en bancs : Haiku et Luna
  décrivent planches, torche et lanterne, et prélèvent une planche (vol discret).
- Lisibilité : carte avec la pénombre (vert sombre dans l'interface), une lettre par personnage,
  méta-langage refusé dans le texte affiché.
- Branche `don-et-refus` (vu en partie : la cloche ne pouvait pas être donnée à Gorm, et Luna
  lui prêtait un motif inventé) : `remettre` est le geste de donner, avec récompense si un accord
  est accepté, sinon un don (l'objet passe au personnage, qui s'en souvient) ; une explication de
  refus ne fait parler aucun personnage ; un déplacement vers un personnage oriente vers
  remettre ; la contre-revue voit « nom (identifiant) » au lieu d'identifiants nus (« marchand »
  lu comme un marchand). Bancs : don de la cloche 3/3 avec Haiku et avec Luna.
- Branche `fabrication-generale`, étape 3 : action `assembler` (usage, pièces par rôle, lien,
  outil) avec n'importe quelle pièce décrite ; `fabriquer` en reste un alias ; l'échelle prend
  le nom « échelle » et sa matière de ses pièces. Action `decouper` : une barre ou un lien
  coupé à longueur donne un morceau, le reste garde la masse complémentaire ; l'outil doit
  pouvoir couper cette matière. Un lot se prélève d'abord pièce par pièce (prélever sur place
  ne déplace rien) ; la dernière pièce garde le nom de pièce. Bancs : échelle de perches et
  ficelle coupée d'un mètre, 3/3 avec Luna et avec Haiku.
- Branche `recit-pnj` : le banc sans joueur imprime un récit (`donjon/recit_pnj.py`) : buts et
  gestes de chaque PNJ, rondes résumées, besoins pressants et minutes sans rien entreprendre,
  échanges et témoins, méfiances à la fin ; `--chronique` ajoute chaque pas. Il montre un Relais
  surtout fait de rondes, une vie sociale réduite aux parts demandées, Gorm au devoir urgent en
  permanence sans rien à faire, un affamé honnête refusé sans autre idée.
- Branche `planificateur` : les plans des PNJ viennent d'une recherche sur des gestes déclarés
  une fois (`donjon/planification.py` : conditions sur ce que le PNJ croit, effets, coût ; faute
  comptée par personne lésée, chance de crocheter selon la lumière, flamme qui se consume).
  Faim, froid, pulsions, paroles données, garder, prévenir, s'abriter et la complétion du stratège
  y passent ; les méthodes écrites sont retirées. Comparées avant retrait : 6 800 plans
  identiques, deux ordres différents gardés. Banc identique à `main`, +33 % de temps. Trouvé sans
  être écrit : de la lumière avant de crocheter dans le noir ; demander un objet que porte un
  autre (Gorm demande ses planches à Aubin pour le feu). Bilan dans `docs/plan-planificateur.md`.
- Branche `vitesse-banc` : la vision des PNJ (lumière par case, champs de vue) est gardée
  pendant leur vie minute par minute, tant que portes, sources allumées et objets opaques n'ont
  pas changé ; `--graines` joue plusieurs nuits en parallèle. Résultats identiques (empreinte de
  la chronique, des mesures et de l'état final sur 4 graines). Une nuit : 9,2 s → 6,4 s en
  moyenne ; 4 nuits : 57 s → 11 s ; la suite de tests : 236 s → 135 s.
- Jalon `temps-fin` (`docs/plan-temps.md`) : l'horloge compte à la seconde (minutes et dixièmes) ;
  les PNJ vivent par événements, geste après geste avec leur durée, et marchent case par case
  par la règle du pas du joueur ; orientation en huit directions, cône de 120° et côtés
  immédiats, rotation 0,5 s par huitième de tour ; un pas s'entend à 6 cases et fait se retourner,
  un pas feutré (3 s) seulement de la case voisine ; tour d'horizon avant un geste sans témoin ;
  témoins pendant toute la durée d'un geste illicite. Le joueur est sur la même horloge : pas
  1,5 s, pas chassé (Maj), pas feutré (Alt), « tourner », regard sur la carte ; un geste sur ce
  qu'il a dans le dos le tourne d'abord ; les sorties connues restent listées. Les scènes de test
  posent l'orientation avec la position. Banc 4 graines : une nuit ~6 s, aucune violation.
- Jalon `vue-web` (`docs/plan-vue.md`) : `jeu.py --web` joue dans une page locale (127.0.0.1,
  commandes refusées d'un autre hôte) avec le même contrat que le terminal. Une scène perçue
  (`donjon/scene.py`) est la source unique de la carte du terminal et de la page : rien de ce que
  le joueur ne perçoit pas. La carte dessine chaque objet et personnage (icône, couleur, nom,
  regard, ce qu'il tient), le degré de lumière de chaque case tel que le moteur le calcule et le
  cône réel du joueur ; un clic mène à une case (commandes « pas », arrêt si quelqu'un entre dans
  le champ) ou propose les gestes possibles sur ce qui s'y trouve, en s'approchant d'abord.
  `banc_pnj --rejeu page.html` enregistre une nuit sans la changer et la rejoue : barre de temps,
  but, besoins, regard réel et croyances de chaque PNJ (fausses en rouge).
- Branche `annonces-presence` (vu en partie : « Aubin, Gorm et Brune arrivent puis s'éloignent »
  pendant qu'on allume une torche) : les présences se disent en bilan, à la fin de l'action du
  joueur (une manœuvre entière comprise) : qui il voit désormais, qui il ne voit plus, qui il n'a
  fait qu'apercevoir (`pnj.bilan_presences`). « Entre dans la pièce » ou « quitte la pièce »
  seulement s'il a vu le passage ; sinon « Tu aperçois… » ou « Tu ne vois plus… », ce qui couvre
  aussi son propre regard. L'humeur remarquée suit ce bilan. Banc identique à `main`.
- Branche `temps-fin-marche` (relecture du jalon temps fin) : aucun geste ne s'achève sur une
  case occupée (le pas qui mène sur quelqu'un se poursuit jusqu'à la case libre suivante ; le
  joueur ne marche pas sur un PNJ ; contrôlé par `Monde.verifier`, anciennes parties écartées au
  chargement) ; tout ce qu'un geste touche (cible, outil fixe) se rejoint par la marche, sans
  bond (`_a_toucher`, `_approcher`) ; le trajet en cases est le seul juge du passage : sans
  chemin, geste manqué, obstacle appris, et le chemin par salles évite un seuil qu'on croit
  barré ; on marche vers la case crue, puis on constate. Détail dans `docs/plan-temps.md`.
- Branche `temps-fin-etat` (relecture du jalon temps fin, `docs/plan-temps.md`, dernière
  section) : tout ce dont dépend la suite est dans `data` ; le même laps, attendu d'un bloc ou
  découpé en rotations et rechargé en route, donne le même monde (`tests/test_temps_etat.py`).
  Tour d'horizon dans l'esprit du PNJ ; un registre des gestes en cours, joueur compris, jusqu'à
  leur fin (témoin : quiconque voit l'auteur pendant le geste) ; bruits datés à l'instant ;
  interlocuteur = personnage perçu (vu, ou entendu pendant le dernier geste) ; perception des
  PNJ après chaque événement. Banc : aucune usurpation, plus d'échanges et de confidences.
- Branche `planif-rapide` : le planificateur des PNJ ne pèse plus que 7 % d'une nuit (41 %
  avant). Diagnostics des recherches au banc (`--diagnostic`) ; le dernier résultat de chaque PNJ
  pour chaque but est repris tant que rien de ce que lit la recherche n'a changé ; chaque but dit
  ce qu'il peut employer (repas, feu) et l'on ne porte que ce qui peut le servir. Empreinte des
  4 nuits identique ; nœuds examinés 185 000 → 11 700 ; une nuit 10,1 s → 5,6 s (processeur).
  `planification.VERIFIER` refait chaque résultat repris ou borné par une recherche complète :
  toute lecture nouvelle de la recherche (un coût, une croyance) doit entrer dans `_entrees`.
- Branche `perception-rapide` : ce que perçoit un acteur, les places des objets et les champs
  sont gardés tant que l'empreinte complète de l'état ne change pas (`spatial.etat_vue` : chaque
  clé que lit la perception) ; une consultation qui ne révise que des esprits la calcule une fois
  (`etat_fige`). Lignes de vue, vue autour d'une case et champs ne dépendent que des salles et de
  la signature d'une salle (seules les sources qui peuvent l'éclairer) : gardés d'une étape à
  l'autre, clé le texte des salles. `spatial.VERIFICATION` recompare les lectures mémorisées à un
  calcul de zéro. Empreintes des 4 nuits identiques, aussi en vérification complète. Perception :
  2,7 s → 1,0 s par nuit (30 % → 13 %), au profil 33 % → 11 % ; une nuit 9,1 s → 7,4 s ; 4 nuits
  12,2 s → 10,1 s.
- Branche `scenario-auberge` : second scénario, l'auberge du Col-Pendu (`donjon/scenario_auberge.json`,
  `donjon/auberge.py`, `banc_pnj --scenario auberge --joueur dortoir`, `jeu.py --auberge`). Une nuit de
  tempête, huit salles sur trois niveaux, huit PNJ aux buts concurrents (aubergiste, cuisinière,
  enfant, palefrenier, marchand et son ballot, ancien soldat, pèlerine, voyageur au crochet qui cache
  un reliquaire), bois et vivres comptés, trois foyers, une rafale qui éteint l'âtre (horloge). Écrit
  seulement avec des données ; un seul correctif de moteur, `social.GESTES` (une rumeur sur un feu
  allumé, éteint ou rechargé par un autre faisait planter le banc). Mécaniques qui manquent, relevées
  en l'écrivant : demander du combustible pour une pulsion de feu (aujourd'hui seulement pour le
  froid de soi), un objet prêté encore illicite pour l'emprunteur s'il a un propriétaire déclaré, une
  nouvelle sans lieu (le marchand ne retrouve pas son ballot), aucun recours au bruit pour retrouver
  quelqu'un dans le noir, le froid sec trop lent (2 par heure) pour menacer qui est au sec.
- Branche `caracteres-valeurs` (étape 1 de `docs/plan-social.md`, `donjon/caractere.py`) : VOL,
  ELO et PSY pour tous ; les états modulent les caractéristiques par une règle commune (la
  fatigue touche aussi INT et PER ; volonté brisée prévue en donnée) ; persuasion d20 + CHA + ELO
  contre la VOL de l'auditeur. Huit valeurs de 0 à 100 dans le profil ; les limites deviennent
  honnêteté ou douceur 100 (profils et sauvegardes migrés au chargement). Une faute a un prix
  en minutes selon l'honnêteté, usé par la détresse, moins vite avec de la volonté ; l'altruisme
  de qui donne facilite une demande. Banc : même ordre, plus d'échanges, moins de vols dans
  certaines nuits ; bilan et limites dans `docs/plan-social.md`.
- Branche `crue-eau` (étape 3 de `docs/plan-crue.md`) : un niveau d'eau tiré de la
  graine par un tirage à part (`donjon/eau.py`) ; salles mouillées puis noyées (100 cm) selon
  leur altitude ; l'eau trempe, éteint un feu posé, barre le passage, pour le joueur comme pour
  les PNJ. Les PNJ voient l'eau, en jugent la vitesse, l'attendent dans l'heure ; l'eau inquiète,
  un lieu menacé n'est pas un abri, et tant qu'elle monte l'abri est le plus haut lieu éclairé.
  Scénario dérivé `crue` (`donjon/scenario_crue.json`, `jeu.py --crue`, `banc_pnj --scenario
  crue`) ; le Relais et son banc sont inchangés. Banc 16 graines : feu noyé 5 fois, quelqu'un
  monte à la galerie 14 fois. Corrigés en route : un réflexe d'alerte sans passage tombe ; un PNJ
  ne prend rien dans la main d'autrui ; pas de bois demandé pour un feu cru sous l'eau.
- Intégration du 2026-10-20 (branche `integration`, une fusion par branche, suite et banc après
  chacune) : chronique du banc, vue web, présences, marche, temps fin sans état caché,
  planificateur et perception rapides, mine, auberge, caractères et valeurs, crue. Correctifs de
  fusion : les témoins reçoivent le geste en cours ; la mémoire du planificateur lit aussi le prix
  d'une faute et l'adresse modulée (contrôle `VERIFIER` sur 4 nuits). Défaut d'origine corrigé :
  l'étage d'une salle est celui du plan (`niveau`), pas l'altitude de son sol ; deux salles d'un
  même étage à des hauteurs différentes se voient et s'éclairent, un escalier change d'étage.
  Relais : empreinte des 4 nuits inchangée par les optimisations et par la crue ; une nuit ~13,7 s
  → ~4,7 s (4 nuits en parallèle). Constat : combinées, la marche et la perception par événement
  redonnent au Relais une nuit proche de celle d'avant (mêmes mesures), alors que chacune seule
  multipliait échanges et vols vus ; à examiner avec le rejeu.
- Branche `laisser-passer` (vu en partie : Brune, désœuvrée sur le seuil du refuge, barrait la
  sortie ; Luna lui faisait promettre de se pousser sans que rien ne la déplace, et « je la
  pousse » était refusé) : trois règles communes, joueur compris (`donjon/passage.py`). Un PNJ
  sur la case où l'on doit s'arrêter s'écarte d'une case hors du chemin, sauf geste en cours
  (dont la porte qu'il va ouvrir), méfiance ou fierté qui l'emporte de 30 sur l'altruisme ;
  sinon le pas du joueur est refusé avec un `attendu`. Demander le passage est un contenu de
  parole typé (`passage`) que le moteur tranche ; acceptée, le PNJ bouge vraiment. Pousser :
  action et commande, jet de FOR opposé, la victime recule d'une case ; victime et témoins
  cessent de croire l'auteur fiable ; douceur 100 l'interdit, sinon faute au prix de la
  douceur. Un PNJ bloqué attend, demande, pousse si ses valeurs le permettent, sinon patiente et
  renonce ; il prie le joueur de le laisser passer. Bancs Relais (8 graines), mine et auberge :
  identiques à `main` (personne n'y bloque quelqu'un d'immobile). Joueur posté sur une porte
  (`--joueur crypte` au Relais, `--joueur cuisine` à l'auberge) : les PNJ le prient de les
  laisser passer (1,25 et 6,25 demandes par nuit), puis renoncent au bout de 30 min au lieu
  d'attendre sans fin (renoncements 1 → 1,25 et 1 → 7) ; aucune poussée, tous ces PNJ ayant la
  douceur entière. Luna (3 parties courtes) type la demande `passage` et l'action `pousser`.
  Détail, cas vérifiés et limites dans `docs/plan-temps.md`, « Correctif : laisser passer ».
- Branche `don-et-promesses` (vu en partie : « je donne la cloche a Gorm » partait au MJ ; Brune
  répondait « Je vais me pousser » sans que rien ne la fasse bouger, puis le MJ le rappelait
  comme acquis) : l'analyse locale reconnaît donner et remettre à la première personne et à
  l'impératif, avec « à », « au » ou « a », le destinataire avant ou après l'objet, chaque nom
  désignant exactement un objet et un personnage ; le moteur refuse ce qui manque. Après un
  refus, quelle que soit la voie, la réponse ne cite aucune parole nouvelle (contrôle
  déterministe, sans dépendre du verdict de l'auditeur). Une promesse d'agir d'un PNJ (verdict
  d'audit `engagement`) doit recopier ce que le moteur a enregistré : engagements pris, intention
  en cours, accords (`esprits_interlocuteurs.<id>.engagements`) ou l'issue qu'il vient de valider
  (`conversation_validee`) ; sinon elle est reformulée sans promesse. Luna sur la sauvegarde
  réelle : « Je vais me pousser » (Brune) et « je peux garder un œil sur la réserve » (Ilse)
  refusés puis reformulés. Limite : repérer une promesse reste un jugement de l'auditeur ; seul
  son appui est vérifié de façon déterministe.
- Branche `ouie` (`docs/plan-ouie.md`, `donjon/ouie.py`) : une règle d'ouïe commune
  au joueur et aux PNJ remplace `pnj.alerter`. Tout geste retentit selon sa nature, déclarée une
  fois (pas feutré < pas, geste ordinaire < voix < bruyant < appel) ; la distance et les passages
  l'atténuent ; seuil mieux aux aguets, moins bien au repos, modulé par la PER. Un bruit ordinaire
  de qui l'on croit là est attribué ; inconnu ou inhabituel, on se retourne de près (témoin par le
  registre), sinon on retient un bruit vers ce lieu, qui inquiète à la mesure de ce qu'on entend ;
  aller voir est un but du planificateur que décident le devoir de garde et, pour un fracas ou un
  appel, le courage ; le bruit de qui l'on se méfie se surveille. Le joueur entend par le même
  calcul et lit qui se retourne vers lui. Correctif révélé : un geste social vers qui n'est pas là
  corrige la croyance. Bancs : aucune usurpation ; vols vus au Relais 1 → 2,9 ; minutes sans
  recours égales ou moindres (auberge 584 → 584, mine 680 → 604). Limite : les réflexes déclarés
  gardent l'ancienne portée des sons.
- Branche `diagonales` : un pas en diagonale dure √2 fois un pas droit, à toute
  allure, pour le joueur et les PNJ (`temps.duree_pas`, 15 → 21 dixièmes) ; les chemins
  (`spatial.trajet`, le clic de la page) sont les plus courts en temps ; lumière, vue, ouïe et voix
  se mesurent en distance réelle arrondie à la case (`geometrie.distance`) : halos ronds, une
  diagonale voisine reste au contact. Bancs sans usurpation ni violation, même temps de calcul ;
  Brune, arrivée face aux témoins, attend avant de crocheter (plus de vols aboutis et vus). Détail
  et limites dans `docs/plan-temps.md` (« Correctif : les diagonales »).
- Branche `parole` (`docs/plan-ouie.md`, section Paroles) : le moteur fixe à qui
  parle le joueur (`paroles.analyser`, `paroles.destinataires`), celui qu'il nomme, sinon celui
  qui est en face de lui ; à égalité, le joueur précise. « à tous » vise tous les présents qui
  l'entendent, chacun décidant pour lui ; des guillemets en tête valent « je dis » ; chuchoter ou
  murmurer, à un seul, au contact. Toute parole à voix haute, du joueur ou d'un PNJ, est retenue
  de tous ceux qui en saisissent les mots (`ouie.mots_saisis`, `social.retenir_parole`) : une
  affirmation se juge comme une confidence, une nouvelle comme une rumeur, un aveu (nouveau
  contenu typé) se croit ; seuls les destinataires répondent (contrôle narratif déterministe).
  Sans personne en vue, une parole sans conteste est dite à la cantonade ; le MJ ne peut plus la
  raconter lui-même ni la changer en geste. Vérifié avec Luna sur des copies de la sauvegarde
  réelle (cas réel, aveu, guillemets, chuchotement, à tous). Correctif révélé : une parole qui confirme ce qu'on vient de voir ne le change plus en ouï-dire.
  Bancs : Relais identique (9,75 paroles surprises par nuit) ; mine et auberge, moins de
  confidences (les témoins savent déjà), plus de rumeurs crues et de méfiances à l'auberge ;
  minutes sans recours en hausse par des jets décalés (une part refusée à Gaspard, mine 2024).
- Branche `constater-et-rumeurs`, non fusionnée (`docs/plan-ouie.md`, « Constater, raconter où,
  chercher quelqu'un ») : trois manques de la mine et de l'auberge. **On constate ce que la main
  rencontre** : un geste manqué sur un objet cru dans un contenant ouvert, alors fermé, apprend le
  contenant fermé (verrouillé ou non, par l'essai) et garde l'objet cru dedans (`pnj._hors_d_atteinte`) ;
  Brune force de nouveau la réserve au lieu de croire les vivres disparues. **Le témoin d'un geste
  qui déplace un objet voit où il va** (`pnj._lieu_vu`, `prendre` et `poser`) : il le croit là, sa
  nouvelle porte le lieu (« … a posé le ballot de soie dans l'étable »), qui la croit en tire une
  croyance de lieu à confiance de ouï-dire, sauf constat propre postérieur (`social._apprendre_lieu`) ;
  qui sait depuis l'objet ailleurs tait le lieu ; le protecteur qui prévient la victime lui dit
  aussi où sont ses biens. Anselme reprend son ballot (graine 42). Ne pas avoir trouvé un objet ne
  dément plus qu'il soit ailleurs (`paroles.dementi`), le voir dans d'autres mains non plus
  (`esprits.reviser`). **Chercher quelqu'un** : en parcourant une salle où on le cherche sans le
  voir, on l'appelle (`pnj.appeler`) ; il répond, sauf à qui il reconnaît et dont il se méfie.
  Mireille trouve Odile au grenier noir au lieu de tourner une heure. **Se parler, c'est
  s'entendre et savoir qui parle** (accepté) : chacun saisit les mots de l'autre par l'ouïe commune
  (`ouie.s_entendent` : distance réelle, ouverture, porte fermée ; plus de `de_pres`) et le voit ou
  reconnaît sa voix ; on ne s'adresse qu'à qui l'on a vu ou reconnu (`pnj.identifie`,
  `croit_present`), jamais d'après sa place réelle. Chacun connaît ceux qu'il a vus ou entendus
  parler (`voix` de l'esprit, `data["voix_connues"]` du joueur, migrées) ; une voix connue dont on
  saisit les mots situe qui parle (`entendu`), une voix jamais entendue est un bruit inconnu. Le
  joueur : `ecoute` ne nomme qu'une voix connue, seules elles font savoir qui est là ; un échange
  qu'il ne voit pas ne s'écrit plus « X parle avec Y ». Salles désignées avec leur article
  (`francais.lieu`). Accordée avec `integration` (jusqu'à la lumière comme besoin) : une seule
  règle, `pnj.peuvent_se_parler`, pour toute parole échangée, y compris servir une part et la
  parole du joueur (refus distincts) ; on identifie aussi qui l'on verrait en se tournant vers sa
  voix (la lumière, pas le noir). Bancs contre `integration` (8 h) : aucune usurpation ni
  violation ; par nuit 4 appels au Relais, 7 à la mine, 17 à l'auberge, 9,8 à la crue ; minutes
  sans recours Relais 401 → 404, mine 636 → 665, auberge 581 → 628, crue 273 → 293 (des
  recherches qui aboutissent plus tôt laissent attendre une part promise ou refusée) ; vols vus
  inchangés hors la crue (1,5 → 1,3) ; minutes dans l'eau 318 → 259. Détail et limites dans
  `docs/plan-ouie.md`.
- Branche `rejeu-enrichi` (observation seule : `rejeu.py`, `web/rejeu.html`, option du banc) : le rejeu
  note la lumière de chaque case (même degrés que la page de jeu, recalculés quand sources, portes ou
  obstacles changent), chaque bruit émis avec ce que chacun qui l'a entendu en a fait (vu, attribué,
  retourné, bruit retenu, parole saisie, avec le niveau parvenu), les gestes illicites (qui était là, qui
  les voyait, qui en a été témoin et quand) et les « aller voir ». La page colore le sol, dessine une onde
  par bruit, montre ce que le personnage choisi entend et filtre le journal par personnage et par nature.
  `--rejeu` avec `--graines` écrit une page par graine. Une nuit de 8 h pèse 420 à 450 Ko (bruits 77 Ko,
  esprits 134 Ko, vues 73 Ko, lumière 4 Ko) ; la nuit reste identique (empreinte). Constats sur le Relais
  (graines 7 et 1985) : un « vol vu » compte un souvenir par geste d'une minute et par témoin, d'où 12 pour un
  seul cambriolage vu par deux personnes (graine 7, min 122 à 128, Brune forçant la réserve de l'antichambre) ;
  Brune guette 31 min sans rien tenter tant qu'un témoin est en vue, jusqu'à la faim à 95 (`DESESPOIR`),
  qui lève la précaution ; le fracas du crochetage (geste bruyant, même « sans témoin ») fait se retourner
  Ilse, de dos, qui devient témoin. Les 8 échanges de chaque nuit sont 6 demandes de part à Gorm, plus des
  dons ou la rumeur d'Ilse, au rythme de la faim, pas de la perception. Détail dans
  `docs/plan-vue.md`.
- Branche `banc-luna`, non fusionnée : Luna remesurée sur le moteur actuel (2 passes, `--fil`) et
  un banc `echanges` (parler sans nommer, guillemets, à tous, chuchoter, passage, pousser, donner,
  interpeller dans son dos ; la préparation d'un banc place des personnages et leur regard).
  Défauts communs corrigés : ce que Corvus a dans son dos (vu plus tôt, hors du cône) se nomme et
  se vise comme tout geste (`Monde.designable` : analyse du don, noms, liste d'un refus ; chaque
  souvenir visuel porte son identifiant et `vu_a`) ; une parole se tourne vers celui qu'on nomme
  dans son dos, et à même distance celui qui est droit devant est « en face » ; le récit d'un
  résultat reçoit les gestes exécutés (`gestes_accomplis`), que l'auditeur admet comme le
  narrateur ; écouter dit « contre la porte » ; un support trop loin se dit sans en détailler un
  autre ; patienter a la cible vide ; une citation recopiée avec ses guillemets reste la parole ;
  un refus d'improvisation nomme son seul champ fautif. Trois bancs (31 tours MJ), avant → après :
  3,50 → 3,26 appels et 16,7 → 15,3 s par tour MJ, replis 1 → 0,5, obstacles 14 → 9,5 ; tours
  avec refus 2 → 4, des « approche-toi » justes là où Luna supposait l'objet absent. Banc
  échanges : 2,75 → 3,0 appels, 13,5 → 12,5 s, obstacles 3 → 0,5, et les huit saisies traitées
  (avant : deux « précise à qui tu parles », deux « Ilse n'est pas ici » faux). Reste : la
  faisabilité d'une échelle (« est-ce que je peux… ») sans fait qui l'établisse, décrire un objet
  trop loin passe encore parfois par etablir_faits, un personnage dont la place connue s'est vidée
  n'est plus reconnu par son nom (`paroles._connu_du_joueur`). Les deux premiers : branche `mj-restes` ;
  le troisième : branche `parole-voix`.
- Branche `repli-et-appel`, non fusionnée (vu en partie : « pousse toi ca prend trop de temps »
  finissait sur « Je ne peux pas encore répondre avec certitude. » ; « Aubin, viens m'aider à
  porter l'échelle », Aubin derrière le pilier, finissait en dix appels ; « est-ce que je peux
  fabriquer une échelle ? » partait en conversation où Luna devinait). Trois règles communes.
  **Parole sans conteste** (décidé par l'utilisateur) : une saisie qui commence par des guillemets,
  un verbe de parole (« je dis… », « je lui dis… », « je demande à Gorm… », « je chuchote… ») ou « à
  tous » (`paroles.analyser`, `explicite`) n'est ni un dialogue du MJ ni un geste ; destinataire
  hors de vue : message du moteur sans appel ; MJ obstiné : le moteur prononce les mots du joueur
  (`mj.parole_du_moteur`). Une interpellation sans guillemets (« Brune, pousse-toi ») reste du
  texte libre ; si Luna en fait une parole, le moteur en fixe le destinataire. **Repli du contrôle
  narratif** (trois réponses refusées) : chaque relance reçoit tous les refus du tour ; le joueur
  lit ce que le moteur a établi (résultat, issue d'une parole), sinon les phrases admises de la
  meilleure réponse (`narration.rescape`), sinon ce que Corvus perçoit de ce qu'il vise et ce qui
  manque (`narration.repli`) ; un souvenir visuel est marqué `hors_de_vue` (l'auditeur refusait
  « tu ne la vois pas d'ici »). **Question de faisabilité** (« puis-je… ? ») : Luna propose le
  geste comme s'il était demandé, le moteur le prépare ou le refuse avec sa raison, et le joueur
  voit la même fiche sans rien exécuter (« Rien n'est encore tenté », puis tenter ou annuler) ;
  seules les perceptions répondent tout de suite (`commandes.PERCEPTIONS`). Luna, copies de la
  sauvegarde réelle et bancs ciblés : Aubin en face, « Aubin, viens m'aider… » devient une parole
  (3 appels) ; derrière le pilier, Luna répond qu'elle ne le voit pas (2 appels), « je dis à Aubin :
  … » reçoit le message du moteur (0 appel) ; devant les perches, « est-ce que je peux fabriquer
  une échelle ? » montre la fiche (52 min, sans jet) en 2 appels, « tenter » la fabrique ; trop
  loin, le moteur dit « Approche-toi de la perche… » ; « qu'est-ce que je vois au nord ? » reste
  une conversation (2 appels). Bancs de référence (1 passe, 31 tours MJ) : avant 3 replis, 9
  relances narratives, 3,32 appels par tour ; après 0 repli, 5 relances, 3,35 appels par tour
  (refus du moteur 3 → 7 : les questions de faisabilité passent désormais par lui). Limites :
  l'auditeur reste sémantique ; une interpellation libre peut encore être racontée par Luna sans
  rien faire dire ; « Gorm, je te donne la cloche » entre guillemets reste une parole. Détail dans
  `docs/plan-ouie.md` (« Correctif : ce qui est une parole sans conteste »).
- Branche `entretenir-feu`, non fusionnée (manques de la mine et de l'auberge : Odile et Mireille
  devant un foyer mort sans demander le bois de Joss ; le poêle de Josse tenu seulement par la
  dérive de son devoir ; Mathe servant Lucien en boucle). Trois règles communes. Une pulsion qui
  cesse d'être satisfaite est **rompue** (`esprit["pulsions"]` : True, False rompue, None désir
  jamais satisfait) : il la rétablit sans attendre que son besoin presse, quelle qu'en soit la
  cause (un feu qui baisse, un protégé qui a faim, ce qu'il a ouvert ou emporté lui-même) ; les
  rondes gardent leur routine, un désir attend son besoin. Un feu à entretenir peut employer le
  bois d'un autre : la part de combustible va au feu que le but entretient (le donneur le
  recharge et le rallume), on ne demande pas ce qu'on a sur soi, on ne prête pas ce qu'on garde
  (`echanges.garde`), une parole n'est tenue que sur ce qu'on a constaté depuis (un feu vu vif
  avant la demande se revoit), une part de bois est servie quand on a revu le feu rechargé.
  Servir un protégé : seulement s'il est cru affamé (la faim qui presse se voit, `etat` d'un
  personnage), et il le voit manger ; la pulsion de Mathe est remise. Cas vérifiés après
  rechargement (`tests/test_entretenir.py`) : Mireille demande les fagots de Joss, qui recharge
  le fourneau puis garde sa dernière charge ; Josse, devoir à 10 sans dérive, recharge son poêle
  de ses étais, puis sans étais obtient une part des bûches de Gaspard ; Mathe sert Lucien une
  fois ; Gorm, bois en main et sans flamme, va allumer la torche au lieu de demander des planches.
  Bancs (8 h ; `VERIFIER` sur 5 nuits) : Relais 8 graines, sans recours 428 → 401, événements
  23,3 → 26,5 ; crue 300 → 281 ; mine 668 → 670, poêle allumé 385 → 448 min (Josse obtient le
  bois de Gaspard), Odon, privé d'une part que Mathe a servie à Lucien, force le garde-manger ;
  auberge 573 → 673 : les demandes ont lieu (Joss donne une charge par nuit, Anselme garde les
  deux siennes), les trois foyers brûlent 622 → 710 min, mais le bois manque avant la fin de la
  nuit et le devoir, que rien n'apaise, reste urgent (Odile et Mireille inchangées) ; Anselme
  recharge son poêle à temps, ce qui déplace le crochetage de Lucien. Aucune usurpation. Limites :
  on ne demande que le bois qu'on connaît ; une part de bois promise s'attend 60 minutes si l'on
  n'a pas revu le feu ; une ancienne sauvegarde lit False comme rompue.
- Branche `lumiere-besoin`, non fusionnée, accordée avec `integration` (manque relevé par la mine :
  dans le noir, personne ne cherchait de lumière ; détail dans `docs/plan-planificateur.md`,
  « Lumière ») : une source qui consomme se recharge de ce qu'elle brûle (`perception.recharge` :
  son contenu déclaré, un foyer brûle du bois ; une torche, sans contenu déclaré, ne se recharge
  pas) ; `alimenter` vaut pour le joueur, le MJ, le stratège et les PNJ, verser de l'huile dans la
  lampe aussi. La mine déclare l'huile de ses lampes et un bidon d'huile à la réserve. Dans le noir,
  qui le craint (`peur_du_noir`) cherche à avoir de la lumière (recours de la sécurité, avant
  l'abri) ; le planificateur trouve les moyens par ses gestes : allumer une source à une flamme
  portée ou fixe, la recharger, prendre une lampe, la demander, rejoindre un lieu éclairé. Toute
  minute dans un lieu qu'il croit obscur lui coûte (`NOIR` × sa peur) : il allume sa lampe avant
  une ronde dans le noir ; la lampe qui l'éclaire ne se ménage ni ne se prête. Une salle se croit
  éclairée par ce qui y est posé, pas par ce qu'on y porte (lui ou un autre) : la lampe d'un
  passant ne fait pas éteindre la sienne. Accord avec `entretenir-feu` : la pulsion rompue du
  poêle fait rallumer le feu (part de bois demandée) ; celui qui avait allumé sa lampe la ménage
  alors. Bancs contre `integration` (8 h, `VERIFIER` sur une nuit de chaque scénario, aucune
  usurpation) : Relais 7 graines sur 8 identiques ; sans recours mine 670 → 636, auberge 673 →
  581, crue 281 → 273. Auberge : aux rondes, Odile allume la lampe du comptoir, Hugues sa
  lanterne ; Lucien quitte le grenier noir pour le couloir éclairé, puis va et vient entre sa
  garde et la lumière. Mine : la dernière flamme est le briquet de Gaspard, que personne ne
  retrouve dans le noir ; ceux qui craignent le noir vont vers la lumière dont ils se souviennent
  (le bureau) et Bram n'y est plus seul.
- Branche `feat/websocket-persistant` (Codex, `docs/integration-websocket.md`) : en mode forfait
  ChatGPT, le MJ parle à Luna par une WebSocket Responses persistante (`donjon/transport_openai.py`),
  ouverte au premier appel et partagée par l'interprétation, les audits et la narration. Chaque
  demande renvoie instructions, outils et contexte complets (`store: false`, aucun historique
  serveur) ; seul `response.completed` est validé. Jeton renouvelé, socket fermée ou âgée de
  55 min : nouvelle ouverture ; coupure pendant une demande : une reconnexion et une reprise du
  même appel dans le même délai (45 s pour l'échange entier, et non plus par lecture). Le mode
  API garde HTTP. Microbanc (`tmp-worktrees/ttft-luna-medium`) : premier jeton −32 %, durée d'un
  appel −17,5 % contre HTTP. Vérifié après fusion : deux parties réelles avec une coupure
  simulée chacune (4 ouvertures, 4 fermetures, une seule exécution de l'action).
  Dépendance `websockets` (`requirements-chatgpt.txt`).
- Branche `voix` (`docs/plan-ouie.md`, « Les voix » ; `donjon/voix.py`). Deux manques :
  l'appel par le nom ne passait pas une porte fermée (Hugues appelait Anselme en boucle, Aubin Gorm
  à chaque minute) ; une voix inconnue n'était qu'un bruit, et voir quelqu'un faisait connaître sa
  voix. **Héler** est un cri (nature `hele`, 9 crans) : les mots saisis disent qu'on appelle tel nom,
  sans alarme ; le cri seul est un bruit fort inconnu ; « Ici ! » répond, hélé, et vaut se nommer ; un
  appel sans réponse compte la salle pour parcourue dans la recherche (`deliberation.appels_vains`,
  60 min). **Se parler** = s'entendre (`pnj.peuvent_se_parler`, règle unique) : une voix qu'on ne sait
  à qui prêter est un étranger (`voix.fiabilite`, `voix.INCONNU`), à qui le prudent répond « Qui va
  là ? » (`echanges.accueil`) ; le joueur parle dans le noir, le refus « ne saurait pas qui lui parle »
  disparaît. **Voix** : on connaît la voix de qui l'on a entendu parler en le voyant, ou que le
  scénario fait connaître (un savoir) ; plus à la simple vue ; chacun retient les voix inconnues et ce
  qu'elles prétendent ; toute reconnaissance passe par `voix.reconnaitre` (où se brancheront
  l'imitation et la méfiance). **Se nommer** (contenu `nom`, et `qui` pour « Qui est là ? ») : démasqué
  par la vraie voix, sinon cru sur parole (lieu `se_dit`) sans jamais plus de confiance qu'un inconnu,
  démasqué après coup quand on entend la vraie voix, puis le menteur reconnu. Le MJ ne connaît une voix
  inconnue que comme « voix_<n> » (« une voix qui se dit Brune »), sans identifiant ni traits ; contrôle
  déterministe : sa réplique ne nomme personne au-delà de ce que le moteur a établi, le récit ne lui
  donne pas son nom prétendu (`narration.voix_inconnues`). Plus de migration des anciennes sauvegardes
  (décision de l'utilisateur). Bancs (8 h, 4 graines, avant → après) : sans recours Relais 362,5 → 335,
  mine 665 → 655, auberge 627,5 → 670, crue 292,5 → 301 ; appels / réponses auberge 17 / 2,25 → 3,5 /
  2,75, mine 7 / 0,75 → 2,5 / 2,5 ; aucune usurpation. Luna (copies de scènes) : demande refusée à la
  voix dans le noir, « c'est Corvus » cru sans confiance, « c'est moi, Brune » démasqué, une voix
  inconnue nommée par le moteur puis « la voix » dans le récit ; deux défauts de Luna vus et corrigés
  par le contrôle (voix qui se disait Brune d'elle-même, « Brune répond » dans le récit). Limites dans
  `docs/plan-ouie.md`.
- Branche `echanges-argent`, non fusionnée (manques de l'auberge : un objet prêté restait illicite
  pour l'emprunteur ; l'argent n'existait que pour le joueur ; détail et bancs dans
  `docs/plan-social.md`, « Argent, prêts et garde confiée », règles du joueur dans
  `docs/mecaniques.md`, « Prêter, confier, payer »). **Permissions** (`donjon/biens.py`) : un
  prêt (`data["permissions"]`, clos quand l'objet revient à son propriétaire) ou une garde
  confiée (tâche acceptée sur un bien de qui la confie, pulsion déléguée) font user du bien
  d'autrui sans faute, au plan, à l'exécution, aux yeux des témoins et pour le joueur ; une clé
  prêtée ouvre ce qu'elle ouvre, pas le contenu ; rien ne permet de consommer. Remis par son
  propriétaire, un objet qui dure est prêté, ce qui se consomme donné ; l'emprunteur PNJ le rend
  quand il ne lui sert plus, le propriétaire le récupère en le redemandant ; on ne demande un
  objet qu'à son propriétaire. **Argent** : bourse par PNJ (`finances_pnj`, 5 par défaut),
  objets à pièces, prix d'une part ou d'un objet ; une pièce vaut pour chacun (10 + dette,
  proches, projet pesés par ses valeurs) / (10 + richesse) minutes, au plus 6
  (`caractere.valeur_piece`) ; geste `acheter` du planificateur, vente acceptée au prix sans jet
  sauf ce qu'il garde ou méfiance, don d'autant plus dur que la pièce lui est chère ; dernier but,
  prendre des pièces qui valent plus que le chemin et la faute ; le joueur paie une part, un
  objet ou un passage dans sa parole (`valeur`), au plus son or (`attendu` sinon). Situations,
  bourses et prix déclarés dans les quatre scénarios ; valeurs retouchées à la mine (Odon, Bram,
  Josse, Mathe) et à l'auberge (Anselme, Mireille, Mathurine, Hugues, Lucien, Odile) ; la paie de
  la mine (200) et une bourse d'Anselme (150) ; pas de migration des anciennes sauvegardes.
  Accordée avec `main` après `voix` : une voix inconnue qui offre de payer ou réclame son bien
  s'entend d'abord demander « Qui va là ? » (`echanges.accueil`), puis la vente vaut. Bancs contre
  `main` 1e96cb6 (8 h) : minutes urgentes sans recours Relais 393 → 294, mine 655 → 463, auberge
  670 → 690, crue 301 → 445 ; achats par nuit 1,6 / 1 / 0,75 / 2 ; aucune usurpation ;
  `VERIFIER` sur une nuit de chaque scénario. Au Relais, Ilse et Aubin refusés achètent leur part,
  Brune (honnêteté 20, endettée) vole encore ; à la mine, Odon endetté guette la paie et s'acharne
  sur le coffre dans le noir (mine 15 → 23 s) ; à la crue Brune (50) achète au lieu de voler, d'où
  Gorm au devoir sans rien à faire et Ilse au refuge, dans l'eau, au lieu de la galerie. Limites :
  aucun prêt ni vol de bourse au banc (Odon ne sait pas ouvrir la porte du bureau, personne ne
  connaît la bourse d'Anselme), une part payée non servie n'est pas remboursée, pas de
  marchandage ni de tâche payée entre PNJ.
- Branche `mj-restes`, non fusionnée (`docs/plan-ouie.md`, « Correctif : ce que le MJ ne raconte
  plus sans le moteur ») : les restes des bancs Luna. **Parole** : sans parole de Corvus validée ni
  geste résolu, le récit ne fait pas parler Corvus (« tu demandes à Ilse… », « dis-tu » :
  `narration.parole_racontee`) et, saisie adressée à quelqu'un ou après un refus, personne ne répond
  par une citation nouvelle (`narration.paroles_sans_moteur`, déterministe) ; une interpellation libre
  que son destinataire entendrait, répondue en dialogue, est renvoyée une fois sans contrôle
  (`mj.renvoi`) : parole, geste (« Gorm, je te donne la cloche » → remettre), ou dialogue contrôlé.
  **Détail de loin** : le refus du moteur (détail ou description physique d'un objet hors de portée,
  une cause, `attendu`) passe avant la contre-revue sémantique (`mj.refus_assure`) ; les faits disent
  que de loin les détails d'un objet échappent (un personnage reste décrit de souvenir) ; les
  consignes ne promettent plus la description d'un objet seulement vu. **Faisabilité** : « puis-je… ? »
  (`commandes.faisabilite`) répondu en dialogue est renvoyé une fois ; refusé par le moteur, le joueur
  lit sa raison, pas une explication libre ; un rôle vide d'un assemblage ou d'un franchissement dit
  ce qui manque et s'il y a de quoi le tenir parmi ce que Corvus peut désigner. Le cas « « Gorm, je te
  donne la cloche » » reste une parole (voulu) : « Tu dis à Gorm : « … » », la cloche reste dans la
  besace, Gorm répond sans la prendre. Luna, copies de la sauvegarde réelle : « est-ce que je peux
  fabriquer une échelle ? » (« possible en principe… » → « il te manque un lien… rien de tel n'est à ta
  disposition ici »), perches trop loin (« Oui, une échelle est une possibilité… » → « Approche-toi de
  la perche de bois 1… », 1 appel), mur trop loin (trois refus de la contre-revue, 30 s → refus du
  moteur puis réponse par ce que Corvus voit), « Gorm, je te donne la cloche » sans guillemets
  (« Gorm acquiesce » sans rien changer → la cloche remise). Bancs contre `main` 789be7a, même
  transport (WebSocket), 2 passes, relais + crypte + atelier + échanges (38 tours MJ) : 3,04 → 3,14
  appels et 13,9 → 14,0 s par tour MJ, 0 repli des deux côtés, tours avec refus 6,5 → 6,5, obstacles
  narratifs 2,5 → 5,0 (tous sémantiques, aucun des nouveaux contrôles ; l'étendue des passes couvre
  l'écart) ; l'échelle de l'atelier 3 → 1,5 appel. Trois bancs écartés (coupures réseau, quota).
  Limites : le récit d'une parole est repéré par ses formes (deuxième personne), une réaction sans
  citation (« Gorm acquiesce ») n'est arrêtée que par le renvoi ; la faisabilité ne se juge pas à
  distance (le joueur lit « approche-toi », pas la fiche) ; une règle d'auditeur « personne ne réagit
  sans conversation_validee », essayée, faisait refuser à tort des réponses validées et a été retirée.
- Branche `planif-defauts`, non fusionnée (`docs/plan-planificateur.md`, « Défauts corrigés ») :
  trois défauts du planificateur des PNJ. **Chance crue** : la chance de crocheter est celle du jet
  réel (`pnj.seuil_crochetage`) à la lumière qu'il croit là où il se tient (`lumiere_crue` ; la
  croyance d'une salle porte son niveau, `esprits.constater_lumiere`) ; plus de chance plancher,
  un geste impossible n'est pas envisagé, un essai manqué fait constater la lumière qu'il avait.
  **Portes** : une porte qu'il croit verrouillée se crochète comme un contenant (même chance,
  faute, bruit), puis la route y passe (`pnj.chemin`, `ouvertes`) ; la porte du bureau est à Bram.
  **Pièces crues** : `enrichir` compte la croyance `pieces` (en tenant la bourse, ou savoir : la
  paie de 200 que sait le camp), jamais l'objet. Cas réels et cas de même nature après
  rechargement (`tests/test_planif_defauts.py`), `VERIFIER` sur une nuit de chaque scénario. Bancs
  8 h contre `main` (au même moment) : sans recours Relais 294 → 296, mine 463 → 449, auberge
  690 → 643, crue identique ; essais de crochetage mine 28,5 → 0,75, auberge 31,5 → 0,25 (Odon et
  Lucien s'acharnaient dans le noir), Relais 3,6 → 3,5 ; achats égaux ; vols vus auberge 1 → 0,25
  (plus de fracas à voir) ; aucune usurpation ; temps d'une nuit égal, auberge 28 → 32,5 s. Odon
  envisage la porte du bureau mais le baraquement n'est jamais sans témoin : il renonce (aucune
  porte crochetée au banc). Limites : lumière crue de la case où il se tenait (un essai perdu au
  plus), pas de « forcer » pour les PNJ, contenu d'une bourse appris seulement en la tenant.
- Branche `depart-tire`, non fusionnée (`docs/plan-crue.md`, « Le départ tiré de la graine ») : les
  nuits étaient presque déterministes (au Relais, une seule nuit jusqu'à la minute 5, deux jusqu'à
  120 sur 16 graines ; tout le hasard venait du d20). À la création du monde, le moteur tire le
  départ de la graine par un tirage à part (`donjon/depart.py`, `seed:depart`, les d20 inchangés),
  une fois, gardé dans `data["depart"]` : états du corps (repas, veille, trempé) à 20 % près, besoins
  du profil à 10 points près, périodes de ronde à 20 % près et la prochaine ronde dans la première
  moitié de sa période (au départ déclaré, toutes tombent à la minute 0), échéance des horloges à
  25 % près ; aucun besoin tiré au-delà de 85, sauf déclaré plus haut. Bornes déclarées par les
  quatre scénarios (`depart.bornes`), défauts du moteur sinon ; `depart="fixe"` (constructeurs,
  `banc_pnj --depart fixe`) garde le départ déclaré, et les tests de scène partent de lui. Banc :
  empreintes de l'état aux minutes 5, 60, 120, 240, 480 et issue de la nuit (`divergence`), jets
  par heure ; une pulsion confiée à qui l'on croit fiable compte à part (`minutes_urgentes_confiees`),
  plus « sans recours » ; `echanges` sans les appels ni leurs réponses. Bancs 8 h, fixe → tiré :
  Relais (16 graines) nuits distinctes à 5/60/120/240/480 min 1/2/2/6/10 → 14/16/16/16/16, issues
  4 → 13 ; mine 3/2/2/2/4 → 8 partout ; auberge 1/1/3/8/8 → 8 partout ; crue 2/4/6/7/8 → 8 partout.
  Aucune usurpation ni violation, `VERIFIER` sur une nuit de chaque scénario. Limite relevée : au
  Relais, Gorm n'est plus d'office au refuge à la première minute, et Brune affamée vole dès qu'il
  s'éloigne (minute 3 dans une nuit sur 16, ~30 dans deux) ; jugé dans son caractère, à revoir si
  l'on veut un premier acte plus long.
- Branche `besoins`, non fusionnée (`docs/plan-planificateur.md`, « Dynamique des besoins » ; vu au
  banc : Lucien, à l'auberge, allait et venait entre le grenier noir où il garde ses affaires et le
  couloir éclairé, 19 changements de salle en 4 h). Trois règles communes. **L'effet de seuil**
  (`deliberation.urgents`, `eveiller`, `esprit["urgences"]`) : apaisé, un besoin ne presse de
  nouveau qu'à son seuil + `REPRISE` (15), sauf s'il est d'abord descendu sous seuil − 15 (comblé) ;
  au choix du but, un besoin n'interrompt le plan d'un autre que s'il presse plus que lui
  d'`INERTIE` (5). **Ce qu'un plan laisse monter** (`planification.Vue.pression`, `RESTER` 30,
  `GARDE` 2) : une minute coûte le noir pour qui le craint et chaque lieu gardé dont on est loin ;
  un but qui se tient en restant (lumière, garder, abri, se chauffer) compte 30 minutes de ce que son
  état final laisse monter, et la recherche continue au-delà du premier état qui l'atteint ; pour la
  lumière et la garde, on ne part que si le plan coûte moins que rester (sinon on endure : issue
  « endure » du diagnostic, que `--diagnostic` compte désormais au lieu de planter) ; l'abri compte
  aussi ce qu'il apporte. **L'attente** (`deliberation._classer`, `attentes`) : un besoin dont chaque
  recours a été essayé sans plan attend, sans être oublié ; le banc distingue
  `minutes_urgentes_en_attente` (aucun plan sur ce qu'il croit) de `minutes_urgentes_sans_recours`
  (un plan possible, non entrepris) et des pulsions confiées (`depart-tire`) : chaque PNJ oisif dans
  une seule catégorie. Correctif commun révélé, accordé avec la croyance à niveaux de
  `planif-defauts` en une seule règle (`esprits.constater_lumiere`) : sur place, il juge à la lumière
  de sa case, lueur voisine comprise (`niveau`, chance du crochetage) ; de loin, à ce que la salle
  tient de ses propres sources (`propre`, `eclairee`, `deliberation.lumiere_crue`) : le seuil d'une
  salle obscure ne la fait plus croire éclairée (alternances lumière ↔ abri à l'auberge 15,75 → 0
  par nuit). Cas vérifiés après rechargement (`tests/test_dynamique_besoins.py`) :
  Lucien rapporte la lanterne de l'étable au grenier et y reste (5 changements de salle) ; Bram
  (mine) prend la lampe du filon et revient garder la paie ; sans lumière à emporter, le plus fort
  l'emporte et l'autre besoin attend ; le devoir de Gorm attend puis reprend ; la faim refusée attend
  puis redemande (scènes en départ fixe). Bancs 8 h, départ tiré, contre `main` 87c1ed5 (Relais 8
  graines, autres 4, lancés ensemble) : minutes sans recours Relais 117 → 53, mine 369 → 56, auberge
  665 → 68, crue 81 → 45, le reste passe en attente (oisives totales égales à 2 % près, confiées
  inchangées) ; événements égaux ou en hausse, échanges égaux sauf l'auberge 20,25 → 23,75 ;
  va-et-vient entre deux besoins Relais 8,25 → 8,1, mine 13 → 6, auberge 19,25 → 2,25 (le cas réel de
  Lucien, revenu au banc avec le départ tiré : 70 → 3 en quatre nuits), crue 4,75 → 5,5 (les rondes
  de Gorm) ; vols vus égaux (Relais 0,9 → 1, crue 0,5 → 0,75) ; aucune usurpation ni violation ;
  `VERIFIER` sur une nuit de chaque scénario. Temps d'une nuit (`main` et branche lancés ensemble) :
  Relais 4,8 → 5 s, mine 16,6 → 17,2 s, auberge 18,7 → 21,1 s, crue 6,6 → 6,8 s ; aucun élagage
  exact trouvé pour l'auberge (Lucien refait chaque minute une recherche `garder` que la mémoire ne
  reprend pas, le prix d'une faute variant avec la détresse). Limites : `GARDE` est une constante du
  moteur ; seuls le noir et la garde coûtent par minute ; un besoin apaisé sans être comblé monte
  jusqu'à seuil + 15 (au départ fixe, Ilse hésitait deux fois entre l'abri et le brasero) ; la peur
  du noir ne s'émousse pas ; Odon, qui sait crocheter la porte du bureau, y fait fuir Bram (le test
  de Bram le rend honnête) ; pas de migration, le champ `urgences` vient par défaut. Les échecs de
  `tests/test_tui.py` (« La TUI n'est pas redevenue disponible ») viennent de la charge de la machine
  (attente bornée à 5 s) : les mêmes cinq échouent sur `main` sous charge, tous passent au calme sur
  les deux. Corrigé : branche `parole-voix`.
- Branche `parole-voix`, non fusionnée (`docs/plan-ouie.md`, « Nommer, attendre, héler ») : quatre
  correctifs. **Tests du terminal** : `tests/test_tui.py` attend un état (`attendre`, `pret`) avec un
  délai de 60 s qui tient sous charge, au lieu de 250 tours de 20 ms ; un arrêt du jeu échoue aussitôt
  et l'échec dit l'état observé. Démarrage du jeu ralenti de 20 s : `main` échoue, la branche passe ;
  27 tests sous charge (deux bancs de 8 nuits, 30 processus) et au calme : verts. **Nommer qui l'on
  connaît** : le joueur connaît un personnage vu (`data["personnages_vus"]`, `Monde.identifier`, aussi
  qui n'a été qu'aperçu), dont il connaît la voix ou dont une voix s'est donné le nom
  (`paroles.identites`), jamais d'après une place ; nommer un absent connu donne le refus juste (parole :
  « Tu ne vois pas Ilse d'ici », don : « … n'est pas là pour le recevoir ») ; le MJ reçoit
  `personnages_connus`, sans place. **Qui répond attend** (`deliberation.attendre_l_appelant`, esprit
  `rejoint`) : 5 minutes sur place, sauf un besoin qui presse, la parole due, prévenir, ce qu'il fait sur
  place ; la routine, un bruit à voir, l'argent cèdent aussitôt ; s'il cherche l'appelant et reconnaît sa
  voix, il va vers lui ; fin quand ils se voient ou se parlent, ou à l'échéance. **Le joueur hèle** :
  « j'appelle Gorm », « je hèle Gorm », « je crie le nom de Gorm », « je crie « Gorm ? » »… (analyse locale,
  `paroles.hele`, même en forme de question) sont le geste `emettre_son` méthode `heler`, par la règle
  des PNJ (`pnj.heler` puis `pnj.repondre`) : l'appelé répond « Ici ! » sauf méfiance et l'attend, le
  joueur entend la réponse par l'ouïe commune (« Gorm répond », ou « une voix qui se dit Gorm
  répondre »). Cas réels et cas de même nature après rechargement (`tests/test_parole_voix.py`),
  `VERIFIER` sur une nuit de chaque scénario. Bancs 8 h contre `main` 1ee493b, lancés ensemble : appels
  Relais 1,25 → 1, mine 2,75 → 2,5, auberge 6 → 6, crue 2,75 → 2,25 (12 graines : 2,33 → 1,67 ; graine 3,
  7 → 3) ; 1 à 2 retrouvailles par nuit, attentes vaines 0 à 0,25 ; échanges, minutes sans recours, vols
  vus identiques ; en attente Relais 67,5 → 68,1, crue 105 → 106,25 ; aucune usurpation ; temps égal.
  Luna (copies de la sauvegarde réelle) : « j'appelle Gorm » derrière la porte, 4 appels et « tu ne peux
  pas l'interpeller » → 0 appel et la réponse du moteur ; « j'appelle Ilse » absente, 6 appels → 0 ; « je
  donne la cloche à Ilse » 2 → 0 (refus du moteur). Limites : une interpellation libre d'un absent reste
  au MJ (2 à 10 appels selon les parties) ; l'attente se juge à la minute ; `REJOINT` constant.
  les deux.
- Branche `petits-correctifs-pnj`, non fusionnée (poussée sous `claude/petits-correctifs-pnj-gtlo8g` ;
  `docs/plan-planificateur.md`, « Petits correctifs », et `docs/plan-social.md`, « Une part payée et
  jamais servie »). Quatre règles communes. **Lumière devant la serrure** (`pnj._assez_de_lumiere`) :
  l'étape `crocheter` porte la lumière prévue ; devant, il constate la sienne et la retient de l'objet
  (croyance `lumiere`) ; moindre ou nulle, il renonce sans essai et replanifie (Odon au coffre de la
  paie, Brune à la réserve). **Part payée non servie** : à l'échéance (240 min) ou dès qu'il ne peut
  plus la servir, le vendeur doit le prix (`data["dettes"]`, `biens.rembourser`, `solder`), rendu dès
  qu'ils se savent ensemble ; le joueur le lit ; un PNJ va réclamer son dû (but `reclamer`).
  **Forcer** pour les PNJ (`donjon/force.py`, geste `frapper`) : la règle du joueur partagée, faute
  au prix de l'honnêteté et dégât au prix de la douceur sur le bien d'autrui ; Brune force la porte
  étanche, Gorm sans clé la force pour la cloche. **Gorm et les planches** : diagnostiqué au coût des
  plans ; les vannes, baignées de la lueur diffuse du brasero, étaient crues noires (`propre` compte
  désormais la lueur diffuse, `esprits.lumiere_ici`) et une part demandée comptait comme accordée
  (elle coûte désormais 1 + `DEMANDE` / `PRET`) ; quand ses biens le pressent, `GARDE` le fait encore
  acheter. Bancs 8 h contre `main` (même moment) : sans recours auberge 67,5 → 15, autres égaux ;
  achats en hausse partout (Relais 1,1 → 2, auberge 0,25 → 2,25) ; crochetages à l'auberge 13,5 →
  3,75 essais ; aucun forçage au banc (les PNJ qui prendraient le bien d'autrui ont la douceur à 100) ;
  un remboursement en 8 nuits au Relais ; nuits toutes distinctes ; aucune usurpation ni violation ;
  `VERIFIER` sur une nuit de chaque scénario ; temps mine +20 %. Tests changés et pourquoi :
  `test_entretenir` (Mireille achète au lieu de demander), `test_besoins` (Gorm force la porte, le cas
  sans outil gardé), `test_auberge` (seuil d'événements à 12 : 14 dans cette nuit), `test_mine` (la
  nuit 3, départ fixe : le blessé allume une lampe de rechange à la réserve ouverte au lieu d'appeler
  dans le noir, et Bram est éclairé par celle d'Odon). Limites : la lumière devant une serrure est
  celle qu'il y a vue en dernier (une source posée près d'elle depuis ne compte qu'à son retour ou
  avec la lumière de son plan) ; la chance d'une demande reste une constante (`PRET`) ; forcer ne
  sert qu'à lever une serrure fermée à clé, et abîmer ce qui n'est à personne ou à soi ne coûte que
  le temps et le bruit ; la lueur diffuse est supposée égale dans toute la salle (un recoin qu'elle
  n'atteint pas serait cru en pénombre) ; Gorm achète encore les planches d'Aubin quand ses biens le
  pressent (`GARDE`) ; tout débiteur rembourse, quelle que soit son honnêteté ; le joueur ne réclame
  pas par une parole typée et ne voit la dette qu'au remboursement ; seule une part vendue d'avance
  crée une dette.
- Branche `voix-inconnues`, non fusionnée (`docs/plan-ouie.md`, « Les voix inconnues ») : trois limites de
  la branche `voix`. **Demande d'une voix inconnue** : revue, la part « impossible » de la mine venait de la
  réserve verrouillée (même issue pour une voix connue) ; la règle tenait (étranger, `voix.INCONNU`), vérifiée
  dans le noir comme pour un inconnu vu ; corrigé en route, une part de bois va au feu de la salle d'où vient
  la demande, joueur compris (`echanges.foyer_de`). **Répliques d'une voix inconnue**
  (`narration.voix_inconnues`, `voix.connait_nom`) : le moteur sait qui parle ; la réplique nomme qui son
  locuteur connaît (Corvus seulement s'il lui a donné son nom ou qu'il en a entendu parler), jamais
  elle-même au-delà de ce qui est établi, et ne se dit personne (« je suis… »). **Côté joueur** : voir parler
  quelqu'un fait connaître sa voix (la réponse d'un PNJ à un autre retentit de sa propre voix,
  `social.faire_entendre` ; « Qui va là ? » et « C'est … » chacun de sa voix ; une réplique du MJ d'un
  personnage vu) ; une voix nommée par une autre qui s'adresse à elle dans le même échange est « une voix
  qu'on appelle Gorm » (`ecoute.lier`, `voix.nommer`, ouï-dire), une voix qui dit son nom se dit ainsi ; les
  mots cités d'une parole nette s'entendent tels quels ; juste après un appel de Corvus par son nom, « je
  réponds », « « Ici ! » »… sont le geste de réponse commun (`emettre_son` méthode `repondre`,
  `pnj.repondre_a`), sans le MJ, et l'appelant le croit là. Bancs 8 h contre `main` 888bbc4 (Relais 4 graines
  `--joueur chambre_cloche`, auberge `--joueur dortoir`) : aucune usurpation ni violation, échanges, appels
  et réponses identiques ; trois nuits du Relais et deux de l'auberge identiques, les autres divergent sur
  une réponse qui retentit (auberge : bruits inconnus 117 → 115,75, allés voir 29,75 → 30,5). Luna (copies de
  scènes) : « Qui es-tu ? » à une voix fait nommer Gorm par le moteur, aucun refus du contrôle, Luna ne nomme
  pas de tiers (elle ne sait pas qui la voix connaît) ; « je réponds » 0 appel ; une réponse libre (« je lui
  crie que je suis là ») reste au MJ, qui a fait un cri sans mots ou échoué. Limites : aucun scénario ne fait
  chercher le joueur (cas réel placé d'autorité) ; le nom de Corvus vu se nommer n'est pas retenu ; le MJ
  ignore ce que sait une voix et son genre.
- Branche `audits-attendu`, non fusionnée (`docs/contrat-mj.md`, « Ce que le MJ reçoit d'un refus
  d'audit ») : les refus d'audit suivent le contrat des refus du moteur. Chaque refus du contrôle
  narratif (texte vide, voix d'auteur, nom sans fondement, parole racontée ou citation nouvelle sans
  moteur, voix inconnue, verdicts de l'auditeur), de la portée des ajouts, des capacités et de la
  contre-revue d'action porte un `attendu` (`refus.audit`, `refus.attendu_audit`) : la partie et le
  segment (ou le champ de l'ajout, `proposition.ajouts[0].texte`), la phrase, le nom ou la citation
  reçus tels qu'écrits (`narration.tel_quel`), le verdict et le motif de l'auditeur donnés pour ce
  qu'ils sont, et ce qui serait accepté en identifiants ou citations exactes (destinataires,
  présents, engagements prévus mot pour mot, `parole_prevue.personnage`, clés `objet:<id>` qui
  nomment ce que vise une affirmation sans source, plan reçu de la contre-revue) ; une cause par
  refus (un mot, un nom, une parole racontée, une citation chacun : avant, un refus pour tous). Un
  rapport illisible (`refus.RapportIllisible`, dont `AuditIllisible` et `RapportInvalide`) ne
  reproche rien au texte et le dit ; une proposition mal formée relevée pendant un audit garde
  l'`attendu` du moteur (`refus.depuis_refus`). Le nom d'une entité cachée n'est jamais accompagné de
  son identifiant. `INSTRUCTIONS_REVISION` dit à Luna de suivre `attendu`. Le joueur ne lit jamais
  `attendu` (texte refusé jamais affiché ; repli inchangé). `banc_multi` compte aussi les relances
  narratives et les refus ; `rapport_fil` montre `attendu`. Cas réels et un autre de même nature,
  chaînes complètes après rechargement (`tests/test_audits_attendu.py`) : Ilse et « Pas
  maintenant », « Je vais me pousser », « les faits ne disent… », la voix qui se disait Brune,
  « Prise non demandée » ; invention refusée trois fois (repli), audit illisible, contre-revue non
  conforme puis corrigée. Luna, bancs `main` 4c53791 puis la branche, l'un après l'autre, 2 passes
  chacun, relais + crypte + atelier + échanges (38 tours MJ) : 3,08 → 3,07 appels et 11,3 → 11,5 s
  par tour MJ, 0 repli des deux côtés, relances narratives 4,0 → 3,0 (étendue 2 à 4), tours avec
  refus 6,5 → 7,0, refus du moteur et de la contre-revue 10 → 10,5. Des deux côtés, chaque réponse
  refusée a été corrigée dès la première relance : le banc ne peut pas montrer de gain sur la
  correction, et le nombre de relances dépend surtout des premières réponses, qu'`attendu` ne
  touche pas ; l'écart est dans le bruit. Limites : le verdict de l'auditeur reste sémantique (un
  refus juste ou non reste le sien, cité tel quel) ; les clés proposées pour une affirmation sans
  source sont une indication par le premier mot du nom ; le récit d'une parole de Corvus est cité en
  mots retrouvés dans le texte, sinon sous forme normalisée ; les refus du moteur hors audit sans
  `attendu` (« Réexamine l'intention entière… ») restent tels quels.
- Branche `pnj-lumiere-garde`, non fusionnée (`docs/plan-planificateur.md`, « Lumière et garde ») :
  quatre limites des branches précédentes, diagnostiquées sur les bancs et des copies de leurs états.
  **Lumière dans le noir** : quand le but emploie lui-même un objet (ce qu'il vise, une source ou une
  flamme pour la lumière), on cherche et appelle son porteur perdu de vue, comme pour une part ; et
  l'on **demande du feu** (`demander_feu`, `echanges.demander_feu`) : on tend sa source à qui porte
  une flamme, qui l'y allume sans rien prêter, sauf méfiance (Rémy, le camp éteint, appelle Gaspard
  et allume une lampe de rechange à son briquet ; Joss à l'auberge, au briquet d'Odile). Mine de 11 h :
  appels à l'aide 192 → 96, minutes dans le noir 812 → 696 par nuit. **Lumière devant une serrure** :
  une source qu'il sait allumée ou posée près de l'objet depuis compte de loin (`apport_cru`, la
  croyance `lumiere` retient les sources `allumees`) ; la lueur diffuse par case, le moteur ne la
  connaît que par salle (limite du modèle). **L'échange compte l'éloignement** : Gorm achetait les
  planches d'Aubin parce que le plan d'échange s'arrêtait à l'achat, sans compter l'attente près du
  brasero, loin de ses biens (même sans `GARDE`, 5,66 contre 7) ; une part promise s'attend là où elle
  se sert, ce temps compte avec ce qu'il laisse monter (`Vue.attente_part`), et ne s'explore que si
  elle atteint le but ; Gorm prend ses fagots (Relais 7, 42, 2024). **Un gardien ne laisse pas son
  bien à qui le menace** (`deliberation.menaces`) : un bien dont il a la charge, avec quelqu'un dont il
  se méfie, coûte `GARDE` à tout plan qui s'en éloigne, l'abri n'y gagne pas de quitter cette personne,
  et il appelle à l'aide si sa crainte l'emporte sur son courage (Bram reste, Josse accourt). Cas réels
  et cas de même nature après rechargement (`tests/test_lumiere_garde.py`), `VERIFIER` sur une nuit de
  chaque scénario. Bancs 8 h contre `main` 888bbc4 (lancés ensemble ; mesure `minutes_dans_le_noir`
  ajoutée des deux côtés) : sans recours Relais 53 → 54, mine 59 → 55, auberge 15 → 44 (appels à
  l'aide de Lucien et d'Anselme près de leurs biens menacés, d'où des témoins et des renoncements),
  crue 15 → 15 ; en attente 63 → 66, 290 → 281, 536 → 541, 89 → 108 ; vols vus égaux à 0,25 près ;
  aucune usurpation ni violation ; temps égal à ±14 %. Tests changés : `test_planification` (le plan
  d'une part mène l'attendre près des vivres), `test_constater_rumeurs` (lampe de Josse vide pour
  garder le baraquement noir ; Odon honnête dans la réserve noire, scène partagée avec
  `test_voix_inconnues`, car attendre sa part dans le noir lui coûte un peu plus que forcer le garde-manger). Limites : chercher le porteur
  seulement pour la lumière et ce que le but vise (pas pour un feu : sinon la borne de nœuds) ; pas de
  feu demandé pour une source fixe ; rejoindre qui porte une lampe n'est ni abri ni lumière ; l'apport
  d'une source ignore l'ombre ; l'attente d'une part reste une estimation ; la menace se juge sur où il
  croit les autres.
- Branche `planif-cout`, non fusionnée (`docs/plan-planificateur.md`, « Coût de calcul ») : le temps
  d'une nuit, sans rien changer à ce que décident les PNJ. Points chauds : des recherches refaites à
  chaque minute alors que seul le prix d'une faute ou d'abîmer avait changé avec la détresse (Lucien à
  l'auberge, Odon et Rémy à la mine), la vue du planificateur construite ~10 000 fois par nuit, la
  perception de tous qui relisait l'empreinte de l'état pour chaque PNJ, un trajet qui relisait tous
  les objets à chaque case. **Graphe repris** (`planification._GRAPHES`) : chaque état développé garde
  ses gestes avec les termes de leur coût ; quand seuls ces deux prix ont changé, la recherche se refait
  sur lui, mêmes additions et mêmes égalités, sans recalculer un geste (gardé à la deuxième recherche
  de suite sur les mêmes entrées). Lectures moins chères : la vue (gardes confiées lues une fois par
  propriétaire, aucune vue sans pièces crues ni créance), les gestes (un parcours des salles par départ,
  `pnj.parcours` ; un objet d'une autre salle n'offre qu'une part, `_parts` ; l'état d'un plan comparé
  comme un tuple), la perception de tous dans un seul `etat_fige`, les obstacles d'une salle une fois
  par trajet, le pas sans exception, `monde.copie`. Nuits identiques à `main` 888bbc4 (chronique,
  mesures, état final complet, récit, empreintes, recherches et nœuds) sur 48 nuits (4 scénarios ×
  4 graines, départ tiré et fixe, deux passes tirées) ; `VERIFIER` et `spatial.VERIFICATION` sur 16
  nuits ; `tests/test_planif_cout.py` (Lucien, Odon : même monde avec ou sans graphe après
  rechargement). Temps au processeur, 8 processus, `main` → branche, départ tiré : Relais 14,5 →
  9,2 s, mine 57,3 → 31,7 s, auberge 62 → 26,4 s, crue 15,3 → 10,5 s ; le planificateur passe de 58 %
  à 36 % d'une nuit à l'auberge, de 59 % à 47 % à la mine. Accordée avec `main` 5861f71
  (`pnj-lumiere-garde` : la part promise passe dans `_parts`) : empreintes identiques sur 32 nuits
  (tiré et fixe), `VERIFIER` sur une nuit de chaque scénario ; départ tiré, 4 processus au plus :
  Relais 11,7 → 7,2 s, mine 70 → 39,5 s, auberge 47,3 → 24,2 s, crue 12,6 → 9 s. Limites : une recherche neuve coûte
  toujours ~100 µs par état (mine graine 7 : Josse, deux recherches de 4 000 nœuds par minute en fin de
  nuit) ; une croyance nouvelle refait tout ; pic de mémoire 30 → 59 Mo (mine, graine 7) ; la
  perception reste un tiers d'une nuit.
- Branche `ouie-commune`, non fusionnée (`docs/plan-ouie.md`, « L'ancien son fondu dans l'ouïe
  commune ») : appel à l'aide, cri, sifflement du joueur, son d'un objet (selon sa sonorité,
  `ouie.SONS`) et son improvisé retentissent par l'ouïe commune ; `sons.portee`, l'humeur forcée, le
  souvenir `son`, `esprits.entendre` et `pnj.reagir` disparaissent. Un appel porte la voix : qui la
  connaît sait qui crie. Le réflexe déclaré devient le seuil d'alerte du profil (`alerte`, en crans) :
  un bruit à ce niveau, ou l'appel reconnu d'un protégé, envoie voir avant tout le reste
  (`deliberation.alarme`, but `voir`) ; Hugues migré (`reaction_son` 2 → `alerte` 3). L'appelé se
  tourne vers la voix ; la réponse au joueur hélant se décide à la fin de ses 3 secondes. Bancs
  contre `main` : Relais et crue mêmes nuits (l'appelé se tourne vers la voix) ; mine, les protecteurs
  de Lucien accourent par le but « voir » (allés voir 13,75 → 18,25) ; auberge, Hugues 68 → 54 « va
  voir », sans recours 43,8 → 30 ; aucune usurpation ni violation ; `VERIFIER` sur une nuit de chaque
  scénario. Limites : un personnage sans profil retient le bruit sans réagir ; seuil d'alerte
  constant ; l'appelé d'une autre salle se tourne vers le seuil.
- Branche `echanges-suite`, non fusionnée, accordée avec `main` 099dad8 (`docs/plan-social.md`, « Suite
  des échanges » ; règles du joueur dans `docs/mecaniques.md`, « Prêter, confier, payer ») : six limites
  de `echanges-argent` et `petits-correctifs-pnj`. **Rendre est un choix** (`biens.garde_du`, `regler`) :
  garder l'argent dû est une faute au prix de l'honnêteté contre ce que valent ces pièces ; réclamé, le
  débiteur qui garde refuse, le créancier s'en méfie et le confie (nouvelle `dette_niee`). **Une règle
  pour toute contrepartie** : `paye` et la dette portent `quoi` (part, objet, tâche) ; un objet que le
  vendeur ne porte pas se vend d'avance et se remet (`echanges.differee`, condition `remettre`,
  `planification._remettre`). **Tâche payée entre PNJ** (`echanges.engager`, geste `engager`) : pour une
  pulsion à soi sur ce qu'on pourrait faire sans faute ; acceptée si les pièces valent pour l'autre ce
  que la tâche lui coûte (`devis_pulsion`), sauf méfiance ou ce qu'il garde ; engagement payé d'avance,
  dû à l'échéance ; le payeur ne la fait pas à sa place (`deliberation.tache_payee`). **Prêt réclamé** :
  un prêt échu (240 min) se réclame au joueur comme à un PNJ (but `reclamer`, `echanges._avec_joueur`) ;
  qui le garde perd la confiance (`biens.prets_reclames`, nouvelle `pret_garde`). **Le joueur réclame**
  par la parole (contenu `reclamer`, `attendu` si le sujet est inconnu) et voit ses comptes sur sa fiche
  (`biens.comptes_joueur`). **« As-tu du bois ? »** (`echanges.enqueter`, `planification.s_enquerir`,
  contenu `ressource` pour le joueur) : recours de la faim, du froid et d'un feu quand le plan échoue ; la
  réponse dit ce qu'il a vraiment, le demandeur l'apprend par ouï-dire. Cas réels et cas de même nature
  après rechargement (`tests/test_echanges_suite.py`, 21 tests), `VERIFIER` sur une nuit de chaque
  scénario. Bancs 8 h contre `main` 099dad8, l'un après l'autre : tâches proposées / acceptées par nuit
  Relais 2,6 / 0,4, mine 4,8 / 0,25, auberge 38 / 1 (faite), crue 2,75 / 1 ; « as-tu… ? » 2,4 / 13 / 22 /
  2 ; minutes en attente 66 → 58, 279 → 273, 541 → 298, 108 → 69 ; sans recours égales sauf l'auberge
  30 → 60 ; achats égaux ; aucune dette née au banc ; aucune usurpation ni violation ; temps Relais 8,7 →
  9,3 s, mine 24,9 → 25,2 s, auberge 20 → 26,2 s (offres « impossible » répétées, l'auberge à court de
  bois), crue 9,2 → 10 s. Luna (2 parties courtes sur des copies, `tests/data/bancs/comptes.json`,
  `ressources.json`) : « Gorm, rends-moi… » typé `reclamer`, Gorm rend (5 appels) ; « « Brune, tu me dois
  deux pièces… » » : refus du moteur, Brune refuse (3) ; « Aubin, as-tu du bois ? », « je demande à Brune
  si elle a de quoi manger », « Aubin, tu me dois quelque chose ? » typés `ressource` et `reclamer`,
  tranchés par le moteur (3 chacun). Limites : le payeur paie la peine qu'il estime, sans marchandage ;
  ce qu'on consomme de ses biens pour une tâche n'est pas compté ; pas de tâche « aller voir » ; le
  joueur ne prête ni ne paie de tâche ; la réponse ne dit que ce qu'il croit avoir ; constantes à régler.
- Branche `voix-suite`, non fusionnée (`docs/plan-ouie.md`, « La suite des voix ») : quatre limites des
  branches de voix. **Noms retenus** (`voix.apprendre_nom`, `noms` de l'esprit) : un PNJ retient le nom de
  qui il sait être lui, quand il l'entend se nommer (il le voit ou reconnaît sa voix), qu'une autre voix
  l'appelle ainsi, ou qu'une voix qui s'était dite ou qu'on avait appelée ainsi se révèle la sienne ;
  `connait_nom` les lit (Gorm, qui a vu Corvus se nommer, peut l'appeler Corvus dans le noir). **Une règle
  pour relier les voix** (`voix.lier`, `parole_saisie`, `mots`, `nom_dit`) : « une voix qu'on appelle Gorm »
  s'apprend par la même fonction pour le joueur (`ecoute.lier`) et les PNJ (`ouie.retentir`, `echange` de
  l'esprit, le temps d'un échange) ; ce qu'on saisit des mots, une règle commune (la réplique du joueur
  passe en `dits`). **Vers l'appelant** (`ouie._vers_qui_l_a_hele`) : hélé, on se tourne vers l'appelant si
  on le verrait ainsi, même au-delà d'un seuil, sinon vers le seuil ; qui attend d'être rejoint se tourne
  vers l'appelant qu'il entend approcher dès qu'il le verrait. **Genre d'une voix inconnue** (`voix.genre`) :
  le MJ reçoit « masculin » ou « féminin » (`interlocuteurs.voix_<n>.genre`, `esprits_interlocuteurs`), ce
  que la réplique fait entendre, sans identité. Cas réels et cas de même nature après rechargement
  (`tests/test_voix_suite.py`, 14 tests), `VERIFIER` sur une nuit de chaque scénario. Bancs 8 h contre
  `main` 8c108c3, l'un après l'autre (Relais 8 graines, auberge 4) : toutes les mesures d'avant identiques
  graine par graine, sauf un retournement de moins à l'auberge ; qui attend se tourne vers qui l'avait
  hélé 0,25 fois par nuit ; à l'auberge, 1,75 voix « qu'on appelle … » par nuit pour les PNJ ; aucune
  usurpation ni violation ; temps égal. Limites : « Ici ! » surpris vaut se nommer pour un PNJ, « qu'on
  appelle » pour le joueur (écart gardé) ; une voix « qu'on appelle » ne situe personne ; les répliques du
  MJ ne retentissent pas pour les PNJ ; genre sans timbre ni âge, son emploi par Luna non vérifié.
- Branche `banc-luna-soir` (contrôle seul, rien corrigé ; [rapport](banc-luna-soir.md)) : Luna sur `main` 8c108c3,
  3 passes des quatre bancs de référence : 3,14 appels et 11,1 s par tour MJ, 0 repli, relances 4,7, tours avec
  refus 7,0 (audits-attendu : 3,08 / 11,3 / 0 / 4,0 / 6,5) ; bancs ciblés `soir-appel`, `soir-noir`, `soir-voix`.
  Défauts relevés : vocatif en fin de phrase ignoré (« as-tu de quoi manger, Ilse ? » va à Aubin), vocatif d'un
  inconnu ignoré, planche achetée donnée au feu, question à la cantonade dans le noir jamais répondue, refus de
  format affiché pour une question de faisabilité, silences affirmés après un refus de l'auditeur, « aucun passage
  praticable » quand aucune sortie n'est connue, « c'est moi, Brune » typé en se nommer, « as-tu du bois ? » sans
  les planches qu'on possède.
- Branche `audit-nuits`, non fusionnée, audit sans correctif ([rapport](audit-nuits.md),
  `tools/audit_nuits.py`) : 192 nuits de 12 h (4 scénarios, 48 graines), contrôles activés. Aucun
  plantage du moteur, aucune violation de `Monde.verifier`, aucun écart de `spatial.VERIFICATION` ;
  `planification.VERIFIER` échoue à la mine (15/16) et à l'auberge (11/16) : `emplois` ajoute la
  recherche du porteur d'une lampe (`moyen_du_but`), et sa référence s'arrête à la borne de nœuds.
  Boucles et absurdités relevées : appels à l'aide sans fin, aller voir ↔ garder, prévenir en boucle,
  bruit de sa propre salle jamais examiné, vol à une case dans le noir jamais découvert, tâches payées
  acceptées puis non faites, PNJ piégés par l'eau à la crue.
- Branche `parole-corrections`, non fusionnée (`docs/plan-ouie.md`, « Corrections de la parole » ;
  `docs/contrat-mj.md`) : les défauts de parole du [banc Luna du soir](banc-luna-soir.md). **Vocatif où
  qu'il soit** (`paroles._vocatifs`) : un nom détaché par une virgule désigne le destinataire, en fin de
  phrase comme en tête (« as-tu de quoi manger, Ilse ? »), sauf après « moi, » (« c'est moi, Brune » se
  nomme). **Nom inconnu** : un vocatif ou « je dis à X » qui nomme un personnage que Corvus ne connaît pas
  donne « Tu ne connais personne du nom de X ici », jamais un autre destinataire. **Nommer une voix**
  (`voix.porteur_du_nom`) : nommer X quand seule une voix qui s'est dite X est là, c'est s'adresser à
  elle, pour une parole comme pour un don (la règle de la branche `voix` « il ne peut s'adresser à Brune
  qu'il ne sait pas là » est remplacée) ; un absent : « Tu ne vois pas X d'ici », plus « n'est pas là ».
  **Répondre à la cantonade** (`paroles.repondants`) : une parole sans destinataire nommé qui appelle une
  réponse (« ? », contenu `qui`, `ressource`, `demande`…) est entendue de qui en saisit les mots ; il
  répond sauf méfiance (`voix.repond`, la règle de l'appel), selon la règle d'un destinataire ; Corvus
  entend sa voix et peut lui parler ensuite. **Ce que reçoit l'auditeur** : `conversation_validee.repondent`
  et `issue` (attestée), `a_portee_de_main` (au lieu de `a_portee`), `a_portee_de_voix`,
  `salle.sorties_connues`. **Refus de forme** (`refus.RefusDeForme`) : corrigé à part, jamais affiché ;
  une question de faisabilité garde la raison du monde. **Sorties** : « Sorties que tu connais : aucune
  pour l'instant ». **Se nommer** (`paroles.verifier_nom`) : le nom est celui que disent les mots ; un
  `nom` contredit ou absent des mots est refusé, un nom non typé ajouté. Faibles : « je réponds » seul
  n'est plus une parole sans conteste ; « je » hors des répliques est une voix d'auteur. Cas réels et cas
  de même nature après rechargement (`tests/test_parole_corrections.py`, 22 tests ; suite après fusion de `main` 8589ca2 : 1171 tests). Luna, 2 passes,
  `main` 0489fea puis la branche (9 tours en panne serveur écartés côté `main`) : 4 bancs de référence
  2,99 → 3,24 appels et 14,2 → 15,0 s par tour MJ, replis 0 → 1, relances 3,5 → 6, refus 8,5 → 11 (la
  correction à part d'un refus de forme, au Relais) ; soir-noir 4,2 → 3,3 appels ; la voix d'Ilse répond
  dans le noir 2/2, « as-tu de quoi manger, Ilse ? » va à Ilse 2/2, imposture démasquée 4/4, aucun « aucun
  passage praticable » affiché. Limites : vocatif lu à la virgule ; un nom inconnu n'est refusé que s'il
  est celui d'un personnage du monde ; répondre à la cantonade se décide sur la seule méfiance ; le
  silence d'un destinataire n'est arrêté que par l'auditeur ; « je réponds » sans appel reste une parole
  que Luna remplit de ses mots ; « est-ce que quelqu'un a du bois ? » va à celui d'en face.
- Branche `refus-retenus`, non fusionnée (`docs/plan-social.md`, « Des refus retenus selon leur cause ») :
  à l'auberge sans bois, les offres « impossible » se répétaient toutes les deux heures comme un refus
  d'humeur (38 par nuit, sans recours 30 → 60). **Un refus se retient selon sa cause** (`deliberation.
  retenir_refus`, `tient`, `moyens_crus`), d'après ce que croit le demandeur : ce que l'autre ne peut pas
  ou garde (« impossible », « absent », « eteinte », « rien », « necessaire ») tient tant qu'il ne croit aucun
  moyen nouveau de sa demande (une ressource apprise, l'autre vu avec du bois, une porte crue ouverte ;
  perdre un moyen ne lève rien), sans délai ; « cher », pour ce prix seulement : il offre au moins le
  double (`planification.SURENCHERE`) s'il le peut ; méfiance et humeur, `REDEMANDE`. La dernière
  réponse de chaque demande est gardée à part des souvenirs (`esprit["refus"]`), une demande accordée
  l'efface ; même règle pour part, objet, prêt, achat, feu, « as-tu… ? », tâche payée ou confiée ; le
  passage et la créance sans le sou gardent le délai (place momentanée ; argent d'autrui invisible).
  Deux défauts du banc Luna du soir corrigés dans les mêmes fichiers : une part de combustible achetée
  est remise à l'acheteur (`echanges._vendre_part`, `detacher_part`) ; seule une part demandée pour un
  feu va au feu ; on sait ce qu'on porte et ce qui est à soi à portée de main (`echanges.siens_a_portee` :
  Aubin dit avoir ses planches). Cas réels et cas de même nature après rechargement
  (`tests/test_refus_retenus.py`, `tests/test_parts_achetees.py`), `VERIFIER` sur une nuit de chaque
  scénario (auberge : graine 42 ; 1985 et 7 s'arrêtent sur le défaut V1 de l'audit, d'une recherche à
  `emplois`, pas de cette branche). Défaut A3 de l'audit des nuits : un devis de tâche payée ne compte que
  sur ses moyens et ceux du payeur (`devis_pulsion`, `chercher(seul=…)`), et une tâche qu'on ne voit plus
  comment faire est rendue aussitôt (`echanges.empeche`). Bancs 8 h contre `main` 0489fea, l'un après
  l'autre : refus répétés à l'identique auberge 24,75 → 1,75 par nuit (mine 3,75 → 1,25), « as-tu… ? »
  sans rien auberge 20,5 → 11, offres de tâche 38 → 26, sans recours 60 → 43,8 ; tâches acceptées sur le
  bois d'un autre refusées (Relais 0,4 → 0, crue 1 → 0,25), d'où plus de minutes en attente (Relais 58 →
  69, crue 67,5 → 99) ; aucune usurpation ni violation ; temps égaux sauf une nuit d'auberge plus active.
  Limites : un refus retenu ne s'oublie pas tant que rien de nouveau n'est cru ; la surenchère peut payer
  le double du nécessaire ; une part sans pièce décrite est remise sous le nom du lot.
- Branche `ouie-temoins`, non fusionnée (`docs/plan-ouie.md`, « Témoins par l'ouïe, le bruit de sa salle,
  l'examen vain » ; défauts A1, A2 et B2 de `docs/audit-nuits.md`). **Un bruit se situe à une case** :
  entendu de sa salle même, il est retenu avec sa case et s'examine, comme celui d'un autre lieu, selon le
  devoir et le courage (`deliberation.bruit_a_voir`, `alarme`) ; aller voir mène à portée de vue de cette
  case, ou au contact dans le noir (`planification.voir`, étape `inspecter` avec `vers`). **Témoin par
  l'ouïe** (`pnj._temoins_a_l_oreille`) : le registre porte le bruit de chaque geste ; qui l'entend tant
  qu'il dure, dans la salle même, et croit l'objet tout près de là sait qu'on y touche ; il ne nomme
  l'auteur que s'il le croyait là (`vu_agir` marqué `par` « ouie », méfiance `entendu`, nouvelle de rang 1),
  sinon il sait seulement qu'on touche à ce bien (`entendu_agir`). L'auteur d'un geste sans témoin compte
  ceux qu'il croit à portée d'oreille (`pnj.oreilles_crues`). **Être allé voir règle le bruit** : un examen
  vain (`examen`) couvre le même bruit, ou un moindre, du même lieu ; seul un bruit nouveau relance
  (`ouie.couvert`). Correctif révélé : ce que les PNJ voient du geste du joueur est daté de son début
  (`moteur._terminer_etape`), sinon la minute d'une croyance dépendait du découpage. Cas réels et cas de
  même nature après rechargement (`tests/test_ouie_temoins.py`, 12 tests) ; `VERIFIER` sans écart sur une
  nuit de 8 h de chaque scénario (graine 7, `main` aussi). Audit 32 nuits de 12 h, `main` 0489fea →
  branche : retours voir le même lieu à moins de 30 min Relais 7,6 → 1,1, mine 63 → 22, auberge 58 → 16,
  crue 4,6 → 1,9 ; gestes illicites d'un présent ni vus ni entendus 1,3 / 4,4 / 7 / 0,5 → 0 / 0,1 / 0,5 /
  0,1 ; aucun plantage, violation ni usurpation. Effets : les voleurs attendent qu'on ne les entende plus,
  d'où des crochetages manqués doublés au Relais et à l'auberge (réussis égaux) et, à l'auberge, minutes
  sans recours 61 → 154 (Lucien renonce près d'Anselme). Limites : au contact dans le noir on n'identifie
  personne ; l'appel à l'aide répété (B1) reste. Tests d'autres branches adaptés : `test_ouie`,
  `test_constater_rumeurs`, `test_dynamique_besoins`, `test_besoins` (raisons dans le plan).
- Branche `verifier-eau`, non fusionnée, accordée avec `integration` f5cf65f (`docs/plan-planificateur.md`,
  « VERIFIER et l'eau » ; `docs/plan-crue.md`, « L'eau dans tous les plans ») : défauts V1 et A4 de l'audit
  des nuits. **`VERIFIER`** : `emplois` ajoutait des gestes (chercher le porteur d'une flamme, les flammes
  non superflues) que la recherche complète n'offrait pas ; ce que le but demande se lit du but
  (`vises={"eclairer": True}`, `Vue.eclairer`), `emplois` ne fait plus que borner ce qu'on porte. La
  référence est la recherche complète du même but bornée à 60 000 nœuds (`REFERENCE`), comparée par le
  coût (à égalité, l'ordre de découverte diffère nécessairement) ; un résultat repris de la mémoire ou du
  graphe doit égaler exactement une recherche refaite ; une recherche jouée qui atteint sa borne est notée
  (`planification.BORNES`), pas tenue pour fausse. Nuits identiques (Relais, mine, auberge : empreintes
  des 8 graines). 32 nuits de 12 h : 0 écart (avant mine 15/16, auberge 11/16), 161 recherches bornées
  reconnues (Lucien, Josse, Odon) ; `test_lumiere` (Lucien et Josse dans la mine noire) passe. **L'eau** :
  l'eau attendue (`eau.attendue`) coûte à tout plan par minute comme le noir ; un but qui se tient en
  restant ne se tient pas où on la croit ou l'attend (ni se chauffer, ni une part de bois pour ce feu) ;
  pas de descente vers une salle qu'on attend noyée ou d'où le retour serait coupé, ni vers un lieu coupé
  du plus haut qu'on puisse gagner (`Vue.descente`, `piege`) ; qui attend sa salle noyée en sort avant
  tout (`eau.en_peril`, repli vers le moins d'eau). Crue, audit 12 h, 8 graines : se chauffer dans l'eau
  7 nuits sur 8 → 0, minutes à 86 cm ou plus 128 → 14 par nuit, appels à l'aide 94 → 2, aucun PNJ une
  heure à 50 cm ou plus ; banc 8 h : dans l'eau 589 → 507, appels à l'aide 7,4 → 0,1, en attente
  188 → 520 (le froid : plus de feu hors de l'eau), aucune usurpation ni violation, temps égal. Cas réels
  et de même nature après rechargement, même laps découpé (`tests/test_verifier_eau.py`). Limites : l'eau
  ne coûte que par la salle d'arrivée ; le plus haut lieu ignore les portes au-delà de ce qu'il peut
  ouvrir ; désœuvré dans une eau qui ne noie pas sa salle, il attend que sa sécurité presse ; la crue n'a
  qu'un foyer, le froid attend.
- Branche `deliberation-evenements`, non fusionnée (`docs/plan-temps.md`, « Correctif : délibérer à
  l'événement ») : le jalon temps fin prévoyait que les PNJ réfléchissent à la fin de leur plan, à un
  geste manqué, à un événement et au moins chaque minute ; seule la minute était faite. `deliberer`
  (la minute : besoins, corps, effet de seuil) appelle `choisir` (le but, sans faire passer le temps),
  que `pnj._avancer` appelle aussi à l'instant : plan fini, geste manqué (non retenté avant la minute,
  `esprit["manque"]`), et à la fin du geste en cours, ou aussitôt s'il attend (`esprit["veille"]`), après
  un événement (`esprits.reconsiderer`, `esprit["eveil"]`) : bruit interprété, quelqu'un qui entre dans
  son regard ou en sort, porte ou feu qui change sous ses yeux, absence, son bien aux mains d'un autre,
  geste illicite vu, parole adressée ou qui lui apprend quelque chose ; ce qu'il voit changer de son
  propre geste ne l'éveille pas. Le filet de la minute reste ; aucun franchissement de seuil n'est un
  événement. Gestes qui durent : achevés ou impossibles, il choisit aussitôt. Ordre : le temps, puis les
  identifiants à un même instant. Même laps découpé, même monde : tout est dans l'esprit ; la perception
  du résultat d'une action du joueur se fait à son début (elle se datait de sa fin, selon le découpage).
  Dans la foulée : guet compté une fois par minute (`patience`), regard autour de soi quand un événement
  réveille celui qui guette, un bruit du lieu où l'on est venu le voir reste à voir à l'arrivée, une
  parole tenue sur ce qu'on a vu la minute suivante, la chronique datée à l'instant. Deux boucles de
  l'audit corrigées : un appel à l'aide ne se répète pas tant que dure le même désarroi (B1) ; on ne
  prévient une victime que de ce qu'elle ignore (B3). 18 tests après rechargement
  (`tests/test_deliberation_evenements.py`), `VERIFIER` et `spatial.VERIFICATION` sans écart sur une nuit
  de chaque scénario (après `verifier-eau`). Bancs 8 h contre `main` 4261bf5, l'un après l'autre : allés
  voir +1 à +34 %, minutes en attente égales ou en baisse, sans recours en hausse (auberge 40 → 75 : Lucien
  guette, renonce, attend son répit) ; un tiers à la moitié des choix se font entre deux minutes ;
  temps d'une nuit Relais 10,5 → 9,7 s, mine 25 → 34 s, auberge 26,8 → 31,9 s, crue 10,3 → 12 s (une
  vue du planificateur par choix ; une reprise du choix entier serait la suite). Restent à la minute : corps et
  besoins, combustion, crue, horloges, échéances, dates des croyances, patience et répit.
- Branche `tension-relais`, analyse non fusionnée (`docs/analyse-relais.md`, `tools/tension_relais.py`) :
  une nuit du Relais n'a de hasard que ses jets (7,7 par nuit) ; 48 graines font 2 nuits jusqu'à
  120 min, 27 à 480, 7 issues, et les branches se rejoignent en deux heures ; la faim fixe les
  demandes à heure fixe, Brune vole quand sa faim passe 95. Variantes de données mesurées (feu à
  nourrir, réserve aux vannes, faims décalées, valeurs graduées) et sept manques du moteur en
  invariants (tirage du départ, risque d'être vu pesé, tort qui ouvre des buts…), à trancher.
- Branche `reverification` (contrôle seul, rien corrigé ; [rapport](reverification.md)) : `main` ec2352e après
  les fusions de la nuit, 64 nuits de 12 h (4 scénarios × 16 graines, `VERIFIER` continu sur 16) et 48 de
  référence (`main` 0489fea), Luna 2 passes de neuf bancs. Aucun plantage, violation, écart de `VERIFIER`
  ou de `VERIFICATION` ; B1, B2, A1, A2, A4 et V1 de l'audit confirmés corrigés. Nouveaux : ouvrir/fermer le
  garde-manger toutes les 2 s (mine 42, Odon et Mathe, délibération à l'événement), aller-retour lumière ↔
  abri à chaque seconde (crue 3), surenchère jusqu'à 64 pièces et tâche acceptée puis aussitôt due (13
  auberges sur 16), le lieu d'un bien redit en boucle à qui l'a posé (variante de B3). Luna : 4 bancs de
  référence 3,25 appels, 15,1 s, 0,5 repli, relances 5,5 (au niveau de `parole-corrections`) ; défauts du
  soir corrigés sauf silences de l'auditeur, « je réponds », « quelqu'un », « geste d'effort » ; nouveaux :
  un PNJ vu nomme Corvus sans le connaître, « Aubin remet … à Corvus » lu par le joueur.
- Branche `relations-socle`, non fusionnée (sous-étape 3a de `docs/plan-relations.md`, « Fait ») : le
  socle des relations, sans changer le comportement. `donjon/relations.py` est le seul accès à ce qu'un
  personnage éprouve envers un autre : lectures (`envers`, les cinq axes confiance, affection, rancune,
  peur, dette ; `percue`, qui remplace `voix.fiabilite`, retirée ; `se_mefie`, `se_fie`, `en_veut`,
  `craint`, `doit`, `fiable`, `connus`, `croyance`) et écritures par cause nommée (`eprouver` sur la table
  `EPREUVES` : témoin, geste entendu, vol découvert, mensonge, imposture, rumeur, aveu, poussée, vol
  surpris, dette niée, prêt gardé, part servie ; `avis` pour « X est / n'est pas fiable » cru). En 3a, la
  relation reste portée par la croyance `fiable`, traduite (vrai 70, absente 40, faux 15 ; voix sue
  menteuse 0) ; rancune, peur et dette restent à 0. Tous les sites y passent (persuasion, refus, confidences
  et rumeurs, ouïe, appel, passage, sécurité, abri, délégation, tâche payée, humeur `vol.mefiance`, Luna
  `esprits_interlocuteurs`, stratège, récit, `mefiances` du banc, gestes du planificateur `Vue.se_mefie`) ;
  une lecture générique par attribut passe par `esprits.croyance`. `tests/test_relations_socle.py` (8
  tests) : aucun code du jeu ni des outils ne nomme plus l'attribut hors du module ni ne lit ou écrit la
  croyance en direct (le même contrôle en relève 42 sur `main`) ; traduction ; Gorm qui voit ses vivres
  aux mains de Brune (refus d'office, DD +6, « peu fiable » pour Luna) et son marteau dans la main du joueur
  (humeur), après rechargement. Nuits identiques à `main` 0551ba2 (chronique, récit, souvenirs, état final
  complet, empreintes, mesures) sur 36 nuits de 8 h : départ tiré (Relais 8 graines, mine, auberge, crue 4)
  et fixe (4 × 4) ; `VERIFIER` et `spatial.VERIFICATION` 0,2 sur une nuit de chaque scénario, sans écart ;
  audit 12 h (4 × 4) identique. Temps égaux au bruit près (machine chargée par d'autres calculs). Limites
  dans `docs/plan-relations.md`.

## Décisions prises le 2026-10-28

- **Lot 195 (ouïe des compagnons) : reprendre** (lot 233). Garder l'attribution d'un pas à un compagnon cru proche, mais ce bruit reste une information de présence utilisable pour les initiatives sociales : on ne perd pas la rencontre (S du hameau 40,5 → 27 sur la livraison 195).
- **Feuille de route (point du 28)** : A0, A1, A2 = 3e, A3 = 3f faits ; A4 fait pour l'essentiel (restent suivi vocal, interposition devant un lieu, ouï-dire des fins de garde) ; A6 et 3d partiels ; A5, A7, A8 non commencés. Ordre retenu : (1) clore la consolidation : vérification 241, avancer `main` si elle est propre, petits lots qui en sortent et lot C du diagnostic 237 ; (2) **A5, mandat et autorité**, suite du lot 242, épreuve de la crue étendue au hameau (Gorm confie Brune à Aubin) ; (3) 3d (la peur chez un proche) et A6 (occasion, soupçon déduit) ; puis A7/A8. Le MJ reste en veille.
- **Lot 233 (reprise 195) : accepter la perte de richesse au hameau** (S 35 → 27,75). Les rencontres nées de retournements fortuits ne sont pas une source légitime ; cinq écarts d'oracles/prémisses arbitrés sur la reprise après `01ce467` ; le placement reste au lot 234, qui peut être fusionné avant ou après 233. Suite de reprise : trois préexistants et le placement 234 restent rouges ; voir l'entrée 233 et son rapport.
- **Lot 206 (savoir des observations) : reprendre** (lot 235). Le locuteur ne lit jamais l'esprit de l'auditeur ; il dit ce qu'il croit nouveau **et** pertinent pour lui (confidences 206 b tombées de 80 à 90 %).
- **Lot 228 (céder un outil, reprise du 202) : reprendre.** Garder la règle (ne pas céder une capacité sans compensation), mais une offre reste possible quand la contrepartie compense vraiment la capacité perdue ; corriger l'achat à une pièce sous-compensé ; viser la richesse du hameau dans l'étendue de la référence (S 40,5 → 34,75 sur 228).
- **A5, arbitrages (rapport 245)** : statut de Gorm sourcé, portée limitée à ses lieux, connu des seuls occupants déclarés, ascendants initiaux neutres sauf liens renseignés ; deux niveaux de mandat depuis l'agenda racine, cycles interdits ; mandataire en retard : avertir l'ancien titulaire s'il est joignable puis réaffecter sur croyances, sans annulation à distance ; les refus d'accueil (méfiance, rancune) tiennent, l'autorité perçue (statut, ascendant, dette) donne un bonus borné au jugement de qui écoute déjà, sans obéissance automatique. « Obéir sous contrainte » (la peur arrache un mandat malgré la méfiance : exécution réticente, abandon hors de vue, rancune) : lot ultérieur, avec A7 ou 4f.
- **`main` avancée à `c870c8b`** (vérification 241 : 49/49 nuits, zéro plantage ; le défaut bloquant de Lucien à 435 est corrigé depuis par le lot 244). Ce qui a été fusionné après (lots 244 à 254) attend la prochaine vérification d'intégration, jouée en Luna high.
- **Lot 250 (preuve d'usage) : un dernier lot ciblé** (255) sur l'observation partagée de l'environnement ; s'il ne suffit pas, le chantier 206/235/250 est mis de côté sans nouvelle reprise.
- **Chantier 206 → 235 → 250 → 255 mis de côté** (décision appliquée) : le lot 255 date chaque composante d'une observation partagée et fait disparaître les 46 redites du hameau 1985, mais 21 réapparaissent au hameau 7 (niveaux de conduite annoncés en sens contraires) et les suspects montent sur deux nuits (mine 1985, hameau 1985). `social.bavarder` garde donc la lecture `_sait` du savoir réel de l'auditeur, limite connue du contrat (aucune lecture privée ailleurs). Branche `codex-sait-observations-c` (`b0396b5`) conservée sur `origin` ; rapports 235, 249, 250, 255 et bruts `artifacts/usage-250/`, `artifacts/partagee-255/`.

## Décisions prises le 2026-10-27 au soir

- **`main` avancée à `395834b`** (vérifications moteur 212 et Luna 216 bonnes ; lots 205, 207, 211, 214, 219, 220 fusionnés après leur base avec suites vertes). Points ouverts connus : attente en crue, retours suspects (lot 213), aller-retour vers un secours ancien (lot 223).
- **Services payés : ne pas défaire ce qu'on a été payé pour faire.** Celui qui a été payé ne défait pas lui-même l'état obtenu tant qu'il croit que le payeur en a encore besoin ; aucune obligation d'entretien (un feu qui s'éteint seul n'est pas sa faute). Pas de contrat « maintenir » à durée pour l'instant.
- **Réessai lié à l'obstacle** : la patience de 30 min reste ; le répit de 60 min est remplacé par la cause du renoncement (témoin présent, porte verrouillée, refus, absent) : on ne reprend le but que si l'on croit cette cause changée ou un moyen nouveau, jamais par le seul délai. Lot après le 213 (même fonction `choisir`).

## Décisions prises le 2026-10-27 (revue vierge 187)

- **Réflexion limitée / saillance** (`docs/plan-decision.md`) : **mesurer d'abord** ce qu'une recherche limitée aux moyens
  saillants changerait (coût, plans perdus, comportements), puis décider ; l'ordre du 2026-10-23 tient d'ici là.
- **Projets hors détresse** : un agenda né (A6) se place sur l'échelle commune selon son poids, pas au dernier palier
  « argent » ; lot après 184 b.
- **Suivi d'une délégation** : après un délai, le mandant va voir où en est sa charge confiée (joueur ou PNJ), au lieu de
  rester figé (Gorm, 220 min au Relais) ; rattaché à A5.
- Lots compatibles issus de la revue : 189 sortie extérieure (régression du lot 181), portes d'un lieu gardé, valeur des biens
  non monétaires et des outils de capacité, parole sans constats auto-causés ni avis redits, ouïe des compagnons connus.

## Décisions prises le 2026-10-24

- **A2b, les PNJ proposent « faute de mieux »** (`docs/plan-relations.md` § 7.2) : un recours de dernier
  ressort, après une demande refusée ou avant une faute contre quelqu'un, jamais un geste comparé dans la
  recherche ; contreparties portées et pièces d'abord, tâches promises ensuite. Les lots 33 et 36
  (`codex-pnj-proposent`, `codex-proposer-cout`) ne sont pas fusionnés.
- **Un gardien en détresse agit sans partir** (Bram, mine 42, 12 h : la paie gardée contre Odon, le bureau
  noir de 450 à 720, sécurité 100 et faim « en attente » sans aucun geste ; même blocage sur 42bb9c0 après deux
  allers vers la lumière) : il garde son bien, mais une détresse qui dure le fait appeler à l'aide ou demander
  qu'on lui apporte de la lumière ou qu'on la lui allume, sans quitter ce qu'il garde. La peur ne lève pas la
  garde. À vérifier d'abord : pourquoi l'appel à l'aide existant ne part pas, et s'il croit encore Odon là
  (garde à 100 après le départ d'Odon vers 600).
- **Le coût des bancs est à résoudre** avant d'avancer `main` : après le lot 38, une nuit de 12 h coûte
  encore ×3 contre 42bb9c0 (mine, auberge).

## Décisions prises le 2026-10-22 (à implémenter)

- **Réglages et données** : profils du Relais et de la crue selon `docs/analyse-relais.md` (Brune
  douceur 75 ; Ilse honnêteté 80 ; Aubin honnêteté 65, douceur 80 ; Gorm inchangé) ; froid sec 4 par
  heure ; seuil + 15 (`REPRISE`) gardé ; premier acte du Relais gardé (Brune peut voler tôt) ;
  crochetage plus ou moins bruyant selon l'adresse (habile et réussi : discret ; échec ou forcement :
  fracas) ; surenchère progressive (+50 % par palier tant que l'offre vaut la peine) (ces deux-là : branche
  `crochetage-surenchere`) ; réglages de
  l'ouïe gardés (ajustés au banc si besoin) ; `GARDE` et `PRET` à tirer des valeurs et des relations.
- **Noms** : un nom ne s'apprend qu'en entendant la personne se nommer ou quelqu'un la nommer, pas en
  la voyant de près ; sinon la scène la décrit (« un homme trapu ») ; seuls les liens déclarés par le
  scénario donnent le nom d'office.
- **Appel négocié** : l'appelé et l'appelant conviennent de qui vient à qui (« J'arrive », « Ici,
  viens », « Qu'est-ce que tu veux ? », silence) selon qui a besoin de qui, qui peut bouger, la
  distance et l'urgence ; l'attente se règle sur la distance ; même règle pour le joueur, réponses
  typées sans Luna.
- **Plan force** (`docs/plan-force.md`) : les coups ne tuent jamais (PV 0 = hors de combat, seul
  « tuer » donne la mort) ; **douceur 100 peut frapper pour se défendre ou défendre un protégé**
  (écart à la recommandation du plan) ; joueur assommé : le temps passe jusqu'au réveil ; pas de mort
  par faim, froid ou eau à cette étape ; le reste selon les recommandations du plan.
- **Plan relations** (`docs/plan-relations.md`) : cinq axes (confiance, affection, rancune, peur,
  dette) ; le joueur perçoit signes et impressions (commande « observer »), sa PSY peut le tromper ;
  un PNJ donne son avis sans qu'on le lui demande seulement si l'autre risque d'agir contre et qu'il
  s'en soucie ; le reste selon les recommandations du plan.
- **Plus tard** : fabrication étape 4 ; imitation de voix (après les relations).
- Branche `ressources`, non fusionnée (données seulement, décision de l'utilisateur ; `docs/plan-crue.md`,
  « Un feu hors de l'eau ») : deux scénarios manquaient de ressources. **Crue** : depuis `verifier-eau`,
  personne ne se chauffait au brasero menacé de la conduite, seul feu. Ajouté à la galerie de ronde,
  hors d'atteinte de l'eau, un poêle du guet allumé (120 min) et trois charges de bûches du guet (90 min)
  à Gorm, sus de tous ; un âtre au refuge, essayé, supprimait tout froid. Bancs 8 h (8 graines, `main`
  ec2352e puis la branche) : froid pressant 491 → 111 minutes·PNJ par nuit (Brune 281 → 71), en attente
  541 → 219, dans l'eau 438 → 373, échanges 19 → 18, achats 1 → 2 ; audit 12 h : froid 794 → 199, en
  attente 914 → 571. **Auberge** : le bois (750 minutes pour trois foyers) finissait vers la cinquième
  heure. Mesuré : un foyer brûle une minute de combustible par minute, trois foyers 1 440 minutes en 8 h,
  2 160 en 12 h. Portés à 1 815 minutes : bûches de la cuisine 4 → 8 charges, d'Anselme 2 → 3, fagots de
  Joss 2 → 3, et une réserve de bûches d'Odile au cellier (12 charges de 60 min, sue de la maisonnée).
  Bancs 8 h : dans le noir 1 159 → 236 (dont 128 de Lucien au grenier, qui n'a pas de lumière), en
  attente 341 → 24, sans recours 101 → 146 (Lucien, qui guette pour ses biens, désormais éclairé),
  foyers allumés âtre 215 → 471, fourneau 243 → 424, poêle 235 → 464 min ; restent à la fin 3,5 charges
  de la réserve et 2,2 fagots ; offres de tâche 33 → 7, « as-tu… ? » 14 → 2,4, échanges 82 → 33 (surtout
  les demandes vaines), vols vus 1,2 → 1,1, une nuit 50 → 32 s. Audit 12 h : noir 2 690 → 1 017
  (le bois s'épuise vers la huitième heure ; la lanterne de l'étable vide), en attente 1 141 → 351, froid
  172 → 19, échanges 120 → 100 ; Odile prête sa réserve à Anselme puis la lui refuse. L'huile n'a pas été
  augmentée : un pot d'huile essayé n'a jamais servi (aucune part de combustible ne se demande pour une
  lampe, seulement pour la chaleur ; qui a peur dans le noir n'a pas rechargé la lanterne de l'étable).
  Aucune usurpation ni violation ; `VERIFIER` sans écart sur une nuit de chaque scénario (graine 7, 8 h).
  `tests/test_ressources.py` (crue 7 et auberge 1985 après rechargement) ; scènes d'auteur à court de bois
  sans la réserve d'Odile (`test_refus_retenus`, `test_echanges_suite`, `test_entretenir`) ; `test_auberge`
  (11 événements distincts en 210 minutes, seuil 12 → 10), `test_eau`, `test_verifier_eau` (on sèche au
  poêle du guet). Limites : moteur inchangé ; la lumière des lampes n'est pas une ressource que les PNJ se
  partagent ; un scénario de 12 h finit encore dans le noir à l'auberge (rareté voulue).
- Branche `relances-luna`, non fusionnée (`docs/contrat-mj.md`, « Ce qui n'appelle pas de relance » et « Refus
  et échecs ») : après `parole-corrections`, les quatre bancs de référence étaient montés à 3,24 appels et 6
  relances par tour MJ. Causes lues dans les fils : un « impossible » au premier examen audité alors que la
  boucle le refuse ensuite (réexamen), avec sa prose relancée (« le moteur… ») ; la contre-revue refusant
  l'examen que le moteur prescrit pour chercher (« je cherche des traces de pas », 9 appels) ; l'explication
  d'un geste refusé par le monde (trop loin) relancée jusqu'à trois fois sur des refus sémantiques ; un nom
  typé autrement que ne le disent les mots de Corvus renvoyé au MJ ; une citation recopiée par l'auditeur
  avec son attribution ; des règles du contrôle déterministe jamais dites au MJ (« je », « Corvus »,
  « moteur » hors des répliques ; une voix inconnue nommée dans le récit). Règles : un avis que la boucle
  écartera n'est pas audité (`mj.refus_assure`) ; le nom que Corvus se donne est lu dans ses mots
  (`paroles.verifier_nom`) ; la citation d'une parole est la réplique du segment qu'elle recouvre
  (`narration.citation_du_segment`, `cite_entiere`) ; l'explication d'un refus du monde a un essai, puis le
  joueur lit les refus du monde dans l'ordre (`mj.ExplicationCedee`) ; `REGLE_NARRATION` dit la voix
  d'auteur, la voix inconnue et les noms connus ; `attendu` d'une voix d'auteur, du réexamen et d'un héler
  sans nom plus précis ; la contre-revue admet la perception qui cherche ; l'auditeur sait que les témoins se
  taisent, que les mots de qui répond ne sont jamais fournis, que ce que fait sentir un objet perçu est
  ambiance. Ajouts de la revérification (`docs/reverification.md`, N5) : une réplique ne nomme que qui son
  locuteur connaît, voix connue ou non (`narration.voix_inconnues`, `voix.connait_nom` ; Aubin ne dit plus
  « Corvus ») ; « tu demandes à passer » n'est pas une parole racontée ; un objet remis au joueur lui est dit
  une fois, son ouïe ne le lui redit pas à la troisième personne (`ouie.retentir`, `appris`). Tests après
  rechargement, cas réel et cas de même nature (`tests/test_relances_luna.py`, 20 tests) ; tests accordés :
  `test_narration`, `test_defi` (le refus du monde au lieu de « Corvus n'a rien tenté »),
  `test_parole_corrections` (« C'est moi, Brune » sans relance), `test_audits_attendu`. Luna, 2 passes,
  `main` ec2352e puis la branche 23fd759, une exécution à la fois, neuf bancs : 4 bancs de référence 3,17 →
  3,11 appels et 14,4 → 14,2 s par tour MJ, replis 0 → 0, relances 5,5 → 4,5, refus 9 → 8,5, tours avec
  refus 5,5 → 5,5 (une passe intermédiaire, 1c484c0, sans les ajouts de la revérification : 3,01 appels,
  13,5 s, relances 3, refus 11) ; avant `parole-corrections` : 2,99 / 14,2 / 3,5 / 8,5. Bancs du soir, appels
  par tour : soir-noir 3,90 → 3,40, soir-voix 3,50 → 3,00, soir-appel 3,08 → 2,92, ressources 3,33 → 3,00,
  comptes 3,00 → 3,50 (une passe à 5) ; relances soir-noir 1,5 → 0,5, soir-voix 1 → 0. « je cherche des
  traces de pas » 9 et 2 → 6 et 4 appels ; « J'attends que Gorm ait le dos tourné… » 5 et 7 → 3 et 3 ; « Qui
  est là ? » 6 et 5 → 4 et 4 ; « C'est moi, Brune » 6 et 4 → 3 et 5. Saisies du rapport du soir : textes
  affichés équivalents, aucun refus de forme ni `attendu` montré, imposture démasquée 4/4. Limites : un
  « impossible » au premier examen reste refusé (une relance ; 4 par passe de référence) ; un `nom` typé sans
  nom dans les mots reste refusé (« Qui est là ? » typé `nom`) ; l'arbitrage sommaire `difficulte` 0 avec une
  stat reste un refus de forme ; les refus sémantiques de l'auditeur (absence affirmée, « hors de vue »)
  restent la première source de relances ; le refus du monde montré à la place d'une explication porte ses
  coordonnées (« case 5, 11 du plan ») et ne dit que le dernier geste proposé ; « passer sous la poutre »
  peut encore répondre par « Il faut une échelle » (`franchir`, défaut N5 de la revérification) ; les
  consignes de l'auditeur restent sémantiques. `couverture_action.py`, `sons.py`, `ouie.py`, `echanges.py`,
  `rejeu.py` touchés hors du périmètre annoncé, chacun pour une règle commune.
- Branche `boucles-pnj`, non fusionnée (`docs/plan-planificateur.md`, « Les boucles de la revérification » ;
  `docs/plan-ouie.md`, « Ce qu'on a déjà dit ») : trois boucles de la [revérification](reverification.md),
  nées de la délibération à l'événement. **Un geste défait sous ses yeux** (N1, mine 42 : Odon ouvre le
  garde-manger, Mathe le referme, 689 fois ; la précaution sans témoin était levée par la faim à 95, pas
  absente) : ce qu'un PNJ vient de faire de sa main à une chose (ouvrir, fermer, verrouiller, crocheter,
  allumer, éteindre ; `DEFAIT` 5 min, esprit `donne`), un autre — PNJ ou joueur — le défait sous ses yeux :
  on s'oppose à lui sur cette chose, retenu comme un refus (`defaire`, « oppose ») qui tient tant qu'il croit
  l'opposant là, et le planificateur n'y offre plus de geste (`deliberation.changer_etat`, `contrarie`,
  `Vue.contrarie`). **Le recours en cours garde la main** (N2, crue 3 : 1 705 passages de salle en 8 h ; la
  galerie est éclairée par le jour) : hystérésis entre recours d'un même besoin et d'un même rang
  (`choisir`, `_candidats`) ; l'abri vers lequel il est en route garde la main tant qu'il en est un, sauf eau
  qui monte sous ses yeux ou péril (`_plan_abri`) ; la lumière d'un autre ne satisfait plus le besoin de
  lumière (`_plan_lumiere`). **Ce qu'on a déjà dit** (N4, auberge : Hugues redit 26 fois où est le ballot) :
  un lieu dit l'est jusqu'à ce que sa valeur change ; pas à qui a le bien dans sa salle (`_a_dire`). Cas réels
  et cas de même nature après rechargement, même laps découpé (`tests/test_boucles_pnj.py`, 11 tests, 8
  échouent sur `main`). `tools/audit_nuits.py` mesure les boucles (bascules, passages par heure,
  avertissements redits, appels à l'aide). Audit 4 scénarios × 8 graines × 12 h contre `main` e07bc20 :
  bascules mine 180,6 → 2,1 (mine 42 : 1 436 → 8), auberge 15,5 → 2,5 (la même boucle, Lucien et le coffre
  d'Anselme, 62 → 2), avertissements redits auberge 4,4 → 0,75, appels à l'aide mine 5,6 → 4,1 ; Relais et
  crue identiques nuit pour nuit ; en attente mine 1 369 → 1 404, auberge 379 → 456 (on attend que
  l'opposant s'en aille) ; aucun plantage, violation ni usurpation ; `VERIFIER` et `spatial.VERIFICATION` (0,2) sans écart
  sur une nuit de 8 h de chaque scénario (graine 42). Limites : la fenêtre
  « vient de faire » est fixe ; l'opposition porte sur la chose entière et se fie à où il croit l'opposant ;
  l'hystérésis compare des buts, pas des coûts ; le souvenir d'un fait dit peut sortir de la mémoire bornée
  (un « peu fiable » redit à quatre heures d'écart).
- Branche `temps-reel`, non fusionnée (`docs/plan-temps.md`, « Correctif : le temps réel » ; `donjon/vecu.py`) :
  ce qui restait à la minute après `deliberation-evenements`. **Horloges à leur instant** : déclenchées par la vie
  des PNJ à chaque minute franchie (`pnj._avancer`, `horloges.declencher`), plus à la fin de l'action du joueur ;
  la rafale de l'auberge avancée à la minute 2 d'une attente de 5 minutes éteint l'âtre à la minute 2 et Hugues
  le voit alors ; Gorm rallume le brasero éteint par une horloge avant la fin de l'action. **Corps et besoins au
  temps vécu** (`vecu.noter`, `solder`, `minute` ; `corps["vecu"]`) : chacun, joueur compris, porte l'état où il
  est depuis un instant (activité du geste fait : effort, repos ; chaud d'un feu ; eau ; écart de sécurité par
  minute, `deliberation.ecart_securite`) ; le temps passé est soldé quand l'état change et à chaque minute ; la
  faim, la fatigue, le froid, le séchage, la dérive des besoins et la sécurité comptent ce temps-là au lieu
  d'échantillonner la frontière de minute. Ilse qui traverse le noir et Gorm dont la ronde passe au chaud vivent
  la même chose quelle que soit la phase de la minute (à 0,005 près ; avant, la phase décidait) ; le corps du
  joueur compte la marche à l'effort et les rotations au calme dans l'ordre qu'on veut ; se tourner ne creuse
  plus. **Froid sec à 4 par heure.** **Patience et répit en temps** (`pnj.commencer_attente`, `compter_attente`,
  `intention["attente"]` en dixièmes ; `renoncements` à l'instant) : Brune renonce après 30 minutes de guet
  comptées au temps, Gorm bloqué par le joueur aussi. Cas réels et cas de même nature après rechargement, même
  laps découpé (`tests/test_temps_reel.py`, 10 tests). Tests adaptés : `test_marche` (attente en dixièmes),
  `test_entretenir` (une part servie en appelant compte aussi), `test_recit_pnj` (la nuit 7 renonce devant une
  serrure trop sombre), `test_refus_retenus` (les offres pour un feu ; Anselme et Lucien se disputent le ballot,
  chaque déplacement est un moyen nouveau), `test_lumiere_garde` (la scène réelle de la graine 42, minute 145,
  enregistrée dans `tests/data`, la graine faisant désormais une autre nuit). `VERIFIER` sans écart sur une nuit
  de 8 h de chaque scénario (graine 42). Bancs 8 h contre `main` 0551ba2, l'un après l'autre (détail dans le
  plan) : aucune usurpation ni violation ; nuits toutes distinctes ; les écarts suivent des nuits qui divergent
  (Relais : en attente 52,5 → 72,5 et minutes dans le noir 27 → 59, presque tout dans la graine 42 ; mine : sans
  recours 56 → 39 ; auberge : événements 101,5 → 89,75, la graine 42 de `main` à part). Audit 4 scénarios × 4 graines × 12 h (nuits de `main` jouées par le lot B, même
  commande) : aucun plantage ni violation, mêmes familles de constats (sans but en pressant 38 → 45, noir long 59 →
  64, aller voir alterné 6 → 9, appels nombreux 3 → 0, eau longue 4 → 1, dettes en fin 5 → 2). Coût au processeur
  (une nuit de 8 h, graines 1985 et 7, `main` puis branche sous le même verrou) : Relais 27,8 → 30,4 s, mine 60,8
  → 69,2 s, auberge 84,3 → 90,8 s, crue 33,8 → 36,4 s (+8 à +14 %, nuits différentes ; la relecture des
  conditions à chaque geste, ~0,8 ms, en est l'essentiel). Limites : les conditions (lumière, compagnie, feu, eau) se relisent à chacun de ses gestes, à
  chaque éveil et à chaque minute, pas à chaque geste des autres ; combustion et crue restent à la minute (le
  combustible se compte en minutes entières, le niveau d'eau en centimètres par minute) ; dates des croyances,
  échéances et dettes à la minute ; le corps du joueur, soldé aux minutes et aux changements d'état, ne montre
  pas les secondes en cours. Défaut vu au banc, hors de ce lot : Aubin, payé pour garder le brasero allumé, sans
  flamme pour le rallumer, ne rend pas la tâche et promet deux fois une part de planches qu'il ne sert pas ;
  Gorm l'attend 160 minutes dans la conduite noire (Relais, graine 42). **Accordée avec `main` 30fcd07**
  (`relances-luna`, `boucles-pnj`, `ressources`, `relations-socle`) : un seul conflit de code, `choisir`, qui
  garde l'hystérésis entre recours de `boucles-pnj` et le répit compté de l'instant du renoncement ; la
  sécurité ressentie au temps vécu lit `se_fie` et `se_mefie` (aucun accès à la croyance hors de
  `relations.py`). `test_ressources` suit les nuits au temps vécu : crue 7 jusqu'à 240 min (Brune, chauffée au
  poêle du guet dès 130, ne demande plus son bois ; le poêle s'éteint vers 245), auberge 1985 (la réserve
  passe d'Odile à Anselme et revient, le poêle tient encore à 420). Suite verte, pyflakes sans nom indéfini,
  `VERIFIER` et `spatial.VERIFICATION` 0,2 sans écart sur une nuit de 8 h de chaque scénario (graine 42).
  Banc rapide (`tools/audit_nuits.py`, 4 h, graines 1985, 7, 42, 2024, `main` puis la branche) : aucun
  plantage, violation ni usurpation ; sans recours Relais 42,5 → 45, mine 31,25 → 26,25, auberge 20 → 20,
  crue 0 → 0 ; en attente 0 → 2,5, 6,25 → 0, 1,25 → 1,25, 7,5 → 17,5 ; les boucles de `boucles-pnj` ne
  reviennent pas : bascules 1 → 1,5 (un vol puis la réserve refermée, pas une boucle), 1 → 0, 0 → 0, 0 → 0,
  avertissements redits 0 partout ; passages par heure (moyenne du maximum, pire) Relais 6,75 (8) → 8,5 (11),
  mine et auberge égaux, crue 22,25 (36) → 21,25 (44) : dans les deux, Gorm va et vient entre la galerie et le
  refuge pour le brasero en surenchérissant une tâche qu'on accepte puis doit aussitôt (crue 1985, défaut
  connu de la revérification) ; minutes dans le noir Relais 17,5 → 40 ; temps d'une nuit (relevés compris)
  Relais 10,8 → 12,5 s, mine 24,6 → 24,4 s, auberge 22,1 → 23,4 s, crue 15,2 → 14,3 s. Le défaut d'Aubin se
  confirme sous une variante (Relais 42, 8 h) : il vend à Gorm une part de planches pour le brasero (min 151)
  sans flamme pour le rallumer (la torche lui est refusée), ne la sert ni ne le dit, et Gorm attend 60 minutes
  avant que la part, remise autrement, devienne une dette rendue ; à 334, il accepte pour 16 pièces de
  rallumer le brasero puis la doit aussitôt (non corrigé ici).
- Branche `attente`, non fusionnée (`docs/plan-temps.md`, « Correctif : attendre une durée » ; demande de
  l'utilisateur) : `attendre 30 s`, `attendre 10 min`, `attendre 1 h 30` sans Luna (« attendre » seul,
  cinq minutes) ; Espace sur une saisie vide fait attendre 1,5 s, dans la page et le terminal (une saisie
  commencée garde son espace). L'attente passe par tranches de 15 s (`Moteur._attendre`) et cesse quand
  le joueur voit paraître quelqu'un, même un instant, ou entend un appel, un cri, un fracas, des paroles
  dont il saisit les mots (`ecoute.eveille`). Même monde d'un bloc ou par tranches : le corps du joueur
  au temps vécu (lot A) ne dépend pas du découpage, une voix inconnue est retenue à la minute entendue. La proposition
  à cible vide (MJ, banc, tests) reste le bloc de cinq minutes ; le MJ peut donner une durée en secondes.
  Cas vérifiés après rechargement (`tests/test_attente.py`, `test_tui`, `test_web`) : Gorm qui entre au
  refuge, Aubin aperçu, un appel entendu de la galerie. Limites : l'arrêt se juge à la tranche ; une
  parole adressée au joueur n'est pas distinguée d'une autre.
- Branche `crochetage-surenchere`, non fusionnée, accordée avec `main` d5d4bee (`docs/plan-ouie.md`, « Le bruit
  du crochetage selon l'adresse » ; `docs/plan-social.md`, « La surenchère progressive et la tâche aussitôt
  due ») : deux réglages décidés le 2026-10-22 et le défaut N3 de la revérification. **Crochetage** : son bruit
  tient à son jet, règle commune au joueur et aux PNJ (`ouie.nature_crochetage`, même seuil
  `pnj.seuil_crochetage`, `Plan.marge`) : réussi, un geste ordinaire (feutré en douce), « crochète la serrure
  de … sans forcer » ; manqué, il s'acharne : un fracas, comme forcer. Le voleur qui veut agir sans être
  entendu attend le bruit que lui promet son adresse (`planification.bruit_crochetage` : feutré s'il a au
  moins une chance sur deux, `HABILE`). **Surenchère** (`planification._engager`, `hausse`, `PALIER`
  1,5, `Vue.hausse_faite`) : +50 % par refus « cher », une hausse par minute, jamais ce que les pièces coûtent
  au payeur (`Vue.depense`) au-delà de la peine que la tâche lui épargne, première offre comprise ; puis il
  renonce. **Tâche acceptée** : l'empêchement (`echanges.empeche`) et le plan de la tâche
  (`planification.planifier_tache`) sont le devis qui l'a fait accepter ; un feu payé se compte à recharger,
  et éteint si le payeur ne le croit pas allumé, sauf ce que le payé a vu ou fait depuis l'offre
  (`_vu_avant_la_tache`). Cas réels et de même nature après rechargement (`tests/test_crochetage_surenchere.py`,
  11 tests ; `test_refus_retenus`), `VERIFIER` et `spatial.VERIFICATION` sur une nuit de chaque scénario. Bancs 8 h,
  `main` d5d4bee puis la branche (Relais 8 graines, autres 4), par nuit : à l'auberge, offres de tâche 32 →
  15,5, hausses 5,75 → 0,75, offre la plus haute 36,75 → 4,25 pièces, pièces des tâches 39,25 → 2,5, tâches
  dues aussitôt 1 → 0, dettes 1,25 → 0, sans recours 75 → 45, échanges 81 → 66 ; crue en attente 472 → 516 ;
  crochetages réussis sans forcer 0 → 0,5 (Relais), 7 (mine), 0,75 (auberge), 0,5 (crue), entendus sans être
  vus 0,5 / 0,75 / 0,75 / 0,5 → 0,5 / 0,75 / 1 / 0 ; Relais aux mêmes mesures, aucune usurpation ni violation ; temps
  faussés par la charge (+4 à +10 %). Audit 12 h (4 × 4) : dettes de fin de nuit 5 → 0, aucun plantage ;
  N1 et N4 demeurent (d'autres lots). Limites : la valeur d'une tâche est la peine qu'elle épargne, pas le
  besoin ; un payeur pauvre n'offre plus rien ; une hausse par minute ; les premières offres à plusieurs
  dans la même minute restent ; aux DEX des scénarios, aucun voleur ne se sait habile (il attend un fracas
  comme avant) ; `AISANCE` (0 : toute réussite cède sans fracas), `HABILE`, `PALIER` à régler.
  Fusionné après le lot A (`main` ebca508) : seul conflit de code, la forme des buts (`deliberation`) ;
  deux scènes « sans bois » de l'auberge vident aussi la réserve d'Odile (branche `ressources`, absente de
  la base du lot), sans quoi Tilo, payé pour l'âtre, en demande une part à Odile, qui la met au feu et le
  rallume elle-même : le payeur fait la tâche qu'il paie (limite, à corriger). Banc rapide 4 h, 4 graines,
  `main` puis la fusion : mine et auberge identiques ; Relais 3,5 crochetages par nuit dont 0,75 réussis
  sans fracas, bascules 1,5 → 0,75, en attente 2,5 → 8,75 ; aucun plantage ni usurpation.
- Branche `codex-profils`, fusionnée (données seulement, décision du 2026-10-22) : dans le Relais
  et la crue, Brune douceur 75 ; Ilse honnêteté 80 ; Aubin honnêteté 65 et douceur 80 ; Gorm
  inchangé. Limites anciennes incompatibles retirées dans la crue, traits d'Ilse et d'Aubin nuancés.
  Six scènes de tests posent explicitement leur honnêteté ou douceur 100, avec commentaire,
  pour conserver la vérification des interdits. Le test console simule aussi le récit du résultat,
  jusque-là laissé partir vers HTTPS avec sa clé factice ; garde sans réseau ajoutée à cette scène.
  Suite complète verte : **1241 tests, 14 sautés** sans `jsonschema` (facultatif pour MiMo),
  en priorité BelowNormal, sans réseau extérieur pour la passe finale.
  Bancs 8 h (huit graines, `main` f1eee53 puis branche), audits 12 h et analyseur : pas de nouveau
  voleur sur 8 h ; sur 12 h, Aubin force la réserve dans deux nuits par scénario et mange une part
  en 1985 dans chacun. Vols vus par nuit Relais 1,25 → 1,375, crue 0,5 → 0,625 ; attente
  298,125 → 245,625 et 571,25 → 499,375 minutes·PNJ, sans recours 111,25 → 126,875 et 42,5 → 67,5.
  Aucune poussée ; 64 nuits mesurées sans plantage, violation ni usurpation ; `VERIFIER` et
  `spatial.VERIFICATION` (0,2), graine 42 sur 8 h de chaque scénario : sans écart ni borne.
  Valeurs et traits conservés après sauvegarde/rechargement ; aucune autre donnée ou moteur modifié.
  Limites : effet surtout après 8 h, aucun vol d'Ilse sur ce lot, les occasions restent nécessaires.
  Voir [l'analyse](analyse-relais.md) et le [rapport](taches/rapport-codex-1-profils.md).
  Fusionné après `main` 06602a6 (relations-socle, lot A temps réel, attente, lot C) : seul conflit
  `docs/etat-dev.md` ; aucun test adapté ; suite 1282 tests. Banc rapide 4 h, 4 graines, `main` puis la
  fusion : Relais identique (l'effet des profils vient après la 4e heure) ; crue échanges 6,75 → 7,25,
  noir 13,75 → 11,25, en attente égales ; aucun plantage, usurpation ni bascule nouvelle.
- **Des parts pour les sources rechargeables**. Branche `codex-lampes`, fusionnée.
  La recherche compose la réception d'une part puis `alimenter` et `allumer`, selon ce que la
  source brûle (`recharge`), sans branche de substance. Le lot, posé ou porté, reste au donneur ;
  une charge est détachée et réellement livrée, gratuitement ou au prix convenu. L'accord ne
  charge pas la source : le plan s'arrête à la demande et se refait à réception ; ces frontières
  restent dans le cache. Engagement et mémoire gardent la provenance, sans convention d'identifiant.
  Les parts physiques héritent aussi de leur contenu par copie indépendante ; quantités et masse
  restent conservées. La catégorie combustible ne garantit plus la chaleur : enquêtes, garde
  urgente et moyens du refus vérifient un foyer connu compatible (`part_pour`). Une source
  explicitement incompatible est refusée. Huile rare remise dans les données de l'auberge : pot
  d'Odile (3 × 120 min) et burette de Joss (2 × 90), avec le contenu des lampes et les croyances
  initiales. Joueur par la parole typée existante, sans nouvelle consigne au MJ.
  Cas réel après 8 h, mine, lots posés/portés joueur/PNJ, autre substance et lot physique : état,
  ressources, possession et rendu après rechargement (`test_lampes_parts`, 11 tests).
  Bancs 8 h contre main f1eee53 : noir moyen min·PNJ auberge 237,5 → 137,5,
  mine 291,25 → 291,25, Relais 26,875 → 26,875,
  crue 33,75 → 48,75 (régression observée).
  Une recharge de lampe à l'auberge sur quatre nuits de 8 h ; aucun échange d'huile dans ces
  nuits de 8 h. À 12 h, l'auberge totalise une part donnée et cinq achetées réellement livrées,
  puis dix recharges de lampes sur huit nuits. Audit auberge/mine 8 graines × 12 h et
  `VERIFIER` sur chaque scénario 8 h : aucun plantage, violation ni usurpation, aucun écart de
  recherche. Limites, alertes restantes, mesures détaillées et temps observés :
  `docs/taches/rapport-codex-3-lampes.md`. Défaut de mock réseau préexistant de `test_proto`
  corrigé séparément ; la suite finale inclut tous les changements.
  Fusionné après `main` 06602a6 et `codex-profils` : conflits `paroles.py` (imports : `relations` de
  main et `complement_de` des lampes), `test_proto` (garde réseau de profils gardée), `test_ressources`
  (auberge : la version des lampes, la réserve portée ne passe plus entière), docs. Suite 1293 tests.
  Banc rapide 4 h, 4 graines, avant → après : auberge et mine identiques (l'huile ne sert qu'après la
  4e heure) ; Relais échanges 6 → 5,25, noir 41,25 → 48,75 min·PNJ, sans recours et en attente égaux ;
  aucun plantage, usurpation ni bascule nouvelle. Relecture : `_parts_remises` compte un besoin de
  lumière aussi pour qui sait crocheter (heuristique par capacité, à revoir) ; temps d'une nuit de
  12 h doublé à l'auberge selon le rapport (120 → 249 s), non revu ici.
- Branche `appel-negocie`, fusionnée (`docs/plan-ouie.md`, « L'appel négocié » ; `donjon/appel.py` ;
  décision du 2026-10-22) : l'appelé et l'appelant conviennent de qui vient à qui, par des paroles typées
  que le moteur tranche, une règle pour les PNJ et le joueur. « J'arrive ! » (il cherche lui-même
  l'appelant, on le prie de venir, ou la raison le fait venir : un avertissement, une aide, ce qu'il a sur
  lui), « Ici, viens ! » (il ne peut ou ne veut bouger : geste en cours sur place, garde, ce qu'il fait sur
  place, un autre rendez-vous, un chemin qu'il croit fermé, l'eau, ce qui le presse ailleurs), « Qu'est-ce
  que tu veux ? » (libre, sans raison : l'appelant dit ce qu'il veut, tiré de son intention, et l'appelé
  décide de nouveau), le silence (méfiance, ou un geste qu'il veut sans témoin) ; l'appelant répond
  « J'arrive ! » à « Ici, viens ! » s'il peut venir, sinon « Ici, viens ! » à son tour, et l'autre en décide
  de nouveau. Le convenu entre dans l'esprit des deux (`rejoint` : qui il attend, jusqu'à quand, si l'autre
  a promis ; `rejoindre` : à qui il a promis de venir, une parole due) ; qui attend quelqu'un qui vient ne le
  cherche plus (`deliberation._attendre_qui_vient`) ; l'attente se règle sur la distance (le plus court
  chemin, et sa moitié, plus deux minutes ; plus de `REJOINT`) ; venu, celui que l'autre ne voit pas dit
  « Me voici ! » ; « J'arrive ! » attendu en vain est une parole rompue (méfiance, cause `parole_rompue`),
  joueur compris. Le joueur répond sans le MJ (« j'arrive », « viens », « qu'est-ce que tu veux ? », entre
  guillemets ou non, `emettre_son` méthodes `repondre`, `arriver`, `demander_raison`) et entend les
  réponses par l'ouïe commune. Correctif révélé : on n'appelle pas qui l'on sait là après avoir parcouru
  la salle des yeux (`pnj._inspecter`). Cas réels après rechargement, même laps découpé
  (`tests/test_appel_negocie.py`, 22 tests ; scènes enregistrées de la mine, graine 2024, et de la crue,
  graine 42) ; `VERIFIER` et `spatial.VERIFICATION` 0,2 sans écart sur une nuit de 8 h de chaque scénario.
  Bancs contre `main` 06602a6 : 4 h identiques hors des appels (on y hèle 0 à 0,5 fois par nuit) ; 8 h, mine
  et auberge, appels 3 → 3,5 et 6,75 → 4,75, attentes vaines 0,25 → 0 (mine), aucune parole rompue, sans
  recours et échanges égaux, aucune usurpation ni violation, temps égal. Luna non vérifiée : pas de
  connexion sur ce poste. Rapport : `docs/taches/rapport-appel-negocie.md`. Limites dans le plan.
  Fusionné après les tâches Codex 1 à 5 : conflits `deliberation` (`_attendre_qui_vient` et la
  `promesse_en_cours` des lampes et tâches payées), `pnj` (`repondre`/`repondre_a` retirés), tests, docs.
  Accord avec les noms : une réponse ou « Me voici ! » ne nomme celui qui parle (contenu `nom`, `se_nommer`)
  que pour qui connaît déjà son nom (`appel.dire`, `se_signaler`). Tests adaptés : `test_noms` (la réponse
  passe par `appel.dire`) ; `test_voix` (Hugues hèle Anselme : Corvus apprend son nom en le voyant parler de
  la voix qu'on appelait Anselme) ; `test_appel_negocie` (scènes enregistrées sur `main` : liens `connait_noms`
  repris du scénario ; Gorm a entendu le nom de Corvus ; l'appel de la crue 42 placé d'autorité, la nuit ne
  l'amenant plus d'elle-même) ; `test_ressources` (crue 7 : Gorm sans flamme ne sert pas la part d'Aubin, le
  poêle reste éteint à 240, 3 charges). `parole_rompue` passe par `relations.EPREUVES`. Suite 1372 tests.
  Banc rapide (`comparer_bancs`, 4 h, 4 graines, quatre scénarios) : Relais, mine, auberge identiques (on n'y
  hèle pas en 4 h) ; crue réponses 0,75 → 1,5, attentes vaines 0,25 → 0. 8 h mine et auberge : réponses 1,5 →
  7,25 et 2,75 → 9,75, retrouvailles 1,25 → 1,75 et 2,75 → 3,25, attentes vaines 0,25 → 0, aucune parole
  rompue, échanges et minutes sans recours égaux ; aucun plantage, usurpation ni violation. Luna non vérifiée.
- Branche `cout-calcul`, fusionnée en dernier (`docs/plan-planificateur.md`, « Coût de
  calcul, suite » ; [rapport](taches/rapport-cout-calcul.md)) : le temps d'une nuit, sans rien changer à ce
  que décident les PNJ. Mesuré sur `main` 06602a6 (échantillonnage `py-spy` ; `cProfile` grossit cinq fois
  les petites fonctions) : choix du but 19 à 57 % d'une nuit, perception 16 à 27 %, gestes et marche 13 à
  28 %, ouïe 6 à 16 %, empreinte de l'état 5 à 8 %. PyPy : mêmes nuits, 1,5 à 1,7 fois plus lent, écarté.
  Reprendre le choix entier : mesuré, non retenu (entrées identiques dans 1 à 12 % des choix, les moins
  chers ; au plus 1 à 2 % à gagner). Fait : perception incrémentale (`esprits._percus_depuis` : seuls les
  objets changés et ce qu'ils portent sont revus, deux perceptions sur trois) et signatures de la vue
  héritées d'un état à l'autre ; regard et lumière de sa case gardés pour l'état ; perception, témoins,
  présences et temps vécu d'un geste dans un seul état figé ; pas d'un trajet et passages de l'ouïe gardés
  sous la géométrie, les obstacles et les portes ; dans le planificateur, `enrichir` sans vue, le bien
  d'autrui jugé en un calcul (`biens.leses`), tests de but sans tri, parts jugées seulement là où est le
  donneur ; le contexte du joueur et le lexique une fois par lecture. Chaque lecture gardée est recomparée
  par `spatial.VERIFICATION`. Outil : `tools/empreintes_nuits.py` (empreintes de chronique, mesures, récit,
  souvenirs, état final complet, repères et recherches neuves ; temps au processeur ; pic de mémoire).
  Nuits identiques à `main` 06602a6 sur 32 nuits (4 scénarios × 4 graines, départ tiré et fixe, 8 h),
  aussi par `tools/comparer_bancs.py --empreintes` ; `VERIFIER` et `spatial.VERIFICATION` sur une nuit de
  chaque scénario. Temps au processeur, lancés ensemble, départ tiré (2 passes) : Relais 8,9 → 6,4 s,
  mine 23,7 → 18,8 s, auberge 16,2 → 12,6 s, crue 7,7 → 5,8 s (× 1,26 à × 1,39 ; départ fixe × 1,20 à
  × 1,49) ; pic de mémoire égal ou moindre. Limites : la mine reste dominée par des recherches neuves
  (épuisées, refaites chaque minute) ; l'empreinte de l'état se recalcule encore hors d'un état figé
  (5 à 8 %) ; qui bouge revoit toute sa perception.
  Fusionné après les tâches Codex 1 à 5 et l'appel négocié : conflits `paroles._connu_du_joueur` (la règle des
  noms gardée), `planification._parts` (parts jugées là où est le donneur, lot porté des lampes) et
  `rechauffe` (sans tri des faits, avec le foyer compatible des lampes), docs. Vérifié contre l'intégration
  d'avant (9eb7d09) : 32 nuits identiques (`tools/empreintes_nuits.py`, 4 scénarios × 1985, 7, 42, 2024,
  tiré et fixe, 8 h) ; `VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h de chaque scénario, puis `VERIFIER` et
  `VERIFICATION` 0,2 sur 8 h graine 42 : sans écart, nuits identiques à celles sans contrôle. Temps au
  processeur, référence → fusion (l'une après l'autre) : Relais 12,9 → 9,7 s, mine 60,5 → 48,5 s, auberge
  35,9 → 28 s, crue 23,7 → 17,9 s en départ tiré (× 1,25 à × 1,34 ; fixe × 1,26 à × 1,34), pic de mémoire
  moindre. Suite 1372 tests. `empreintes_nuits.py comparer` plante à l'affichage (« → ») sous une sortie
  redirigée en cp1252 : lancer avec `PYTHONIOENCODING=utf-8`.
- La suite complète passe : **1 696 tests, 16 ignorés**, sans appel au modèle (intégration 77473f9, après
  les lots 29 à 35 ; `tools/tests.py --processus 4`, 1 015,5 s, aucun échec ni erreur),
  `tools/tests.py` (ceux du clic demandent Node ; `jsonschema` est facultatif pour MiMo).

## À revoir

- **Coût, suites retenues** (revue externe du 2026-10-24, retenue par l'utilisateur) :
  - **C1, une capacité nouvelle ou rien** : généraliser la règle du lot 46 (une seconde lampe sans capacité
    nouvelle n'ouvre aucun geste) à toute catégorie d'objets que lisent les gestes (couper, frapper, combustible,
    clé, contenant) : ne prendre, demander, acheter ou saisir un objet non visé par le but que s'il apporte une
    capacité absente de ce qu'on porte. Le diagnostic mesurait 94 à 99 % d'états de fin de nuit avec préparatifs.
    Prochain lot de coût, contrat des lots 46 et 48.
  - **A, les entrées de la mémoire des recherches** : `_entrees` est un relevé écrit à la main (chaque lot qui lit
    une donnée doit l'y ajouter, sinon `VERIFIER` casse). Le lot 71, non fusionné, partage sa partie commune
    dans un même choix ; elle est encore refaite au choix suivant. Pistes : un compteur de révision par facette de
    l'esprit, incrémenté dans les seules portes d'écriture (`esprits.croire`, `relations`, `agendas`, refus,
    mémoire) ; ou une trace automatique des lectures de la recherche. Après C1 ; lot risqué (toute la mémoire).
  - **Le stratège Luna des PNJ** (historique, retiré au lot 130) : son interception des plans illicites
    contourne l'arbitrage moral du moteur (`prix_faute`) et son vocabulaire ignore les gestes récents ; retiré
    par le lot de ménage 130.
  - **Principe : réduire l'espace plutôt qu'ajouter un cache** (revue externe du 2026-10-24, retenue). Chaque cache
    (`_MEMOIRE`, les deux graphes repris, le certificat `_sans_plan`, la perception incrémentale, le court-circuit
    des devis) impose une clé exacte que tout lot doit tenir et que `VERIFIER`/`spatial.VERIFICATION` contrôlent.
    Préférer les gains d'algorithme (C1, saillance) ; après chacun, mesurer ce que rapporte encore chaque cache et
    retirer celui qui ne rapporte plus.
  - **Réduire l'espace sans perdre un plan** (revue externe du 2026-10-24, vérifiée dans le code à 5125d06). Rappel :
    68 à 88 % du coût de fin de nuit vient de recherches **sans plan**, qu'une borne A* n'accélère pas (il faut tout
    parcourir pour prouver l'absence) : seul un espace plus petit les rend moins chères. (P3) **Aller seulement vers une
    salle d'intérêt** : `gestes` offre un `aller` vers chaque salle accessible (`v.allers`) ; un plan n'a besoin de
    s'arrêter que là où il agit (objet ou porte en jeu, personne utile, lieu du but, abri), les trajets directs de
    `allers` couvrant le reste ; à prouver avec les coûts par minute (pression, noir, eau) et les gestes de recherche
    de personne. (P2) **Pertinence par chaînage arrière** : `Vue.pertinent` rend pertinents tous les outils de choc et
    de coupe dès qu'une serrure est crue verrouillée quelque part (`self.verrous`) ; ne garder que les moyens qui lèvent
    un obstacle entre le PNJ et ce que vise le but (contenant fermé, porte verrouillée sur le chemin), par une clôture
    complète sur les préconditions des gestes, fautes comprises. Prolonge C1 (lot 52). Contrat des lots 46 et 48 pour
    les deux. (P1) Une borne A* par « ancres de but » (distance minimale à la salle où le but se conclut) n'aide que les
    recherches qui trouvent un plan ; à mesurer après P2 et P3.
  - **Coût fixe, mêmes nœuds** (revue externe du 2026-10-24, vérifiée dans le code à 5125d06) : gains à décisions et
    nœuds identiques. **(a) et (b), lot 71 non fusionné** : trois clés géométriques sans réencodage de carte,
    préparation de `Vue` et entrées communes partagées pendant un choix ; la comparaison du témoin de carte
    reste linéaire, aucun partage d'un choix au suivant. Voir le rapport pour les mesures et limites.
    **Restent** : (c) `_explorer_etats`
    copie `etapes + ajout` à chaque transition poussée et `deepcopy` le chemin trouvé : un maillon (parent, ajout) et
    la liste reconstruite une seule fois. (d) `signes.percevoir_tous` recalcule les émissions et une signature (`repr`)
    de tous les acteurs à chaque événement : à profiler (la mine avait pris +35 % avec 3c). Les imports locaux des
    fonctions chaudes, aussi relevés, sont déjà sortis (lot 38). Un ou deux lots après C1 (lot 52), qui touche aussi
    la `Vue`.
  - **Bitsets dans l'état de recherche** : objets portés et faits de `Etat` en entiers à bits au lieu de `frozenset`
    (hachage, comparaison et `Etat.apres` moins chers, mêmes décisions). Lot de coût possible après C1, si la part
    d'`Etat.apres` au profil le justifie.
  - **Rust (PyO3) : rester en Python pendant les agendas.** La lenteur des bancs vient du nombre d'états explorés
    (planificateur 94-95 % en fin de nuit de 12 h), pas du langage ; PyPy était 1,5 à 1,7 fois plus lent. Option
    datée, rien avant A5 : extraire le seul noyau géométrique (vue, lumière, ouïe, trajets sur cases) si, après C1
    et la saillance, il dépasse ~30 % d'une nuit et que son contrat est stable ; condition : empreintes identiques
    au bit près (arrondis de flottants), chaîne de compilation sur les deux postes.
- **Après la peur transmise (lot 53)** : demander « qu'est-ce qu'il y a ? » à l'allié
  et suivre le regard d'un autre (attention conjointe) restent à faire ; coût de perception à mesurer.

- Routes et eau (lot 41, `codex-route-admissible`, non fusionnée) : les captures du refuge
  mouillé rejoignent le sec ; les traversées en cours ne sont plus coupées par l'horizon du séjour.
  Restent la durée moyenne par salle (occupation et actions futures non prédites), les attentes
  d'un passage mobile et les besoins concurrents ; ne pas promettre la disparition générale des
  boucles. CPU +17 % sur la paire finale crue 1985 ; archives d'audit `ffcc295` absentes ici,
  comparaison complète des deux nuits de 12 h à refaire sur le poste qui les possède.


- **Coût sur 12 h**, après le lot 38 (`codex-cout-12h`, non fusionnée) : −20,2 % à la mine, −15,6 %
  à l'auberge contre `63a717c`, mais encore ×2,39 à ×3,71 contre `42bb9c0` par nuit (42/1985).
  La borne terminale, les caches exacts des parts/devis et les références des fonctions chaudes sont faits.
  Le surcoût croît toujours en fin de nuit : mêmes 1,60/2,19 M états à la mine, 0,99/0,68 M à l'auberge,
  mêmes 272/471 et 8/1 recherches bornées que la base. Le profil de reprise à 8 h reste à 94–96 % dans
  l'exploration ; approches 26 %, devis 18 %, imports moins de 1 %. Une borne positive générale sur les
  états ordinaires reste ouverte ; ne pas retirer des états dominés ou changer leur plafond en prétendant
  conserver les recherches bornées. [Mesures, admissibilité et limites](taches/rapport-codex-38-cout-12h.md).

- Coût exact (lot 31, `codex-cout-exact`, fusionnée) : l'explosion du coût joueur du profil
  fourni n'est pas reproduite par les profils cProfile des fusions Q, R, 25, 26, 27 et 30 :
  48 transactions et 49 mémorisations sur chacune des nuits mine 42, 4 h, joueur en galerie.
  Le départ natif augmente les lectures, mais ancien/base restent comparables sur ces postes.
  La portée trop courte de la mémoire physique est commune aux deux versions ; le lot l'étend
  à la transaction. Les symboles de carte recalculés, les copies complètes et les lectures
  de `deliberation.autour` par le banc ne sont pas réduits. Le CPU reste ×1,28 / ×1,55 contre
  `42bb9c0` (mine/auberge, 4 h, 42/1985), malgré −20,6 % / −17,6 % contre 2590c4a.
  Aucun lot fautif affirmé pour la hausse joueur non reproduite.

- Relations 3c, après `codex-signes-calibration` (fusionnée) : cache incrémental,
  relectures sans réapprentissage et refus local d'observation corrigés ; répétitions
  27 → 0 sur le rapide final. **Calibration ouverte** : historique du réglage provisoire 4/3/8,
  21,32 % de méprises sur 816 lectures de 4 h, encore au-dessus de 20 % ; les mesures
  PSY réglées précèdent le dernier correctif de continuité. Refaire grille commune,
  justesses haute/basse, abstention par sorte et contrôles longs à l'intégration,
  selon « Rythme des lots » (42bb9c0), sans relancer de campagne dans le lot.
  `test_mine.py:84`, en échec sur la branche (à 600 min, Bram garde ses biens à 100 malgré sa
  sécurité à 100, sans lumière ni compagnie fiable), passe après fusion avec Q : la nuit a changé ;
  l'arbitrage garde/sécurité qu'elle révélait n'est pas tranché en général (aucun test ne le fixe).
  Le coût isolé économise seulement 1,5 % à la mine face à 8855312 ; la comparaison
  à 276524c porte sur des nuits différentes. Vols vus : ablations mine 7 et 11,
  effets de positions/orientations ; tentatives maintenues, aucune dissuasion par
  les lectures démontrée. Trajet isolé 8f60441 gardé avec Q (`Vue.descente` dans la marche).
  Lot 129 fusionné sans son réglage : critère bas révisé à 0,7, aucun réglage commun
  admissible ; l'utilisateur garde 4/3/8 (2026-10-26), calibration close en l'état.
- Force 4c (critère partiel) : aux valeurs actuelles, Aubin fuit comme Ilse au lieu de riposter ou de se
  dégager ; la fin de tout affrontement en moins de dix minutes n'est pas prouvée (les poursuites gardent
  rejoindre, chercher, appeler et la patience) ; le risque d'une riposte est l'estimation `force.force_crue`
  et un surcoût d'exposition forfaitaire, pas un duel simulé. `defense.choisir` met la sécurité à 100 en
  présence d'un danger (écriture directe d'un besoin, pas une épreuve graduée). Le souvenir `secours` (cri
  d'un protégé, P) et le champ d'esprit `secours` (appel à l'aide, K) portent le même nom pour deux choses.
  La contre-revue ne refuse plus une réaction mal choisie que par jugement (« je m'enfuis » typé `se_rendre`
  n'a pas été essayé avec Luna).
- Auberge 8 h, graine 42 : les recherches bornées de Lucien (`garder:grenier`, `garder:etable`, 66
  notées par `planification.BORNES` depuis `codex-garde-pret`) : la garde plus chère à l'ambition 70
  rend ces recherches plus longues que la borne de 4 000 nœuds.
- Mine après `codex-signalements` : nuits divergentes où Josse et Rémy enchaînent des recherches
  bornées (graine 2024 : 73 au lieu de 2, 2,5 fois le temps de la nuit) ; à examiner avec la recherche
  du porteur quand ses salles sont écartées (`appels_vains`).
- Part estimée (`codex-part-estimee`) : le devis suit un ordre fixe (recharger la source, puis aller à la
  flamme) ; il peut payer le noir plus longtemps que la chaîne détaillée et faire perdre un recours ponctuel
  (Anselme, auberge 11, minute 585 : `endure` au lieu de prendre la lanterne, demander l'huile, revenir au
  poêle) ; ce n'est pas une borne admissible de l'optimum (pessimiste sur les préparatifs multiples, optimiste
  sur les délais et les autres). Le devis a un coût propre : à la mine, la fusion est ×1,04 au processeur
  sur 8 h mais une graine (1985) coûte +9 % ; le rapport mesurait +6,8 % contre 4fc5212.
- Luna, après `codex-luna-restes` : le sens des références d'audience est comparé
  par le moteur et la revue reçoit les conséquences des achats ; les positions sont en mètres avec
  garde déterministe des unités. Le choix d'audience reste sémantique (`soir-appel`, une correction
  sur deux passes) ; faux refus encore vus sur la manière d'un sifflement. Le nom saisi non relié donne
  désormais un refus local avant le MJ (`codex-nom-non-relie`, fusionnée), pour le lexique
  dérivé du monde ; un nom extérieur au lexique et la sémantique des formulations restent hors
  de ce contrôle déterministe, notamment les formulations mixtes classées comme parole.
  Les conditions sur un absent nommé reçoivent aussi le refus local.
  Aucune garantie générale supplémentaire pour la narration.
  Le lot `codex-designations` (fusionné) reconnaît les noyaux publics malgré leurs
  qualificatifs ; les deux revues reçoivent leurs liens canoniques et les faits publics.
  La compatibilité sémantique des qualificatifs et les paraphrases restent à surveiller :
  ce lien lexical ne garantit pas toute phrase ni toute absence de faux refus.
  Ambiance : la branche `codex-ambiance`, fusionnée,
  distingue le vocabulaire de preuve et la perception dans le garde commun et les règles existantes.
  Le garde lexical ne garantit pas la détection de toute paraphrase de méta-preuve ; les
  contradictions de sens et la qualification d'une ambiance restent en partie sémantiques.
  La passe finale de cette branche garde un refus discutable du silence au Relais, motivé par le
  bruit courant et le fredonnement antérieur : ne pas clore le critère d'absence de faux refus.

- Passer sous un obstacle (`codex-sous-obstacle`) : gabarits humains par défaut (170 cm, 70 kg, carrure
  déduite par convention, pas du portrait) ; un objet porté sans dimension compte pour un mètre, d'où
  l'escalade refusée à qui porte un briquet ou une lanterne non décrits (85 cm au plus). Depuis
  `codex-luna-restes`, forme inconnue : le moteur dit immédiatement ce qui manque à une question ;
  une qualification valable et sa suite peuvent être validées en trois appels, la plausibilité
  restant sémantique. Depuis `codex-trajets-reels`, une salle coupée sans franchissement cru est
  inaccessible aussi dans le plan. Coût : +4 à +5 % au processeur, dont la preuve de domination et sa clé.
- Trajets réels (`codex-trajets-reels`, fusionnée) : le coût en minutes abstraites par salle est
  réglé (`obstacles.cout_route`, une seule mesure). Restent :
  - après le lot 30 (`codex-trajet-estime`, fusionnée), la position est retirée des états
    et les trajets sont estimés par salle : nœuds environ divisés par deux contre l'intégration
    `ecbbed7`, mais CPU encore **×1,64 (mine) / ×1,85 (auberge)** contre `42bb9c0` sur 4 h,
    graines 42/1985. Cible ×1,3 non atteinte ; le lot ne prouve pas l'absence stricte de toute
    répétition nouvelle (lecture sociale mine 7). Les salles coupées ne distinguent plus la
    composante de départ ; les approches locales peuvent échouer au contrôle réel ;
  - l'échelle des préférences inchangée (`DEMANDE`, `CHERCHER`, `TACHE`, `RESTER` face à des trajets de
    quelques secondes) ;
  - **fuite ↔ sécurité** (déjà sur `main`, Relais 2024 à 12 h : Ilse 165 passages en une heure ; après la
    fusion 37) : après une vraie violence (Aubin assomme Brune pour prendre torche et planches), Ilse fuit
    l'auteur vers la conduite noire ; la fuite s'achève dès que la salle diffère, puis l'abri (Gorm, au refuge
    éclairé) ou la lumière la ramène dans la salle de l'auteur, et `defense.choisir` la fait refuir.
    **Corrigé sur `codex-fuite-lumiere`, non fusionnée, lot 155** : auteurs actifs communs,
    pression sociale, terminaux lumière/abri et revalidation des recours, `_entrees` couvert.
    Capture Brune crue 2024 et autre scène d'Ilse vérifiées après recharge ; ce correctif
    ne prouve pas l'absence de toute boucle entre les autres besoins ;
  - **faim ↔ eau** (crue 2024, Brune heures 5-6) : le seul chemin de la galerie aux vivres du refuge traverse la
    conduite basse, que Brune attend noyée (116 cm) ; le parcours n'écarte que les salles crues noyées
    (`noyee_crue`) et `Vue.descente` ne juge que la salle d'arrivée, mais `eau.en_peril` juge la salle
    traversée : prise dans la conduite à une minute ronde, elle remonte s'abriter, puis la faim la renvoie.
    Déjà possible sur `main` (là, elle passe entre deux minutes et mange). Le lot 41
    (`codex-route-admissible`, non fusionnée) remplace cette proposition : même admissibilité pour
    recherche, marche et traversée en cours, mais durée du passage distincte de l'horizon du séjour.

## Décisions en attente

- **Agendas des PNJ, mandat et groupes** (`docs/plan-agendas.md`, branche `plan-agendas`, fusionnée,
  documentation seule) : un agenda est un projet durable, révocable, en sommeil ou actif, choisi sur la
  même échelle d'urgence que les besoins ; le mandat confie un agenda à un autre ; un groupe de départ
  fixé par le scénario est un état initial réévalué par les mécaniques communes (`docs/plan-social.md`).
  Sept décisions du 2026-10-23 dans la section 10 du plan : autorité à trois sources (statut du
  scénario, sixième axe « ascendant », lecture dérivée) ; un agenda passe devant un besoin pressant non
  désespéré, jamais devant le désespoir, une alarme ou le péril de l'eau ; Luna reçoit ce que le PNJ est
  prêt à dire à Corvus et ce que Corvus a entendu, jamais un agenda secret ; ténacité selon la VOL ;
  banc des groupes, la crue étendue aux évacués du hameau (six à huit PNJ) ; au plus trois agendas
  actifs ; le plan de décision (habitudes, réflexion limitée) repris après A4. **Ordre des lots**, un à la
  fois (tous touchent `planification.py` ou `deliberation.py`) :
  1. **Q, trajets réels** (`codex-trajets-reels`, fusionnée) : il absorbe ce que liste « À revoir » pour O
     (`obstacles.cout_route` et ses appelants, la preuve de domination, `defense.chemin_fuite`), une seule
     fonction de route. Il change le comportement (un trajet passe d'environ une minute à quelques
     secondes : demander, la faute et le noir pèsent relativement plus) : banc rapide avant et après,
     écarts lus dans le récit, aucune usurpation, temps de calcul.
  2. **A0, le choix du but sur une échelle commune** : chaque candidat de `deliberation._candidats` porte
     une urgence comparable dont l'ordre actuel découle ; empreintes identiques sur 2 h puis 8 h, quatre
     scénarios × quatre graines, sur la base laissée par Q.
  3. **A1, le socle des agendas** : `donjon/agendas.py` seul accès, les engagements y sont portés ; aucun
     changement de comportement, contrôle AST comme le socle des relations (3a).
  4. **A2 = 3e (propositions)**, puis **A3 = 3f (avis)**, tels que prévus dans `docs/plan-relations.md`.
  5. **A4 à A8** selon le plan ; après A4, mesurer le coût avant de décider du plan de décision
     (esquisse : `docs/plan-decision.md`, habitudes, réflexion limitée, recherche complète en dernier
     recours ; rien de décidé). Précaution à reporter dans les briefs d'A4 et d'A5 : le choix du prochain
     sous-but et celui d'un mandataire restent des fonctions séparées, appelées chacune à un seul endroit.
  Chaque brief renvoie à `docs/plan-agendas.md` pour le contexte, sans élargir le périmètre du lot ; un cas
  réel et un autre de même nature vérifiés après rechargement ; limites dites dans le rapport.
- **Fabrication générale** (`docs/plan-fabrication.md`) : étapes 1 à 3 fusionnées ; l'étape 4
  (d'autres usages : passerelle, cale…) attend un accord. Limite : les planches du Relais ne
  suffisent pas à une échelle (deux pièces, à Aubin) ; l'assemblage de planches est vérifié en
  test sur l'atelier, pas en partie au Relais.
- **PNJ d'abord, joueur passif** : la crue du Relais comme scénario d'étude (`docs/plan-crue.md`,
  étape 3, le niveau d'eau, faite ; suite : influence et relations) ;
  caractères, valeurs, relations, lire les autres, contrainte et groupes (`docs/plan-social.md`).
  Faits : temps fin et orientation, jeu dans le navigateur, caractères et valeurs (sans
  l'empathie), niveau d'eau, l'ouïe et la parole (`docs/plan-ouie.md`) ; réglages de l'ouïe à trancher : l'échelle, le crochetage en geste bruyant,
  l'inquiétude d'un bruit inconnu, le courage qui fait aller voir ; les réflexes déclarés et le
  souvenir « son » sont fondus dans l'ouïe commune (branche `ouie-commune`).
  l'inquiétude d'un bruit inconnu, le courage qui fait aller voir ; à fondre ensuite : les réflexes
  déclarés et le souvenir « son » dans l'ouïe commune.
- **Étape 4 du plan social, le corps et la force** : 4a, 4b et 4c fusionnées (`codex-force-4a`, `codex-force-4b`, `codex-force-4c`) ;
  4c avec les limites de critère de son rapport (voir « À revoir ») ; 4d partiellement
  réalisée sur `codex-force-4d-tenir` (lot 126 : prises et liens) et `codex-trainer`
  (lot 134 : traîner), non fusionnées. Le reste de 4d, puis 4e et 4f restent à réaliser,
  dans `docs/plan-force.md`. Décisions de
  la tâche 4a appliquées : recommandations retenues, sauf douceur 100 qui pourra se défendre
  ou défendre un protégé. Aucun geste de violence en 4a.
- **Manques relevés par la mine et l'auberge** : avoir de la lumière comme but (branche
  `lumiere-besoin`) ; prêter, permissions déléguées et l'argent (branche `echanges-argent`) ; un
  besoin que rien n'apaise (le devoir reste urgent une fois franchi son seuil ; il attend désormais
  sans compter comme « sans recours », branche `besoins`). Demander du bois pour un feu et le protégé
  nourri en boucle : branche `entretenir-feu`. Chercher quelqu'un dans le noir, le lieu dans une
  rumeur et le contenant fermé cru ouvert : branche `constater-et-rumeurs`.
- **Voix** (branche `voix`) : imiter une voix, plus ou moins bien (un changelin qui dupe les PNJ),
  puis des PNJ qui, sachant qu'un imitateur rôde, se méfient même d'une voix connue. Préparé : toute
  reconnaissance passe par `voix.reconnaitre` (`docs/plan-ouie.md`, « Suite prévue »).
- **Instructions conditionnées à l'état du monde** : plus tard ; critère retenu, inclure une
  règle quand le moteur pourrait valider ce type de proposition dans l'état actuel, jamais
  selon un lieu ou un scénario.
- **Suite du plan PNJ**, au choix (la crue est reprise dans `docs/plan-crue.md`) :
  - un événement qui éteint le feu en laissant du bois (les `horloges` existent, aucun
    scénario n'en déclare encore) ;
  - la voix des PNJ : Luna donne voix aux échanges entre PNJ dont le joueur est témoin, et
    les répliques ne contredisent plus l'issue décidée par le moteur ;
  - une protection plus riche ; d'autres remèdes au froid ;
- **Branches d'essai**, poussées sur `origin` et non fusionnées :
  - `essai-code` : le MJ écrit un script Python borné au lieu du JSON ;
  - `essai-haiku` : premier adaptateur Anthropic, remplacé par celui de `banc-haiku`.
  Les mesures sont rapportées dans leurs commits.

## Reprendre sur un autre poste

1. `git clone https://github.com/msicsic/jdr.git`, puis l'installation du README (`.venv`,
   `requirements-tui.txt`, `requirements-chatgpt.txt`).
2. Connexion de Luna : `python connexion.py connecter` (forfait ChatGPT, voir
   `docs/connexion.md`). L'autorisation (`.seuil-auth/`) n'est pas versionnée et se refait
   sur chaque poste.
3. Clés éventuelles dans `.env`, non versionné : `OPENAI_API_KEY` pour `--connexion api`.
   `ANTHROPIC_API_KEY` pour `--connexion anthropic` (Haiku, `requirements-claude.txt`).
4. Vérifier : `python -m unittest discover -s tests -q`.

Non versionnés, donc absents d'un nouveau poste :
- `sauvegardes/` ;
- `artifacts/` (chroniques et verdicts des bancs, traces du MJ). Les bilans chiffrés des bancs
  sont recopiés dans `docs/plan-pnj.md`.

## Outils de mesure

- Coût déterministe, sans Luna : `python tools/mesure_cout.py --reference 42bb9c0
  --branche integration --verifier --sortie artifacts/cout.json`. Par défaut : auberge 1985
  12 h fixe/tiré et mine 1985 12 h fixe ; `--scenario`, `--graine`, `--heures`, `--depart`
  pour une nuit. Références figées en commits, worktrees détachés nettoyés, aucun checkout
  du worktree courant. Cache commun `<commit>/mesure_cout/`, clé incluant configuration,
  version de la sonde et vérification ; `--sans-cache` ignore et ne remplit pas le cache.
  Compteurs entiers par heure et PNJ × but, totaux et moyennes par heure : appels de
  `choisir` (but `__choix__`, car un choix compare plusieurs buts), recherches, neuves,
  reprises mémoire, graphes réutilisés, passes, nœuds examinés de toutes les passes,
  nœuds de certificats, générations et propositions de gestes réellement produites.
  Une reprise de graphe sans réponse mémorisée reste une recherche neuve selon le banc.
  Les nœuds incluent les terminaux examinés ; les gestes comptent les sorties du générateur
  (une proposition immédiate ou différée), pas les gestes exécutés ni les arêtes uniques.
  Générations des certificats incluses, nœuds des certificats séparés. Ventilation à l'heure
  de début de recherche ; intervalle `[h*60, (h+1)*60[`. Le CPU instrumenté est indicatif.
  `--verifier` exige deux mesures identiques et des empreintes identiques au témoin sans
  sonde (chronique, récit, souvenirs, mesures et état complet). Un seul calcul à la fois
  par invocation, priorité réduite ; aucune suite complète nécessaire pour cet outil.
- Suite sans appel au modèle, par fichiers isolés : `python tools/tests.py` ; moitié des cœurs
  par défaut, `--processus N` pour régler la charge. Fichiers en arguments (`tests/test_web.py
  tests/test_tui.py`) ou `--motif "test_*banc*.py"` ; `--sortie artifacts/tests.json` pour les traces
  et temps détaillés. Les durées dans `artifacts/durees_tests.json` servent aux exécutions suivantes
  (fichiers les plus longs en premier). Rendu et comptes de `unittest`, y compris subtests, erreurs
  d'import, sauts, échecs attendus et succès inattendus. Code 1 si échec ou processus interrompu.
  Le mode `--processus 1` garde l'isolation par fichier ; la référence en un seul interpréteur reste
  `python -m unittest discover -s tests -q`.
- Comparaison sans Luna : `python tools/comparer_bancs.py --reference main --scenarios relais mine
  --processus 2 --sortie artifacts/comparaison.json` : 4 h, graines 1985/7/42/2024, salles passives
  adaptées aux scénarios ; `--branche REF` pour une référence git, sinon fichiers du worktree courant.
  Worktrees détachés créés et supprimés automatiquement, sans changer la branche principale.
  `--depart fixe`, `--verifier`, `--joueur mine=galerie` ; tableau moyenne [min–max], audit des boucles,
  usurpations, plantages, temps écoulé et temps processeur par nuit (`secondes_cpu` dans le JSON).
  `--empreintes` : 2 h par défaut, identité de chronique, mesures et état final complet (`data`, SHA-256),
  code 1 si divergence. Première nuit dans l'ordre scénarios/graines, première minute observée par un
  rejeu instrumenté uniquement en cas d'écart (exclu des temps). Voir les limites dans le rapport.
  **Cache des références** : la référence (et `--branche REF`) est résolue en commit ; chaque nuit est
  lue dans `artifacts/references/<commit>/comparer_bancs/f<format>-i<observation>/` avant d'être jouée,
  et rangée une fois jouée (un fichier par nuit, nommé par scénario, graine, heures, départ, salle du
  joueur, empreintes, `-verifier`, `-localiser` ; la clé complète relue avant réemploi ; `i…` est
  l'empreinte du code de `jouer_nuit` et de `audit_nuits.py`). Une nuit plantée n'est pas rangée ; le
  worktree courant jamais. Le worktree de la référence n'est créé que s'il reste une nuit à jouer. La
  sortie dit combien de nuits viennent du cache et que leurs temps ont été mesurés dans d'autres
  conditions de charge ; `--sans-cache` rejoue tout, pour comparer des temps.
- Cache commun (`tools/references.py`) : dossier du dépôt principal, partagé par ses worktrees
  (`SEUIL_REFERENCES` le déplace). `python tools/references.py lister` (commits, sujet, contenu par
  outil, taille) ; `purger [--garder N] [--simulation]` retire les commits qui ne sont plus des ancêtres
  de `main` et ceux qui ont plus de N commits de retard ; un dossier qui ne se résout pas en commit
  est signalé, jamais retiré.
- Luna en plusieurs passes : `python tools/banc_multi.py --variante main=main --variante lot=. --repetitions
  1 --connexion chatgpt <scripts>`. Une variante résolue en commit réemploie ses parties déjà jouées,
  par script : `<commit>/banc_multi/<script>-<connexion>-<effort>-<réflexion>-m<max-appels>[-offline]-<empreinte>/partie-<n>.json`
  (`cle.json` : contenu du script et de `banc_parties.py`, options) ; la passe i prend la i-ième partie
  rangée, seuls les scripts manquants se jouent. Une partie arrêtée par le budget ou touchée par une
  erreur technique n'est pas rangée ; `nom=.` jamais. Le résumé dit, par variante, les passes venues du
  cache ; `--sans-cache` rejoue tout.
- Banc moteur seul, sans appel à Luna, avec son récit (`--chronique` pour chaque pas) :
  `python -m donjon.banc_pnj --heures 8 --graine 1985 --joueur chambre_cloche` ; plusieurs nuits
  en parallèle, avec le tableau des mesures et leur moyenne : `--graines 1985 7 42 2024`.
  `--diagnostic` ajoute les recherches du planificateur par PNJ et par but (issue, reprises de
  la mémoire, nœuds, durée), aussi dans `--sortie`.
  `--scenario crue` joue la crue : récit de l'eau (tirage, salles gagnées, feux noyés, où chacun
  finit) et mesures `minutes_dans_l_eau`, `feux_noyes`, `trempes_fin`, `au_sec_fin`.

## Règles de travail

- `AGENTS.md` : corriger l'invariant général, jamais le cas de l'exemple ; vérifier le cas réel
  et un autre cas de même nature après rechargement ; dire les limites.
- Une branche par jalon, fusionnée avant d'ouvrir la suivante ; pas de nouveau mécanisme en
  cours de jalon sans accord.
- Les phrases des docs tirées d'un test ou d'un scénario décrivent ce scénario, pas une règle
  de conception du jeu.
