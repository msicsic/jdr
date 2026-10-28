# Tâche Codex 251 : un service qui vient d'échouer n'est pas reproposé à l'identique

Le diagnostic 249 (`docs/taches/rapport-codex-249-confidences-perdues.md`, dernière ligne du tableau ; bruts
`C:\Users\msics\donjon\artifacts\confidences-249\`, et ceux du lot 235 dans `...\artifacts\sait-235\`) relève un **défaut
réel d'admission et de reprise du service** : auberge 2024, vers 226 min, Mireille (cuisine) tente de `servir` Mathurine,
crue et réellement dans la salle commune ; le geste échoue à l'instant **135695**, puis **le même plan est reproposé à
135725** sans que rien ait changé (Mathurine n'est pas revenue, aucune croyance nouvelle). Le cas a été vu sur la branche
du lot 235 (`codex-sait-observations-c`, `942a3c2`) ; aucun lien causal avec une confidence n'est établi.

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le PC fixe**, au plus 2 processus, priorité réduite.

## Ce qu'on attend
1. **Reproduire** : d'abord sur l'intégration courante (auberge 2024, départ tiré, 4 h) ; si l'occurrence n'y paraît pas,
   sur une capture de la nuit du 235 juste avant 135695 (worktree détaché de `942a3c2`). Dire où elle se reproduit.
2. **Cause** : pourquoi `servir` échoue (condition du geste : contact, présence, portée, part, lumière…) et pourquoi
   l'admission ou la revalidation du plan ne voit pas cet échec. Le contrat visé est commun : **un geste qui échoue pour une
   cause que le PNJ constate n'est pas reproposé tant qu'il ne croit pas cette cause levée** (lien avec le contrat 213 et
   le réessai lié à l'obstacle du 225), sans délai arbitraire ni cas propre au service ou à l'auberge.
3. **Corriger** dans la fonction commune fautive (admission, revalidation, constat de l'échec), sinon dire précisément
   la limite.

**Fichiers autorisés d'avance** : la condition et le constat d'échec de `servir` et leur raccord dans `pnj.py`,
`deliberation.py` (admission/revalidation), `planification.py` (prédicat d'admission du geste) ; leurs tests voisins,
**arbitrage autorisé avec preuve**. **Pas** : `social.py` (lot 250 en cours), le MJ, les scénarios.

## Vérification
- Cas réel (capture) : plus de reproposition identique ; un autre cas de même nature (autre service ou autre geste qui
  échoue, autre scénario). Monde et rendu identiques après rechargement, même laps d'un bloc ou découpé.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache (ta base `integration`), compteur 219 : lancé
  détaché ; suspects sans hausse, préemptions et « à expliquer » rapportés.
- Pas de suite complète.

## Livraison
- Branche `codex-service-repropose` poussée. Rapport d'une page `docs/taches/rapport-codex-251-service-repropose.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\service-251\`.
  Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
