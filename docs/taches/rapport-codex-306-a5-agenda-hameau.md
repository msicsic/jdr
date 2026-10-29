# Lot 306 — responsabilité d'évacuation dans le hameau

Branche **codex-a5-agenda-hameau**, non fusionnée, base initiale 7ec839e,
données/tests 8145e48, 29 octobre 2026. **Reprise après 309 en cours** :
fusion sans rebase de origin/integration **13ce328** dans **081e65b**.
Seul conflit de documentation, deux historiques conservés. Aucun changement
propre au lot 306 dans le moteur/MJ ; données inchangées après mesure.

**48 tests / huit fichiers verts après fusion**, sept fichiers du lot
et test_recit_agendas, 68,601 s, deux travailleurs réduits. Le test connu
d'ordre des mesures, pris en charge par le lot 310, n'est ni lancé ni
compté contre ce lot. Court témoin de capture : état final, chronique et
mesures identiques avec/sans captures supplémentaires.

**Banc détaché lancé sur 081e65b**, hameau 4 h × 1985/7/42/2024 contre
13ce328, cache commun, deux travailleurs réduits maximum, PID 20232.
Bruts séparés : C:/Users/msics/donjon/artifacts/agenda-hameau-306/reprise-309/,
fichier de fin attendu fin.json. Épisodes complets de la sonde commune
219/271/276, captures aux transitions et aux publications pour Aubin/Gorm
en 7 et Gorm en 2024, état final rechargé. **Instruction à terminer après
le calcul** : entrées publiées utilisées, renouvellement perceptif à
examiner, répétition sans entrée ou autre classe ; aucune alerte ne sera
déclarée légitime sur le seul compteur de suspects. Ni Luna ni suite
complète. Les résultats ci-dessous décrivent la première passe, avant 309.

**Invariant livré.** Gorm reçoit evacuer_crue, sorte amener, vers
chambre_cloche (la galerie), comme dans la crue. Ilse et Brune restent
concernées ; Maël et Sève s'ajoutent : évacués de maisons noyées, accueillis
au Relais, ignorants des salles basses. Gorm est décrit comme protecteur
des évacués ; Maël le connaît et lui fait confiance, Sève connaît Aubin et
Ilse. Sa garde ne suppose pas qu'elle connaisse son statut. Aubin conserve
sa surveillance des vannes. Aucun mandat initial, coût, lien, statut ou
savoir ajouté ; aucune raison pour une seconde charge informer.
Comparaison exhaustive contre la base : seul l'agenda change.
Liste fixée avant mesure et inchangée ensuite.

**45 tests distincts / sept fichiers verts**, deux travailleurs réduits
maximum. Déclaration, activation unique sur quatre graines sans
attribution ; Maël/Sève : accord réel puis marche autonome, monde,
scène, rendu et écoute rechargés, même temps continu/découpé.
Voisins : hameau, autorité, déplacement Ilse/Brune, faire/confier, compte
rendu, réaffectation. Premières erreurs des nouvelles scènes corrigées
sans affaiblir d'oracle ; temporaires Windows accessibles hors sandbox.
Sources/tests inchangés depuis cette validation.

**Crue : 4/4 paires 2 h identiques**, graines 1985/7/42/2024 : chronique,
mesures et empreinte de l'état final complet, aucun plantage.
**Hameau : trois nuits 4 h achevées, une interrompue** :

| Graine | Proposés / acceptés / refusés | Refus par cause | Galerie à 4 h, référence → branche | Agenda de Gorm |
|---|---|---|---|---|
| 1985 | 4 / 0 / 4 | jet 3, impossible 1 | 2 → 4 | atteint, min 62 |
| 7 | 5 / 2 / 3 | méfiance 1, impossible 2 | 1 → 2 | sommeil, refus |
| 42 | 3 / 3 / 0 à 5 min | aucun à l'arrêt | 0 → inconnu à 4 h | sommeil à l'arrêt |
| 2024 | 1 / 1 / 0 | aucun | 0 → 4 | atteint, min 161 |

Sous-mandats inclus (42 : Aubin → Ilse pour Brune). Confirmations,
comptes rendus, réaffectations : **zéro par nuit**, y compris avant
l'arrêt. Mandats atteints : **0/2/1 partiel/1**. En 1985, Gorm → Aubin
est refusé malgré coût 0,26 et bonus 4,8 : total 2 < DD 3,152.
Galerie : les quatre destinataires ; Sève y est déjà initialement.
Présence finale et arrivée crue ne prouvent pas une causalité exclusive
de l'agenda, ni le maintien ultérieur sur place.

**Échec hors périmètre.** Graine 42, minute 5 :
audit_nuits._releve → recit_pnj._but lève KeyError: 'qui' sur le but
valide d'Aubin {"type":"agenda","agenda":"a1"}. L'observateur suppose
une cible pour tout agenda. Reproduit sur capture rechargée ; monde
valide, rendu joueur et scène conservés. Cela prouve l'interruption du
banc, pas un plantage de l'exécution du jeu. **4/4 captures finales**
(dont celle à 5 min) conservent état, rendu, scène et empreinte.

Suspects 219 **0 → 0 par nuit**, quatrième branche limitée à 5 min.
À expliquer **2/2/7/4 → 0/5/0 partiel/11**. Bascules détectées zéro ;
passages horaires maximaux des trois paires complètes **12→33, 6→27,
20→25**. Nouvelles alertes en 7 : actif/sommeil d'Aubin 9/8 occurrences,
sommeil de Gorm 9, achat promis d'Aubin 28 ; en 2024, une alternance
« aller voir ». Elles restent à instruire ; aucune absence générale de
boucle revendiquée. Usurpations zéro sur les trois nuits et le début
de la quatrième.

Calcul détaché, deux travailleurs réduits, **851,143 s** : huit références
absentes calculées une fois et rangées, huit nuits de branche tentées.
Aucun gain de performance déduit. Bruts :
C:/Users/msics/donjon/artifacts/agenda-hameau-306/ ; résultats, captures,
traces et analyse-cloture.json. **fin.json conservé : ok=false**, codes
empreintes/banc **0/1**. Aucun rejeu à la clôture.
**Non validé pour intégration** : rendu des buts A5 puis répétitions à
traiter dans des lots distincts, sans ajuster le scénario.
