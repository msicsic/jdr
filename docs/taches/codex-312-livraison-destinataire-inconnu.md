# Tâche Codex 312 : un destinataire de lieu inconnu ne rend pas une livraison impossible

Premier des deux petits lots proposés par le diagnostic 308. Lis `AGENTS.md` et
`docs/taches/rapport-codex-308-services-apres-303.md` (Relais 7, « Deux petits lots proposés »), ainsi que le rapport
303 (`rapport-codex-303-service-rejoindre.md`). Captures et bruts dans `C:\Users\msics\donjon\artifacts\services-308\`.

## Le constat
Relais 7 : Gorm doit livrer à Aubin, mais ne sait plus où il est. Sur la capture, `planifier_tache` renvoie `None`,
alors que `_remettre` et `rejoindre` proposent de demander à Brune où se trouve Aubin. La livraison est annulée à
l'instant 856, au lieu de préparer le contact. Le même défaut existe sur la base, avant le lot 303.

## L'invariant
**Une tâche de remise ou de livraison dont le destinataire a un lieu inconnu reste faisable : son devis et son plan
passent d'abord par les moyens communs de le rejoindre (inspection, appel, question à un tiers), comme le service du lot
303. Inconnu ne veut pas dire absent.** La faisabilité, l'empêchement et l'annulation lisent le même contrat. Une
livraison n'est annulée que sur un empêchement réellement cru (destinataire parti ou mort, bien perdu, aucun moyen
admissible). Il n'y a aucune lecture de la position réelle, aucun délai ni réessai par le seul temps.

Fonctions en cause : `_devis_remise`, `planification.planifier_tache`, `echanges.empeche` et la voie d'annulation.
Aligne-les sur le contrat du 303, sans le dupliquer.

## Vérification
- La capture Relais 7 rechargée : Gorm cherche ou fait demander Aubin, puis livre. Vérifie que la charge garde son
  parent, que monde, rendu et scène sont identiques après recharge, et que le résultat est le même avec un laps
  d'un bloc ou découpé.
- Un autre cas de même nature, dans un autre scénario.
- La contre-épreuve d'un destinataire cru parti, qui annule toujours.
- **Banc rapide** : 4 h × quatre graines, Relais, auberge et mine, contre la référence de l'intégration (cache). Compte
  les livraisons tenues et annulées, les portions servies et les suspects 219 par nuit, et vérifie l'absence de boucle
  nouvelle. Calcul détaché avec un fichier de fin.
- Pas de Luna, ni de suite complète.

## Contraintes
**Poste : le laptop**, où tournent une vérification d'intégration et un lot du MJ (G1, qui touche `biens.py`,
`dialogues.py` et `mj.py`). Évite ces fichiers ; si l'un d'eux est indispensable, dis-le avant de le modifier.

## Livraison
- Branche `codex-livraison-inconnu`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-312-livraison-destinataire-inconnu.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\livraison-312\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
