# État du développement

Point de reprise, à tenir à jour à chaque fin de jalon. Mis à jour le 2026-10-23.

## Où on en est

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
- Luna (`gpt-6-luna`) reste le MJ. Le stratège Luna des PNJ (jalon E) est optionnel
  (`--stratege`), désactivé par défaut. Remesuré sur le Relais de F, il n'apporte presque
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
- La suite de tests passe : 1535 tests (15 sautés sans `jsonschema`, facultatif pour MiMo), sans clé ni connexion (ceux du clic demandent Node). Même compte avec `tools/tests.py`.

## À revoir

- Relations 3c : calibration des lectures (41,3 % de méprises dans le banc de la branche, contre une borne de
  20 % ; justesse haute ≥ 0,8 atteinte seulement par Gorm à PSY 16) ; coût des signes (mine +35 % au
  processeur après fusion ; une invalidation sociale incrémentale au lieu de tout recalculer à chaque
  minute et événement) ; vols vus en baisse à la mine, l'auberge et la crue dans le banc de la branche, sans
  preuve que ce soit la dissuasion par les guets lus ; « Lecture de … » relue toutes les dix minutes
  (alertes `repetition` de l'audit) ; Luna à vérifier sur les bancs `signes-*` (protocole du rapport) et
  les scènes de force quand le service répondra ; dans le noir, `observer` une personne connue est refusé
  par l'analyse locale avec « cet objet » au lieu du refus du moteur (« cette personne »).
- `combat.prix_violence` n'est employé que par les tests (`test_combat`) ; le planificateur réécrit la
  même règle (`2 * v.degat <= ENJEU`, le double du prix de douceur sous le plafond d'enjeu) au lieu de
  l'appeler (relevé à la fusion de 4b) : une seule règle à garder.
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
- Luna après `codex-luna-noms` : faux refus sémantiques possibles de la contre-revue de fidélité
  (`tous` jugé individuel, achat dit sans transfert) ; une ambiance encore assortie d'une précaution
  sur les bruits.

## Décisions en attente

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
- **Étape 4 du plan social, le corps et la force** : 4a et 4b fusionnées (`codex-force-4a`, `codex-force-4b`) ; 4c à 4f
  restent à réaliser, dans `docs/plan-force.md`. Décisions de
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
  - la priorité du stratège aux PNJ que le joueur perçoit.
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
- Banc moteur seul, sans appel à Luna, avec son récit (`--chronique` pour chaque pas) :
  `python -m donjon.banc_pnj --heures 8 --graine 1985 --joueur chambre_cloche` ; plusieurs nuits
  en parallèle, avec le tableau des mesures et leur moyenne : `--graines 1985 7 42 2024`.
  `--diagnostic` ajoute les recherches du planificateur par PNJ et par but (issue, reprises de
  la mémoire, nœuds, durée), aussi dans `--sortie`.
  `--scenario crue` joue la crue : récit de l'eau (tirage, salles gagnées, feux noyés, où chacun
  finit) et mesures `minutes_dans_l_eau`, `feux_noyes`, `trempes_fin`, `au_sec_fin`.
- Banc A/B du stratège, avec Luna, environ 15 minutes pour 8 graines :
  `python tools/banc_stratege.py --graines 1985 7 42 2024 --graines-sup 3 11 99 500`
  Plusieurs exécutions Luna peuvent tourner en même temps (le coffre sérialise le renouvellement
  du jeton) : Luna pèse peu sur le quota, plusieurs bancs Luna en parallèle sont permis ; comparer les
  temps dans les mêmes conditions de charge.

## Règles de travail

- `AGENTS.md` : corriger l'invariant général, jamais le cas de l'exemple ; vérifier le cas réel
  et un autre cas de même nature après rechargement ; dire les limites.
- Une branche par jalon, fusionnée avant d'ouvrir la suivante ; pas de nouveau mécanisme en
  cours de jalon sans accord.
- Les phrases des docs tirées d'un test ou d'un scénario décrivent ce scénario, pas une règle
  de conception du jeu.
