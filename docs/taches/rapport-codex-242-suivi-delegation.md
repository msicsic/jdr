# Lot 242 — suivi d'une délégation

Branche `codex-suivi-delegation`, **non fusionnée**, base `c870c8b`.

**Contrat.** Le mandant juge sa charge confiée sur une échéance connue et
ses croyances. `agendas.aide_echue` et `suivis_delegations` proposent un
contrôle du résultat ou du mandataire par `voir`, sous les priorités
ordinaires. Une visite postérieure à l'échéance suffit : aucune ronde
périodique inventée. `_amener` contrôle également le retard au lieu prévu,
sans annuler l'accord ni émettre une deuxième délégation identique.
`clore_aides_constatees`, au début du choix, clôt une aide sur une preuve
postérieure à l'accord ; une réalisation apprise en route arrête le contrôle.
Un résultat perdu ensuite ne ressuscite pas l'ancien mandat. Une pulsion
initialement confiée redevient autonome à l'échéance et son mandat se clôt
quand le résultat est cru réalisé.

**Raccords autorisés.** `echanges.confier` conserve l'échéance calculée par
`planification.duree_devis` : durée physique du plan retenu, routes et tarifs
communs, distincte du coût pondéré. La relance du même mandant et de même
condition réutilise l'obligation active, recalcule le devis et actualise sa
date par `agendas.renouveler`, sans nouveau jet. Ordre, contreparties et
autres conditions sont conservés ; paroles closes/annulées/rompues exclues.
`Vue.aides` revalide l'attente ; recherche, bornes et ouverture de
`Vue.detresses` du lot 240 inchangées. Validateurs : échéance facultative,
refus mal formé avec `attendu`, anciennes sauvegardes sans migration.

**Cas et limites.** Sur la base, Gorm reste « charge confiée » à 240 min
au Relais (1985/7/2024 ; nuit 1985 : 140 PNJ·min confiées). Sa délégation
initiale n'a ni accord daté ni échéance : **aucun scénario ne reçoit un délai
inventé, cette attente historique reste sans suivi temporel**. Scène
d'auteur avec accord explicite, autre charge à la mine (Bram/Josse).
Plan hypothétique, réponse incertaine, geste aléatoire/durable ou durée
inconnue : pas d'échéance estimée. Le schéma conserve une aide attendue par
objet ; les obligations distinctes du mandataire restent séparées. Aucune
garantie générale des boucles. Aucun Luna, vente, `tenu`, biens, ouïe,
`pnj` ou classement des besoins modifié.

**Preuves.** **54 tests concernés verts / six fichiers**, dont 17 nouveaux,
AST A1, monde/rendu rechargés, résultat à temps, constat en route, laps
bloc/découpé, relance réelle (d'abord rouge : 2 obligations au lieu de 1),
autres conditions et paroles closes/annulées. Le test historique d'abri
héritait d'une hausse crue **+8 cm/h**, justifiant un second trajet vers le
haut : deux niveaux réels datés établissent maintenant sa prémisse de baisse.
Toutes ses assertions de trajet et d'abri sont conservées ; fichier entier vert.

**Banc final : vingt paires de nuits 4 h**, zéro plantage/usurpation, aucune
hausse des suspects par nuit, chroniques/récits/souvenirs identiques 20/20.
Moyennes des quatre graines avant → après **inchangées** :

| Scénario | Suspects (total) | S / F / D | Attente | Confiées (PNJ·min) |
|---|---:|---:|---:|---:|
| Relais | 0 | 13 / 4 / 1,5625 | 1,25 | 162,5 |
| Mine | 0 | 25 / 5 / 1,9286 | 0 | 0 |
| Auberge | 1 | 8,75 / 3,75 / 0,9375 | 0 | 0 |
| Crue | 1 | 25,75 / 7,25 / 3,25 | 110 | 35 |
| Hameau | 0 | 25 / 7,5 / 2,2083 | 5 | 23,75 |

**Suite complète laissée au superviseur**, consigne `4422f13` du 2026-10-28 :
arrêt à **18 fichiers / 323 tests, aucun échec**. Première passe interrompue
à 45 fichiers / 784 tests pour reprise du contrat et de la scène ; aucune
suite complète revendiquée. Vingt références calculées une fois puis toutes
relues ; aucun temps de référence comparé. Créneau dépassé, aucun calcul actif.
Bruts : `C:/Users/msics/donjon/artifacts/delegation-242/`.
