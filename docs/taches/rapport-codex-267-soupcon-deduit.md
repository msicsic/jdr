# Lot 267 — Soupçon déduit

Branche `codex-soupcon-deduit`, **non fusionnée**, base `7404d2d`.
Bruts : `C:/Users/msics/donjon/artifacts/soupcon-267/`.

**Changement.** `esprits._constater_bien` rapproche deux constats propres
datés au dixième : présence du bien, intégrité visible, contenu vu vide ou non,
disponibilité d'une ressource et flamme. Chaque propriété conserve sa date :
refermer un coffre ne revoit pas son contenu. L'extinction par épuisement et
le geste propre ne sont pas imputés. Les présences vues, ou situées par une
voix reconnue, entrent dans les quarante souvenirs communs ; une présence
répétée dans le même lieu rafraîchit son souvenir. L'inférence ne lit ni
position cachée ni chronique ; propriétaire et rattachement du bien sont
ceux retenus au constat. Zéro ou plusieurs présences : aucune attribution.
Un geste déjà vu ou entendu, sur le bien ou son contenant, garde sa voie
existante (`vu_agir`/`vu_porter`, pas de cause historique `vol_vu` dans ce moteur).

`relations.EPREUVES.soupcon_deduit` diminue seulement la confiance :
**6 à 18 points**, selon la PSY, contre 20 pour une rumeur et 40 pour un vol
constaté ; niveau de preuve **0,4**, source `devine`. Les bandes existantes
peuvent alors produire la méfiance et ses refus, sans colère ni culpabilité
inventée. Plusieurs conséquences concomitantes étayent un seul indice.
`reviser_soupcons` retire cet indice quand le bien revient, quand l'atteinte
est réparée ou qu'une attribution du geste est apprise. Seule la perte de
confiance effectivement appliquée est compensée, sans effacer les autres
épreuves. Motifs, indices actifs, constats et levées sont sauvegardés avant
leur récit ; le libellé du soupçon emploie la désignation connue du PNJ.

**Preuves.** **118 tests ciblés distincts : 117 verts, un échec préexistant**
de dette (`test_relations_graduees`, 40 au lieu de 20, déjà documenté au 254).
Onze fichiers concernés, jamais de suite complète ; consolidation initiale
117 tests en 36,026 s, derniers constats/restitutions 21 tests verts en 7,932 s.
Onze nouveaux tests : Gorm/réserve/vivres et Anselme/coffre/ballot ; zéro/deux
passants, oubli, geste vu/entendu, auteur appris, retour dans le coffre et
remise au propriétaire, PSY/plancher, intégrité, flamme, épuisement,
ressource vidée/reconstituée, ignorance des positions et noms, laps 3 ou
1+1+1. État complet, rendu et scène identiques après recharge ; récit et
relation contrôlés. Captures `relais.json`, `auberge.json`, résultats
`tests.json` et `tests-soupcon-final.json`.

**Banc en attente.** Détaché, priorité réduite, deux travailleurs au plus :
4 h × Relais/mine/auberge/crue/hameau × graines 1985/7/42/2024, référence
`main` résolue en commit `c870c8b`. Les vingt références exactes sont absentes
du cache : le comparateur les calcule et les range une fois, puis joue la
branche. `comparaison.json` conserve les fils ; `fin.json`, écrit en dernier,
donne les soupçons nés et suspects 219 par nuit, plantages et mesures.
**Absence de hausse des suspects 219 et d'usurpation non encore certifiée.**

**Portée.** Un soupçon reste faillible, notamment après oubli ; il n'apprend
aucun nom et ne prouve aucun portage. Aucun raccord à `récupérer` : le lot 192
exige encore sa preuve propre. Aucune interpellation autonome nouvelle, aucun
verrou caché deviné, aucune disparition déduite d'une suppression distante
du registre. L'effraction couverte est une dégradation matériellement
constatée, pas un crochetage invisible. `agendas.py`, `echanges.py`, le choix
de délibération, scénarios et MJ inchangés ; ni Luna ni comparaison de modèles.
