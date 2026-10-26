# Tâche Codex 130 (ménage) : retirer le stratège Luna des PNJ

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. Ce lot touche `donjon/stratege.py` (supprimé), `donjon/deliberation.py`, `donjon/pnj.py`,
`donjon/banc_pnj.py`, `jeu.py`, `tools/banc_stratege.py` et les tests du stratège ; **pas** `signes.py` (lot 129), ni
`mj.py`, `paroles.py`, `consignes.py` (lot 128). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par
`QUESTION : …`.

Lis `AGENTS.md`, `docs/etat-dev.md` (jalon E, remesure du stratège, « À revoir » : le stratège contourne l'arbitrage
moral du moteur), puis tous les usages : `grep -rn stratege donjon tools tests jeu.py`.

## Décision de l'utilisateur (2026-10-26)
Le stratège Luna des PNJ (`--stratege`, désactivé par défaut, jalon E) est **retiré** : module, option du jeu et du banc,
outil `banc_stratege.py`, tests propres, champ `data["stratege"]` et mesures `stratege_*` du banc. Pas de migration des
anciennes sauvegardes (décision permanente) : un champ `stratege` présent dans une vieille sauvegarde est ignoré ou retiré
au chargement, sans plantage.

## L'invariant
**Retrait sans changement de comportement** : le stratège étant désactivé par défaut, les nuits sans `--stratege` restent
strictement identiques. Les points d'appel dans `deliberation` (`plan_illicite`, `occupe`, `desoeuvre`) et `pnj`
(`terminer`, `verifier`) disparaissent sans autre effet ; aucune règle de délibération ne change. La documentation
(`docs/plan-pnj.md`, README, `docs/etat-dev.md` « Outils de mesure ») ne mentionne plus l'option comme disponible ; le
bilan historique du jalon E reste dans les docs comme histoire.

## Vérification
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes`), quatre scénarios × quatre graines contre la base (cache) :
  chronique, mesures et état final identiques (hors le seul champ `stratege` s'il était présent dans l'état initial ; dis-le).
- Une ancienne sauvegarde ou scène de test portant `data["stratege"]` se charge et se joue.
- `pyflakes` sans nom indéfini sur les fichiers touchés ; suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-retrait-stratege` poussée (pas `main`).
`docs/etat-dev.md` (« Branche `codex-retrait-stratege`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-130-retrait-stratege.md`.
