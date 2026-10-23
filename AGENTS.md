# Instructions de développement — Le Seuil

## Règle de conception prioritaire

Ne corrige pas un comportement du jeu en ajoutant un cas particulier pour l'exemple qui l'a révélé. Cela inclut les branches liées à un objet, un lieu, un personnage, une formulation du joueur, un type de fait narratif ou une consigne supplémentaire au prompt de Luna.

Pour chaque bug, identifie l'invariant général en cause et corrige le contrat commun entre la saisie, le MJ, le moteur, le rendu et la sauvegarde. Une règle propre au scénario peut exister comme donnée ou mécanique explicite du scénario ; elle ne doit pas masquer une lacune du moteur général.

Avant de déclarer la correction terminée, vérifie la chaîne complète avec le cas réel qui a révélé le problème et au moins un autre cas de même nature. Les tests doivent contrôler l'état du monde et ce que le joueur voit après rechargement, pas seulement la réponse d'une fonction isolée.

Si l'invariant ne peut pas encore être garanti, indique clairement cette limite. Ne présente pas un traitement partiel ou une liste élargie de cas comme une solution générale.

## Contrat du MJ

Toute affirmation factuelle du MJ affichée au joueur doit être compatible avec l'état du monde et ses conséquences doivent être enregistrées avant l'affichage. Cette exigence s'applique à toutes les voies de narration, y compris le dialogue ordinaire, les descriptions et les résultats d'action. Une parole de PNJ établit qu'elle a été prononcée et entendue, sans établir que son contenu est vrai.

Les affirmations du MJ relèvent de trois niveaux. **Mécanique** : entités identifiées, positions, sorties et passages, possession, ressources, lumière, présence des PNJ, missions et résultats d'action. Ces affirmations doivent être compatibles avec l'état ; une invention dans ces domaines passe par une proposition typée validée avant affichage. **Interactif** : un objet ou un détail que le joueur peut cibler existe dans l'état avant d'être manipulé. **Ambiance** : aspect, odeur, son de fond, impression. L'ambiance est libre, enregistrée avec son lieu avant affichage, et ne crée aucune entité mécanique. Un élément d'ambiance ciblé par le joueur est matérialisé par le moteur ou déclaré non manipulable.

Luna reste le MJ du jeu avec le modèle `gpt-6-luna`. Le moteur conserve l'autorité sur les positions, la perception, les ressources, les actions et les sauvegardes. La comparaison entre modèles reste désactivée.

Le contrôle garantit de façon déterministe l'absence de fuite d'entités non perçues. La détection des contradictions mécaniques reste en partie sémantique. Ne contourne pas ce manque par un nouveau mode, un mot-clé ou une exception propre à un exemple ; renforce le mécanisme commun.

## Travail sur ce dépôt (tous les agents : Claude, Codex et leurs sous-agents)

Le point de reprise est `docs/etat-dev.md` : à lire avant tout chantier, et à tenir à jour.

- Python : `.venv\Scripts\python.exe` (installation dans le README).
- Tests sans appel au modèle : `.venv\Scripts\python.exe -m unittest discover -s tests -q`.
  En parallèle, priorité réduite : `.venv\Scripts\python.exe tools/tests.py` (moitié des cœurs ;
  `--processus N`, fichiers en arguments ou `--motif "test_*.py"` ; durées dans
  `artifacts/durees_tests.json`, non versionné).
- Luna passe par le forfait ChatGPT. Le coffre (`donjon/connexion.py`) sérialise le renouvellement
  du jeton ; plusieurs exécutions peuvent tourner en même temps. Luna pèse peu sur le quota du
  forfait : plusieurs bancs Luna en parallèle sont permis (4 à 8 exécutions) ; comparer les temps
  de réponse dans les mêmes conditions de charge. Toujours sur des copies, jamais sur
  `sauvegardes/`. Depuis un worktree, `SEUIL_AUTH` désigne le coffre du dépôt principal.
- Tout refus `ErreurMonde` qu'une proposition du MJ peut déclencher porte un `attendu`
  (`donjon/refus.py`) : le champ fautif, la valeur reçue et ce qui serait accepté, en
  identifiants. Le message reste pour le joueur ; `attendu` ne va qu'au MJ. Une cause par
  refus : ne fusionne pas des causes distinctes dans un même message.
- Une branche par jalon ou correctif, fusionnée dans `main` avec un commit « Fusion du … ».
  Tenir `docs/etat-dev.md` à jour à chaque fin de jalon.
- Worktrees : dans `.worktrees/<nom>` à la racine du dépôt (ignoré par git), jamais à côté du
  dépôt. Les fusions se font dans `.worktrees/integration` (branche `integration`), puis `main`
  avance en avance rapide. `tmp-worktrees/` est à Codex ; `.claude/worktrees/` reçoit les agents
  isolés de Claude Code. Supprimer le worktree et la branche une fois fusionnés.
- Charge du poste : l'utilisateur travaille sur la machine qui calcule. `banc_pnj` cède la priorité
  et plafonne ses nuits simultanées à la moitié des cœurs (`--processus`). Lancer les bancs de
  `main` et de la branche l'un après l'autre, sauf quand le chantier mesure le temps de calcul ;
  pas plus de deux agents qui font des bancs en même temps ; les autres processus Python lourds
  (suite de tests longue) en priorité réduite.
## Rythme des lots

Un lot doit tenir en 30 à 45 minutes. Le temps va au code, pas à la vérification : le lourd se
fait une fois, à l'intégration, pour plusieurs lots ensemble.

- **Un invariant par lot.** Un brief qui en porte plusieurs se découpe en lots successifs.
- **Pas de référence relancée.** Les résultats de `main` (empreintes, banc rapide, Luna) se
  calculent une fois par commit de `main` et se réutilisent (`artifacts/references/<commit>/`,
  non versionné) ; un lot ne lance que sa branche. Si la référence manque, la lancer une fois et
  l'y ranger.
- **Vérification du lot**, le minimum qui prouve l'invariant :
  - tests ciblés pendant le travail, suite complète (`tools/tests.py`) **une seule fois**, à la fin ;
  - un changement censé ne rien changer : empreintes sur 2 h (`tools/comparer_bancs.py
    --empreintes`), seulement les scénarios touchés et le Relais, 4 graines ;
  - un changement de comportement : banc rapide, 4 h de jeu, 4 graines, mêmes scénarios ; il suffit
    pour une usurpation, une boucle ou une régression grossière ;
  - Luna, si le lot touche le MJ : **une passe**, seulement les scripts qui exercent le changement.
  - Pas de banc de 8 à 12 h, d'audit de nuits, de `VERIFIER`/`VERIFICATION` sur 8 h, ni de campagne
    Luna à deux passes dans un lot, sauf si le brief le demande expressément.
- **Vérification à l'intégration**, groupée tous les deux ou trois lots fusionnés et lancée en fond
  pendant le lot suivant : banc complet (8 à 12 h, 8 graines, quatre scénarios et `rixe`,
  `VERIFIER`), audit des nuits, `VERIFIER` et `spatial.VERIFICATION` sur 8 h, Luna deux passes sur
  les quatre bancs de référence et les bancs ciblés. Un défaut trouvé là devient un petit lot de
  correction. À la fusion, la suite complète est relancée seulement si la branche et `main` ont
  touché les mêmes fichiers de code depuis la base.
- **Rapport d'une page** : ce qui change et pourquoi (l'invariant, les fonctions), les mesures,
  les limites. Les fils bruts restent dans `artifacts/`.

