# Le Seuil

Les règles de développement et le point de reprise sont tenus dans le dépôt :

@AGENTS.md
@docs/etat-dev.md

- Python : `.venv\Scripts\python.exe` (installation dans le README).
- Tests sans appel au modèle : `.venv\Scripts\python.exe -m unittest discover -s tests -q`.
- Luna passe par le forfait ChatGPT : une seule exécution à la fois, jamais deux scripts réels ou
  bancs en parallèle.
- Une branche par jalon ou correctif, fusionnée dans `main` avec un commit « Fusion du … ».
  Tenir `docs/etat-dev.md` à jour à chaque fin de jalon.
