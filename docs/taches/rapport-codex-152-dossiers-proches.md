# Lot 152 — Dossiers techniques au contact (L4)

27 octobre 2026 — branche `codex-dossiers-proches`, **non fusionnée**, base
`45e9f95` (brief `63d7430`, mesure 149 intégrée en avance rapide). `main` intact.

**Invariant.** Les quatre dossiers techniques prennent leurs sources dans
`espace.objets_proches` : objets visibles et `spatial.proche`, biens portés compris.
`artisanat.dossier` filtre matières, assemblages, appuis et outils ; ses manœuvres
ne citent pas de support hors du filtre. `franchissement.dossier` filtre obstacles
et outils avant de borner les candidats ; `obstacles.dossier` filtre avant toute
préparation. `espace.dossier` filtre aussi les installations et leur support.
Sans coordonnées dans une ancienne sauvegarde, aucune portée au sol n'est
supposée ; les biens portés restent à portée. Les objets éloignés restent dans
la vue et les faits perceptifs. Aucun objet, scénario ou texte du joueur n'est
traité spécialement. Ni consignes, schémas, fournisseurs, actions, trajets,
`cout_route` ou décisions des PNJ modifiés.

**Preuves.** Six nouveaux tests, vrais parcours console avec MJ simulé, sauvegarde
avant saisie et recharge après : poutre du Relais et table de l'auberge, éloignées
puis adjacentes (fiche, passage et position finale) ; perche de l'atelier éloignée
puis au contact (découpe préparée sans consommation) ; mur de l'atelier éloigné
puis proche (dossiers de franchissement/espace, saut préparé sans déplacement) ;
perche portée, obstacle dans le dos, perception absente, installations éloignées,
ancienne sauvegarde sans position. État et rendu rechargés contrôlés. Les anciens
tests de dossier placent désormais explicitement leurs matières/appuis au contact ;
le refus moteur sur une cible éloignée reste exercé même quand le dossier est absent.
Six nouveaux tests verts ; 63 ciblés existants verts après adaptation des placements.
Suite complète unique : **2 169 tests, 244 fichiers, 1 242,46 s**, deux processus
réduits ; **deux échecs MiMo historiques `6 != 5`**, zéro erreur, zéro ignoré.
Ils sont déjà consignés au point de reprise (lots 145–147) :
`test_fournisseurs_jeu.test_mimo_correction_avant_action_sur_deux_scenes`
et son parcours repris par `test_restes_fusions`. Aucune seconde suite ni
nouvelle référence relancée pour ces échecs connus.

**Mesure isolée**, dix scènes identiques, un appel d'interprétation simulé par
scène, avant/après en ne remplaçant que les quatre fonctions `dossier` de
`45e9f95`. Sonde `tools/mesure_prompt.py` du lot 149 ; aucune mutation d'état,
aucun réseau. Taille JSON de `faits`, caractères ; fréquence = appels avec dossier.

| Bloc | Avant | Après |
|---|---:|---:|
| `faits`, total | 136 247 | 129 655 (−4,8 %) |
| atelier | 6/10 ; 1 706 | 5/10 ; 1 369 |
| franchissements | 6/10 ; 5 061 | 2/10 ; 851 |
| passages d'obstacles | 4/10 ; 2 600 | 2/10 ; 700 |
| espace | 2/10 ; 1 046 | 2/10 ; 1 046 |

**Moteur.** Huit empreintes 2 h, Relais/auberge × graines 1985, 7, 42, 2024 :
chronique, mesures et état complet identiques à `45e9f95`. Huit références absentes
calculées et cachées une fois, puis branche ; un processus réduit.

**Luna.** Une passe des neuf scripts `atelier`, `relais`, `sous-obstacle-*`,
référence `cdaf371` puis branche, une exécution à la fois, copies seulement,
`SEUIL_AUTH` du dépôt principal. Neuf références absentes jouées et cachées une fois.
Sur **29 tours MJ : 84 → 77 appels, 2,90 → 2,66 appels/tour, 9,3 → 8,1 s/tour**.
Dix tours avec refus de chaque côté, refus moteur/contre-revue 18 → 16 ; aucun
repli, erreur technique, arrêt ni erreur de recharge. En interprétation, atelier
19/35 → 12/34 envois, franchissements 19/35 → 0/34, obstacles 16/35 → 10/34 ;
aucun dossier restant classé « aucun proche » par la sonde (inconnus séparés).
**Critère Luna des propositions distantes non atteint** : encore deux actions
brutes sur des cibles éloignées (assembler, saut improvisé) et un détail proposé
sur le mur distant, contre quatre propositions avant. Le moteur les refuse ;
les réponses finales demandent l'approche ou se limitent à la vue. Aucune nouvelle
consigne ni exception ajoutée pour les cacher. Les scènes Luna divergent après
interprétation : la mesure isolée ci-dessus seule attribue la réduction au filtre.

**Limites et livraison.** Le filtre garantit les sources des dossiers ; il ne
garantit pas les propositions spontanées du modèle à partir des repères visuels.
La portée est revalidée par le moteur. Une passe ne prouve pas un gain de latence
ni toute compréhension en langage libre.
La référence Luna demandée précède aussi des changements PNJ ; ces temps ne
mesurent pas un gain causal du seul lot 152. Pas de clé Git de signature :
commit non signé. Branche poussée seule. Bruts dans `artifacts/` :
`mesure152.py`, `projection-152-{avant,apres}.json`, `mesures-152.json`,
`empreintes-152.{json,log}`, `suite-152.{json,log}`, `luna-152.log`,
`bancs-multi/20261027-013631-12064/` et `luna-mesures-152.json`.
