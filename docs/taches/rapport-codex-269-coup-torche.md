# Lot 269 — le coup d’Aubin pour prendre une flamme

28 octobre 2026, laptop. Branche `codex-coup-torche`, **non fusionnée**,
base `integration 47fd0a2`. **Diagnostic seul ; aucun code du jeu modifié.
Verdict : choix conforme aux recours et croyances modélisés sur la capture
historique ; aucun moyen pacifique moins coûteux admissible trouvé.**

**Reproduction.** Deux nuits successives de 12 h, `crue_hameau`, graine
1985, départ tiré, joueur passif en `chambre_cloche`, un processus à priorité
réduite. Sur la base actuelle : 1 372 entrées, aucun coup. Sur `c870c8b`,
worktree détaché : 1 233 entrées, coup à **391220 (652 min)** avec le
`baluchon_mael`, prise de la torche à **391235**, Gorm encore inconscient
à 655 (`inconscient` jusqu’à 400220). L’épisode 241 est reproduit ; ses
archives absentes du laptop empêchent une comparaison intégrale des traces.
Premier écart entre les deux rejeux : entrée 79, Brune active son agenda à
600 sur l’actuel, contre son passage à 611 sur l’ancien ; ensuite elle propose
ses crochets à Ilse pour huit pièces (`pauvre`, 656), au lieu de l’allumage
payé (`accepte`, 686). Trajectoires divergentes dès la première minute ;
aucun commit causal de disparition isolé.

**But et prix.** La première adoption violente capturée est à **369211
(615 min)** : chaleur à **100**, seuil 70 ; faim 41,152, repos 38,823,
sécurité 0. C’est un **besoin pressant, palier 4**, pas un agenda : le
désespoir de l’arbitrage dépend aussi des agendas présents. En revanche,
le seuil corporel **95** autorise déjà l’embuscade malgré les témoins.
Douceur 80, honnêteté 65, courage 50, VOL 10 : faute **3,714286**,
douceur **8**, `combat.prix_violence(chaleur)` **16** ; force crue **0,5**,
risque **2,5**. `prix_gardes={}` : aucun supplément d’éloignement.
Gorm est cru conscient, indemne et dans l’antichambre ; sa FOR privée
n’est pas lue. À 615, il est perçu, orienté sud ; Brune/Sève sont témoins
visuels crus, Ilse aussi à portée d’ouïe. À 652, la dernière position crue
est `[2,1]`, actualisée à 651 ; à l’exécution il est de nouveau perçu et
orienté est. Le désespoir permet d’assumer les regards et oreilles présents.

Coûts en minutes de plan, recherches refaites à froid sur les captures,
mêmes gestes et profondeur, sans atteindre le plafond de 4 000 nœuds :

| Recours | À 615 | À 652 |
|---|---:|---:|
| Assommer/prendre la flamme → brasero | **25,414710** | 35,597053 |
| Assommer/prendre la flamme → poêle du guet | 29,046310 | **32,320596** |
| Recherche chaleur excluant tout `assommer` | aucun plan, 185 nœuds épuisés | aucun plan, 66 nœuds épuisés |
| Proposition de rechange (`plan_recours`) | aucune | aucune |

Le choix ordinaire refait retrouve exactement les coûts enregistrés pendant
la nuit : brasero à 615, puis poêle à 652. Retirer seulement `demander` ou
`acheter` ne change pas le résultat. Le plan final prend la torche, rejoint
la chambre de la cloche, prend du bois, recharge/allume le poêle et s’y chauffe.

**Pourquoi les moyens pacifiques manquent.** À 269, Maël ne connaît pas de
bois, Ilse en signale ; Sève répond `rien` à 413. À 532, l’achat d’une part
à Ilse est refusé `necessaire`, la demande et l’offre d’une pièce à Gorm
pour `bois_guet` sont `impossible` ; même demande/offre pour `bois` à 572,
même issue. Ces refus tiennent encore sur les deux captures. Aucun refus
de torche n’est inventé : **elle appartient à Maël, Gorm la porte avec
permission**. Le générateur commun n’admet ni demande de prêt à ce tiers
détenteur, ni achat (pas de propriété admissible ni de prix déclaré), même
avec les cinq pièces d’Aubin. Aucun service de rechange ni aide attendue ;
attendre ne fournit donc aucun plan de chaleur garanti. Demander du feu
exige une source portable utilisable qu’Aubin puisse tendre au porteur :
la recherche pacifique n’en trouve pas de chaîne complète.

**Portée du verdict.** Aucun défaut de classement démontré, aucun correctif
proposé. La preuve porte sur le catalogue de recours et l’horizon existants,
pas sur toute négociation imaginable avec le détenteur du bien d’un tiers.
À 652, la torche est réellement éteinte/épuisée, mais encore crue allumée
depuis 633 : le choix suit cette croyance ; après la prise, Aubin constate
l’extinction. Le diagnostic ne certifie pas une réussite future du chauffage.

**Preuves.** **169 captures** (168 historiques, dont avant/après choix et
coup, relevé 655 et fin ; une fin actuelle) : monde complet, `regarder` et
`scene_percue` identiques après sauvegarde/rechargement. Le joueur éloigné
ne voit pas directement le coup ; le rendu local rechargé est vérifié.
Nuits terminées en 440,5 et 232,6 s, sans comparaison de vitesse. Ni Luna,
suite complète ni banc comparatif ; aucun calcul actif. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/coup-269/` (`comparaison.json`, captures,
`rejeu-choix.json`, `rejeu-652/`, `candidats-foyers.json`, `recharges.json`).
