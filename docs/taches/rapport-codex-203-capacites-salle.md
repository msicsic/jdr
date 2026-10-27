# Lot 203 — capacités et frontières de salle

27 octobre 2026 ; `codex-capacites-salle`, base **2fe05b9** vérifiée. Diagnostic
seul, sans Luna ni fichier du jeu modifié. Lectures : AGENTS, état-dev,
plan-prompt, rapports 151/152/154. **La proximité manuelle reste bornée au secteur,
contrairement au contact entre personnages : la décision n'est pas garantie.**

Inventaire par contrat partagé (alias regroupés). Chemins dans `donjon/`, lignes
sur cette base. C = capacité ; S = secteur légitime ; M = représentation MJ gelée.
Possession, matière, charge, intégrité, conscience et outils restent des conditions
indépendantes nécessaires.

| Règle : fichier, fonction, ligne | Condition → classement | Cas → proposition |
|---|---|---|
| `commandes.analyser:280`, `_nomme:152` ; `monde.designable:324` | Nom, vue ou souvenir ; pas de salle obligatoire. | A/B résolus ; préserver désignation ≠ accès. |
| `spatial.proche:275`, `_salle_position:157,195` ; `proximite.exiger:11` | Cible dans **la salle de l'acteur**, distance ≤ 1, diagonale praticable, ou bien porté. **C contraire.** | A/B refusés au seuil ouvert. **P1** : portée topologique commune, passage fermé exclu. |
| `monde.present_physique:257`, `accessible:309` | Présence récursive par salle/contenant ouvert ; en cases : vue ou porté/connu proche. **C**, repli tactile sectoriel. | **P1** conjointement avec accès et portée ; conserver les contenants fermés. |
| `moteur.Moteur._preparer:413–460` | Examiner : vue, détails proches ; toucher/fouiller un contenant ouvert : main ; lire/copier : main + lumière. **C.** | A/B examinables, détails dits lointains, toucher refusé. **P1** ; aucune action de fouille de salle entière trouvée. |
| `moteur._preparer:413–664` ; `operations.compiler:160,185` | Ouvrir/fermer, verrouiller/déverrouiller/crocheter, frapper/couper un objet, détacher, caler/débloquer : accès + main + outil approprié ; crochetage modulé par lumière. **C.** | Héritent de **P1**, préparation commune aux séquences. |
| `operations.compiler:185–412`, `a_portee:125` | Prendre/voler/prélever/manger/allumer/éteindre/alimenter : accès + main ; ressource proche/portée ; contenant destination ouvert/proche. **C.** | A/B : prise refusée. **P1**, tous les participants du geste. |
| `deplacement_objet.destination_depot:11`, `deplacer:38` | `sol` → stockage salle courante, position aux pieds. **S stockage.** | L8 correct ; préserver la case effective. |
| `moteur._preparer:397,484` ; `dialogues.verifier_don:202`, `verifier_remise:236` | Donner/remettre : destinataire validé puis main ; acheter : vendeur présent puis main. **C.** | Héritent de **P1** ; vente/remise au seuil non rejouées. |
| `combat.valider:57`, `tenir.valider:196`, `corps.ranimer:383`, `passage.au_contact:70` | Combat personnel, prises/liens/libération/traînage/mise à mort, ranimer/pousser : contact par pas accessible, seuil compris. **C conforme.** | Contact vrai A/B ; référence topologique pour **P1**. |
| `paroles.destinataires:876`, `_contact:801` ; `dialogues.interlocuteurs:32` ; `pnj.peuvent_se_parler:1545` | Parler/demander : perception + ouïe réciproque ; chuchoter : contact. **C conforme.** | Parole vraie A/B ; ne pas appliquer la main aux voix. |
| `ecoute.entendus:53`, `_a_la_porte:38` ; `perception.eclairage:56`, `couverture_vue:78` | Niveaux reçus, bonus contre porte proche ; champ et propagation lumineuse. **S acoustique/optique.** | Secteurs conservés ; aucune permission par seule coappartenance en cases. |
| `pnj._accessible:619`, `_a_toucher:641`, `_approcher:1450` | Présence même salle puis proximité ; approche vers coordonnées crues locales. **C contraire.** | A/B : Brune côté Corvus n'atteint pas l'objet ; Gorm auprès le peut. **P1** en conservant croyances et marche. |
| `pnj.de_pres:1518` ; `deliberation.autour:718` | Même salle avant distance/acteurs vus. **C perceptive.** | A/B : `de_pres=False`, parole vraie. **P2** : contexte social borné à la perception ; effet décisionnel non mesuré. |
| `pnj._inspecter:549`, `_executer_effet:877` ; `obstacles.parcours_cru:368`, `cout_route:526` | Tour d'horizon depuis une position ; lieu cru et route estimée. **S.** | Conserver mémoire sectorielle, aucune inspection omnisciente démontrée. |
| `artisanat.ressource:130`, `preparer_usage:317`, `preparer_decoupe:579` ; `franchissement.compiler:124` ; `obstacles.compiler:590` ; `espace.compiler_saut:234` | Assembler/fabriquer/découper : ressources accessibles proches ; franchir/passer/sauter : main, géométrie, côtés bas/haut. **C + S topologique.** | **P1** pour les prises ; bas/haut reste une mécanique explicite. |
| `artisanat.obstacle_soin:252` | `travail_calme`, urgence du secteur, lumière projetée. **Donnée explicite de scénario.** | Atelier rechargé : accepté, puis refus si calme désactivé au même point. **P3** : décider d'une zone de calme perceptible. |
| `improvisation.preparer:194,224`, `compiler_effet:97` ; `moteur._preparer:268–395` | Improviser : cibles proches/effets compilés ; déplacement : pas ; orientation ; attendre/écouter sur place. Sans cases : aller par sortie, proximité désactivée. | **P1** pour improvisation ; **S** navigation. Mode sans cases incompatible avec une garantie universelle : maintien à préciser. |

**Reproduction.** Relais calme ; Corvus `antichambre (0,3)`, face ouest ; pas
ouest légal vers `echoppe (8,3)`, sans porte. A : crochets sur cette case ; B :
torche, copie indépendante. `je prends trousse de crochets` / `je prends torche`
→ « Approche-toi… », malgré vue vraie et contact vrai avec Gorm sur la case cible.
Même secteur : préparation acceptée. Sauvegarde/recharge avant et après saisie :
objets toujours visibles à l'échoppe, aucun transfert ; rendus archivés. Autres
verbes hérités de P1 établis par lecture, pas tous rejoués.

**MJ gelé.** Les quatre dossiers (`artisanat.dossier:485`, `franchissement.dossier:158`,
`obstacles.dossier:658`, `espace.dossier:187`) passent par `espace.objets_proches:166` :
L4 appliqué, mais A/B exclus par P1. `monde.contexte:395,443,479` copie le secteur
courant (sorties filtrées) et conserve des champs mécaniques des objets distants.
`mj._echanger:1074–1154` retire les coordonnées, pas tous ces champs : **M1**, projection
perceptive commune. Surfaces : `spatial.visible:447`, `_salle_position:196` ; sol
générique de l'atelier sans position propre visible/proche, envoyé complet : **M2/L7**,
surfaces paresseuses, portion ciblée. `improvisation.contexte:341` et
`narration.ambiance_etablie:1461` filtrent par salle : **M3**, mémoire locale distincte
de perception actuelle. `enrichissement.catalogue:30`, `faits_locaux.supports:115`
filtrent déjà vue/proximité (P1) ; `faits_locaux.potentiel:174` garde un budget
sectoriel explicite de scénario, à discuter séparément.

**Livraison et limites.** Ordre : P1 (actions), P2 (social PNJ), P3 (conception) ;
M1–M3 en veille. Bruts exclusivement `C:/Users/msics/donjon/artifacts/capacites-203/` :
sondes, copies, observations, saisies, sources numérotées, index AST des conditions.
Un processus Python à la fois, BelowNormal ; aucune suite/banc lourd, aucun temps
comparé. Index non exhaustif sémantiquement ; anciennes sauvegardes, tous les verbes
et décisions autonomes non rejoués. Aucune correction ni garantie générale annoncée.
