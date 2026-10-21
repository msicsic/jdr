# Le Seuil

Les règles de développement et le point de reprise sont tenus dans le dépôt :

@AGENTS.md
@docs/etat-dev.md

- Python : `.venv\Scripts\python.exe` (installation dans le README).
- Tests sans appel au modèle : `.venv\Scripts\python.exe -m unittest discover -s tests -q`.
- Luna passe par le forfait ChatGPT. Le coffre (`donjon/connexion.py`) sérialise le renouvellement
  du jeton ; plusieurs exécutions peuvent tourner en même temps (4 vérifiées). Rester à quelques
  exécutions simultanées pour ne pas atteindre les plafonds du forfait ; mesurer les temps de
  réponse au calme. Depuis un worktree, `SEUIL_AUTH` désigne le coffre du dépôt principal.
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
