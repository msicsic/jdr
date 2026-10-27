# Tâche Codex 183 (diagnostic) : les mécanismes sociaux qui ne se déclenchent jamais, et une mesure de la richesse

Décision de l'utilisateur, 2026-10-27 : se concentrer sur la **richesse du comportement des PNJ** plutôt que sur la narration. Les
bancs montrent que beaucoup de mécanismes existent mais ne se déclenchent presque jamais dans une nuit réelle (vérification `ee835d2`,
lot 174, moyennes par nuit) : commissions par intermédiaire 0 (scènes d'auteur seulement, lot 122), tâches promises 0 tenue
(lot 115), disputes 0 à 0,12 (lot 121), avis 2,5 dits / 0,12 adopté en crue (lots 80, 88, 125), services spontanés surtout à la
mine (lot 120), propositions « faute de mieux » peu acceptées (lot 45). **Diagnostic seul, aucun code du jeu modifié.**

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille ; un
autre diagnostic, lot 182, y tourne). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`. **Au plus
2 processus de calcul**, priorité réduite. Réemploie d'abord les bruts existants (`C:\Users\msics\donjon\artifacts\verif-integ-ee835d2\`,
49 nuits) avant de rejouer quoi que ce soit. **Bruts dans `C:\Users\msics\donjon\artifacts\dormants-183\`, jamais dans le worktree.**
Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (§ 6.4, 7) et `docs/plan-agendas.md` (§ 3 table des cas, § 9 A5 à A8), puis les
rapports des lots cités.

## Ce qu'il faut établir, pour chaque mécanisme
- Ses conditions de déclenchement dans le code (fonction, seuils, ordre parmi les recours) et, dans les nuits réelles, **quelle
  condition manque quand l'occasion semble là** : seuil jamais atteint, occasion absente des scénarios, recours ordinaire qui passe
  toujours avant, refus systématique, ou pièce manquante (renvoi aux étapes A5, A6, 3d du plan).
- Un ou deux moments réels par mécanisme où l'occasion était presque là (scénario, graine, minute, PNJ), sauvegardés en capture
  rechargeable dans les bruts pour un lot suivant.
- Ce qui relève d'une **donnée de scénario** (profil, lien, ressource, situation) plutôt que du moteur ; ne modifie aucune donnée,
  propose-la.

## Une mesure de la richesse
Propose et calcule sur les 49 nuits existantes une mesure simple, lisible dans le récit, de la richesse sociale d'une nuit :
par exemple épisodes sociaux distincts (demande, offre, service, avis, dispute, commission, tâche, interposition, appel, vol vu),
PNJ qui changent de but après un événement social, projets nés (aujourd'hui seulement les agendas déclarés), et leur diversité par
PNJ. Elle doit pouvoir entrer dans `tools/audit_nuits.py` ou le récit du banc sans changer une nuit ; décris l'ajout, sans
l'implémenter dans ce lot si cela dépasse le créneau.

## Livraison
Branche `codex-mecanismes-dormants` : `docs/taches/rapport-codex-183-mecanismes-dormants.md` (une page : tableau mécanisme →
condition manquante → donnée ou pièce à ajouter → lot proposé ; la mesure proposée et ses valeurs actuelles par scénario) et une
entrée dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas `main`).
