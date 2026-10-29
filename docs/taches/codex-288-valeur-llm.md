# Tâche Codex 288 : regard de game designer, ce que le LLM apporte vraiment au jeu

**Lot de conception seulement : aucun code du jeu, aucun appel à Luna, aucun banc.** Il complète la conception de la
refonte du MJ (`docs/conception-refonte-mj.md`, lot 287) et en révise le plan.

## La demande de l'utilisateur (29 octobre)
« La plupart des actions pourraient être effectuées avec des boutons ou des menus (ex. le menu au clic de souris) :
ouvrir une porte, examiner quelque chose… C'est souvent plus ergonomique que d'écrire. Le LLM peut servir à composer
des actions, mais pour le basique, des actions directes sont plus pratiques. Là où le LLM peut être pertinent, c'est
pour les dialogues complexes, ou pour les contrats éventuellement (générer un contrat ?). Il faut prendre un regard de
game designer : étudier ce qu'un LLM apporte comme réelle valeur de gameplay, qu'un moteur déterministe ne peut pas déjà
faire. »

## Décisions déjà prises sur le lot 287 (section 10)
- **1. Ambiance.** Elle reste secondaire, mais doit être décrite correctement, sans erreur flagrante qui casse
  l'immersion (une torche éteinte qui brûle, une porte ouverte dite fermée, un PNJ absent décrit). Elle ne bloque pas
  la boucle. Propose le contrôle qui l'assure : gardes déterministes renforcées, données publiques plus complètes données
  au narrateur, et le cas échéant une vérification **en fond**, qui ne retarde que l'ambiance, sans relance bloquante.
- **2.** Les répliques à contenu typé sont formulées par le moteur (option A).
- **3.** Un appel bloquant nominal, avec les corrections bornées qui récupèrent une intention.
- **4.** Fidélité de la saisie, décidée : le joueur est le contrôleur. Une ligne « Compris : … » précède les actes
  lourds ou irréversibles (fiche tenter/annuler) et suit les autres ; rien pour une action venue d'un clic. Contre-revue
  et fidélité de parole restent en filet pour les seuls actes à effets pendant la transition.
- **5.** Une revue ciblée seulement à l'admission d'une propriété inventée que le moteur ne peut pas calculer.
- **6.** Une ambiance arrivée pour un lieu quitté est jetée. **Ajout de l'utilisateur** : un retour visuel indique
  qu'une ambiance est en cours de calcul (terminal et page web).
- **7.** Portage lot par lot de `prompt-simplifie`, la négociation de mission comme critère.

## À lire
- `docs/conception-refonte-mj.md` (sections 2 à 5 et 9), `docs/plan-vue.md` (la page web, la scène perçue, le menu au
  clic qui « propose les gestes possibles »), `donjon/web/page.html` (menu `#menu`, « Agir par clic »),
  `donjon/scene.py`, `donjon/commandes.py`, l'analyse locale des saisies (`paroles.analyser`, commandes sans modèle),
  `jeu.py` (terminal), `docs/mecaniques.md`.
- Le catalogue des actions et opérations du moteur (`moteur.py`, `operations.py`, `actions` du schéma d'interprétation)
  et des contenus de parole (`paroles.TYPES`, `SENS_CONTENU`).
- Les bancs Luna : scripts `tests/data/bancs/*.json` et fils archivés (`C:\Users\msics\donjon\artifacts\bancs-multi\`,
  `artifacts\refonte-287\classement.json`), **en lecture seule**, pour classer les saisies réelles.

## Ce que le document doit établir
1. **Inventaire des interactions du joueur.** Groupe les actions, opérations, perceptions et contenus de parole en
   familles. Pour chacune, quelle interface est la meilleure :
   - **directe** : clic, menu contextuel, bouton, touche ;
   - **composée** : une saisie libre que le LLM traduit en plusieurs gestes ;
   - **dialogue**.

   Dis ce que le menu au clic couvre déjà, ce qui lui manque, et le coût de chaque ajout. Applique ce classement aux
   saisies réelles des bancs : quelle part aurait été servie par une action directe.
2. **La valeur propre du LLM.** Ce qu'il apporte qu'un moteur déterministe ne fait pas déjà ou ne pourrait pas faire à
   coût raisonnable : comprendre une intention libre ou composée, les dialogues ouverts, la négociation, la génération
   de contrats ou de missions, l'invention de détails manquants, l'improvisation d'un PNJ, l'ambiance. Pour chacune :
   - l'exemple de jeu ;
   - ce que fait le moteur aujourd'hui ;
   - ce que le LLM ajoute ;
   - le risque pour le contrat du MJ ;
   - si l'apport justifie un appel bloquant, un appel en fond ou aucun appel.
3. **Contrats et missions générés.** Étudie la proposition de l'utilisateur. Un PNJ, ou le MJ, propose un contrat
   (tâche, prix, condition, échéance) adapté à la situation et typé dans le moteur existant (`agendas`, `echanges`,
   missions, propositions, mandats A5). Dis ce qui est réalisable sur les contrats existants, ce qui manque, et où
   s'arrête la liberté du LLM.
4. **Dialogues complexes.** Ce que le joueur doit pouvoir faire en parlant qu'aucun menu ne permet : persuader,
   mentir, questionner, marchander, raconter, menacer. Dis ce que le moteur sait déjà juger (actes typés) et ce qui
   reste ouvert. Articule-le avec la décision 2 (formulation par le moteur) et la question de la conversation ouverte
   laissée par le lot 287.
5. **Révision du plan de la refonte.** Reprends le plan G0 à G21 avec ce regard. Ce qui monte, ce qui descend, ce qui
   disparaît (un appel inutile quand l'action vient d'un clic), et les lots d'interface à ajouter :
   - menu contextuel étendu ;
   - actions directes au terminal ;
   - indicateur d'ambiance en cours (décision 6) ;
   - récapitulatif du plan (décision 4).

   Mêmes règles qu'au lot 287 : un invariant et 30 à 45 minutes par lot, mesures sur les quatre axes du gameplay
   (interprétation, vitesse perçue, invention à la volée, richesse des interactions PNJ).
6. **Questions à l'utilisateur**, numérotées, avec ta recommandation de game designer pour chacune.

## Contraintes
- Lecture et rédaction seulement : aucun fichier sous `donjon/`, `tests/` ou `tools/` modifié. Les scripts de comptage
  vont dans `C:\Users\msics\donjon\artifacts\valeur-llm-288\`.
- **Poste : le laptop.** La vérification d'intégration 284 y tourne : un seul processus Python léger à la fois.
- Garde le contrat actuel tant que l'utilisateur n'a pas décidé (section 7 du lot 287).

## Livraison
- Branche `codex-valeur-llm` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ; si la
  poussée échoue, laisse le commit local, donne son hash et l'erreur exacte.
- Document `docs/conception-valeur-llm.md`.
- Rapport d'une page `docs/taches/rapport-codex-288-valeur-llm.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
