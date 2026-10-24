# Tâche Codex 55 : deux personnes qui se font confiance se disent leurs constats matériels

Branche `codex-constats-partages` (elle porte ce fichier, issue de l'intégration **5b174ad** : lots 38 à 53 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant,
vérification minimale, rapport d'une page. Pas de Luna.

Lots en même temps : 52 sur ce même poste (`planification.py`) ; 54 sur l'autre poste (`francais.py`, `noms.py`,
peut-être `social.py` pour l'élision). Ne touche pas à `planification.py` ; dans `social.py`, ne touche pas aux
fonctions d'accord du français (elles changent dans le lot 54).

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `constater-et-rumeurs`, `codex-refus-retenus`/`refus-retenus` (moyens
crus), `boucles-pnj` (« ce qu'on a déjà dit »), `codex-soi-meme` lot 35), **`docs/plan-relations.md` § 3f, le point
« Partager ses constats »** (décision du 2026-10-24), puis `donjon/social.py` (`NOUVELLES`, `nouvelles`, `bavarder`,
`recevoir`, `_auditeur`, `RANG_MAX`), `donjon/esprits.py` (`croire`, sources `dit:`), `donjon/deliberation.py`
(`moyens_crus`, `tient` : un refus retenu tient tant qu'aucun moyen nouveau n'est cru).

## Le constat
`social.bavarder` ne confie que des accusations et des anomalies sociales (`NOUVELLES` : vu agir, vol surpris, absence,
dette niée…). Un PNJ qui a trouvé la réserve vide, une porte fermée à clé, un feu éteint ou l'eau montée ne le dit
à personne : chacun va buter seul sur la même porte, et le joueur n'entend presque jamais d'échange utile.

## L'invariant
**Un constat matériel récent (ce qu'il a vu ou essayé lui-même : un contenant ou une réserve vide, une porte ou un
contenant fermé à clé, un feu ou une source éteints, l'eau dans un lieu) se confie comme une nouvelle**, par le même
chemin que les autres (`bavarder` → `recevoir`), à qui il fait confiance et dont il croit qu'il ne le sait pas
(« ce qu'on a déjà dit » reste vrai) ; l'auditeur le croit en ouï-dire (source `dit:`, confiance de ouï-dire), sauf
constat propre plus récent ; la règle des refus retenus et des moyens crus en tient compte d'elle-même. Une seule
nouvelle par minute comme aujourd'hui ; le constat a priorité plus basse qu'une accusation. Pas de liste de lieux ni
de scénarios : ce qui se confie est ce que les croyances d'état et de lieu disent déjà, daté.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : un PNJ qui trouve une réserve vide le dit à un proche, qui ne s'y
  rend plus (ou la croit vide en ouï-dire) ; une porte trouvée fermée à clé dite et crue ; un constat déjà su de
  l'auditeur, non répété ; un constat contredit par ce que l'auditeur a vu depuis, ignoré ; le joueur qui entend
  l'échange lit la nouvelle.
- Banc rapide (`tools/comparer_bancs.py --reference 5b174ad`, 4 h, 4 graines, quatre scénarios) : aucune usurpation,
  violation, plantage ni boucle nouvelle (`tools/audit_nuits.py` : avertissements redits, bascules) ; nouvelle mesure
  `constats_confies` ; écarts lus en deux lignes.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` § 3f (ce qui est fait), `docs/etat-dev.md`
(« Branche `codex-constats-partages`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-55-constats-partages.md` (invariant, fonctions, mesures, limites).
