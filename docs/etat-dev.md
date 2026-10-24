# État du développement

Point de reprise, à tenir à jour à chaque fin de jalon. Mis à jour le 2026-10-25.

## Où on en est

- Branche `codex-offre-sensee`, non fusionnée, lot **57**, base **c592d68** : le
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
    une donnée doit l'y ajouter, sinon `VERIFIER` casse) et sérialisé à chaque appel (~17 % de coût fixe à
    l'auberge : 2 200 vues et entrées pour 1 350 recherches). Pistes : un compteur de révision par facette de
    l'esprit, incrémenté dans les seules portes d'écriture (`esprits.croire`, `relations`, `agendas`, refus,
    mémoire) ; ou une trace automatique des lectures de la recherche. Après C1 ; lot risqué (toute la mémoire).
  - **Le stratège Luna des PNJ** (`--stratege`, désactivé par défaut) : son interception des plans illicites
    contourne l'arbitrage moral du moteur (`prix_faute`) et son vocabulaire ignore les gestes récents ; à retirer
    ou à cantonner, lot de ménage.
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
    nœuds identiques, à mesurer au profil avant de les classer. (a) `obstacles.metrique_necessaire` sérialise toute la
    géométrie (`json.dumps(m.data["salles"], …)`) pour sa clé à chaque appel, alors que ses calculs réels sont rares :
    une clé légère (identité immuable de la carte, obstacles, gabarit, allure). (b) `Vue(monde, id)` et la partie de
    `_entrees` qui ne dépend pas du but sont refaites pour chaque candidat d'un même `choisir` : les construire une fois
    par état du monde et de l'esprit (le diagnostic mesurait ~17 % de coût fixe à l'auberge). (c) `_explorer_etats`
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
  27 → 0 sur le rapide final. **Calibration ouverte** : réglage provisoire 4/3/8,
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
    éclairé) ou la lumière la ramène dans la salle de l'auteur, et `defense.choisir` la fait refuir. Correction
    proposée : la salle crue d'un danger actif (`defense.auteurs`, `salle_crue`) pèse dans `Vue.pression` comme
    une présence crainte et n'est pas un abri (`_plan_abri.sures`) ; lecture à mettre dans `_entrees` ;
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
  4c avec les limites de critère de son rapport (voir « À revoir ») ; 4d à 4f
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
