# Tâche Codex 226 : un contact nécessaire devient un sous-but de recherche ou d'appel

Manque **P1** du diagnostic 215 (`docs/taches/rapport-codex-215-richesse-crue.md`), recommandation 2 de la revue 217 (« contact
comme sous-but commun »). Depuis le lot 211, un PNJ ne sait plus où est quelqu'un qu'il n'a pas localisé (juste). Mais quand un
but **exige un contact** avec une personne qu'il ne sait pas localiser, il attend au lieu de la chercher : `_plan_abri.sures`
(s'abriter auprès d'un proche fiable) et `planification.s_enquerir` (enquête de ressource auprès de quelqu'un) exigent une personne
localisée, alors que `rejoindre` sait déjà inspecter et appeler. Captures du lot 215 : `crue-7-attente-ilse-10`,
`crue_hameau-42-attente-brune-160`, `crue_hameau-7-attente-aubin-200` (`C:\Users\msics\donjon\artifacts\richesse-215\` sur ce
poste). Le lot 221 (fusionné) a ajouté la question au tiers « Où est X ? » dans `_chercher`. Priorité de l'utilisateur : richesse.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (195, 225) : au plus 2 processus, priorité
réduite. Fichiers : `deliberation.py` **seulement `_plan_abri` et l'appel du contact** (le lot 225 modifie `renoncer` et le contrôle
des renoncements, le lot 218 `choisir` via `agendas.py` : n'y touche pas), `planification.py` **seulement `s_enquerir` et le
raccord à la recherche/appel**, et leurs tests ; **pas** `esprits.py`, `social.py`, `pnj.py`, `ouie.py`, `echanges.py`, `agendas.py`,
ni le MJ. **Bruts dans `C:\Users\msics\donjon\artifacts\contact-226\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

Lis `AGENTS.md`, les rapports 215, 217, 211, 221, 37 et 69 (chercher, indices), 213 (contrat d'engagement : un sous-but garde son
parent), puis `_plan_abri`, `s_enquerir`, `rejoindre`, `_chercher`.

## L'invariant
**Quand un but exige un contact avec une personne dont le PNJ ne connaît pas le lieu, ce contact devient un sous-but de recherche :
chercher là où il l'a vue en dernier, appeler, demander à un tiers présent (lot 221), avec les coûts, dangers, refus et indices
communs ; une position inconnue ne signifie ni impossible, ni localisée.** Le sous-but garde son parent (contrat 213) et cesse quand
le contact est établi, démenti ou que le but parent n'a plus lieu. Même règle pour tout PNJ et tout but à contact ; aucune règle
propre à Ilse, Aubin, Brune ou au scénario ; aucun accès à la position réelle.

## Vérification
- Reproduire d'abord les trois attentes du lot 215 sur la base actuelle (`346c1aa`).
- Tests après rechargement : Ilse cherche ou appelle le proche fiable au lieu d'attendre ; un autre cas (enquête de ressource,
  autre scénario) ; route dangereuse ou refus : l'attente reste juste ; même laps d'un bloc ou découpé ; monde et rendu rechargés.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec les classes du compteur 219** :
  attente urgente (doit baisser en crue et hameau), répétitions suspectes (ne doivent pas monter), appels, S/F/D du lot 183 ;
  aucune usurpation, plantage ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-contact-sous-but` poussée (pas `main`) ; si la poussée est
bloquée, laisse le commit local et dis-le. `docs/etat-dev.md` (« Branche `codex-contact-sous-but`, non fusionnée ») ; rapport d'une
page `docs/taches/rapport-codex-226-contact-sous-but.md`.
