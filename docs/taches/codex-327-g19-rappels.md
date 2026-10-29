# Tâche Codex 327 : G19, les rappels

Lot G19 de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md), après G15 (lot 320, fusionné : registre
unique des émissions). Lis `AGENTS.md` (contrat du MJ : une parole établit qu'elle a été prononcée et entendue, sans établir
que son contenu est vrai), `docs/conception-refonte-mj.md` (ligne G19) et les rapports 112, 135 et 156 (rappels du passé,
rappel exact, ordre), puis 320.

## L'invariant
**Un rappel (« que m'a dit Ilse ? », « qu'a répondu Gorm tout à l'heure ? ») restitue les mots historiques réellement
entendus par Corvus, tels qu'enregistrés, sans créer de nouvelle émission, de parole ni de connaissance.** La restitution
lit le registre des émissions et la mémoire des paroles entendues ; un rappel de ce qui n'a pas été entendu est dit comme
tel, sans invention. L'audit des citations historiques exactes se retire dans ce lot, la preuve exacte le remplaçant ; un
rappel libre que le moteur ne sait pas restituer garde sa voie actuelle.

## Vérification
- Rappel inventé du lot 110 (refusé), rappel réel, et un rappel d'un autre locuteur : texte, mémoire et monde identiques
  après recharge ; zéro émission ajoutée au registre par un rappel (test), MJ simulé sans réseau.
- Luna : **une passe** de `soir-noir` et `echanges`, référence lue du cache : zéro audit des citations exactes, zéro parole
  ou connaissance créée. Si la revue automatique bloque Luna, laisse la commande exacte dans
  `C:\Users\msics\donjon\artifacts\g19-327\luna-a-jouer.txt`.
- Tests ciblés des fichiers touchés ; pas de suite complète ni de banc PNJ.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Recouvrements possibles avec le lot 326 (G17) et le lot
323 (G5, non fusionné, `narration.py`) : signale-les.

## Livraison
- Branche `codex-g19-rappels`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-327-g19-rappels.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g19-327\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
