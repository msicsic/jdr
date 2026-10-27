# Tâche Codex 221 : demander à un tiers où est quelqu'un

Manque **P2** du diagnostic 215 (`docs/taches/rapport-codex-215-richesse-crue.md`), confirmé par la revue 217 (contact comme
sous-but commun). Depuis le lot 211, un PNJ ne sait plus où est un personnage qu'il n'a pas localisé (juste : il le devinait par
sa position réelle). Mais il n'a aucun moyen de **demander à quelqu'un qu'il voit** « Où est X ? » : `echanges.enqueter` ne porte
que sur des ressources et exclut les personnages ; `rejoindre` et `_chercher` parcourent les lieux au hasard des visites. Une
réponse donne une croyance de lieu **sourcée** (ouï-dire), jamais la vérité cachée. Priorité de l'utilisateur : richesse des
comportements des PNJ.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille) :
au plus 2 processus, priorité réduite. Fichiers : `echanges.py` (**seulement** `enqueter` et la réponse ; le lot 220 modifie la
restitution et les demandes de biens), `planification.py` (**seulement** `s_enquerir` et l'appel de ce recours ; le lot 220 touche
l'enrichissement), `paroles.py` si la question du joueur a besoin d'un contenu typé, et leurs tests ; **pas** `deliberation.py`,
`agendas.py` (lot 213), `social.py`, `esprits.py`, `pnj.py` (lot 206, en attente), ni le MJ. **Bruts dans
`C:\Users\msics\donjon\artifacts\ou-est-221\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 215, 211, 217, 37 et 69 (chercher, indices), 50 (`ressource.sujet`), puis `echanges.enqueter`,
`planification.s_enquerir`, `rejoindre`, `_chercher` et la croyance de lieu (`esprits`, lecture seule).

## L'invariant
**Un PNJ qui a besoin de quelqu'un dont il ne connaît pas le lieu peut le demander à une personne présente à qui il peut parler,
par la question commune ; celle-ci répond d'après ses seules croyances (où elle l'a vu ou entendu en dernier, et quand), ou dit
qu'elle ne sait pas, ou refuse selon la relation ; la réponse devient pour le demandeur une croyance de lieu de ouï-dire, datée et
sourcée, qu'il peut aller vérifier.** La question est comparée aux autres moyens (chercher, appeler) par la recherche commune. Même
règle pour le joueur (il peut poser la question et recevoir la réponse d'après les croyances du PNJ) ; aucune règle propre à un
personnage ou un scénario ; aucun accès à la position réelle.

## Vérification
- Captures du lot 215 (`crue_hameau-7-attente-aubin-200.json` dans `C:\Users\msics\donjon\artifacts\richesse-215\`, copiable
  depuis le PC fixe par `scp msics@msi-desktop:C:/Users/msics/donjon/artifacts/richesse-215/...`) : Aubin demande où est la personne
  qu'il cherche et y va ; un autre cas de même nature (autre scénario) ; réponse fausse ou ancienne suivie puis démentie ; refus ;
  joueur qui demande ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur 199** : questions,
  retrouvailles, attente urgente, S/F/D du lot 183 ; aucune usurpation, plantage ni boucle nouvelle (questions répétées comprises).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-ou-est-il` poussée (pas `main`) ; `docs/etat-dev.md`
(« Branche `codex-ou-est-il`, non fusionnée ») ; rapport d'une page `docs/taches/rapport-codex-221-ou-est-il.md`.
