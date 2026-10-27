# Lot 167 — A4b partiel : s'interposer

Branche `codex-garder-proteger`, **non fusionnée**, base `45d07fb`, code
`d230e4a` puis `0bdfee4`. Livraison partielle autorisée par le brief ; aucun
Luna, fichier MJ réservé ou `main` modifié. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/garder-167/`.

**Invariant.** L'approche est un événement perçu, sans renouvellement par délai.
`esprits.croire` transmet les mouvements vus à `defense.approche_vue` : charges
des pulsions de biens licites ou protégés du profil, soupçon ou guet lu.
Après les besoins pressants, `pnj.agir` rejoint le poste par la marche commune,
revalide et avertit : souvenir/chronique avant affichage, aucune charge privée
dans le contenu typé. `passage` maintient le poste ; demande de franchissement
ou rapprochement vu supplémentaire donnent l'épreuve `garde_ignoree` de
`relations` (confiance/rancune, modulations communes). Défense 4c et
`prix_gardes` inchangés ; aucune violence ajoutée.

**Huit tests verts** : Anselme/ballot sorti du coffre et autre gardien,
approchants joueur/PNJ, poste/parole/persistance et axes rechargés ; ami laissant
le passage, guet lu, protégé, absence de vue/charge emportée ; même `data` et
rendu après laps entier/découpé ; 31 minutes immobiles sans répétition.
Épreuve en données de tests ; déclarations historiques inchangées.

**Mesures finales.** Suite complète unique : **2 240 tests, 257 fichiers,
1 309,96 s, zéro erreur/ignoré**, 25 échecs bruts : 21 sous-tests de l'oracle A0
attendant la liste historique, deux permissions globales perturbées par le
prêt autonome d'une autre lampe, deux MiMo historiques `6 != 5`. Oracle filtré
pour le seul nouveau candidat, prêt contrôlé sur sa lampe : **24 repris verts**,
dont les huit d'interposition ; aucune seconde suite.
`VERIFIER` + spatial 0,2 : auberge 1985 fixe, 2 h, monde complet et rendu
identiques après recharge. Coût auberge 1985 fixe, 4 h : **201 recherches,
190 neuves, 4 220 nœuds** de chaque côté ; CPU indicatif **8,17 → 10,19 s**,
charges différentes et référence cachée : aucun surcoût isolé démontré.
Empreintes 2 h : **8/8 Relais/auberge identiques**, **8/8 mine/crue différentes** :
souvenirs d'approche, postes et paroles ; crue 2024 : état seul différent.
Seize références relues. Première passe : répétition par délai révélée puis
corrigée par événement ; seule branche rejouée.
Banc final **4 h × quatre graines × auberge/mine/crue**, sans plantage,
usurpation, violation, poussée ni boucle nouvelle détectée. Auberge : chronique
et mesures identiques sur 4/4, état seul différent sur 7/42 (souvenirs).
Passages horaires moyens **13,75 → 13,75 / 8 → 8,25 / 21,5 → 20** ; vols vus
**0 → 0 / 0,5 → 0,25 / 1,5 → 1,5**. Eau crue **21,25 → 17,5 PNJ·min**.
Observations : un noir long inchangé ; deux `fige_presse` de chaque côté,
mais Josse passe de 2024 (130 min) à 1985 (125 min), devoir déjà satisfait :
**à surveiller** ; aucune amélioration générale des attentes revendiquée.
Huit références rapides manquantes calculées une fois, quatre relues.

**Limites.** Les sortes d'agenda `garder` et `protéger`, transitions différées,
suivi à portée de voix et réponse à l'appel sur ce socle restent à faire ;
aucun agenda nouveau livré. Hystérésis générale hors lot. Poste contournable,
contact déjà établi/poste inaccessible/approche non vue : interception non
garantie ; mémoire bornée, absence générale de boucle non garantie.
Pas de clé Git : commits non signés, branche seule poussée. Deux travailleurs
réduits au plus pour ce lot ; vérification au-delà du créneau. Deux journaux
automatiques initialement créés dans le worktree déplacés dans
`journaux-tests-auto/` ; aucun brut local restant.
