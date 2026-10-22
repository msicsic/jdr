# Rapport Codex 3 — de l'huile pour une lampe

Branche `codex-lampes`, non fusionnée. Référence : `main` f1eee53, inchangée pendant tous les bancs
de référence. Aucun push, aucune fusion, aucune campagne avec Luna et aucune sauvegarde utilisateur touchée.

## Invariant et correction

Ce qu'une source brûle doit être accessible par les mêmes gestes de ressource que les autres
moyens du plan. Recevoir une part ne signifie pas que la source est chargée ou allumée : il faut
une livraison réelle, puis les gestes `alimenter` et `allumer`.

La recherche trouve la réserve par `perception.recharge`, sur le contenu déclaré ; aucune branche
ne reconnaît de l'huile, un personnage ou un scénario. `_parts_remises` projette la réception d'une
charge consommable, puis la recherche ordinaire compose les gestes suivants. Le plan exécutable
s'arrête à la demande ou avant la livraison : l'identité simulée du lot n'est jamais employée
comme si sa part avait déjà été reçue. `_couper` conserve ces frontières dans les plans mémorisés.
Porter du combustible incompatible ne masque plus une réserve compatible.

La règle sociale vaut pour un lot posé et un lot porté, pour le joueur et pour les PNJ. Le donneur
garde le lot, détache une charge et la livre, gratuitement ou contre le prix convenu, selon
l'accueil, la réserve, les refus et le partage habituels. Une part pour entretenir une source
identifiée reste possible ; une source explicitement incompatible est refusée sans substitution.
La provenance de la part est enregistrée dans l'engagement (`lot`), sans déduction d'un préfixe.
Un engagement gratuit n'est plus raconté comme un objet payé.

L'audit de tous les consommateurs de `besoin_de_part` sépare la catégorie comptée de son emploi :

| Lecture | Contrat retenu |
|---|---|
| Reconnaître une ressource, la donner plutôt que la prêter, la détacher, calculer le prix perdu | Catégorie comptée ; aucune chaleur n'est présumée. |
| Enquête envisagée et réponse, moyens d'un refus, ressource déjà portée, garde urgente | `part_pour` sur les sources connues et `recharge`. |
| Part qui réchauffe | Foyer compatible allumé, dans la salle du plan. |
| Recharge d'une source précise | Compatibilité de cette source ; l'état des autres foyers ne l'écarte pas. |

La demande d'une part n'exige plus que le demandeur possède un besoin de chaleur : c'est son but,
composé par les gestes, qui détermine son emploi. Une réserve d'un autre combustible connue chez
un propriétaire n'empêche plus de l'interroger sur ce qui chauffe ; cette lecture manquante a été
repérée par la suite, corrigée avant le gel final, puis toutes les campagnes ont été rejouées.

## Fonctions et données

- `planification._parts_remises`, `_parts`, `Vue.promesse`, `Vue.foyer_froid`, `_couper`, `_entrees` :
  réception, compatibilité, coûts de livraison, frontières de replanification et mémoire.
- `s_enquerir`, `Vue.sur_soi`, `rechauffe` : un combustible connu ne se confond pas avec une
  ressource pour la chaleur ; seule une part servie près d'un foyer compatible allumé réchauffe.
- `echanges.demande_de_part`, `demander`, `_remettre_part`, `foyer_de`, `garde`, `enqueter`, `executer`,
  `_avec_joueur` : parts portées ou posées, engagement de livraison, contrepartie et refus.
- `deliberation.part_pour`, `promesse_en_cours`, `moyens_crus`, `esprits.verifier` : emploi d'un
  combustible pour un besoin, réception effective, moyens des refus et provenance sauvegardée.
- `paroles._demander`, `_part_vendue` : faits rendus au joueur cohérents avec le service réellement
  engagé et avec sa contrepartie. Aucun nouveau type de parole ni ajout au prompt de Luna.
- `matiere.prelever_piece` : copie indépendante du contenu déclaré, qui décrit une substance et
  aucune quantité ; charges, pièces et masse sont conservées lors du prélèvement physique.
- `scenario_auberge.json` : huile déclarée pour la lampe du comptoir, les lanternes de l'étable,
  du couloir et d'Hugues ; pot d'Odile au cellier, 3 charges × 120 min ; burette de Joss à l'étable,
  2 × 90 min. Positions et disponibilité initiales sues de la maisonnée. La réserve gardée reste
  applicable. Mine inchangée : bidon de 3 × 120 min déjà présent.

## Vérifications

Suite complète : **1252 tests, OK (14 sautés)**, 1292.511 s observées, priorité BelowNormal, temporaires dans
le worktree. Les nouveaux tests suivent l'état et le rendu après sauvegarde et rechargement :

- vraie nuit auberge 1985 de 8 h : lanterne de l'étable vide ; parole typée de Corvus, achat d'une
  part à Odile, livraison, prise de la lanterne, recharge puis allumage ; possession, charges,
  lumière et perception rendue vérifiées après rechargement ;
- PNJ : même lanterne vide à l'auberge et lampe de Rémy à la mine, demande d'une part, accord sans
  recharge anticipée, livraison puis recharge et allumage ; bidon posé employé sans échange ;
- lots portés : demande et achat par les PNJ des deux scénarios, demande et achat par le joueur ;
  le donneur conserve deux charges du lot, une seule est reçue et consommée ;
- même chaîne avec une source et une réserve déclarant de la cire, refus de méfiance, réserve
  gardée, achat au prix, cible incompatible refusée, provenance sans convention de nom et plans
  relus du cache sans perte de leur frontière.
- lot physique de trois pièces à contenu de cire : substance conservée sans alias mutable,
  conservation des trois charges, trois pièces et 1,8 kg à la séparation, sauvegarde, livraison,
  consommation d'une seule charge, lumière et rendu après rechargement. Les tests matière et
  ce cas ont aussi été vérifiés ensemble (17 tests) avant la suite complète.

Tests existants adaptés et assertions métier conservées : `test_echanges_suite` vérifie qu'une
enquête sur le bois reste possible en connaissant un autre combustible de Joss ; `test_entretenir`
vérifie que la dernière charge est refusée, même si le plan choisit un achat plutôt qu'une demande ;
`test_ressources` vérifie la propriété conservée du lot, la seule charge reçue et consommée, les
trois foyers à cinq heures et la diminution de la réserve totale (parts comprises). Le partage
peut maintenir le poêle plus longtemps : son extinction à une heure fixée n'était pas l'invariant.

Défaut de vérification préexistant, distinct du moteur : le test de console de `test_proto` ne
simulait pas `raconter_resultat` après « tenter » et pouvait contacter le réseau avec sa clé
factice. Le premier lancement concerné a été interrompu et son mock manquant complété ; aucune
règle de jeu n'a été changée pour ce test et aucun appel de modèle réussi n'a été utilisé.
Les restrictions sandbox sur les tubes multiprocessing et les répertoires `tempfile` ont requis
des lancements élevés ; tous les calculs restent en priorité réduite dans le worktree.

`planification.VERIFIER` : 8 h, graine 7, chaque scénario ; aucune exception, aucun écart ni borne
reconnue. `Monde.verifier` contrôle les nuits à chaque pas. **Aucune usurpation et aucune violation
d'état observées** dans les campagnes ci-dessous. Les gestes illicites de PNJ relevés par l'audit
sont des actes du jeu, pas des violations de ces invariants.

## Campagnes 8 heures, main → branche

Auberge et mine : graines 1985, 7, 42, 2024 ; Relais : les mêmes plus 3, 11, 99, 500 ; crue :
1985, 7, 42, 2024. Joueur passif respectivement au dortoir, à la galerie, à la chambre de la
cloche pour Relais et crue ; départ tiré. Tous les bancs main précèdent ceux de la branche :
quatre workers pour main, trois pour les campagnes de branche puis deux pour VERIFIER pendant la
suite (qui peut lancer deux calculs enfants), toujours BelowNormal. Les
secondes sont des durées observées avec la charge
partagée du poste, pas une mesure de vitesse isolée du moteur.

| Mesure moyenne par nuit | Auberge | Mine | Relais | Crue |
|---|---|---|---|---|
| Noir (min·PNJ) | 237,5 → 137,5 | 291,25 → 291,25 | 26,875 → 26,875 | 33,75 → 48,75 |
| Recharges de lampes | 0 → 0,25 | 0 → 0 | 0 → 0 | 0 → 0 |
| Parts demandées | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Parts données | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Parts achetées | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Achetées livrées | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Parts refusées | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Sans recours (min·PNJ) | 155 → 135 | 55 → 55 | 60,625 → 60,625 | 17,5 → 51,25 |
| En attente (min·PNJ) | 17,5 → 16,25 | 278,75 → 278,75 | 52,5 → 52,5 | 107,5 → 55 |
| Nuit (s) | 48,55 → 61,425 | 57,925 → 51,825 | 17,45 → 14,387 | 25,725 → 21,05 |

Les recharges comptent les gestes réellement appliqués aux sources sans foyer. « Demandées »
compte les tentatives gratuites, « achetées » les achats acceptés, « données » les parts gratuites
effectivement remises et « achetées livrées » leurs contreparties réellement livrées ; « refusées »
regroupe les refus de demande et d'achat, hors simple identification d'une voix. Une promesse
n'est pas une livraison. La référence ne comporte aucune demande ni remise d'huile (vérifié dans
sa chronique complète). Pour la branche, l'observateur externe relève transactions, provenance et
recharges à leur application, sans écrire dans le monde.

La seule recharge de lampe des 20 nuits est à l'auberge 2024 : à la minute 407, Lucien prend la
burette de Joss et alimente la lanterne de l'étable. Ce n'est pas une livraison gratuite ou payée.
Les parcours de partage sont établis par les tests ; ces nuits passives ne les déclenchent pas.
La crue régresse pour le noir et les minutes sans recours ; ses minutes en attente diminuent.
Les mesures ne prouvent donc aucune amélioration uniforme des comportements.

## Audit 12 heures, main → branche

`audit_nuits.py jouer` puis `analyser` : auberge et mine, chacune 8 graines
(1985, 7, 42, 2024, 3, 11, 99, 500), mêmes salles du joueur.

| Mesure moyenne par nuit | Auberge | Mine |
|---|---|---|
| Noir (min·PNJ) | 1023,125 → 858,75 | 1576,875 → 1576,875 |
| Recharges de lampes | 0 → 1,25 | 0 → 0 |
| Parts demandées | 0 → 1 | 0 → 0 |
| Parts données | 0 → 0,125 | 0 → 0 |
| Parts achetées | 0 → 0,625 | 0 → 0 |
| Achetées livrées | 0 → 0,625 | 0 → 0 |
| Parts refusées | 0 → 0,875 | 0 → 0 |
| Sans recours (min·PNJ) | 187,5 → 154,375 | 47,5 → 47,5 |
| En attente (min·PNJ) | 430 → 446,875 | 1420,625 → 1420,625 |
| Nuit (s) | 120,587 → 249,15 | 117,625 → 183,075 |

Sur les huit nuits de l'auberge : 8 demandes gratuites, 7 refus, une part gratuite et 5 parts
achetées réellement livrées, puis 10 recharges de lampes au total. Anselme achète à Joss à la
minute 528 de la graine 1985, puis à Odile à 618 (livraison et recharge à 619) ; graine 42, Odile
promet gratuitement une part à 700, la livre à 701 et la lanterne est alors rechargée. La mine
ne déclenche pas ces échanges sur les graines mesurées.

| Signalements de l'analyseur (toutes nuits) | Main → branche |
|---|---|
| appels_nombreux | 3 → 0 |
| buts_alternes | 0 → 1 |
| fige_presse | 64 → 60 |
| illicite_entendu | 50 → 45 |
| illicite_sans_temoin_avec_present | 10 → 8 |
| noir_long | 75 → 71 |
| repetition | 1 → 0 |
| voir_alterne | 11 → 10 |

Les fichiers détaillés et chroniques sont conservés dans `artifacts/codex-lampes/` :
`main-8h`, `branche-finale-8h`, `main-12h`, `branche-finale-12h`, `verifier-final-8h`,
`main-audit.json`, `branche-finale-audit.json`, `gel-final.json`, `gel-livre.json`,
`mesures.json` et `tests-complets.log`. `artifacts/lampes_audit.py` conserve l'observateur utilisé ;
`artifacts/mesurer_lampes.py` refait les tableaux à partir des sorties réelles.

La dernière correction de `matiere.prelever_piece` est postérieure au gel des campagnes. Les
empreintes identifient ce seul fichier modifié ; aucun objet des quatre scénarios ne combine
description physique et contenu déclaré (`preuve-gel-matiere.json`). Les nuits passives ne font
aucun ajout du MJ : le nouveau champ hérité n'y est donc jamais présent et leurs trajectoires
restent valides. La suite exhaustive finale porte sur le code livré, cette correction comprise.

## Limites

- Une source vide est un moyen d'un but : sa recharge spontanée n'est pas systématique. Le test
  réel fait agir le joueur après la nuit, sans modifier les autres sources ni les réserves du
  scénario pour obtenir le constat de la lanterne vide.
- La recherche reste bornée et dépend des croyances, des priorités et du prix d'endurer ; une
  ressource présente ne garantit pas son emploi par chaque PNJ. L'huile et les autres ressources
  restent rares ; la disparition de tout noir ou de toute attente n'est pas un objectif garanti.
- Les alertes restantes de l'analyseur sont consignées ci-dessus ; aucune n'est présentée comme
  corrigée par le seul partage de combustible.
- Les données d'huile ajoutées concernent les nouvelles parties. Les sauvegardes utilisateur
  n'ont pas été modifiées ; un ancien engagement sans provenance garde sa livraison, mais cette
  information absente n'est pas reconstruite en devinant le nom de son objet.
