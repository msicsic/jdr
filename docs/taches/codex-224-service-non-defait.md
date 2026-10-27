# Tâche Codex 224 : on ne défait pas ce qu'on a été payé pour faire

Décision de l'utilisateur du 2026-10-27 au soir (`docs/etat-dev.md`, « Décisions prises le 2026-10-27 au soir », point 2), après la
revue 217 et le compteur 219. Cas réel : **hameau 1985, Maël paie Brune pour que la torche soit allumée ; elle l'allume (7 min),
le moteur tient le service pour rendu, puis elle l'éteint une minute après** (`deliberation.menager_flamme` : une flamme que son
propre plan n'emploie plus se consume pour rien). Le compteur 219 relève 7 « états payés perdus après réussite » sur 20 nuits de
4 h. Le contrat actuel ne porte aucune durée : `echanges.tenu` constate l'état une fois, puis l'engagement se clôt. Bruts de la
revue 217 et du lot 219 : `C:\Users\msics\donjon\artifacts\revue-217\` et `transitions-219\` (sur le laptop ; copie par
`scp msics@...` inutile : rejoue la nuit, commande dans `revue-217\protocole.json`, base `8177959`, ou sur la base actuelle).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (213, 223) : au plus 2 processus,
priorité réduite. Fichiers : `echanges.py` (clôture d'un service rendu ; le lot 221 modifie `enqueter`), `planification.py`
(**seulement** le filtre des gestes qui défont un état ; les lots 221 et 223 touchent `s_enquerir` et `reagir`),
`deliberation.py` **seulement `menager_flamme`** (le lot 213 modifie `choisir` et voisines), `biens.py` si la trace du service y vit,
et leurs tests ; **pas** `agendas.py` (lot 213), `social.py`, `esprits.py`, `pnj.py`, ni le MJ. **Bruts dans
`C:\Users\msics\donjon\artifacts\service-224\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 217 et 219, 115 (tâche promise), 120 (service rendu), le contrat « un geste défait sous ses yeux »
(`deliberation.changer_etat`, `Vue.contrarie`, `docs/plan-planificateur.md`, « Les boucles de la revérification »), puis
`echanges.tenu`, la clôture des engagements et `menager_flamme`.

## L'invariant
**Celui qui a été payé (ou s'est engagé) pour obtenir un état ne le défait pas lui-même, par aucun de ses gestes ni par son
économie de flamme, tant qu'il croit que le bénéficiaire en a encore besoin (d'après ses propres croyances sur ce besoin) ; il n'a
pas d'obligation d'entretenir cet état : s'il cesse de lui-même (combustible épuisé, autre personne), ce n'est pas sa faute.** Même
règle pour tout PNJ, pour une tâche que le joueur paie à un PNJ, et pour tout état (allumé, fermé, verrouillé, posé) ; aucune règle
propre à Brune, à la torche ou à un scénario ; aucun contrat « maintenir » à durée (décision de l'utilisateur).

## Vérification
- Reproduire d'abord le cas réel (hameau 1985, 7–8 min) sur la base actuelle ; dire si la torche est encore éteinte par Brune.
- Tests après rechargement : Brune n'éteint plus la torche tant qu'elle croit que Maël en a besoin, puis peut l'éteindre quand ce
  besoin cesse ; un autre cas de même nature (autre état : porte fermée ou verrouillée payée, autre scénario) ; l'état qui cesse seul
  ne rompt aucun contrat ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur 219** : la classe
  « état payé perdu après réussite » doit baisser, aucune autre classe monter ; coût mine 4 h ; aucune usurpation, plantage ni
  boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-service-non-defait` poussée (pas `main`) ; si la poussée
est bloquée, laisse le commit local et dis-le. `docs/etat-dev.md` (« Branche `codex-service-non-defait`, non fusionnée ») ;
rapport d'une page `docs/taches/rapport-codex-224-service-non-defait.md`.
