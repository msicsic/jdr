# Lot 234 — une place périmée rend la main

Branche `codex-place-perimee`, non fusionnée, base `adb52c4`, code `1b8ea32`.
**Correction non validée : trois régressions confirmées par comparaison à la base.**

`signes.place` efface l'ancienne place avant chaque tentative et ne la renouvelle
qu'après un pas social produit par le trajet commun. Cible inconnue/démentie,
absence de case améliorante ou trajet impossible rendent la main. Dans
`pnj.agir`, sans pas social, le rapprochement ordinaire reprend au même instant.
Aucun autre module moteur ni MJ modifié.

Trois nouveaux tests, huit sous-cas : Ilse au Relais et Hugues à l'auberge,
cible inconnue/démentie malgré un autre compagnon connu, trajet impossible.
Les quatre variantes de localisation échouent avant correction et passent ensuite.
Ils rejoignent la compagnie dans une salle éclairée ; monde complet et rendu
identiques après recharge, deux minutes d'un bloc ou en deux laps. Une place
de proximité ou d'écart ne survit pas au trajet social impossible.

**L'assertion historique sur Aubin reste intacte et rouge.** Ilse termine en
`[6,1]`, Aubin en `[1,5]`, Gorm en `[4,5]`. Le recours libéré rejoint Brune,
crue en `[7,1]`, avant qu'Aubin soit localisé. Ilse reste près de Brune ; Aubin
n'entre pas dans ses croyances de lieu. « Ilse reste en compagnie. » apparaît
bien, sans satisfaire l'assertion de proximité d'Aubin. Aucun ajout de perception
ni exception d'acteur pour la rendre verte.

Validation ciblée : **33 tests, 32 verts, un échec introduit**, zéro erreur.
**Suite complète unique : 2 524 tests / 292 fichiers, 4 071,069 s, quatre échecs,
zéro erreur, 16 ignorés.** Calcul pur/mémorisé après recharge vert. Les autres
échecs sont une navette d'Aubin (**188 passages**, plafond **12**), une garde non
livrée (`0 != 1`) et une perte de torche au hameau. Reprise des quatre tests
avec les fonctions exactes de la base : **trois passent**, seule la torche
échoue déjà, aux mêmes instants **3188/3615**. Donc **trois régressions
introduites**, un échec préexistant ; aucun oracle modifié.

Banc unique : **20 paires × 4 h**, cinq scénarios × quatre graines, contre
`adb52c4`. Vingt références manquantes calculées et rangées une fois, zéro
réemploi à cette passe. **Zéro plantage/usurpation ; suspects 219 : 2 → 2**,
épisodes de l'auberge intégralement identiques (Mireille 1985, Tilo 42), aucune
hausse par nuit. Aucune nouvelle alerte de répétition, demande en boucle,
va-et-vient, alternance, agitation ou passages en rafale par nuit/PNJ ;
l'observation d'Hugues auberge 2024 est identique. Répétitions textuelles **4 → 0**,
cycles **507 → 505**, préemptions **58 → 46**, à expliquer **87 → 63**,
dérives ouvertes **204 → 175**, perte de service fautive préexistante **1 → 1**.
Ce banc passif ne lève pas la navette de la capture : **absence générale de
boucle nouvelle non garantie**.

Aucun Luna ; deux travailleurs au plus, priorité réduite. Créneau dépassé par
les vérifications. Bruts et scripts : `C:/Users/msics/donjon/artifacts/place-234/`
(`base-echecs.txt`, `suite.json`, `banc.json`, `bilan.txt` notamment).

La branche ne doit pas être fusionnée en l'état. Le choix du rapprochement
ordinaire et celui du placement social doivent encore partager leur jugement
d'admissibilité ; la seule restitution du recours ne garantit pas leur cohérence.
