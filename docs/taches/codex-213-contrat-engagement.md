# Tâche Codex 213 (lot 196 c) : le contrat d'engagement dans `choisir`

Troisième lot de la parade générale aux changements d'avis intempestifs (demande de l'utilisateur du 2026-10-27, « pas au cas par
cas »), après 201 (196 a, réserve brisée) et 205 (196 b, péril d'eau et abri), tous deux fusionnés. Le contrat est écrit au § 4.1
du rapport 196 (`docs/taches/rapport-codex-196-changements-avis.md`) ; le diagnostic 209
(`docs/taches/rapport-codex-209-retours-restants.md`) lui attribue **21 retours de secours, rondes et services** (un secours
interrompu dès que sa cible sort de la vue alors que la faim de la cible reste connue ; préemptions de ronde, rendez-vous) et la part
« stabilité de cible » des **7 retours d'abri d'Ilse**. Après 205, le compteur 199 compte **24 retours suspects** (crue 9,
hameau 9, auberge 5, mine 1). Le lot 205 laisse aussi, en hameau 2024, **Brune qui active et endort huit fois son agenda a1** et
**Gorm 125 min sans but**, et l'attente urgente monte (crue 77,5 → 102,5, hameau 27,5 → 111,25) : à examiner ici. Le lot 195
(pas des compagnons, `ouie.py`, en attente) attend ce contrat ; ses retours (Relais 2024, Gorm sert Ilse, abandonne, reprend à
117595) en sont un cas.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (211, 212) : au plus 2 processus,
priorité réduite. Fichiers : `deliberation.py` (**sauf `_lieu_cru`/`salle_crue`**, lot 211), `agendas.py`, et leurs tests ;
**pas** `social.py`, `esprits.py`, `pnj.py` (lot 206), `ouie.py` (lot 195 en attente), `planification.py` sauf raccord minimal
justifié, ni le MJ. **Bruts dans `C:\Users\msics\donjon\artifacts\engagement-213\`.** Termine par `LOT TERMINÉ` (résumé d'une
ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, le rapport 196 en entier (§ 4.1 et 4.4), les rapports 199, 201, 205 et 209 (et ses captures
`C:\Users\msics\donjon\artifacts\retours-209\`, sur ce poste), le rapport 195 (sur `origin/codex-pas-compagnons`), puis
`deliberation.choisir`, `_candidats`, `_continuer_progres`, `secours`, l'hystérésis et `INERTIE`.

## L'invariant
**Une intention adoptée reste tenue, même à `plan == []` (garde, attente sur place, cible momentanément hors de vue), tant
qu'aucune des quatre raisons fermées n'est remplie : accomplie (prédicat propre au but) ; démentie ou bloquée (geste manqué, croyance
nouvelle qui rend la cible ou la route inadmissible) ; préemptée par un palier strictement supérieur (le palier actif garde la raison
qui l'a fait naître tant qu'elle persiste) ; supplantée au même palier par un autre but qui la domine d'au moins `INERTIE`. La
naissance d'un candidat (ce qui le fait apparaître) est distincte de sa poursuite (ce qui le garde) : un secours engagé ne disparaît
pas parce que sa cible sort de la vue, si sa détresse reste crue.** Même règle pour tout PNJ ; aucune règle propre à un personnage,
un but ou un scénario ; les préemptions légitimes (secours avant ronde, palier supérieur) restent permises.

## Vérification
- Reproduire d'abord les familles du 209 (secours/rondes, cibles d'abri) et les cas 205 (Brune a1 hameau 2024, Gorm sans but) sur la
  base actuelle ; dire lesquels relèvent du contrat et lesquels non.
- Tests après rechargement : secours poursuivi hors de vue jusqu'à accomplissement ou démenti ; préemption permise d'une ronde par
  un secours ; abandon sur démenti ; un autre cas de même nature (autre PNJ, autre but, autre scénario) ; même laps d'un bloc ou
  découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur 199** (départ :
  24) : il doit baisser, aucun scénario monter ; attente urgente, sans recours, S/F/D du lot 183 relevés ; aucune usurpation,
  plantage ni boucle nouvelle (y compris entêtement : un PNJ qui tient une intention devenue vaine).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-contrat-engagement` poussée (pas `main`) ; si la
poussée est bloquée par la revue, laisse le commit local et dis-le. `docs/etat-dev.md` (« Branche `codex-contrat-engagement`, non
fusionnée ») ; rapport d'une page `docs/taches/rapport-codex-213-contrat-engagement.md`.
