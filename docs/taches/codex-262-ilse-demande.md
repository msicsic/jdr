# Tâche 262 (diagnostic) : pourquoi Ilse ne demande pas une part à Gorm (crue 7)

Suite du diagnostic 261 (`docs/taches/rapport-codex-261-ilse-poele.md`, fusionné ; bruts
`C:\Users\msics\donjon\artifacts\ilse-261\`, dont les captures `snapshot_270.json`, `snapshot_400.json`,
`snapshot_600.json`). À la crue 7, de 270 à 720 min, Ilse a faim mais sa recherche de recours pour manger s'arrête à
**un seul nœud** (`epuise`). Les vivres sont à la réserve gardée par Gorm. Le rapport 261 ne dit pas **pourquoi la
demande d'une part à Gorm** (geste `demander` du planificateur, contenu `demande` de la parole commune) n'apparaît même
pas comme successeur.

**Diagnostic seul : aucun code du jeu modifié.**

## Ce que le rapport doit établir
Sur les captures 270, 400 et 600 rechargées :
1. Les gestes que `planification.gestes` propose à Ilse depuis l'état initial pour le but `faim` (liste complète).
2. Si `demander` (part des vivres à Gorm) en est absent : **quelle condition l'exclut**, nommée par sa fonction et sa
   ligne : refus retenu (`deliberation.tient`, `esprit["refus"]`, sa cause et sa date), méfiance ou rancune, croyance sur
   l'endroit de Gorm ou des vivres, épuisement cru des vivres, autre.
3. Si cette exclusion est **juste** selon les croyances d'Ilse (par exemple un refus « nécessaire » toujours valable,
   aucun moyen nouveau), ou si elle repose sur une lecture erronée (un refus qui aurait dû être levé, une croyance
   périmée) : dans ce cas, la règle commune en cause en une phrase, sans exception propre à Ilse, à Gorm ou à la crue.

Sources : `donjon/planification.py` (`gestes`, `_parts`, `Vue`), `donjon/deliberation.py` (`_candidats`, `tient`,
`moyens_crus`, `retenir_refus`), `docs/plan-social.md` (« Des refus retenus selon leur cause »).

Lot court (moins de 45 minutes). **Poste : le PC fixe**, un processus à priorité réduite. Pas de Luna, pas de suite
complète, pas de banc. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.

## Livraison
- Branche `codex-ilse-demande` : seulement `docs/taches/rapport-codex-262-ilse-demande.md` (une page) et une entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\ilse-262\`. Commite ; pousse si
  tu peux, sinon laisse le commit local et dis-le. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou
  `QUESTION : …`.
