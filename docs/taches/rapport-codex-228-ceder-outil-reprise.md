# Lot 228 — Capacités conservées ou réellement compensées

**Branche `codex-ceder-outil-b`, non fusionnée.** Reprise autorisée le
28 octobre 2026 ; intégration fusionnée jusqu'à **`3c0e1ca`**, lots 232 et 236
inclus. Code figé dans `6652ed2`, correctif `e8feb8f`. Deux travailleurs
réduits au plus, aucun Luna, aucune clé de signature configurée.
Bruts : `C:/Users/msics/donjon/artifacts/ceder-228/reprise/`.

**Analyse préalable**, captures hameau 1985/42 sur intégration `26258b4` :

| Graine / offre | Capacité perdue / gain | Décision |
|---|---|---|
| 1985, allumer une torche pour une pièce | Service, aucune cession | À conserver |
| 42, clé de Brune, trois offres à 132–133 min | 12 / 5,174 ; aucun doublon cru | Refus à maintenir |
| 42, torche de Brune, 230 min | 12 / 4,840 ; aucun doublon cru | Refus à maintenir |

Aucune de ces cessions matérielles à une pièce n'était compensée. Les tests
reprennent leurs états réels : refus sans mouvement de bien ni d'argent, puis
vente à un prix suffisant. Aucun échange sous-compensé rétabli pour enrichir le banc.

**Invariant.** Le lot 202 conserve sa protection de capacité. `biens.valeur_capacites`
isole sa valeur marginale des prix marchands ; un moyen équivalent conservé
réduit la perte. `echanges.necessaire` compare cette perte à la valeur réellement
reçue lors d'une cession, y compris pour un outil du plan courant.
`evaluer_proposition` compte le remplacement acquis simultanément ; `demander`
traite un achat explicite positif comme une vente même sans prix déclaré.
L'achat sous-compensé **8,4 contre 0,909** est refusé par la même règle.
`contre_offre` peut annoncer un prix compensant, sans lire les fonds privés de
l'acheteur ; prêts et réserves consommables gardent leurs contrôles distincts.
Le refus visible exprime les conditions, sans prétendre un usage en cours.

Le cache négatif du premier 228 reste durable à dépendances crues égales ; sa
version change pour rejuger les anciens refus sous ce contrat. Tests de recharge,
remplacement et prix honoré sans second jet ; monde, rendu et scène conservés.
**70 ciblés verts**, puis **15 compensation/cache verts**. `echanges.tenu`,
`plan_recours` et `deliberation.choisir` sont ceux de l'intégration ; aucun
contournement de la pureté, traitée par le lot 232.

**Vingt paires de 4 h**, graines 1985/7/42/2024, référence `3c0e1ca` : vingt
références manquantes calculées une fois et rangées au cache. Première passe
sur `e0fff6d` interrompue pour intégrer 236 ; aucun résultat de cette passe utilisé.
Zéro plantage/usurpation. S/F/D moyens (classification 183) :

| Scénario | Référence → branche |
|---|---|
| Relais | 10,75/4/1,563 → 10,25/4/1,5 |
| Mine | 26,75/5/1,893 → 26,5/5/1,893 |
| Auberge | 11,5/4,5/1,094 → identique |
| Crue | 25,75/7,5/3,5 → 27,25/7,25/3,438 |
| Hameau | 35/8/2,625 → 35,75/8/2,625 |

S hameau, par graine : **36/26/34/44 → 36/35/28/44** ; toutes les nuits restent
dans **[26 ; 44]**, étendue de référence. Compteur 219 : suspects **2→2**
(auberge, aucune hausse par nuit), cycles **507→520**, préemptions **58→54**,
entrées à expliquer **87→84**. Sans recours : zéro hors crue ; crue
**13,75→15 PNJ·min par nuit**. Ces chiffres ne garantissent pas l'absence de
toute boucle ; le classement des renoncements est confié au lot 239.

**Coût mine fixe 1985/4 h : 910→887 recherches (−2,5 %), 10 925→9 959 nœuds
(−8,8 %)**. Temps CPU de passes distinctes non comparés.
**Suite complète unique : 2 558 tests / 296 fichiers, 8 échecs, 2 erreurs,
2 460,937 s ; suite non verte, intégration non validée.**

**Attribution ciblée**, sans seconde suite : 82 tests sur intégration
(79,164 s), puis 46 sur copie 202 + cache + raccord 236 (109,757 s).
Trois défauts préexistants : deux MiMo et torche hameau (lot 238).
Trois autres hérités de 202 : empreinte monde auberge (`etapes_chainees`),
chronique de demande de lampe (`verifier_eau`), fonds insuffisants pour le
prix de clé du test `navettes_garde` (aucun changement de `plan_recours`).
Quatre écarts propres à la reprise : `crochetage_surenchere`, deux cas
`ouie_temoins`, `rejeu`. Replays exacts rechargés : Brune propose ses crochets
contre des vivres ou huit pièces avant la faute ; selon le jet, marché refusé
ou accepté, puis Gorm ouvre sa réserve. Les tests attendent encore la faute
ou son attente immédiate. **Attentes de trajectoire à arbitrer**, pas
réancrées silencieusement ; ces six fichiers voisins sont laissés intacts.
Le contrôle de pureté passe depuis l'intégration 232.

**Limites conservées.** Le relevé du cache est conservateur. Ancien écart 202
reproduit lors de la première passe : lanterne 400→47 à 480 min, huile inchangée,
allumages 436/438 séparés par extinction ; poêle rallumé avec du bois réel.
Le rallumage après extinction d'une autre flamme n'est pas garanti par ce lot.
Créneau dépassé par les vérifications ; aucune campagne longue ni appel au MJ.
