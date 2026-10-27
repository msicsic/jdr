# Tâche Codex 186 (données) : des occasions asymétriques dans les scénarios

Accord de l'utilisateur, 2026-10-27 : priorité à la richesse du comportement des PNJ, et un lot de **données de scénario** pour que
les mécanismes sociaux existants trouvent des occasions. Le diagnostic 183 (`docs/taches/rapport-codex-183-mecanismes-dormants.md`,
bruts et 18 captures dans `C:\Users\msics\donjon\artifacts\dormants-183\`) montre que les offres, promesses, commissions, services,
avis et disputes se déclenchent mais échouent presque toujours parce que les situations sont symétriques : tout le monde garde ses
biens, n'a rien d'utile à céder ni à faire, et sait la même chose. **Données seulement, aucun code du jeu modifié.**

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille ; une
validation Luna y tourne). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`. **Au plus 2 processus
de calcul**, priorité réduite. Deux lots tournent sur le PC fixe (184 agendas, 185 prévision d'eau). Ce lot touche les données de
`scenario_relais.json`, `scenario_mine.json`, `scenario_auberge.json`, `scenario_crue.json` (et leurs dérivés si une donnée y est
recopiée) et les tests qui figent ces données ; **aucun fichier `donjon/*.py`**. **Bruts dans
`C:\Users\msics\donjon\artifacts\occasions-186\`, jamais dans le worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé
d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (§ 7), `docs/plan-social.md`, le rapport 183 (colonne « donnée » de son tableau) et les
rapports 45, 115, 120, 121, 122, 125.

## Ce qu'il faut faire
Pour chaque mécanisme du tableau 183, au plus une ou deux données par scénario, cohérentes avec les personnages et leurs traits :
- **offre / marché** : un bien qu'un PNJ accepte de céder (non gardé, non nécessaire) et une contrepartie utile à un autre ;
- **promesse de travail** : une réserve ou un bien négociable contre un travail que le promettant peut réellement faire ;
- **commission** : un triangle de liens perceptibles (le demandeur tient à quelqu'un qui est disposé envers le détenteur) ;
- **service** : un moyen réalisable (bois, flamme, clé) au bon endroit pour un service spontané ;
- **avis / dispute** : des observations asymétriques (un PNJ qui a vu ce que d'autres ignorent, une rencontre précoce), et pour la
  dispute deux estimations contraires étayées.
**Sans affaiblir les gardes** : ne retire pas une garde existante pour faire céder un bien ; ajoute plutôt un bien, un lien, une
connaissance ou une situation. Garde le caractère des personnages (traits et valeurs) ; aucun nouveau personnage dans les scénarios
historiques. Chaque ajout porte un commentaire de donnée ou une ligne dans le rapport qui dit quel mécanisme il vise.

## Vérification
- Banc rapide 4 h, quatre scénarios × quatre graines, références du cache : aucune usurpation, plantage, violation ni boucle
  nouvelle ; puis audit 12 h, quatre scénarios × deux graines, et la **mesure de richesse S/F/D du lot 183** (mêmes définitions,
  scripts de `dormants-183`) avant/après, ainsi que propositions/acceptées, commissions, tâches tenues, avis adoptés, disputes,
  services. Les empreintes changent : c'est attendu, dis-le.
- Tests qui figent les données : adaptés seulement là où la donnée change, chacun justifié.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-occasions-asymetriques` poussée (pas `main`).
`docs/etat-dev.md` (« Branche `codex-occasions-asymetriques`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-186-occasions-asymetriques.md` (tableau donnée → mécanisme visé → effet observé).
