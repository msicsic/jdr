# Tâche Codex 293 (refonte U-D) : un geste choisi au clic garde son identité jusqu'au validateur du moteur

Premier lot d'interface de la refonte du MJ, après G2 et G4 (lots 291 et 292, fusionnés). Lis `AGENTS.md`
(« Contrat du MJ » : une action choisie par clic ou menu n'est pas réinterprétée), `docs/plan-refonte-mj.md`
(ligne U-D), `docs/conception-valeur-llm.md` (sections 2 et 7, ligne U-D) et `docs/plan-vue.md` (la page, la scène
perçue, le menu au clic).

## Le constat
Le menu au clic de la page (`donjon/web/page.html`, `gestes`, `gestesPorte`, `choixCase`) fabrique une commande
textuelle `"<verbe> <id>"` et l'envoie par `/commande` (`donjon/web/pont.py`, `soumettre`), comme une saisie. Le jeu la
réanalyse ensuite (`commandes.analyser`), et une analyse qui ne la reconnaît pas peut partir au MJ. Le choix du joueur
est pourtant déjà explicite : un geste et une cible désignée sur la carte. Rien ne garantit aujourd'hui que ce choix
arrive tel quel au validateur, sans interprétation, ni qu'il ne coûte aucun appel au modèle.

## L'invariant
**Une entrée structurée (geste, cible et paramètres publics) garde son identité jusqu'au validateur commun du
moteur : le même plan qu'une commande équivalente, sans analyse de texte, sans compilation ni contre-revue de
fidélité, sans appel au modèle.** La cible est désignée par la référence publique que la scène perçue donne au
navigateur. Le navigateur ne reçoit aucune précondition ni donnée cachée. Le moteur tranche à la réception : il refuse
avec son message public (G2) ou exécute et rend le résultat (G4). Un descripteur périmé (cible disparue, hors de vue,
geste devenu impossible) reçoit le refus public du moteur, jamais une autre cible de même nom.

Le menu annonce un verbe, pas une faisabilité. Le lot ne promet pas qu'un clic réussit ; il garantit que ce que le
joueur a choisi est ce que le moteur juge.

Ce que le lot ne fait pas : aucun geste nouveau au menu (les familles viennent avec les lots U-M), pas de terminal
(U-T), pas de récapitulatif (U-P). « Lui parler » reste une parole libre (dialogue, hors descripteur) : dis comment il
se comporte après le lot, sans le changer s'il n'entre pas dans le contrat. Garde la commande textuelle pour la saisie
libre.

## Fichiers attendus
`donjon/commandes.py` (construire le plan d'un descripteur par le même chemin que la commande locale),
`donjon/web/pont.py` (recevoir le descripteur), `donjon/web/page.html` (l'envoyer), `donjon/moteur.py` seulement si le
validateur commun manque d'une entrée. Le descripteur est une forme commune, que le terminal réutilisera (U-T) : ne le
lie pas au web. Ne touche pas aux mécaniques des PNJ ni aux voies du MJ.

## Vérification
- Tests ciblés, sans modèle, pour chacun des gestes que le menu propose aujourd'hui (objets, portes) :
  - deux cibles de même nom dans la vue : le geste porte sur celle qui a été choisie ;
  - un descripteur périmé : refus public du moteur, aucune autre cible ;
  - la parité avec la commande textuelle équivalente : même plan, même effet du monde, même texte rendu ;
  - zéro appel au MJ ;
  - après recharge : monde, scène et carte identiques.
- Vérifie que ce que la page reçoit ne contient aucune précondition ni entité non perçue.
- Les tests du clic existants (`tests/test_web.py`, `tests/test_clic*` ou équivalents, qui demandent Node) restent
  verts ; adapte seulement ceux qui attendaient la commande textuelle, en le disant.
- Mesure : pour chaque geste du menu, nombre d'appels au modèle avant et après (attendu zéro) et renvois au MJ dus à un
  préalable réellement manquant.
- **Pas de passe Luna** si aucun chemin du modèle n'est touché ; dis-le. Pas de suite complète (le superviseur la
  lance).

## Contraintes
**Poste : le laptop.** Une vérification d'intégration (lot 284) y tourne : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-ud-descripteur` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ; si
  la poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-293-ud-descripteur.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\ud-293\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
