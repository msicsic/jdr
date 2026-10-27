# Lot 184 b — Comparer les moyens d'obtenir des pièces

Branche `codex-naissance-agendas`, **non fusionnée** ; suite de `ae9504a`,
référence moteur `4efb277`. Pas de Luna ; aucun fichier réservé aux lots
180/185 modifié. Deux calculs réduits au plus. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/naissance-184/`.

**Invariant.** Le projet de pièces compare les acquisitions permises, le prêt
et le vol (`planification.devis_enrichissement`), les ventes de biens propres
cessibles et les travaux connus utiles (`argent_projet.obtenir`). Les marches
et paroles passent par `chercher` ; les échanges par `proposer`, et le travail
contre numéraire par `engager` : avance, engagement payé, garde et remboursement
éventuel restent communs. Les moyens viennent des connaissances du porteur ;
les fonds adverses et le verdict réel sont contrôlés à l'échange. Le prêt réemploie la bourse physique et son obligation de
restitution ; aucun crédit monétaire nouveau n'est inventé.

Le coût comprend route, parole, chance d'accord, travail devisé et faute.
Il est ramené à la fraction du manque couverte. La valeur du bien vendu est
comparée au prix reçu par `offre_sensee`, sans la compter une seconde fois
comme effort perdu. Une borne optimiste (parole, chance ≤ 1 et tarif commun
`ceil(peine/SALAIRE)`) retire les devis qui ne peuvent battre le meilleur recours.
Un projet sans plan dort ; mêmes croyances, aucun nouvel essai. Refus, relations,
biens portés et engagements participent au réveil. La routine d'argent ne double
plus la recherche du projet. Un travail payé en cours laisse place à sa parole due.
Publication différée, trois actifs au plus et sauvegarde restent ceux du lot 184.

**Preuves ciblées.** Odon et Rémy vendent avant un vol plus cher ; travail payé
puis accompli, bourse empruntée avec propriétaire/permission conservés, vol moins
cher selon l'honnêteté, refus non relancés par le temps seul, sommeil sans nouvelle
recherche, même laps entier/découpé ; état et rendu rechargés. Comparaison avec/sans
borne sur quatre scènes. **273 ciblés/repris distincts verts, 31 fichiers**
(77 ciblés ; 196 repris, dont six repris une dernière fois). Suite unique :
**2 306 tests, 265 fichiers, 1 594,589 s, 28 échecs et trois erreurs bruts**.
Les cas en défaut sont repris verts, hors deux MiMo historiques `6 != 5`.
Les oracles de mécanismes antérieurs isolent les nouveaux projets ; les tests A6
et le banc les gardent actifs. Le récit d'auto-accusation contrôle les rumeurs
transmises, pas l'absence de toute conversation. Correction moteur révélée :
couper les annotations de projection avant de publier une intention monétaire.
Capture recherche/appel : 31 passages, dont 17 monétaires et 14 des autres recours ;
le plafond de recherche porte désormais sur ces derniers, monde/ouïe découpés conservés.
Aucune seconde suite complète ; borne et coupe finales vérifiées en ciblés et au banc.

**Répétition 42 établie sur capture.** Reconstitution 184 a identique à l'archive,
minute 5 sauvegardée/rechargée ; reprise jusqu'à 240 : monde et rendu strictement
identiques, huit lectures de Mathe (7/17/37/47/77/122/141/213). Même capture,
seul projet d'Odon abandonné, dette conservée : trois lectures (70/80/120).
Le projet contribue causalement à la trajectoire répétitive ; ce n'est pas une
modification de la lecture des signes (fichier identique à la base).

**Banc final, 4 h mine/auberge × quatre graines** : huit références déjà cachées
relues, **8/8 sans plantage/usurpation**, zéro bascule, alertes `repetition` et
`voir_alterne` absentes. Restent deux observations `fige_presse` (Josse mine
42/2024, 135/130 min) et le `noir_long` inchangé d'auberge 1985. Mine : attente
sous regard base/184 a/184 b **59,43/164,03/73,94 min**, propositions **2,5/1/1,25**,
acceptations **0,25/0/0** ; noir **31,25/1,25/90 PNJ·min**. Auberge stable.
**Coût mine fixe 1985, 4 h** : base/184 a/184 b, recherches **749/941/793**,
neuves **264/401/342**, nœuds **7 564/13 202/10 979**. Le premier devis exhaustif
de 184 b coûtait **187 362 nœuds** et 781 neuves. Après borne, monde/chronique/
récit/souvenirs du relevé fixe identiques ; états et chroniques des huit nuits
tirées strictement identiques avant/après borne. CPU final **14,52 s**, indicatif,
pas de comparaison de temps avec le cache. Surcoût résiduel contre la base explicite.

Richesse : fonction `cats` du lot 183 reprise exactement, épisodes
famille × auteur × texte, PNJ inactifs inclus ; comparaisons sur 4 h, jamais
aux moyennes de 12 h. Mine base/184 a/184 b final : S **13,5/12,25/12,75**,
F **4,5/4,75/5**, D **1,286/1,143/1,179**. Auberge : **6,5/2,75/0,625** inchangés.
Les familles progressent, pas toutes les signatures ni la diversité par PNJ.

**Limites.** Aucun gain général de richesse promis par la seule infrastructure.
Les moyens dépendent des occasions connues, des droits et des refus effectifs.
Vente des biens portés cessibles ; pas de démarchage d'un tiers inconnu, de lecture
de ses fonds ni de promesse d'accord. Restent le solde subjectif des créances
locales, l'identité d'une nouvelle dette après une fin, occasion, événement et
soupçon déduit. L'acquisition de pièces ne signifie pas remboursement extérieur.
Aucune clé de signature Git configurée ; livraison sur la branche seule, `main` intacte.
Vérifications au-delà du créneau ; jonctions des traces automatiques retirées en fin de lot.
