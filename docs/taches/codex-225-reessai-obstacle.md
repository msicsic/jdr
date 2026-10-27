# Tâche Codex 225 : on ne reprend un but abandonné que si ce qui l'a arrêté a changé

Décision de l'utilisateur du 2026-10-27 au soir (`docs/etat-dev.md`, « Décisions prises le 2026-10-27 au soir », point 3), après la
revue 217 (« L'entêtement a parfois une allure d'horloge »). Aujourd'hui un PNJ bloqué patiente `PATIENCE` = 30 minutes, puis
renonce (`deliberation.renoncer`) et ne reprend ce but qu'après `REPIT` = 60 minutes comptées de l'instant du renoncement
(`deliberation.py`, contrôle des `renoncements` dans le choix). Cas réel : **mine 1985, Odon vise 40 pièces à 0, 91 et 182 min et
abandonne vers 30, 121 et 212** : un rythme commandé par l'horloge, pas par ce qu'il apprend. **Décision : la patience de 30 minutes
reste ; le répit de 60 minutes est remplacé par la cause du renoncement** (témoin présent, porte verrouillée, refus, personne
absente, moyen manquant) : le but ne reprend que si le PNJ croit cette cause changée ou s'il croit un moyen nouveau, comme les refus
retenus selon leur cause (lot 110) et les emprunts rendus (lot 220) ; jamais par le seul délai.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (195, 224) : au plus 2 processus, priorité
réduite. Fichiers : `deliberation.py` (`renoncer`, le contrôle des renoncements dans le choix, `PATIENCE`/`REPIT` ; le lot 224
modifie `menager_flamme`, n'y touche pas), `esprits.py` (**seulement** le champ `renoncements` et sa validation ; les lots 206 b et
221 y modifient d'autres registres), et leurs tests ; **pas** `social.py`, `pnj.py`, `ouie.py` (lot 195), `echanges.py`, ni le MJ.
**Bruts dans `C:\Users\msics\donjon\artifacts\reessai-225\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 217 et 213 (contrat d'engagement fusionné : sortie attestée, agenda en sommeil), 110 et 220 (retenu
selon sa cause), 87 (attentes bornées), puis `renoncer`, `_patienter`, le contrôle des `renoncements` et `deliberation.tient`.

## L'invariant
**Un renoncement retient sa cause, telle que le PNJ la croit au moment de renoncer ; le but ne redevient candidat que lorsqu'il croit
cette cause levée (le témoin parti, la porte ouverte, la personne revenue, la réponse changée) ou un moyen nouveau, et jamais par le
seul passage du temps. Un PNJ ne reste pas figé faute d'information : ses moyens ordinaires (rondes, regard, bruits, nouvelles)
mettent à jour ce qu'il croit de la cause.** La patience de 30 minutes reste. Même règle pour tout PNJ et tout but ; aucune règle
propre à Odon ou au scénario.

## Vérification
- Reproduire d'abord le cas réel (mine 1985) sur la base actuelle et dire la cause de chaque renoncement d'Odon.
- Tests après rechargement : Odon ne reprend plus son but au bout de 60 min si rien n'a changé, et le reprend quand la cause est levée ;
  un autre cas de même nature (autre PNJ, autre cause, autre scénario) ; un PNJ qui n'apprend rien ne se fige pas indéfiniment s'il
  a un moyen ordinaire de revérifier ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec les classes du compteur 219** :
  répétitions suspectes (ne doivent pas monter), attente urgente, sans recours, renoncements, S/F/D du lot 183 ; aucune usurpation,
  plantage ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-reessai-obstacle` poussée (pas `main`) ; si la poussée est
bloquée, laisse le commit local et dis-le. `docs/etat-dev.md` (« Branche `codex-reessai-obstacle`, non fusionnée ») ; rapport d'une
page `docs/taches/rapport-codex-225-reessai-obstacle.md`.
