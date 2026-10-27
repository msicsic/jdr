# Tâche Codex 163 : les recours de survie réévalués pendant le trajet et l'attente

Petit lot de correction issu des vérifications d'intégration 2d504ae et 7adc788 (lots 148 et 160). Lot de 30 à 45 minutes
(`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (162, audit narratif) et un sur le laptop : au
plus 2 processus de calcul, priorité réduite. Ce lot touche `deliberation.py`, `planification.py`, `eau.py` si besoin, et leurs
tests ; **pas** `mj.py`, `narration.py`, `consignes.py`, `sources.py`, les fournisseurs. **Bruts dans
`C:\Users\msics\donjon\artifacts\survie-163\` (dépôt principal), jamais dans le worktree.** Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, les rapports des lots 148 et 160 (section « Restes et agendas ») et leurs bruts
(`C:\Users\msics\donjon\artifacts\verif-integ-7adc788\`, audit 12 h crue 2024), le rapport du lot 155, `docs/plan-crue.md`
(« L'eau dans tous les plans »), puis `deliberation.choisir`, `_classer`/attentes, `eau.en_peril` et les recours de faim.

## Les cas (crue 2024, inchangés entre 2d504ae et 7adc788)
- **Brune dans l'eau** : 16 relevés de cinq minutes entre 135 et 360 min.
- **Ilse à faim 100 en attente** : 47 relevés de 490 à 720 min.
Le lot 160 ne conclut pas qu'un recours praticable était disponible : **commence par l'établir** sur des captures rechargées
(juste avant, puis pendant) : quels recours le PNJ croit possibles, pourquoi il attend ou reste, ce qu'un plan admissible
donnerait. Si l'attente est justifiée par ses croyances (aucun moyen cru, route crue coupée), dis-le et ne change rien.

## L'invariant (si un défaut est établi)
**Un besoin de survie qui presse (eau, faim désespérée) est réévalué pendant le trajet et l'attente : un plan en cours ou une
attente ne retient pas le PNJ quand ses croyances offrent un recours admissible meilleur, ni dans l'eau quand le sec est
atteignable.** Aucune règle propre à Brune, à Ilse ou à la crue ; toute lecture nouvelle entre dans `_entrees`.

## Vérification
- Tests après rechargement sur les deux captures et un autre cas de même nature ; même laps d'un bloc ou découpé.
- Empreintes 2 h Relais/mine/auberge × quatre graines identiques ; banc rapide 4 h crue × quatre graines (eau, attente, passages
  par heure, aucune boucle nouvelle) ; audit 12 h de la seule crue 2024 pour le cas réel ; `VERIFIER` + spatial 0,2 crue 2024, 2 h.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-survie-en-route` poussée (pas `main`). `docs/etat-dev.md`
(« Branche `codex-survie-en-route`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-163-survie-en-route.md`.
