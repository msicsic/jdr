# État du développement

Point de reprise, à tenir **court** (une à deux pages). Mis à jour le 2026-10-30.
L'historique détaillé de tous les lots est dans [historique-lots.md](historique-lots.md) : à lire seulement
quand un lot ancien est en cause, jamais en entier. Les outils de mesure sont dans [outils-mesure.md](outils-mesure.md).

**Entrée d'un lot** (règle pour tous les agents) : une entrée de **8 lignes au plus** en tête de « Lots non
fusionnés » : branche, base, ce qui change (l'invariant), mesures clés, limites, lien vers le rapport. Le détail
va dans le rapport du lot, pas ici. N'écris pas dans `historique-lots.md` : le superviseur y range l'entrée à la fusion.

## Où on en est

- **`main`** : `0bad227` (avancée le 2026-10-29). **Intégration** : à jour sur `origin/integration`.
- **Refonte du MJ** : feuille de route [plan-refonte-mj.md](plan-refonte-mj.md) (état de chaque lot G/U/K/A).
  Fusionnés récemment : G2, G4, U-D, G5, G6, G7, G15, G16, G17, G18, G19, U-P, U-C, U-M outils/inventaire/fabrication/
  corps/passage/information, U-T premier geste/outils/inventaire/fabrication/corps/passage, A0 (oracle G1).
- **Groupe 1** (313, 315, 332, 333) et 335 (suivi vocal) fusionnés le 2026-10-30.
- **PNJ** : A5 (mandat) complet (lots 338, 340, 341, 306 fusionnés). A1 provenance publique fusionnée (346, non branchée).
  **Échéance négociée** décidée (lot 347, arbitrages acceptés le 2026-10-30) : lots E1 à E6 ; E1 à E5 fusionnés (348, 350, 352 et 357, 355, 359), E6 = 363.
- **Non validé, à repenser** : 329 G20 `codex-g20-signes` (Luna n'a pas choisi la sélection typée).
- **Suspendu** : G1 compact (294/296/304/311, `origin/codex-g1-compilateur`) ; reprise sous la forme A (lot 346).
- **Abandonnés** : archivés par tags `archive/<branche>` le 2026-10-30 (33, 36, 117 b/c, 162, 166, 168, 170, 176,
  198, 206, 235, 62, 63, 66, 75, 85 b, 118, 119, ancien C1, essais).

## Dernières fusions

- `codex-e5-choix-direct` (1bd2642f) : lot 359, E5 le choix direct conserve l'accord daté affiché jusqu'à la validation. Détail dans l'historique.
- `codex-attentes-perimees` (9f9d6fdd) : lot 361, attentes périmées encore rouges portées au contrat actuel. Détail dans l'historique.
- `codex-suite-rouge-7eb45ff` (198844a5) : lot 356, attribution de la suite rouge 7eb45ff et harnais du consentement. Détail dans l'historique.
- `codex-a5-agenda-hameau` (c7f4ed02) : lot 306, A5 agenda d'évacuation du hameau. Détail dans l'historique.
- `codex-revalider-apres-refus` (63d55dcd) : lot 358, une action différée est revalidée contre un refus encore valable. Détail dans l'historique.
- `codex-suivi-vocal` (c020b62a) : lot 335, suivi vocal. Détail dans l'historique.
- `codex-reclamations-repetees` (0925c556) : lot 315, réclamations répétées. Détail dans l'historique.
- `codex-e3-taches-payees` (999e4c67) : lot 357, régression d'E3 sur les tâches payées corrigée. Détail dans l'historique.
- `codex-attribution-groupe1` (8d1a4c3f) : lot 342, attribution du groupe 1. Détail dans l'historique.
- `codex-ut-corps-passage` (fe464411) : lot 353, U-T corps et passage au terminal. Détail dans l'historique.
- `codex-garder-lieu` (40bd537e) : lot 333, garder un lieu. Détail dans l'historique.
- `codex-attention-conjointe` (c3db8e29) : lot 332, attention conjointe. Détail dans l'historique.

## Lots non fusionnés

- **363 E6**, `codex-e6-libre-date`, base `integration a9f02e5c` : délai libre structuré résolu une fois
  avant transaction ; **clos mais non validé, ne pas fusionner comme E6 acquis**, code `f24c6a06`.
  145 tests distincts verts / 17 fichiers, zéro erreur ou saut ; parité et recharge huile/verrou simulées.
  Luna 14 scripts / 83 appels : huile acceptée/annulée ; « demain » invente 24 h, verrou mal compilé,
  clauses non portées parfois reclassées en parole/propos. Invariant général non acquis ; reprise du contrat requise.
  Bruts `C:/Users/msics/donjon/artifacts/e6-363/`, `fin-cloture.json` valide=false ; aucun calcul actif.
  [Rapport 363](taches/rapport-codex-363-e6-libre-date.md).

Lots en cours : 360 (régressions du lot 337), 362 (16 rouges restants hors 337). E6 (363) reste à reprendre après sa clôture non validée.
**Suite complète `f014c80` : 101 échecs, 3 erreurs, 71 méthodes** (65 déjà rouges sur 7eb45ff, 6 nouvelles) ; listes
dans `artifacts/suite-f014c80/` : 23 régressions du 337 (360), 32 attentes périmées (361, fusionné), 10 autres anciennes
et 6 nouvelles (362). Leurs entrées arrivent ici à leur livraison. 

## Décisions prises le 2026-10-30

- **Échéance négociée avant la menace** (lot 347, `docs/conception-menace-echeance.md`) : les six arbitrages de sa
  section 6 sont acceptés tels que recommandés (prestation ponctuelle avant une limite, payée maintenant ; dépassement
  = clôture sans sanction nouvelle ; durée incertaine non promise ; renégociation et offres PNJ en E7-E9 ; heure de
  jeu sans calendrier). Lots E1 à E6, puis évaluation avant E7-E9.
- **Confidences d'inventaire** (question du lot 360) : ce qu'un PNJ sait depuis le début de la partie n'est pas une
  nouvelle à confier ; seul un changement appris (garde rendue ou perdue, bien pris, déplacé, détruit) se raconte.
  Constat : les confidences suivent la confiance mais pas les besoins de l'auditeur (le filtre de pertinence reste le
  chantier 206/235/255, mis de côté).
- **Branches abandonnées** : 27 branches archivées par tag `archive/<nom>` puis supprimées (abandonnées, essais,
  `cache-kv-local`) ; gardées : `codex-g1-compilateur`, `codex-g20-signes`, `prompt-simplifie`.
- **Sessions de l'orchestrateur** ouvertes dans `.worktrees/integration` (etat-dev court) tant que `main` n'a pas
  avancé au-delà de l'allègement.

## Décisions prises le 2026-10-29

- **Lot 273, option B** : garder la clôture `dementie` d'une demande sur un moyen démenti et ne corriger que sa renaissance par la seule perception (lot 286). Les deux réalisations du 273 (Sol, DeepSeek), qui gardaient la demande, sont abandonnées : suspects 1 → 3 et richesse de la mine hors étendue dans les deux.
- **Refonte du MJ** : ce qui peut être écrit mécaniquement l'est par le moteur, de façon déterministe (regards, signes, pas, distances…) ; la narration est cosmétique et ne bloque pas la boucle de jeu, dans l'esprit de la branche `prompt-simplifie` (non terminée). Lot de conception 287 d'abord, sans code. Les lots 176, 170, 162 et 171 y sont versés ; le lot 166 (faits à la demande) est abandonné.
- **Refonte du MJ, décisions sur le lot 287** (section 10 de `docs/conception-refonte-mj.md`) : 2, 3, 5, 6 et 7 acceptées ; 6 complétée d'un retour visuel quand une ambiance est en cours de calcul ; 1 nuancée : l'ambiance reste secondaire mais sans erreur flagrante qui casse l'immersion ; 4 (fidélité de la saisie) : le joueur est le contrôleur, une ligne « Compris : … » précède les actes lourds ou irréversibles (comme la fiche tenter/annuler) et suit les autres, rien pour une action venue d'un clic ; contre-revue et fidélité de parole gardées en filet pour les seuls actes à effets pendant la transition, retrait décidé sur mesure. Nouveau regard demandé : la plupart des actions de base passent mieux par des actions directes (clic, menu) que par l'écrit ; le LLM sert à composer, aux dialogues complexes et peut-être aux contrats. Lot 288 de conception (game design) : ce que le LLM apporte qu'un moteur déterministe ne fait pas, et révision du plan G0-G21.
- **Refonte du MJ, décisions sur le lot 288** (section 8 de `docs/conception-valeur-llm.md`), toutes selon les recommandations : actions directes d'abord pour les gestes courants (texte libre toujours disponible) ; contrats en deux temps (suggestions déterministes K0 et éditeur de marché K1, puis assistance Luna à la demande K2, offres spontanées plus tard) ; conversation ouverte admise comme parole enregistrée sans effet caché (D0) ; ambiance avec projection publique enrichie, gardes communes et vérification de sens en fond, abandonnée si doute ; mécanique sociale suivante : finir A5, puis menace ou échéance négociée sur un cas de jeu. **Nouveau contrat du MJ inscrit dans `AGENTS.md`**, avec une clause de transition (une voie non portée garde ses contrôles). Ordre des lots : G0, puis G2, G4, U-D, puis G1, U-P, U-C, etc. (section 7 du lot 288).
- **DeepSeek V4.1 Flash** (version Go payante, réflexion high, PC fixe seulement, jamais en heures pleines 01:00-04:00 et 06:00-10:00 UTC) : diagnostics et lots de tests seuls ; le code reste à Sol. Bilan dans `docs/comparaison-deepseek-sol.md`.

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

## À revoir

- **MJ : suivi unique dans la [feuille de route de refonte](plan-refonte-mj.md).**
  Les pistes L2 à L8 et les audits ne forment plus un plan parallèle.
  L2/L3 vont à G1/G2/G3 ; L4 à G1/G5/G6/U-D ; L5 à G2 ; L6/170 est absorbé
  par G1 ; L7/166 est abandonné ; L8 reste un contrat de G2/G4/U-D/U-P.
  L'audit invariant 162 devient sans objet pour les voies portées ; les mesures
  171 vont à G6/G7, les attitudes 176 à G20. Les audits mécaniques restent
  jusqu'aux rendus de G4 à G7/G15 à G20. G8 à G11/U-A portent le contrôle
  cosmétique en fond, avec abandon entier sans relance si doute. G12/G13
  gardent les revues d'admission non calculable. U-P/U-C puis G21 règlent le
  filet de fidélité du libre à effets. Aucun retrait anticipé par G0.

- **Coût, suites retenues** (revue externe du 2026-10-24, retenue par l'utilisateur) :
  - **C1, mesurée sans gain, retirée des pistes actives (lot 285)** : sur les deux captures
    historiques mine/auberge 1985 à 480 min, aucun doublon hors lumière parmi 2 868/2 083 états
    observés ; nœuds 3 185/2 034 inchangés avec le prototype. Gain 0 %, arrêt au seuil du brief,
    aucun code livré. Les 94 à 99 % d'états avec préparatifs du diagnostic ancien ne prouvaient
    pas une redondance de capacités. Portée limitée aux captures et recherches du
    [rapport 285](taches/rapport-codex-285-capacite-nouvelle.md), sans conclusion sur toute une nuit actuelle.
  - **A, les entrées de la mémoire des recherches** : `_entrees` est un relevé écrit à la main (chaque lot qui lit
    une donnée doit l'y ajouter, sinon `VERIFIER` casse). Le lot 71, non fusionné, partage sa partie commune
    dans un même choix ; elle est encore refaite au choix suivant. Pistes : un compteur de révision par facette de
    l'esprit, incrémenté dans les seules portes d'écriture (`esprits.croire`, `relations`, `agendas`, refus,
    mémoire) ; ou une trace automatique des lectures de la recherche. Lot risqué (toute la mémoire).
  - **Le stratège Luna des PNJ** (historique, retiré au lot 130) : son interception des plans illicites
    contourne l'arbitrage moral du moteur (`prix_faute`) et son vocabulaire ignore les gestes récents ; retiré
    par le lot de ménage 130.
  - **Principe : réduire l'espace plutôt qu'ajouter un cache** (revue externe du 2026-10-24, retenue). Chaque cache
    (`_MEMOIRE`, les deux graphes repris, le certificat `_sans_plan`, la perception incrémentale, le court-circuit
    des devis) impose une clé exacte que tout lot doit tenir et que `VERIFIER`/`spatial.VERIFICATION` contrôlent.
    Préférer les gains d'algorithme (saillance ; C1 mesurée sans gain au lot 285) ; après chacun, mesurer ce que rapporte encore chaque cache et
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
    complète sur les préconditions des gestes, fautes comprises. Piste distincte des doublons de C1. Contrat des lots 46 et 48 pour
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
    fonctions chaudes, aussi relevés, sont déjà sortis (lot 38). À mesurer indépendamment de C1,
    close sans gain au lot 285.
  - **Bitsets dans l'état de recherche** : objets portés et faits de `Etat` en entiers à bits au lieu de `frozenset`
    (hachage, comparaison et `Etat.apres` moins chers, mêmes décisions). Lot de coût possible si la part
    d'`Etat.apres` au profil le justifie.
  - **Rust (PyO3) : rester en Python pendant les agendas.** La lenteur des bancs vient du nombre d'états explorés
    (planificateur 94-95 % en fin de nuit de 12 h), pas du langage ; PyPy était 1,5 à 1,7 fois plus lent. Option
    datée, rien avant A5 : extraire le seul noyau géométrique (vue, lumière, ouïe, trajets sur cases) si, après
    la saillance, il dépasse ~30 % d'une nuit et que son contrat est stable ; condition : empreintes identiques
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

Voir [outils-mesure.md](outils-mesure.md).

## Règles de travail

- `AGENTS.md` : corriger l'invariant général, jamais le cas de l'exemple ; vérifier le cas réel
  et un autre cas de même nature après rechargement ; dire les limites.
- Une branche par jalon, fusionnée avant d'ouvrir la suivante ; pas de nouveau mécanisme en
  cours de jalon sans accord.
- Les phrases des docs tirées d'un test ou d'un scénario décrivent ce scénario, pas une règle
  de conception du jeu.
