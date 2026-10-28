# Tâche Codex 228 : reprise du lot 202, céder un outil compte la capacité perdue, sans surcoût

Le lot 202 (`origin/codex-ceder-outil`, `74a4bc4`, **en attente** depuis le 2026-10-27) fait compter à un PNJ la capacité qu'il perd
en cédant un bien (`biens.capacites_crues`, `valeur_bien`, ventes, marchés, contreparties ; prêt distinct). Il était mis en attente
pour son coût (mine 4 h : nœuds +58 %, recherches +41 %) et à reprendre **après le contrat d'engagement (196 c) et la mesure de
saillance**, tous deux faits (lots 213, fusionné, et 210). Le diagnostic 208 (`docs/taches/rapport-codex-208-cout-ceder-outil.md`)
a trouvé la cause : **89 % des nœuds en plus viennent de recours négatifs redemandés** (Odon, Rémy : devis de fermeture) après que
les PNJ ne proposent plus leurs outils ; rien ne retient un recours sans offre acceptable. Correction proposée par 208, un
invariant : **mêmes dépendances crues, même résultat de recours réutilisé, même négatif**. Les lots 110, 220 et 225 ont depuis
établi la même règle pour les refus, les emprunts rendus et les renoncements.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (195, 226) : au plus 2 processus, priorité
réduite. **Pars de la branche `origin/codex-ceder-outil`** (crée `codex-ceder-outil-b` dessus) et fusionne `origin/integration`
(`b6d610b`) avant tout. Fichiers : `biens.py`, `echanges.py` (**pas** `tenu`, modifié par le lot 195), `pnj_propositions.py`
(`recours`), et leurs tests ; **pas** `deliberation.py`, `planification.py` (lot 226), `esprits.py`, `social.py`, `pnj.py`, ni le MJ.
**Bruts dans `C:\Users\msics\donjon\artifacts\ceder-228\`** ; bruts du 202 et du 208 dans `outil-202\` (laptop) et `cout-208\` (ce
poste). Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 202 (sur sa branche), 208, 110, 220, 225 et 213, puis `pnj_propositions.recours`, `offre_sensee`.

## L'invariant (en plus de celui du 202)
**Un recours (proposition faute de mieux) sans offre acceptable est retenu avec les dépendances crues qui l'ont rendu négatif
(capacités et doublons, besoins, droits, liens, engagements, accès) et n'est pas recalculé tant qu'aucune ne change ; une seule
qui change le rend de nouveau possible.** Jamais par le temps seul. Même règle pour tout PNJ ; aucune règle propre à Odon, Rémy,
un bien ou un scénario.

## Vérification
- Reproduire d'abord sur la base fusionnée le surcoût mesuré par 208 (`tools/mesure_cout.py`, mine fixe 1985, 4 h) : avec et sans
  le seul invariant ci-dessus. Le coût doit revenir près de celui de l'intégration (`b6d610b`).
- Tests du 202 et de 208 après rechargement : Gaspard et Lucien ne cèdent plus leur seul outil sans compensation ; Odon et Rémy ne
  redemandent plus leurs devis à entrées inchangées, et recommencent quand une entrée change ; même laps d'un bloc ou découpé ;
  monde et rendu rechargés identiques. Les deux écarts de parcours du 202 (lanterne à 480, poêle du guet) : expliqués.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines contre `b6d610b`, avec les classes du compteur 219 :
  répétitions suspectes (ne doivent pas monter), sans recours, S/F/D du lot 183 (la richesse ne doit pas baisser nettement), coût.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-ceder-outil-b` poussée (pas `main`) ; si la poussée est
bloquée, laisse le commit local et dis-le. `docs/etat-dev.md` (remplace l'entrée « lot 202 mis en attente » par « Branche
`codex-ceder-outil-b`, non fusionnée ») ; rapport d'une page `docs/taches/rapport-codex-228-ceder-outil-reprise.md`.
