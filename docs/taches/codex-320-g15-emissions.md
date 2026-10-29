# Tâche Codex 320 : G15, une émission typée unique pour toute parole entendue

Lot G15 de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md). Lis `AGENTS.md` (contrat du MJ :
« Une parole établit qu'elle a été prononcée et entendue, sans établir que son contenu est vrai »),
`docs/conception-refonte-mj.md` (sections sur les sources contradictoires, la parole et le rapport commun, ligne G15)
et `docs/conception-valeur-llm.md`. Les lots G16 à G19 (information, comptes, avis, rappels parlés) s'appuieront sur ce
flux : ne les réalise pas ici.

## Le constat
`avis-joueur` p1 t1 (archives 86/87, campagne `c9459ce`, `C:\Users\msics\donjon\artifacts\bancs-multi\20261028-235223-6688\`) :
`issue` et `repondent=[marchand]` disent qu'Aubin et Ilse se taisent, alors que `conversation_validee.faits` contient leurs
deux répliques. L'auditeur refuse le silence, puis la garde refuse de leur donner la parole. On déduit aujourd'hui qui a
parlé de listes de phrases et d'un booléen « répond à Corvus » qui peuvent se contredire.

## L'invariant
**Toute parole réellement prononcée et entendue a une émission typée unique, enregistrée avant affichage : son auteur,
son acte (réponse à Corvus, réaction d'un PNJ à un autre, dispute, avis, refus…), ses paramètres, sa modalité
(croyance, refus, offre, constat), l'événement mécanique qui l'autorise, ses auditeurs et son ordre dans le tour.**
La réponse à Corvus et les échanges entre PNJ sont des émissions distinctes, dans un seul ordre. `issue`, les faits de
la conversation, le dossier de l'audit et le rendu lisent ce même flux ; aucune liste parallèle. Une émission n'établit
pas la vérité de son contenu. Les textes existants des opérations peuvent être conservés ; aucune mécanique sociale
nouvelle. Ne multiplie pas les répondants pour faire disparaître une contradiction.

## Vérification
- Cas réel 86/87 rejoué (MJ simulé, sans réseau) : plus de contradiction entre `issue`, `repondent` et les faits ;
  monde, texte sauvegardé et rendu identiques après recharge.
- Une autre dispute entre PNJ, une écoute à distance (auditeur d'une autre salle) et un inconscient qui n'entend rien.
- Tests ciblés des fichiers touchés ; empreintes 2 h, Relais et crue, 4 graines, contre la référence de l'intégration
  (cache) si les nuits ne doivent pas changer ; sinon banc rapide 4 h et explication des écarts.
- Luna : **une passe** de `avis-joueur` et `echanges` seulement, référence lue du cache. Si la revue automatique
  bloque Luna, laisse la commande exacte dans `C:\Users\msics\donjon\artifacts\g15-320\luna-a-jouer.txt`.
- Pas de suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Le lot U-P (319, laptop) touche `moteur.py`,
`rendu.py`, `jeu.py` : signale tout recouvrement.

## Livraison
- Branche `codex-g15-emissions`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-320-g15-emissions.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g15-320\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
