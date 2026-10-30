# Tâche Codex 345 : G16, les paroles d'information formulées par le moteur

Lot G16 de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md), après G15 (lot 320, registre des
émissions), G5 (lot 323, perception) et G17 (lot 326, comptes parlés), tous fusionnés. Lis `AGENTS.md` (contrat du MJ :
une réplique dont le moteur fixe le contenu est formulée par le moteur), `docs/conception-refonte-mj.md` (section 8,
option A, et ligne G16), puis les rapports 320 et 326, qui ont fait le même travail pour les comptes.

## L'invariant
**Les mots d'une réplique qui porte une information typée (identité : nom donné, nom revendiqué, refus de se nommer ;
localisation crue d'un tiers ; ressource déclarée ou refusée ; réponse à « qui est là ? ») sont formulés par le moteur
depuis l'émission G15 et l'issue, et fixés avant publication.** Luna ne reformule pas ces répliques. Leur contenu est la
croyance ou la déclaration du locuteur, pas la vérité du monde : un PNJ qui croit Brune au refuge le dit, même si elle
n'y est plus, et un menteur peut se nommer d'un faux nom sans que ce nom devienne vrai. L'audit de ces seules répliques
typées se retire dans ce lot, puisque ce lot fournit la garantie qui le remplace. Les autres voies gardent leurs
contrôles (conversation ouverte, avis, rappels non exacts).

Les formateurs choisissent leurs variantes de façon déterministe, depuis les seules données autorisées (manière de
parler du personnage comprise), sans geste, sourire ni émotion inventés.

## Contraintes de conception
- Fichiers probables : `paroles.py`, `dialogues.py`, formateurs, `narration.py`. Ne touche pas `jeu.py`/`tui.py`, ni
  aux règles de croyance (`esprits.py`), ni aux mécaniques sociales.
- Aucune exception par personnage, scénario ou formulation du joueur.

## Vérification
- Cas réels : la voix qui se nomme dans `soir-noir` (et l'imposture « c'est moi, Brune »), la question de ressource de
  `ressources`, la question de lieu de `noms-dialogue`. Autres cas de même nature : une localisation crue fausse, un
  refus de ressource, un refus de se nommer. Mots, émissions, croyances apprises et rendu identiques après recharge,
  MJ simulé sans réseau.
- Tests ciblés des fichiers touchés (dont les tests G15, G17, noms et voix) ; pas de suite complète ni de banc PNJ.
- Luna : **une passe** de `soir-noir`, `ressources` et `noms-dialogue`, références lues du cache : zéro appel
  `repondre_dialogue` et zéro audit pour ces répliques typées ; aucune réplique perdue. Si la revue automatique bloque
  Luna, laisse la commande exacte dans `C:\Users\msics\donjon\artifacts\g16-345\luna-a-jouer.txt`.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Recouvrement probable avec le lot 341 (mandat du
joueur, `paroles.py`) et le lot 343 (G7, `narration.py`) : signale tout fichier commun.

## Livraison
- Branche `codex-g16-information`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-345-g16-information-parlee.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g16-345\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
