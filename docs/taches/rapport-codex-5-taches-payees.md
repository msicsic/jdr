# Rapport Codex 5 — servir soi-même ce qu'on promet

Branche `codex-taches-payees`, non fusionnée, créée depuis `main` **06602a6**, dans
`tmp-worktrees/codex-taches-payees`. Aucun changement ni fusion de `main`.

## Invariant et correction

La même recherche décide si le PNJ peut accepter un service, ce qu'il fera pour le tenir et ce
qui le rend ensuite impossible. Elle doit atteindre le résultat promis, pas une inspection
préliminaire, ni seulement la prise d'un objet à livrer. Une part pour un foyer comprend la
recharge et, s'il est éteint, l'allumage. Le prestataire peut recevoir les biens du commanditaire,
mais n'emploie aucun service exécuté par lui ou par un tiers.

Les anciens chemins divergeaient : les parts passaient par `_plan_pulsion` (qui pouvait simplement
aller voir un feu cru vif), tandis que les tâches payées passaient par `devis_pulsion`, dont
`seul=payeur` autorisait encore les services du payeur. Le vendeur pouvait donc encaisser sans
pouvoir servir ; le devis de Tilo pouvait faire servir du bois et allumer l'âtre par Odile.

Fonctions et contrats modifiés :

- `planification._parts`, `_suites`, `chercher` : un devis autonome accepte les transferts de biens
  depuis le commanditaire ; il exclut parts servies, allumages par autrui et délégations. Les moyens
  ordinaires hors engagement gardent leurs services possibles.
- `planification.planifier_engagement`, `planifier_tache`, `devis_pulsion`, `_remettre` : acceptation,
  exécution et abandon partagent le devis ; une livraison couvre le chemin jusqu'à l'acheteur.
- `echanges.demander`, `_vendre_part`, `confier`, `engager`, `empeche` : même évaluation pour parts,
  objets et tâches, gratuites ou payées. Les biens à portée sont constatés avant l'accord.
- `echanges.engagements_echus`, `annoncer_abandon` : un service payé devenu impossible est dû sans
  attendre l'échéance ; un service gratuit devient un abandon à annoncer au destinataire, en le
  rejoignant et en lui parlant. Le marqueur sauvegardé garde cette obligation après rechargement.
- `deliberation.promesse_en_cours`, `_candidats`, `planification._entrees` : créance et annonce
  reçue arrêtent l'attente ; le destinataire retient le refus « impossible » selon sa cause ; les
  mémoires de recherche tiennent compte de ces nouvelles informations.
- `esprits.verifier`, `biens.gardes`, `paroles.engagements_enregistres`, `stratege.dossier` : contrat
  de sauvegarde des champs facultatifs `objet` et `annule`, fin de la garde dès l'abandon et données
  narratives qui distinguent l'abandon à annoncer du service encore promis.

Aucun nom de scénario, d'objet, de PNJ, ni formulation du joueur n'est employé dans la correction.
Aucune consigne n'est ajoutée au MJ ; aucun changement de modèle.

## Cas vérifiés

`tests/test_taches_payees.py` : dix parcours avec sauvegarde/rechargement, état du monde et contrôle
du texte produit lorsqu'un joueur est présent.

1. **Relais, graine 42, minute 151** : sauvegarde exacte de la base, juste avant l'achat des planches
   par Gorm (`tests/data/taches_relais42_avant_part.json.gz`). Aubin envisage d'emprunter la torche ;
   refusée, la part devient due avant la minute 156. Gorm n'attend plus soixante minutes : il reprend
   l'entretien lui-même. Corvus, dans la chambre de la cloche, ne reçoit pas un faux récit de service.
2. Même scène, refus de la torche déjà connu : achat refusé, aucun encaissement, refus « impossible »
   retenu et échange rendu selon ce que le joueur perçoit.
3. **Tilo et l'âtre**, avec `bois_reserve` : sans flamme, refus et bourses intactes ; le devis ne peut
   plus demander à Odile de servir la part et d'allumer l'âtre. La suppression artificielle de cette
   réserve a été retirée de `test_crochetage_surenchere`.
4. Autre chaîne d'allumage : lanterne dans la main de Tilo, aucun feu disponible, briquet du payeur
   connu mais refusé en prêt. Faire allumer la lanterne par le payeur ne sauve pas le devis.
5. L'outil du payeur peut au contraire être emprunté : Odile prête un briquet, puis **Tilo** recharge
   et allume l'âtre, sans dette. Les tests existants vérifient aussi son propre briquet.
6. Part gratuite d'Aubin, sans aucun moyen de flamme : refus lu par Corvus, bois intact.
7. Même nature à l'auberge : Joss refuse une part pour le feu sans flamme, texte et réserve vérifiés.
8. Part payée devenue impossible : remboursement visible au joueur, sans attente jusqu'à l'échéance.
9. Promesse gratuite devenue impossible : annonce visible au joueur, engagement retiré.
10. Abandon gratuit sauvegardé avant l'annonce : le bénéficiaire n'en sait encore rien ; les données
    du MJ annoncent un abandon à dire. Après la parole, le bénéficiaire cesse d'attendre ; Corvus
    éloigné ne voit pas un échange qu'il n'a pas perçu.

Trois scènes positives existantes ont reçu un briquet : Aubin dans `test_parts_achetees` et
`test_echanges_suite`, Gorm dans `test_corps`. Elles vérifient toujours un service réalisable,
plutôt qu'une promesse impossible fondée sur une simple inspection du feu. `test_entretenir`
contrôle que Joss garde sa dernière part et la refuse comme nécessaire, qu'elle soit demandée ou
achetée : les informations nouvelles peuvent changer ce choix sans changer la protection du bien.
Dans `test_stratege`, le marteau à rapporter est connu à sa case réelle : avec une place vague,
Aubin le croyait absent en entrant et annonce désormais l'abandon, au lieu de garder une parole
sans plan. La scène positive vérifie ainsi une tâche dont les moyens sont connus.
Dans `test_ressources`, la crue 7 diverge : Aubin se chauffe au poêle, Brune y monte avant son
rallumage sans s'y être encore chauffée à la minute 240. Le test vérifie cette montée, le poêle
rallumé par Gorm et les deux charges restantes, plutôt qu'un réchauffement que la nuit ne produit
plus. Les ressources du scénario ne sont pas changées.

## Mesures et validation

Les bancs sont exécutés sans modèle, à priorité réduite, avec au plus quatre processus ; la base
précède la branche. Départ tiré, graines **1985, 7, 42, 2024**, 4 h, Relais, auberge et crue.
`tools/comparer_bancs.py` et `tools/tests.py` ne sont pas présents dans la base : utilisation de
`tools/audit_nuits.py jouer` / `analyser` et de `unittest` avec `banc_pnj.ceder()`.

Les relevés et journaux sont dans `artifacts/` (non versionnés). Les fichiers de référence sont
dans `C:/Users/msics/donjon/artifacts/codex-5/main-4h` et `main-8h` ; ceux de la branche sont dans
son propre dossier `artifacts/`.

### Banc rapide, moyennes par nuit de 4 h

| Mesure, base → branche | Relais | Auberge | Crue |
|---|---:|---:|---:|
| Achats | 0,75 → 0,75 | 1,5 → 1,5 | 1,25 → 1,25 |
| Dont achats explicites de parts | 0,75 → 0,75 | 1,5 → 1,5 | 1,25 → 1,25 |
| Parts refusées comme impossibles | 0 → 0 | 0 → 0 | 0 → 0,25 |
| Parts de nourriture servies, toutes | 0,75 → 0,75 | 3 → 3 | 1,5 → 1,5 |
| Recharges de feu, toutes | 1,25 → 1,5 | 10 → 10 | 2 → 2,25 |
| Parts non servies, prix devenu dû | 0,25 → 0,5 | 0 → 0 | 0 → 0 |
| Dettes créées / remboursements | 0,25 / 0,25 → 0,5 / 0,5 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 |
| Tâches proposées / acceptées / faites | 0,25 / 0 / 0 → 0,5 / 0 / 0 | 0 / 0 / 0 → 0 / 0 / 0 | 1,75 / 0 / 0 → 1,5 / 0 / 0 |
| Tâches dues aussitôt | 0 → 0 | 0 → 0 | 0 → 0 |
| Minutes sans recours | 45 → 45 | 20 → 20 | 0 → 0 |
| Minutes en attente | 8,75 → 0 | 1,25 → 1,25 | 16,25 → 16,25 |
| Usurpations / violations | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 |

Douze nuits de chaque côté, aucun plantage. L'auberge n'atteint aucun marché de tâche en 4 h :
les scènes contrôlées de Tilo et Joss vérifient cette voie. Au Relais, la part non servie n'est
plus attendue pendant une heure ; une deuxième nuit (graine 7) la règle également tôt. C'est une
hausse des abandons explicités et remboursés, pas une garantie de livraison malgré des croyances
fausses. Les parts de nourriture et recharges comptent tous les services, gratuits et payés ; les
dettes de parts comptent explicitement les ventes non servies. Ces compteurs ne constituent pas
une ventilation de chaque recharge entre les différents achats.

L'analyse du banc a aussi contrôlé le risque de réachat après remboursement. `retenir_abandon`
retient la cause du service abandonné : « impossible » si les moyens manquent, « refus » à la
simple échéance. Une restitution d'argent n'efface pas ce refus. Aucun constat de répétition ne
reste dans le banc final (la première exécution de travail en avait révélé une, corrigée par ce
contrat commun).

Temps muraux par nuit : Relais 9,3 → 7,0 s, auberge 20,2 → 16,1 s, crue 13,4 → 10,2 s. La base
utilisait quatre processus, la branche deux, sur une machine partagée ; ces relevés ne démontrent
pas un gain de calcul.

### Cas réel au banc, Relais 42, 8 h

| Mesure | Base → branche |
|---|---:|
| Achats | 2 → 2 |
| Parts de nourriture servies | 2 → 2 |
| Recharges de feu | 0 → 3 |
| Parts non servies, prix devenu dû | 1 → 1 |
| Dettes / remboursements | 5 / 5 → 1 / 1 |
| Tâches proposées / acceptées / faites | 19 / 4 / 0 → 2 / 1 / 1 |
| Tâches dues aussitôt | 3 → 0 |
| Pièces payées pour les tâches | 23 → 2 |
| Minutes sans recours | 130 → 120 |
| Minutes en attente | 80 → 0 |
| Usurpations / violations | 0 / 0 → 0 / 0 |

La vente est encore possible sur les croyances de la minute 151 : le vendeur compte emprunter
la torche. Le refus est découvert en agissant. **Minute 153**, Aubin doit la pièce, Gorm reprend
l'entretien ; **154**, la pièce est rendue et Gorm allume le brasero. Sur la base, la dette ne
naissait qu'à **211**. Plus tard, **350**, Aubin accepte une tâche à 2 pièces et recharge lui-même
le brasero ; **351**, le travail est tenu. Ni dette ni engagement en attente en fin de nuit.

### Contrôles du moteur

`planification.VERIFIER=True` et `spatial.VERIFICATION=0.2`, 8 h, graine 42, départ tiré, sur
Relais, mine, auberge et crue : **quatre nuits terminées, aucun plantage, aucun écart de recherche,
aucune borne atteinte, aucune usurpation ni violation**. Le banc du Relais de ce contrôle fournit
aussi le cas réel de 8 h ci-dessus. Aucune dette ni aucun engagement ne reste à la fin de ces
quatre nuits. Les constats de l'audit qui demeurent concernent les besoins pressants sans but,
l'eau et les réactions aux bruits, pas des services payés puis abandonnés en boucle.

### Suite complète

**1292 tests recensés : 0 échec, 0 erreur, 14 sautés** (`jsonschema` facultatif absent).
La découverte complète de `unittest` a été répartie par identifiants de tests dans deux processus
à priorité réduite, en conservant ses doublons éventuels. Les groupes déjà réussis ont été
conservés entre les reprises ; tous les groupes de scènes ajustées ont été revérifiés. Les dix
tests du correctif passent aussi après le dernier ajustement du texte d'abandon.

Les tests d'interface et de HTTP local ont été terminés **hors sandbox Windows** : dans le
sandbox, la création de la socket locale de la boucle `asyncio` se bloquait dans
`socket._fallback_socketpair`, avant le code du jeu (trace capturée par `faulthandler`). Aucun
test n'a été sauté pour ce blocage. Les 28 tests TUI passent, ainsi que les tests web.

Bilan et détail : `artifacts/suite-bilan.json`, `artifacts/suite-resultats-finaux.json` et
`artifacts/suite-*.log`. `git diff --check` est sans écart ; aucun nom indéfini nouveau n'est
relevé par `pyflakes` dans les modules modifiés.

## Limites

- Le devis porte sur ce que le PNJ croit. Un emprunt qu'il espère peut encore être refusé, un objet
  peut manquer ou un passage être bloqué lorsqu'il arrive. Ces découvertes déclenchent la même
  réévaluation ; il ne s'agit pas d'une garantie omnisciente de réussite future.
- Les croyances restent datées à la minute, comme dans le lot C ; la règle « vu ou constaté depuis
  l'offre » conserve cette précision. La tenue d'un objectif se juge toujours sur l'état observé ;
  ce lot garantit l'autonomie du devis, sans ajouter une preuve de l'auteur de chaque résultat.
- La recherche reste bornée. Un devis absent peut aussi refléter cette borne ; les contrôles du
  planificateur distinguent cet épuisement d'un écart de recherche.
- Le vendeur incapable d'entretenir le foyer refuse. Il ne négocie pas spontanément un changement
  de prestation. L'achat explicite d'une part sans foyer garde la livraison de bois déjà existante.
- L'annonce d'un abandon gratuit demande de retrouver et de pouvoir entendre le destinataire ;
  elle reste sauvegardée avant cela. Les urgences et les passages peuvent en retarder l'annonce.
  Les dettes payées suivent le mécanisme existant : la créance est connue des deux dès sa création,
  le remboursement se fait lorsqu'ils peuvent se parler.
- Le prix d'une tâche ne compte toujours pas la valeur des consommables du prestataire. Les règles
  de remboursement, de propriété et de mémoire à durée bornée restent celles du moteur existant.
- Sur la base actuelle, l'offre de **16 pièces à Aubin à la minute 334** ne se reproduit plus : les
  offres du même moment vont jusqu'à **8 pièces**, refusées (« cher »). La vente de la minute 151
  se reproduit exactement ; la même nuit montre encore des tâches acceptées puis dues aussitôt
  avec Ilse. Le banc de 8 h compare cette base effective, sans fabriquer le chiffre ancien.
