# Tâche Codex 182 (diagnostic) : pourquoi l'attente et le noir montent dans le hameau

Issu de la vérification d'intégration `ee835d2` (lot 174, rapport `docs/taches/rapport-codex-174-verif-integ.md`, bruts
`C:\Users\msics\donjon\artifacts\verif-integ-ee835d2\`). Moyennes `7adc788 → ee835d2`, `crue_hameau` 12 h × quatre graines :
attente **192,50 → 750** PNJ·min, noir **146,25 → 268,75**, pire passage **32 → 40/h** ; aussi auberge noir 951,88 → 1 055,62,
crue sans recours 178,75 → 195,62. Lots fusionnés entre les deux : 146 e (amener par la parole, lumière devant la cible), 163 (le
séjour humide cède au sec), 167/167 b/167 c (interposition, garder, protéger), et des lots MJ sans effet moteur. **Diagnostic seul,
aucun code du jeu modifié** ; si la cause est établie et le correctif évident, décris-le pour un petit lot suivant.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille).
Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`. Deux lots tournent sur le PC fixe : **au plus
2 processus de calcul**, priorité réduite. **Bruts dans `C:\Users\msics\donjon\artifacts\attente-182\`, jamais dans le worktree.**
Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Ce qu'il faut établir
- Qui attend, pour quel besoin, où, et depuis quand, dans les nuits du hameau où la hausse est la plus forte ; ce que croit le PNJ
  (recours, refus retenus, plans bornés, eau attendue, lumière) au moment où l'attente commence.
- Quel lot l'a introduite : rejoue la même nuit sur les commits intermédiaires utiles (`7adc788`, puis après 146 e, 163, 167 c)
  en priorité réduite, deux nuits au plus à la fois ; arrête dès que la marche est trouvée.
- Si l'attente est justifiée par les croyances (aucun moyen cru) ou si un recours existant est manqué (invariant en cause, fonction).
- Même question, plus brève, pour le noir de l'auberge, seulement si elle partage la cause.

## Livraison
Branche `codex-attente-hameau` : seulement `docs/taches/rapport-codex-182-attente-hameau.md` (une page, captures et invariant en
cause) et une entrée dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas `main`). Captures
sauvegardées utiles au correctif (état à la minute où l'attente commence) dans les bruts, avec leur rechargement vérifié.
