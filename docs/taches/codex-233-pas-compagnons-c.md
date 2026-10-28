# Tâche Codex 233 : reprise du lot 195, entendre un compagnon sans perdre la rencontre

Le lot 195 (branche `codex-pas-compagnons`, dernière livraison `cf777e7`, rapport
`docs/taches/rapport-codex-195-pas-compagnons.md` et annexe `rapport-codex-195-arbitrage.md` sur cette branche) attribue un
pas compatible avec la marche d'un compagnon cru là, sans retournement ni bruit inconnu. Résultat sur 20 paires de 4 h :
suspects 5 → 1, retournements divisés par deux à quatre. Mais **le hameau perd sa richesse** : S 40,5 → 27, échanges
acceptés 16 → 9, demandes −28, offres −10, promesses −10 ; des interactions naissaient des perceptions fortuites qu'offrait
le retournement.

**Décision de l'utilisateur (2026-10-28) : reprendre.** Garder l'attribution, mais un son de compagnon proche continue
d'attirer l'attention sans retournement complet : on ne doit pas perdre la rencontre.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. D'autres lots
calculent sur ce poste : au plus 2 processus, priorité réduite.

**Départ** : branche `codex-pas-compagnons-c` depuis `integration` ; fusionne `origin/codex-pas-compagnons` (`cf777e7`),
conflits documentaires seulement attendus. **Fichiers** : `ouie.py`, `echanges.tenu` (extension déjà autorisée au 195) et
leurs tests. **Pas** : `biens.services_proteges` (lot 232), `social.py` (lot 235), `signes.place` et `pnj.agir` (lot 234 :
le défaut de placement relevé par 195 n'est pas à corriger ici), `planification.py`, le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\pas-233\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

## Ce qu'on te demande
1. Sur deux nuits du hameau (1985 et 42, 4 h), pour les interactions perdues (demandes, offres, promesses) : à quelle
   perception tenaient-elles sur la référence (retournement, vue de qui, croyance de lieu rafraîchie) et ce qui manque sur
   la branche. Un tableau court.
2. **Invariant à établir** : un bruit attribué à un compagnon cru proche est une information sur sa présence, utilisable
   comme celle d'une rencontre (lui parler, lui demander, lui proposer), sans retournement complet ni position inventée ;
   une parole ou une initiative qui en naît passe par les mêmes règles que pour un compagnon vu (s'entendre, identifier).
   Aucune règle propre au hameau ou à un PNJ.
3. Si l'invariant exige un raccord hors de tes fichiers, arrête-toi et pose la `QUESTION`.

## Vérification
- Tests après rechargement : un cas réel du hameau où l'interaction revient, un autre cas de même nature (autre
  scénario), le bruit d'un inconnu toujours inconnu, même laps d'un bloc ou découpé, monde et rendu rechargés.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache, compteur 219 et S/F/D du lot 183 :
  suspects sans hausse, retournements toujours en baisse nette, **S du hameau revenu dans l'étendue de la référence**.
  Si ce critère n'est pas atteint, dis-le avec les chiffres ; ne le présente pas comme acquis.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-pas-compagnons-c` poussée (pas `main`). Si la poussée est bloquée par la revue, laisse le commit local
  et dis-le.
- `docs/etat-dev.md` : « Branche `codex-pas-compagnons-c`, non fusionnée ».
- Rapport d'une page `docs/taches/rapport-codex-233-pas-compagnons-c.md`.
