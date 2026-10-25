# Lot 68 — Observer restitue les impressions actuelles

Branche `codex-impressions-observer`, non fusionnée, issue de `d78cfcc`, brief
`764e040`. Aucun changement de `main`. Travail sur un seul poste, vérifications
en priorité réduite et au plus trois processus, sans Luna.

**Invariant.** Une observation explicite restitue les impressions déjà acquises de
la personne demandée tant que leur signe d'appui reste perçu. Leur caractère
faillible et le délai commun de lecture sont conservés. Le bilan spontané annonce
seulement les conclusions nouvelles.

**Cause établie.** Dans les deux passes des archives `verif-luna-f033364` et
`verif-luna-8443458`, le premier « observer Brune » lit déjà Ilse au bilan de fin
d'action ; les deux « observer Ilse » suivants taisent ses impressions.
La capture versionnée reproduit exactement cette séquence sans modèle : les
lectures `crainte` et `peur` demeurent sauvegardées et visibles dans la description.
Le filtre des nouveautés ajouté à `_bilan_signes` par la calibration `0f16152`
s'appliquait aussi aux demandes explicites. Le lot 53 n'a pas supprimé ces lectures.

**Correction.** `signes._bilan_signes` restitue les impressions actuelles de la cible
quand `observer` est explicite ; la déduplication des textes demeure. Il réemploie
`impressions`, qui exige le signe encore perçu, et `lire`, inchangé, qui mémorise le
jet et applique le même contrat aux joueurs et PNJ. Aucun changement des émissions,
de la calibration, des sauvegardes, des scénarios ou de `deliberation.autour` ;
`planification.py` intact. Le plan des relations (§ 6.5 et 3c) décrit ce contrat.

**Tests.** Trois nouveaux tests de chaîne saisie → moteur → journal → sauvegarde →
recharge → rendu, chacun sur la capture réelle d'Ilse et sur Brune craignant Ilse.
Deux observations successives restituent signes et impressions sans nouvelle
lecture ni nouveau tirage du joueur. Un signe disparu retire seulement son
impression, en gardant la mémoire ; le retour dans le regard restitue la lecture
sans dé supplémentaire. L'état complet et le journal sont identiques après
recharge. Avant correction : cinq assertions échouent ; après correction : les
49 tests ciblés passent. Trois anciens tests de calibration sont alignés sur la
restitution explicite ; les annonces spontanées restent sans répétition.
Bruts : `artifacts/lot68-avant.json`, `artifacts/lot68-cibles.json`.

**Empreintes.** `tools/comparer_bancs.py --empreintes --reference d78cfcc
--scenarios relais crue --graines 1985 7 42 2024 --heures 2 --processus 3` :
chronique, mesures et état final complet identiques pour les huit nuits. Référence
calculée une fois et rangée dans le cache partagé ; branche jouée ensuite.
Bruts : `artifacts/lot68-empreintes.json` et `.log`.

**Suite complète unique.** `tools/tests.py --processus 3` : **1 837 tests, 16 ignorés,
aucun échec ni erreur**, 182 fichiers, **1 484,1 s**, priorité réduite. Les dossiers
temporaires Python étant inaccessibles aux sous-processus dans le bac à sable,
les vérifications ont été exécutées hors de celui-ci, sans augmenter la charge.
Bruts : `artifacts/lot68-suite.json` et `.log`. Aucun appel à Luna.

**Limites.** Une observation peut ne fournir aucune impression si le jet mémorisé
ne conclut pas, ou donner une méprise. Après dix minutes, la règle commune permet
un nouvel essai ; ses durées de validité restent inchangées. Les empreintes portent
sur les huit nuits prescrites, pas sur toutes les parties possibles. Ce lot ne
recalibre pas la PSY et n'améliore pas les garanties sémantiques du MJ.
